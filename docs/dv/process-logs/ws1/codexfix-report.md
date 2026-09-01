# Codex post-execution review fixes (2026-09-01-codex-review-02-ws1-post-execution.md)

Repo: /localdev/fzhang/ws/ibex, branch `fzhang/auto-dv-setup`.
Verdict addressed: REQUEST-CHANGES, 4 major findings, all fixed per the controller's scoped rulings.

Commits:
- `56acf9c8` [ci] Make env.sh nounset-safe, load gcc-toolset-11, and fail loud
- `3f381447` [docs] Rerun WS1 gates at final HEAD, commit raw evidence

## Finding 1 — env.sh robustness (`ci/env.sh:11`, `ci/env.sh:30`)

Scoped ruling: keep the existing per-load `|| true` guards (site's `module` command exits 1 on success), fix three things instead of the codex-suggested `set -e`-everything rewrite.

**(a) nounset-safe.** `bash -c 'set -euo pipefail; source ci/env.sh'` failed with `RISCV_TOOLCHAIN: unbound variable` at line 30 on a first source, because `$RISCV_TOOLCHAIN`/`$_IBEX_RV_TC_AUTO` were read before ever being set. Fixed by guarding both expansions: `[ -n "${RISCV_TOOLCHAIN:-}" ] && [ "${RISCV_TOOLCHAIN:-}" != "${_IBEX_RV_TC_AUTO:-}" ]`. Verified no other variable in the file is read before being set (`IBEX_TOOLS_DIR`, `IBEX_PYTHON`, `VERDI_HOME`, `PKG_CONFIG_PATH` all already had `:-`/`:+` defaults).

**(b) gcc-toolset-11 for non-login shells.** Added, before the simulator/toolchain sections:
```sh
if [ -f /opt/rh/gcc-toolset-11/enable ]; then
    source /opt/rh/gcc-toolset-11/enable
fi
```
Confirmed `/opt/rh/gcc-toolset-11/enable` is itself nounset-safe (it guards every expansion it touches, e.g. `${PATH:+:${PATH}}`), so it doesn't reintroduce a strict-mode break.

**(c) fail-loud verification tail.** Added a block after the existing informational echo that checks `vcs`, `$RISCV_GCC`, and `python3` resolve, printing one `ibex env ERROR: <what> missing — are you on a site host?` line per gap (to stderr) and `return 1` (not `exit`, so it's safe when sourced) if any are missing.

Verification performed:
- `bash -c 'source ci/env.sh; echo RC=$?'` → RC=0, tools resolve (this host has vcs/gcc-toolset-11/spike/lowRISC toolchain installed).
- `bash -c 'set -euo pipefail; source ci/env.sh; echo RC=$?'` → RC=0, no unbound-variable abort (previously failed at line 30).
- `bash --noprofile --norc -c 'set -euo pipefail; source ci/env.sh; echo RC=$?'` → RC=0, confirming a non-login shell without the user's normal `.bashrc` still works.
- Isolated logic test of the fail-loud tail (extracted the block, pointed `command -v` at nonexistent binaries): prints the two `ibex env ERROR: ... missing — are you on a site host?` lines and, when actually sourced (not `bash -c`'d as a fresh script), correctly `return`s 1 without killing the shell; under a caller's `set -e`, the failed `source` aborts the caller immediately, which is the intended CI behavior.

## Finding 2 — venv/lock enforcement (`ci/setup-venv.sh:7`)

Deleted `.venv` and recreated it from scratch: `rm -rf .venv && "$IBEX_PYTHON" -m venv .venv && pip install --upgrade pip && pip install -r ci/requirements.lock`. Install succeeded (110 packages).

Verification: `pip freeze --local`, sorted, diffed byte-for-byte against sorted `ci/requirements.lock` — **empty diff**, exact match. The one acceptable delta: `pip` itself was upgraded to 26.2.1 as part of `pip install --upgrade pip` (not listed in the lock, which only pins the venv's payload packages), and `setuptools`/`wheel` are not present at all in this venv (Python 3.12's `ensurepip` no longer bundles them) — neither is in `pip freeze` output, so there's no drift to reconcile there.

`grep -i siliconpilot` against the new venv's `pip freeze`: **no match** (exit 1) — the stray `siliconpilot==0.18.1` from the old venv is gone.

Updated `ci/setup-venv.sh` to install from `ci/requirements.lock` when it exists (pinned, no `-U`) and fall back to `python-requirements.txt` (unpinned, `-U`) otherwise; kept the `[ -d "$ROOT/.venv" ] ||` idempotency guard and the `IBEX_PYTHON:?source ci/env.sh first` guard unchanged. Reran `bash ci/setup-venv.sh` against the already-populated venv to confirm idempotency: exit 0, all 110 packages reported "Requirement already satisfied", no changes.

## Finding 3 — gates rerun at final HEAD with raw artifacts

After committing findings 1+2 (commit `56acf9c8`), reran all three gates from a fresh shell (`bash -c 'set -euo pipefail; cd <repo> && source ci/env.sh && ( cd dv/uvm/core_ibex && make ... )'`), each with a brand-new `OUT=` tree, then copied raw output into `docs/dv/evidence/` and deleted the OUT trees.

| Gate | Command | Result |
|---|---|---|
| smoke | `IBEX_CONFIG=opentitan ... OUT=out_ws1_smoke` | 100.00% PASS 1 PASSED, 0 FAILED |
| small | `IBEX_CONFIG=small ... OUT=out_ws1_small` | 100.00% PASS 1 PASSED, 0 FAILED |
| coverage | `IBEX_CONFIG=opentitan ... COV=1 OUT=out_ws1_cov` | 100.00% PASS 1 PASSED, 0 FAILED; urg SCORE 52.13 (LINE 70.46 TOGGLE 39.37 FSM 20.93 BRANCH 62.52 ASSERT 85.63 GROUP 33.86); 0 FCIBH hits; fcov: 10217 instructions processed, TEST PASSED, 0 UVM_ERROR/0 UVM_WARNING |

Committed under `docs/dv/evidence/`:
- `ws1-smoke-regr.log` (unchanged — byte-identical to the prior commit's, since the run is deterministic at the same seed/commit-equivalent RTL), `ws1-smoke-tbconfig.txt` (raw `grep TB-CONFIG`)
- `ws1-small-regr.log`, `ws1-small-tbconfig.txt`
- `ws1-cov-regr.log`, `ws1-cov-dashboard.txt` (raw urg `report/dashboard.txt`), `ws1-cov-fcov-log-tail.txt` (tail of the fcov sim log)
- `ws1-manifest.txt`: commit SHA (`56acf9c806ce260c87f6c1f6994005c5dbb2f23b`), `vcs -full64 -ID` first line, `gcc --version` first line, cross `$RISCV_GCC --version` first line (extra, for traceability), `spike --help` first line, `python3 --version`, and the sha256 of the uncommitted `merged.vdb` (computed as sha256 of the sorted per-file hashes under the VDB directory, since it's a directory not a single file — documented in the manifest)

`ws1-cov-summary.txt` and `ws1-smoke-regr-note.txt` were rewritten to point at the new raw files instead of restating pass/score claims inline; the FCIBH fix-history and vRefine-waiver design notes in `ws1-cov-summary.txt` were kept (re-verified the vRefine grep still returns NOT-APPLIED at current HEAD) since those are independent design-time findings, not evidence-of-this-run claims.

All three `out_ws1_*` OUT trees were deleted after evidence extraction; `out*/` is already gitignored at `dv/uvm/core_ibex/.gitignore:11` so none were ever at risk of being committed. One stray VCS tool byproduct (`dv/uvm/core_ibex/.fsm.sch.verilog.xml`, generated outside any OUT tree by one of the runs) was also deleted before committing.

## Finding 4 — commit structure

Two logical commits, both with `Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>`:
1. `56acf9c8` — `ci/env.sh` + `ci/setup-venv.sh` fixes (findings 1+2).
2. `3f381447` — evidence rerun (finding 3).

Confirmed `git status --short` is clean after both commits; no `out*/`, `.venv/`, or tool trees were staged at any point (`.venv/` is gitignored at repo root; verified with `git status --short` throughout venv recreation).

---

# Round 2: codex re-review (2026-09-01-codex-review-02b-ws1-rereview.md)

Verdict: REQUEST-CHANGES, findings 2+4 ADDRESSED, findings 1+3 NOT-ADDRESSED (per that review) — fixed here per the controller's round-2 scoped rulings, which explicitly rejected codex's ask to make `env.sh` bootstrap a sanitized shell.

Commit: `cd4ad2b6` [ci] Add env.sh contract, WARN-only verdi/dtc, and PYTHONPATH-clean venv lock check

## Finding 1 (`ci/env.sh:70`) — ruled partial, not "bootstrap a sanitized shell"

The controller ruled that initializing site module paths from scratch and hard-failing on `verdi`/`dtc` is out of scope — `env.sh` is meant to load *additional* tooling on top of an already-sourced site profile, not stand one up. Did exactly the two in-scope asks instead:

- **(a) Contract header.** Added a block comment to `ci/env.sh` stating it's supported on site hosts with the standard profile already loaded — a login shell (`bash -l`) or any shell inheriting the site environment from one — and that it does not bootstrap a sanitized/non-site shell.
- **(b) Non-fatal verdi/dtc checks.** Extended the verification tail with `command -v verdi` / `command -v dtc` checks that print a `ibex env WARN: ... unavailable`/`... will fail` line to stderr but do **not** set the failure flag; `vcs`, `RISCV_GCC`, and `python3` remain hard-fail (`_ibex_env_status=1` + `return 1`).

Verification:
- `bash -n ci/env.sh` — syntax OK.
- `bash -c 'set -euo pipefail; source ci/env.sh; echo RC=$?'` — RC=0, no regression from round 1.
- On this host both `verdi` and `dtc` resolve after sourcing (`verdi` via alias, `dtc` via the `module load dtc/1.7.2` line), so no WARN fires here; isolated test of the WARN logic against two nonexistent binary names printed both `ibex env WARN: ... missing` lines to stderr and then continued execution (`echo "did not abort, continuing"` ran), confirming they're non-fatal.

## Finding 3 (`ci/setup-venv.sh:7`) — ruled accept, root cause = ambient PYTHONPATH leak

Root-caused the "111 vs 110 packages, siliconpilot still exposed" observation: `/home/fzhang/.bashrc:145` exports `PYTHONPATH="/tools_risc/tt/siliconpilot/latest/app:${PYTHONPATH:-}"` for every login shell. That directory carries its own package metadata, so `pip freeze` reports it as "installed" via sys.path regardless of what's actually in `.venv` — this is a property of the shell running `pip freeze`, not of the venv itself, which is why round 1's freeze (run in a shell without that PYTHONPATH set) looked clean.

Fix: `ci/setup-venv.sh` now `unset PYTHONPATH` right after `set -euo pipefail`, before any pip operation, so venv creation, `pip install --upgrade pip`, and both install paths all run PYTHONPATH-clean regardless of the caller's shell. Added an exact freeze-vs-lock check at the end of the lock-install branch: sorted `pip freeze --local` (already PYTHONPATH-clean from the `unset` above) diffed against sorted, comment-stripped `ci/requirements.lock`, both sides filtered for `pip`/`setuptools`/`wheel` (belt-and-suspenders — `pip freeze` already excludes those three by default); any other mismatch prints a diff to stderr and `exit 1`.

Verification transcript (the proof codex asked for):
```
$ rm -rf .venv   # round-1 venv, for a clean before/after comparison

# STEP 1 — reproduce the leak: activate the round-1 venv with the same
# PYTHONPATH a real login shell carries
$ bash -c '
export PYTHONPATH="/tools_risc/tt/siliconpilot/latest/app:${PYTHONPATH:-}"
source .venv/bin/activate
pip freeze | wc -l
pip freeze | grep -i siliconpilot
'
PYTHONPATH=/tools_risc/tt/siliconpilot/latest/app:
111
siliconpilot==0.18.1

# STEP 2 — same venv, PYTHONPATH cleared
$ bash -c '
export PYTHONPATH="/tools_risc/tt/siliconpilot/latest/app:${PYTHONPATH:-}"
unset PYTHONPATH
source .venv/bin/activate
pip freeze | wc -l
pip freeze | grep -i siliconpilot || echo "no siliconpilot (clean)"
'
110
no siliconpilot (clean)
```
This is the exact 111-vs-110 / siliconpilot-exposed-vs-not split codex reported, isolated to the PYTHONPATH difference alone (same venv, same packages actually installed).

Then rebuilt the venv from scratch through the **updated** script, deliberately with the leaky PYTHONPATH set in the ambient shell (simulating running `setup-venv.sh` from an ordinary login shell):
```
$ rm -rf .venv
$ bash -c '
export PYTHONPATH="/tools_risc/tt/siliconpilot/latest/app:${PYTHONPATH:-}"
export IBEX_PYTHON=/tools_soc/opensrc/python/python-3.12.10/bin/python3
bash ci/setup-venv.sh
'
EXIT=0
```
No `setup-venv ERROR` line was printed (the freeze-vs-lock check passed with PYTHONPATH cleared internally). Confirmed the resulting venv:
```
$ source .venv/bin/activate && pip freeze | wc -l
110
$ pip freeze | grep -i siliconpilot || echo "no siliconpilot (clean)"
no siliconpilot (clean)
$ diff <(sort ci/requirements.lock) <(pip freeze | sort) && echo "EXACT MATCH vs lock"
EXACT MATCH vs lock
```
Reran `bash ci/setup-venv.sh` a second time, still with the dirty ambient PYTHONPATH set, to confirm idempotency: exit 0, all 110 "Requirement already satisfied", no errors.

## Minor — docs/dv/BUILD_AND_SIM.md:27

Fixed the stale description ("installs `python-requirements.txt`") to match the script: installs from `ci/requirements.lock` when present, falling back to `python-requirements.txt` otherwise.

## Commit structure

One commit, `cd4ad2b6`, co-authored trailer included, covering `ci/env.sh`, `ci/setup-venv.sh`, and `docs/dv/BUILD_AND_SIM.md`. `bash -n` passes on both shell scripts. `git status --short` clean after commit.
