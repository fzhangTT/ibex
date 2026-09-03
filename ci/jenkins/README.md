# Jenkins + LSF setup for the ibex auto-DV fork

This covers running `ci/jenkins/{smoke,nightly,coverage}.sh` by hand and wiring them into Jenkins.
The scripts are the primary regression entry points; see `docs/dv/BUILD_AND_SIM.md` for the
underlying `make` flow they wrap (direct-`make` stays the documented fallback).

## The three scripts

All three source `ci/jenkins/common.sh`, which owns option parsing, `OUT` reservation, the `make`
invocation, LSF phase-1 wrapping (`bsub -K`), and the `regr.log` pass/fail verdict. Each script
presets its own job name and defaults, then hands off to `common.sh`'s `ci_main`.

| Script | What it runs | Defaults |
|---|---|---|
| `smoke.sh` | Two fast tests (one riscv-dv, one directed) | `TEST=riscv_arithmetic_basic_test,mcounteren_test ITERATIONS=1 SEED=1` |
| `nightly.sh` | Full regression at testlist iterations | `TEST=all`, `SEED=$(date -u +%y%m%d)` (no `ITERATIONS` override) |
| `coverage.sh` | Full regression with coverage | `TEST=all COV=1`, `SEED=$(date -u +%y%m%d)`; tars `merged.vdb` to `merged_vdb.tgz` on a passing run |

Full option set (shared by all three; run `<script> --help` for the live text):

| Option | Meaning |
|---|---|
| `--test LIST` | Comma-separated test name(s) |
| `--testlist YAML` | Absolute path to an alternate `riscv_dv_extension/testlist.yaml` (stock if omitted) |
| `--directed-testlist YAML` | Absolute path to an alternate `directed_tests/directed_testlist.yaml` (stock if omitted) |
| `--iterations N` | Positive integer iteration count |
| `--seed S` | Nonnegative integer seed |
| `--config NAME` | `ibex_configs.yaml` config name (default `opentitan`) |
| `--out DIR` | Output directory (default `out_ci/<job>-<UTC timestamp>`) |
| `--jobs N` | Positive integer `make -jN` / LSF slot count (default 4) |
| `--lsf` | Submit under `bsub -K` |
| `--lsf-queue Q` | LSF queue name (default `regress`) |
| `--cocotb` | Run the cocotb overlay |
| `--cocotb-module MOD` | cocotb Python test module; implies `--cocotb` |
| `--dry-run` | Print the command(s) and exit 0 |
| `--help` | Print usage and exit 0 |

Hand-run examples:

```bash
# Local, no LSF
ci/jenkins/smoke.sh
ci/jenkins/nightly.sh --test riscv_arithmetic_basic_test --iterations 2

# Through LSF
ci/jenkins/nightly.sh --lsf --lsf-queue regress --jobs 8
ci/jenkins/coverage.sh --lsf --test riscv_arithmetic_basic_test --iterations 1 --seed 1
```

Measured wall-clocks: gate runs for this delivery are recorded in
`docs/dv/evidence/ws4-nightly-lsf/` and `docs/dv/evidence/ws4-coverage/` — each `summary.txt` is the
source of truth for observed timing on this host (the smoke gate is subsumed into the
nightly-reduced run; see §Smoke policy below); treat any number here as illustrative only.

## Smoke policy

The smoke *selection* (`riscv_arithmetic_basic_test,mcounteren_test`, `ITERATIONS=1`, `SEED=1`) is
CI policy, defined exactly once, in `smoke.sh`'s own header comment — not a derived or tagged list
elsewhere. The test definitions themselves stay canonical in the testlist YAMLs; `smoke.sh` merely
references two entries by name, the same `TEST=` selection interface used everywhere else in the
flow. A dedicated smoke *gate* run was subsumed into this delivery's compressed schedule: smoke's
budget timing comes from the nightly-reduced LSF run's evidence
(`docs/dv/evidence/ws4-nightly-lsf/summary.txt`), which exercises the same script machinery smoke.sh
wraps — a controller ruling recorded in `docs/dv/process-logs/ws4/progress.md`, not a gap in coverage.

## Dual-suite knob

`--testlist`/`--directed-testlist` resolve to the `RISCV-DV-TESTLIST`/`DIRECTED-TESTLIST` make
knobs, which metadata.py plumbs into `RISCVDV_TESTLIST`/`DIRECTED_TESTLIST` on the regression
metadata object (empty = stock testlist; see `docs/dv/BUILD_AND_SIM.md` for the make-knob
reference — not duplicated here). Any generated suite (e.g. the challenge's own generated
testlists) runs through these same three scripts by pointing `--testlist`/`--directed-testlist` at
the generated YAML — no separate entry point is needed.

One exclusion carries over unchanged: a testlist entry tagged `cocotb: 1` is skipped under
`COCOTB=0` (`filter_cocotb_only_tests()`), regardless of which testlist supplies it; name it
explicitly in `--test` and pass `--cocotb`/`--cocotb-module` to select it anyway.

Gate evidence for the knob itself: `docs/dv/evidence/ws4-coverage/summary.txt` — this delivery's
compressed gate schedule folds the alternate-testlist proof into the coverage gate run, showing the
override selects the alternate suite, not the stock one.

## Jenkins job setup

- Repo: `https://github.com/fzhangTT/ibex.git`
- Branch spec: `master`, `fzhang/*`
- Pipeline script path: `ci/jenkins/Jenkinsfile` (this repo, "Pipeline script from SCM")

**Scheduling.** A plain `cron` trigger cannot set build parameters, so a scheduled `RUN_NIGHTLY`/
`RUN_COVERAGE` build needs one of:

- (a) the `parameterizedCron` plugin on a single job:
  ```groovy
  parameterizedCron('''
  H 2 * * * %RUN_SMOKE=false;RUN_NIGHTLY=true
  H 4 * * 6 %RUN_SMOKE=false;RUN_COVERAGE=true
  ''')
  ```
- (b) three separate Jenkins jobs sharing this one `Jenkinsfile`, each with its own parameter
  defaults overridden at the job level: smoke triggered per-push, nightly and coverage on their own
  `cron` schedules.

Which of (a)/(b) is available is decided at Jenkins-setup time (plugin availability); both are
documented here, neither is assumed.

**Node requirements:**
- An LSF submit host, labeled `lsf-submit` in Jenkins.
- Environment-modules (`module` command) present and loadable, per `ci/env.sh`.
- `/tools_vendor`, `/tools_risc`, and `/localdev/fzhang/ws/tools` visible and readable.
- Two VCS licenses available per fresh build (the riscv-dv generator and the TB compile are
  separate VCS invocations — see `docs/dv/BUILD_AND_SIM.md` Gotchas).

**Storage.** The Jenkins workspace *and* the `--out` path must be visible at the same absolute path
on both the submit host and every LSF compute host it dispatches to (shared storage) — a `--lsf`
run's inner invocation re-execs the same absolute paths on whichever host LSF schedules it to.
`/localdev/*` paths are typically submit-host-local, not compute-host-visible; the probe result for
this environment is recorded in `docs/dv/evidence/ws4-nightly-lsf/summary.txt` (Task 4's
pre-gate LSF workspace-visibility check) — consult it before assuming this workspace is usable
as-is for a `--lsf` job, and fall back to a clone on confirmed shared storage if it is not.

**Credentials.** Checkout needs a GitHub PAT with read access to `fzhangTT/ibex` (a Jenkins
"Username with password" or "Secret text" credential), or the existing `fzhangTT` credential helper
already configured on the submit host if Jenkins is set up to inherit it. No other credentials are
needed — LSF submission and VCS licensing are host-level, not per-job.

## LSF phase 1 vs. phase 2

**Phase 1 (this delivery):** each script submits one `bsub -K` job that runs the *entire* `make`
invocation (build + full test selection) on a single LSF slot allocation (`-R "span[hosts=1]"`,
`-n $CI_JOBS`); parallelism inside that allocation is `make -jN` on one host. This is what
`smoke.sh`/`nightly.sh`/`coverage.sh` and the Jenkinsfile implement and what the gate evidence
proves end-to-end.

**Phase 2 (future work, not delivered here):** per-test `bsub` fan-out, where the build stages run
once and each test then gets its own LSF job. Feasibility, from reading
`dv/uvm/core_ibex/scripts/metadata.py`: the single-writer design holds — `create_metadata` runs
once per invocation in the top-level Makefile before `wrapper.mk` (`Makefile:71-85`), and each
test/seed gets its own uniquely-named `TestRunResult` pickle file (`<test>.<seed>.pickle`), so
per-test result files don't collide under fan-out. Reads and updates to the shared
`metadata.pickle` after creation (`compile_tb.py`, `build_instr_gen.py`, `collect_results.py`,
`get_fcov.py`, `merge_cov.py`, `render_config_template.py`) all go through `LockedMetadata`, which
takes a `portalocker` exclusive lock (with a 5-second alarm-based timeout around the open/lock/read
step), so concurrent access is serialized rather than corrupted — no data-corruption risk from
fan-out. The open question is contention, not correctness: `collect_results.py` (used per test to
fold its pass/fail into the shared file) would have every fanned-out test job queuing for the same
exclusive lock, and a burst of near-simultaneous completions could exceed that 5-second alarm and
raise `OSError` rather than block indefinitely — a real design point for phase 2, not yet addressed.

## Cleanroom-sync job (pending WS7)

**Not yet created.** The design calls for a Jenkins job that runs `ci/sync-cleanroom.sh` on every
`master` push, syncing the fenced/cleanroom split once the fence authority (`docs/dv/FENCE.md`,
WS7) lands. `ci/sync-cleanroom.sh` does not exist yet — creating this job before that script exists
would fail closed with nothing to run, so it is deliberately deferred until WS7 delivers the script.

## Lint status

This `Jenkinsfile` is **not lint-validated — no Jenkins reachable from this host** (only a plain
`SimpleHTTPServer` answers on `localhost:8080`; no `jenkins-cli` on `PATH`). It was checked by eye
against the declarative-pipeline grammar (`pipeline`/`agent`/`options`/`parameters`/
`environment`/`stages`/`stage`/`when`/`steps`/`post` nesting, `sh` heredoc quoting) but has not been
run through an actual Jenkins instance's `Replay`/linter.
