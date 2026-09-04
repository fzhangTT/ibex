# Cross-model review - committed diff 678b27b6..bbe7ee8a

**Reviewer:** claude CLI 2.1.260 (Claude Code); run-reported model: claude-fable-5-1,claude-haiku-4-5-20251001; requested effort: high (the CLI does not report the effective setting); fresh session 8faf0f5c-b33b-45d3-a29c-6d6f305c89ed; sandbox: bubblewrap, working directory = detached read-only checkout of commit bbe7ee8aaa05c107cab46db4798c7bda874fe4ec (the live working tree is not read), filesystem read-only except this run's own output directory, scratch HOME (no access to the executing model's settings, instructions or memory), private PID namespace; network open for the model API, web tools disallowed by policy (fallback reviewer per owner ruling A-001)
**Codex unavailable because:** ERROR: You hit your spend cap set by the owner of your workspace. Ask an owner to increase your spend cap to continue.
**Wrapper:** dv/auto_dv/tools/gen_cross_review.sh blob 713e8c09 (the copy executed; equals the wrapper committed at the reviewed commit); reviewed commit bbe7ee8aaa05c107cab46db4798c7bda874fe4ec
**Date:** 2026-09-04
**Target:** committed diff 678b27b6..bbe7ee8a (echo at raw line 1)

---

TARGET: 678b27b69268d4f30b9ec09e2ff7870875012509..bbe7ee8aaa05c107cab46db4798c7bda874fe4ec

Reviewer: Claude Fable 5.1 (claude-fable-5-1), fresh detached session at bbe7ee8, read-only. Scope: the single commit bbe7ee8 on base 678b27b, 14 files, all Markdown/CSV under dv/auto_dv/docs and dv/auto_dv/evidence.

**Rubric sweep.** None of the 14 changed files match any rubric filter (no rtl/, no .sv/.svh/.py, no ci/, no top-level docs/). ai-slop-comments PASS, rtl-purity PASS, magic-numbers PASS, forces-and-hier-access PASS, assertion-integrity PASS. No fcov_expectations manifest, coverpoint, cross or sample line is in the diff (confirmed from the stat).

**Verified against the repository.**
- The three promoted notes are ASCII, gen_-prefixed, and each carries exactly one work path, in the provenance paragraph. All 153 rtl/ file:line citations (15 + 32 + 106) resolve to existing files with in-range lines. Bare basenames cited inside them (gen_param_resolution.md, gen_cheriot_carveout.md, gen_hierarchy_map.md, gen_probe_register.md, gen_unreachability_evidence.md) resolve to committed copies.
- Flattened-text counts of "unproven", "owed and parked", "recorded re-review", "widening is owed", "owed from Runtime" and the retired log name are 0 across the five plan documents. No gen_tp_parts_rtl_factcheck / gen_arch_v2_rtl_factcheck / gen_behaviour_summaries path remains in the eleven files.
- gen_run.py:204 reads `if measured and debug_only:` with no coverage term; gen_flow_const.py:461 defines MEASURED_KNOB_CONDITIONS with two rows (tag and data-RAM rate); gen_run.py names knob_icache_ecc_bits nowhere. Plan and flow agree (item 2).
- gen_fu_l16_trace17_tagwrite_history.log: I re-derived the episodes from its ICTRACE tagwrite lines independently and get 16 episodes, 13 at index 26, 3 at index 27, all added into way 0, with cycles matching the log's rows. Its header directs the narrow reading the feature list adopts. The feature list claims only what the artifact evidences (item 3). gen_fu_l16_trace17_duplicate_copies.log has 20 lines, 17 at index 26, 3 at index 27.
- gen_critic_tb_l16.md (committed at fc81da5) states "The REQUEST-CHANGES of tb_l15 is lifted by this verdict" and names RETSEQ and RETIDX as form (b) mutations of its retirement rule caught with ablations; the WP-12 description and status columns now agree on this (item 1, with the exception below).
- The CM180 rows match the six findings of dv/auto_dv/reviews/2026-09-04-claude-diff-5eb7ddbb-435f8d40.md (M-1, L-1, L-2, I-1, I-2, I-3). dv/auto_dv/docs/gen_critic_feature_list_v1.md is committed.
- sha256 of gen_testlist.yaml = 4d3eb6250733..., 101 tests; sha256 of gen_test_plan.md = 56c1f236f966..., matching the promotion table header. The covergroup set .md/.csv changes are the label, the inputs digest and fcov-plan line numbers shifted by one; no content row changed.
- In this checkout gen_trace_check.py PASS, gen_fcov_codegen.py --check "up to date", gen_round_credit.py --self-test ok.

**Findings.**

[Medium][dv/auto_dv/docs/gen_test_plan.md:19384] TP-SEC-001's notes still contradict themselves inside one sentence: "it was proven at landing 15: every landing-14 mutation ran with the probe on, so no named mutation has been caught by this form yet". The "yet" clause is the pre-landing-15 state and is false now (probe-off DATAMISS/DATAWAY and RETSEQ/RETIDX are caught). RE-KEY-4 says every occurrence was checked; this one was missed. - Rewrite the clause in the past tense ("so this form had no named mutation of its own until landing 15") so the sentence reads as one current statement.

[Medium][dv/auto_dv/docs/gen_tb_architecture.md:269] Section 6 is headed "included verbatim", says the text below is the note "in full" at the de5bc9573c84255b revision, that "a diff with headings flattened shows no other difference", and now adds that quoting the hash FREEZES the source and "the note is not edited while this quotation stands". In this same diff the DV Lead edits four passages inside that embedded block (the version-3 fact-check sentence at :294, the Sources paragraph at :299-307, the link-test paths at :787 and :1137). The embedded copy therefore no longer matches the hashed source, and the "no other difference" and "verbatim" claims are false as written. The FREEZES statement is also the wrong direction: a hash pins what was quoted, it cannot stop the work file changing, and the sentence itself concedes that an edit makes the claim false. Item 4: not accepted as stated. - Either keep the embedded block byte-identical to the hashed note and put the re-pointings in a DV Lead editorial note outside the quotation, or drop "verbatim / in full / no other difference", mark each DV Lead substitution inline, and re-word the sentence to "the hash identifies the revision quoted; the embedded copy, not the work file, is the text this document verifies".

[Low][dv/auto_dv/docs/gen_test_plan.md:438] The WP-12 description still says "the tag-write trace that counted the duplicates retired with landing 15, so the mechanism rests on those RTL terms and the retained gen_fu_l16_trace17_duplicate_copies.log shows only that 20 injections met the two-way-valid equal-tag condition", while the feature list (:11360-11366) now cites gen_fu_l16_trace17_tagwrite_history.log for 16 episodes. Not false, but the two records describe different retained-evidence sets for the same claim, which is the cross-record rule the response file says it applies. - Add the tagwrite-history citation with the same narrow reading to the WP-12 row.

[Low][dv/auto_dv/docs/gen_test_plan.md:22421] The knob:icache_ecc_bits row has a garbled, duplicated clause: "...while every injecting run is already covered by a rate row, and The flow needs no row of its own for it, since every injecting run is covered by a rate row, and Runtime still owes...". - Keep one of the two clauses.

[Low][dv/auto_dv/evidence/gen_critic_response_plan_set_v1.md:747] The CONVENTION row says a superseded row carries a SUPERSEDED clause naming its successor and "governs every row above", but rows superseded by RE-KEY-2, RE-KEY-5 and L15-EVIDENCE-2 carry none: CM177-M-2 (:714, flow row owed), CM178-I-1 (:725, widening pending), L15-RETIRE-1 (:728, direction rests on RTL alone, no count), L15-RETIRE-2 (:729, no retained direction evidence), L15-EVIDENCE-1 (:730, remaining gate is the re-review). Only F1, Form (b) and CM177-L-1 got the clause. - Add the SUPERSEDED clause to those five rows.

[Low][dv/auto_dv/docs/gen_test_plan.md:22299] "Feature references are to dv/auto_dv/work/dv-lead/gen_feature_list_draft.md" is a path-form citation of a gitignored draft that the part-file provenance patterns in the header do not cover; the committed successor is dv/auto_dv/docs/gen_feature_list.md. It is a pointer, not sole evidence for a claim. - Re-point to the committed feature list.

No citation in the eleven DV Lead files was found to function as the sole evidence for a claim while pointing at a gitignored file; the remaining work paths are the plan set's own part files, the architecture document's Inputs row and Section 6 provenance, and Runtime out-tree paths that name their committed byte copies.

Final verdict: APPROVE-WITH-CHANGES
