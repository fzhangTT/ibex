# WS2 final fix wave — report

Branch: `fzhang/auto-dv-setup` (confirmed via `git branch --show-current` before starting).
Fixes exactly the 7 findings from the WS2 final whole-branch review (ruling recorded in
`progress.md`). No other changes made.

## 1. [Critical] Dangling `.superpowers/sdd/` evidence-chain references — FIXED

`.superpowers/sdd/` is entirely gitignored (`.superpowers/sdd/.gitignore` has a blanket `*`
pattern, confirmed via `git check-ignore`), so any doc citing a path under it can never resolve
in the committed tree.

- Copied `progress.md` and `task-1-report.md` .. `task-8-report.md` from
  `.superpowers/sdd/2026-09-01-ws2-cocotb/` to `docs/dv/process-logs/ws2/` (matching the ws1/ws3
  convention: reports + progress log only, no briefs, no review diffs).
- Repointed all 6 dangling citations to the new committed path:
  - `docs/dv/BUILD_AND_SIM.md:181,210` (`task-5-report.md`) and `:236` (`task-4-report.md`).
  - `docs/dv/evidence/ws2-hello.log:27` ("Task 5 report" -> explicit path).
  - `docs/dv/evidence/ws2-milestone-b.log:89,253` ("Task 7 report" / bare `task-7-report.md` ->
    explicit `docs/dv/process-logs/ws2/` path).

## 2. [Important] TB_CONTRACT.md Section 3 — FIXED

- Fixed the documented `trigger()` parameter name from `event_name` to `ev_name`, matching
  `dv/cocotb/common/uvm_bridge.py`'s actual signature (`def trigger(ev_name: str) -> None`).
- Added the available event name: `"cocotb_irq_raise"` — one `trigger()` call drives one full
  raise/drop pulse (the TB side owns both edges; confirmed by reading
  `core_ibex_base_test.sv`'s `cocotb_irq_listener()`, which triggers `start_cocotb_irq_raise()`,
  holds, then `start_cocotb_irq_drop()` itself — the Python side never triggers a separate drop).

## 3. [Important] em-dash in `core_ibex_cocotb_if.sv:44` — FIXED

Replaced the U+2014 em-dash in the `$fatal` message with ASCII `--`. Grepped the whole file
(`LC_ALL=C grep -P '[^\x00-\x7F]'`) plus the rest of the cocotb-adjacent surface
(`dv/cocotb/`, `core_ibex_cocotb_dpi.svh`, `core_ibex_base_test.sv`) for other non-ASCII: all
other hits are em-dashes inside `//` comments (exempt per the finding), none in strings.

## 4. [Important] `COCOTB=1` silent no-op on non-VCS simulators — FIXED

Added a loud failure to `scripts/compile_tb.py`, first thing inside the `LockedMetadata` block:

```python
if md.cocotb and md.simulator != 'vcs':
    raise RuntimeError(
        f'COCOTB=1 currently supports SIMULATOR=vcs only (got SIMULATOR={md.simulator!r}).')
```

Verified: `make GOAL=rtl_tb_compile COCOTB=1 OUT=out_f4check` (fresh OUT, no `SIMULATOR` ->
xlm default) exits nonzero (exit code 2) before any simulator invocation:

```
Building RTL testbench
Traceback (most recent call last):
  ...
  File "/localdev/fzhang/ws/ibex/dv/uvm/core_ibex/scripts/compile_tb.py", line 86, in _main
    raise RuntimeError(
RuntimeError: COCOTB=1 currently supports SIMULATOR=vcs only (got SIMULATOR='xlm').
make[1]: *** [scripts/ibex_sim.mk:42: out_f4check/metadata/tb.compile.stamp] Error 1
make: *** [Makefile:77: run] Error 2
```

No `xrun`/`vcs` process is spawned — the raise happens before `compile_tb.py` builds any
compile command. `out_f4check` removed after capture.

## 5. [Important, real manifest] fcov-expectation manifest for `cocotb_irq_python_test` — DONE (real manifest, not fallback)

Ran `COV=1 COCOTB=1 COCOTB_MODULE=dv.cocotb.tests.test_irq_from_python`, `TEST=cocotb_irq_python_test`,
`SEED=1`, fresh `OUT`. `100.00% PASS 1 PASSED, 0 FAILED`.

Generated the per-test urg text report via `ci/check_fcov_expectations.py`'s own
`urg_per_test_report()`/`parse_groups_report()` (the mechanism the fcov-expectation skill
documents) against `out/run/coverage/shared_cov/test.vdb`, `cm-name test_cocotb_irq_python_test_1`.
All irq-related bins in that report:

```
uarch_cg.cp_controller_fsm.out_of_decode2 12
uarch_cg.cp_controller_fsm.out_of_irq_taken 12
uarch_cg.cp_interrupt_taken.irq_external 12
uarch_cg.cp_interrupt_taken.irq_fast 0
uarch_cg.cp_interrupt_taken.irq_software 0
uarch_cg.cp_interrupt_taken.irq_timer 0
```

Chose two provably-hit, non-vacuous bins (both require the controller to actually *take* an
interrupt, not merely see one pending — a run where cocotb's triggers are never serviced, per
the existing `+cocotb_irq_count=0` ablation in `docs/dv/evidence/ws2-milestone-b.log`, scores 0
on both):

- `uarch_cg.cp_interrupt_taken.irq_external` — `cocotb_irq_raise_seq` (`core_ibex_seq_lib.sv`)
  randomizes `irq_external == 1` exclusively, so this bin's hit is directly attributable to the
  cocotb-driven stimulus, not incidental SV-sequence activity (none run for this test).
- `uarch_cg.cp_controller_fsm.out_of_decode2` — the `DECODE => IRQ_TAKEN` FSM transition.

Wrote `dv/uvm/core_ibex/fcov_expectations/cocotb_irq_python_test.fcov.yaml` with these two bins.

Re-ran with the manifest present (fresh `OUT=out_fcov5b`, same command): flow still
`100.00% PASS 1 PASSED, 0 FAILED`; `trr.yaml`:
```
passed:                   True
failure_mode:
failure_message:
```
(no `failure_mode: FCOV_EXPECTATION`, confirming `check_fcov_expectations()` ran — `COV=1` and
the manifest is present — and did not downgrade the result). Direct invocation of the checker
against the same run for an explicit quote:
```
FCOV-EXPECTATION: uarch_cg.cp_interrupt_taken.irq_external = HIT (count=12)
FCOV-EXPECTATION: uarch_cg.cp_controller_fsm.out_of_decode2 = HIT (count=12)
FCOV-EXPECTATION: PASS — all 2 declared bins hit
```
`out_fcov5b` removed after capture (never committed).

## 6. [Important] COCOTB_MODULE-mismatch vacuous window — FIXED, with a reachability caveat (see Concerns)

Added a `check_phase` (not `final_phase`) override inside `` `ifdef COCOTB_SIM `` in
`core_ibex_base_test.sv`, right after `cocotb_irq_listener()`:

```systemverilog
virtual function void check_phase(uvm_phase phase);
  int unsigned demanded_irq_count;
  super.check_phase(phase);
  if ($value$plusargs("cocotb_irq_count=%0d", demanded_irq_count) &&
      (demanded_irq_count > 0) && (cocotb_vif.trigger_received_count == 0)) begin
    `uvm_error(`gfn,
      "cocotb_irq_count plusarg demanded triggers but trigger_received_count is 0 -- irq stimulus was never serviced (COCOTB_MODULE mismatch?)")
  end
endfunction
```

**Why `check_phase`, not `final_phase` (reasoning, per the finding's ask):** the PASS/FAIL
banner ("--- RISC-V UVM TEST PASSED/FAILED ---") is printed by
`core_ibex_report_server::report_summarize()` (`tests/core_ibex_report_server.sv:17-21`), which
runs during `report_phase` — i.e. *after* `check_phase` but *before* `final_phase` in standard
UVM phase order. `report_summarize()` decides PASS/FAIL from the cumulative
`get_severity_count(UVM_ERROR/UVM_FATAL/UVM_WARNING)` up to that point. An error raised in
`final_phase` would be counted too late to flip that banner; `check_phase` is the latest phase
that still precedes it. Verified this doesn't break the positive-control path: the Milestone B
re-run (finding 5, above) compiled and ran clean with zero UVM_ERROR and no spurious trip.

**Live verification and the finding it surfaces:** ran `TEST=cocotb_irq_python_test` with the
default `COCOTB_MODULE` (fresh `OUT=out_f6mismatch`, no `COCOTB_MODULE=` override). Result:
`0.00% PASS 0 PASSED, 1 FAILED`, but via the **same pre-existing timeout-accident path**, not the
new check:
```
    48: Traceback (most recent call last):
    49: File "/localdev/fzhang/ws/ibex/dv/cocotb/tests/test_hello.py", line 16, in test_hello
    50: await finish(dut)
failure_mode: LOG_ERROR(3)
```
Reason: the default `COCOTB_MODULE` (`dv.cocotb.ibex_cocotb`) loads `test_hello`, whose
`finish(dut)` uses the default 2ms `timeout_ms`. `cocotb_irq_python_test`'s generated program
(`+instr_cnt=10000`) needs ~2.8ms to reach its own riscv-dv handshake (per the Milestone B
evidence). cocotb's own `TimeoutError` fires at 2ms — *before* the UVM side ever reaches its
handshake — and cocotb's uncaught-exception handling `$finish`es the simulation immediately.
Because that `$finish` is abrupt, UVM's own `run_phase` never gracefully completes and
`check_phase` never executes at all for this exact scenario — so the new check is not reachable
here, and this specific verification command still fails for the old reason. See Concerns.

## 7. [Ride-along minor] `COCOTB_MODULE` named in the knob-flip gotcha — FIXED

`docs/dv/BUILD_AND_SIM.md`'s "Stale `metadata.pickle`" gotcha now lists `COCOTB_MODULE`
explicitly alongside `COCOTB`, `WAVES`, `COV`, `SIMULATOR`.

## Concerns

**Finding 6's check_phase guard is not reachable through the literal "default `COCOTB_MODULE`"
repro command**, because that specific mismatch (`test_hello`'s built-in 2ms `finish()` timeout)
already fails earlier and more abruptly than the guard, via cocotb's own uncaught-`TimeoutError`
-> `$finish`, which preempts UVM's phase machine before `check_phase` runs. The guard *is*
reachable and does add real protection for the more dangerous silent-pass case the finding is
actually about: a `COCOTB_MODULE` that is broken/mismatched in some other way (e.g. a custom or
future module that never triggers `"cocotb_irq_raise"` but also never times out early enough to
abort the sim before the generated program's own ~2.8ms natural handshake) would previously have
scored a silent flow-level PASS; now it would be caught in `check_phase` before
`report_summarize()` prints the banner. I did not fabricate a throwaway cocotb module to
demonstrate that scenario live, since the finding's ask was reasoning + compile (plus an
*optional* live run of the literal repro command), and building a new module to force that path
felt like scope creep beyond the 7 findings. Flagging this reachability gap explicitly rather
than presenting the timeout-accident run as if it exercised the new check.

## Commands run (all fresh OUTs, all cleaned up after capture; nothing under `out*/` or
`results.xml` committed)

- `make GOAL=rtl_tb_compile COCOTB=1 OUT=out_f4check` (finding 4)
- `make SIMULATOR=vcs IBEX_CONFIG=opentitan ISS=spike TEST=cocotb_irq_python_test ITERATIONS=1 SEED=1 COV=1 COCOTB=1 COCOTB_MODULE=dv.cocotb.tests.test_irq_from_python OUT=out_fcov5b` (findings 5, 6-positive-control)
- `make SIMULATOR=vcs IBEX_CONFIG=opentitan ISS=spike TEST=cocotb_irq_python_test ITERATIONS=1 SEED=1 COCOTB=1 OUT=out_f6mismatch` (finding 6 live mismatch attempt)
- Direct `ci/check_fcov_expectations.py` invocation against `out_fcov5b`'s vdb (finding 5 quote)

## Files changed

- `docs/dv/process-logs/ws2/{progress,task-1..8-report}.md` (new; copied from `.superpowers/sdd/2026-09-01-ws2-cocotb/`)
- `docs/dv/BUILD_AND_SIM.md`
- `docs/dv/TB_CONTRACT.md`
- `docs/dv/evidence/ws2-hello.log`
- `docs/dv/evidence/ws2-milestone-b.log`
- `dv/uvm/core_ibex/scripts/compile_tb.py`
- `dv/uvm/core_ibex/tb/core_ibex_cocotb_if.sv`
- `dv/uvm/core_ibex/tests/core_ibex_base_test.sv`
- `dv/uvm/core_ibex/fcov_expectations/cocotb_irq_python_test.fcov.yaml` (new)
