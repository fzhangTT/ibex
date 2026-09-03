# Task 2 Report: SV overlay — cocotb interface, watchdog, objection holder, finish ownership

## Status: DONE (all steps green)

## Steps

### Step 1
Read the quasar reference files (`quasar_cocotb_if.sv`, `quasar_cocotb_monitor.sv`,
`quasar_tb.sv:504-512`) once. Wrote `dv/uvm/core_ibex/tb/core_ibex_cocotb_if.sv`: entire
body under `` `ifdef COCOTB_SIM ``, with `cctb_alive`, `cocotb_active`, `uvm_finished`,
`uvm_ready` (all `bit`, default 0), a `COCOTB_SIM__DEFINED = 1` flag bit, and the 100ns
watchdog `initial` block with the exact `$fatal` message from the brief.

Simplification vs. quasar: quasar's `` `QUASAR_DEFINE_MACRO_FLAG `` macro handles both the
defined and undefined case so cocotb can see the flag either way. Since our entire
interface file (including `COCOTB_SIM__DEFINED`) only exists when `COCOTB_SIM` is already
defined, the generic ifdef/else machinery is redundant here — the bit is declared directly
as `1`. Flagging this as a deliberate deviation, not an oversight.

### Step 2
Wrote `dv/uvm/core_ibex/common/ibex_cocotb/core_ibex_cocotb_monitor.sv`: a `uvm_component`
whose entire body is under `` `ifdef COCOTB_SIM `` (it references `virtual
core_ibex_cocotb_if`, which doesn't exist otherwise). `build_phase` gets the vif via
`uvm_config_db#(virtual core_ibex_cocotb_if)::get(null, "", "cocotb_if", cocotb_vif)`
(config_db, not quasar's resource-db-set-from-the-interface pattern, per the brief) —
mirrors the existing `get(null, "", ...)` convention used for `clk_if`/`dut_if`/etc. in
`core_ibex_base_test.sv`. `run_phase` raises the objection, then waits `cctb_alive==1`,
then `cocotb_active==1`, then `cocotb_active==0`, then drops — never samples
`cocotb_active` before `cctb_alive` is confirmed, so there's no time-zero race.
`final_phase` sets `uvm_finished = 1`.

In `core_ibex_tb_top.sv`, added `` uvm_config_db#(virtual core_ibex_cocotb_if)::set(null,
"*", "cocotb_if", cocotb_if) `` and `` uvm_root::get().finish_on_completion = 0 `` — both
under `` `ifdef COCOTB_SIM ``, unconditional (no runtime gate) — placed in the *same*
existing initial block immediately before `run_test()`, rather than quasar's separate
clock-synced initial block with a runtime `if (cocotb_active)` gate. This matches the
brief's explicit simplification ("mirror quasar's placement, minus the runtime gate").

### Step 3 — file wiring (exact insertion points)
- **Package**: created `dv/uvm/core_ibex/common/ibex_cocotb/core_ibex_cocotb_pkg.sv`,
  mirroring the `common/irq_agent/irq_agent_pkg.sv` shape (`import uvm_pkg::*;` +
  `` `include `` of the class file). Its content is unconditional (no ifdef) — when
  `COCOTB_SIM` is undefined, the `` `include ``'d monitor file preprocesses to nothing, so
  the package still compiles, just empty. This is the "files may be unconditionally
  listed... contents compile away" pattern from the Global Constraints, applied one level
  up (the package file, not just the interface/monitor files, stays unconditional).
- **`ibex_dv.f`**:
  - `+incdir+${PRJ_DIR}/dv/uvm/core_ibex/common/ibex_cocotb` added to the incdir block
    (next to `ibex_cosim_agent`), so the package's `` `include "core_ibex_cocotb_monitor.sv"``
    resolves.
  - `${PRJ_DIR}/dv/uvm/core_ibex/tb/core_ibex_cocotb_if.sv` inserted **after the existing
    interfaces** (right after `core_ibex_csr_if.sv`, before `core_ibex_env_pkg.sv`) —
    despite living in `tb/`, it must compile early because the monitor package references
    `virtual core_ibex_cocotb_if`.
  - `${PRJ_DIR}/dv/uvm/core_ibex/common/ibex_cocotb/core_ibex_cocotb_pkg.sv` inserted
    **right before `core_ibex_test_pkg.sv`** (after `core_ibex_env_pkg.sv`), i.e. "where
    other test-support classes are compiled" — `core_ibex_test_pkg.sv` imports it.
  - Compile-order proof: the ifdef-on log (Step 4) shows `core_ibex_cocotb_if` parsed
    right after `core_ibex_csr_if.sv`/before `core_ibex_env_pkg.sv`, and
    `core_ibex_cocotb_pkg.sv` parsed right after `core_ibex_env_pkg.sv`/before
    `core_ibex_test_pkg.sv` — matching the intended order.
- **`core_ibex_test_pkg.sv`**: added `` `ifdef COCOTB_SIM import core_ibex_cocotb_pkg::*;
  `endif `` alongside the package's other agent-pkg imports, so `core_ibex_base_test.sv`
  (also `` `include ``d into this package) can name `core_ibex_cocotb_monitor` unqualified.
- **`core_ibex_base_test.sv`**: added a `` `ifdef COCOTB_SIM `` field
  `core_ibex_cocotb_monitor cocotb_monitor;` and, in `build_phase` right after `vseq` is
  built, `cocotb_monitor = core_ibex_cocotb_monitor::type_id::create("cocotb_monitor",
  this);` under the same ifdef. The monitor runs its own `run_phase`/`final_phase`
  automatically once created (standard UVM phasing) — no other test-side wiring needed.
- **`core_ibex_tb_top.sv`**: interface instantiated under ifdef right after the other
  `core_ibex_*_if` instances (before the ISA-config `` `define `` block, not disturbing the
  WS1 `TB-CONFIG:` banner); config_db set + `finish_on_completion = 0` added under ifdef
  immediately before `run_test()` in the existing initial block.

### Step 4 — compile-only green, both ways
Ran (subshell discipline, `source ci/env.sh` first for `pathlib3x`/venv deps):
```
( cd dv/uvm/core_ibex && make GOAL=rtl_tb_compile SIMULATOR=vcs IBEX_CONFIG=opentitan OUT=out_cctbchk )
```
**Stock (COCOTB_SIM undefined)**: compiled clean, `vcs_simv` produced, "All of 104 modules
done". `grep -o COCOTB <(grep '^vcs -full64' compile_tb_stdstreams.log) | wc -l` → **0** —
the actual vcs command line carries no `COCOTB` artifact. (A whole-log case-insensitive
grep for "cocotb" does hit 6 lines, but those are just the new *filenames* being parsed/
recompiled, e.g. `Parsing design file '.../core_ibex_cocotb_if.sv'` — expected, since
Global Constraints explicitly allow unconditionally listing the files in `ibex_dv.f`.)

**ifdef-on**: no clean pre-Task-4 knob exists yet (Task 4 owns `COCOTB=1`), so per the
brief I injected `+define+COCOTB_SIM` directly into
`dv/uvm/core_ibex/yaml/rtl_simulation.yaml`'s vcs compile `cmd:` (one line, after
`+define+FCOV_NO_DEFAULT_SEQUENCE`), ran the same compile into a second fresh OUT
(`out_cctbchk_on`), then reverted the yaml file. Diff used for the check:
```diff
           +define+FCOV_NO_DEFAULT_SEQUENCE
+          +define+COCOTB_SIM
           -timescale=1ns/10ps
```
Result: compiled clean, `vcs_simv` produced, "All of 105 modules done" (one more than
stock — the interface now elaborates as a real module instead of an empty shell), the vcs
command line shows `+define+COCOTB_SIM`, zero `Error`/`fatal` lines, and the log confirms
`core_ibex_cocotb_if` and `core_ibex_cocotb_pkg` (which now really includes the monitor)
recompiled with no warnings attributed to either file. This proves the interface, the
monitor, the tb_top instantiation/config_db/finish_on_completion, the base_test creation,
and the test_pkg import all elaborate correctly together.
Reverted the yaml file: `git checkout -- dv/uvm/core_ibex/yaml/rtl_simulation.yaml`,
confirmed via `git diff`/`git status` that it's back to the committed state (no residual
diff).

### Step 5
Removed `out_cctbchk` and `out_cctbchk_on`. Committed.

## Files changed
- `dv/uvm/core_ibex/tb/core_ibex_cocotb_if.sv` (new)
- `dv/uvm/core_ibex/common/ibex_cocotb/core_ibex_cocotb_monitor.sv` (new)
- `dv/uvm/core_ibex/common/ibex_cocotb/core_ibex_cocotb_pkg.sv` (new)
- `dv/uvm/core_ibex/ibex_dv.f`: `+incdir` for `common/ibex_cocotb`; file-list entries for
  the interface and the new package, at the insertion points described above
- `dv/uvm/core_ibex/tb/core_ibex_tb_top.sv`: interface instance + config_db set +
  `finish_on_completion = 0`, all under `` `ifdef COCOTB_SIM ``
- `dv/uvm/core_ibex/tests/core_ibex_test_pkg.sv`: `` `ifdef ``-guarded import of
  `core_ibex_cocotb_pkg`
- `dv/uvm/core_ibex/tests/core_ibex_base_test.sv`: `` `ifdef ``-guarded
  `cocotb_monitor` field + creation

## Concerns
- No `COCOTB_MODULE`/plusarg knob exists yet, so this task's ifdef-on proof is
  compile-only (as the brief anticipated) — Task 4 owns turning this on via the real
  `COCOTB=1` flow knob, and Task 5 is the first place the handshake actually runs a
  simulation end to end.
- `uvm_ready` is declared but unused by anything in this task (Task 7 arms it) — flagged
  in-file so it's not mistaken for dead code later. **Accepted as disclosed by review; no
  action.**
- `run_phase`'s three sequential `wait` statements assume cocotb drives
  `cctb_alive`→`cocotb_active`→`!cocotb_active` monotonically once per test; if a future
  Python test needs to go active/inactive more than once per sim, the monitor would need a
  loop. Not needed for Milestone A/B as specified, so left as the brief's literal
  race-free sequence. **Accepted as disclosed by review; no action.**

## Fix round 1 (review finding)

**Finding [Critical]**: `core_ibex_cocotb_pkg.sv`'s package shell was unconditional —
every stock build compiled a real (empty) `core_ibex_cocotb_pkg`, violating "ALL new SV
content compiles away when the define is absent." (The two Minors above — `uvm_ready`
scaffolding and the single-pass handshake — were accepted as disclosed; no action taken
on those.)

**Fix**: wrapped the entire file body (`package...endpackage`, including the
`import`/`` `include ``s) in `` `ifdef COCOTB_SIM ``/`` `endif ``, matching
`core_ibex_cocotb_if.sv`/`core_ibex_cocotb_monitor.sv`:
```diff
 // Packages core_ibex_cocotb_monitor for import into core_ibex_test_pkg, mirroring how the other
-// common/ agents (e.g. irq_agent_pkg) package their classes.
+// common/ agents (e.g. irq_agent_pkg) package their classes. Entire body compiles away when
+// COCOTB_SIM is undefined, matching core_ibex_cocotb_if/core_ibex_cocotb_monitor.
+`ifdef COCOTB_SIM
+
 package core_ibex_cocotb_pkg;
 
   import uvm_pkg::*;
@@
   `include "core_ibex_cocotb_monitor.sv"
 
 endpackage
+
+`endif // COCOTB_SIM
```
No change needed to `core_ibex_test_pkg.sv`'s import — it was already
`` `ifdef COCOTB_SIM ``-guarded.

**Re-verification**:
- Fresh-OUT stock compile (`OUT=out_fix2`): compiled clean (`vcs_simv` produced, zero
  `Error`/`fatal` lines). Exact greps run against
  `out_fix2/build/tb/compile_tb_stdstreams.log`:
  - `grep -n "recompiling.*cocotb" compile_tb_stdstreams.log` → **no matches** (before the
    fix this showed `recompiling package core_ibex_cocotb_pkg`) — the package symbol is
    gone from elaboration, not just empty.
  - Module count dropped from **104 → 103** modules elaborated vs. the pre-fix stock
    build, confirming the package no longer exists as a compiled unit at all (previously
    the empty package still counted as one).
  - The filename still appears via `Parsing design file
    '.../core_ibex_cocotb_pkg.sv'` (line 787) — expected and fine, since Global
    Constraints explicitly allow unconditionally listing the file in `ibex_dv.f`; only the
    post-preprocessor *symbol* had to disappear, and it did.
  - vcs command line: `grep -o COCOTB <(grep "^vcs -full64" compile_tb_stdstreams.log) |
    wc -l` → **0**, unchanged from before.
- ifdef-on re-check: re-injected `+define+COCOTB_SIM` into
  `dv/uvm/core_ibex/yaml/rtl_simulation.yaml` (same one-line diff as the original Step 4),
  compiled into a fresh `OUT=out_fix2_on`: clean compile, `+define+COCOTB_SIM` present on
  the vcs command line, `recompiling module core_ibex_cocotb_if` and `recompiling package
  core_ibex_cocotb_pkg` both present (105 modules, matching the original ifdef-on run),
  zero errors. Confirms the now fully-guarded package still compiles and elaborates
  correctly when the define is on.
- Reverted the yaml injection again (`git checkout --
  dv/uvm/core_ibex/yaml/rtl_simulation.yaml`), confirmed clean via `git diff`/`git
  status`. Removed `out_fix2` and `out_fix2_on`.

**Contract**: with `COCOTB_SIM` undefined, `core_ibex_cocotb_pkg` no longer exists as an
elaborated package (was previously an empty-but-real package) — stock builds now carry
zero cocotb SV content of any kind, only the unconditionally-listed filenames on the vcs
parse trace, per the Global Constraints' explicit allowance.
