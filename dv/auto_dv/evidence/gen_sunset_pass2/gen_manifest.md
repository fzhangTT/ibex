# Retained runs of the sunset pass-2 reference regression (Runtime, 2026-09-03)

Regression /proj_soc/user_dev/fzhang/ibex_dv_out/probe_t150_979350a: gen_ut_export plus the five T-150 export-observing
entries, one head-mode gen_tb build pinned to 979350aadee1 behind the gen_boot_zc canary on the same sha, six runs PASS,
UVM_ERROR 0; its build manifest (export_rows_observed, 28 of 28 declared rows) is the pass-2 input the DV Lead retains here.
Retained below: the first greens of the gen_ut_export module under the debug-request storm and the delayed scramble-key
regime (stdout verbatim, the run header = run.log verbatim, the verdict = result.yaml fields plus the GEN_RUN_VERDICT line).
Out-tree paths are the shared out root; these copies are the committed record. Columns: evidence path, source, bytes, md5.

| evidence path | source | bytes | md5 |
|---|---|---|---|
| dv/auto_dv/evidence/gen_sunset_pass2/gen_t150_export_dbg_storm_s1_stdout.log | /proj_soc/user_dev/fzhang/ibex_dv_out/probe_t150_979350a/runs/gen_ut_export_dbg_storm_1/sim_stdout.log | 11955 | 3ac85382fbfae5dd105892fee4e1a3d7 |
| dv/auto_dv/evidence/gen_sunset_pass2/gen_t150_export_dbg_storm_s1_run_header.txt | /proj_soc/user_dev/fzhang/ibex_dv_out/probe_t150_979350a/runs/gen_ut_export_dbg_storm_1/run.log | 1117 | 422df4a815968303354bb3b025e43eba |
| dv/auto_dv/evidence/gen_sunset_pass2/gen_t150_export_dbg_storm_s1_verdict.txt | /proj_soc/user_dev/fzhang/ibex_dv_out/probe_t150_979350a/runs/gen_ut_export_dbg_storm_1/result.yaml | 1569 | 4e5b42c346ee2b2fa705d2d880129f3b |
| dv/auto_dv/evidence/gen_sunset_pass2/gen_t150_export_scrkey_delayed_s1_stdout.log | /proj_soc/user_dev/fzhang/ibex_dv_out/probe_t150_979350a/runs/gen_ut_export_scrkey_delayed_1/sim_stdout.log | 11956 | 55ccbacf26bdb176843eeffc10e7c872 |
| dv/auto_dv/evidence/gen_sunset_pass2/gen_t150_export_scrkey_delayed_s1_run_header.txt | /proj_soc/user_dev/fzhang/ibex_dv_out/probe_t150_979350a/runs/gen_ut_export_scrkey_delayed_1/run.log | 1131 | 3cd3abc9466d352962c119d092f57a0d |
| dv/auto_dv/evidence/gen_sunset_pass2/gen_t150_export_scrkey_delayed_s1_verdict.txt | /proj_soc/user_dev/fzhang/ibex_dv_out/probe_t150_979350a/runs/gen_ut_export_scrkey_delayed_1/result.yaml | 1599 | cbc6ae93fb48e048aa3318d3811d354f |
| dv/auto_dv/evidence/gen_sunset_pass2/gen_build_manifest_979350a.yaml | /proj_soc/user_dev/fzhang/ibex_dv_out/probe_t150_979350a/build/gen_tb/build_manifest.yaml | 14508 | 5f921b491e15f7b24f803024a553baf3 |
| dv/auto_dv/evidence/gen_sunset_pass2/gen_token_sunset_released_gated.log | dv/auto_dv/tools/gen_token_sunset.py --build-manifest <that manifest> output, captured by the DV Lead landing script | 10968 | 959a4d5bdddd6d89cf07f60fabc65a2f |
| dv/auto_dv/evidence/gen_sunset_pass2/gen_trace_check_before_after.log | dv/auto_dv/tools/gen_trace_check.py --build-manifest <that manifest> output before and after the removal, captured by the DV Lead landing script | 14958 | db340e53f1ec2dc86f5c38a197b512ea |
| dv/auto_dv/evidence/gen_sunset_pass2/gen_README.md | written by the DV Lead landing script (names LOG-038 and the four files) | 2534 | b76b706ccce8dcf9777a87a70322abd3 |

The four rows above are the DV Lead's pass-2 files (plan v2m, ruling LOG-038): the byte copy of the build manifest named in the
header, the sunset driver's RELEASED / GATED log, the trace tool's before / after output, and the README; from this landing on the
DV Lead is the only writer of this directory (Orchestrator, 2026-09-03).
