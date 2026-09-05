# Critic verdict: the "flow follow-ups" group, a58f562..44a24f5 (runtime-2: 7930d04, 84daf23, ad357f1, 6caf314, 44a24f5)

Artifacts (runtime-2's five commits; sha256 first 16 hex of each blob at 44a24f5):
- dv/auto_dv/flow/gen_build.py 74599741aa16966e; gen_flow_util.py 8744412c9ca5297b; gen_flow_const.py 419a6d25f9025af7;
  gen_regress.py 26aab93c0f186e1f; gen_round.py 1ab2fba4783b9fa9; gen_run.py 600012e27f978436; gen_dashboard.py faf55d23c7bec117
- dv/auto_dv/docs/gen_rt39_flow_record_fixes_plan.md 8d330d46bf0deb0c; dv/auto_dv/docs/gen_runtime_api.md 37a6f39875c81aa1
- dv/auto_dv/evidence/gen_critic_response_flow.md b7f5dace7425690f; dv/auto_dv/evidence/gen_tdd_logs/flow/gen_manifest.md 47d262e685a63ab2
- dv/auto_dv/evidence/gen_tdd_logs/flow/gen_build_identity_red.log 50dd74ed4d5471cc; gen_rt37_red_case13.log 0c08c8b556f116b4;
  gen_rt39_reds_basis.log 60c74a5b8aca438c; gen_rt39_reds2.log b69f55f8c74d010f; gen_export_default_red.log 1a6fb20821014cb5

Date: 2026-09-05 (UTC). Role: Critic. Method: the five commits' diffs read from the blobs; the nine flow self-tests and the
const check run on a detached worktree of 44a24f5; the five scripts folded into gen_rt39_reds2.log extracted by their block
markers, their md5s checked against the log's, and re-run by me against the 44a24f5 flow modules (the scripts hardcode the
clone's flow path, which I substituted for the worktree's and nothing else); the reds2 log's basis tree 8e90263 compared to
the range end blob by blob; the response rows, plan corrections, API text and manifest rows read against the blobs.
Exposure: the Orchestrator's range message summarised the five commits' content and named the rows they answer; rev69's
artifact exists in the tree and is read only in Section 6. Logs: dv/auto_dv/work/critic/rt39/ (selftests_44a24f5.log,
reds2_scripts_rerun_44a24f5.log, reds2_scripts/).

CRITIC VERDICT: REQUEST-CHANGES (confined to M-1, M-2 and M-3, three records findings of the same shape as the rt39 M-2 this
range closes, all three found by rev69 and verified by me after my Sections 1-4 had missed them; stated as my misses in Section
6). The REQUEST-CHANGES of gen_critic_flow_rt39.md on 557e490..a58f562 is LIFTED on this range: its M-1, M-2 and M-3 are closed
as Section 1 states.

## 1. The rt39 rows, verified

- M-1 (the coverage record's build_defines key changing population): gen_regress.py:721-722 at 44a24f5 writes
  build_defines_all and build_parameters_all and no longer writes the old keys, so a reader of a round-2 record finds them
  absent rather than changed, and the API document's Section 10 says the new keys appear from round 2 while rounds 0 and 1
  carry the one-token build_defines, naming the boundary. CLOSED.
- M-2 (the reds transcript's tree header, the unretained scripts, the unevidenced identity red): gen_rt39_reds2.log re-runs
  the four scripts at 8e90263, a commit that holds the rt39 code, proves its basis in Section 0 (the nine flow modules'
  working-tree digests equal the commit's blobs, git status empty; I confirmed those nine values against 8e90263's blobs),
  folds all five scripts in with md5s, and runs the identity red for the first time (Section 5). Re-derived by me: the five
  extracted scripts hash to the log's md5s and all five pass against the 44a24f5 modules (red_item5 fails its control shape and
  passes the changed one; control_item5 reproduces both committed archives; control_item1 the three figures and the
  3484/4048 red; control_item4 the digest absent 0 times in the committed index; identity_item1 three consumers agreeing and
  the dashboard-diverges case caught). The four rt39 modules the reds exercise are byte-identical between 8e90263 and 44a24f5;
  the four that differ do so only by 44a24f5's export default. gen_rt39_reds_basis.log states the old transcript's basis
  without touching its bytes, and the old rows are repointed in the manifest with their sizes and md5s unchanged. CLOSED.
- M-3 (the plan's Section 2 contradicting the landed selector and the withheld restatement): two dated CORRECTION blocks at
  84daf23 say the shipped selector reads group_bins_all under LOG-097 addendum 4 and that the restatement was planned and
  not done, with the reasoning kept for the day the selector moves; the label half was done at 84daf23 rather than left
  undone (gen_round.py:145-146 and :355 build from C.GROUP_CELL_FIELD, C.GATE_PCT and C.group_cell_scope(); the literal
  "bins >= 80" survives only in the prose comment at :35, as the row says). CLOSED.
- L-1 (property demonstrations mislabelled as reds against pre-change code): two dated corrections in the plan, and the
  identity red now run (above). L-2 (round_sources first build only): round_sources_all collects every build, the scalar and
  the match are None unless the set is a singleton (gen_round.py:272-292). L-3 (the rt37 case-13 line): the companion
  gen_rt37_red_case13.log carries the measured line and states that the archive contrast stays prose; disclosed, owed.
  L-4 (the A-002 line): my premise was wrong too, as runtime-2's row says of its own: the ci/env.sh case at
  gen_flow_util.py:985 is a deliberate negative case; the real defect, one message for two causes, is fixed with two
  branches and a self-test that drives both. L-5 (label and API): the label derives; Section 10 names group_bins_all and
  why. L-6 (dead totals): gone from metric_row and dut_scope_row. L-7 (the manifest write untested): the key-set case plus
  the live regress_bid3 manifest carrying defines_all (9), parameters_all (14), no defines, and vpi_lib; the write itself is
  still unreached by a self-test, disclosed. All as the rows state.

## 2. The export default (44a24f5)

export_file_for (gen_flow_util.py) is the one predicate: the entry's own plusarg wins, an entry in C.EXPORT_DEFAULT_FEATURE_GROUPS
("irq",) gets C.EXPORT_DEFAULT_FILE, any other entry none; gen_run.effective_plusargs appends the default plusarg once and
export_origin records entry, default, operator or none in result.yaml (an operator plusarg outranks both); gen_regress.prune_plan
reads the same predicate, so a defaulted export is retained and pruned like a named one; the self-tests cover the three
origins, the operator override and the prune plan. The scope is two testlist entries (gen_test_irq_basic and its red fixture);
the eight gen_ut_export entries name their own file and keep it. The live red (gen_export_default_red.log Section 1): the same
entry, seed, simv and mirror, driver trees differing in exactly four files; PRE records export_file None and writes no
gen_export.txt, POST writes 152068 bytes with all seven sources in its header and origin "default", the verdict PASS in both,
which was the risk worth checking (export_check fails a PASS run that names a file and writes none). The sizing is stated per
record with the author's earlier per-cycle figure corrected in the log. The removal guard names its two refusal causes
apart and a self-test drives both.

## 3. The build identity (7930d04)

The identity gains vpi_lib (path, digest, presence) since two builds linking different VPI libraries share a sources digest;
--local-cocotb refuses before compiling when cocotb-config or the library resolves outside the clone's pinned venv, and the
version record names which cocotb-config answered and whether it is the pinned one. gen_build_identity_red.log measures the
red on the committed round-0 manifest (the identity names the library 0 times; swapping the library leaves it unchanged),
proves rows 1 and 3 on a real head-mode build (regress_bid3, vpi_lib present with its digest) and row 2 by a refusal that
leaves no compile.log and no simv, and states honestly that the pinned flag reads False from an archive because an archive
has no .venv, with the clone control reading True.

## 4. Records, three Mediums and the Lows

- The five new logs' manifest rows carry the files' sizes and md5s (20952 / f1c48578..., 1766 / 22b707b8..., 1893 /
  ad77e384..., 3363 / 91acc545..., 8350 / 2f60aec4...); all ASCII. The two retained logs' rows are repointed in their
  description columns with sizes and md5s unchanged, which is the index and not the log.
- M-1 (Medium, records; runtime-2). gen_export_default_red.log's live red rests on an asserted basis: its header says the two
  driver trees are archives of edbe821 differing in exactly four named files, but it records no digest of those four files on
  either side and no build identity for the run pair, so a reader cannot tie the POST tree to 44a24f5's blobs (the log carries
  no sha256, md5 or blob reference at all). The same shape as my rt39 M-2, which this range closes for the rt39 reds; the
  export red needs its Section 0. I accepted the header's word in Section 2 and rev69 did not.
- M-2 (Medium, records; runtime-2). The Critic rt39 L-2 response row's Proof says "the self-test covers the singleton and the
  mixed cases"; gen_round.py's self_test at 44a24f5 (:408 onward) never calls collect and has no case on round_sources_all or
  sources_sha256_match, so the row states a test that does not exist. The code is right (Section 1); the row is not. I
  verified the code and not the row's proof.
- M-3 (Medium, records; runtime-2). gen_build_identity_red.log's header names tree acbb40d, the parent of 7930d04, which
  contains none of the build-identity code (vpi_lib_identity occurs 0 times in gen_flow_util.py at acbb40d and 1 time at
  7930d04), and its RED and ROW sections do not name the flow files that ran: the transcript ran on uncommitted working-tree
  files over that HEAD without saying so, exactly the rt39 M-2 shape, one landing later. I read the header's tree and did
  not test it.
- L-1 (Low, test; runtime-2). The three-consumer identity check, the plan's first red for item one, exists as a retained
  script in the log's appendix and passes on my re-run, but no committed self-test drives metric_row and dut_scope_row from
  one record, so a future divergence of the selector's consumers is caught by a reader re-running a log, not by the suite.
  Make identity_item1's check a gen_round self-test case (rev62's M-4 asked for the same).
- L-2 (Low, records; runtime-2). All five appendix scripts hardcode /localdev/fzhang/ws/ibex-challenge/dv/auto_dv/flow, so
  "reproducible from the record" needs a path edit on any other checkout; resolve the flow directory from the script's own
  location, as gen_round_form_check does, or say the substitution in the appendix header.
- L-3 (Low, comment; runtime-2). gen_regress.py:717-720 narrates history and names a review row ("which is the defect CM222
  L-1 fixed for the build manifest"); gen_flow_const.py:583 carries "(CM219 MINOR-2)". State the intent, drop the tags.
- L-4 (Low, code; runtime-2). The pinned-venv test is substring containment (gen_build.py:49 and :56, gen_flow_util.py:314:
  `str(venv) in str(resolved)`), so a sibling path beginning with the venv's name passes, and the predicate is written twice.
  One Path.is_relative_to in gen_flow_util, called from gen_build.
- L-5 (Low, test comment; runtime-2). The gen_build case added for my L-7 reads set(compile_config(argv)), the same return the
  adjacent cases assert on, while its comment says it "reads the manifest's own construction"; it cannot fire on the manifest
  literal. The row discloses the limit; the comment should too.
- L-6 (Low, records; runtime-2). gen_runtime_api.md Section 1 still scopes the header check to "a run whose entry names
  +gen_export_file" and lists result.yaml's export keys without export_origin; under the default the check applies to any run
  whose argv carries the plusarg from the entry, the operator or the default.
- L-7 (Low, records; runtime-2). The L-7 response row dates the regress_bid3 build manifest "07:18:29Z"; the manifest's own
  finished_utc is 2026-09-05T11:18:29Z (started 11:18:05Z), so the row wrote the local time as UTC.

- Info: gen_flow_util.py's self-test hardcodes +gen_export_file=own.txt where gen_run's derives the name from
  sv_plusarg_names (rev69).

Conformance (dv_principles.md): no measurement changes; every new record fields carries its scope; the reds are live and
their scripts are in the tree; the export default is one constant, one predicate and one recorded origin, with a red whose
verdict does not move.

Verdict: CRITIC VERDICT: REQUEST-CHANGES on a58f562..44a24f5, confined to M-1, M-2 and M-3. The rt39 group's REQUEST-CHANGES lifts
(its three rows are closed by 84daf23 and the reds2 re-run, whose basis IS proven); what remains is the same basis defect on two
newer transcripts and one false proof sentence in a row. Approved as they stand: the export default's one predicate and one
recorded origin, the build identity's VPI term and its pre-compile refusal, the plan corrections, the API text, the five
re-run scripts. L-1..L-7 owed as disclosed.

## 6. Reconciliation with the cross-model artifact rev69

Read after Sections 1-4 were written: dv/auto_dv/reviews/2026-09-05-claude-diff-a58f5620-44a24f5e.md at 4b8d667 (claude CLI
fallback under A-001; APPROVE-WITH-CHANGES; three Mediums, six Lows, one Info). Its verified list agrees with Sections 1-3 on
the single predicate, the four origins and the operator precedence, the removal guard's two branches, the reds2 basis (it
recomputed the same nine digests and the five md5s and byte counts I did), the manifest rows and the 84daf23 attributions; it
adds three checks I record as its: every consumer of the export plusarg grepped across flow, tools, tb/unit, fixtures and the
local runner; the export header written in start_of_simulation_phase, so a PASS or RED-OK irq run always has one for
export_check; and measured_refusal returning None for the real entry with measured forced true.

- Its three Mediums are my M-1, M-2 and M-3, all three verified by me after reading it and all three MY MISSES in Sections
  1-4: I accepted the export red's "differ in exactly four files" without asking for the digests (the log has none); I
  verified the round_sources code and not the response row's proof sentence (gen_round's self_test has no such case); and I
  read the build-identity log's "tree acbb40d" without testing that acbb40d holds the code (it is 7930d04's parent and does
  not). The rt39 M-2 standard I applied one range earlier applies here, so the grade is Medium and the form REQUEST-CHANGES.
- Its six Lows are adopted as L-3 (the two review-naming comments), L-4 (substring containment, the predicate twice), L-5
  (the gen_build case's comment overstating what the return-dict check reads), L-6 (API Section 1 stale under the default)
  and L-7 (the 07:18:29Z stamp; the manifest reads 11:18:29Z, verified on the out-tree file); its Info on the hardcoded
  plusarg name is carried as an Info. My L-1 (no committed identity self-test) and L-2 (the appendix scripts' hardcoded
  clone path) are not in rev69.
- On the verdict: rev69 approves with changes; I hold REQUEST-CHANGES confined to the three Mediums because two of them are the
  transcript-basis defect this very range was landed to close, reappearing on the two transcripts it added, and the third is a
  proof sentence that names a test the tree does not hold. The fixes are companions and one row edit.

Verdict unchanged: REQUEST-CHANGES on a58f562..44a24f5 confined to M-1..M-3; the rt39 REQUEST-CHANGES lifted; L-1..L-7 owed.
