# fcov-expectation fixture (live run, commit range ws3)

Source: a fresh `COV=1` single-test run (`riscv_arithmetic_basic_test` seed 1, opentitan) in this
worktree; shared VDB `out_ws3fix/run/coverage/shared_cov/test.vdb` (not committed).

Per-test isolation mechanism (proven): `urg -tests <file>` where the file holds the full vdb test
identifier `<vdb minus .vdb>/<cm_name>` → `per-test-tests.txt` shows "Total tests in report: 1".

Bin fixture: `cp_controller_fsm-bins.txt` (grpinfo.txt excerpt) — `out_of_decode0` HIT,
`out_of_irq_taken` UNHIT for this test.

Verified classifications (ci/check_fcov_expectations.py against the live VDB):
  - manifest {out_of_decode0, out_of_irq_taken} → exit 2, UNHIT named   → test FAILS
    (trr.yaml: passed False, failure_mode FCOV_EXPECTATION(4); regr.log: 0 PASSED 1 FAILED)
  - manifest {out_of_decode0}                   → exit 0                → test PASSES (restored)
Mutation MUT-001 (classify `<=0`→`<0`) is caught by `--self-test` (exit 2) and passes on revert.

## TDD deviation (recorded)

The checker was built implementation-first — no pre-implementation failing-check transcript
exists (a triad rule-1 process violation on the tool itself, caught by the WS3 post-execution
cross-review). Compensating raw evidence that the check can fail, accepted per that review:
MUT-001 (the detector FAILs on mutated classification logic, exit 2, passes on revert) and the
live declared-unhit run (exit 2 → trr FCOV_EXPECTATION(4) → regr.log FAILED). All future
tests/checkers follow rule 1 as written.

Controller ruling (WS3 controller, delegated authority, 2026-09-01): the rule-1 deviation on
this checker is ACCEPTED with the compensating evidence above (MUT-001 + live declared-unhit
FAIL) — recorded per the cross-model policy's exception path; the triad binds as written for
all subsequent work. Disagreement with this ruling goes to the human owner.
