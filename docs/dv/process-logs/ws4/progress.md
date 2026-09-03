# WS4 Jenkins+LSF — process ledger

Plan: docs/superpowers/plans/2026-09-02-ws4-jenkins-lsf.md (codex pre-review rounds: see docs/dv/reviews/).

Gate status: PASS. Compressed gate (Run A, T3/T4) initially hit a real mcounteren_test
cosim mismatch, root-caused to a stale spike pin, fixed and re-verified 100% PASS; Run B
(T5, coverage) was 100% PASS throughout. See docs/dv/evidence/ws4-mcounteren-refix/summary.txt,
docs/dv/evidence/ws4-nightly-lsf/summary.txt, docs/dv/evidence/ws4-coverage/summary.txt.

- [x] T1 common.sh + selftest
- [x] T2 dual-suite testlist plumbing (metadata.py + Makefile) — gate pending (compressed gate stage)
- [x] T3 smoke.sh — compressed gate run: subsumed by Run A (nightly.sh with
      both testlist tests), which found a real mcounteren_test cosim-mismatch
      failure. Script machinery proven (build/run/collect/report/exit-code
      all correct); test-content verdict is not clean. See
      docs/dv/evidence/ws4-nightly-lsf/summary.txt.
      mcounteren failure triaged to stale spike pin, fixed + re-verified —
      see docs/dv/evidence/ws4-mcounteren-refix/summary.txt.
- [x] T4 nightly.sh — compressed gate run: same Run A — LSF pre-probe failed
      (workspace not visible from compute host, see
      docs/dv/evidence/ws4-nightly-lsf/lsf-probe-result.txt), fell back to a
      local run per the recorded fallback rule; that local run's regr.log
      showed 1 PASSED / 1 FAILED (mcounteren_test cosim mismatch — a real
      RTL/cosim finding, not a script defect).
      mcounteren failure triaged to stale spike pin, fixed + re-verified —
      see docs/dv/evidence/ws4-mcounteren-refix/summary.txt.
- [x] T5 coverage.sh — gate DONE via compressed run (Run B): COV=1 artifacts
      (merged.vdb, report/dashboard.txt, merged_vdb.tgz) all produced, and the
      alternate-testlist override proven end-to-end (regr.log lists exactly
      riscv_arithmetic_basic_test.1, not the full all_riscvdv suite). 100% PASS.
      See docs/dv/evidence/ws4-coverage/summary.txt.
- [x] T6 Jenkinsfile + README — reviewed separately
- [x] T7 tt-regress assessment — see docs/dv/tt-regress-assessment.md
      (commits 1a452d99, 55023012)
- [x] T8 docs + regress skill update — reviewed separately

WS4 CLOSED (2026-09-02): post-execution review APPROVE over fc86a077..799e510b (WS4 pathspec) —
docs/dv/reviews/2026-09-02-claude-diff-ws4-fc86a077-799e510b.md (opus fallback, sanity-scoped per
owner directive; identity in artifact). Deferred follow-up (review nit, non-gating): three negative
case-match selftest checks (selftest.sh:67,85,132) should gate on the preceding command's success so
an absent/crashing script cannot emit their PASS lines.
