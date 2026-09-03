// gen_icache_ram: transparent synchronous single-port RAM model for one way of the core's icache tag
// or data RAM (architecture C3.4), the same timing as prim_ram_1p: a write takes effect at the edge
// with req & write; a read presents its data the cycle after req & ~write and holds it until the next
// read. Contents initialise per +gen_icram_init (random by default: the core's reset sweep invalidates
// every tag before use, and data of never-hit lines is never consumed; zero only for directed bring-up).
// ECC injection hooks (ICACHE_ECC_ARM) arrive with the icram checkers in step 2.
module gen_icache_ram import gen_tb_pkg::*; #(
  parameter int unsigned Width = 28,
  parameter int unsigned Depth = 256,
  parameter string       Name  = "tag0"
) (
  input  logic                     clk,
  input  logic                     rst_n,
  input  logic                     req,
  input  logic                     write,
  input  logic [$clog2(Depth)-1:0] addr,
  input  logic [Width-1:0]         wdata,
  output logic [Width-1:0]         rdata
);
  logic [Width-1:0] mem [Depth];
  int unsigned writes = 0;
  int unsigned reads  = 0;

  initial begin
    string mode = GEN_ENUM_ICRAM_INIT_DEFAULT;
    void'($value$plusargs({PLUSARG_ICRAM_INIT, "=%s"}, mode));
    for (int i = 0; i < Depth; i++) begin
      if (mode == "zero") mem[i] = '0;
      else begin
        logic [Width-1:0] v = '0;
        for (int b = 0; b < Width; b++) v[b] = $urandom_range(1, 0);   // bitwise: constant-width select
        mem[i] = v;
      end
    end
    rdata = '0;
  end

  // always (not always_ff): mem and rdata also have initial-block writers (VCS ICPD rule).
  always @(posedge clk) begin
    if (req) begin
      if (write) begin
        mem[addr] <= wdata;
        writes++;
      end else begin
        rdata <= mem[addr];
        reads++;
      end
    end
  end
endmodule
