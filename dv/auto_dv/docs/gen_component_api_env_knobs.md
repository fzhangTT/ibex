# Component API: gen_env, gen_env_cfg and the three randomization layers

Owner: tb-infra. Status: skeleton written before the code (T-031, 2026-09-03; regenerated for the v2 component sections after the Critic's review); items marked
"at build" are completed when the component lands (component SV opens after the TB architecture
review). Source: `dv/auto_dv/work/tb-infra/gen_tb_arch_component_sections.md` C9; DV_prompt.txt deliverable 4 (TB architecture document,
component API documents). Conventions (shared by every component document): every runtime
knob is a plusarg whose name is a `parameter string` in `gen_tb_pkg` (column 2 below) and a
generated Python constant of the same value; every checker fails through `uvm_error` with its
id (or `uvm_fatal` where stated); `+gen_chk_<id>=0` disables exactly that checker,
`+gen_chk_all=0 +gen_chk_<id>=1` isolates one for mutation evidence (DV_prompt Section 8).

## 1. Purpose

The UVM environment: instantiates the agents, monitors, scoreboard, shim wrapper and coverage;
holds `gen_env_cfg` (one field per knob) built once from plusargs; implements the three
randomization layers and command-line regime pinning (DV_prompt Section 6).

## 2. Files (planned) and how to call it

`dv/auto_dv/env/gen_env_pkg.sv` (`gen_env_cfg`, `gen_env`, `gen_base_test`), `gen_tb/gen_regimes.py`
(schedule derivation from RANDOM_SEED).

`gen_base_test::build_phase` reads plusargs through `gen_tb_pkg::PLUSARG_*` into `gen_env_cfg`,
puts it in `uvm_config_db`, builds `gen_env`; tests differ by Python, not by UVM test class.

## 3. Knobs

| Plusarg | gen_tb_pkg name | Meaning | Default |
|---|---|---|---|
| `+gen_knob_<name>=<value>` | `PLUSARG_KNOB_*` | layer-2 regime knob (v3, aligned with the DV Lead's gen_fcov_plan.md Section REG): 20 enumerated knobs (imem/dmem gnt_delay, rvalid_delay, err_rate, intg_err_rate, imem_outstanding_cap, irq_regime, irq_line_mix, irq_hold, debug_req_regime, scr_key_delay, icache_ecc_err_rate, fetch_enable_regime, mcounteren_writable, instr_mix, priv_regime, pmp_regime) with the value sets of gen_tb_knobs.yaml; supplying one PINS it for the run (the pinned count is in the banner, CG-REG cp_pinned_count); absent knobs are drawn by Python from RANDOM_SEED. Replaces the v2 `+gen_<agent>_regime` and `+gen_regime_pin` knobs | yaml default per knob |
| `+gen_regime_sched=<knob>:<value>@r<N>|c<N>,...` | `PLUSARG_REGIME_SCHED` | layer-3 schedule over the same knob names: derived by Python from RANDOM_SEED and echoed in the banner when absent; when supplied it is CONSUMED as the schedule, overriding the seed-derived one (v2, XM-L5); Python issues REGIME_SET at the triggers; every applied phase is published as a phase-log record {phase_idx, knob, applied_value, start_cycle, start_rvfi_order, pinned} for CG-REG-*. No `+gen_regime_seed`: one seed drives everything (DV_prompt Section 6) | derived |
| `+gen_chk_all=0|1` | `PLUSARG_CHK_ALL` | master checker enable; with 0 and one `+gen_chk_<id>=1` a single checker is isolated | 1 |
| `+gen_dbg_<component>=1` | `PLUSARG_DBG_*` | debug prints per component | 0 |
| `+gen_build_config=<name>` | `PLUSARG_BUILD_CONFIG` | printed in the banner (opentitan) | UNSPECIFIED |

## 4. Wave-level behaviour

Layer 1: `rand` fields with `dist` weights inside the agents' items, constrained by the current
regime. Layer 2: named regime sets per agent. Layer 3: the schedule (retirement- or cycle-count
triggers) applied through REGIME_SET commands: for each trigger Python writes `evt_retired_target` or
`evt_cycle_target` and awaits the single `evt_thresh_hit` edge (no counter is awaited, A-01); covered
by `gen_regime_cg` including transitions. Site dependency (A-25, Q-012): cocotb-master runs execute
`--local` on the submit host until the clone is on shared storage; pure-SV runs fan out on LSF.

## 5. Checkers

None: this component carries no pass/fail check (test equipment or infrastructure).

## 6. Failure path and diagnostics

`uvm_fatal GEN_UNKNOWN_PLUSARG` at time 0 for an unknown `+gen_*` plusarg (a warning is collected by
nothing, A-23); `uvm_fatal ENV_CFG` on an
unknown regime name.

## 7. Coverage hooks

`gen_regime_cg` (regime ids per agent, transition pairs); seed and schedule in the banner.

## 8. At build

Freeze the regime names per agent with the Test Writer.
