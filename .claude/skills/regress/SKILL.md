---
name: regress
description: Run and summarize ibex regressions (single test, full testlist, coverage) using the verified flow commands, and read the results artifacts. Use when asked to run tests/regressions or summarize their outcome.
---

# regress

Commands are the verified set in `docs/dv/BUILD_AND_SIM.md` — always `source ci/env.sh` first and
run from `( cd dv/uvm/core_ibex && ... )`.

- Single test: `make SIMULATOR=vcs IBEX_CONFIG=opentitan ISS=spike TEST=<t> ITERATIONS=1 SEED=<s>`
- Full riscv-dv regression: `TEST=all` (testlist iterations); directed: `TEST=all_directed`
- Coverage: add `COV=1` and a fresh `OUT=`; merged vdb + urg report under `<OUT>/run/coverage/`
- Fresh `OUT=`/`make clean` after editing testlists or `ibex_configs.yaml` (metadata.pickle).

Results: `regr.log` (verdicts), `report.html`, `regr_junit.xml`, per-test `trr.yaml`. Summarize:
pass rate, failure buckets by first-error signature (group identical `failure_message` prefixes),
and for COV runs the urg dashboard score line. Hand failures to the `sim-debug` skill.

Maintenance note (binding): WS4 delivers `ci/jenkins/{smoke,nightly,coverage}.sh`; when those land
this skill MUST be updated to wrap them as the primary entry points, keeping direct-make as the
local fallback.
