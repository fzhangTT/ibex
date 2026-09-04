# Cross-model review - committed diff dde456f5..fe7ad0b4

**Reviewer:** claude CLI 2.1.260 (Claude Code); run-reported model: claude-fable-5-1,claude-haiku-4-5-20251001; requested effort: high (the CLI does not report the effective setting); fresh session 2de01aa6-359f-45ad-9ec3-2bec342aa2fd; sandbox: bubblewrap, working directory = detached read-only checkout of commit fe7ad0b43f877c43b25af4ef6ad0de1caf5b2788 (the live working tree is not read), filesystem read-only except this run's own output directory, scratch HOME (no access to the executing model's settings, instructions or memory), private PID namespace; network open for the model API, web tools disallowed by policy (fallback reviewer per owner ruling A-001)
**Codex unavailable because:** ERROR: You hit your spend cap set by the owner of your workspace. Ask an owner to increase your spend cap to continue.
**Wrapper:** dv/auto_dv/tools/gen_cross_review.sh blob 713e8c09 (the copy executed; equals the wrapper committed at the reviewed commit); reviewed commit fe7ad0b43f877c43b25af4ef6ad0de1caf5b2788
**Date:** 2026-09-04
**Target:** committed diff dde456f5..fe7ad0b4 (echo at raw line 1)

---

TARGET: dde456f508dbaa5b291f5157b6462aa2a46fd12a..fe7ad0b43f877c43b25af4ef6ad0de1caf5b2788

Reviewer identity: Claude Fable 5.1 (claude-fable-5-1), fresh session, detached read-only checkout of fe7ad0b. Scope: the single commit fe7ad0b on base dde456f, eleven files, +92/-53, all `gen_`-prefixed Markdown and CSV under dv/auto_dv/docs and dv/auto_dv/evidence. No RTL, SV, Python or manifest in the diff (confirmed with `git diff --stat`).

**What I verified against the repository**

- RTL anchors: rtl/ibex_icache.sv 499-501 tag compare with forced valid bit, 507-514 OR mux under one shared `data_tweak_lw_ic1`, 534-535 lowest-invalid-else-round-robin way select, 541 the ECC generate block, 568-573 per-bank `prim_secded_inv_39_32_dec` on the muxed word, 585 error term qualified by hit, 588-592 correction ways. `fill_addr_q` appears in zero equality comparisons. All plan citations resolve.
- Masked-case confinement: the bug log S5 row, the F-IC-042 What, the cp_multiway_mismatch.masked bin text and the TP-IC-038 fire-check all now restrict OR-restoration to one copy being a corrupted image of the other, and TP-IC-038 says the masked outcome does not apply to its store-produced copies. The old "valid in one way only" qualifier has zero occurrences; the cp_alert_pulses qualifier is "the injection owes a pulse" with the two-way rising-flip case spelled out.
- Bins: the csv row for CG-IC-006.cp_no_alert_case.masked_duplicate_copy moved from TP-IC-044 to TP-SEC-001; TP-SEC-001's Bins line (19444-19448) carries it; TP-IC-044 keeps four bins (17974-17975); the fcov plan's CG-IC-006 TP-items line and Tests table gained TP-SEC-001 / gen_sec_alert_inject_icache, which is TP-SEC-001's test group (19443). `gen_trace_check.py` PASSes in this checkout.
- Doc citations: icache.rst:214 reads "Any error (single or double bit) in any RAM will effectively cancel a cache hit in IC1"; :73-74 and :218 as cited. D22 now carries :214.
- Checker anchors: attribute_pulse (634), pending_in_window (620), resolve_held (668-672), close_owed (674), judge_data (594) exist by name; no `:489-495`, `:496-499`, `:502-503` or "oldest-unseen"/"oldest first" remains in the plan docs. The resolve_held description (release when own window has no pending verdict, arrival order among those released together) matches the code.
- Form (b) figures: 148 of 494 and 27 of 180 are the landing-14 review's major-row figures (dv/auto_dv/reviews/2026-09-04-claude-diff-508ffbc2-a28d1ae7.md:25) and the Critic's tb_l15 noprobe tails; DATAMISS and DATAWAY are the named mutants. Ruling (1) is consistent with both records.
- Regenerated files: the promotion table header sha 35148447e544 matches gen_test_plan.md at fe7ad0b; covergroup set changes are line-number shifts plus the label; credit report and summary change label and digest only.
- Every CM175 and CM176 row marked "fixed" has a corresponding text change in the diff; CM175-I-3 is honestly marked "correct, no text change".
- Rubrics: no changed file falls under any of the five filter sets; no assertion, checker, force, comment or manifest bin list is added or removed. ai-slop-comments, rtl-purity, magic-numbers, forces-and-hier-access, assertion-integrity: all `{"status": "PASS"}`.

**Findings**

[Medium][dv/auto_dv/docs/gen_test_plan.md:438] The WP-12 status cell still says "BUILT at a28d1ae (the landing's own review record is not written yet, so this cell claims built and not reviewed)". At fe7ad0b that record exists twice: the cross-model review dv/auto_dv/reviews/2026-09-04-claude-diff-508ffbc2-a28d1ae7.md (APPROVE-WITH-CHANGES, committed 96bb84c) and the Critic's tb_l15 verdict gen_critic_tb_l15.md (REQUEST-CHANGES, committed 7b2765b), and the same cell now quotes that review's major-row figures. The status column contradicts the row's own content and hides a gating REQUEST-CHANGES on the landing it calls built. - Replace the parenthesis with the actual state: reviewed at 96bb84c APPROVE-WITH-CHANGES, Critic tb_l15 REQUEST-CHANGES on form (b)'s catch evidence, landing 15 owed.

[Medium][dv/auto_dv/docs/gen_test_plan.md:22421] The knob:icache_ecc_bits row says both transferred conditions "are enforced through the active rate knob's row" and that "Runtime pins that with a self-test case in which the bit count is two". Neither holds in the committed flow: MEASURED_KNOB_CONDITIONS (dv/auto_dv/flow/gen_flow_const.py:454-459) carries only the tag knob `icache_ecc_err_rate`; `icache_data_ecc_err_rate` appears nowhere under dv/auto_dv/flow/, so a measured run with the data rate on and the alert_minor row off is not refused today, and gen_run.py's self_test (245-260) has no bit-count case. The adjacent data-rate row (22420) likewise states the Q-018 extension as enforced. Ruling (3) is sound, but the plan text is ahead of the flow without saying so. - Mark both rows "plan condition; flow row and self-test owed from Runtime, not in the committed refusal table at fe7ad0b" until the widening lands.

[Low][dv/auto_dv/evidence/gen_critic_response_plan_set_v1.md:709] The F1 row's Where column ends "so plan and flow describe one rule", but gen_run.py:203 still refuses only `measured and coverage and debug_only`; the LOG-067 B8 rule two lines below is the one that also refuses coverage-off. The WP-12 cell (438) words it as a ruling that the refusal "widens", which is acceptable, but the response row claims present agreement. - Say "the flow's P6 widening is owed from Runtime (parked touch), not yet committed; the plan wording leads".

[Low][dv/auto_dv/docs/gen_test_plan.md:17872] TP-IC-038's fire-check (and the same sentence in gen_feature_list.md:11341-11342 and gen_fcov_plan.md:4820-4823) says "an OR that happens to equal one codeword delivers that copy's data, which is stale rather than correct". OR(A,B) equals A exactly when B's set bits are a subset of A's; A may be either copy. When it is the second fill's post-store word, the fetched word is the new one, not stale. Only the old-codeword case is stale. - Say "delivers that copy's data, stale when it is the pre-store copy".

[Info][dv/auto_dv/docs/gen_feature_list.md:11341] The F-IC-042 What anchors the per-bank decoder at ":541, :569-572"; line 541 is the `if (ICacheECC) begin : gen_data_ecc_checking` generate header and the decoder instance spans 568-573. Carried over from the v3y record; harmless but imprecise. - Cite 568-573 alone.

Rulings judged: (1) form (b) built and unproven with the judged fractions as its power is consistent with the landing-14 review and tb_l15; (2) the P9 measured-regression wording is a sound rule but ahead of gen_run.py, and only the response row overclaims; (3) the bit-count knob inheriting through the rate row is the right structure, but the data-rate row it inherits through does not exist in the flow yet. No row is marked answered without a text change.

Final verdict: APPROVE-WITH-CHANGES
