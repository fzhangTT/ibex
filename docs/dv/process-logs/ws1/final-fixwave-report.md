# Final fix wave report — WS1 (branch fzhang/auto-dv-setup)

Repo: `/localdev/fzhang/ws/ibex`, branch `fzhang/auto-dv-setup` (verified via
`git branch --show-current` before starting; working tree was clean).

All six findings fixed. Details, reproduction, and verification transcripts
below.

## Finding 1 [Important] — `ci/env.sh` dies under `set -e`

**Reproduce (before fix):**

```
$ bash -c 'set -e; source ci/env.sh'
Module ERROR: invalid command name "module-hide"
...
EXIT CODE: 1
```

Confirmed root cause: `module load synopsys/licenses/2.3` and
`module load synopsys/vcs/X-2025.06-SP2` both exit 1 on this site even when
the load succeeds (same behavior already documented/guarded for `dtc`
below them), but were unguarded.

**Fix** (`ci/env.sh`): guarded both loads with `2>/dev/null || true`, same
pattern as the existing dtc guard, and consolidated the "exits 1 even on
success" comment above the two new guards instead of duplicating it.

```diff
 # --- Simulator (VCS must match the Verdi release already on PATH) ---
 source /etc/profile.d/modules.sh 2>/dev/null || true
 # synopsys/vcs has an undeclared prereq on synopsys/licenses; 2.3 is the newest
 # available (of 1.0-2.3) and a superset of older servers, so pick it.
-module load synopsys/licenses/2.3
-module load synopsys/vcs/X-2025.06-SP2
+# This site's module command exits 1 even on a successful load, hence `|| true`.
+module load synopsys/licenses/2.3 2>/dev/null || true
+module load synopsys/vcs/X-2025.06-SP2 2>/dev/null || true
 export VERDI_HOME="${VERDI_HOME:-/tools_vendor/synopsys/verdi/X-2025.06-SP2}"
```

**Re-verify (after fix):**

```
$ bash -c 'set -e; source ci/env.sh; echo "SOURCE_OK exit=$?"; command -v vcs'
ibex env: vcs=/tools_vendor/synopsys/vcs/X-2025.06-SP2/bin/vcs gcc=... spike=...
SOURCE_OK exit=0
/tools_vendor/synopsys/vcs/X-2025.06-SP2/bin/vcs
=== overall exit: 0 ===
```

Exits 0 under `set -e`, and `command -v vcs` resolves. PASS.

## Finding 2 [Important] — toolchain fallback poisons re-sourced shells

Root cause confirmed: `export RISCV_TOOLCHAIN="${RISCV_TOOLCHAIN:-...}"`
followed by an `else` branch that does `export RISCV_TOOLCHAIN=/tools_risc/...`
means that once the fallback fires, `RISCV_TOOLCHAIN` is non-empty in the
shell, so `${RISCV_TOOLCHAIN:-...}` on a later `source ci/env.sh` (e.g.
after `ci/get-toolchain.sh` installs the lowRISC toolchain) sees the
site-fallback value sitting in the "user override" slot and never
re-evaluates.

**Fix** (`ci/env.sh`): introduced an internal cache variable
`_IBEX_RV_TC_AUTO` that records our own last auto-pick. On each source, a
non-empty `RISCV_TOOLCHAIN` is only treated as a genuine user override if
it differs from `_IBEX_RV_TC_AUTO`; otherwise the lowRISC-preferred /
site-fallback logic re-runs fresh every time.

```bash
# --- RISC-V toolchain (Task 4 decides which; lowRISC preferred) ---
# _IBEX_RV_TC_AUTO caches our own last pick so re-sourcing after installing
# the lowRISC toolchain picks it up, without clobbering a real user override
# (RISCV_TOOLCHAIN set to anything other than our own last pick).
if [ -n "$RISCV_TOOLCHAIN" ] && [ "$RISCV_TOOLCHAIN" != "$_IBEX_RV_TC_AUTO" ]; then
    _ibex_rv_tc="$RISCV_TOOLCHAIN"
elif [ -x "$IBEX_TOOLS_DIR/lowrisc-toolchain-gcc-rv32imcb/bin/riscv32-unknown-elf-gcc" ]; then
    _ibex_rv_tc="$IBEX_TOOLS_DIR/lowrisc-toolchain-gcc-rv32imcb"
else
    _ibex_rv_tc=/tools_risc/opensrc/latest/newlib
fi
export RISCV_TOOLCHAIN="$_ibex_rv_tc"
export _IBEX_RV_TC_AUTO="$_ibex_rv_tc"
unset _ibex_rv_tc
```

**Re-verify — full transcript, one shell, run start to finish:**

```
=== Step 1: unset RISCV_TOOLCHAIN, move lowRISC toolchain aside ===
=== Step 2: source env.sh (expect fallback riscv64 gcc) ===
ibex env: vcs=.../vcs gcc=/tools_risc/opensrc/latest/newlib/bin/riscv64-unknown-elf-gcc spike=...
RISCV_TOOLCHAIN=/tools_risc/opensrc/latest/newlib
RISCV_GCC=/tools_risc/opensrc/latest/newlib/bin/riscv64-unknown-elf-gcc
=== Step 3: move lowRISC toolchain back ===
=== Step 4: re-source (expect lowRISC riscv32 gcc now selected) ===
ibex env: vcs=.../vcs gcc=/localdev/fzhang/ws/tools/lowrisc-toolchain-gcc-rv32imcb/bin/riscv32-unknown-elf-gcc spike=...
RISCV_TOOLCHAIN=/localdev/fzhang/ws/tools/lowrisc-toolchain-gcc-rv32imcb
RISCV_GCC=/localdev/fzhang/ws/tools/lowrisc-toolchain-gcc-rv32imcb/bin/riscv32-unknown-elf-gcc
=== Step 5: explicit user override survives a re-source ===
export RISCV_TOOLCHAIN=/some/path
ibex env: vcs=.../vcs gcc=MISSING spike=...
RISCV_TOOLCHAIN=/some/path
RISCV_GCC=/some/path/bin/riscv64-unknown-elf-gcc
=== DONE ===
transcript exit: 0
```

After the transcript, `/localdev/fzhang/ws/tools/lowrisc-toolchain-gcc-rv32imcb`
was confirmed restored to its original location (moved aside and back
inside the same `mv`/`mv` pair). PASS — fallback no longer sticks after the
real toolchain appears, and an explicit user export survives a re-source.

## Finding 3 [Important] — `ci/requirements.lock` contamination

**Process:** built a throwaway venv with `$IBEX_PYTHON`
(`/tools_soc/opensrc/python/python-3.12.10/bin/python3`) in
`/localdev/fzhang/ws/tmp.<random>-ibex-lock-regen` (outside the repo,
deleted afterward), installed only from the repo-root
`python-requirements.txt` (the file `ci/setup-venv.sh` actually installs
from — there is no `ci/python-requirements.txt`), then `pip freeze` to
regenerate `ci/requirements.lock`.

**Correction to the finding's premise:** the fresh, from-scratch freeze
came back byte-for-byte identical to the previously-committed lock file
*except for one line*:

```
$ diff ci/requirements.lock <(fresh pip freeze)
83d82
< siliconpilot==0.18.1
```

`mcp`, `mcp-types`, `uvicorn`, `sse-starlette`, `httpx2`, `httpcore2`, and
`opentelemetry-api` are **not** orphaned — they are genuine transitive
dependencies of `pyucis` (pulled in via
`python-requirements.txt` → `vendor/google_riscv-dv/requirements.txt` →
`pyvsc` → `pyucis`). Confirmed via `pip show -f pyucis` in the fresh venv:
`Requires: jsonschema, lxml, mcp, python-jsonschema-objects, pyyaml, rich`,
and pyucis itself installs a `pyucis-mcp-server` console script — pyucis
ships an MCP-server feature as a hard (non-extras) dependency, so any clean
install of `python-requirements.txt` pulls that whole cluster in
deterministically. Only `siliconpilot==0.18.1` — an internal package not
required by anything in the dependency closure — was actual contamination
and a real dependency-confusion vector.

**Fix:** overwrote `ci/requirements.lock` with the fresh freeze (removes
only `siliconpilot==0.18.1`; every other line is unchanged and now
verified round-trippable).

**Re-verify:**

```
$ grep -iE 'siliconpilot' ci/requirements.lock   # no output — confirmed gone
$ pip install --dry-run -r ci/requirements.lock   # in the throwaway venv that produced the freeze
... 110 "Requirement already satisfied" lines ...
=== dry-run exit: 0 ===
```

Additionally re-ran `pip install --dry-run -r ci/requirements.lock` in a
**second, completely empty** venv (never touched by the freeze) built from
the same `$IBEX_PYTHON` — exit 0, confirming the lock is independently
installable, not just self-consistent with the venv that produced it. The
throwaway venv directory was then `rm -rf`'d.

Note for the team: `mcp`/`uvicorn`/`httpx2`/etc. remaining in the lock is
correct and expected, not a residual issue — flag this if a future review
re-raises it.

## Finding 4 [Minor] — `dv/uvm/core_ibex/.gitignore` only ignores `out`

Changed `out` to `out*/` (with a one-line comment pointing at the
`OUT=out_cov2`-style docs) so alternate `OUT=` output directories used per
`docs/dv/BUILD_AND_SIM.md` are also ignored.

## Finding 5 [Minor] — `docs/dv/BUILD_AND_SIM.md` never mentions `IBEX_TOOLS_DIR`

Added one line in the "One-time setup" section, before the setup commands:

> If you are not fzhang, first `export IBEX_TOOLS_DIR=/path/to/writable/dir`
> — it defaults to `/localdev/fzhang/ws/tools`.

## Finding 6 [Minor] — stray backtick breaking rendering (~line 155/158)

Original: `` - **`site `module` command exits 1 even on success.** ``
(mismatched backtick nesting inside the bold span). Fixed to:
`` - **Site `module` command exits 1 even on success.** `` — matches the
short-heading style of the other Gotchas bullets and renders cleanly.

## Verification summary

| # | Finding | Status |
|---|---|---|
| 1 | env.sh set -e death | Fixed, verified (exit 0, vcs resolves) |
| 2 | toolchain fallback poisoning | Fixed, verified (full transcript, override survives) |
| 3 | requirements.lock contamination | Fixed, verified (only siliconpilot was contamination; dry-run installs clean in 2 venvs) |
| 4 | .gitignore `out` only | Fixed |
| 5 | missing IBEX_TOOLS_DIR doc | Fixed |
| 6 | stray backtick | Fixed |

## Files changed

- `ci/env.sh`
- `ci/requirements.lock`
- `dv/uvm/core_ibex/.gitignore`
- `docs/dv/BUILD_AND_SIM.md`

No `out*/`, venvs, or tool trees were committed. The throwaway venv used for
finding 3 lived under `/localdev/fzhang/ws/tmp.*-ibex-lock-regen` (outside
the repo) and was deleted after verification.
