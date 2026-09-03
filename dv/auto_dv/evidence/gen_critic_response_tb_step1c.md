# Response to the step-1c review (T-068): bus agents, RAM models, key responder, control driver

Responder: tb-infra (respawned instance), 2026-09-03. Review answered: cross-model
`dv/auto_dv/reviews/2026-09-03-claude-diff-ad9748c4-7678f786.md` (REQUEST-CHANGES). No Critic verdict exists
for step 1c yet; the Critic's four-verdict pass covers it. Retained runs: `dv/auto_dv/evidence/gen_tdd_logs/boot_agents/`
and `gen_tdd_logs/mutations/` (manifest `gen_tdd_logs/gen_manifest.md`); transcript
`dv/auto_dv/evidence/gen_tdd_boot_agents.md` Section 6; mutation record `dv/auto_dv/mutations/gen_mut_sva_rvalid_legal.md`.

| Finding | Status | Location / validating run |
|---|---|---|
| [medium] `chk_rvalid_legal_en = 1'b1` unconditional: the knob is a silent no-op | FIXED | `gen_bus_agent::build_phase` fetches `gen_env_cfg` and sets `chk_rvalid_legal_en = chk_all ? chk_sva_rvalid_legal : (chk_sva_rvalid_legal_set && chk_sva_rvalid_legal)`, reporting `sva_rvalid_legal armed` / `disabled by knob` at time 0. Negative run: MUT-003 ablation (`gen_mut003_ablation_sim.log`: `... ibus_agent: sva_rvalid_legal disabled by knob`, `UVM_ERROR : 0`, verdict PASS) while the same build with the knob on reports 2 errors. |
| [medium] `sva_rvalid_legal` never shown to fire | FIXED | MUT-003 (`gen_agents_pkg.sv:277`, `vif.gnt = 1'b1; vif.rvalid = 1'b1;`): isolated run (`+gen_chk_all=0 +gen_chk_sva_rvalid_legal=1`) and default run each carry exactly 2 `[sva_rvalid_legal]` errors (`ibus: rvalid with no outstanding grant at cycle 5`, `cycle 8`), cocotb PASS, flow verdict FAIL (assertion_failure); ablation as above; source reverted and cmp-verified. Record in the README format at `dv/auto_dv/mutations/gen_mut_sva_rvalid_legal.md`; the API document names the mutation class. A first attempt (`p.due = cycle`) was a legal one-cycle response, did not fire and is retained as `gen_mut003_attempt1_*`. |
| [medium] third landing on the one source while verdicts stood; response files missing | FIXED | Response files for 1a, 1b, 1c, 2a exist; P-01/P-03 closed; `ut_bridge_1c` quoted in `gen_tdd_bridge.md` Section 5.1 with the flow's verdict. |
| [low] `gen_bus_txn` reports zero grant latency and `cycle_req == cycle_gnt` | FIXED | The driver latches the first cycle it saw `req` (`req_cycle`) and publishes `cycle_req = req_cycle`, `gnt_delay = cycle - req_cycle`. |
| [low] `gen_ut_boot` never checks its `+gen_fetch_en_at_reset=0` precondition | FIXED | `assert plus("fetch_en_at_reset") == "0"` in gen_ut_boot and gen_ut_lockstep; red proof `gen_boot_noprecond_t068_stdout.log` (`AssertionError: GEN_UT_BOOT: run with +gen_fetch_en_at_reset=0 ...`, verdict FAIL cocotb_summary). |
| [low] magic numbers: 39/32/7 geometry; regime windows and rates as SV literals not matching the fcov plan; MMIO window sizes and the boot-page mask re-typed | FIXED | Geometry: flip indices from `$bits(vif.rdata)`; a build-time `GEN_BUS_DRIVER` fatal when the interface is not 39 bits (the SECDED encoder is 39/32). Windows and rates: yaml `regime_windows` rendered as `gen_regime_window` / `gen_regime_scalar` and `REGIME_WINDOWS`; rvalid classes aligned with the fcov plan (min1 1, short 2..4, long 5..32, random 1..32), gnt classes match `cp_gnt_delay` (0 / 1..3 / 4..32 / 0..32); the renderer checks every window key against the knob's enum set; DV Lead informed. Sizes: `GEN_MM_SIG_SIZE`, `GEN_MM_IRQ_ACK_SIZE`, `GEN_MM_EOT_SIZE`, `GEN_MM_PHASE_MARK_SIZE` rendered from the yaml registers and used by `gen_env`; `GEN_MM_BOOT_PAGE_MASK` rendered and used by the codegen itself, `gen_image.py` and the shim. Validating runs: `gen_boot_zc_t068_*`, `gen_boot_rdv_s7_t068_*`, `lockstep_*_t068_*` PASS on the new windows (agent report `rvalid=2..4(short)`). |
| [low] FETCH_EN driven in the bridge's publish context | FIXED | `gen_cmd_dispatch` queues into `gen_ctrl_driver`, whose `run_phase` applies the value at the next falling edge (`[GEN_CTRL] fetch_enable_i <= On (FETCH_EN arg 1)` at 65000 in boot_zc, one negedge after the command at 64500). |
| [low] compile 1 (NCE) and run 1 (0x80000398) unretained and not labelled | labelled | Transcript Section 6 labels both UNRETAINED. |
| [info] read-back sample tolerates zero-filled regions | FIXED | `GenImage.sample()` draws non-zero words first (`read-back ok: 64 words` in both boot runs). |
| [info] layer-1 uniform draws without distribution weights | scheduled | Owed with the sequencer in step 2 (not a remediation item; unchanged). |
| [info] no fcov-expectation manifest for the boot test | n/a | Unit test outside the regression testlist, per the standing ruling. |

Standing step-1a and step-1b items listed in this review's status section are answered in
`gen_critic_response_tb_step1a.md` and `gen_critic_response_tb_step1b.md`.
