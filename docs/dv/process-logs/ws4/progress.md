# WS4 Jenkins+LSF — process ledger

Plan: docs/superpowers/plans/2026-09-02-ws4-jenkins-lsf.md (codex pre-review rounds: see docs/dv/reviews/).

- [x] T1 common.sh + selftest
- [x] T2 dual-suite testlist plumbing (metadata.py + Makefile) — gate pending (compressed gate stage)
- [~] T3 smoke.sh — compressed gate run BLOCKED, not closed: subsumed by Run A
      (nightly.sh with both testlist tests), which found a real mcounteren_test
      cosim-mismatch failure. Script machinery proven (build/run/collect/report/
      exit-code all correct); test-content verdict is not clean. See
      docs/dv/evidence/ws4-nightly-lsf/summary.txt.
- [~] T4 nightly.sh — compressed gate run BLOCKED, not closed: same Run A —
      LSF pre-probe failed (workspace not visible from compute host, see
      docs/dv/evidence/ws4-nightly-lsf/lsf-probe-result.txt), fell back to a
      local run per the recorded fallback rule; that local run's regr.log
      shows 1 PASSED / 1 FAILED (mcounteren_test cosim mismatch — a real
      RTL/cosim finding, not a script defect). Gate re-run after the
      mcounteren_test finding is triaged.
- [x] T5 coverage.sh — gate DONE via compressed run (Run B): COV=1 artifacts
      (merged.vdb, report/dashboard.txt, merged_vdb.tgz) all produced, and the
      alternate-testlist override proven end-to-end (regr.log lists exactly
      riscv_arithmetic_basic_test.1, not the full all_riscvdv suite). 100% PASS.
      See docs/dv/evidence/ws4-coverage/summary.txt.
- [x] T6 Jenkinsfile + README — reviewed separately
- [ ] T7 tt-regress assessment
- [x] T8 docs + regress skill update — reviewed separately
