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
