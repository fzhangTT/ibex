# Critic verdict: the range 813994b..332aa17 as one (tb-infra landing 27 23c9728, Runtime rt33 8f265b2, tb-infra landings 28 a736f94 and 29 332aa17), reviewed as tb_l27

Scope (the Orchestrator's): four working commits judged together: landing 27 (the P6 scope sentence in the WP-8 plan's Section 7); rt33 (the exercising run
retained as gen_l25_fcov_exercised.log: nine PASS, 78 of 78 declared bins hit, build identity b48479a3bc6f1d9f; its header's two-form claim known to rest on
two entries, disclosed by Runtime's corrigendum outside this range); landing 28 (the fcov leg recorded as declared, bound and exercised with the log cited by
path; CM203 Low-1, Low-2, Info-1 and the tool-comment note; gen_build_identity.py's docstring intent-only); landing 29 (gen_norm_probe.py with its self-test;
the construct census marker 30 / 14, scope 23 / 15, guard 1, retired 32 / 16, other 72 / 37; two response rows citing the log). The review artifact aa8b663 and
my tb_l26 (44b336e) in the range are committed-as-written and not judged. The DV Lead's CM203 touch (v4p) is not in the range.

Artifacts reviewed (committed blobs at 332aa17; sha256 first 16 hex):

- dv/auto_dv/docs/gen_wp8_part1_plan.md  834c68452c0efc1e
- dv/auto_dv/evidence/gen_tdd_logs/flow/gen_l25_fcov_exercised.log  55bc5f7e9e578024
- dv/auto_dv/evidence/gen_tdd_logs/flow/gen_manifest.md  9810aa8e0da912b8
- dv/auto_dv/evidence/gen_critic_response_fu2a.md  7f67950a95fb2811
- dv/auto_dv/tools/gen_build_identity.py  6930dc0be8400932
- dv/auto_dv/tools/gen_norm_probe.py  b18912b93f43e7a6
- dv/auto_dv/fcov_expectations/gen_ut_lockstep_icache_ecc.fcov.yaml  657082c3437c3a8a
- the other eight per-entry manifests dv/auto_dv/fcov_expectations/gen_ut_lockstep_icache_ecc_*.fcov.yaml (headers read together)

Date: 2026-09-04 (UTC). Role: Critic (reviewer other than the author). Basis: docs/dv/dv_principles.md d9c27db18f511411; gen_critic_tb_l26.md
(76ccfd59b350d679); dv/auto_dv/flow/gen_run.py:193-205 (the P6 refusal keyed on the measured flag alone); the renderer's loader gen_fcov_codegen.load_plan and
its two coverpoint regexes; the evidence rule (an unretained claim counts as nothing).
Method: detached git worktree of 332aa17 and copies. Landing 28's list (917300ef3ba4, 12 rows) equals its own commit's diff and 12 of 12 md5s verify on an
archive of a736f94; landing 29's list (d56f09ee860b, 2 rows) equals its diff and 2 of 2 md5s verify; rt33's two files match TASKS row 1149 and the log's
manifest row recomputes (8866 bytes, md5 d7ebcb05197e73e1). Gates on the worktree, all PASS: both codegen checks and unit tests, CONST-CHECK, RED-CHECK, the
manifest schema sweep 27 OK 0 FAIL, the flow self-test 155 ok, gen_run 28 ok, gen_covergroup_set on a copy 58 / 4106 / 27 / 0, gen_build_identity.py
--expect b48479a3bc6f1d9f rc 0, gen_norm_probe.py --self-test PASS, a wrong call rc 2, a missing root rc 2. Both identities unchanged across the range
(b48479a3bc6f1d9f over 117 sources; the TB recipe f80e2c719e16b73c): no TB source moved. rt33's log read whole: nine RUN-EXIT 0 in the isolated form, the
shared-root cross-check's nine PASS lines and its summary, the per-entry keyed reading (declared bins 7, 10, 10, 7, 10, 11, 9, 8, 6, sum 78, each agreeing with
Runtime's own parser), the owed-bin table (during_invalidation 10 / 9 / 22 in ecc, tag_two, both; masked_duplicate_copy 4 / 2 / 14 in data, data_two, both,
equal to the plan's local figures), and the section on what the run does not establish. The census reproduced two ways: gen_norm_probe.py run on the
worktree gives retired 32, marker 30 (11 rule-1-alone plus 19 rules-1-and-2), scope 23, guard 1, other 72 over 65 covergroups, and its per-group listing
parsed by me gives the group counts 14 / 15 / 1 / 16 / 37; independently, the renderer's two regexes applied verbatim to the plan at 332aa17 refuse 76
coverpoint and 82 cross bullets, 158 across 65 covergroups, 32 of them RETIRED-marked. The P6 sentence checked against gen_run.py:204 and the self-test
cases 251 and 255 (tb_l26 Section 1). The CM203 rows read against the diffs (the :46 field citation, the committed manifest figures with the intermediate
pair labelled, the nine clause, the docstring without the review id, re-tested rc 0 / 1). No subagent used. EXPOSURE: none beyond the Orchestrator's
message and the git log subjects. Section 6 reconciles with this range's cross-model review; at the time Sections 1-5 were written its artifact was the
wrapper's empty placeholder, and per the Orchestrator's standing instruction this verdict waits for it.

CRITIC VERDICT: APPROVE. The fcov-expectation leg is exercised for the first time with its evidence retained per entry and bin, the P6 scope is stated from
the code, the CM203 rows are answered as stated, and the normalisation probe calls the renderer's own loader and reproduces the plan owner's 158 with a
self-test and wrong-call exits. One low: the log's and the plan's two-form cross-check sentence claims per-bin agreement the retained record does not carry.

## 1. What was verified

| commit | item | evidence (re-derived by me) |
|---|---|---|
| 23c9728 (landing 27) | Section 7: all nine manifests exercisable unmeasured; the refusal keys on the measured flag alone (gen_run.py:193 takes coverage, :204 reads `if measured and debug_only`); zero refusals unmeasured with coverage on, exactly the four probe-carrying entries refused when measured is forced; the probe knob's cost is promotion (_data, _data_two, _both, _far_data) | the code and the gen_run self-test cases; tb_l26's own reading of P6, now the plan's |
| 8f265b2 (Runtime rt33) | gen_l25_fcov_exercised.log: source HEAD 813994b, identity b48479a3bc6f1d9f read against the source root the runs used; the isolated form (one output directory and coverage database per entry) as the source: nine RUN-EXIT 0; the shared-root form's nine PASS and summary as the cross-check; per entry the declared bins read bin by bin against Runtime's own parser of the report with the checker's PASS recorded as a separate fact; the two owed bins collected per entry; "does not establish: that a declared-but-unhit bin fails a run" | the log read whole; 78 = 7 + 10 + 10 + 7 + 10 + 11 + 9 + 8 + 6; the owed figures equal the plan's; the manifest row recomputes |
| a736f94 (landing 28) | Section 7 "DECLARED, BOUND AND EXERCISED" citing the log by path and commit, the per-entry counts, the owed figures reproduced, the failing direction stated as evidenced by the landing-23 reds and unexercised as a flow run; the nine headers cite the log; CM203 Low-1 (the baseline cited by field with :46 and why it moved), Low-2 (the committed manifest figures with the intermediate pair labelled), Info-1 (the count became nine), the tool docstring without the review id (re-tested rc 0 / 1) | the diffs; the field is on :46; the figures equal the committed rows; the docstring read |
| 332aa17 (landing 29) | gen_norm_probe.py: loads gen_fcov_codegen.load_plan from the named tree (the loader is the authority, no copied grammar), lists every bullet the loader captures nothing for, classifies it (retired by intent; marker with rule 1 alone or rules 1 and 2; scope; guard; other), --group, --self-test with a case per construct, exit 2 on a wrong call, Python 3.9-clean; the census at HEAD as the commit states; the CM200-Minor-1 and CM202-Minor-1 rows citing the exercising log at 8f265b2 by path and saying the six owed-bin counts are compared while the 78-count comparison waits for the corrigendum log | the self-test PASS; the census reproduced by the tool and by the verbatim regexes (158 across 65; 32 retired); the group counts 14 / 15 / 1 / 16 / 37 from the tool's own listing |

## 2. Rows

- CR-26-L-1 (the identity tool's proof and self-test): not in this range; Runtime's pending tool touch, as the Orchestrator says.
- CM203 Low-1, Low-2, Info-1 and the tool-comment note: answered as stated. CM203's Medium (the DV Lead's rank clause) is the DV Lead's v4p, not in the range.

## 3. Findings

### L-1 (low) [S6 retention] The two-form cross-check claims per-bin agreement the retained record does not carry

gen_l25_fcov_exercised.log:11-12 says the shared-root form "agreed on all nine verdicts and all 78 bins and is recorded here as a cross-check". Section 2
retains the shared form's nine verdicts and its summary; no section retains a per-bin comparison between the two forms (section 3 is the isolated form's
keyed reading against Runtime's parser, which is a different agreement). The Orchestrator discloses that the per-bin cross-form claim rested on two entries
when the log committed and that Runtime's corrigendum log states so in its next touch, outside this range. The isolated form's 78 figures stand on their
own retained lines, so the leg's evidence is not in question; the cross-check sentence over-claims, and landing 28's Section 7 repeats it ("agreed on
every verdict and every bin, which settles the flow's per-entry isolation by measurement"). DISPOSITION, outside this range: Runtime's rt33b at aaff8f5
retains gen_l25_fcov_exercised_corrigendum.log beside the run log (left byte-identical to 8f265b2), states that the claim rested on two entries of nine when
it committed, and measures it on all nine: 78 declared bins compared, 78 identical in both forms, eighteen reports each holding exactly one test, and the
prefix-glob near-miss that first reported two bins differing recorded as a hazard (read by me at aaff8f5). The row is therefore answered for the log; landing
28's Section 7 still carries the unqualified sentence and tb-infra's next touch cites the corrigendum for it.

### Informational

- I-1: the census figures are definition-exact under two independent routes (the renderer's loader through the probe; the renderer's regexes applied by
  me), which is what tb_l22 L-1 and CM194-L-1 had asked of the plan's earlier counts; the probe's classification (marker / scope / guard / retired / other) is
  the tool's own and I did not re-derive it beyond the totals per construct.
- I-2: the failing direction of the fcov leg (a flow run failing on an unhit declared bin) is stated as unexercised in both the log and the plan; Runtime's
  rt34, if it lands, is the deliberate red for it and the next range's item.
- I-3: the probe's --root default is the clone's working tree, which the docstring warns may hold another role's uncommitted edits (TASKS row 1170 records a
  census of 64 / 32 / 26 / 23 / 1 / 72 on the tree with the DV Lead's four lines uncommitted against 30 / 14 ... at HEAD); the committed record carries the
  HEAD figures, which I reproduced on the detached worktree.

## 4. Principles check

dv-principles-check (docs/dv/dv_principles.md d9c27db18f511411): S6 retention: the exercising run retained per entry and per bin with its identity read
against the source root used (conforming; L-1 on the cross-check sentence). S2 derive from intent: the P6 scope stated from the gate's own clause; the
normalisation probe calls the renderer's loader rather than copying its grammar (conforming). S4 honesty: what the run does not establish is stated in the
log and repeated in the plan (conforming). One-line verdict: PASS with L-1.

## 5. Verdict

CRITIC VERDICT: APPROVE on the range 813994b..332aa17. Low L-1 with Runtime's corrigendum touch and tb-infra's next plan touch. Rows CR-27.

## 6. Reconciliation with the cross-model review of this range

Read after Sections 1-5 were written, as the Orchestrator instructed: dv/auto_dv/reviews/2026-09-04-claude-diff-813994b3-332aa172.md (sha256 a13b705a12f137ae, 48 lines, written by a fresh claude session at 332aa17;
committed as written by the Orchestrator), APPROVE-WITH-CHANGES: one Medium, four Lows, four Infos. Verdicts agree: both approve the range, and every
figure both of us recomputed is equal (the log's bytes and manifest row, the 78 per entry and the union of 13, the P6 evaluation on all nine entries, the
owed bins, the failing-direction citation, the :46 line, the identity tool's controls, the probe's self-test, wrong-call exits, 3.9-cleanness and census
30 / 14, 23 / 15, 1, 32 / 16, 72 / 37 over 158). Its rows, each verified by me on the tree:

- Medium (three rows cite "the GREEN root baseline field (:46)" while line 46 is the UNINITALL root's baseline field and the GREEN root, by the file's own
  convention, carries no baseline pair): verified, lines 31-46. tb_l26 and tb_l27 checked that :46 carries fc376b9db3ad3868 and did not check which root
  owns it; the line and the hash are right, the field owner is wrong in three rows. Missed; adopted.
- Low (the CM202-Minor-1 row says Section 7 "says plainly that no run of these entries through the flow has happened" while Section 7 at HEAD no longer
  does, and asserts the 78-count agreement on the then-uncommitted corrigendum): verified (0 occurrences of the sentence in the plan; the row's assertion
  present). The corrigendum has since landed at aaff8f5 (L-1's disposition), so the assertion's ground now exists outside the range; the row's first
  sentence still contradicts the plan. Missed; adopted.
- Low (read_keyed.py, the parser behind the per-entry "agrees on N" tallies, is not in the tree, and the log retains tallies rather than the 78 per-bin
  counts): verified, 0 tracked matches. The CM202-Low-2 class; the corrigendum at aaff8f5 lists every declared bin with its count (its section 4, 78 rows
  by its own total line), which answers the second half outside the range; the parser itself remains a work file. Missed by tb_l27; adopted.
- Low (gen_norm_probe.py's plan_bullets reads a bullet's first physical line while load_plan joins continuations, so classify tests arity against the
  first line; no marker line wraps today): verified in the code (lines 53-71 take the raw line). The census totals are unaffected, as the reviewer says
  and as my regex count over joined bullets confirms. Missed; adopted.
- Low (REL_PLAN re-typed instead of read from the loaded module): verified (line 30). Missed; adopted.
- Infos (the self-test copies the renderer from the clone and ignores --root; -h exits 2; "Unannotated on purpose" beside PEP 585 annotations; the same
  five-line run-outcome block with the commit SHA pasted into all nine manifest headers; the header sentence "every figure below is from the second" while
  section 2 is the shared form's own verdicts): verified (-h rc 2; parents[3] at 128 and 196; the block in 9 of 9 headers; the sentence at line 9). The
  last is the same over-statement family as my L-1. Adopted.

No corrigendum to Sections 1-5: nothing tb_l27 states is false. It under-found on the response rows' field owner and on the tool's untracked parser, the
classes my own notes name, and on the probe's implementation details, which I had judged by its outputs rather than its code. The verdict on the range
stands as APPROVE; the reviewer's rows are record and tool items for tb-infra and Runtime, and the next range carries them.
