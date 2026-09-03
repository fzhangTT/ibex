# Build-input gate for the head-mode canary hold (the rule; revision 2 passed the plan re-review, artifact 67a3f5d, and is implemented in the flow)

## Motivating case (2026-09-03, the batch-3 acceptance wave)

The hold refused the same four purpose-1 requests twice before a chained canary-and-serve attempt got through:

1. 20:54:00Z, canary 0a07536 vs HEAD 1dbb8bf: delta `M dv/auto_dv/docs/gen_intervention_log.md` (nothing a build or run reads).
   Record dv/auto_dv/work/runtime/batches/20260903T205400Z_1dbb8bff28bf.yaml. This refusal was spurious.
2. 20:57Z, canary 1dbb8bf vs HEAD 902da1f: delta `M dv/auto_dv/docs/gen_bug_log.md`, `M dv/auto_dv/docs/gen_fcov_plan.md`,
   `M dv/auto_dv/docs/gen_feature_list.md`, `M dv/auto_dv/docs/gen_test_plan.md`, `M dv/auto_dv/tools/gen_covergroup_set.py`.
   gen_fcov_plan.md is a build input (gen_fcov_codegen.py:24) and both plan documents are run inputs (gen_fcov_manifest.py:43-44), so
   this refusal stands under the rule too; it is listed here because the rule must reproduce it (case 14).
3. 20:57:45Z, canary 3 pinned 902da1f, accepted (record 20260903T205742Z_902da1f693d8.yaml).

At the day's commit rate (a review record or log entry every few minutes) a canary pinned to a HEAD sha loses the race whenever
the intervening commit touches only record documents.

## Rule

The hold keeps its shape: a batch needs the commit a gen_boot_zc canary passed on, the record keeps both shas and the whole mirrored
diff. It DECIDES on the build inputs: the batch is refused when a file that a gen_tb build or a run reads differs between the canary
commit and HEAD, and accepted when every differing file is a record document or a hand-run tool that nothing at build or run time
reads.

Classifier `is_build_input(path)`: default INPUT (an unknown or new file refuses; fail-safe). The non-input set is named file by
file or by a glob that matches files directly under dv/auto_dv/docs only (never a subdirectory):

- tools, file by file (hand-run generators and reviewers; nothing under flow, tb, env, gen_tb, isa, tests or stim imports them):
  dv/auto_dv/tools/gen_covergroup_set.py, gen_promotion_table.py, gen_round_credit.py, gen_plan_holds.py, gen_token_sunset.py,
  gen_cross_review.sh, gen_launch_check.sh. NOT non-inputs: dv/auto_dv/tools/gen_trace_check.py (gen_fcov_manifest.py:45 compiles
  its `segmentable` rule from the source at :96-110, used at :251 / :264 when finish() reaches declare_bins() -> plan_bins) and
  dv/auto_dv/tools/gen_plan_marker.py (imported at gen_fcov_manifest.py:50-51, TOKEN used at :191); a new tools file is INPUT.
- record documents directly under dv/auto_dv/docs: gen_intervention_log.md, gen_bug_log.md, gen_runtime_api.md, gen_dashboard.md,
  gen_build_input_gate_rule.md, gen_component_api_*.md, gen_critic_*.md. Every other docs file is INPUT by default, in particular
  the run-time-read set: gen_trace_witness_ids.csv (gen_flow_util.witness_index, gen_test_lib.py:1123), gen_trace_tp_bin.csv,
  gen_test_plan.md and gen_fcov_plan.md (gen_fcov_manifest.py:42-44, reached at run time through declare_bins; a drift fails the
  run in check_manifest_matches, gen_test_lib.py:902-916, the assert at :912-915), gen_test_template_api.md (gen_test_lib.py:86, :360), and the plan
  companions gen_feature_list.md and gen_trace_feature_tp.csv (INPUT by default, no reader claim needed).

Everything else in the mirrored set is INPUT: rtl/**, vendor/**, util/**, ci/**, *.core, ibex_configs.yaml, python-requirements.txt,
dv/auto_dv/{tb,env,gen_tb,isa,tests,stim,flow,fcov_expectations,excl}/**. The classifier itself lives in dv/auto_dv/flow, which is
INPUT, so editing the non-input list changes HEAD's build inputs and forces a fresh canary before any batch is served on it.

Measured dispatch stays exact-sha and is not touched by this rule: `gen_flow_util.measured_dispatch_refusal` and
`gen_round.check_canary_build` require the canary build to be a head-mode build of exactly the pinned commit (ruling LOG-046a), and
`gen_serve_requests.measured_gate` applies that to purpose-4 requests. So a batch whose canary sha differs from HEAD by non-inputs
only serves its purpose-1..3 requests and still has its purpose-4 requests refused by measured_gate (the record says which rule
refused what). The round-0 dispatch of 2026-09-03 was driven by an ad-hoc shell wrapper that applied a hand-run mirrored-set hold, not by flow
code: the committed record dv/auto_dv/evidence/gen_round_0_probe/gen_dispatch_record.yaml:13-15,26 and gen_README.md:3 (the work-tree
log dv/auto_dv/work/runtime/round_0.log is unmirrored); gen_round.py carries no mirrored-delta rule and none is added.

## Record (batch record fields: the record keeps utc, requests, pinned_sha, canary_sha and delta_pathspecs and gains these)

- `delta`: the deciding subset, the file names from `git diff --name-status <canary> <HEAD> -- <mirrored pathspecs>` that
  is_build_input calls inputs (a rename counts under both names; a failed git command refuses with the error as the one entry);
- `delta_full`: the whole mirrored diff as `git diff --stat=200` (transparency only);
- `noninputs_changed`: the differing files the rule let through;
- `noninput_list_sha256`: sha256 over the classifier's rendered non-input list, so a record states which list decided;
- `decision`: accepted / refused_build_inputs_changed / refused_no_canary_sha as today.

## Red before green (self-test cases on fabricated name lists; no repository history needed except case 14)

Cases 1-11 and 13 run in `gen_flow_util.py --self-test`, cases 12 and 14 in `gen_serve_requests.py --self-test`; the red run
before the implementation (NameError / TypeError on the missing classifier) is kept in dv/auto_dv/work/runtime/gate_rule_red.log.

1.  [dv/auto_dv/docs/gen_intervention_log.md]                      -> accept (case 1 of the motivating set)
2.  [dv/auto_dv/tools/gen_covergroup_set.py]                        -> accept
3.  [dv/auto_dv/docs/gen_test_plan.md]                              -> refuse
4.  [dv/auto_dv/flow/gen_testlist.yaml]                             -> refuse
5.  [rtl/ibex_core.sv]                                              -> refuse
6.  [dv/auto_dv/docs/gen_some_new_doc.md]                           -> refuse (unknown docs file: default INPUT)
7.  [dv/auto_dv/docs/gen_critic_flow_x.md, dv/auto_dv/tools/gen_round_credit.py] -> accept
8.  [dv/auto_dv/docs/gen_intervention_log.md, dv/auto_dv/docs/gen_test_plan.md]
      -> refuse with delta == [gen_test_plan.md] and noninputs_changed == [gen_intervention_log.md]
9.  [dv/auto_dv/tools/gen_trace_check.py]                           -> refuse (the segmentable rule source)
10. [dv/auto_dv/tools/gen_plan_marker.py]                           -> refuse (the marker token)
11. prefix boundaries: [dv/auto_dv/toolsx/y.py] -> refuse; [dv/auto_dv/docs/sub/gen_critic_x.md] -> refuse (globs match files
    directly under docs only); [dv/auto_dv/docs/gen_component_api_fcov.md] -> accept; [dv/auto_dv/docs/gen_critic_sub/x.md] -> refuse
    (a subdirectory whose own name matches the glob: plain fnmatch would let it through, the direct-child match does not)
12. record shape: the return of build_input_delta carries exactly delta, delta_full, noninputs_changed, noninput_list_sha256,
    decision (the batch record keeps its existing keys and adds these); HEAD..HEAD accepts with empty lists
13. existence: every listed non-input file resolves to a tracked file (`git ls-files`), and each glob class matches at least one
    tracked file; a listed name that no longer exists fails the self-test (the list cannot rot silently)
14. real history, guarded (skipped with a printed line when a sha is absent from the clone): 0a07536..1dbb8bf -> accept with
    noninputs_changed == [dv/auto_dv/docs/gen_intervention_log.md]; 1dbb8bf..902da1f -> refuse with delta ==
    [dv/auto_dv/docs/gen_fcov_plan.md, dv/auto_dv/docs/gen_feature_list.md, dv/auto_dv/docs/gen_test_plan.md] and
    noninputs_changed == [dv/auto_dv/docs/gen_bug_log.md, dv/auto_dv/tools/gen_covergroup_set.py]

## Implementation (the flow touch of 2026-09-03 after the revision-2 plan review; the red retained in the self-test)

- gen_flow_const.py: BUILD_INPUT_NONINPUT_TOOLS (file by file), BUILD_INPUT_NONINPUT_DOCS (names) and BUILD_INPUT_NONINPUT_DOC_GLOBS
  (the two globs), with the rule text in the comment.
- gen_flow_util.is_build_input(path), classify_delta(names) -> (inputs, noninputs), noninput_list_sha256() and noninput_list_check()
  (case 13); gen_serve_requests.build_input_delta returns the deciding subset and the record fields above; the hold's log line names
  both lists, and an accepted batch whose canary differs from HEAD in non-inputs logs them.
- gen_runtime_api.md Section 4 (the hold) states the rule and the record fields; the response rows in
  dv/auto_dv/evidence/gen_critic_response_flow.md cite this document, the three work-tree records of the motivating case and the
  committed round-0 record.
- Not changed: the canary stays mandatory; a missing canary sha still refuses; measured dispatch stays exact-sha (above); the build
  manifest's inputs.sources_sha256 stays informational (it covers the filelists' rtl and tb sources only, not tests, stim or flow,
  which is why a git-level classifier over the mirrored set, exact on committed content, is the gate rather than a content digest).
