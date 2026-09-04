# Component API: gen_dbg_agent (debug request driver)

Owner: tb-infra. Status: skeleton written before the code (T-031, 2026-09-03; regenerated for the v2 component sections after the Critic's review); items marked
"at build" are completed when the component lands (component SV opens after the TB architecture
review). Source: `dv/auto_dv/work/tb-infra/gen_tb_arch_component_sections.md` C3.7; DV_prompt.txt deliverable 4 (TB architecture document,
component API documents). Conventions (shared by every component document): every runtime
knob is a plusarg whose name is a `parameter string` in `gen_tb_pkg` (column 2 below) and a
generated Python constant of the same value; every checker fails through `uvm_error` with its
id (or `uvm_fatal` where stated); `+gen_chk_<id>=0` disables exactly that checker,
`+gen_chk_all=0 +gen_chk_<id>=1` isolates one for mutation evidence (DV_prompt Section 8).

## 1. Purpose

Drives `debug_req_i` with randomized timing and hold policies; the debug program is the image's
`.debug_rom` section linked at DmHaltAddr (gen_link.ld; riscv-dv ROMs relocated by
`dv/auto_dv/stim/gen_relocate_debug_rom.py`). AS BUILT (step 2b, T-090): `gen_agents_pkg::gen_dbg_driver` on
`dv/auto_dv/tb/gen_dbg_if.sv` (instance `u_dbg_if`), acting at the falling edge: DBG_REQ (arg0 1 assert / 0 release, arg1
hold policy 0 CYCLES(arg2) / 1 UNTIL_DEBUG_MODE (released once the core IS in debug mode, the `evt_dbg_mode`
level) / 2 STICKY) and the
regime engine for `knob_debug_req_regime` none / sparse / storm (means 5000 / 200 cycles from the yaml `regime_windows.dbg_event_mean`, read through the rendered `gen_regime_scalar`), switched at run time by
REGIME_SET; every change is published as a `gen_irq_evt` (changed[0], level, cycle) for `gen_dbg_checker`.

## 2. Files (planned) and how to call it

`dv/auto_dv/tb/gen_dbg_if.sv`, `dv/auto_dv/env/gen_dbg_pkg.sv` (`gen_dbg_cfg`, `gen_dbg_item`
{assert_delay, hold_policy = UNTIL_DEBUG_MODE | CYCLES(n) | STICKY}, driver, monitor, sequencer).

Items from the bridge (DBG_REQ) or regime-driven sequences. Debug requests are issued only after
the program's initialisation (riscv-dv INITIALIZED signature or a retirement threshold) because the
generated ROM uses the program's kernel stack pointer (T-025 evidence Section 4).

## 3. Knobs

| Plusarg | gen_tb_pkg name | Meaning | Default |
|---|---|---|---|
| `+gen_knob_debug_req_regime=none|sparse|storm` | `PLUSARG_KNOB_DEBUG_REQ_REGIME` | debug_req_i event rate (layer-2 regime knob, gen_tb_knobs.yaml) | none |
| `+gen_dbg_hold_min/max=<n>` | `PLUSARG_DBG_HOLD_MIN/MAX` | hold length for CYCLES policy | 1 / 100 |
| `+gen_dbg_min_retired=<n>` | `PLUSARG_DBG_MIN_RETIRED` | earliest retirement count for a random request | 200 |

## 4. Wave-level behaviour

Level; UNTIL_DEBUG_MODE drops the line the cycle after a retired record shows `rvfi_ext_debug_mode` SET, which
is a level and not an edge: a request asserted while the core is already in debug mode is released at once,
because its condition is already true. Reading an entry edge here could hold the line for a whole run.

## 5. Checkers

None: this component carries no pass/fail check (test equipment or infrastructure).

## 6. Failure path and diagnostics

No checker in the agent (gen_debug_checker). Debug behind `+gen_dbg_dbg=1`.

## 7. Coverage hooks

`gen_dbg_cg`: request arrival relative to WFI, interrupts, Zcmp sequences, ebreak; hold policy;
step-mix regime.

## 8. At build

Confirm the INITIALIZED gating mechanism with the Test Writer.

## Export event rows (T-080 step 2, addendum Section 8)

Written through `gen_export_sink::write_event` with the rendered line functions when the source is active and enabled;
pin row from gen_dbg_driver: `debug_req` (value) on every DBG_REQ assert or release.
