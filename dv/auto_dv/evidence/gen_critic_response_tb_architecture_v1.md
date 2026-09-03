# DV Lead response: TB architecture document reviews (cross-model delta review + Critic part 2)

Artifact: dv/auto_dv/docs/gen_tb_architecture.md v1a (sha256 prefix 31f11d3fc8617523, adopted 2026-09-03 08:04 UTC).
Reviews answered: dv/auto_dv/reviews/2026-09-03-claude-plan-gen_tb_architecture.md (cross-model delta review,
REQUEST-CHANGES: 1 high, 3 medium, 3 low, 1 info) and dv/auto_dv/docs/gen_critic_tb_architecture_v1.md (Critic
part 2, APPROVE with lows L-1..L-8). Nothing is disputed. Built by dv/auto_dv/work/dv-lead/gen_build_arch_v1a.py from
the v1 document and TB Infra's version 3 sections (sha256 prefix b9a3cc16eccec313), so the fold-in is reproducible.

| Finding | Severity | Status | Where / how in v1a |
|---|---|---|---|
| XM High (Section 5 scope mechanism) | high | fixed | Section 5 rewritten to the committed mechanism: cov_trees two disjoint roots, info_trees [u_dut], gate row = per-metric sum of covered/total over the gated URG rows, n/a rule, rule text in gen_runtime_api.md Sections 3 and 7d; admissibility argument under DV_prompt Section 4 stated; the false fcov-plan cross-reference replaced by a real sentence in gen_fcov_plan.md Section 0 (plan v2a); Runtime task done (T-057/T-062) |
| XM Medium 1 (rulings not in the log; gen_flow_const) | medium | fixed | Section 5 and 8.1 cite Q-014 (scope, owner-visible) and R-002 (glitch); the flag is described as extra_vcs_args on both testlist build entries, never a flow constant |
| XM Medium 2 (identifier drift: rvalid knob, bridge event, offset constants, bug ids) | medium | fixed | v3 sections embedded verbatim (the drifted names were in the v2 embed): +gen_chk_sva_rvalid_legal, evt_retired_hit / evt_cycle_hit; 8.2 item 4 and the predicted-constants line use GEN_CSR_WRITE_TO_RVFI_OFFSET / GEN_TRAP_TO_RVFI_OFFSET; 8.1 item 5 bug ids B1/BUG-06, B2/BUG-01, B15/BUG-03; new Section 8.3a is the single name list (knobs, bridge fields, constants, bug ids, seeds) |
| XM Medium 3 (Section 7 incomplete) | medium | fixed | Section 7 lists Q-001, Q-002 (revised), Q-003..Q-014, R-002 and F-001 with condensed text, default and status |
| XM Low 1 (stale status, missing hash, v3 exists) | low | fixed | header status names the Critic v2 APPROVE with its conditions, the embedded v3 hash, the Critic part-2 verdict and this response; 6.13 retired (folded into v3) |
| XM Low 2 (GEN_ICACHE_ECC_WINDOW event) | low | fixed | 8.2: window 1 counted from the lookup request; alert alone 0 from the corrupted-rdata cycle; icram_ecc_response completes 1 cycle later |
| XM Low 3 (seed_used) | low | fixed | Section 4.2: seed, plus seed_used cross-checked against riscv-dv seed.yaml for generated programs |
| XM Info (knob count/form) | info | fixed | 8.3 item 4 and 8.3a: 20 regime knobs from gen_tb_knobs.yaml, +gen_knob_<name>=<value>, +gen_regime_sched, no +gen_regime_seed |
| XM Test Writer readiness note (gen_runtime_api.md not cited) | note | fixed | header governing-documents row cites gen_runtime_api.md for testlist schema, expected_fail, tiers, manifests, run requests |
| Critic L-1 (non-existent ports in 1.1) | low | fixed | scramble_key_i, scramble_nonce_i, ram_cfg_i removed from Section 1.1 (the remaining mention is v3 C1's list of ibex_top-only ports) |
| Critic L-2 (WAIT_SLEEP dip wording in 2.1) | low | fixed | port-level rule (ctrl_busy dip hidden by if_busy / lsu_busy) |
| Critic L-3 (version lag; hash; 6.13) | low | fixed | v3 embedded verbatim with a two-level heading shift; fidelity check in the build script (v3 text found in the flattened embed: True); 6.13 retired |
| Critic L-4 (knob names in 4.2) | low | fixed | Section 4.2 uses the codegen names |
| Critic L-5 (status, gitignored citations, log cites) | low | fixed | header and Section 6 preamble cite committed paths (evidence/gen_critic_response_tb_arch.md, evidence/gen_critic_response_feature_list_v1.md, evidence/gen_critic_tb_arch_components_v2.md); Q-014 / R-002 cited |
| Critic L-6 (info tree) | low | fixed | Section 5 describes info_trees: [u_dut] as implemented |
| Critic L-7 (Section 7 omissions) | low | fixed | as XM Medium 3 |
| Critic L-8 (ECC window wording) | low | fixed | as XM Low 2 |

Items recorded for other roles: TB Infra removes the three retired regime-knob names still present in v3 C9
(Section 6 preamble and 8.3 item 4); the checker-id concordance requested by the Critic's plan-set review lives in
gen_test_plan.md Section 0a (plan v2a). SIMULATION define ruling (stays undefined) recorded in 8.1 item 6.
