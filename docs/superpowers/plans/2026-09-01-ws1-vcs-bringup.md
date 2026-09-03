# WS1: VCS Bring-up Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** One riscv-dv test passing end-to-end under VCS with spike cosim on the `opentitan` config, then the same with `COV=1`, with verified written instructions.

**Architecture:** Ibex's existing `dv/uvm/core_ibex` Makefile flow is used as-is; we add the site environment glue (`ci/env.sh`), build the lowRISC spike fork it links against, fix one fork bug (`IBEX_CFG_*` define-name mismatch), and document everything we actually ran.

**Tech Stack:** VCS X-2025.06-SP2 (environment modules), lowRISC riscv-isa-sim fork (`ibex_cosim`), riscv32 GCC cross-compile, Python venv (site python 3.12.10, fallback 3.9), GNU Make.

**Spec:** `docs/superpowers/specs/2026-09-01-auto-dv-setup-design.md` (Workstream 1)

## Global Constraints

- Simulator: `SIMULATOR=vcs`, module `synopsys/vcs/X-2025.06-SP2` (matches Verdi X-2025.06-SP2 already on PATH).
- Standard config: `IBEX_CONFIG=opentitan`.
- Spike: lowRISC fork rev `4b97396656485a129119deaec2ba35e5bf354841` (`ibex_cosim` lineage, pinned in `flake.nix`), configured `--enable-commitlog --enable-misaligned`.
- Tool installs go to `/localdev/fzhang/ws/tools/` (workspace-local, outside the repo). All paths centralized in `ci/env.sh` — no other file hardcodes tool paths.
- The stock flow's behavior must not change except the documented define-mismatch fix.
- Work happens on branch `fzhang/auto-dv-setup`. Commit at the end of every task. Never commit `out/`, `.venv/`, or downloaded tarballs.
- **Path discipline:** run flow commands in a subshell (`( cd dv/uvm/core_ibex && ... )`); reference repo files via `REPO=$(git rev-parse --show-toplevel)` — never `../..` chains. Create destination dirs (`mkdir -p`) before copying evidence.
- Log-file names (verified): TB compile → `out/build/tb/compile_tb_stdstreams.log`; instruction-generator build → `out/build/instr_gen/build_stdout.log`; test assembly → `out/run/tests/<t>.<s>/compile.riscvdv.log`; sim → `rtl_sim_stdstreams.log`.
- Long runs (VCS compile, spike build, full sim) can take 10–30 min each — use generous timeouts and run them in the background where sensible.

## Preflight facts (verified during design; re-verify only if a step contradicts them)

- `bsub`, `verdi` (X-2025.06-SP2), Node 22.14, `gh` 2.53.0 (`/tools_vendor/FOSS/gh/2.53.0/bin`, authenticated as `fzhangTT`) all available.
- Environment modules work (`module avail` lists 56 `synopsys/vcs/*` entries; the listing was truncated in design — Task 1 confirms the exact X-2025.06-SP2 name).
- Site riscv64 newlib toolchain: `/tools_risc/opensrc/latest/newlib/bin/riscv64-unknown-elf-gcc` (13.2.0).
- Site pythons: 3.9.6 on PATH; `/tools_soc/opensrc/python/python-3.12.10/` exists per beowulf references (Task 2 verifies).
- The UVM flow needs env vars `RISCV_TOOLCHAIN`, `RISCV_GCC`, `RISCV_OBJCOPY`, `SPIKE_PATH`, `PKG_CONFIG_PATH` (see `dv/uvm/core_ibex/README.md:24-28`).
- `scripts/compile_tb.py:91-98` requires `pkg-config` to resolve `riscv-riscv`, `riscv-disasm`, `riscv-fdt`, `riscv-fesvr`.

---

### Task 1: `ci/env.sh` — single environment entry point

**Files:**
- Create: `ci/env.sh`

**Interfaces:**
- Produces: a sourceable script; after `source ci/env.sh`, `vcs`, `verdi`, `gh` are on PATH, `RISCV_*`/`SPIKE_PATH`/`PKG_CONFIG_PATH`/`IBEX_TOOLS_DIR` are exported, and the venv (Task 2) is active if it exists. Every later task and every CI script sources this file first.

- [ ] **Step 1: Confirm the exact VCS module name**

Run: `bash -lc 'module avail synopsys/vcs 2>&1 | tr " " "\n" | grep "X-2025.06-SP2$"'`
Expected: exactly `synopsys/vcs/X-2025.06-SP2`. If only suffixed variants exist (e.g. `-1`, `-2`, `-3`), pick the highest suffix of X-2025.06-SP2 and use it in Step 2 (and record the choice in the file's comment).

- [ ] **Step 2: Write `ci/env.sh`**

```bash
#!/usr/bin/env bash
# Environment entry point for ibex auto-DV work. Source, don't execute:
#   source ci/env.sh
# Central authority for tool paths — nothing else in the repo hardcodes them.

IBEX_CI_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export IBEX_TOOLS_DIR="${IBEX_TOOLS_DIR:-/localdev/fzhang/ws/tools}"

# --- Simulator (VCS must match the Verdi release already on PATH) ---
source /etc/profile.d/modules.sh 2>/dev/null || true
module load synopsys/vcs/X-2025.06-SP2
export VERDI_HOME="${VERDI_HOME:-/tools_vendor/synopsys/verdi/X-2025.06-SP2}"

# --- GitHub CLI (auth already configured for fzhangTT) ---
export PATH="/tools_vendor/FOSS/gh/2.53.0/bin:$PATH"

# --- RISC-V toolchain (Task 4 decides which; lowRISC preferred) ---
export RISCV_TOOLCHAIN="${RISCV_TOOLCHAIN:-$IBEX_TOOLS_DIR/lowrisc-toolchain-gcc-rv32imcb}"
if [ -x "$RISCV_TOOLCHAIN/bin/riscv32-unknown-elf-gcc" ]; then
    export RISCV_GCC="$RISCV_TOOLCHAIN/bin/riscv32-unknown-elf-gcc"
    export RISCV_OBJCOPY="$RISCV_TOOLCHAIN/bin/riscv32-unknown-elf-objcopy"
else
    # Site riscv64 multilib fallback (bitmanip tests unavailable)
    export RISCV_TOOLCHAIN=/tools_risc/opensrc/latest/newlib
    export RISCV_GCC="$RISCV_TOOLCHAIN/bin/riscv64-unknown-elf-gcc"
    export RISCV_OBJCOPY="$RISCV_TOOLCHAIN/bin/riscv64-unknown-elf-objcopy"
fi

# --- Spike (lowRISC ibex_cosim fork, built by ci/build-spike.sh) ---
export SPIKE_INSTALL="$IBEX_TOOLS_DIR/spike-ibex-cosim"
export SPIKE_PATH="$SPIKE_INSTALL/bin"
export PKG_CONFIG_PATH="$SPIKE_INSTALL/lib/pkgconfig${PKG_CONFIG_PATH:+:$PKG_CONFIG_PATH}"

# --- Python venv (created by Task 2; optional until then) ---
if [ -f "$IBEX_CI_ROOT/.venv/bin/activate" ]; then
    source "$IBEX_CI_ROOT/.venv/bin/activate"
fi

echo "ibex env: vcs=$(command -v vcs || echo MISSING)" \
     "gcc=$(command -v "$RISCV_GCC" >/dev/null && echo "$RISCV_GCC" || echo MISSING)" \
     "spike=$([ -d "$SPIKE_INSTALL" ] && echo "$SPIKE_INSTALL" || echo NOT-BUILT)"
```

- [ ] **Step 3: Verify it works in a clean shell**

Run: `bash -lc 'source ci/env.sh && vcs -ID | head -5 && command -v gh'`
Expected: VCS prints its version banner containing `X-2025.06-SP2`; `gh` resolves to `/tools_vendor/FOSS/gh/2.53.0/bin/gh`. `spike=NOT-BUILT` is fine at this point.

- [ ] **Step 4: Commit**

```bash
git add ci/env.sh
git commit -m "[ci] Add environment entry point for VCS DV flow"
```

---

### Task 2: Repo-local Python venv

**Files:**
- Create: `ci/setup-venv.sh`
- Modify: `.gitignore` (add `.venv/`)

**Interfaces:**
- Produces: `.venv/` at repo root satisfying `python-requirements.txt`; auto-activated by `ci/env.sh` (Task 1).

- [ ] **Step 1: Pick the Python**

Run: `/tools_soc/opensrc/python/python-3.12.10/bin/python3 --version`
Expected: `Python 3.12.10`. If missing, `ls /tools_soc/opensrc/python/` and pick the newest ≥3.10; if none, use `python3` (3.9.6) and note that `nix/pythonEnv` wants ≥3.10 — watch for install failures.

- [ ] **Step 2: Write `ci/setup-venv.sh`**

```bash
#!/usr/bin/env bash
# One-time venv setup for the ibex DV flow. Idempotent.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON="${IBEX_PYTHON:-/tools_soc/opensrc/python/python-3.12.10/bin/python3}"

[ -d "$ROOT/.venv" ] || "$PYTHON" -m venv "$ROOT/.venv"
source "$ROOT/.venv/bin/activate"
pip install --upgrade pip
pip install -U -r "$ROOT/python-requirements.txt"
```

- [ ] **Step 3: Run it**

Run: `bash ci/setup-venv.sh` (allow ~5 min; PyPI access was proven by earlier web fetches, but if pip cannot reach the index, stop and report — that changes the approach to a site pip mirror).
Expected: exits 0.

- [ ] **Step 4: Verify the flow's imports resolve**

Run: `bash -lc 'source ci/env.sh && python3 -c "import pydantic, typeguard, portalocker, mako, hjson, junit_xml; import svg; print(\"deps ok\")"'`
Expected: `deps ok`.

- [ ] **Step 5: Smoke-test the flow's actual entry points**

Run: `bash -lc 'source ci/env.sh && python3 vendor/google_riscv-dv/run.py --help >/dev/null && (cd dv/uvm/core_ibex && python3 scripts/metadata.py --help >/dev/null) && echo ENTRYPOINTS-OK'`
Expected: `ENTRYPOINTS-OK`. (Imports alone don't prove the riscv-dv/metadata scripts run under this Python.)

- [ ] **Step 6: Freeze a lock file for reproducibility**

Run: `bash -lc 'source ci/env.sh && pip freeze > ci/requirements.lock'`
`ci/setup-venv.sh` stays on `python-requirements.txt` (upstream-shaped); the lock records what was actually validated so regressions are reproducible.

- [ ] **Step 7: Add `.venv/` to `.gitignore` and commit**

Append a line `.venv/` to the repo-root `.gitignore`.

```bash
git add ci/setup-venv.sh ci/requirements.lock .gitignore
git commit -m "[ci] Add python venv setup for DV flow"
```

---

### Task 3: Build lowRISC spike (`ci/build-spike.sh`)

**Files:**
- Create: `ci/build-spike.sh`

**Interfaces:**
- Consumes: `IBEX_TOOLS_DIR`, `SPIKE_INSTALL` from `ci/env.sh`.
- Produces: `$SPIKE_INSTALL` containing `bin/spike` and `lib/pkgconfig/{riscv-riscv,riscv-disasm,riscv-fdt,riscv-fesvr}.pc` — exactly what `dv/uvm/core_ibex/scripts/compile_tb.py:91-98` resolves.

- [ ] **Step 1: Verify the gap (red)**

Run: `bash -lc 'source ci/env.sh && pkg-config --exists riscv-riscv && echo FOUND || echo MISSING'`
Expected: `MISSING`.

- [ ] **Step 2: Check build prerequisites**

Run: `command -v dtc; command -v cmake; gcc --version | head -1`
Expected: gcc 11.x (gcc-toolset-11 is on PATH). If `dtc` is missing, check `/usr/bin/dtc` and `module avail dtc`; spike's build needs device-tree-compiler — if truly absent on the site, report before proceeding (do not silently build a crippled spike).

- [ ] **Step 3: Write `ci/build-spike.sh`**

```bash
#!/usr/bin/env bash
# Build the lowRISC spike fork the ibex cosim TB links against.
# Rev pinned to match this repo's flake.nix; dv/cosim/* is written against it.
set -euo pipefail
SPIKE_REV=4b97396656485a129119deaec2ba35e5bf354841
IBEX_TOOLS_DIR="${IBEX_TOOLS_DIR:-/localdev/fzhang/ws/tools}"
PREFIX="${SPIKE_INSTALL:-$IBEX_TOOLS_DIR/spike-ibex-cosim}"
SRC="$IBEX_TOOLS_DIR/src/riscv-isa-sim-lowrisc"

mkdir -p "$IBEX_TOOLS_DIR/src"
if [ ! -d "$SRC/.git" ]; then
    git clone https://github.com/lowRISC/riscv-isa-sim.git "$SRC"
fi
git -C "$SRC" fetch --all --tags
git -C "$SRC" checkout "$SPIKE_REV"

mkdir -p "$SRC/build"
cd "$SRC/build"
# Static gcc runtimes: the TB's DPI .so must load inside VCS, whose bundled
# libstdc++ may predate the build compiler's (flake.nix does the same).
../configure --enable-commitlog --enable-misaligned --prefix="$PREFIX" \
             LDFLAGS="-static-libstdc++ -static-libgcc"
make -j"$(nproc)"
make install
echo "spike installed to $PREFIX"
```

- [ ] **Step 4: Run it**

Run: `bash -lc 'source ci/env.sh && bash ci/build-spike.sh'` (background, ~10-20 min).
Expected: exits 0. If the clone cannot reach github.com, report — network policy changes the approach. If compilation fails under gcc 11 (the rev predates gcc 13-era cleanups; gcc 11 is expected to work), capture the first error and fix with the smallest possible patch, documenting it in the script as a comment.

- [ ] **Step 5: Verify (green)**

Run: `bash -lc 'source ci/env.sh && pkg-config --exists riscv-riscv riscv-disasm riscv-fdt riscv-fesvr && echo ALL-FOUND && $SPIKE_PATH/spike --help 2>&1 | head -3'`
Expected: `ALL-FOUND` and spike's usage text.

- [ ] **Step 6: Commit**

```bash
git add ci/build-spike.sh
git commit -m "[ci] Add lowRISC spike build script for cosim"
```

---

### Task 4: RISC-V toolchain

**Files:**
- Create: `ci/get-toolchain.sh`

**Interfaces:**
- Produces: `$IBEX_TOOLS_DIR/lowrisc-toolchain-gcc-rv32imcb/bin/riscv32-unknown-elf-{gcc,objcopy}` — the primary path `ci/env.sh` (Task 1) already prefers; on failure, the documented fallback is the site riscv64 multilib which env.sh selects automatically.

- [ ] **Step 1: Write `ci/get-toolchain.sh`**

```bash
#!/usr/bin/env bash
# Fetch the lowRISC rv32imcb toolchain release (bitmanip-patched GCC).
# Version matches ci/vars.env (RISCV_TOOLCHAIN_TAR_VERSION=20220210-1).
set -euo pipefail
VER=20220210-1
NAME=lowrisc-toolchain-gcc-rv32imcb-$VER
URL=https://github.com/lowRISC/lowrisc-toolchains/releases/download/$VER/$NAME.tar.xz
IBEX_TOOLS_DIR="${IBEX_TOOLS_DIR:-/localdev/fzhang/ws/tools}"
DEST="$IBEX_TOOLS_DIR/lowrisc-toolchain-gcc-rv32imcb"

mkdir -p "$IBEX_TOOLS_DIR"
cd "$IBEX_TOOLS_DIR"
[ -f "$NAME.tar.xz" ] || curl -fL -o "$NAME.tar.xz" "$URL"
tar xf "$NAME.tar.xz"
rm -rf "$DEST"
mv "$NAME" "$DEST"
"$DEST/bin/riscv32-unknown-elf-gcc" --version | head -1
```

- [ ] **Step 2: Run it**

Run: `bash -lc 'source ci/env.sh && bash ci/get-toolchain.sh'`
Expected: prints the gcc version line. If the download fails (network policy), the fallback must be validated against the **exact ISA string the `opentitan` flow emits** — not a generic rv32imc probe. `opentitan` has `RV32B: RV32BOTEarlGrey`, so `scripts/ibex_cmd.get_isas_for_config()` produces a bitmanip `-march` for *every* test (test filtering does not change the compiler ISA). Verify:

```bash
source ci/env.sh && cd dv/uvm/core_ibex && \
python3 -c "
import scripts.ibex_cmd as ic
print(ic.get_isas_for_config('opentitan'))"   # capture the exact gen/gcc ISA strings
echo 'int main(){return 0;}' > /tmp/t.c
"$RISCV_GCC" -march=<the gcc ISA printed above> -mabi=ilp32 -o /tmp/t /tmp/t.c && echo MARCH-OK
```

If the fallback gcc rejects that `-march` (likely — upstream GCC lacks the draft-bitmanip `b` naming the lowRISC toolchain was patched for), the fallback **cannot satisfy the WS1 gate on `opentitan`**: stop and report so we either obtain the lowRISC tarball another way or knowingly bring up on a non-bitmanip config first.

- [ ] **Step 3: Verify env.sh picks it up**

Run: `bash -lc 'source ci/env.sh && "$RISCV_GCC" --version | head -1'`
Expected: the chosen gcc's version banner.

- [ ] **Step 4: Commit**

```bash
git add ci/get-toolchain.sh
git commit -m "[ci] Add lowRISC rv32imcb toolchain fetch script"
```

---

### Task 5: Fix the `IBEX_CFG_*` define-name mismatch (with permanent proof)

**Files:**
- Modify: `dv/uvm/core_ibex/tb/core_ibex_tb_top.sv` (defines near lines 43 and 55; banner in an initial block)

**Interfaces:**
- Consumes: `util/ibex_config.py` emits `+define+IBEX_CFG_<FieldName>` verbatim (CamelCase: `IBEX_CFG_BaseIsa`, `IBEX_CFG_RegFile`) — do NOT change the emitter; `RV32M`/`RV32B` and other consumers depend on the verbatim field-name spelling.
- Produces: TB honors the emitted spellings; a permanent one-line config banner printed at time 0 that later regressions and skills can grep (`grep "TB-CONFIG"`).

- [ ] **Step 1: Audit EVERY emitted define against a TB consumer**

Run: `bash -lc 'source ci/env.sh && python3 util/ibex_config.py opentitan vcs_opts --ins_hier_path core_ibex_tb_top --string_define_prefix IBEX_CFG_'` and list each emitted `+define+IBEX_CFG_*`. For each one: `grep -n "<name>" dv/uvm/core_ibex/tb/core_ibex_tb_top.sv`. Known gaps to confirm (do not assume this list is complete):
- `IBEX_CFG_BaseIsa` — TB guards on `IBEX_CFG_BASE_ISA` (spelling mismatch)
- `IBEX_CFG_RegFile` — TB guards on `IBEX_CFG_REG_FILE` (spelling mismatch)
- `IBEX_CFG_RV32ZC` — **no TB parameter at all**: the TB never overrides nor forwards `RV32ZC`, so `small` (wants `RV32Zca`) silently elaborates the `ibex_top_tracing` default (`RV32ZcaZcbZcmp`)

Also run `grep -rn "IBEX_CFG_" --include=*.sv --include=*.svh dv/ rtl/` to catch consumers outside the TB top; extend Step 3 to each hit and list them in the commit message.

- [ ] **Step 2: Record the broken state (red)**

Run (after Tasks 1–4; this compiles the TB only, ~10 min):
```bash
source ci/env.sh && cd dv/uvm/core_ibex && \
make GOAL=rtl_tb_compile SIMULATOR=vcs IBEX_CONFIG=small OUT=out_definecheck
grep -o "IBEX_CFG_BaseIsa[^ ]*" out_definecheck/build/tb/compile_tb_stdstreams.log | head -2
grep -c "IBEX_CFG_BASE_ISA" out_definecheck/build/tb/compile_tb_stdstreams.log || true
```
Expected: the emitted define `IBEX_CFG_BaseIsa=ibex_pkg::BaseIsaRV32I` appears on the compile command line, while the TB's guard macro `IBEX_CFG_BASE_ISA` never appears — proving the `ifdef` can never take and `small` silently builds the CHERIoT-capable default.

- [ ] **Step 3: Fix the TB spellings and add the banner**

In `core_ibex_tb_top.sv`: (a) change every `IBEX_CFG_BASE_ISA` → `IBEX_CFG_BaseIsa` and `IBEX_CFG_REG_FILE` → `IBEX_CFG_RegFile` (both the `` `ifdef `` and the `` `IBEX_CFG_... `` macro expansions); (b) add an `RV32ZC` parameter with the same ifdef pattern (`` `ifdef IBEX_CFG_RV32ZC``, default = the current `ibex_top_tracing` default `RV32ZcaZcbZcmp`) and **forward it to the `ibex_top_tracing` instantiation** alongside the other parameters; (c) repeat for any additional gaps found in Step 1. Then add, next to the existing initial blocks:

```systemverilog
  // Printed at time 0 so logs prove which config the DUT was actually built with.
  initial begin
    $display("TB-CONFIG: BaseIsa=%s RegFile=%s RV32ZC=%s",
             BaseIsa.name(), RegFile.name(), RV32ZC.name());
  end
```

(Match the file's existing parameter identifiers; the banner must print every parameter the fixed defines control. If `RV32ZC`'s enum type doesn't support `.name()` on a parameter under VCS, print `%0d`.)

- [ ] **Step 4: Verify the fix (green)**

Run:
```bash
rm -rf out_definecheck && \
make GOAL=rtl_tb_compile SIMULATOR=vcs IBEX_CONFIG=small OUT=out_definecheck
```
Expected: compile passes. Then confirm the guard now matches the emitted define: `grep -o "IBEX_CFG_BaseIsa[^ ]*" out_definecheck/build/tb/compile_tb_stdstreams.log | head -1` (define still emitted) and `grep -n "IBEX_CFG_BaseIsa" tb/core_ibex_tb_top.sv` (TB now guards on that exact spelling; zero remaining hits for `IBEX_CFG_BASE_ISA`; same check for `RV32ZC`). The banner is runtime evidence and is checked later: Task 6's smoke log must show `TB-CONFIG: BaseIsa=BaseIsaRV32IorCHERIoT ... RV32ZC=RV32ZcaZcbZcmp` (opentitan), and Task 8's `small` run must show `BaseIsa=BaseIsaRV32I ... RV32ZC=RV32Zca` — those pairs are the mutation-style proof.

- [ ] **Step 5: Clean up and commit**

```bash
rm -rf dv/uvm/core_ibex/out_definecheck
git add dv/uvm/core_ibex/tb/core_ibex_tb_top.sv
git commit -m "[dv] Fix IBEX_CFG define spellings so config params reach the TB

util/ibex_config.py emits +define+IBEX_CFG_BaseIsa/IBEX_CFG_RegFile but the
TB guarded on IBEX_CFG_BASE_ISA/IBEX_CFG_REG_FILE, so every config silently
built the CHERIoT-capable default. Adds a TB-CONFIG banner at time 0 as
permanent evidence of the elaborated config."
```

---

### Task 6: Smoke test — one riscv-dv test end-to-end under VCS

**Files:**
- No new files; produces `out/` artifacts and (only if needed) minimal flow fixes, each committed separately with its own rationale.

**Interfaces:**
- Consumes: everything from Tasks 1–5.
- Produces: a passing `out/run/regr.log`; the exact working command line for BUILD_AND_SIM.md (Task 8).

- [ ] **Step 1: Run the full flow**

```bash
source ci/env.sh && cd dv/uvm/core_ibex && make clean && \
make SIMULATOR=vcs IBEX_CONFIG=opentitan ISS=spike \
     TEST=riscv_arithmetic_basic_test ITERATIONS=1 SEED=1
```
Background, generous timeout (instr-gen VCS build + TB VCS build + sim ≈ 30–60 min first time).

- [ ] **Step 2: Triage loop (repeat until green)**

On failure, find the failing stage's log and fix root-cause only:
- instr gen build: `out/build/instr_gen/build_stdout.log` (riscv-dv compiled by VCS)
- test generation: `out/run/tests/<t>.<s>/` gen logs
- cross-compile: same dir, `compile.riscvdv.log` — toolchain flag issues surface here
- TB compile: `out/build/tb/compile_tb_stdstreams.log` — spike pkg-config/link issues surface here
- sim: `out/run/tests/<t>.<s>/rtl_sim_stdstreams.log` — cosim mismatches surface here
- check: `out/run/tests/<t>.<s>/trr.yaml`

Rules: flow-script or Makefile changes must be minimal, upstream-shaped, and individually committed with the failure they fix quoted in the commit message. If spike API drift breaks `dv/cosim` compilation, re-check the rev against `flake.nix` before patching code — the pinned rev is supposed to match. `COSIM_SIGSEGV_WORKAROUND=1` is available if the documented SIGSEGV issue appears.

- [ ] **Step 3: Verify the pass and the banner**

Run: `grep -E "PASS|FAIL" out/run/regr.log && grep "TB-CONFIG" out/run/tests/*/rtl_sim*.log | head -1`
Expected: the test reports PASSED; banner shows `BaseIsa=BaseIsaRV32IorCHERIoT` (opentitan). Save the evidence:

```bash
REPO=$(git rev-parse --show-toplevel)
mkdir -p "$REPO/docs/dv/evidence"
cp out/run/regr.log "$REPO/docs/dv/evidence/ws1-smoke-regr.log"
```

- [ ] **Step 4: Commit evidence**

```bash
git add docs/dv/evidence/ws1-smoke-regr.log
git commit -m "[dv] WS1 gate evidence: riscv_arithmetic_basic_test passes under VCS+spike"
```

---

### Task 7: Coverage run (`COV=1`)

**Files:**
- No new files; produces `out/run/coverage/` artifacts + evidence.

**Interfaces:**
- Consumes: Task 6's working flow.
- Produces: `out/run/coverage/merged.vdb` + `out/run/coverage/report/`; the verified coverage command for BUILD_AND_SIM.md and later for WS4's `coverage.sh`.

- [ ] **Step 1: Run with coverage**

```bash
source ci/env.sh && cd dv/uvm/core_ibex && \
make SIMULATOR=vcs IBEX_CONFIG=opentitan ISS=spike \
     TEST=riscv_arithmetic_basic_test ITERATIONS=1 SEED=1 COV=1 OUT=out_cov
```

- [ ] **Step 2: Verify coverage artifacts**

Run: `ls out_cov/run/coverage/merged.vdb && ls out_cov/run/coverage/report/ | head && ls out_cov/run/coverage/fcov 2>/dev/null | head -3`
Expected: merged.vdb exists; urg report files exist (`dashboard.txt`/`.html`); fcov dir exists (riscv-dv functional coverage). Record the urg summary line (overall score) into `docs/dv/evidence/ws1-cov-summary.txt` together with the exact command used.

- [ ] **Step 3: Note the waiver caveat**

Confirm `dv/uvm/core_ibex/waivers/*.vRefine` exist and are NOT referenced in `scripts/merge_cov.py` (design-time finding) — one grep: `grep -rn vRefine dv/uvm/core_ibex/scripts/ || echo NOT-APPLIED`. Record the result for the BUILD_AND_SIM.md gotchas section.

- [ ] **Step 4: Commit evidence**

```bash
git add docs/dv/evidence/ws1-cov-summary.txt
git commit -m "[dv] WS1 gate evidence: COV=1 run produces merged.vdb and urg report"
```

---

### Task 8: `small`-config verification + `docs/dv/BUILD_AND_SIM.md`

**Files:**
- Create: `docs/dv/BUILD_AND_SIM.md`

**Interfaces:**
- Consumes: verified commands and gotchas from Tasks 1–7.
- Produces: the bring-up document later skills (`regress`, `sim-debug`) and WS4 scripts reference as the source of truth.

- [ ] **Step 1: Prove the Task 5 fix on a non-default config**

```bash
source ci/env.sh && cd dv/uvm/core_ibex && \
make SIMULATOR=vcs IBEX_CONFIG=small ISS=spike \
     TEST=riscv_arithmetic_basic_test ITERATIONS=1 SEED=1 OUT=out_small
grep "TB-CONFIG" out_small/run/tests/*/rtl_sim*.log
```
Expected: `TB-CONFIG: BaseIsa=BaseIsaRV32I ...` — the mutation-style proof that the define fix changes elaboration. Append the line to `docs/dv/evidence/ws1-smoke-regr.log`'s companion note. (If the sim fails for small-config reasons unrelated to the define, the TB-CONFIG banner from time 0 is still the required evidence.)

- [ ] **Step 2: Write `docs/dv/BUILD_AND_SIM.md`**

Structure (every command must be one that was actually run in Tasks 1–8; copy them verbatim with their observed wall-times):

```markdown
# Building and Running Ibex DV Simulations (VCS)

## One-time setup
(source ci/env.sh; ci/setup-venv.sh; ci/build-spike.sh; ci/get-toolchain.sh — with what each provides)

## Running a single test
(the Task 6 command; where results land: out/run/regr.log, report.html, per-test dirs)

## Running a regression
(TEST=all / all_riscvdv / all_directed / comma-list; ITERATIONS; SEED semantics seed..seed+N-1)

## Coverage
(the Task 7 command; merged.vdb + urg report locations; fcov; the .vRefine waiver caveat)

## Configs
(the 8-config table from the spec: small / opentitan (DV default) / maxperf /
maxperf-pmp / maxperf-pmp-bmbalanced / maxperf-pmp-bmfull / maxperf-pmp-bmfull-icache /
experimental-branch-predictor; top-level Makefile default is small; how rtl_params
filter testlist entries per config)

## Gotchas (each observed or design-verified)
- stale metadata.pickle: make clean after editing testlists/ibex_configs.yaml
- riscv-dv generator is VCS-compiled too: two VCS builds/licenses per fresh build
- VCS -l quirk: sim stdout lands in rtl_sim_stdstreams.log
- .vRefine waivers not applied by merge_cov.py (load in Verdi/urg manually)
- WAVES=1 needs $VERDI_HOME for FSDB (else VPD)
- IBEX_CFG define fix (commit ref): why TB-CONFIG banner exists
- (+ anything new the triage loop in Task 6 uncovered)
```

- [ ] **Step 3: Verify the doc against reality**

Re-run the doc's "single test" command exactly as written from a fresh shell (`bash -lc`), confirming a newcomer path works: expect PASSED again.

- [ ] **Step 4: Commit**

```bash
git add docs/dv/BUILD_AND_SIM.md docs/dv/evidence/
git commit -m "[docs] Add verified VCS build-and-sim instructions"
```

---

### Task 9: `docs/dv/COSIM.md` — cosim architecture deep-dive

**Files:**
- Create: `docs/dv/COSIM.md`

**Interfaces:**
- Consumes: `dv/cosim/*.cc|*.h|*.svh`, `vendor/google_riscv-dv/yaml/iss.yaml`, the built spike source in `$IBEX_TOOLS_DIR/src/riscv-isa-sim-lowrisc`, and a real passing run's `spike_cosim_trace_core_00000000.log` from Task 6.
- Produces: the reference later agents use to reason about cosim failures and trust.

- [ ] **Step 1: Read the in-repo cosim layer**

Read `dv/cosim/cosim.h`, `spike_cosim.h`, `spike_cosim.cc`, `cosim_dpi.svh` (in that order — interface first). Extract: what is stepped, what is compared per retired instruction (RF writes, PC, CSR behavior), how memory/intg errors are injected/checked, how mismatches are reported into the sim log.

- [ ] **Step 2: Diff the spike fork against upstream intent**

Run in `$IBEX_TOOLS_DIR/src/riscv-isa-sim-lowrisc`: `git log --oneline --no-merges -30` and skim for lowRISC-added commits (cosim hooks, commitlog extensions). List the load-bearing ones by subject in the doc — no full diffs.

- [ ] **Step 3: Write `docs/dv/COSIM.md`**

Sections: (1) Architecture — TB ⇄ DPI ⇄ `SpikeCosim` step-and-compare, with the per-instruction check list from Step 1; (2) How failures surface — what a mismatch looks like in `rtl_sim.log`/`trr.yaml`, pointing at one real trace file's format from the Task 6 run; (3) What lowRISC patched in spike (Step 2 list) and what this fork added in `dv/cosim` (e.g. mcounteren behavior, commit `026e71ea`); (4) Augmentation gaps — spike has no CHERIoT knowledge; fine while `cheriot_enable_i` is tied to `IbexMuBiOff` (`tb/core_ibex_tb_top.sv:188`); CHERIoT-enabled verification needs a CHERIoT-aware reference (Sail) — out of scope, tracked here.

- [ ] **Step 4: Commit**

```bash
git add docs/dv/COSIM.md
git commit -m "[docs] Add cosim architecture reference"
```

---

## WS1 exit gate (from the spec)

- [ ] `make SIMULATOR=vcs IBEX_CONFIG=opentitan TEST=riscv_arithmetic_basic_test ITERATIONS=1 SEED=1` — PASSED, evidence committed (`docs/dv/evidence/ws1-smoke-regr.log`)
- [ ] `COV=1` run — merged.vdb + urg report, evidence committed
- [ ] `TB-CONFIG` banner proves `small` ≠ `opentitan` elaboration (define fix works)
- [ ] `docs/dv/BUILD_AND_SIM.md` + `docs/dv/COSIM.md` written from verified reality
