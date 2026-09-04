// gen_icache_ram: transparent synchronous single-port RAM model for one way of the core's icache tag
// or data RAM (architecture C3.4), the same timing as prim_ram_1p: a write takes effect at the edge
// with req & write; a read presents its data the cycle after req & ~write and holds it until the next
// read. Contents initialise per +gen_icram_init (random by default: the core's reset sweep invalidates
// every tag before use, and data of never-hit lines is never consumed; zero only for directed bring-up).
// ECC injection (test equipment, never a DUT change): a TAG RAM flips one bit of a read at
// gen_icram_events::inject_rate per mille and announces the read (cycle, way, index); a tag ECC error
// on any way of a checked lookup raises alert_minor_o (rtl/ibex_icache.sv:585), hit or not, so the
// misc monitor owes every qualified injection one pulse. Data RAMs never inject: their ECC is checked
// only on a hit, which the TB cannot know from the boundary.
module gen_icache_ram import gen_tb_pkg::*; #(
  parameter int unsigned Width = 28,
  parameter int unsigned Depth = 256,
  parameter string       Name  = "tag0",
  parameter int unsigned Ways  = 2,      // IC_NUM_WAYS: a write on every way in one cycle is a sweep or an ECC-correction write
  parameter int unsigned Way   = 0,
  parameter bit          IsTag = 1'b0
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
  int unsigned cycle  = 0;   // the same count as gen_misc_if's (posedge clk from the reset release), so announcements share its base

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

  always @(posedge clk or negedge rst_n) if (!rst_n) cycle <= 0; else cycle <= cycle + 1;

  // always (not always_ff): mem and rdata also have initial-block writers (VCS ICPD rule).
  always @(posedge clk) begin
    if (req) begin
      if (write) begin
        mem[addr] <= wdata;
        writes++;
        if (IsTag) gen_icram_events::note_tag_write(cycle, Ways, int'(addr));
      end else begin
        if (IsTag && gen_icram_events::inject_rate > 0 && ($urandom_range(999, 0) < gen_icram_events::inject_rate)) begin
          rdata <= mem[addr] ^ (Width'(1) << $urandom_range(Width - 1, 0));   // exactly one flipped bit: always a decodable ECC error
          gen_icram_events::injected++;
          gen_icram_events::announce(cycle, Way, int'(addr), "inject", gen_icram_events::qualified_at(cycle));
        end else begin
          rdata <= mem[addr];
        end
        reads++;
      end
    end
  end
endmodule
