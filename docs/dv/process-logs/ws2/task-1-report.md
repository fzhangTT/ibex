# Task 1 Report: Pin cocotb into the venv + env plumbing

## Status: DONE (all steps green)

## Steps

### Step 1 (red)
`bash -lc 'source ci/env.sh && command -v cocotb-config'` resolved to
`/tools_soc/opensrc/python/python-3.9/bin/cocotb-config` (site-wide stray
install, version 1.7.1) rather than a clean MISSING — an environment quirk,
not a blocker. Confirmed via PATH inspection that `.venv/bin` is first on
PATH once activated, so once cocotb is installed into the venv its
`cocotb-config` (1.9.2) correctly shadows the stray site one. Step 4's
version check confirms this resolves correctly.

### Step 2
- Added `ci/requirements-cocotb.txt` (`cocotb==1.9.2`).
- `ci/setup-venv.sh`: added `pip install -r "$ROOT/ci/requirements-cocotb.txt"`
  after the main install in both the lock path and the fallback
  (`python-requirements.txt`) path, inside the existing PYTHONPATH-clean
  block (no new `unset PYTHONPATH` needed — it's already unset for the
  whole script).
- Ran `bash ci/setup-venv.sh` under `source ci/env.sh`: cocotb 1.9.2 and its
  one transitive dep `find-libpython` (0.5.1) installed cleanly, no
  resolver conflicts with the existing python-3.12 package set.
- Regenerated the lock via a PYTHONPATH-clean `pip freeze --local` (same
  filter as the script's own verification: strip pip/setuptools/wheel).
  Diffing the regenerated freeze against the old lock showed two real
  additions (`cocotb==1.9.2`, `find_libpython==0.5.1`) and a set of
  reordered-only lines (e.g. `cli_exit_tools` vs `click`, `sphinx-issues`
  vs `sphinx_rtd_theme`, `typing_extensions` vs `typing-inspection`) — all
  underscore-vs-hyphen artifacts of `sort`'s locale-dependent collation.
  These don't affect the exact-match check since `setup-venv.sh` re-sorts
  both sides at verification time; wrote the lock as the plain sorted
  freeze output.
- Reran `setup-venv.sh`: exits 0, no `ERROR` output — exact-match passes
  with cocotb now in the lock.

### Step 3
Added, after venv activation in `ci/env.sh`:
```sh
command -v cocotb-config >/dev/null 2>&1 && export LIBPYTHON_LOC="$(cocotb-config --libpython)" || true
```
Verified `bash -c 'set -euo pipefail; source ci/env.sh'` still exits 0
(the `&& ... || true` chain absorbs both "not found" and any future
`cocotb-config --libpython` failure without tripping `set -e`, since
neither is the final command in the list).

### Step 4 (green)
```
$ bash -lc 'source ci/env.sh && cocotb-config --version && cocotb-config --lib-name-path vpi vcs && test -f "$LIBPYTHON_LOC" && echo COCOTB-ENV-OK'
1.9.2
/localdev/fzhang/ws/ibex/.venv/lib/python3.12/site-packages/cocotb/libs/libcocotbvpi_vcs.so
COCOTB-ENV-OK
LIBPYTHON_LOC=/tools_soc/opensrc/python/python-3.12.10/lib/libpython3.12.so.1.0
```
All four conditions met: version 1.9.2, a real `.so` path for `vpi vcs`,
`LIBPYTHON_LOC` points at an existing file, `COCOTB-ENV-OK` printed.

### Step 5
Committed as `3b033ae7` — `[ci] Pin cocotb 1.9.2 into the DV venv`.

## Files changed
- `ci/requirements-cocotb.txt` (new): `cocotb==1.9.2`
- `ci/setup-venv.sh`: installs cocotb requirements in both the lock and
  fallback paths
- `ci/requirements.lock`: regenerated (PYTHONPATH-clean freeze), adds
  `cocotb==1.9.2` and `find_libpython==0.5.1`
- `ci/env.sh`: exports `LIBPYTHON_LOC` guarded on `cocotb-config` existing

## Concerns
- The stray site-wide `cocotb-config` (1.7.1, from the `Python version 3.9`
  module load at `/tools_soc/opensrc/python/python-3.9/bin`) sits on PATH
  behind `.venv/bin`. It's harmless today because venv activation puts
  `.venv/bin` first, but it means `command -v cocotb-config` alone is not a
  reliable "not installed" probe on this host — future scripts should
  prefer `cocotb-config --version` output or the venv's own resolution
  rather than presence-only checks. No action taken since it doesn't affect
  this task's interfaces.
- Lock file line order shifted for several unrelated packages due to
  locale-dependent `sort` collation (underscore vs hyphen). Content is
  unaffected and the script's own verification re-sorts at check time, but
  flagging in case a future diff review is confused by the churn.
