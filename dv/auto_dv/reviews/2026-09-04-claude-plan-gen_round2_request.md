# Cross-model review - plan/spec file(s): dv/auto_dv/evidence/gen_round2_request.md at commit 6407118b

**Reviewer:** claude CLI 2.1.261 (Claude Code); run-reported model: claude-fable-5-1,claude-haiku-4-5-20251001; requested effort: high (the CLI does not report the effective setting); fresh session c154bce2-170a-49a8-b53c-ef2fac364382; sandbox: bubblewrap, working directory = detached read-only checkout of commit 6407118b3e156f6ac6982e777fd14154a8ee1657 (the live working tree is not read), filesystem read-only except this run's own output directory, scratch HOME (no access to the executing model's settings, instructions or memory), private PID namespace; network open for the model API, web tools disallowed by policy (fallback reviewer per owner ruling A-001)
**Codex unavailable because:** ERROR: You hit your spend cap set by the owner of your workspace. Ask an owner to increase your spend cap to continue.
**Wrapper:** dv/auto_dv/tools/gen_cross_review.sh blob 713e8c09 (the copy executed; equals the wrapper committed at the reviewed commit); reviewed commit 6407118b3e156f6ac6982e777fd14154a8ee1657
**Date:** 2026-09-04
**Target:** plan/spec file(s): dv/auto_dv/evidence/gen_round2_request.md at commit 6407118b (echo at raw line 1)

---

TARGET: dv/auto_dv/evidence/gen_round2_request.md@8c6cede1

Reviewer identity: Claude Fable 5.1 (claude-fable-5-1), fresh session, detached read-only checkout of 6407118. Scope: dv/auto_dv/evidence/gen_round2_request.md and dv/auto_dv/tools/gen_round_form_check.py as added in 6407118 (577 lines, two files).

**What I recomputed independently (all reproduce)**

- Margin table (focus 1): from dv/auto_dv/evidence/gen_round_0/gen_regress_manifest.yaml, my own script (not the checker) gives 12 measured entries, 36 measured runs, 2895 declared bins, 963 with smallest-over-three-runs count of 1 (33.3 percent), 1327 at three or fewer (45.8 percent), 8685 bin checks all state HIT. Every per-entry row (bins, hit-once, share) matches the form. Four entries have median 1 or 2 (cmp_zcmp_basic, rst_boot, mul_mul at 1; bit_ratified at 2).
- Costs (focus 5): wall 362.9 s (21:54:27Z to 22:00:28Z), 53 runs, sum 940.7 s (689.3 measured, 251.4 unmeasured), mean 17.7, min 6.6, max 69.5, one seed over the twelve 229.8 s, over the three PMP entries 49.2 s, nine seeds on PMP 442.8 s, 9 x 229.8 = 2068 s, 12 x 102.9 = 1234 s, 12 x 126.9 = 1523 s, 2757 s and 9191 s pre-flights, speedup 2.59.
- Rule-of-three table (focus 3): 1 - 0.05^(1/n) and 0.75^n for n in {3, 8, 12, 20, 40} and 0.05^(1/3) = 0.368 all correct to the printed digits.
- Pre-flight table (focus 4): rows byte-equal to gen_r1_preflight_classification.md:22-31; 123 stable and 123 seed-dependent both sum correctly; the four entries with seed-dependent bins are cmp_zcb 8, cmp_zcmp_basic 73, isa_alu 33, mul_div 9; the class-B manifest reason reads "seed-dependent: hit at some seeds and not others ... credited from the merged report" as the form says; the mie_msb 180 writes / 10 of 40 figures are in gen_critic_response_batch3.md:176 and the round-1 diff review.
- Selector (focus 7): applying the tier-rank selection to the testlist at 0203c6e gives 19 entries / 53 runs / 36 measured (smoke 16/44/36, targeted 3/9/0), matching the table. 3b18a50 (the IRQ entry) is not an ancestor of 0203c6e. Cited lines gen_flow_util.py:1618-1631 and :1634-1638, gen_regress.py:613-614 are exact.
- LOG-097 (focus 8): the intervention log's applied list says the DV Lead decides the seed count per entry with the derivation and run budget; the form does exactly that and names the blanket rise as wrong.
- Checker (focus 6): against the retained manifest it exits 0 with 123 claims; the self-test's six cases all discriminate as labelled; the retained manifest is byte-identical to the /proj_soc path the checker defaults to.
- Rubrics (focus 9): both files pure ASCII; no LOG/CR ids in code comments; comments are intent-only; no RTL, force, hierarchical poke, or assertion change in the diff; magic-numbers PASS.

**Findings**

[Medium][dv/auto_dv/evidence/gen_round2_request.md:52-61] The rule "may not exceed the number of seeds its fcov manifest has been measured over" is called checkable, but nothing records that number: the 24 manifests carry only test, owner, bins and anti_vacuity keys (no seed count), and the form names no loader or gen_regress check that would compare the testlist seeds field against it. As written the flow cannot check the rule; it is a convention. - Add the manifest field the rule reads (a measured-seed count with the base and commit it was measured at) and name the check site (the testlist loader or fcov_policy_failures) so the flow refuses a testlist seeds value above it; or reword 3.1 to say the rule is a convention until that lands.

[Medium][dv/auto_dv/evidence/gen_round2_request.md:109-110] "it is the cheapest entry in the set at 10.0 s per run" is false. Per-run means from the manifest: cmp_zcb 8.2, mul_mul 9.2, csr_access 9.7, csr_trap_setup 10.0. It is not the cheapest of the twelve nor of the four with margin. The checker does not parse this sentence, so the form's own guard did not catch it. - Change to "one of the cheaper entries" or "the second cheapest of the four with margin" and add the per-entry mean to the checker.

[Medium][dv/auto_dv/evidence/gen_round2_request.md:37-38] Section 1 says "this form states an expected outcome for every selected run" and section 11 accepts the round when each entry "meets the expectation stated for it in section 7", but section 7 (lines 249-255) states no outcome for any entry; it is a deferred shape. The acceptance criterion therefore points at content that does not yet exist, and the form does not say how the restated sections 1 and 7 get their own review before dispatch (the executing model never self-approves). - Either fill section 7 now for the twelve existing measured entries (whose declared sets and build state are known at HEAD) and leave only the PMP/IRQ rows deferred, or reword line 37 to "will state" and add to section 7 that the restated sections are re-reviewed by the other model before dispatch, with the review artifact named.

[Low][dv/auto_dv/evidence/gen_round2_request.md:20-26] The selector table is derived at 0203c6e, four landings behind the form's own commit. At 6407118 the same call gives 20 entries / 56 runs / 36 measured because gen_test_irq_basic (smoke, 3 seeds, unmeasured) already sits in the testlist. The label is honest but the form's own commit is the natural anchor and the tool exists. - Restate the table at the form's commit and note that the IRQ owning entry has landed unmeasured; section 3.5 row "the new IRQ owning entry" can then name it.

[Low][dv/auto_dv/evidence/gen_round2_request.md:73-78] "median smallest count" uses the upper median (element at index n/2 of the sorted list). For gen_test_csr_access (4 bins) the conventional median is 47.5, not 80; for csr_trap_setup 13.5, not 14. The convention is not stated in the form or the checker docstring. - Say "upper median" in the column header (or in 3.2), or switch to statistics.median in gen_round_form_check.py:92 and update the two rows.

[Low][dv/auto_dv/tools/gen_round_form_check.py:34-35] The comment says "the split itself is checked against the measured shares", but MARGIN_FOUR is used only to sum costs (line 117); nothing verifies that these four are the entries the form names in 3.3 or that their shares are the four lowest. A wrong split would pass. - Assert that MARGIN_FOUR are exactly the entries with the four smallest shares from bin_margins, or parse the four names from section 3.3 and drop the constant.

[Low][dv/auto_dv/tools/gen_round_form_check.py:32] The default manifest is the out-of-tree /proj_soc path, and the form (line 194) cites the same path, although dv/auto_dv/evidence/gen_round_0/gen_regress_manifest.yaml is byte-identical and committed. A reader without the share cannot run the checker from the commit. - Default to the retained copy and cite it in section 4; keep the /proj_soc path as the origin.

[Low][dv/auto_dv/tools/gen_round_form_check.py:215-256] The self-test drives a private subset of checks on a synthetic form instead of run_checks, so the pre-flight table parsing, the rule-of-three parsing, the states check and most regexes have no self-test; a regex that stops matching after a wording edit would surface only on the real form. The commit message's "parses every numeric claim" is also overstated: unchecked claims include 53 of 53, 36 of 36, 10.0 s per run, the 1234 s in 3.3, "three extra minutes", "13 minutes", "between 27 and 72 percent", 0 of 36 shared seeds, 10 of 40 and 180. - Route the self-test through run_checks with a synthetic pre-flight text, and either add the missing claims or state in the docstring which prose figures are outside the checker.

[Low][dv/auto_dv/evidence/gen_round2_request.md:138-139] "two boundary values needing an owner ruling on drivability (rst_boot, 2)" restates the pre-flight's first classification; that document's own correction (gen_r1_preflight_classification.md:126-131) says the bit-8 half needs no ruling because the TB drives the key valid out of reset by default. - Say one boundary value awaits a ruling and the other is a TB-default fact.

[Info][dv/auto_dv/evidence/gen_round2_request.md:133] "The bins the merge is MISSING are the 123 stable ones" is true of the eight entries' pre-flight unmet set only. The round-1 merge also lacks the class A bins (758 unbuilt-covergroup bins plus 127 with ready reasons per LOG-092 in the intervention log), which seeds cannot close either, so the conclusion stands; the sentence should scope itself. - Add "of the pre-flight's unmet set".

[Info][dv/auto_dv/evidence/gen_round2_request.md:255] gen_fcov.py:328-331 is the cause-text mapping ("manifest declares no bins"); the unverifiable reason is assembled at :361. The behavioural claim is right. - Cite :328-331 and :361 together.

[Info][dv/auto_dv/tools/gen_round_form_check.py:179] The value 4.0 is hard-coded rather than parsed from "sit on four entries" (line 130-131 of the form), which is a restatement in a checker whose docstring says nothing is restated. - Parse the word or note the exception in the docstring.

[Info][review scope] I could not locate "P-07" as a standing rule anywhere in the tree (the only P-07 is a closed low item in gen_critic_t005_dv_principles_v1.md); I evaluated the rule against the per-run guarantee in gen_fcov.py and fcov_policy_failures in gen_regress.py:237-260, with which section 3.1 is consistent.

Final verdict: APPROVE-WITH-CHANGES
