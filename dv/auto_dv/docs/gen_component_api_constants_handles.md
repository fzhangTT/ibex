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

`dv/auto_dv/tb/gen_tb_pkg.sv` (as built: PLUSARG_BUILD_CONFIG, PLUSARG_SMOKE_CYCLES,
PLUSARG_SMOKE_INTG_FLIP, GEN_BANNER_TAG, GEN_BOOT_ADDR_DEFAULT, GEN_RV32_NOP, IC geometry aliases,
`gen_mubi_str`), planned `gen_tb_knobs.yaml` -> `gen_knobs_codegen.py` -> `gen_tb_knobs_pkg.sv`
(imported by gen_tb_pkg), `gen_tb/gen_knobs.py`, `gen_isa_shim_map.h`; `gen_tb/gen_handles.py`.

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

Write the YAML and codegen once the knob list of the approved architecture is frozen; extend
gen_program.py's link-constant check to read from the generated header.
