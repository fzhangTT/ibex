# Cross-model review - committed diff 5baa4f52..36bc3a4c

**Reviewer:** claude CLI 2.1.260 (Claude Code); run-reported model: claude-fable-5-1,claude-haiku-4-5-20251001; requested effort: high (the CLI does not report the effective setting); fresh session 300a8de8-f4ad-487f-bed2-7423afa224c5; sandbox: bubblewrap, working directory = detached read-only checkout of commit 36bc3a4c12a352132a1b15437ce58ab3ef523aeb (the live working tree is not read), filesystem read-only except this run's own output directory, scratch HOME (no access to the executing model's settings, instructions or memory), private PID namespace; network open for the model API, web tools disallowed by policy (fallback reviewer per owner ruling A-001)
**Codex unavailable because:** ERROR: You hit your spend cap set by the owner of your workspace. Ask an owner to increase your spend cap to continue.
**Wrapper:** dv/auto_dv/tools/gen_cross_review.sh blob 713e8c09 (the copy executed; equals the wrapper committed at the reviewed commit); reviewed commit 36bc3a4c12a352132a1b15437ce58ab3ef523aeb
**Date:** 2026-09-04
**Target:** committed diff 5baa4f52..36bc3a4c (echo at raw line 1)

---

TARGET: 5baa4f526ff93a805e99c620451f90f12578c7b9..36bc3a4c12a352132a1b15437ce58ab3ef523aeb

Reviewer identity: claude-fable-5-1 (Claude Code CLI), fresh session, detached read-only checkout of 36bc3a4. Scope: one commit, ten files, verified against the repository rather than the hand-off.

**What I verified and found correct**

- The four stale clauses ("OWED to TB Infra's 1c", "not credited until 1c passes", "the entry bound alone does not decide", "T-136 and T-137 lifted") grep to zero, case-insensitive, in all four plan documents. The corrected hold-answer wording is at nine sites in gen_test_plan.md and "landing 7 by the per-line release" at eight.
- The re-keyed IRQ Notes say only what the sources establish. gen_critic_tb_l1c.md:29 says T-136 MAY LIFT and lists "the irq_entry bound restarting at every entry (fu2a M-5, owed with conditions)" as still owed to 2b; :30 says T-137 MAY LIFT for bus-error arming with T-183 owed to 2b; :47 repeats it. gen_critic_tb_l7.md:77-78 says M-5 "CLOSED by the per-line release and the end-of-run rule with MUT-NT / MUT-NT2", with the two reds at :59-60. fb8137e is the tb_l1c verdict commit; 9e912bb is landing 1c; LOG-074 (gen_intervention_log.md:1710) lifts the T-183 carve-out and its :1722 keeps TP-IRQ-079 / TP-SEC-025 COUNTED-ONLY, which no later LOG entry (075 to 084) changes, so Section 1.8 and the TP-IRQ-079 tail are current against HEAD.
- Bug log and PS-1: over the 12 retained popret log files, "popret" hits 12 lines in 8 files (1 per run_header, 2 per stdout excerpt, 0 in the four verdict files); "800003ff" hits none; the store line with "(4 bytes)" hits once in each of the four excerpts and the elided form is at zero in both records.
- LOG-084 split note: 15 coverpoint bins plus 14 cross bins (8+2+4) equals the plan's 29; the ruling text at :1897-1899 (fifteen declared now, fourteen owed) and the false-pass mechanism (:1893-1896, last-coverpoint attribution, three coverpoints sharing "yes") are stated accurately.
- Generated records: gen_test_plan.md sha256 at HEAD starts 5f8e08b05580 as the promotion table states; the covergroup set .md/.csv changes are the label plus gen_fcov_plan.md line anchors only. In this checkout `gen_fcov_codegen.py --check` reports up to date, both self-tests PASS, and gen_trace_check.py PASS.
- Rubrics: no rtl/, .sv, .svh, .py or ci/ line is in the range, so rtl-purity, forces-and-hier-access, magic-numbers and assertion-integrity are `{"status": "PASS"}`. ai-slop-comments over docs/**: the added text is plan prose, not code comments; `{"status": "PASS"}`.

**Findings**

[Medium][dv/auto_dv/docs/gen_fcov_plan.md:290] The Bin-syntax convention's six-line paragraph "How a cross bin is reached, since the mechanism is easy to state wrongly ... is a component-value problem, not a cross-declaration one" is now present twice verbatim (lines 284-290 and 290-296). At 5baa4f5 it appeared once; this commit pasted a second copy, which neither the commit subject nor any response row declares. The duplicate is also what shifted every gen_fcov_plan.md anchor in gen_round0_covergroup_set.md/.csv by exactly +6 lines, so the 114/122-line churn there is a side effect of this defect rather than a plan change. - Remove the duplicate in the parts6 source, regenerate the plan, and regenerate the covergroup set so the anchors return.

[Low][dv/auto_dv/docs/gen_fcov_plan.md:4845] "In practice this is a measured-run bin.." now ends with two periods; this is the clause CM193-I-1 fixed for a missing terminal period, and this commit's diff line is the one that added the second. - One period.

[Low][dv/auto_dv/evidence/gen_critic_response_plan_set_v1.md:800] The CM196-I-2 row says "its Section 5 line says T-183 owed to 2b". In gen_critic_tb_l1c.md T-183 appears at :7 (header), :30 (Section 4) and :47 (Section 6); Section 5 (Findings, :32-41) does not mention it. The plan sites themselves cite Section 4 correctly. - Cite Section 4 (or Section 6).

[Low][dv/auto_dv/evidence/gen_critic_response_plan_set_v1.md:780] The PS-3 row still reads "fb8137e is the Critic tb_l1c verdict with T-136 and T-137 lifted" with no SUPERSEDED or CORRECTED clause, while CM196-I-2 records that exact wording as a compression and fixes it at the plan sites. Under the record's own CONVENTION row (:747) and the CM183-L-3 / CM186-M-1 precedent, a row whose wording a later row corrected carries a clause naming that row. CM193-M-1 (:785) carries a CORRECTED clause for the over-attribution but its own text repeats the same compression without one. - Add a clause naming CM196-I-2 to PS-3 and extend CM193-M-1's clause to cover the compression.

[Low][dv/auto_dv/docs/gen_fcov_plan.md:76] The Section 0 Bin-naming rule still says cross bins are named in the form "the plan, the CSV and the manifests use" and points only at Q-017 for the checker gap, while LOG-084's interim ruling (gen_intervention_log.md:1903) says "Until then no manifest may claim a cross bin." The LOG-084 fold reached only the CG-IC-006 split note, so the general manifest rule the Test Writer reads carries no trace of the interim ban. - Add one clause to the Bin-naming rule citing LOG-084.

Final verdict: APPROVE-WITH-CHANGES
