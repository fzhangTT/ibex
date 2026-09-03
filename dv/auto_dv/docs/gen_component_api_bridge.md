# Component API: gen_bridge (cocotb-to-UVM bridge)

Owner: tb-infra. Status: skeleton written before the code (T-031, 2026-09-03; regenerated for the v2 component sections after the Critic's review); items marked
"at build" are completed when the component lands (component SV opens after the TB architecture
review). Source: `dv/auto_dv/work/tb-infra/gen_tb_arch_component_sections.md` C2; DV_prompt.txt deliverable 4 (TB architecture document,
component API documents). Conventions (shared by every component document): every runtime
knob is a plusarg whose name is a `parameter string` in `gen_tb_pkg` (column 2 below) and a
generated Python constant of the same value; every checker fails through `uvm_error` with its
id (or `uvm_fatal` where stated); `+gen_chk_<id>=0` disables exactly that checker,
`+gen_chk_all=0 +gen_chk_<id>=1` isolates one for mutation evidence (DV_prompt Section 8).

## 1. Purpose

The single object cocotb touches besides the alive/finish bits: a register-like SV interface
through which Python hands commands (interrupt, debug, regime, key mode, error arming) to the UVM
sequencers and receives event flags, without per-cycle polling on either side. C2's top-level items that are not the bridge (gen_tb_top instantiation of gen_dut_top,
clock and reset generation, plusarg parsing and the time-0 banner, the alive watchdog) are covered by
`dv/auto_dv/docs/gen_component_api_dut_top.md` (Sections 5 and 5a) until `gen_component_api_tb_top.md`
lands together with gen_tb_top in build step 2. Commands are routed by `gen_env_pkg::gen_cmd_dispatch` (a `uvm_subscriber` on `cmd_ap`): FETCH_EN to the control driver, MEM_PEEK answered by the bridge itself from `gen_mem_model::peek_word`, MISC consumed, any other kind a collected `uvm_error` until its consumer lands (step 2).

## 2. Files (planned) and how to call it

`dv/auto_dv/tb/gen_bridge_if.sv` (interface, instantiated in gen_tb_top), `dv/auto_dv/env/
gen_bridge.sv` (UVM component holding sequencer handles from `uvm_config_db`), `gen_tb/
gen_bridge.py` (Python side; handles from `gen_handles.py`).

Python: set `alive`; await `listener_armed`; raise `stim_active`; per command write `cmd_kind`,
`cmd_arg[0..3]`, `cmd_seq`, toggle `cmd_valid`, await the `cmd_ack` edge; await `evt_*` edges
instead of polling; before finishing compare `cmds_consumed` with the sent count, drop
`stim_active`, raise `finish_req`, await `finish_ack` with a caller-sized timeout. SV: `always
@(posedge cmd_valid)` captures the fields and pushes a `gen_cmd_item` to the addressed sequencer.

## 3. Knobs

| Plusarg | gen_tb_pkg name | Meaning | Default |
|---|---|---|---|
| `+gen_alive_timeout=<cycles>` | `PLUSARG_ALIVE_TIMEOUT` | SV `$fatal` if `alive` is still 0 after this many cycles (TB_CONTRACT Section 2) | GEN_ALIVE_TIMEOUT_CYCLES |
| `+gen_finish_timeout=<cycles>` | `PLUSARG_FINISH_TIMEOUT` | default finish-handshake budget (Python overrides per test). (T-068) consumed by Python: `GenBridge.finish()` uses the plusarg value when the test passes no budget; the SV default is `GEN_FINISH_TIMEOUT_CYCLES_DEFAULT` | `GEN_FINISH_TIMEOUT_CYCLES_DEFAULT` |

## 4. Wave-level behaviour

AS BUILT (step 1b, `dv/auto_dv/tb/gen_bridge_if.sv`, instance `u_bridge_if` in gen_tb_top; Python
view `gen_handles.GenHandles(dut).b.<field>`). Python-written: `alive`, `stim_active`, `cmd_valid`
(level toggled once per command), `cmd_kind[7:0]` (codes `GEN_CMD_*` from gen_tb_knobs.yaml: IRQ_SET,
IRQ_CLR, NMI_PULSE, DBG_REQ, REGIME_SET, KEY_MODE, MEM_ERR_ARM, ICACHE_ECC_ARM, FETCH_EN, MEM_PEEK, MISC),
`cmd_arg0..3[31:0]` (four scalars, not an unpacked array, for VPI robustness), `cmd_seq[15:0]`,
`evt_retired_target[31:0]` + `evt_retired_arm` (toggle after writing the target), `evt_cycle_target[31:0]`
+ `evt_cycle_arm`, `finish_req`. SV-written: `listener_armed`, `cmd_ack` (toggles the cycle after the
command is consumed), `cmd_ack_seq[15:0]`, `cmds_consumed[15:0]`, `peek_data[31:0]` (memory word answered
with the ack of a MEM_PEEK whose `cmd_arg0` is the word address; the image read-back path, v2 XM-M4;
a peek without a memory model is a `uvm_error`),
`evt_retired_hit` and `evt_cycle_hit` (v3, N-02: one single-bit toggle PER threshold, raised by the
interface's own threshold engine the first cycle at or beyond the armed target; the only thing Python
awaits for a threshold, A-01), `evt_irq_taken`, `evt_dbg_entered`, `evt_eot_seen` (single-bit toggles
from the monitors, step 2), `evt_retired_count[31:0]` (counted from the boundary `rvfi_valid`),
`evt_err_count[15:0]` (read once at finish, never awaited), `cycle_count[31:0]` (cycles since reset
release, read-only), `finish_ack` (toggled in gen_base_test's final_phase, after the UVM report). SV
captures the command fields in the delta of the `cmd_valid` edge (gen_bridge run_phase), publishes a
`gen_cmd_item` on `cmd_ap` and toggles `cmd_ack` the next cycle; two commands need two edges. UVM never
calls `$finish` (`finish_on_completion = 0`): cocotb ends the simulation after `finish_ack`. No bridge
signal is a DUT signal.

## 5. Checkers

| Checker id | Rule | Mutation classes it catches (example locus) | Disable knob |
|---|---|---|---|
| `bridge_accounting` | `cmds_consumed` equals Python's sent count at finish; every `cmd_seq` observed exactly once | n/a (TB self-check, TB_CONTRACT Section 5) | `+gen_chk_bridge_accounting=0` |

## 6. Failure path and diagnostics

`$fatal` alive watchdog; `uvm_error bridge_accounting`; Python `assert` on ack timeout (fails the
cocotb test). Every Python-side string that may be logged or raised is pure ASCII (TB_CONTRACT
Section 4); the gen_tests template enforces it. No per-cycle Python polling exists anywhere in the
TB (A-01). (T-068) `finish()` asserts the command accounting first, then drops `stim_active`, then
raises `finish_req` (TB_CONTRACT Section 2 ordering).

## 7. Coverage hooks

Command kinds and regime ids sampled into `gen_regime_cg` (layer-3 coverage). Unit test:
`dv/auto_dv/gen_tb/gen_tests/gen_ut_bridge.py` (start, 6 commands with sequence acks, two cycle
thresholds, accounting, finish) and `gen_ut_bridge_neg.py` (alive watchdog forced red); local driver
`dv/auto_dv/tb/gen_tb_local.sh`; TDD transcript `dv/auto_dv/evidence/gen_tdd_bridge.md`.

## 8. At build

Fix the kind encodings and argument layouts in the knobs YAML so SV, Python and the shim share
them.
