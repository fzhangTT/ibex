# TDD transcript: constants codegen (architecture C11; build step 1a)

Component: `dv/auto_dv/tb/gen_tb_knobs.yaml` (source) + `dv/auto_dv/tb/gen_knobs_codegen.py`
(renderer, `--check` mode) -> the GEN_KNOBS block of `dv/auto_dv/tb/gen_tb_pkg.sv`,
`dv/auto_dv/gen_tb/gen_knobs.py`, `dv/auto_dv/isa/gen_isa_shim_map.h`.
Test: `dv/auto_dv/tb/unit/gen_ut_knobs_codegen.py` (plain asserts; exit 1 on any failure).
Logs: `dv/auto_dv/work/tb-infra/tdd/knobs_codegen_red.log`, `knobs_codegen_green.log`.
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
