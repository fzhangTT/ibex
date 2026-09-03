# Build-input gate for the head-mode canary hold (rule proposal, pre-execution review requested)

Motivating case (2026-09-03, batch-3 acceptance): the hold refused the same four requests twice while nothing a
build or run reads had changed: 20:54:00Z canary 0a07536 vs HEAD 1dbb8bf (delta dv/auto_dv/docs/gen_intervention_log.md);
20:57Z canary 1dbb8bf vs HEAD 902da1f (delta dv/auto_dv/docs/gen_test_plan.md, dv/auto_dv/tools/gen_covergroup_set.py,
review records). Records: dv/auto_dv/work/runtime/batches/20260903T205400Z_1dbb8bff28bf.yaml and the chained third
attempt 20260903T205742Z_902da1f693d8.yaml. At today's commit rate (a review record or log entry every few minutes) a
canary pinned to a HEAD sha loses the race more often than it wins.

## Rule

The hold keeps its shape (a batch needs the commit a gen_boot_zc canary passed on; the record keeps both shas and the
full mirrored diff) but DECIDES on the build inputs only: the batch is refused when a file that a gen_tb build or a
run reads differs between the canary commit and HEAD, and accepted when the delta consists only of record documents
and analysis tools that nothing in a build or run consumes.

Classifier `is_build_input(path)`, default INPUT (an unknown file refuses; fail-safe), with the non-input set named
explicitly:
- dv/auto_dv/tools/** (analysis and generation tools run by hand; no build or run imports them);
- dv/auto_dv/docs/gen_intervention_log.md, gen_bug_log.md, gen_runtime_api.md, gen_dashboard.md,
  gen_component_api_*.md, gen_critic_*.md, gen_hierarchy_map.md, gen_param_resolution.md (record and reference
  documents; nothing under flow, tb, env, gen_tb, isa, tests or stim opens them).
Everything else in the mirrored set stays an input, in particular: rtl/**, vendor/**, util/**, ci/**, *.core,
ibex_configs.yaml, python-requirements.txt, dv/auto_dv/{tb,env,gen_tb,isa,tests,stim,flow,fcov_expectations,excl}/**,
and the docs files the test library or the flow read at run time: dv/auto_dv/docs/gen_trace_witness_ids.csv
(gen_flow_util.witness_index, gen_test_lib), gen_trace_tp_bin.csv, gen_test_plan.md and gen_fcov_plan.md
(gen_fcov_manifest, imported by the test library). So the 902da1f refusal stays a refusal under this rule (the plan
changed); the 1dbb8bf refusal (intervention log only) becomes an acceptance.

## Red before green (self-test cases, all on fabricated name lists, no repository history needed)

1. delta = [dv/auto_dv/docs/gen_intervention_log.md]           -> no refusal (build_input_delta empty)   # today's case 1
2. delta = [dv/auto_dv/tools/gen_covergroup_set.py]             -> no refusal
3. delta = [dv/auto_dv/docs/gen_test_plan.md]                   -> refusal (the library reads the plan)  # today's case 2
4. delta = [dv/auto_dv/flow/gen_testlist.yaml]                  -> refusal
5. delta = [rtl/ibex_core.sv]                                   -> refusal
6. delta = [dv/auto_dv/docs/gen_some_new_doc.md]                -> refusal (unknown docs file: default INPUT)
7. delta = [dv/auto_dv/docs/gen_critic_flow_x.md, dv/auto_dv/tools/y.py] -> no refusal (all non-inputs)
8. one real-history check when both shas exist in the clone: build_input_delta(0a07536, 1dbb8bf) == "" and
   build_input_delta(1dbb8bf, 902da1f) != "" (guarded: skipped with a printed line when a sha is absent).

## Implementation sketch (one flow touch, after this review)

- gen_flow_const.py: BUILD_INPUT_NONINPUT_DIRS = ("dv/auto_dv/tools",), BUILD_INPUT_NONINPUT_DOCS = (the list above,
  glob-capable), with the rule text in the comment.
- gen_flow_util.is_build_input(path) and gen_serve_requests.build_input_delta(sha_a, sha_b): `git diff --name-only`
  over the mirrored pathspecs, filtered by the classifier; the returned delta text names only the build-input files
  (stat form) and the batch record gains `delta_full` (the whole mirrored diff, kept for transparency) beside `delta`
  (the deciding subset) and `noninputs_changed` (the list the rule let through).
- The round-0 dispatch wrapper's mirrored-delta rule (gen_round pre-dispatch, LOG-042d) uses the same classifier.
- gen_runtime_api.md Section 4 (the hold), a CM row citing this file and the two refusal records; STATUS.
- Not changed: the canary itself stays mandatory; a missing canary sha still refuses; the digest facts in the build
  manifest (inputs.sources_sha256 over the filelists) stay informational because they cover rtl and tb only, not
  tests, stim or flow, so a git-level classifier over the mirrored set is the precise gate.
