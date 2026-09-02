---
name: dv-principles-check
description: Conformance review of a diff or file against docs/dv/dv_principles.md — cites section numbers, explicitly NOT a general code review. Use on new/changed DV code (tests, checkers, coverage, TB).
---

# dv-principles-check

Input: a diff range or file list. This check reviews ONLY conformance to
`docs/dv/dv_principles.md` (read it fresh each run — never quote this skill as the source; the
doc is the single source of truth).

Procedure: for each changed DV artifact, walk the doc's sections and cite violations as
`[§N bullet] file:line — what violates it — the conforming alternative`. Pay specific attention
to: §1 boundary-realistic stimulus and randomize-don't-walk; §2 fail-through-a-collected-mechanism
and derive-from-intent; §4 don't-hide-failures; §5 comment/single-source rules; §6 the trust triad
(TDD evidence, mutation-proof, fcov-expectation — for any new test/checker, absence of triad
evidence is itself a finding).

Output: PASS, or findings list + a one-line verdict. Scope discipline: general quality/bug review
belongs to the review rubrics (`ci/reviews/`), not here; flag only principle conformance.
