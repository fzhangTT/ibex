---
name: mutation-check
description: Prove a new checker or assertion actually fires — inject a named mutation, show the named checker catches it with hidden referees inert, run the ablation control, revert. Required evidence for every new DV checker (trust triad rule 2).
---

# mutation-check

Executes trust-triad rule 2. The canonical rules (from docs/dv/dv_principles.md §6 — that doc is
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

## Procedure

1. **Declare** the mutation record in `dv/auto_dv/mutations/` (create the directory and a README
   stating this format on first use): id, file:line, original, mutated, expected detector (the
   NAMED checker/test that must catch it).
2. **Apply** the one-line mutation.
3. **Run** the covering test with hidden referees inert — in Zone A that means every check other
   than the named detector is disabled for the evidence run (via your TB's own check-enable
   knobs), so nothing else can mask or claim the catch. For host-side checkers, "inert" means
   running only the named detector (e.g. a script's `--self-test`).
4. **Verify attribution**: the run FAILS and the failure signature in the log belongs to the named
   detector — a failure from anything else does not count.
5. **Ablation control**: disable the named checker (comment/knob), rerun — the mutation must
   SURVIVE (run passes). A mutation "caught" even with the checker off means something else
   detected it and the proof is void.
6. **Revert** the mutation (and the ablation, and the check-disable knobs), rerun once green, and
   commit the mutation record + the transcript excerpts as evidence alongside the checker.
