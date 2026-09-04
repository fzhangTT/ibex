# Critic verdict: the range 390f40f..b105c09 (runtime-2's rt35b bea12ec, tb-infra-2's landing 34 782582f, the LOG-085 entry 71c1c70, tb-infra-2's landing 35 962d31f, the joint standing-guard landing b105c09), reviewed as tb_l33

Scope (the Orchestrator's): the range opens at 390f40f with rt35b (three files: the supplement to the retained rt35 log stating both gen_regress.py hashes
and the race first, PART D's reconstruction of the two appended cases as the whole delta, PART E's RED 1 measured both ways, the loader command, three
reds with blob-restoring greens, the response rows including CR-32-L-1 and a self-disclosed forbidden git checkout) and landing 34 (four files: the age-17
record corrected in place, the whole attempt retained as gen_fu_l33_age17_attempt.log with a manifest row, answering CR-32 L-2 by retention) and landing 35 (seven files: the cap
sized over the bound plus one, the pure-SV unit case gen_ut_drain_cap_top.sv with its filelist, the retained log with the fail-then-pass pair, the exact
diff and the verbatim command, the records at 202, closing CM209-Low-1 and CM208-Info-1); the intervention log entry LOG-085 (71c1c70, the owner's round-1 directive,
committed as written and binding on this role: the round-1 record is the Critic's next priority once it exists); and the joint standing-guard landing
(b105c09, tb-infra-2 and runtime-2: the red fixture entry gen_ut_lockstep_icache_ecc_fcov_red in the testlist, its one-bin fixture manifest, the retained
failing run gen_fu_guard_fcov_red.log with its build caveat and its as-staged limit, the flow manifest row, the WP-8 plan's Section 7 clause). The range
end is 390f40f..b105c09, named at the launch of its review (18:46Z); c8821a9, d8f5d99 and 0a510e4 in the range are review and Critic artifacts committed
as written. The DV Lead's v4t did not land in this range.

Artifacts reviewed (committed blobs at bea12ec for rt35b, at 782582f for landing 34, at 962d31f for landing 35, at b105c09 for the guard, at 71c1c70 for the log entry; sha256 first 16 hex):

- dv/auto_dv/docs/gen_wp8_part1_plan.md  8f51157e8b837d8a
- dv/auto_dv/evidence/gen_tdd_logs/flow/gen_fu_guard_fcov_red.log  f377f28440b82eeb
- dv/auto_dv/evidence/gen_tdd_logs/flow/gen_manifest.md  3ac4e6e319b96882
- dv/auto_dv/fcov_expectations/gen_ut_lockstep_icache_ecc_fcov_red.fcov.yaml  5afebcf87fa66d1e
- dv/auto_dv/flow/gen_testlist.yaml  8a9fb114dec997c7
- dv/auto_dv/docs/gen_intervention_log.md  45d36f45fc09d7ec

- dv/auto_dv/evidence/gen_critic_response_fu2a.md  be9b25bd2e9120f7
- dv/auto_dv/evidence/gen_tdd_logs/gen_manifest.md  84c7c0d918b8b596
- dv/auto_dv/evidence/gen_tdd_logs/mutations/gen_fu_l35_drain_cap_resize.log  b90062afcc363939
- dv/auto_dv/evidence/gen_tdd_step2b.md  992ed1087eb34fa2
- dv/auto_dv/tb/gen_tb_pkg.sv  5251198fb5468700
- dv/auto_dv/tb/unit/gen_ut_drain_cap.f  d348ceedba94f8bf
- dv/auto_dv/tb/unit/gen_ut_drain_cap_top.sv  5a7fd81dd71058f5
- dv/auto_dv/evidence/gen_critic_response_flow.md  07310c92382f181b
- dv/auto_dv/evidence/gen_tdd_logs/flow/gen_manifest.md  bc995d4a8a0b3309
- dv/auto_dv/evidence/gen_tdd_logs/flow/gen_rt35_red_grading_supplement.log  8b4e1c4a9cd16a3f
- dv/auto_dv/evidence/gen_critic_response_fu2a.md  520cb97f347dad39
- dv/auto_dv/evidence/gen_tdd_logs/gen_manifest.md  aba3199ec75c1848
- dv/auto_dv/evidence/gen_tdd_logs/mutations/gen_fu_l33_age17_attempt.log  34988642e0c4eb67
- dv/auto_dv/evidence/gen_tdd_step2b.md  e97020c0ceefb911

Date: 2026-09-04 (UTC). Role: Critic (reviewer other than the author). Basis: docs/dv/dv_principles.md d9c27db18f511411; gen_critic_tb_l32.md (ab442c6a33b867af, rows
CR-32) and the CM210 artifact (47ac33f727903e7d); the mutation-proof / TDD-red standard (a red's applied change is retained or exactly stated so the red
reproduces); the evidence rule.
Method: detached git worktrees of bea12ec and 782582f (the gate on each: CONST, RED-CHECK, validate 27 OK, TBMAN 3472 then 3473 rows 0 bad; the flow
manifest at 28 rows with the supplement's row 16792 / 217a2fd223682b7892b588357e9d9af5 verified against the blob; no code touched by either commit).
rt35b's supplement read whole (245 lines); PART D reproduced (the committed gen_regress.py blob minus lines 469-498 hashes 57b934c34c91 byte for byte; my
newline counts 762 / 732 against its 763 / 733); PART E reproduced (the gate reverted on the committed file, hash e660220bf7ba equal to my own reversion,
gives 3 BAD; the unchecked-fixture rule reverted, hash 2fb2ebe79cdb equal to mine, gives 1 BAD); RED 3 attempted from its description (Section 3 L-1);
PART A's loader command re-run in tb_l32 (102 / 22 / 27 / 0). Landing 34's attempt log read whole (336 lines) and every summary figure recomputed from its
own 195 rows; the eleven deleted record lines and the one deleted response line checked line by line against 9a6c975's additions. Landing 35 on a detached worktree
of 962d31f (the gate PASS, TBMAN 3474 rows 0 bad; build identity 3ecd04b3f9dc0734 over 117 sources, the package having changed); the SV unit test RUN BY
ME with the log's verbatim command from the worktree (vcs compile and simv): GEN_UT_DRAIN_CAP PASS (0 failures) with nine OK lines; then the same test
compiled in a scratch copy of the four filelist sources with gen_tb_pkg.sv replaced by the 782582f blob (3f4919ad62777bdd): GEN_UT_DRAIN_CAP FAIL (4
failures), the same four FAIL lines and the same four positive controls OK as the log's RED; the package digests 3f4919ad62777bdd and 5251198fb5468700
reproduced from the blobs; the guard landing on a detached worktree of b105c09 (the gate PASS with validate 28 OK, the new manifest bins 1 with stem and
entry matching, RED-CHECK PASS, TBMAN 3474; the loader run by me: 103 entries, 23 red fixtures, 28 manifests, exactly one deferred entry, the guard, with
expected_fail false, measured false and the tag-RAM knob alone; gen_fcov_groups.svh and gen_fcov_pkg.sv byte-identical between 813994b and b105c09 by
sha256; the manifest's md5 and sha256 as the log states; the log's own manifest row 8126 / 5c59feb272c40be64b45b271937b4472 against the blob; the data
entry's manifest declaring cp_ram.data with its corrigendum count 904; the loader's refusal of red_fixture beside expected_fail at gen_flow_util.py:1486;
the plan clause on flattened text with 962d31f as the control; the two scratch runs g1 and g2 read for their verdicts); the capfix root's local figure 9b6a43a73ca7774c reproduces as my recipe over the 782582f sources with only gen_tb_pkg.sv swapped to the landed blob (the committed 962d31f sources give f8087204d5d26cc3 because they add the two unit-test files under tb/unit, which the capfix root did not carry). EXPOSURE: the
Orchestrator's messages only; no scratch build root of the attempt was read (the log's rows are the record). No subagent used. Section 6 reconciles with
the range's cross-model review when its artifact lands (none exists yet).

CRITIC VERDICT: APPROVE on the range 390f40f..b105c09. The standing guard exists as a committed entry whose failure is the checking mechanism alone, its
first run graded RED-OK, its unhittability argued from the entry's plusargs and the covergroup's bins and surviving the build caveat by byte-identity. CR-32 L-1 is closed by rt35b (both hashes
and the race stated first, the delta proved to be the two appended cases, RED 1 measured as 3 BAD against the commit) and CR-32 L-2 by landing 34 (the
whole attempt retained, every figure of its summary recomputable from its rows, the record corrected in place and the case not claimed unreachable). Three
Lows, all record defects with the evidence itself sound: rt35b's RED 3 is not reproducible from its description and its PART B excerpt of RED 1 disagrees
with its own PART E; landing 34's "25 distinct outcomes" rests on an unstated definition.

## 1. What was verified

| commit | item | evidence (re-derived by me) |
|---|---|---|
| bea12ec (runtime-2 rt35b) | the supplement's first paragraph: the rt35 log names gen_regress.py 57b934c34c91 at :46, :114, :199, :269, :379 while the commit's blob is 5c9869bbe078; the cause a post-hand-off append that raced the committer's final hash check, called a rule breach; CR-32-L-1 answered by id | the five cites read; both hashes reproduced; the response row read |
| bea12ec | PART D: the committed blob minus the two appended case blocks (one contiguous 30-line span) is 57b934c34c91 byte for byte, holding both case labels and nothing else | reproduced: lines 469-498 removed gives 57b934c34c91; my counts 762 / 732 by newline against the supplement's 763 / 733 (a counting convention; the delta and the hash agree) |
| bea12ec | PART E: RED 1 measured both ways, 3 BAD against the committed file and 2 against the file the log ran on, each base named; PART B: RED 1 and RED 2 repeated and RED 3 new (the pre-grading restore removed, the crash case coming out NOT_RUN), every green restoring the commit's blob hashes; the NOT_RUN accounting case stated as a reliance check with no red; RED 4 not constructed and why | RED 1's variant hash e660220bf7ba equals my own reversion and gives 3 BAD; RED 2's variant 2fb2ebe79cdb equals mine and gives 1 BAD; RED 3: Section 3 L-1; the greens' hashes are the blobs |
| bea12ec | PART A: the loader command written out in full with its output 102 / 22 / 27 / 0 and its standing form (0 until the standing guard, then exactly 1) | reproduced through the loader in tb_l32 |
| bea12ec | the self-disclosed forbidden git checkout of the two record files, blast radius stated as its own two edits and the full tree status unchanged for other roles | the row read; a rule breach disclosed before further work, the Orchestrator's matter; not verifiable after the fact by me (Section 3, informational) |
| 782582f (tb-infra-2 landing 34) | the age-17 record corrected in place: the landing-33 figures (three builds, 53 runs, 111 survivor lines, ages 8 to 15) replaced by the attempt's own summariser over every run of the three roots: 195 runs over six build names and three faults (9 this instance's), 90 survivor entries in 48 runs, ages 1 to 15, none at 16 or 17, zero seeds differing in bound-failure count between the two drains, the free-phase sample 47 onsets to 25 distinct outcomes, the case not claimed unreachable; three measurements (the boot-retire plusarg not a lever, 251 of 251 creations at offset 0, the raise spacing 227 / 26 / 44 / 5 / 83 against 5.27 cycles per record); the construction named and not built | every summary figure recomputed from the log's own 195 rows: per build bnew 42 / boldi 13 / doldi 52 / doldp 1 / new 57 / old 30; 48 runs, 90 entries, min 1, max 15, none at 16 or 17, the histogram equal entry for entry; fault B 55 runs, 28 entries, max 14; fault A 55 seeds, 30 shared, bound-failure differing on none, open differing on 13, 18, 26; fault C 47 distinct onsets; the three measurements read in the log's sections 1-3; the "25": Section 3 L-3 |
| 962d31f (tb-infra-2 landing 35) | the cap sized over GEN_IRQ_ENTRY_BOUND_RECORDS plus one (193 to 202 at the defaults), the comment saying the margin is left to the finish handshake and the last write-back; the pure-SV unit case on the gen_mem_model harness compiling gen_tb_pkg.sv directly: nine checks, four failing on the committed function, none after, four positive controls green both ways, the wide-bus case (i 20/25: a record costs 47 against the 40-cycle margin, the old cap 839 where the drain needs 846) the discriminating one; the simulation pair stated as not a red; the harness run by hand, its gate wiring owed | the diff read (the return line and the comment, two lines deleted as stated); the unit test run by me: PASS 0 failures on the committed function and FAIL 4 failures against the pre-change package, line for line the log's RED and GREEN; the arithmetic 9x18+40 = 202, 47x17+40 = 839, 47x18 = 846, 47x18+40 = 886; the base figure 98629b00cb34e79e equal to my recipe over e988ee6's sources |
| 962d31f | CM209-Low-1 DONE and CM208-Info-1 CLOSED by id; CR-32-L-2 and CM210-Low-3 answered by id with the figures stated as corrected in landing 34; the records' 193 moved to 202 | the rows read; the record's landing-35 section read; TBMAN 3474 rows including the new log's row |
| b105c09 (the standing guard, tb-infra-2 and runtime-2) | the red fixture entry gen_ut_lockstep_icache_ecc_fcov_red (tier check, measured false, expected_fail false, red_expect the flow's unmet-bin reason naming cp_ram.data) with its fixture manifest declaring the one bin gen_ic_ecc_cg.cp_ram.data, unhittable by construction (the tag-RAM knob alone, no data-RAM knob; cp_ram bins tag 0 and data 1) and reachable in general (the data entry meets it at 904); the retained failing run: standalone RED-OK at exit 0 with the fcov check exiting 2 and the simulation passing; the regression shape NOT_RUN in the run log and RED-OK in result.yaml after the pre-merge pass; the retention under gen_tdd_logs/flow with the reason; the build caveat stated first (the l25 exercise build b48479a3bc6f1d9f from 813994b, its sources predating the landing, the covergroup sources byte-identical at both commits) and the limit that the run is evidence about the entry AS STAGED, the head-mode run of the committed entry to follow | the loader's 103 / 23 / 28 / 1 (rt35b's standing form: exactly one when the guard lands); every hash in the log reproduced from the blobs; the two source digests equal at 813994b and b105c09; g1 RED-OK exit 0 and g2 NOT_RUN then RED-OK read from the scratch records; the loader rule at :1486; the plan clause replaced (pending clause 0, guard clause 1, the control the reverse); the manifest bound to its entry by validate (28 OK) |
| 71c1c70 (LOG-085) | the owner's directive recorded: round 1 proceeds, its gating items named, the non-gating TB and plan work frozen, the round record the Critic's next priority | the entry read; a record, nothing to verify beyond its presence and its consistency with the state it names (103 entries, 23 red fixtures, 28 manifests, which the guard landing makes true) |
| 782582f | every deleted line was landing 33's own; the attempt log retained with a manifest row; CR-32 L-2 and CM209-Info-1 answered by id | 11 deleted record lines and 1 deleted response line, each present among 9a6c975's additions; TBMAN 3473 rows 0 bad |

## 2. Rows

- CR-32 L-1: CLOSED by rt35b. CR-32 L-2: CLOSED by landing 34 (retention). CM209-Info-1: answered (the attempt measured and retained, the fixture still
  owed). CM209-Low-1 and CM208-Info-1: CLOSED by landing 35 (my own run of the unit case is the evidence). CM210-Low-3: answered. CM210 Low-1 (the rt35 identity block's unshown invocation), Low-2 (the reader's reset set), Low-5 (the default entry list) and Info-2: Runtime's,
  not in these two commits; rt35b predates the CM210 relay. The standing guard: LANDED and verified (its canonical head-mode run OWED as the log states). v4t: not in this range.

## 3. Findings

- L-1 (rt35b; gen_rt35_red_grading_supplement.log:134-140 and :186-190): RED 3 is not reproducible from its description. "The pre-grading restore removed"
  read literally (the if-pre restore in fcov_check_and_grade deleted) hashes 9a9ee29b951e and makes THREE cases BAD, the two gate cases too, because a
  parked NOT_RUN record then never leaves NOT_RUN; the supplement's RED 3 variant hashes b0efb4372941 and shows exactly one BAD. The edit that produces
  b0efb4372941 is not retained, so the one-BAD red cannot be re-derived, while RED 1's and RED 2's variants reproduce exactly from their descriptions.
  Retain the three reverted-rule diffs beside the supplement (the gen_fu_l13 convention) or state each revert as its exact edit.
- L-2 (rt35b; gen_rt35_red_grading_supplement.log:91-99 against :227-234): PART B's RED 1 block prints two BAD lines for the under-test hash e660220bf7ba
  while PART E prints three for the same hash; PART B's own header says a partial run "would invite the reader to guess" and its excerpt is the partial
  one (runtime-2 has since confirmed a filtered self-test excerpt as the cause, per the Orchestrator). Print all three or state the filter.
- L-3 (landing 34; gen_fu_l33_age17_attempt.log:66 and the record's "47 onsets collapsing to 25 distinct outcomes"): the 25 is not re-derivable from the
  log's own 195 rows under any stated or guessed definition of an outcome (seventeen candidates over the 53 fault-C rows give 18 to 29), because the log
  does not say what an outcome is. The caveat's direction holds, every candidate being far below the 47 onsets, so the fix is to state the definition and
  its command or to drop the number and keep the caveat in words.

### Informational

- I-1: the supplement's line counts 763 / 733 are one above the newline counts 762 / 732; the hash is the claim and it holds.
- I-2: runtime-2's forbidden git checkout is disclosed in the record with its stated blast radius; the working rules reserve every git write to the
  Orchestrator, who has the disclosure; nothing in the committed evidence depends on the discarded working state, which the row says was rebuilt from
  HEAD blobs.
- I-4 (landing 35): the SV unit harness is run by hand and no gate invokes it, which the landing states; until a gate runs gen_ut_drain_cap_top the
  green rests on the retained log and on runs like mine. Both simulation-pair figures reproduce: the base as the recipe over e988ee6's sources (98629b00cb34e79e) and the capfix as the 782582f sources with the landed package swapped in (9b6a43a73ca7774c).
- I-5 (the guard): the retained run's build predates the landing (813994b's sources, identity b48479a3bc6f1d9f) and the entry was staged, not committed,
  at run time, both stated first in the log; the unhittability argument survives because the two covergroup sources are byte-identical at both commits
  (verified), and the canonical head-mode run is owed. The flow's own classify_delta over git diff --name-only 813994b b105c09 gives 83 build inputs and 3 non-inputs (gen_component_api_irq_checker.md, gen_intervention_log.md, gen_runtime_api.md) today; the log's 30 paths and two non-inputs were measured against the HEAD of its run time, which it does not name, so that figure is dated rather than wrong.
- I-3: the six scratch builds of the attempt carry their own local digests and no gate identity, stated; the two probe builds are marked as measurement
  aids from which no claim about the drain is read.

## 4. Principles check

dv-principles-check (docs/dv/dv_principles.md d9c27db18f511411): S4 honesty: the race and the breach stated first (conforming); the attempt's figures
corrected against the summariser and the case not claimed unreachable (conforming); three figures a reader cannot re-derive or that disagree within one
record (L-1 to L-3, non-conforming at those lines). S6 trust triad: the two later self-test cases now have reds that fail with the rule reverted, one
stated as a reliance check without a red (conforming as disclosed). One-line verdict (these two commits): PASS, with three record corrections.

## 5. Verdict

CRITIC VERDICT: APPROVE on the range 390f40f..b105c09 (rt35b, landing 34, LOG-085, landing 35, the standing guard); landing 35's red is a genuine
discriminating unit case reproduced by me in both directions, and the guard's first failing run is the checking mechanism alone. Rows CR-33: L-1, L-2 (runtime-2, corrigendum rows for rt35c) and L-3 (tb-infra-2).
Nothing in the range is gated. OWED and disclosed: the guard's canonical head-mode run of the committed entry (the retained run
is on a build predating the landing, from a staged root).

## 6. Reconciliation with the range's cross-model review

Artifact: dv/auto_dv/reviews/2026-09-04-claude-diff-390f40f1-b105c096.md (da7f548279e8f151, 35 lines), read after Sections 1-5 were written (it was the
wrapper's empty placeholder while they were). Reviewer: Claude Fable 5.1 as the fallback (codex spend cap), fresh session on a detached read-only
checkout of b105c09. Its verdict: APPROVE-WITH-CHANGES with four Lows and two Infos, the five rubrics PASS. Mine: APPROVE on the range. The verdicts
agree; the artifact's rows are record corrections, two of them mine already, two misses of mine, and it corrects one clause of my L-1.

Shared recomputations, each re-run by me and equal to the artifact's: rt35b's hashes and the 30-line delta, the gate revert e660220bf7ba with 3 BAD
against the commit and 2 against the 733-line file, the loader's 102 / 22 / 27 / 0 at bea12ec and 103 / 23 / 28 / 1 at b105c09, the parent log's five cites,
the supplement's manifest row, the flow manifest's 29 rows, gen_regress's 15 ok; landing 34's twelve deleted lines and every summary figure from the 195
rows; landing 35's package digests, the unit test PASS on the landed package and FAIL 4 on the 782582f package with the same four checks, the loop and the
constants; the guard's manifest hashes and log row, the two covergroup sources byte-identical at 813994b and b105c09, cp_ram's bins and the entry's single
knob, the data entry's 904, the plan clause gone. The artifact's guard-efficacy reading (a stopped checker turns the entry PASS and grade_red_fixture
makes that FAIL; a never-run check leaves NOT_RUN and gen_regress.py:754 counts not_run in bad, :758 returning 2) I verified at both lines.

The artifact's findings against mine:

- Its Low (the supplement's PART B prints filtered excerpts: RED 1 shows 2 BAD where PART E shows 3 under one hash; RED 3 under b0efb4372941 shows 1
  where the complete run gives 3; the reverted lines not printed, b0efb4372941 being checkable only as the literal deletion of gen_run.py:166-168): my L-1
  and L-2 as one row, and it corrects one clause of my L-1. CORRIGENDUM to Section 3 L-1: I wrote that the edit producing b0efb4372941 "is not retained, so
  the one-BAD red cannot be re-derived"; the hash IS re-derivable as the deletion of the three lines 166-168 (I deleted two of them and kept the
  assignment, which is why my variant hashed 9a9ee29b951e), verified now: the three-line deletion gives b0efb4372941 and the complete self-test gives 3
  BAD, not the 1 the log prints. What stands of L-1 is that the revert's exact lines are not stated and the one-BAD count is a filtered excerpt, which is
  L-2's finding; the two rows are one defect with one fix (state the filter, print the complete counts 3 / 1 / 3, and the lines each revert removes).
  runtime-2's rt35c corrigendum, already drafted per the Orchestrator, is the vehicle.
- Its Low (gen_fu_guard_fcov_red.log:87, "NOT_RUN ... needs no action" understating that gen_regress.py:754 counts not_run in the failing total, so a
  NOT_RUN guard returns exit 2, and a coverage-off check-tier regression, whose pre-merge gate at :151 skips a run with no vdb, now exits 2 on this
  entry): a miss of tb_l33, adopted and verified (:151, :754, :758 read). The operational point matters for every regression run without coverage from
  now on, and the record should say which regressions are expected to carry the guard.
- Its Low (gen_intervention_log.md, LOG-085's "103 testlist entries ... 23 red fixtures, 28 manifests" presented as state at a commit whose tree had
  102 / 22 / 27, the guard being staged): a miss of severity in my Section 1 row, which called the counts "consistent with the state it names, which the
  guard landing makes true" and did not name the defect; adopted. The counts describe the staged tree and should say so or cite b105c09.
- Its Low (the "25 distinct outcomes" undefined; over one row per onset the finish record, the record total and fired_at each give 25 distinct values):
  my L-3, reached independently; the artifact found the definition, which I verified (47 onsets, one row each: 25 distinct finish records, 25 record
  totals, 25 fired_at lists; the (boundfail, open, ages) tuple 23). L-3 stands with the fix narrowed: state the definition.
- Its Info (763 / 733 against 762 / 732 by newline): my I-1, agreement.
- Its Info (the guard log's "30 changed paths ... two non-inputs" reproduces only against d8f5d99 or c8821a9; later HEADs give three non-inputs and 32
  or 34 inputs): agreement, and it corrects my I-5's figure: I fed every changed path to classify_delta and got 83 / 3, the wrong function for the
  claim; the flow's own build_input_delta over the mirrored subset gives 30 changed inputs and 2 non-inputs against d8f5d99 and 34 / 3 against b105c09 (gen_component_api_irq_checker.md, gen_intervention_log.md, gen_runtime_api.md), so the log's figure is right for the HEAD of its run and dated since.

Nothing else in Sections 1-5 is contradicted; one corrigendum (L-1's "cannot be re-derived" clause) and one figure correction (I-5) are recorded above,
two misses adopted (the NOT_RUN exit path, the LOG-085 counts), all owed through the CM211 rows; no CR-33 row is added and Section 5 stands: APPROVE on
390f40f..b105c09 with rows CR-33 L-1, L-2 (runtime-2) and L-3 (tb-infra-2).
