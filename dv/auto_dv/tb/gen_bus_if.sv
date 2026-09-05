// gen_bus_if: one memory-bus interface (instruction or data side of gen_dut_top, architecture C3.1 /
// C3.2). The TB drives gnt, rvalid, rdata (with integrity) and err; the DUT drives req, addr and, on
// the data side, we, be, wdata. Carries the stimulus-legality self-check sva_rvalid_legal (rtl-arch
// T-022 evidence 5.2: rvalid only while a grant is outstanding, never in the grant cycle), reported as
// a collected UVM error with id sva_rvalid_legal (knob +gen_chk_sva_rvalid_legal via chk_rvalid_legal_en).
interface gen_bus_if #(
  parameter int unsigned DataW = 39,
  parameter string       Name  = "ibus"
) (
  input logic clk,
  input logic rst_n
);
  import uvm_pkg::*;

  logic              req;
  logic              gnt;
  logic              rvalid;
  logic              err;
  logic              we;
  logic [3:0]        be;
  logic [31:0]       addr;
  logic [DataW-1:0]  wdata;
  logic [DataW-1:0]  rdata;

  logic              intg_corrupt = 1'b0;   // with rvalid: rdata carries corrupted integrity (alert_bus expectation)

  bit chk_rvalid_legal_en = 1'b1;

  // Grants not yet answered, counted at the clock edge (a grant and a response in the same cycle
  // cancel; the response belongs to an older grant).
  int unsigned outstanding = 0;
  int unsigned cycle = 0;
  always @(posedge clk or negedge rst_n) begin
    if (!rst_n) begin
      outstanding <= 0;
      cycle       <= 0;
    end else begin
      // saturate at zero: a wrap leaves the count permanently one below the truth, which makes the assertion
      // below pass on the next real violation and then fail on legal traffic, and lies to its cover both ways
      outstanding <= (rvalid && (outstanding + ((req && gnt) ? 1 : 0)) == 0) ? 0
                     : outstanding + ((req && gnt) ? 1 : 0) - (rvalid ? 1 : 0);
      cycle       <= cycle + 1;
    end
  end

  // TB self-check: a response needs an older outstanding grant (rvalid in the grant cycle of the
  // only request would see outstanding == 0 here).
  property p_rvalid_legal;
    @(posedge clk) disable iff (!rst_n || !chk_rvalid_legal_en)
      rvalid |-> (outstanding > 0);
  endproperty
  sva_rvalid_legal: assert property (p_rvalid_legal)
    else uvm_report_error("sva_rvalid_legal", $sformatf("%s: rvalid with no outstanding grant at cycle %0d", Name, cycle));
  cov_rvalid_legal: cover property (@(posedge clk) disable iff (!rst_n) rvalid && outstanding > 0);
endinterface
