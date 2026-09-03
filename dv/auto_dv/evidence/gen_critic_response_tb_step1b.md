# Response to the step-1b reviews (T-068): TB top, bridge, environment skeleton, memory model

Responder: tb-infra (respawned instance), 2026-09-03. Reviews answered: Critic
`dv/auto_dv/docs/gen_critic_tb_step1b_dv_principles_v1.md` (REQUEST-CHANGES) and the cross-model review
`dv/auto_dv/reviews/2026-09-03-claude-diff-b8e361d9-efe2a3ed.md` (APPROVE-WITH-CHANGES). Retained runs:
`dv/auto_dv/evidence/gen_tdd_logs/bridge/` (manifest `gen_tdd_logs/gen_manifest.md`); transcript
`dv/auto_dv/evidence/gen_tdd_bridge.md` Section 5. Build: `gen_tdd_logs/boot_agents/compile_t068.log` (vcs exit 0, 0 errors).

## Critic findings

| Finding | Status | Location / validating run |
|---|---|---|
| M-1 uvm_error never forced red in the dangerous form (cocotb PASS, UVM_ERROR > 0) with the flow's verdict | FIXED | Two retained runs, both judged by `gen_verdict.decide` (the function `gen_run.py` uses): the accidental step-1c run `gen_ut_bridge_1c_uvm_error_*` (REGIME_SET without a consumer: `UVM_ERROR : 1`, `TESTS=1 PASS=1`, verdict FAIL uvm_error) and the deliberate `gen_neg_uvm_error_cocotb_pass_t068_*` (`+gen_boot_addr=00000000`: 23 `MEM_UNMAPPED` errors, `TESTS=1 PASS=1 FAIL=0`, `verdict: FAIL`, `reason: uvm_error at log line 30`). The MEM_PEEK-without-model branch the Critic named is unreachable from a run at HEAD (`gen_env` always builds the model), stated in the transcript. |
| L-1 `finish()` drops `stim_active` before its own assert | FIXED | `gen_bridge.py finish()`: assert accounting, then `stim_active = 0`, then `finish_req`; `gen_ut_bridge_green_t068_*` PASS. |
| L-2 `gen_ut_bridge_neg.py` uses `dut.clk` | FIXED | Handles through `GenHandles(dut)`, one `Timer` in ns from `GEN_CLK_PERIOD_NS`; `gen_neg_noalive_t068_sim.log`: `GEN_ALIVE_TIMEOUT: Python never set the alive bit within 3000 cycles`, verdict FAIL sv_fatal. |
| L-3 `hart_id_i` tied to a literal | FIXED | Knob `+gen_hart_id` (hex, default 0) in the yaml; `gen_tb_top` reads it beside `+gen_boot_addr`; the banner prints both (`GEN_CONFIG_BANNER boot_addr=0x80000000 hart_id=0x00000000 ...`). |
| L-4 `runs_summary.txt` cocotb columns disagreed with the logs | FIXED | The columns are gone; `gen_tb_local.sh` records the flow's verdict and reason from `gen_verdict.decide(sim.log, marker, rc, extra_logs=[stdout.log])` in `verdict.txt` and the summary (`gen_runs_summary_t068.txt`). |
| L-5 no UTC header on the bridge red log | FIXED (convention) | Every local run writes `run_header.txt` with a UTC stamp, host, seed, module and plusargs (`*_t068_run_header.txt`); the tdd logs carry stamps. |
| L-6 step-1a P-01..P-03 open | FIXED | See `gen_critic_response_tb_step1a.md`. |
| I-1 `kind_name()` re-types the command names | FIXED | Rendered `gen_cmd_name()` in gen_tb_pkg.sv (unit test `OK pkg gen_cmd_name maps <i> to <K>` x11); `gen_cmd_item::kind_name()` calls it. |
| I-2 `gen_ut_handles.py` docstring narrates history | FIXED | Removed. |
| I-3 banner does not print boot_addr | FIXED | As L-3. |

## Cross-model findings

| Finding | Status | Location / validating run |
|---|---|---|
| [medium] codegen extended while its REQUEST-CHANGES stood; response file and re-review missing | FIXED | P-01/P-03 closed (step-1a response); this file and its siblings exist; the re-review is the Orchestrator's T-068 gate. |
| [medium] `+gen_finish_timeout` has no consumer | FIXED | `GenBridge.finish()` takes the plusarg when the caller passes no budget (`finish_timeout_cycles()`); the SV default is the new constant `GEN_FINISH_TIMEOUT_CYCLES_DEFAULT` through `default_from`; the API document row says so. |
| [low] clock delay in the compile timescale | FIXED | `forever #(ClkHalfPeriodNs * 1ns) clk = ~clk;` |
| [low] VCS flags re-typed from `gen_flow_const.py` | FIXED | `gen_tb_local.sh` reads `VCS_BASE_FLAGS + VCS_UVM_FLAGS + VCS_COMMON_FLAGS + VCS_DEBUG_PP_FLAGS + COCOTB_DEFINE` from the module (NUL-separated) and records them in `config_opts.txt` (`gen_config_opts_t068.txt`). |
| [low] `gen_ut_bridge_neg.py` `dut.clk` and 20000 `ClockCycles` | FIXED | As Critic L-2. |
| [low] bare bool plusargs silently ignored | FIXED | `check_unknown_plusargs` fatals `GEN_BARE_PLUSARG` on a known bool name without `=` (rendered `gen_is_bool_plusarg`); `gen_neg_bare_bool_t068_sim.log`: `UVM_FATAL ... [GEN_BARE_PLUSARG] +gen_chk_all needs =0 or =1 ...`, verdict FAIL uvm_fatal. |
| [low] widths mirrored from gen_dut_top; `irq_fast [14:0]` | FIXED (irq_fast) / DISPUTED (MemDataWidth) | `irq_fast` is `[GEN_IRQ_FAST_W-1:0]` with `GEN_IRQ_FAST_W = $bits(GEN_IRQS_ZERO.irq_fast)` from `ibex_pkg::irqs_t`. `MemDataWidth` stays a mirror of the wrapper's derivation because a `gen_dut_pkg` would change the approved DUT wrapper (T-005); instead `gen_tb_top` fatals at time 0 when `MemDataWidth != $bits(u_dut.instr_rdata_i)` (`GEN_WIDTH_GUARD`), so a drift is loud, not silent. |
| [low] history narration in three comments | FIXED | `gen_ut_handles.py`, `gen_ut_mem_model_top.sv`, `gen_ut_knobs_codegen.py` (and `gen_ut_isa_shim.cc`, `gen_ut_lockstep.py`). |
| [low] API doc placeholders (`(none)` checker row, duplicate bridge fields, no mem-model AS BUILT) | FIXED | `gen_component_api_tb_top.md` (self-checks sentence, no knob column), `gen_component_api_bridge.md` (deduped, finish order and finish_timeout sentences), `gen_component_api_mem_model.md` (AS BUILT paragraph with functions, ids and knobs). |
| [info] two compile defects unretained | labelled | Transcript Section 5 labels them UNRETAINED. |
| [info] `peek_fn_t` unused | FIXED | Removed in 7678f78 (verified by the step-1c review). |
| [info] vacuous-pass guard owed | FIXED | `gen_base_test::build_phase` fatals `GEN_NO_COCOTB` unless `COCOTB_SIM` is defined; proven on a pure-SV build (`gen_neg_no_cocotb_t068_sim.log`: `UVM_FATAL ... [GEN_NO_COCOTB] ...` at time 0). |
