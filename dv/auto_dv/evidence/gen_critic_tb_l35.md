# Critic verdict: the range 1deec4c..df1d8c5 (LOG-086 with its addendum and corrigendum, tb-infra-2's landing 37 and 37b, runtime-2's rt35c and nine-entry detach, the DV Lead's v4t; 20b3a4e and 050ef63 committed as written), reviewed as tb_l35

Scope (the Orchestrator's): ten commits judged together, 26 files, 1001 insertions, 177 deletions, nothing under rtl/: 20b3a4e (the cross-model
review of the previous range, as written), a69e285 + 8b22572 + 3db4dde (owner-log LOG-086: nine entries detached from fcov manifests whose bins sit on
unbuilt covergroups, the measured split eight checked plus seven counted-only, 1836 plan-referenced bins withdrawn of which 1101 on built
covergroups), bc4eba8 (tb-infra-2's landing 37: the icache-ECC tag-half end-of-run allowance in gen_checkers_pkg.sv with a two-sided red, plus the
age17 and landing-36 corrigendum logs), 050ef63 (tb_l34, as written), ede678c (runtime-2's rt35c: two corrigendum logs, the gen_read_keyed reset
set, gen_compare_forms --entries, an API paragraph, eight response rows), 35ed0d4 (the DV Lead's v4t, records-only corrigenda re-based on 20b3a4e),
18ac053 (runtime-2's nine-entry detach), df1d8c5 (tb-infra-2's landing 37b: the supplement for the landing-36 log, after the committed corrigendum
was restored to its bc4eba8 bytes; INCIDENT rows 19:33:49Z and 19:58:37Z in the Orchestrator's task list). The range closed at df1d8c5; its
cross-model review launched at 19:59Z.

Artifacts reviewed (committed blobs at the commit named; sha256 first 16 hex):

- dv/auto_dv/docs/gen_intervention_log.md @3db4dde  65a5bdcb7cf7cb6a
- dv/auto_dv/env/gen_checkers_pkg.sv @bc4eba8  f63ca8aaa92dc627
- dv/auto_dv/evidence/gen_tdd_logs/mutations/gen_fu_l37_tag_eor_unconsumed.log @bc4eba8  42851fd5fc7e82c8
- dv/auto_dv/evidence/gen_tdd_logs/mutations/gen_fu_l33_age17_attempt_corrigendum.log @bc4eba8  075130dbb5386ab0
- dv/auto_dv/evidence/gen_tdd_logs/mutations/gen_fu_l36_dbg_driver_livelock_corrigendum.log @bc4eba8  9656a9ad8b2896c8
- dv/auto_dv/evidence/gen_tdd_logs/mutations/gen_fu_l36_dbg_driver_livelock_supplement.log @df1d8c5  c803a9695257b3ac
- dv/auto_dv/evidence/gen_tdd_logs/gen_manifest.md @df1d8c5  182cd451c28c318f
- dv/auto_dv/evidence/gen_tdd_step2b.md @df1d8c5  657e3338e050a426
- dv/auto_dv/tools/gen_read_keyed.py @ede678c  e2db8c7ed95425c1
- dv/auto_dv/tools/gen_compare_forms.py @ede678c  b1353d77256c8073
- dv/auto_dv/flow/gen_run.py @ede678c  ad3e464a39b45635
- dv/auto_dv/docs/gen_runtime_api.md @ede678c  b11bee39b4431c97
- dv/auto_dv/evidence/gen_critic_response_flow.md @ede678c  1c2b7bf985ed5b90
- dv/auto_dv/evidence/gen_tdd_logs/flow/gen_rt35_supplement_corrigendum.log @ede678c  df4bf6b600736ba5
- dv/auto_dv/evidence/gen_tdd_logs/flow/gen_fu_guard_fcov_red_corrigendum.log @ede678c  ea04cb7806368ab6
- dv/auto_dv/evidence/gen_tdd_logs/flow/gen_manifest.md @ede678c  93de3fe707b11eaf
- dv/auto_dv/docs/gen_test_plan.md @35ed0d4  9e73d4f83aec3e0b
- dv/auto_dv/evidence/gen_round0_covergroup_set.csv @35ed0d4  8f0c856c46d20037
- dv/auto_dv/evidence/gen_round0_promotion_table.md @35ed0d4  0ee05de41a453fe8
- dv/auto_dv/evidence/gen_round0_credit/gen_round0_credit.md @35ed0d4  7750dcef2b494422
- dv/auto_dv/evidence/gen_critic_response_plan_set_v1.md @35ed0d4  8834faace87c7212
- dv/auto_dv/flow/gen_testlist.yaml @18ac053  6722f0c806333b29

Date: 2026-09-04 (UTC). Role: Critic (reviewer other than the author). Basis: docs/dv/dv_principles.md d9c27db18f511411; gen_critic_tb_l34.md
(f3c3f10cda7ca704); the CM212 rows (artifact 20b3a4e) and my CR-34 rows that landings 37 and 37b answer; the CM210/CM211 rows and my CR-33 rows that
rt35c answers; the RTL-facts rule (every gating term quoted before a behaviour is stated) applied to a TB rule about the DUT; the retained-header
rule; the mutation-proof standard (baseline and mutated hashes, the applied diff retained, an ablation); LOG-085 and LOG-086.
Method: detached git worktree of df1d8c5 (the gate: both codegen --check up to date, three UTs PASS, CONST, RED-CHECK PASS, validate 28 OK, TBMAN 3479
rows 0 bad; flow build identity 6a1d73dfb815cfc7 over 117 sources for gen_tb, 273622bb3b90ed9d over 95 for the smoke builds; my TB-source recipe
50981c82f49d7574, unchanged from bc4eba8 since no later commit touches env, tb, isa or gen_tb). Every figure of every retained log in the range
re-derived from the committed blobs, the out-tree dry run, or the authors' scratch roots (tb-infra-2's tag_root, tagfix_root, tagmut_root,
tohost_root, drv_root; read on disk). Loader and manifest counts through the flow's own loader and the checker's own parser on detached archives
of 18ac053, 35ed0d4 and 8b22572; the plan-referenced set through gen_covergroup_set.py on the 18ac053 archive; the v4t records regenerated from
their recorded invocations. The landing-37 rule tested by a PROBE RUN of my own: a scratch copy of 92c0850 (the FAIL side) with two $display
additions and nothing else (diff retained at scratchpad l35/probe.diff, sha256 2e35e81f8ee150e0; compile digest 952d58bc9e92e999; stdout at
scratchpad l35/probe_stdout.log), which reproduces the failing seed's figures exactly and prints the icache lookup terms per cycle. EXPOSURE: the
Orchestrator's messages; the authors' scratch roots and the task list's rows; the out-tree. No subagent used. Section 6 reconciles with the
range's cross-model review when its artifact lands (none exists yet).

CRITIC VERDICT: REQUEST-CHANGES, confined to landing 37 (bc4eba8): the tag-half end-of-run allowance is justified by a DUT behaviour the RTL does
not have, and its predicate is a proxy for the condition the failing seed actually has. Every figure of the landing reproduces and its two-sided
red is real; what is wrong is the rule's premise and the retained statements of it (M-1). Every other commit in the range is verified and
approved as written: LOG-086's figures reproduce in both of their universes, rt35c answers CR-33 L-1/L-2 and eight review rows with reproducible
evidence, the nine-entry detach is byte-exact outside its two fields per entry, v4t's records regenerate byte-identically, and landing 37b
answers CR-34 L-1/L-2 (with one count that does not reproduce, L-3). Three Lows.

## 1. What was verified

| commit | item | evidence (re-derived by me) |
|---|---|---|
| 20b3a4e | the cross-model artifact of b105c09..1deec4c committed as written | identity header, TARGET echo, Final verdict line; reconciled in tb_l34 Section 6 (blob 7f5e6ba6a259ee0f) |
| a69e285, 8b22572, 3db4dde (LOG-086) | seven then nine entries detached for round 1: gen_test_pmp_csr_warl 266/266, gen_test_bit_ratified 176/830, gen_test_csr_access 76/80, gen_test_csr_reset 68/68, gen_test_csr_trap_setup 17/168, gen_test_bit_draft 15/15, gen_test_cmp_zca 13/337, gen_test_pmp_mseccfg 77/77, gen_test_pmp_lock 50/50; 631 of 3838 measured, 758 over 27 manifest-naming entries; the corrigendum: measured 15 = 8 checked + 7 counted-only; 3902 -> 2066 plan-referenced bins (735 unbuilt, 1101 on built) | the checker's own parser (ci/check_fcov_expectations.parse_manifest) over the 27 manifests the loader names on the 8b22572 archive against the 25 covergroup declarations in gen_fcov_groups.svh: every per-entry figure, 758 of 4044, 631 of 3838, nine entries; on the 18ac053 archive measured 15 = 8 + 7; gen_covergroup_set.py on the 18ac053 archive: 20 covergroups, 2066 referenced bins, 18 manifests against v4t's 50 / 3902 / 27, the withdrawal 1101 on the 25 rendered covergroups and 735 on unrendered ones. Two universes, both exact: the manifests' declared bins over the nine (1891 = 758 unbuilt + 1133 built) and the plan's referenced set (1836 = 735 + 1101) |
| bc4eba8 (tb-infra-2 landing 37) | the failing seed 508609593 of gen_ut_lockstep_icache_ecc_tag_two: last retirement 21478, injection at 21479 way 1 index 28, finish_req 21433, index 28 retired 18 times with the last at 21478 pc 800000e4; the fix: a qualified tag injection with no retirement at or after its cycle deferred in-run and counted unconsumed at report_phase; side A: FAIL -> PASS, 906/894/0/1 at the seed and 944/935/0/0 at seed 1; side B: MUT-ALERTSUP 875 misses first at cycle 862 with unconsumed 1, ablation 0 | the repro root (base 92c0850, digest f8087204d5d26cc3 = my recipe over 962d31f, the recipe set unchanged to 92c0850): export 16024 records, last retirement 21478, 18 index-28 retirements ending at 21478 pc 800000e4 (index = pc bits 10:3), the missing line at 21479, finish_req 21433; the fixed root (digest 50981c82f49d7574 = my recipe over the COMMITTED bc4eba8 sources) 906/894/0/1 UVM_ERROR 0 and 944/935/0/0 UVM_ERROR 0; the mutated root: gen_tb_top.sv 736a8d8099339024 (= the 1deec4c blob) -> 85b50e1343c65af1 by three lines (a mutsup_at plusarg; alert_minor forced low once evt_retired_count >= mutsup_at), checker blob = bc4eba8, recipe 46f6e1dfdddebb10 as logged, 875 errors first at 862 way 1 index 25, unconsumed 1; ablation UVM_ERROR 0, 906/894/0/1. The code read term by term (close_owed :741-752, report_phase :768-786, rt_cyc :350/:416/:419). The RULE'S PREMISE tested: see M-1 |
| bc4eba8 | gen_fu_l33_age17_attempt_corrigendum.log (CM211-Low-4, CR-33 L-3): DISTINCT OUTCOMES 25 = distinct finish records per onset over 47 onsets in 52 rows; row-keyed 29; the reviewer's 27 not reproduced | the 52 doldi rows of the retained gen_fu_l33_age17_attempt.log parsed: 47 distinct onsets; keyed by onset every variant (six fields, six plus fired_at, finish alone, records alone, fired_at alone) gives 25; keyed by row every variant gives 29; no keying tried gives 27 |
| bc4eba8 | gen_fu_l36_dbg_driver_livelock_corrigendum.log (OR-36-1, CM212 Low-1/Low-2/Info-3, CR-34 L-1 in part): three roots by git head with the three SV files' sha256 before and after; severity lines 0/0/2; the command-claim scoped; the exit lag | before = the 962d31f and b105c09 blobs (gen_bridge_if.sv 8102a0f2199ee1be, gen_rvfi_pkg.sv a95a7fb5318c2b2c, gen_agents_pkg.sv d3f0672de0a270fd), after = the 1deec4c blobs (16aa4c868f79fbb2, f41f8c8cde61b5ad, 217c3910142dd3a0), md5s equal; digests f8087204d5d26cc3 and 1a7de65f7001a0fa equal my recipe values; gen_tb_local.sh:37 and :55 as quoted; severity lines 0 / 0 / 2 and report summaries 0 / 0 / 1 on tohost_root/out/old, out/new2 and drv_root/out/fixed |
| bc4eba8 | three manifest rows | gen_fu_l33_age17_attempt_corrigendum.log 2809 / acc3f35784fddf3d, gen_fu_l36_dbg_driver_livelock_corrigendum.log 6162 / cb593f105976d28f, gen_fu_l37_tag_eor_unconsumed.log 5426 / ca11e5107b3e171f: sizes and md5s equal the blobs |
| 050ef63 | tb_l34 committed as written | content f3c3f10cda7ca704 = the handed hash, 148 lines |
| ede678c (runtime-2 rt35c) | gen_read_keyed.parse_report resets on all four checker alternatives (Excluded/Illegal bins, Summary for, Variables for, ten-plus dashes or equals) with a RESET_FIXTURE self-test case; gen_compare_forms --entries required, DEFAULT_ENTRIES removed; the gen_run history comment dropped | on the 35ed0d4 archive: gen_read_keyed --self-test 7 ok 0 BAD; a fault restoring the old two-alternative regex turns exactly the new case BAD (the checker's reset set at ci/check_fcov_expectations.py:87 compared pattern by pattern); gen_compare_forms --self-test PASS rc 0, a compare call without --entries rc 2 with the named message; the CM210-Low-5 derivation reproduced: ten entries name a gen_ic_ecc_cg bin at ede678c, the tenth the standing guard; gen_run.py differs in one comment line |
| ede678c | gen_rt35_supplement_corrigendum.log (CM211-Low-1, CM211-Info-1, CR-33 L-1/L-2): RED 3 = deleting gen_run.py:166-168 at e988ee6, 6d20a0b5dc32 / 513 lines -> b0efb4372941 / 510; complete BAD counts 3 / 1 / 3; gen_regress.py 762 lines 5c9869bbe078 | all re-derived on the e988ee6 blobs; the 3 / 1 / 3 are the counts I measured for tb_l33 Section 6; manifest row 8583 / 0d79e9d5372c5017 |
| ede678c | gen_fu_guard_fcov_red_corrigendum.log (CM211-Low-2, CM211-Info-2): not_run summed into bad (gen_regress.py:754, exit 2 at :758); the guard check-tier, measured false, manifest-naming; a coverage-off check-tier regression exits 2 on it; RULED to stay so (task list 19:22:24Z); a round passes neither --no-coverage nor --repro and the coverage flag is their conjunction, so the guard grades RED-OK in a round; the build-input figure pinned: 30/2 vs d8f5d99 and c8821a9, 30/3 vs 71c1c70, 32/3 vs 962d31f, 34/3 vs b105c09 | :754 and :758 as quoted at ede678c; gen_round.py has zero occurrences of either flag; gen_regress.py:615 coverage = not a.no_coverage and not a.repro; the RULING row present; gen_serve_requests.build_input_delta from 813994b3d483 gives 30/2, 30/2, 30/3, 32/3, 34/3; manifest row 6344 / 264f58f704cf4012. This closes the NOT_RUN flag I raised in tb_l33 |
| ede678c | gen_runtime_api.md: where a verdict is read from (manifest or per-seed result.yaml, never the driver log) | matches post_fcov_checks (gen_regress.py:156-163) and the dry run's pmc seed (result.yaml FAIL / UNHIT, driver.log PASS) verified in tb_l34 |
| 35ed0d4 (DV Lead v4t) | records-only corrigenda: the NMI figures over distinct summaries (1654 / 4, CM210-Info-1), the cap clause folded to landing 35 (202 at the defaults, bound plus one plus margin 40), the early-drain-end row, CM210-Low-4 three pairs, the credit, covergroup set and promotion table regenerated with --plan-sha v4t-on-20b3a4e | the three record sets regenerate byte-identically from their recorded invocations on a 35ed0d4 archive (credit e17bc5bd3259e30a / 7750dcef2b494422 / 551b62bc73447a5e; covergroup set 8f0c856c46d20037 / 3dcb1bf0cb29804c; promotion table 0ee05de41a453fe8) with the recorded input digests 9e73d4f83aec and 203732c47eb2 equal to the blobs; 1654 / 4 and 202 are the figures I re-derived in tb_l31 and tb_l33 |
| 18ac053 (runtime-2) | the nine-entry detach, 94 entries byte-identical | loader on the 18ac053 archive: 103 entries, 23 red fixtures, 18 manifests, the guard the only red-fixture-plus-manifest entry; non-tests keys and the name order equal to 35ed0d4; exactly nine entries differ, each only in description and fcov_expectation_file (the parent reference dv/auto_dv/fcov_expectations/<name>.fcov.yaml, now None, the description ending with the return clause); dv/auto_dv/fcov_expectations byte-unchanged 8b22572..18ac053 |
| df1d8c5 (tb-infra-2 landing 37b) | the committed corrigendum restored to its bc4eba8 bytes; the supplement: the four landing-36 runs by path and figure (flow filelist_digest 3ecd04b3f9dc0734; f8087204d5d26cc3 for the local repro and the x16 run; 1a7de65f7001a0fa for the fixed run), the recipe over committed 1deec4c = 1a7de65f7001a0fa, the 39/38 figure cited as 20 retained logs | md5 cb593f105976d28fb0ed111cf976e167 at both bc4eba8 and df1d8c5; build_manifest.yaml of the dry run reads 3ecd04b3f9dc0734; tohost_root/out/old and out/new2 run headers read f8087204d5d26cc3 at seed 700483392 with the SimTimeoutError line; drv_root/out/fixed 1a7de65f7001a0fa; git grep over dv/auto_dv/evidence at df1d8c5: 24 files, 22 logs of which 2 are the landing's own, so 20 retained logs (reproduces); the file total 25 and the third prose file do not (L-3); manifest row 5044 / 05428ad51247a3ef |

## 2. Rows

- CM212-Low-1, Low-2, Info-3 and my CR-34 L-1 / L-2: answered by the landing-36 corrigendum (bc4eba8) and its supplement (df1d8c5); verified above.
  CM212-Info-1 (the pmc_ctrl description separator) is not touched in this range and stays open for the entry's next touch; CM212-Info-2 needed no
  file; CM212-Info-4 stays with the DV Lead.
- CR-33 L-1 / L-2 (= CM211-Low-1) and CM211-Info-1: answered by gen_rt35_supplement_corrigendum.log; CM211-Low-2 and CM211-Info-2: answered by
  gen_fu_guard_fcov_red_corrigendum.log, the NOT_RUN flag of tb_l33 ruled and recorded; CM210-Low-1/Low-2/Low-5/Info-2: answered in rt35c; all
  verified above. CR-33 L-3 (= CM211-Low-4): answered by the age17 corrigendum; verified.
- CR-30b-M-1's surviving items, CM210-Low-4 and CM210-Info-1: answered by v4t; the figures are the ones I re-derived earlier.
- Rows raised here: CR-35 M-1, L-1, L-2 (tb-infra-2, landing 37); CR-35 L-3 (tb-infra-2, landing 37b).

## 3. Findings

- M-1 (landing 37, bc4eba8; gen_checkers_pkg.sv close_owed and its comment; gen_fu_l37_tag_eor_unconsumed.log lines 11 and 24-27): the allowance
  rests on "the DUT checks a lookup it consumes", and the RTL has no such term. Quoted: rtl/ibex_icache.sv:585 ecc_err_ic1 = lookup_valid_ic1 &
  (((|data_err_ic1) & tag_hit_ic1) | (|tag_err_ic1)), with the RTL's own comment at :578-582 that the tag check "does not need to be qualified by
  hit or tag valid"; :644 ecc_error_o = ecc_err_ic1; :470 lookup_valid_ic1 <= lookup_actual_ic0; :266 lookup_actual_ic0 = lookup_grant_ic0 &
  icache_enable_i & ~inval_block_cache; :262 lookup_grant_ic0 = lookup_req_ic0; :269 tag_req_ic0 = lookup_req_ic0 | fill_req_ic0 |
  inval_write_req | ecc_write_req; rtl/ibex_core.sv:1337 alert_minor_o = icache_ecc_error. A tag error on ANY lookup that reaches IC1 alerts in
  the next cycle, whether or not the fetched instruction is ever used or retired. What the failing seed actually has, measured by my probe run:
  the injection announced at RAM cycle 21473 (way 0) shows lookup_valid_ic1 = 1, tag_err_ic1 = 01, ecc_err_ic1 = 1 and alert_minor = 1 in cycle
  21474, so an injection at cycle k is checked and alerts at k+1; the tail injection is announced at RAM cycle 21479 with lookup_req_ic0 = 1,
  lookup_actual_ic0 = 1, tag_req_ic0 = 1, tag_write_ic0 = 0, icache_enable_i = 1, inval_block_cache = 0 and both tag banks read, a real lookup
  the DUT would check, and that edge is the LAST posedge of the simulation (the cocotb clock stops when the test ends; $finish at 214845 ns): cycle
  21480 never occurs. The miss is the run ending inside the alert window, not a lookup the core never consumed. The Orchestrator's question,
  whether a consumed lookup can fall inside the no-retirement-after window: yes, every lookup after the last retirement is one, and the DUT
  checks each in the following cycle. So the predicate rt_cyc[$] < q[i].cycle is neither necessary nor sufficient for what it excuses: it
  coincides here (21478 < 21479 = the last observed cycle) but it also excuses an injection any number of OBSERVED cycles after the last
  retirement (a spinning or stalled core keeps fetching, and a missing alert there is a real defect the checker would now count unconsumed), and
  it still fails an injection at the last observed cycle when a record retired in that same cycle, the false-FAIL class the landing set out to
  remove. The condition the failure has is observability: injection cycle + GEN_ICACHE_ECC_WINDOW (2) reaching past the last observed cycle, which
  the misc monitor knows at report_phase; the P9 probe's lookup_valid_ic1 is the DUT-side alternative when it is on. Side B of the landing's red
  (875 in-run misses under MUT-ALERTSUP) is unaffected by which predicate is used. Severity Medium: the checker's core evidence stands, but a
  rule about the DUT is stated without its gating terms and contradicts them, in the code comment and in a retained log, and the rule as written
  can excuse a genuine miss. Required: the log's DUT statements corrected by corrigendum (bytes never move); the allowance re-keyed on the
  condition it names, with the code comment corrected, the failing seed re-run (PASS with the tail injection reported as unobservable), side B
  re-run, and a red that the old predicate would have excused (a qualified injection after the last retirement whose window closes inside the
  run, with the alert withheld) failing under the new one. REQUEST-CHANGES stands until re-review.
- L-1 (landing 37; gen_fu_l37_tag_eor_unconsumed.log section 2): the fixed-checker runs of side A name no build digest, where sections 1 and 3
  name theirs. The figure exists: the root's config_opts.txt reads 50981c82f49d7574, which equals my recipe over the committed bc4eba8 sources, so
  the green ran on the landed bytes. Corrigendum row.
- L-2 (landing 37; MUT-ALERTSUP): the applied mutation is retained as two hashes and a prose description; the diff itself is not (the
  gen_fu_l13 mutant.diff convention). Re-derived from the mutated root: three lines in gen_tb_top.sv (a mutsup_at plusarg read by
  $value$plusargs, and alert_minor forced low once evt_retired_count >= mutsup_at), 736a8d8099339024 -> 85b50e1343c65af1. Retain the diff.
- L-3 (landing 37b; gen_fu_l36_dbg_driver_livelock_supplement.log section 2 (b)): "all matching files 25" and "prose files that quote it 3"
  naming gen_manifest.md do not reproduce on the committed tree: git grep over dv/auto_dv/evidence at df1d8c5 finds 24 files, of which 22 are logs
  (20 retained plus the landing's own two) and 2 are prose (gen_critic_tb_l34.md, gen_tdd_step2b.md); the manifest carries no such phrase. The
  cited quantity, 20 retained logs, reproduces; the file total and the third prose file are a working-tree count. Corrigendum row.

### Informational

- I-1: dv/auto_dv/tools/gen_icache_ecc_figures.py TAG_RE still matches the widened GEN_MISC line (unanchored) and reads no unconsumed figure;
  whichever predicate lands, the figures tool should read the new count.
- I-2: the INCIDENT of 19:33:49Z is recorded by both sides and its consequence verified: the corrigendum's committed bytes are unchanged at
  df1d8c5 and the post-commit facts live in the supplement.
- I-3: the LOG-086 detach's two universes (declared 1891 / 758 / 1133; referenced 3902 -> 2066 = 735 + 1101) are both exact; the round record
  should state plan percentages in the referenced-set language, as 3db4dde says.
- I-4: rt35c's response says the guard corrigendum "names three options and answers none" while the log itself records the RULING and its
  reasoning (the ruling arrived between the two texts); the log is the later and correct statement.
- I-5: landing 37's positive control (index 28 retired 18 times, the last at 21478) and the rejected finish-keyed alternative (45 cycles of
  retirement past the finish request) both reproduce from the repro export.

## 4. Principles check

dv-principles-check (docs/dv/dv_principles.md d9c27db18f511411): S3 intent-derived checking: the tag-half allowance derives its intent from a DUT
behaviour the RTL does not have (M-1; non-conforming until re-keyed). S4 honesty: LOG-086 states its counts and their universe, rt35c corrects its
own presentation defects with the method beside every figure, v4t re-derives its corrigenda, the incident is recorded by both sides
(conforming); one working-tree count in the supplement (L-3) and one unnamed build (L-1). S6 trust triad: landing 37's red is two-sided with an
ablation and reproduces (conforming in evidence), the mutant diff is not retained (L-2); rt35c's parser change carries a discriminating
self-test case (conforming). One-line verdict: FAIL on S3 for landing 37; PASS elsewhere.

## 5. Verdict

CRITIC VERDICT: REQUEST-CHANGES on the range 1deec4c..df1d8c5, confined to landing 37 (bc4eba8). Rows CR-35 M-1, L-1, L-2 (tb-infra-2, landing 37)
and CR-35 L-3 (tb-infra-2, landing 37b). Gated: progress built on the tag-half allowance as committed, until the re-keyed rule and its red are
re-reviewed. Not gated: the LOG-086 detach, rt35c, v4t and landing 37b, all verified. Round-1 consequence, stated for the Orchestrator's ruling
rather than decided here: with the rule as committed a round cannot fail falsely on the tail case, but a genuine missing alert after a run's last
retirement would be counted unconsumed; if round 1 runs on this checker, its record must state the allowance's actual predicate and that
exposure.

## 6. Reconciliation with the range's cross-model review

Artifact: dv/auto_dv/reviews/2026-09-04-claude-diff-1deec4c5-df1d8c53.md, committed e89d01f, blob 948d027d5c17dc2e, 38 lines, verdict
APPROVE-WITH-CHANGES. Reviewer identity as its header states: the Claude fallback (claude CLI 2.1.261, run-reported model claude-fable-5-1 with
claude-haiku-4-5-20251001, requested effort high, a fresh session on a detached read-only checkout of df1d8c5; codex unavailable on the spend cap;
owner ruling A-001). Five rubrics PASS. Read after Sections 1-5 were written; nothing above was changed on reading it.

Agreements:

- Its Low-1 is my L-3 (the supplement's 25 files and third prose file against 24 and two at df1d8c5; the 20 retained logs reproduce), with the
  same fix, a corrigendum row pinning the total to the commit.
- Its Low-2 is my L-1 (side A of the l37 log names no root or digest) WIDENED by a miss of mine, adopted and verified: the log's line 77 says
  "Every figure is read from a run's own artefacts by the command printed above it" while no command line appears in any of its 77 lines (a
  count of lines beginning with a dollar sign or an invocation gives zero), the same overclaim CM212-Low-2 corrected in the l36 log and that I
  adopted in tb_l34. CR-35 L-1 now carries both: the side-A root and digest, and the closing claim scoped or dropped. Missed for the same reason as
  last time, reading the log for its figures and not for the claim it makes about them.
- Its figures re-derived by me: gen_covergroup_set.py at b105c09 gives 58 covergroups / 4106 referenced bins / 28 manifests and at 18ac053 20 /
  2066 / 18 (I had 50 / 3902 / 27 at 35ed0d4); the with_nmi logs at df1d8c5 number 23 with 19 carrying a GEN_IRQ_CHK summary; the corrigendum's
  git blob is 4e436ecf at both bc4eba8 and df1d8c5; the manifest-row sizes and md5s, the doldi 52 / 47 / 25 / 29, the six before-and-after hashes,
  the 513 -> 510 deletion with the 3 BAD lines in the PROTOCOL_ERROR variant, gen_regress.py:754 / :758 / :615, gen_round.py without either flag,
  the loader figures 103 / 18 / 23 with the guard the only red-fixture-plus-manifest entry, and the six byte-identical v4t records all agree with
  Section 1. Its recipe figure f8087204d5d26cc3 at 92c0850 and b105c09 agrees with mine (the recipe set is unchanged from 962d31f to b105c09).

Adopted and verified:

- Info-1: gen_tdd_step2b.md:1096-1097 at df1d8c5 reads "which names the / three local roots and / three local runs with their roots' heads", a
  duplicated clause from the 37b edit. Cosmetic; the next records touch.
- Info-2: the guard corrigendum's "RULED, not open" cites the Orchestrator's task list, which is not tracked, and at df1d8c5 no intervention-log
  entry carried the ruling. Resolved outside this range by f1087c9 (LOG-087, "recorded here so the corrigendum's citation resolves inside the
  repository"), which I read; it belongs to the next range's verification.

Disagreement, recorded for the Orchestrator: the artifact's assertion-integrity rubric reads the landing-37 allowance as "a narrow, commented
allowance mirroring the data half" and its verification confirms the mechanism as coded and the two-sided red; it does not test the rule's
premise against the RTL, and it raises no finding on it. My M-1 stands on the probe run and the quoted terms of Section 3: the DUT checks a tag
error on every lookup that reaches IC1 (rtl/ibex_icache.sv:585, :644, :470, :266), the failing seed's injection sat on a real lookup at the last
posedge of the run, and the predicate excuses more than the run's end. The verdicts therefore differ, REQUEST-CHANGES here against
APPROVE-WITH-CHANGES there; under the policy my REQUEST-CHANGES stands until a re-review of the re-keyed rule, and if the Orchestrator rules
otherwise the disagreement goes to the human owner rather than back into the loop.

Corrigenda to Sections 1-5: none; nothing above was found false. L-1 is widened as stated. Rows after reconciliation: CR-35 M-1, L-1 (widened),
L-2, L-3. CRITIC VERDICT: REQUEST-CHANGES, unchanged.
