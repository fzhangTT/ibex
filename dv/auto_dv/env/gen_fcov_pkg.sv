// gen_fcov_pkg: functional coverage sampled from TB-side facts: the RVFI record (gen_isa_cov, the plan's covergroups rendered
// in gen_fcov_groups.svh) and the witness command. CG-WIT-001 (gen_wit_cycle_clause_cg): one bin per marked
// test-plan item, sampled by the COV_WITNESS bridge command a test's epilogue issues for a fire-check whose cycle clause held
// (dv/auto_dv/docs/gen_fcov_plan.md, WIT). The dispatcher refuses an index outside the list and an item of another test's
// group (arg1); the peek word returns the distinct bins hit as the covergroup itself counts them.
package gen_fcov_pkg;
  import uvm_pkg::*;
  `include "uvm_macros.svh"
  import gen_tb_pkg::*;
  import gen_cfg_pkg::*;
  import gen_rvfi_pkg::*;
  import gen_agents_pkg::*;
  import gen_isa_dpi_pkg::*;
  `include "gen_wit_bins.svh"
  `include "gen_fcov_groups.svh"

  // type-based: urg reports gen_wit_cycle_clause_cg.cp_clause.<bin>, the names the fcov manifests carry
  covergroup gen_wit_cycle_clause_cg with function sample(int unsigned idx);
    option.per_instance = 0;
    option.weight = 0;   // ledger bins, excluded from the score (Runtime excludes the group by name as the mechanism of record)
    cp_clause: coverpoint idx { `GEN_WIT_BINS }
  endgroup

  // the n-th token of a comma-separated list ("" past the end)
  function automatic string gen_csv_nth(string csv, int unsigned n);
    int unsigned k = 0, start = 0;
    for (int i = 0; i <= csv.len(); i++) begin
      if (i == csv.len() || csv[i] == ",") begin
        if (k == n) return csv.substr(start, i - 1);
        k++; start = i + 1;
      end
    end
    return "";
  endfunction

  class gen_wit_cov extends uvm_component;
    `uvm_component_utils(gen_wit_cov)
    gen_env_cfg cfg;
    gen_wit_cycle_clause_cg cg;
    int unsigned witnessed = 0, foreign = 0, out_of_range = 0;
    bit hit [GEN_WITNESS_COUNT];
    function new(string name, uvm_component parent);
      super.new(name, parent);
      foreach (hit[i]) hit[i] = 1'b0;
    endfunction
    function void build_phase(uvm_phase phase);
      super.build_phase(phase);
      if (!uvm_config_db#(gen_env_cfg)::get(this, "", "cfg", cfg)) `uvm_fatal("GEN_WIT", "cfg not in uvm_config_db")
      if (cfg.fcov_en) cg = new();
    endfunction
    // distinct bins hit: the covergroup's own count when it exists (so a dropped sample shows), the bookkeeping otherwise
    function int unsigned distinct();
      int unsigned n = 0;
      if (cg != null) return int'(cg.cp_clause.get_coverage() * GEN_WITNESS_COUNT / 100.0);   // the int cast rounds to nearest
      foreach (hit[i]) if (hit[i]) n++;
      return n;
    endfunction
    function int unsigned witness(int unsigned idx, int unsigned owner);
      if (idx >= GEN_WITNESS_COUNT) begin
        out_of_range++;
        `uvm_error("GEN_CMD_DISPATCH", $sformatf("COV_WITNESS index %0d is outside the witness list (%0d rows)", idx, GEN_WITNESS_COUNT))
        return distinct();
      end
      if (GEN_WITNESS_GROUP_OF[idx] != owner) begin
        foreign++;
        `uvm_error("GEN_WITNESS_FOREIGN", $sformatf("COV_WITNESS %s (index %0d) belongs to %s, issued by %s", gen_csv_nth(GEN_WITNESS_TP_NAMES, idx), idx,
                   gen_csv_nth(GEN_WITNESS_GROUP_NAMES, GEN_WITNESS_GROUP_OF[idx]), owner < GEN_WITNESS_GROUP_COUNT ? gen_csv_nth(GEN_WITNESS_GROUP_NAMES, owner) : "an unknown group"))
        return distinct();
      end
      witnessed++; hit[idx] = 1'b1;
      if (cg != null) cg.sample(idx);
      return distinct();
    endfunction
    function void report_phase(uvm_phase phase);
      int unsigned n = 0;
      foreach (hit[i]) if (hit[i]) n++;
      `uvm_info("GEN_WIT", $sformatf("witnesses=%0d distinct=%0d covergroup=%0d foreign=%0d out_of_range=%0d", witnessed, n, cg != null ? distinct() : 0, foreign, out_of_range), UVM_LOW)
      if (cg != null && distinct() != n)
        `uvm_error("wit_referee", $sformatf("the covergroup counts %0d distinct bins, the dispatcher accepted %0d distinct witnesses", distinct(), n))
    endfunction
  endclass

  // The RVFI sampler of the plan's instruction covergroups (T-205). Every classifier is a partition of a record field the plan
  // names; the sample condition is the plan's (decoded encoding, rvfi_trap == 0). RVFI reports a compressed instruction in its
  // 16-bit form, so c.mul is decoded from it (rtl/ibex_core.sv:2263-2267); rd_wdata is forced to 0 on an rd = x0 record.
  `uvm_analysis_imp_decl(_dbus)
  `uvm_analysis_imp_decl(_ibus)
  `uvm_analysis_imp_decl(_key)
  `uvm_analysis_imp_decl(_irqe)
  `uvm_analysis_imp_decl(_dbge)
  `uvm_analysis_imp_decl(_mst)
  class gen_isa_cov extends uvm_subscriber #(gen_rvfi_txn);
    `uvm_component_utils(gen_isa_cov)
    gen_env_cfg cfg;
    gen_mul_ops_cg     mul_cg;
    gen_div_ops_cg     div_cg;
    gen_isa_alu_reg_cg alu_cg;
    gen_bit_zba_zbb_ops_cg bit_cg;
    gen_isa_alu_imm_cg imm_cg;
    gen_isa_shift_cg   sh_cg;
    gen_bit_count_cg   cnt_cg;
    gen_cmp_zca_cg     zca_cg;
    gen_cmp_zcmp_pushpop_cg zcmp_cg;
    gen_cmp_zcmp_mv_cg mv_cg;
    gen_csr_trap_setup_warl_cg csr_cg;
    gen_isa_branch_cg  br_cg;
    gen_bit_sbit_cg    sbit_cg;
    gen_cmp_zcb_cg     zcb_cg;
    gen_rvfi_record_cg rec_cg;       // Slice A (T-205): every record
    gen_mul_timing_cg  mt_cg;        // the multiply's timing neighbours
    gen_rst_boot_cg    rst_cg;       // one sample per reset
    gen_ic_ecc_cg      ic_ecc_cg;    // CG-IC-006: one sample per closed icache-RAM ECC injection, one per drained never-written read
    int unsigned       n_ic_ecc = 0;
    gen_sec_ctrl_inputs_cg sec_cg;   // the security-input events
    gen_cmp_zcmp_hazard_cg hz_cg;    // the Zcmp neighbour patterns (CG-CMP-009)
    gen_isa_lui_auipc_cg lu_cg;      // U-type immediates, PC regions, the auipc wrap (CG-ISA-004)
    gen_isa_hint_x0_cg hx_cg;        // x0-destination writers and the read after them (CG-ISA-005)
    gen_isa_jump_cg jp_cg;           // jumps: offsets, link, targets (CG-ISA-006)
    gen_div_timing_cg dt_cg;         // the divider's timing neighbours and the mid-op events (CG-MUL-004)
    gen_cmp_imm_edges_cg ie_cg;      // Zca immediate extremes (CG-CMP-002)
    // CG-BIT-006 binv_twice: the record before was binv / binvi, with its rd and index
    bit sb_prev_binv = 0; logic [4:0] sb_prev_rd, sb_prev_idx; int unsigned n_sbit = 0, n_zcb = 0;
    // CG-CMP-007 move pair: form, register fields, the two source values, the neighbour facts; sampled once the next record is known
    int zp_mv = -1, mv_r1, mv_r2, mv_hz, mv_prev; logic [31:0] mv_src1, mv_src2; bit mv_ok, mv_pend = 0; int mv_v [8];
    // the registers written and the load fact of the instruction in progress and of the one before it (an expansion is one instruction)
    logic [31:0] cur_wr = '0, prev_wr = '0; bit cur_ld = 0, prev_ld = 0; int cur_mv = -1, prev_mv = -1;
    // CG-CSR-002 pairs per tracked CSR: the open write (op, operand, rd, effective value) and the standing value of the last read-back
    bit csr_pend [8], csr_eff_ok [8], csr_shadow_ok [8]; int csr_op [8], csr_rd [8], csr_gate [8]; logic [31:0] csr_wval [8], csr_eff [8], csr_shadow [8];
    virtual gen_ctrl_if ctrl_vif;   // mcounteren_writable_i as driven when a CSR write record arrives (cp_mcen_gate)
    virtual gen_irq_if irq_vif; virtual gen_dbg_if dbg_vif;   // the pins pending at the reset release
    virtual gen_misc_if misc_vif;   // core_busy, the only pin this subscriber reads from the misc bundle
    int unsigned n_br = 0, n_mv = 0, n_csr_pairs = 0, n_csr_wr = 0, n_csr_replaced = 0;
    int unsigned n_mv_miss = 0, ut_mv_miss_expected = 0;   // legal move pairs whose micro-ops did not match the expansion (the self-test's own excluded)
    // counters and last-sample copies the unit test reads (FCOV_QUERY / FCOV_SELFTEST)
    int unsigned n_slt_eq = 0, n_cnt_res_na = 0; int ut_last_zcmp [13], ut_last_imm [8], ut_last_cnt [5], ut_last_mv [8];
    // CG-CMP-006 sequence collector: one cm.push / cm.pop / cm.popret / cm.popretz from its first micro-op record to its last
    bit zp_in = 0, zp_sp_valid, zp_order_ok, zp_tags_ok; int zp_kind, zp_rlist, zp_spimm, zp_n, zp_adj, zp_count, zp_mem_k, zp_ret_align;
    logic [31:0] zp_pc, zp_sp, zp_mhpm10_first; logic [4:0] zp_prev_reg; int unsigned n_zcmp = 0, n_zcmp_abandoned = 0;
    // the sequence's sample waits for the record after it: that record's mhpmcounter10 counts through the last micro-op, the first micro-op's counts through the instruction before the sequence, so their difference is the cm.*'s own count
    bit zcmp_pend = 0; int zcmp_v [13]; int unsigned n_zcmp_uop_no = 0, n_zcmp_order_no = 0, n_zcmp_tags_no = 0, n_zcmp_minstret_no = 0;
    // data-bus responses seen (cycle of rvalid, latency after grant): cp_dmem_delay classifies the responses inside the sequence's window
    int unsigned dlat_cyc [$], dlat_lat [$], dlat_gnt [$]; logic [31:0] dlat_addr [$]; int unsigned prev_rec_cycle = 0, cur_rec_cycle = 0, zp_win_start;
    // CG-CMP-009 state: the neighbour facts of a sequence (the instruction before it, the sequence before it, the fall-through halfword,
    // the store record before it, the micro-op cycles) and the pended return-target check
    int unsigned n_hz = 0; int ut_last_hz [7]; logic [31:0] zp_load_addr [$]; int prev_seq_kind = -1, hz_b2b_prev = -1; bit hz_prev_st_valid = 0; logic [31:0] hz_prev_st_addr;
    logic [31:0] hz_prev_wr; bit hz_prev_ld; int unsigned zp_last_uop_cycle, zp_ra_load_cycle; bit zp_uop_stall; logic [31:0] zp_ret_target, zp_ra_addr;
    bit hz_pend = 0; int hz_pend_kind; int hz_pend_v [7]; int unsigned hz_pend_cycle;
    // Slice A state: the previous record (continuity, gap, the multiply's neighbour), the pending multiply (its successor decides
    // cp_next_dep), the recent fetches (fetch-stall), the reset-release facts and the security-input trackers
    gen_rvfi_txn prev_t, last_t; bit have_prev = 0, have_last = 0; int unsigned n_rec = 0, n_mt = 0, n_rst = 0, n_sec = 0;   // last_t: the record before the one write() is handling
    bit mt_pend = 0; int mt_v [7]; logic [4:0] mt_rd; int ut_last_rec [14], ut_last_mt [7], ut_last_rst [8], ut_last_sec [11];
    logic [31:0] ib_addr [$]; int unsigned ib_rv [$]; int unsigned boot_to_req = 0; bit boot_to_req_seen = 0;
    int rst_fetch_en = -1, rst_pending = -1; bit rst_release_seen = 0, rst_sampled = 0; logic [31:0] hart_id_v = 0;
    bit icache_en_tracked = 0; bit fencei_pending = 0; bit mcen_pend = 0; logic [31:0] mcen_old, mcen_new; int mcen_pin_cls = -1;   // icache_en_tracked: cpuctrlsts.icache_enable resets to 0
    // Slice B state: the pending x0-writer (its successor decides cp_x0_read), the pending divide (its successor decides cp_next and the
    // irq latency), the asserted-edge events of the irq and debug drivers (cycle, cp_event_mid bin) and cpuctrlsts.data_ind_timing as written
    bit hx_pend = 0; int hx_v [3]; bit dt_pend = 0, dt_irq_seen = 0; int dt_v [10]; logic [4:0] dt_rd; int unsigned dt_irq_cycle;
    int unsigned ev_cyc [$]; int ev_kind [$]; bit dit_tracked = 0;   // dit_tracked: cpuctrlsts.data_ind_timing resets to 0
    int unsigned n_lu = 0, n_hx = 0, n_jp = 0, n_dt = 0, n_ie = 0; int ut_last_lu [6], ut_last_hx [3], ut_last_jp [10], ut_last_dt [10], ut_last_ie [13];
    uvm_analysis_imp_irqe #(gen_irq_evt, gen_isa_cov) irq_imp;   // the irq driver's line changes
    uvm_analysis_imp_dbge #(gen_irq_evt, gen_isa_cov) dbg_imp;   // the debug driver's request changes (the same item: changed[0] = req)
    uvm_analysis_imp_mst #(gen_model_state, gen_isa_cov) state_imp;   // the model of record per retired record
    uvm_analysis_imp_dbus #(gen_bus_txn, gen_isa_cov) dbus_imp;
    uvm_analysis_imp_ibus #(gen_bus_txn, gen_isa_cov) ibus_imp;
    uvm_analysis_imp_key #(gen_key_evt, gen_isa_cov) key_imp;
    int unsigned n_mul = 0, n_div = 0, n_alu = 0, n_bit = 0, n_imm = 0, n_sh = 0, n_cnt = 0, n_zca = 0, n_zca32 = 0;
    // the pending 16-bit record of CG-CMP-001: sampled when the next record tells the next instruction's length
    bit zca_pend = 0; int zca_v [7];
    function new(string name, uvm_component parent); super.new(name, parent); dbus_imp = new("dbus_imp", this); ibus_imp = new("ibus_imp", this); key_imp = new("key_imp", this); irq_imp = new("irq_imp", this); dbg_imp = new("dbg_imp", this); state_imp = new("state_imp", this); endfunction
    // ---- IRQ step 1: CG-IRQ-001 gen_irq_entry_cg ---------------------------------------------------------
    // The entry is a retired record with rvfi_intr; its facts come from the record itself and from the model of
    // record the scoreboard publishes (gen_model_state), which carries mcause's cause, mstatus, mepc and mie as
    // of that record. The pin levels come from the irq agent's own events, kept here per line.
    gen_irq_entry_cg irq_entry_cg;
    int unsigned n_irq_entry = 0;
    int unsigned n_irq_mret_masked = 0;   // mrets that mask a pending enabled line: the one case with no bin
    int unsigned n_irq_mret_entry = 0, n_irq_mret_newbin_entry = 0;
    bit          prev_trapped = 0;   // the previous record trapped, so an entry cleared MIE inside it
    bit irq_view_ok = 0;   // this record had a published view sample
    int unsigned n_irq_entry_rel = 0;   // second samples carrying only the pre/post mip relation
    gen_rvfi_txn irq_last_t; bit irq_have_t = 0;      // the record the state below belongs to
    logic [31:0] irq_prev_pc = '0, irq_prev_insn = '0; bit irq_have_prev_pc = 0, irq_prev_was_zcmp = 0;

    // the plan's cp_line: an ordinary line keeps its index (0 sw, 1 timer, 2 ext, 3+i fast[i]); an NMI is its own
    function int irq_line_bin(gen_model_state st, gen_rvfi_txn t);
      int line;
      if (t != null && t.ext_nmi_int) return GEN_FC_IRQ_ENTRY_CP_LINE_NMI_INT;
      if (st.entry_cause == int'(ibex_pkg::ExcCauseIrqNm.lower_cause)) return GEN_FC_IRQ_ENTRY_CP_LINE_NMI_EXT;
      line = gen_irq_line_of_cause(st.entry_cause);
      if (line < 0) return -1;
      if (line == 0) return GEN_FC_IRQ_ENTRY_CP_LINE_SOFTWARE;
      if (line == 1) return GEN_FC_IRQ_ENTRY_CP_LINE_TIMER;
      if (line == 2) return GEN_FC_IRQ_ENTRY_CP_LINE_EXTERNAL;
      return GEN_FC_IRQ_ENTRY_CP_LINE_FAST + (line - 3);
    endfunction

    // cp_others: the other mie-enabled lines at the entry, against the entry's own line
    function int irq_others_bin(gen_model_state st, int this_line);
      bit any_enabled = 0, any_pending_lower = 0;
      logic [18:0] pins;
      if (!irq_view_ok) return -1;   // no published pins for this cycle: judge nothing rather than judge zero
      pins = irq_pins_at(irq_commit_cycle(st));   // the pins as of the commit, not the level now
      for (int l = 0; l < 18; l++) begin
        if (l == this_line) continue;
        if (!st.mie[gen_irq_mie_bit(l)]) continue;
        any_enabled = 1;
        if (pins[l] && this_line >= 0 && gen_irq_rank(l) > gen_irq_rank(this_line)) any_pending_lower = 1;
      end
      if (any_pending_lower) return GEN_FC_IRQ_ENTRY_CP_OTHERS_OTHERS_PENDING_LOWER;
      return any_enabled ? GEN_FC_IRQ_ENTRY_CP_OTHERS_OTHERS_ENABLED_IDLE
                         : GEN_FC_IRQ_ENTRY_CP_OTHERS_ONLY_THIS;
    endfunction

    // cp_mepc_src: what mepc points at, decided against the record before the entry
    function int irq_mepc_bin(gen_model_state st);
      logic [31:0] seq_pc;
      if (!irq_have_prev_pc) return (st.mepc == gen_reset_pc(cfg.boot_addr)) ? GEN_FC_IRQ_ENTRY_CP_MEPC_SRC_BOOT_PC : -1;
      seq_pc = irq_prev_pc + ((irq_prev_insn[1:0] == 2'b11) ? 32'd4 : 32'd2);
      if (irq_prev_was_zcmp) return GEN_FC_IRQ_ENTRY_CP_MEPC_SRC_CM_PC;
      if (irq_prev_insn == GEN_RV32_WFI) return GEN_FC_IRQ_ENTRY_CP_MEPC_SRC_WFI_NEXT;
      if (irq_prev_insn == GEN_RV32_MRET) return GEN_FC_IRQ_ENTRY_CP_MEPC_SRC_MRET_TARGET;
      if (irq_prev_insn == GEN_RV32_DRET) return GEN_FC_IRQ_ENTRY_CP_MEPC_SRC_DRET_TARGET;
      if (st.mepc == seq_pc) return GEN_FC_IRQ_ENTRY_CP_MEPC_SRC_SEQUENTIAL;
      if (irq_prev_insn[6:0] == ibex_pkg::OPCODE_BRANCH) return GEN_FC_IRQ_ENTRY_CP_MEPC_SRC_BRANCH_TARGET;
      if (irq_prev_insn[6:0] inside {ibex_pkg::OPCODE_JAL, ibex_pkg::OPCODE_JALR})
        return GEN_FC_IRQ_ENTRY_CP_MEPC_SRC_JUMP_TARGET;
      return (st.mepc == gen_reset_pc(cfg.boot_addr)) ? GEN_FC_IRQ_ENTRY_CP_MEPC_SRC_BOOT_PC : -1;
    endfunction

    // cp_rvfi_marks: the record's own interrupt markers, in the plan's order of preference
    function int irq_marks_bin(gen_rvfi_txn t);
      if (t == null) return -1;
      if (t.ext_nmi_int) return GEN_FC_IRQ_ENTRY_CP_RVFI_MARKS_NMI_INT_FLAG;
      if (t.ext_nmi) return GEN_FC_IRQ_ENTRY_CP_RVFI_MARKS_NMI_FLAG;
      if (t.ext_pre_mip != 0) return GEN_FC_IRQ_ENTRY_CP_RVFI_MARKS_INTR_WITH_PRE_MIP;
      if (t.ext_irq_valid) return GEN_FC_IRQ_ENTRY_CP_RVFI_MARKS_IRQ_VALID_LEVEL;
      return GEN_FC_IRQ_ENTRY_CP_RVFI_MARKS_IRQ_VALID_ABSENT;
    endfunction

    // one entry per interrupt-entry record
    function void irq_entry_sample(gen_model_state st);
      gen_rvfi_txn t = (irq_have_t && irq_last_t != null && irq_last_t.order == st.order) ? irq_last_t : null;
      int v_line = irq_line_bin(st, t);
      int v_priv = (st.mstatus[ibex_pkg::CSR_MSTATUS_MPP_BIT_HIGH:ibex_pkg::CSR_MSTATUS_MPP_BIT_LOW] == 2'b11) ? GEN_FC_IRQ_ENTRY_CP_PRIV_PRE_M :
                   (st.mstatus[ibex_pkg::CSR_MSTATUS_MPP_BIT_HIGH:ibex_pkg::CSR_MSTATUS_MPP_BIT_LOW] == 2'b00) ? GEN_FC_IRQ_ENTRY_CP_PRIV_PRE_U : -1;
      int raw_line = gen_irq_line_of_cause(st.entry_cause);
      if (irq_entry_cg == null) return;
      irq_entry_cg.sample(v_line,
                          v_priv,
                          st.mstatus[ibex_pkg::CSR_MSTATUS_MPIE_BIT] ? GEN_FC_IRQ_ENTRY_CP_MIE_GLOBAL_MIE1    // MPIE holds MIE as it was
                                        : GEN_FC_IRQ_ENTRY_CP_MIE_GLOBAL_MIE0,
                          irq_others_bin(st, raw_line),
                          irq_mepc_bin(st),
                          -1,     // cp_u_path and cp_u_pending_at_return need the return into U, which the
                          -1,     // handler-flow group's stack will carry: filled when CG-IRQ-005 lands
                          irq_marks_bin(t));
      n_irq_entry++;
      // cp_rvfi_marks is a first-match chain, so its two mip-relation bins could never be returned. The
      // relation is a fact of its own: a second sample carries it under the same line, which is what
      // cr_line_marks.timer_pre_post_mip_differ needs to see.
      if (t != null) begin
        int v_rel = (t.ext_pre_mip == t.ext_post_mip) ? GEN_FC_IRQ_ENTRY_CP_RVFI_MARKS_PRE_POST_MIP_EQUAL
                                                      : GEN_FC_IRQ_ENTRY_CP_RVFI_MARKS_PRE_POST_MIP_DIFFER;
        irq_entry_cg.sample(v_line, -1, -1, -1, -1, -1, -1, v_rel);
        n_irq_entry_rel++;
      end
    endfunction

    // the model of record for each retired record, published by the scoreboard
    function void write_mst(gen_model_state st);
      gen_rvfi_txn t = (irq_have_t && irq_last_t != null && irq_last_t.order == st.order) ? irq_last_t : null;
      // several classifiers read the published view, so it is decided ONCE here, before the first of them,
      // and a miss is counted once per record rather than once per accessor call
      irq_view_ok = irq_view_has(irq_commit_cycle(st));
      if (!irq_view_ok) n_irq_view_miss++;
      if (st.is_intr) irq_entry_sample(st);
      irq_pend_record(st, t);
      irq_prev_pc = st.pc_rdata; irq_prev_insn = st.insn; irq_have_prev_pc = 1;
      irq_prev_was_zcmp = (t != null) ? t.ext_exp_valid : 1'b0;
      irq_st = st; irq_have_st = 1;   // the state a cycle event between records is judged against
    endfunction

    // ---- IRQ step 1: CG-IRQ-003 gen_irq_pending_model_cg -------------------------------------------------
    // Three sample events, not one per record: ev_edge is a CYCLE event (a pin change, or the commit of a
    // retired mie write), ev_access and ev_mie are record events. Each entry point fills its own coverpoints
    // and passes -1 for the rest, so no coverpoint is given a value its iff clause excludes.
    // The pending state is the TB's own model of irq_pending_o (a pin high whose mie bit is set): comparing
    // the DUT's output against that model is the irq_pending checker's job, and modelling it here keeps a DUT
    // fault out of the bins. Pin levels and mie are kept by cycle so a record event is judged at its commit
    // cycle, which is GEN_CSR_WRITE_TO_RVFI_OFFSET cycles before the record that reports it.
    gen_irq_pending_model_cg irq_pend_cg;
    int unsigned n_irq_edge = 0, n_irq_access = 0, n_irq_mie = 0;
    int unsigned n_irq_view_miss = 0;   // record events whose cycle had aged out of the published view
    gen_model_state irq_st; bit irq_have_st = 0;      // the last retired record's model state
    bit irq_nmi_mode = 0; int irq_nmi_depth = 0;      // NMI mode, tracked as gen_irq_checker tracks it
    logic [31:0] irq_mie_prev = '0, irq_mstatus_prev = '0;

    // the irq checker's own sampled view of a cycle (gen_tb_pkg::gen_irq_view), so this covergroup judges a
    // record's commit cycle from the SAME sample the checker judges it from, with no offset arithmetic here
    function logic [31:0] irq_mie_at(int unsigned c);
      return gen_irq_view::mie_at(c);
    endfunction
    function logic [18:0] irq_pins_at(int unsigned c);
      logic [18:0] pins; bit pending;
      if (gen_irq_view::sample_at(c, pins, pending)) return pins;
      return '0;   // callers check irq_view_ok before judging: zero pins is not a reading, and the miss is
                   // counted once per record by write_mst rather than once per call from here
    endfunction
    function bit irq_view_has(int unsigned c);
      logic [18:0] pins; bit pending;
      return gen_irq_view::sample_at(c, pins, pending);
    endfunction
    // the model of irq_pending_o: the nm line is not in mie/mip and never contributes
    function bit irq_pending_model(logic [18:0] pins, logic [31:0] mie);
      for (int i = 0; i < 18; i++) if (pins[i] && mie[gen_irq_mie_bit(i)]) return 1'b1;
      return 1'b0;
    endfunction
    function logic [31:0] irq_mie_warl();
      return GEN_IRQ_FAST_MASK | (32'h1 << ibex_pkg::CSR_MSIX_BIT)
                               | (32'h1 << ibex_pkg::CSR_MTIX_BIT)
                               | (32'h1 << ibex_pkg::CSR_MEIX_BIT);
    endfunction
    function int unsigned irq_commit_cycle(gen_model_state st);
      return (st.cycle >= GEN_CSR_WRITE_TO_RVFI_OFFSET) ? st.cycle - GEN_CSR_WRITE_TO_RVFI_OFFSET + 1 : 0;
    endfunction

    // cp_state: debug and NMI mode outrank the rest. Sleep is the only class that is not a record fact, so it
    // is read from core_busy (mubi-off is the controller's WAIT_SLEEP/SLEEP, rtl/ibex_controller.sv:598,:619)
    // and only for a cycle event, where the read is of that cycle.
    function int irq_state_bin(gen_model_state st, bit cycle_event);
      if (st != null && st.debug_mode) return GEN_FC_IRQ_PENDING_MODEL_CP_STATE_DEBUG_MODE;
      if (irq_nmi_mode) return GEN_FC_IRQ_PENDING_MODEL_CP_STATE_NMI_MODE;
      if (cycle_event && misc_vif != null && misc_vif.core_busy == ibex_pkg::IbexMuBiOff)
        return GEN_FC_IRQ_PENDING_MODEL_CP_STATE_SLEEP;
      if (st == null) return -1;
      if (st.dcsr[2]) return GEN_FC_IRQ_PENDING_MODEL_CP_STATE_STEP;   // dcsr.step (rtl/ibex_cs_registers.sv:231)
      if (st.prv == ibex_pkg::PRIV_LVL_U) return GEN_FC_IRQ_PENDING_MODEL_CP_STATE_U_MODE;
      return st.mstatus[ibex_pkg::CSR_MSTATUS_MIE_BIT] ? GEN_FC_IRQ_PENDING_MODEL_CP_STATE_MIE1_M
                                                       : GEN_FC_IRQ_PENDING_MODEL_CP_STATE_MIE0_M;
    endfunction

    // cp_line_kind: the plan's thirds over the fast lines, sized from the mie fast field itself
    function int irq_kind_bin(int line);
      int fw = ibex_pkg::CSR_MFIX_BIT_HIGH - ibex_pkg::CSR_MFIX_BIT_LOW + 1;
      if (line == 0) return GEN_FC_IRQ_PENDING_MODEL_CP_LINE_KIND_SOFTWARE;
      if (line == 1) return GEN_FC_IRQ_PENDING_MODEL_CP_LINE_KIND_TIMER;
      if (line == 2) return GEN_FC_IRQ_PENDING_MODEL_CP_LINE_KIND_EXTERNAL;
      if (line < 3 || line > 17) return -1;                        // the nm line has no mie/mip class
      if ((line - 3) * 3 < fw) return GEN_FC_IRQ_PENDING_MODEL_CP_LINE_KIND_FAST_LOW;
      if ((line - 3) * 3 < 2 * fw) return GEN_FC_IRQ_PENDING_MODEL_CP_LINE_KIND_FAST_MID;
      return GEN_FC_IRQ_PENDING_MODEL_CP_LINE_KIND_FAST_HIGH;
    endfunction

    // ev_edge, pin side: one sample per changed line, classified at the event's own cycle. An edge whose class
    // the plan does not name (a disabled line falling) samples nothing rather than a bin it did not earn.
    function void irq_edge_pins(gen_irq_evt e);
      logic [18:0] pins_pre = e.lines_after ^ e.changed;
      logic [31:0] mie = irq_mie_at(e.cycle);
      bit pend_before = irq_pending_model(pins_pre, mie);
      bit pend_after  = irq_pending_model(e.lines_after, mie);
      if (irq_pend_cg == null) return;
      for (int l = 0; l < 19; l++) begin
        int v_tr = -1;
        if (!e.changed[l]) continue;
        if (l == 18) begin
          if (e.level && e.changed[17:0] == 0) v_tr = GEN_FC_IRQ_PENDING_MODEL_CP_TRANSITION_NMI_ONLY_RISE;
        end else if (e.level) begin
          v_tr = !mie[gen_irq_mie_bit(l)] ? GEN_FC_IRQ_PENDING_MODEL_CP_TRANSITION_RISE_DISABLED :
                 pend_before              ? GEN_FC_IRQ_PENDING_MODEL_CP_TRANSITION_RISE_ENABLED_OTHER_HIGH :
                                            GEN_FC_IRQ_PENDING_MODEL_CP_TRANSITION_RISE_ENABLED;
        end else if (mie[gen_irq_mie_bit(l)]) begin
          v_tr = pend_after ? GEN_FC_IRQ_PENDING_MODEL_CP_TRANSITION_FALL_NOT_LAST
                            : GEN_FC_IRQ_PENDING_MODEL_CP_TRANSITION_FALL_LAST;
        end
        if (v_tr < 0) continue;
        irq_pend_cg.sample(v_tr, irq_state_bin(irq_have_st ? irq_st : null, 1'b1), irq_kind_bin(l), -1, -1, -1);
        n_irq_edge++;
      end
    endfunction

    // ev_edge, mie-write side: the write commits before its record, so the pins are read at the commit cycle
    function void irq_edge_mie(gen_model_state st);
      logic [18:0] pins = irq_pins_at(irq_commit_cycle(st));
      bit pend_before = irq_pending_model(pins, irq_mie_prev);
      if (irq_pend_cg == null) return;
      for (int l = 0; l < 18; l++) begin
        int b = gen_irq_mie_bit(l);
        int v_tr = -1;
        if (b < 0 || !pins[l] || irq_mie_prev[b] == st.mie[b]) continue;
        if (st.mie[b] && !pend_before) v_tr = GEN_FC_IRQ_PENDING_MODEL_CP_TRANSITION_MIE_SET_PIN_HIGH;
        else if (!st.mie[b])           v_tr = GEN_FC_IRQ_PENDING_MODEL_CP_TRANSITION_MIE_CLEAR_PIN_HIGH;
        if (v_tr < 0) continue;
        irq_pend_cg.sample(v_tr, irq_state_bin(st, 1'b0), irq_kind_bin(l), -1, -1, -1);
        n_irq_edge++;
      end
    endfunction

    // ev_access: a retired csr access to mip or mie. The class comes from the record's own instruction; the
    // read classes from mie and the pins as of the commit cycle; the mie write value from rs1_rdata (or the
    // immediate form's own field), which is the value the write presented, not what the WARL mask kept.
    function void irq_access_sample(gen_model_state st, gen_rvfi_txn t);
      logic [11:0] csr = st.insn[31:20];
      logic [2:0]  f3  = st.insn[14:12];
      logic [4:0]  rs1 = st.insn[19:15];
      bit is_csr = (st.insn[6:0] == 7'b1110011) && (f3 != 3'b000);
      bit reads_only = (f3[1:0] != 2'b01) && (rs1 == 5'd0);   // csrrs/csrrc with a zero source writes nothing
      logic [18:0] pins;
      logic [31:0] wdata;
      int v_mip = -1, v_mie = -1;
      if (!is_csr || irq_pend_cg == null) return;
      if (csr != ibex_pkg::CSR_MIP && csr != ibex_pkg::CSR_MIE) return;
      pins = irq_pins_at(irq_commit_cycle(st));
      if (csr == ibex_pkg::CSR_MIP) begin
        if (reads_only) begin
          bit any_high = 0, any_high_en = 0, any_high_dis = 0;
          for (int l = 0; l < 18; l++) if (pins[l]) begin
            any_high = 1;
            if (st.mie[gen_irq_mie_bit(l)]) any_high_en = 1; else any_high_dis = 1;
          end
          if (st.mie == 32'h0 && any_high)   v_mip = GEN_FC_IRQ_PENDING_MODEL_CP_MIP_ACCESS_READ_MIE0_PINS_HIGH;
          else if (any_high_en && any_high_dis) v_mip = GEN_FC_IRQ_PENDING_MODEL_CP_MIP_ACCESS_READ_PARTIAL_MIE;
          else if (!any_high)                v_mip = GEN_FC_IRQ_PENDING_MODEL_CP_MIP_ACCESS_READ_ALL_LOW;
        end else begin
          v_mip = (f3[1:0] == 2'b01) ? GEN_FC_IRQ_PENDING_MODEL_CP_MIP_ACCESS_WRITE_CSRRW_IGNORED :
                  (f3[1:0] == 2'b10) ? GEN_FC_IRQ_PENDING_MODEL_CP_MIP_ACCESS_WRITE_CSRRS_IGNORED :
                                       GEN_FC_IRQ_PENDING_MODEL_CP_MIP_ACCESS_WRITE_CSRRC_IGNORED;
        end
      end else if (!reads_only) begin
        if (!f3[2] && t == null) return;                      // the register form needs its record's rs1_rdata
        wdata = f3[2] ? {27'h0, rs1} : t.rs1_rdata;
        if (wdata == 32'hffffffff)            v_mie = GEN_FC_IRQ_PENDING_MODEL_CP_MIE_WRITE_ALL_ONES;
        else if (wdata == 32'h0)              v_mie = GEN_FC_IRQ_PENDING_MODEL_CP_MIE_WRITE_ZERO;
        else if ((wdata & ~irq_mie_warl()) != 0) v_mie = GEN_FC_IRQ_PENDING_MODEL_CP_MIE_WRITE_RANDOM_MASKED;
        else if ((wdata & ~GEN_IRQ_FAST_MASK) == 0) v_mie = GEN_FC_IRQ_PENDING_MODEL_CP_MIE_WRITE_FAST_ONLY;
      end
      if (v_mip < 0 && v_mie < 0) return;
      irq_pend_cg.sample(-1, irq_state_bin(st, 1'b0), -1, v_mip, v_mie, -1);
      n_irq_access++;
    endfunction

    // ev_mie: mstatus.MIE seen from a retired mstatus write or an mret, with the pending state at the commit
    // cycle. The mret arm samples on EVERY mret, not only one that changes MIE: the plan's mret_mpie0_pending
    // bin is an mret that leaves MIE at 0, which is not a change.
    function void irq_mie_global_sample(gen_model_state st);
      // An entry record's pre-state is what the ENTRY left, not the interrupted instruction's: a trap
      // clears MIE for a non-debug entry (rtl/ibex_cs_registers.sv:924, inside else if (!debug_mode_i) at
      // :918) and, for an rvfi_intr record, retires no record of its own, so the
      // previous record here is the instruction that was interrupted, whose MIE was necessarily set.
      // is_trap is NOT the same case: that record's own pre-state really is its predecessor's.
      // the entry's clear is guarded on !debug_mode_i in the RTL, so the term is carried here too. The
      // Critic proved a debug entry cannot carry rvfi_intr (it needs exc_pc_mux_id == EXC_PC_IRQ), so this
      // is hygiene: it matches the guard rather than relying on a reachability argument staying true.
      bit was  = (st.is_intr && !st.debug_mode) ? 1'b0 : irq_mstatus_prev[ibex_pkg::CSR_MSTATUS_MIE_BIT];
      bit now  = st.mstatus[ibex_pkg::CSR_MSTATUS_MIE_BIT];
      int unsigned c = irq_commit_cycle(st);
      bit pend = irq_pending_model(irq_pins_at(c), irq_mie_at(c));
      int v = -1;
      if (irq_pend_cg == null) return;
      if (st.is_mret) begin
        // an mret that itself TRAPPED did not perform the return, so its post-state is the entry's, not MPIE's
        if (!pend || st.prv != ibex_pkg::PRIV_LVL_M || st.is_trap) return;
        // Four combinations of MIE before and MPIE, keyed the way this coverpoint's other four bins are
        // keyed: edge direction crossed with pending. 0->1 is a set edge, 0->0 and 1->1 are not edges, and
        // 1->0 is a CLEAR edge that no bin names yet, so it must not fall into the stays-clear bin.
        v = (now && !was)  ? GEN_FC_IRQ_PENDING_MODEL_CP_MIE_GLOBAL_EDGE_MRET_MPIE1_PENDING
          : (!now && !was) ? GEN_FC_IRQ_PENDING_MODEL_CP_MIE_GLOBAL_EDGE_MRET_MPIE0_PENDING
          : (now && was)   ? GEN_FC_IRQ_PENDING_MODEL_CP_MIE_GLOBAL_EDGE_MRET_MIE1_MPIE1_PENDING
                           : -1;
        if (v < 0) n_irq_mret_masked++;   // the clear edge: an mret that masks a pending enabled line
        if (st.is_intr) n_irq_mret_entry++;   // an mret that IS a handler's first instruction
        // The invariant: nothing booked into the stays-set bin may follow an entry,
        // because an entry leaves MIE clear. It must witness BOTH routes, and the asymmetry is why one term
        // cannot: an EXCEPTION is taken BY an instruction, so its clear lands inside that instruction's own
        // published state and shows up as the PREVIOUS record having trapped; an INTERRUPT is taken BETWEEN
        // instructions, so its clear lands in no record at all and shows up only as THIS record's entry flag.
        // Keying on the entry flag alone made this counter blind to the first route by construction.
        if ((st.is_intr || prev_trapped) && v == GEN_FC_IRQ_PENDING_MODEL_CP_MIE_GLOBAL_EDGE_MRET_MIE1_MPIE1_PENDING)
          n_irq_mret_newbin_entry++;
      end else if (st.wrote_mstatus && was != now) begin
        v = now ? (pend ? GEN_FC_IRQ_PENDING_MODEL_CP_MIE_GLOBAL_EDGE_SET_PENDING
                        : GEN_FC_IRQ_PENDING_MODEL_CP_MIE_GLOBAL_EDGE_SET_IDLE)
                : (pend ? GEN_FC_IRQ_PENDING_MODEL_CP_MIE_GLOBAL_EDGE_CLEAR_PENDING
                        : GEN_FC_IRQ_PENDING_MODEL_CP_MIE_GLOBAL_EDGE_CLEAR_IDLE);
      end
      if (v < 0) return;
      irq_pend_cg.sample(-1, irq_state_bin(st, 1'b0), -1, -1, -1, v);
      n_irq_mie++;
    endfunction

    // per record: the histories the cycle reads use, NMI mode, then the two record events
    function void irq_pend_record(gen_model_state st, gen_rvfi_txn t);
      // a missing published sample disqualifies the view-fed judgements only. irq_view_ok is already set for
      // this record by write_mst. Of the three called after the guard, two read the record itself; the debug
      // one reads the view and emits an undecided window on a miss, which is its intended behaviour.
      if (irq_view_ok) begin
        if (st.is_intr && st.entry_cause == ibex_pkg::ExcCauseIrqNm.lower_cause) begin irq_nmi_mode = 1; irq_nmi_depth = 0; end
        else if (irq_nmi_mode && (st.is_trap || st.is_intr)) irq_nmi_depth++;
        else if (irq_nmi_mode && st.is_mret && !st.is_trap) begin if (irq_nmi_depth > 0) irq_nmi_depth--; else irq_nmi_mode = 0; end
        if (st.wrote_mie && irq_have_st) irq_edge_mie(st);
        irq_access_sample(st, t);
        irq_mie_global_sample(st);
      end
      irq_dbg_record(st);
      irq_mtvec_base = gen_isa_read_csr(ibex_pkg::CSR_MTVEC);   // the model's mtvec as of BEFORE this record
      irq_mtvec_have = 1;
      irq_rst_record(st, t);
      irq_off_take();
      irq_mie_prev = st.mie; irq_mstatus_prev = st.mstatus; prev_trapped = st.is_trap;
    endfunction

    // ---- IRQ step 1: CG-IRQ-010 gen_irq_debug_interplay_cg -----------------------------------------------
    // A WINDOW group: it opens on a record where a line is pending and enabled while the core is in debug mode
    // or stepping outside it, closes at the exit (dret, or the retirement of the stepped instruction), and is
    // sampled ONCE per window after the record that decides cp_post_exit. Every coverpoint of the group belongs
    // to the same window, which is why the seven values go in one call.
    gen_irq_debug_interplay_cg irq_dbg_cg;
    int unsigned n_irq_dbg = 0, n_irq_dbg_undecided = 0, n_irq_dbg_dropped = 0;
    // one slot: this DUT takes no debug entry from debug mode, so windows do not nest
    bit dbgw_open = 0, dbgw_await = 0, dbgw_held = 0, dbgw_nmi = 0, dbgw_mret_seen = 0;
    int dbgw_line = -1, dbgw_mode = -1, dbgw_prv = -1, dbgw_nmip = -1, dbgw_exit = -1;
    int unsigned dbgw_records = 0;
    int unsigned dbgw_post_bound = 256;   // records to wait for an NMI handler's mret before judging the window

    // the class of the line that opened the window, in the plan's order: an internal NMI outranks the pin,
    // which outranks an ordinary enabled line
    function int irq_dbg_line_bin(gen_model_state st, logic [18:0] pins, logic [31:0] mie);
      if (st.nmi_int_pend) return GEN_FC_IRQ_DEBUG_INTERPLAY_CP_LINE_NMI_INT;
      if (st.nmi_pend || pins[18]) return GEN_FC_IRQ_DEBUG_INTERPLAY_CP_LINE_NMI_EXT;
      if (irq_pending_model(pins, mie)) return GEN_FC_IRQ_DEBUG_INTERPLAY_CP_LINE_IRQ;
      return -1;
    endfunction
    // is the window's own line still asserted?
    function bit irq_dbg_still(gen_model_state st, logic [18:0] pins, logic [31:0] mie);
      case (dbgw_line)
        GEN_FC_IRQ_DEBUG_INTERPLAY_CP_LINE_NMI_INT: return st.nmi_int_pend;
        GEN_FC_IRQ_DEBUG_INTERPLAY_CP_LINE_NMI_EXT: return st.nmi_pend || pins[18];
        GEN_FC_IRQ_DEBUG_INTERPLAY_CP_LINE_IRQ:     return irq_pending_model(pins, mie);
        default: return 1'b0;
      endcase
    endfunction
    // the plan does not sample a window whose observation has not closed, so one that outlives its bound is
    // dropped and counted instead of being given a bin it did not earn
    function void irq_dbg_drop();
      n_irq_dbg_dropped++;
      dbgw_open = 0; dbgw_await = 0;
    endfunction
    function void irq_dbg_emit(int v_post);
      if (irq_dbg_cg == null) return;
      irq_dbg_cg.sample(dbgw_line, dbgw_mode, dbgw_held ? GEN_FC_IRQ_DEBUG_INTERPLAY_CP_DURATION_HELD_THROUGH_EXIT
                                                        : GEN_FC_IRQ_DEBUG_INTERPLAY_CP_DURATION_DROPPED_BEFORE_EXIT,
                        v_post, dbgw_prv, dbgw_nmip, dbgw_exit);
      n_irq_dbg++;
      if (v_post < 0) n_irq_dbg_undecided++;
      dbgw_open = 0; dbgw_await = 0;
    endfunction

    // one record of the window's life. A record can open the window AND close it (a line that becomes
    // pending on the dret itself, or the single record of a step window), so the open test runs first and
    // the hold and exit tests run on the same record.
    function void irq_dbg_record(gen_model_state st);
      logic [18:0] pins = irq_pins_at(irq_commit_cycle(st));
      logic [31:0] mie = st.mie;
      bit stepping = st.dcsr[2] && !st.debug_mode;   // dcsr.step outside debug mode
      if (irq_dbg_cg == null) return;
      if (dbgw_await) begin
        // the first record after the exit decides cp_post_exit: an entry is the taken case, an ordinary
        // retirement with the line still asserted is the not-taken case, anything else is undecided and the
        // window is sampled with cp_post_exit in its ignore bin rather than a bin it did not earn. A window
        // opened inside an NMI handler defers past that handler's mret first.
        if (dbgw_nmi && !dbgw_mret_seen) begin
          if (st.is_intr) irq_dbg_emit(GEN_FC_IRQ_DEBUG_INTERPLAY_CP_POST_EXIT_TAKEN_BEFORE_FIRST_INSN);
          else if (st.is_mret) dbgw_mret_seen = 1;
          else if (dbgw_records >= dbgw_post_bound) irq_dbg_drop();
          dbgw_records++;
        end else if (st.is_intr) begin
          irq_dbg_emit(dbgw_mret_seen ? GEN_FC_IRQ_DEBUG_INTERPLAY_CP_POST_EXIT_TAKEN_AFTER_NMI_MRET
                                      : GEN_FC_IRQ_DEBUG_INTERPLAY_CP_POST_EXIT_TAKEN_BEFORE_FIRST_INSN);
        end else if (irq_dbg_still(st, pins, mie)) begin
          irq_dbg_emit(GEN_FC_IRQ_DEBUG_INTERPLAY_CP_POST_EXIT_NOT_TAKEN);
        end else begin
          irq_dbg_emit(-1);
        end
        return;
      end
      if (!dbgw_open) begin
        if (!st.debug_mode && !stepping) return;
        dbgw_line = irq_dbg_line_bin(st, pins, mie);
        if (dbgw_line < 0) return;                     // no line pending: not a window of this group
        dbgw_mode = !st.debug_mode ? GEN_FC_IRQ_DEBUG_INTERPLAY_CP_MODE_STEP_OUTSIDE :
                    irq_nmi_mode   ? GEN_FC_IRQ_DEBUG_INTERPLAY_CP_MODE_DEBUG_IN_NMI_HANDLER
                                   : GEN_FC_IRQ_DEBUG_INTERPLAY_CP_MODE_DEBUG_MODE;
        dbgw_prv = (st.dcsr[1:0] == ibex_pkg::PRIV_LVL_U) ? GEN_FC_IRQ_DEBUG_INTERPLAY_CP_DCSR_PRV_U
                                                          : GEN_FC_IRQ_DEBUG_INTERPLAY_CP_DCSR_PRV_M;
        dbgw_nmi = (dbgw_mode == GEN_FC_IRQ_DEBUG_INTERPLAY_CP_MODE_DEBUG_IN_NMI_HANDLER);
        dbgw_nmip = -1; dbgw_exit = -1; dbgw_held = 1; dbgw_mret_seen = 0;
        dbgw_open = 1;
      end
      if (!irq_dbg_still(st, pins, mie)) dbgw_held = 0;
      if (st.insn[6:0] == 7'b1110011 && st.insn[14:12] != 3'b000 && st.insn[31:20] == ibex_pkg::CSR_DCSR)
        dbgw_nmip = (st.nmi_pend || pins[18]) ? GEN_FC_IRQ_DEBUG_INTERPLAY_CP_NMIP_READ_READ_WITH_NMI_HIGH
                                              : GEN_FC_IRQ_DEBUG_INTERPLAY_CP_NMIP_READ_READ_WITH_NMI_LOW;
      if (dbgw_mode == GEN_FC_IRQ_DEBUG_INTERPLAY_CP_MODE_STEP_OUTSIDE) begin
        dbgw_exit = GEN_FC_IRQ_DEBUG_INTERPLAY_CP_EXIT_KIND_STEP_COMPLETE;   // this record IS the stepped one
        dbgw_await = 1; dbgw_records = 0;
      end else if (st.is_dret) begin
        dbgw_exit = GEN_FC_IRQ_DEBUG_INTERPLAY_CP_EXIT_KIND_DRET;
        dbgw_await = 1; dbgw_records = 0;
      end
    endfunction

    // ---- IRQ step 1: CG-IRQ-011 gen_irq_reset_fetch_en_cg ------------------------------------------------
    // Two sample events. ev_reset is the reset release: the pins latched there, the first architectural event,
    // the first reset-time CSR read-backs and a boot mret. Each observation is its own sample, so one
    // coverpoint carries one fact instead of a sample inventing values for the others. ev_off is a CLOSED
    // fetch-enable Off window, TAKEN from gen_misc_monitor's published queue rather than detected here a
    // second time from the same pin, and completed by the first fetch after the return to On, which arrives
    // on the ibus subscription this class already has.
    gen_irq_reset_fetch_en_cg irq_rst_cg;
    int unsigned n_irq_rst = 0, n_irq_off = 0, n_irq_off_unclosed = 0;
    int irq_rst_lines = -1, irq_rst_first = -1;
    bit irq_rst_have = 0, irq_rst_first_done = 0, irq_rst_trapped = 0;
    logic [18:0] irq_rst_pins = '0; bit irq_rst_dbg = 0;
    bit irq_rd_mstatus = 0, irq_rd_mie = 0, irq_rd_mtvec = 0, irq_rd_mip = 0;
    bit irq_off_open = 0; int irq_off_cls = -1; int unsigned irq_off_on_cycle = 0;
    bit          irq_mtvec_have = 0;   // a record has retired, so irq_mtvec_base is the model's
    logic [31:0] irq_mtvec_base = '0;   // mtvec as of the last record, for "the first fetch after On is the vector"

    // cp_lines_at_reset: the pin pattern latched at the release. A debug request with neither an NMI nor a
    // regular line has no bin in the plan and samples nothing.
    function int irq_rst_lines_bin(logic [18:0] pins, bit dbg);
      bit nm = pins[18];
      bit reg_line = |pins[17:0];
      if (dbg && nm) return GEN_FC_IRQ_RESET_FETCH_EN_CP_LINES_AT_RESET_DEBUG_AND_NMI;
      if (dbg && reg_line) return GEN_FC_IRQ_RESET_FETCH_EN_CP_LINES_AT_RESET_DEBUG_AND_REGULAR;
      if (dbg) return -1;
      if (nm && reg_line) return GEN_FC_IRQ_RESET_FETCH_EN_CP_LINES_AT_RESET_NMI_AND_REGULAR;
      if (nm) return GEN_FC_IRQ_RESET_FETCH_EN_CP_LINES_AT_RESET_NMI_ONLY;
      if (reg_line) return GEN_FC_IRQ_RESET_FETCH_EN_CP_LINES_AT_RESET_REGULAR_ONLY;
      return GEN_FC_IRQ_RESET_FETCH_EN_CP_LINES_AT_RESET_NONE;
    endfunction

    function void irq_rst_emit(int v_reads, int v_mret);
      if (irq_rst_cg == null || !irq_rst_have) return;
      irq_rst_cg.sample(irq_rst_lines, irq_rst_first, v_reads, v_mret, -1, -1);
      n_irq_rst++;
    endfunction

    // the first architectural event after the release, and the reset-time facts that ride with it
    function void irq_rst_record(gen_model_state st, gen_rvfi_txn t);
      logic [11:0] csr = st.insn[31:20];
      logic [2:0]  f3  = st.insn[14:12];
      bit is_read = (st.insn[6:0] == 7'b1110011) && (f3 != 3'b000) && (st.insn[19:15] == 5'd0) && (f3[1:0] != 2'b01);
      logic [18:0] pins;
      if (!irq_rst_have) return;
      if (!irq_rst_first_done) begin
        irq_rst_first = st.nmi_pend && st.is_intr ? GEN_FC_IRQ_RESET_FETCH_EN_CP_FIRST_EVENT_NMI_BEFORE_INSN :
                        st.debug_mode            ? GEN_FC_IRQ_RESET_FETCH_EN_CP_FIRST_EVENT_DEBUG_BEFORE_INSN :
                        (st.pc_rdata == gen_reset_pc(cfg.boot_addr)) ? GEN_FC_IRQ_RESET_FETCH_EN_CP_FIRST_EVENT_BOOT_INSN : -1;
        irq_rst_first_done = 1;
        irq_rst_emit(-1, -1);                       // the pin pattern and the first event, once
      end
      // cp_reset_reads: the FIRST read-back of each of the four, judged against the record's own rd_wdata
      if (is_read && t != null && t.rd_addr != 5'd0) begin
        int v = -1;
        if (csr == ibex_pkg::CSR_MSTATUS && !irq_rd_mstatus) begin irq_rd_mstatus = 1; if (t.rd_wdata == 32'h80) v = GEN_FC_IRQ_RESET_FETCH_EN_CP_RESET_READS_MSTATUS_0X80; end
        else if (csr == ibex_pkg::CSR_MIE && !irq_rd_mie) begin irq_rd_mie = 1; if (t.rd_wdata == 32'h0) v = GEN_FC_IRQ_RESET_FETCH_EN_CP_RESET_READS_MIE_0; end
        else if (csr == ibex_pkg::CSR_MTVEC && !irq_rd_mtvec) begin irq_rd_mtvec = 1; if (t.rd_wdata[31:8] == cfg.boot_addr[31:8]) v = GEN_FC_IRQ_RESET_FETCH_EN_CP_RESET_READS_MTVEC_BOOT_PAGE; end
        else if (csr == ibex_pkg::CSR_MIP && !irq_rd_mip && irq_view_ok) begin   // the only reset read that needs the view
          logic [31:0] exp_mip = '0;
          irq_rd_mip = 1;
          pins = irq_pins_at(irq_commit_cycle(st));
          // mip is bit-positioned and the pins are line-indexed: map each line through its CSR bit rather
          // than comparing slices, which agreed only when every pin was low
          for (int l = 0; l < 18; l++) if (pins[l]) exp_mip[gen_irq_mie_bit(l)] = 1'b1;
          if (t.rd_wdata == exp_mip) v = GEN_FC_IRQ_RESET_FETCH_EN_CP_RESET_READS_MIP_REFLECTS_PINS;
        end
        if (v >= 0) irq_rst_emit(v, -1);
      end
      // cp_boot_mret: an mret before any trap, returning to U with MIE restored
      if (st.is_mret && !irq_rst_trapped && st.prv == ibex_pkg::PRIV_LVL_U
          && st.mstatus[ibex_pkg::CSR_MSTATUS_MIE_BIT])
        irq_rst_emit(-1, GEN_FC_IRQ_RESET_FETCH_EN_CP_BOOT_MRET_TO_U_MIE1);
      if (st.is_trap || st.is_intr) irq_rst_trapped = 1;
    endfunction

    // cp_fetch_off: the interrupt situation in a closed Off window, read from the published samples that
    // still cover it. A window longer than the published depth is judged on the part still covered, which the
    // note states; the classes are exclusive and taken in the plan's order of specificity.
    function int irq_off_bin(int unsigned off_cycle, int unsigned on_cycle);
      bit nm_rose = 0, line_rose = 0, pending_at_start = 0, any = 0;
      logic [18:0] pins, prev; bit pending, have_prev = 0;
      for (int unsigned c = off_cycle; c <= on_cycle; c++) begin
        if (!gen_irq_view::sample_at(c, pins, pending)) continue;
        if (|pins[17:0] || pins[18]) any = 1;
        if (c == off_cycle && irq_pending_model(pins, gen_irq_view::mie_at(c))) pending_at_start = 1;
        if (have_prev) begin
          if (pins[18] && !prev[18]) nm_rose = 1;
          if (|(pins[17:0] & ~prev[17:0])) line_rose = 1;
        end
        prev = pins; have_prev = 1;
      end
      if (nm_rose) return GEN_FC_IRQ_RESET_FETCH_EN_CP_FETCH_OFF_NMI_WHILE_OFF;
      if (pending_at_start) return GEN_FC_IRQ_RESET_FETCH_EN_CP_FETCH_OFF_IRQ_PENDING_WHILE_OFF_CSR_UPDATED;
      if (line_rose) return GEN_FC_IRQ_RESET_FETCH_EN_CP_FETCH_OFF_IRQ_ARRIVES_WHILE_OFF;
      if (!any) return GEN_FC_IRQ_RESET_FETCH_EN_CP_FETCH_OFF_NONE_PENDING_WHILE_OFF;
      return -1;
    endfunction

    // one closed window per call, opened here and completed by the first fetch after the return to On
    function void irq_off_take();
      int unsigned off_cycle, on_cycle;
      if (irq_rst_cg == null || irq_off_open) return;
      if (!gen_fetch_en_windows::take(off_cycle, on_cycle)) return;
      irq_off_cls = irq_off_bin(off_cycle, on_cycle);
      irq_off_on_cycle = on_cycle;
      irq_off_open = 1;
    endfunction

    // the trap vector itself: with vectored mode an entry is base + 4*cause, so a page compare cannot tell
    // the vector from boot code that shares its page
    function bit irq_addr_is_vector(logic [31:0] addr, logic [31:0] mtvec);
      logic [31:0] base = {mtvec[31:2], 2'b00};
      if (mtvec[1:0] == 2'b01) begin
        if (addr < base || addr >= base + (32 * 4)) return 1'b0;
        return ((addr - base) % 4) == 0;
      end
      return addr == base;
    endfunction

    // the first fetch after On decides cp_fetch_on_after: the trap vector, or anything else (a resume)
    function void irq_off_first_fetch(gen_bus_txn b);
      int v_on;
      logic [31:0] tvec;
      if (!irq_off_open || b.stamp_gnt < irq_off_on_cycle) return;
      // the base is mtvec as of the last retired record, or as hardware initialised it when nothing has
      // retired, which is the reset-opened window (DV Lead's ev_off clause)
      tvec = irq_mtvec_have ? irq_mtvec_base : gen_mtvec_reset(cfg.boot_addr);
      v_on = irq_addr_is_vector(b.addr, tvec)
             ? GEN_FC_IRQ_RESET_FETCH_EN_CP_FETCH_ON_AFTER_HANDLER_FETCHED_AT_ON
             : GEN_FC_IRQ_RESET_FETCH_EN_CP_FETCH_ON_AFTER_RESUME_AT_ON;
      if (irq_rst_cg != null) begin
        irq_rst_cg.sample(-1, -1, -1, -1, irq_off_cls, v_on);
        n_irq_off++;
      end
      irq_off_open = 0;
    endfunction

    function void write_irqe(gen_irq_evt e);   // an asserted edge of an interrupt line: an NMI raise or an ordinary irq (cp_event_mid)
      irq_edge_pins(e);
      if (e.level) ev_push(e.cycle, e.changed[18] ? GEN_FC_DIV_TIMING_CP_EVENT_MID_NMI : GEN_FC_DIV_TIMING_CP_EVENT_MID_IRQ);
    endfunction
    function void write_dbge(gen_irq_evt e);   // an asserted edge of debug_req_i
      if (e.level) ev_push(e.cycle, GEN_FC_DIV_TIMING_CP_EVENT_MID_DEBUG_REQ);
    endfunction
    function void ev_push(int unsigned cycle, int kind);
      ev_cyc.push_back(cycle); ev_kind.push_back(kind);
      if (ev_cyc.size() > 64) begin void'(ev_cyc.pop_front()); void'(ev_kind.pop_front()); end
    endfunction
    function void write_dbus(gen_bus_txn b);   // every completed data-bus transaction, in completion order
      dlat_cyc.push_back(b.stamp_rvalid); dlat_lat.push_back(b.rvalid_delay); dlat_gnt.push_back(b.stamp_gnt); dlat_addr.push_back({b.addr[31:2], 2'b00});   // the RVFI record's cycle base (bridge counter)
      if (dlat_cyc.size() > 256) begin void'(dlat_cyc.pop_front()); void'(dlat_lat.pop_front()); void'(dlat_gnt.pop_front()); void'(dlat_addr.pop_front()); end
    endfunction
    function void build_phase(uvm_phase phase);
      super.build_phase(phase);
      if (!uvm_config_db#(gen_env_cfg)::get(this, "", "cfg", cfg)) `uvm_fatal("GEN_FCOV", "cfg not in uvm_config_db")
      if (!uvm_config_db#(virtual gen_ctrl_if)::get(this, "", "vif", ctrl_vif)) `uvm_fatal("GEN_FCOV", "ctrl vif not in uvm_config_db")
      if (!uvm_config_db#(virtual gen_irq_if)::get(this, "", "irq_vif", irq_vif)) `uvm_fatal("GEN_FCOV", "irq vif not in uvm_config_db")
      if (!uvm_config_db#(virtual gen_dbg_if)::get(this, "", "dbg_vif", dbg_vif)) `uvm_fatal("GEN_FCOV", "dbg vif not in uvm_config_db")
      if (!uvm_config_db#(virtual gen_misc_if)::get(this, "", "misc_vif", misc_vif)) `uvm_fatal("GEN_FCOV", "misc vif not in uvm_config_db")
      hart_id_v = cfg.hart_id;
      if (cfg.fcov_en) begin mul_cg = new(); div_cg = new(); alu_cg = new(); bit_cg = new(); imm_cg = new(); sh_cg = new(); cnt_cg = new(); zca_cg = new(); zcmp_cg = new(); mv_cg = new(); csr_cg = new(); br_cg = new(); sbit_cg = new(); zcb_cg = new(); rec_cg = new(); mt_cg = new(); rst_cg = new(); ic_ecc_cg = new(); sec_cg = new(); hz_cg = new(); lu_cg = new(); hx_cg = new(); jp_cg = new(); dt_cg = new(); ie_cg = new(); irq_entry_cg = new(); irq_pend_cg = new(); irq_dbg_cg = new(); irq_rst_cg = new(); pmp_acc_cg = new(); pmp_tbl_cg = new(); pmp_cfg_cg = new(); pmp_addr_cg = new(); end
    endfunction
    // ---- classifiers (plan bin order = the rendered GEN_FC_* indices)
    // CG-IC-006 cp_no_alert_case, most-masking first, which is the fcov plan's precedence: the enable and the sweep are terms
    // of lookup_actual_ic0 and mask the DUT's check whatever else holds, so they outrank the rest; then the two injection
    // cases, mutually exclusive by their own conditions; then the never-written read, reachable only with no injection at all.
    // -1 = no no-alert case applies (a hit-way injection that owed its pulse).
    function int ic_no_alert_case(bit en_ok, bit sweep_ok, bit injected, int verdict, bit dup_masked, bit uninit);
      if (!en_ok)    return GEN_FC_IC_ECC_CP_NO_ALERT_CASE_DISABLED_CACHE;
      if (!sweep_ok) return GEN_FC_IC_ECC_CP_NO_ALERT_CASE_DURING_INVALIDATION;
      if (injected) begin
        if (dup_masked)   return GEN_FC_IC_ECC_CP_NO_ALERT_CASE_MASKED_DUPLICATE_COPY;
        if (verdict == 0) return GEN_FC_IC_ECC_CP_NO_ALERT_CASE_UNUSED_WAY_DATA;
        return -1;
      end
      if (uninit) return GEN_FC_IC_ECC_CP_NO_ALERT_CASE_UNINITIALISED_DATA_RAM;
      return -1;
    endfunction
    // CG-IC-006 cp_major_nmi_quiet. The bin is a yes alone, so anything but quiet is not applicable rather than a bin. A window
    // in which no retirement was seen cannot support the NMI half, so it claims nothing instead of claiming quiet.
    function int ic_major_nmi_quiet(bit major_seen, bit nmi_seen, bit retirement_seen);
      if (major_seen || nmi_seen) return -1;
      if (!retirement_seen)       return -1;
      return GEN_FC_IC_ECC_CP_MAJOR_NMI_QUIET_YES;
    endfunction
    // CG-IC-006 cp_knob: the injection-rate regime in force for the RAM kind that was injected, since the tag and the data
    // hooks have a knob each and a data injection under a tag rate of none would otherwise sample none and lose its cross bin
    function int ic_knob_cls(bit is_data);
      string s = is_data ? cfg.knob_icache_data_ecc_err_rate : cfg.knob_icache_ecc_err_rate;
      case (s)
        "none":     return GEN_FC_IC_ECC_CP_KNOB_NONE;
        "rare":     return GEN_FC_IC_ECC_CP_KNOB_RARE;
        "frequent": return GEN_FC_IC_ECC_CP_KNOB_FREQUENT;
        default:    return -1;
      endcase
    endfunction
    // the four part-2 coverpoints take -1 here rather than at every call site, so a caller cannot supply one by mistake;
    // the argument order is the plan's coverpoint order, which is what the renderer emits
    function void sample_ic_ecc(int v_ram, int v_bits, int v_way, int v_beat, int v_alert_pulses, int v_major_nmi_quiet,
                                int v_no_alert_case, int v_knob);
      if (ic_ecc_cg == null) return;
      n_ic_ecc++;
      ic_ecc_cg.sample(v_ram, v_bits, v_way, v_beat, v_alert_pulses, -1, -1, v_major_nmi_quiet, -1, v_no_alert_case, -1, v_knob);
    endfunction
    // The two entry points the misc monitor calls. Every bin INDEX is mapped here, from facts the monitor states in its own
    // terms, so the checkers package names no GEN_FC_ constant and needs no import of this package.
    function void sample_ic_ecc_injection(bit is_data, int unsigned bits, int unsigned way, int unsigned beat, bit got_pulse,
                                          bit en_ok, bit sweep_ok, int verdict, bit dup_masked,
                                          bit major_seen, bit nmi_seen, bit retirement_seen);
      sample_ic_ecc(is_data ? GEN_FC_IC_ECC_CP_RAM_DATA : GEN_FC_IC_ECC_CP_RAM_TAG,
                    (bits == 2) ? GEN_FC_IC_ECC_CP_BITS_DOUBLE : GEN_FC_IC_ECC_CP_BITS_SINGLE,
                    (way == 1) ? GEN_FC_IC_ECC_CP_WAY_WAY1 : GEN_FC_IC_ECC_CP_WAY_WAY0,
                    is_data ? ((beat == 1) ? GEN_FC_IC_ECC_CP_BEAT_BEAT1 : GEN_FC_IC_ECC_CP_BEAT_BEAT0) : -1,
                    got_pulse ? GEN_FC_IC_ECC_CP_ALERT_PULSES_ONE : -1,
                    ic_major_nmi_quiet(major_seen, nmi_seen, retirement_seen),
                    ic_no_alert_case(en_ok, sweep_ok, 1'b1, verdict, dup_masked, 1'b0),
                    ic_knob_cls(is_data));
    endfunction
    // a never-written data line read on a checked lookup with no injection in its cycle: one bin and nothing else applies
    function void sample_ic_ecc_uninit();
      sample_ic_ecc(-1, -1, -1, -1, -1, -1, ic_no_alert_case(1'b1, 1'b1, 1'b0, -2, 1'b0, 1'b1), -1);
    endfunction
    function int mul_rs_cls(logic [31:0] v);   // CG-MUL-001 cp_rs1_class / cp_rs2_class (same bin list)
      case (v)
        32'h0000_0000: return GEN_FC_MUL_OPS_CP_RS1_CLASS_ZERO;
        32'h0000_0001: return GEN_FC_MUL_OPS_CP_RS1_CLASS_ONE;
        32'hFFFF_FFFF: return GEN_FC_MUL_OPS_CP_RS1_CLASS_ALL_ONES;
        32'h8000_0000: return GEN_FC_MUL_OPS_CP_RS1_CLASS_INT_MIN;
        32'h7FFF_FFFF: return GEN_FC_MUL_OPS_CP_RS1_CLASS_INT_MAX;
        32'h0001_0000: return GEN_FC_MUL_OPS_CP_RS1_CLASS_P16;
        32'h0000_0002: return GEN_FC_MUL_OPS_CP_RS1_CLASS_TWO;
        default:       return v[31] ? GEN_FC_MUL_OPS_CP_RS1_CLASS_NEG_RAND : GEN_FC_MUL_OPS_CP_RS1_CLASS_POS_RAND;
      endcase
    endfunction
    function int mul_res_cls(logic [31:0] v);
      case (v)
        32'h0000_0000: return GEN_FC_MUL_OPS_CP_RESULT_CLASS_ZERO;
        32'h0000_0001: return GEN_FC_MUL_OPS_CP_RESULT_CLASS_ONE;
        32'hFFFF_FFFF: return GEN_FC_MUL_OPS_CP_RESULT_CLASS_ALL_ONES;
        32'h8000_0000: return GEN_FC_MUL_OPS_CP_RESULT_CLASS_INT_MIN;
        32'h7FFF_FFFF: return GEN_FC_MUL_OPS_CP_RESULT_CLASS_INT_MAX;
        32'hFFFF_FFFE: return GEN_FC_MUL_OPS_CP_RESULT_CLASS_FFFFFFFE;
        32'h3FFF_FFFF: return GEN_FC_MUL_OPS_CP_RESULT_CLASS_R3FFFFFFF;
        32'h4000_0000: return GEN_FC_MUL_OPS_CP_RESULT_CLASS_R40000000;
        default:       return GEN_FC_MUL_OPS_CP_RESULT_CLASS_OTHER;
      endcase
    endfunction
    // sign pair: bins pp, pn, np, nn in that order = {rs1[31], rs2[31]}
    function int sign_pair(logic [31:0] a, logic [31:0] b); return int'({a[31], b[31]}); endfunction
    function int mul_same(logic [4:0] rs1, logic [4:0] rs2, logic [4:0] rd);
      if (rs1 == rs2 && rs2 == rd && rd != 0) return GEN_FC_MUL_OPS_CP_SAME_REGS_ALL_SAME;
      if (rs1 == rs2 && rs1 != rd) return GEN_FC_MUL_OPS_CP_SAME_REGS_RS1_EQ_RS2;
      if ((rs1 == rd || rs2 == rd) && rs1 != rs2) return GEN_FC_MUL_OPS_CP_SAME_REGS_RS_EQ_RD;
      return GEN_FC_MUL_OPS_CP_SAME_REGS_DISTINCT;
    endfunction
    function int div_dividend_cls(logic [31:0] v);
      case (v)
        32'h0000_0000: return GEN_FC_DIV_OPS_CP_DIVIDEND_ZERO;
        32'h0000_0001: return GEN_FC_DIV_OPS_CP_DIVIDEND_ONE;
        32'hFFFF_FFFF: return GEN_FC_DIV_OPS_CP_DIVIDEND_ALL_ONES;
        32'h8000_0000: return GEN_FC_DIV_OPS_CP_DIVIDEND_INT_MIN;
        32'h7FFF_FFFF: return GEN_FC_DIV_OPS_CP_DIVIDEND_INT_MAX;
        32'h0000_0002: return GEN_FC_DIV_OPS_CP_DIVIDEND_TWO;
        32'h0000_0007: return GEN_FC_DIV_OPS_CP_DIVIDEND_SEVEN;
        default:       return v[31] ? GEN_FC_DIV_OPS_CP_DIVIDEND_NEG_RAND : GEN_FC_DIV_OPS_CP_DIVIDEND_POS_RAND;
      endcase
    endfunction
    // the listed values first, then the relations to the dividend, then the sign classes (plan order)
    function int div_divisor_cls(logic [31:0] rs2, logic [31:0] rs1);
      logic [32:0] abs1 = rs1[31] ? (33'd0 - {rs1[31], rs1}) : {1'b0, rs1};   // |x| of the sign-extended value (2^31 for INT_MIN)
      logic [32:0] abs2 = rs2[31] ? (33'd0 - {rs2[31], rs2}) : {1'b0, rs2};
      case (rs2)
        32'h0000_0000: return GEN_FC_DIV_OPS_CP_DIVISOR_ZERO;
        32'h0000_0001: return GEN_FC_DIV_OPS_CP_DIVISOR_ONE;
        32'hFFFF_FFFF: return GEN_FC_DIV_OPS_CP_DIVISOR_ALL_ONES;
        32'h8000_0000: return GEN_FC_DIV_OPS_CP_DIVISOR_INT_MIN;
        32'h0000_0002: return GEN_FC_DIV_OPS_CP_DIVISOR_TWO;
        32'hFFFF_FFFE: return GEN_FC_DIV_OPS_CP_DIVISOR_MINUS_TWO;
        default: begin
          if (rs2 == rs1) return GEN_FC_DIV_OPS_CP_DIVISOR_EQ_DIVIDEND;
          if (abs2 > abs1) return GEN_FC_DIV_OPS_CP_DIVISOR_ABS_GT_DIVIDEND;
          return rs2[31] ? GEN_FC_DIV_OPS_CP_DIVISOR_NEG_RAND : GEN_FC_DIV_OPS_CP_DIVISOR_POS_RAND;
        end
      endcase
    endfunction
    function int div_res_cls(logic [31:0] v, logic [31:0] rs1);
      case (v)
        32'h0000_0000: return GEN_FC_DIV_OPS_CP_RESULT_CLASS_ZERO;
        32'h0000_0001: return GEN_FC_DIV_OPS_CP_RESULT_CLASS_ONE;
        32'hFFFF_FFFF: return GEN_FC_DIV_OPS_CP_RESULT_CLASS_ALL_ONES;
        32'h8000_0000: return GEN_FC_DIV_OPS_CP_RESULT_CLASS_INT_MIN;
        32'h7FFF_FFFF: return GEN_FC_DIV_OPS_CP_RESULT_CLASS_INT_MAX;
        default:       return (v == rs1) ? GEN_FC_DIV_OPS_CP_RESULT_CLASS_EQ_DIVIDEND : GEN_FC_DIV_OPS_CP_RESULT_CLASS_OTHER;
      endcase
    endfunction
    function int alu_rs_cls(logic [31:0] v);   // CG-ISA-002 cp_rs1_class / cp_rs2_class
      case (v)
        32'h0000_0000: return GEN_FC_ISA_ALU_REG_CP_RS1_CLASS_ZERO;
        32'hFFFF_FFFF: return GEN_FC_ISA_ALU_REG_CP_RS1_CLASS_ALL_ONES;
        32'h8000_0000: return GEN_FC_ISA_ALU_REG_CP_RS1_CLASS_INT_MIN;
        32'h7FFF_FFFF: return GEN_FC_ISA_ALU_REG_CP_RS1_CLASS_INT_MAX;
        32'h0000_0001: return GEN_FC_ISA_ALU_REG_CP_RS1_CLASS_ONE;
        default:       return v[31] ? GEN_FC_ISA_ALU_REG_CP_RS1_CLASS_NEG_RAND : GEN_FC_ISA_ALU_REG_CP_RS1_CLASS_POS_RAND;
      endcase
    endfunction
    function int alu_res_cls(logic [31:0] v);
      case (v)
        32'h0000_0000: return GEN_FC_ISA_ALU_REG_CP_RESULT_CLASS_ZERO;
        32'hFFFF_FFFF: return GEN_FC_ISA_ALU_REG_CP_RESULT_CLASS_ALL_ONES;
        32'h8000_0000: return GEN_FC_ISA_ALU_REG_CP_RESULT_CLASS_INT_MIN;
        32'h7FFF_FFFF: return GEN_FC_ISA_ALU_REG_CP_RESULT_CLASS_INT_MAX;
        32'h0000_0001: return GEN_FC_ISA_ALU_REG_CP_RESULT_CLASS_ONE;
        default:       return GEN_FC_ISA_ALU_REG_CP_RESULT_CLASS_OTHER;
      endcase
    endfunction
    function int alu_same(logic [4:0] rs1, logic [4:0] rs2, logic [4:0] rd);
      if (rs1 == rs2 && rs2 == rd && rd != 0) return GEN_FC_ISA_ALU_REG_CP_SAME_REGS_ALL_SAME;
      if (rs1 == rs2 && rs1 != rd) return GEN_FC_ISA_ALU_REG_CP_SAME_REGS_RS1_EQ_RS2;
      if (rs1 == rd && rs1 != rs2) return GEN_FC_ISA_ALU_REG_CP_SAME_REGS_RS1_EQ_RD;
      if (rs2 == rd && rs1 != rs2) return GEN_FC_ISA_ALU_REG_CP_SAME_REGS_RS2_EQ_RD;
      return GEN_FC_ISA_ALU_REG_CP_SAME_REGS_DISTINCT;
    endfunction
    // add / sub only; the overflow cases take precedence over the carry / borrow they imply (one bin per sample)
    function int alu_wrap(int op, logic [31:0] a, logic [31:0] b);
      logic [32:0] sum = {1'b0, a} + {1'b0, b};
      if (op == GEN_FC_ISA_ALU_REG_CP_OP_ADD) begin
        if (!a[31] && !b[31] && sum[31]) return GEN_FC_ISA_ALU_REG_CP_WRAP_ADD_POS_OVF;
        if (a[31] && b[31] && !sum[31]) return GEN_FC_ISA_ALU_REG_CP_WRAP_ADD_NEG_OVF;
        if (sum[32]) return GEN_FC_ISA_ALU_REG_CP_WRAP_ADD_CARRY;
        return GEN_FC_ISA_ALU_REG_CP_WRAP_NONE;
      end
      if (op == GEN_FC_ISA_ALU_REG_CP_OP_SUB) begin
        if (a == 32'h8000_0000 && !b[31] && b != 0) return GEN_FC_ISA_ALU_REG_CP_WRAP_SUB_OVF;
        if (a < b) return GEN_FC_ISA_ALU_REG_CP_WRAP_SUB_BORROW;
        return GEN_FC_ISA_ALU_REG_CP_WRAP_NONE;
      end
      return -1;
    endfunction

    // ---- CG-BIT-001 (Zba / Zbb / pack): the listed values, then the byte / half-word sign classes, then the sign
    // A change here must change gen_bit_ratified_prog.py's _NAMED_EXACT and its bit-7/bit-15 rule, which draw
    // operands to land in these classes; nothing fails if they drift, the bins just stop being hit.
    function int bit_rs1_cls(logic [31:0] v);
      case (v)
        32'h0000_0000: return GEN_FC_BIT_ZBA_ZBB_OPS_CP_RS1_CLASS_ZERO;
        32'hFFFF_FFFF: return GEN_FC_BIT_ZBA_ZBB_OPS_CP_RS1_CLASS_ALL_ONES;
        32'h8000_0000: return GEN_FC_BIT_ZBA_ZBB_OPS_CP_RS1_CLASS_INT_MIN;
        32'h7FFF_FFFF: return GEN_FC_BIT_ZBA_ZBB_OPS_CP_RS1_CLASS_INT_MAX;
        32'h0000_0001: return GEN_FC_BIT_ZBA_ZBB_OPS_CP_RS1_CLASS_ONE;
        32'hE000_0000: return GEN_FC_BIT_ZBA_ZBB_OPS_CP_RS1_CLASS_E0000000;
        default: begin
          if (v[7] && !v[15]) return GEN_FC_BIT_ZBA_ZBB_OPS_CP_RS1_CLASS_BYTE_MSB;
          if (v[15] && !v[7]) return GEN_FC_BIT_ZBA_ZBB_OPS_CP_RS1_CLASS_HALF_MSB;
          return v[31] ? GEN_FC_BIT_ZBA_ZBB_OPS_CP_RS1_CLASS_NEG_RAND : GEN_FC_BIT_ZBA_ZBB_OPS_CP_RS1_CLASS_POS_RAND;
        end
      endcase
    endfunction
    function int bit_rs2_cls(logic [31:0] v);
      case (v)
        32'h0000_0000: return GEN_FC_BIT_ZBA_ZBB_OPS_CP_RS2_CLASS_ZERO;
        32'hFFFF_FFFF: return GEN_FC_BIT_ZBA_ZBB_OPS_CP_RS2_CLASS_ALL_ONES;
        32'h8000_0000: return GEN_FC_BIT_ZBA_ZBB_OPS_CP_RS2_CLASS_INT_MIN;
        32'h7FFF_FFFF: return GEN_FC_BIT_ZBA_ZBB_OPS_CP_RS2_CLASS_INT_MAX;
        32'h0000_0001: return GEN_FC_BIT_ZBA_ZBB_OPS_CP_RS2_CLASS_ONE;
        default:       return v[31] ? GEN_FC_BIT_ZBA_ZBB_OPS_CP_RS2_CLASS_NEG_RAND : GEN_FC_BIT_ZBA_ZBB_OPS_CP_RS2_CLASS_POS_RAND;
      endcase
    endfunction
    function int bit_res_cls(logic [31:0] v);
      case (v)
        32'h0000_0000: return GEN_FC_BIT_ZBA_ZBB_OPS_CP_RESULT_CLASS_ZERO;
        32'hFFFF_FFFF: return GEN_FC_BIT_ZBA_ZBB_OPS_CP_RESULT_CLASS_ALL_ONES;
        32'h8000_0000: return GEN_FC_BIT_ZBA_ZBB_OPS_CP_RESULT_CLASS_INT_MIN;
        32'h7FFF_FFFF: return GEN_FC_BIT_ZBA_ZBB_OPS_CP_RESULT_CLASS_INT_MAX;
        default:       return GEN_FC_BIT_ZBA_ZBB_OPS_CP_RESULT_CLASS_OTHER;
      endcase
    endfunction
    function int bit_same(logic [4:0] rs1, logic [4:0] rs2, logic [4:0] rd);
      if (rs1 == rs2 && rs2 == rd && rd != 0) return GEN_FC_BIT_ZBA_ZBB_OPS_CP_SAME_REGS_ALL_SAME;
      if (rs1 == rs2 && rs1 != rd) return GEN_FC_BIT_ZBA_ZBB_OPS_CP_SAME_REGS_RS1_EQ_RS2;
      return GEN_FC_BIT_ZBA_ZBB_OPS_CP_SAME_REGS_DISTINCT;
    endfunction
    // the Zba / Zbb / pack op of an OP or OP-IMM encoding, -1 when none (decoder arms rtl/ibex_decoder.sv:609-624, :1106-1107)
    function int bit_op(logic [31:0] insn);
      logic [6:0] f7 = insn[31:25]; logic [2:0] f3 = insn[14:12]; logic [4:0] r2 = insn[24:20];
      if (insn[6:0] == ibex_pkg::OPCODE_OP_IMM && f3 == 3'b001 && f7 == 7'b0110000) begin
        if (r2 == 5'b00100) return GEN_FC_BIT_ZBA_ZBB_OPS_CP_OP_SEXT_B;
        if (r2 == 5'b00101) return GEN_FC_BIT_ZBA_ZBB_OPS_CP_OP_SEXT_H;
        return -1;
      end
      if (insn[6:0] != ibex_pkg::OPCODE_OP) return -1;
      case ({f7, f3})
        {7'b0010000, 3'b010}: return GEN_FC_BIT_ZBA_ZBB_OPS_CP_OP_SH1ADD;
        {7'b0010000, 3'b100}: return GEN_FC_BIT_ZBA_ZBB_OPS_CP_OP_SH2ADD;
        {7'b0010000, 3'b110}: return GEN_FC_BIT_ZBA_ZBB_OPS_CP_OP_SH3ADD;
        {7'b0100000, 3'b111}: return GEN_FC_BIT_ZBA_ZBB_OPS_CP_OP_ANDN;
        {7'b0100000, 3'b110}: return GEN_FC_BIT_ZBA_ZBB_OPS_CP_OP_ORN;
        {7'b0100000, 3'b100}: return GEN_FC_BIT_ZBA_ZBB_OPS_CP_OP_XNOR;
        {7'b0000101, 3'b100}: return GEN_FC_BIT_ZBA_ZBB_OPS_CP_OP_MIN;
        {7'b0000101, 3'b110}: return GEN_FC_BIT_ZBA_ZBB_OPS_CP_OP_MAX;
        {7'b0000101, 3'b101}: return GEN_FC_BIT_ZBA_ZBB_OPS_CP_OP_MINU;
        {7'b0000101, 3'b111}: return GEN_FC_BIT_ZBA_ZBB_OPS_CP_OP_MAXU;
        {7'b0000100, 3'b100}: return (r2 == 5'd0) ? GEN_FC_BIT_ZBA_ZBB_OPS_CP_OP_ZEXT_H : GEN_FC_BIT_ZBA_ZBB_OPS_CP_OP_PACK;
        {7'b0100100, 3'b100}: return GEN_FC_BIT_ZBA_ZBB_OPS_CP_OP_PACKU;
        {7'b0000100, 3'b111}: return GEN_FC_BIT_ZBA_ZBB_OPS_CP_OP_PACKH;
        default: return -1;
      endcase
    endfunction
    // carry out of rs2 + ((rs1 << n) mod 2^32) for shNadd (the truncated shifted operand feeds the adder, rtl/ibex_alu.sv:87-89)
    function int bit_wrap(int op, logic [31:0] rs1, logic [31:0] rs2);
      int n = (op == GEN_FC_BIT_ZBA_ZBB_OPS_CP_OP_SH1ADD) ? 1 : (op == GEN_FC_BIT_ZBA_ZBB_OPS_CP_OP_SH2ADD) ? 2 : (op == GEN_FC_BIT_ZBA_ZBB_OPS_CP_OP_SH3ADD) ? 3 : 0;
      logic [32:0] sum;
      if (n == 0) return -1;
      sum = {1'b0, rs2} + {1'b0, rs1 << n};
      return sum[32] ? GEN_FC_BIT_ZBA_ZBB_OPS_CP_WRAP_YES : GEN_FC_BIT_ZBA_ZBB_OPS_CP_WRAP_NO;
    endfunction
    // ---- CG-ISA-001 (OP-IMM ALU)
    function int imm_rs1_cls(logic [31:0] v);
      case (v)
        32'h0000_0000: return GEN_FC_ISA_ALU_IMM_CP_RS1_CLASS_ZERO;
        32'hFFFF_FFFF: return GEN_FC_ISA_ALU_IMM_CP_RS1_CLASS_ALL_ONES;
        32'h8000_0000: return GEN_FC_ISA_ALU_IMM_CP_RS1_CLASS_INT_MIN;
        32'h7FFF_FFFF: return GEN_FC_ISA_ALU_IMM_CP_RS1_CLASS_INT_MAX;
        32'h0000_0001: return GEN_FC_ISA_ALU_IMM_CP_RS1_CLASS_ONE;
        default:       return v[31] ? GEN_FC_ISA_ALU_IMM_CP_RS1_CLASS_NEG_RAND : GEN_FC_ISA_ALU_IMM_CP_RS1_CLASS_POS_RAND;
      endcase
    endfunction
    function int imm_cls(int imm);
      case (imm)
        0:     return GEN_FC_ISA_ALU_IMM_CP_IMM_CLASS_ZERO;
        1:     return GEN_FC_ISA_ALU_IMM_CP_IMM_CLASS_PLUS1;
        -1:    return GEN_FC_ISA_ALU_IMM_CP_IMM_CLASS_MINUS1;
        2047:  return GEN_FC_ISA_ALU_IMM_CP_IMM_CLASS_MAX_POS;
        -2048: return GEN_FC_ISA_ALU_IMM_CP_IMM_CLASS_MIN_NEG;
        default: return imm > 0 ? GEN_FC_ISA_ALU_IMM_CP_IMM_CLASS_POS_RAND : GEN_FC_ISA_ALU_IMM_CP_IMM_CLASS_NEG_RAND;
      endcase
    endfunction
    function int imm_res_cls(logic [31:0] v);
      case (v)
        32'h0000_0000: return GEN_FC_ISA_ALU_IMM_CP_RESULT_CLASS_ZERO;
        32'hFFFF_FFFF: return GEN_FC_ISA_ALU_IMM_CP_RESULT_CLASS_ALL_ONES;
        32'h8000_0000: return GEN_FC_ISA_ALU_IMM_CP_RESULT_CLASS_INT_MIN;
        32'h7FFF_FFFF: return GEN_FC_ISA_ALU_IMM_CP_RESULT_CLASS_INT_MAX;
        32'h0000_0001: return GEN_FC_ISA_ALU_IMM_CP_RESULT_CLASS_ONE;
        default:       return GEN_FC_ISA_ALU_IMM_CP_RESULT_CLASS_OTHER;
      endcase
    endfunction
    function int addi_wrap(int op, logic [31:0] rs1, int imm);   // from the operands alone: rvfi_rd_wdata is forced to 0 on rd = x0
      logic [31:0] res = rs1 + 32'(imm);
      if (op != GEN_FC_ISA_ALU_IMM_CP_OP_ADDI) return -1;
      if (!rs1[31] && imm > 0 && res[31]) return GEN_FC_ISA_ALU_IMM_CP_ADDI_WRAP_POS_WRAP;
      if (rs1[31] && imm < 0 && !res[31]) return GEN_FC_ISA_ALU_IMM_CP_ADDI_WRAP_NEG_WRAP;
      return GEN_FC_ISA_ALU_IMM_CP_ADDI_WRAP_NONE;
    endfunction
    // the named boundary cases first (they imply eq in two places), then eq, then other
    function int slt_case(int op, logic [31:0] rs1, int imm);
      bit slti = (op == GEN_FC_ISA_ALU_IMM_CP_OP_SLTI), sltiu = (op == GEN_FC_ISA_ALU_IMM_CP_OP_SLTIU);
      if (!slti && !sltiu) return -1;
      if (slti && rs1 == 32'h8000_0000 && imm == 0) return GEN_FC_ISA_ALU_IMM_CP_SLT_CASE_SLTI_INTMIN_0;
      if (slti && rs1 == 32'h0 && imm < 0) return GEN_FC_ISA_ALU_IMM_CP_SLT_CASE_SLTI_0_NEG;
      if (sltiu && rs1 == 32'hFFFF_FFFF && imm == -1) return GEN_FC_ISA_ALU_IMM_CP_SLT_CASE_SLTIU_ONES_M1;
      if (sltiu && imm == -1) return GEN_FC_ISA_ALU_IMM_CP_SLT_CASE_SLTIU_IMM_M1;
      if (sltiu && imm == 1) return GEN_FC_ISA_ALU_IMM_CP_SLT_CASE_SLTIU_SEQZ;
      if (rs1 == 32'(imm)) return GEN_FC_ISA_ALU_IMM_CP_SLT_CASE_EQ;   // sext(imm) as a 32-bit word
      return GEN_FC_ISA_ALU_IMM_CP_SLT_CASE_OTHER;
    endfunction
    // ---- CG-ISA-003 (base shifts)
    function int sh_operand_cls(logic [31:0] v);
      case (v)
        32'h0000_0000: return GEN_FC_ISA_SHIFT_CP_OPERAND_ZERO;
        32'hFFFF_FFFF: return GEN_FC_ISA_SHIFT_CP_OPERAND_ALL_ONES;
        32'h8000_0000: return GEN_FC_ISA_SHIFT_CP_OPERAND_MSB_ONLY;
        32'h0000_0001: return GEN_FC_ISA_SHIFT_CP_OPERAND_LSB_ONLY;
        default:       return v[31] ? GEN_FC_ISA_SHIFT_CP_OPERAND_NEG_RAND : GEN_FC_ISA_SHIFT_CP_OPERAND_POS_RAND;
      endcase
    endfunction
    function int sh_res_cls(logic [31:0] v);
      case (v)
        32'h0000_0000: return GEN_FC_ISA_SHIFT_CP_RESULT_CLASS_ZERO;
        32'hFFFF_FFFF: return GEN_FC_ISA_SHIFT_CP_RESULT_CLASS_ALL_ONES;
        32'h8000_0000: return GEN_FC_ISA_SHIFT_CP_RESULT_CLASS_MSB_ONLY;
        32'h0000_0001: return GEN_FC_ISA_SHIFT_CP_RESULT_CLASS_ONE;
        32'hC000_0000: return GEN_FC_ISA_SHIFT_CP_RESULT_CLASS_C0000000;
        default:       return GEN_FC_ISA_SHIFT_CP_RESULT_CLASS_OTHER;
      endcase
    endfunction
    function int sh_amt_cls(logic [4:0] a);
      if (a == 0) return GEN_FC_ISA_SHIFT_CP_SHAMT_S0;
      if (a == 1) return GEN_FC_ISA_SHIFT_CP_SHAMT_S1;
      if (a == 31) return GEN_FC_ISA_SHIFT_CP_SHAMT_S31;
      return GEN_FC_ISA_SHIFT_CP_SHAMT_MID;
    endfunction
    // register forms only: the exact values first, then the upper-bits-clear class, else other_nonzero
    function int sh_rs2_upper(logic [31:0] v);
      case (v)
        32'd32:        return GEN_FC_ISA_SHIFT_CP_RS2_UPPER_IS32;
        32'd33:        return GEN_FC_ISA_SHIFT_CP_RS2_UPPER_IS33;
        32'hFFFF_FFFF: return GEN_FC_ISA_SHIFT_CP_RS2_UPPER_ALL_ONES;
        32'h8000_0000: return GEN_FC_ISA_SHIFT_CP_RS2_UPPER_MSB_ONLY;
        32'hFFFF_FFE0: return GEN_FC_ISA_SHIFT_CP_RS2_UPPER_FFFFFFE0;
        default:       return (v[31:5] == 0) ? GEN_FC_ISA_SHIFT_CP_RS2_UPPER_ZERO : GEN_FC_ISA_SHIFT_CP_RS2_UPPER_OTHER_NONZERO;
      endcase
    endfunction

    // ---- CG-BIT-002 (clz / ctz / cpop)
    function int cnt_operand_cls(logic [31:0] v);
      case (v)
        32'h0000_0000: return GEN_FC_BIT_COUNT_CP_OPERAND_ZERO;
        32'hFFFF_FFFF: return GEN_FC_BIT_COUNT_CP_OPERAND_ALL_ONES;
        32'h8000_0000: return GEN_FC_BIT_COUNT_CP_OPERAND_MSB_ONLY;
        32'h0000_0001: return GEN_FC_BIT_COUNT_CP_OPERAND_LSB_ONLY;
        32'h5555_5555: return GEN_FC_BIT_COUNT_CP_OPERAND_ALT_5;
        32'hAAAA_AAAA: return GEN_FC_BIT_COUNT_CP_OPERAND_ALT_A;
        32'h7FFF_FFFF: return GEN_FC_BIT_COUNT_CP_OPERAND_INT_MAX;
        default:       return ($countones(v) == 1) ? GEN_FC_BIT_COUNT_CP_OPERAND_SINGLE_OTHER : GEN_FC_BIT_COUNT_CP_OPERAND_RAND;
      endcase
    endfunction
    function int cnt_single_pos(logic [31:0] v);   // p0..p31 are consecutive indices from GEN_FC_BIT_COUNT_CP_SINGLE_POS_P0
      if ($countones(v) != 1) return -1;
      for (int i = 0; i < 32; i++) if (v[i]) return GEN_FC_BIT_COUNT_CP_SINGLE_POS_P0 + i;
      return -1;
    endfunction
    function int cnt_result_cls(logic [31:0] v);
      case (v)
        32'd0:  return GEN_FC_BIT_COUNT_CP_RESULT_R0;
        32'd1:  return GEN_FC_BIT_COUNT_CP_RESULT_R1;
        32'd16: return GEN_FC_BIT_COUNT_CP_RESULT_R16;
        32'd31: return GEN_FC_BIT_COUNT_CP_RESULT_R31;
        32'd32: return GEN_FC_BIT_COUNT_CP_RESULT_R32;
        default: return GEN_FC_BIT_COUNT_CP_RESULT_OTHER;
      endcase
    endfunction
    // ---- CG-CMP-001 (Zca): the 16-bit form as RVFI reports it (rvfi_insn[1:0] != 11); -1 for an encoding outside the plan's list
    function int zca_insn(logic [15:0] i);
      logic [2:0] f3 = i[15:13]; logic [4:0] rd = i[11:7], rs2 = i[6:2];
      case (i[1:0])
        2'b00: case (f3)
          3'b000: return (i != 16'h0) ? GEN_FC_CMP_ZCA_CP_INSN_C_ADDI4SPN : -1;
          3'b010: return GEN_FC_CMP_ZCA_CP_INSN_C_LW;
          3'b110: return GEN_FC_CMP_ZCA_CP_INSN_C_SW;
          default: return -1;
        endcase
        2'b01: case (f3)
          3'b000: return (rd == 0) ? GEN_FC_CMP_ZCA_CP_INSN_C_NOP : GEN_FC_CMP_ZCA_CP_INSN_C_ADDI;
          3'b001: return GEN_FC_CMP_ZCA_CP_INSN_C_JAL;
          3'b010: return GEN_FC_CMP_ZCA_CP_INSN_C_LI;
          3'b011: return (rd == 5'd2) ? GEN_FC_CMP_ZCA_CP_INSN_C_ADDI16SP : GEN_FC_CMP_ZCA_CP_INSN_C_LUI;
          3'b100: case (i[11:10])
            2'b00: return GEN_FC_CMP_ZCA_CP_INSN_C_SRLI;
            2'b01: return GEN_FC_CMP_ZCA_CP_INSN_C_SRAI;
            2'b10: return GEN_FC_CMP_ZCA_CP_INSN_C_ANDI;
            default: begin
              if (i[12]) return -1;   // c.subw / c.addw (RV64) and the Zcb arithmetic forms
              case (i[6:5])
                2'b00: return GEN_FC_CMP_ZCA_CP_INSN_C_SUB; 2'b01: return GEN_FC_CMP_ZCA_CP_INSN_C_XOR;
                2'b10: return GEN_FC_CMP_ZCA_CP_INSN_C_OR;  default: return GEN_FC_CMP_ZCA_CP_INSN_C_AND;
              endcase
            end
          endcase
          3'b101: return GEN_FC_CMP_ZCA_CP_INSN_C_J;
          3'b110: return GEN_FC_CMP_ZCA_CP_INSN_C_BEQZ;
          default: return GEN_FC_CMP_ZCA_CP_INSN_C_BNEZ;
        endcase
        2'b10: case (f3)
          3'b000: return GEN_FC_CMP_ZCA_CP_INSN_C_SLLI;
          3'b010: return GEN_FC_CMP_ZCA_CP_INSN_C_LWSP;
          3'b100: begin
            if (!i[12]) return (rs2 == 0) ? ((rd != 0) ? GEN_FC_CMP_ZCA_CP_INSN_C_JR : -1) : GEN_FC_CMP_ZCA_CP_INSN_C_MV;
            if (rs2 == 0) return (rd != 0) ? GEN_FC_CMP_ZCA_CP_INSN_C_JALR : -1;   // rd = 0 is c.ebreak, a trap record
            return GEN_FC_CMP_ZCA_CP_INSN_C_ADD;
          end
          3'b110: return GEN_FC_CMP_ZCA_CP_INSN_C_SWSP;
          default: return -1;
        endcase
        default: return -1;
      endcase
    endfunction
    function bit zca_is_cti(int op);
      return op inside {GEN_FC_CMP_ZCA_CP_INSN_C_JAL, GEN_FC_CMP_ZCA_CP_INSN_C_J, GEN_FC_CMP_ZCA_CP_INSN_C_JR, GEN_FC_CMP_ZCA_CP_INSN_C_JALR, GEN_FC_CMP_ZCA_CP_INSN_C_BEQZ, GEN_FC_CMP_ZCA_CP_INSN_C_BNEZ};
    endfunction
    // the 3-bit register field of the CIW / CL / CS / CA / CB formats (rd' of c.addi4spn, rs1' otherwise); -1 for the other formats
    function int zca_reg3(int op, logic [15:0] i);
      if (op == GEN_FC_CMP_ZCA_CP_INSN_C_ADDI4SPN) return GEN_FC_CMP_ZCA_CP_REG3_R8 + int'(i[4:2]);
      if (op inside {GEN_FC_CMP_ZCA_CP_INSN_C_LW, GEN_FC_CMP_ZCA_CP_INSN_C_SW, GEN_FC_CMP_ZCA_CP_INSN_C_SRLI, GEN_FC_CMP_ZCA_CP_INSN_C_SRAI, GEN_FC_CMP_ZCA_CP_INSN_C_ANDI,
                     GEN_FC_CMP_ZCA_CP_INSN_C_SUB, GEN_FC_CMP_ZCA_CP_INSN_C_XOR, GEN_FC_CMP_ZCA_CP_INSN_C_OR, GEN_FC_CMP_ZCA_CP_INSN_C_AND, GEN_FC_CMP_ZCA_CP_INSN_C_BEQZ, GEN_FC_CMP_ZCA_CP_INSN_C_BNEZ})
        return GEN_FC_CMP_ZCA_CP_REG3_R8 + int'(i[9:7]);
      return -1;
    endfunction
    // the 5-bit register field of the CI / CR formats (rd, insn[11:7]) and of c.swsp (rs2, insn[6:2]); x0 has no bin
    function int zca_rd_full(int op, logic [15:0] i);
      logic [4:0] r;
      if (op inside {GEN_FC_CMP_ZCA_CP_INSN_C_ADDI, GEN_FC_CMP_ZCA_CP_INSN_C_LI, GEN_FC_CMP_ZCA_CP_INSN_C_LUI, GEN_FC_CMP_ZCA_CP_INSN_C_ADDI16SP, GEN_FC_CMP_ZCA_CP_INSN_C_SLLI,
                     GEN_FC_CMP_ZCA_CP_INSN_C_LWSP, GEN_FC_CMP_ZCA_CP_INSN_C_MV, GEN_FC_CMP_ZCA_CP_INSN_C_ADD, GEN_FC_CMP_ZCA_CP_INSN_C_JR, GEN_FC_CMP_ZCA_CP_INSN_C_JALR}) r = i[11:7];
      else if (op == GEN_FC_CMP_ZCA_CP_INSN_C_SWSP) r = i[6:2];
      else return -1;
      if (r == 1) return GEN_FC_CMP_ZCA_CP_RD_FULL_X1;
      if (r == 2) return GEN_FC_CMP_ZCA_CP_RD_FULL_X2;
      if (r >= 8 && r <= 15) return GEN_FC_CMP_ZCA_CP_RD_FULL_X8_15;
      if (r >= 16) return GEN_FC_CMP_ZCA_CP_RD_FULL_X16_31;
      if (r >= 3) return GEN_FC_CMP_ZCA_CP_RD_FULL_X3_7;
      return -1;
    endfunction
    // the pending 16-bit record samples once the following record's length is known (a Zcmp micro-op record is a 16-bit instruction)
    function void zca_flush(gen_rvfi_txn nxt);
      if (!zca_pend) return;
      zca_v[2] = (nxt == null) ? -1 : ((nxt.insn[1:0] != 2'b11 || nxt.ext_exp_valid) ? GEN_FC_CMP_ZCA_CP_NEXT_LEN_N16 : GEN_FC_CMP_ZCA_CP_NEXT_LEN_N32);
      zca_cg.sample(zca_v[0], zca_v[1], zca_v[2], zca_v[3], zca_v[4], zca_v[5], zca_v[6]);
      zca_pend = 0;
    endfunction

    // ---- CG-CMP-006: the 16-bit source word of a Zcmp stack instruction (rvfi_ext_expanded_insn): kind, rlist, spimm, N, stack_adj
    // ---- CG-CMP-009 helpers: the registers a push / pop rlist names, the cm.* kind of a halfword, the pattern sample
    function logic [4:0] zcmp_sx(int k);   // the Zcmp s-register list: s0 = x8, s1 = x9, s2..s11 = x18..x27
      return 5'((k < 2) ? 8 + k : 16 + k);
    endfunction
    function logic [31:0] zp_regs(int rlist);   // ra, then s0..s(rlist - 5); rlist 15 = all twelve
      logic [31:0] m = 32'h2; int n_s = (rlist == 15) ? 12 : (rlist >= 5) ? rlist - 4 : 0;
      for (int k = 0; k < n_s; k++) m[zcmp_sx(k)] = 1'b1;
      return m;
    endfunction
    function int hz_cm_kind(logic [15:0] hw);   // the fall-through halfword: a Zcmp stack op or a move, else -1
      if (hw[15:13] == 3'b101 && hw[1:0] == 2'b10) case (hw[12:8])
        5'b11000: return GEN_FC_CMP_ZCMP_HAZARD_CP_FT_KIND_CM_PUSH; 5'b11010: return GEN_FC_CMP_ZCMP_HAZARD_CP_FT_KIND_CM_POP;
        5'b11100: return GEN_FC_CMP_ZCMP_HAZARD_CP_FT_KIND_CM_POPRETZ; 5'b11110: return GEN_FC_CMP_ZCMP_HAZARD_CP_FT_KIND_CM_POPRET;
        default: ;
      endcase
      if (hw[15:10] == 6'b101011 && hw[1:0] == 2'b10) return hw[6:5] == 2'b01 ? GEN_FC_CMP_ZCMP_HAZARD_CP_FT_KIND_CM_MVSA01 : hw[6:5] == 2'b11 ? GEN_FC_CMP_ZCMP_HAZARD_CP_FT_KIND_CM_MVA01S : -1;
      return -1;
    endfunction
    localparam int unsigned HZ_LAT_MIN1 = 1, HZ_LAT_SHORT_MAX = 4;   // the data-bus response classes: 1 / 2..4 / 5 and above
    function int hz_delay_cls(int unsigned lat);
      return (lat == HZ_LAT_MIN1) ? GEN_FC_CMP_ZCMP_HAZARD_CP_DMEM_DELAY_MIN1 : (lat <= HZ_LAT_SHORT_MAX) ? GEN_FC_CMP_ZCMP_HAZARD_CP_DMEM_DELAY_SHORT : GEN_FC_CMP_ZCMP_HAZARD_CP_DMEM_DELAY_LONG;
    endfunction
    function int hz_delay_of(int pushpop_cls);   // the sequence's class (gen_cmp_zcmp_pushpop_cg's) by name; the mixed class has no hazard bin
      case (pushpop_cls)
        GEN_FC_CMP_ZCMP_PUSHPOP_CP_DMEM_DELAY_MIN1:  return GEN_FC_CMP_ZCMP_HAZARD_CP_DMEM_DELAY_MIN1;
        GEN_FC_CMP_ZCMP_PUSHPOP_CP_DMEM_DELAY_SHORT: return GEN_FC_CMP_ZCMP_HAZARD_CP_DMEM_DELAY_SHORT;
        GEN_FC_CMP_ZCMP_PUSHPOP_CP_DMEM_DELAY_LONG:  return GEN_FC_CMP_ZCMP_HAZARD_CP_DMEM_DELAY_LONG;
        default: return -1;
      endcase
    endfunction
    function int hz_rlist_cls(int rlist);
      return (rlist == 4) ? GEN_FC_CMP_ZCMP_HAZARD_CP_RLIST_CLASS_R4 : (rlist == 15) ? GEN_FC_CMP_ZCMP_HAZARD_CP_RLIST_CLASS_R15 : GEN_FC_CMP_ZCMP_HAZARD_CP_RLIST_CLASS_R5_14;
    endfunction
    function void hz_sample(int pattern, int ft, int ret_once, int redirect_once, int rlist_cls, int delay, int delta_uop);
      int v [7];
      if (hz_cg == null) return;
      v[0] = pattern; v[1] = ft; v[2] = ret_once; v[3] = redirect_once; v[4] = rlist_cls; v[5] = delay; v[6] = delta_uop;
      hz_cg.sample(v[0], v[1], v[2], v[3], v[4], v[5], v[6]); ut_last_hz = v; n_hz++;
    endfunction
    // the pended popret / popretz: its return target must retire next (cp_ret_once, popret(z)_then_target; cp_redirect_once counts the fetches
    // of the target word between the ret and its retirement while the icache is disabled)
    function void hz_flush(gen_rvfi_txn nxt);
      if (!hz_pend) return;
      if (nxt != null && !nxt.ext_exp_valid && nxt.pc_rdata == zp_ret_target) begin
        int redir = -1;
        if (!icache_en_tracked) begin int nf = 0; foreach (ib_addr[i]) if (ib_addr[i][31:2] == zp_ret_target[31:2] && ib_rv[i] > hz_pend_cycle && ib_rv[i] <= nxt.cycle) nf++; redir = (nf == 1) ? GEN_FC_CMP_ZCMP_HAZARD_CP_REDIRECT_ONCE_YES : -1; end
        hz_sample(hz_pend_kind == GEN_FC_CMP_ZCMP_PUSHPOP_CP_INSN_CM_POPRET ? GEN_FC_CMP_ZCMP_HAZARD_CP_HAZARD_POPRET_THEN_TARGET : GEN_FC_CMP_ZCMP_HAZARD_CP_HAZARD_POPRETZ_THEN_TARGET,
                  -1, GEN_FC_CMP_ZCMP_HAZARD_CP_RET_ONCE_YES, redir, hz_pend_v[4], hz_pend_v[5], hz_pend_v[6]);
      end
      hz_pend = 0;
    endfunction
    function void zp_start(gen_rvfi_txn t);
      logic [15:0] w = t.ext_exp_insn;
      zp_in = 1; zp_pc = t.pc_rdata; zp_count = 0; zp_mem_k = 0; zp_sp_valid = 0; zp_order_ok = 1; zp_tags_ok = 1; zp_ret_align = -1; zp_prev_reg = 5'd31;
      zp_mhpm10_first = t.ext_mhpmcounters[7]; zp_win_start = prev_rec_cycle;
      zp_load_addr.delete(); zp_last_uop_cycle = t.cycle; zp_uop_stall = 0; zp_ra_load_cycle = 0; zp_ret_target = 0;
      hz_b2b_prev = (have_last && last_t.ext_exp_valid && last_t.ext_exp_last) ? prev_seq_kind : -1;   // the record before this first micro-op closed a sequence
      prev_seq_kind = -1;   // set again only by a sampled push / pop sequence: a move pair or an unsampled sequence closes no pair
      hz_prev_st_valid = have_last && !last_t.ext_exp_valid && last_t.mem_wmask != 0; hz_prev_st_addr = {last_t.mem_addr[31:2], 2'b00};   // the store record before the sequence
      hz_prev_wr = prev_wr; hz_prev_ld = prev_ld;   // the instruction before the sequence
      zp_kind = -1;
      if (w[15:13] == 3'b101 && w[1:0] == 2'b10) case (w[12:8])
        5'b11000: zp_kind = GEN_FC_CMP_ZCMP_PUSHPOP_CP_INSN_CM_PUSH;
        5'b11010: zp_kind = GEN_FC_CMP_ZCMP_PUSHPOP_CP_INSN_CM_POP;
        5'b11100: zp_kind = GEN_FC_CMP_ZCMP_PUSHPOP_CP_INSN_CM_POPRETZ;
        5'b11110: zp_kind = GEN_FC_CMP_ZCMP_PUSHPOP_CP_INSN_CM_POPRET;
        default:  zp_kind = -1;
      endcase
      zp_rlist = int'(w[7:4]); zp_spimm = int'(w[3:2]);
      zp_mv = mv_form(w);
      if (zp_mv >= 0) begin   // the sources: a0 / a1 for cm.mvsa01, r1s' / r2s' for cm.mva01s; the neighbour facts come from the instruction before
        logic [31:0] srcs;
        mv_r1 = int'(w[9:7]); mv_r2 = int'(w[4:2]); mv_ok = 1;
        srcs = (zp_mv == GEN_FC_CMP_ZCMP_MV_CP_INSN_CM_MVSA01) ? (32'h1 << 10) | (32'h1 << 11) : (32'h1 << zcmp_sreg(mv_r1)) | (32'h1 << zcmp_sreg(mv_r2));
        mv_hz = ((prev_wr & srcs) == 0) ? GEN_FC_CMP_ZCMP_MV_CP_HAZARD_SRC_NONE : prev_ld ? GEN_FC_CMP_ZCMP_MV_CP_HAZARD_SRC_LOAD_PREV : GEN_FC_CMP_ZCMP_MV_CP_HAZARD_SRC_ALU_PREV;
        mv_prev = prev_mv;
      end
      zp_n = (zp_rlist == 15) ? 13 : zp_rlist - 3;                                       // rlist 15 saves x27..x18, x9, x8, x1
      zp_adj = ((zp_rlist <= 7) ? 16 : (zp_rlist <= 11) ? 32 : (zp_rlist <= 14) ? 48 : 64) + zp_spimm * 16;   // zcmp.adoc stack_adj (RV32)
    endfunction
    // the plan's latency classes over the data-bus responses whose rvalid fell after the record before the sequence and up to the last
    // micro-op's record: min1 {1}, short {[2:4]}, long {[5:$]}, mixed otherwise; -1 when no response fell in the window
    function int zp_delay_cls(int unsigned lo, int unsigned hi);
      bit any = 0, all1 = 1, all_short = 1, all_long = 1;
      foreach (dlat_cyc[i]) if (dlat_cyc[i] > lo && dlat_cyc[i] <= hi) begin
        any = 1; all1 &= (dlat_lat[i] == HZ_LAT_MIN1); all_short &= (dlat_lat[i] > HZ_LAT_MIN1 && dlat_lat[i] <= HZ_LAT_SHORT_MAX); all_long &= (dlat_lat[i] > HZ_LAT_SHORT_MAX);
      end
      if (!any) return -1;
      return all1 ? GEN_FC_CMP_ZCMP_PUSHPOP_CP_DMEM_DELAY_MIN1 : all_short ? GEN_FC_CMP_ZCMP_PUSHPOP_CP_DMEM_DELAY_SHORT : all_long ? GEN_FC_CMP_ZCMP_PUSHPOP_CP_DMEM_DELAY_LONG : GEN_FC_CMP_ZCMP_PUSHPOP_CP_DMEM_DELAY_MIXED;
    endfunction
    // the pending sequence samples on the record after it (its mhpmcounter10 counts through the last micro-op)
    function void zcmp_flush(gen_rvfi_txn nxt);
      if (!zcmp_pend) return;
      zcmp_v[9] = (nxt != null && nxt.ext_mhpmcounters[7] - zp_mhpm10_first == 32'd1) ? GEN_FC_CMP_ZCMP_PUSHPOP_CP_MINSTRET_ONCE_YES : -1;
      if (zcmp_v[9] < 0) n_zcmp_minstret_no++;
      zcmp_cg.sample(zcmp_v[0], zcmp_v[1], zcmp_v[2], zcmp_v[3], zcmp_v[4], zcmp_v[5], zcmp_v[6], zcmp_v[7], zcmp_v[8], zcmp_v[9], zcmp_v[10], zcmp_v[11], zcmp_v[12]);
      ut_last_zcmp = zcmp_v;
      zcmp_pend = 0;
    endfunction
    // one micro-op record of an open sequence; samples the group on the last micro-op of a sequence that never trapped
    function void zp_step(gen_rvfi_txn t);
      bit is_st; int unsigned bytes; logic [4:0] r; logic [31:0] want;
      zp_count++;
      if (zp_count > 1 && t.cycle - zp_last_uop_cycle > 1) zp_uop_stall = 1; zp_last_uop_cycle = t.cycle;   // cp_delta_uop
      if (!t.ext_exp_last && t.pc_wdata != t.pc_rdata) zp_tags_ok = 0;   // intermediate micro-ops report their own pc (R9)
      if (t.insn[1:0] != 2'b11) zp_tags_ok = 0;                            // every micro-op word is the synthesized 32-bit one
      if (zp_mv >= 0) begin   // a move micro-op: `addi dst, src, 0` with the register pair of its position
        logic [4:0] want_rd, want_rs1; logic [4:0] sreg = zcmp_sreg(zp_count == 1 ? mv_r1 : mv_r2); logic [4:0] areg = (zp_count == 1) ? 5'd10 : 5'd11;
        if (zp_mv == GEN_FC_CMP_ZCMP_MV_CP_INSN_CM_MVSA01) begin want_rd = sreg; want_rs1 = areg; end else begin want_rd = areg; want_rs1 = sreg; end
        if (t.insn[6:0] != ibex_pkg::OPCODE_OP_IMM || t.insn[14:12] != 3'b000 || t.insn[31:20] != 12'h0 || t.insn[11:7] != want_rd || t.insn[19:15] != want_rs1 || zp_count > 2) mv_ok = 0;
        if (zp_count == 1) mv_src1 = t.rs1_rdata; else mv_src2 = t.rs1_rdata;
        if (t.ext_exp_last) begin
          mv_v[0] = zp_mv; mv_v[1] = mv_r1; mv_v[2] = mv_r2;
          mv_v[3] = (mv_r1 == mv_r2) ? GEN_FC_CMP_ZCMP_MV_CP_EQUAL_YES : GEN_FC_CMP_ZCMP_MV_CP_EQUAL_NO;
          mv_v[4] = (mv_src1 == mv_src2) ? GEN_FC_CMP_ZCMP_MV_CP_SRC_VALUES_SAME : GEN_FC_CMP_ZCMP_MV_CP_SRC_VALUES_DISTINCT;
          mv_v[5] = (mv_prev >= 0 && mv_prev != zp_mv) ? mv_b2b(mv_prev, zp_mv) : GEN_FC_CMP_ZCMP_MV_CP_B2B_NONE;   // the neighbour after is checked at the flush
          mv_v[6] = mv_hz;
          mv_v[7] = (zp_count == 2 && mv_ok && zp_tags_ok) ? GEN_FC_CMP_ZCMP_MV_CP_UOP_COUNT_OK_YES : -1;
          if (mv_v[7] < 0) begin
            n_mv_miss++;
            `uvm_info("GEN_FCOV_MV", $sformatf("legal move pair (form %0d, r1s' %0d, r2s' %0d) at pc %08h: micro-ops do not match the expansion (count %0d, form ok %0d, tags ok %0d)", zp_mv, mv_r1, mv_r2, t.pc_rdata, zp_count, mv_ok, zp_tags_ok), UVM_LOW)
          end
          mv_pend = 1; cur_mv = zp_mv; n_mv++;
        end
      end
      if (gen_insn_mem_access(t.insn, is_st, bytes) && t.insn[19:15] == 5'd2) begin   // sp-based store (push) / load (pop*)
        if (!zp_sp_valid) begin zp_sp = t.rs1_rdata; zp_sp_valid = 1; end
        r = is_st ? t.insn[24:20] : t.insn[11:7];
        zp_mem_k++;
        want = is_st ? zp_sp - 32'(4 * zp_mem_k) : zp_sp + 32'(zp_adj) - 32'(4 * zp_mem_k);
        if (t.mem_addr != want || (zp_mem_k > 1 && r >= zp_prev_reg)) zp_order_ok = 0;   // descending registers, addresses as predicted
        zp_prev_reg = r;
        if (!is_st) begin zp_load_addr.push_back({t.mem_addr[31:2], 2'b00}); if (r == 5'd1) begin zp_ra_load_cycle = t.cycle; zp_ra_addr = {t.mem_addr[31:2], 2'b00}; end end   // the pop's slots; the ra load
      end
      if (t.insn[6:0] == ibex_pkg::OPCODE_JALR) zp_ret_target = t.rs1_rdata;   // the ret's target (the loaded ra)
      if (t.insn[6:0] == ibex_pkg::OPCODE_JALR)   // the jalr x0, 0(ra) of popret / popretz: the loaded ra
        zp_ret_align = t.rs1_rdata[0] ? GEN_FC_CMP_ZCMP_PUSHPOP_CP_RET_ALIGN_ODD : t.rs1_rdata[1] ? GEN_FC_CMP_ZCMP_PUSHPOP_CP_RET_ALIGN_HALF : GEN_FC_CMP_ZCMP_PUSHPOP_CP_RET_ALIGN_WORD;
      if (t.ext_exp_last) begin
        if (zp_kind >= 0 && zp_sp_valid) begin
          int want_n = zp_n + ((zp_kind == GEN_FC_CMP_ZCMP_PUSHPOP_CP_INSN_CM_PUSH || zp_kind == GEN_FC_CMP_ZCMP_PUSHPOP_CP_INSN_CM_POP) ? 1 : (zp_kind == GEN_FC_CMP_ZCMP_PUSHPOP_CP_INSN_CM_POPRET) ? 2 : 3);
          bit is_push = (zp_kind == GEN_FC_CMP_ZCMP_PUSHPOP_CP_INSN_CM_PUSH);
          int wrap = is_push ? ((zp_sp < 32'(4 * zp_n)) ? GEN_FC_CMP_ZCMP_PUSHPOP_CP_SP_WRAP_PUSH_BELOW_ZERO : GEN_FC_CMP_ZCMP_PUSHPOP_CP_SP_WRAP_NONE)
                             : (({1'b0, zp_sp} + 33'(zp_adj) >= 33'h1_0000_0000) ? GEN_FC_CMP_ZCMP_PUSHPOP_CP_SP_WRAP_POP_ABOVE_MAX : GEN_FC_CMP_ZCMP_PUSHPOP_CP_SP_WRAP_NONE);
          n_zcmp++;
          if (zp_count != want_n) n_zcmp_uop_no++;
          if (!(zp_order_ok && zp_mem_k == zp_n)) n_zcmp_order_no++;
          if (!zp_tags_ok) n_zcmp_tags_no++;
          zcmp_v[0] = zp_kind; zcmp_v[1] = GEN_FC_CMP_ZCMP_PUSHPOP_CP_RLIST_R4 + (zp_rlist - 4); zcmp_v[2] = GEN_FC_CMP_ZCMP_PUSHPOP_CP_SPIMM_S0 + zp_spimm;
          zcmp_v[3] = GEN_FC_CMP_ZCMP_PUSHPOP_CP_STACK_ADJ_A16 + (zp_adj / 16 - 1); zcmp_v[4] = GEN_FC_CMP_ZCMP_PUSHPOP_CP_SP_ALIGN_ALIGNED + int'(zp_sp[1:0]); zcmp_v[5] = wrap;
          zcmp_v[6] = (zp_count == want_n) ? GEN_FC_CMP_ZCMP_PUSHPOP_CP_UOP_COUNT_OK_YES : -1; zcmp_v[7] = (zp_order_ok && zp_mem_k == zp_n) ? GEN_FC_CMP_ZCMP_PUSHPOP_CP_ORDER_OK_YES : -1;
          zcmp_v[8] = zp_tags_ok ? GEN_FC_CMP_ZCMP_PUSHPOP_CP_RVFI_TAGS_OK_YES : -1; zcmp_v[9] = -1;   // minstret: at the flush
          zcmp_v[10] = is_push || zp_kind == GEN_FC_CMP_ZCMP_PUSHPOP_CP_INSN_CM_POP ? -1 : zp_ret_align; zcmp_v[11] = zp_delay_cls(zp_win_start, t.cycle);
          zcmp_v[12] = gen_isa_read_csr(GEN_CSR_CPUCTRLSTS)[GEN_CPUCTRLSTS_DUMMY_INSTR_EN_BIT] ? GEN_FC_CMP_ZCMP_PUSHPOP_CP_DUMMY_EN_ON : GEN_FC_CMP_ZCMP_PUSHPOP_CP_DUMMY_EN_OFF;
          zcmp_pend = 1;
          begin   // CG-CMP-009: the neighbour patterns of this sequence, one sample per pattern seen
            int rl = hz_rlist_cls(zp_rlist), dl = hz_delay_of(zcmp_v[11]), du = zp_uop_stall ? GEN_FC_CMP_ZCMP_HAZARD_CP_DELTA_UOP_SOME_STALL : GEN_FC_CMP_ZCMP_HAZARD_CP_DELTA_UOP_ALL_ONE;
            bit is_pop = (zp_kind == GEN_FC_CMP_ZCMP_PUSHPOP_CP_INSN_CM_POP), is_ret = (zp_kind == GEN_FC_CMP_ZCMP_PUSHPOP_CP_INSN_CM_POPRET || zp_kind == GEN_FC_CMP_ZCMP_PUSHPOP_CP_INSN_CM_POPRETZ);
            if (is_push && (hz_prev_wr & zp_regs(zp_rlist)) != 0)
              hz_sample(hz_prev_ld ? GEN_FC_CMP_ZCMP_HAZARD_CP_HAZARD_LOAD_PUSHED_REG_THEN_PUSH : GEN_FC_CMP_ZCMP_HAZARD_CP_HAZARD_WRITE_PUSHED_REG_THEN_PUSH, -1, -1, -1, rl, dl, du);
            if (is_push && hz_b2b_prev == GEN_FC_CMP_ZCMP_PUSHPOP_CP_INSN_CM_POP) hz_sample(GEN_FC_CMP_ZCMP_HAZARD_CP_HAZARD_POP_THEN_PUSH_B2B, -1, -1, -1, rl, dl, du);
            if (is_pop && hz_b2b_prev == GEN_FC_CMP_ZCMP_PUSHPOP_CP_INSN_CM_PUSH) hz_sample(GEN_FC_CMP_ZCMP_HAZARD_CP_HAZARD_PUSH_THEN_POP_B2B, -1, -1, -1, rl, dl, du);
            if (is_pop || is_ret) begin bit same = 0; if (hz_prev_st_valid) foreach (zp_load_addr[i]) if (zp_load_addr[i] == hz_prev_st_addr) same = 1;   // the store immediately before the pop
              if (same) hz_sample(GEN_FC_CMP_ZCMP_HAZARD_CP_HAZARD_STORE_SAME_SLOT_THEN_POP, -1, -1, -1, rl, dl, du); end
            if (is_ret) begin
              logic [31:0] w = gen_isa_read_word({zp_pc[31:2], 2'b00} + (zp_pc[1] ? 32'd4 : 32'd0)); logic [15:0] hw = zp_pc[1] ? w[15:0] : w[31:16];   // the halfword at pc + 2
              int ft = hz_cm_kind(hw);
              begin   // the ra load's response later than the cycle after its grant defers the addi (C-9); the min1 response never does (the plan's ignore)
                int ra_lat = -1; foreach (dlat_addr[i]) if (dlat_addr[i] == zp_ra_addr && dlat_cyc[i] <= t.cycle) ra_lat = dlat_lat[i];
                if (zp_ra_load_cycle != 0 && ra_lat > 1) hz_sample(GEN_FC_CMP_ZCMP_HAZARD_CP_HAZARD_POPRET_RA_DEFERRED, -1, -1, -1, rl, dl, du);
              end
              if (ft >= 0) hz_sample(zp_kind == GEN_FC_CMP_ZCMP_PUSHPOP_CP_INSN_CM_POPRET ? GEN_FC_CMP_ZCMP_HAZARD_CP_HAZARD_POPRET_FT_CM : GEN_FC_CMP_ZCMP_HAZARD_CP_HAZARD_POPRETZ_FT_CM, ft, -1, -1, rl, dl, du);
              hz_pend = 1; hz_pend_kind = zp_kind; hz_pend_v[4] = rl; hz_pend_v[5] = dl; hz_pend_v[6] = du; hz_pend_cycle = t.cycle;   // the target check on the next record
            end
            prev_seq_kind = zp_kind;
          end
        end
        zp_in = 0;
      end
    endfunction
    // ---- CG-CMP-007 helpers: the move form of a Zcmp source word (-1 for the stack forms), the b2b bin of an ordered pair
    // the Zcmp 3-bit sreg field: s0 = x8, s1 = x9, s2..s7 = x18..x23 (rtl/ibex_compressed_decoder.sv:153-165)
    function logic [4:0] zcmp_sreg(int r);   // the 3-bit sreg field names the first eight of the list
      return zcmp_sx(r);
    endfunction
    function int mv_form(logic [15:0] w);
      if (w[15:13] != 3'b101 || w[12:10] != 3'b011 || w[1:0] != 2'b10) return -1;
      return (w[6:5] == 2'b01) ? GEN_FC_CMP_ZCMP_MV_CP_INSN_CM_MVSA01 : (w[6:5] == 2'b11) ? GEN_FC_CMP_ZCMP_MV_CP_INSN_CM_MVA01S : -1;
    endfunction
    function int mv_b2b(int first, int second);
      return (first == GEN_FC_CMP_ZCMP_MV_CP_INSN_CM_MVSA01) ? GEN_FC_CMP_ZCMP_MV_CP_B2B_MVSA01_THEN_MVA01S : GEN_FC_CMP_ZCMP_MV_CP_B2B_MVA01S_THEN_MVSA01;
    endfunction
    // the pending move pair samples once the following record is known: the other move form opening there is the b2b neighbour after
    function void mv_flush(gen_rvfi_txn nxt);
      if (!mv_pend) return;
      if (nxt != null && mv_v[5] == GEN_FC_CMP_ZCMP_MV_CP_B2B_NONE && nxt.ext_exp_valid && !zp_in) begin
        int k = mv_form(nxt.ext_exp_insn);
        if (k >= 0 && k != mv_v[0]) mv_v[5] = mv_b2b(mv_v[0], k);
      end
      mv_cg.sample(mv_v[0], mv_v[1], mv_v[2], mv_v[3], mv_v[4], mv_v[5], mv_v[6], mv_v[7]);
      begin   // CG-CMP-009: the move patterns (no rlist; the delay class is the preceding load's response)
        int du = zp_uop_stall ? GEN_FC_CMP_ZCMP_HAZARD_CP_DELTA_UOP_SOME_STALL : GEN_FC_CMP_ZCMP_HAZARD_CP_DELTA_UOP_ALL_ONE;
        if (mv_v[0] == GEN_FC_CMP_ZCMP_MV_CP_INSN_CM_MVA01S && mv_v[6] == GEN_FC_CMP_ZCMP_MV_CP_HAZARD_SRC_LOAD_PREV) begin
          int dl = -1; foreach (dlat_cyc[i]) if (dlat_cyc[i] <= zp_win_start + 1) dl = hz_delay_cls(dlat_lat[i]);
          hz_sample(GEN_FC_CMP_ZCMP_HAZARD_CP_HAZARD_LOAD_THEN_MVA01S, -1, -1, -1, -1, dl, du);
        end
        if (mv_v[0] == GEN_FC_CMP_ZCMP_MV_CP_INSN_CM_MVA01S && mv_v[5] == GEN_FC_CMP_ZCMP_MV_CP_B2B_MVSA01_THEN_MVA01S) hz_sample(GEN_FC_CMP_ZCMP_HAZARD_CP_HAZARD_MVSA01_THEN_MVA01S, -1, -1, -1, -1, -1, du);
      end
      ut_last_mv = mv_v;
      mv_pend = 0;
    endfunction

    // ---- CG-ISA-007: the compare classes in plan precedence (the named operand pairs before equal and the sign-order classes)
    function int br_cmp_cls(logic [31:0] a, logic [31:0] b);
      if (a == 32'h8000_0000 && b == 32'h8000_0000) return GEN_FC_ISA_BRANCH_CP_CMP_CLASS_BOTH_MSB_EQ;
      if (a == 32'h8000_0000 && b == 32'h0) return GEN_FC_ISA_BRANCH_CP_CMP_CLASS_INTMIN_ZERO;
      if (a == 32'h0 && b == 32'h8000_0000) return GEN_FC_ISA_BRANCH_CP_CMP_CLASS_ZERO_INTMIN;
      if (a == 32'h0 && b == 32'hffff_ffff) return GEN_FC_ISA_BRANCH_CP_CMP_CLASS_ZERO_ONES;
      if (a == 32'hffff_ffff && b == 32'h0) return GEN_FC_ISA_BRANCH_CP_CMP_CLASS_ONES_ZERO;
      if (a == b) return GEN_FC_ISA_BRANCH_CP_CMP_CLASS_EQUAL;
      if ($signed(a) < $signed(b) && a > b) return GEN_FC_ISA_BRANCH_CP_CMP_CLASS_SLT_UGT;
      if ($signed(a) > $signed(b) && a < b) return GEN_FC_ISA_BRANCH_CP_CMP_CLASS_SGT_ULT;
      return GEN_FC_ISA_BRANCH_CP_CMP_CLASS_RAND;
    endfunction
    function int br_off_cls(int imm, bit c16);
      if (imm == 0) return GEN_FC_ISA_BRANCH_CP_OFFSET_SELF;
      if (imm == (c16 ? 254 : 4094)) return GEN_FC_ISA_BRANCH_CP_OFFSET_MAX_FWD;
      if (imm == (c16 ? -256 : -4096)) return GEN_FC_ISA_BRANCH_CP_OFFSET_MAX_BWD;
      return (imm > 0) ? GEN_FC_ISA_BRANCH_CP_OFFSET_POS_RAND : GEN_FC_ISA_BRANCH_CP_OFFSET_NEG_RAND;
    endfunction
    // a BRANCH record (funct3 000 / 001 / 1xx) or c.beqz / c.bnez in its 16-bit form; taken = the next pc is not the sequential one
    function bit br_sample(gen_rvfi_txn t);
      int op, imm; bit c16, taken; logic [31:0] rs2, target; logic signed [33:0] ssum;
      if (t.insn[1:0] == 2'b11) begin
        if (t.insn[6:0] != ibex_pkg::OPCODE_BRANCH || t.insn[14:13] == 2'b01) return 0;
        case (t.insn[14:12])
          3'b000: op = GEN_FC_ISA_BRANCH_CP_OP_BEQ; 3'b001: op = GEN_FC_ISA_BRANCH_CP_OP_BNE;  3'b100: op = GEN_FC_ISA_BRANCH_CP_OP_BLT;
          3'b101: op = GEN_FC_ISA_BRANCH_CP_OP_BGE; 3'b110: op = GEN_FC_ISA_BRANCH_CP_OP_BLTU; default: op = GEN_FC_ISA_BRANCH_CP_OP_BGEU;
        endcase
        imm = signed'({t.insn[31], t.insn[7], t.insn[30:25], t.insn[11:8], 1'b0});   // imm_b, 13 bits
        c16 = 0; rs2 = t.rs2_rdata;
      end else begin
        if (t.insn[1:0] != 2'b01 || t.insn[15:14] != 2'b11) return 0;   // c.beqz 110, c.bnez 111
        op = t.insn[13] ? GEN_FC_ISA_BRANCH_CP_OP_C_BNEZ : GEN_FC_ISA_BRANCH_CP_OP_C_BEQZ;
        imm = signed'({t.insn[12], t.insn[6:5], t.insn[2], t.insn[11:10], t.insn[4:3], 1'b0});   // CB offset, 9 bits
        c16 = 1; rs2 = 32'h0;   // the compare is against x0
      end
      taken = (t.pc_wdata != t.pc_rdata + (c16 ? 32'd2 : 32'd4));
      target = t.pc_rdata + 32'(imm);
      ssum = 34'(signed'({2'b00, t.pc_rdata})) + 34'(imm);   // the 33-bit signed target: a wrap leaves [0, 2^32)
      n_br++;
      br_cg.sample(op, taken ? GEN_FC_ISA_BRANCH_CP_TAKEN_YES : GEN_FC_ISA_BRANCH_CP_TAKEN_NO, br_cmp_cls(t.rs1_rdata, rs2), br_off_cls(imm, c16),
                   target[1] ? GEN_FC_ISA_BRANCH_CP_TARGET_ALIGN_HALF : GEN_FC_ISA_BRANCH_CP_TARGET_ALIGN_WORD,
                   taken ? ((ssum[33] || ssum[32]) ? GEN_FC_ISA_BRANCH_CP_WRAP_YES : GEN_FC_ISA_BRANCH_CP_WRAP_NO) : -1);
      return 1;
    endfunction

    // ---- CG-CSR-002: the tracked CSRs in plan order and the bits Ibex lets a write change (mcounteren: bit 0 and 2..MHPMCounterNum+2)
    function int csr_idx(logic [11:0] a);
      if (a == ibex_pkg::CSR_MSTATUS) return GEN_FC_CSR_TRAP_SETUP_WARL_CP_CSR_MSTATUS;
      if (a == ibex_pkg::CSR_MISA) return GEN_FC_CSR_TRAP_SETUP_WARL_CP_CSR_MISA;
      if (a == ibex_pkg::CSR_MIE) return GEN_FC_CSR_TRAP_SETUP_WARL_CP_CSR_MIE;
      if (a == ibex_pkg::CSR_MTVEC) return GEN_FC_CSR_TRAP_SETUP_WARL_CP_CSR_MTVEC;
      if (a == ibex_pkg::CSR_MCOUNTEREN) return GEN_FC_CSR_TRAP_SETUP_WARL_CP_CSR_MCOUNTEREN;
      if (a == ibex_pkg::CSR_MSTATUSH) return GEN_FC_CSR_TRAP_SETUP_WARL_CP_CSR_MSTATUSH;
      if (a == ibex_pkg::CSR_MENVCFG) return GEN_FC_CSR_TRAP_SETUP_WARL_CP_CSR_MENVCFG;
      if (a == ibex_pkg::CSR_MENVCFGH) return GEN_FC_CSR_TRAP_SETUP_WARL_CP_CSR_MENVCFGH;
      return -1;
    endfunction
    function logic [31:0] csr_wmask(int i);
      case (i)
        GEN_FC_CSR_TRAP_SETUP_WARL_CP_CSR_MSTATUS:    return (32'h1 << ibex_pkg::CSR_MSTATUS_MIE_BIT) | (32'h1 << ibex_pkg::CSR_MSTATUS_MPIE_BIT) | (32'h3 << ibex_pkg::CSR_MSTATUS_MPP_BIT_LOW) |
                                                             (32'h1 << ibex_pkg::CSR_MSTATUS_MPRV_BIT) | (32'h1 << ibex_pkg::CSR_MSTATUS_TW_BIT);
        GEN_FC_CSR_TRAP_SETUP_WARL_CP_CSR_MIE:        return 32'h7FFF_0888;   // software, timer, external, fast 16..30
        GEN_FC_CSR_TRAP_SETUP_WARL_CP_CSR_MTVEC:      return 32'hFFFF_FF00;
        GEN_FC_CSR_TRAP_SETUP_WARL_CP_CSR_MCOUNTEREN: return 32'h1 | (((32'h1 << (GEN_MHPM_COUNTER_NUM + 3)) - 1) & ~32'h3);
        default:                                      return 32'h0;
      endcase
    endfunction
    function int mie_w_cls(logic [31:0] v);
      logic [31:0] std = v & 32'h0000_0888, fast = v & 32'h7FFF_0000;
      if (fast == 32'h7FFF_0000) return GEN_FC_CSR_TRAP_SETUP_WARL_CP_MIE_W_ALL_FAST;
      if (std != 0 && fast != 0) return GEN_FC_CSR_TRAP_SETUP_WARL_CP_MIE_W_STD_FAST;
      if (std != 0) return GEN_FC_CSR_TRAP_SETUP_WARL_CP_MIE_W_STD_ONLY;
      if (fast != 0) return GEN_FC_CSR_TRAP_SETUP_WARL_CP_MIE_W_FAST_ONLY;
      return (v != 0) ? GEN_FC_CSR_TRAP_SETUP_WARL_CP_MIE_W_RO_ONLY : -1;
    endfunction
    function int mcen_w_cls(logic [31:0] v);
      logic [31:0] low = v & ((32'h1 << (GEN_MHPM_COUNTER_NUM + 3)) - 1);
      if (v == 32'hffff_ffff) return GEN_FC_CSR_TRAP_SETUP_WARL_CP_MCEN_W_ALL1;
      if (low != 0 && (low & (low - 1)) == 0 && low == v) begin   // exactly one bit, in the counter field
        if (low == 32'h1) return GEN_FC_CSR_TRAP_SETUP_WARL_CP_MCEN_W_CY;
        if (low == 32'h2) return GEN_FC_CSR_TRAP_SETUP_WARL_CP_MCEN_W_TM_RO;
        if (low == 32'h4) return GEN_FC_CSR_TRAP_SETUP_WARL_CP_MCEN_W_IR;
        return GEN_FC_CSR_TRAP_SETUP_WARL_CP_MCEN_W_HPM3 + ($clog2(low) - 3);
      end
      return (v != 0 && low == 0) ? GEN_FC_CSR_TRAP_SETUP_WARL_CP_MCEN_W_HI_RO : -1;   // only bits above the counter field
    endfunction
    // the pair closes on the read-back: the write operand classifies cp_wpat, the effective written value the field coverpoints
    function void csr_pair_sample(int i);
      int wpat, mpp = -1, mie_b = -1, mpie_b = -1, mprv_b = -1, tw_b = -1, tmode = -1, tlo = -1, tbase = -1, miew = -1, gate = -1, mcw = -1;
      logic [31:0] v = csr_eff[i], w = csr_wval[i], mask = csr_wmask(i);
      wpat = (w == 32'h0) ? GEN_FC_CSR_TRAP_SETUP_WARL_CP_WPAT_ALL0 : (w == 32'hffff_ffff) ? GEN_FC_CSR_TRAP_SETUP_WARL_CP_WPAT_ALL1 :
             (w == 32'h8000_0000) ? GEN_FC_CSR_TRAP_SETUP_WARL_CP_WPAT_MSB_ONLY : ((w & ~mask) == 0) ? GEN_FC_CSR_TRAP_SETUP_WARL_CP_WPAT_LEGAL_ONLY :
             ((w & mask) == 0 && mask != 0) ? GEN_FC_CSR_TRAP_SETUP_WARL_CP_WPAT_ILLEGAL_ONLY : GEN_FC_CSR_TRAP_SETUP_WARL_CP_WPAT_RAND;   // a CSR without writable bits has no illegal-only class: mixed patterns are rand
      if (csr_eff_ok[i]) case (i)
        GEN_FC_CSR_TRAP_SETUP_WARL_CP_CSR_MSTATUS: begin
          mpp = int'(v[ibex_pkg::CSR_MSTATUS_MPP_BIT_HIGH:ibex_pkg::CSR_MSTATUS_MPP_BIT_LOW]); mie_b = int'(v[ibex_pkg::CSR_MSTATUS_MIE_BIT]); mpie_b = int'(v[ibex_pkg::CSR_MSTATUS_MPIE_BIT]);
          mprv_b = int'(v[ibex_pkg::CSR_MSTATUS_MPRV_BIT]); tw_b = int'(v[ibex_pkg::CSR_MSTATUS_TW_BIT]);
        end
        GEN_FC_CSR_TRAP_SETUP_WARL_CP_CSR_MTVEC: begin
          tmode = int'(v[1:0]); tlo = (v[7:2] != 0) ? GEN_FC_CSR_TRAP_SETUP_WARL_CP_MTVEC_LO_W_NONZERO : GEN_FC_CSR_TRAP_SETUP_WARL_CP_MTVEC_LO_W_ZERO;
          tbase = (v[31:8] == cfg.boot_addr[31:8]) ? GEN_FC_CSR_TRAP_SETUP_WARL_CP_MTVEC_BASE_W_BOOT_PAGE : (v < 32'h1000) ? GEN_FC_CSR_TRAP_SETUP_WARL_CP_MTVEC_BASE_W_LOW :
                  v[31] ? GEN_FC_CSR_TRAP_SETUP_WARL_CP_MTVEC_BASE_W_HIGH : GEN_FC_CSR_TRAP_SETUP_WARL_CP_MTVEC_BASE_W_RAND;
        end
        GEN_FC_CSR_TRAP_SETUP_WARL_CP_CSR_MIE: miew = mie_w_cls(v);
        GEN_FC_CSR_TRAP_SETUP_WARL_CP_CSR_MCOUNTEREN: mcw = mcen_w_cls(v);
        default: ;
      endcase
      if (i == GEN_FC_CSR_TRAP_SETUP_WARL_CP_CSR_MCOUNTEREN) gate = csr_gate[i];   // the pin as driven when the write record arrived
      n_csr_pairs++;
      csr_cg.sample(i, csr_op[i], wpat, (csr_rd[i] == 0) ? GEN_FC_CSR_TRAP_SETUP_WARL_CP_RD_X0 : GEN_FC_CSR_TRAP_SETUP_WARL_CP_RD_NONX0,
                    mpp, mie_b, mpie_b, mprv_b, tw_b, tmode, tlo, tbase, miew, gate, mcw);
      csr_pend[i] = 0;
    endfunction
    // a CSR-op record on a tracked CSR: rd != x0 returns the standing value (closes an open pair, refreshes the shadow); a write opens a pair
    function bit csr_track(gen_rvfi_txn t);
      int i; logic [2:0] f3 = t.insn[14:12]; logic [31:0] src, old; bit old_ok, is_write;
      if (t.insn[6:0] != ibex_pkg::OPCODE_SYSTEM || f3 == 3'b000 || f3 == 3'b100) return 0;
      i = csr_idx(t.insn[31:20]);
      if (i < 0) return 0;
      src = f3[2] ? 32'(t.insn[19:15]) : t.rs1_rdata;
      is_write = (f3[1:0] == 2'b01) || (t.insn[19:15] != 5'd0);   // csrrs / csrrc with rs1 = x0 (uimm 0) are reads (the decoder demotes them)
      if (t.rd_addr != 0) begin
        if (csr_pend[i]) csr_pair_sample(i);
        csr_shadow[i] = t.rd_wdata; csr_shadow_ok[i] = 1;
      end
      if (is_write) begin
        if (csr_pend[i]) n_csr_replaced++;   // a second write with rd = x0 before any read-back: the first pair never closes
        old = (t.rd_addr != 0) ? t.rd_wdata : csr_shadow[i]; old_ok = (t.rd_addr != 0) || csr_shadow_ok[i];
        csr_pend[i] = 1; csr_op[i] = int'(f3[1:0]) - 1 + (f3[2] ? 3 : 0); csr_rd[i] = int'(t.rd_addr); csr_wval[i] = src;
        csr_gate[i] = (ctrl_vif.mcounteren_writable == ibex_pkg::IbexMuBiOn) ? GEN_FC_CSR_TRAP_SETUP_WARL_CP_MCEN_GATE_ON : (ctrl_vif.mcounteren_writable == ibex_pkg::IbexMuBiOff) ? GEN_FC_CSR_TRAP_SETUP_WARL_CP_MCEN_GATE_OFF : GEN_FC_CSR_TRAP_SETUP_WARL_CP_MCEN_GATE_INVALID;
        case (f3[1:0])
          2'b01:   begin csr_eff[i] = src;        csr_eff_ok[i] = 1; end
          2'b10:   begin csr_eff[i] = old | src;  csr_eff_ok[i] = old_ok; end
          default: begin csr_eff[i] = old & ~src; csr_eff_ok[i] = old_ok; end
        endcase
        csr_shadow_ok[i] = 0;   // the standing value is now the legalised write, known only from the next read-back
        n_csr_wr++;
      end
      return 1;
    endfunction
    // ---- CG-BIT-006: bclr / bset / binv (OP funct3 001, funct7 0100100 / 0010100 / 0110100), bext (OP funct3 101, funct7 0100100), and the
    // immediate forms (OP-IMM funct3 001 with insn[31:27] 01001 / 00101 / 01101, bexti funct3 101 with 01001); -1 for any other record
    function int sbit_op(logic [31:0] insn);
      logic [6:0] f7 = insn[31:25]; logic [2:0] f3 = insn[14:12]; logic [4:0] hi = insn[31:27];
      if (insn[6:0] == ibex_pkg::OPCODE_OP) begin
        if (f3 == 3'b001) case (f7) 7'b0100100: return GEN_FC_BIT_SBIT_CP_OP_BCLR; 7'b0010100: return GEN_FC_BIT_SBIT_CP_OP_BSET; 7'b0110100: return GEN_FC_BIT_SBIT_CP_OP_BINV; default: return -1; endcase
        return (f3 == 3'b101 && f7 == 7'b0100100) ? GEN_FC_BIT_SBIT_CP_OP_BEXT : -1;
      end
      if (insn[6:0] == ibex_pkg::OPCODE_OP_IMM) begin
        if (f3 == 3'b001) case (hi) 5'b01001: return GEN_FC_BIT_SBIT_CP_OP_BCLRI; 5'b00101: return GEN_FC_BIT_SBIT_CP_OP_BSETI; 5'b01101: return GEN_FC_BIT_SBIT_CP_OP_BINVI; default: return -1; endcase
        return (f3 == 3'b101 && hi == 5'b01001) ? GEN_FC_BIT_SBIT_CP_OP_BEXTI : -1;
      end
      return -1;
    endfunction
    function bit sbit_sample(gen_rvfi_txn t);
      int op = sbit_op(t.insn); logic [4:0] idx; bit imm_form, is_binv, twice; int upper, operand;
      if (op < 0) return 0;
      imm_form = (op >= GEN_FC_BIT_SBIT_CP_OP_BCLRI); is_binv = (op == GEN_FC_BIT_SBIT_CP_OP_BINV || op == GEN_FC_BIT_SBIT_CP_OP_BINVI);
      idx = imm_form ? t.insn[24:20] : t.rs2_rdata[4:0];
      upper = imm_form ? -1 : (t.rs2_rdata == 32'hffff_ffff) ? GEN_FC_BIT_SBIT_CP_RS2_UPPER_ALL_ONES : (t.rs2_rdata[31:5] == 0) ? GEN_FC_BIT_SBIT_CP_RS2_UPPER_ZERO : GEN_FC_BIT_SBIT_CP_RS2_UPPER_OTHER_NONZERO;
      operand = (t.rs1_rdata == 0) ? GEN_FC_BIT_SBIT_CP_OPERAND_ZERO : (t.rs1_rdata == 32'hffff_ffff) ? GEN_FC_BIT_SBIT_CP_OPERAND_ALL_ONES : GEN_FC_BIT_SBIT_CP_OPERAND_RAND;
      twice = sb_prev_binv && is_binv && t.rd_addr == sb_prev_rd && idx == sb_prev_idx;   // binv / binvi right after binv / binvi on the same rd and index
      n_sbit++;
      sbit_cg.sample(op, (idx == 0) ? GEN_FC_BIT_SBIT_CP_INDEX_I0 : (idx == 31) ? GEN_FC_BIT_SBIT_CP_INDEX_I31 : GEN_FC_BIT_SBIT_CP_INDEX_MID, upper,
                     t.rs1_rdata[idx] ? GEN_FC_BIT_SBIT_CP_PRIOR_BIT_SET : GEN_FC_BIT_SBIT_CP_PRIOR_BIT_CLEAR, operand,
                     (t.rd_addr == 0) ? GEN_FC_BIT_SBIT_CP_RD_X0_YES : GEN_FC_BIT_SBIT_CP_RD_X0_NO, twice ? GEN_FC_BIT_SBIT_CP_BINV_TWICE_YES : -1);
      sb_prev_binv = is_binv; sb_prev_rd = t.rd_addr; sb_prev_idx = idx;
      return 1;
    endfunction

    // ---- CG-CMP-005: the Zcb encodings in their 16-bit form: quadrant 00 funct3 100 (c.lbu / c.lhu / c.lh / c.sb / c.sh by insn[12:10] and
    // insn[6]), quadrant 01 insn[15:10] 100111 (c.mul with insn[6:5] 10, the ALU forms with 11 by insn[4:2]); -1 for any other word
    function int zcb_insn(logic [15:0] i);
      if (i[1:0] == 2'b00 && i[15:13] == 3'b100) case (i[12:10])
        3'b000: return GEN_FC_CMP_ZCB_CP_INSN_C_LBU; 3'b001: return i[6] ? GEN_FC_CMP_ZCB_CP_INSN_C_LH : GEN_FC_CMP_ZCB_CP_INSN_C_LHU;
        3'b010: return GEN_FC_CMP_ZCB_CP_INSN_C_SB;  3'b011: return i[6] ? -1 : GEN_FC_CMP_ZCB_CP_INSN_C_SH; default: return -1; endcase
      if (i[1:0] == 2'b01 && i[15:10] == 6'b100111) begin
        if (i[6:5] == 2'b10) return GEN_FC_CMP_ZCB_CP_INSN_C_MUL;
        if (i[6:5] == 2'b11) case (i[4:2])
          3'b000: return GEN_FC_CMP_ZCB_CP_INSN_C_ZEXT_B; 3'b001: return GEN_FC_CMP_ZCB_CP_INSN_C_SEXT_B; 3'b010: return GEN_FC_CMP_ZCB_CP_INSN_C_ZEXT_H;
          3'b011: return GEN_FC_CMP_ZCB_CP_INSN_C_SEXT_H; 3'b101: return GEN_FC_CMP_ZCB_CP_INSN_C_NOT; default: return -1; endcase
      end
      return -1;
    endfunction
    function int zcb_alu_cls(logic [31:0] v);   // plan order with zero / all_ones first; bit15_set before bit7_set; rand is unreachable (the classes partition the rest)
      if (v == 0) return GEN_FC_CMP_ZCB_CP_ALU_OPERAND_ZERO;
      if (v == 32'hffff_ffff) return GEN_FC_CMP_ZCB_CP_ALU_OPERAND_ALL_ONES;
      if (v[15]) return GEN_FC_CMP_ZCB_CP_ALU_OPERAND_BIT15_SET;
      return v[7] ? GEN_FC_CMP_ZCB_CP_ALU_OPERAND_BIT7_SET : GEN_FC_CMP_ZCB_CP_ALU_OPERAND_BIT7_CLEAR;
    endfunction
    function bit zcb_sample(gen_rvfi_txn t);
      logic [15:0] i = t.insn[15:0]; int k = zcb_insn(i); int ub = -1, uh = -1, sign = -1, alu = -1, align = -1, regs = -1;
      if (k < 0) return 0;
      case (k)
        GEN_FC_CMP_ZCB_CP_INSN_C_LBU, GEN_FC_CMP_ZCB_CP_INSN_C_SB: ub = int'({i[5], i[6]});   // uimm[1] = insn[5], uimm[0] = insn[6]
        GEN_FC_CMP_ZCB_CP_INSN_C_LHU, GEN_FC_CMP_ZCB_CP_INSN_C_LH, GEN_FC_CMP_ZCB_CP_INSN_C_SH: uh = i[5] ? GEN_FC_CMP_ZCB_CP_UIMM_H_U2 : GEN_FC_CMP_ZCB_CP_UIMM_H_U0;
        GEN_FC_CMP_ZCB_CP_INSN_C_MUL: begin regs = (i[9:7] == i[4:2]) ? GEN_FC_CMP_ZCB_CP_REGS_SAME : GEN_FC_CMP_ZCB_CP_REGS_DISTINCT; alu = zcb_alu_cls(t.rs1_rdata); end   // the CSV crosses c.mul with the operand class too
        default: alu = zcb_alu_cls(t.rs1_rdata);
      endcase
      if (k == GEN_FC_CMP_ZCB_CP_INSN_C_LBU) sign = t.mem_rdata[7] ? GEN_FC_CMP_ZCB_CP_DATA_SIGN_NEG : GEN_FC_CMP_ZCB_CP_DATA_SIGN_POS;
      if (k == GEN_FC_CMP_ZCB_CP_INSN_C_LHU || k == GEN_FC_CMP_ZCB_CP_INSN_C_LH) sign = t.mem_rdata[15] ? GEN_FC_CMP_ZCB_CP_DATA_SIGN_NEG : GEN_FC_CMP_ZCB_CP_DATA_SIGN_POS;
      if (k == GEN_FC_CMP_ZCB_CP_INSN_C_LHU || k == GEN_FC_CMP_ZCB_CP_INSN_C_LH || k == GEN_FC_CMP_ZCB_CP_INSN_C_SH)
        align = !t.mem_addr[0] ? GEN_FC_CMP_ZCB_CP_ADDR_ALIGN_ALIGNED : t.mem_addr[1] ? GEN_FC_CMP_ZCB_CP_ADDR_ALIGN_MIS3 : GEN_FC_CMP_ZCB_CP_ADDR_ALIGN_MIS1;
      n_zcb++;
      zcb_cg.sample(k, ub, uh, sign, alu, align, regs);
      return 1;
    endfunction

    // ---- Slice A: the record group (CG-RVFI-001), the multiply's timing (CG-MUL-002), the reset release (CG-RST-001) and the
    //      security inputs (CG-SEC-005). Classifiers are partitions of record fields, the neighbour facts come from the previous
    //      record and the bus agents' completed transactions, stamped on the bridge interface's cycle counter (the RVFI record's base).
    function bit is_redirect_insn(logic [31:0] insn);   // a trap-side record is classified by rvfi_trap; mret, dret and fence.i redirect
      return insn == 32'h3020_0073 || insn == 32'h7b20_0073 || (insn[6:0] == 7'b0001111 && insn[14:12] == 3'b001);
    endfunction
    function int rec_pc_delta_cls(logic [31:0] pc_r, logic [31:0] pc_w, bit redirect);
      logic [31:0] d = pc_w - pc_r;
      if (redirect) return GEN_FC_RVFI_RECORD_CP_PC_DELTA_REDIRECT_OTHER;
      if (d == 32'd2) return GEN_FC_RVFI_RECORD_CP_PC_DELTA_PLUS2;
      if (d == 32'd4) return GEN_FC_RVFI_RECORD_CP_PC_DELTA_PLUS4;
      return d[31] ? GEN_FC_RVFI_RECORD_CP_PC_DELTA_JUMP_BACK : GEN_FC_RVFI_RECORD_CP_PC_DELTA_JUMP_FWD;
    endfunction
    function int rec_cont_cls(logic [31:0] prev_pc_w, logic [31:0] pc_r, bit intr, bit prev_trap, bit prev_redirect, bit debug_changed);
      if (pc_r == prev_pc_w) return GEN_FC_RVFI_RECORD_CP_PC_CONTINUITY_CONTINUOUS;
      if (intr) return GEN_FC_RVFI_RECORD_CP_PC_CONTINUITY_DISCONTINUOUS_INTR;
      if (prev_trap) return GEN_FC_RVFI_RECORD_CP_PC_CONTINUITY_DISCONTINUOUS_AFTER_TRAP;
      if (prev_redirect) return GEN_FC_RVFI_RECORD_CP_PC_CONTINUITY_DISCONTINUOUS_AFTER_FLUSH_REDIRECT;
      if (debug_changed) return GEN_FC_RVFI_RECORD_CP_PC_CONTINUITY_DISCONTINUOUS_DEBUG;
      return -1;   // any other discontinuity is the rvfi protocol checker's error, not a bin
    endfunction
    function int rec_intr_kind_cls(bit intr, logic [31:0] pre_mip, bit nmi, bit nmi_int);
      if (!intr) return GEN_FC_RVFI_RECORD_CP_INTR_KIND_NONE;
      if (nmi) return GEN_FC_RVFI_RECORD_CP_INTR_KIND_NMI;
      if (nmi_int) return GEN_FC_RVFI_RECORD_CP_INTR_KIND_NMI_INT;
      return (pre_mip != 0) ? GEN_FC_RVFI_RECORD_CP_INTR_KIND_IRQ : -1;
    endfunction
    function int rec_rd_source_cls(logic [4:0] rd, logic [31:0] insn);
      bit st; int unsigned nb;
      if (rd == 0) return GEN_FC_RVFI_RECORD_CP_RD_SOURCE_NONE;
      return (gen_insn_mem_access(insn, st, nb) && !st) ? GEN_FC_RVFI_RECORD_CP_RD_SOURCE_LOAD_LSU : GEN_FC_RVFI_RECORD_CP_RD_SOURCE_ALU_WB;
    endfunction
    function int rec_gap_cls(int unsigned gap);
      return (gap == 1) ? GEN_FC_RVFI_RECORD_CP_VALID_GAP_G1 : (gap == 2) ? GEN_FC_RVFI_RECORD_CP_VALID_GAP_G2 : GEN_FC_RVFI_RECORD_CP_VALID_GAP_G3_PLUS;
    endfunction
    function void rec_sample(gen_rvfi_txn t);
      int v [14]; bit st; int unsigned nb;
      v[0] = t.trap ? GEN_FC_RVFI_RECORD_CP_TRAP_YES : GEN_FC_RVFI_RECORD_CP_TRAP_NO;
      v[1] = t.intr ? GEN_FC_RVFI_RECORD_CP_INTR_YES : GEN_FC_RVFI_RECORD_CP_INTR_NO;
      v[2] = (t.mode == ibex_pkg::PRIV_LVL_U) ? GEN_FC_RVFI_RECORD_CP_MODE_U : (t.mode == ibex_pkg::PRIV_LVL_M) ? GEN_FC_RVFI_RECORD_CP_MODE_M : -1;
      v[3] = t.ext_exp_valid ? GEN_FC_RVFI_RECORD_CP_INSN_KIND_ZCMP_UOP : (t.insn[1:0] != 2'b11) ? GEN_FC_RVFI_RECORD_CP_INSN_KIND_C16 : GEN_FC_RVFI_RECORD_CP_INSN_KIND_I32;
      v[4] = (t.rd_addr == 0) ? GEN_FC_RVFI_RECORD_CP_RD_X0 : GEN_FC_RVFI_RECORD_CP_RD_NONZERO;
      v[5] = (t.rs1_addr == 0) ? GEN_FC_RVFI_RECORD_CP_RS1_X0 : GEN_FC_RVFI_RECORD_CP_RS1_NONZERO;
      v[6] = (t.rs2_addr == 0) ? GEN_FC_RVFI_RECORD_CP_RS2_X0 : GEN_FC_RVFI_RECORD_CP_RS2_NONZERO;
      v[7] = (t.rs3_addr == 0) ? GEN_FC_RVFI_RECORD_CP_RS3_ZERO : GEN_FC_RVFI_RECORD_CP_RS3_NONZERO;
      v[8] = t.trap ? GEN_FC_RVFI_RECORD_CP_PC_DELTA_REDIRECT_OTHER : rec_pc_delta_cls(t.pc_rdata, t.pc_wdata, is_redirect_insn(t.insn));   // a trap record is redirect_other by kind (the plan); its pc_wdata is the sequential address, the vector shows in the next record
      v[9] = (t.order == 64'd1) ? GEN_FC_RVFI_RECORD_CP_ORDER_STEP_FIRST : -1;
      v[10] = have_prev ? rec_cont_cls(prev_t.pc_wdata, t.pc_rdata, t.intr, prev_t.trap, is_redirect_insn(prev_t.insn), prev_t.ext_debug_mode != t.ext_debug_mode) : -1;
      v[11] = have_prev ? rec_gap_cls(t.cycle - prev_t.cycle) : -1;
      v[12] = rec_intr_kind_cls(t.intr, t.ext_pre_mip, t.ext_nmi, t.ext_nmi_int);
      v[13] = rec_rd_source_cls(t.rd_addr, t.insn);
      n_rec++;
      rec_cg.sample(v[0], v[1], v[2], v[3], v[4], v[5], v[6], v[7], v[8], v[9], v[10], v[11], v[12], v[13]);
      ut_last_rec = v;
    endfunction
    // the multiply's timing: sampled on the record after the multiply (its successor decides cp_next_dep)
    function int mt_prev_cls(logic [31:0] insn);
      bit st; int unsigned nb; logic [6:0] op = insn[6:0]; logic [2:0] f3 = insn[14:12];
      if (insn[1:0] != 2'b11) begin   // compressed: loads / stores by the decoder, branches and jumps by quadrant, the rest ALU
        if (gen_insn_mem_access(insn, st, nb)) return st ? GEN_FC_MUL_TIMING_CP_PREV_STORE : GEN_FC_MUL_TIMING_CP_PREV_LOAD;
        if (insn[1:0] == 2'b01 && (insn[15:13] inside {3'b001, 3'b101, 3'b110, 3'b111})) return GEN_FC_MUL_TIMING_CP_PREV_BRANCH;   // c.jal, c.j, c.beqz, c.bnez
        if (insn[1:0] == 2'b10 && insn[15:13] == 3'b100 && insn[6:2] == 5'd0 && insn[11:7] != 5'd0) return GEN_FC_MUL_TIMING_CP_PREV_BRANCH;   // c.jr / c.jalr
        if (insn[1:0] == 2'b10 && insn[15:13] == 3'b100 && insn[12] && insn[6:2] == 5'd0 && insn[11:7] == 5'd0) return GEN_FC_MUL_TIMING_CP_PREV_OTHER;   // c.ebreak
        if (insn[1:0] == 2'b01 && insn[15:10] == 6'b100111 && insn[6:5] == 2'b10) return GEN_FC_MUL_TIMING_CP_PREV_MUL;   // c.mul
        return GEN_FC_MUL_TIMING_CP_PREV_ALU;
      end
      case (op)
        ibex_pkg::OPCODE_OP: begin
          if (insn[31:25] == 7'b0000001) return f3[2] ? GEN_FC_MUL_TIMING_CP_PREV_DIV : (f3 == 3'b000) ? GEN_FC_MUL_TIMING_CP_PREV_MUL : GEN_FC_MUL_TIMING_CP_PREV_MULH_CLASS;
          return GEN_FC_MUL_TIMING_CP_PREV_ALU;
        end
        ibex_pkg::OPCODE_OP_IMM, ibex_pkg::OPCODE_LUI, ibex_pkg::OPCODE_AUIPC: return GEN_FC_MUL_TIMING_CP_PREV_ALU;
        ibex_pkg::OPCODE_LOAD: return GEN_FC_MUL_TIMING_CP_PREV_LOAD;
        ibex_pkg::OPCODE_STORE: return GEN_FC_MUL_TIMING_CP_PREV_STORE;
        ibex_pkg::OPCODE_BRANCH, ibex_pkg::OPCODE_JAL, ibex_pkg::OPCODE_JALR: return GEN_FC_MUL_TIMING_CP_PREV_BRANCH;
        default: return GEN_FC_MUL_TIMING_CP_PREV_OTHER;
      endcase
    endfunction
    function int mt_delta_cls(int unsigned gap);
      return (gap == 1) ? GEN_FC_MUL_TIMING_CP_DELTA_D1 : (gap == 2) ? GEN_FC_MUL_TIMING_CP_DELTA_D2 : GEN_FC_MUL_TIMING_CP_DELTA_D3PLUS;
    endfunction
    function int lat_cls(int unsigned lat);
      return (lat == HZ_LAT_MIN1) ? GEN_FC_MUL_TIMING_CP_DMEM_DELAY_MIN1 : (lat <= HZ_LAT_SHORT_MAX) ? GEN_FC_MUL_TIMING_CP_DMEM_DELAY_SHORT : GEN_FC_MUL_TIMING_CP_DMEM_DELAY_LONG;
    endfunction
    function void mt_flush(gen_rvfi_txn nxt);
      if (!mt_pend) return;
      mt_v[3] = (nxt == null) ? -1 : ((mt_rd != 0 && (nxt.rs1_addr == mt_rd || nxt.rs2_addr == mt_rd)) ? GEN_FC_MUL_TIMING_CP_NEXT_DEP_YES : GEN_FC_MUL_TIMING_CP_NEXT_DEP_NO);
      mt_cg.sample(mt_v[0], mt_v[1], mt_v[2], mt_v[3], mt_v[4], mt_v[5], mt_v[6]);
      ut_last_mt = mt_v;
      mt_pend = 0;
    endfunction
    function void mt_sample(gen_rvfi_txn t, int f3);
      int unsigned id_cyc = have_last ? last_t.cycle : 0; bit busy = 0, stall = 0; int unsigned busy_lat = 0;
      if (!have_last) return;   // the first retirement after reset has no previous one: not sampled (plan)
      // a data access outstanding when the multiply entered ID (approximated by the previous retirement's cycle) whose response came later
      foreach (dlat_cyc[i]) if (dlat_gnt[i] < id_cyc && dlat_cyc[i] > id_cyc) begin busy = 1; busy_lat = dlat_lat[i]; end
      // the fetch of this instruction's word answered after the previous retirement: the fetch data was not available in time
      foreach (ib_addr[i]) if (ib_addr[i][31:2] == t.pc_rdata[31:2] && ib_rv[i] >= id_cyc) stall = 1;
      mt_v[0] = f3; mt_v[1] = (!busy && !stall) ? mt_delta_cls(t.cycle - last_t.cycle) : -1; mt_v[2] = mt_prev_cls(last_t.insn);
      mt_v[4] = busy ? GEN_FC_MUL_TIMING_CP_WB_BUSY_YES : GEN_FC_MUL_TIMING_CP_WB_BUSY_NO; mt_v[5] = stall ? GEN_FC_MUL_TIMING_CP_FETCH_STALL_YES : GEN_FC_MUL_TIMING_CP_FETCH_STALL_NO;
      mt_v[6] = busy ? lat_cls(busy_lat) : -1; mt_rd = t.rd_addr; mt_pend = 1; n_mt++;
    endfunction

    // ---- CG-ISA-004: lui / auipc. The wrap is the 33-bit signed sum of pc and the sign-extended immediate leaving [0, 2^32).
    function int lu_imm_cls(logic [19:0] imm20);
      if (imm20 == 20'h0) return GEN_FC_ISA_LUI_AUIPC_CP_IMM20_ZERO;
      if (imm20 == 20'hFFFFF) return GEN_FC_ISA_LUI_AUIPC_CP_IMM20_ALL_ONES;
      if (imm20 == 20'h80000) return GEN_FC_ISA_LUI_AUIPC_CP_IMM20_MSB;
      if (imm20 == 20'h1) return GEN_FC_ISA_LUI_AUIPC_CP_IMM20_ONE;
      return GEN_FC_ISA_LUI_AUIPC_CP_IMM20_RAND;
    endfunction
    function int lu_region_cls(logic [31:0] pc);
      if (pc <= 32'h0000_0FFF) return GEN_FC_ISA_LUI_AUIPC_CP_PC_REGION_LOW;
      if (pc >= 32'hFFFF_F000) return GEN_FC_ISA_LUI_AUIPC_CP_PC_REGION_HIGH;
      return GEN_FC_ISA_LUI_AUIPC_CP_PC_REGION_MID;
    endfunction
    function bit sum_wraps(logic [31:0] base, int imm);   // base (unsigned) + imm (signed) leaves [0, 2^32)
      logic signed [33:0] ssum = 34'(signed'({2'b00, base})) + 34'(imm);
      return ssum[33] || ssum[32];
    endfunction
    function void lu_sample(gen_rvfi_txn t);
      bit auipc = (t.insn[6:0] == ibex_pkg::OPCODE_AUIPC);
      if (t.insn[6:0] != ibex_pkg::OPCODE_LUI && !auipc) return;
      ut_last_lu = '{auipc ? GEN_FC_ISA_LUI_AUIPC_CP_OP_AUIPC : GEN_FC_ISA_LUI_AUIPC_CP_OP_LUI, lu_imm_cls(t.insn[31:12]),
                     t.pc_rdata[1] ? GEN_FC_ISA_LUI_AUIPC_CP_PC_ALIGN_HALF : GEN_FC_ISA_LUI_AUIPC_CP_PC_ALIGN_WORD, lu_region_cls(t.pc_rdata),
                     auipc ? (sum_wraps(t.pc_rdata, signed'({t.insn[31:12], 12'h000})) ? GEN_FC_ISA_LUI_AUIPC_CP_WRAP_YES : GEN_FC_ISA_LUI_AUIPC_CP_WRAP_NO) : -1,
                     (t.rd_addr == 0) ? GEN_FC_ISA_LUI_AUIPC_CP_RD_X0_YES : GEN_FC_ISA_LUI_AUIPC_CP_RD_X0_NO};
      n_lu++;
      lu_cg.sample(ut_last_lu[0], ut_last_lu[1], ut_last_lu[2], ut_last_lu[3], ut_last_lu[4], ut_last_lu[5]);
    endfunction

    // ---- CG-ISA-006: jumps. cp_jal_off and cp_rd_class belong to the 32-bit forms; the compressed offsets are CG-CMP-002's.
    function int cj_off(logic [15:0] i);   // the CJ-format offset, 12 bits
      return signed'({i[12], i[8], i[10:9], i[6], i[7], i[2], i[11], i[5:3], 1'b0});
    endfunction
    function int jal_off_cls(int imm);
      if (imm == 0) return GEN_FC_ISA_JUMP_CP_JAL_OFF_SELF;
      if (imm == 32'h000F_FFFE) return GEN_FC_ISA_JUMP_CP_JAL_OFF_MAX_FWD;
      if (imm == -32'h0010_0000) return GEN_FC_ISA_JUMP_CP_JAL_OFF_MAX_BWD;
      return (imm > 0) ? GEN_FC_ISA_JUMP_CP_JAL_OFF_POS_RAND : GEN_FC_ISA_JUMP_CP_JAL_OFF_NEG_RAND;
    endfunction
    function int jalr_imm_cls(int imm);   // the extremes before the parity bin: 2047 is max_pos, not odd
      if (imm == 0) return GEN_FC_ISA_JUMP_CP_JALR_IMM_ZERO;
      if (imm == 2047) return GEN_FC_ISA_JUMP_CP_JALR_IMM_MAX_POS;
      if (imm == -2048) return GEN_FC_ISA_JUMP_CP_JALR_IMM_MIN_NEG;
      if (imm[0]) return GEN_FC_ISA_JUMP_CP_JALR_IMM_ODD;
      return (imm > 0) ? GEN_FC_ISA_JUMP_CP_JALR_IMM_POS_RAND : GEN_FC_ISA_JUMP_CP_JALR_IMM_NEG_RAND;
    endfunction
    function int jp_rd_cls(logic [4:0] rd);
      return (rd == 0) ? GEN_FC_ISA_JUMP_CP_RD_CLASS_X0 : (rd == 1) ? GEN_FC_ISA_JUMP_CP_RD_CLASS_X1 : (rd == 5) ? GEN_FC_ISA_JUMP_CP_RD_CLASS_X5 : GEN_FC_ISA_JUMP_CP_RD_CLASS_OTHER;
    endfunction
    function void jp_sample(gen_rvfi_txn t);
      int op = -1, imm = 0; bit pc_rel = 0, reg_base = 0; logic [31:0] base, tgt, link; logic [15:0] i = t.insn[15:0];
      if (t.insn[1:0] == 2'b11) begin
        if (t.insn[6:0] == ibex_pkg::OPCODE_JAL) begin op = GEN_FC_ISA_JUMP_CP_OP_JAL; pc_rel = 1; imm = signed'({t.insn[31], t.insn[19:12], t.insn[20], t.insn[30:21], 1'b0}); end
        else if (t.insn[6:0] == ibex_pkg::OPCODE_JALR && t.insn[14:12] == 3'b000) begin op = GEN_FC_ISA_JUMP_CP_OP_JALR; reg_base = 1; imm = signed'(t.insn[31:20]); end
        else return;
      end else begin
        if (i[1:0] == 2'b01 && i[15:13] == 3'b101) begin op = GEN_FC_ISA_JUMP_CP_OP_C_J; pc_rel = 1; imm = cj_off(i); end
        else if (i[1:0] == 2'b01 && i[15:13] == 3'b001) begin op = GEN_FC_ISA_JUMP_CP_OP_C_JAL; pc_rel = 1; imm = cj_off(i); end
        else if (i[1:0] == 2'b10 && i[15:13] == 3'b100 && i[6:2] == 5'd0 && i[11:7] != 5'd0) begin op = i[12] ? GEN_FC_ISA_JUMP_CP_OP_C_JALR : GEN_FC_ISA_JUMP_CP_OP_C_JR; reg_base = 1; end
        else return;
      end
      base = pc_rel ? t.pc_rdata : t.rs1_rdata; tgt = base + 32'(imm); link = t.rd_wdata - t.pc_rdata;
      ut_last_jp[0] = op;
      ut_last_jp[1] = (op == GEN_FC_ISA_JUMP_CP_OP_JAL || op == GEN_FC_ISA_JUMP_CP_OP_JALR) ? jp_rd_cls(t.rd_addr) : -1;
      ut_last_jp[2] = (op == GEN_FC_ISA_JUMP_CP_OP_JAL) ? jal_off_cls(imm) : -1;
      ut_last_jp[3] = (op == GEN_FC_ISA_JUMP_CP_OP_JALR) ? jalr_imm_cls(imm) : -1;
      ut_last_jp[4] = reg_base ? ((t.rs1_addr == 0) ? GEN_FC_ISA_JUMP_CP_JALR_RS1_X0 : (t.rs1_addr == t.rd_addr && t.rd_addr != 0) ? GEN_FC_ISA_JUMP_CP_JALR_RS1_EQ_RD : GEN_FC_ISA_JUMP_CP_JALR_RS1_OTHER) : -1;
      ut_last_jp[5] = t.pc_wdata[1] ? GEN_FC_ISA_JUMP_CP_TARGET_ALIGN_HALF : GEN_FC_ISA_JUMP_CP_TARGET_ALIGN_WORD;
      ut_last_jp[6] = reg_base ? (tgt[0] ? GEN_FC_ISA_JUMP_CP_TARGET_ODD_YES : GEN_FC_ISA_JUMP_CP_TARGET_ODD_NO) : -1;
      ut_last_jp[7] = sum_wraps(base, imm) ? GEN_FC_ISA_JUMP_CP_WRAP_YES : GEN_FC_ISA_JUMP_CP_WRAP_NO;
      ut_last_jp[8] = (t.pc_rdata <= 32'h0000_00FF) ? GEN_FC_ISA_JUMP_CP_PC_REGION_ZERO_PAGE : (t.pc_rdata >= 32'hFFFF_F000) ? GEN_FC_ISA_JUMP_CP_PC_REGION_HIGH : GEN_FC_ISA_JUMP_CP_PC_REGION_MID;
      ut_last_jp[9] = (t.rd_addr == 0) ? -1 : (link == 32'd4) ? GEN_FC_ISA_JUMP_CP_LINK_LEN_PC4 : (link == 32'd2) ? GEN_FC_ISA_JUMP_CP_LINK_LEN_PC2 : -1;
      n_jp++;
      jp_cg.sample(ut_last_jp[0], ut_last_jp[1], ut_last_jp[2], ut_last_jp[3], ut_last_jp[4], ut_last_jp[5], ut_last_jp[6], ut_last_jp[7], ut_last_jp[8], ut_last_jp[9]);
    endfunction

    // ---- CG-ISA-005: an rd-writing instruction retired with rd = x0, then whether its successor reads x0. Ibex reports rs1_addr / rs2_addr
    // as 0 for a field the format does not have, so a read of x0 is decided from the encoding: the field exists and is 0.
    function bit insn_has_rs1(logic [31:0] insn);
      logic [15:0] i = insn[15:0];
      if (insn[1:0] == 2'b11) begin
        case (insn[6:0])
          ibex_pkg::OPCODE_OP, ibex_pkg::OPCODE_OP_IMM, ibex_pkg::OPCODE_LOAD, ibex_pkg::OPCODE_STORE, ibex_pkg::OPCODE_BRANCH, ibex_pkg::OPCODE_JALR: return 1;
          ibex_pkg::OPCODE_SYSTEM: return insn[14:12] inside {3'b001, 3'b010, 3'b011};   // the register forms of csrrw / csrrs / csrrc
          default: return 0;
        endcase
      end
      case (i[1:0])
        2'b00: return i[15:13] inside {3'b000, 3'b010, 3'b110};                        // c.addi4spn (sp), c.lw / c.sw (rs1')
        2'b01: return i[15:13] inside {3'b000, 3'b010, 3'b100, 3'b110, 3'b111} || (i[15:13] == 3'b011 && i[11:7] == 5'd2);   // c.addi (rd), c.li (x0), c.addi16sp (sp; c.lui has none), the ALU forms, c.beqz / c.bnez
        default: return i[15:13] inside {3'b000, 3'b010, 3'b100, 3'b110};                 // c.slli (rd), c.lwsp / c.swsp (sp), c.jr / c.jalr / c.mv (x0) / c.add, c.swsp
      endcase
    endfunction
    function bit insn_has_rs2(logic [31:0] insn);
      logic [15:0] i = insn[15:0];
      if (insn[1:0] == 2'b11) return insn[6:0] inside {ibex_pkg::OPCODE_OP, ibex_pkg::OPCODE_STORE, ibex_pkg::OPCODE_BRANCH};
      case (i[1:0])
        2'b00: return i[15:13] == 3'b110;                                                 // c.sw
        2'b01: return (i[15:13] == 3'b100 && i[11:10] == 2'b11) || i[15:14] == 2'b11;      // c.sub / c.xor / c.or / c.and, c.beqz / c.bnez (x0)
        default: return i[15:13] == 3'b110 || (i[15:13] == 3'b100 && i[6:2] != 5'd0);      // c.swsp, c.mv / c.add
      endcase
    endfunction
    function int hx_rs_field(logic [31:0] insn, bit second);   // the rs1 (rs2) register the encoding names, -1 when the format has none
      logic [15:0] i = insn[15:0];
      if (second ? !insn_has_rs2(insn) : !insn_has_rs1(insn)) return -1;
      if (insn[1:0] == 2'b11) return second ? int'(insn[24:20]) : int'(insn[19:15]);
      if (second) begin
        if (i[1:0] == 2'b00 || (i[1:0] == 2'b01 && i[15:13] == 3'b100)) return 8 + int'(i[4:2]);   // rs2'
        if (i[1:0] == 2'b01) return 0;                                                          // c.beqz / c.bnez compare against x0
        return int'(i[6:2]);                                                                    // c.swsp, c.mv, c.add
      end
      case (i[1:0])
        2'b00: return (i[15:13] == 3'b000) ? 2 : 8 + int'(i[9:7]);                              // sp, rs1'
        2'b01: begin
          if (i[15:13] == 3'b010) return 0;                                                       // c.li reads x0
          if (i[15:13] inside {3'b100, 3'b110, 3'b111}) return 8 + int'(i[9:7]);                  // rs1'
          return int'(i[11:7]);                                                                   // c.addi (c.nop reads x0), c.addi16sp (sp)
        end
        default: begin
          if (i[15:13] inside {3'b010, 3'b110}) return 2;                                          // c.lwsp / c.swsp
          if (i[15:13] == 3'b100 && !i[12] && i[6:2] != 5'd0) return 0;                            // c.mv reads x0
          return int'(i[11:7]);                                                                   // c.slli, c.jr / c.jalr, c.add
        end
      endcase
    endfunction
    function int hx_x0_read_cls(gen_rvfi_txn nxt);
      if (hx_rs_field(nxt.insn, 0) == 0 && nxt.rs1_rdata == 0) return GEN_FC_ISA_HINT_X0_CP_X0_READ_RS1_ZERO;
      if (hx_rs_field(nxt.insn, 1) == 0 && nxt.rs2_rdata == 0) return GEN_FC_ISA_HINT_X0_CP_X0_READ_RS2_ZERO;
      return GEN_FC_ISA_HINT_X0_CP_X0_READ_NONE;
    endfunction
    function bit bit_two_cycle(logic [31:0] insn);   // the multicycle bit-manipulation ops: rotates, funnel shifts, cmov / cmix, crc32
      logic [6:0] f7 = insn[31:25]; logic [2:0] f3 = insn[14:12]; logic [4:0] r2 = insn[24:20];
      if (insn[6:0] == ibex_pkg::OPCODE_OP_IMM) begin
        if (f3 == 3'b101 && (f7 == 7'b0110000 || insn[26])) return 1;                                  // rori, fsri
        if (f3 == 3'b001 && f7 == 7'b0110000 && r2 inside {5'h10, 5'h11, 5'h12, 5'h18, 5'h19, 5'h1A}) return 1;   // crc32 / crc32c .b / .h / .w
        return 0;
      end
      if (insn[6:0] != ibex_pkg::OPCODE_OP) return 0;
      if (f7 == 7'b0110000 && (f3 == 3'b001 || f3 == 3'b101)) return 1;                                // rol, ror
      if (insn[26:25] == 2'b11 && (f3 == 3'b001 || f3 == 3'b101)) return 1;                            // cmix, cmov
      if (insn[26:25] == 2'b10 && (f3 == 3'b001 || f3 == 3'b101)) return 1;                            // fsl, fsr
      return 0;
    endfunction
    function int hx_writer_cls(logic [31:0] insn);   // the class an rd-writing encoding belongs to; -1 for one that writes no rd
      logic [6:0] f7 = insn[31:25]; logic [2:0] f3 = insn[14:12]; logic [15:0] i = insn[15:0];
      if (insn[1:0] != 2'b11) begin   // c.li, c.lui, c.slli, c.mv, c.add with rd = x0 are the compressed HINTs
        if (i[1:0] == 2'b01 && (i[15:13] == 3'b010 || (i[15:13] == 3'b011 && i[11:7] != 5'd2))) return GEN_FC_ISA_HINT_X0_CP_WRITER_CLASS_CMP_HINT;
        if (i[1:0] == 2'b10 && (i[15:13] == 3'b000 || (i[15:13] == 3'b100 && i[6:2] != 5'd0))) return GEN_FC_ISA_HINT_X0_CP_WRITER_CLASS_CMP_HINT;
        return -1;
      end
      case (insn[6:0])
        ibex_pkg::OPCODE_LUI, ibex_pkg::OPCODE_AUIPC: return GEN_FC_ISA_HINT_X0_CP_WRITER_CLASS_LUI_AUIPC;
        ibex_pkg::OPCODE_LOAD: return GEN_FC_ISA_HINT_X0_CP_WRITER_CLASS_LOAD;
        ibex_pkg::OPCODE_JAL: return GEN_FC_ISA_HINT_X0_CP_WRITER_CLASS_JAL;
        ibex_pkg::OPCODE_JALR: return GEN_FC_ISA_HINT_X0_CP_WRITER_CLASS_JALR;
        ibex_pkg::OPCODE_SYSTEM: return (f3 != 3'b000) ? GEN_FC_ISA_HINT_X0_CP_WRITER_CLASS_CSRR : -1;
        ibex_pkg::OPCODE_OP_IMM: begin
          if (f3 != 3'b001 && f3 != 3'b101) return GEN_FC_ISA_HINT_X0_CP_WRITER_CLASS_ALU_IMM;
          if (f7 == 7'b0000000 || (f3 == 3'b101 && f7 == 7'b0100000)) return GEN_FC_ISA_HINT_X0_CP_WRITER_CLASS_SHIFT;
          return bit_two_cycle(insn) ? GEN_FC_ISA_HINT_X0_CP_WRITER_CLASS_BIT_2CYC : GEN_FC_ISA_HINT_X0_CP_WRITER_CLASS_BIT_1CYC;
        end
        ibex_pkg::OPCODE_OP: begin
          if (f7 == 7'b0000001) return f3[2] ? GEN_FC_ISA_HINT_X0_CP_WRITER_CLASS_DIV_REM : (f3 == 3'b000) ? GEN_FC_ISA_HINT_X0_CP_WRITER_CLASS_MUL : GEN_FC_ISA_HINT_X0_CP_WRITER_CLASS_MULH;
          if (f7 == 7'b0000000) return (f3 == 3'b001 || f3 == 3'b101) ? GEN_FC_ISA_HINT_X0_CP_WRITER_CLASS_SHIFT : GEN_FC_ISA_HINT_X0_CP_WRITER_CLASS_ALU_REG;
          if (f7 == 7'b0100000 && f3 == 3'b000) return GEN_FC_ISA_HINT_X0_CP_WRITER_CLASS_ALU_REG;   // sub
          if (f7 == 7'b0100000 && f3 == 3'b101) return GEN_FC_ISA_HINT_X0_CP_WRITER_CLASS_SHIFT;     // sra
          return bit_two_cycle(insn) ? GEN_FC_ISA_HINT_X0_CP_WRITER_CLASS_BIT_2CYC : GEN_FC_ISA_HINT_X0_CP_WRITER_CLASS_BIT_1CYC;
        end
        default: return -1;
      endcase
    endfunction
    function int hx_hint_cls(logic [31:0] insn);   // the 32-bit HINT encodings the plan names; every other x0 writer is other
      logic [6:0] f7 = insn[31:25]; logic [2:0] f3 = insn[14:12]; logic [4:0] rs1 = insn[19:15], shamt = insn[24:20];
      if (insn[1:0] != 2'b11) return GEN_FC_ISA_HINT_X0_CP_HINT_CLASS_OTHER;
      case (insn[6:0])
        ibex_pkg::OPCODE_LUI: return GEN_FC_ISA_HINT_X0_CP_HINT_CLASS_LUI_X0;
        ibex_pkg::OPCODE_AUIPC: return GEN_FC_ISA_HINT_X0_CP_HINT_CLASS_AUIPC_X0;
        ibex_pkg::OPCODE_OP_IMM: case (f3)
          3'b000: return (rs1 == 0 && insn[31:20] == 12'h0) ? GEN_FC_ISA_HINT_X0_CP_HINT_CLASS_CANONICAL_NOP : GEN_FC_ISA_HINT_X0_CP_HINT_CLASS_ADDI_X0_NZIMM;
          3'b010: return GEN_FC_ISA_HINT_X0_CP_HINT_CLASS_SLTI_X0;
          3'b011: return GEN_FC_ISA_HINT_X0_CP_HINT_CLASS_SLTIU_X0;
          3'b100: return GEN_FC_ISA_HINT_X0_CP_HINT_CLASS_XORI_X0;
          3'b110: return GEN_FC_ISA_HINT_X0_CP_HINT_CLASS_ORI_X0;
          3'b111: return GEN_FC_ISA_HINT_X0_CP_HINT_CLASS_ANDI_X0;
          3'b001: begin
            if (f7 != 7'b0000000) return GEN_FC_ISA_HINT_X0_CP_HINT_CLASS_OTHER;
            return (rs1 == 0 && shamt == 5'd31) ? GEN_FC_ISA_HINT_X0_CP_HINT_CLASS_SLLI_X0_SEMIHOST : GEN_FC_ISA_HINT_X0_CP_HINT_CLASS_SLLI_X0_OTHER;
          end
          default: begin
            if (f7 == 7'b0000000) return GEN_FC_ISA_HINT_X0_CP_HINT_CLASS_SRLI_X0;
            if (f7 != 7'b0100000) return GEN_FC_ISA_HINT_X0_CP_HINT_CLASS_OTHER;
            return (rs1 == 0 && shamt == 5'd7) ? GEN_FC_ISA_HINT_X0_CP_HINT_CLASS_SRAI_X0_SEMIHOST : GEN_FC_ISA_HINT_X0_CP_HINT_CLASS_SRAI_X0_OTHER;
          end
        endcase
        ibex_pkg::OPCODE_OP: begin
          if (f7 == 7'b0000000) case (f3)
            3'b000: return GEN_FC_ISA_HINT_X0_CP_HINT_CLASS_ADD_X0; 3'b001: return GEN_FC_ISA_HINT_X0_CP_HINT_CLASS_SLL_X0;
            3'b010: return GEN_FC_ISA_HINT_X0_CP_HINT_CLASS_SLT_X0; 3'b011: return GEN_FC_ISA_HINT_X0_CP_HINT_CLASS_SLTU_X0;
            3'b100: return GEN_FC_ISA_HINT_X0_CP_HINT_CLASS_XOR_X0; 3'b101: return GEN_FC_ISA_HINT_X0_CP_HINT_CLASS_SRL_X0;
            3'b110: return GEN_FC_ISA_HINT_X0_CP_HINT_CLASS_OR_X0;  default: return GEN_FC_ISA_HINT_X0_CP_HINT_CLASS_AND_X0;
          endcase
          if (f7 == 7'b0100000 && f3 == 3'b000) return GEN_FC_ISA_HINT_X0_CP_HINT_CLASS_SUB_X0;
          if (f7 == 7'b0100000 && f3 == 3'b101) return GEN_FC_ISA_HINT_X0_CP_HINT_CLASS_SRA_X0;
          return GEN_FC_ISA_HINT_X0_CP_HINT_CLASS_OTHER;
        end
        default: return GEN_FC_ISA_HINT_X0_CP_HINT_CLASS_OTHER;
      endcase
    endfunction
    function void hx_sample(gen_rvfi_txn t);
      int wc = hx_writer_cls(t.insn);
      if (t.rd_addr != 0 || wc < 0) return;
      hx_v[0] = hx_hint_cls(t.insn); hx_v[1] = wc; hx_pend = 1;
    endfunction
    function void hx_flush(gen_rvfi_txn nxt);
      if (!hx_pend) return;
      hx_v[2] = (nxt == null) ? -1 : hx_x0_read_cls(nxt);
      hx_cg.sample(hx_v[0], hx_v[1], hx_v[2]);
      ut_last_hx = hx_v; n_hx++; hx_pend = 0;
    endfunction

    // ---- CG-MUL-004: the divider's timing, sampled on the record after the divide (its successor decides cp_next and the irq latency).
    // The occupancy window is approximated by the previous retirement's cycle and the divide's own, as the multiply's is.
    function int dt_delta_cls(int unsigned gap);
      return (gap == 2) ? GEN_FC_DIV_TIMING_CP_DELTA_D2 : (gap == 37) ? GEN_FC_DIV_TIMING_CP_DELTA_D37 : GEN_FC_DIV_TIMING_CP_DELTA_OTHER;
    endfunction
    function int dt_prev_cls(gen_rvfi_txn last, gen_rvfi_txn t);
      bit st; int unsigned nb; int mc = mt_prev_cls(last.insn);
      if (gen_insn_mem_access(last.insn, st, nb) && !st && last.rd_addr != 0 && (last.rd_addr == t.rs1_addr || last.rd_addr == t.rs2_addr)) return GEN_FC_DIV_TIMING_CP_PREV_LOAD_DEP;
      if (mc == GEN_FC_MUL_TIMING_CP_PREV_MUL || mc == GEN_FC_MUL_TIMING_CP_PREV_MULH_CLASS) return GEN_FC_DIV_TIMING_CP_PREV_MUL;
      if (mc == GEN_FC_MUL_TIMING_CP_PREV_DIV) return GEN_FC_DIV_TIMING_CP_PREV_DIV;
      if (mc == GEN_FC_MUL_TIMING_CP_PREV_ALU) return GEN_FC_DIV_TIMING_CP_PREV_ALU;
      return GEN_FC_DIV_TIMING_CP_PREV_OTHER;
    endfunction
    function int dt_next_cls(gen_rvfi_txn nxt, logic [4:0] rd);
      int mc = mt_prev_cls(nxt.insn);
      if (mc == GEN_FC_MUL_TIMING_CP_PREV_MUL || mc == GEN_FC_MUL_TIMING_CP_PREV_MULH_CLASS) return GEN_FC_DIV_TIMING_CP_NEXT_MUL;
      if (mc == GEN_FC_MUL_TIMING_CP_PREV_DIV) return GEN_FC_DIV_TIMING_CP_NEXT_DIV;
      if (mc == GEN_FC_MUL_TIMING_CP_PREV_ALU && rd != 0 && (nxt.rs1_addr == rd || nxt.rs2_addr == rd)) return GEN_FC_DIV_TIMING_CP_NEXT_DEP_ALU;
      return GEN_FC_DIV_TIMING_CP_NEXT_OTHER;
    endfunction
    function void dt_sample(gen_rvfi_txn t, int f3);
      int unsigned id_cyc; bit busy = 0, stall = 0; int ev = GEN_FC_DIV_TIMING_CP_EVENT_MID_NONE;
      if (!have_last) return;   // the first retirement after reset has no previous one: not sampled (plan)
      id_cyc = last_t.cycle;
      foreach (dlat_cyc[i]) if (dlat_gnt[i] < id_cyc && dlat_cyc[i] > id_cyc) busy = 1;
      foreach (ib_addr[i]) if (ib_addr[i][31:2] == t.pc_rdata[31:2] && ib_rv[i] >= id_cyc) stall = 1;
      dt_irq_seen = 0;
      foreach (ev_cyc[i]) if (ev == GEN_FC_DIV_TIMING_CP_EVENT_MID_NONE && ev_cyc[i] > id_cyc && ev_cyc[i] < t.cycle) begin   // the first assertion strictly inside the window
        ev = ev_kind[i];
        if (ev == GEN_FC_DIV_TIMING_CP_EVENT_MID_IRQ) begin dt_irq_seen = 1; dt_irq_cycle = ev_cyc[i]; end
      end
      dt_v[0] = f3; dt_v[1] = dit_tracked ? GEN_FC_DIV_TIMING_CP_DIT_ON : GEN_FC_DIV_TIMING_CP_DIT_OFF;
      dt_v[2] = (t.rs2_rdata == 0) ? GEN_FC_DIV_TIMING_CP_DIV0_YES : GEN_FC_DIV_TIMING_CP_DIV0_NO;
      dt_v[3] = (!busy && !stall) ? dt_delta_cls(t.cycle - last_t.cycle) : -1;
      dt_v[4] = ev; dt_v[5] = busy ? GEN_FC_DIV_TIMING_CP_WB_DEFER_YES : GEN_FC_DIV_TIMING_CP_WB_DEFER_NO;
      dt_v[6] = dt_prev_cls(last_t, t); dt_v[7] = -1;
      dt_v[8] = stall ? GEN_FC_DIV_TIMING_CP_FETCH_STALL_YES : GEN_FC_DIV_TIMING_CP_FETCH_STALL_NO; dt_v[9] = -1;
      dt_rd = t.rd_addr; dt_pend = 1;
    endfunction
    function void dt_flush(gen_rvfi_txn nxt);
      if (!dt_pend) return;
      dt_v[7] = (nxt == null) ? -1 : dt_next_cls(nxt, dt_rd);
      dt_v[9] = (dt_irq_seen && nxt != null && nxt.intr) ? ((nxt.cycle - dt_irq_cycle <= 37) ? GEN_FC_DIV_TIMING_CP_IRQ_LATENCY_LE37 : GEN_FC_DIV_TIMING_CP_IRQ_LATENCY_GT37) : -1;
      dt_cg.sample(dt_v[0], dt_v[1], dt_v[2], dt_v[3], dt_v[4], dt_v[5], dt_v[6], dt_v[7], dt_v[8], dt_v[9]);
      ut_last_dt = dt_v; n_dt++; dt_pend = 0;
    endfunction

    // ---- CG-CMP-002: the immediate of a Zca retirement, decoded per format; every other coverpoint of the record stays na
    function int ie_off_cls(int imm, int max_fwd, int max_bwd, int self_b, int fwd_b, int bwd_b, int pos_b, int neg_b);
      if (imm == 0) return self_b;
      if (imm == max_fwd) return fwd_b;
      if (imm == max_bwd) return bwd_b;
      return (imm > 0) ? pos_b : neg_b;
    endfunction
    function void ie_sample(gen_rvfi_txn t);
      logic [15:0] i = t.insn[15:0]; int op = zca_insn(i), imm, v [13]; logic [4:0] shamt = i[6:2];
      if (op < 0) return;
      foreach (v[k]) v[k] = -1;
      case (op)
        GEN_FC_CMP_ZCA_CP_INSN_C_ADDI4SPN: begin
          imm = {i[10:7], i[12:11], i[5], i[6], 2'b00};
          v[0] = (imm == 4) ? GEN_FC_CMP_IMM_EDGES_CP_ADDI4SPN_IMM_MIN : (imm == 1020) ? GEN_FC_CMP_IMM_EDGES_CP_ADDI4SPN_IMM_MAX : GEN_FC_CMP_IMM_EDGES_CP_ADDI4SPN_IMM_RAND;
          v[11] = sum_wraps(t.rs1_rdata, imm) ? GEN_FC_CMP_IMM_EDGES_CP_SP_WRAP_YES : GEN_FC_CMP_IMM_EDGES_CP_SP_WRAP_NO;
        end
        GEN_FC_CMP_ZCA_CP_INSN_C_LW, GEN_FC_CMP_ZCA_CP_INSN_C_SW: begin
          imm = {i[5], i[12:10], i[6], 2'b00};
          v[1] = (imm == 0) ? GEN_FC_CMP_IMM_EDGES_CP_LW_SW_UIMM_ZERO : (imm == 124) ? GEN_FC_CMP_IMM_EDGES_CP_LW_SW_UIMM_MAX : GEN_FC_CMP_IMM_EDGES_CP_LW_SW_UIMM_RAND;
        end
        GEN_FC_CMP_ZCA_CP_INSN_C_LWSP, GEN_FC_CMP_ZCA_CP_INSN_C_SWSP: begin
          imm = (op == GEN_FC_CMP_ZCA_CP_INSN_C_LWSP) ? {i[3:2], i[12], i[6:4], 2'b00} : {i[8:7], i[12:9], 2'b00};
          v[2] = (imm == 0) ? GEN_FC_CMP_IMM_EDGES_CP_SP_UIMM_ZERO : (imm == 252) ? GEN_FC_CMP_IMM_EDGES_CP_SP_UIMM_MAX : GEN_FC_CMP_IMM_EDGES_CP_SP_UIMM_RAND;
        end
        GEN_FC_CMP_ZCA_CP_INSN_C_ADDI, GEN_FC_CMP_ZCA_CP_INSN_C_LI, GEN_FC_CMP_ZCA_CP_INSN_C_ANDI: begin
          imm = signed'({i[12], i[6:2]});
          v[3] = (op == GEN_FC_CMP_ZCA_CP_INSN_C_ADDI) ? GEN_FC_CMP_IMM_EDGES_CP_CI_OP_C_ADDI : (op == GEN_FC_CMP_ZCA_CP_INSN_C_LI) ? GEN_FC_CMP_IMM_EDGES_CP_CI_OP_C_LI : GEN_FC_CMP_IMM_EDGES_CP_CI_OP_C_ANDI;
          v[4] = (imm == -32) ? GEN_FC_CMP_IMM_EDGES_CP_CI_IMM6_MIN : (imm == -1) ? GEN_FC_CMP_IMM_EDGES_CP_CI_IMM6_MINUS1 : (imm == 0) ? GEN_FC_CMP_IMM_EDGES_CP_CI_IMM6_ZERO :
                 (imm == 1) ? GEN_FC_CMP_IMM_EDGES_CP_CI_IMM6_ONE : (imm == 31) ? GEN_FC_CMP_IMM_EDGES_CP_CI_IMM6_MAX : GEN_FC_CMP_IMM_EDGES_CP_CI_IMM6_RAND;
        end
        GEN_FC_CMP_ZCA_CP_INSN_C_LUI: begin
          imm = signed'({i[12], i[6:2]});
          v[5] = (imm == 1) ? GEN_FC_CMP_IMM_EDGES_CP_LUI_IMM_POS_MIN : (imm == 31) ? GEN_FC_CMP_IMM_EDGES_CP_LUI_IMM_POS_MAX : (imm == -32) ? GEN_FC_CMP_IMM_EDGES_CP_LUI_IMM_NEG_MIN :
                 (imm == -1) ? GEN_FC_CMP_IMM_EDGES_CP_LUI_IMM_NEG_MAX : GEN_FC_CMP_IMM_EDGES_CP_LUI_IMM_RAND;
        end
        GEN_FC_CMP_ZCA_CP_INSN_C_ADDI16SP: begin
          imm = signed'({i[12], i[4:3], i[5], i[2], i[6], 4'b0000});
          v[6] = (imm == -512) ? GEN_FC_CMP_IMM_EDGES_CP_ADDI16SP_IMM_MIN : (imm == 496) ? GEN_FC_CMP_IMM_EDGES_CP_ADDI16SP_IMM_MAX : (imm == 16) ? GEN_FC_CMP_IMM_EDGES_CP_ADDI16SP_IMM_PLUS16 :
                 (imm == -16) ? GEN_FC_CMP_IMM_EDGES_CP_ADDI16SP_IMM_MINUS16 : GEN_FC_CMP_IMM_EDGES_CP_ADDI16SP_IMM_RAND;
          v[11] = sum_wraps(t.rs1_rdata, imm) ? GEN_FC_CMP_IMM_EDGES_CP_SP_WRAP_YES : GEN_FC_CMP_IMM_EDGES_CP_SP_WRAP_NO;
        end
        GEN_FC_CMP_ZCA_CP_INSN_C_SRLI, GEN_FC_CMP_ZCA_CP_INSN_C_SRAI, GEN_FC_CMP_ZCA_CP_INSN_C_SLLI: begin
          v[7] = (op == GEN_FC_CMP_ZCA_CP_INSN_C_SRLI) ? GEN_FC_CMP_IMM_EDGES_CP_SHIFT_OP_C_SRLI : (op == GEN_FC_CMP_ZCA_CP_INSN_C_SRAI) ? GEN_FC_CMP_IMM_EDGES_CP_SHIFT_OP_C_SRAI : GEN_FC_CMP_IMM_EDGES_CP_SHIFT_OP_C_SLLI;
          if (shamt != 0) v[8] = (shamt == 1) ? GEN_FC_CMP_IMM_EDGES_CP_SHAMT_ONE : (shamt == 31) ? GEN_FC_CMP_IMM_EDGES_CP_SHAMT_MAX : GEN_FC_CMP_IMM_EDGES_CP_SHAMT_RAND;
        end
        GEN_FC_CMP_ZCA_CP_INSN_C_J, GEN_FC_CMP_ZCA_CP_INSN_C_JAL: begin
          v[9] = ie_off_cls(cj_off(i), 2046, -2048, GEN_FC_CMP_IMM_EDGES_CP_CJ_OFF_SELF, GEN_FC_CMP_IMM_EDGES_CP_CJ_OFF_MAX_FWD, GEN_FC_CMP_IMM_EDGES_CP_CJ_OFF_MAX_BWD,
                          GEN_FC_CMP_IMM_EDGES_CP_CJ_OFF_POS_RAND, GEN_FC_CMP_IMM_EDGES_CP_CJ_OFF_NEG_RAND);
          if (op == GEN_FC_CMP_ZCA_CP_INSN_C_JAL) v[12] = (t.rd_wdata - t.pc_rdata == 32'd2) ? GEN_FC_CMP_IMM_EDGES_CP_LINK_PC2 : -1;
        end
        GEN_FC_CMP_ZCA_CP_INSN_C_BEQZ, GEN_FC_CMP_ZCA_CP_INSN_C_BNEZ: begin
          imm = signed'({i[12], i[6:5], i[2], i[11:10], i[4:3], 1'b0});
          v[10] = ie_off_cls(imm, 254, -256, GEN_FC_CMP_IMM_EDGES_CP_CB_OFF_SELF, GEN_FC_CMP_IMM_EDGES_CP_CB_OFF_MAX_FWD, GEN_FC_CMP_IMM_EDGES_CP_CB_OFF_MAX_BWD,
                           GEN_FC_CMP_IMM_EDGES_CP_CB_OFF_POS_RAND, GEN_FC_CMP_IMM_EDGES_CP_CB_OFF_NEG_RAND);
        end
        GEN_FC_CMP_ZCA_CP_INSN_C_JALR: v[12] = (t.rd_wdata - t.pc_rdata == 32'd2) ? GEN_FC_CMP_IMM_EDGES_CP_LINK_PC2 : -1;
        default: return;   // no immediate: c.nop, c.mv, c.add, c.jr, the register ALU forms
      endcase
      n_ie++;
      ie_cg.sample(v[0], v[1], v[2], v[3], v[4], v[5], v[6], v[7], v[8], v[9], v[10], v[11], v[12]);
      ut_last_ie = v;
    endfunction
    function void write_ibus(gen_bus_txn b);
      irq_off_take();           // open here too: a window opened only at a record lets earlier fetches pass undecided
      irq_off_first_fetch(b);   // CG-IRQ-011 cp_fetch_on_after: the first fetch after the return to On
      // every completed fetch: its word and response cycle for the fetch-stall class, and the first request's distance
      ib_addr.push_back(b.addr); ib_rv.push_back(b.stamp_rvalid);   // the RVFI record's cycle base
      if (ib_addr.size() > 64) begin void'(ib_addr.pop_front()); void'(ib_rv.pop_front()); end
      if (b.first_after_release && !boot_to_req_seen) begin boot_to_req = b.since_release; boot_to_req_seen = 1; end
    endfunction
    // the reset release (CG-RST-001): the pins at the release, then the first event
    function int mubi_cls_rst(ibex_pkg::ibex_mubi_t v);
      return (v == ibex_pkg::IbexMuBiOn) ? GEN_FC_RST_BOOT_CP_FETCH_EN_AT_RELEASE_ON : (v == ibex_pkg::IbexMuBiOff) ? GEN_FC_RST_BOOT_CP_FETCH_EN_AT_RELEASE_OFF : GEN_FC_RST_BOOT_CP_FETCH_EN_AT_RELEASE_INVALID;
    endfunction
    function int rst_boot_cls(logic [31:0] a);
      if (a[31:8] == 24'd0) return GEN_FC_RST_BOOT_CP_BOOT_ADDR_ZERO;
      if (a[31:8] <= 24'h0FFFFF) return GEN_FC_RST_BOOT_CP_BOOT_ADDR_LOW;
      if (a[31:8] <= 24'h7FFFFF) return GEN_FC_RST_BOOT_CP_BOOT_ADDR_MID;
      return GEN_FC_RST_BOOT_CP_BOOT_ADDR_HIGH;
    endfunction
    function int rst_hart_cls(logic [31:0] h);
      return (h == 0) ? GEN_FC_RST_BOOT_CP_HART_ID_ZERO : (h == 32'hFFFF_FFFF) ? GEN_FC_RST_BOOT_CP_HART_ID_MAX : GEN_FC_RST_BOOT_CP_HART_ID_RANDOM;
    endfunction
    function int rst_pending_cls(logic [17:0] lines, bit nm, bit dbg);
      bit irq = |lines;
      if (nm && dbg) return GEN_FC_RST_BOOT_CP_PENDING_NMI_AND_DEBUG;
      if (irq && dbg) return GEN_FC_RST_BOOT_CP_PENDING_IRQ_AND_DEBUG;
      if (dbg) return GEN_FC_RST_BOOT_CP_PENDING_DEBUG_REQ;
      if (nm) return GEN_FC_RST_BOOT_CP_PENDING_NMI;
      if (irq) return GEN_FC_RST_BOOT_CP_PENDING_IRQ_ENABLED_LATER;   // mie is 0 at reset: a line can only be enabled later
      return GEN_FC_RST_BOOT_CP_PENDING_NONE;
    endfunction
    function int rst_first_event_cls(bit intr, bit nmi, bit debug_mode);
      if (debug_mode) return GEN_FC_RST_BOOT_CP_FIRST_EVENT_DEBUG_ENTRY;
      if (intr) return nmi ? GEN_FC_RST_BOOT_CP_FIRST_EVENT_NMI_TAKEN : -1;   // a maskable first entry is the plan's ignore
      return GEN_FC_RST_BOOT_CP_FIRST_EVENT_FIRST_INSTR_RETIRE;
    endfunction
    function int rst_req_cls(int unsigned c);
      return (c == 2) ? GEN_FC_RST_BOOT_CP_BOOT_TO_REQ_CYCLES_TWO : (c == 3) ? GEN_FC_RST_BOOT_CP_BOOT_TO_REQ_CYCLES_THREE : (c >= 4) ? GEN_FC_RST_BOOT_CP_BOOT_TO_REQ_CYCLES_MORE : -1;
    endfunction
    function void rst_sample(int first_event);
      int v [8];
      if (rst_sampled || rst_cg == null) return;
      v[0] = rst_boot_cls(cfg.boot_addr); v[1] = (cfg.boot_addr[7:0] == 8'd0) ? GEN_FC_RST_BOOT_CP_BOOT_LOW_BYTE_ZERO : -1;
      v[2] = rst_fetch_en; v[3] = rst_pending; v[4] = first_event; v[5] = rst_hart_cls(hart_id_v);
      v[6] = GEN_FC_RST_BOOT_CP_RESET_KIND_POWER_ON;   // the TB has no mid-run reset regime: mid_run stays unreachable (stated)
      v[7] = boot_to_req_seen ? rst_req_cls(boot_to_req) : -1;
      rst_cg.sample(v[0], v[1], v[2], v[3], v[4], v[5], v[6], v[7]);
      ut_last_rst = v; rst_sampled = 1; n_rst++;
    endfunction
    // the security inputs (CG-SEC-005): one sample per event, the other coverpoints na
    function int mubi_cls_sec(ibex_pkg::ibex_mubi_t v);
      return (v == ibex_pkg::IbexMuBiOn) ? GEN_FC_SEC_CTRL_INPUTS_CP_FETCH_EN_VAL_ON : (v == ibex_pkg::IbexMuBiOff) ? GEN_FC_SEC_CTRL_INPUTS_CP_FETCH_EN_VAL_OFF : GEN_FC_SEC_CTRL_INPUTS_CP_FETCH_EN_VAL_INVALID;
    endfunction
    function int key_delay_cls();
      case (cfg.knob_scr_key_delay)
        "immediate": return GEN_FC_SEC_CTRL_INPUTS_CP_KEY_DELAY_IMMEDIATE;
        "delayed": return GEN_FC_SEC_CTRL_INPUTS_CP_KEY_DELAY_DELAYED;
        "withheld_then_valid": return GEN_FC_SEC_CTRL_INPUTS_CP_KEY_DELAY_WITHHELD_THEN_VALID;
        default: return -1;
      endcase
    endfunction
    function void sec_sample(int ev, int bits67 = -1, int bit8 = -1, int ic_dbg = -1, int fe = -1, int mw = -1, int eff = -1, int kctx = -1, int kv = -1);
      int v [11];
      if (sec_cg == null) return;
      v[0] = ev; v[1] = -1; v[2] = bit8; v[3] = bits67; v[4] = ic_dbg; v[5] = fe; v[6] = mw; v[7] = eff; v[8] = (ev == GEN_FC_SEC_CTRL_INPUTS_CP_EVENT_KEY_REQ || ev == GEN_FC_SEC_CTRL_INPUTS_CP_EVENT_KEY_VALID_CHANGE || ev == GEN_FC_SEC_CTRL_INPUTS_CP_EVENT_CPUCTRL_READ) ? key_delay_cls() : -1; v[9] = kctx; v[10] = kv;
      sec_cg.sample(v[0], v[1], v[2], v[3], v[4], v[5], v[6], v[7], v[8], v[9], v[10]);
      ut_last_sec = v; n_sec++;
    endfunction
    function void write_key(gen_key_evt e);   // the scramble-key responder's req / valid changes
      if (e.req_changed && e.req) begin
        int ctx = !have_prev ? GEN_FC_SEC_CTRL_INPUTS_CP_KEY_REQ_CONTEXT_RESET_INVAL : fencei_pending ? GEN_FC_SEC_CTRL_INPUTS_CP_KEY_REQ_CONTEXT_FENCE_I :
                  prev_t.ext_debug_mode ? GEN_FC_SEC_CTRL_INPUTS_CP_KEY_REQ_CONTEXT_DEBUG_MODE : !icache_en_tracked ? GEN_FC_SEC_CTRL_INPUTS_CP_KEY_REQ_CONTEXT_ICACHE_DISABLED : -1;
        sec_sample(GEN_FC_SEC_CTRL_INPUTS_CP_EVENT_KEY_REQ, .kctx(ctx));
      end
      if (e.valid_changed) sec_sample(GEN_FC_SEC_CTRL_INPUTS_CP_EVENT_KEY_VALID_CHANGE);
    endfunction
    function void sec_record(gen_rvfi_txn t);   // the record-side events: cpuctrlsts reads, mcounteren writes and their read-back, the trackers
      bit is_csr = (t.insn[6:0] == ibex_pkg::OPCODE_SYSTEM) && (t.insn[14:12] != 3'b000) && !t.trap;
      logic [11:0] csr = t.insn[31:20]; logic [2:0] f3 = t.insn[14:12];
      bit is_write = is_csr && (f3[1:0] == 2'b01 || t.insn[19:15] != 5'd0);   // csrrw always writes; csrrs / csrrc with rs1 / uimm 0 read only
      logic [31:0] opnd = f3[2] ? 32'(t.insn[19:15]) : t.rs1_rdata;   // the write operand: uimm for the i forms, rs1 otherwise
      fencei_pending = (t.insn[6:0] == 7'b0001111 && t.insn[14:12] == 3'b001);
      if (is_csr && csr == GEN_CSR_CPUCTRLSTS && is_write) begin   // cpuctrlsts.icache_enable as written: rw takes the operand, set / clear apply it to the old value (rd_wdata when read, else the tracked bit)
        bit old_en = (t.rd_addr != 0) ? t.rd_wdata[0] : icache_en_tracked;
        bit old_dit = (t.rd_addr != 0) ? t.rd_wdata[GEN_CPUCTRLSTS_DATA_IND_TIMING_BIT] : dit_tracked;
        icache_en_tracked = (f3[1:0] == 2'b01) ? opnd[0] : (f3[1:0] == 2'b10) ? (old_en | opnd[0]) : (old_en & ~opnd[0]);
        dit_tracked = (f3[1:0] == 2'b01) ? opnd[GEN_CPUCTRLSTS_DATA_IND_TIMING_BIT] : (f3[1:0] == 2'b10) ? (old_dit | opnd[GEN_CPUCTRLSTS_DATA_IND_TIMING_BIT])
                                                                                     : (old_dit & ~opnd[GEN_CPUCTRLSTS_DATA_IND_TIMING_BIT]);
      end
      if (mcen_pend && is_csr && csr == ibex_pkg::CSR_MCOUNTEREN && t.rd_addr != 0) begin   // the read-back after a mcounteren write decides its effect
        int eff = (t.rd_wdata == mcen_old && mcen_new != mcen_old) ? GEN_FC_SEC_CTRL_INPUTS_CP_MCOUNTEREN_WRITE_EFFECT_DROPPED : (t.rd_wdata != mcen_old) ? GEN_FC_SEC_CTRL_INPUTS_CP_MCOUNTEREN_WRITE_EFFECT_APPLIED : -1;
        sec_sample(GEN_FC_SEC_CTRL_INPUTS_CP_EVENT_MCOUNTEREN_WRITE, .mw(mcen_pin_cls), .eff(eff)); mcen_pend = 0;
      end
      if (is_csr && csr == GEN_CSR_CPUCTRLSTS && t.rd_addr != 0)
        sec_sample(GEN_FC_SEC_CTRL_INPUTS_CP_EVENT_CPUCTRL_READ, .bits67(int'(t.rd_wdata[7:6])), .bit8(t.rd_wdata[8] ? GEN_FC_SEC_CTRL_INPUTS_CP_BIT8_READBACK_ONE : GEN_FC_SEC_CTRL_INPUTS_CP_BIT8_READBACK_ZERO),
                   .ic_dbg(t.ext_debug_mode ? (t.rd_wdata[0] ? GEN_FC_SEC_CTRL_INPUTS_CP_ICACHE_EN_READBACK_IN_DEBUG_ONE : GEN_FC_SEC_CTRL_INPUTS_CP_ICACHE_EN_READBACK_IN_DEBUG_ZERO) : -1),
                   .kv(t.ext_ic_scr_key_valid ? GEN_FC_SEC_CTRL_INPUTS_CP_RVFI_EXT_KEY_VALID_ONE : GEN_FC_SEC_CTRL_INPUTS_CP_RVFI_EXT_KEY_VALID_ZERO));
      if (is_csr && csr == ibex_pkg::CSR_MCOUNTEREN && is_write) begin   // the effect waits for the program's read-back
        mcen_old = t.rd_wdata; mcen_new = (f3[1:0] == 2'b01) ? opnd : (f3[1:0] == 2'b10) ? (t.rd_wdata | opnd) : (t.rd_wdata & ~opnd); mcen_pend = (t.rd_addr != 0);   // the set / clear result from the read-back old value
        mcen_pin_cls = (ctrl_vif.mcounteren_writable == ibex_pkg::IbexMuBiOn) ? GEN_FC_SEC_CTRL_INPUTS_CP_MCOUNTEREN_W_VAL_ON : (ctrl_vif.mcounteren_writable == ibex_pkg::IbexMuBiOff) ? GEN_FC_SEC_CTRL_INPUTS_CP_MCOUNTEREN_W_VAL_OFF : GEN_FC_SEC_CTRL_INPUTS_CP_MCOUNTEREN_W_VAL_INVALID;
        if (!mcen_pend) sec_sample(GEN_FC_SEC_CTRL_INPUTS_CP_EVENT_MCOUNTEREN_WRITE, .mw(mcen_pin_cls));   // no old value to compare: effect na
      end
    endfunction
    task run_phase(uvm_phase phase);
      ibex_pkg::ibex_mubi_t fe_q, mw_q;
      @(posedge ctrl_vif.rst_n);
      rst_fetch_en = mubi_cls_rst(ctrl_vif.fetch_enable);
      rst_pending = rst_pending_cls(irq_vif.lines()[17:0], irq_vif.nm, dbg_vif.req);
      rst_release_seen = 1;
      irq_rst_pins = irq_vif.lines(); irq_rst_dbg = dbg_vif.req;   // CG-IRQ-011 ev_reset: the pins latched at the release
      irq_rst_lines = irq_rst_lines_bin(irq_rst_pins, irq_rst_dbg); irq_rst_have = 1;
      fe_q = ctrl_vif.fetch_enable; mw_q = ctrl_vif.mcounteren_writable;
      forever begin
        @(posedge ctrl_vif.clk);
        if (ctrl_vif.fetch_enable != fe_q) begin fe_q = ctrl_vif.fetch_enable; sec_sample(GEN_FC_SEC_CTRL_INPUTS_CP_EVENT_FETCH_EN_CHANGE, .fe(mubi_cls_sec(fe_q))); end
        if (ctrl_vif.mcounteren_writable != mw_q) begin
          mw_q = ctrl_vif.mcounteren_writable;
          sec_sample(GEN_FC_SEC_CTRL_INPUTS_CP_EVENT_MCOUNTEREN_W_CHANGE, .mw((mw_q == ibex_pkg::IbexMuBiOn) ? GEN_FC_SEC_CTRL_INPUTS_CP_MCOUNTEREN_W_VAL_ON : (mw_q == ibex_pkg::IbexMuBiOff) ? GEN_FC_SEC_CTRL_INPUTS_CP_MCOUNTEREN_W_VAL_OFF : GEN_FC_SEC_CTRL_INPUTS_CP_MCOUNTEREN_W_VAL_INVALID));
        end
      end
    endtask
    // ---- PMP: the model's table and the samplers of CG-PMP-004 and CG-PMP-014 ----------------------------
    // The table read here is the MODEL's, through the ISA shim (gen_isa_read_csr passes the CSR number to the
    // model). MEASURED, not assumed: at this subscriber the model has NOT yet executed the record being handled,
    // so the read is the state BEFORE it. A write's effect is therefore read at the NEXT record, which is also the
    // grain CG-PMP-014 asks for (a snapshot counts only once a record retires after the table change).
    gen_pmp_csr_access_cg  pmp_acc_cg;
    gen_pmp_table_state_cg pmp_tbl_cg;
    logic [7:0]  pmp_cfg_now [16], pmp_cfg_pre [16];
    logic [31:0] pmp_addr_now [16], pmp_addr_pre [16];
    logic [31:0] pmp_msec_now = '0, pmp_msec_pre = '0;
    bit pmp_have_pre = 0, pmp_wr_pend = 0;
    // cp_first_after_reset is per CSR CLASS, as the plan defines it: one run-wide flag let at most one
    // of the four class bins ever read yes
    bit pmp_first_acc [4] = '{1, 1, 1, 1};
    int unsigned n_pmp_acc = 0, n_pmp_tbl = 0, n_pmp_tbl_dropped = 0;
    // CG-PMP-014 defers: a snapshot is sampled only once a record retires before the next table change (the plan's
    // condition), which is also when cp_all_off_u is decided.
    bit pmp_snap_pend = 0, pmp_snap_all_off = 0, pmp_snap_u_seen = 0;
    int pmp_snap [10]; int unsigned pmp_snap_retires = 0;

    function void pmp_read_now();
      logic [31:0] v;
      for (int w = 0; w < 4; w++) begin
        v = gen_isa_read_csr(int'(ibex_pkg::CSR_PMPCFG0) + w);
        for (int b = 0; b < 4; b++) pmp_cfg_now[4*w + b] = v[8*b +: 8];
      end
      for (int i = 0; i < 16; i++) pmp_addr_now[i] = gen_isa_read_csr(int'(ibex_pkg::CSR_PMPADDR0) + i);
      pmp_msec_now = gen_isa_read_csr(int'(ibex_pkg::CSR_MSECCFG));
    endfunction

    function void pmp_keep_pre();
      for (int i = 0; i < 16; i++) begin pmp_cfg_pre[i] = pmp_cfg_now[i]; pmp_addr_pre[i] = pmp_addr_now[i]; end
      pmp_msec_pre = pmp_msec_now; pmp_have_pre = 1;
    endfunction

    // 0 pmpcfg, 1 pmpaddr, 2 mseccfg, 3 mseccfgh, -1 not a PMP CSR instruction; idx = the entry or word index
    function int pmp_csr_class(logic [31:0] insn, output int idx);
      logic [11:0] csr = insn[31:20];
      logic [11:0] c_cfg = 12'(ibex_pkg::CSR_PMPCFG0), c_addr = 12'(ibex_pkg::CSR_PMPADDR0);
      logic [11:0] c_ms = 12'(ibex_pkg::CSR_MSECCFG), c_msh = 12'(ibex_pkg::CSR_MSECCFGH);
      idx = -1;
      if (insn[6:0] != ibex_pkg::OPCODE_SYSTEM || insn[14:12] == 3'b000) return -1;
      if (csr >= c_cfg && csr < c_cfg + 4) begin idx = int'(csr - c_cfg); return 0; end
      if (csr >= c_addr && csr < c_addr + 16) begin idx = int'(csr - c_addr); return 1; end
      if (csr == c_ms) return 2;
      if (csr == c_msh) return 3;
      return -1;
    endfunction

    // the CSR op bin of a system instruction, in the plan's order; -1 when funct3 names none
    function int pmp_op_bin(logic [31:0] insn);
      case (insn[14:12])
        3'b001: return GEN_FC_PMP_CSR_ACCESS_CP_OP_CSRRW;
        3'b010: return GEN_FC_PMP_CSR_ACCESS_CP_OP_CSRRS;
        3'b011: return GEN_FC_PMP_CSR_ACCESS_CP_OP_CSRRC;
        3'b101: return GEN_FC_PMP_CSR_ACCESS_CP_OP_CSRRWI;
        3'b110: return GEN_FC_PMP_CSR_ACCESS_CP_OP_CSRRSI;
        3'b111: return GEN_FC_PMP_CSR_ACCESS_CP_OP_CSRRCI;
        default: return -1;
      endcase
    endfunction

    // a set/clear whose operand is zero writes nothing; csrrw / csrrwi always write
    function bit pmp_is_write(logic [31:0] insn);
      bit set_clear = insn[13:12] inside {2'b10, 2'b11};
      return !set_clear || insn[19:15] != 5'd0;
    endfunction

    // CG-PMP-004: every PMP CSR instruction, trapped ones included
    function void pmp_acc_sample(gen_rvfi_txn t);
      int idx, cls = pmp_csr_class(t.insn, idx);
      int v_cls, v_priv, v_op;
      if (cls < 0 || pmp_acc_cg == null) return;
      case (cls)
        0: v_cls = GEN_FC_PMP_CSR_ACCESS_CP_CLASS_PMPCFG;
        1: v_cls = GEN_FC_PMP_CSR_ACCESS_CP_CLASS_PMPADDR;
        2: v_cls = GEN_FC_PMP_CSR_ACCESS_CP_CLASS_MSECCFG;
        default: v_cls = GEN_FC_PMP_CSR_ACCESS_CP_CLASS_MSECCFGH;
      endcase
      v_priv = (t.mode == 2'b11) ? GEN_FC_PMP_CSR_ACCESS_CP_PRIV_M :
               (t.mode == 2'b00) ? GEN_FC_PMP_CSR_ACCESS_CP_PRIV_U : -1;
      v_op = pmp_op_bin(t.insn);
      pmp_acc_cg.sample(v_cls, v_priv,
                        t.ext_debug_mode ? GEN_FC_PMP_CSR_ACCESS_CP_DBG_D1 : GEN_FC_PMP_CSR_ACCESS_CP_DBG_D0,
                        v_op,
                        pmp_is_write(t.insn) ? GEN_FC_PMP_CSR_ACCESS_CP_RW_WRITE
                                             : GEN_FC_PMP_CSR_ACCESS_CP_RW_READ_ONLY,
                        // the plan names mcause 2; rvfi_trap is ONE BIT here (gen_rvfi_if.sv:8) so the cause is
                        // not on the record, and the model state that carries mcause arrives on another
                        // callback. Any retired trap on a PMP CSR access is booked illegal, which is sound
                        // for this DUT (a PMP CSR access traps only as an illegal instruction) but is a
                        // classification by elimination rather than a read of the cause
                        t.trap ? GEN_FC_PMP_CSR_ACCESS_CP_TRAP_ILLEGAL : GEN_FC_PMP_CSR_ACCESS_CP_TRAP_NONE,
                        pmp_first_acc[cls] ? GEN_FC_PMP_CSR_ACCESS_CP_FIRST_AFTER_RESET_YES
                                           : GEN_FC_PMP_CSR_ACCESS_CP_FIRST_AFTER_RESET_NO);
      n_pmp_acc++; pmp_first_acc[cls] = 0;
    endfunction

    // the byte range of entry i in words of four bytes, from the model's table; returns 0 when the entry is off
    function bit pmp_range(int i, output logic [33:0] lo, output logic [33:0] hi);
      logic [1:0] a = pmp_cfg_now[i][4:3];
      logic [31:0] addr = pmp_addr_now[i];
      logic [33:0] base;
      int k;
      lo = '0; hi = '0;
      case (a)
        2'b00: return 1'b0;
        2'b01: begin lo = (i == 0) ? '0 : {2'b0, pmp_addr_now[i-1]}; hi = {2'b0, addr}; return hi > lo; end
        2'b10: begin lo = {2'b0, addr}; hi = lo + 1; return 1'b1; end
        default: begin
          k = 0;
          while (k < 32 && addr[k] == 1'b1) k++;      // NAPOT: the run of low ones sets the size
          base = {2'b0, addr} & ~((34'd1 << (k + 1)) - 1);
          lo = base; hi = base + (34'd1 << (k + 1));
          return 1'b1;
        end
      endcase
    endfunction

    // CG-PMP-014's ten values from the table this class last read
    function void pmp_snap_build();
      int n_active = 0, n_locked = 0, n_tor_empty = 0, n_overlap = 0;
      bit have_tor = 0, have_na = 0;
      logic [33:0] lo_i, hi_i, lo_j, hi_j;
      for (int i = 0; i < 16; i++) begin
        if (pmp_cfg_now[i][4:3] != 2'b00) begin
          n_active++;
          if (pmp_cfg_now[i][4:3] == 2'b01) begin
            logic [33:0] prev = (i == 0) ? '0 : {2'b0, pmp_addr_now[i-1]};
            have_tor = 1;
            if (prev >= {2'b0, pmp_addr_now[i]}) n_tor_empty++;
          end else have_na = 1;
        end
        if (pmp_cfg_now[i][7]) n_locked++;
      end
      for (int i = 0; i < 16; i++)
        for (int j = i + 1; j < 16; j++)
          if (pmp_range(i, lo_i, hi_i) && pmp_range(j, lo_j, hi_j) && lo_i < hi_j && lo_j < hi_i) n_overlap++;
      pmp_snap[0] = (n_active == 0) ? GEN_FC_PMP_TABLE_STATE_CP_ACTIVE_N0 :
                    (n_active == 1) ? GEN_FC_PMP_TABLE_STATE_CP_ACTIVE_N1 :
                    (n_active <= 4) ? GEN_FC_PMP_TABLE_STATE_CP_ACTIVE_N2_4 :
                    (n_active <= 8) ? GEN_FC_PMP_TABLE_STATE_CP_ACTIVE_N5_8 :
                    (n_active <= 15) ? GEN_FC_PMP_TABLE_STATE_CP_ACTIVE_N9_15 : GEN_FC_PMP_TABLE_STATE_CP_ACTIVE_N16;
      pmp_snap[1] = (n_locked == 0) ? GEN_FC_PMP_TABLE_STATE_CP_LOCKED_N0 :
                    (n_locked <= 4) ? GEN_FC_PMP_TABLE_STATE_CP_LOCKED_N1_4 :
                    (n_locked <= 15) ? GEN_FC_PMP_TABLE_STATE_CP_LOCKED_N5_15 : GEN_FC_PMP_TABLE_STATE_CP_LOCKED_N16;
      pmp_snap[2] = (!have_tor && !have_na) ? GEN_FC_PMP_TABLE_STATE_CP_MODES_NONE :
                    (have_tor && !have_na)  ? GEN_FC_PMP_TABLE_STATE_CP_MODES_TOR_ONLY :
                    (!have_tor && have_na)  ? GEN_FC_PMP_TABLE_STATE_CP_MODES_NA_ONLY :
                                              GEN_FC_PMP_TABLE_STATE_CP_MODES_MIXED;
      pmp_snap[3] = (n_tor_empty == 0) ? GEN_FC_PMP_TABLE_STATE_CP_TOR_EMPTY_NONE : GEN_FC_PMP_TABLE_STATE_CP_TOR_EMPTY_SOME;
      pmp_snap[4] = (n_overlap == 0) ? GEN_FC_PMP_TABLE_STATE_CP_OVERLAP_NONE : GEN_FC_PMP_TABLE_STATE_CP_OVERLAP_SOME;
      case (cfg.knob_pmp_regime)
        "sparse":  pmp_snap[5] = GEN_FC_PMP_TABLE_STATE_CP_REGIME_SPARSE;
        "dense":   pmp_snap[5] = GEN_FC_PMP_TABLE_STATE_CP_REGIME_DENSE;
        "mml_on":  pmp_snap[5] = GEN_FC_PMP_TABLE_STATE_CP_REGIME_MML_ON;
        default:   pmp_snap[5] = GEN_FC_PMP_TABLE_STATE_CP_REGIME_OFF;
      endcase
      pmp_snap[6] = GEN_FC_PMP_TABLE_STATE_CP_ALL_OFF_U_NO;   // resolved when the snapshot closes
      pmp_snap[7] = (pmp_cfg_now[15][4:3] == 2'b00) ? GEN_FC_PMP_TABLE_STATE_CP_E15_OFF : GEN_FC_PMP_TABLE_STATE_CP_E15_ACTIVE;
      pmp_snap[8] = (pmp_cfg_now[0][4:3] == 2'b01) ? GEN_FC_PMP_TABLE_STATE_CP_E0_TOR_YES : GEN_FC_PMP_TABLE_STATE_CP_E0_TOR_NO;
      pmp_snap[9] = GEN_FC_PMP_TABLE_STATE_CP_MSECCFG_S000 + int'(pmp_msec_now[2:0]);
      pmp_snap_all_off = (n_active == 0);
      pmp_snap_pend = 1; pmp_snap_retires = 0; pmp_snap_u_seen = 0;
    endfunction

    // the plan's condition: a snapshot counts only when a record retires before the next table change
    function void pmp_snap_close();
      if (!pmp_snap_pend) return;
      if (pmp_snap_retires == 0) begin n_pmp_tbl_dropped++; pmp_snap_pend = 0; return; end
      if (pmp_snap_all_off && pmp_snap_u_seen) pmp_snap[6] = GEN_FC_PMP_TABLE_STATE_CP_ALL_OFF_U_YES;
      if (pmp_tbl_cg != null) begin
        pmp_tbl_cg.sample(pmp_snap[0], pmp_snap[1], pmp_snap[2], pmp_snap[3], pmp_snap[4],
                          pmp_snap[5], pmp_snap[6], pmp_snap[7], pmp_snap[8], pmp_snap[9]);
        n_pmp_tbl++;
      end
      pmp_snap_pend = 0;
    endfunction

    // one entry point per retired record
    function void pmp_record(gen_rvfi_txn t);
      int idx, cls = pmp_csr_class(t.insn, idx);
      if (pmp_acc_cg == null) return;
      pmp_read_now();                 // the model state BEFORE this record executes
      if (pmp_wr_pend) begin          // the read above is the effect of the write one record back
        pmp_snap_close();             // the snapshot that write replaced closes first
        if (pmp_wr_idx >= 0) begin
          if (pmp_wr_is_cfg) pmp_cfg_sample(); else pmp_addr_sample();
        end
        pmp_snap_build();
        pmp_wr_pend = 0;
      end
      if (cls >= 0) pmp_acc_sample(t);
      if (pmp_snap_pend) begin
        pmp_snap_retires++;
        if (t.mode == 2'b00) pmp_snap_u_seen = 1;
      end
      if (cls >= 0 && !t.trap && pmp_is_write(t.insn)) begin
        logic [31:0] old_w = '0;
        pmp_keep_pre();               // this record's pre-state is the table the write starts from
        pmp_wr_pend = 1; pmp_wr_is_cfg = (cls == 0); pmp_wr_idx = (cls <= 1) ? idx : -1;
        pmp_wr_op = (cls == 0) ? pmp_op_class_cfg(t) : pmp_op_class_addr(t);
        if (cls == 0) begin
          for (int b = 0; b < 4; b++) old_w[8*b +: 8] = pmp_cfg_pre[4*idx + b];
          pmp_wr_val = pmp_rmw(t, old_w);
        end else if (cls == 1) begin
          pmp_wr_val = pmp_rmw(t, pmp_addr_pre[idx]);
        end
      end
    endfunction

    // the run's last record leaves a write unread: at the report phase the model has executed everything
    function void pmp_final();
      if (!pmp_wr_pend) return;
      pmp_read_now();
      pmp_snap_close();
      if (pmp_wr_idx >= 0) begin
        if (pmp_wr_is_cfg) pmp_cfg_sample(); else pmp_addr_sample();
      end
      pmp_snap_build();
      pmp_wr_pend = 0;
    endfunction

    // ---- CG-PMP-001 and CG-PMP-002: the two write groups -------------------------------------------------
    gen_pmp_cfg_write_cg  pmp_cfg_cg;
    gen_pmp_addr_write_cg pmp_addr_cg;
    int unsigned n_pmp_addr_readback_odd = 0;
    int unsigned n_pmp_cfg = 0, n_pmp_addr = 0;
    // the write being resolved: its facts are taken at the write record, its outcome at the next one
    bit pmp_wr_is_cfg = 0; int pmp_wr_idx = -1; logic [31:0] pmp_wr_val = '0; int pmp_wr_op = -1;

    // the value a CSR instruction attempts to write, after the read-modify-write combine
    function logic [31:0] pmp_rmw(gen_rvfi_txn t, logic [31:0] old_w);
      logic [31:0] opnd = t.insn[14] ? {27'b0, t.insn[19:15]} : t.rs1_rdata;
      case (t.insn[13:12])
        2'b01: return opnd;
        2'b10: return old_w | opnd;
        default: return old_w & ~opnd;
      endcase
    endfunction

    // the plan's three op classes: the immediate forms share a bin with their register form
    function int pmp_op_class_cfg(gen_rvfi_txn t);
      case (t.insn[13:12])
        2'b01: return GEN_FC_PMP_CFG_WRITE_CP_OP_CSRRW;
        2'b10: return GEN_FC_PMP_CFG_WRITE_CP_OP_CSRRS;
        default: return GEN_FC_PMP_CFG_WRITE_CP_OP_CSRRC;
      endcase
    endfunction

    function int pmp_op_class_addr(gen_rvfi_txn t);
      case (t.insn[13:12])
        2'b01: return GEN_FC_PMP_ADDR_WRITE_CP_OP_CSRRW;
        2'b10: return GEN_FC_PMP_ADDR_WRITE_CP_OP_CSRRS;
        default: return GEN_FC_PMP_ADDR_WRITE_CP_OP_CSRRC;
      endcase
    endfunction

    // CG-PMP-001: one sample per entry byte of the written word, resolved against the readback
    // the byte the DUT would store for an attempted cfg byte: bits 6:5 have no field in pmp_cfg_t
    // (rtl/ibex_cs_registers.sv:1429-1437 assigns lock from bit 7, mode from [4:3], RWX from [2:0]), and W
    // is dropped when R is clear while MML is 0
    function logic [7:0] pmp_stored_byte(logic [7:0] a_b, bit mml);
      logic [7:0] s = a_b & 8'h9f;
      if (!mml && !s[0] && s[1]) s[1] = 1'b0;
      return s;
    endfunction
    // the RTL's executable-lock set, is_mml_m_exec_cfg (rtl/ibex_cs_registers.sv:164-176): with lock set,
    // {read, write, exec} in {001, 010, 011, 101} only. A locked RWX=111 row IS written under MML.
    function bit pmp_mml_exec_lock(logic [7:0] a_b);
      return a_b[7] && ({a_b[0], a_b[1], a_b[2]} inside {3'b001, 3'b010, 3'b011, 3'b101});
    endfunction
    function void pmp_cfg_sample();
      logic [31:0] old_w = '0;
      logic [31:0] att;
      logic [7:0]  a_b, pre_b, post_b, exp_b;
      int lockmix = 0, v_lrwx, v_outcome;
      bit mml = pmp_msec_pre[ibex_pkg::CSR_MSECCFG_MML_BIT], rlb = pmp_msec_pre[ibex_pkg::CSR_MSECCFG_RLB_BIT];
      if (pmp_cfg_cg == null || pmp_wr_idx < 0) return;
      for (int b = 0; b < 4; b++) old_w[8*b +: 8] = pmp_cfg_pre[4*pmp_wr_idx + b];
      att = pmp_wr_val;                                     // the attempted word, already combined
      for (int b = 0; b < 4; b++) if (!rlb && pmp_cfg_pre[4*pmp_wr_idx + b][7]) lockmix++;
      for (int b = 0; b < 4; b++) begin
        int i = 4*pmp_wr_idx + b;
        a_b = att[8*b +: 8]; pre_b = pmp_cfg_pre[i]; post_b = pmp_cfg_now[i];
        v_lrwx = GEN_FC_PMP_CFG_WRITE_CP_WR_LRWX_C0000 + int'({a_b[7], a_b[0], a_b[1], a_b[2]});
        exp_b = pmp_stored_byte(a_b, mml);
        // the outcome compares the stored byte against what the DUT WOULD store, not against the raw
        // attempted byte: bits 6:5 are never stored and W is dropped when R is clear under MML=0, so a raw
        // comparison books a reserved-bit-only write as ignored on an unlocked entry and a W-drop as written
        if (post_b == pre_b && exp_b != pre_b) begin
          v_outcome = (mml && !rlb && pmp_mml_exec_lock(a_b))
                      ? GEN_FC_PMP_CFG_WRITE_CP_OUTCOME_IGNORED_MML_EXEC
                      : GEN_FC_PMP_CFG_WRITE_CP_OUTCOME_IGNORED_LOCK;
        end else if (post_b == exp_b && exp_b != (a_b & 8'h9f)) begin
          v_outcome = GEN_FC_PMP_CFG_WRITE_CP_OUTCOME_W_DROPPED;   // the write landed with W dropped
        end else begin
          v_outcome = GEN_FC_PMP_CFG_WRITE_CP_OUTCOME_WRITTEN;
        end
        pmp_cfg_cg.sample(GEN_FC_PMP_CFG_WRITE_CP_ENTRY_E0 + i,
                          pmp_wr_op,
                          GEN_FC_PMP_CFG_WRITE_CP_WR_MODE_OFF + int'(a_b[4:3]),
                          v_lrwx,
                          (a_b[6:5] == 2'b00) ? GEN_FC_PMP_CFG_WRITE_CP_RES_BITS_ZERO
                                              : GEN_FC_PMP_CFG_WRITE_CP_RES_BITS_NONZERO,
                          mml ? GEN_FC_PMP_CFG_WRITE_CP_MML_MML1 : GEN_FC_PMP_CFG_WRITE_CP_MML_MML0,
                          rlb ? GEN_FC_PMP_CFG_WRITE_CP_RLB_RLB1 : GEN_FC_PMP_CFG_WRITE_CP_RLB_RLB0,
                          pre_b[7] ? GEN_FC_PMP_CFG_WRITE_CP_PRELOCK_LOCKED
                                   : GEN_FC_PMP_CFG_WRITE_CP_PRELOCK_UNLOCKED,
                          v_outcome,
                          (lockmix == 0) ? GEN_FC_PMP_CFG_WRITE_CP_WORD_LOCKMIX_NONE :
                          (lockmix == 4) ? GEN_FC_PMP_CFG_WRITE_CP_WORD_LOCKMIX_ALL
                                         : GEN_FC_PMP_CFG_WRITE_CP_WORD_LOCKMIX_SOME);
        n_pmp_cfg++;
      end
    endfunction

    // CG-PMP-002: one sample per pmpaddr write, resolved against the readback
    function void pmp_addr_sample();
      int i = pmp_wr_idx, v_outcome, v_next;
      bit rlb = pmp_msec_pre[ibex_pkg::CSR_MSECCFG_RLB_BIT];
      // cp_self_lock and cp_next_cfg carry the RAW lock bit; RLB is carried by cp_rlb alone, so the cross of
      // the two expresses the effective lock. Encoding RLB in both made the components dependent and two
      // declared cross bins unreachable. The effective lock stays, for the OUTCOME rule only.
      bit self_locked = pmp_cfg_pre[i][7];
      bit self_blocked = self_locked && !rlb;
      bit next_locked, next_blocked, next_tor;
      if (pmp_addr_cg == null || i < 0) return;
      next_tor = (i < 15) && (pmp_cfg_pre[i+1][4:3] == 2'b01);
      next_blocked = (i < 15) && pmp_cfg_pre[i+1][7] && !rlb;
      // the outcome is decided by the PRE-STATE rule and only CONFIRMED by the readback: a locked entry
      // rewritten with its current value reads back equal and is still ignored
      if (self_blocked)            v_outcome = GEN_FC_PMP_ADDR_WRITE_CP_OUTCOME_IGNORED_SELF_LOCK;
      else if (next_blocked && next_tor) v_outcome = GEN_FC_PMP_ADDR_WRITE_CP_OUTCOME_IGNORED_TOR_LOCK;
      else                         v_outcome = GEN_FC_PMP_ADDR_WRITE_CP_OUTCOME_WRITTEN;
      // the readback must agree with the rule; a disagreement is counted and reported, never absorbed
      if ((v_outcome == GEN_FC_PMP_ADDR_WRITE_CP_OUTCOME_WRITTEN) != (pmp_addr_now[i] == pmp_wr_val))
        n_pmp_addr_readback_odd++;
      if (i == 15) v_next = GEN_FC_PMP_ADDR_WRITE_CP_NEXT_CFG_TOP;
      else begin
        next_locked = pmp_cfg_pre[i+1][7];
        v_next = next_locked ? (next_tor ? GEN_FC_PMP_ADDR_WRITE_CP_NEXT_CFG_NEXT_LOCKED_TOR
                                         : GEN_FC_PMP_ADDR_WRITE_CP_NEXT_CFG_NEXT_LOCKED_OTHER)
                             : (next_tor ? GEN_FC_PMP_ADDR_WRITE_CP_NEXT_CFG_NEXT_UNLOCKED_TOR
                                         : GEN_FC_PMP_ADDR_WRITE_CP_NEXT_CFG_NEXT_UNLOCKED_OTHER);
      end
      pmp_addr_cg.sample(GEN_FC_PMP_ADDR_WRITE_CP_IDX_A0 + i,
                         pmp_wr_op,
                         self_locked ? GEN_FC_PMP_ADDR_WRITE_CP_SELF_LOCK_LOCKED
                                     : GEN_FC_PMP_ADDR_WRITE_CP_SELF_LOCK_UNLOCKED,
                         v_next,
                         rlb ? GEN_FC_PMP_ADDR_WRITE_CP_RLB_RLB1 : GEN_FC_PMP_ADDR_WRITE_CP_RLB_RLB0,
                         v_outcome,
                         GEN_FC_PMP_ADDR_WRITE_CP_HI_BITS_NONE + int'(pmp_wr_val[31:30]),
                         GEN_FC_PMP_ADDR_WRITE_CP_SELF_MODE_OFF + int'(pmp_cfg_pre[i][4:3]));
      n_pmp_addr++;
    endfunction

    function void write(gen_rvfi_txn t);
      logic [6:0] f7 = t.insn[31:25]; logic [2:0] f3 = t.insn[14:12];
      bit is_op = (t.insn[6:0] == ibex_pkg::OPCODE_OP), is_opimm = (t.insn[6:0] == ibex_pkg::OPCODE_OP_IMM);
      bit is_cmul = (t.insn[1:0] == 2'b01 && t.insn[15:10] == 6'b100111 && t.insn[6:5] == 2'b10);   // c.mul (Zcb)
      if (mul_cg == null) return;
      prev_rec_cycle = cur_rec_cycle; cur_rec_cycle = t.cycle;
      mt_flush(t);
      hz_flush(t);
      dt_flush(t);
      hx_flush(t);
      rec_sample(t);
      pmp_record(t);
      irq_last_t = t; irq_have_t = 1;   // the state for this record arrives next
      if (!rst_sampled) rst_sample(rst_first_event_cls(t.intr, t.ext_nmi, t.ext_debug_mode));
      sec_record(t);
      last_t = prev_t; have_last = have_prev;   // the neighbour facts of the rest of write() (the multiply's cp_prev / cp_delta) read the record before this one
      prev_t = t; have_prev = 1;
      mv_flush(t);
      zcmp_flush(t);
      zca_flush(t);
      // an instruction boundary (a plain record, or the first micro-op of an expansion) closes the write set of the instruction before
      if (!t.ext_exp_valid || !zp_in || t.pc_rdata != zp_pc) begin prev_wr = cur_wr; prev_ld = cur_ld; prev_mv = cur_mv; cur_wr = '0; cur_ld = 0; cur_mv = -1; end
      if (!t.trap && t.rd_addr != 0) cur_wr[t.rd_addr] = 1'b1;
      begin bit st; int unsigned nb; if (gen_insn_mem_access(t.insn, st, nb) && !st) cur_ld = 1; end   // decoded: Ibex reports rvfi_mem_rmask for non-memory records too
      if (t.ext_exp_valid) begin   // a Zcmp micro-op record: the sequence collector owns it
        if (zp_in && t.pc_rdata != zp_pc) n_zcmp_abandoned++;   // a sequence replaced by another one's first micro-op (an entry split it)
        if (!zp_in || t.pc_rdata != zp_pc) zp_start(t);
        if (t.trap) begin zp_in = 0; n_zcmp_abandoned++; end else zp_step(t);
      end else if (zp_in) begin zp_in = 0; n_zcmp_abandoned++; end   // an entry split the sequence (its restart begins again)
      if (t.trap) begin sb_prev_binv = 0; return; end   // a trap record breaks a binv pair like any other record
      if (!t.ext_exp_valid && t.insn[1:0] != 2'b11) begin   // a Zca retirement: pending until the next record's length is known
        int op = zca_insn(t.insn[15:0]);
        if (op >= 0) begin
          n_zca++;
          zca_v[0] = op; zca_v[1] = t.pc_rdata[1] ? GEN_FC_CMP_ZCA_CP_PC_ALIGN_HALF : GEN_FC_CMP_ZCA_CP_PC_ALIGN_WORD;
          zca_v[3] = (!zca_is_cti(op) && t.pc_wdata - t.pc_rdata == 32'd2) ? GEN_FC_CMP_ZCA_CP_PC_INC_TWO : -1;
          zca_v[4] = -1; zca_v[5] = zca_reg3(op, t.insn[15:0]); zca_v[6] = zca_rd_full(op, t.insn[15:0]);
          zca_pend = 1;
        end
      end else if (!t.ext_exp_valid && t.insn[1:0] == 2'b11) begin   // a 32-bit retirement: only the straddle coverpoint
        n_zca32++;
        zca_cg.sample(-1, -1, -1, -1, t.pc_rdata[1] ? GEN_FC_CMP_ZCA_CP_INSN32_STRADDLE_YES : GEN_FC_CMP_ZCA_CP_INSN32_STRADDLE_NO, -1, -1);
      end
      if (t.ext_exp_valid) begin sb_prev_binv = 0; return; end   // a micro-op record belongs to the collector, not to the base groups
      if (t.insn[1:0] != 2'b11) ie_sample(t); else lu_sample(t);   // Slice B: the groups no later branch of this chain owns
      jp_sample(t);
      hx_sample(t);
      if (sbit_sample(t)) return;
      sb_prev_binv = 0;
      void'(zcb_sample(t));   // c.mul also samples the M-extension group below
      if (br_sample(t) || csr_track(t)) return;
      if (is_opimm && f3 == 3'b001 && t.insn[31:20] inside {12'h600, 12'h601, 12'h602}) begin
        int op = (t.insn[31:20] == 12'h600) ? GEN_FC_BIT_COUNT_CP_OP_CLZ : (t.insn[31:20] == 12'h601) ? GEN_FC_BIT_COUNT_CP_OP_CTZ : GEN_FC_BIT_COUNT_CP_OP_CPOP;
        n_cnt++;
        ut_last_cnt = '{op, cnt_operand_cls(t.rs1_rdata), cnt_single_pos(t.rs1_rdata), (t.rd_addr == 0) ? -1 : cnt_result_cls(t.rd_wdata), t.rd_addr == 0};
        if (t.rd_addr == 0) n_cnt_res_na++;
        cnt_cg.sample(ut_last_cnt[0], ut_last_cnt[1], ut_last_cnt[2], ut_last_cnt[3], ut_last_cnt[4]);
        return;
      end
      if ((is_op && f7 == 7'b0000001 && !f3[2]) || is_cmul) begin
        int op = is_cmul ? GEN_FC_MUL_OPS_CP_OP_C_MUL : int'(f3[1:0]);   // mul, mulh, mulhsu, mulhu in funct3 order
        n_mul++;
        mul_cg.sample(op, mul_rs_cls(t.rs1_rdata), mul_rs_cls(t.rs2_rdata), sign_pair(t.rs1_rdata, t.rs2_rdata),
                      mul_same(t.rs1_addr, t.rs2_addr, t.rd_addr), t.rd_addr == 0, (t.rd_addr == 0) ? -1 : mul_res_cls(t.rd_wdata), is_cmul ? -1 : int'(f3));
        if (!is_cmul) mt_sample(t, int'(f3[1:0]));
      end else if (is_op && f7 == 7'b0000001) begin
        n_div++;
        div_cg.sample(int'(f3[1:0]), div_dividend_cls(t.rs1_rdata), div_divisor_cls(t.rs2_rdata, t.rs1_rdata), sign_pair(t.rs1_rdata, t.rs2_rdata),
                      t.rd_addr == 0, (t.rd_addr == 0) ? -1 : div_res_cls(t.rd_wdata, t.rs1_rdata));
        dt_sample(t, int'(f3[1:0]));
      end else if (bit_op(t.insn) >= 0) begin
        int op = bit_op(t.insn);
        n_bit++;
        bit_cg.sample(op, bit_rs1_cls(t.rs1_rdata), bit_rs2_cls(t.rs2_rdata), t.rs1_rdata == t.rs2_rdata, bit_same(t.rs1_addr, t.rs2_addr, t.rd_addr),
                      t.rd_addr == 0, sign_pair(t.rs1_rdata, t.rs2_rdata), (t.rd_addr == 0) ? -1 : bit_res_cls(t.rd_wdata), bit_wrap(op, t.rs1_rdata, t.rs2_rdata));
      end else if (is_opimm && f3 != 3'b001 && f3 != 3'b101) begin
        int op, imm = signed'(t.insn[31:20]);   // sign-extended imm12
        case (f3)
          3'b000: op = GEN_FC_ISA_ALU_IMM_CP_OP_ADDI; 3'b010: op = GEN_FC_ISA_ALU_IMM_CP_OP_SLTI; 3'b011: op = GEN_FC_ISA_ALU_IMM_CP_OP_SLTIU;
          3'b100: op = GEN_FC_ISA_ALU_IMM_CP_OP_XORI; 3'b110: op = GEN_FC_ISA_ALU_IMM_CP_OP_ORI;  default: op = GEN_FC_ISA_ALU_IMM_CP_OP_ANDI;
        endcase
        n_imm++;
        ut_last_imm = '{op, imm_rs1_cls(t.rs1_rdata), imm_cls(imm), t.rd_addr == 0, (t.rs1_addr == t.rd_addr && t.rd_addr != 0), (t.rd_addr == 0) ? -1 : imm_res_cls(t.rd_wdata),
                        addi_wrap(op, t.rs1_rdata, imm), slt_case(op, t.rs1_rdata, imm)};
        if (ut_last_imm[7] == GEN_FC_ISA_ALU_IMM_CP_SLT_CASE_EQ) n_slt_eq++;
        imm_cg.sample(ut_last_imm[0], ut_last_imm[1], ut_last_imm[2], ut_last_imm[3], ut_last_imm[4], ut_last_imm[5], ut_last_imm[6], ut_last_imm[7]);
      end else if ((is_opimm || is_op) && (f3 == 3'b001 || f3 == 3'b101) && (f7 == 7'b0000000 || f7 == 7'b0100000) && !(f3 == 3'b001 && f7 == 7'b0100000)) begin
        int op;
        if (is_opimm) op = (f3 == 3'b001) ? GEN_FC_ISA_SHIFT_CP_OP_SLLI : (f7 == 7'b0100000) ? GEN_FC_ISA_SHIFT_CP_OP_SRAI : GEN_FC_ISA_SHIFT_CP_OP_SRLI;
        else          op = (f3 == 3'b001) ? GEN_FC_ISA_SHIFT_CP_OP_SLL  : (f7 == 7'b0100000) ? GEN_FC_ISA_SHIFT_CP_OP_SRA  : GEN_FC_ISA_SHIFT_CP_OP_SRL;
        n_sh++;
        sh_cg.sample(op, sh_amt_cls(is_opimm ? t.insn[24:20] : t.rs2_rdata[4:0]), is_opimm ? -1 : sh_rs2_upper(t.rs2_rdata), sh_operand_cls(t.rs1_rdata),
                     t.rd_addr == 0, (t.rd_addr == 0) ? -1 : sh_res_cls(t.rd_wdata));
      end else if (is_op && (f7 == 7'b0000000 || f7 == 7'b0100000) && f3 != 3'b001 && f3 != 3'b101 && !(f7 == 7'b0100000 && f3 != 3'b000)) begin
        int op;
        case (f3)
          3'b000: op = (f7 == 7'b0100000) ? GEN_FC_ISA_ALU_REG_CP_OP_SUB : GEN_FC_ISA_ALU_REG_CP_OP_ADD;
          3'b010: op = GEN_FC_ISA_ALU_REG_CP_OP_SLT;  3'b011: op = GEN_FC_ISA_ALU_REG_CP_OP_SLTU;
          3'b100: op = GEN_FC_ISA_ALU_REG_CP_OP_XOR;  3'b110: op = GEN_FC_ISA_ALU_REG_CP_OP_OR;
          default: op = GEN_FC_ISA_ALU_REG_CP_OP_AND;
        endcase
        n_alu++;
        alu_cg.sample(op, alu_rs_cls(t.rs1_rdata), alu_rs_cls(t.rs2_rdata), sign_pair(t.rs1_rdata, t.rs2_rdata), t.rs1_rdata == t.rs2_rdata,
                      alu_same(t.rs1_addr, t.rs2_addr, t.rd_addr), t.rd_addr == 0, (t.rd_addr == 0) ? -1 : alu_res_cls(t.rd_wdata), alu_wrap(op, t.rs1_rdata, t.rs2_rdata));
      end
    endfunction
    // ---- FCOV_QUERY: the sampler's counters by index (the unit test compares them with the program's known counts)
    function int unsigned query(int k);
      case (k)
        0: return n_slt_eq; 1: return n_zcmp; 2: return n_zcmp_minstret_no; 3: return n_cnt; 4: return n_cnt_res_na; 5: return n_imm;
        6: return n_zcmp_uop_no; 7: return n_zcmp_order_no; 8: return n_zcmp_tags_no; 9: return n_br; 10: return n_mv; 11: return n_csr_pairs; 12: return n_mv_miss; 13: return n_rec; 14: return n_mt; 15: return n_rst; 16: return n_sec; 17: return n_hz; 18: return n_lu; 19: return n_hx; 20: return n_jp; 21: return n_dt; 22: return n_ie;
        default: return 32'hffff_ffff;
      endcase
    endfunction
    // ---- FCOV_SELFTEST: the classifier vector table; each row names the case, the classifier's answer and the plan's bin.
    // Synthetic records go through write() itself, so the run's coverage database carries these samples: a self-test run is never a proof run.
    function gen_rvfi_txn ut_rec(logic [31:0] insn, logic [4:0] rd, logic [31:0] rd_wdata, logic [4:0] rs1, logic [31:0] rs1_rdata, logic [31:0] pc, int unsigned cyc, logic [31:0] c10,
                                 bit exp_valid = 0, bit exp_last = 0, logic [15:0] exp_insn = 0);
      gen_rvfi_txn t = gen_rvfi_txn::type_id::create("ut_rec");
      t.insn = insn; t.rd_addr = rd; t.rd_wdata = rd_wdata; t.rs1_addr = rs1; t.rs1_rdata = rs1_rdata; t.rs2_addr = 0; t.rs2_rdata = 0;
      t.pc_rdata = pc; t.pc_wdata = (exp_valid && !exp_last) ? pc : pc + (insn[1:0] == 2'b11 ? 32'd4 : 32'd2); t.trap = 0; t.intr = 0; t.mode = 3;
      t.mem_addr = 0; t.mem_rmask = 0; t.mem_wmask = 0; t.cycle = cyc; t.ext_exp_valid = exp_valid; t.ext_exp_last = exp_last; t.ext_exp_insn = exp_insn;
      foreach (t.ext_mhpmcounters[i]) begin t.ext_mhpmcounters[i] = 0; t.ext_mhpmcountersh[i] = 0; end
      t.ext_mhpmcounters[7] = c10;
      return t;
    endfunction
    function int unsigned self_test();
      int unsigned fails = 0, n = 0, imm0, miss0;
      `define GEN_FCOV_UT(name, got, exp) begin n++; if ((got) !== (exp)) begin fails++; `uvm_error("GEN_FCOV_UT", $sformatf("%s: got %0d expected %0d", name, got, exp)) end else `uvm_info("GEN_FCOV_UT", $sformatf("%s OK (%0d)", name, got), UVM_LOW) end
      // slt_case: eq needs the whole 32-bit compare, the boundary cases come first
      `GEN_FCOV_UT("slti rs1 == imm is eq", slt_case(GEN_FC_ISA_ALU_IMM_CP_OP_SLTI, 32'd5, 5), GEN_FC_ISA_ALU_IMM_CP_SLT_CASE_EQ)
      `GEN_FCOV_UT("slti rs1[0] == imm[0] alone is not eq", slt_case(GEN_FC_ISA_ALU_IMM_CP_OP_SLTI, 32'h11, 1), GEN_FC_ISA_ALU_IMM_CP_SLT_CASE_OTHER)
      `GEN_FCOV_UT("slti INT_MIN, 0 is slti_intmin_0", slt_case(GEN_FC_ISA_ALU_IMM_CP_OP_SLTI, 32'h8000_0000, 0), GEN_FC_ISA_ALU_IMM_CP_SLT_CASE_SLTI_INTMIN_0)
      `GEN_FCOV_UT("slt_case on addi is na", slt_case(GEN_FC_ISA_ALU_IMM_CP_OP_ADDI, 32'd5, 5), -1)
      // addi_wrap from the operands: rd = x0 does not matter
      `GEN_FCOV_UT("addi INT_MAX + 1 wraps positive", addi_wrap(GEN_FC_ISA_ALU_IMM_CP_OP_ADDI, 32'h7fff_ffff, 1), GEN_FC_ISA_ALU_IMM_CP_ADDI_WRAP_POS_WRAP)
      `GEN_FCOV_UT("addi INT_MIN - 1 wraps negative", addi_wrap(GEN_FC_ISA_ALU_IMM_CP_OP_ADDI, 32'h8000_0000, -1), GEN_FC_ISA_ALU_IMM_CP_ADDI_WRAP_NEG_WRAP)
      `GEN_FCOV_UT("addi 5 + 1 does not wrap", addi_wrap(GEN_FC_ISA_ALU_IMM_CP_OP_ADDI, 32'd5, 1), GEN_FC_ISA_ALU_IMM_CP_ADDI_WRAP_NONE)
      // the divisor's magnitude: |-3| > 2, |-3| < |-5|
      `GEN_FCOV_UT("divisor -3 against dividend 2 is abs_gt_dividend", div_divisor_cls(32'hffff_fffd, 32'd2), GEN_FC_DIV_OPS_CP_DIVISOR_ABS_GT_DIVIDEND)
      `GEN_FCOV_UT("divisor -3 against dividend -5 is neg_rand", div_divisor_cls(32'hffff_fffd, 32'hffff_fffb), GEN_FC_DIV_OPS_CP_DIVISOR_NEG_RAND)
      `GEN_FCOV_UT("divisor 3 against dividend -5 is pos_rand", div_divisor_cls(32'd3, 32'hffff_fffb), GEN_FC_DIV_OPS_CP_DIVISOR_POS_RAND)
      // the result class on an rd = x0 record is na (the RTL forces rvfi_rd_wdata to 0): a clz x0 record through write()
      write(ut_rec(32'h6001_1013, 5'd0, 32'h0, 5'd2, 32'h0000_00f0, 32'h9000_0000, 1000, 32'd7));   // clz x0, sp
      `GEN_FCOV_UT("clz rd = x0: result class na", ut_last_cnt[3], -1)
      `GEN_FCOV_UT("clz rd = x0: rd_x0 yes", ut_last_cnt[4], 1)
      write(ut_rec(32'h6001_1093, 5'd1, 32'd24, 5'd2, 32'h0000_00f0, 32'h9000_0004, 1002, 32'd7));   // clz ra, sp = 24
      `GEN_FCOV_UT("clz rd = ra: result class from rd_wdata", ut_last_cnt[3], cnt_result_cls(32'd24))
      // minstret_once: a cm.push {ra} sequence followed by a record whose counter moved by one, then one that did not
      imm0 = n_imm;
      write(ut_rec(32'hfe11_2e23, 5'd0, 32'h0, 5'd2, 32'h8000_0230, 32'h9000_0010, 1010, 32'd100, 1, 0, 16'hb84a));   // sw ra, -4(sp): the first micro-op
      write(ut_rec(32'hfd01_0113, 5'd2, 32'h8000_0200, 5'd2, 32'h8000_0230, 32'h9000_0010, 1012, 32'd100, 1, 1, 16'hb84a));   // addi sp, sp, -48: the last
      `GEN_FCOV_UT("the synthesized addi sp micro-op does not feed the immediate group", n_imm, imm0)
      write(ut_rec(32'h0000_0013, 5'd0, 32'h0, 5'd0, 32'h0, 32'h9000_0012, 1014, 32'd101));   // the record after: counter moved by one
      `GEN_FCOV_UT("cm.push followed by a counter move of one: minstret_once yes", ut_last_zcmp[9], GEN_FC_CMP_ZCMP_PUSHPOP_CP_MINSTRET_ONCE_YES)
      write(ut_rec(32'hfe11_2e23, 5'd0, 32'h0, 5'd2, 32'h8000_0230, 32'h9000_0020, 1020, 32'd101, 1, 0, 16'hb84a));
      write(ut_rec(32'hfd01_0113, 5'd2, 32'h8000_0200, 5'd2, 32'h8000_0230, 32'h9000_0020, 1022, 32'd101, 1, 1, 16'hb84a));
      write(ut_rec(32'h0000_0013, 5'd0, 32'h0, 5'd0, 32'h0, 32'h9000_0022, 1024, 32'd101));   // the record after: counter unchanged
      `GEN_FCOV_UT("cm.push followed by an unchanged counter: minstret_once na", ut_last_zcmp[9], -1)
      // the Zcmp sreg field: cm.mva01s s7, s6 expands to addi a0, x23, 0 then addi a1, x22, 0
      write(ut_rec(32'h000b_8513, 5'd10, 32'h77, 5'd23, 32'h77, 32'h9000_0030, 1030, 32'd101, 1, 0, 16'haffa));
      write(ut_rec(32'h000b_0593, 5'd11, 32'h66, 5'd22, 32'h66, 32'h9000_0030, 1032, 32'd101, 1, 1, 16'haffa));
      write(ut_rec(32'h0000_0013, 5'd0, 32'h0, 5'd0, 32'h0, 32'h9000_0032, 1034, 32'd101));
      `GEN_FCOV_UT("cm.mva01s s7, s6: form", ut_last_mv[0], GEN_FC_CMP_ZCMP_MV_CP_INSN_CM_MVA01S)
      `GEN_FCOV_UT("cm.mva01s s7, s6: r1s' field", ut_last_mv[1], 7)
      `GEN_FCOV_UT("cm.mva01s s7, s6: the pair over x23 / x22 is well-formed", ut_last_mv[7], GEN_FC_CMP_ZCMP_MV_CP_UOP_COUNT_OK_YES)
      // the divisor pairs that separate the sign-extended |x| from the zero-extended one: |0x9ABCDEF0| < |INT_MAX|, |0x12345678| > |-2|
      `GEN_FCOV_UT("divisor 0x9ABCDEF0 against dividend INT_MAX is neg_rand", div_divisor_cls(32'h9abc_def0, 32'h7fff_ffff), GEN_FC_DIV_OPS_CP_DIVISOR_NEG_RAND)
      `GEN_FCOV_UT("divisor 0x12345678 against dividend -2 is abs_gt_dividend", div_divisor_cls(32'h1234_5678, 32'hffff_fffe), GEN_FC_DIV_OPS_CP_DIVISOR_ABS_GT_DIVIDEND)
      // cm.mvsa01 s2, s3 (r1s' 2, r2s' 3 -> x18, x19: the s2..s5 branch of zcmp_sreg) expands to addi x18, a0, 0 then addi x19, a1, 0
      write(ut_rec(32'h0005_0913, 5'd18, 32'h55, 5'd10, 32'h55, 32'h9000_0040, 1040, 32'd101, 1, 0, 16'had2e));
      write(ut_rec(32'h0005_8993, 5'd19, 32'h44, 5'd11, 32'h44, 32'h9000_0040, 1042, 32'd101, 1, 1, 16'had2e));
      write(ut_rec(32'h0000_0013, 5'd0, 32'h0, 5'd0, 32'h0, 32'h9000_0042, 1044, 32'd101));
      `GEN_FCOV_UT("cm.mvsa01 s2, s3: form", ut_last_mv[0], GEN_FC_CMP_ZCMP_MV_CP_INSN_CM_MVSA01)
      `GEN_FCOV_UT("cm.mvsa01 s2, s3: r1s' field", ut_last_mv[1], 2)
      `GEN_FCOV_UT("cm.mvsa01 s2, s3: r2s' field", ut_last_mv[2], 3)
      `GEN_FCOV_UT("cm.mvsa01 s2, s3: the pair over x18 / x19 is well-formed", ut_last_mv[7], GEN_FC_CMP_ZCMP_MV_CP_UOP_COUNT_OK_YES)
      // a legal pair whose second micro-op names the wrong source (addi a1, x21, 0 under cm.mva01s s7, s6) is a counted miss
      miss0 = n_mv_miss;
      write(ut_rec(32'h000b_8513, 5'd10, 32'h77, 5'd23, 32'h77, 32'h9000_0050, 1050, 32'd101, 1, 0, 16'haffa));
      write(ut_rec(32'h000a_8593, 5'd11, 32'h66, 5'd21, 32'h66, 32'h9000_0050, 1052, 32'd101, 1, 1, 16'haffa));
      write(ut_rec(32'h0000_0013, 5'd0, 32'h0, 5'd0, 32'h0, 32'h9000_0052, 1054, 32'd101));
      `GEN_FCOV_UT("cm.mva01s with a wrong second micro-op: uop_count_ok na", ut_last_mv[7], -1)
      `GEN_FCOV_UT("cm.mva01s with a wrong second micro-op: one counted miss", n_mv_miss, miss0 + 1)
      ut_mv_miss_expected += n_mv_miss - miss0;   // only the self-test's own miss is excluded from the referee
      // Slice A classifiers: the record group's partitions
      `GEN_FCOV_UT("pc delta +2 is plus2", rec_pc_delta_cls(32'h8000_0100, 32'h8000_0102, 0), GEN_FC_RVFI_RECORD_CP_PC_DELTA_PLUS2)
      `GEN_FCOV_UT("pc delta +4 is plus4", rec_pc_delta_cls(32'h8000_0100, 32'h8000_0104, 0), GEN_FC_RVFI_RECORD_CP_PC_DELTA_PLUS4)
      `GEN_FCOV_UT("pc delta +40 on a non-redirect record is jump_fwd", rec_pc_delta_cls(32'h8000_0100, 32'h8000_0128, 0), GEN_FC_RVFI_RECORD_CP_PC_DELTA_JUMP_FWD)
      `GEN_FCOV_UT("pc delta -8 on a non-redirect record is jump_back", rec_pc_delta_cls(32'h8000_0100, 32'h8000_00f8, 0), GEN_FC_RVFI_RECORD_CP_PC_DELTA_JUMP_BACK)
      `GEN_FCOV_UT("an mret record is redirect_other whatever its delta", rec_pc_delta_cls(32'h8000_0100, 32'h8000_0104, is_redirect_insn(32'h3020_0073)), GEN_FC_RVFI_RECORD_CP_PC_DELTA_REDIRECT_OTHER)
      `GEN_FCOV_UT("fence.i is a redirect", is_redirect_insn(32'h0000_100f), 1)
      `GEN_FCOV_UT("continuity: pc_rdata == previous pc_wdata", rec_cont_cls(32'h8000_0104, 32'h8000_0104, 0, 0, 0, 0), GEN_FC_RVFI_RECORD_CP_PC_CONTINUITY_CONTINUOUS)
      `GEN_FCOV_UT("continuity: an intr record", rec_cont_cls(32'h8000_0104, 32'h8000_0080, 1, 0, 0, 0), GEN_FC_RVFI_RECORD_CP_PC_CONTINUITY_DISCONTINUOUS_INTR)
      `GEN_FCOV_UT("continuity: after a trap record", rec_cont_cls(32'h8000_0104, 32'h8000_0080, 0, 1, 0, 0), GEN_FC_RVFI_RECORD_CP_PC_CONTINUITY_DISCONTINUOUS_AFTER_TRAP)
      `GEN_FCOV_UT("continuity: after an mret / dret / fence.i", rec_cont_cls(32'h8000_0104, 32'h8000_0200, 0, 0, 1, 0), GEN_FC_RVFI_RECORD_CP_PC_CONTINUITY_DISCONTINUOUS_AFTER_FLUSH_REDIRECT)
      `GEN_FCOV_UT("continuity: debug mode changed", rec_cont_cls(32'h8000_0104, 32'h1a11_0800, 0, 0, 0, 1), GEN_FC_RVFI_RECORD_CP_PC_CONTINUITY_DISCONTINUOUS_DEBUG)
      `GEN_FCOV_UT("continuity: any other discontinuity is na (the protocol checker's error)", rec_cont_cls(32'h8000_0104, 32'h8000_0200, 0, 0, 0, 0), -1)
      `GEN_FCOV_UT("intr kind: none", rec_intr_kind_cls(0, 32'h800, 0, 0), GEN_FC_RVFI_RECORD_CP_INTR_KIND_NONE)
      `GEN_FCOV_UT("intr kind: irq (a pending bit, no NMI flag)", rec_intr_kind_cls(1, 32'h800, 0, 0), GEN_FC_RVFI_RECORD_CP_INTR_KIND_IRQ)
      `GEN_FCOV_UT("intr kind: nmi", rec_intr_kind_cls(1, 32'h800, 1, 0), GEN_FC_RVFI_RECORD_CP_INTR_KIND_NMI)
      `GEN_FCOV_UT("intr kind: nmi_int", rec_intr_kind_cls(1, 0, 0, 1), GEN_FC_RVFI_RECORD_CP_INTR_KIND_NMI_INT)
      `GEN_FCOV_UT("rd source: x0 is none", rec_rd_source_cls(5'd0, 32'h0000_2083), GEN_FC_RVFI_RECORD_CP_RD_SOURCE_NONE)
      `GEN_FCOV_UT("rd source: lw is load_lsu", rec_rd_source_cls(5'd1, 32'h0000_2083), GEN_FC_RVFI_RECORD_CP_RD_SOURCE_LOAD_LSU)
      `GEN_FCOV_UT("rd source: addi is alu_wb", rec_rd_source_cls(5'd1, 32'h0010_0093), GEN_FC_RVFI_RECORD_CP_RD_SOURCE_ALU_WB)
      `GEN_FCOV_UT("valid gap 1 / 2 / 5", rec_gap_cls(1) * 100 + rec_gap_cls(2) * 10 + rec_gap_cls(5), GEN_FC_RVFI_RECORD_CP_VALID_GAP_G1 * 100 + GEN_FC_RVFI_RECORD_CP_VALID_GAP_G2 * 10 + GEN_FC_RVFI_RECORD_CP_VALID_GAP_G3_PLUS)
      // the multiply's neighbour classes
      `GEN_FCOV_UT("prev class: addi is alu", mt_prev_cls(32'h0010_0093), GEN_FC_MUL_TIMING_CP_PREV_ALU)
      `GEN_FCOV_UT("prev class: mul is mul", mt_prev_cls(32'h0220_80b3), GEN_FC_MUL_TIMING_CP_PREV_MUL)
      `GEN_FCOV_UT("prev class: mulhu is mulh_class", mt_prev_cls(32'h0220_b0b3), GEN_FC_MUL_TIMING_CP_PREV_MULH_CLASS)
      `GEN_FCOV_UT("prev class: divu is div", mt_prev_cls(32'h0220_d0b3), GEN_FC_MUL_TIMING_CP_PREV_DIV)
      `GEN_FCOV_UT("prev class: lw is load", mt_prev_cls(32'h0000_2083), GEN_FC_MUL_TIMING_CP_PREV_LOAD)
      `GEN_FCOV_UT("prev class: sw is store", mt_prev_cls(32'h0010_2023), GEN_FC_MUL_TIMING_CP_PREV_STORE)
      `GEN_FCOV_UT("prev class: beq is branch", mt_prev_cls(32'h0000_0063), GEN_FC_MUL_TIMING_CP_PREV_BRANCH)
      `GEN_FCOV_UT("prev class: c.j is branch", mt_prev_cls(32'h0000_a001), GEN_FC_MUL_TIMING_CP_PREV_BRANCH)
      `GEN_FCOV_UT("prev class: c.lw is load", mt_prev_cls(32'h0000_4108), GEN_FC_MUL_TIMING_CP_PREV_LOAD)
      `GEN_FCOV_UT("prev class: c.addi is alu", mt_prev_cls(32'h0000_0085), GEN_FC_MUL_TIMING_CP_PREV_ALU)
      `GEN_FCOV_UT("prev class: csrr is other", mt_prev_cls(32'h3000_2573), GEN_FC_MUL_TIMING_CP_PREV_OTHER)
      `GEN_FCOV_UT("mul delta 1 / 2 / 7", mt_delta_cls(1) * 100 + mt_delta_cls(2) * 10 + mt_delta_cls(7), GEN_FC_MUL_TIMING_CP_DELTA_D1 * 100 + GEN_FC_MUL_TIMING_CP_DELTA_D2 * 10 + GEN_FC_MUL_TIMING_CP_DELTA_D3PLUS)
      // the reset release classes
      `GEN_FCOV_UT("boot address 0x80000000 is high", rst_boot_cls(32'h8000_0000), GEN_FC_RST_BOOT_CP_BOOT_ADDR_HIGH)
      `GEN_FCOV_UT("boot address 0x00100000 is low (page 0x001000)", rst_boot_cls(32'h0010_0000), GEN_FC_RST_BOOT_CP_BOOT_ADDR_LOW)
      `GEN_FCOV_UT("boot address 0x10000000 is mid", rst_boot_cls(32'h1000_0000), GEN_FC_RST_BOOT_CP_BOOT_ADDR_MID)
      `GEN_FCOV_UT("boot address 0x00000000 is zero", rst_boot_cls(32'h0000_0000), GEN_FC_RST_BOOT_CP_BOOT_ADDR_ZERO)
      `GEN_FCOV_UT("hart id all-ones is max", rst_hart_cls(32'hffff_ffff), GEN_FC_RST_BOOT_CP_HART_ID_MAX)
      `GEN_FCOV_UT("pending: nothing", rst_pending_cls(18'd0, 0, 0), GEN_FC_RST_BOOT_CP_PENDING_NONE)
      `GEN_FCOV_UT("pending: a line with mie 0 is irq_enabled_later", rst_pending_cls(18'h4, 0, 0), GEN_FC_RST_BOOT_CP_PENDING_IRQ_ENABLED_LATER)
      `GEN_FCOV_UT("pending: nmi and debug", rst_pending_cls(18'd0, 1, 1), GEN_FC_RST_BOOT_CP_PENDING_NMI_AND_DEBUG)
      `GEN_FCOV_UT("pending: a line and debug", rst_pending_cls(18'h2, 0, 1), GEN_FC_RST_BOOT_CP_PENDING_IRQ_AND_DEBUG)
      `GEN_FCOV_UT("first event: a plain first record", rst_first_event_cls(0, 0, 0), GEN_FC_RST_BOOT_CP_FIRST_EVENT_FIRST_INSTR_RETIRE)
      `GEN_FCOV_UT("first event: an NMI entry", rst_first_event_cls(1, 1, 0), GEN_FC_RST_BOOT_CP_FIRST_EVENT_NMI_TAKEN)
      `GEN_FCOV_UT("first event: a maskable entry is the plan's ignore (na)", rst_first_event_cls(1, 0, 0), -1)
      `GEN_FCOV_UT("first event: debug entry", rst_first_event_cls(0, 0, 1), GEN_FC_RST_BOOT_CP_FIRST_EVENT_DEBUG_ENTRY)
      `GEN_FCOV_UT("boot-to-request 2 / 3 / 6 / 1", rst_req_cls(2) * 1000 + rst_req_cls(3) * 100 + rst_req_cls(6) * 10 + (rst_req_cls(1) + 1), GEN_FC_RST_BOOT_CP_BOOT_TO_REQ_CYCLES_TWO * 1000 + GEN_FC_RST_BOOT_CP_BOOT_TO_REQ_CYCLES_THREE * 100 + GEN_FC_RST_BOOT_CP_BOOT_TO_REQ_CYCLES_MORE * 10)
      `GEN_FCOV_UT("mubi: On / Off / other", mubi_cls_sec(ibex_pkg::IbexMuBiOn) * 100 + mubi_cls_sec(ibex_pkg::IbexMuBiOff) * 10 + mubi_cls_sec(ibex_pkg::ibex_mubi_t'(4'b0011)), GEN_FC_SEC_CTRL_INPUTS_CP_FETCH_EN_VAL_ON * 100 + GEN_FC_SEC_CTRL_INPUTS_CP_FETCH_EN_VAL_OFF * 10 + GEN_FC_SEC_CTRL_INPUTS_CP_FETCH_EN_VAL_INVALID)
      // CG-CMP-009 classifiers: the rlist register set, the fall-through halfword kind, the rlist class
      `GEN_FCOV_UT("rlist 4 saves ra only", zp_regs(4), 32'h0000_0002)
      `GEN_FCOV_UT("rlist 6 saves ra, s0, s1", zp_regs(6), 32'h0000_0302)
      `GEN_FCOV_UT("rlist 8 saves ra, s0..s3 (x18, x19)", zp_regs(8), 32'h000c_0302)
      `GEN_FCOV_UT("rlist 15 saves ra, s0..s11 (x18..x27)", zp_regs(15), 32'h0ffc_0302)
      `GEN_FCOV_UT("halfword cm.push {ra} is a cm_push", hz_cm_kind(16'hb842), GEN_FC_CMP_ZCMP_HAZARD_CP_FT_KIND_CM_PUSH)
      `GEN_FCOV_UT("halfword cm.popret {ra} is a cm_popret", hz_cm_kind(16'hbe42), GEN_FC_CMP_ZCMP_HAZARD_CP_FT_KIND_CM_POPRET)
      `GEN_FCOV_UT("halfword cm.mva01s s7, s6 is a cm_mva01s", hz_cm_kind(16'haffa), GEN_FC_CMP_ZCMP_HAZARD_CP_FT_KIND_CM_MVA01S)
      `GEN_FCOV_UT("halfword cm.mvsa01 s2, s3 is a cm_mvsa01", hz_cm_kind(16'had2e), GEN_FC_CMP_ZCMP_HAZARD_CP_FT_KIND_CM_MVSA01)
      `GEN_FCOV_UT("halfword c.addi is not a cm.*", hz_cm_kind(16'h0085), -1)
      `GEN_FCOV_UT("rlist classes 4 / 9 / 15", hz_rlist_cls(4) * 100 + hz_rlist_cls(9) * 10 + hz_rlist_cls(15), GEN_FC_CMP_ZCMP_HAZARD_CP_RLIST_CLASS_R4 * 100 + GEN_FC_CMP_ZCMP_HAZARD_CP_RLIST_CLASS_R5_14 * 10 + GEN_FC_CMP_ZCMP_HAZARD_CP_RLIST_CLASS_R15)
      // Slice B classifiers
      `GEN_FCOV_UT("jalr imm 2047 is max_pos, not odd", jalr_imm_cls(2047), GEN_FC_ISA_JUMP_CP_JALR_IMM_MAX_POS)
      `GEN_FCOV_UT("jalr imm 3 is odd", jalr_imm_cls(3), GEN_FC_ISA_JUMP_CP_JALR_IMM_ODD)
      `GEN_FCOV_UT("jalr imm -2046 is neg_rand", jalr_imm_cls(-2046), GEN_FC_ISA_JUMP_CP_JALR_IMM_NEG_RAND)
      `GEN_FCOV_UT("jal offset 0xFFFFE is max_fwd", jal_off_cls(32'h000F_FFFE), GEN_FC_ISA_JUMP_CP_JAL_OFF_MAX_FWD)
      `GEN_FCOV_UT("jal offset -0x100000 is max_bwd", jal_off_cls(-32'h0010_0000), GEN_FC_ISA_JUMP_CP_JAL_OFF_MAX_BWD)
      `GEN_FCOV_UT("a jump from 0xFFFFFFF0 by +0x20 wraps", sum_wraps(32'hFFFF_FFF0, 32'h20), 1'b1)
      `GEN_FCOV_UT("a jump from 0x80000000 by -4 does not wrap", sum_wraps(32'h8000_0000, -4), 1'b0)
      `GEN_FCOV_UT("a jump from 0x00000010 by -0x20 wraps", sum_wraps(32'h0000_0010, -32'h20), 1'b1)
      `GEN_FCOV_UT("auipc at 0x80000000 with the msb immediate does not wrap", sum_wraps(32'h8000_0000, signed'(32'h8000_0000)), 1'b0)
      `GEN_FCOV_UT("auipc at 0 with the all-ones immediate wraps", sum_wraps(32'h0, signed'(32'hFFFF_F000)), 1'b1)
      `GEN_FCOV_UT("lui imm20 0x80000 is msb", lu_imm_cls(20'h80000), GEN_FC_ISA_LUI_AUIPC_CP_IMM20_MSB)
      `GEN_FCOV_UT("pc 0xFFFFF000 is the high region", lu_region_cls(32'hFFFF_F000), GEN_FC_ISA_LUI_AUIPC_CP_PC_REGION_HIGH)
      `GEN_FCOV_UT("addi x0, x0, 0 is the canonical nop", hx_hint_cls(32'h0000_0013), GEN_FC_ISA_HINT_X0_CP_HINT_CLASS_CANONICAL_NOP)
      `GEN_FCOV_UT("addi x0, x1, 0 is addi_x0_nzimm", hx_hint_cls(32'h0000_8013), GEN_FC_ISA_HINT_X0_CP_HINT_CLASS_ADDI_X0_NZIMM)
      `GEN_FCOV_UT("slli x0, x0, 0x1f is the semihosting hint", hx_hint_cls(32'h01f0_1013), GEN_FC_ISA_HINT_X0_CP_HINT_CLASS_SLLI_X0_SEMIHOST)
      `GEN_FCOV_UT("srai x0, x0, 7 is the semihosting hint", hx_hint_cls(32'h4070_5013), GEN_FC_ISA_HINT_X0_CP_HINT_CLASS_SRAI_X0_SEMIHOST)
      `GEN_FCOV_UT("srai x0, x1, 7 is srai_x0_other", hx_hint_cls(32'h4070_d013), GEN_FC_ISA_HINT_X0_CP_HINT_CLASS_SRAI_X0_OTHER)
      `GEN_FCOV_UT("rori is a two-cycle bit op", hx_writer_cls(32'h6050_d013), GEN_FC_ISA_HINT_X0_CP_WRITER_CLASS_BIT_2CYC)
      `GEN_FCOV_UT("andn is a one-cycle bit op", hx_writer_cls(32'h4062_f033), GEN_FC_ISA_HINT_X0_CP_WRITER_CLASS_BIT_1CYC)
      `GEN_FCOV_UT("sub x0 is alu_reg", hx_writer_cls(32'h4062_8033), GEN_FC_ISA_HINT_X0_CP_WRITER_CLASS_ALU_REG)
      `GEN_FCOV_UT("csrr x0, mcycle is csrr", hx_writer_cls(32'hb000_2073), GEN_FC_ISA_HINT_X0_CP_WRITER_CLASS_CSRR)
      `GEN_FCOV_UT("c.li x0, 1 is a compressed hint writer", hx_writer_cls(32'h0000_4005), GEN_FC_ISA_HINT_X0_CP_WRITER_CLASS_CMP_HINT)
      `GEN_FCOV_UT("sw writes no rd", hx_writer_cls(32'h0062_a023), -1)
      `GEN_FCOV_UT("c.li names x0 as rs1", hx_rs_field(32'h0000_4285, 0), 0)
      `GEN_FCOV_UT("c.mv names x0 as rs1", hx_rs_field(32'h0000_8286, 0), 0)
      `GEN_FCOV_UT("c.beqz compares against x0 (rs2)", hx_rs_field(32'h0000_c001, 1), 0)
      `GEN_FCOV_UT("jal has no rs1", hx_rs_field(32'h0000_00ef, 0), -1)
      `GEN_FCOV_UT("c.lui a0, 1 names no rs1", hx_rs_field(32'h0000_6505, 0), -1)
      `GEN_FCOV_UT("c.addi16sp names sp", hx_rs_field(32'h0000_7139, 0), 2)
      `GEN_FCOV_UT("add t0, x0, t1 names x0 as rs1", hx_rs_field(32'h0060_02b3, 0), 0)
      `GEN_FCOV_UT("add t0, t1, x0 names x0 as rs2", hx_rs_field(32'h0003_02b3, 1), 0)
      `GEN_FCOV_UT("lui has neither rs1 nor rs2", hx_rs_field(32'h0000_12b7, 0) * 10 + hx_rs_field(32'h0000_12b7, 1), -11)
      `GEN_FCOV_UT("divide deltas 2 / 37 / 5", dt_delta_cls(2) * 100 + dt_delta_cls(37) * 10 + dt_delta_cls(5), GEN_FC_DIV_TIMING_CP_DELTA_D2 * 100 + GEN_FC_DIV_TIMING_CP_DELTA_D37 * 10 + GEN_FC_DIV_TIMING_CP_DELTA_OTHER)
      `GEN_FCOV_UT("c.j offset 2046 is max_fwd", ie_off_cls(2046, 2046, -2048, 0, 1, 2, 3, 4), 1)
      `GEN_FCOV_UT("c.beqz offset -256 is max_bwd", ie_off_cls(-256, 254, -256, 0, 1, 2, 3, 4), 2)
      `GEN_FCOV_UT("c.j offset -2 is neg_rand", ie_off_cls(-2, 2046, -2048, 0, 1, 2, 3, 4), 4)
      `GEN_FCOV_UT("the CJ offset of c.j +2046", cj_off(16'haffd), 2046)
      `GEN_FCOV_UT("the CJ offset of c.j -2048", cj_off(16'hb001), -2048)
      // x0 writer then its successor through write(): add x0, x1, x2 then add t0, x0, t1 (rs1 zero) then lui (none)
      write(ut_rec(32'h0020_8033, 5'd0, 32'h0, 5'd1, 32'h5, 32'h9000_0100, 1100, 32'd200));   // add x0, x1, x2
      write(ut_rec(32'h0060_02b3, 5'd5, 32'h7, 5'd0, 32'h0, 32'h9000_0104, 1101, 32'd201));   // add t0, x0, t1
      `GEN_FCOV_UT("add x0: hint class add_x0", ut_last_hx[0], GEN_FC_ISA_HINT_X0_CP_HINT_CLASS_ADD_X0)
      `GEN_FCOV_UT("add x0: writer class alu_reg", ut_last_hx[1], GEN_FC_ISA_HINT_X0_CP_WRITER_CLASS_ALU_REG)
      `GEN_FCOV_UT("add x0 then add t0, x0, t1: rs1_zero", ut_last_hx[2], GEN_FC_ISA_HINT_X0_CP_X0_READ_RS1_ZERO)
      write(ut_rec(32'h0000_1037, 5'd0, 32'h0, 5'd0, 32'h0, 32'h9000_0108, 1102, 32'd202));   // lui x0, 1
      write(ut_rec(32'h0000_12b7, 5'd5, 32'h1000, 5'd0, 32'h0, 32'h9000_010c, 1103, 32'd203));   // lui t0, 1: reads nothing
      `GEN_FCOV_UT("lui x0 then lui t0: none", ut_last_hx[2], GEN_FC_ISA_HINT_X0_CP_X0_READ_NONE)
      `GEN_FCOV_UT("lui x0: writer class lui_auipc", ut_last_hx[1], GEN_FC_ISA_HINT_X0_CP_WRITER_CLASS_LUI_AUIPC)
      `GEN_FCOV_UT("lui t0, 1 at a word pc: op lui, imm one, rd nonzero", ut_last_lu[0] * 100 + ut_last_lu[1] * 10 + ut_last_lu[5], GEN_FC_ISA_LUI_AUIPC_CP_OP_LUI * 100 + GEN_FC_ISA_LUI_AUIPC_CP_IMM20_ONE * 10 + GEN_FC_ISA_LUI_AUIPC_CP_RD_X0_NO)
      // a jalr record: jalr ra, 8(ra) from ra = 0x90000200 (rs1 == rd), even target, link pc + 4
      write(ut_rec(32'h0080_80e7, 5'd1, 32'h9000_0114, 5'd1, 32'h9000_0200, 32'h9000_0110, 1104, 32'd204));
      `GEN_FCOV_UT("jalr ra, 8(ra): rs1 eq_rd, imm pos_rand, target even, link pc4", ut_last_jp[4] * 1000 + ut_last_jp[3] * 100 + ut_last_jp[6] * 10 + ut_last_jp[9],
                   GEN_FC_ISA_JUMP_CP_JALR_RS1_EQ_RD * 1000 + GEN_FC_ISA_JUMP_CP_JALR_IMM_POS_RAND * 100 + GEN_FC_ISA_JUMP_CP_TARGET_ODD_NO * 10 + GEN_FC_ISA_JUMP_CP_LINK_LEN_PC4)
      // a c.addi16sp record: sp = 0x10 minus 32 borrows across 0
      write(ut_rec(32'h0000_7139, 5'd2, 32'hffff_fff0, 5'd2, 32'h0000_0010, 32'h9000_0114, 1105, 32'd205));   // c.addi16sp sp, -32
      `GEN_FCOV_UT("c.addi16sp sp, -32 from 0x10: imm rand, sp wrap yes", ut_last_ie[6] * 10 + ut_last_ie[11], GEN_FC_CMP_IMM_EDGES_CP_ADDI16SP_IMM_RAND * 10 + GEN_FC_CMP_IMM_EDGES_CP_SP_WRAP_YES)
      write(ut_rec(32'h0000_1141, 5'd2, 32'hffff_fff0, 5'd2, 32'h0000_0000, 32'h9000_0116, 1106, 32'd206));   // c.addi sp, -16
      `GEN_FCOV_UT("c.addi sp, -16: ci op c_addi, imm6 rand", ut_last_ie[3] * 10 + ut_last_ie[4], GEN_FC_CMP_IMM_EDGES_CP_CI_OP_C_ADDI * 10 + GEN_FC_CMP_IMM_EDGES_CP_CI_IMM6_RAND)
      // CG-IC-006's two classifiers, which are what a wrongly HIT bin needs: a manifest fails only an UNHIT declared bin, so
      // the precedence order and both window terms are pinned here rather than by any expectation file
      `GEN_FCOV_UT("no_alert_case: the cache disabled outranks every other reason", ic_no_alert_case(1'b0, 1'b1, 1'b1, 0, 1'b1, 1'b1), GEN_FC_IC_ECC_CP_NO_ALERT_CASE_DISABLED_CACHE)
      `GEN_FCOV_UT("no_alert_case: the sweep outranks the injection cases", ic_no_alert_case(1'b1, 1'b0, 1'b1, 0, 1'b1, 1'b1), GEN_FC_IC_ECC_CP_NO_ALERT_CASE_DURING_INVALIDATION)
      `GEN_FCOV_UT("no_alert_case: a masked duplicate copy outranks the unused way", ic_no_alert_case(1'b1, 1'b1, 1'b1, 1, 1'b1, 1'b0), GEN_FC_IC_ECC_CP_NO_ALERT_CASE_MASKED_DUPLICATE_COPY)
      `GEN_FCOV_UT("no_alert_case: a verdict of another or invalid way is the unused way", ic_no_alert_case(1'b1, 1'b1, 1'b1, 0, 1'b0, 1'b0), GEN_FC_IC_ECC_CP_NO_ALERT_CASE_UNUSED_WAY_DATA)
      `GEN_FCOV_UT("no_alert_case: a hit-way injection that owed its pulse is no no-alert case", ic_no_alert_case(1'b1, 1'b1, 1'b1, 1, 1'b0, 1'b0), -1)
      `GEN_FCOV_UT("no_alert_case: the never-written read needs a qualified cycle and no injection", ic_no_alert_case(1'b1, 1'b1, 1'b0, -2, 1'b0, 1'b1), GEN_FC_IC_ECC_CP_NO_ALERT_CASE_UNINITIALISED_DATA_RAM)
      `GEN_FCOV_UT("no_alert_case: an injection in the cycle takes the bin from the never-written read", ic_no_alert_case(1'b1, 1'b1, 1'b1, 0, 1'b0, 1'b1), GEN_FC_IC_ECC_CP_NO_ALERT_CASE_UNUSED_WAY_DATA)
      `GEN_FCOV_UT("quiet: both levels low and a retirement seen is quiet", ic_major_nmi_quiet(1'b0, 1'b0, 1'b1), GEN_FC_IC_ECC_CP_MAJOR_NMI_QUIET_YES)
      `GEN_FCOV_UT("quiet: a major level anywhere in the window is not quiet", ic_major_nmi_quiet(1'b1, 1'b0, 1'b1), -1)
      `GEN_FCOV_UT("quiet: an internal-NMI retirement in the window is not quiet", ic_major_nmi_quiet(1'b0, 1'b1, 1'b1), -1)
      `GEN_FCOV_UT("quiet: a window with no retirement claims nothing", ic_major_nmi_quiet(1'b0, 1'b0, 1'b0), -1)
      // the routing itself, not a classifier: a never-written report must land in the bypass queue and leave the announcement
      // queue untouched, since q is what the pulse attribution, the deferral and the closure iterate. A wrongly ROUTED event
      // is invisible to any expectation file, so this is where that mutation is caught.
      begin
        int q0 = int'(gen_icram_events::q.size()), u0 = int'(gen_icram_events::uq.size());
        gen_icram_events::note_uninit_read(32'hdead, 0, 0);
        `GEN_FCOV_UT("a never-written report leaves the announcement queue untouched", int'(gen_icram_events::q.size()) - q0, 0)
        `GEN_FCOV_UT("a never-written report lands in the bypass queue", int'(gen_icram_events::uq.size()) - u0, 1)
      `GEN_FCOV_UT("window: the reference cycle itself is outside the window", gen_ic_in_window(100, 100, 2), 0)
      `GEN_FCOV_UT("window: the first cycle after the reference is inside", gen_ic_in_window(101, 100, 2), 1)
      `GEN_FCOV_UT("window: the LAST cycle of the window is inside", gen_ic_in_window(102, 100, 2), 1)
      `GEN_FCOV_UT("window: one cycle past the window is outside", gen_ic_in_window(103, 100, 2), 0)
        // the probe leaves the queue AND the statistic as it found them, so a run's reported count stays the number of real reads
        if (gen_icram_events::uq.size() > 0) void'(gen_icram_events::uq.pop_back());
        if (gen_icram_events::uninit_reads > 0) gen_icram_events::uninit_reads--;
      end
      `undef GEN_FCOV_UT
      `uvm_info("GEN_FCOV_UT", $sformatf("self-test: %0d cases, %0d failures", n, fails), UVM_LOW)
      return fails;
    endfunction
    function void report_phase(uvm_phase phase);
      zca_flush(null);   // the last 16-bit record has no successor: its next_len is not applicable
      mt_flush(null);    // a multiply at the very end has no successor: cp_next_dep na
      hz_flush(null);    // a popret at the very end has no target record
      if (!rst_sampled && rst_release_seen && rst_fetch_en != GEN_FC_RST_BOOT_CP_FETCH_EN_AT_RELEASE_ON) rst_sample(GEN_FC_RST_BOOT_CP_FIRST_EVENT_NONE_FETCH_DISABLED);   // no record: fetch stayed disabled
      mv_flush(null);    // a move pair at the very end has no neighbour after
      pmp_final(); pmp_snap_close();  // the last write is read and the standing snapshot closes at the end
      zcmp_flush(null);  // a sequence at the very end has no record after it: minstret_once not applicable
      `uvm_info("GEN_FCOV", $sformatf("move pairs: %0d sampled, %0d with mismatching micro-ops (%0d of them the self-test's)", n_mv, n_mv_miss, ut_mv_miss_expected), UVM_LOW)
      `uvm_info("GEN_FCOV", $sformatf("slice A samples: records=%0d mul_timing=%0d rst_boot=%0d (boot_to_req %0d) sec_ctrl_inputs=%0d zcmp_hazard=%0d", n_rec, n_mt, n_rst, boot_to_req, n_sec, n_hz), UVM_LOW)
      `uvm_info("GEN_FCOV", $sformatf("irq samples: entry=%0d entry_rel=%0d edge=%0d access=%0d mie_global=%0d debug_window=%0d (post-exit undecided %0d, dropped unclosed %0d) reset=%0d fetch_off=%0d (windows published %0d, dropped as shorter than the minimum %0d) view misses %0d (mret masking a pending enabled line, the clear edge with no bin: %0d; mrets that are a handler's first instruction: %0d, of which wrongly booked stays-set: %0d)", n_irq_entry, n_irq_entry_rel, n_irq_edge, n_irq_access, n_irq_mie, n_irq_dbg, n_irq_dbg_undecided, n_irq_dbg_dropped, n_irq_rst, n_irq_off, gen_fetch_en_windows::published, gen_fetch_en_windows::skipped_short, n_irq_view_miss, n_irq_mret_masked, n_irq_mret_entry, n_irq_mret_newbin_entry), UVM_LOW)
      `uvm_info("GEN_FCOV", $sformatf("pmp samples: cfg_write=%0d addr_write=%0d csr_access=%0d table_state=%0d (dropped without a retire %0d, readback disagreed with the pre-state rule %0d)", n_pmp_cfg, n_pmp_addr, n_pmp_acc, n_pmp_tbl, n_pmp_tbl_dropped, n_pmp_addr_readback_odd), UVM_LOW)
      if (mul_cg != null) begin   // referee: a group the sampler fed must show coverage, a dropped sample is a collected failure
        if (n_mv_miss > ut_mv_miss_expected) `uvm_error("GEN_FCOV_REF", $sformatf("gen_cmp_zcmp_mv_cg: %0d legal move pairs whose micro-ops did not match the expansion", n_mv_miss - ut_mv_miss_expected))
        if (n_irq_entry > 0 && irq_entry_cg.get_coverage() == 0.0) `uvm_error("GEN_FCOV_REF", "gen_irq_entry_cg sampled without coverage")
        if ((n_irq_edge + n_irq_access + n_irq_mie) > 0 && irq_pend_cg.get_coverage() == 0.0) `uvm_error("GEN_FCOV_REF", "gen_irq_pending_model_cg sampled without coverage")
        if (n_irq_dbg > 0 && irq_dbg_cg.get_coverage() == 0.0) `uvm_error("GEN_FCOV_REF", "gen_irq_debug_interplay_cg sampled without coverage")
        if ((n_irq_rst + n_irq_off) > 0 && irq_rst_cg.get_coverage() == 0.0) `uvm_error("GEN_FCOV_REF", "gen_irq_reset_fetch_en_cg sampled without coverage")
        // the two-route invariant, as an ERROR rather than a print: a booking into the stays-set bin that
        // follows an entry cannot be right, and a counter that only prints cannot fail a run
        if (n_irq_mret_newbin_entry > 0) `uvm_error("GEN_FCOV_REF", $sformatf("%0d mret sample(s) booked into mret_mie1_mpie1_pending after an entry (this record an interrupt entry, or the previous record trapped): the pre-state cannot have been set", n_irq_mret_newbin_entry))
        if (n_pmp_acc > 0 && pmp_acc_cg.get_coverage() == 0.0) `uvm_error("GEN_FCOV_REF", "gen_pmp_csr_access_cg sampled without coverage")
        if (n_pmp_tbl > 0 && pmp_tbl_cg.get_coverage() == 0.0) `uvm_error("GEN_FCOV_REF", "gen_pmp_table_state_cg sampled without coverage")
        if (n_pmp_cfg > 0 && pmp_cfg_cg.get_coverage() == 0.0) `uvm_error("GEN_FCOV_REF", "gen_pmp_cfg_write_cg sampled without coverage")
        if (n_pmp_addr > 0 && pmp_addr_cg.get_coverage() == 0.0) `uvm_error("GEN_FCOV_REF", "gen_pmp_addr_write_cg sampled without coverage")
        if (n_mul > 0 && mul_cg.get_coverage() == 0.0) `uvm_error("GEN_FCOV_REF", "gen_mul_ops_cg sampled without coverage")
        if (n_div > 0 && div_cg.get_coverage() == 0.0) `uvm_error("GEN_FCOV_REF", "gen_div_ops_cg sampled without coverage")
        if (n_alu > 0 && alu_cg.get_coverage() == 0.0) `uvm_error("GEN_FCOV_REF", "gen_isa_alu_reg_cg sampled without coverage")
        if (n_bit > 0 && bit_cg.get_coverage() == 0.0) `uvm_error("GEN_FCOV_REF", "gen_bit_zba_zbb_ops_cg sampled without coverage")
        if (n_imm > 0 && imm_cg.get_coverage() == 0.0) `uvm_error("GEN_FCOV_REF", "gen_isa_alu_imm_cg sampled without coverage")
        if (n_sh > 0 && sh_cg.get_coverage() == 0.0) `uvm_error("GEN_FCOV_REF", "gen_isa_shift_cg sampled without coverage")
        if (n_cnt > 0 && cnt_cg.get_coverage() == 0.0) `uvm_error("GEN_FCOV_REF", "gen_bit_count_cg sampled without coverage")
        if (n_zca + n_zca32 > 0 && zca_cg.get_coverage() == 0.0) `uvm_error("GEN_FCOV_REF", "gen_cmp_zca_cg sampled without coverage")
        if (n_mv > 0 && mv_cg.get_coverage() == 0.0) `uvm_error("GEN_FCOV_REF", "gen_cmp_zcmp_mv_cg sampled without coverage")
        if (n_rec > 0 && rec_cg.get_coverage() == 0.0) `uvm_error("GEN_FCOV_REF", "gen_rvfi_record_cg sampled without coverage")
        if (n_mt > 0 && mt_cg.get_coverage() == 0.0) `uvm_error("GEN_FCOV_REF", "gen_mul_timing_cg sampled without coverage")
        if (n_rst > 0 && rst_cg.get_coverage() == 0.0) `uvm_error("GEN_FCOV_REF", "gen_rst_boot_cg sampled without coverage")
        if (n_ic_ecc > 0 && ic_ecc_cg.get_coverage() == 0.0) `uvm_error("GEN_FCOV_REF", "gen_ic_ecc_cg sampled without coverage")
        if (n_sec > 0 && sec_cg.get_coverage() == 0.0) `uvm_error("GEN_FCOV_REF", "gen_sec_ctrl_inputs_cg sampled without coverage")
        if (n_hz > 0 && hz_cg.get_coverage() == 0.0) `uvm_error("GEN_FCOV_REF", "gen_cmp_zcmp_hazard_cg sampled without coverage")
        if (n_br > 0 && br_cg.get_coverage() == 0.0) `uvm_error("GEN_FCOV_REF", "gen_isa_branch_cg sampled without coverage")
        if (n_zcmp > 0 && zcmp_cg.get_coverage() == 0.0) `uvm_error("GEN_FCOV_REF", "gen_cmp_zcmp_pushpop_cg sampled without coverage")
        if (n_csr_pairs > 0 && csr_cg.get_coverage() == 0.0) `uvm_error("GEN_FCOV_REF", "gen_csr_trap_setup_warl_cg sampled without coverage")
        if (n_sbit > 0 && sbit_cg.get_coverage() == 0.0) `uvm_error("GEN_FCOV_REF", "gen_bit_sbit_cg sampled without coverage")
        if (n_zcb > 0 && zcb_cg.get_coverage() == 0.0) `uvm_error("GEN_FCOV_REF", "gen_cmp_zcb_cg sampled without coverage")
      end
      `uvm_info("GEN_FCOV", $sformatf("isa samples: mul=%0d div=%0d alu_reg=%0d zba_zbb=%0d alu_imm=%0d shift=%0d bit_count=%0d zca=%0d zca32=%0d zcmp=%0d (abandoned %0d; uop_count no %0d, order no %0d, tags no %0d, minstret_once no %0d) zcmp_mv=%0d branch=%0d csr_pairs=%0d (writes %0d, replaced %0d) sbit=%0d zcb=%0d%s", n_mul, n_div, n_alu, n_bit, n_imm, n_sh, n_cnt, n_zca, n_zca32, n_zcmp, n_zcmp_abandoned, n_zcmp_uop_no, n_zcmp_order_no, n_zcmp_tags_no, n_zcmp_minstret_no, n_mv, n_br, n_csr_pairs, n_csr_wr, n_csr_replaced, n_sbit, n_zcb, mul_cg == null ? " (covergroups off)" : ""), UVM_LOW)
    endfunction
  endclass
endpackage
