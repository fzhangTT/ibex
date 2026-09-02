---
name: mutation-check
description: Prove a new checker or assertion actually fires — inject a named mutation, show the named checker catches it with hidden referees inert, run the ablation control, revert. Required evidence for every new DV checker (trust triad rule 2).
---

# mutation-check

Executes trust-triad rule 2. The canonical rules (from docs/dv/dv_principles.md §6 — that doc is
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

## Procedure

1. **Declare** the mutation in `dv/auto_dv/mutations/` (format in its README): id, file:line,
   original, mutated, expected detector (the NAMED checker/test that must catch it).
2. **Apply** the one-line mutation.
3. **Run** the covering test with hidden referees inert: add `+disable_cosim=1` to the sim (cosim
   mismatches become informational and cannot fail the test). For host-side checkers, "inert"
   means running only the named detector (e.g. a script's `--self-test`).
4. **Verify attribution**: the run FAILS and the failure signature in the log belongs to the named
   detector — a failure from anything else does not count.
5. **Ablation control**: disable the named checker (comment/knob), rerun — the mutation must
   SURVIVE (run passes). A mutation "caught" even with the checker off means something else
   detected it and the proof is void.
6. **Revert** the mutation (and the ablation), rerun once green, and commit the mutation record +
   the transcript excerpts as evidence alongside the checker.

Worked example: MUT-001 in `dv/auto_dv/mutations/README.md` (the fcov-expectation checker's own
classify rule, detector `--self-test`).
