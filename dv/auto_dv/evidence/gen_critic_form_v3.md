# Critic verdict: the round-2 request form v3 and v3.1, e95a4c9..64a4ac9 (DV Lead)

Artifacts (the two commits of the range; sha256 first 16 hex of each blob at 64a4ac9, with the v3 blob at 242a64b in brackets):
- dv/auto_dv/evidence/gen_round2_request.md 224dda7458cbd818 (v3: 37f1f13ae89d67d7)
- dv/auto_dv/tools/gen_round_form_check.py ac8594d7b60583d8 (v3: 42a19dfa29ea0380)

Date: 2026-09-05 (UTC). Role: Critic. Method: the checker run by me on a detached archive of 64a4ac9 from the archive root and
from a foreign working directory, its self-test run, and the v3 checker (the unfixed path) run from a foreign directory
against the same form to reproduce the red; the form's derivations checked against the records they rest on (the wave census
and index at 1fb417f, the PMP step-1b block at 2956a8a, the checker-fix re-run block at 69eb33f, my own re-verdicts) and the
promotion-condition statuses against the commit order. Exposure: the Orchestrator's range message named rev65's outcome
(three Mediums, seven Lows) and the v3.1 commit message describes the rows it answers; rev65's content (edbe821) is read
only in Section 6; rev68, running on 5af8269..64a4ac9, is not read. Logs: dv/auto_dv/work/critic/form3/.

CRITIC VERDICT: APPROVE (two Lows owed as disclosed; no Medium).

## 1. What the form is and how it was checked

v3 restates Section 1 from a selector call at 9c28944 (smoke 17 entries / 47 runs / 39 measured; targeted 3 / 9 / 6; the plan
20 / 56 / 45), fills Section 7 with fifteen measured entries (three seeds each, 3171 declared bins, every covergroup built, an
expected fcov verdict per row) and five unmeasured ones, and records the irq entry's six promotion conditions with a status
each; its checker grows to 203 claims by recomputing Section 1 and Section 7 through the flow's own select_tests,
seeds_for_test and validate_manifest. v3.1 fixes the checker's manifest path (repository root rather than the process
working directory), adds a control that runs the whole check from a temporary directory, adds three controls for the
seventy selection claims, reads the restatement's commit out of the form, and corrects the form's own text under its
Section 0 rule (a block is evidence for what it measured).

## 2. The checker

On my archive of 64a4ac9: `gen_round_form_check.py` PASS, 203 claims compared and all reproduce, from the archive root and
from /tmp alike; `--self-test` passes ten cases, the seven pre-existing ones, the three new selection controls (a wrong
Section 7 declared count, a dropped Section 7 row, a wrong restated plan run count, each failing as it should) and the
working-directory control (0 failures from a temporary directory). The red is real and exact: the v3 checker (blob
42a19dfa29ea0380, the unfixed path) run from /tmp against the same form reads "FAIL, 16 claim(s) did not reproduce", the
number the commit message states, and PASS from the root, so the v3 verdict depended on where it was invoked and the v3.1
one does not. The tier labels are read from the form's own "THE ROUND'S PLAN AT <commit>" row, so a later restatement is
checked rather than skipped.

## 3. Section 7 and the narrowing under the Section 0 rule

The fifteen rows reproduce through the checker (seeds, declared, built, covergroups). "No entry expects a failure" is stated
as a claim the round tests, which is the honest form. The v3.1 narrowing of "nine measured over forty fresh seeds" is right in
both figures and half right in one reason: gen_test_bit_ratified's 654 are 617 measured in the wave plus 37 declared from the
pair-fix block on a different generator, exactly as my generator-fixes re-verdict (gen_critic_genfix.md Section 7) has it;
gen_test_pmp_csr_warl's "produced a program at all forty seeds and one run refused its coverage, so its measurement is 39 of
40" describes the wave correctly (gen_wave_4017573/gen_index.md:32: 40 runs, 39 PASS, one refused on
cr_hi_mode.bit30_napot at 39 of 40), but that bin left the declared set at 9c28944, so against the manifest Section 7 names
(178 bins) every wave run passes; and "the figure its provisional status cleared on" points at the wrong measurement: the
provisional PMP entries cleared on the step-1b block (gen_pmp_measurement/gen_index.md:34-37, 86-87), whose csr_warl
denominator is 39 because seed 230969025 produced no program at all, not because a run refused (L-1).

## 4. The six conditions against the tree

- (a) "checker half fixed at b9e5fad ... the Critic's re-verdict pending": my re-verdict was committed at 5af8269, an
  ancestor of 64a4ac9 (08:30 against 08:35 local), so the status was already stale when v3.1 was committed; it now reads
  delivered, M-1 and M-2 closed, the one records sentence closed by landing 56 at fab8a61 (L-2).
- (b) REOPENED, rightly, under the form's own rule; my irq re-verdict Section 7 measured RED-OK at seed 1038372995 on a
  b9e5fad build (the designed fire alone, zero checker fires), which supports the re-run and does not replace the record of
  all three seeds that (b) asks for.
- (c) "fixed at 6b894ab, re-review pending": correct at the commit; my APPROVE was committed at ba189fe, after v3.1.
- (d) open: correct.
- (e) open and LOAD-BEARING: correct, and now measured rather than argued: my irq re-verdict's M-3 and landing 56's companion
  (fab8a61) establish that the storm-shape vacuity survives landing 54 through the entry restart, so the end-of-test
  expectation is the only thing that closes it.
- (f) open; the form's 6447 is exact (15737500 - 9290500 = 6447000 ps at 1000 ps a cycle) and the two chkfix records that
  say "about 6443" are the ones owed the one-line corrigendum the form names.

## 5. Records, conformance, rows, verdict

Section 3.5 now says its seed table is a request and not the plan, with the consequence spelled out (twelve-seed runs
against three-seed rows would fail Section 7); Section 7 derives which eleven entries are capped at forty and which four at
three; the directory holds 27 manifests as v3.1 says; the two open items (the hart_id plusargs, the coverage criterion) are
named as not claimed. Both files are ASCII. Conformance (dv_principles.md): every figure in the form is derived by calling
the flow and re-derivable by its checker, the checker has a red that fires the defect it fixes, and the form claims no
outcome it has not measured.

- L-1 (Low, records; DV Lead). The csr_warl sentence: name the wave as the measurement it describes, say the refused bin has
  since left the declared set, and attribute the provisional clearing to the step-1b block and its no-program seed.
- L-2 (Low, records; DV Lead). Condition (a)'s status was stale at the form's own commit; restate it from 5af8269 and fab8a61.

Verdict: CRITIC VERDICT: APPROVE on e95a4c9..64a4ac9. The checker reproduces all 203 claims from any working directory and
its red is the sixteen failures claimed; Section 7 and the conditions hold against the tree with the two record corrections
above owed. The form gates round-2 dispatch on conditions it states correctly; the irq entry stays unmeasured as it says.

## 6. Reconciliation with the cross-model artifact rev65

Read after Sections 1-5 were written: dv/auto_dv/reviews/2026-09-05-claude-diff-e95a4c99-242a64b1.md at edbe821 (claude CLI
fallback under A-001; APPROVE-WITH-CHANGES on v3, 242a64b; three Mediums, seven Lows). rev65 reviewed v3 alone; the range I
judge ends at v3.1, which answers it, so the reconciliation is against v3.1's answers.

- Its Medium 1 (validate_manifest opening the testlist's repo-relative path against the process working directory) is fixed
  at 64a4ac9 (the path resolves against the repository root) and my Section 2 reproduces its red exactly: the v3 checker
  from /tmp fails sixteen claims, the v3.1 checker passes from anywhere.
- Its Medium 2 (no self-test control for the seventy selection claims) is fixed: three selection controls and the
  working-directory control are in the self-test and each fails as it should (Section 2).
- Its Medium 3 (Section 3.5 asking twelve seeds while Section 7 states three) is fixed by v3.1's request-versus-plan
  paragraphs, which say what applying the request without the testlist touch would do and that Section 7 is restated from
  a fresh selector call if it lands (Section 5).
- Its seven Lows are all answered in v3.1: "five" is "six"; the 6447 figure is kept as the re-derived one with a corrigendum
  owed on the "about 6443" records (Section 4, (f)); the "nine over forty fresh seeds" sentence is narrowed under the
  Section 0 rule, on which my L-1 adds the csr_warl attribution; the antecedent is repaired; the hart_id plusargs are named
  as an open item; the tier labels are read from the form; the manifest count reads 27. Its closing note that no flow tool
  reads the form, so Section 11's "does NOT claim the functional gate" cannot be misread by a gate, is right and matches
  gen_flow_const.py's GROUP_CELL selector note in the rt39 range.
- Nothing in rev65 bears on my two Lows, which are v3.1 text: L-1 (the csr_warl sentence's attribution) and L-2 (condition (a)
  stale at the commit). rev68, running on 5af8269..64a4ac9, will see v3.1 itself; I have not read it.
- Verdict unchanged: APPROVE on e95a4c9..64a4ac9; L-1 and L-2 owed as disclosed. rev65 and this file agree there is no Major,
  and its three Mediums are closed by v3.1.

## 7. v3.2 at fb65fc3: L-1 and L-2 closed; the range widened to e95a4c9..fb65fc3 (appended under a HOLD, 2026-09-05T13:24:05Z)

Artifacts: gen_round_form_check.py d4c3f6e9166e1f93 and gen_round2_request.md d16a00792e1ab7da, both at fb65fc3; the v3.1
checker ac8594d7b60583d8 at 64a4ac9; rev70, dv/auto_dv/reviews/2026-09-05-claude-diff-64a4ac95-fb65fc35.md 1dcbaa19ccfb7c56.
Method: a detached archive of fb65fc3 driven by dv/auto_dv/work/critic/form3/v32_checks.sh, its log v32_checks.log and the
run outputs under form3/runs/ (the checker from the archive root and from a foreign directory, --self-test, my own
sixteen-row control against both checkers, the csr_warl manifest at three commits through the flow's validate_manifest, the
wave block's census and index, commit times, then rev70's rows against the tree). Exposure: the Orchestrator's message named
rev70's first Medium (the row-count control absent from the committed self-test) before these checks; rev70 itself was read
only after the confirmation paragraph was fixed (form3/draft_s7_prerev70.txt, 13:19Z); the reconciliation list follows it.

L-1 is CLOSED: the sentence now names the wave's census (40 runs, 40 coverage reports, 178 of 179 bins at every seed, the
exception one cross leg at 39 of 40; gen_wave_census.txt:66-69 at fb65fc3), says the manifest was re-rendered at 9c28944 to
those 178, which validate_manifest confirms (179 bins with gen_pmp_addr_write_cg.cr_hi_mode.bit30_napot at 4017573; 178
without it at 9c28944 and at fb65fc3), and attributes the 39-seed figure to the PMP blocks at 218e9f3 and 4cd3ff6 and their
no-program seed. One residual sentence, L-4 (Low, records; DV Lead): "rather than any coverage refusal"
(gen_round2_request.md:335-336 at fb65fc3) is true of the PMP blocks only; the wave index's PASS column reads 39 of 40 for
this entry (gen_index.md:32 at fb65fc3, the yaml's pass: 39) and :18 says those figures are each run's own checker verdict,
so one wave run's verdict did refuse on that cross leg under the 179-bin set before the leg left the set, and the commit
message's "there was no coverage refusal" overstates the same way. L-2 is CLOSED: condition (a) (:365) is restated from
5af8269 and fab8a61 as asked. I-1 (Info): its trailing clause "the Critic's confirmation pending" was accurate against the
tree, since no record of mine named fab8a61 at fb65fc3 (git grep); my confirmation that fab8a61 closes M-3 of the irq
re-verdict went to the Orchestrator by message after fab8a61 (12:43:36Z) and the Orchestrator's message announcing fb7226c
(committed 12:50:19Z) records it as received; the first record of it in the tree is this file's own Section 4 (:54-56 at
55d784a, committed 12:56:46Z, 81 seconds after fb65fc3), so the form's next touch reads (a) CLOSED from there. (Sentence
corrected at 13:30:02Z after reading rev72 and before the hand; the earlier text called this section the first record.)
The checker at fb65fc3 passes 204 claims from the archive root and from a foreign directory and --self-test passes its ten
cases. M-1 (Medium, checker record; DV Lead): fb65fc3's commit message says the row-count check comes "with its control"
that "adds a sixteenth row and fails with 'form 16 vs source 15' where the previous checker passed", and no such case is in
the committed self-test: eight perturbation tuples (gen_round_form_check.py:349-361 at fb65fc3), none adds a row, and the
diff to self_test() changes comments only. The check itself is sound and the claim is true of a run nobody retained: my
sixteen-row form (gen_test_rst_boot's row copied under a new name, form3/runs/form_16rows.md) fails the v3.2 checker with
exactly "Section 7 row count: form 16 vs source 15" and passes the v3.1 checker at 203 claims. Closes when v3.3 puts the
sixteen-row case in self_test() and it fails as claimed.

Reconciliation with rev70, read after the paragraph above was fixed:
- Its Medium 1 is my M-1: the same absence and the same measurement (its sixteenth row is an irq_basic row, mine a copied
  rst_boot row; both fail with the exact message).
- Its Medium 2, VERIFIED and adopted as M-2, my miss: "TWO OF THE NINE ARE NARROWER" (:326-327) survives in the paragraph
  whose new sentence makes csr_warl measured at forty, so the paragraph establishes one narrower entry (bit_ratified) and
  says two. I judged the L-1 sentence inside that paragraph and did not re-read its opening.
- Its Medium 4, VERIFIED and adopted as M-3: Section 3.5 (:181-182) still asks twelve under "the rule in 3.1 permits up to
  40", :198-199 still describes landing the rise as a permitted path and Section 3.7 (:234) closes "runtime-2 applies them",
  while Section 7 (:346-351) says no entry is licensed above its calibrated count until measured_seeds lands. One form both
  directs the touch and says it is unlicensed; a reader of 3.5 or 3.7 alone is directed to apply it.
- Its Medium 3, VERIFIED and adopted as L-3 (Low, records; DV Lead), my miss: condition (f) (:370) says a one-line
  corrigendum on the cited record "is owed", and 29daef3 (12:51:56Z, an ancestor of fb65fc3) landed it at
  gen_chkfix_reruns/gen_index.md:80-85 reading 6447. Stale at the form's own commit, the class of my L-2, which I rated Low;
  I keep that class where rev70 says Medium. My check of the conditions this time was confined to (a), which is how it was
  missed.
- Its Low, VERIFIED and adopted as L-5: dv/auto_dv/docs/gen_fcov_plan.md:164-167 makes the cap one header value "beside
  fcov_manifest_required_tiers", and gen_testlist.yaml at fb65fc3 carries no such value (zero measured_seeds occurrences;
  that key's neighbour is debug_only_plusargs); no manifest carries the field either, so the plan's rule is applied by hand
  until the value lands.
- Its reading of condition (a) ("no Critic record mentions fab8a61, so 'confirmation pending' is accurate") is right
  against the tree and is what I-1 says. Its Info (eleven commits in the range, the other ten other roles' records and my
  verdicts) matches the log.

Verdict. The pre-rev70 draft read APPROVE with M-1 owed; that was lenient against my own precedent, where a claim the tree
does not hold is a REQUEST-CHANGES row (gen_critic_flow_followups.md M-3), and with M-2 and M-3 verified there are three
Mediums in fb65fc3's own text or commit message. CRITIC VERDICT: REQUEST-CHANGES on e95a4c9..fb65fc3, confined to M-1, M-2
and M-3 of this section. The APPROVE on e95a4c9..64a4ac9 stands and its L-1 and L-2 are CLOSED by v3.2. Lifted when v3.3
lands with the sixteen-row case in self_test() failing as claimed, the narrowing sentence counting one, and Sections 3.5
and 3.7 pointing at Section 7's licence paragraph; L-3, L-4 and L-5 ride the same touch. rev70 and this section agree there
is no Major and that no row here needs a re-measurement.

## 8. v3.3 at b7fefd7: the Section 7 REQUEST-CHANGES is lifted; APPROVE on e95a4c9..b7fefd7 (2026-09-05T13:27:23Z)

v3.3 (b7fefd7, 13:15:51Z, one commit on 67c6ac1 touching the form and the checker) landed before Section 7 was fixed and
after its checks began, so it is judged here rather than left for a second hand. Artifacts at b7fefd7:
gen_round_form_check.py 07c32212798e985f, gen_round2_request.md 18338b852d66afe3. Method: a detached archive of b7fefd7
driven by dv/auto_dv/work/critic/form3/v33_checks.sh, log v33_checks.log, outputs under form3/runs33/. rev72 (2e70c5d,
84bb6d5e1ce858b8) on fb65fc3..b7fefd7 was committed at 13:25:32Z, before this section was written and unseen by me until
the hand's HEAD check; I read it after the rows below were fixed, and it is reconciled at the end of this section.

- M-1 CLOSED: self_test() gains "an extra Section 7 row fails" (a ghost row appended after gen_test_rst_boot's row;
  gen_round_form_check.py:361-363 at b7fefd7), and --self-test passes its eleven cases including it. The checker passes 204
  claims from the archive root and from a foreign directory, and my own sixteen-row control still fails it with exactly
  "Section 7 row count: form 16 vs source 15". The claim of Section 7's M-1 is now true of the tree.
- M-2 CLOSED: "ONE OF THE NINE IS NARROWER" (gen_round2_request.md:329 at b7fefd7).
- M-3 CLOSED with a residual: Section 3.5's table now carries the stop where the request is made, "THE VALUES HERE ARE NOT
  APPLIED UNTIL THE PROVENANCE FIELD LANDS ... not a path the Runtime Manager may take today" (:199-202). Section 3.7 still
  closes "This form requests the values; runtime-2 applies them." (:237) with no qualifier, L-6 (Low, records; DV Lead), not
  blocking because the table a reader would apply now carries the stop itself.
- L-3 CLOSED: condition (f) (:376) reads "the corrigendum landed at 29daef3 where gen_chkfix_reruns/gen_index.md:80-85 now
  reads 6447".
- L-5 CLOSED: "THE CAP IS APPLIED BY HAND TODAY" names the single testlist-header value beside fcov_manifest_required_tiers
  and its absence from gen_testlist.yaml:59 (:354-357), matching what I measured at fb65fc3; the plan cite on that line is
  stale at b7fefd7 (L-9 below).
- L-4 OPEN, as expected: the refusal sentence is unchanged (:338-339); v3.3 predates Section 7. I-1 OPEN: condition (a)
  (:371) still reads "the Critic's confirmation pending"; this file's Section 4 at 55d784a is the record that closes it, and
  at b7fefd7 that record is in the tree (L-8 below). Both ride the next touch.

CRITIC VERDICT: APPROVE on e95a4c9..b7fefd7. The REQUEST-CHANGES of Section 7 on e95a4c9..fb65fc3 is LIFTED: M-1, M-2 and
M-3 are closed at b7fefd7, L-3 and L-5 with them; L-4, L-6 and I-1 are owed to the form's next touch as disclosed. The
checker reproduces all 204 claims from any working directory, its self-test now controls the row-count check, and the form's
Section 7 and conditions hold against the tree with the three text items named.

Reconciliation with rev72 (read after the rows above were fixed; every row verified at b7fefd7 by git show, log v33_checks.log):
- Its verification of the row-count control is stronger than mine and agrees: with the check replaced by pass, the new
  self-test case goes BAD while the dropped-row case stays ok, so the case depends on exactly the check it controls.
- Its Medium 1, VERIFIED and adopted as L-7 (Low, records; DV Lead), my miss: condition (b) (:372) says the reds are
  "re-run on a b9e5fad build" as owed and :387 counts "Four of the six" open, while 67c6ac1 (13:14:57Z, an ancestor, 54
  seconds before b7fefd7) records the three red seeds RED-OK with zero irq_entry firings on a b9e5fad build
  (gen_reds2_b9e5fad/gen_index.md:19-26). Stale at the form's own commit, the class of L-2 and L-3, so Low here where rev72
  says Medium; my check of the conditions in this section was confined to (a) and (f), which is how it was missed.
- Its Medium 2, VERIFIED and adopted as L-8 (Low, records; DV Lead): condition (a) (:371) is stale at b7fefd7's own commit,
  since this file's Section 4 at 55d784a (:54-56, committed 12:56:46Z) records the records sentence closed by landing 56 at
  fab8a61 and 55d784a is an ancestor of b7fefd7 and not of fb65fc3. rev70 was right at fb65fc3 and rev72 is right at
  b7fefd7; Section 7's I-1 sentence naming that section the first record was wrong and is corrected above.
- Its Medium 3, VERIFIED and adopted as L-9 (Low, records; DV Lead): the form's plan cites :351 ("164-167") and :356
  ("165-167") point at the measured_seeds bullet's opening at b7fefd7; the cap sentence sits at gen_fcov_plan.md:170-173
  because 66a4f48 (13:09:17Z) inserted the rule (b) lines above it. A stale line cite; Low in my scale.
- Its Low on gen_fcov_plan.md:151-157 at 66a4f48, VERIFIED: the clarification that answers my genfix follow-up L-2 makes the
  byte comparison "the evidence the carry-over rests on" and, unlike rule (c), names no committed place for it, and "red
  forms" is defined nowhere. I agree the comparison's record (seeds, red forms, per-seed result, script) belongs beside the
  block it extends; my own comparison is retained in gen_critic_genfix_followup.md, which is where rev72 found it.
- Its Low on :380-381, VERIFIED: "the same rule that governs a manifest after a generator change governs a red after a
  checker change" leans on rule (b) whose subject is now the emitted stimulus, which a checker change leaves byte-identical;
  a red measures the checker against the stimulus, so the analogy should be dropped for that statement. Agreed, Low.
- Its Low on :237 is my L-6; its Info on the plural "NARROWS THEM" (:329) I had noticed and not written, agreed. Its Info on
  66a4f48's commit message (the digest headers move 86c54a6a6319 to 266624bb25d4 in three files, which I confirmed; the
  stated cause I did not check) is noted, not verified.
- Verdict after reconciliation: unchanged, APPROVE on e95a4c9..b7fefd7, with L-4, L-6, L-7, L-8, L-9 and I-1 owed to the
  form's next touch as disclosed. rev72 rates the three status and citation rows Medium; I keep them at Low as the class of
  L-2 and L-3, a stale status or cite at the commit rather than a claim the tree contradicts. Both agree there is no Major.

## 9. v3.4 at ef2385a: the owed rows answered; APPROVE on e95a4c9..ef2385a (2026-09-05T14:16:00Z)

Artifacts at ef2385a: gen_round2_request.md 2f3e1e37bb4e6051, gen_round_form_check.py 07c32212798e985f (unchanged from b7fefd7),
gen_fcov_plan.md, gen_test_plan.md, gen_feature_list.md; rev74 (dv/auto_dv/reviews/2026-09-05-claude-diff-b7fefd71-ef2385a2.md at
4bd933f). Method: a detached archive of ef2385a (dv/auto_dv/work/critic/form3/v33_checks.sh ef2385a, log v34_checks.log): the checker
passes 204 claims from the archive root and from a foreign directory, --self-test passes its eleven cases, my sixteen-row control
still fails on the row count; the owed rows read against the text; rev74 read after the findings were fixed (the Orchestrator's
messages had relayed its Medium, on the irq gating record, which Section 8 of gen_critic_irq_checker_fix.md answers, and four Lows).

- L-7 CLOSED: condition (b) (:376) reads CLOSED at 67c6ac1, three of six open, the block I verified in gen_critic_flow_followups.md
  Section 7. L-8 CLOSED: condition (a) (:375) is restated from this file's Section 4 at 55d784a and fab8a61 and says no Critic
  confirmation is outstanding, which is what Section 8 of the gating record now states in that record's own words; the row can
  cite it. L-9 CLOSED: both plan citations name the rule ("Section 0, the Seeds against the guarantee rule"), a phrase that occurs
  once in gen_fcov_plan.md and once in the form, so a later plan edit cannot move it. L-6 CLOSED: Section 3.7 opens with the values
  not applied until measured_seeds lands (:233-235). I-1 CLOSED by the (a) restatement. rev72's plural is fixed ("NARROWS IT",
  :334). The (b) paragraph no longer leans on the manifest rule by analogy (:383-386).
- Rule (b)'s recording sentence (gen_fcov_plan.md:156-160): a RED FORM is defined as any variant of the entry the block also
  measured, and the comparison is recorded beside the block with the seeds, the red forms, the per-seed result and the script. That
  is the home my genfix follow-up L-2 asked for and the recording rev72's Low asked for; my own comparison for the pair-fix
  carry-over is retained in gen_critic_genfix_followup.md, which is where a reader finds it until the block gains the record.
- L-4 OPEN, unchanged: :342 still reads "rather than any coverage refusal" while the wave index's PASS column for csr_warl is 39 of
  40 by each run's own verdict (Section 7); the sentence is true of the PMP blocks only. Owed to the next touch.
- The three documents' digest headers read f9a685486369 and agree with each other (b7fefd7 carried 266624bb25d4). The commit message's
  account of why they moved, and its parts-only digest 916cc594a845, I did not verify; the headers' agreement is what a reader of
  the tree can check and it holds.

CRITIC VERDICT: APPROVE on e95a4c9..ef2385a. The checker reproduces all 204 claims from any working directory with its eleven-case
self-test; L-6, L-7, L-8, L-9 and I-1 are CLOSED at ef2385a; L-4 is owed as disclosed.

Reconciliation with rev74 (read after the rows above were fixed; rows checked at ef2385a, v34_checks.log):
- Its Medium is the irq gating record still reading REQUEST-CHANGES with no lifting section; Section 8 of
  gen_critic_irq_checker_fix.md, handed under a HOLD before this section, is that lift, and the (a) row's next touch can cite it
  and say CLOSED for the Critic's part in one word, as rev74 asks.
- Its Low on the rule's motivating case, VERIFIED and agreed (DV Lead with the Test Writer): gen_bit_ratified_pairfix/gen_index.md
  mentions neither rev58 nor the emitted-bytes comparison (its one "byte-identical" at :11 says env/ equals the wave root), the
  comparison lives in
  gen_tdd_logs/test_writer/gen_fu_bit_ratified_rev58.log and its script sidecar, and the red forms compared there are the 18 items at
  seeds 1 to 3, not the block's forty seeds; only my own re-derivation in gen_critic_genfix_followup.md covered the TP-BIT-018 red at
  seed 1. The rule should say at which seeds red forms are compared, and the block's index should point at the record.
- Its Low on the rule name being unenforced, VERIFIED and agreed: gen_round_form_check.py at ef2385a reads no plan citation (0
  occurrences of gen_fcov_plan or the rule name), so "occurs once" is a grep fact; one claim in the checker with a renaming case.
- Its Low on the present tense at :382-384 ("REOPENED ITSELF ... the fix has moved, so that evidence certifies a build the round will
  not run") two lines below the CLOSED row, VERIFIED and agreed. Its Low on the commit message's parts-only digest 916cc594a845 is
  what my digest paragraph says: unverifiable from the tree; agreed. Its Info (the :238 cite gen_flow_util.py:1634-1638 where
  seeds_for_test is at :1757) VERIFIED.
- Verdict after reconciliation: unchanged, APPROVE on e95a4c9..ef2385a with L-4 owed; the rev74 rows are the DV Lead's for v3.5 or
  the round record, none of them a claim the tree contradicts. Both agree there is no Major.

## 10. v3.5 and v3.6 at 001c302..c1239af: the form's rows closed, the checker grows two controls; APPROVE (2026-09-05T14:47:28Z)

Artifacts at c1239af: gen_round2_request.md 685c2df5a6633fc4, gen_round_form_check.py fd9c38649d2264f5, gen_plan_digest_provenance.md
(3533 bytes); rev75 (dv/auto_dv/reviews/2026-09-05-claude-diff-ef2385a2-001c3021.md at ac88944, 8900724c0e9d03a7) and rev78
(dv/auto_dv/reviews/2026-09-05-claude-diff-001c3021-c1239af9.md at b59051b, 85a6551ec4372f93). Method: a detached archive of c1239af
(form3/v33_checks.sh c1239af, log v36_checks.log): the checker passes 206 claims from the archive root and from a foreign directory
(the 204 of v3.4 plus the cap-rule citation claim and the open-condition count claim); --self-test passes twelve cases, the two new
controls among them ("renaming the cap rule fails the citation claim", done on a copy of the plan, and "a wrong open-condition count
fails"); my sixteen-row control still fails the row count; the rows read against the text; rev75 and rev78 read after the findings
were fixed (form3/s10_ready.txt). Exposure: the Orchestrator's messages summarised both landings and rev75's shape before these checks.

- Condition (a) (:376) reads CLOSED at 5f9bea6 and cites this file's companion record, gen_critic_irq_checker_fix.md Section 8, for
  M-3 closed by landing 56's companion at fab8a61, the REQUEST-CHANGES lifted and the standing verdict APPROVE; that is what Section
  8 says. The (b) paragraph reads "HAD REOPENED ITSELF" (:383), past tense. The cap rule is cited by name, the checker asserts the
  name occurs exactly once in gen_fcov_plan.md (gen_round_form_check.py:186) and reads the name from the form's own citation, and
  the rename control fails as it should. gen_plan_digest_provenance.md states what the digest covers and the run that produced
  f9a685486369, which the three documents' headers carry and agree on; I did not recompute the digest, the parts and generator
  being gitignored, and the record says so of itself.
- L-4 OPEN, unchanged: :342 still reads "rather than any coverage refusal"; owed to the next touch, the one row left from me.
- The smoke, targeted and Section 7 rows are unchanged from v3.4 and still reproduce inside the 206.

Reconciliation with rev75 and rev78 (read after the rows above were fixed):
- rev75's three Mediums (the rename test writing the tracked plan in place; the open count stated in prose against a row that read
  neither open nor closed; the provenance commands not running as printed) are each answered in v3.6 by rev78's account and by what
  I ran: the rename case uses a temporary copy and the twelve cases pass from a foreign directory; the open count is a claim with a
  flip control; the provenance record's commands are single lines. rev75's Lows (the docstring's "parsed out of the form" against a
  string constant; nothing pointing at the provenance record) are answered at the form.
- rev78's Medium, VERIFIED and adopted as L-10 (Low, code; DV Lead): the open-condition count classifies a status cell as open only
  when the cell begins with "open" (gen_round_form_check.py:198-199); a cell reading "fixed at deadbee; OPEN on the sweep record" in a
  copy of the form counts as closed (the claim then fails as "form 3 vs source 2", which is the count moving, not the classifier
  reading the cell). Every v3.6 cell begins with its verdict word, so the claim holds today; the classifier should read a status token
  rather than a prefix, or the form should fix the convention it relies on. Low in my scale (a check weaker than its label, no claim
  the tree contradicts); rev78 says Medium.
- rev78's Lows (the spliced digest sentence at :359-360; the provenance commands printing the digest of an empty input on a plain
  checkout; the misplaced comment above the inserted case) and its Info (the digest order and figures unverifiable from any checkout)
  are read and agreed as the DV Lead's; none is a claim the tree contradicts.

CRITIC VERDICT: APPROVE on 001c302..c1239af. Nothing of mine is open on the form but L-4 and the L-10 note; the checker reproduces all
206 claims from any working directory with a twelve-case self-test whose two new controls fail as they should.
