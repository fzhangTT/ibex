# WS4 — Jenkins + LSF Regression Scripts Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Self-contained regression entry scripts (`ci/jenkins/{smoke,nightly,coverage}.sh`) runnable by hand or by Jenkins, with LSF phase-1 wrapping, a working dual-suite testlist knob plumbed through the make flow, a declarative Jenkinsfile, setup README, and the tt-regress written assessment.

**Architecture:** Three thin entry scripts share one sourced helper (`ci/jenkins/common.sh`) that parses a common option set, builds the verified `make` invocation from `docs/dv/BUILD_AND_SIM.md`, reserves a fresh output directory (stale-`metadata.pickle` guard), optionally resubmits itself under `bsub -K` (LSF phase 1: one LSF job per regression, `make -jN` inside), and parses `regr.log` for a fail-loud verdict independent of make's exit code. The dual-suite knob is plumbed for real: `metadata.py` gains overridable testlist-path fields fed from the Makefile's `--args-list`. A license-free `selftest.sh` (dry-run assertions + fixtures) gives every script a TDD cycle.

**Tech Stack:** bash, GNU make (ibex core_ibex flow), Python (`scripts/metadata.py`), LSF 10.1 (`bsub`), Jenkins declarative pipeline, VCS via `SIMULATOR=vcs`.

**Spec:** `docs/superpowers/specs/2026-09-01-auto-dv-setup-design.md` §Workstream 4, plus the session-1 handoff item 2 (dual-suite requirement) in `docs/superpowers/handoffs/2026-09-02-session1-handoff.md`.

## Global Constraints

- `source ci/env.sh` before any flow command; never `&&`-chain `module` (it exits 1 on success — env.sh handles loads). In scripts the source is **checked**: `source "$CI_ENV_SH" || exit 1` (no `set -e`, so an unchecked failing source would fall through).
- Every real sim run uses a **fresh `OUT=`** (stale `metadata.pickle` gotcha), enforced by `ci_reserve_out` — a location containing prior `run/`, `build/`, or `metadata/` is rejected, and a sentinel file guards same-path concurrent runs. `out*/` under `dv/uvm/core_ibex/` is gitignored.
- Verified command shape (BUILD_AND_SIM.md): `make SIMULATOR=vcs IBEX_CONFIG=opentitan ISS=spike TEST=<t> [ITERATIONS=n] SEED=<s> [COV=1] [COCOTB=1] OUT=<dir>`, run in `dv/uvm/core_ibex`.
- **Dual-suite requirement (handoff item 2), plumbed for real:** the Makefile's `RISCV-DV-TESTLIST`/`DIRECTED-TESTLIST` variables are today **vestigial** — `scripts/metadata.py:138,141` hardcodes both stock testlist paths and nothing consumes the variables (verified 2026-09-02). Task 2 adds the plumbing (args-list → metadata fields); the scripts' `--testlist`/`--directed-testlist` map onto those make variables; the nightly gate includes an actual alternate-testlist run.
- `TEST=all` excludes testlist entries marked `cocotb: 1` when `COCOTB=0` (commit 0498fbea) — expected, not a script bug.
- Option-value validation in `ci_parse_args` — two injection surfaces exist: Jenkins parameters enter the scripts, and every make variable is later interpolated into the Makefile's double-quoted `--args-list` recipe (a quote/semicolon breaks out of it; whitespace breaks `shlex.split` pair-splitting). Strict rules: `--jobs` and `--iterations` positive integers (GNU make rejects `-j0`; metadata rejects iterations ≤ 0); `--seed` nonnegative integer; `--lsf-queue` and `--config` match `^[A-Za-z0-9_-]+$`; `--test` matches `^[A-Za-z0-9_,]+$`; `--testlist`/`--directed-testlist` absolute-resolved paths match `^[A-Za-z0-9_/.+-]+$` (no whitespace or shell metacharacters) and must exist at run time (existence not required under `--dry-run`). Violations ⇒ usage error, exit 2. Selftest carries injection and whitespace-path attempts.
- Error messages in ci scripts are an ASD-STE100 surface (`simple-english` skill scope): short, imperative, unambiguous.
- Scripts must be `bash`, `set -uo pipefail` (NOT `-e` — result parsing must run after a failed make), executable, and self-contained (compute repo root from `BASH_SOURCE`).
- Nonzero exit on any failure; a missing `regr.log` is a failure (fail loud, never fake-pass — dv_principles §4).
- LSF: queue default `regress` (exists on this site; override `--lsf-queue`), `bsub -K` (block, propagate exit), `-R "span[hosts=1]"` (make -j needs one host). LSF compute hosts must see the workspace at the same absolute path (shared storage); the nightly gate verifies this before submitting, and README documents it.
- Evidence files go under `docs/dv/evidence/` (`ws4-*`); process ledger `docs/dv/process-logs/ws4/progress.md` gets one appended line per completed task.
- Run `.codex/compat/validator.py` after any edit to CLAUDE.md/skills/docs it validates; must stay PASS.
- Commit after every task; commit messages follow the branch's `[ci]`/`[dv]`/`[docs]` prefix convention.

---

### Task 1: `ci/jenkins/common.sh` + selftest harness

**Files:**
- Create: `ci/jenkins/common.sh`
- Create: `ci/jenkins/selftest.sh`
- Create: `ci/jenkins/testdata/regr_pass.log`, `ci/jenkins/testdata/regr_fail.log`, `ci/jenkins/testdata/env_fail.sh`
- Create: `docs/dv/process-logs/ws4/progress.md`

**Interfaces:**
- Consumes: Makefile knobs listed in Global Constraints; `regr.log` first-line format `NN.NN% PASS X PASSED, Y FAILED` (writer: `dv/uvm/core_ibex/scripts/report_lib/text.py:gen_summary_line`).
- Produces (used by Tasks 3–5):
  - `ci_parse_args "$@"` — parses the shared option set into globals `CI_TEST CI_TESTLIST CI_DIRECTED_TESTLIST CI_ITERATIONS CI_SEED CI_CONFIG CI_OUT CI_JOBS CI_LSF CI_LSF_QUEUE CI_COCOTB CI_COV CI_DRY_RUN`, applying the validation rules from Global Constraints. Callers preset job-specific defaults (`CI_JOB_NAME`, `CI_TEST`, `CI_SEED`, `CI_ITERATIONS`, `CI_COV`) **before** calling; options override. Unknown option or invalid value ⇒ usage on stderr, exit 2.
  - `ci_main "$@"` — the whole driver: parse args → resolve `CI_OUT` to absolute `CI_OUT_ABS` (pure path math, no env) → **dry-run prints the exact command(s) and exits 0 — before env.sh, so selftest never loads modules** → `source "$CI_ENV_SH" || { echo "ERROR: environment setup failed ($CI_ENV_SH). Stop." >&2; exit 1; }` → `ci_reserve_out "$CI_OUT_ABS"` → LSF resubmission (see below) or run make (capture exit) → always run `ci_report_results` → exit nonzero if make failed OR results failed. `CI_ENV_SH` defaults to `$REPO_ROOT/ci/env.sh`; overridable via environment for selftest fault injection only.
  - `ci_reserve_out <out_abs_dir>` — rejects a directory containing prior results (`run/`, `build/`, or `metadata/` present ⇒ error naming the offender + "Use a fresh --out.", return 1); then `mkdir -p` and claims ownership by creating `.ci-out-owner` with `noclobber` (existing sentinel ⇒ "owned by another running job" error) — EXCEPT when `LSB_JOBID` is set (the inner LSF invocation runs in the directory the outer submission already reserved; it must not re-claim). Separately callable so selftest can drive it with fixture dirs.
  - `ci_report_results <out_abs_dir>` — parses `<out_abs_dir>/run/regr.log`: exit 0 iff the file exists and reports `0 FAILED`; prints the summary line and, on failure, the failing-test detail block. Separately callable for fixtures.
- Option set (all of Tasks 3–5 expose exactly this):
  `--test LIST --testlist YAML --directed-testlist YAML --iterations N --seed S --config NAME --out DIR --jobs N --lsf --lsf-queue Q --cocotb --dry-run --help`
- Defaults: `CI_CONFIG=opentitan`, `CI_JOBS=4`, `CI_LSF=0`, `CI_LSF_QUEUE=${LSF_QUEUE:-regress}`, `CI_OUT=out_ci/${CI_JOB_NAME}-$(date -u +%Y%m%d-%H%M%S)` (relative to `dv/uvm/core_ibex`; a same-second collision is caught by `ci_reserve_out`, which turns it into a loud error, never silent reuse).
- LSF mode: after reserving `CI_OUT_ABS` (so the `-o` log's parent exists), `ci_main` re-executes the calling script under `bsub -K -J "ibex-${CI_JOB_NAME}" -q "$CI_LSF_QUEUE" -n "$CI_JOBS" -R "span[hosts=1]" -o "$CI_OUT_ABS/lsf.log"` with **all values resolved to explicit flags and `--lsf` removed** (so the inner invocation is deterministic and the timestamped OUT is fixed once). `--dry-run --lsf` prints the full bsub command without submitting.
- Make command shape (built as an array, printed verbatim by dry-run):
  `make -C "$REPO_ROOT/dv/uvm/core_ibex" -j"$CI_JOBS" SIMULATOR=vcs ISS=spike IBEX_CONFIG="$CI_CONFIG" TEST="$CI_TEST" SEED="$CI_SEED" OUT="$CI_OUT"` plus, only when set: `ITERATIONS=`, `COV=1`, `COCOTB=1`, `RISCV-DV-TESTLIST=`, `DIRECTED-TESTLIST=`.

- [ ] **Step 1: Write the failing selftest**

`ci/jenkins/selftest.sh` — license-free checks; starts with common.sh unit checks (script-level checks are appended by Tasks 3–5):

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
T=$(mktemp -d)

# --- common.sh: ci_report_results against fixtures ---
mkdir -p "$T/pass/run" "$T/fail/run" "$T/empty/run"
cp testdata/regr_pass.log "$T/pass/run/regr.log"
cp testdata/regr_fail.log "$T/fail/run/regr.log"
( CI_JOB_NAME=selftest; source ./common.sh; ci_report_results "$T/pass" ); check_status "report: pass log exits 0" 0 $?
( CI_JOB_NAME=selftest; source ./common.sh; ci_report_results "$T/fail" ); check_status "report: fail log exits nonzero" 1 $?
( CI_JOB_NAME=selftest; source ./common.sh; ci_report_results "$T/empty" ); check_status "report: missing regr.log exits nonzero" 1 $?

# --- common.sh: ci_reserve_out ---
mkdir -p "$T/poisoned/run" "$T/owned"; touch "$T/owned/.ci-out-owner"
( CI_JOB_NAME=selftest; source ./common.sh; ci_reserve_out "$T/fresh" ); check_status "reserve: fresh dir ok" 0 $?
[ -f "$T/fresh/.ci-out-owner" ] && echo "PASS: reserve: sentinel created" || { echo "FAIL: reserve: no sentinel"; FAILURES=$((FAILURES+1)); }
( CI_JOB_NAME=selftest; source ./common.sh; ci_reserve_out "$T/poisoned" ); check_status "reserve: prior run/ rejected" 1 $?
( CI_JOB_NAME=selftest; source ./common.sh; unset LSB_JOBID; ci_reserve_out "$T/owned" ); check_status "reserve: foreign sentinel rejected" 1 $?
( CI_JOB_NAME=selftest; source ./common.sh; LSB_JOBID=12345 ci_reserve_out "$T/owned" ); check_status "reserve: inner LSF run accepts reserved dir" 0 $?

rm -rf "$T"
echo; echo "selftest: $FAILURES failure(s)"
[[ "$FAILURES" -eq 0 ]]
```

Fixtures (format from `report_lib/text.py`): `testdata/regr_pass.log` first line `100.00% PASS 2 PASSED, 0 FAILED`; `testdata/regr_fail.log` first line `50.00% PASS 1 PASSED, 1 FAILED` followed by a plausible `Details of failing tests` block (copy the box_comment shape from `text.py`). `testdata/env_fail.sh` contains just `return 1` (a sourceable file that fails; used by Task 3's checks).

- [ ] **Step 2: Run selftest, verify it fails** — `bash ci/jenkins/selftest.sh`; expected: FAIL lines (common.sh does not exist), nonzero exit.

- [ ] **Step 3: Implement `ci/jenkins/common.sh`** per the Produces contract above. Key requirements beyond the contract:
  - `REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"`; `CI_ENV_SH="${CI_ENV_SH:-$REPO_ROOT/ci/env.sh}"`.
  - `set -uo pipefail` discipline; no `set -e`; every step that can fail is explicitly checked.
  - `ci_report_results`: `head -n1` of regr.log, match with `[[ "$line" =~ %\ PASS\ ([0-9]+)\ PASSED,\ ([0-9]+)\ FAILED ]]`; failure count from `BASH_REMATCH[2]`; on failure also print the section between `# Details of failing tests` and `# Details of passing tests`. Missing/unparsable file ⇒ `echo "ERROR: no regr.log at <path>. The run did not produce results." >&2; return 1`.

- [ ] **Step 4: Run selftest, verify the common.sh checks pass** — `bash ci/jenkins/selftest.sh`; expected: all PASS, exit 0.

- [ ] **Step 5: Create the ledger and commit**

`docs/dv/process-logs/ws4/progress.md`:
```markdown
# WS4 Jenkins+LSF — process ledger

Plan: docs/superpowers/plans/2026-09-02-ws4-jenkins-lsf.md (codex pre-review rounds: see docs/dv/reviews/).

- [ ] T1 common.sh + selftest
- [ ] T2 dual-suite testlist plumbing (metadata.py + Makefile)
- [ ] T3 smoke.sh (+ gate run)
- [ ] T4 nightly.sh (+ reduced LSF run + alternate-testlist run)
- [ ] T5 coverage.sh (+ reduced COV run)
- [ ] T6 Jenkinsfile + README
- [ ] T7 tt-regress assessment
- [ ] T8 docs + regress skill update
```
Tick T1, then:
```bash
git add ci/jenkins docs/dv/process-logs/ws4
git commit -m "[ci] WS4: jenkins common.sh + license-free selftest harness"
```

---

### Task 2: Dual-suite testlist plumbing (`metadata.py` + Makefile)

**Files:**
- Modify: `dv/uvm/core_ibex/scripts/metadata.py` (new fields + `__post_init__` resolution, around lines 138/141)
- Modify: `dv/uvm/core_ibex/Makefile` (lines 44–45 defaults + `--args-list` block at lines ~80–85)
- Create: `ci/jenkins/check_testlist_knob.sh`

**Interfaces:**
- Consumes: `RegressionMetadata.arg_list_initializer` (`scripts/metadata.py:176` — parses `--args-list` `KEY=VALUE` pairs, lowercases keys, matches dataclass field names, typecasts by field type; only `str`/`int`/`bool` are handled, so **new fields must be `str`**).
- Produces: `make RISCV-DV-TESTLIST=<yaml>` / `DIRECTED-TESTLIST=<yaml>` actually swap the suites; empty (the new default) means stock. Tasks 3–5's `--testlist`/`--directed-testlist` flags rely on this.

- [ ] **Step 1: Write the failing check** — `ci/jenkins/check_testlist_knob.sh`:

```bash
#!/usr/bin/env bash
# Prove the testlist-override knob reaches metadata (no simulator needed).
set -uo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
source "$REPO_ROOT/ci/env.sh" || { echo "ERROR: environment setup failed. Stop." >&2; exit 1; }
cd "$REPO_ROOT/dv/uvm/core_ibex"
PYTHONPATH=$(python3 -c 'from scripts.setup_imports import get_pythonpath; get_pythonpath()') \
python3 - <<'EOF'
# metadata.py is runtime-typechecked against pathlib3x, not stdlib pathlib.
import pathlib3x as pathlib
import sys, tempfile
sys.path.insert(0, 'scripts')
from metadata import RegressionMetadata
with tempfile.TemporaryDirectory() as td:
    td = pathlib.Path(td)
    md = RegressionMetadata.arg_list_initializer(
        dir_metadata=td/'metadata', dir_out=td, git_commit='selfcheck',
        args_list='SEED=1 RISCVDV_TESTLIST=/tmp/alt_testlist.yaml DIRECTED_TESTLIST=/tmp/alt_directed.yaml')
    assert str(md.ibex_riscvdv_testlist) == '/tmp/alt_testlist.yaml', md.ibex_riscvdv_testlist
    assert str(md.directed_test_data) == '/tmp/alt_directed.yaml', md.directed_test_data
    md2 = RegressionMetadata.arg_list_initializer(
        dir_metadata=td/'m2', dir_out=td, git_commit='selfcheck', args_list='SEED=1')
    assert md2.ibex_riscvdv_testlist.name == 'testlist.yaml', md2.ibex_riscvdv_testlist
    assert md2.directed_test_data.name == 'directed_testlist.yaml', md2.directed_test_data
print('check_testlist_knob: PASS')
EOF
```
Adjust the `arg_list_initializer` call signature to the real one when writing (read `scripts/metadata.py:176-240` first; if `git_commit` or another parameter differs, follow the source — the assertions are the contract, not the exact constructor line).

- [ ] **Step 2: Run it, verify it fails** — `bash ci/jenkins/check_testlist_knob.sh`; expected: AssertionError/AttributeError (fields don't exist yet).

- [ ] **Step 3: Implement the metadata fields** — in `RegressionMetadata`: add near the other args-list-settable fields
```python
riscvdv_testlist  : str = ''   # override path for riscv_dv_extension/testlist.yaml ('' = stock)
directed_testlist : str = ''   # override path for directed_tests/directed_testlist.yaml ('' = stock)
```
and in `__post_init__` replace the two hardcoded assignments (lines ~138/141):
```python
self.ibex_riscvdv_testlist = (pathlib.Path(self.riscvdv_testlist).resolve()
                              if self.riscvdv_testlist
                              else self.ibex_riscvdv_customtarget/'testlist.yaml')
...
self.directed_test_data = (pathlib.Path(self.directed_testlist).resolve()
                           if self.directed_testlist
                           else self.directed_test_dir/'directed_testlist.yaml')
```
(Relative override paths resolve against the make working dir `dv/uvm/core_ibex`; the ci scripts pass absolute paths.)

- [ ] **Step 4: Plumb the Makefile** — change lines 44–45 to empty defaults with an intent comment:
```make
# Alternate-suite knobs (dual-suite requirement): set to a testlist yaml path to
# swap the riscv-dv / directed suite; empty = stock testlists.
RISCV-DV-TESTLIST   :=
DIRECTED-TESTLIST   :=
```
and append to the `--args-list` string: `RISCVDV_TESTLIST=$(RISCV-DV-TESTLIST) DIRECTED_TESTLIST=$(DIRECTED-TESTLIST)`. NOTE: with empty values this yields bare `RISCVDV_TESTLIST=` pairs — verify `arg_list_initializer`'s `pair.split('=', maxsplit=1)` tolerates empty values and the `str` typecast keeps `''` (it does by inspection, but the Step-5 rerun is the proof).

- [ ] **Step 5: Add the Make-boundary check** — the unit check alone would pass even if the Makefile plumbing were absent, so `check_testlist_knob.sh` also proves the make → args-list hop (no license; `make -n` prints the recipe without running it):

```bash
recipe=$(make -C "$REPO_ROOT/dv/uvm/core_ibex" -n run \
           RISCV-DV-TESTLIST=/tmp/alt_testlist.yaml DIRECTED-TESTLIST=/tmp/alt_directed.yaml \
           TEST=all SEED=1 SIMULATOR=vcs 2>/dev/null)
case "$recipe" in
  *"RISCVDV_TESTLIST=/tmp/alt_testlist.yaml"*) : ;;
  *) echo "FAIL: Makefile does not pass RISCV-DV-TESTLIST into --args-list" >&2; exit 1;;
esac
case "$recipe" in
  *"DIRECTED_TESTLIST=/tmp/alt_directed.yaml"*) : ;;
  *) echo "FAIL: Makefile does not pass DIRECTED-TESTLIST into --args-list" >&2; exit 1;;
esac
echo "check_testlist_knob: make-boundary PASS"
```

- [ ] **Step 6: Run the check, verify it passes end-to-end** — `bash ci/jenkins/check_testlist_knob.sh` ⇒ both PASS lines (unit + make-boundary). Also rerun `bash ci/jenkins/selftest.sh` (no regression) and one stock dry-run sanity: `make -C dv/uvm/core_ibex -n run TEST=riscv_arithmetic_basic_test SEED=1 SIMULATOR=vcs 2>&1 | head` still constructs with empty overrides.

- [ ] **Step 7: Commit** — tick T2.

```bash
git add dv/uvm/core_ibex/scripts/metadata.py dv/uvm/core_ibex/Makefile ci/jenkins/check_testlist_knob.sh docs/dv/process-logs/ws4/progress.md
git commit -m "[dv] WS4: plumb RISCV-DV-TESTLIST/DIRECTED-TESTLIST through metadata (dual-suite knob)"
```

---

### Task 3: `ci/jenkins/smoke.sh` + real smoke run (gate evidence)

**Files:**
- Create: `ci/jenkins/smoke.sh`
- Modify: `ci/jenkins/selftest.sh` (append smoke checks)
- Create: `docs/dv/evidence/ws4-smoke-summary.txt`

**Interfaces:**
- Consumes: `ci_main` and preset globals from Task 1.
- Produces: `ci/jenkins/smoke.sh` — smoke regression, default `TEST=riscv_arithmetic_basic_test,mcounteren_test ITERATIONS=1 SEED=1` (one riscv-dv + one directed test — exercises both testlists; pinned seed for a reproducible gate; ~15 min budget).

**Recorded policy exemption (single-source-of-truth):** the smoke *selection* (two test names + `ITERATIONS=1` + `SEED=1`) is CI policy, defined exactly once, in `smoke.sh`. The test definitions stay canonical in the testlist YAMLs; referencing entries by name is the flow's normal selection interface (`TEST=` takes names everywhere). This exemption is recorded here, in a `smoke.sh` header comment ("smoke selection is CI policy; defined only here"), and in the README (Task 6). No derived/tagged smoke list is built (YAGNI — two entries).

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
case "$out" in *" --lsf"*) echo "FAIL: smoke: inner command still carries --lsf"; FAILURES=$((FAILURES+1));; *) echo "PASS: smoke: inner command drops --lsf";; esac
out=$(./smoke.sh --no-such-flag 2>&1); st=$?
check_status "smoke: unknown flag exits 2" 2 $st
out=$(./smoke.sh --dry-run --jobs banana 2>&1); st=$?
check_status "smoke: non-integer --jobs exits 2" 2 $st
out=$(./smoke.sh --dry-run --lsf --lsf-queue 'q; rm -rf /' 2>&1); st=$?
check_status "smoke: queue token validation exits 2" 2 $st
out=$(./smoke.sh --dry-run --config 'opentitan"; touch /tmp/pwned; echo "' 2>&1); st=$?
check_status "smoke: config injection attempt exits 2" 2 $st
out=$(./smoke.sh --dry-run --test 'a_test;b' 2>&1); st=$?
check_status "smoke: test-name metacharacter exits 2" 2 $st
out=$(./smoke.sh --dry-run --testlist '/tmp/has space.yaml' 2>&1); st=$?
check_status "smoke: whitespace testlist path exits 2" 2 $st
out=$(./smoke.sh --dry-run --jobs 0 2>&1); st=$?
check_status "smoke: --jobs 0 exits 2" 2 $st
out=$(./smoke.sh --dry-run --iterations 0 2>&1); st=$?
check_status "smoke: --iterations 0 exits 2" 2 $st
out=$(CI_ENV_SH="$PWD/testdata/env_fail.sh" ./smoke.sh --out "$(mktemp -d)/o" 2>&1); st=$?
check_status "smoke: failing env.sh stops the run" 1 $st
check "smoke: env failure message" "environment setup failed" "$out"
```

- [ ] **Step 2: Run selftest, verify new checks fail** — smoke.sh missing.

- [ ] **Step 3: Implement `ci/jenkins/smoke.sh`**

```bash
#!/usr/bin/env bash
# Smoke regression: two fast tests, one from each testlist. Budget: ~15 minutes.
# Smoke selection is CI policy; it is defined only here (see README §Smoke policy).
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

- [ ] **Step 5: Real smoke run (gate)** — `bash -lc 'ci/jenkins/smoke.sh'` with a watchdog per CLAUDE.md (poll `$OUT/run/` artifacts; budget 45 min for the fresh build). Expected: exit 0, summary `100.00% PASS 2 PASSED, 0 FAILED`. Record wall-clock; if over the 15 min budget, note actual time in README (Task 6) — do not silently re-scope the test set.

- [ ] **Step 6: Save evidence + commit** — `docs/dv/evidence/ws4-smoke-summary.txt`: the invocation, regr.log summary line, wall-clock, OUT path. Tick T3 in the ledger.

```bash
git add ci/jenkins docs/dv/evidence/ws4-smoke-summary.txt docs/dv/process-logs/ws4/progress.md
git commit -m "[ci] WS4: smoke.sh + verified smoke run"
```

---

### Task 4: `ci/jenkins/nightly.sh` + reduced LSF run + alternate-testlist run (gate evidence)

**Files:**
- Create: `ci/jenkins/nightly.sh`
- Modify: `ci/jenkins/selftest.sh` (append nightly checks)
- Create: `docs/dv/evidence/ws4-nightly-lsf-summary.txt`
- Create: `docs/dv/evidence/ws4-alt-testlist-summary.txt`

**Interfaces:**
- Consumes: `ci_main` from Task 1; the Task 2 plumbing.
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

- [ ] **Step 5: LSF workspace-visibility probe (pre-gate)** — compute hosts must see this workspace at the same absolute path:
`bash -lc 'source ci/env.sh && bsub -K -q regress -o /dev/null "test -d $PWD && test -r $PWD/ci/env.sh && echo VISIBLE"'`
If it fails, this workspace root (`/localdev/...`) is submit-host-local: record that in README §Storage, and run the Step-6 gate from a clone on shared storage (record which path was used in the evidence file). Do not skip the gate.

- [ ] **Step 6: Reduced nightly run THROUGH LSF (gate)** — proves the bsub path end-to-end:
`bash -lc 'ci/jenkins/nightly.sh --lsf --test riscv_arithmetic_basic_test,mcounteren_test --iterations 1 --jobs 4'`
Watchdog: poll `bjobs -J ibex-nightly` AND the OUT dir; budget 60 min. Expected: bsub submits to `regress`, blocks, exits 0, `regr.log` shows `0 FAILED`. If the `regress` queue rejects the job (site policy), fall back `--lsf-queue normal` and record the working default — then change the default in common.sh and re-run selftest.

- [ ] **Step 7: Alternate-testlist run (gate for the dual-suite knob)** — build a one-entry testlist in a temp dir by extracting the `riscv_arithmetic_basic_test` entry from the stock `riscv_dv_extension/testlist.yaml` (copy the YAML entry verbatim into `<tmp>/alt_testlist.yaml`), then:
`bash -lc 'ci/jenkins/nightly.sh --test all_riscvdv --testlist <tmp>/alt_testlist.yaml --iterations 1 --seed 1'`
Expected: exit 0 and `regr.log` lists EXACTLY one test (`riscv_arithmetic_basic_test.1`) — proving the override selected the alternate suite, not the stock one (which would run many tests). Save invocation + the temp testlist content + the regr.log summary to `docs/dv/evidence/ws4-alt-testlist-summary.txt`.

- [ ] **Step 8: Save evidence + commit** — `docs/dv/evidence/ws4-nightly-lsf-summary.txt`: invocation, LSF job id + queue, visibility-probe result, summary line, wall-clock. Tick T4.

```bash
git add ci/jenkins docs/dv/evidence/ws4-nightly-lsf-summary.txt docs/dv/evidence/ws4-alt-testlist-summary.txt docs/dv/process-logs/ws4/progress.md
git commit -m "[ci] WS4: nightly.sh + LSF and alternate-testlist gate runs"
```

---

### Task 5: `ci/jenkins/coverage.sh` + reduced COV run (gate evidence)

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

- [ ] **Step 5: Reduced coverage run (gate)** — `bash -lc 'ci/jenkins/coverage.sh --test riscv_arithmetic_basic_test --iterations 1 --seed 1'` (local, no --lsf — LSF already proven in T4). Watchdog 60 min. Expected: exit 0; `merged.vdb`, `report/dashboard.txt`, `merged_vdb.tgz` all present; dashboard score line captured.

- [ ] **Step 6: Save evidence + commit** — `docs/dv/evidence/ws4-coverage-summary.txt`: invocation, summary line, dashboard score line, artifact paths. Tick T5.

```bash
git add ci/jenkins docs/dv/evidence/ws4-coverage-summary.txt docs/dv/process-logs/ws4/progress.md
git commit -m "[ci] WS4: coverage.sh + verified COV run with archived vdb+report"
```

---

### Task 6: `Jenkinsfile` + `ci/jenkins/README.md` (+ LSF phase-2 feasibility note)

**Files:**
- Create: `ci/jenkins/Jenkinsfile`
- Create: `ci/jenkins/README.md`

**Interfaces:**
- Consumes: the three scripts' option set (Tasks 3–5); artifact paths `dv/uvm/core_ibex/out_ci/**/run/{regr_junit.xml,report.html,regr.log}` and `.../run/coverage/{report/**,merged_vdb.tgz}`.
- Produces: a declarative pipeline (stages Smoke → Nightly → Coverage gated by boolean params, per spec "Build → Smoke/Regress → Coverage" — the build happens inside each script's fresh OUT) and the Jenkins setup README.

- [ ] **Step 1: Write `ci/jenkins/Jenkinsfile`** — parameters pass to the shell **only via environment variables, quoted at use**; suite args are built as a bash array inside the step (no Groovy interpolation into script text):

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
    environment {
        P_CONFIG = "${params.IBEX_CONFIG}"
        P_TL     = "${params.TESTLIST}"
        P_DTL    = "${params.DIRECTED_TESTLIST}"
        P_QUEUE  = "${params.LSF_QUEUE}"
        P_JOBS   = "${params.JOBS}"
    }
    stages {
        stage('Smoke') {
            when { expression { params.RUN_SMOKE } }
            steps {
                sh '''
                    set -u
                    args=( --lsf --lsf-queue "$P_QUEUE" --jobs "$P_JOBS" --config "$P_CONFIG" --out "out_ci/smoke-b${BUILD_NUMBER}" )
                    [ -n "$P_TL" ]  && args+=( --testlist "$P_TL" )
                    [ -n "$P_DTL" ] && args+=( --directed-testlist "$P_DTL" )
                    ci/jenkins/smoke.sh "${args[@]}"
                '''
            }
        }
        stage('Nightly') {
            when { expression { params.RUN_NIGHTLY } }
            steps {
                sh '''
                    set -u
                    args=( --lsf --lsf-queue "$P_QUEUE" --jobs "$P_JOBS" --config "$P_CONFIG" --out "out_ci/nightly-b${BUILD_NUMBER}" )
                    [ -n "$P_TL" ]  && args+=( --testlist "$P_TL" )
                    [ -n "$P_DTL" ] && args+=( --directed-testlist "$P_DTL" )
                    ci/jenkins/nightly.sh "${args[@]}"
                '''
            }
        }
        stage('Coverage') {
            when { expression { params.RUN_COVERAGE } }
            steps {
                sh '''
                    set -u
                    args=( --lsf --lsf-queue "$P_QUEUE" --jobs "$P_JOBS" --config "$P_CONFIG" --out "out_ci/coverage-b${BUILD_NUMBER}" )
                    [ -n "$P_TL" ]  && args+=( --testlist "$P_TL" )
                    [ -n "$P_DTL" ] && args+=( --directed-testlist "$P_DTL" )
                    ci/jenkins/coverage.sh "${args[@]}"
                '''
            }
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
(Script-side validation from Task 1 — integer `--jobs`, token-only `--lsf-queue` — is the enforcement backstop for anything a parameter still carries.)

- [ ] **Step 2: Lint-check the Jenkinsfile best-effort** — if a Jenkins server/`jenkins-cli` is unavailable (expected), validate structure by eye against the declarative-pipeline grammar and note "not lint-validated — no Jenkins reachable from this host" in README. Do not claim it was validated.

- [ ] **Step 3: Read `dv/uvm/core_ibex/scripts/metadata.py` and assess phase-2 fan-out** — confirm (or refute) the single-writer `metadata.pickle` design: who writes it, when (note `create_metadata` runs once in the top Makefile before `wrapper.mk`), and whether per-test `bsub` fan-out after the build stages could race it or the per-test pickles. 3–6 sentences, goes in README §LSF (spec: "feasibility ... assessed and documented during implementation").

- [ ] **Step 4: Write `ci/jenkins/README.md`** covering, each in its own short section:
  - The three scripts: what each runs, defaults, the full option set, hand-run examples (with and without `--lsf`), measured wall-clocks from Tasks 3–5 evidence.
  - **Smoke policy:** the recorded exemption from Task 3 — smoke selection (2 test names, ITERATIONS=1, SEED=1) is CI policy defined only in `smoke.sh`.
  - Dual-suite knob: `--testlist`/`--directed-testlist` ⇒ `RISCV-DV-TESTLIST`/`DIRECTED-TESTLIST` ⇒ metadata override (Task 2); the challenge's generated suites run through the same scripts by passing their testlist; note the `cocotb: 1` exclusion rule under `COCOTB=0`; point at the alternate-testlist gate evidence.
  - Jenkins job setup: repo `https://github.com/fzhangTT/ibex.git`, branch spec (`master`, `fzhang/*`), the Jenkinsfile path. **Scheduling:** plain `cron` triggers cannot set parameters, so scheduled nightly/coverage need one of: (a) the `parameterizedCron` plugin — `parameterizedCron('H 2 * * * %RUN_SMOKE=false;RUN_NIGHTLY=true')` and `('H 4 * * 6 %RUN_SMOKE=false;RUN_COVERAGE=true')`, or (b) three Jenkins jobs sharing this Jenkinsfile with per-job parameter-default overrides (smoke: per-push; nightly, coverage: their cron). Which is available is decided at Jenkins-setup time; both are documented, neither is assumed.
  - Node requirements: LSF submit host (label `lsf-submit`), environment-modules, `/tools_vendor` + `/tools_risc` + `/localdev/fzhang/ws/tools` visibility, VCS licenses (two per fresh build: generator + TB).
  - **Storage:** the Jenkins workspace AND the OUT path must be visible at the same absolute path on LSF compute hosts (shared storage); record the Task 4 probe result, and the caveat that `/localdev/*` paths are typically submit-host-local.
  - Credentials: gh machine PAT (or the existing `fzhangTT` credential helper) for checkout.
  - LSF phase 1 (this delivery) vs phase 2 (per-test fan-out) with the Step-3 feasibility assessment.
  - Cleanroom-sync job: **pending WS7** — one paragraph: on every `master` push, run `ci/sync-cleanroom.sh` (lands with WS7); the job must not be created before that script exists (fail-closed).

- [ ] **Step 5: Commit** — tick T6.

```bash
git add ci/jenkins/Jenkinsfile ci/jenkins/README.md docs/dv/process-logs/ws4/progress.md
git commit -m "[ci] WS4: declarative Jenkinsfile + Jenkins/LSF setup README"
```

---

### Task 7: `docs/dv/tt-regress-assessment.md`

**Files:**
- Create: `docs/dv/tt-regress-assessment.md`

**Interfaces:**
- Consumes: the tool at `/tools_risc/tt/regression-scheduler/latest` (its `README.md` and entry scripts — `regr-info`, `regr-clean`, `regr-kill` siblings); spec §WS4 recon line.
- Produces: the written assessment the spec's "tt-regress: written assessment only" decision requires.

- [ ] **Step 1: Read the tool** — `/tools_risc/tt/regression-scheduler/latest/README.md` + skim the top-level entry points enough to verify each spec claim: YAML/DAG orchestrator skeleton; build/run backends Bazel/bzsim-only; scheduling delegated to LSF `bsub -w`; results reporting assumes internal Simscope (hard exit on unknown repos); a raw-`command:` escape hatch exists.

- [ ] **Step 2: Write the assessment (~1 page)** with sections: What tt-regress is (verified, with file paths into the install as evidence); Why it does not fit ibex today (each blocker cited to the file that shows it); What adopting it would take (the raw-`command:` route + a results backend, sized honestly); Decision (Jenkins+LSF scripts chosen — spec §Approved decisions — revisit trigger: if per-test LSF fan-out (phase 2) is ever needed, tt-regress's DAG/`bsub -w` machinery is the natural comparison point). Every claim cites a path; anything not verified is marked unverified (dv_principles §4 evidence-over-inference).

- [ ] **Step 3: Commit** — tick T7.

```bash
git add docs/dv/tt-regress-assessment.md docs/dv/process-logs/ws4/progress.md
git commit -m "[docs] WS4: tt-regress written assessment"
```

---

### Task 8: Docs integration — BUILD_AND_SIM.md section + `regress` skill update

**Files:**
- Modify: `docs/dv/BUILD_AND_SIM.md` (new "Regression scripts (ci/jenkins)" section after "Running a regression")
- Modify: `.claude/skills/regress/SKILL.md`

**Interfaces:**
- Consumes: the final script option set (Tasks 3–5), evidence files, README.
- Produces: docs that make the scripts the primary regression entry points; direct-make remains the documented fallback.

- [ ] **Step 1: Add the BUILD_AND_SIM.md section** — ASD-STE100 style (in-scope surface): the three scripts, one usage line each, the shared option table (one line per option), the dual-suite knob (including that `RISCV-DV-TESTLIST`/`DIRECTED-TESTLIST` are now live make knobs plumbed through metadata), LSF usage (`--lsf`, queue default, `span[hosts=1]` rationale, shared-storage requirement), where results land, pointer to `ci/jenkins/README.md` for Jenkins setup. Do not duplicate the make-knob reference — link back to the existing sections (single source of truth).

- [ ] **Step 2: Update `.claude/skills/regress/SKILL.md`** — honor its binding maintenance note: scripts become the primary entry points (`ci/jenkins/smoke.sh` for quick sanity, `nightly.sh`/`coverage.sh` with `--test`/`--iterations` for scoped runs, suite knob for generated testlists), direct-make kept as the local fallback; results-reading guidance unchanged; delete the maintenance note (it is now satisfied). Keep the description line format intact.

- [ ] **Step 3: Run the validator** — `bash -lc 'source ci/env.sh >/dev/null 2>&1; python3 .codex/compat/validator.py'`; expected `VALIDATOR: PASS`.

- [ ] **Step 4: Run the full selftest and the testlist-knob check one last time** — `bash ci/jenkins/selftest.sh` and `bash ci/jenkins/check_testlist_knob.sh`; expected exit 0 / PASS.

- [ ] **Step 5: Commit** — tick T8; mark the ledger header with the gate status.

```bash
git add docs/dv/BUILD_AND_SIM.md .claude/skills/regress/SKILL.md docs/dv/process-logs/ws4/progress.md
git commit -m "[docs] WS4: regression-scripts docs + regress skill points at ci/jenkins"
```

---

## Workstream close (controller, not a subagent task)

After Task 8: run the `cross-review` skill for the codex post-execution review of the full WS4 commit range (plus any fix rounds it triggers), commit the review artifact under `docs/dv/reviews/`, and update the WS4 ledger to DONE. The WS4 gate is satisfied by the Task 3/4/5 evidence files (all three scripts executed by hand at least once; smoke fully; nightly/coverage reduced with the mechanism proven — including one run through LSF and one through an alternate testlist).

## Review disposition (codex pre-review round 1 — REQUEST-CHANGES)

Findings from `docs/dv/reviews/2026-09-02-codex-plan-2026-09-02-ws4-jenkins-lsf-round1.md`, each addressed in rev 2:
1. **[critical] testlist vars unused** — CONFIRMED against `metadata.py:138,141`; new Task 2 plumbs args-list → metadata fields with a red→green check (`check_testlist_knob.sh`) and Task 4 Step 7 adds the alternate-testlist gate run.
2. **[high] smoke selection duplication** — explicit policy exemption recorded (Task 3 header + smoke.sh comment + README §Smoke policy).
3. **[high] Jenkins parameter injection** — parameters now flow through `environment {}` into single-quoted `sh` blocks, quoted at use, suite args built as a bash array; script-side value validation added (Global Constraints + Task 3 selftest checks).
4. **[high] stale/colliding OUT** — `ci_reserve_out`: prior-results rejection + noclobber sentinel ownership; selftest fixtures cover fresh/poisoned/owned/inner-LSF cases.
5. **[high] lsf.log parent missing** — reservation (mkdir -p) happens before `bsub`; inner invocation accepts the reserved dir via the `LSB_JOBID` carve-out.
6. **[high] unchecked env.sh source** — explicit `|| exit 1` with message; fault-injection selftest via `CI_ENV_SH` + `testdata/env_fail.sh`.
7. **[medium] cron cannot set params** — README documents `parameterizedCron` and the three-job-defaults alternative; neither assumed.
8. **[medium] LSF workspace visibility** — Task 4 Step 5 probe before the LSF gate; README §Storage requirement.

## Review disposition (codex pre-review round 2 — REQUEST-CHANGES)

Findings from `docs/dv/reviews/2026-09-02-codex-plan-2026-09-02-ws4-jenkins-lsf-round2.md`, each addressed in this revision:
1. **[high] second injection boundary in the make `--args-list` recipe** — strict value validation chosen (the offered alternative to structured transport): charset rules for `--config`/`--test`/testlist paths (no whitespace or shell metacharacters), with injection and whitespace-path selftest checks added in Task 3.
2. **[high] stdlib pathlib vs runtime-typechecked pathlib3x** — the check script now uses `import pathlib3x as pathlib`.
3. **[medium] unit check bypasses the Make boundary** — Task 2 Step 5 adds a `make -n` recipe check proving both variables reach `--args-list`; the Task 4 alternate-testlist run stays as the end-to-end proof.
4. **[medium] zero permitted for `--jobs`/`--iterations`** — both now require positive integers (`-j0` rejected by make; iterations ≤ 0 rejected by metadata); `--seed` stays nonnegative; selftest checks added.
