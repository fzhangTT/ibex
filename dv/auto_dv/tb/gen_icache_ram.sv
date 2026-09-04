// gen_icache_ram: transparent synchronous single-port RAM model for one way of the core's icache tag
// or data RAM (architecture C3.4), the same timing as prim_ram_1p: a write takes effect at the edge
// with req & write; a read presents its data the cycle after req & ~write and holds it until the next
// read. Contents initialise per +gen_icram_init (random by default: the core's reset sweep invalidates
// every tag before use, and data of never-hit lines is never consumed; zero only for directed bring-up).
// ECC injection (test equipment, never a DUT change): a TAG RAM flips one or two bits of a read at
// gen_icram_events::inject_rate per mille and announces the read (cycle, way, index); a tag ECC error
// on any way of a checked lookup raises alert_minor_o (rtl/ibex_icache.sv:585), hit or not, so the
// misc monitor owes every qualified injection one pulse. A DATA RAM flips bits at inject_rate_data and
// announces the read with the way's stored tag state: the DUT checks data ECC only on the way the
// lookup hit, which the monitor derives from the tag shadow and the lookup tag (the P9 probe, or the retirement stream).
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
  int unsigned rng;          // the instance's own stream: on the shared $urandom stream every way injects in the same cycle at the same position

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
      if (IsTag) gen_icram_events::note_tag_init(Way, i, GEN_IC_TAG_ECC_W'(mem[i]));
    end
    rdata = '0;
    rng = $urandom ^ (32'h9E37_79B9 * (Way + 1)) ^ (IsTag ? 32'h0 : 32'hA5A5_5A5A);
  end
  function automatic int unsigned rnd(int unsigned n);   // 0..n-1 from the instance's xorshift stream
    rng ^= rng << 13; rng ^= rng >> 17; rng ^= rng << 5;
    return rng % n;
  endfunction

  always @(posedge clk or negedge rst_n) if (!rst_n) cycle <= 0; else cycle <= cycle + 1;

  // one or two distinct flipped positions, a second one inside the same beat (span: the tag word, or one 39-bit data beat); function
  // locals are automatic: no state survives between reads
  // the DUT's data tweak for a stored line: its own address bits [31:3] at the base of every beat (rtl/ibex_icache.sv gen_tweak_infection);
  // the line's address is the way's stored tag (from the tag shadow) with this index
  function automatic logic [Width-1:0] data_tweak(logic [31:0] line_addr);
    logic [Width-1:0] t = '0;
    for (int i = 0; i < ibex_pkg::IC_LINE_BEATS; i++) t |= Width'({line_addr[31:3], 3'b000}) << (i * (Width / ibex_pkg::IC_LINE_BEATS));
    return t;
  endfunction
  function automatic logic [Width-1:0] inject_mask(int unsigned bits, int unsigned span, output int unsigned first_pos);
    logic [Width-1:0] m = '0; int unsigned p1 = rnd(Width), base, p2;
    m[p1] = 1'b1; first_pos = p1; base = (p1 / span) * span;
    if (bits > 1) begin p2 = base + ((p1 - base) + 1 + rnd(span - 1)) % span; m[p2] = 1'b1; end
    return m;
  endfunction

  // always (not always_ff): mem and rdata also have initial-block writers (VCS ICPD rule).
  always @(posedge clk) begin
    if (req) begin
      if (write) begin
        mem[addr] <= wdata;
        writes++;
        if (IsTag) gen_icram_events::note_tag_write(cycle, Ways, int'(addr), Way, GEN_IC_TAG_ECC_W'(wdata));
      end else begin
        if (IsTag && gen_icram_events::inject_rate > 0 && (rnd(1000) < gen_icram_events::inject_rate)) begin
          int unsigned pos;
          rdata <= mem[addr] ^ inject_mask(gen_icram_events::inject_bits, Width, pos);   // one or two flipped bits: always a detectable ECC error
          gen_icram_events::injected++;
          gen_icram_events::announce(cycle, Way, int'(addr), "inject", gen_icram_events::qualified_at(cycle), 0, gen_icram_events::inject_bits);
        end else if (!IsTag && gen_icram_events::inject_rate_data > 0 && (rnd(1000) < gen_icram_events::inject_rate_data)) begin
          int unsigned pos; logic [Width-1:0] mask;   // no initializer: a block-local with one would be static and keep its first value
          mask = inject_mask(gen_icram_events::inject_bits, Width / ibex_pkg::IC_LINE_BEATS, pos);   // both flips inside one beat
          rdata <= mem[addr] ^ mask;
          gen_icram_events::injected_data++;
          begin
            logic [31:0] line_addr;   // no initializer (static block-local)
            line_addr = {gen_icram_events::shadow_tag(Way, int'(addr))[ibex_pkg::IC_TAG_SIZE-2:0], addr[ibex_pkg::IC_INDEX_W-1:0], {ibex_pkg::IC_LINE_W{1'b0}}};
            gen_icram_events::announce(cycle, Way, int'(addr), "inject_data", gen_icram_events::qualified_at(cycle), pos / (Width / ibex_pkg::IC_LINE_BEATS), gen_icram_events::inject_bits,
                                       |(mask & ~(mem[addr] ^ data_tweak(line_addr))));   // a flip that raises a DATA bit (the un-tweaked word the DUT ORs) stays visible across duplicate copies
          end
        end else begin
          rdata <= mem[addr];
        end
        reads++;
      end
    end
  end
endmodule
