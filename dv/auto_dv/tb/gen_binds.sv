// gen_binds.sv: the one file that holds every bind of the TB (architecture C10). The protocol SVA layer gen_protocol_props
// binds into gen_dut_top with the wrapper's own port names; the two TB-side integrity flags come from the bus interfaces
// of gen_tb_top through absolute paths (TB-owned signals, not DUT internals). No bind forces or drives a DUT net.
bind gen_dut_top gen_protocol_props #(
  .IBUS_MAX_OUTSTANDING (gen_tb_pkg::GEN_IBUS_MAX_OUTSTANDING),
  .DBUS_MAX_OUTSTANDING (gen_tb_pkg::GEN_DBUS_MAX_OUTSTANDING),
  .ICACHE_ECC_WINDOW    (gen_tb_pkg::GEN_ICACHE_ECC_WINDOW),
  .TagSizeECC           (TagSizeECC),
  .LineSizeECC          (LineSizeECC)
) gen_protocol_props_i (
  .*,
  .ibus_intg_corrupt_i (gen_tb_top.u_ibus_if.intg_corrupt),
  .dbus_intg_corrupt_i (gen_tb_top.u_dbus_if.intg_corrupt)
);
// The B8 probe (LOG-067: a probe bind behind a knob, off by default): a bind that reads DUT internals, the dummy insertion
// and the Zcmp expansion FSM of ibex_if_stage; it drives nothing. The P9 probe below is the only other one.
bind ibex_if_stage gen_b8_probe gen_b8_probe_i (
  .clk_i        (clk_i),
  .rst_ni       (rst_ni),
  .pipe_we_i    (if_id_pipe_reg_we),
  .dummy_i      (gen_dummy_instr.insert_dummy_instr),
  .fsm_stable_i (compressed_decoder_i.cm_state_d == compressed_decoder_i.cm_state_q && compressed_decoder_i.cm_rlist_d == compressed_decoder_i.cm_rlist_q &&
                 compressed_decoder_i.cm_sp_offset_d == compressed_decoder_i.cm_sp_offset_q)
);
// The lookup-tag probe (P9, LOG-079: a read-only probe bind behind a knob, off by default, debug only): the icache's registered
// lookup tag, so the misc monitor can derive the hit way for a data-RAM ECC injection from the TB's own tag RAM contents; it drives nothing.
bind ibex_icache gen_ic_lookup_probe #(.TagW(ADDR_W - IC_INDEX_HI - 1)) gen_ic_lookup_probe_i (
  .clk_i        (clk_i),
  .rst_ni       (rst_ni),
  .lookup_tag_i (lookup_addr_ic1)
);
