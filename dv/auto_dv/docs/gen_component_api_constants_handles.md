# Component API: gen_tb_pkg, knobs codegen and gen_handles.py (constants home)

Owner: tb-infra. Status: skeleton written before the code (T-031, 2026-09-03; regenerated for the v2 component sections after the Critic's review); items marked
"at build" are completed when the component lands (component SV opens after the TB architecture
review). Source: `dv/auto_dv/work/tb-infra/gen_tb_arch_component_sections.md` C11; DV_prompt.txt deliverable 4 (TB architecture document,
component API documents). Conventions (shared by every component document): every runtime
knob is a plusarg whose name is a `parameter string` in `gen_tb_pkg` (column 2 below) and a
generated Python constant of the same value; every checker fails through `uvm_error` with its
id (or `uvm_fatal` where stated); `+gen_chk_<id>=0` disables exactly that checker,
`+gen_chk_all=0 +gen_chk_<id>=1` isolates one for mutation evidence (DV_prompt Section 8).

## 1. Purpose

Single source of truth for plusarg names, TB memory map, banner tag, bounds constants and the
Python/C mirrors; the only Python file that spells hierarchical paths.

## 2. Files (planned) and how to call it

AS BUILT (step 1a, 2026-09-03): `dv/auto_dv/tb/gen_tb_knobs.yaml` is the ONE source (schema_version 1:
`isa_string`; `plusargs[]` with name/kind string|int|hex|bool|enum/default/values/debug_only/desc;
`constants[]` with name/value/optional `sv` right-hand side/sv_type/desc, in SV elaboration order;
`memory_map` with boot_addr_default, the MMIO page and its register offsets). `dv/auto_dv/tb/
gen_knobs_codegen.py` renders it into (1) the `// GEN_KNOBS_BEGIN` .. `// GEN_KNOBS_END` block of
`dv/auto_dv/tb/gen_tb_pkg.sv` (`PLUSARG_<NAME> = "gen_<name>"`, `GEN_ENUM_<NAME>_VALUES/_DEFAULT`
for enums, the constants, `GEN_MM_<KEY>` addresses and the literal twin `GEN_BOOT_ADDR_DEFAULT`), so
the package stays the one file Runtime's testlist loader and the smoke driver read by regex; (2)
`dv/auto_dv/gen_tb/gen_knobs.py` (PLUSARGS, CONSTANTS, MEMORY_MAP, ISA_STRING, DEBUG_ONLY, CHECKERS,
`plusarg()`), imported by cocotb tests and by `gen_program.py` for the ISA string and the MMIO window;
(3) `dv/auto_dv/isa/gen_isa_shim_map.h` (GEN_ISA_STRING, GEN_MM_*, constants) for the shim. The DM
windows come from `gen_dut_top.sv` parameters and the program window from `gen_link.ld` at render
time. Deviation from the C11 sketch: no separate `gen_tb_knobs_pkg.sv`; the marked block inside
`gen_tb_pkg.sv` keeps one file for the regex readers. The rest of gen_tb_pkg.sv (GEN_BANNER_TAG,
GEN_RV32_NOP, IC geometry aliases, `gen_mubi_str`) is hand-written. `gen_tb/gen_handles.py` follows
with gen_tb_top.

SV imports `gen_tb_pkg::*`; Python imports `gen_tb.gen_knobs` and `gen_tb.gen_handles`; the
shim includes `gen_isa_shim_map.h`. Generated files are committed and a `--check` mode diffs them
(the gen_filelist.py pattern). `gen_handles.py` builds bridge/alive/finish/memory-sample handles
from `TOPLEVEL` and fails at start-up on a missing handle.

## 3. Knobs

| Plusarg | gen_tb_pkg name | Meaning | Default |
|---|---|---|---|
| `+(all)` | `PLUSARG_*` | every plusarg name lives here; an unknown `+gen_*` plusarg is a `uvm_fatal GEN_UNKNOWN_PLUSARG` at time 0 (A-23) | - |

## 4. Wave-level behaviour

None (constants).

## 5. Checkers

None: this component carries no pass/fail check (test equipment or infrastructure).

## 6. Failure path and diagnostics

Codegen `--check` failure fails the build; an unknown `+gen_*` plusarg is `uvm_fatal GEN_UNKNOWN_PLUSARG` at time 0 (A-23).

## 7. Coverage hooks

None.

## 8. At build

Unit test `dv/auto_dv/tb/unit/gen_ut_knobs_codegen.py` (TDD transcript
`dv/auto_dv/evidence/gen_tdd_knobs_codegen.md`: red, one defect caught by the test, green, `--check`
mutation proof). Knob names follow the DV Lead's regime knobs (`+gen_knob_<name>=<value>`, 20 enums
from gen_fcov_plan.md Section REG); `+gen_dbg_<component>` debug knobs are added to the yaml by the
component that uses them. `gen_handles.py` lands with gen_tb_top (step 1b).
