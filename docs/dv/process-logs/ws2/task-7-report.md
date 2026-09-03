# Task 7 Report: Milestone B — Python-driven irq stimulus through the UVM irq agent

## Status: DONE (all steps green; two real bugs found and fixed along the way)

## Design notes (as requested)

### Why the handler-entry counter counts ENTRIES, not line toggles

The observation point is `controller_state == ibex_pkg::IRQ_TAKEN`, sampled on `posedge clk` in
`core_ibex_tb_top.sv` (a new `always_ff` block right after the file's existing, pre-existing
sanity check that already watches the same state:
`if (controller_state == ibex_pkg::IRQ_TAKEN) ... WARNING: Controller in IRQ_TAKEN but no IRQ to
handle`). `controller_state` is itself an existing top-level wire
(`dut.u_ibex_top.u_ibex_core.id_stage_i.controller_i.ctrl_fsm_cs`), so no new hierarchical probe
was needed.

`IRQ_TAKEN` is entered from `DECODE` only when the controller's `handle_irq` combinational signal
was true (i.e. an actual enabled, unmasked interrupt was pending) and unconditionally returns to
`DECODE` the very next cycle (`rtl/ibex_controller.sv`: `ctrl_fsm_ns = DECODE;` sits outside the
`if (handle_irq)` guard at the end of the `IRQ_TAKEN` case), so it is guaranteed to be a
single-cycle pulse per interrupt actually taken — never a multi-cycle level. This is the RTL's own
definition of "the CPU is redirecting to the interrupt handler": `ibex_core.sv`'s `rvfi_intr`
plumbing uses the identical condition (`pc_set && pc_mux_id == PC_EXC && exc_pc_mux_id ==
EXC_PC_IRQ`) to mark "PC is set to enter a trap handler".

Counting raw `irq_vif` line toggles instead would be wrong for two independent reasons: (1) a
raise doesn't imply the CPU ever took it — if the source is masked (`mie`) or globally disabled
(`mstatus.MIE`) at that moment, the line can toggle with zero handler entries; (2) since Ibex
interrupts are level-sensitive, a single raise-then-drop line transition pair doesn't have a fixed
1:1 relationship with entries in general (a held level can, in principle, cause repeated entries
across multiple `mret`s). `IRQ_TAKEN` sidesteps both: it only pulses when the core actually
committed to redirecting to the handler.

### Raise/drop pulse timing

`core_ibex_base_test.sv`'s `cocotb_irq_listener()` holds the raise for
`CocotbIrqHoldCycles = 100` cycles before dropping:
- **Long enough**: `handle_irq` is re-evaluated by the controller every cycle it's in `DECODE`, so
  100 cycles is generous margin for the core to notice and start taking the interrupt, well beyond
  worst-case multi-cycle-instruction stalls in a `+enable_interrupt=1` random-instruction program.
- **Short enough**: it must be *dropped* well before the ISR reaches `mret` — since interrupts are
  level-sensitive, a still-asserted line at the point `mret` re-enables `mstatus.MIE` would
  immediately retake it, turning one Python trigger into an uncontrolled retrigger storm. A
  generated riscv-dv interrupt handler takes on the order of tens–hundreds of cycles to run; 100
  cycles is comfortably inside that window.
- Each pulse fully returns the irq lines to 0 (via a fresh `irq_drop_seq`-derived sequence) before
  the listener goes back to `raise_ev.wait_trigger()`, so the *next* trigger is always a clean 0→1
  edge — a level held from one trigger into the next wouldn't represent a distinguishable event to
  attribute a fresh entry to.

The irq line raised is deterministically `irq_external` only (`cocotb_irq_raise_seq`,
`core_ibex_seq_lib.sv`) — not randomized like the stock `irq_raise_single_seq` — so every trigger
exercises the same, always-enabled-by-`+enable_interrupt=1` MEIE path rather than risking an NMI
or fast-interrupt line the generated handler may not gracefully service.

### Armed-listener + `uvm_ready` ordering (no lost triggers)

`cocotb_irq_listener()` is the *first* branch listed in `run_phase`'s `fork` (ahead of
`send_stimulus()`/`handle_reset()`), so its two zero-delay statements — get the
`uvm_event_pool::get_global("cocotb_irq_raise")` handle, then set `cocotb_vif.uvm_ready = 1'b1`
— execute before any other forked branch has run even one blocking statement (VCS runs a fork
statement's branches in listed order up to each branch's first blocking point before advancing
simulation time). Python's `test_irq_from_python.py` polls `cocotb_if.uvm_ready` before its first
`uvm_bridge.trigger()` call. Since the listener is already inside its `forever begin
raise_ev.wait_trigger(); ... end` loop by the time `uvm_ready` is visible to Python, there is no
window where a trigger could arrive before a listener exists to consume it, and no window where
the listener could miss an event because it wasn't listening yet.

## Steps

### Step 1 — testlist entry, DPI export, listener, counter

- **Testlist** (`riscv_dv_extension/testlist.yaml`): new `cocotb_irq_python_test` entry.
  `gen_test: riscv_rand_instr_test`, `gen_opts` include `+enable_interrupt=1 +enable_timer_irq=1`
  (following the existing irq-test entries at the `testlist.yaml:444`-region) so the generated
  program sets up `mtvec`/`mie`/`mstatus` and a working trap handler. `rtl_test:
  core_ibex_base_test` (the plain base test) and `sim_opts` carry only
  `+require_signature_addr=1 +cocotb_irq_count=3` — deliberately **no** `+enable_irq_single_seq`/
  `+enable_irq_multiple_seq`/`+enable_irq_nmi_seq`, so `core_ibex_vseq.body()` never creates or
  starts any stock irq sequence; the entry's description documents this explicitly.
- **DPI export** (`dv/uvm/core_ibex/tb/core_ibex_cocotb_dpi.svh`, new): `` `ifdef COCOTB_SIM ``-only
  file `` `include ``d directly into `core_ibex_tb_top`'s module body (a new
  `+incdir+${PRJ_DIR}/dv/uvm/core_ibex/tb` line added to `ibex_dv.f` so the include resolves —
  the file isn't a standalone compile unit). It declares
  `task automatic cocotb_trigger_uvm_event(input string ev_name)` (body: `uvm_event_pool::
  get_global(ev_name).trigger()`) and `export "DPI-C" task cocotb_trigger_uvm_event;`. Living
  directly in `core_ibex_tb_top`'s own scope (not inside `cocotb_if` or a nested instance) is what
  makes the DPI scope name exactly `"core_ibex_tb_top"` — the value `uvm_bridge.py` targets via
  `svSetScope(svGetScopeFromName(...))`.
- **Interface** (`core_ibex_cocotb_if.sv`): added `int unsigned handler_entry_count;` (no
  initializer — VCS's `ICPD_INIT` check flags an interface-level initializer as a second driver
  once an `always_ff` elsewhere also drives it; caught and fixed during the first compile
  attempt). `uvm_ready` already existed from Task 2 and needed no interface change, only an
  external writer.
- **Counter** (`core_ibex_tb_top.sv`): new `` `ifdef COCOTB_SIM ``-guarded `always_ff` right after
  the pre-existing `IRQ_TAKEN` sanity-check block, incrementing `cocotb_if.handler_entry_count` on
  `controller_state == ibex_pkg::IRQ_TAKEN` (see design note above), reset to 0 on `!rst_n`.
- **Listener** (`core_ibex_base_test.sv`): `cocotb_vif` fetched via `uvm_config_db` in
  `build_phase` (same `"cocotb_if"` key `core_ibex_cocotb_monitor` already uses, set globally by
  `tb_top`). New `cocotb_irq_listener()` task (armed-listener + `uvm_ready` + raise/drop loop,
  see design notes) forked first in `run_phase`.
- **Sequences**: `core_ibex_vseq.sv` gained `start_cocotb_irq_raise()`/`start_cocotb_irq_drop()`,
  each creating a *fresh* sequence object per call (not the `cfg.enable_irq_*_seq`-gated handles
  used by `body()`) and starting it on `p_sequencer.irq_seqr`. `core_ibex_seq_lib.sv` gained the
  new deterministic `cocotb_irq_raise_seq` class (`irq_external==1`, everything else 0); the
  existing `irq_drop_seq` is reused as-is for the drop half.

### Step 2 — `uvm_bridge.py` and the test

- `dv/cocotb/common/uvm_bridge.py` (new): hand-written minimal version of the quasar
  `qsr_tb_dpi.py` pattern — `ctypes.CDLL(None, mode=ctypes.RTLD_GLOBAL)` then `ctypes.CDLL(None)`
  to get the process's own symbol table (simv's DPI/VPI runtime plus the generated C stub for our
  exported task are already linked in), binds `svGetScopeFromName`/`svSetScope`/
  `cocotb_trigger_uvm_event`, and exposes `trigger(ev_name)`: `svSetScope(svGetScopeFromName(
  b"core_ibex_tb_top"))` then call the exported task with the UTF-8-encoded event name.
- `dv/cocotb/tests/test_irq_from_python.py` (new): `await start(dut)`; poll `cocotb_if.uvm_ready`
  before the first trigger; read `n = int(cocotb.plusargs.get("cocotb_irq_count", "3"))`; loop `n`
  times waiting a `RANDOM_SEED`-seeded gap (`_BASE_GAP_CYCLES=3000` + jitter up to 2000 cycles,
  generous margin for the generated program's early mie/mstatus setup and each ISR's completion)
  then `uvm_bridge.trigger("cocotb_irq_raise")`; wait a short settle (`500` cycles) for the last
  pulse to be serviced; check `handler_entry_count >= _MIN_EXPECTED_HANDLER_ENTRIES` (fixed at 3,
  intentionally *not* read from the same plusarg — see Step 4); only then `await finish(dut,
  timeout_ms=30)`. See "Bug 2" below for why the check happens before `finish()`, not after.
- `dv/cocotb/common/handshake.py` (modified): `finish()` gained an optional `timeout_ms=2`
  parameter (default preserves Milestone A's exact behavior/contract — `test_hello.py`'s call is
  unchanged); this test passes `timeout_ms=30` since its heavier `+instr_cnt=10000`
  interrupt-handling program takes noticeably longer to reach its own riscv-dv signature handshake
  than Milestone A's bare hello-world program did (see "Bug 1" below).

### Step 3 — run it (green)

```
( cd dv/uvm/core_ibex && make SIMULATOR=vcs IBEX_CONFIG=opentitan ISS=spike \
  TEST=cocotb_irq_python_test ITERATIONS=1 SEED=1 COCOTB=1 \
  COCOTB_MODULE=dv.cocotb.tests.test_irq_from_python OUT=out_mb )
```
PASS: `100.00% PASS 1 PASSED, 0 FAILED`, `cocotb_irq_python_test.1: PASS`. All 3 triggers produced
exactly 3 handler entries (`handler_entry_count=3 (triggered=3, required>=3)`), zero
`WARNING: Controller in IRQ_TAKEN` lines, zero `UVM_ERROR`/`UVM_FATAL`, and
`Co-simulation matched 14833 instructions` (cosim clean — irq stimulus goes through the same
`irq_vif` the cosim step function reads, so RTL and spike see identical inputs and stay in
lockstep). Full log + regr.log: `docs/dv/evidence/ws2-milestone-b.log`.

Two real bugs were found and fixed while getting here (both triage-loop findings, not deviations
from the design above):

**Bug 1 — `finish()`'s inherited 2ms poll timeout was too short for this program.** First attempt
timed out: `TimeoutError: uvm_finished did not assert within 2ms timeout`. Root-caused via the
RTL execution trace: the core was still actively retiring instructions in lockstep with spike
right up to the timeout (last trace entry at ~2245.48us vs. a 2245.54us cutoff — a ~60ns/3-cycle
gap, i.e. still running, not hung), zero `UVM_ERROR`s, zero `IRQ_TAKEN` warnings. Milestone A's own
evidence log independently confirms the underlying cause: its bare hello-world program (same
`+instr_cnt=10000`, no interrupts) already took 1.668ms to reach its natural riscv-dv signature
handshake; this test's heavier `riscv_rand_instr_test` program plus 3 interrupt round-trips needs
more than the 2ms budget `handshake.finish()` was hardcoded to from Milestone A. Fixed by making
the timeout a parameter (default 2ms, preserving Milestone A's contract) and passing `30` from
this test. Re-run: full natural completion at 2.82ms, well inside the new budget.

**Bug 2 — an em-dash in the assertion message silently broke the negative control** (found and
fixed during Step 4; full detail there).

### Step 4 — negative control (mutation-style, named-checker ablation)

Fresh OUT, testlist's `cocotb_irq_python_test` sim_opts temporarily edited from
`+cocotb_irq_count=3` to `+cocotb_irq_count=0` (reverted immediately after capture via re-edit;
confirmed back to the committed `=3` state before the final evidence run and before this commit —
never committed in the `=0` state). `_MIN_EXPECTED_HANDLER_ENTRIES` in the test stays a fixed `3`,
independent of the plusarg, specifically so this ablation exercises the checker (`0 >= 3` is
false) instead of trivially degenerating to `0 >= 0`.

**First attempt: false PASS, and a real bug found.** With zero triggers, `handler_entry_count`
correctly stayed 0 and the assertion correctly raised `AssertionError`, but the flow's regr.log
still reported `100.00% PASS 1 PASSED, 0 FAILED` — the check's own failure evidence never made it
into the log. Root cause: the assertion message contained an em-dash (`—`, U+2014); cocotb's
`_log_test_failed` writes through a `logging.StreamHandler` backed by an ASCII-only stream in this
environment, so emitting that message raised `UnicodeEncodeError`, and cocotb's own error-handling
for a logging failure just prints `--- Logging error ---` instead of the real message — silently
swallowing the exact text (`AssertionError: ...`) the flow's log scanner
(`ibex_log_to_trace_csv.check_ibex_uvm_log`) needed to see. Fixed by keeping every
runtime-logged/raised string in `dv/cocotb/` plain ASCII (the assertion message and one similarly
affected `RuntimeError` in `uvm_bridge.py`; comments/docstrings, never logged, were left as-is).

**Second attempt (after the em-dash fix): still a false PASS, and a second, more fundamental bug
found.** The clean `AssertionError:` traceback now appeared in the log exactly as expected, and
cocotb itself correctly reported `test_irq_from_python failed` — but the flow-level verdict was
*still* `100.00% PASS`. Root cause, found by reading `ibex_log_to_trace_csv.check_ibex_uvm_log`
directly: it stops treating `'Error'`-containing lines as failures once it has already seen
`'RISC-V UVM TEST PASSED'` in the log (`... and not test_result_seen`), specifically to avoid
false failures from the UVM report summary's own `UVM_ERROR :    0` line. The original design
(brief's Step 2 order: trigger, `await finish()`, *then* assert) checks the counter only after
`finish()` returns — which only happens after the whole generated program has already reached its
natural riscv-dv signature handshake and printed that exact banner. So a real check failure placed
after `finish()` can *never* fail the flow, regardless of what it asserts — this is the same
"post-report window" class of hazard flagged for DUT SVAs in the brief's Milestone-A hazards,
just hitting our own Python-side check instead. Fixed by moving the check (log + assert) to run
right after the trigger loop (plus the 500-cycle settle already needed for the last pulse), before
`finish()` is ever called — which always lands chronologically before that banner. As a bonus,
on a real failure this ordering means cocotb's own uncaught-exception handling `$finish`es
immediately, so the banner never prints in a failing run at all, removing any doubt.

**Final result (both fixes in place):** `AssertionError: COCOTB-IRQ-CHECK: handler_entry_count=0
is below the required 3 (triggered 0 times); irq stimulus was not serviced`, flow-level
`0.00% PASS 0 PASSED, 1 FAILED`, `cocotb_irq_python_test.1: FAILED`, `trr.yaml` `failure_mode:
LOG_ERROR(3)`, `make` exit code `2`. Confirms this check — not cosim, not a generic UVM_ERROR —
is what fires. Positive run re-verified afterward (fresh OUT, `+cocotb_irq_count=3` restored) to
confirm the reordering didn't regress the passing case: identical `handler_entry_count=3` result,
checked at ~255us, well before the natural `RISC-V UVM TEST PASSED` banner at ~2.76ms. Full
excerpts in `docs/dv/evidence/ws2-milestone-b.log`; the negative run's own OUT tree was never
committed.

### Step 5 — evidence and commit

`docs/dv/evidence/ws2-milestone-b.log` written (full sim log, regr.log, negative-control excerpt,
design summary). Commit: `[dv] WS2 Milestone B: python-driven irq stimulus through UVM irq agent`.

## Files changed

- New: `dv/uvm/core_ibex/tb/core_ibex_cocotb_dpi.svh`
- New: `dv/cocotb/common/uvm_bridge.py`
- New: `dv/cocotb/tests/test_irq_from_python.py`
- New: `docs/dv/evidence/ws2-milestone-b.log`
- Modified: `dv/uvm/core_ibex/tb/core_ibex_cocotb_if.sv` (`handler_entry_count` field)
- Modified: `dv/uvm/core_ibex/tb/core_ibex_tb_top.sv` (DPI `` `include ``, counter `always_ff`)
- Modified: `dv/uvm/core_ibex/tests/core_ibex_base_test.sv` (`cocotb_vif`, `cocotb_irq_listener`)
- Modified: `dv/uvm/core_ibex/tests/core_ibex_vseq.sv` (`start_cocotb_irq_raise`/`_drop`)
- Modified: `dv/uvm/core_ibex/tests/core_ibex_seq_lib.sv` (`cocotb_irq_raise_seq`)
- Modified: `dv/uvm/core_ibex/riscv_dv_extension/testlist.yaml` (`cocotb_irq_python_test` entry)
- Modified: `dv/uvm/core_ibex/ibex_dv.f` (`+incdir` for `tb/`)
- Modified: `dv/cocotb/common/handshake.py` (`finish(dut, timeout_ms=2)`)

## Concerns

1. `CocotbIrqHoldCycles = 100` and the Python gap constants (`_BASE_GAP_CYCLES=3000`,
   `_JITTER_MAX_CYCLES=2000`, `_POST_TRIGGER_SETTLE_CYCLES=500`) are reasoned-about but empirically
   tuned against exactly one seed (`SEED=1`) and one gen_test (`riscv_rand_instr_test`). They
   worked cleanly (zero `IRQ_TAKEN` warnings, exact 1:1 trigger-to-entry correspondence) for this
   seed; a different seed's random instruction mix or interrupt-enable timing could in principle
   need a larger settle/gap, though the design (level-sensitive, no forced synchronization point
   between Python and instruction execution) is meant to be robust to reasonable variation. Not
   swept across multiple seeds given time constraints.
2. `finish()`'s `timeout_ms` default (2ms) is unchanged for Milestone A compatibility, but any
   *future* cocotb test with a heavier generated program will hit the same Bug-1 timeout unless it
   remembers to pass a larger value explicitly — nothing enforces or auto-scales this. Worth a
   `TB_CONTRACT.md` callout (Task 8) that `timeout_ms` exists and why.
3. The "post-report assertion window" class of hazard (Bug 2's second half) is now known to apply
   to *any* cocotb-side check performed after `finish()`/`uvm_finished`, not just this test. Future
   cocotb checkers should assert before calling `finish()`, or the flow's log scanner would need to
   stop suppressing `'Error'` lines after `test_result_seen` — the former is the lower-risk fix and
   is what this task does; the latter is a shared-script change out of this task's scope.

## Commits
(see `git log` — testlist.yaml, SV, and Python changes plus the evidence log, one commit per the
brief's Step 5 message)

---

## Fix round 1 (review response)

Review found 3 Important findings against this task's first pass, all confirmed correct.

### Finding 1 — vacuous-pass hazard when COCOTB=0

In a default regression (`TEST=all`/no `COCOTB`), `cocotb_irq_python_test` would run as a plain
`riscv_rand_instr_test` under `core_ibex_base_test` and pass, with nothing in the flow signaling
that its named python-irq coverage never happened.

**Fix (a):** `core_ibex_base_test.sv`'s `build_phase` gained an `` `else `` branch alongside the
existing `` `ifdef COCOTB_SIM `` block: when `COCOTB_SIM` is not compiled in, it reads the
`+cocotb_irq_count` plusarg via `$value$plusargs` and `` `uvm_fatal ``s if it's present ("cocotb_irq_count
plusarg seen but COCOTB_SIM not compiled in -- this test requires COCOTB=1"). Verified: fresh OUT,
`COCOTB=0`, same test — `UVM_FATAL` fires at simulation time 0 (before any generated code runs),
`regr.log`: `0.00% PASS 0 PASSED, 1 FAILED` / `FAILED`, `make` exit code `2`.

**Fix (b):** `testlist.yaml`'s `cocotb_irq_python_test` entry: `iterations: 10` → `iterations: 1`,
with a note in the description explaining why (this test's timing constants were tuned and
verified against `SEED=1` only; a 10-seed sweep with `+randomize_csr=1` risks an untuned timing
corner false-failing).

### Finding 2 — "no lost events" was overstated

`uvm_event.trigger()` is not queued: a trigger arriving while the listener is still inside a
previous raise/drop pulse (not back at `wait_trigger()`) is silently dropped. The `uvm_ready`
handshake only closes the *startup* race (listener not yet armed vs. the very first trigger); it
says nothing about a trigger landing during an in-progress pulse. Prose claiming "no event is
lost" was wrong to generalize.

**Fix:** added `trigger_received_count` to `core_ibex_cocotb_if.sv` (parallel to
`handler_entry_count`, no initializer needed — it's a 2-state `int unsigned`, and only one
procedural writer drives it, so no `ICPD_INIT` conflict). `core_ibex_base_test.sv`'s
`cocotb_irq_listener()` increments it every time `wait_trigger()` actually returns. Python
(`test_irq_from_python.py`) tracks its own `triggers_sent` counter and asserts
`triggers_sent == triggers_received` right after the trigger loop, before `finish()` (same
before-finish placement as the handler-entry check, for the same log-scanner-window reason).
Corrected the overclaiming comments in `core_ibex_cocotb_if.sv` and `test_irq_from_python.py` to
state the real invariant: `uvm_ready` closes the startup race only; the trigger-accounting check
is what catches a mid-pulse drop.

Verified both directions: positive run (3 triggers) shows `triggers_sent=3 triggers_received=3`;
negative-control run (0 triggers) shows `triggers_sent=0 triggers_received=0` — the accounting
check itself stays green when there's genuinely nothing to drop, so it doesn't interfere with the
Finding-3 ablation below.

### Finding 3 — 1:1 correspondence unenforced

The original `handler_entry_count >= 3` fixed floor would pass silently even if a pulse somehow
produced more than one entry per trigger (e.g. a future timing regression causing a retrigger),
since 3 actual triggers producing, say, 5 entries still satisfies `>= 3` with no visibility into
the mismatch.

**Fix:** the assertion now requires `handler_entry_count >= max(n, _MIN_EXPECTED_HANDLER_ENTRIES)`
— `_MIN_EXPECTED_HANDLER_ENTRIES` stays a fixed floor of 3 (so the `+cocotb_irq_count=0` ablation
still fails: `max(0, 3) = 3`, `0 >= 3` is false), but for `n > 3` the check now tightens to require
at least as many entries as triggers actually sent, rather than being permanently satisfied once
`n` reaches the floor. Separately, if `handler_entry_count > triggers_sent` (over-counting,
attributable to no specific trigger), `test_irq_from_python.py` logs a loud
`cocotb.log.warning(...)` (plain ASCII, distinct `COCOTB-IRQ-CHECK` prefix) — informational only,
does not fail the test, but makes an over-count visible and attributable rather than silently
absorbed into a passing `>=` comparison. Verified the warning does *not* fire in the normal
3-trigger/3-entry case (no spurious noise) — re-triggering it would need a deliberate
over-count-mutation run, which wasn't done here (out of this fix round's scope; the code path was
inspected directly instead: the log call is unconditional on `count > triggers_sent`, no reason to
doubt it fires when that condition holds).

### Style fix

Trimmed the 11-line "checked before finish()" rationale comment in `test_irq_from_python.py` down
to 2 intent lines (full rationale lives in this report / TB_CONTRACT.md), per the user's global
comment-conciseness rule.

### Deferred (per review instruction, not touched)

Evidence-log header `OUT=out_mb` vs. the internal log paths showing `out_mb_final` (a leftover
from an earlier rerun during the original triage loop); the double `ctypes.CDLL(None, ...)` call
in `uvm_bridge.py`; the `run_phase` fork-listing-order comment wording; remaining em-dashes in
comments (not runtime-logged/raised strings, so no crash risk); the spurious-`IRQ_TAKEN` warning
caveat. All ledgered by the reviewer as separate, deferred items.

### Re-verification summary

All three fixes verified end-to-end in fresh, uncommitted OUTs (excerpts in
`docs/dv/evidence/ws2-milestone-b.log`'s "Fix round 1" appendix):
- Positive run (`+cocotb_irq_count=3`, committed state): PASS, `triggers_sent=3
  triggers_received=3`, `handler_entry_count=3 (required>=3)`, zero warnings/errors.
- Negative control (`+cocotb_irq_count=0`, temporary): FAILED, `triggers_sent=0
  triggers_received=0` (accounting check itself green), `handler_entry_count=0` fails the fixed
  floor, `LOG_ERROR(3)`, `make` exit 2.
- `COCOTB=0` vacuous-pass guard (new): `UVM_FATAL` at time 0, `FAILED`, `make` exit 2.

testlist.yaml restored to the committed `+cocotb_irq_count=3` / `iterations: 1` state before this
commit; no `out*/` trees or `results.xml` committed.

## Files changed (fix round 1, in addition to the original list above)
- Modified: `dv/uvm/core_ibex/tb/core_ibex_cocotb_if.sv` (`trigger_received_count` field, comment
  corrections)
- Modified: `dv/uvm/core_ibex/tests/core_ibex_base_test.sv` (COCOTB=0 `uvm_fatal` guard,
  `trigger_received_count` increment)
- Modified: `dv/cocotb/tests/test_irq_from_python.py` (trigger accounting assert, `max(n, floor)`,
  over-count warning, comment trim/correction)
- Modified: `dv/uvm/core_ibex/riscv_dv_extension/testlist.yaml` (`iterations: 1` + rationale)
- Modified: `docs/dv/evidence/ws2-milestone-b.log` (appended re-verification section)
