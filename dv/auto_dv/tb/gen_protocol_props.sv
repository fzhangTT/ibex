// gen_protocol_props.sv: the DUT-boundary protocol SVA layer bound into gen_dut_top by dv/auto_dv/tb/gen_binds.sv (C10).
// Source: rtl-arch's property table (the anchors in dv/auto_dv/evidence/gen_cg_sampling_anchors.md and the protocol rows it
// cites), kept id-for-id except: the four properties that read DUT internals (sva_irq_pending_comb,
// sva_dbg_entry_bound, sva_dbg_entry_seen, sva_dbg_req_withdrawn) are not bound (probe register; the irq and debug checkers
// hold those rules at the boundary), the integrity rows take the bus interfaces' intg_corrupt flags instead of a static
// parameter, every property reports through uvm_report_error under its own id, and the knobs are per group
// (+gen_chk_sva_<group>, +gen_chk_all precedence) rather than per property; the two split-address rows are covers (below). Nothing here
// drives or forces a DUT net.
module gen_protocol_props
  import ibex_pkg::*;
  import prim_secded_pkg::*;
  import uvm_pkg::*;
#(
  parameter int unsigned IBUS_MAX_OUTSTANDING   = 8,    // NUM_FB (rtl/ibex_icache.sv:72) x IC_LINE_BEATS (rtl/ibex_pkg.sv:406)
  parameter int unsigned DBUS_MAX_OUTSTANDING   = 2,    // the two halves of one split access (rtl/ibex_load_store_unit.sv:403-405)
  parameter int unsigned ICACHE_ECC_WINDOW      = 2,    // GEN_ICACHE_ECC_WINDOW (cycles from RAM read to alert_minor_o; the bind passes the yaml value)
  parameter int unsigned TagSizeECC             = 28,   // gen_dut_top's TagSizeECC / LineSizeECC (passed by the bind)
  parameter int unsigned LineSizeECC            = 78
) (
  // TB-side flags (gen_bus_if intg_corrupt, connected by the bind through absolute TB paths): the response carries an
  // intended integrity corruption, so the *_rdata_intg rows do not fire on it
  input  logic                 ibus_intg_corrupt_i,
  input  logic                 dbus_intg_corrupt_i,
  input  logic                 clk_i,
  input  logic                 rst_ni,
  input  logic [31:0]          hart_id_i,
  input  logic [31:0]          boot_addr_i,
  // instruction bus
  input  logic                 instr_req_o,
  input  logic                 instr_gnt_i,
  input  logic                 instr_rvalid_i,
  input  logic [31:0]          instr_addr_o,
  input  logic [38:0]          instr_rdata_i,
  input  logic                 instr_err_i,
  // data bus
  input  logic                 data_req_o,
  input  logic                 data_gnt_i,
  input  logic                 data_rvalid_i,
  input  logic                 data_we_o,
  input  logic [3:0]           data_be_o,
  input  logic [31:0]          data_addr_o,
  input  logic [38:0]          data_wdata_o,
  input  logic [38:0]          data_rdata_i,
  input  logic                 data_tag_o,
  input  logic                 data_err_i,
  // icache RAM ports
  input  logic [1:0]           ic_tag_req_o,
  input  logic                 ic_tag_write_o,
  input  logic [7:0]           ic_tag_addr_o,
  input  logic [TagSizeECC-1:0] ic_tag_wdata_o,
  input  logic [TagSizeECC-1:0] ic_tag_rdata_i [2],
  input  logic [1:0]           ic_data_req_o,
  input  logic                 ic_data_write_o,
  input  logic [7:0]           ic_data_addr_o,
  input  logic [LineSizeECC-1:0] ic_data_wdata_o,
  input  logic [LineSizeECC-1:0] ic_data_rdata_i [2],
  input  logic                 ic_scr_key_valid_i,
  input  logic                 ic_scr_key_req_o,
  // interrupts and debug
  input  logic                 irq_software_i,
  input  logic                 irq_timer_i,
  input  logic                 irq_external_i,
  input  logic [14:0]          irq_fast_i,
  input  logic                 irq_nm_i,
  input  logic                 irq_pending_o,
  input  logic                 debug_req_i,
  // alerts and control
  input  logic                 alert_minor_o,
  input  logic                 alert_major_internal_o,
  input  logic                 alert_major_bus_o,
  input  ibex_mubi_t           fetch_enable_i,
  input  ibex_mubi_t           core_busy_o
`ifdef RVFI
  ,
  input  logic                 rvfi_valid,
  input  logic [63:0]          rvfi_order,
  input  logic                 rvfi_trap,
  input  logic                 rvfi_halt,
  input  logic [1:0]           rvfi_mode,
  input  logic [1:0]           rvfi_ixl,
  input  logic                 rvfi_ext_irq_valid
`endif
);

  // ------------------------------------------------------------------------------------------------
  // Knobs per property group: +gen_chk_sva_<group>=0|1 wins over +gen_chk_all=0|1; default enabled (both names are
  // declared plusargs of gen_tb_knobs.yaml, so gen_base_test's unknown-plusarg fatal does not see them).
  // ------------------------------------------------------------------------------------------------
  function automatic bit chk_en(string name);   // name = the declared plusarg (gen_tb_pkg PLUSARG_CHK_SVA_*, the constants home)
    int unsigned v;
    if ($value$plusargs({name, "=%d"}, v)) return (v != 0);
    if ($value$plusargs({gen_tb_pkg::PLUSARG_CHK_ALL, "=%d"}, v)) return (v != 0);
    return 1'b1;
  endfunction
  bit en_st = 1'b1, en_ibus = 1'b1, en_dbus = 1'b1, en_icram = 1'b1, en_scrkey = 1'b1, en_irq = 1'b1, en_dbg = 1'b1, en_alert = 1'b1, en_rvfi = 1'b1;
  initial begin
    en_st = chk_en(gen_tb_pkg::PLUSARG_CHK_SVA_ST); en_ibus = chk_en(gen_tb_pkg::PLUSARG_CHK_SVA_IBUS); en_dbus = chk_en(gen_tb_pkg::PLUSARG_CHK_SVA_DBUS);
    en_icram = chk_en(gen_tb_pkg::PLUSARG_CHK_SVA_ICRAM); en_scrkey = chk_en(gen_tb_pkg::PLUSARG_CHK_SVA_SCRKEY); en_irq = chk_en(gen_tb_pkg::PLUSARG_CHK_SVA_IRQ);
    en_dbg = chk_en(gen_tb_pkg::PLUSARG_CHK_SVA_DBG); en_alert = chk_en(gen_tb_pkg::PLUSARG_CHK_SVA_ALERT); en_rvfi = chk_en(gen_tb_pkg::PLUSARG_CHK_SVA_RVFI);
  end
  int unsigned cycle;
  always_ff @(posedge clk_i or negedge rst_ni) if (!rst_ni) cycle <= 0; else cycle <= cycle + 1;
  // every violation is a collected UVM error under the property's id (the flow counts UVM_ERROR)
  `define GEN_PROTO_ERROR(ID_) uvm_report_error(ID_, $sformatf("GEN_PROTO %s: protocol property violated at cycle %0d", ID_, cycle))

  // P_ASSERT: group-knob-gated concurrent assertion; P_COVER: cover.
  `define P_ASSERT(GRP_, ID_, PROP_) \
    ID_: assert property (@(posedge clk_i) disable iff (!rst_ni || !en_``GRP_) (PROP_)) \
      else `GEN_PROTO_ERROR(`"ID_`");
  `define P_COVER(ID_, PROP_) \
    ID_: cover property (@(posedge clk_i) disable iff (!rst_ni) (PROP_));

  // ------------------------------------------------------------------------------------------------
  // Bookkeeping: outstanding granted-unanswered requests per bus; scramble-key pending flag; the
  // first-half data request of a split access; RVFI order tracking.
  // "outstanding" increments at the end of a grant cycle and decrements at the end of a response
  // cycle, so a response in its own grant cycle sees outstanding == 0 and fails the TB obligation.
  // ------------------------------------------------------------------------------------------------
  int unsigned ibus_outstanding, dbus_outstanding;
  always_ff @(posedge clk_i or negedge rst_ni) begin
    if (!rst_ni) begin
      ibus_outstanding <= 0;
      dbus_outstanding <= 0;
    end else begin
      ibus_outstanding <= ibus_outstanding + (instr_req_o & instr_gnt_i) - instr_rvalid_i;
      dbus_outstanding <= dbus_outstanding + (data_req_o & data_gnt_i) - data_rvalid_i;
    end
  end

  // data-side split tracking: remember the granted first-half address and byte enables
  logic        dbus_first_half_pending;
  logic [31:0] dbus_first_addr;
  logic [3:0]  dbus_first_be;
  wire  dbus_first_half_be = data_be_o inside {4'b1110, 4'b1100, 4'b1000};  // first half of a split (word +1/+2/+3, half +3)
  always_ff @(posedge clk_i or negedge rst_ni) begin
    if (!rst_ni) begin
      dbus_first_half_pending <= 1'b0;
      dbus_first_addr         <= '0;
      dbus_first_be           <= '0;
    end else if (data_req_o && data_gnt_i) begin
      dbus_first_half_pending <= dbus_first_half_be & ~dbus_first_half_pending;
      dbus_first_addr         <= data_addr_o;
      dbus_first_be           <= data_be_o;
    end
  end

  // scramble-key request pending (req seen, valid not yet returned high)
  logic scrkey_pending;
  always_ff @(posedge clk_i or negedge rst_ni) begin
    if (!rst_ni)                  scrkey_pending <= 1'b0;
    else if (ic_scr_key_req_o)    scrkey_pending <= 1'b1;
    else if (ic_scr_key_valid_i)  scrkey_pending <= 1'b0;
  end

  // icache lookup read (both RAM banks read, no write): the cycle before an ECC check
  wire icram_lookup_read = (|ic_tag_req_o) & ~ic_tag_write_o;
  logic [ICACHE_ECC_WINDOW:0] lookup_hist;   // bit k = the lookup read k cycles ago (bit 0 this cycle)
  always_ff @(posedge clk_i or negedge rst_ni) if (!rst_ni) lookup_hist <= '0; else lookup_hist <= (lookup_hist << 1) | {{ICACHE_ECC_WINDOW{1'b0}}, icram_lookup_read};

  // integrity decode of the three 39-bit words (err == 0 means a valid inverted-SECDED codeword)
  wire instr_rdata_bad = (prim_secded_inv_39_32_dec(instr_rdata_i).err != 2'b00);
  wire data_rdata_bad  = (prim_secded_inv_39_32_dec(data_rdata_i).err  != 2'b00);
  wire data_wdata_bad  = (prim_secded_inv_39_32_dec(data_wdata_o).err  != 2'b00);

  // ================================================================================================
  // ST: static inputs and MuBi control
  // ================================================================================================
  `P_ASSERT(st, sva_st_boot_addr_low_zero,  boot_addr_i[7:0] == 8'h00)                                    // TB
  `P_ASSERT(st, sva_st_hart_id_stable,      $stable(hart_id_i))                                           // TB
  `P_ASSERT(st, sva_st_fetch_enable_mubi,   fetch_enable_i inside {IbexMuBiOn, IbexMuBiOff})              // TB (off in MuBi-fault tests)
  `P_ASSERT(st, sva_st_core_busy_mubi,      core_busy_o inside {IbexMuBiOn, IbexMuBiOff})                 // DUT

  // ================================================================================================
  // IB: instruction bus
  // ================================================================================================
  `P_ASSERT(ibus, sva_ibus_req_hold,          instr_req_o && !instr_gnt_i |=> instr_req_o)                  // DUT
  `P_ASSERT(ibus, sva_ibus_addr_hold,         instr_req_o && !instr_gnt_i |=> $stable(instr_addr_o))        // DUT
  `P_ASSERT(ibus, sva_ibus_addr_aligned,      instr_req_o |-> instr_addr_o[1:0] == 2'b00)                   // DUT
  `P_ASSERT(ibus, sva_ibus_req_known,         !$isunknown(instr_req_o) && (!instr_req_o || !$isunknown(instr_addr_o))) // DUT
  `P_ASSERT(ibus, sva_ibus_gnt_only_with_req, instr_gnt_i |-> instr_req_o)                                  // TB
  `P_ASSERT(ibus, sva_ibus_rvalid_outstanding, instr_rvalid_i |-> ibus_outstanding > 0)                     // TB (never in the grant cycle, never unsolicited)
  `P_ASSERT(ibus, sva_ibus_outstanding_max,   ibus_outstanding <= IBUS_MAX_OUTSTANDING)                     // DUT (bound 8)
  `P_ASSERT(ibus, sva_ibus_err_with_rvalid,   instr_err_i |-> instr_rvalid_i)                               // TB hygiene
  `P_ASSERT(ibus, sva_ibus_rdata_intg,        instr_rvalid_i && !ibus_intg_corrupt_i |-> !instr_rdata_bad) // TB (unless injecting)
  `P_ASSERT(ibus, sva_ibus_rdata_known,       instr_rvalid_i |-> !$isunknown(instr_rdata_i))                // TB
  `P_COVER(sva_ibus_depth_max_seen,     ibus_outstanding == IBUS_MAX_OUTSTANDING)
  `P_COVER(sva_ibus_gnt_same_cycle,     $rose(instr_req_o) && instr_gnt_i)
  `P_COVER(sva_ibus_gnt_delayed,        instr_req_o && !instr_gnt_i ##1 instr_req_o && instr_gnt_i)
  `P_COVER(sva_ibus_err_beat,           instr_rvalid_i && instr_err_i)

  // ================================================================================================
  // DB: data bus
  // ================================================================================================
  `P_ASSERT(dbus, sva_dbus_req_hold,          data_req_o && !data_gnt_i |=> data_req_o)                     // DUT
  `P_ASSERT(dbus, sva_dbus_fields_hold,       data_req_o && !data_gnt_i |=> $stable(data_addr_o) && $stable(data_we_o) &&
                                                                     $stable(data_be_o) && (!data_we_o || $stable(data_wdata_o))) // DUT (a load's wdata is don't-care)
  `P_ASSERT(dbus, sva_dbus_addr_aligned,      data_req_o |-> data_addr_o[1:0] == 2'b00)                     // DUT
  `P_ASSERT(dbus, sva_dbus_be_legal,          data_req_o |-> data_be_o inside {4'b0001, 4'b0010, 4'b0100, 4'b1000,
                                                                       4'b0011, 4'b0110, 4'b1100,
                                                                       4'b1110, 4'b0111, 4'b1111})   // DUT
  `P_ASSERT(dbus, sva_dbus_store_intg,        data_req_o && data_we_o |-> !data_wdata_bad)                  // DUT (stores only; load wdata is don't-care)
  `P_ASSERT(dbus, sva_dbus_req_known,         !$isunknown(data_req_o) &&
                                        (!data_req_o || !$isunknown({data_addr_o, data_we_o, data_be_o}))) // DUT
  `P_ASSERT(dbus, sva_dbus_gnt_only_with_req, data_gnt_i |-> data_req_o)                                    // TB
  `P_ASSERT(dbus, sva_dbus_rvalid_outstanding, data_rvalid_i |-> dbus_outstanding > 0)                      // TB
  `P_ASSERT(dbus, sva_dbus_outstanding_max,   dbus_outstanding <= DBUS_MAX_OUTSTANDING)                     // DUT (bound 2)
  // (dbus_outstanding == 1 excludes a single byte access at offset 3, whose be 1000 equals a split first half)
  // The split rows are covers, not asserts: at the boundary a byte or half-word access at offset 2 or 3 (be 1100 / 1000)
  // is indistinguishable from a split's first half, and a pipelined unrelated request may follow it with one
  // outstanding, so the assert form fired on legal traffic (landing 2b). No TB checker owns the second-half address / byte-enable rule:
  // it is covered by the lock-step compare of every split access's data and by these covers (the chk_dbus_split knob has no consumer).
  `P_COVER(sva_dbus_split_second_addr, data_req_o && dbus_first_half_pending && (dbus_outstanding == 1) && data_addr_o == dbus_first_addr + 32'd4)
  `P_COVER(sva_dbus_split_second_be,   data_req_o && dbus_first_half_pending && (dbus_outstanding == 1) &&
                                          ((dbus_first_be == 4'b1110 && data_be_o == 4'b0001) ||
                                           (dbus_first_be == 4'b1100 && data_be_o == 4'b0011) ||
                                           (dbus_first_be == 4'b1000 && data_be_o inside {4'b0111, 4'b0001})))
  `P_ASSERT(dbus, sva_dbus_no_third_request,  data_req_o |-> dbus_outstanding < DBUS_MAX_OUTSTANDING)       // DUT (a request is never issued with two outstanding)
  `P_ASSERT(dbus, sva_dbus_err_with_rvalid,   data_err_i |-> data_rvalid_i)                                 // TB hygiene
  `P_ASSERT(dbus, sva_dbus_rdata_intg,        data_rvalid_i && !dbus_intg_corrupt_i |-> !data_rdata_bad)   // TB (unless injecting)
  `P_ASSERT(dbus, sva_dbus_rdata_known,       data_rvalid_i |-> !$isunknown(data_rdata_i))                  // TB
  `P_ASSERT(dbus, sva_dbus_tag_quiet,         data_tag_o == 1'b0)                                           // DUT (carve-out)
  `P_COVER(sva_dbus_split_seen,         data_req_o && dbus_first_half_pending && (dbus_outstanding == 1))
  `P_COVER(sva_dbus_depth_two_seen,     dbus_outstanding == 2)
  `P_COVER(sva_dbus_gnt_delayed,        data_req_o && !data_gnt_i ##1 data_req_o && data_gnt_i)
  `P_COVER(sva_dbus_store_err_resp,     data_rvalid_i && data_err_i)

  // ================================================================================================
  // IC: instruction-cache RAM ports (tag/data), 1-cycle synchronous RAM model
  // ================================================================================================
  `P_ASSERT(icram, sva_icram_tag_write_implies_req, ic_tag_write_o |-> |ic_tag_req_o)                        // DUT
  `P_ASSERT(icram, sva_icram_lookup_both_rams,      icram_lookup_read |-> |ic_data_req_o)                    // DUT
  `P_ASSERT(icram, sva_icram_lookup_all_ways,       icram_lookup_read |-> &ic_tag_req_o)                     // DUT
  `P_ASSERT(icram, sva_icram_addr_known,            (!(|ic_tag_req_o)  || !$isunknown({ic_tag_addr_o, ic_tag_write_o})) &&
                                             (!(|ic_data_req_o) || !$isunknown({ic_data_addr_o, ic_data_write_o}))) // DUT
  `P_ASSERT(icram, sva_icram_write_data_known,      (!ic_tag_write_o  || !$isunknown(ic_tag_wdata_o)) &&
                                             (!ic_data_write_o || !$isunknown(ic_data_wdata_o)))       // DUT
  `P_ASSERT(icram, sva_icram_tag_rdata_after_read,  icram_lookup_read |=> !$isunknown(ic_tag_rdata_i[0]) && !$isunknown(ic_tag_rdata_i[1])) // TB (RAM model latency 1)
  `P_ASSERT(icram, sva_icram_data_rdata_after_read, ((|ic_data_req_o) && !ic_data_write_o) |=>
                                             !$isunknown(ic_data_rdata_i[0]) && !$isunknown(ic_data_rdata_i[1])) // TB
  initial begin : sva_icram_widths                                                                    // DUT (static)
    assert ($bits(ic_tag_wdata_o) == TagSizeECC && $bits(ic_data_wdata_o) == LineSizeECC)   // gen_dut_top's TagSizeECC / LineSizeECC
      else `GEN_PROTO_ERROR("sva_icram_widths");
  end
  `P_COVER(sva_icram_alloc_write,       ic_tag_write_o && (ic_tag_req_o inside {2'b01, 2'b10}))       // one-way allocation write
  `P_COVER(sva_icram_inval_write,       ic_tag_write_o && (ic_tag_req_o == 2'b11))                    // invalidation sweep write

  // ================================================================================================
  // SK: scramble-key handshake
  // ================================================================================================
  `P_ASSERT(scrkey, sva_scrkey_req_pulse,       ic_scr_key_req_o |=> !ic_scr_key_req_o)                       // DUT
  `P_ASSERT(scrkey, sva_scrkey_no_req_pending,  scrkey_pending && !ic_scr_key_valid_i |-> !ic_scr_key_req_o)  // DUT
  `P_ASSERT(scrkey, sva_scrkey_valid_drops,     ic_scr_key_req_o |-> !ic_scr_key_valid_i)                     // TB (responder contract, C3.5): the registered req pulse and the valid the responder dropped at that cycle's negedge are sampled together
  `P_ASSERT(scrkey, sva_scrkey_valid_known,     !$isunknown(ic_scr_key_valid_i))                              // TB
  `P_COVER(sva_scrkey_req_seen,         ic_scr_key_req_o)
  `P_COVER(sva_scrkey_req_while_valid,  ic_scr_key_req_o && ic_scr_key_valid_i)                       // fence.i re-key with a valid key held

  // ================================================================================================
  // IQ: interrupts
  // ================================================================================================
  `P_ASSERT(irq, sva_irq_pins_known,         !$isunknown({irq_software_i, irq_timer_i, irq_external_i, irq_fast_i, irq_nm_i})) // TB
  `P_COVER(sva_irq_pending_seen,        irq_pending_o)
  `P_COVER(sva_irq_nmi_seen,            irq_nm_i)

  // ================================================================================================
  // DG: debug request
  // ================================================================================================
  `P_ASSERT(dbg, sva_dbg_req_known,          !$isunknown(debug_req_i))                                     // TB

  // ================================================================================================
  // AL: alerts
  // ================================================================================================
  `P_ASSERT(alert, sva_alert_internal_never,   !alert_major_internal_o)                                      // DUT (legal stimulus, RegFileECC=0)
  `P_ASSERT(alert, sva_alert_bus_iff_intg,     alert_major_bus_o == ((instr_rvalid_i && instr_rdata_bad) ||
                                                              (data_rvalid_i  && data_rdata_bad)))    // DUT (exact, same cycle)
  `P_ASSERT(alert, sva_alert_minor_window,     alert_minor_o |-> |lookup_hist[ICACHE_ECC_WINDOW:1]) // DUT (windowed: 1..ICACHE_ECC_WINDOW = 2 cycles from the lookup, GEN_ICACHE_ECC_WINDOW)
  `P_ASSERT(alert, sva_alerts_known,           !$isunknown({alert_minor_o, alert_major_internal_o, alert_major_bus_o})) // DUT
  `P_COVER(sva_alert_bus_seen,          alert_major_bus_o)
  `P_COVER(sva_alert_minor_seen,        alert_minor_o)

  // ================================================================================================
  // RV: RVFI sanity (only under +define+RVFI)
  // ================================================================================================
`ifdef RVFI
  logic        rvfi_seen_first;
  logic [63:0] rvfi_last_order;
  always_ff @(posedge clk_i or negedge rst_ni) begin
    if (!rst_ni) begin
      rvfi_seen_first <= 1'b0;
      rvfi_last_order <= '0;
    end else if (rvfi_valid) begin
      rvfi_seen_first <= 1'b1;
      rvfi_last_order <= rvfi_order;
    end
  end
  `P_ASSERT(rvfi, sva_rvfi_order_incr,        rvfi_valid && rvfi_seen_first |-> rvfi_order == rvfi_last_order + 64'd1) // DUT
  `P_ASSERT(rvfi, sva_rvfi_irq_valid_exclusive, rvfi_ext_irq_valid |-> !rvfi_valid)                         // DUT (T-017 3.2 static analysis)
  `P_ASSERT(rvfi, sva_rvfi_halt_zero,         !rvfi_halt)                                                   // DUT
  `P_ASSERT(rvfi, sva_rvfi_mode_legal,        rvfi_valid |-> (rvfi_mode inside {2'b11, 2'b00}) && (rvfi_ixl == 2'b01)) // DUT
  `P_ASSERT(rvfi, sva_rvfi_valid_known,       !$isunknown(rvfi_valid) && (!rvfi_valid || !$isunknown({rvfi_order, rvfi_trap}))) // DUT
  `P_COVER(sva_rvfi_trap_seen,          rvfi_valid && rvfi_trap)
  `P_COVER(sva_rvfi_irq_valid_seen,     rvfi_ext_irq_valid)
`endif

  `undef P_ASSERT
  `undef P_COVER
  `undef GEN_PROTO_ERROR
endmodule
