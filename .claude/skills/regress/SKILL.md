---
name: regress
description: Run and summarize regressions of the team-built TB (single test, testlist tier, coverage run) using the verified site flow in docs/dv/SIM_RECIPE.md, and read the results artifacts. Use when asked to run tests/regressions or summarize their outcome.
---

# regress

Commands and flags are the verified set in `docs/dv/SIM_RECIPE.md` — always `source ci/env.sh`
first. Zone A owns its own regression scripts under `dv/auto_dv/` (compile of the generated TB,
the team's testlist tiers on LSF, coverage merge, URG reporting); this skill runs those — there is
no other flow in this clone. If the team's runner does not exist yet, say so and stop: building it
is a deliverable (seed prompt, Section 11), not something to improvise here.

- Single test: compile once (`SIM_RECIPE.md` §2), run with the test's `+UVM_TESTNAME` and a pinned
  seed (§5).
- Regression: the team's runner over the team's testlist; LSF via
  `bsub -K -q regress -n <N> -R "span[hosts=1]"` (§7).
- Coverage runs: add the §3 flags; merge and URG-report per §8 into the run's coverage dir.
- Fresh output directory after changing testlists, filelists, or knobs (§9).

Results: read the runner's own verdict artifacts plus the URG `dashboard.txt` for coverage runs.
Summarize: pass rate, failure buckets by first-error signature (group identical failure-message
prefixes), and the per-metric URG totals. Hand failures to the `sim-debug` skill.
