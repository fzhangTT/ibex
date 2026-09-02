# WS4 — Jenkins + LSF Regression Scripts Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Self-contained regression entry scripts (`ci/jenkins/{smoke,nightly,coverage}.sh`) runnable by hand or by Jenkins, with LSF phase-1 wrapping, a declarative Jenkinsfile, setup README, and the tt-regress written assessment.

**Architecture:** Three thin entry scripts share one sourced helper (`ci/jenkins/common.sh`) that parses a common option set, builds the verified `make` invocation from `docs/dv/BUILD_AND_SIM.md`, optionally resubmits itself under `bsub -K` (LSF phase 1: one LSF job per regression, `make -jN` inside), and parses `regr.log` for a fail-loud verdict independent of make's exit code. A license-free `selftest.sh` (dry-run assertions + regr.log fixtures) gives every script a TDD cycle.

**Tech Stack:** bash, GNU make (ibex core_ibex flow), LSF 10.1 (`bsub`), Jenkins declarative pipeline, VCS via `SIMULATOR=vcs`.

**Spec:** `docs/superpowers/specs/2026-09-01-auto-dv-setup-design.md` §Workstream 4, plus the session-1 handoff item 2 (dual-suite requirement) in `docs/superpowers/handoffs/2026-09-02-session1-handoff.md`.

## Global Constraints

- `source ci/env.sh` before any flow command; never `&&`-chain `module` (it exits 1 on success — env.sh handles loads).
- Every real sim run uses a **fresh `OUT=`** (stale `metadata.pickle` gotcha); `out*/` under `dv/uvm/core_ibex/` is gitignored.
- Verified command shape (BUILD_AND_SIM.md): `make SIMULATOR=vcs IBEX_CONFIG=opentitan ISS=spike TEST=<t> [ITERATIONS=n] SEED=<s> [COV=1] [COCOTB=1] OUT=<dir>`, run in `dv/uvm/core_ibex`.
- Dual-suite requirement (handoff item 2): every script accepts `--testlist <yaml>` / `--directed-testlist <yaml>` mapping to the Makefile's exported `RISCV-DV-TESTLIST` / `DIRECTED-TESTLIST` vars, so the existing suite runs as reference AND new suites (e.g. a future `dv/auto_dv` testlist) run through the same scripts.
- `TEST=all` excludes testlist entries marked `cocotb: 1` when `COCOTB=0` (commit 0498fbea) — expected, not a script bug.
- Error messages in ci scripts are an ASD-STE100 surface (`simple-english` skill scope): short, imperative, unambiguous.
- Scripts must be `bash`, `set -uo pipefail` (NOT `-e` — result parsing must run after a failed make), executable, and self-contained (compute repo root from `BASH_SOURCE`).
- Nonzero exit on any failure; a missing `regr.log` is a failure (fail loud, never fake-pass — dv_principles §4).
- LSF: queue default `regress` (exists on this site; override `--lsf-queue`), `bsub -K` (block, propagate exit), `-R "span[hosts=1]"` (make -j needs one host).
- Evidence files go under `docs/dv/evidence/` (`ws4-*`); process ledger `docs/dv/process-logs/ws4/progress.md` gets one appended line per completed task.
- Run `.codex/compat/validator.py` after any edit to CLAUDE.md/skills/docs it validates; must stay PASS.
- Commit after every task; commit messages follow the branch's `[ci]`/`[dv]`/`[docs]` prefix convention.

---

### Task 1: `ci/jenkins/common.sh` + selftest harness

**Files:**
- Create: `ci/jenkins/common.sh`
- Create: `ci/jenkins/selftest.sh`
- Create: `ci/jenkins/testdata/regr_pass.log`, `ci/jenkins/testdata/regr_fail.log`
- Create: `docs/dv/process-logs/ws4/progress.md`

**Interfaces:**
- Consumes: Makefile knobs listed in Global Constraints; `regr.log` first-line format `NN.NN% PASS X PASSED, Y FAILED` (writer: `dv/uvm/core_ibex/scripts/report_lib/text.py:gen_summary_line`).
- Produces (used by Tasks 2–4):
  - `ci_parse_args "$@"` — parses the shared option set into globals `CI_TEST CI_TESTLIST CI_DIRECTED_TESTLIST CI_ITERATIONS CI_SEED CI_CONFIG CI_OUT CI_JOBS CI_LSF CI_LSF_QUEUE CI_COCOTB CI_COV CI_DRY_RUN`. Callers preset job-specific defaults (`CI_JOB_NAME`, `CI_TEST`, `CI_SEED`, `CI_ITERATIONS`, `CI_COV`) **before** calling; options override. Unknown option ⇒ usage on stderr, exit 2.
  - `ci_main "$@"` — the whole driver: parse args, `source "$REPO_ROOT/ci/env.sh"`, build the make command, dry-run/LSF-resubmit/execute, then `ci_report_results "$CI_OUT_ABS"`; returns the final verdict as exit code.
  - `ci_report_results <out_abs_dir>` — parses `<out_abs_dir>/run/regr.log`: exit 0 iff the file exists and reports `0 FAILED`; prints the summary line and, on failure, the failing-test detail block. Separately callable so selftest can drive it with fixtures.
- Option set (all of Tasks 2–4 expose exactly this):
  `--test LIST --testlist YAML --directed-testlist YAML --iterations N --seed S --config NAME --out DIR --jobs N --lsf --lsf-queue Q --cocotb --dry-run --help`
- Defaults: `CI_CONFIG=opentitan`, `CI_JOBS=4`, `CI_LSF=0`, `CI_LSF_QUEUE=${LSF_QUEUE:-regress}`, `CI_OUT=out_ci/${CI_JOB_NAME}-$(date -u +%Y%m%d-%H%M%S)` (relative to `dv/uvm/core_ibex`).
- LSF mode: `ci_main` re-executes the calling script under `bsub -K -J "ibex-${CI_JOB_NAME}" -q "$CI_LSF_QUEUE" -n "$CI_JOBS" -R "span[hosts=1]" -o "<out_abs>/lsf.log"` with **all values resolved to explicit flags and `--lsf` removed** (so the inner invocation is deterministic and the timestamped OUT is fixed once). `--dry-run --lsf` prints the full bsub command without submitting.
- Make command shape (built as an array, printed verbatim by dry-run):
  `make -C "$REPO_ROOT/dv/uvm/core_ibex" -j"$CI_JOBS" SIMULATOR=vcs ISS=spike IBEX_CONFIG="$CI_CONFIG" TEST="$CI_TEST" SEED="$CI_SEED" OUT="$CI_OUT"` plus, only when set: `ITERATIONS=`, `COV=1`, `COCOTB=1`, `RISCV-DV-TESTLIST=`, `DIRECTED-TESTLIST=`.

- [ ] **Step 1: Write the failing selftest**

`ci/jenkins/selftest.sh` — license-free checks; starts with common.sh unit checks (script-level checks are appended by Tasks 2–4):

```bash
#!/usr/bin/env bash
# Self-test for ci/jenkins scripts. No simulator, no license, no LSF submission.
set -uo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"
FAILURES=0
check() { # <name> <needle> <haystack>
  if [[ "$3" == *"$2"* ]]; then echo "PASS: $1"; else
    echo "FAIL: $1 — expected to find [$2] in output:"; echo "$3" | sed 's/^/  | /'
    FAILURES=$((FAILURES + 1))
  fi
}
check_status() { # <name> <expected-exit> <actual-exit>
  if [[ "$3" -eq "$2" ]]; then echo "PASS: $1"; else
    echo "FAIL: $1 — expected exit $2, got $3"; FAILURES=$((FAILURES + 1))
  fi
}

# --- common.sh: ci_report_results against fixtures ---
mkdir -p /tmp/ci-selftest.$$/pass/run /tmp/ci-selftest.$$/fail/run /tmp/ci-selftest.$$/empty/run
cp testdata/regr_pass.log /tmp/ci-selftest.$$/pass/run/regr.log
cp testdata/regr_fail.log /tmp/ci-selftest.$$/fail/run/regr.log
( CI_JOB_NAME=selftest; source ./common.sh
  ci_report_results /tmp/ci-selftest.$$/pass ); check_status "report: pass log exits 0" 0 $?
( CI_JOB_NAME=selftest; source ./common.sh
  ci_report_results /tmp/ci-selftest.$$/fail ); check_status "report: fail log exits nonzero" 1 $?
( CI_JOB_NAME=selftest; source ./common.sh
  ci_report_results /tmp/ci-selftest.$$/empty ); check_status "report: missing regr.log exits nonzero" 1 $?
rm -rf /tmp/ci-selftest.$$

echo; echo "selftest: $FAILURES failure(s)"
[[ "$FAILURES" -eq 0 ]]
```

Fixtures (format from `report_lib/text.py`): `testdata/regr_pass.log` first line `100.00% PASS 2 PASSED, 0 FAILED`; `testdata/regr_fail.log` first line `50.00% PASS 1 PASSED, 1 FAILED` followed by a plausible `Details of failing tests` block (copy the box_comment shape from `text.py`).

- [ ] **Step 2: Run selftest, verify it fails** — `bash ci/jenkins/selftest.sh`; expected: FAIL lines (common.sh does not exist), nonzero exit.

- [ ] **Step 3: Implement `ci/jenkins/common.sh`** per the Produces contract above. Key requirements beyond the contract:
  - `REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"`.
  - `set -uo pipefail` discipline; no `set -e`.
  - `ci_report_results`: `head -n1` of regr.log, match with `[[ "$line" =~ %\ PASS\ ([0-9]+)\ PASSED,\ ([0-9]+)\ FAILED ]]`; failure count from `BASH_REMATCH[2]`; on failure also print the section between `# Details of failing tests` and `# Details of passing tests`. Missing/unparsable file ⇒ `echo "ERROR: no regr.log at <path>. The run did not produce results." >&2; return 1`.
  - `ci_main` execution order: parse → usage/exit paths → resolve `CI_OUT` to absolute (`CI_OUT_ABS`; pure path math, no env) → **dry-run prints the exact command(s) and exits 0 — before env.sh, so selftest never loads modules** → source env.sh → LSF resubmission (see contract) → run make (capture exit) → always run `ci_report_results` → exit nonzero if make failed OR results failed.

- [ ] **Step 4: Run selftest, verify the common.sh checks pass** — `bash ci/jenkins/selftest.sh`; expected: all PASS, exit 0.

- [ ] **Step 5: Create the ledger and commit**

`docs/dv/process-logs/ws4/progress.md`:
```markdown
# WS4 Jenkins+LSF — process ledger

Plan: docs/superpowers/plans/2026-09-02-ws4-jenkins-lsf.md (codex pre-review: see docs/dv/reviews/).

- [ ] T1 common.sh + selftest
- [ ] T2 smoke.sh (+ gate run)
- [ ] T3 nightly.sh (+ reduced LSF run)
- [ ] T4 coverage.sh (+ reduced COV run)
- [ ] T5 Jenkinsfile + README
- [ ] T6 tt-regress assessment
- [ ] T7 docs + regress skill update
```
Tick T1, then:
```bash
git add ci/jenkins docs/dv/process-logs/ws4
git commit -m "[ci] WS4: jenkins common.sh + license-free selftest harness"
```

---

### Task 2: `ci/jenkins/smoke.sh` + real smoke run (gate evidence)

**Files:**
- Create: `ci/jenkins/smoke.sh`
- Modify: `ci/jenkins/selftest.sh` (append smoke checks)
- Create: `docs/dv/evidence/ws4-smoke-summary.txt`

**Interfaces:**
- Consumes: `ci_main` and preset globals from Task 1.
- Produces: `ci/jenkins/smoke.sh` — smoke regression, default `TEST=riscv_arithmetic_basic_test,mcounteren_test ITERATIONS=1 SEED=1` (one riscv-dv + one directed test — exercises both testlists; pinned seed for a reproducible gate; ~15 min budget).

- [ ] **Step 1: Append failing selftest checks**

```bash
# --- smoke.sh ---
out=$(./smoke.sh --dry-run 2>&1); st=$?
check_status "smoke: dry-run exits 0" 0 $st
check "smoke: default TEST" "TEST=riscv_arithmetic_basic_test,mcounteren_test" "$out"
check "smoke: default ITERATIONS" "ITERATIONS=1" "$out"
check "smoke: default SEED" "SEED=1" "$out"
check "smoke: vcs flow" "SIMULATOR=vcs" "$out"
out=$(./smoke.sh --dry-run --testlist /x/tl.yaml --directed-testlist /x/dt.yaml 2>&1)
check "smoke: suite knob riscv-dv" "RISCV-DV-TESTLIST=/x/tl.yaml" "$out"
check "smoke: suite knob directed" "DIRECTED-TESTLIST=/x/dt.yaml" "$out"
out=$(./smoke.sh --dry-run --lsf --jobs 8 --lsf-queue normal 2>&1)
check "smoke: lsf wraps bsub -K" "bsub -K" "$out"
check "smoke: lsf queue" "-q normal" "$out"
check "smoke: lsf single host" "span[hosts=1]" "$out"
check "smoke: lsf inner call drops --lsf" "smoke.sh" "$out"
case "$out" in *" --lsf "*) echo "FAIL: smoke: inner command still has --lsf"; FAILURES=$((FAILURES+1));; esac
out=$(./smoke.sh --no-such-flag 2>&1); st=$?
check_status "smoke: unknown flag exits 2" 2 $st
```

- [ ] **Step 2: Run selftest, verify new checks fail** — smoke.sh missing.

- [ ] **Step 3: Implement `ci/jenkins/smoke.sh`**

```bash
#!/usr/bin/env bash
# Smoke regression: two fast tests, one from each testlist. Budget: ~15 minutes.
# Run by hand or from Jenkins; see ci/jenkins/README.md. Options: --help.
set -uo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/common.sh"
CI_JOB_NAME=smoke
CI_TEST=riscv_arithmetic_basic_test,mcounteren_test
CI_ITERATIONS=1
CI_SEED=1
ci_main "$@"
```

- [ ] **Step 4: Run selftest, verify it passes.**

- [ ] **Step 5: Real smoke run (gate)** — `bash -lc 'ci/jenkins/smoke.sh'` with a watchdog per CLAUDE.md (poll `$OUT/run/` artifacts; budget 45 min for the fresh build). Expected: exit 0, summary `100.00% PASS 2 PASSED, 0 FAILED`. Record wall-clock; if over the 15 min budget, note actual time in README (Task 5) — do not silently re-scope the test set.

- [ ] **Step 6: Save evidence + commit** — `docs/dv/evidence/ws4-smoke-summary.txt`: the invocation, regr.log summary line, wall-clock, OUT path. Tick T2 in the ledger.

```bash
git add ci/jenkins docs/dv/evidence/ws4-smoke-summary.txt docs/dv/process-logs/ws4/progress.md
git commit -m "[ci] WS4: smoke.sh + verified smoke run"
```

---

### Task 3: `ci/jenkins/nightly.sh` + reduced run through LSF (gate evidence)

**Files:**
- Create: `ci/jenkins/nightly.sh`
- Modify: `ci/jenkins/selftest.sh` (append nightly checks)
- Create: `docs/dv/evidence/ws4-nightly-lsf-summary.txt`

**Interfaces:**
- Consumes: `ci_main` from Task 1.
- Produces: `ci/jenkins/nightly.sh` — full regression, default `TEST=all` at testlist iterations (no ITERATIONS override), default `SEED=$(date -u +%y%m%d)` (Makefile's own overnight-seed recommendation; pinned per calendar day so failures reproduce).

- [ ] **Step 1: Append failing selftest checks**

```bash
# --- nightly.sh ---
out=$(./nightly.sh --dry-run 2>&1); st=$?
check_status "nightly: dry-run exits 0" 0 $st
check "nightly: default TEST=all" "TEST=all" "$out"
check "nightly: date seed" "SEED=$(date -u +%y%m%d)" "$out"
case "$out" in *"ITERATIONS="*) echo "FAIL: nightly: must not override ITERATIONS by default"; FAILURES=$((FAILURES+1));; *) echo "PASS: nightly: testlist iterations";; esac
out=$(./nightly.sh --dry-run --test riscv_arithmetic_basic_test --iterations 2 2>&1)
check "nightly: --test override" "TEST=riscv_arithmetic_basic_test" "$out"
check "nightly: --iterations override" "ITERATIONS=2" "$out"
```

- [ ] **Step 2: Run selftest, verify new checks fail.**

- [ ] **Step 3: Implement `ci/jenkins/nightly.sh`**

```bash
#!/usr/bin/env bash
# Nightly regression: TEST=all at testlist iterations. Seed pins to the UTC date.
# Run by hand or from Jenkins; see ci/jenkins/README.md. Options: --help.
set -uo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/common.sh"
CI_JOB_NAME=nightly
CI_TEST=all
CI_SEED="$(date -u +%y%m%d)"
ci_main "$@"
```

- [ ] **Step 4: Run selftest, verify it passes.**

- [ ] **Step 5: Reduced nightly run THROUGH LSF (gate)** — proves the bsub path end-to-end:
`bash -lc 'ci/jenkins/nightly.sh --lsf --test riscv_arithmetic_basic_test,mcounteren_test --iterations 1 --jobs 4'`
Watchdog: poll `bjobs -J ibex-nightly` AND the OUT dir; budget 60 min. Expected: bsub submits to `regress`, blocks, exits 0, `regr.log` shows `0 FAILED`. If the `regress` queue rejects the job (site policy), fall back `--lsf-queue normal` and record the working default — then change the default in common.sh and re-run selftest.

- [ ] **Step 6: Save evidence + commit** — `docs/dv/evidence/ws4-nightly-lsf-summary.txt`: invocation, LSF job id + queue, summary line, wall-clock. Tick T3.

```bash
git add ci/jenkins docs/dv/evidence/ws4-nightly-lsf-summary.txt docs/dv/process-logs/ws4/progress.md
git commit -m "[ci] WS4: nightly.sh + reduced regression proven through LSF"
```

---

### Task 4: `ci/jenkins/coverage.sh` + reduced COV run (gate evidence)

**Files:**
- Create: `ci/jenkins/coverage.sh`
- Modify: `ci/jenkins/selftest.sh` (append coverage checks)
- Create: `docs/dv/evidence/ws4-coverage-summary.txt`

**Interfaces:**
- Consumes: `ci_main` from Task 1; coverage artifact layout from BUILD_AND_SIM.md (`$OUT/run/coverage/{merged.vdb,report/}`).
- Produces: `ci/jenkins/coverage.sh` — nightly + `COV=1`; after a passing run it tars the merged vdb for archiving: `$OUT/run/coverage/merged_vdb.tgz`.

- [ ] **Step 1: Append failing selftest checks**

```bash
# --- coverage.sh ---
out=$(./coverage.sh --dry-run 2>&1); st=$?
check_status "coverage: dry-run exits 0" 0 $st
check "coverage: COV=1" "COV=1" "$out"
check "coverage: default TEST=all" "TEST=all" "$out"
```

- [ ] **Step 2: Run selftest, verify new checks fail.**

- [ ] **Step 3: Implement `ci/jenkins/coverage.sh`**

```bash
#!/usr/bin/env bash
# Coverage regression: nightly + COV=1. Archives the urg report and merged vdb.
# Run by hand or from Jenkins; see ci/jenkins/README.md. Options: --help.
set -uo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/common.sh"
CI_JOB_NAME=coverage
CI_TEST=all
CI_SEED="$(date -u +%y%m%d)"
CI_COV=1
ci_main "$@"
```

Post-success vdb packaging lives in common.sh's `ci_main` (guarded by `CI_COV=1` and a passing verdict): `tar -C "$CI_OUT_ABS/run/coverage" -czf "$CI_OUT_ABS/run/coverage/merged_vdb.tgz" merged.vdb` — with an existence check that errors loudly if `merged.vdb` or `report/dashboard.txt` is missing after a "passing" COV run (a silent no-coverage pass is a fake pass).

- [ ] **Step 4: Run selftest, verify it passes.**

- [ ] **Step 5: Reduced coverage run (gate)** — `bash -lc 'ci/jenkins/coverage.sh --test riscv_arithmetic_basic_test --iterations 1 --seed 1'` (local, no --lsf — LSF already proven in T3). Watchdog 60 min. Expected: exit 0; `merged.vdb`, `report/dashboard.txt`, `merged_vdb.tgz` all present; dashboard score line captured.

- [ ] **Step 6: Save evidence + commit** — `docs/dv/evidence/ws4-coverage-summary.txt`: invocation, summary line, dashboard score line, artifact paths. Tick T4.

```bash
git add ci/jenkins docs/dv/evidence/ws4-coverage-summary.txt docs/dv/process-logs/ws4/progress.md
git commit -m "[ci] WS4: coverage.sh + verified COV run with archived vdb+report"
```

---

### Task 5: `Jenkinsfile` + `ci/jenkins/README.md` (+ LSF phase-2 feasibility note)

**Files:**
- Create: `ci/jenkins/Jenkinsfile`
- Create: `ci/jenkins/README.md`

**Interfaces:**
- Consumes: the three scripts' option set (Tasks 2–4); artifact paths `dv/uvm/core_ibex/out_ci/**/run/{regr_junit.xml,report.html,regr.log}` and `.../run/coverage/{report/**,merged_vdb.tgz}`.
- Produces: a declarative pipeline (stages Smoke → Nightly → Coverage gated by boolean params, per spec "Build → Smoke/Regress → Coverage" — the build happens inside each script's fresh OUT) and the Jenkins setup README.

- [ ] **Step 1: Write `ci/jenkins/Jenkinsfile`**

```groovy
// Declarative pipeline for the ibex auto-DV fork. Job setup: ci/jenkins/README.md.
pipeline {
    agent { label 'lsf-submit' }
    options { timestamps(); buildDiscarder(logRotator(numToKeepStr: '30')) }
    parameters {
        booleanParam(name: 'RUN_SMOKE',    defaultValue: true,  description: 'Run the smoke regression')
        booleanParam(name: 'RUN_NIGHTLY',  defaultValue: false, description: 'Run TEST=all at testlist iterations')
        booleanParam(name: 'RUN_COVERAGE', defaultValue: false, description: 'Run TEST=all with COV=1')
        string(name: 'IBEX_CONFIG',       defaultValue: 'opentitan', description: 'ibex_configs.yaml config name')
        string(name: 'TESTLIST',          defaultValue: '', description: 'riscv-dv testlist override (suite knob; empty = stock)')
        string(name: 'DIRECTED_TESTLIST', defaultValue: '', description: 'directed testlist override (empty = stock)')
        string(name: 'LSF_QUEUE',         defaultValue: 'regress', description: 'LSF queue')
        string(name: 'JOBS',              defaultValue: '8', description: 'LSF slots / make -j')
    }
    environment { SUITE_ARGS = "${params.TESTLIST ? '--testlist ' + params.TESTLIST : ''} ${params.DIRECTED_TESTLIST ? '--directed-testlist ' + params.DIRECTED_TESTLIST : ''}" }
    stages {
        stage('Smoke') {
            when { expression { params.RUN_SMOKE } }
            steps { sh "ci/jenkins/smoke.sh --lsf --lsf-queue ${params.LSF_QUEUE} --jobs ${params.JOBS} --config ${params.IBEX_CONFIG} --out out_ci/smoke-b${BUILD_NUMBER} ${SUITE_ARGS}" }
        }
        stage('Nightly') {
            when { expression { params.RUN_NIGHTLY } }
            steps { sh "ci/jenkins/nightly.sh --lsf --lsf-queue ${params.LSF_QUEUE} --jobs ${params.JOBS} --config ${params.IBEX_CONFIG} --out out_ci/nightly-b${BUILD_NUMBER} ${SUITE_ARGS}" }
        }
        stage('Coverage') {
            when { expression { params.RUN_COVERAGE } }
            steps { sh "ci/jenkins/coverage.sh --lsf --lsf-queue ${params.LSF_QUEUE} --jobs ${params.JOBS} --config ${params.IBEX_CONFIG} --out out_ci/coverage-b${BUILD_NUMBER} ${SUITE_ARGS}" }
        }
    }
    post {
        always {
            junit allowEmptyResults: true, testResults: 'dv/uvm/core_ibex/out_ci/*/run/regr_junit.xml'
            archiveArtifacts allowEmptyArchive: true, artifacts: 'dv/uvm/core_ibex/out_ci/*/run/report.html, dv/uvm/core_ibex/out_ci/*/run/regr.log, dv/uvm/core_ibex/out_ci/*/run/coverage/report/**, dv/uvm/core_ibex/out_ci/*/run/coverage/merged_vdb.tgz'
        }
        cleanup { sh 'rm -rf dv/uvm/core_ibex/out_ci' }
    }
}
```

- [ ] **Step 2: Lint-check the Jenkinsfile best-effort** — if a Jenkins server/`jenkins-cli` is unavailable (expected), validate structure by eye against the declarative-pipeline grammar and note "not lint-validated — no Jenkins reachable from this host" in README. Do not claim it was validated.

- [ ] **Step 3: Read `dv/uvm/core_ibex/scripts/metadata.py` and assess phase-2 fan-out** — confirm (or refute) the single-writer `metadata.pickle` design: who writes it, when, and whether per-test `bsub` fan-out after the build stages could race it. 3–6 sentences, goes in README §LSF (spec: "feasibility ... assessed and documented during implementation").

- [ ] **Step 4: Write `ci/jenkins/README.md`** covering, each in its own short section:
  - The three scripts: what each runs, defaults, the full option set, hand-run examples (with and without `--lsf`), measured wall-clocks from Tasks 2–4 evidence.
  - Dual-suite knob: `--testlist`/`--directed-testlist` ⇒ `RISCV-DV-TESTLIST`/`DIRECTED-TESTLIST`; the challenge's generated suites run through the same scripts by passing their testlist; note the `cocotb: 1` exclusion rule under `COCOTB=0`.
  - Jenkins job setup: repo `https://github.com/fzhangTT/ibex.git`, branch spec (`master`, `fzhang/*`), the Jenkinsfile path, suggested triggers (smoke: per-push; nightly: cron `H 2 * * *` with `RUN_NIGHTLY=true RUN_SMOKE=false`; coverage: cron `H 4 * * 6` with `RUN_COVERAGE=true RUN_SMOKE=false`).
  - Node requirements: LSF submit host (label `lsf-submit`), environment-modules, `/tools_vendor` + `/tools_risc` + `/localdev/fzhang/ws/tools` visibility, VCS licenses (two per fresh build: generator + TB).
  - Credentials: gh machine PAT (or the existing `fzhangTT` credential helper) for checkout.
  - LSF phase 1 (this delivery) vs phase 2 (per-test fan-out) with the Step-3 feasibility assessment.
  - Cleanroom-sync job: **pending WS7** — one paragraph: on every `master` push, run `ci/sync-cleanroom.sh` (lands with WS7); the job must not be created before that script exists (fail-closed).

- [ ] **Step 5: Commit** — tick T5.

```bash
git add ci/jenkins/Jenkinsfile ci/jenkins/README.md docs/dv/process-logs/ws4/progress.md
git commit -m "[ci] WS4: declarative Jenkinsfile + Jenkins/LSF setup README"
```

---

### Task 6: `docs/dv/tt-regress-assessment.md`

**Files:**
- Create: `docs/dv/tt-regress-assessment.md`

**Interfaces:**
- Consumes: the tool at `/tools_risc/tt/regression-scheduler/latest` (its `README.md` and entry scripts — `regr-info`, `regr-clean`, `regr-kill` siblings); spec §WS4 recon line.
- Produces: the written assessment the spec's "tt-regress: written assessment only" decision requires.

- [ ] **Step 1: Read the tool** — `/tools_risc/tt/regression-scheduler/latest/README.md` + skim the top-level entry points enough to verify each spec claim: YAML/DAG orchestrator skeleton; build/run backends Bazel/bzsim-only; scheduling delegated to LSF `bsub -w`; results reporting assumes internal Simscope (hard exit on unknown repos); a raw-`command:` escape hatch exists.

- [ ] **Step 2: Write the assessment (~1 page)** with sections: What tt-regress is (verified, with file paths into the install as evidence); Why it does not fit ibex today (each blocker cited to the file that shows it); What adopting it would take (the raw-`command:` route + a results backend, sized honestly); Decision (Jenkins+LSF scripts chosen — spec §Approved decisions — revisit trigger: if per-test LSF fan-out (phase 2) is ever needed, tt-regress's DAG/`bsub -w` machinery is the natural comparison point). Every claim cites a path; anything not verified is marked unverified (dv_principles §4 evidence-over-inference).

- [ ] **Step 3: Commit** — tick T6.

```bash
git add docs/dv/tt-regress-assessment.md docs/dv/process-logs/ws4/progress.md
git commit -m "[docs] WS4: tt-regress written assessment"
```

---

### Task 7: Docs integration — BUILD_AND_SIM.md section + `regress` skill update

**Files:**
- Modify: `docs/dv/BUILD_AND_SIM.md` (new "Regression scripts (ci/jenkins)" section after "Running a regression")
- Modify: `.claude/skills/regress/SKILL.md`

**Interfaces:**
- Consumes: the final script option set (Tasks 2–4), evidence files, README.
- Produces: docs that make the scripts the primary regression entry points; direct-make remains the documented fallback.

- [ ] **Step 1: Add the BUILD_AND_SIM.md section** — ASD-STE100 style (in-scope surface): the three scripts, one usage line each, the shared option table (one line per option), the dual-suite knob, LSF usage (`--lsf`, queue default, `span[hosts=1]` rationale), where results land, pointer to `ci/jenkins/README.md` for Jenkins setup. Do not duplicate the make-knob reference — link back to the existing sections (single source of truth).

- [ ] **Step 2: Update `.claude/skills/regress/SKILL.md`** — honor its binding maintenance note: scripts become the primary entry points (`ci/jenkins/smoke.sh` for quick sanity, `nightly.sh`/`coverage.sh` with `--test`/`--iterations` for scoped runs, suite knob for generated testlists), direct-make kept as the local fallback; results-reading guidance unchanged; delete the maintenance note (it is now satisfied). Keep the description line format intact.

- [ ] **Step 3: Run the validator** — `bash -lc 'source ci/env.sh >/dev/null 2>&1; python3 .codex/compat/validator.py'`; expected `VALIDATOR: PASS`.

- [ ] **Step 4: Run the full selftest one last time** — `bash ci/jenkins/selftest.sh`; expected exit 0.

- [ ] **Step 5: Commit** — tick T7; mark the ledger header with the gate status.

```bash
git add docs/dv/BUILD_AND_SIM.md .claude/skills/regress/SKILL.md docs/dv/process-logs/ws4/progress.md
git commit -m "[docs] WS4: regression-scripts docs + regress skill points at ci/jenkins"
```

---

## Workstream close (controller, not a subagent task)

After Task 7: run the `cross-review` skill for the codex post-execution review of the full WS4 commit range (plus any fix rounds it triggers), commit the review artifact under `docs/dv/reviews/`, and update the WS4 ledger to DONE. The WS4 gate is satisfied by the Task 2/3/4 evidence files (all three scripts executed by hand at least once; smoke fully; nightly/coverage reduced with the mechanism proven — including one run through LSF).
