# TDD transcript: constants codegen (architecture C11; build step 1a)

Component: `dv/auto_dv/tb/gen_tb_knobs.yaml` (source) + `dv/auto_dv/tb/gen_knobs_codegen.py`
(renderer, `--check` mode) -> the GEN_KNOBS block of `dv/auto_dv/tb/gen_tb_pkg.sv`,
`dv/auto_dv/gen_tb/gen_knobs.py`, `dv/auto_dv/isa/gen_isa_shim_map.h`.
Test: `dv/auto_dv/tb/unit/gen_ut_knobs_codegen.py` (plain asserts; exit 1 on any failure).
Logs: `dv/auto_dv/work/tb-infra/tdd/knobs_codegen_red.log`, `gen_knobs_codegen_green.log`.
Owner: tb-infra. dv_principles Section 6 rule 1 (the failing check precedes the implementation).

## 1. Red (test written first; the source and the renderer did not exist)

```
# RED run: 2026-09-03T07:10:54Z host=soc-l-11 cmd: python3 dv/auto_dv/tb/unit/gen_ut_knobs_codegen.py
FAIL yaml source exists (/localdev/fzhang/ws/ibex-challenge/dv/auto_dv/tb/gen_tb_knobs.yaml)
FAIL codegen exists (/localdev/fzhang/ws/ibex-challenge/dv/auto_dv/tb/gen_knobs_codegen.py)
GEN_UT_KNOBS_CODEGEN FAIL (2 failures)
exit=1
```

## 2. Green attempt 1 (implementation written; one real defect found by the test)

The renderer emitted `GEN_BOOT_ADDR_DEFAULT = GEN_MM_BOOT_ADDR_DEFAULT;` (an alias), which the
regex reader in `gen_program.py` cannot parse, so the cross-check against gen_program's memory-map
derivation aborted:

```
# GREEN run: 2026-09-03T07:13:46Z host=soc-l-11 cmd: python3 dv/auto_dv/tb/unit/gen_ut_knobs_codegen.py
... 228 OK lines ...
cannot find parameter GEN_BOOT_ADDR_DEFAULT in /localdev/fzhang/ws/ibex-challenge/dv/auto_dv/tb/gen_tb_pkg.sv
exit=1
```

Fix: render `GEN_BOOT_ADDR_DEFAULT` as a `32'h` literal (twin of `GEN_MM_BOOT_ADDR_DEFAULT`).

## 3. Green

```
# GREEN run 2: 2026-09-03T07:14:43Z host=soc-l-11 cmd: python3 dv/auto_dv/tb/unit/gen_ut_knobs_codegen.py (after fixing the GEN_BOOT_ADDR_DEFAULT alias that green run 1 exposed)
GEN_UT_KNOBS_CODEGEN PASS (0 failures)
exit=0
```

What the green run checks (each an OK line in the log): `--check` passes on a fresh render; every
yaml plusarg is declared exactly once as `PLUSARG_<NAME>` and no `PLUSARG_` exists outside the
rendered block (115 plusargs); every enum knob has >= 2 values, a default among them and its value
set in the package; every debug-only knob (`gen_dbg_csr_probe`) is in Runtime's
`debug_only_plusargs`; the 20 DV Lead regime knobs of `gen_fcov_plan.md` Section REG exist as enum
knobs `knob_*`; the Python mirror carries every name, the value sets, the ISA string and the memory
map; the C header carries the ISA string and every `GEN_MM_*` address; the memory map agrees with
`gen_program.py`'s own derivation from `gen_dut_top.sv` and `gen_link.ld`; gen_program's ISA
string equals the yaml's; the MMIO page lies outside the program and DM windows; every constant
is declared in the package and mirrored in Python.

## 4. `--check` mode proven (mutation of a rendered file)

```
sed GEN_IRQ_ENTRY_BOUND_RECORDS = 17 -> 16 in gen_tb_pkg.sv
gen_knobs_codegen --check: STALE dv/auto_dv/tb/gen_tb_pkg.sv      check exit (mutated)=1
re-render
gen_knobs_codegen --check: up to date                             check exit (restored)=0
```

## 5. Downstream re-proof

`gen_program.py` now takes the ISA string and the MMIO page from the rendered `gen_knobs.py`;
the directed Zc program re-ran with `-m0x1a110000:0x1000,0x80000000:0x100000,0x8ffff000:0x1000`,
Spike exit 0 (`dv/auto_dv/work/tb-infra/out_codegen/zc/`). Compile proof of the rendered package:
the smoke driver into `dv/auto_dv/work/tb-infra/out_codegen/smoke/` (result appended below).

Compile proof result (2026-09-03, `gen_smoke_run.sh` into `out_codegen/smoke`, VCS exit 0, 0 compile
errors; the smoke top compiles against the rendered package, whose plusarg names the driver read back):

```
names: +gen_build_config +gen_smoke_cycles +gen_smoke_intg_flip tokens: GEN_SMOKE_PASS GEN_SMOKE_FAIL
run_01_green           plusargs=[+gen_smoke_cycles=3000] simv_exit=0 token=PASS fatal_lines=0 expected=PASS -> as-expected
run_02_red_noretire    plusargs=[+gen_smoke_cycles=1] simv_exit=0 token=FAIL fatal_lines=1 expected=FAIL -> as-expected
run_03_red_intg        plusargs=[+gen_smoke_cycles=3000 +gen_smoke_intg_flip=5] simv_exit=0 token=FAIL fatal_lines=1 expected=FAIL -> as-expected
run_04_green           plusargs=[+gen_smoke_cycles=3000] simv_exit=0 token=PASS fatal_lines=0 expected=PASS -> as-expected
sequence result: ALL-AS-EXPECTED
```

## 6. Step 1b extension (bridge command codes, rendered env-cfg include, known-plusarg check)

Test extended first (`gen_ut_knobs_codegen.py`, 1b block), red, then the renderer:

```
# RED run (step 1b extension): 2026-09-03T07:20:10Z host=soc-l-11 cmd: python3 dv/auto_dv/tb/unit/gen_ut_knobs_codegen.py
FAIL yaml has bridge_cmds
FAIL env cfg include exists (/localdev/fzhang/ws/ibex-challenge/dv/auto_dv/tb/gen_env_cfg_knobs.svh)
FAIL pkg has gen_is_known_plusarg
FAIL known-plusarg list covers every name
GEN_UT_KNOBS_CODEGEN FAIL (4 failures)
exit=1
# GREEN run (step 1b extension): 2026-09-03T07:21:26Z host=soc-l-11 cmd: python3 dv/auto_dv/tb/unit/gen_ut_knobs_codegen.py
GEN_UT_KNOBS_CODEGEN PASS (0 failures)
exit=0
```

Rendered additions: `GEN_CMD_<KIND>` codes (pkg, `CMD` dict, header), `gen_is_known_plusarg()`
(pkg; gen_base_test fatals on any other `+gen_*`), `dv/auto_dv/tb/gen_env_cfg_knobs.svh` (one field
plus `_set` flag per plusarg, `parse_plusargs()`, `validate()` for enum values against
`GEN_ENUM_<NAME>_VALUES`, `pinned_count()`); hand-written helper `gen_str_in_csv` in gen_tb_pkg.sv.
After the green run the enum parameter prefix was renamed `GEN_KNOB_` -> `GEN_ENUM_` (the knob
names already start with `knob_`, so the old prefix doubled the word); renderer and test changed
together, `--check` and the unit test re-run PASS (509 checks).

## 7. T-068 (2026-09-03): retention audit, corrections and the strict-schema re-run

Retained logs of this component live under `dv/auto_dv/evidence/gen_tdd_logs/knobs_codegen/` (verbatim copies
of the work-tree logs, listed with sizes and md5 in `dv/auto_dv/evidence/gen_tdd_logs/gen_manifest.md`).

Corrections to the sections above (Critic step-1a P-03, P-06, L-1; cross-model medium 4):

- Section 4 (`--check` proven by a mutation): UNRETAINED. The excerpt was hand-typed; no log of that run exists.
  It is superseded by the unit test, which now performs the mutation itself (Section 7.2).
- Section 6 ("`--check` and the unit test re-run PASS (509 checks)" after the GEN_ENUM_ rename): UNRETAINED.
- Section 5 ("Spike exit 0" for the zc re-run): the retained `out_codegen/zc/spike_stdout.log` carries the
  command line and the commit log but no exit-status line; the exit status is UNRETAINED. Every log this
  component writes from now on ends with an `exit=<rc>` line.

### 7.1 What changed (Critic P-01, P-02, P-04, P-05; cross-model mediums 1-3, lows)

- `load()` refuses any key outside the schema (top level, plusarg, constant, memory_map, register,
  regime_windows), a missing `desc`, `default` and `default_from` together, an unknown derivation, a window
  value outside its knob's enum set. Every `desc` in the yaml is quoted; the four descriptions that had been
  split on unquoted commas render whole again.
- Derived constants: `GEN_IBUS_MAX_OUTSTANDING`, `GEN_IRQ_FAST_W` (new) and `GEN_IRQ_FAST_MASK` carry
  `derive:` instead of a re-typed `value:`; the renderer computes the Python/C literal from `rtl/ibex_pkg.sv`
  (`BUS_SIZE`, `IC_LINE_SIZE`, the `irq_fast` width) and renders a `<NAME>_PY` mirror beside the SV expression;
  `gen_tb_top` compares the two at time 0 (`GEN_WIDTH_GUARD`, `$fatal`).
- `default_from:` resolves the defaults of `boot_addr`, `mem_readback_words`, `alive_timeout` and
  `finish_timeout` (new constant `GEN_FINISH_TIMEOUT_CYCLES_DEFAULT`) from their constant or memory-map key.
- `debug_only: true` on `rvfi_trace`, `isa_string`, `isa_log`, `sb_trace`; Runtime extended
  `debug_only_plusargs` to the same five names.
- New: `regime_windows` (numeric meaning of the latency/rate/cap regimes, rendered as `gen_regime_window` /
  `gen_regime_scalar` and `REGIME_WINDOWS`), register sizes (`GEN_MM_<REG>_SIZE`), `boot_page_mask`,
  `gen_cmd_name()`, `gen_is_bool_plusarg()`, knob `hart_id`; knob `ut_lockstep_min_ratio_pct` removed.
- `--src` and `--root` options for fixtures and scratch trees. The dead `for ... pass` loop is gone.

### 7.2 Unit test re-run (retained: `knobs_codegen/knobs_codegen_t068.log`)

```
# T-068 run: 2026-09-03T08:59:53Z host=soc-l-11 cmd: python3 dv/auto_dv/tb/unit/gen_ut_knobs_codegen.py (strict schema, ...)
OK   loader refuses: unknown plusarg key
OK   loader refuses: unquoted comma in desc
OK   loader refuses: unknown constant key
OK   loader refuses: unknown memory_map key
OK   loader refuses: unknown register key
OK   loader refuses: unknown top-level key
OK   loader refuses: regime window value outside the enum set
OK   loader refuses: unknown derivation
OK   loader refuses: default and default_from together
OK   --check passes on the fresh scratch copy
OK   --check fails on a mutated dv/auto_dv/tb/gen_tb_pkg.sv
OK   --check passes again after restoring dv/auto_dv/tb/gen_tb_pkg.sv
OK   --check fails on a mutated dv/auto_dv/tb/gen_env_cfg_knobs.svh
OK   --check fails on a mutated dv/auto_dv/gen_tb/gen_knobs.py
OK   --check fails on a mutated dv/auto_dv/isa/gen_isa_shim_map.h
OK   --check passes on the restored scratch copy
GEN_UT_KNOBS_CODEGEN PASS (0 failures)
exit=0
```

674 OK lines, 0 FAIL. The refused fixtures are written under `dv/auto_dv/work/tb-infra/ut_scratch/` (repo-local,
never /tmp) and the stale-target mutations run on a scratch copy of the four rendered files through `--root`.
Three earlier T-068 runs are retained as `gen_knobs_codegen_t068_attempt1.log` (exit 1: the pkg mutation landed in
the hand-written text outside the rendered region, which `--check` preserves by design), `_attempt2.log`
(StopIteration: the header mutation skipped every `#define` line) and `_attempt3.log` (StopIteration: the
header literals `0x...u` / `4u` matched no word-bounded integer). All three are defects of the test's mutation
helper, not of the renderer; the helper now flips one digit of the first non-narrative line inside the rendered
region.

### 7.3 Compile proof of the rendered package

The remediated TB compiled with the rendered `gen_tb_pkg.sv` / `gen_env_cfg_knobs.svh`:
`dv/auto_dv/evidence/gen_tdd_logs/boot_agents/compile_t068.log` (last line `vcs exit: 0`, zero `Error-[` lines;
the VCS flag set is now read from `dv/auto_dv/flow/gen_flow_const.py`, recorded in `gen_config_opts_t068.txt`).
The time-0 guard did not fire in any T-068 run: the `_PY` mirrors (8, 15, 2147418112) equal the SV expressions.
