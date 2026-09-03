# Critic re-review: Runtime flow remediation (T-038, T-042)

Artifacts under review:
- dv/auto_dv/work/runtime/gen_critic_response_flow_v1.md      sha256 520e76ca4aa112d0
- dv/auto_dv/evidence/gen_t038_flow_red_runs.md               sha256 27aa1dd4d552ce39
- dv/auto_dv/flow/*.py, gen_testlist.yaml, dv/auto_dv/docs/gen_runtime_api.md as present in the
  working tree at HEAD 24f3dc0 (per-file hashes at the end of this file)
- Out-tree artifacts under /proj_soc/user_dev/fzhang/ibex_dv_out named in Section 2
Date: 2026-09-03 (UTC)
Role: Critic (dv-principles conformance check, DV_prompt.txt Section 10 honesty rules)
Supersedes: dv/auto_dv/docs/gen_critic_t010_dv_principles_v1.md (REQUEST-CHANGES, P-01..P-10)

CRITIC VERDICT: APPROVE

Every P-01..P-10 finding is addressed with code I read and, where a run was claimed, with a
distinct retained artifact I located and checked for path, stamp and content (Section 2). The one
item still open, the coverage-scope ruling behind P-04, is a DV Lead decision, not a flow defect;
the flow side is done. Residual findings (Section 4) are low or informational and do not hold the
gate. The gate of v1 is lifted.

## 1. Disposition of v1 findings

| Finding | v1 severity | Status | How I verified |
|---|---|---|---|
| P-01 red paths proven only on fabricated lines | high | FIXED | Five real LSF runs on 2026-09-03 06:16Z in <out root>/t038_red/: fatal (FAIL sv_fatal, rc 0, $finish seen), timeout1 (TIMEOUT, rc 124, no sim.log), nomarker (FAIL marker not found), timeout5 and green (PASS). Each has its own sim.log or stdout capture, result.yaml, lsf.out with the LSF job number and host. The self-test pins the fatal, green, timeout, missing-marker and cocotb excerpts as REAL_* cases (gen_verdict.py). UVM_ERROR/UVM_FATAL and assertion red paths are stated as not yet reachable (evidence Section 4); see R-03 |
| P-02 marker substring PASS; exit code and $finish ignored | high | FIXED | gen_verdict.py: marker_matches() requires the marker as the last whole token; decide_lines() FAILs a would-be PASS on a crash signature, on marker without $finish and rc != 0, and on rc outside {0, 124}; sim.log missing without timeout is FAIL. Self-test 20 decide_lines cases plus 5 decide() file cases plus 2 banner checks: PASS when I ran it. gen_runtime_api.md lines 106-121 state the same rule |
| P-03 --waves render crash | medium | FIXED | regress_t027_waves/runs/gen_smoke_330815564/waves.fsdb, 161985 bytes, mtime 05:58:27Z, manifest PASS. The -ucli compile-time rejection is retained in t038_evidence_ucli (build_manifest status failed, error_classes DBG_UCLI_DEP, compile.log line 2, finished 06:26:43Z) |
| P-04 two documents, two coverage scopes | medium | FIXED (flow); ruling PENDING (DV Lead) | builds.<name>.cov_trees is the single source (gen_build.cov_trees/cov_scopes, one +tree per root); build manifests record cov_scopes ['gen_smoke_tb_top.u_dut']. The wrapper-vs-core ruling is with the DV Lead; my recommendation is in Section 5 |
| P-05 -elfile without -excl_strict | medium | FIXED | gen_cov_report.merge(): -excl_strict with every -elfile, -excl_propagation and -excl_bypass_checks refused, UCAPI-ILOAD sets coverage.status exclusion_violation and gen_regress.py exits 3. Retained pair: regress_t010_r5_violation (status exclusion_violation, 05:47:00Z) and regress_t010_r5_ok (status ok, 05:47:13Z). The -excl_embed dispute is accepted: the merged vdb is regenerated each round |
| P-06 constants check never called; names re-typed | medium | FIXED | require_sv_constants() is the first call in gen_build.py:197, gen_run.py:161, gen_regress.py:309; load_testlist() refuses a plusarg that is neither a PLUSARG_* of gen_tb_pkg.sv nor a simulator plusarg (gen_flow_util.py:285-287); gen_flow_const.py --check PASS when I ran it |
| P-07 null fcov manifest silently exempt | medium | FIXED | summarize() counts runs_without_fcov_manifest and names the tests; fcov_manifest_required_tiers header policy FAILs a null manifest on the named tiers; gen_regress.py --self-test PASS; regress_t038_check2 summary shows runs_without_fcov_manifest 2 |
| P-08 compiler_version regex | low | FIXED | build manifests record compiler_version X-2025.06-SP2_Full64 |
| P-09 banner not required | low | FIXED | scan_log() raises without a build_config and FAILs without the sim.log banner line; the banner block is copied into result.yaml (seen in all five t038_red results) |
| P-10 out root fallback only warned | low | FIXED | gen_regress.py refuses a local out root without --allow-local-out-root; manifests record out_root, out_root_fs (wekafs from regress_t038_check2 on; the earlier check run holds the raw magic, as stated) and site_yaml; dv/auto_dv/flow/gen_site.yaml.example exists with the setup step in API Section 0 |
| A-24 RTL-root override for mutation builds | (T-011 item) | FIXED, unexercised | gen_build.py absolutize_filelist() substitutes listed sources under --rtl-root, dies on leftovers or on no substitution; gen_regress.py forces every mutation run unmeasured and refuses --purpose 4. First use comes with the Test Writer; evidence then |
| P6 debug-only CSR-flop probe never in a measured run | (T-011 item) | FIXED | gen_run.py:201-208 refuses in writing; retained run regress_t045_p6_refusal (06:42:18Z): result.yaml NOT_RUN with the reason, lsf null (no job submitted), manifest not_run 1 |
| R-01 gen_smoke in tier smoke contradicts its contract | (T-029 residual) | FIXED | tier check (CHECK_TIER) selectable only by name or --tier check; load_testlist() requires measured: false on it; gen_smoke and gen_cocotb_probe are tier check, measured false; regress_t038_check ran both (coverage status ok_no_measured_tests) |

## 2. Evidence audit (distinct retained artifact per claimed run)

Rule: each claimed run maps to its own artifact whose path, mtime and in-log stamp agree with the
claim; identical content across two claimed runs is a red flag. Local times are -0400.

| Claimed run | Artifact | LSF job / host (lsf.out) | sim.log md5 / mtime | In-log stamp and identifying content | Result |
|---|---|---|---|---|---|
| fatal | t038_red/fatal | 10930762 / soc-c-10 | 0a5f5234 / 02:16:24.7 | Command line names t038_red/fatal/sim.log and +gen_smoke_cycles=1; VCS stamp Sep 3 02:16; lines 18-23 identical to the evidence excerpt | consistent |
| timeout1 | t038_red/timeout1 | 10930764 / soc-c-05 | no sim.log; sim_stdout.log 295 bytes 02:16:24.4 | lsf.out GEN_RUN_EXIT rc=124, Subject Exited; exit_code file 124 | consistent |
| timeout5 (control) | t038_red/timeout5 | 10930761 / soc-c-20 | 552c124a / 02:16:24.8 | Command names timeout5; +gen_smoke_cycles=3000 | consistent |
| nomarker | t038_red/nomarker | 10930763 / soc-c-03 | 43ab3a08 / 02:16:24.9 | Command names nomarker; result reason names GEN_NEVER_PRINTED | consistent |
| green (control) | t038_red/green | 10930765 / soc-c-20 | 79ef3840 / 02:16:29.7 | submitted 02:16:24, after the other four (02:16:19); Command names green | consistent |
| discarded first attempt | none | 10930753-10930756 named in evidence Section 5 | overwritten | stated as unretained, LOG-005 standard | acceptable |
| P6 refusal | regress_t045_p6_refusal | none submitted (lsf null) | n/a | result.yaml NOT_RUN, reason quotes the knob; manifest finished 06:42:18Z | consistent; see R-01 |
| waves | regress_t027_waves | 10930446 (manifest) | waves.fsdb 161985 bytes 05:58:27Z | manifest PASS 05:58:29Z | consistent |
| -ucli rejection | t038_evidence_ucli | build only | compile.log line 2 Error-[DBG_UCLI_DEP] | build_manifest status failed 06:26:43Z | consistent |
| strict-load pair | regress_t010_r5_violation, regress_t010_r5_ok | (T-010) | cov status exclusion_violation / ok | manifests 05:47:00Z / 05:47:13Z | consistent |
| check-tier runs | regress_t038_check, regress_t038_check2 | jobs per manifest | both PASS, measured false | 06:22:26Z / 06:28:09Z; check2 records out_root_fs wekafs and mirror tree hash | consistent |

All five t038_red logs differ from one another in content and path. Hosts and job numbers match the
evidence table. The audit passes.

## 3. Rule verification by code reading

- PASS = no collected mechanism AND marker (or $finish when the test has none) AND the sim.log
  banner for the expected build configuration AND ($finish seen OR rc 0) AND rc in {0, 124} AND
  no crash line in lsf.err/run.log/sim_stdout.log AND no LSF kill reason (gen_run.py:257-258).
  A missing exit-code file (rc None) with $finish seen FAILs as an unexplained exit code. Correct.
- Timeout: rc 124 or the LSF deadline kill sets timed_out; TIMEOUT wins over any log content.
- FAIL_PATTERNS cover UVM_FATAL/UVM_ERROR message and summary lines, SV $fatal (Fatal:), the TB's
  GEN_*_FAIL markers, VCS Error-[ and Error: lines (so a $error from a bound T022_NEVER_* property
  is a collected failure, which is what my exclusion ruling N-4 needs), cocotb CRITICAL and failing
  summaries, and SVA Offending lines. A cocotb summary with zero passed tests is a failure. Good.
- Refusals in writing: --pass-marker on a measured run (gen_run.py:197), unmeasured run into the
  build vdb (:191), debug-only plusarg in a measured coverage run (:201-208), local out root for a
  non-local regression (gen_regress.py:314), mutation build under purpose 4 (:312), unknown plusarg
  names and check-tier tests with measured: true (load_testlist). build_vcs_args accepted under
  purpose 2 only (gen_serve_requests.py:151-156).
- Self-tests: gen_flow_const.py --check, gen_flow_util.py --self-test, gen_verdict.py --self-test
  and gen_regress.py --self-test all PASS when I ran them from a sourced environment.

## 4. Residual findings (none blocks)

R-01 (low, provenance). Regression manifests do not record the testlist they ran: no testlist path
or sha256 among the manifest keys (checked regress_t045_p6_refusal and regress_t038_check2). The
P6 refusal run used a temporary testlist that is not retained in its outdir, so the run cannot be
reproduced from the manifest alone. Required change: record testlist path and sha256 in every
regression and run manifest, and copy a non-default testlist into the outdir.

R-02 (low, retention). t038_red/refuse_covdir/ is empty: the local refusal test for the unmeasured
cov-dir rule left no output. Capture the refusal's stdout/stderr into that directory or state in
the response that the check is unretained.

R-03 (low, wording). The self-test's fabricated format cases (uvm error count, uvm error line, vcs
runtime error, cocotb fail summary, cocotb critical) are not marked as fabricated by name; the
evidence Section 4 says they are "marked as such by their names". Prefix them "fabricated:" (the
real ones already say "real") so the sentence is true, and replace each with a real excerpt when
the UVM top and the first DUT assertion trigger exist.

R-04 (info). Self-test counts differ across documents: evidence Section 3 says 20 cases, the
response says 25, the run prints 20 decide_lines cases plus 5 decide() cases plus 2 banner checks.
Harmless; align on the next edit.

R-05 (info). A-24 and the mutation path are code-only until the Test Writer's first mutation build;
the first such run must retain a build manifest with rtl_substitutions (original and mutated
sha256) and an unmeasured vdb, and I will audit it then.

R-06 (info). -cm_glitch 0, if the DV Lead adopts it (LOG-007), goes into builds.<name>.extra_vcs_args
so measured builds carry it in compile_cmd.sh and the manifest, not through --build-vcs-arg, which
is a purpose-2 trial mechanism by design.

## 5. Recommendation on the pending P-04 ruling (for the DV Lead)

gen_dut_top is DV-authored wrapper glue (the CHERIoT tie, port adaptation), not DUT RTL.
DV_prompt.txt Section 4 scopes coverage to the DUT hierarchy, so the measured trees should be
u_dut.u_ibex_core and u_dut.u_register_file, which removes the wrapper's 312 toggle objects from
the denominator without touching a single DUT object. The flow already supports two roots
(cov_trees). Whatever the ruling, it must be recorded before the round-0 baseline is re-measured,
and every report must state the scope.

## 6. Fence and method record

Inputs: the two artifacts above, the flow sources and API document in the working tree, the out
root manifests, logs and reports named in Section 2, and the two cross-model review artifacts in
dv/auto_dv/reviews/ (read to avoid duplicating their findings; their APPROVE-WITH-CHANGES minors
are marked FIXED in the response and I re-verified the retained ones). No LSF command was issued
by me; job numbers and hosts come from the retained lsf.out files. No fenced content was read.

## File hashes at review time (sha256, first 16 hex)
- 3feb59fcefb07729  dv/auto_dv/flow/gen_verdict.py
- b07192f996320da4  dv/auto_dv/flow/gen_run.py
- 0357bdbf40e95ff1  dv/auto_dv/flow/gen_regress.py
- 315b0d2970aceddc  dv/auto_dv/flow/gen_build.py
- 30f276a4daf43816  dv/auto_dv/flow/gen_cov_report.py
- fa69bf9ee99deefb  dv/auto_dv/flow/gen_flow_util.py
- 26ec7c169bb7b2eb  dv/auto_dv/flow/gen_flow_const.py
- 4fe4848156e23b7d  dv/auto_dv/flow/gen_serve_requests.py
- eb9e0ff3b00100c3  dv/auto_dv/flow/gen_testlist.yaml
- aec8d5234ad0211b  dv/auto_dv/docs/gen_runtime_api.md

Note: at review time the working tree carried uncommitted Runtime edits to gen_flow_const.py and
gen_dashboard.py and an untracked gen_round.py (git status). The hashes above are of the working
tree; the committed state at HEAD 24f3dc0 differs for those two files. The rules verified in
Section 3 were read from the working tree and re-checked by the self-tests, which passed.
