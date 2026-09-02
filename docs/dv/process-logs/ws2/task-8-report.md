# Task 8 Report: TB_CONTRACT.md + BUILD_AND_SIM.md cocotb section

Branch: `fzhang/auto-dv-setup` (verified before starting; working tree was clean).

## Step 1: `docs/dv/TB_CONTRACT.md`

New file. Covers, interfaces only (verified each item against the current code before
writing):

- Two-level selection: `COCOTB=1`/`COCOTB_MODULE=<dotted.module>` make knobs
  (`dv/uvm/core_ibex/Makefile:35-37`, resolved via `MODULE` env var in
  `scripts/run_rtl.py:116`), `+cocotb_*` plusargs read via `cocotb.plusargs.get(...)`.
- Handshake API (`dv/cocotb/common/handshake.py`): `start`/`finish` semantics, the
  alive-before-active ordering and its 100ns SV watchdog, `timeout_ms` sizing note.
- uvm_bridge API (`dv/cocotb/common/uvm_bridge.py`): `trigger(event_name)`, `uvm_ready`,
  and the two accounting counters — described generically as "trigger-received" /
  "handler-entry" counters and what each counts, without naming the specific counter
  fields' internal derivation (e.g. the controller FSM state) or any existing test/
  testlist entry that uses them, per the fence-allowlist-survivor constraint.
- Hard rules 1-4 (assert-before-finish, ASCII-only, post-report assertion window,
  triggers-not-queued) and 5a/5b (vacuous-pass guard + conscious `iterations`), each
  phrased as a generic testlist-authoring rule, not tied to the one existing test that
  motivated it.
- The checking obligation, copied **verbatim** from
  `docs/superpowers/specs/2026-09-01-auto-dv-setup-design.md` line 53 (diffed by eye
  against the source paragraph to confirm exact wording).
- fcov-expectation duty, pointing at `.claude/skills/fcov-expectation/SKILL.md`.

**Judgment call — `results.xml`-in-CWD.** The brief's context list included this under
"what TB_CONTRACT.md must cover," but it's a build-harness/CWD-artifact detail, not part
of using the Python/uvm_bridge interfaces, and TB_CONTRACT.md is the file explicitly
named as the cleanroom's declassified Zone-A doc (spec, WS7 fence section) while
BUILD_AND_SIM.md is not (it "names existing tests" and stays full-tree). Documented it in
BUILD_AND_SIM.md's new cocotb Gotchas instead, and added `results.xml` to
`dv/uvm/core_ibex/.gitignore` (verified true: it lands in cwd, uncommitted — see Step 3).

## Step 2: `docs/dv/BUILD_AND_SIM.md` cocotb section

Added `## cocotb (python) tests` (before `## Gotchas`) with the verified Milestone A
(`docs/dv/evidence/ws2-hello.log`) and Milestone B (`docs/dv/evidence/ws2-milestone-b.log`)
commands, the `SEED=2` deviation note, and a `### Gotchas specific to cocotb` subsection:
knob-flip caveat (pointer to the generalized metadata gotcha below), `finish_on_completion=0`
and its post-report assertion window, the watchdog-vs-import-failure distinction (verified
against `.superpowers/sdd/2026-09-01-ws2-cocotb/task-5-report.md` — a bad `COCOTB_MODULE`
is actually caught by cocotb's own regression manager at time 0, not the SV `$fatal`@100ns
watchdog, which guards a narrower VPI/libpython-load failure class), `timeout_ms` non-scaling,
log-scan-only pass/fail, and the `results.xml` CWD location.

Also generalized the existing "Stale `metadata.pickle`" gotcha to cover flipping *any*
top-level knob (not just testlist/config edits) in a persisted `OUT`, citing Task 4's
finding — this is the same mechanism `COCOTB`/`COCOTB_MODULE` hit, so I merged rather than
duplicated the bullet.

## Step 3: Fresh-shell re-verification of the Milestone A command

```
bash -lc '
source ci/env.sh
cd dv/uvm/core_ibex
rm -rf out_ma_verify
make SIMULATOR=vcs IBEX_CONFIG=opentitan ISS=spike \
     TEST=riscv_arithmetic_basic_test ITERATIONS=1 SEED=2 COCOTB=1 OUT=out_ma_verify
'
```

Result: `100.00% PASS 1 PASSED, 0 FAILED`. Confirmed cocotb actually ran (not just a
vanilla PASS): `rtl_sim_stdstreams.log` shows `COCOTB-HELLO: alive (seed=2)`,
`COCOTB-HELLO: read hart_id_i=0`, `RISC-V UVM TEST PASSED`, `test_hello passed`. Also
confirmed the `results.xml`-in-CWD claim empirically: `dv/uvm/core_ibex/results.xml` was
present after the run. `out_ma_verify/` and `results.xml` removed after inspection, not
committed.

## Disposition of the 5 codex dv-principles-check findings

(`docs/dv/process-logs/ws3/codex-dv-principles-check-exercise.txt`, final verdict block)

1. **[§4 Evidence over inference] line 55 — module-load attribution unmeasured.** REAL,
   fixed. The doc asserted "extra time in env/module-load overhead" as if confirmed; the
   underlying evidence (`task-8-report.md`) only isolates that the TB-compile phase's own
   reported time was unchanged — it doesn't isolate module-load specifically from other
   candidates (instr-gen build variance, license-queue wait, etc.). Reworded to name
   module-load as *one candidate, not isolated further*, and linked the source report.
2. **[§4 Don't hide failures] line 147 — "silently excluded" tests.** REAL, fixed, and the
   finding was actually generous: I read `filter_tests_by_config()`
   (`scripts/ibex_cmd.py:126-187`) directly — it already calls `logger.warning(...)` naming
   the rejected test and the unsatisfied parameter for every exclusion. So the code was
   never silent; only the doc's *wording* was wrong. Fixed to state the logged-warning
   behavior accurately, per the team lead's "excluded-with-logged-warning" framing.
3. **[§5 No hardcoded paths] line 13 — user-specific tools path.** REAL, fixed. Removed
   the literal `/localdev/fzhang/ws/tools` default from the doc; now points solely at
   `ci/env.sh` as the authority for the default, per §5's single-source-of-truth rule.
4. **[§5 Single source of truth] line 126 — config table duplicates `ibex_configs.yaml`.**
   REAL, fixed. Replaced the per-config parameter values in the table with a one-line
   qualitative "distinguishing shape" description and an explicit pointer to
   `ibex_configs.yaml` as the source of truth for actual values.
5. **[§6 Trust & evidence] line 5 — blanket "every command observed" claim unbacked for
   setup commands/timings.** REAL, partially — the evidence for the setup-script timings
   does exist (`docs/dv/process-logs/ws1/task-{3,4}-report.md`, committed), it just wasn't
   *linked*. Fixed by attaching those report links inline next to each timing claim, and
   softening the top-of-doc claim to point at the evidence rather than asserting it
   unconditionally.

No finding judged invalid — all 5 pointed at a real, fixable doc-accuracy gap (three of
them already flagged as known by the team lead's brief; I independently verified findings
1 and 5 against the underlying code/evidence before fixing rather than taking the codex
wording at face value, since finding 2 in particular turned out to be about wording, not
an actual code-behavior violation).

**Also fixed (not one of the 5, per the team lead's brief): FCIBH follow-up needs a
tracked pointer.** Created `docs/dv/known-followups.md` (new, minimal) and pointed the
FCIBH gotcha's "out of scope here" at it instead, since this repo has no issue tracker to
hold this kind of item.

## Step 4: Commit

Committed as `[docs] Add TB contract and cocotb run instructions` (co-authored per site
convention). Files: `docs/dv/TB_CONTRACT.md` (new), `docs/dv/known-followups.md` (new),
`docs/dv/BUILD_AND_SIM.md` (modified), `dv/uvm/core_ibex/.gitignore` (modified, +`results.xml`).
No `out*/` or `results.xml` artifacts committed (verified clean `git status` before commit).

## Concerns

1. TB_CONTRACT.md's counter descriptions ("trigger-received", "handler-entry") are
   deliberately generic per the no-existing-test-references constraint; a future reader
   comparing this doc against the one existing test that exercises them
   (`dv/cocotb/tests/test_irq_from_python.py`, itself likely fenced later) will find the
   contract doc lighter on specifics than the code. That's intentional, not an oversight.
2. `docs/dv/known-followups.md` is a new, minimal tracking convention with exactly one
   entry — it's not an issue tracker, just a durable pointer. If WS3/WS7 already has (or
   later adds) a better home for this, migrate the one entry there.
3. Per the spec's fence document (not yet written — WS7 is later), `TB_CONTRACT.md` is
   explicitly named as part of the cleanroom's declassified doc set; I did not check this
   against an actual `ci/fence.yaml` since it doesn't exist yet, only against the spec's
   stated intent and the "no existing-test references" instruction directly.

## Fix round 1 (team-lead review)

Finding: TB_CONTRACT.md §3 named `cocotb_if.uvm_ready` literally but left the two
counters as prose labels only, so a test author couldn't actually write code against
them. Fixed by naming `cocotb_if.trigger_received_count` and
`cocotb_if.handler_entry_count` alongside their existing descriptions; derivations stay
withheld as before. The `trigger()` param-name prose mismatch was flagged as deferred and
left untouched.

## WS2 exit gate — status at end of this task

- [x] Milestone A log: both frameworks visibly active, test PASSES (evidence committed,
  Task 5; re-verified fresh-shell here)
- [x] Milestone B: python-driven irq stimulus through the UVM agent, negative-control
  proof (evidence committed, Task 7)
- [x] `COCOTB=0` identity evidence committed (Task 6)
- [x] Dead-cocotb watchdog demonstrated on import failure — with the empirically-corrected
  understanding that it's cocotb's own regression manager, not the SV `$fatal`@100ns path,
  that actually fires for a bad `COCOTB_MODULE` (Task 5); documented accurately here rather
  than restating the brief's original assumption.
- [x] `TB_CONTRACT.md` exists with the checking obligation (this task)
