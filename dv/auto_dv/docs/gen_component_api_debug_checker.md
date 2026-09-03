# Component API: gen_debug_checker (debug entry, exception, masking, dret, trigger)

Owner: tb-infra. Status: skeleton written before the code (T-031, 2026-09-03; regenerated for the v2 component sections after the Critic's review); items marked
"at build" are completed when the component lands (component SV opens after the TB architecture
review). Source: `dv/auto_dv/work/tb-infra/gen_tb_arch_component_sections.md` C4.5; DV_prompt.txt deliverable 4 (TB architecture document,
component API documents). Conventions (shared by every component document): every runtime
knob is a plusarg whose name is a `parameter string` in `gen_tb_pkg` (column 2 below) and a
generated Python constant of the same value; every checker fails through `uvm_error` with its
id (or `uvm_fatal` where stated); `+gen_chk_<id>=0` disables exactly that checker,
`+gen_chk_all=0 +gen_chk_<id>=1` isolates one for mutation evidence (DV_prompt Section 8).

## 1. Purpose

Predicts debug-mode entry and exit from `debug_req_i`, ebreak, the trigger CSRs and `dcsr.step`,
and checks entry address, `dcsr.cause`, `dpc`, masking of interrupts in debug mode, and `dret`
semantics on the RVFI stream.

## 2. Files (planned) and how to call it

`dv/auto_dv/env/gen_debug_checker.sv` (scoreboard sub-checker); inputs: gen_dbg_agent `ap`,
the CSR model (dcsr, dpc, tdata1/2), RVFI records.

Called by the scoreboard per RVFI record.

## 3. Knobs

| Plusarg | gen_tb_pkg name | Meaning | Default |
|---|---|---|---|
| `+gen_chk_dbg_entry / _dbg_exc / _dbg_masked / _dbg_dret / _dbg_trigger` | `PLUSARG_CHK_*` | checker enables | 1 |

## 4. Wave-level behaviour

Entry pc = DmHaltAddr; exception in debug mode = DmExceptionAddr; `dpc` = pc_if for haltreq/
step/trigger, the ebreak pc for ebreak; a halt coinciding with a special-request instruction
enters from FLUSH with `dpc` = trap vector / mret target (rtl-arch CTRL-24..26).

## 5. Checkers

| Checker id | Rule | Mutation classes it catches (example locus) | Disable knob |
|---|---|---|---|
| `dbg_entry` | `debug_req_i` (not in debug mode) => within bound a record with `rvfi_ext_debug_mode = 1` and `pc_rdata == DmHaltAddr`; `dcsr.cause` (read in the debug ROM) = 3 haltreq / 1 ebreak / 2 trigger / 4 step; `dpc` per rule | controller debug entry (`rtl/ibex_controller.sv:451-476, 764-800`), dcsr cause priority | `+gen_chk_dbg_entry=0` |
| `dbg_exc` | exception in debug mode => `pc_rdata == DmExceptionAddr`, no mepc/mcause side effects | debug exception vector (`EXC_PC_DBG_EXC`) | `+gen_chk_dbg_exc=0` |
| `dbg_masked` | no interrupt or NMI entry while `rvfi_ext_debug_mode = 1`; a request held during a Zcmp sequence enters only after `_last` | `handle_irq` gating (`rtl/ibex_controller.sv:498-500`) | `+gen_chk_dbg_masked=0` |
| `dbg_dret` | `dret` returns to `dpc` with privilege `dcsr.prv`; single-step (`dcsr.step`) re-enters debug after exactly one retired instruction. SPEC direction on B1: `dret` into U clears `mstatus.MPRV` (Sdext.adoc:202); tests that `dret` to U with MPRV set are `expected_fail: true` against the current RTL | dret path (`rtl/ibex_controller.sv`), mstatus restore (`rtl/ibex_cs_registers.sv`) | `+gen_chk_dbg_dret=0` |
| `dbg_trigger` | `tdata1/tdata2` execute-address match (one trigger) enters debug before the matching instruction retires; M-mode writes to tdata1/2 ignored | trigger compare in `rtl/ibex_cs_registers.sv` | `+gen_chk_dbg_trigger=0` |

## 6. Failure path and diagnostics

`uvm_error` per id with record order, cause, expected-versus-actual.

## 7. Coverage hooks

`gen_debug_cg`: entry causes, dpc rule cases, step, trigger, requests during WFI/interrupt/Zcmp.

## 8. At build

Confirm CTRL-24..26 timing on the first debug waveforms.
