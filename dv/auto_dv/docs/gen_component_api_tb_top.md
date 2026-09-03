# Component API: gen_tb_top (VCS -top and cocotb TOPLEVEL)

Owner: tb-infra. Status: skeleton written before the code (T-031, 2026-09-03; regenerated for the v2 component sections after the Critic's review); items marked
"at build" are completed when the component lands (component SV opens after the TB architecture
review). Source: `dv/auto_dv/work/tb-infra/gen_tb_arch_component_sections.md` C2; DV_prompt.txt deliverable 4 (TB architecture document,
component API documents). Conventions (shared by every component document): every runtime
knob is a plusarg whose name is a `parameter string` in `gen_tb_pkg` (column 2 below) and a
generated Python constant of the same value; every checker fails through `uvm_error` with its
id (or `uvm_fatal` where stated); `+gen_chk_<id>=0` disables exactly that checker,
`+gen_chk_all=0 +gen_chk_<id>=1` isolates one for mutation evidence (DV_prompt Section 8).

## 1. Purpose

The top of the generated TB: declares the 19 opentitan configuration parameters and forwards them
to `gen_dut_top u_dut`, generates clock and reset, hosts the cocotb bridge, the interface instances
and (from step 1c) the agents and RAM models, runs the single UVM test `gen_base_test` and owns the
alive watchdog. Python (cocotb) owns the end of simulation. AS BUILT (step 1c): interfaces `u_ibus_if`, `u_dbus_if` (gen_bus_if), `u_scrkey_if`, `u_ctrl_if` (fetch_enable_i, mcounteren_writable_i), the four `gen_icache_ram` instances and the bridge `u_bridge_if`; only the interrupt and debug pins stay tied idle. (T-068) `hart_id_i` from `+gen_hart_id` (default 0), `boot_addr_i` from `+gen_boot_addr`; the clock half period is written in explicit ns (`* 1ns`); `irq_fast` width derives from `ibex_pkg::irqs_t`. Milestone: `dv/auto_dv/evidence/gen_tdd_boot_agents.md` (boots and retires on the directed Zc program and a riscv-dv program).

## 2. Files (planned) and how to call it

`dv/auto_dv/tb/gen_tb_top.sv`, filelist `dv/auto_dv/tb/gen_tb.f` (compiled after `gen_rtl.f`, with
`+incdir+dv/auto_dv/tb` for the rendered `gen_env_cfg_knobs.svh`); UVM environment
`dv/auto_dv/env/gen_env_pkg.sv`; local driver `dv/auto_dv/tb/gen_tb_local.sh` (compile with the
SIM_RECIPE Section 4 cocotb triple; run one Python module with plusargs).

Runtime's build entry compiles `gen_rtl.f` + `gen_tb.f` with `-top gen_tb_top`, `+define+RVFI`
and the cocotb triple; every test runs `+UVM_TESTNAME=gen_base_test` with `MODULE=<cocotb test>`,
`TOPLEVEL=gen_tb_top`. `gen_tb_top` puts the bridge virtual interface into `uvm_config_db` and calls
`run_test()`; `gen_base_test` builds `gen_env_cfg` from plusargs (rendered `parse_plusargs()`; any
unknown `+gen_*` is `uvm_fatal GEN_UNKNOWN_PLUSARG`, an enum value outside its yaml set is
`uvm_fatal GEN_BAD_KNOB`), prints the TB banner and builds `gen_env`. Step 1b ties the DUT inputs the
agents will drive to their idle values (no grant, no response, key valid, no events).

## 3. Knobs

| Plusarg | gen_tb_pkg name | Meaning | Default |
|---|---|---|---|
| `+gen_boot_addr=<hex>` | `PLUSARG_BOOT_ADDR` | boot_addr_i (default GEN_BOOT_ADDR_DEFAULT; must match the image entry page) | GEN_BOOT_ADDR_DEFAULT |
| `+gen_hart_id=<n>` | `PLUSARG_HART_ID` | hart_id_i (T-068) | 0 |
| `+gen_alive_timeout=<cycles>` | `PLUSARG_ALIVE_TIMEOUT` | alive watchdog budget: `$fatal GEN_ALIVE_TIMEOUT` if Python has not set `alive` (TB_CONTRACT Section 2) | GEN_ALIVE_TIMEOUT_CYCLES_DEFAULT |
| `+gen_build_config=<name>` | `PLUSARG_BUILD_CONFIG` | echoed in the banner | opentitan |
| `+ntb_random_seed=<n>` | `(VCS)` | the one run seed; Python's RANDOM_SEED must equal it (both echoed at time 0) | - |

## 4. Wave-level behaviour

Clock period `GEN_CLK_PERIOD_NS` (10 ns, `ClkHalfPeriodNs = 5`); asynchronous active-low reset released
after `ResetCycles` (5) clock edges; `rvfi_valid` feeds the bridge's retirement counter. Banner lines start
with `GEN_CONFIG_BANNER` (wrapper lines from gen_dut_top plus the TB's: seed, build_config, pinned knob
count, regime_sched derived-or-supplied, the SIMULATION define state for F-DIT-025, the COCOTB_SIM define
state, alive/finish budgets, image path). `ifndef RVFI` is a compile-time `$fatal`.

## 5. Checkers

No checkers. TB self-checks: the alive watchdog (`$fatal GEN_ALIVE_TIMEOUT`), the objection held until
`finish_req`, the time-0 refusal of a non-cocotb build (`uvm_fatal GEN_NO_COCOTB`, T-068), and the time-0
width guards on MemDataWidth and the derived-constant mirrors (`$fatal`, T-068). None has a disable knob.

## 6. Failure path and diagnostics

`$fatal GEN_ALIVE_TIMEOUT`; `uvm_fatal GEN_UNKNOWN_PLUSARG` / `GEN_BAD_KNOB` / `GEN_BASE_TEST`; UVM
errors from the environment fail the run through the flow's log scan (SIM_RECIPE Section 5). Python
asserts fail the cocotb test.

## 7. Coverage hooks

None directly (the banner is the time-0 evidence).

## 8. At build

Step 1c replaces the tie-offs with the bus agents, RAM models and scramble-key responder and adds the
build entry for Runtime (the "boots and retires" milestone); step 2 bundles the RVFI signals into
`gen_rvfi_if` and the misc outputs into `gen_misc_if`; R-02/R-03 of the smoke top stay owed there.
