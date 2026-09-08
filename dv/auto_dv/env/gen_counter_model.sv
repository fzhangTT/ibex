// gen_counter_pkg: the boundary model of the performance counters (component API document
// dv/auto_dv/docs/gen_component_api_counter_model.md; the per-event RVFI-visible rule of each counter is
// dv/auto_dv/evidence/gen_hpm_event_defs.md Section 2). Two checkers live here and both judge the window
// between two ARCHITECTURAL READS of the counter, which is the only anchor that makes an exact prediction
// sound: the event pulses of counters 7, 8 and 9 fire in the instruction's own ID cycles
// (rtl/ibex_id_stage.sv:928, :934, :941 into rtl/ibex_controller.sv:681-687) while rvfi_ext_mhpmcounters is
// sampled at the record's ID exit (rtl/ibex_core.sv:2108-2128), so an instruction that holds ID for one cycle
// does not see its own pulse and one that holds it longer does; both endpoints of a read window are taken at
// the same point of the pipeline, so that asymmetry cancels (a csrr of counters 5..9 returns the register
// value in the cycle the csrr is in ID, older pulses having landed: gen_hpm_event_defs.md Section 1).
//   ctr_hpm_exact: the read difference of counter 7 (NumJumps), 8 (NumBranches) and 9 (NumBranchesTaken)
//   equals the events the records strictly between the two reads owe.
//   ctr_hpm_bound: every counter advances over a read window by at most the window's cycles (one event per
//   cycle at most), and counters 11 (NumCyclesMulWait) and 12 (NumCyclesDivWait) by at most the window's
//   cycles in which no data-bus access was outstanding, because a cycle spent waiting for a memory response
//   is not a cycle waiting for the multiply to complete (doc/03_reference/performance_counters.rst:47-50).
// Four knobs carry the known RTL deviations, all with one sense: 1 follows the RTL and 0 follows the
// documentation (the direction ruling in gen_bug_log.md Section 0.6). The default is 1 on all four, each
// accommodation is counted per bug, and the counts are reported at the end of every run, so a run that met a
// candidate says so and a run that did not says that too.
// Nothing here reads the ISA model or a DUT internal: every term comes from the RVFI record stream and from
// the data-bus agent's completed transactions.
package gen_counter_pkg;
  import uvm_pkg::*;
  import gen_tb_pkg::*;
  import gen_cfg_pkg::*;
  import gen_agents_pkg::*;
  import gen_rvfi_pkg::*;
  import gen_checkers_pkg::*;
  `include "uvm_macros.svh"

  `uvm_analysis_imp_decl(_ctr_dbus)

  // index k of rvfi_ext_mhpmcounters is mhpmcounter[k+3] (rtl/ibex_core.sv:2108-2128)
  parameter int unsigned GEN_CTR_JUMPS    = 4;   // mhpmcounter7  NumJumps
  parameter int unsigned GEN_CTR_BRANCHES = 5;   // mhpmcounter8  NumBranches
  parameter int unsigned GEN_CTR_TAKEN    = 6;   // mhpmcounter9  NumBranchesTaken
  parameter int unsigned GEN_CTR_MULWAIT  = 8;   // mhpmcounter11 NumCyclesMulWait
  parameter int unsigned GEN_CTR_DIVWAIT  = 9;   // mhpmcounter12 NumCyclesDivWait

  // The counter index a CSR address names, -1 for anything else; `high` reports the h alias, whose value is
  // the counter's bits 63:32 and so reads 0 at MHPMCounterWidth 32.
  function automatic int gen_ctr_index_of_csr(logic [11:0] addr, output bit high);
    high = 1'b0;
    if (addr >= ibex_pkg::CSR_MHPMCOUNTER3 && addr < ibex_pkg::CSR_MHPMCOUNTER3 + GEN_MHPM_COUNTER_NUM)
      return int'(addr - ibex_pkg::CSR_MHPMCOUNTER3);
    if (addr >= ibex_pkg::CSR_MHPMCOUNTER3H && addr < ibex_pkg::CSR_MHPMCOUNTER3H + GEN_MHPM_COUNTER_NUM) begin
      high = 1'b1;
      return int'(addr - ibex_pkg::CSR_MHPMCOUNTER3H);
    end
    return -1;
  endfunction

  class gen_counter_model extends uvm_subscriber #(gen_rvfi_txn);
    `uvm_component_utils(gen_counter_model)
    uvm_analysis_imp_ctr_dbus #(gen_bus_txn, gen_counter_model) imp_ctr_dbus;
    gen_env_cfg cfg;

    // One window per counter index, opened by a read of the counter and closed by the next read of it.
    typedef struct {
      bit          open;
      logic [31:0] base;             // the value the opening read returned
      int unsigned base_cycle;       // the opening read record's cycle
      int unsigned owed;             // events the records since the opening read owe (counters 7, 8, 9)
      int unsigned mul_recs;         // multiply records in the window (counter 11)
      int unsigned div_recs;         // divide records in the window (counter 12)
      bit          mem_rec;          // a load or store record fell inside
      bit          wrote;            // a write to the counter or its h alias fell inside
      bit          inhibited;        // the counter's mcountinhibit bit was set at a record inside
      bit          memtrap;          // a memory-access trap fell inside
      bit          dummies;          // cpuctrlsts.dummy_instr_en was set at a record inside
      bit          acc_fencei;       // a fence.i was counted as a jump under the knob
      bit          acc_dit;          // a not-taken branch was counted as taken under the knob
    } gen_ctr_window_t;
    gen_ctr_window_t win [GEN_MHPM_COUNTER_NUM];

    // Shadows kept from the record stream alone, by the architectural write rule (the pattern
    // gen_fcov_pkg.sv:2153-2166 uses for cpuctrlsts): rw takes the operand, set ORs it, clear ANDs its
    // complement, and the operand is the uimm for the immediate forms.
    logic [31:0] inhibit = 32'h0;   // mcountinhibit, reset 0 (rtl/ibex_cs_registers.sv:1725)
    bit          dit = 1'b0;        // cpuctrlsts.data_ind_timing
    bit          dummy_en = 1'b0;   // cpuctrlsts.dummy_instr_en

    // Completed data-bus transactions as [grant, response] spans on the bridge cycle counter, which is the
    // base a record's `cycle` is on (gen_agents_pkg.sv:19-37, :288, :310). An access still outstanding at a
    // closing read has no span yet, which only makes the bound of that window looser, never tighter.
    typedef struct { int unsigned lo, hi; } gen_ctr_span_t;
    gen_ctr_span_t dbus_span [$];

    // report counters, per the direction ruling: the accommodations are counted per bug
    int unsigned judged_exact = 0, judged_bound = 0, unjudged_write = 0, unjudged_inhibit = 0;
    int unsigned miss_exact = 0, miss_bound = 0;
    // Accommodation counts, per the direction ruling: each one counts a window in which the RTL default
    // ACTUALLY differed from the documentation, so a nonzero count says the run met the candidate and a zero
    // count says it did not.
    int unsigned acc_b20_fencei = 0;      // a fence.i was counted as a jump and the counter moved for it
    int unsigned acc_b11_dit = 0;         // a not-taken branch under dit was counted as taken
    int unsigned acc_b17_branch = 0;      // counter 8 was bounded and the RTL exceeded the documented count
    int unsigned acc_b17_wait = 0;        // counter 11 / 12 exceeded the documented bound, dummies off
    int unsigned acc_b7_dummy = 0;        // counter 11 / 12 exceeded it with dummy instructions enabled
    int unsigned rec_fencei = 0, rec_dit_branch = 0, rec_mul = 0, rec_div = 0;

    function new(string name, uvm_component parent);
      super.new(name, parent);
      imp_ctr_dbus = new("imp_ctr_dbus", this);
    endfunction

    function void build_phase(uvm_phase phase);
      super.build_phase(phase);
      if (!uvm_config_db#(gen_env_cfg)::get(this, "", "cfg", cfg)) `uvm_fatal("GEN_CTR", "cfg not in uvm_config_db")
    endfunction

    function bit exact_on();
      return gen_chk_en(cfg, cfg.chk_ctr_hpm_exact, cfg.chk_ctr_hpm_exact_set);
    endfunction
    function bit bound_on();
      return gen_chk_en(cfg, cfg.chk_ctr_hpm_bound, cfg.chk_ctr_hpm_bound_set);
    endfunction

    // ---- the data-bus side: one span per completed transaction
    function void write_ctr_dbus(gen_bus_txn tr);
      gen_ctr_span_t s;
      s.lo = tr.stamp_gnt;
      s.hi = (tr.stamp_rvalid > tr.stamp_gnt) ? tr.stamp_rvalid : tr.stamp_gnt;
      dbus_span.push_back(s);
      prune();
    endfunction

    // a span that ends before every open window began can never contribute again
    function void prune();
      int unsigned oldest = 32'hFFFFFFFF;
      foreach (win[k]) if (win[k].open && win[k].base_cycle < oldest) oldest = win[k].base_cycle;
      while (dbus_span.size() > 0 && dbus_span[0].hi < oldest) void'(dbus_span.pop_front());
    endfunction

    // cycles of [lo, hi] covered by at least one span. The bus answers in grant order, so the spans arrive
    // sorted and `reach` merges the overlap of a span with the ones already counted.
    function int unsigned busy_cycles(int unsigned lo, int unsigned hi);
      int unsigned covered = 0, reach = lo, a, b;
      if (hi <= lo) return 0;
      foreach (dbus_span[i]) begin
        a = (dbus_span[i].lo > lo) ? dbus_span[i].lo : lo;
        b = (dbus_span[i].hi < hi) ? dbus_span[i].hi : hi;
        if (b <= a) continue;
        if (a < reach) a = reach;
        if (b > a) begin covered += b - a; reach = b; end
      end
      return covered;
    endfunction

    function void note_event(int k, bit fencei, bit dit_not_taken);
      if (!win[k].open) return;
      win[k].owed++;
      if (fencei) win[k].acc_fencei = 1'b1;
      if (dit_not_taken) win[k].acc_dit = 1'b1;
    endfunction

    // ---- the record side
    function void write(gen_rvfi_txn t);
      bit is_csr, is_write, high, ld_st;
      logic [11:0] csr;
      logic [2:0] f3;
      logic [31:0] opnd;
      int ctr_k;
      int unsigned bytes;
      bit is_branch, is_taken, is_jump, is_fencei, is_mul, is_div, is_mem;

      is_csr   = (t.insn[6:0] == ibex_pkg::OPCODE_SYSTEM) && (t.insn[14:12] != 3'b000) && !t.trap;
      csr      = t.insn[31:20];
      f3       = t.insn[14:12];
      is_write = is_csr && (f3[1:0] == 2'b01 || t.insn[19:15] != 5'd0);   // csrrw always writes; csrrs / csrrc with rs1 or uimm 0 only read
      opnd     = f3[2] ? 32'(t.insn[19:15]) : t.rs1_rdata;               // uimm for the i forms, rs1 otherwise
      ctr_k    = gen_ctr_index_of_csr(csr, high);

      // ---- close the window this record's read of a counter ends, before its own events are added
      if (is_csr && ctr_k >= 0 && !high && t.rd_addr != 5'd0) judge(ctr_k, t);

      // ---- the shadows this record leaves behind
      if (is_csr && csr == ibex_pkg::CSR_MCOUNTINHIBIT && is_write)
        inhibit = (f3[1:0] == 2'b01) ? opnd : (f3[1:0] == 2'b10) ? (inhibit | opnd) : (inhibit & ~opnd);
      if (is_csr && csr == GEN_CSR_CPUCTRLSTS && is_write) begin
        // the old value is the record's own read result where it read, else the tracked bit
        bit old_dit = (t.rd_addr != 5'd0) ? t.rd_wdata[GEN_CPUCTRLSTS_DATA_IND_TIMING_BIT] : dit;
        bit old_dmy = (t.rd_addr != 5'd0) ? t.rd_wdata[GEN_CPUCTRLSTS_DUMMY_INSTR_EN_BIT] : dummy_en;
        dit      = (f3[1:0] == 2'b01) ? opnd[GEN_CPUCTRLSTS_DATA_IND_TIMING_BIT]
                 : (f3[1:0] == 2'b10) ? (old_dit | opnd[GEN_CPUCTRLSTS_DATA_IND_TIMING_BIT])
                                      : (old_dit & ~opnd[GEN_CPUCTRLSTS_DATA_IND_TIMING_BIT]);
        dummy_en = (f3[1:0] == 2'b01) ? opnd[GEN_CPUCTRLSTS_DUMMY_INSTR_EN_BIT]
                 : (f3[1:0] == 2'b10) ? (old_dmy | opnd[GEN_CPUCTRLSTS_DUMMY_INSTR_EN_BIT])
                                      : (old_dmy & ~opnd[GEN_CPUCTRLSTS_DUMMY_INSTR_EN_BIT]);
      end

      // ---- what this record owes the counters
      is_mem    = gen_insn_mem_access(t.insn, ld_st, bytes);
      is_jump   = !t.trap && gen_insn_is_jump(t.insn);
      is_fencei = !t.trap && gen_insn_is_fencei(t.insn);
      is_branch = !t.trap && gen_insn_is_cond_branch(t.insn);
      is_taken  = is_branch && (t.pc_wdata != t.pc_rdata + gen_insn_len(t.insn));
      is_mul    = !t.trap && gen_insn_is_mul(t.insn);
      is_div    = !t.trap && gen_insn_is_div(t.insn);
      if (is_fencei) rec_fencei++;
      if (is_branch && dit) rec_dit_branch++;
      if (is_mul) rec_mul++;
      if (is_div) rec_div++;

      // NumJumps counts jal and jalr in either encoding; mret and dret take the special-request path and are
      // not jumps. This RTL implements fence.i as a jump to the next pc (rtl/ibex_decoder.sv:704-720) and the
      // counter moves for it, which the documentation excludes: bug candidate B20, so the knob decides.
      if (is_jump) note_event(GEN_CTR_JUMPS, 1'b0, 1'b0);
      else if (is_fencei && cfg.ctr_rtl_jumps_fencei) note_event(GEN_CTR_JUMPS, 1'b1, 1'b0);
      // NumBranches counts every conditional branch once.
      if (is_branch) note_event(GEN_CTR_BRANCHES, 1'b0, 1'b0);
      // NumBranchesTaken counts a conditional branch whose next fetch address is not the fall-through. With
      // cpuctrlsts.data_ind_timing set this RTL sets the branch for every branch, taken or not
      // (rtl/ibex_id_stage.sv:928): bug candidate B11, so the knob decides.
      if (is_branch && is_taken) note_event(GEN_CTR_TAKEN, 1'b0, 1'b0);
      else if (is_branch && dit && cfg.ctr_rtl_taken_dit) note_event(GEN_CTR_TAKEN, 1'b0, 1'b1);

      foreach (win[k]) begin
        if (!win[k].open) continue;
        if (inhibit[k + 3]) win[k].inhibited = 1'b1;
        if (dummy_en) win[k].dummies = 1'b1;
        if (is_mem) win[k].mem_rec = 1'b1;
        // a memory-access trap kills an instruction that may already have pulsed and is re-fetched after the
        // handler, so a window holding one is not exactly predictable (gen_hpm_event_defs.md Section 2, the
        // second corner of events 7 and 9)
        if (t.trap && is_mem) win[k].memtrap = 1'b1;
      end
      if (is_mul && win[GEN_CTR_MULWAIT].open) win[GEN_CTR_MULWAIT].mul_recs++;
      if (is_div && win[GEN_CTR_DIVWAIT].open) win[GEN_CTR_DIVWAIT].div_recs++;
      // a write to a counter loads it, so the window it falls in has no derivable difference
      if (is_csr && is_write && ctr_k >= 0 && win[ctr_k].open) win[ctr_k].wrote = 1'b1;

      // ---- open a window at a read of the counter; the read record itself owes no event
      if (is_csr && ctr_k >= 0 && !high && t.rd_addr != 5'd0) begin
        win[ctr_k] = '{default: 0};
        win[ctr_k].open = 1'b1;
        win[ctr_k].base = t.rd_wdata;
        win[ctr_k].base_cycle = t.cycle;
      end
      prune();
    endfunction

    // judge the window of counter k that this record's read closes
    function void judge(int k, gen_rvfi_txn t);
      logic [31:0] delta;
      int unsigned span, busy, free, lo, hi, ceil;
      bit as_bound;
      if (!win[k].open) return;
      win[k].open = 1'b0;
      delta = t.rd_wdata - win[k].base;   // 32 bits wide, so a counter wrap is the same subtraction
      lo = win[k].base_cycle; hi = t.cycle;
      span = (hi > lo) ? (hi - lo) : 0;
      busy = busy_cycles(lo, hi);
      free = (span > busy) ? (span - busy) : 0;
      // Both anchors are CSR-read records, whose distance from their own ID exit carries no memory wait, so
      // the record span is the span between the two counter samples up to the ID-exit offset the two anchors
      // need not share; every upper bound below carries that offset as slack.
      if (win[k].wrote) begin unjudged_write++; return; end
      if (win[k].inhibited) begin unjudged_inhibit++; return; end
      // the accommodated event was predicted, so the RTL's own count is what the window shows: it differed
      // from the documentation exactly when the window's difference matches the accommodated prediction
      if (win[k].acc_fencei && delta == win[k].owed) acc_b20_fencei++;
      if (win[k].acc_dit && delta == win[k].owed) acc_b11_dit++;

      if (bound_on()) begin
        judged_bound++;
        if (delta > span + GEN_RVFI_ID_EXIT_OFFSET) begin
          miss_bound++;
          `uvm_error("ctr_hpm_bound", $sformatf("mhpmcounter%0d advanced %0d over a %0d cycle window, and a counter moves by at most one per cycle: read %08h -> %08h, cycles %0d..%0d, order %0d",
                                                k + 3, delta, span, win[k].base, t.rd_wdata, lo, hi, t.order))
        end
        if (k == GEN_CTR_MULWAIT || k == GEN_CTR_DIVWAIT) begin
          int unsigned recs = (k == GEN_CTR_MULWAIT) ? win[k].mul_recs : win[k].div_recs;
          string what = (k == GEN_CTR_MULWAIT) ? "multiply" : "divide";
          // A window with no multiply (or divide) record and no dummy instruction must not move the counter at
          // all, and both readings of the RTL agree on that, so this row is always on.
          if (recs == 0 && !win[k].dummies && delta != 0) begin
            miss_bound++;
            `uvm_error("ctr_hpm_bound", $sformatf("mhpmcounter%0d advanced %0d with no %s record in the window and dummy instructions off: read %08h -> %08h, cycles %0d..%0d, order %0d",
                                                  k + 3, delta, what, win[k].base, t.rd_wdata, lo, hi, t.order))
          end else if (recs > 0 || win[k].dummies) begin
            // The documentation's bound is the tighter of two sound ceilings. The first is the instruction's
            // own latency: a multiply stalls at most GEN_MUL_WAIT_MAX_CYCLES and a divide at most
            // GEN_DIV_WAIT_MAX_CYCLES, both derived from the multdiv FSM. The second is the window's free
            // cycles: a cycle in which a memory response was outstanding cannot be a wait cycle of the
            // multiply, because the multiply has not started then (rtl/ibex_id_stage.sv:866-869 advances the
            // state only under instr_executing, which carries the outstanding-access term that :1054-1057
            // leaves out of instr_executing_spec). This RTL counts the deferred-start cycles anyway (bug
            // candidate B17) and counts the wait cycles of its own dummy multiplies and divides (bug
            // candidate B7); neither is derivable from the record stream, so the knob decides, and the
            // accommodation is counted only here, where the RTL actually exceeded the documented bound.
            int unsigned per_rec = recs * ((k == GEN_CTR_MULWAIT) ? GEN_MUL_WAIT_MAX_CYCLES : GEN_DIV_WAIT_MAX_CYCLES);
            int unsigned doc_ceil = (per_rec < free) ? per_rec : free;
            string note = "";
            if (win[k].dummies) note = " (dummy instructions were enabled in this window)";
            if (delta > doc_ceil + GEN_RVFI_ID_EXIT_OFFSET) begin
              if (cfg.ctr_rtl_wait_cycles) begin
                if (win[k].dummies) acc_b7_dummy++; else acc_b17_wait++;
              end else begin
                miss_bound++;
                `uvm_error("ctr_hpm_bound", $sformatf("mhpmcounter%0d advanced %0d, at most %0d documented (%0d %s record(s) at %0d cycles each, and %0d of the window's %0d cycles had a data access outstanding leaving %0d free)%s: read %08h -> %08h, cycles %0d..%0d, order %0d",
                                                      k + 3, delta, doc_ceil, recs, what,
                                                      (k == GEN_CTR_MULWAIT) ? GEN_MUL_WAIT_MAX_CYCLES : GEN_DIV_WAIT_MAX_CYCLES,
                                                      busy, span, free, note,
                                                      win[k].base, t.rd_wdata, lo, hi, t.order))
              end
            end
          end
        end
      end

      if (exact_on() && (k == GEN_CTR_JUMPS || k == GEN_CTR_BRANCHES || k == GEN_CTR_TAKEN)) begin
        // counter 8 gains one per cycle a conditional branch waits in decode behind an outstanding write-back
        // access (bug candidate B17), and the waiting cycles are not derivable from the record stream, so a
        // window that held any data access is bounded rather than predicted unless the knob asks otherwise
        as_bound = win[k].memtrap || (k == GEN_CTR_BRANCHES && win[k].mem_rec && cfg.ctr_rtl_branches_wait);
        if (as_bound) begin
          string why = ", a data access in the window";
          if (win[k].memtrap) why = ", a memory-access trap in the window";
          if (k == GEN_CTR_BRANCHES && win[k].mem_rec && cfg.ctr_rtl_branches_wait && delta != win[k].owed) acc_b17_branch++;
          judged_bound++;
          ceil = win[k].owed + span + GEN_RVFI_ID_EXIT_OFFSET;
          if (delta < win[k].owed || delta > ceil) begin
            miss_exact++;
            `uvm_error("ctr_hpm_exact", $sformatf("mhpmcounter%0d advanced %0d, outside [%0d, %0d] (%0d predicted events over %0d cycles%s): read %08h -> %08h, cycles %0d..%0d, order %0d",
                                                  k + 3, delta, win[k].owed, ceil, win[k].owed, span, why,
                                                  win[k].base, t.rd_wdata, lo, hi, t.order))
          end
        end else begin
          judged_exact++;
          if (delta != win[k].owed) begin
            miss_exact++;
            `uvm_error("ctr_hpm_exact", $sformatf("mhpmcounter%0d advanced %0d, %0d predicted: read %08h -> %08h, cycles %0d..%0d, order %0d",
                                                  k + 3, delta, win[k].owed, win[k].base, t.rd_wdata, lo, hi, t.order))
          end
        end
      end
    endfunction

    function void report_phase(uvm_phase phase);
      `uvm_info("GEN_CTR", $sformatf("counter model: windows exact=%0d bound=%0d unjudged(write)=%0d unjudged(inhibit)=%0d misses exact=%0d bound=%0d",
                judged_exact, judged_bound, unjudged_write, unjudged_inhibit, miss_exact, miss_bound), UVM_LOW)
      `uvm_info("GEN_CTR", $sformatf("counter model accommodations (windows where the RTL differed from the documentation and the knob accepted it): B20 fence.i=%0d B11 dit=%0d B17 counter8=%0d B17 counter11/12=%0d B7 dummy=%0d; records fence.i=%0d branch-under-dit=%0d multiply=%0d divide=%0d",
                acc_b20_fencei, acc_b11_dit, acc_b17_branch, acc_b17_wait, acc_b7_dummy, rec_fencei, rec_dit_branch, rec_mul, rec_div), UVM_LOW)
      `uvm_info("GEN_CTR", $sformatf("counter model knobs (1 follows the RTL, 0 the documentation): jumps_fencei=%0b taken_dit=%0b branches_wait=%0b wait_cycles=%0b",
                cfg.ctr_rtl_jumps_fencei, cfg.ctr_rtl_taken_dit, cfg.ctr_rtl_branches_wait, cfg.ctr_rtl_wait_cycles), UVM_LOW)
    endfunction
  endclass
endpackage
