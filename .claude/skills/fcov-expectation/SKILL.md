---
name: fcov-expectation
description: Declare and enforce the functional-coverage bins a test intends to hit — declared-but-unhit bins fail the run (trust triad rule 3). Use when writing any new test and when auditing coverage claims.
---

# fcov-expectation

Executes trust-triad rule 3. The canonical rules (from docs/dv/dv_principles.md §6 — that doc is
the source of truth; this copy is validator-hash-checked against it):

<!-- TRUST-TRIAD-CANONICAL-BEGIN -->
**The trust triad** — required for every new test, checker, assertion, or covergroup, whether
human-written or generated:

1. **TDD** — the behavior is specified by a failing check before the implementation that makes
   it pass; the red→green transcript is part of the evidence.
2. **Mutation-proof** — a new checker or assertion counts only when a named mutation (recorded
   as id, file:line, original, mutated, expected detector) is caught by the NAMED checker with
   hidden referees inert, plus a checker-ablation negative control (checker disabled ⇒ the
   mutation survives). "Hidden referees inert" operationally: run with `+disable_cosim=1` (cosim
   mismatches become informational and cannot fail the test) and verify the failure signature in
   the log belongs to the named checker.
3. **fcov-expectation** — every new test declares the functional-coverage bins it intends to
   hit; declared-but-unhit bins FAIL the run. Verification is per-test and pre-merge (merged
   databases let one test claim another's bins), generated covergroups live in an isolated
   namespace, and every sampling condition gets an anti-vacuity review (a bin hit by an
   always-true sample proves nothing).
<!-- TRUST-TRIAD-CANONICAL-END -->

## How to declare

Write `dv/uvm/core_ibex/fcov_expectations/<testname>.fcov.yaml`:
```yaml
bins:
  - <covergroup>.<coverpoint>.<bin>   # e.g. my_auto_cg.cp_req_kind.saw_write (your OWN covergroup)
```
Bin names come from the urg text report (`grpinfo.txt`) of a COV run over your own covergroups;
counts sum across instances of the same covergroup name — the expectation is "hit anywhere in
this test". In generation sessions, declare bins ONLY from covergroups you authored under
`dv/auto_dv/**` — existing coverage-model identifiers are fenced and must not appear here. Namespace rule: generated covergroups live in their own namespace
(`dv/auto_dv/`-owned covergroup names), never added into existing human covergroups. Anti-vacuity
rule: review each declared bin's sampling condition — a bin hit by an always-true sample proves
nothing; the declaration should name bins whose hit genuinely evidences the intended stimulus.

## How it is enforced (already wired)

`scripts/check_logs.py` runs `ci/check_fcov_expectations.py` for any test with a manifest in a
`COV=1` run: per-test isolation via `urg -tests` with the full vdb test identifier
(`<vdb minus .vdb>/test_<name>_<seed>`, proven "Total tests in report: 1"); a declared-but-unhit
bin (or an unverifiable query) fails the test with `failure_mode: FCOV_EXPECTATION(4)` in
`trr.yaml` and FAILED in `regr.log`. Infra-only references (fenced from generation sessions):
the evidence fixture `docs/dv/evidence/ws3-fcov-fixture/` and the checker's mechanism notes.
Note: enforcement needs `COV=1`; a non-coverage run skips the check by design.
