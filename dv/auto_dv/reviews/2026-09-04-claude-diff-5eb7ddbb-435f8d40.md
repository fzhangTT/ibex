# Cross-model review - committed diff 5eb7ddbb..435f8d40

**Reviewer:** claude CLI 2.1.260 (Claude Code); run-reported model: claude-fable-5-1,claude-haiku-4-5-20251001; requested effort: high (the CLI does not report the effective setting); fresh session e7fd3f30-6be2-4c41-98a2-777d5cb794a5; sandbox: bubblewrap, working directory = detached read-only checkout of commit 435f8d40b3fedda4e8793c95e6ed34b174f8328c (the live working tree is not read), filesystem read-only except this run's own output directory, scratch HOME (no access to the executing model's settings, instructions or memory), private PID namespace; network open for the model API, web tools disallowed by policy (fallback reviewer per owner ruling A-001)
**Codex unavailable because:** ERROR: You hit your spend cap set by the owner of your workspace. Ask an owner to increase your spend cap to continue.
**Wrapper:** dv/auto_dv/tools/gen_cross_review.sh blob 713e8c09 (the copy executed; equals the wrapper committed at the reviewed commit); reviewed commit 435f8d40b3fedda4e8793c95e6ed34b174f8328c
**Date:** 2026-09-04
**Target:** committed diff 5eb7ddbb..435f8d40 (echo at raw line 1)

---

TARGET: 5eb7ddbbe06c7b025ac46892c013dd7fb1d1c7b9..435f8d40b3fedda4e8793c95e6ed34b174f8328c

Reviewer identity: Claude Fable 5.1 (claude-fable-5-1), fresh session, detached read-only checkout of 435f8d4. Scope: one commit, ten .md files, 46 insertions / 25 deletions; no fcov_expectations manifest, coverpoint, cross or Sample line in the diff (confirmed from `git diff --stat`).

**What I verified against the tree**

- Convention paragraph present in all five records (bug log, fcov plan, feature list, tb architecture, test plan). Its factual content holds: the D-number series (D1..D22) and B-numbers are defined in gen_bug_log.md; sampled bare part-file citations (tp_pmp.md C-PMP-MONLY, tp_isa.md OQ-9, tp_xcut.md "Regime schedule") resolve to content present in gen_test_plan.md. No sampled part-file citation functions as sole evidence.
- Three peer re-points: dv/auto_dv/docs/gen_rv32b_otearlgrey_encodings.md exists with a promotion header; dv/auto_dv/evidence/gen_hierarchy_map.md exists and carries H-D3 (:1485), H-N1 (:1704) and "Unverified items" (:2042). Exactly three work-path citations were removed by the diff; the encodings note's header is untouched.
- CM178: the v4b review artifact's Low (:28), Info (:30) and Info (:32) match the three response rows. gen_run.py:203 is `if measured and coverage and debug_only:` at both a22c1ca and 435f8d4, so "coverage run today, every measured run once Runtime's touch lands" is the correct committed-versus-owed statement.
- Landing 15: gen_fu_l16_TRACE_index26.log is absent at HEAD (present at 5eb7ddb^); zero citations remain in the test plan and feature list. gen_fu_l16_trace17_duplicate_copies.log has 20 ICTRACE inject lines: 17 with index=26, 3 with index=27, all v0=1 v1=1 t0=t1. No trace17 artifact contains tag-write or allocation-way records. The run header is the landing-15 build (probe on, +gen_probe_ic_lookup=1), consistent with "build w18" per gen_manifest.md:3395.
- RTL citations: :534-535 is sel_way_ic1 (lowest invalid way else round-robin), :591-592 is ecc_correction_ways_d, :507-514 is the hit-data OR mux. All match the sentences that now rest on them.
- Retained verdicts: DATAMISS probe-off catch ERROR 150 on the [alert_minor] row; DATAWAY probe-off catch ERROR 557; DATAWAY and DATAMISS probe-off ablations PASS at 0. gen_critic_tb_l15.md M-2 is exactly the form (b) catch-evidence gap. No committed review of 5eb7ddb exists yet, so "remaining gate is the recorded re-review" is accurate.
- Regeneration: gen_promotion_table and gen_covergroup_set regenerate byte-identical (57 covergroups, 4093 referenced bins, 19 manifests); gen_round_credit CSV byte-identical and the .md differs only where it echoes my --csv/--md paths in the invocation line. sha256 prefixes 84a88fb2a387 and 77f93865ec8f match. Self-tests pass: gen_test_lib, gen_fcov_manifest, gen_round_credit, gen_trace_check; gen_fcov_codegen --check reports up to date.

**Rubrics (Zone A set)**: ai-slop-comments PASS, rtl-purity PASS, magic-numbers PASS, forces-and-hier-access PASS, assertion-integrity PASS. The diff touches only Markdown records; no rubric filter matches and no assertion, checker, manifest bin list, force or hand-encoded authority value is added, removed or changed.

**Findings**

[Medium][dv/auto_dv/docs/gen_test_plan.md:438] The WP-12 row now contradicts itself: its description column still says "BUILT AND UNPROVEN: every mutation of landing 14 ran with the probe on, so no named mutation has yet been caught by this form ... until probe-off DATAMISS and DATAWAY catches with their ablations land (DV Lead ruling: the plan makes no measured claim for the no-probe entries until then)", while the status column of the same row says those catches landed at 5eb7ddb, rule 2 is satisfied, and the gate is the recorded re-review. One row states two different gates and two different proof states - rewrite the description clause in the past tense (proven at landing 15 by the probe-off DATAMISS and DATAWAY catches) and name the single remaining gate, as TP-SEC-001's notes at :19388 already do.

[Low][dv/auto_dv/docs/gen_feature_list.md:4] A fourth already-committed target was missed by the v4c-2 census: the header cites dv/auto_dv/work/critic/gen_critic_feature_list_v1.md, but dv/auto_dv/docs/gen_critic_feature_list_v1.md is committed and is the path two other committed documents use - re-point it and amend the v4c-2 row count.

[Low][dv/auto_dv/evidence/gen_critic_response_plan_set_v1.md:727] The v4c-3 row says "the fact-check note and the behaviour summaries re-point" but five citations of dv/auto_dv/work/rtl-arch/gen_tp_parts_rtl_factcheck.md remain (for example feature list :1098, where "fact-check: ... X-12" is the cited support for mult_hold being unreachable), and the row names neither the re-point target nor the touch that carries it - state both so the ruling is checkable.

[Info][dv/auto_dv/docs/gen_fcov_plan.md:301] "the ENC table (dv/auto_dv/docs/gen_rv32b_otearlgrey_encodings.md, the promoted reference)": the promoted document contains no table or token named ENC (its sections 1-3 are mnemonic tables), and ENC is not an identifier in committed TB code - say "the mnemonic tables of ..." or state that the monitor's ENC table is derived from them.

[Info][dv/auto_dv/docs/gen_tb_architecture.md:11] The inserted part-file convention is vacuous for this document: it names none of the tp_/fcov_/gen_part_/trace_*_/README_*_BRIEF patterns (only gen_trace_witness_ids.csv, which is committed under dv/auto_dv/docs). Harmless; the second added sentence about other roles' work notes is the operative one.

[Info][dv/auto_dv/evidence/gen_critic_response_plan_set_v1.md:728] "checked across all five": seven trace17-named artifacts are retained (two are the compile log and sources list). The claim that none records tag writes is correct; adjust the count or say "all retained trace17 artifacts".

Final verdict: APPROVE-WITH-CHANGES
