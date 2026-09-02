---
name: regress
description: Run and summarize ibex regressions (single test, full testlist, coverage) using the verified flow commands, and read the results artifacts. Use when asked to run tests/regressions or summarize their outcome.
---

# regress

Commands are the verified set in `docs/dv/BUILD_AND_SIM.md` — always `source ci/env.sh` first.

`ci/jenkins/{smoke,nightly,coverage}.sh` are the primary entry points (see
`docs/dv/BUILD_AND_SIM.md#regression-scripts-ci-jenkins` and `ci/jenkins/README.md` for the full
option set):

- Quick sanity: `ci/jenkins/smoke.sh`
- Scoped run: `ci/jenkins/nightly.sh --test <t> --iterations <n> --seed <s>`
- Coverage: `ci/jenkins/coverage.sh --test <t> --iterations <n> --seed <s>` (add `--out` for a
  fresh dir; merged vdb + urg report under `<OUT>/run/coverage/`)
- Generated testlists: `--testlist <yaml>` / `--directed-testlist <yaml>` select an alternate suite
- LSF: add `--lsf` (`--lsf-queue` to override the default queue)

Direct `make` (from `( cd dv/uvm/core_ibex && ... )`) stays the local fallback:

- Single test: `make SIMULATOR=vcs IBEX_CONFIG=opentitan ISS=spike TEST=<t> ITERATIONS=1 SEED=<s>`
- Full riscv-dv regression: `TEST=all` (testlist iterations); directed: `TEST=all_directed`
- Coverage: add `COV=1` and a fresh `OUT=`; merged vdb + urg report under `<OUT>/run/coverage/`
- Fresh `OUT=`/`make clean` after editing testlists or `ibex_configs.yaml` (metadata.pickle).

Results: `regr.log` (verdicts), `report.html`, `regr_junit.xml`, per-test `trr.yaml`. Summarize:
pass rate, failure buckets by first-error signature (group identical `failure_message` prefixes),
and for COV runs the urg dashboard score line. Hand failures to the `sim-debug` skill.
