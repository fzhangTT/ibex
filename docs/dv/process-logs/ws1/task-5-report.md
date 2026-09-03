# Task 5 Report: Fix the `IBEX_CFG_*` define-name mismatch

## Step 1: Audit — every emitted `+define+IBEX_CFG_*` vs TB consumer

Ran `python3 util/ibex_config.py <config> vcs_opts --ins_hier_path core_ibex_tb_top --string_define_prefix IBEX_CFG_` for both `opentitan` and `small` configs, and `grep -rn "IBEX_CFG_" --include=*.sv --include=*.svh dv/ rtl/`.

`opentitan` emits:
```
+define+IBEX_CFG_BaseIsa=ibex_pkg::BaseIsaRV32IorCHERIoT
+define+IBEX_CFG_RV32M=ibex_pkg::RV32MSingleCycle
+define+IBEX_CFG_RV32B=ibex_pkg::RV32BOTEarlGrey
+define+IBEX_CFG_RV32ZC=ibex_pkg::RV32ZcaZcbZcmp
+define+IBEX_CFG_RegFile=ibex_pkg::RegFileFF
```
(plus non-define `-pvalue+` overrides for RV32E, BranchTargetALU, WritebackStage, ICache, ICacheECC, ICacheScramble, BranchPredictor, DbgTriggerEn, SecureIbex, PMPEnable, PMPGranularity, PMPNumRegions, MHPMCounterNum, MHPMCounterWidth — these aren't `+define+IBEX_CFG_*` so out of scope for this audit).

`small` emits the same five defines with different values (`BaseIsaRV32I`, `RV32MFast`, `RV32BNone`, `RV32Zca`, `RegFileFF`).

Audit table (pre-fix, against `tb/core_ibex_tb_top.sv` at commit before this change):

| Emitted define | TB consumer (grep) | Status |
|---|---|---|
| `IBEX_CFG_BaseIsa` | `` `ifndef IBEX_CFG_BASE_ISA `` (line 43) | **MISMATCH** — TB guards on `IBEX_CFG_BASE_ISA`, never set → `ifdef` always takes the default branch |
| `IBEX_CFG_RV32M` | `` `ifndef IBEX_CFG_RV32M `` (line 47) | OK — spelling matches, no fix needed |
| `IBEX_CFG_RV32B` | `` `ifndef IBEX_CFG_RV32B `` (line 51) | OK — spelling matches, no fix needed |
| `IBEX_CFG_RV32ZC` | *(none)* | **GAP** — no `` `ifdef ``, no parameter, no forwarding to `ibex_top_tracing` at all |
| `IBEX_CFG_RegFile` | `` `ifndef IBEX_CFG_REG_FILE `` (line 55) | **MISMATCH** — TB guards on `IBEX_CFG_REG_FILE`, never set |

`grep -rn "IBEX_CFG_" --include=*.sv --include=*.svh dv/ rtl/` found **no consumers outside `dv/uvm/core_ibex/tb/core_ibex_tb_top.sv`** — so the fix scope is confined to that one file, as the brief's "Files" section stated. No additional gaps found beyond the three named in the brief.

## Step 2: Red state (proven)

Compiled `IBEX_CONFIG=small` against the *unmodified* TB (`make GOAL=rtl_tb_compile SIMULATOR=vcs IBEX_CONFIG=small OUT=out_definecheck`, ~10 min, ran in background). Compile succeeded (`vcs_simv up to date`, CPU time 11.8s compile + 0.3s elab + 23.7s link) — this bug is a silent-misconfiguration bug, not a compile failure, matching the brief's expectation.

Evidence from `out_definecheck/build/tb/compile_tb_stdstreams.log`:
```
$ grep -o "IBEX_CFG_BaseIsa[^ ]*" compile_tb_stdstreams.log | head -2
IBEX_CFG_BaseIsa=ibex_pkg::BaseIsaRV32I
$ grep -c "IBEX_CFG_BASE_ISA" compile_tb_stdstreams.log
0
$ grep -o "IBEX_CFG_RegFile[^ ]*" compile_tb_stdstreams.log | head -2
IBEX_CFG_RegFile=ibex_pkg::RegFileFF
$ grep -c "IBEX_CFG_REG_FILE" compile_tb_stdstreams.log
0
$ grep -o "IBEX_CFG_RV32ZC[^ ]*" compile_tb_stdstreams.log | head -2
IBEX_CFG_RV32ZC=ibex_pkg::RV32Zca
```
`IBEX_CFG_BaseIsa=ibex_pkg::BaseIsaRV32I` and `IBEX_CFG_RegFile=ibex_pkg::RegFileFF` are on the VCS command line, but the TB's actual guard macros (`IBEX_CFG_BASE_ISA`, `IBEX_CFG_REG_FILE`) appear **zero** times anywhere in the log — proving the `` `ifdef ``s can never take, so `small` was silently elaborating `ibex_top_tracing`'s CHERIoT-capable defaults (`BaseIsaRV32IorCHERIoT`, and — via the missing `RV32ZC` forwarding — `RV32ZcaZcbZcmp` instead of the requested `RV32Zca`).

## Step 3: Fix applied

In `dv/uvm/core_ibex/tb/core_ibex_tb_top.sv`:
- `` `ifndef IBEX_CFG_BASE_ISA `` / `` `define IBEX_CFG_BASE_ISA `` → `IBEX_CFG_BaseIsa` (both the `ifdef` guard and the macro-expansion use at the `BaseIsa` parameter declaration).
- `` `ifndef IBEX_CFG_REG_FILE `` / `` `define IBEX_CFG_REG_FILE `` → `IBEX_CFG_RegFile` (both the guard and the `RegFile` parameter declaration).
- Added a new `` `ifndef IBEX_CFG_RV32ZC `` block (default `ibex_pkg::RV32ZcaZcbZcmp`, matching `ibex_top_tracing`'s own default), a new `parameter ibex_pkg::rv32zc_e RV32ZC = `IBEX_CFG_RV32ZC;` declaration, and forwarded `.RV32ZC (RV32ZC)` into the `ibex_top_tracing` instantiation alongside `RV32M`/`RV32B`.
- `RV32M`/`RV32B` were already spelled correctly — untouched.
- Added the TB-CONFIG banner exactly as specified in the brief, placed immediately before the existing clock/reset `initial` block.

## Step 4: Green state (proven)

Clean rebuild (`rm -rf out_definecheck && make GOAL=rtl_tb_compile SIMULATOR=vcs IBEX_CONFIG=small OUT=out_definecheck`) passed (`vcs_simv up to date`, `vcs_simv` binary present, no `Error-` lines in the log; parsing of `core_ibex_tb_top.sv` completed cleanly per the log's "Parsing design file" / "Back to file" markers).

```
$ grep -o "IBEX_CFG_BaseIsa[^ ]*" compile_tb_stdstreams.log | head -1
IBEX_CFG_BaseIsa=ibex_pkg::BaseIsaRV32I
$ grep -n "IBEX_CFG_BaseIsa" tb/core_ibex_tb_top.sv
43:  `ifndef IBEX_CFG_BaseIsa
44:    `define IBEX_CFG_BaseIsa ibex_pkg::BaseIsaRV32IorCHERIoT
64:  parameter ibex_pkg::base_isa_e BaseIsa  = `IBEX_CFG_BaseIsa;
$ grep -c "IBEX_CFG_BASE_ISA" tb/core_ibex_tb_top.sv
0
$ grep -c "IBEX_CFG_REG_FILE" tb/core_ibex_tb_top.sv
0
$ grep -n "IBEX_CFG_RegFile" tb/core_ibex_tb_top.sv
59:  `ifndef IBEX_CFG_RegFile
60:    `define IBEX_CFG_RegFile ibex_pkg::RegFileFF
74:  parameter ibex_pkg::regfile_e RegFile   = `IBEX_CFG_RegFile;
$ grep -n "RV32ZC" tb/core_ibex_tb_top.sv
55:  `ifndef IBEX_CFG_RV32ZC
56:    `define IBEX_CFG_RV32ZC ibex_pkg::RV32ZcaZcbZcmp
73:  parameter ibex_pkg::rv32zc_e RV32ZC     = `IBEX_CFG_RV32ZC;
117:    .RV32ZC               (RV32ZC              ),
378:    $display("TB-CONFIG: BaseIsa=%s RegFile=%s RV32ZC=%s",
379:             BaseIsa.name(), RegFile.name(), RV32ZC.name());
$ grep -n "TB-CONFIG" tb/core_ibex_tb_top.sv
378:    $display("TB-CONFIG: BaseIsa=%s RegFile=%s RV32ZC=%s",
```

The emitted define is unchanged (still `IBEX_CFG_BaseIsa=ibex_pkg::BaseIsaRV32I` for `small`), but the TB now guards on that exact spelling; zero remaining hits for either old spelling; `RV32ZC` now has a guard, a parameter, and is forwarded to `ibex_top_tracing`. The banner is runtime evidence checked by Task 6 (`opentitan` smoke) and Task 8 (`small` run) — not re-verified here since this task only compiles the TB (no simulation run).

The only compile warnings present are a `PCWM-W` port-width-mismatch warning on the unrelated `trvk_revbm_rdata_intg_i` port (pre-existing, untouched by this change) and `SIOB` select-index-out-of-bounds warnings in `rtl/ibex_top.sv`/`rtl/ibex_core.sv` (pre-existing RTL, unrelated to config defines). Neither warning references `BaseIsa`, `RegFile`, or `RV32ZC`.

## Files changed

- `dv/uvm/core_ibex/tb/core_ibex_tb_top.sv` — the only file touched, matching the brief's declared scope. No consumers of `IBEX_CFG_*` exist outside this file (confirmed by the `dv/` + `rtl/` grep in Step 1), so no other files needed changes.

## Step 5: Cleanup and commit

`dv/uvm/core_ibex/out_definecheck` removed after both compiles (red and green). `git status --short` showed only the intended file modified before commit.

Commit: `54e01775` — `[dv] Fix IBEX_CFG define spellings so config params reach the TB` (branch `fzhang/auto-dv-setup`), body updated from the brief's suggested message to also call out the `RV32ZC` gap explicitly, ends with the required `Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>` trailer.

## Self-review

- Emitter (`util/ibex_config.py`) was not touched, per the brief's constraint.
- `RV32M`/`RV32B` defines were already correctly spelled in the TB — left untouched rather than "fixed" needlessly.
- The `RV32ZC` default (`ibex_pkg::RV32ZcaZcbZcmp`) matches `ibex_top_tracing`'s own default, per the brief's instruction, so `opentitan`'s behavior (which relies on the CHERIoT-capable default) is unaffected — only `small` (and any config that sets a non-default `RV32ZC`) changes behavior, which is the fix's intent.
- Banner uses `.name()` for all three parameters as specified; `rv32zc_e` is a plain 4-value enum in `ibex_pkg.sv` so `.name()` is expected to work under VCS the same way it already would for `BaseIsa`/`RegFile`'s enum types — confirmed the design elaborated cleanly with no VCS diagnostics on that line.
- Verified via direct log/file inspection (not by trusting background-task notifications, which were reported unreliable on this site and one did in fact appear to fire late).
- No `out*/` directories committed; `git status --short` clean except the one intended file, both before and after commit.

## Concerns

None. The three known gaps from the brief were the only gaps found; the `dv/`+`rtl/` grep confirmed no other `IBEX_CFG_*` consumers exist to extend the fix to.
