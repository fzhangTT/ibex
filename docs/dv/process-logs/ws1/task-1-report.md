# Task 1 & 2 Report — ci/env.sh + Python venv

Branch: `fzhang/auto-dv-setup` (verified via `git branch --show-current` before starting and again after both commits).

## Task 1: `ci/env.sh`

### What was done

- Confirmed the exact VCS module name per Step 1:
  `bash -lc 'module avail synopsys/vcs 2>&1 | tr " " "\n" | grep "X-2025.06-SP2$"'`
  returned exactly `synopsys/vcs/X-2025.06-SP2` — no suffix disambiguation needed.
- Wrote `ci/env.sh` matching the brief's content verbatim, **with one addition**: an
  undeclared prerequisite module load. See "Deviation from brief" below.
- Ran Step 3's exact verification command and confirmed `gh` resolves; separately
  confirmed the VCS version banner content (see below) because the exact command as
  written in the brief does not succeed on this host without `-full64` (also see
  "Deviation from brief").
- Committed as `02404601` — `[ci] Add environment entry point for VCS DV flow`.

### Deviation from brief (found during Step 3 verification)

**1. Missing `synopsys/licenses` prerequisite.** `module load synopsys/vcs/X-2025.06-SP2`
failed outright with:
```
ERROR: synopsys/vcs/X-2025.06-SP2 cannot be loaded due to missing prereq.
  HINT: the following module must be loaded first: synopsys/licenses
```
This prereq is not mentioned anywhere in the brief. `module avail synopsys/licenses`
lists versions 1.0 through 2.3, with no `(default)` marker. I compared file
modification times (2.3 is newest, Jul 12 2025) and diffed 2.2 vs 2.3 (2.3 only
reorders/adds license servers — a superset, not a behavior change). This mirrors the
brief's own guidance for the VCS module itself ("pick the highest suffix... and record
the choice in the file's comment"), so I added `module load synopsys/licenses/2.3`
immediately before the VCS module load, with an inline comment explaining the choice.
**This is a judgment call, not something explicitly authorized by the brief** — flagging
for review even though I'm confident in the reasoning.

**2. `vcs -ID` needs `-full64`.** After fixing the license prereq, the brief's exact
Step 3 command still failed:
```
Error-[VCS_COM_UNE] Cannot find VCS compiler
  VCS compiler not found. Environment variable VCS_HOME
  (/tools_vendor/synopsys/vcs/X-2025.06-SP2/linux) is selecting a directory in
  which there isn't a compiler
```
Tracing the `vcs` wrapper script: without `-full64`, `VCS_MODE_FLAG` stays `0` and VCS
picks the legacy 32-bit `linux` arch directory (which doesn't exist on this install —
only `linux64` does), instead of `linux64`. This is standard Synopsys VCS behavior on
64-bit-only hosts, **not a defect in env.sh** — the brief's Interfaces section only
requires `vcs` to be on PATH, which it is (`command -v vcs` succeeds; the diagnostic
echo at the end of env.sh also confirms this). I did **not** bake `-full64` into
env.sh, since that's an invocation-time flag that belongs in build/compile scripts
(e.g. whatever Task 3 or later writes to actually run VCS), not in the environment
setup. Flagging this so whoever writes the next VCS-invoking script knows to pass
`-full64`.

### Verification output

Exact brief command (fails at the VCS_COM_UNE step, but proves gh works, and after the
licenses fix proves `vcs` resolves in PATH via the module):
```
$ bash -lc 'source ci/env.sh && vcs -ID | head -5 && command -v gh'
... (module load noise) ...
ibex env: vcs=/tools_vendor/synopsys/vcs/X-2025.06-SP2/bin/vcs gcc=/tools_risc/opensrc/latest/newlib/bin/riscv64-unknown-elf-gcc spike=NOT-BUILT

Error-[VCS_COM_UNE] Cannot find VCS compiler
  ...
/tools_vendor/FOSS/gh/2.53.0/bin/gh
```

Corrected command (adds `-full64`, matching standard VCS usage on this host):
```
$ bash -lc 'source ci/env.sh 2>/dev/null >/dev/null; vcs -full64 -ID | head -5 && command -v gh'
vcs script version : X-2025.06
machine name = soc-l-11
machine type = linux64
machine os = Linux 4.18.0-553.el8_10.x86_64
The FLEXlm host ID of this machine is "..."
/tools_vendor/FOSS/gh/2.53.0/bin/gh
```
(Full uncut output also showed `Compiler version = VCS X-2025.06-SP2_Full64`, confirming
the exact module/version match.)

`verdi` also confirmed on PATH per the brief's Interfaces claim:
```
$ command -v verdi
/tools_vendor/synopsys/verdi/X-2025.06-SP2/bin/verdi
```

Note: the "Module ERROR: invalid command name 'module-hide'" lines seen throughout are a
pre-existing site `.modulerc` issue unrelated to this change — they appear on every
`module load` regardless of which module, and don't affect functionality.

---

## Task 2: Python venv

### What was done

1. Confirmed `/tools_soc/opensrc/python/python-3.12.10/bin/python3 --version` →
   `Python 3.12.10` (exact match, no fallback needed).
2. Wrote `ci/setup-venv.sh` verbatim per the brief.
3. Ran `bash ci/setup-venv.sh` — exit 0, all packages from `python-requirements.txt`
   (including the recursive `vendor/google_riscv-dv/requirements.txt`) installed
   successfully. Re-ran it a second time to confirm idempotency (all
   "Requirement already satisfied", exit 0).
4. Step 4 import check:
   `python3 -c "import pydantic, typeguard, portalocker, mako, hjson, junit_xml; import svg; print('deps ok')"`
   → `deps ok`.
5. Step 5 entry-point smoke test — **needed a correction, documented below**.
6. Froze `ci/requirements.lock` via `pip freeze` (111 lines).
7. Added `.venv/` to `.gitignore` (grouped under the existing "Python cache files"
   section) and committed as `3c0e5d80` — `[ci] Add python venv setup for DV flow`.

### Deviation from brief (found during Step 5 verification)

The brief's exact Step 5 command:
```
bash -lc 'source ci/env.sh && python3 vendor/google_riscv-dv/run.py --help >/dev/null && (cd dv/uvm/core_ibex && python3 scripts/metadata.py --help >/dev/null) && echo ENTRYPOINTS-OK'
```
`run.py --help` succeeds (with harmless pre-existing `SyntaxWarning`s from vendored
regex escapes — not something I introduced or fixed, out of scope). `metadata.py --help`
fails:
```
Traceback (most recent call last):
  File ".../dv/uvm/core_ibex/scripts/metadata.py", line 28, in <module>
    import ibex_cmd
  File ".../dv/uvm/core_ibex/scripts/ibex_cmd.py", line 10, in <module>
    import ibex_config
ModuleNotFoundError: No module named 'ibex_config'
```
`ibex_config.py` lives in `util/`, not `dv/uvm/core_ibex/scripts/`. This isn't a missing
pip package — it's a `PYTHONPATH` issue. `dv/uvm/core_ibex/scripts/setup_imports.py`
defines `get_pythonpath()` specifically to compute this path list, and the repo's own
`dv/uvm/core_ibex/Makefile:64` does:
```
export PYTHONPATH := $(shell python3 -c 'from scripts.setup_imports import get_pythonpath; get_pythonpath()')
```
before ever invoking `metadata.py` directly (see also `riscvdv.mk`, `ibex_sim.mk`,
`wrapper.mk`, `get_meta.mk` — all of them pass `PYTHONPATH=$(PYTHONPATH)` explicitly).
The brief's Step 5 command runs `metadata.py` directly without going through `make` and
without this `PYTHONPATH`, so it can't succeed as written on any correctly-installed
checkout — this looks like an oversight in the brief, not a venv defect.

I did **not** change `ci/env.sh` or `ci/setup-venv.sh` to inject this PYTHONPATH — it's
specific to `core_ibex` script invocation, not global venv/tool setup, and the repo
already has the correct mechanism for it (`setup_imports.get_pythonpath()`, wired into
the Makefiles). Instead I re-ran the verification with that same PYTHONPATH
construction to actually prove the venv/deps are sufficient for these entry points,
which was the real intent of Step 5:

```
$ bash -lc '
source ci/env.sh >/dev/null 2>&1
python3 vendor/google_riscv-dv/run.py --help >/dev/null && echo "run.py OK"
cd dv/uvm/core_ibex
export PYTHONPATH="$(python3 -c "from scripts.setup_imports import get_pythonpath; get_pythonpath()")"
python3 scripts/metadata.py --help >/dev/null && echo ENTRYPOINTS-OK
'
run.py OK
PYTHONPATH=/localdev/fzhang/ws/ibex:/localdev/fzhang/ws/ibex/util:/localdev/fzhang/ws/ibex/dv/uvm/core_ibex/scripts:/localdev/fzhang/ws/ibex/dv/uvm/core_ibex/riscv_dv_extension:/localdev/fzhang/ws/ibex/dv/uvm/core_ibex/yaml:/localdev/fzhang/ws/ibex/vendor/google_riscv-dv/scripts
ENTRYPOINTS-OK
```

Flagging this for whoever writes the next task's scripts: any script that runs
`core_ibex/scripts/*.py` directly (outside of `make`) needs this PYTHONPATH export
first, or should just go through the existing `make` targets.

### Verification output

- `bash ci/setup-venv.sh`: exit 0. All packages installed (fusesoc 2.4.3, pydantic
  2.13.5, typeguard 2.13.3, portalocker 4.3.0, mako 1.4.1, hjson 3.1.0, junit-xml 1.9,
  svg.py 1.10.0, pandas 3.0.5, numpy 2.5.2, pyvsc 0.9.5, and full riscv-dv transitive
  deps — no failures, no fallback to an older Python needed).
- Re-run for idempotency: exit 0, all "Requirement already satisfied" except a fresh
  `argparse` fetch (harmless — `argparse` is a stdlib-shadowing backport pin in
  `python-requirements.txt`; pip re-resolves it each time since it isn't otherwise a
  dependency of anything already installed, but installing it is a no-op cost).
- Import check: `deps ok`.
- Entry-point smoke test (corrected per above): `run.py OK` / `ENTRYPOINTS-OK`.
- `ci/requirements.lock`: 111 pinned packages, generated via
  `pip freeze` inside the activated venv.
- `.gitignore`: `.venv/` line added; confirmed via
  `git check-ignore -v .venv/bin/activate` → matches `.gitignore:21:.venv/`.

---

## Self-review

- Read both diffs (`git show 02404601`, `git show 3c0e5d80`) — contents match the
  briefs' verbatim file contents plus the two documented, minimal additions (license
  module load in `ci/env.sh`; no additions to `ci/setup-venv.sh` itself).
- `git status --short` is clean after both commits — no `out/`, `.venv/`, or tarballs
  staged or committed. `.venv/` confirmed git-ignored.
- Both commit messages end with `Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>`.
- File permissions: `ci/env.sh` is non-executable (correct — it's sourced, matches
  the existing `ci/setup-cosim.sh` convention), `ci/setup-venv.sh` is executable
  (matches `ci/install-build-deps.sh`, `ci/lint-commits.sh`, `ci/run-cosim-test.sh`).
- Did not touch any other files; did not attempt Task 3/4 or beyond.

## Concerns for the controller / next task author

1. **`ci/env.sh` line 13 (`module load synopsys/licenses/2.3`) is a judgment call**,
   not explicitly specified by the brief. The reasoning (newest version, superset of
   license servers, same pattern the brief itself used for picking the VCS module) is
   solid but this should get an explicit nod in review since it silently picks among
   7 available versions.
2. **Any future script that invokes `vcs` must pass `-full64`**, or it will fail with
   `VCS_COM_UNE`. This is standard practice for this VCS install on this host, but
   isn't captured anywhere in `ci/env.sh` on purpose (it's a per-invocation flag, not
   an environment default) — worth calling out explicitly in whatever task writes the
   actual compile/sim scripts, in case that isn't obvious to the author.
3. **Any future script invoking `dv/uvm/core_ibex/scripts/*.py` directly** (bypassing
   `make`) needs `PYTHONPATH` set via `setup_imports.get_pythonpath()` first, exactly
   as `dv/uvm/core_ibex/Makefile` already does. Not a venv defect, but easy to trip
   over if a later task's test script calls these scripts directly.

---

## Fix round 1 (review finding: centralize IBEX_PYTHON)

**Finding:** `ci/setup-venv.sh:5` hardcoded
`/tools_soc/opensrc/python/python-3.12.10/bin/python3` directly, violating the plan's
global constraint that all tool paths are centralized in `ci/env.sh`. The brief's
verbatim script had this hardcode; the controller ruled the global constraint wins.

**Fix applied, exactly as directed by the controller:**

1. `ci/env.sh` — added, alongside the other tool-path exports:
   ```bash
   export IBEX_PYTHON="${IBEX_PYTHON:-/tools_soc/opensrc/python/python-3.12.10/bin/python3}"
   ```
2. `ci/setup-venv.sh` — replaced the hardcoded default with a hard requirement on the
   now-centralized variable:
   ```bash
   PYTHON="${IBEX_PYTHON:?source ci/env.sh first}"
   ```

**Verification (only what the fix touches):**

- Sourced path, confirming still idempotent:
  ```
  $ bash -lc 'source ci/env.sh && bash ci/setup-venv.sh'
  ... (pip "Requirement already satisfied" for everything, one fresh argparse install) ...
  EXIT_CODE=0
  ```
- Unsourced path, confirming the intended hard failure:
  ```
  $ env -i HOME="$HOME" PATH="/usr/bin:/bin" bash ci/setup-venv.sh
  ci/setup-venv.sh: line 5: IBEX_PYTHON: source ci/env.sh first
  EXIT_CODE=1
  ```

Both match the expected behavior from the fix instructions. Diff is minimal — one added
export line in `ci/env.sh`, one changed line in `ci/setup-venv.sh`. Committed as
`f5a726be` — `[ci] Centralize IBEX_PYTHON default in env.sh`.

The two minor findings from the review were deferred per the controller's instruction
and are not addressed here.
