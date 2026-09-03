---
name: fcov-expectation
description: Declare and enforce the functional-coverage bins a test intends to hit — declared-but-unhit bins fail the run (trust triad rule 3). Use when writing any new test and when auditing coverage claims.
---

# fcov-expectation

Executes trust-triad rule 3. The canonical rules (from docs/dv/dv_principles.md §6 — that doc is
the source of truth; this copy is validator-checked against it):

<!-- TRUST-TRIAD-CANONICAL-BEGIN -->
**The trust triad** — required for every new test, checker, assertion, or covergroup, whether
human-written or generated:

1. **TDD** — the behavior is specified by a failing check before the implementation that makes
   it pass; the red→green transcript is part of the evidence.
2. **Mutation-proof** — a new checker or assertion counts only when a named mutation (recorded
   as id, file:line, original, mutated, expected detector) is caught by the NAMED checker with
   hidden referees inert, plus a checker-ablation negative control (checker disabled ⇒ the
   mutation survives). "Hidden referees inert" operationally (Zone A): every Zone A check other
   than the named one is disabled for the evidence run, and the failure signature in the log
   belongs to the named check (seed prompt, Section 8).
3. **fcov-expectation** — every new test declares the functional-coverage bins it intends to
   hit; declared-but-unhit bins FAIL the run. Verification is per-test and pre-merge (merged
   databases let one test claim another's bins), generated covergroups live in an isolated
   namespace, and every sampling condition gets an anti-vacuity review (a bin hit by an
   always-true sample proves nothing).
<!-- TRUST-TRIAD-CANONICAL-END -->

## How to declare

Write `dv/auto_dv/fcov_expectations/<testname>.fcov.yaml` (filename matches the test's name
exactly):
```yaml
bins:
  - <covergroup>.<coverpoint>.<bin>   # e.g. gen_myfeature_cg.cp_mymode.bin_active
```
Bin names come from the urg text report (`grpinfo.txt`) of a coverage run over your own
covergroups; counts sum across instances of the same covergroup name — the expectation is "hit
anywhere in this test". Declare bins ONLY from covergroups you authored under `dv/auto_dv/**`
(`gen_` namespace — generated covergroups live in their own namespace, never added into another
covergroup). Anti-vacuity rule: review each declared bin's sampling condition — a bin hit by an
always-true sample proves nothing; declare bins whose hit genuinely evidences the intended
stimulus.

## How to enforce

`ci/check_fcov_expectations.py` implements the verdict; wire it into your own regression flow's
post-run step for every test with a manifest, on coverage-enabled runs. Per-test isolation is via
`urg -tests` with the full vdb test identifier (`<vdb path minus .vdb>/<cm_name>`, using the
`-cm_name test_<name>_<seed>` convention from `docs/dv/SIM_RECIPE.md` §3 — verify the report says
"Total tests in report: 1"). A declared-but-unhit bin, or an unverifiable query, must FAIL the
test — unverifiable is not a pass (run the checker's `--self-test` once to see the
classification behavior). Enforcement needs coverage enabled; a non-coverage run skips the check
by design. Under a parallel regression, run the per-test query only after every writer to the
shared vdb has finished — a mid-write read is unvalidated.
