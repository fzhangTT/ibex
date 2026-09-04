# Critic verdict: the range e641b24..d1f6019 (landing 39b, tb_l36 as written, LOG-088, the six-entry detach, the round-1 request form), reviewed as tb_l37

Scope (the Orchestrator's): five commits, 8 files, 535 insertions, 21 deletions, nothing under rtl/ or the TB sources: 420cbc6 (tb-infra-2's landing 39b,
records-only: the MUT-ALERTSUP mutant diff as a retained file, the l39 supplement log with the measured negative for the discriminating red, manifest rows,
a step2b sentence), c3dc115 (tb_l36, as written), 7f61cd1 (owner-log LOG-088: six more measured entries detached after the fcov pre-flight), f60bee5
(runtime-2's six-field detach), d1f6019 (the DV Lead's round-1 request form, 261 lines; the round HEAD). By the Orchestrator's instruction this verdict also
carries the landing-38 (9baf3f9) finding adopted in tb_l36 Section 6 and the 39b rows held from the tb_l36 prep. The range closes at d1f6019 once the
dispatch has pinned; its cross-model review had not launched when this was written, so Section 6 follows by corrigendum or in a later touch.

Artifacts reviewed (committed blobs at the commit named; sha256 first 16 hex):

- dv/auto_dv/evidence/gen_tdd_logs/mutations/gen_fu_l39_MUTALERTSUP_mutant.diff @420cbc6  28a24975f7047f6a
- dv/auto_dv/evidence/gen_tdd_logs/mutations/gen_fu_l39_tag_eor_supplement.log @420cbc6  7ff81b59e9369f38
- dv/auto_dv/evidence/gen_tdd_logs/gen_manifest.md @420cbc6  cd9c0a1ec611bfe2
- dv/auto_dv/evidence/gen_tdd_step2b.md @420cbc6  f86c02a321910771
- dv/auto_dv/evidence/gen_critic_tb_l36.md @c3dc115  a65dbccf121f7a12
- dv/auto_dv/docs/gen_intervention_log.md @7f61cd1  b434cd3202caa749
- dv/auto_dv/flow/gen_testlist.yaml @f60bee5  88665c81f7b9ffd6
- dv/auto_dv/evidence/gen_round1_request.md @d1f6019  6c70ccfe37d8b49c
- dv/auto_dv/gen_tb/gen_tests/gen_ut_intg_store.py @9baf3f9  ff2cf74e8042250c
- dv/auto_dv/evidence/gen_tdd_logs/lockstep/gen_fu_l38_intg_store_read_race.log @9baf3f9  21888b5c77713a42

Date: 2026-09-04 (UTC). Role: Critic (reviewer other than the author). Basis: docs/dv/dv_principles.md d9c27db18f511411; gen_critic_tb_l36.md (a65dbccf121f7a12,
committed c3dc115) and its adopted landing-38 item; the review e641b24 (blob f20a5ccbff7fa13c) whose Low-4 that item is; LOG-085, LOG-086 with its corrigenda,
LOG-087, LOG-088; the acceptance-form rule (expected per-entry outcomes stated before the wave); the retained-header rule; the loader rules (P6, LOG-067,
LOG-077).
Method: detached git worktree of d1f6019 (the gate: both codegen --check up to date, three UTs PASS, CONST, RED-CHECK PASS, validate 28 OK, TBMAN 3484 rows
0 bad; flow build identity bc0cd7778e382b13 over 117 sources for gen_tb, unchanged from 726682a; my TB-source recipe 18c7a44b8edfefc4, unchanged from
726682a). Every figure of the request form re-derived with the flow's own functions on a detached archive of d1f6019 (load_testlist, select_tests,
seeds_for_test, measured_refusal with its two controls, gen_covergroup_set.py, gen_build_identity.py --root on archives of 3cabc7e, 9baf3f9 and 726682a) and
from the retained pre-flight regression in the out-tree (its manifest and its rst_boot run banners); the six-field detach checked field by field against
its parent 7f61cd1 through the loader; landing 39b's diff applied to the committed gen_tb_top.sv; the landing-38 loop read at 9baf3f9. EXPOSURE: the
Orchestrator's messages; the authors' retained artefacts and the out-tree; the DV Lead's form (read after my own figures were in the prep notes). No
subagent used.

CRITIC VERDICT: APPROVE. The request form states an expected outcome for every one of the round's 53 runs and nothing outside them, and every figure in it
reproduces through the flow's own selector, seed derivation, gate function and identity tool; the six-field detach is byte-exact outside its two fields
per entry and the projection it was written against (5 covergroups, 471 referenced bins, 12 manifests) holds on the committed testlist; landing 39b
answers CR-35 L-2 and records the discriminating red as a measured negative with figures that match my own probe; tb_l36 is committed as handed. Four Lows,
none gating: a landing-38 loop that can break on a transient equality (adopted from the review), a landing-38 digest that names the pre-fix tree, two
records inaccuracies in 39b with CR-36 L-3 still open, and the form's pending-edit clauses that are stale at its own commit.

## 1. What was verified

| commit | item | evidence (re-derived by me) |
|---|---|---|
| 420cbc6 (tb-infra-2 landing 39b) | gen_fu_l39_MUTALERTSUP_mutant.diff retained with a manifest row (CR-35 L-2); the supplement: the discriminating red not constructible on this entry (tail = last observed cycle 21480 minus last retirement 21478 = 2 = GEN_ICACHE_ECC_WINDOW, so no injection is both after the last retirement and window-closed in-run); the l37 corrigendum's bytes restored after a post-commit edit | the diff (686 bytes, md5 ab3fb3d157fb8779 = row) applies to the 726682a gen_tb_top.sv 736a8d8099339024 and yields 85b50e1343c65af1, both hashes the l37 and l39 logs cite; the supplement's 21480 equals my own report-phase probe of tb_l36 (misc.cycle 21480, last export event 21479), and the emptiness holds under both the committed predicate (judged iff c + 2 <= 21480) and tb_l36 L-1's corrected boundary (c + 2 < 21480), so the negative stands; the corrigendum blob is 467980032e371c2e at both 726682a and 420cbc6; supplement row 5452 / ddf32c21c... equals the blob |
| c3dc115 | tb_l36 committed as handed | content a65dbccf121f7a12, 136 lines |
| 7f61cd1 (LOG-088) | the fcov pre-flight at the round's seeds: 24 runs, pass 6, unmet 18; six entries fail every seed with UNHIT bins (cmp_zcb 8/8/10 of 110, cmp_zcmp_basic 112/119/116 of 472, isa_alu 19/22/24 of 602, isa_cti 16/16/16 of 200, mul_div 22/23/24 of 224, rst_boot 2/2/2 of 8); isa_shift and mul_mul pass; stable unmet bins named; six detached, manifests 18 -> 12, the round checks 2 and counts 13 | the retained manifest at /proj_soc/user_dev/fzhang/ibex_dv_out/regress_r1_fcov_preflight (head 726682a, status done, 24 runs, 6 pass, 18 fail, no timeout or not_run): every per-seed count as stated, every failing status UNHIT, gen_isa_branch_cg.cp_op.c_beqz / c_bnez unmet in every isa_cti run, gen_rst_boot_cg.cp_boot_addr.zero and gen_sec_ctrl_inputs_cg.cp_bit8_readback.zero in every rst_boot run; each entry's three pre-flight seeds equal seeds_for_test at base 20260904 |
| f60bee5 (runtime-2) | six fields nulled with the reason in the description; the other 97 entries yaml-equal; manifests 18 -> 12; the guard the only deferred-shape entry | loader on the d1f6019 archive: 103 entries, 23 red fixtures, 12 manifests, the guard the only red-fixture-plus-manifest entry; non-tests keys and the name order equal to 7f61cd1; exactly the six entries differ and only in description and fcov_expectation_file; dv/auto_dv/fcov_expectations byte-unchanged 7f61cd1..d1f6019 |
| d1f6019 (DV Lead, the form) section 1 | tier full = 19 entries (16 smoke, 3 targeted), 53 runs (44 + 9), 45 measured (42 + 3) over 15 entries, 8 unmeasured; check tier 84 entries / 88 runs not selected | select_tests(tl, "full", None, None) and seeds_for_test(t, None, 20260904) on the d1f6019 archive give exactly those figures; select_tests with the check tier gives 84 / 88 |
| section 2 | base seed 20260904: 53 distinct seeds and pairs, deterministic, 0 of 45 measured seeds shared with base 20260905 | reproduced |
| section 3 | --seeds 3 gives 57 runs with 45 measured, --seeds 5 gives 95 with 75 | reproduced through seeds_for_test with the override |
| section 4 | every measured entry pins nothing (one plusarg, +gen_fetch_en_at_reset=0) and regenerates its program per seed (program seed: run); the two one-seed entries run a directed image with seed 1; rst_boot's banners differ by seed (249 vs 297 words, different crc32, regime draws random / same_cycle, random / long, quiet / sparse, grants 174 to 250) | the 15 measured entries carry exactly that one plusarg and program seed run; gen_boot_zc and gen_ut_lockstep carry the directed gen_zc_directed.S with seed 1; the pre-flight's three rst_boot runs read 249 / 249 / 297 words, three crc32 values, the regime draws as stated, grants 174 / 179 / 250 |
| section 5 | the pre-flight table with union and every-seed columns (14/6, 147/74, 39/6, 16/16, 28/19, 2/2), 246 distinct unmet bins over the six, 123 stable and 123 seed-dependent, gen_div_timing_cg.cp_dit.on unmet in every mul_div run; checked = isa_shift + mul_mul, 458 distinct declarations over 4 rendered covergroups, 6 runs; counted-only 13; the pmc groups' 1019 planned rows and no mention in the credit report; declared set 3902 / 3167 built at ede678c, 2066 all built at 18ac053, the LOG-088 projection 5 / 471 / 12 | every column reproduced from the pre-flight manifest; 458 distinct over gen_cmp_zcb_cg, gen_isa_shift_cg, gen_mul_ops_cg, gen_mul_timing_cg, all rendered; 1019 CG-PMC rows in gen_trace_tp_bin.csv and zero gen_pmc_ mentions in gen_round0_credit.md; 3902 / 3167 and 2066 are my tb_l35 figures; gen_covergroup_set.py on the COMMITTED d1f6019 testlist reports 5 covergroups, 471 referenced bins, 12 manifests, so the projection is now a measurement (2066 - 471 = 1595 as stated) |
| section 6 | the eight unmeasured runs and their expectations; coverage on for every run (gen_regress.py:615, gen_round.py without either flag) | the four unmeasured entries and seed counts reproduced; :615 and the zero occurrences verified in tb_l35 |
| section 7 | P6 / LOG-067 / LOG-077 through measured_refusal: 0 refusals over 19; the controls | measured_refusal(t, [], tl, measured, True) is None for all 19; rst_boot with +gen_dbg_csr_probe=1 returns the P6 refusal when measured and None when unmeasured; with +gen_chk_sva_b8 the LOG-067 refusal; seven debug_only knobs declared |
| sections 8 and 11 | identities: 726682a bc0cd7778e382b13, 3cabc7e and 9baf3f9 6a1d73dfb815cfc7; only landing 39 touches a source path between 9baf3f9 and 726682a; no source path changes 726682a..d1f6019 | gen_build_identity.py --root on archives of the three commits gives exactly those; git log over tb, env, isa and rtl lists 726682a alone; the diff 726682a..d1f6019 over those paths is empty; the gate at d1f6019 reads bc0cd7778e382b13 |
| 9baf3f9 (landing 38, adopted item) | the quiesce loop and the log's build digest | see L-1 and L-2 |

## 2. Rows

- CR-35 L-2: answered by 420cbc6 (the diff file). CR-36 L-2 (the discriminating red): the measured negative is recorded with its figures, as the row asked;
  the red stays owed until a stimulus with a longer tail exists. CR-36 L-1: open (post-round). CR-36 L-3: OPEN, not answered in 420cbc6 (see L-3 below).
- CM214 (the e641b24 rows): Low-1 = CR-36 L-3 (open); Low-2 answered by 420cbc6; Low-3 = CR-36 L-2 (recorded); Low-4 = CR-37 L-1 here.
- Rows raised here: CR-37 L-1, L-2 (tb-infra-2, landing 38, post-round); CR-37 L-3 (tb-infra-2, 39b records); CR-37 L-4 (DV Lead, the form).

## 3. Findings

- L-1 (landing 38, gen_ut_intg_store.py:67 at 9baf3f9; adopted from e641b24 Low-4 and verified by reading): the quiesce loop breaks on a single-instant
  equality of evt_retired_count and evt_isa_records, sampled once per cycle up to QUIESCE_CYCLES. A genuine one-record skip (the comparator one behind)
  coinciding with a record in flight (the comparator one ahead) reads as equality, so the loop breaks and the unchanged assertion passes with a skipped
  record. Non-convergence fails as the landing says; transient convergence does not. Fix: wait for the retired count to be unchanged across a cycle and
  then compare, or require equality on two consecutive samples. Post-round: gen_ut_intg_store is check tier and not in the round.
- L-2 (landing 38, gen_fu_l38_intg_store_read_race.log line 34): the one digest the log names, 50981c82f49d7574, is the local recipe over the PRE-fix tree
  (equal to my recipe over df1d8c5). The recipe's set includes dv/auto_dv/gen_tb/*.py, so the fixed side's source set has another figure: my recipe over the
  committed 9baf3f9 is 034f4e4f2905cb72. The simv is the same for both sides, as the log says, and the digest is the compile-time figure; but a reader
  recomputing the recipe over the landing's commit gets 034f4e4f2905cb72 and concludes a mismatch, the class CM211-Info-2 named. The red side's source
  state is not on disk either (tb-infra-2's intgfix_root was edited in place between the runs, its test file now carrying QUIESCE_CYCLES twice), so the
  log's occurrence-count control is a run-time figure only. Corrigendum row naming both tree figures.
- L-3 (landing 39b records): (a) the gen_tdd_step2b.md sentence says the l37 corrigendum's "five parts also answer CM213 Low-1 and Low-2 and CR-35 L-2 and
  M-1"; the corrigendum has three parts, and L-2 and the M-1 negative are answered by the supplement, not by it. (b) CR-36 L-3, the l39 observability
  log's line-56 claim that every figure is read "by the command printed above it" while the log prints no command, is not scoped anywhere in 420cbc6:
  its manifest row is unchanged, the supplement and the step2b sentence do not mention it, and no corrigendum row exists for it, so the row stays open
  despite the relay's "answered in 420cbc6". Next records touch.
- L-4 (the form, gen_round1_request.md lines 9, 12-13, 132-133, 150-154): the clauses "that ruling's testlist edit is not committed yet", "the testlist
  has not moved since the detach at 18ac053", "once runtime-2's field edit is committed, and until then the round must not be dispatched" and "a PROJECTION
  until runtime-2 commits" were true at the form's stated measurement point e641b24 and are stale at its own commit: f60bee5 is the commit before d1f6019.
  The figures are unaffected (the projection reproduces on the committed testlist as 5 / 471 / 12, and I have the form's own promise that the round record
  carries the measured figure), so this is the record's tense, not its content. One line in the round record or the form's next touch stating that the
  edit landed as f60bee5.

### Informational

- I-1: the form's grant-count example (174 to 250) is two of rst_boot's three seeds; the third reads 179. Not a defect.
- I-2: the pre-flight manifest carries no top-level base_seed key; the seed identity with the round is established by derivation (every entry's three
  seeds equal seeds_for_test at base 20260904), which is the stronger check.
- I-3: for the round record, from LOG-088 and the form: 2 checked entries (6 runs) and 13 counted-only; the 18 unmet sets are declaration findings; the
  check-tier fixes of landings 36 to 39 are outside the round; percentages over the declared set move for bookkeeping (2066 -> 471 referenced bins).

## 4. Principles check

dv-principles-check (docs/dv/dv_principles.md d9c27db18f511411): S2 realistic stimulus: the round's measured set pins nothing and regenerates its program
per seed (conforming, verified). S3 intent-derived checking: the checked set shrinks to what the runs guarantee per run, with the declaration question
routed to a post-round ruling rather than fitted to the sample (conforming); the landing-38 loop can pass a skipped record on a transient (L-1). S4
honesty: the form states an expected outcome for all 53 runs and none outside them, names what it does not select, and corrects its own first version;
the pre-flight is cited by path and reproduces; one set of stale clauses (L-4), one digest of the wrong tree (L-2), two records inaccuracies (L-3). S6
trust triad: the mutant diff is now retained (CR-35 L-2 closed); the discriminating red is recorded as a measured negative and stays owed. One-line
verdict: PASS, four Lows owed.

## 5. Verdict

CRITIC VERDICT: APPROVE on the range e641b24..d1f6019. Rows CR-37 L-1 and L-2 (tb-infra-2, landing 38, post-round), CR-37 L-3 (tb-infra-2, 39b records, with
CR-36 L-3 still open), CR-37 L-4 (DV Lead, the form), all Low and none gating. Nothing of mine gates the round-1 dispatch. The round record is next: its
verdict will re-derive the 53 outcomes against the form's section 5 and 6 expectations, the 18 unmet sets from the retained pre-flight, the 2 checked
entries' six runs, the credit and covergroup-set regeneration at the round's commit, and the identity bc0cd7778e382b13 against the canary.
