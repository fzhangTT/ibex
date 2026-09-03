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

## v1b (lows of the scoped re-review and the Critic's part 2, no re-review required) and v1c (re-embed + Section 9)

| Finding | Status | Where / how |
|---|---|---|
| replan review low: GEN_ICACHE_ECC_WINDOW has two anchors | fixed (v1b) | 8.2 and 8.3a define the one event the constant bounds (lookup request to alert_minor_o = 1); the invalidation write is checked as alert + 1, no second constant; TB Infra's C4.8 (T-068 revision, embedded in v1c) uses the same anchor |
| replan review low: Section 6 preamble contradicts itself on the heading shift | fixed (v1b) | one statement: two levels |
| replan review low: 8.1 numbering 1,2,3,4,6,5; 8.2 item 7 reference | fixed (v1b) | SIMULATION is item 5, checker direction item 6; 8.2 item 7 points at 8.1 item 6 |
| replan review low: Section 2.1 and C5.3b bug-id naming | fixed (v1b) for 2.1; C5.3b is TB Infra text | 2.1 names B1/BUG-06, B2/BUG-01, B3, B5, B15/BUG-03; a note before 8.3a asks TB Infra to align C5.3b in its next revision |
| replan review low: Inputs row lacks the components v2 verdict | fixed (v1b) | Inputs row lists evidence/gen_critic_tb_arch_components_v2.md, docs/gen_critic_tb_architecture_v2.md and the replan review |
| replan review medium: API docs and C9 carry retired knob names | fixed by TB Infra (T-068) and re-embedded (v1c) | Section 6 now embeds the T-068 revision (sha256 prefix in the header); no retired knob name remains in the document |
| Critic part 2 v2 lows L-1..L-8 | fixed (v1a/v1b) | see the v1a table above; L-3 fidelity repeated for the T-068 revision in v1c (flattened embed contains the source text: True) |
| new: T-080 RVFI record export addendum v2 | accepted and embedded (v1c) | Section 9 verbatim; acceptance note 8.5 (one clarification: `I` lines once per rising edge of the irq_valid level); the Orchestrator's cross-model replan review of the addendum precedes code |
| v1d: sections re-embedded at TB Infra's current revision (sha256 prefix de5bc9573c84255b, incl. the C3.4/C4.2 expected-alert feed); committed docs/gen_rvfi_export_addendum.md (4c0ba11) embedded as Section 9 and the standalone file reduced to a pointer per the Orchestrator | done (v1d) | header status; Section 6 preamble; Section 9; docs/gen_rvfi_export_addendum.md pointer |
| v1e (2026-09-03 09:40 UTC): Section 9 re-embedded from TB Infra's addendum version 2a (sha256 prefix f17d0e7897773549): one I line per rising edge of rvfi_ext_irq_valid at the rise cycle, level semantics stated (X-16 / C-13), Section 6 resolution; TB Infra disclosed that the step-2a monitor publishes ap_irq per high cycle (never fired; fixed in the T-080 build) | done (v1e) | Section 9; header status |

| v1f | Section 9 re-embedded from TB Infra's addendum version 4c (committed docs copy at 4c4b9b8, sha256 prefix e2822b1bdd62c9ba) after the Orchestrator's gate verdict dv/auto_dv/reviews/2026-09-03-claude-replan-gen_rvfi_export_addendum-r5.md (APPROVE-WITH-CHANGES); 8.5 rewritten: C-2 present (+gen_witness_ids, GEN_WITNESS_FOREIGN), 29 exact rows, and five alignment items open for TB Infra's next revision (plan-name covergroup vs SV name gen_wit_cycle_clause_cg, WIT_IDS vs WITNESS_IDS, plusarg rendering owner per the Orchestrator's ruling (Runtime's gen_run), icram lookup/tag_write/fill_write rows of WP-8, digest guard of WP-8), matching the verdict's D1, D2 and D6; header rows updated; Section 6 unchanged (de5bc9573c84255b) | DV Lead 12:0x UTC |
