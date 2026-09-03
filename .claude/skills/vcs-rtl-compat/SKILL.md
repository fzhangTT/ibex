---
name: vcs-rtl-compat
description: Fix Synopsys VCS-specific RTL/SystemVerilog/SVA compilation and elaboration errors — $past() restrictions, SVA operator limits, elaboration failures, X-state handling, clocking blocks, dynamic types in assertions, and common Error-[...] codes. Use when VCS (this repo's simulator) rejects standard-compliant SV during TB/RTL compile.
---

Adapted from ChipSmart (riscv/ChipSmart) vcs-rtl-compat.

# VCS RTL Compatibility — Fix Reference

## How to Use This Skill

1. Copy the error code from the VCS log (e.g., `Error-[SVA-PAST-EXPR]`)
2. Find the matching section below
3. Apply the before→after fix recipe directly to the source file
4. Do not commit — leave staging to the user

Confirm it's VCS: log contains `Synopsys VCS`, `vcs_simv`, or `simv` binary.

---

## Identify the Failing Construct

- Search the log file for `Error-\[` — all VCS error codes
- Search the log file for `Warning-\[PCWM\]` — port width mismatch warning
- Search the log file for `Error-\[ELAB\]` — elaboration errors

---

## SVA / $past() Restrictions

### VCS-SVA-1 — Bit-select on `$past()` result

**Error:**
```
Error-[SVA-PAST-EXPR] SVA $past expression
  Bit-select or part-select on the return value of $past() is not allowed.
```

**Cause:** VCS requires the slice to be inside the `$past()` argument. IEEE 1800 is
ambiguous here; VCS is stricter than Xcelium/Questa on this.

**Fix — move bit-select inside:**
```systemverilog
// BEFORE (VCS rejects)
$past(data_bus)[7:0]
$past(status_reg)[N-1:0]
$past({tag, data})[3:0]

// AFTER (VCS accepts)
$past(data_bus[7:0])
$past(status_reg[N-1:0])
$past({tag, data}[3:0])
```

To find all instances, search for `\$past\s*([^)]*)\s*\[` in all `.sv` files.

---

### VCS-SVA-2 — `$past()` on full struct

**Error:**
```
Error-[SVA-PAST-EXPR] $past on struct type not allowed.
  Use individual struct field access inside $past().
```

**Fix — expand to fields:**
```systemverilog
// BEFORE
$past(pkt)            // pkt is a struct

// AFTER
$past(pkt.addr)
$past(pkt.data)
// OR pack into a logic vector first:
logic [W-1:0] pkt_flat;
assign pkt_flat = {pkt.addr, pkt.data, pkt.valid};
$past(pkt_flat)
```

---

### VCS-SVA-3 — `$past()` inside a function call

**Error:**
```
Error-[SVA-PAST-EXPR] $past() not allowed inside function argument.
```

**Fix — extract to intermediate signal:**
```systemverilog
// BEFORE
my_check_func($past(x), y)

// AFTER
logic past_x;
assign past_x = $past(x);
my_check_func(past_x, y)
```

---

### VCS-SVA-4 — `$past()` with infinite range

**Error:**
```
Error-[SVA-PAST-EXPR] $past with variable or unbounded depth not supported.
```

**Cause:** VCS does not support `$past(sig, [1:$])` — unbounded history depth.

**Fix — use bounded depth or register chain:**
```systemverilog
// BEFORE
$past(busy, [1:$])

// AFTER — use fixed max depth or shift register
logic [DEPTH-1:0] busy_hist;
always_ff @(posedge clk) busy_hist <= {busy_hist[DEPTH-2:0], busy};
// use busy_hist[N-1] for N-cycle history
```

---

### VCS-SVA-5 — `$stable()` / `$changed()` on packed slice

**Error:**
```
Error-[SVA-STBL] $stable on a slice expression is not supported.
```

**Fix — replace with explicit `$past` comparison:**
```systemverilog
// BEFORE
$stable(bus[N-1:0])
$changed(bus[N-1:0])

// AFTER
($past(bus[N-1:0]) == bus[N-1:0])     // equivalent to $stable
($past(bus[N-1:0]) != bus[N-1:0])     // equivalent to $changed
```

---

### VCS-SVA-6 — `inside` operator in concurrent SVA

**Error:**
```
Error-[SVA-IOP] inside set membership operator not supported inside
  sequence or property expression.
```

**Fix — expand to explicit OR comparisons:**
```systemverilog
// BEFORE
(state inside {ST_IDLE, ST_WAIT}) |-> req

// AFTER
(state == ST_IDLE || state == ST_WAIT) |-> req
```

For large sets, use a function:
```systemverilog
function automatic logic is_valid_state(input logic [2:0] s);
  return (s == ST_IDLE || s == ST_WAIT || s == ST_RUN);
endfunction
// use in SVA: is_valid_state(state) |-> req
```

---

### VCS-SVA-7 — Dynamic/associative array in SVA

**Error:**
```
Error-[SVA-DYNTYP] Dynamic type not allowed in SVA expression.
  Type 'dynamic array', 'associative array', 'string', 'class', or
  'event' cannot be used in concurrent assertion.
```

**Fix — extract to a static logic signal before assertion:**
```systemverilog
// BEFORE (dynamic array in assertion)
assert property (@(posedge clk) q.size() == 0 |-> idle);

// AFTER — track in static RTL signal
logic q_empty;
assign q_empty = (q.size() == 0);   // in a module, driven by always
assert property (@(posedge clk) q_empty |-> idle);
```

Restricted types in SVA: `dynamic array`, `associative array`, `queue`,
`string`, `class`, `event`, `chandle`, `real`, `shortreal`, `realtime`.

---

### VCS-SVA-8 — `disable iff` with hierarchical reference

**Error:**
```
Error-[SDFCMC] disable iff condition cannot be a hierarchical reference.
  Signal 'u_top.rst_n' is not allowed as disable iff condition.
```

**Fix — alias through a local wire:**
```systemverilog
// BEFORE
assert property (@(posedge clk) disable iff (u_top.rst_n == 0) p |-> q);

// AFTER
wire local_rst_n = u_top.rst_n;
assert property (@(posedge clk) disable iff (!local_rst_n) p |-> q);
```

---

### VCS-SVA-9 — `disable iff` in recursive property

**Error:**
```
Error-[SVA-RDIFF] disable iff not allowed in recursive property.
```

**Fix — remove `disable iff` from the recursive body; apply at the call site:**
```systemverilog
// BEFORE (disable iff inside recursive property)
property p_rec(n);
  disable iff (!rst_n) n > 0 |-> ##1 p_rec(n-1);
endproperty

// AFTER — disable iff at assertion site, not inside recursive property
property p_rec(n);
  n > 0 |-> ##1 p_rec(n-1);
endproperty
assert property (@(posedge clk) disable iff (!rst_n) p_rec(DEPTH));
```

---

### VCS-SVA-10 — `not` in recursive property

**Error:**
```
Error-[SVA-RNOT] not operator not allowed in recursive property body.
```

**Fix — De Morgan expansion or rephrase with non-recursive properties:**
```systemverilog
// BEFORE
property p_bad;
  not (a ##1 p_bad);   // recursive + not
endproperty

// AFTER — rephrase without not-in-recursive
property p_good;
  a |-> ##1 !b;        // expand what you intended
endproperty
```

---

### VCS-SVA-11 — `++` / `+=` operators in SVA sequence

**Error:**
```
Error-[SVA-ASSIGN] Assignment operator not allowed in SVA sequence/property.
  Use local variable initialization and match items only.
```

**Fix — use local variable with match item syntax:**
```systemverilog
// BEFORE
sequence s;
  int cnt = 0;
  (valid, cnt++)[*3];
endsequence

// AFTER — LRM-compliant local variable with match items
sequence s;
  int cnt;
  (valid, cnt = 0) ##1 (valid, cnt = cnt + 1)[*2];
endsequence
```

---

### VCS-SVA-12 — `cover property` in class scope

**Error:**
```
Error-[SVA-CPCLS] cover property cannot be declared in a class.
  cover property is only allowed in module, interface, or program scope.
```

**Fix — move to a bind module or checker bound to the DUT:**
```systemverilog
// BEFORE (in a class — illegal)
class my_cov;
  cover property (@(posedge clk) a ##1 b);
endclass

// AFTER — structural bind module
module cov_bind;
  bind my_dut my_cov_checker u_cov(.clk, .a, .b);
endmodule
module my_cov_checker(input logic clk, a, b);
  cover property (@(posedge clk) a ##1 b);
endmodule
```

---

### VCS-SVA-13 — String type in SVA expression

**Error:**
```
Error-[SVA-DYNTYP] string type not allowed in concurrent assertion expression.
```

**Fix — convert string comparison to integer/enum:**
```systemverilog
// BEFORE
assert property (@(posedge clk) (state_str == "IDLE") |-> rdy);

// AFTER — use enum or localparam
typedef enum logic [1:0] {ST_IDLE, ST_BUSY} state_e;
assert property (@(posedge clk) (state == ST_IDLE) |-> rdy);
```

---

## Elaboration Errors

### VCS-ELAB-1 — Hierarchical reference in parameter

**Error:**
```
Error-[IEHP] Illegal Elaboration-time Hierarchical Path
  Hierarchical reference not allowed in parameter value expression.
```

**Fix — use a localparam or package constant instead:**
```systemverilog
// BEFORE
parameter W = u_core.DATA_W;    // hierarchical — illegal at elab

// AFTER
localparam W = CORE_DATA_W;     // from package or explicit param
```

---

### VCS-ELAB-2 — `$bits()` on non-constant at elaboration

**Error:**
```
Error-[ELAB-BITS] $bits() argument not evaluable at elaboration time.
```

**Fix — use an explicit width parameter:**
```systemverilog
// BEFORE
localparam W = $bits(my_struct_t);   // fails in some VCS versions

// AFTER
localparam W = MY_STRUCT_WIDTH;      // define in package explicitly
// OR: typedef union { my_struct_t s; logic [W-1:0] flat; } u_t;
```

---

### VCS-ELAB-3 — Multiple drivers on same net

**Error:**
```
Error-[MDRN] Multiple drivers on net
  Net 'sig_name' has multiple drivers.
```

**Fix — resolve contention:**
```systemverilog
// BEFORE — two always blocks driving same signal
always_comb sig = a & b;
always_comb sig = c | d;    // multiple drivers

// AFTER — merge into one block or use wor/wand
always_comb sig = (a & b) | (c & d);
```

---

### VCS-ELAB-4 — Unconnected interface port (bind)

**Error:**
```
Error-[SV-UIP] Unconnected interface port in bind
  Interface port 'axi_if' is not connected in bind instance.
```

**Fix — bind modules must connect all interface ports; use input ports only:**
```systemverilog
// BEFORE — bind module with floating interface port
module chk(axi_if.monitor axi);
  ...
endmodule
bind my_dut chk u_chk();   // axi port unconnected

// AFTER — pass signals explicitly through scalar ports
module chk(input logic clk, valid, input logic [31:0] addr);
  ...
endmodule
bind my_dut chk u_chk(.clk, .valid, .addr);
```

---

### VCS-ELAB-5 — Port width mismatch

**Warning:**
```
Warning-[PCWM] Port Connection Width Mismatch
  Instantiation 'u_sub' port 'data_in' width 8 != expression width 16.
```

**Fix — explicit width cast at instantiation:**
```systemverilog
// BEFORE
sub_module u_sub(.data_in(wide_bus));   // 16-bit bus → 8-bit port: truncation

// AFTER — be explicit about the slice
sub_module u_sub(.data_in(wide_bus[7:0]));
```

---

## X-State / 2-State Handling

### VCS-X-1 — 2-state variable spurious negedge at time-0

**Issue:** VCS initializes 2-state (`bit`, `int`, `byte`) variables to 0 at time-0,
which can fire a spurious `negedge` on any 2-state variable that was X before time-0.

**Fix — use 4-state types for signals with reset semantics:**
```systemverilog
// BEFORE — spurious negedge fires at time-0
bit data_valid;       // initializes 0: X→0 = negedge fires

// AFTER — 4-state: stays X until driven, no spurious edge
logic data_valid;
```

For testbench variables that must be 2-state, initialize explicitly:
```systemverilog
bit data_valid = 1'b0;   // explicit init — no X phase
```

---

### VCS-X-2 — `'x` / `'z` in 2-state context warning

**Warning:**
```
Warning-[ISNVU] Implicit signal narrow to value with unresolved bits
  'x or 'z assigned to 2-state variable loses X/Z.
```

**Fix — use 4-state signal or conditional compile guard:**
```systemverilog
// BEFORE
bit [7:0] out = 'x;    // warning: x assigned to 2-state

// AFTER
logic [7:0] out = 'x;  // 4-state: OK
// or guard for synthesis/sim split:
`ifdef SIMULATION
  assign out = 'x;     // catch uninitialized
`else
  assign out = '0;
`endif
```

---

## Clocking Block Restrictions

### VCS-CLK-1 — Multiple synchronous drives to same signal

**Error (runtime):**
```
Error-[MDRN-CB] Multiple synchronous clocking block drives to same signal.
  Signal 'ready' driven from two clocking blocks simultaneously.
```

**Fix — use only one clocking block as driver per signal:**
```systemverilog
// BEFORE — two clocking blocks drive same signal
clocking cb1 @(posedge clk); output ready; endclocking
clocking cb2 @(posedge clk); output ready; endclocking

// AFTER — single driver clocking block
clocking cb @(posedge clk); output ready; endclocking
```

---

### VCS-CLK-2 — `##1` before default clocking declared

**Error:**
```
Error-[SVA-NODC] No default clocking block declared.
  ##N cycle delay requires a default clocking block.
```

**Fix — declare `default clocking` before any cycle-delay assertions:**
```systemverilog
// Add at module level before assertions:
default clocking main_cb @(posedge clk); endclocking
```

---

## `always_comb` / `always_latch` Issues

### VCS-AC-1 — Latch inferred in `always_comb`

**Warning:**
```
Warning-[LATCH] Latch inferred
  Signal 'out' not assigned in all paths of always_comb block.
```

**Fix — ensure all branches assign the output:**
```systemverilog
// BEFORE — latch on else-missing if
always_comb begin
  if (sel) out = a;
  // no else: out holds value → latch
end

// AFTER — explicit default
always_comb begin
  out = '0;           // default assignment first
  if (sel) out = a;
end
```

---

### VCS-AC-2 — `$readmemh` / `$readmemb` in `always_latch`

**Error:**
```
Error-[ARLM] always_latch with $readmem
  $readmemh cannot be used inside always_latch block.
```

**Fix — move to `initial` block:**
```systemverilog
// BEFORE
always_latch $readmemh("init.hex", mem);

// AFTER
initial $readmemh("init.hex", mem);
```

---

## Cross-Module Reference (XMR)

### VCS-XMR-1 — Ambiguous XMR in SVA

**Error:**
```
Error-[XMRS] Ambiguous XMR in SVA
  Cross-module reference 'M.sig' resolves to multiple instances.
```

**Fix — use fully qualified path from the top:**
```systemverilog
// BEFORE (ambiguous — M exists under P and R)
assert property (M.sig == 1);

// AFTER — full path
assert property (tb_top.P.M.sig == 1);
```

---

### VCS-XMR-2 — Hierarchical reference in bind checker

**Error:**
```
Error-[XMRE] XMR in bind module
  Cross-module reference not allowed in this scope inside bind.
```

**Fix — pass signals as ports to the bind module; do not use XMRs inside bind:**
```systemverilog
// BEFORE — bind module uses XMR internally
module chk;
  assert property (u_top.core.stall == 0);   // XMR inside bind
endmodule

// AFTER — pass as port
module chk(input logic stall);
  assert property (stall == 0);
endmodule
bind my_dut chk u_chk(.stall(u_core.stall));
// XMR in bind instantiation port connection is OK
```

---

## `$cast()` Restrictions

### VCS-CAST-1 — Unguarded `$cast` failure becomes fatal

**Issue:** When used as a task, `$cast(dest, src)` calls `$fatal` on type mismatch.
When used as a function, it returns 0. VCS may handle differently from Questa.

**Fix — always use as function with check:**
```systemverilog
// BEFORE (task form — fatal on mismatch)
$cast(child_h, parent_h);

// AFTER (function form — safe)
if (!$cast(child_h, parent_h)) begin
  `uvm_fatal("CAST", "Cast failed — parent does not hold child type")
end
```

---

## Compilation / Preprocessor

### VCS-PP-1 — Assertion compile-time disable

**Pattern:** Selectively disable assertions for specific compile modes:

```systemverilog
// Disable all concurrent assertions at compile time:
//   vcs +define+SV_ASSERT_OFF ...

`ifndef SV_ASSERT_OFF
  assert property (@(posedge clk) p |-> q);
`endif

// Disable specific assertion:
`ifndef DISABLE_CHK_FIFO_OVERFLOW
  assert property (...fifo overflow check...);
`endif
```

---

### VCS-PP-2 — SVA extended features flag

**Error:**
```
Error-[SVACST] SVA context error.
  Feature requires -assert svaext compilation option.
```

**Fix — add to VCS compile flags:**
```
vcs -sverilog -assert svaext ...
```
In this repo, add `-assert svaext` to your VCS compile flags (the `docs/dv/SIM_RECIPE.md`
§2 command, or your own flag file).

---

## Local Variables in SVA Sequences

### VCS-LV-1 — Local variable not visible across parallel branches

**Issue:** A local variable written inside a `first_match` or `intersect` branch
is not guaranteed visible in the other branch. VCS creates a new copy per match attempt.

**Fix — do not share state between parallel branches; use the local variable
only within a single linear sequence:**
```systemverilog
// BEFORE (undefined behavior — cross-branch local var)
sequence s;
  int cnt;
  (valid, cnt = 0) intersect (req[*1:$], cnt++);
endsequence

// AFTER — track externally with RTL register
logic [7:0] req_cnt;
always_ff @(posedge clk or negedge rst_n)
  if (!rst_n) req_cnt <= '0;
  else if (req) req_cnt <= req_cnt + 1;
  else if (done) req_cnt <= '0;
// Use req_cnt directly in SVA
```

---

## Quick Error-Code Lookup Table

| VCS Error Code | Construct | Section |
|---|---|---|
| `Error-[SVA-PAST-EXPR]` | `$past()` bit-select / struct / func | VCS-SVA-1..3 |
| `Error-[SVA-STBL]` | `$stable` on slice | VCS-SVA-5 |
| `Error-[SVA-IOP]` | `inside` in property/sequence | VCS-SVA-6 |
| `Error-[SVA-DYNTYP]` | Dynamic/string/class in SVA | VCS-SVA-7 |
| `Error-[SDFCMC]` | Hierarchical `disable iff` | VCS-SVA-8 |
| `Error-[SVA-RDIFF]` | `disable iff` in recursive prop | VCS-SVA-9 |
| `Error-[SVA-RNOT]` | `not` in recursive property | VCS-SVA-10 |
| `Error-[SVA-ASSIGN]` | `++`/`+=` in SVA sequence | VCS-SVA-11 |
| `Error-[SVA-CPCLS]` | `cover property` in class | VCS-SVA-12 |
| `Error-[IEHP]` | Hierarchical ref in parameter | VCS-ELAB-1 |
| `Error-[ELAB-BITS]` | `$bits()` at elaboration | VCS-ELAB-2 |
| `Error-[MDRN]` | Multiple net drivers | VCS-ELAB-3 |
| `Error-[SV-UIP]` | Unconnected interface in bind | VCS-ELAB-4 |
| `Warning-[PCWM]` | Port width mismatch | VCS-ELAB-5 |
| `Warning-[ISNVU]` | X/Z to 2-state variable | VCS-X-2 |
| `Warning-[LATCH]` | Latch inferred in always_comb | VCS-AC-1 |
| `Error-[ARLM]` | `$readmemh` in always_latch | VCS-AC-2 |
| `Error-[XMRS]` | Ambiguous XMR in SVA | VCS-XMR-1 |
| `Error-[XMRE]` | XMR inside bind module | VCS-XMR-2 |
| `Error-[SVACST]` | SVA feature needs `-assert svaext` | VCS-PP-2 |
| `Error-[MDRN-CB]` | Multiple CB drives | VCS-CLK-1 |
| `Error-[SVA-NODC]` | No default clocking | VCS-CLK-2 |

---

## Fix Workflow for Automated RTL Repair

1. Search the log file for `Error-\[` → extract error codes
2. Match code to table above → find section
3. Search for the offending pattern in all `.sv` files → locate all instances
4. Apply the before→after fix recipe by editing the source file
5. Verify: search for the AFTER pattern (should exist) and the BEFORE pattern (should be gone)
6. Do NOT commit — edit source file only

<!-- length-justified: 13 specific VCS error patterns each with before/after diff — pruning loses reference value -->
