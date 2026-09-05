# Critic verdict: the "template timeout" group, 81355d1..6b894ab (test-writer-2)

Artifacts (the one commit of the range, 6b894ab; sha256 first 16 hex of each blob at that commit):
- dv/auto_dv/tests/gen_test_template.py cc749fd5a35cb623 (the range start 81355d1 carries b285b41845799d14)
- dv/auto_dv/tests/gen_test_lib.py fba4aadf30bc7e3f
- dv/auto_dv/tests/gen_fixtures/gen_ut_wait_past_eot.py dfa65595ccdc2f1e (new)
- dv/auto_dv/docs/gen_test_template_api.md f5eb48e6ed454683
- dv/auto_dv/evidence/gen_tdd_test_template.md 80eab89bd24f6288 (Section 18)
- dv/auto_dv/evidence/gen_tdd_logs/test_writer/gen_tmo_wait_past_eot_red_stdout.log b09a277d8247ae3c
- dv/auto_dv/evidence/gen_tdd_logs/test_writer/gen_tmo_wait_past_eot_green_stdout.log 444dd41468514bf3
- dv/auto_dv/evidence/gen_tdd_logs/test_writer/gen_tmo_irq_1800473338_red_stdout.log bcfa3c04c80a43cf
- dv/auto_dv/evidence/gen_tdd_logs/test_writer/gen_tmo_irq_1800473338_green_stdout.log e647a63891a31190
- dv/auto_dv/evidence/gen_tdd_logs/test_writer/gen_tmo_lib_selftest.log 830b690aa431beb0
- dv/auto_dv/evidence/gen_tdd_logs/test_writer/gen_manifest.md 7dad228056401104

Date: 2026-09-05 (UTC). Role: Critic. Method: the diff read from the committed blobs; the four evidence runs re-run by me
on two detached worktrees, 81355d1 (the committed template) and 6b894ab (the fixed one), each compiled to the same TB
identity 861209d7f0fd1ed1 (the range touches Python only), the fixture image built by me from the committed
gen_report_channel.S, the wave seed's own image and plusargs taken from its retained run command; the records checked
against the blobs. Exposure: the Orchestrator's range message named rev64's outcome (one Medium, three Lows) and the
Medium's subject before this file was written; rev64's content is read only in Section 6. Logs:
dv/auto_dv/work/critic/tmo/ (README.txt, runs/).

CRITIC VERDICT: APPROVE (five Lows owed as disclosed, three adopted from rev64 in Section 6; no Medium).

## 1. The defect and the fix, read from the code

The wave's harness failure (seed 1800473338 of gen_test_irq_basic, classified in gen_wave_4017573/gen_index.md:74-79 as
the one harness timeout) is a waiter left behind at the end of test: the cycle-slot service returned on the final
store and left its pending wait_cycles callers to their own budget of program_budget_cycles, so a wait for a trigger
the program never reached answered a hundred thousand cycles late, the settle wait slept another budget, and run()'s
post-end join, given the same budget, lost. The fix is in the template and its library only:
- CycleWaiters.ended() (gen_test_lib.py:108-112 at 6b894ab) hands back every pending waiter and empties the list; the
  slot service calls it when _edge_or_eot reports the end of test and sets each event before it breaks
  (gen_test_template.py:196-198).
- wait_cycles returns count <= self.cycle() whether a hit or the end woke it, and a call made after eot_seen returns at
  once under the same rule (:210-211, :223): a target the program did not live to see reads False in the cycle the
  program stopped in, which is what the docstring promised and the irq entry's hold_for_last_phase already relies on
  (gen_test_irq_basic.py:104-109 returns False when the wait does).
- run() bounds stimulus() and the runner's last boundary by drain_budget_cycles() (:479-483, :489, :496), the TB's
  finish-handshake budget (the test's finish_timeout_cycles, else +gen_finish_timeout, default
  GEN_FINISH_TIMEOUT_CYCLES_DEFAULT = 20000 from gen_bridge.finish_timeout_cycles), independent of the program's length.
  Since every wait either coroutine can be in answers at the end of test, that bound catches a hang and never a long
  program, and the message names the budget. program_budget_cycles keeps its two remaining roles (the no-progress rule
  and the runner's per-trigger wait), neither a wall on the program's length, as Section 18 states.
The library self-test gains the ended() case (two waiters woken in order, the list empty, a second call idle). The
bins_not_hit class comment on the template (:84-89) now documents five classes including the two the wave re-renders
introduced, which closes my L-2 of gen_critic_wave_rerenders.md and rev63's Low 3 as routed. No test module changed.

## 2. The evidence, re-run by me on one TB build each way

| run | template | outcome |
|---|---|---|
| gen_ut_wait_past_eot, committed template (GEN_TB_PYROOT at 81355d1, header template_sha b285b41845799d14, test_sha dfa65595ccdc2f1e) | red | "stimulus() did not finish after the end of test (SimTimeoutError)" at 50895.01 ns |
| gen_ut_wait_past_eot, fixed template (header template_sha cc749fd5a35cb623) | green | PASS at 2075.01 ns; fire_far_not_reached, fire_far_answered_at_eot, fire_settle_not_reached, fire_settle_answered_at_eot all ok, both waits answered at cycle 84, the end of test at 84; UVM_ERROR 0 |
| gen_test_irq_basic seed 1800473338 on 81355d1 (the wave run's image, crc32 03c84170, its plusargs) | red | FAIL at 1123735.01 ns, GEN_TEST_EOT retired=405 cycle=12368, five GEN_TEST_PHASE lines at cycles 100069-100073 (the c15223 phase applied after the end), the SimTimeoutError |
| the same seed on 6b894ab | green | GEN_TEST_PASS at 131275.01 ns, 0 real UVM_ERROR, no phase after the end |

Every figure equals the retained logs' to the nanosecond, and my headers name the two committed template blobs (the
range's start and end) where the landing's name the export of 9c28944 (the same blob as 81355d1's, b285b41845799d14)
and the landed blob cc749fd5a35cb623 for the re-run green arms. The fixture is the two-wait shape of the irq entry's
last-phase hold with the budget lowered to 5000 cycles (GEN_ALIVE_TIMEOUT_CYCLES_DEFAULT / 20), so it shows the
mechanism without the irq entry and guards the template on its own, as Section 18 says. The red reproducing on a build
of the current TB shows the wave failure was the template's and not the 4017573 testbench's.

## 3. Records

- The five manifest rows carry the retained files' sizes and md5s (11983 / 742e3bf7..., 18645 / 3d742beb..., 28793 /
  62fd08b1..., 49984 / 25b61937..., 1911 / 5638e859...); all five logs ASCII. The lib self-test log is a working-tree
  run at HEAD 3e91c84 and names the template, library and fixture shas that the landing commits (cc749fd5a35cb623,
  fba4aadf30bc7e3f, dfa65595ccdc2f1e).
- The green fixture row's description says "the fixed template f4811134b74c2dca on the same build"; no blob of
  gen_test_template.py in the tree has that digest (81355d1 b285b41845799d14, 6b894ab and HEAD cc749fd5a35cb623), and
  the retained green log's own header reads template_sha=cc749fd5a35cb623, the landed blob: the row describes the first
  green run and was not re-written when the green was re-run after the last edit. The bytes the row binds (size and
  md5) are the re-run's, so the row points at the right file with the wrong sentence (L-1).
- Section 18 states the wave finding from the run's own log, the fix in four numbered parts, what program_budget_cycles
  still bounds, the evidence with its digests, and what is not claimed (the other promotion conditions; other
  entries' behaviour under the drain bound), and the API document's step 3 and wait_cycles row say the same as the code.
- The fixture's docstring calls it "a committed fixture, never a testlist entry": nothing runs it but a hand. A template
  regression of this shape would surface again only as a seed failure of the irq entry (L-2).

## 4. Conformance, rows, verdict

Conformance (dv_principles.md): the failing check preceded the fix and the red-to-green pair is retained on one build
with the template blob named per run; the fix removes a seed-dependent harness wall without touching a test module; the
new fixture states its four fire checks in the entry's own terms; no checker, assertion or coverage changes, so the
mutation and fcov rules do not apply.

- L-1 (Low, records; test-writer-2). The green fixture manifest row names a template blob (f4811134b74c2dca) that exists
  nowhere in the tree; the retained log's header carries the right one. Correct the row's sentence to
  cc749fd5a35cb623, or say the row describes the re-run.
- L-2 (Low, guarding; test-writer-2 with the Runtime Manager). gen_ut_wait_past_eot has no runner: add it to the check
  tier or to a fixtures list the regression can call, so the template's end-of-test contract is checked by machine.

Verdict: CRITIC VERDICT: APPROVE on 81355d1..6b894ab. The mechanism is right by reading, the four evidence runs
reproduce on my own builds to the nanosecond with the committed template blobs named, the records are accurate but for
one manifest sentence; L-1 and L-2 owed as disclosed (L-3..L-5 join them from Section 6). This closes the irq entry's promotion condition (c) as Section 18
scopes it.

## 6. Reconciliation with the cross-model artifact rev64

Read after Sections 1-4 were written: dv/auto_dv/reviews/2026-09-05-claude-diff-81355d1e-6b894ab3.md at 348e4ae (claude
CLI fallback under A-001; APPROVE-WITH-CHANGES; one Medium, three Lows). Its nine verifications agree with Sections 1-3
on every shared point (the wake rule and the post-end guard, the drain budget's sources and its 20000 default, the
fixture's 5000-cycle budget and its red arithmetic, the four headers' template and test blobs, the five manifest rows,
the late phase prevented rather than tolerated) and add three I record as its: wait_retired and wait_event already
returned at once after the end, so the three waits now agree; the EOT-timestep registration race is covered by the new
service's first iteration; and no caller depends on a True return after the end.

- Its Medium (the green fixture row naming f4811134b74c2dca) is my L-1, found independently. I hold it at Low: the
  retained log's own header names the landed blob, Section 18 names it, and the row's size and md5 bind the right bytes,
  so the wrong sentence sits in a description column beside three right identifiers; the fix is the same one token.
- Its Low 1 (the fixture's far target is never reachable, so on the committed template the first wait reads False after
  its budget, the right value at the wrong time, and the wave's value defect, True after the sleep because the target
  passed meanwhile, is not exercised directly; the red comes through the join timeout and the answered-at-EOT checks) is
  verified against the committed template's return path (:217 at 81355d1 returns count <= self.cycle() on the timeout)
  and adopted as L-3 (Low, fixture; test-writer-2): add a wait whose target lies inside one budget past the end so the
  True-after-the-fact path is checked by value too; not blocking, the two checks already fail on either regression.
- Its Low 2 (the cycle-level wave facts, 12368 and 100069 and 17 of 18, are read from the uncommitted run directory while
  the committed wave index carries the message and the nanosecond figure only) is right; adopted as L-4 (Low, records):
  say which comparison is committed.
- Its Low 3 (a post-end wait_cycles returns without consuming simulation time, so an unconditional loop over it would
  spin without advancing time and escape the drain bound; no caller does this) is right on the code (:210-211 returns
  before any await); adopted as L-5 (Low, API document): one clause that a loop over wait_cycles must test its return
  value or eot_seen.
- Verdict unchanged: APPROVE; L-1..L-5 owed as disclosed. rev64 and this file agree there is no Major and, on the row,
  differ only in grade.
