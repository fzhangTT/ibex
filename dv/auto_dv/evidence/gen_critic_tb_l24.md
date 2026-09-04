# Critic verdict: tb-infra landing 24, the re-review of tb_l23 (commit fb494f4, diff base 1a7f506), reviewed as tb_l24

Scope (the Orchestrator's): the twelve paths of landing 24, the recorded re-review of gen_critic_tb_l23.md (f824b1547ae6d44f, committed d0ab116,
REQUEST-CHANGES): CR-23-M-1 (the queue bound as a gen_tb_knobs.yaml constant with an sv expression, gen_ic_in_window below GEN_KNOBS_END), CR-23-M-2 (the
routing and window mutations retained with per-root identity, the evidence re-taken on build w26), CR-23-L-1 (the group manifest confirmed unable to
pass, the eight entries reverted to null, per-entry manifests owed in landing 25), CR-23-L-2 (the never-written bin's term chain verified at the RTL and
the anti-vacuity note reworded), the manifest's schema, the Section 7 build-before-red sentence, the quiet-window detector restated, and the CM198 rows.
This verdict also carries the reconciliation owed by tb_l23 with the landing-23 cross-model review (Section 6). Each CR-23 row is verdicted in Section 2.

Artifacts reviewed (committed blobs at fb494f4; sha256 first 16 hex):

- dv/auto_dv/tb/gen_tb_knobs.yaml  778c36713afa3ed7
- dv/auto_dv/tb/gen_tb_pkg.sv  351444333fe6ed75
- dv/auto_dv/gen_tb/gen_knobs.py  5e3735d1d5355043
- dv/auto_dv/isa/gen_isa_shim_map.h  271a78654737f057
- dv/auto_dv/env/gen_checkers_pkg.sv  d4b41edaa722a2e3
- dv/auto_dv/fcov_expectations/gen_cg_ic_ecc_part1.fcov.yaml  567cb7a90d51da24
- dv/auto_dv/docs/gen_wp8_part1_plan.md  d80e3f7b024c6b7b
- dv/auto_dv/evidence/gen_critic_response_fu2a.md  2923a6528777dfe8
- dv/auto_dv/evidence/gen_tdd_logs/gen_manifest.md  d7ae890184053a17
- dv/auto_dv/evidence/gen_tdd_logs/mutations/gen_fu_l24_wp8_ut_muts.log  f9cd0d0ba78a9231
- dv/auto_dv/evidence/gen_tdd_logs/mutations/gen_fu_l23_wp8_cov_reds.log  4458a42404ac9ebe
- dv/auto_dv/evidence/gen_tdd_logs/mutations/gen_fu_l23_fcov_checker_cross_bins.log  08ec21f23035c004

Date: 2026-09-04 (UTC). Role: Critic (reviewer other than the author). Basis: docs/dv/dv_principles.md d9c27db18f511411; gen_critic_tb_l23.md;
LOG-084, LOG-084c; rtl/ibex_icache.sv:277, :280, :283, :585 (the term chain the plan now quotes: tag_write_ic0 = fill_grant | inval_write | ecc_write;
data_req_ic0 includes fill_req_ic0; data_write_ic0 = tag_write_ic0; ecc_err_ic1 needs tag_hit_ic1 for the data term); rtl/ibex_pkg.sv:400-405
(IC_SIZE_BYTES 4096, IC_NUM_WAYS 2, IC_LINE_SIZE 64: 4096 / 2 / 8 = 256 lines, times 2 ways = 512).
Method: detached git worktree of fb494f4 and copies. The landing-24 list equals the twelve-path diff and 12 of 12 md5s verify. Gates on the worktree,
all PASS: gen_knobs_codegen --check up to date, gen_ut_knobs_codegen 0 failures, gen_fcov_codegen --check up to date, gen_ut_fcov_codegen 0 failures,
CONST-CHECK, and the flow's manifest schema sweep gen_fcov.py --validate (19 OK, 0 FAIL, rc 0), which tb_l23 did not run and now sits in my standing checks.
Build identity first-hand: the recipe on the tree gives 9ff74126059016cb, equal to the control root of both mutation logs and the cross-bins log's build
(w26): the retained runs compiled the committed tree. Mutant identity re-derived from committed files alone, for all six roots: applying each logged
diff to the fb494f4 blob of the named file reproduces the logged mutated sha256 (6 of 6), and the tree's per-file list with that file's hash swapped for
the mutated one hashes to the root's logged sources sha for the four single-diff roots (UNINITQ, WINSHORT, UNINITALL, UNINITDRAIN); the two ablation
roots reproduce only when BOTH the fault and the removed cases are applied (98dafe128b90841c and 9117eb311006c8c9, exact), which proves the ablations
carry the fault and shows their identity blocks list one of their two diffs (L-2). The logged "committed" hashes for gen_tb_pkg.sv and
gen_checkers_pkg.sv are those files at 1a7f506, not at fb494f4 (L-1). The constant's placement, the mirrors (512 in gen_knobs.py and the C header), the
function's position (line 548, below GEN_KNOBS_END at 542), the manifest (test = stem, 15 bins, 15 anti-vacuity notes, one per bin), the cross-bins log's
provenance block (its checker sha 282127c9994dd824 equals the committed checker), the plan's Section 7 sentence, the response rows ("eleven unit-test
cases" 0 on flattened text, "seventeen" 5) and the testlist (the eight entries at fcov null) read and checked. No subagent used. EXPOSURE: none
beyond the Orchestrator's message and the git log subjects. Section 7 says whether this range's cross-model artifact was read.

CRITIC VERDICT: APPROVE. CR-23 M-1 and M-2 are answered with evidence that reproduces from the committed tree; L-2 is answered with the RTL chain; L-1 is
ruled and scheduled for landing 25. The REQUEST-CHANGES of tb_l23 is lifted by this verdict. Three lows on the retained identity blocks and the unit-test
pass, none touching what the runs show.

## 1. What was verified

| item | as built at fb494f4 | evidence (re-derived by me) |
|---|---|---|
| CR-23-M-1 | GEN_ICRAM_UNINIT_Q_DEPTH is a gen_tb_knobs.yaml constant (value 512, sv "ibex_pkg::IC_NUM_LINES * ibex_pkg::IC_NUM_WAYS"), rendered inside the knobs region at line 248 with the mirrors in gen_knobs.py and gen_isa_shim_map.h; gen_ic_in_window sits below GEN_KNOBS_END with a comment saying why | both knobs gates PASS; the generator's other outputs unchanged; 4096 / 2 / 8 x 2 = 512 from ibex_pkg |
| CR-23-M-2 | gen_fu_l24_wp8_ut_muts.log: UNINITQ (the report routed into q) FAIL with 2 unit-test failures, the two routing cases' lines; UNINITQ_ABL PASS 0; WINSHORT (the arithmetic one short) FAIL with 1 failure, exactly the last-cycle case; WINSHORT_ABL PASS 0; every catch with +gen_chk_all=0; each root with an identity block (file, committed and mutated hashes, applied diff, anchor checks); gen_fu_l23_wp8_cov_reds.log re-taken on w26 with identity blocks for UNINITALL and UNINITDRAIN; the control root equals the tree | six mutated hashes and six sources shas reproduced from committed files (Method); the failing lines are the cases named |
| the evidence re-taken | the record says three times, because the build identity moved twice; the final set is of one build, w26 = the tree | the recipe; both logs' control sha |
| CR-23-L-1 | confirmed worse than the row: the flow validates the manifest's test against the entry name before coverage is read, so the group shape fails every entry at once; the eight entries reverted to null (514bb74); per-entry manifests owed in landing 25; the manifest carries a promotion note | the testlist at fb494f4: all eight at fcov null; the manifest's comment; the Orchestrator's ruling |
| CR-23-L-2 | the plan states the term chain (:277 the three tag writers, :280 and :283 the data write riding the fill, :585 the data term needing tag_hit_ic1) and what the bin witnesses (the unhit-way masking; the qualification buys a volume bound); the anti-vacuity note for uninitialised_data_ram says the same | the four RTL lines read; the note in the manifest |
| the manifest's schema | test: gen_cg_ic_ecc_part1, 15 bins, an anti_vacuity note per bin, the 14 cross bins listed in a comment as checkable on the derived path (LOG-084c) and left for the touch that verifies them there | gen_fcov.py --validate 19 OK, 0 FAIL |
| CM198 rows | Major-1 and Major-2 as above; Minor-1 the cross-bins log's provenance block (build, sha, run, database, urg invocation, report count, checker sha, time); Minor-2 the Section 7 sentence at the head of the section; Info-1 seventeen; Info-2 the detector restated with the accumulation residual named; the nit kept at the declaration | the diffs; the checker sha equals the committed file's |
| CM198 relay count (tb-infra's open row) | tb-infra saw two Minors described and three counted | the third Minor is Runtime's (gen_log084_cross_parse.log's provenance), not tb-infra's; nothing is unrelayed to tb-infra |
| the deviations table | the schema defect of the landing-23 manifest (four counts) and the generated-region defect stated as tb-infra's own, with causes and the measured consequence (the six-line difference, no knob value changed) | consistent with tb_l23 M-1's diagnosis |

## 2. Verdict per CR-23 row

- CR-23-M-1: CLOSED. The bound is a yaml constant rendered into the region; the function is outside it; both gates pass; the evidence was re-taken on the
  moved build rather than carried.
- CR-23-M-2: CLOSED. Both unit-test-caught mutations retained as failing runs with ablations; the two manifest reds re-taken; every root's identity
  reproducible from committed files (with the two record lows below).
- CR-23-L-1: RULED, OPEN UNTIL LANDING 25. The eight entries are at null; the eight per-entry manifests and the loader red are the next landing's.
- CR-23-L-2: CLOSED. The plan and the note say what the bin witnesses, with the RTL chain quoted; verified line by line.
- CR-23 I-1..I-4: I-1 (the copy-in disclosure) stands as recorded; Runtime's confirmation is Runtime's row. I-2 to I-4 need nothing.

## 3. Findings

### L-1 (low) [S4 record] The identity blocks' "committed" hash is the pre-landing file for the two files landing 24 edits

For UNINITQ and WINSHORT (gen_tb_pkg.sv) and UNINITDRAIN (gen_checkers_pkg.sv) the blocks record committed 1e9c6220b81b298f and ceae51ad2b959198, the
hashes of those files at 1a7f506 (HEAD when the identity was taken), while the file the diff was applied to is fb494f4's (351444333fe6ed75 and
d4b41edaa722a2e3): applying the logged diff to fb494f4's blob reproduces the logged mutated hash exactly, and the roots' sources shas reproduce from the
fb494f4 list, so the base was the landing's content. The identity therefore holds in substance and the recorded anchor hash is the wrong file. Record the
hash of the file the diff was applied to (or label the field "HEAD at identity time" with its commit).

### L-2 (low) [S4 record] The ablation blocks list one of their two diffs

UNINITQ_ABL and WINSHORT_ABL each show "applied diff 1 of 1", the removed cases in gen_fcov_pkg.sv, yet their sources shas reproduce only with the fault in
gen_tb_pkg.sv applied as well (98dafe128b90841c and 9117eb311006c8c9, exact, versus e66b979bf55e6406 and 9ee33e3340dab8c8 without it). The roots are right,
the fault present and the detector removed, which is what an ablation is; the blocks under-report. List both diffs in an ablation's identity block.

### L-3 (low) [S6 retention] The seventeen cases' pass on the unmutated build is not retained as a count

The response says the seventeen cases have their in-simulation pass in the same runs. The logs record "unit-test failures: N" per mutant root and nothing
for the GREEN control; the catch roots prove the harness ran (their failing cases are printed) and the ablation roots show 0 failures on a mutated build
with cases removed. Add the GREEN root's "cases run 17, failures 0" line, which is the pass the record claims.

### Informational

- I-1: the yaml constant carries value 512 beside its sv expression and nothing compares the two (the twin check exists only for derived constants), as
  tb-infra discloses; the arithmetic checks today (256 x 2) and no Python or C consumer reads the mirror. A generator-side check is the plan owner's and
  tb-infra's to schedule, not this landing's.
- I-2: LOG-084c (after tb_l23): the flow's measured path derives a variable-form report in which cross bins are keyed, so the checker defect is confined
  to direct raw-report calls; the manifest's fourteen cross bins are left for the touch that verifies them through the derived path. tb_l23 described the
  interim ruling as applied at f0723d6, which was true then.
- I-3: tb_l23 did not run the flow's manifest schema sweep, the gate the committed group manifest failed at f0723d6; neither did the cross-model review.
  Run here and added to my standing checks.
- I-4: the review artifact for this range (Section 7) also covers Runtime's 71f207c (the loader rule); its rows on that commit are Runtime's.

## 4. Principles check

dv-principles-check (docs/dv/dv_principles.md d9c27db18f511411): S5 single source: the bound in the yaml, the function outside the region, both gates
green (conforming). S6 trust triad: four mutations retained with ablations on identified roots whose identity reproduces from committed files
(conforming; L-1, L-2, L-3 on the record of that identity). S4 honesty: the deviations table names the landing-23 defects as tb-infra's own with causes
and measured consequences; the plan says what the bin witnesses and what the detector does not cover (conforming). One-line verdict: PASS with three lows.

## 5. Verdict

CRITIC VERDICT: APPROVE. The REQUEST-CHANGES of tb_l23 is lifted. Lows L-1..L-3 with landing 25. CR-23-L-1 stays open until landing 25's per-entry
manifests. Rows CR-24.

## 6. Reconciliation owed by tb_l23 (frozen): the cross-model review of 36bc3a4..f0723d6

Read after tb_l23 was frozen: dv/auto_dv/reviews/2026-09-04-claude-diff-36bc3a4c-f0723d6d.md (sha256 fb37cb90f02ea5fd, 48 lines, committed b94c2f8),
REQUEST-CHANGES. Verdicts agreed: its two Majors were tb_l23's M-1 and M-2 with the same re-derivations (the six-line difference, the STALE and sixteen
failures, the evidence standing on the committed tree; the routing and window mutations retained nowhere). Its fix route for M-1 (the yaml constant with an
sv expression) is the one this landing took; tb_l23 had offered either route. Four items it found that tb_l23 missed, each verified then and answered by
this landing: the cross-bins log's missing provenance (now a provenance block), the plan's missing build-before-red sentence (now at the head of Section
7), the "eleven" figure (now seventeen), and the quiet-window detector narrower than the plan's wording (now restated with its residual). Its Runtime Minor
(gen_log084_cross_parse.log's provenance) is Runtime's. No corrigendum to tb_l23: nothing it said was false; it under-found.

## 7. The cross-model review of this range

Not read: at hand-off the artifact covering this commit, dv/auto_dv/reviews/2026-09-04-claude-diff-1a7f5066-71f207ca.md (the range 1a7f506..71f207c,
which holds fb494f4 and Runtime's 71f207c), existed as an empty, uncommitted file (0 lines, sha256 of the empty input e3b0c44298fc1c14; `git log` names no
commit for it): the review was still running. Its rows are reconciled by the Orchestrator's relay or in my next verdict. Both verdicts gate landing 25.
