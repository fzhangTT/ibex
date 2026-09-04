# Critic verdict: the range fd76548..390f40f (runtime-2's rt35 e988ee6, tb-infra-2's landing 33 9a6c975, the DV Lead's v4s 390f40f), reviewed as tb_l32

Scope (the Orchestrator's): the range opens at fd76548 with Runtime rt35 (eleven files: the red-fixture grading moved into one check-then-grade function
reached by gen_run and the regression's pre-merge pass, the deferred red's NOT_RUN verdict when no stage checked the expectation, gen_read_keyed.py's
reset fix, gen_compare_forms.py as a tool, the retained log gen_rt35_red_grading.log with four verdict directions on one entry, build and seed, the
CM205 and CM206 rows); landing 33 (tb-infra-2, 9a6c975: two corrigenda to retained logs, the drain-cap resize measurement, the age-17 fixture attempt, answering CR-31b L-1
and L-2 and CM209 Low-1, Low-2, Low-3 and Info-1 by id) joined it while this file was unfrozen, and v4s (the DV Lead, 390f40f: the inputs-digest headers, the CR-30b lift, the CM209 answers) closed it: the
range's review launched on fd76548..390f40f at 18:00Z. v4s is judged by id in tb_l30c (its own file, the CR-30 re-review); this file judges it as a member
of the range. runtime-2's rt35b (the CR-32 L-1 corrigendum) is not in this range.

Artifacts reviewed (committed blobs at e988ee6 for rt35, at 9a6c975 for landing 33, at 390f40f for v4s; sha256 first 16 hex):

- dv/auto_dv/docs/gen_fcov_plan.md  f3eb5b5f7c9fa35b
- dv/auto_dv/docs/gen_feature_list.md  2bd7b33ba65ff7b5
- dv/auto_dv/docs/gen_test_plan.md  7294ee9071da271c
- dv/auto_dv/evidence/gen_critic_response_plan_set_v1.md  f637545b0e5a5918
- dv/auto_dv/evidence/gen_round0_covergroup_set.md  5d27e1b645626aa7
- dv/auto_dv/evidence/gen_round0_credit/gen_round0_credit.md  036021c0c3b6c1dc
- dv/auto_dv/evidence/gen_round0_credit/gen_round0_credit_summary.md  e1a397fcebe93d10
- dv/auto_dv/evidence/gen_round0_promotion_table.md  0fe27d1ff55a6e25
- dv/auto_dv/tools/gen_record_check.py  4f59e8c3cfe2ff02
- dv/auto_dv/evidence/gen_critic_response_fu2a.md  0ee513fd1f3b891c
- dv/auto_dv/evidence/gen_tdd_logs/gen_manifest.md  cee80bfe90c59654
- dv/auto_dv/evidence/gen_tdd_logs/mutations/gen_fu_l31b_drain_corrections_corrigendum.log  59cab9130f3ee5cf
- dv/auto_dv/evidence/gen_tdd_logs/mutations/gen_fu_l31b_nmi_wave_run_corrigendum.log  6442818c43311833
- dv/auto_dv/evidence/gen_tdd_logs/mutations/gen_fu_l33_drain_cap_resize.log  e7c0c79d0653e10c
- dv/auto_dv/evidence/gen_tdd_step2b.md  d642fe590a5abd87
- dv/auto_dv/docs/gen_runtime_api.md  316acb958628ccf0
- dv/auto_dv/evidence/gen_critic_response_flow.md  eabed6e57052ee48
- dv/auto_dv/evidence/gen_tdd_logs/flow/gen_manifest.md  f1cdc8538128483e
- dv/auto_dv/evidence/gen_tdd_logs/flow/gen_rt35_red_grading.log  0383df9f374e9704
- dv/auto_dv/flow/gen_flow_const.py  0789b7b5389d8dea
- dv/auto_dv/flow/gen_flow_util.py  0c495812d1eeed60
- dv/auto_dv/flow/gen_regress.py  5c9869bbe0784aee
- dv/auto_dv/flow/gen_run.py  6d20a0b5dc329827
- dv/auto_dv/flow/gen_verdict.py  e1f6734747bf1c03
- dv/auto_dv/tools/gen_compare_forms.py  c65b4f17f697d194
- dv/auto_dv/tools/gen_read_keyed.py  00e94d7c8cb647c9

Date: 2026-09-04 (UTC). Role: Critic (reviewer other than the author). Basis: docs/dv/dv_principles.md d9c27db18f511411; the CM205 artifact
(67321c64cfcfd5e4) and the CM206 artifact (57cae3d7dc078c0f) whose rows rt35 answers; my tb_l29 Section 6 (the Excluded/Illegal table reproduction that
became CM206-Low-2); the evidence rule; the mutation-proof / TDD-red standard that a new rule's cases fail with the rule reverted and pass with it.
Method: detached git worktree of e988ee6 (the gate: both codegen --check up to date, three UTs PASS, CONST, RED-CHECK, validate 27 OK, TBMAN 3469 rows 0
bad including the new flow row, 27 flow rows; build identity e674e6339b5bea85 unchanged, the range touching no build source; the eight flow --self-test
commands all PASS, gen_verdict's 62 cases 0 BAD). The retained log read whole (463 lines). Reproduced by me: the two self-test reds, by reverting each
rule in a full archive copy of e988ee6 and running the self-test (the pre-merge gate: 3 BAD; the unchecked-fixture rule: 1 BAD; both restored: 0 BAD);
the retention trap, by adding the scratch root's fixture entry and manifest to the copy and calling load_testlist three times (accepted 103, REFUSED with
the red_expect message once direction one's sim_stdout.log sat at the lockstep family path gen_lockstep_icache_ecc_fcov_red1_stdout.log, accepted 103
again); the positive control and the A/B from the six scratch run records the log names (verdicts and result.yaml hashes); the keyed reader on e1, e4 and
e5 (rc 0, 0, 1); the reader's reset fix on my own tb_l29 fixture and the old parser on the new fixture (five keys against three); gen_compare_forms.py's
--self-test and its run on the two real run trees; the build identity against the build manifest; the testlist shape through the loader; the CM205-Low-1
quantities at cea5a4a; the API document's phrasing. Landing 33 on a detached worktree of 9a6c975 (the same gate, TBMAN 3472 rows 0 bad including its three
new rows; the gate's identity leg reports the wave root's 32ee156a5dd888e8 as matching no build of the tree, which the corrigendum itself states); its
three retained corrigenda read whole and every measurement re-run by me over the wave root and the tb-infra work directory (the three artefacts printing
96697a6fee7025b4, the compile command's tokens, the 0 / 0 / 3 file counts, the identity tool's rc 1 and 0; the seed-7 drain line in exactly one root, wit/l31a
with no drain line and "younger than the bound=1", the four roots printing f80e2c719e16b73c and one root each for the two corrected figures, the FIX root's
98629b00cb34e79e and its two drain lines); the cap arithmetic and the base build's figure reproduced from an archive of e988ee6. v4s on a detached worktree of 390f40f (the same gate; the four
records byte-identical on an archive copy with --plan-sha v4s-on-e988ee6; gen_record_check.py three pairs, self-test 7 of 7, tree run 0 problems; the
reword on flattened text with 2410402 as the control; the three headers' digest 86adeb302725 and no clock left), the row-by-row verification in tb_l30c. EXPOSURE: the Orchestrator's message; Runtime's scratch run records under scratchpad/rt35 and its
work directory out trees (read on disk). No subagent used. Section 6 reconciles with the range's cross-model review when its artifact lands (none
exists yet).

CRITIC VERDICT: APPROVE on the range fd76548..390f40f (rt35, landing 33, v4s). The grading moves to where its evidence is and
every direction is shown by a real run with the record's own hashes; the self-reported regression-path defect is fixed in the same touch with a positive
control that keeps the skip honest; every CM205 and CM206 row is answered as stated and verified by my own reproduction. One Low: the retained log's
code-under-test hash for gen_regress.py names a pre-final draft, two self-test cases having been appended after PART E ran, so the log's RED 1 shows two
cases going BAD where three do against the committed file; the grading code is identical between the two versions.

## 1. What was verified

| commit | item | evidence (re-derived by me) |
|---|---|---|
| e988ee6 (Runtime rt35) | the four verdict directions on one entry (gen_ut_lockstep_icache_ecc_fcov_red, a scratch copy of the committed tag_disabled entry with red_fixture and red_expect), one build (b48479a3bc6f1d9f, the l25 exercise build at 813994b) and seed 1: RED-OK on the declared unreachable bin; FAIL undeclared on a different unreachable bin; FAIL passed-unexpectedly on a reachable bin; the regression shape NOT_RUN from gen_run then RED-OK by the pre-merge pass | the six scratch run records: e1 RED-OK, e2 FAIL, e3 FAIL, e4 RED-OK with result.yaml 48d8e26b5c99, e5 FAIL with fd92f3b97f83 unchanged by the pre-fix pass, e6 PASS rewritten to a39ae04eeef5; the three fixture copies hash 26948ce0f9e0 / 208a627414bc / 2436b2d4c028 as PART A states; the build manifest's inputs.sources_sha256 begins b48479a3bc6f1d9f with source root mirror_head/813994b |
| e988ee6 | the self-reported defect and its fix: the first form graded the fixture on the passing sim log and the pre-merge pass skipped every verdict but PASS and XFAIL; fixed by the gate admitting a deferred red whatever its parked verdict and the record carrying red_pre_grading; latent because no committed entry carries both red_fixture and a manifest (102 entries, 22 and 27) | the code diffs (gen_regress.post_fcov_checks, gen_run.fcov_check_and_grade and finalize_deferred_red, gen_flow_util.red_grading_deferred, gen_flow_const); PART C's A/B read from the e5 / e6 records; the loader on the committed testlist at e988ee6: 102 entries, 22 red fixtures, 27 manifests, 0 both |
| e988ee6 | the self-test reds: each new case run with its rule reverted and with the fix | reproduced in an archive copy: the gate reverted gives 3 BAD lines (the log's RED 1 shows 2: Section 3 L-1), restored 0; the unchecked-fixture rule reverted gives 1 BAD (the log's RED 2), restored 0; RED 3 not constructed and said so |
| e988ee6 | the retention trap: a failing stdout under the lockstep family's naming makes load_testlist refuse the entry | reproduced: 103 accepted, REFUSED (SystemExit 1) with "red_expect ... refused: no collected evidence line in the retained pinned-red log (gen_lockstep_icache_ecc_fcov_red1_stdout.log ...)", 103 accepted again after removal; red_group gives lockstep_icache_ecc_fcov from the gen_ut_ prefix and the _red suffix |
| e988ee6 | the keyed reading never reads a verdict: e1 and e4 agree line for line, e5 reports no derived report and exits 1 | the committed reader run on the three directories: rc 0, 0, 1 with the same lines |
| e988ee6 | CM206-Low-2: parse_report resets on Excluded/Illegal bins and Variables for, with a name-collision fixture the committed parser fails | my tb_l29 fixture: reader and checker now equal with the illegal table and the masking case reads NOT IN MY READING rc 1; the 2410402 parser on the new fixture reads five keys including cp_b.hit_a 99 and cp_b.bogus 42, the e988ee6 parser three |
| e988ee6 | CM205-Info-2: gen_compare_forms.py as a tool with --self-test; CM205-Info-1: "five cases over three exit codes" in the API document with the retained header's "four exit paths" explained; CM206-Info-1: the OWED_SUFFIXES comment naming the plan as authority; CM206-Info-2: both scratch run directories named in the row | --self-test PASS rc 0, no argument rc 2; run on l25_isolated_1435 against l25_exercise_1430/runs it prints the corrigendum's two closing lines byte for byte at rc 0; the phrases present once each; the comment read; the row's two paths read |
| e988ee6 | CM205-Low-1: a mislabel not a miscount; four quantities with their commands at cea5a4a: 1043, 673, 979, 647 | all four reproduced at cea5a4a by the row's own commands |
| 9a6c975 (tb-infra-2 landing 33) | CR-31b L-2 = CM209-Low-2: the wave-run corrigendum withdraws d71984c246000108 and 2bae046d70476d78, names 96697a6fee7025b4 as the figure the compile log (:1154), config_opts (:2) and the run header agree on, measures the root's gate digest at 32ee156a5dd888e8 with the tool exiting 1 against the withdrawn figure, and corrects the debug flags (+pp then +all) | every line re-run: the three artefacts, the tokens, 0 / 0 / 3 files, 32ee156a5dd888e8 with rc 1 and 0; the retained wave log untouched (its manifest row still verifies) |
| 9a6c975 | CR-31b L-1 = CM209-Low-3: the drain-corrections corrigendum re-attributes landing 31's build to wit/l31c (d34daf56c8871437) by matching the five quoted drain lines, names wit/l31a as an earlier build with no drain line, the pre-fix red as wit/nmi1 (f80e2c719e16b73c), prints the corrected build's figure 98629b00cb34e79e, and states that a local figure names sources, not a root (four roots share f80e2c719e16b73c) | every measurement re-run in the work directory and equal; 98629b00cb34e79e equals my recipe over the committed a759752 and e988ee6 sources |
| 9a6c975 | CM209-Low-1: the cap sized over the record bound confirmed term by term (gen_tb_pkg.sv:556, gen_env_pkg.sv:377, :253), 9x17+40 = 193 against 9x18+40 = 202, two builds on one out-of-tree root both retiring 18 records in 126 cycles with only the printed cap moving; not offered as a discriminating red; the source edit OWED because gen_tb_pkg.sv in the shared tree carries the uncommitted NMI knob gated on tb_l30b | the constants and lines read; the arithmetic; the base figure 98629b00cb34e79e reproduced from e988ee6; the tree's gen_tb_pkg.sv is modified (the knob) as stated; the capfix figure: Section 3 I-4 |
| 9a6c975 | CM209-Info-1: the age-17 fixture attempted (MUT-BND2 withholding every maskable line past a record count) and STILL OWED, the route named (a directed program raising a line on the finish-request record) | the disclosure read; the attempt's runs: Section 3 L-2 |
| 390f40f (DV Lead v4s) | the CR-30b lift (the surviving clause reconciled, the pair declared; the precondition argument on the retained runs), CM209-Low-1 stated as the code's and one record short, CM209-Info-2's three pairs, the inputs-digest headers at all three sites, the records re-keyed to v4s-on-e988ee6, the gitignored generator stated | tb_l30c Section 1, every item; here: the records byte-identical, the tool's tree run B / A / A with 0 problems, the digest 86adeb302725 at all three sites, no build source touched |
| e988ee6 | the final-manifest verdict stated as a source-order claim (gen_regress.py :658, :709, :712), not measured, since gen_build refuses a bound root without a head-mode mirror manifest; pinned by two self-test cases instead | the disclosure read; the two cases are among the three the gate reversion fails |

## 2. Rows

- CM205-Low-1, Info-1, Info-2 (Runtime's) and CM206-Low-2, Info-1, Info-2 (Runtime's): answered as stated and verified. CR-31b L-1 and L-2 (tb-infra's):
  CLOSED by landing 33's corrigenda, every figure re-derived. CM209 Low-2 and Low-3: answered as stated; CM209-Low-1: measured, the source edit owed and
  the reason stated; CM209-Info-1: attempted, still owed. CR-30b M-1 and L-1 (the DV Lead's): CLOSED by v4s, verified in tb_l30c; CM209-Low-1 (the DV Lead's half) stated,
  CM209-Info-2 answered. The rt34 detector control's
  fixture-manifest informational (my tb_l29 I-1, relayed as CM205-Info-2's second half): the log now carries each fixture's full text as the run recorded
  it. Landing 33's and v4s's rows: when they land.

## 3. Findings

- L-1 (rt35; gen_rt35_red_grading.log:46, :114, :269, :379): the code-under-test hash for gen_regress.py is 57b934c34c91 while the committed file at
  e988ee6 is 5c9869bbe078. The difference, read from the scratch root's copy against the commit, is two self-test cases appended inside self_test after
  the log's runs (the NOT_RUN summary case and the crashed-deferred-red regrade case); post_fcov_checks and summarize are identical, so every run in the
  log exercised the committed grading logic. But the log's RED 1 reports two cases going BAD against the reverted gate where three do against the
  committed file, and a reader cannot match the log's hash to any committed blob. The other six hashes match the commit. Fix by corrigendum row: name the
  committed hash, the two added cases and the three-case red (the log's bytes never move).

- L-2 (landing 33; gen_tdd_step2b.md, the age-17 section, and the CM209-Info-1 response row): the attempt's figures (three builds, 53 runs, 111 survivor
  lines, ages 8 to 15 stepping by two, the crossing at T = 3417 to 3421 with the finish request moving 3629 to 3633, three of four seeds with no survivor)
  come from runs no retained artefact carries: the landing retains three logs and none is the MUT-BND2 sweep (0 files under gen_tdd_logs name it). Under
  the evidence rule those figures count as nothing; the outcome they support (the fixture still owed, the threshold axis unable to dial the age, the
  route a directed program) is stated honestly and stands, and the record should either retain the sweep's summary with a manifest row or state the
  figures as an unretained observation, as the DV Lead's v4r row did for the 24-seed sweep.

### Informational

- I-1: the log's :34 says "gen_build_identity.py exit status above: 0" and no line above prints that status; the identity itself is right (the build
  manifest's inputs.sources_sha256 begins b48479a3bc6f1d9f and my tool run on that manifest's root is not needed to see it), so the sentence describes a
  check it does not show.
- I-2: the CM205-Info-2 row's "the two real run trees" are l25_isolated_1435 and l25_exercise_1430/runs; the tool needs the runs subdirectory named, which
  the row does not say.
- I-4 (landing 33): the cap-resize log names the capfix build's local figure 7661f6b6b3a65a3e for "the one-line change and its comment" but retains
  neither the diff nor the comment text; the return line alone changed on an archive of e988ee6 gives 598fbc1e33c940fb, so the figure is not reproducible
  from the record. The pair is explicitly not offered as evidence and the source edit, when it lands, carries its own diff, so this is a note and not a row.
- I-3: the age-bound and retirement-stall items of landing 32 are untouched here; the standing guard itself (a committed red fixture with a manifest) is
  still not in the tree, which the log states as the reason the defect was latent.

## 4. Principles check

dv-principles-check (docs/dv/dv_principles.md d9c27db18f511411): S6 trust triad: the new rules carry reds that fail with the rule reverted and pass with
it (two of three constructed, the third stated impossible and why), a positive control for the skip, and the retention trap measured, not predicted
(conforming). S4 honesty: the scratch entry, the non-durable run directories, the unmeasured final-manifest ordering and the unconstructed RED 3 are all
stated; one code hash in the identity block is not the commit's (L-1). One-line verdict (rt35): PASS, with L-1 a record correction.

## 5. Verdict

CRITIC VERDICT: APPROVE on the range fd76548..390f40f. Rows CR-32: L-1 (Runtime, a corrigendum row on the gen_regress.py hash) and L-2 (tb-infra-2, the
age-17 attempt's unretained figures). CR-31b L-1 and L-2 are closed by landing 33; CR-30b M-1 and L-1 are closed by v4s (tb_l30c), so the CR-30 gate lifts
on that file. Nothing in the range is gated.

## 6. Reconciliation with the range's cross-model review

Artifact: dv/auto_dv/reviews/2026-09-04-claude-diff-fd765489-390f40f1.md (47ac33f727903e7d, 59 lines), read after Sections 1-5 of this file and of its
companion were written (it was the wrapper's empty placeholder while they were; one artifact covers the range, so tb_l32 and tb_l30c reconcile against
it). Reviewer: Claude Fable 5.1 as the fallback (codex spend cap), fresh session on a detached read-only checkout of 390f40f. Its verdict:
APPROVE-WITH-CHANGES with five Lows and two Infos; the rubrics PASS except one minor item each under ai-slop-comments and magic-numbers. Mine: APPROVE on the range. The verdicts are compatible: the artifact's rows are record corrections and two tool refinements, none
reopening a claim of the range, and it confirms both of my CR-32 rows.

Shared recomputations, each re-run by me and equal to the artifact's: the gen_regress.py delta (the committed blob 5c9869bbe078 minus lines 469-498 gives
57b934c34c91; my count 762 lines by newline) and the six other code hashes equal to the commit; the self-tests (gen_verdict 62, gen_flow_util 159, gen_run
31, gen_regress 15 ok, gen_read_keyed and gen_compare_forms and gen_record_check PASS; RED-CHECK PASS); grade_red_fixture as a verbatim extraction,
fcov_check_and_grade's restore-check-grade order, finalize_deferred_red's NOT_RUN, red_grading_deferred the single predicate; run_one's argv without
--fcov-check, the widened gate, summarize's NOT_RUN accounting; the loader's 102 / 22 / 27 / 0; the reader's fixture reading five keys on the old parser
and three on the new; "five cases over three exit codes"; the CM205-Low-1 counts 1043 / 673 / 979 / 647; the flow manifest's 27 rows; landing 33's two
retained logs byte-identical to a759752's blobs, the wave log's :19 header and :10-11 withdrawn figures, the drain corrigendum's five quoted drain lines
and the withdrawn clause at :9, the resize arithmetic 193 and 202 with the source edit absent; the 3472 manifest rows; v4s's items as tb_l30c states them.

The artifact's findings against mine:

- Its Low (gen_rt35_red_grading.log:33, "exit status above: 0" with no invocation or rc printed, the manifest named only through the build outdir):
  my I-1, which I carried as informational because the identity itself checks against the build manifest; its severity is adopted: a recomputation
  asserted and not shown is the class my rules name for retained identity blocks, and the fix it proposes (the tool's invocation, printed line and rc in
  the rt35b supplement) is right. The supplement at bea12ec, already committed for the next range, cites the commit blobs and not that invocation, so the
  item stays open for Runtime.
- Its Low (gen_read_keyed.py:56, the new reset matching Excluded/Illegal bins and Variables for only, while the checker's :87 also resets on any
  "Summary for" and on 10-dash or 10-equals rules, the reader's own Summary branch at :43 firing only for Variable and Cross; the CM206-Low-2 row's "the
  parser now resets on the checker's own set" overstating): a miss of tb_l32, adopted and verified (:43 and :56 against ci/check_fcov_expectations.py:87).
  I proved the fix on my own fixture, whose only extra table was the Excluded/Illegal one, and did not compare the two reset sets pattern by pattern,
  the class my rules name (a parser's boundary set is checked against the reference's, not against the case that prompted the fix).
- Its Low (gen_critic_response_fu2a.md, the CM209-Info-1 row's age-17 figures with no retained artefact): my L-2, reached independently. Landing 34
  (782582f, the range after this one) has since retained the whole attempt as 195 rows with a manifest row and corrected the row and the record in
  place; I recomputed every one of its summary figures from the retained rows for the next verdict.
- Its Low (gen_critic_response_plan_set_v1.md:845, "two declared pairs" against the tool's three): v4s's, reconciled in tb_l30c's Section 6.
- Its Low (gen_compare_forms.py, DEFAULT_ENTRIES hand-encoding nine testlist names): a miss of tb_l32, adopted and verified (all nine exist in the
  testlist at 390f40f; a rename would break the default silently). The name list exists so the corrigendum's invocation stays reproducible, which the
  tool says; deriving it from the entries that carry an icache-ECC manifest, or requiring --entries, is the right shape.
- Its Info (the plan's "12 taken NMI entries" summing the duplicated summaries; over the 10 distinct summaries 4 NMI entries over 1654): adopted and
  verified (my sum over the 10 distinct texts: 1654 and 4). It bears on v4s's sentence and is carried in tb_l30c's Section 6.
- Its Info (gen_run.py:458 "exactly as before" narrating history): adopted; a comment rule item.

Nothing in Sections 1-5 is contradicted by the artifact; no corrigendum. One severity adopted (I-1 to Low), two misses adopted (the reset set, the
default list), all owed through the CM210 rows; the CR-32 rows stand. Section 5 stands: APPROVE on fd76548..390f40f.
