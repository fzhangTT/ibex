# Critic verdict: the "flow rt39" group, 557e490..a58f562 (runtime-2, the flow record fixes)

Artifacts (the one commit of the range, a58f562; sha256 first 16 hex of each blob at that commit):
- dv/auto_dv/flow/gen_build.py ffb3f1207c0365db
- dv/auto_dv/flow/gen_cov_report.py b7c03821454af345
- dv/auto_dv/flow/gen_dashboard.py f2d6b65582ecf408
- dv/auto_dv/flow/gen_flow_const.py 62ccbcd99fa37050
- dv/auto_dv/flow/gen_flow_util.py df5894f5dcff0889
- dv/auto_dv/flow/gen_regress.py 9eae962e0012bff0
- dv/auto_dv/flow/gen_round.py cf7213739ed6988f
- dv/auto_dv/flow/gen_run.py 7632eca5b10f840c
- dv/auto_dv/flow/gen_verdict.py 66c3dc5e8f493a70
- dv/auto_dv/docs/gen_rt39_flow_record_fixes_plan.md f3a79e084e570545
- dv/auto_dv/docs/gen_runtime_api.md 4e28d67222ac2cbf
- dv/auto_dv/evidence/gen_critic_response_flow.md 412358fa054272c6
- dv/auto_dv/evidence/gen_tdd_logs/flow/gen_manifest.md 795748c42d0ba442
- dv/auto_dv/evidence/gen_tdd_logs/flow/gen_rt39_reds.log 5b8e268a5a45f5bf
- dv/auto_dv/evidence/gen_tdd_logs/flow/gen_rt37_red.log 42c5b862dd555775

Date: 2026-09-05 (UTC). Role: Critic. Method: the diff read from the committed blobs against the plan v2 at the same
commit and the ruling it works under (LOG-097 addendum 4); the nine flow self-tests, the const check, the three group
figures, the round-0 defines count, the sources-digest count and item five's gzip control re-derived by me on a detached
worktree of a58f562 and on the committed round-0 records; every line number is "file:line at a58f562". Exposure: the
Orchestrator's range message listed rev62's row headings before I read the range; rev62's artifact (acbb40d) was not
read before Sections 1-5 were written and is reconciled in Section 6. Logs: dv/auto_dv/work/critic/rt39/ (selftests.log,
gzip_control.txt).

CRITIC VERDICT: REQUEST-CHANGES (confined to M-1, M-2 and M-3, all records-and-schema: a downstream key that now means two
things across rounds, a re-run transcript whose header names a tree the code is not in, and a plan whose Section 2 the
landing contradicts without saying so; the five mechanisms themselves are approved below).

## 1. What the landing claims and how it was checked

Five items from the plan (one group cell definition and one selector; the build manifest's compile options under names
that say what they are; the dirty-file facts with scope and stamp; the canary identity compared to the round's; a
reproducible retention shape), verified by the landing on a detached worktree with the changed files staged and hashed
on a detached archive, with two retained transcripts. My checks: gen_flow_util, gen_verdict, gen_run, gen_regress,
gen_fcov, gen_mirror, gen_round, gen_build and gen_cov_report self-tests PASS on my worktree of a58f562 (gen_mirror
skipping its mirror_root case and saying so), CONST-CHECK PASS; the mechanisms of Sections 2-4 re-derived from the
committed round-0 records; the transcripts read line by line (Section 5).

## 2. Item one: the group quantities and the selector

Re-derived by me from the committed dv/auto_dv/evidence/gen_round_0/gen_groups.txt through the landing's own
parse_groups and group_quantities: group_bins_gate 85.89 (3477/4048) over 25 covergroups with gen_wit_cycle_clause_cg
(0 of 220) out of both terms; group_bins_all 81.47 (3477/4268) over 26; group_score_weighted 78.29 over 25 with no
ratio. These are the three committed figures and the self-test's COMMITTED case prints the same. The selector
group_cell (gen_cov_report.py:297-306) is the one place both consumers read (gen_round.py:110, gen_dashboard.py:92), the
content-dependent fallback is gone, and the percent always travels with its own ratio and scope string. Its default is
C.GROUP_CELL_FIELD = "group_bins_all" (gen_flow_const.py:567), with the comment that the criterion ruling is suspended
(LOG-097 addendum 4) and the question is recorded rather than answered; that follows the addendum's own instruction
("the DEFINITION held in one place and the stored round-1 figure not restated") and leaves every printed figure equal
to what the round-0 record already shows, so nothing moves under a suspended ruling. Correct as code.

The red. The self-test's WITNESSED case (15/20 against a denominator-only 22/20) and the transcript's control_item1
(3477/4048 against 3484/4048) demonstrate the both-terms rule on the new function; the plan's sentence "Both fail
against the pre-change code" is not what was run, since the pre-change code has no such quantity to fail, and the
plan's first red (the ruled field, ratio and scope identical in the manifest, the round summary and the dashboard row)
has no retained evidence: gen_dashboard has no self-test and gen_round's does not reach metric_row. The Orchestrator's
question is answered in two halves: the red fires the rule it names (denominator-only scoping is what 22/20 and
3484/4048 are), and it is a property demonstration of the landed code, not a failing run of the code it replaces (L-1).

## 3. Item two: the build manifest's compile options, and where the old name survives

compile_config (gen_build.py:252-257) records defines_all and parameters_all from the assembled command and the old
`defines` key is gone from the manifest (:404 spreads compile_config; the self-test asserts its absence). On the
committed round-0 build record the command carries 9 +define+ tokens and 14 -pvalue parameters against the old key's
one token, which I counted from the command text and the self-test prints the same. The builds entry of the regression
manifest carries the new keys (gen_regress.py:84-85). Approved.

The coverage record does not. gen_regress.py:707 writes `cov["build_defines"] = {n: b.get("defines_all") ...}`: the key
that the committed round-0 regression manifest carries as `build_defines: gen_tb: ['+define+RVFI']` (one token, the
entry's group) will carry nine tokens (the compile's full set) in the next round under the same name. That is the
defect the plan names in its own words ("one name would still mean two things", :16-17) re-created one artefact
downstream, and the plan's :113-114 says the downstream copies "carry the new keys" (M-1).

## 4. Items three, four and five

- Dirty-file facts: git_head returns the porcelain list, the scope string and the stamp beside the boolean
  (gen_flow_util.py:219-224); the index entry carries the regression-start reading and the collect-time reading with
  their own scopes and stamps (gen_round.py:286-292); no refusal is added, and the self-test's fabricated repository
  (two modified tracked files, one untracked) names exactly the two, with an older record read without error. Approved.
- Canary identity: canary_build_facts carries the manifest's inputs.sources_sha256 with the scope string
  (gen_flow_util.py:184-185); collect records canary_sources_sha256, round_sources_sha256 and the match
  (gen_round.py:270-277, :285-286). The pre-change defect re-derived by me on the committed index: the round-0 entry
  contains the digest bc0cd7778e382b13 zero times. round_sources takes the first build with a manifest and stops
  (`round_sources or ...`, :274), so a multi-build round compares the canary to one build only (L-2). Approved with L-2.
- Retention: retain_gz shells `gzip -n -c` (gen_round.py:388-396); the collect retains modlist and modinfo compressed
  and counts them (gz_copied). Re-derived by me: the committed gen_modlist.txt.gz and gen_modinfo.txt.gz
  (743b177c1065fddb, a5f939d2115e9693) are reproduced byte for byte by `gzip -n -c` of their decompressed text with the
  site's gzip 1.9, while Python's GzipFile(filename="", mtime=0) gives 7cdfdd943bf151a4 and e36a5747e57f2e09, so the
  plan's Section 6 recipe would have been reproducible and WRONG against the committed archives; the landing changed
  the recipe and the API document says so (gen_runtime_api.md:1065-1071). The committed headers read 1f8b 08 00
  00000000 00 03 (no name, mtime 0). The transcript's control_item5 and the gen_round self-test agree. Approved.

## 5. Records, rows, conformance, verdict

- gen_rt37_red.log states its environment (a detached worktree of 5df6403 plus the nine changed flow files), shows
  green, red and the revert, and explains why the earlier archive transcript was discarded. Its response row says the
  build-input gate's case 13 "reads ok in a worktree and BAD in an archive"; the archive line is not retained, so that
  half rests on prose (L-3). The line it flags as unrelated ("refusing to remove self-test dir .../ci/env.sh: not an
  existing directory (A-002)") is a self-test cleanup handed a file path; the log is right that it confounds nothing
  here, and it is owed a locate (L-4).
- gen_rt39_reds.log is a "live re-run transcript" whose two section headers read "tree 9c7f8f63...", the HEAD of the
  time, which contains none of the rt39 code the scripts exercise (the changed modules were in the working tree); the
  scripts are named by scratchpad path and md5 only and are not in the tree, so the re-run cannot be reproduced from
  the record; and control_item1's output is the only item-one evidence (Section 2). The commit message's "the
  retained logs saying which check ran where" holds for the rt37 transcript and not for this one (M-2).
- The plan document at a58f562 still says "gen_round and gen_dashboard both select group_bins_gate" (:63) and "THE
  RESTATEMENT IS PART OF THIS LANDING ... restates the stored figure as 85.89 (3477/4048)" (:75-79), while the landing
  selects group_bins_all and gen_rounds.yaml is untouched (the range changes no file under gen_round_0 or the index).
  The code is right under LOG-097 addendum 4, which supersedes both sentences; but the plan was edited in this same
  commit (+16 lines) without marking Section 2 as superseded, and no response row records the deviation (M-3). The
  label promise (:72-73, derive "bins >= 80" from the scope string) is likewise unmet at gen_round.py:145 and :346; I
  hold that one at Low because the label is true of the selected quantity (bins) and the scope string travels in the
  row's group_cell (L-5).
- The API document's Section 10 is accurate on every mechanism, including the GzipFile non-reproduction; it does not say
  which field GROUP_CELL_FIELD currently names, so a reader learns the printed quantity from the constants file or the
  dashboard header (part of L-5).
- Manifest rows: gen_rt39_reds.log 4735 bytes / 2eeafa46418bc666095eaaabed5e2190 and gen_rt37_red.log 2138 bytes /
  ba58bbc48d36985e3bfdc9002bc3481c equal the blobs; both ASCII. The rt37 L-2 row is done as stated: gen_run.py:315,
  gen_verdict.py:268-271 and gen_flow_util.py:440 build the signature from C.FCOV_UNMET_REASON.
- Leftovers: `totals = cov.get("totals") or {}` at gen_round.py:95 and gen_dashboard.py:78 is now unused in its
  function (L-6); the gen_build self-test asserts on compile_config's return and never on a written manifest, so the
  spread at :404 is untested (L-7).

Conformance (dv_principles.md): no measurement changes and none is claimed; the records gain names that say what they
hold; the self-tests are green and their controls run on committed bytes; the reds are honest where they are
demonstrations, except that the plan sentence promising reds "against the pre-change code" was not corrected.

- M-1 (Medium, schema; runtime-2). gen_regress.py:707 keeps the coverage record's key `build_defines` and changes its
  population from the entry's group to the compile's full set, so records before and after this landing disagree
  under one name, which is the plan's own definition of the defect (:16-17, :113-114). Fix: a new key
  (build_defines_all beside build_parameters, or build_parameters renamed to match), the old key left absent, and one
  sentence in the API document naming the round from which the new key appears.
- M-2 (Medium, records; runtime-2). gen_rt39_reds.log's headers name tree 9c7f8f6 for code not in that tree, its
  scripts live outside the tree with only md5s recorded, and item one's planned first red has no retained evidence.
  Fix: a corrigendum companion (the log's bytes untouched) stating the worktree and the staged files each section ran
  on, folding the three scripts in, and either retaining the manifest/summary/dashboard identity check or stating that
  it was not run.
- M-3 (Medium, records; runtime-2 with the Orchestrator). The plan's Section 2 promises a selector (group_bins_gate)
  and a restatement (85.89) that the landing does not deliver, because LOG-097 addendum 4 superseded both after the
  plan was approved; the same commit edits the plan and leaves those sentences standing, and no row says so. Fix: a
  dated paragraph in the plan marking :63 and :75-79 superseded by the addendum with the selector actually landed, and
  a response row for the label item (:72-73) saying it was not done.
- L-1 (Low, records). Item one's reds are property demonstrations of the landed code; the plan's "fail against the
  pre-change code" sentence should say so.
- L-2 (Low, code). round_sources compares the canary against the first build with a manifest only (gen_round.py:274).
- L-3 (Low, records). The rt37 response row's "BAD in an archive" half has no retained line.
- L-4 (Low, self-test hygiene). The A-002 refusal line the rt37 transcript flags is a cleanup handed a file path; locate
  and fix or name the case.
- L-5 (Low, records). The label at gen_round.py:145 and the header at :346 stay hardcoded against plan :72-73, and the
  API document does not name the selected field; rev62's grade on this row is reconciled in Section 6.
- L-6 (Low, code). Dead `totals` assignments at gen_round.py:95 and gen_dashboard.py:78.
- L-7 (Low, test). gen_build's self-test never exercises the manifest write at :404.

Verdict: CRITIC VERDICT: REQUEST-CHANGES on 557e490..a58f562, confined to M-1, M-2 and M-3. Approved as they stand: the
three named group quantities and the one selector under the suspended ruling, the build manifest's defines_all and
parameters_all with the old key removed, the dirty-file facts with scope and stamp, the canary identity with its
compare result, and the gzip -n retention shape proven against the committed archives. L-1..L-7 owed as disclosed.
Re-review scope: the M-1 key change and its API sentence, the M-2 companion, the M-3 plan paragraph and rows.

## 6. Reconciliation with the cross-model artifact rev62

Read after Sections 1-5 were written: dv/auto_dv/reviews/2026-09-05-claude-diff-557e490d-a58f5620.md at acbb40d
(claude CLI fallback under A-001; APPROVE-WITH-CHANGES; four Mediums, four Lows). Its verified list re-derives the same
three figures, the same 9-and-14 count, the same zero occurrences of the digest and the same gzip header bytes as
Sections 2-4, and adds one observation I had not made: the eight committed full_exclusions archives carry the
gzip.open shape (FNAME set, wall-clock mtime, OS 255), so the round-0 record holds both shapes side by side, which the
API document's "no committed archive is converted" sentence now describes.

- Its Medium 1 (gen_regress.py:707 build_defines) is my M-1, found independently, same fix.
- Its Medium 2 (the rt39 reds transcript's tree header and the unretained scripts) is my M-2; it adds that the 3484/4048
  figure the plan names "the one to reproduce" is reproducible only through those scripts, the shipped self-test
  reproducing the fabricated 15/20 against 22/20 alone. Adopted into M-2's fix as stated there.
- Its Medium 3 (the plan's Section 2 against the landed selector and the withheld restatement; the API document not
  naming the selected field or the suspension) is my M-3 plus the API half of my L-5; adopted.
- Its Medium 4 (the label and the two headers hardcoded against plan :70-73; no self-test drives metric_row and
  dut_scope_row from one record) is my L-5 and L-1. I hold the label half at Low: the label "bins" is true of the
  selected quantity, the scope string is in the index entry's group_cell, and the addendum-3 sentence it cites ("the
  same string in the summary header and the dashboard") belongs to the suspended ruling. Its identity-test half is
  right and is adopted into L-1: the plan's first red has no retained evidence and no self-test reaches the two row
  functions. Both halves are owed, so the difference is the grade and not the work. On a REQUEST-CHANGES range the
  grade does not gate.
- Its Lows 1, 2 and 4 are my L-2, L-7 and L-6. Its Low 1 cites gen_round.py:262-264; the `round_sources or` line is
  :274 at a58f562 by my read. Its Low 3 (the rt37 excerpt shows neither the case-13 line nor the A-002 line its header
  discusses) is my L-3 and L-4 with a sharper edge: the header discusses two lines the excerpt does not contain;
  adopted into L-3's fix (retain the full transcripts or trim the header to the excerpt).
- On the verdict we agree on every finding and differ on the form: rev62 approves with changes; under my rules three
  Mediums that the landing does not disclose (a schema key changing meaning, a transcript header naming the wrong tree,
  a plan contradicting its own landing) are REQUEST-CHANGES until the companions land. The mechanisms are approved in
  both reviews.
