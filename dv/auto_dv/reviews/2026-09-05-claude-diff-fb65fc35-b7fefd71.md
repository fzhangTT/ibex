# Cross-model review - committed diff fb65fc35..b7fefd71

**Reviewer:** claude CLI 2.1.261 (Claude Code); run-reported model: claude-fable-5-1,claude-haiku-4-5-20251001; requested effort: high (the CLI does not report the effective setting); fresh session 81daefe0-6efa-4422-b450-faf9b8861e84; sandbox: bubblewrap, working directory = detached read-only checkout of commit b7fefd71c9c2c2d5bb1cea591a54bb87e8d59bd6 (the live working tree is not read), filesystem read-only except this run's own output directory, scratch HOME (no access to the executing model's settings, instructions or memory), private PID namespace; network open for the model API, web tools disallowed by policy (fallback reviewer per owner ruling A-001)
**Codex unavailable because:** ERROR: You hit your spend cap set by the owner of your workspace. Ask an owner to increase your spend cap to continue.
**Wrapper:** dv/auto_dv/tools/gen_cross_review.sh blob 713e8c09 (the copy executed; equals the wrapper committed at the reviewed commit); reviewed commit b7fefd71c9c2c2d5bb1cea591a54bb87e8d59bd6
**Date:** 2026-09-05
**Target:** committed diff fb65fc35..b7fefd71 (echo at raw line 1)

---

TARGET: fb65fc35df8cf8518b9dd3976b915609e31f6146..b7fefd71c9c2c2d5bb1cea591a54bb87e8d59bd6

Range: twelve commits. The review target is the DV Lead's two commits, b7fefd7 (form v3.3 and its checker) and 66a4f48 (rule (b) clarification, three digest headers). The other ten (Critic verdicts 55d784a, ad3abe3, 9c2c550; reviews f62c599, 4b8d667; rtl-arch records 94fcd49, 0a0fa8d, 7ab91ab; runtime-2's flow landing 1fa0bc7 and reds2 block 67c6ac1) were read for the five rubrics and as the records the form's statuses must match at this commit. No `rtl/` or SV line changes anywhere in the range. Reviewer: claude-fable-5-1, fresh session, detached read-only checkout of b7fefd7.

**Verified by running the tool at b7fefd7**
- Checker from the repo root and from `/tmp`: both `PASS, 204 claims compared and all reproduce`, exit 0.
- `--self-test`: ten form cases plus the working-directory control, all ok, PASS. The new case prints `SELF-TEST ok   an extra Section 7 row fails: fail, want fail` (`gen_round_form_check.py:360-362 @b7fefd7`).
- Control: in a copy with the row-count check at `gen_round_form_check.py:180` replaced by `pass`, the self-test reports `SELF-TEST BAD  an extra Section 7 row fails: pass, want fail` and overall FAIL, while `a dropped Section 7 row fails` still reads ok. So the committed case depends on exactly the check it controls, and rev70's Medium 1 is closed as claimed: the dropped-row case could not stand in for it.
- The ghost row `| gen_test_ghost | 3 | 9 | 1 of 1 | PASS |` matches the count regex at `:179` and no per-entry regex, which is the right shape for the control.

**Verified against the committed records**
- Heading and paragraph agree: `gen_round2_request.md:329` reads ONE OF THE NINE, and the paragraph establishes bit_ratified alone as narrower (617 of 654 in the wave, 37 on the pair-fix block) with csr_warl "measured at every one of forty seeds". rev70 Medium 2 closed.
- Condition (f) at `:376` cites 29daef3; that commit resolves, is an ancestor of b7fefd7, and `gen_chkfix_reruns/gen_index.md:80-85` at this commit reads `THE GAP IS 6447, not "about 6443"`. rev70 Medium 3 closed.
- Section 3.5 at `:199-202` now states in its own text that the values are not applied until measured_seeds lands and that this is "not a path the Runtime Manager may take today"; read together with 3.7 and Section 7, a Runtime Manager is told the twelve-seed request waits on the field. rev70 Medium 4 closed in substance (one loose end below).
- `gen_testlist.yaml:59` is `fcov_manifest_required_tiers: [smoke, targeted]` with no cap value beside it, as `:355-356` says. rev70 Low closed in substance, but the plan citation on that line is stale (finding 3).
- `gen_flow_util.py:1634-1638` cited by 3.7 no longer shows the `seeds_for_test` override (it is the program-key validation at this commit); pre-existing citation, not in the diff, noted only.
- 66a4f48: the eight lines at `gen_fcov_plan.md:151-157` are the only text change; the three digest headers all move to 266624bb25d4 and agree with each other. The Critic's genfix follow-up (`gen_critic_genfix_followup.md:32-35, :59-63, :75`) records the byte comparison actually done (80 of 80 seeds, the TP-BIT-018 red form at seed 1) and its L-2 asked for exactly this rule text, so the clarification answers a recorded finding rather than inventing a carve-out. The "comparing the emitted bytes at those seeds" condition is a checkable procedure: regenerate at both commits, diff the bytes.

**Rubrics**
ai-slop-comments PASS (the checker's added comment at `:360` states intent, no history or review id; the flow's added comments in 1fa0bc7 explain a VCS log ordering, the why). rtl-purity PASS (no `rtl/` lines). magic-numbers PASS (`MECHANISM_LOOKAHEAD = 3` lives in the flow's constants module with its reason; the self-test fixtures are synthetic text and say so). forces-and-hier-access PASS (no drives). assertion-integrity PASS (nothing disabled or weakened; both touched self-tests gain cases).

**Findings**

[Medium][dv/auto_dv/evidence/gen_round2_request.md:372 @b7fefd7] Condition (b) reads "REOPENED: ... so it is re-run on a b9e5fad build", and `:387` says "Four of the six are open at this commit", but 67c6ac1 (09:14:57, 54 seconds before this commit and inside this range) landed `gen_reds2_b9e5fad/gen_index.md:19-26` recording all three red seeds RED-OK with zero irq_entry firings on a b9e5fad build. The table claims "status at this commit" and states a re-run as owed that is already recorded. - Restate (b) as measured 3 of 3 RED-OK at b9e5fad in the reds2 block (67c6ac1), review of that block owed, and drop the open count to three.

[Medium][dv/auto_dv/evidence/gen_round2_request.md:371 @b7fefd7] Condition (a) still ends "the Critic's confirmation pending", but the Critic's form-v3 verdict 55d784a (08:56:46, inside this range, `gen_critic_form_v3.md:54-56`) reads "it now reads delivered, M-1 and M-2 closed, the one records sentence closed by landing 56 at fab8a61 (L-2)" and its L-2 (`:79`) asks the DV Lead to restate (a) from 5af8269 and fab8a61. That is the Critic recording M-3 closed by fab8a61; the form's status predates it. - Restate (a): M-3 closed by landing 56 at fab8a61 per the Critic's form-v3 verdict, and name the record if a re-verdict on the irq-checker-fix file itself is still wanted.

[Medium][dv/auto_dv/evidence/gen_round2_request.md:356 @b7fefd7] The sentence added in this commit cites `gen_fcov_plan.md:165-167` for "a single testlist-header value beside fcov_manifest_required_tiers", and `:351` cites `:164-167` for the absence-caps rule. At b7fefd7 those lines are the opening of the measured_seeds bullet (the field's claim and bins_sha256, `gen_fcov_plan.md:164-167`); the cap sentence sits at `:170-173` because 66a4f48, by the same author six minutes earlier, inserted six lines above it. The form's own argument is that this cap "is checked by hand", so a reader following the citation lands on different text. - Re-cite both to `gen_fcov_plan.md:170-173`, and when a plan edit moves lines, sweep the form's plan citations in the same landing.

[Low][dv/auto_dv/docs/gen_fcov_plan.md:153-157 @66a4f48] The clarification makes the comparison "the evidence the carry-over rests on" but, unlike rule (c) which demands "the block's committed path", says nothing about where the comparison is recorded, and "red forms" is used nowhere else in the plan. As written, a carry-over asserted in a commit message with the diff run only in a shell satisfies the letter. - Add: the comparison (seeds, red forms, per-seed result, the script) is committed beside the block it extends, and define "red form" once (the entry's red fixtures at the seeds the block names).

[Low][dv/auto_dv/evidence/gen_round2_request.md:380-381 @b7fefd7] The form's (b) paragraph says "the same rule that governs a manifest after a generator change governs a red after a checker change", but after 66a4f48 rule (b)'s subject is the emitted stimulus, and a checker change leaves the emitted stimulus byte-identical, so the analogy read literally now carries the reds over rather than reopening them. The plan text is internally consistent (it speaks only of generator changes); the form's analogy is what no longer fits. - Say a red measures the checker against the stimulus, so a checker change alters what was measured, rather than leaning on the manifest rule by analogy.

[Low][dv/auto_dv/evidence/gen_round2_request.md:237 @b7fefd7] Section 3.7 still closes "This form requests the values; runtime-2 applies them" with no condition, while 3.5 two paragraphs earlier now says they are not applied until measured_seeds lands. The two are reconcilable but the directive sentence is the one a Runtime Manager acts on. - Append "after measured_seeds lands (3.5, Section 7)".

[Info][dv/auto_dv/evidence/gen_round2_request.md:329 @b7fefd7] "ONE OF THE NINE IS NARROWER ... WHAT NARROWS THEM" keeps the plural from the two-entry version. - "narrows it".

[Info][66a4f48 commit message] "The three inputs-digest headers move because the generator's source is now an input to them" misdescribes the cause: the digest is over the part files and moved because the fcov part file changed. The headers themselves are correct and agree.

Final verdict: APPROVE-WITH-CHANGES
