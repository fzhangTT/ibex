// gen_bridge_if: the cocotb-to-UVM bridge register block (architecture C2). Python writes the
// command and threshold fields and awaits single-bit edges; SV acks and raises events. Nothing here
// is a DUT signal. Threshold compares are evaluated here every cycle so Python never polls (A-01):
// one edge bit per threshold (v3, N-02). Field semantics: dv/auto_dv/docs/gen_component_api_bridge.md.
interface gen_bridge_if (
  input logic clk,
  input logic rst_n,
  input logic rvfi_valid   // retirement count source (boundary signal)
);
  import gen_tb_pkg::*;

  // Python-written (deposited through VPI); initialised so nothing is X before Python starts.
  logic        alive        = 1'b0;
  logic        stim_active  = 1'b0;
  logic        cmd_valid    = 1'b0;
  logic [7:0]  cmd_kind     = GEN_CMD_NONE;
  logic [31:0] cmd_arg0     = '0;
  logic [31:0] cmd_arg1     = '0;
  logic [31:0] cmd_arg2     = '0;
  logic [31:0] cmd_arg3     = '0;
  logic [15:0] cmd_seq      = '0;
  logic [31:0] evt_retired_target = '0;
  logic        evt_retired_arm    = 1'b0;   // toggle after writing the target
  logic [31:0] evt_cycle_target   = '0;
  logic        evt_cycle_arm      = 1'b0;
  logic        finish_req   = 1'b0;

  // SV-written
  logic        listener_armed = 1'b0;
  logic        cmd_ack        = 1'b0;   // toggles once per consumed command
  logic [15:0] cmd_ack_seq    = '0;
  logic [15:0] cmds_consumed  = '0;
  logic [31:0] peek_data      = '0;
  logic        evt_retired_hit = 1'b0;  // toggles when retired_count >= target after an arm edge
  logic        evt_cycle_hit   = 1'b0;
  logic        evt_irq_taken   = 1'b0;
  logic [4:0]  evt_irq_taken_cause = '0;   // the vector cause of the last interrupt entry (31 = NMI), written by the scoreboard
  logic        evt_dbg_entered = 1'b0;
  logic        evt_eot_seen    = 1'b0;   // toggles on every end-of-test store (tohost or the EOT register)
  logic [31:0] evt_eot_code    = '0;     // the stored value (1 = pass by the riscv-dv/tohost convention)
  logic [15:0] evt_eot_count   = '0;
  logic [31:0] evt_retired_count = '0;
  logic [15:0] evt_err_count     = '0;
  logic [31:0] evt_isa_records   = '0;   // RVFI records the scoreboard compared against the model
  logic [15:0] evt_isa_mismatch  = '0;   // ISA compare mismatches (each also a uvm_error)
  logic [31:0] evt_ibus_grants   = '0;   // grant beats the bus drivers drove (the export's independent gnt count)
  logic [31:0] evt_dbus_grants   = '0;
  logic        finish_ack        = 1'b0;

  // Free-running counters (cycles since reset release; retirements from the RVFI valid pin).
  logic [31:0] cycle_count = '0;
  always @(posedge clk or negedge rst_n) begin  // always, not always_ff: the variables carry initialisers (VCS ICPD)
    if (!rst_n) begin
      cycle_count       <= '0;
      evt_retired_count <= '0;
    end else begin
      cycle_count <= cycle_count + 32'd1;
      if (rvfi_valid) evt_retired_count <= evt_retired_count + 32'd1;
    end
  end

  // Threshold engine: an arm edge latches the target; the first cycle at or beyond it toggles the
  // hit bit exactly once. Two thresholds, two arm bits, two hit bits (N-02).
  logic retired_armed = 1'b0, cycle_armed = 1'b0;
  logic evt_retired_arm_q = 1'b0, evt_cycle_arm_q = 1'b0;
  always @(posedge clk) begin
    evt_retired_arm_q <= evt_retired_arm;
    evt_cycle_arm_q   <= evt_cycle_arm;
    if (evt_retired_arm != evt_retired_arm_q) retired_armed <= 1'b1;
    else if (retired_armed && evt_retired_count >= evt_retired_target) begin
      retired_armed   <= 1'b0;
      evt_retired_hit <= ~evt_retired_hit;
    end
    if (evt_cycle_arm != evt_cycle_arm_q) cycle_armed <= 1'b1;
    else if (cycle_armed && cycle_count >= evt_cycle_target) begin
      cycle_armed   <= 1'b0;
      evt_cycle_hit <= ~evt_cycle_hit;
    end
  end
endinterface
