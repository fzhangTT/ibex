# Critic verdict: tb-infra landing 7 (commit ab67c6c, diff base f255b04), reviewed as tb_l8

CORRIGENDUM to dv/auto_dv/docs/gen_critic_tb_l7.md (frozen, 2f78b6f17d8feb57): the row prefix "CR-L6" in its Sections 2, 5 and 6 reads
"CR-6", the prefix already in use in gen_critic_response_fcov.md (the Orchestrator's correction).

Base verdict re-reviewed here: gen_critic_tb_l6.md (9c2e15956008be26, REQUEST-CHANGES) M-1..M-4, L-1..L-7, and its Section 7 widenings
of M-3 (a retained red of the unit test itself) and M-4 (every counted group refereed) and adopted lows L-8, L-9, L-10.

Artifacts reviewed (committed blobs at ab67c6c; sha256 first 16 hex):

- dv/auto_dv/env/gen_fcov_pkg.sv  fa524e76105e9eee
- dv/auto_dv/tb/unit/gen_ut_fcov_codegen.py  96b92bf6096c6ddc
- dv/auto_dv/docs/gen_component_api_fcov.md  9ebdb5a4f4a22058
- dv/auto_dv/evidence/gen_tdd_fcov.md  c75d152aa929eaaa
- dv/auto_dv/mutations/gen_mut_fcov.md  6cd14a37595b2402
- dv/auto_dv/evidence/gen_critic_response_fcov.md  9977b0c36751f611
- dv/auto_dv/evidence/gen_tdd_logs/gen_manifest.md  1498886a3962d63a
- dv/auto_dv/evidence/gen_tdd_logs/fcov/gen_fu_l8_sources_sha256_x.txt  a48917a3f74eeea3
- dv/auto_dv/evidence/gen_tdd_logs/fcov/gen_fu_l6_sources_sha256_s.txt  9f123de2aa16eb21
- dv/auto_dv/evidence/gen_tdd_logs/fcov/gen_fu_l6_sources_sha256_committed.txt  d1bfc2720e665c94
- dv/auto_dv/evidence/gen_fcov_proof_slice3a.fcov.yaml  000319a4ca554013
- dv/auto_dv/evidence/gen_fcov_proof_slice3c.fcov.yaml  cf285e9ff77e6237
- dv/auto_dv/docs/gen_fcov_plan.md  8514f7e9702e2f18
- the 119 gen_fu_l8_* logs under dv/auto_dv/evidence/gen_tdd_logs/fcov/ (manifest rows recomputed 121/121 with the two l6 lists)

Date: 2026-09-03 (UTC). Role: Critic (reviewer other than the author). Basis: docs/dv/dv_principles.md d9c27db18f511411, LOG-058,
LOG-072, tools/specs/riscv-isa-manual (Zcmp cm.mvsa01 / cm.mva01s expansions), dv/auto_dv/docs/gen_fcov_plan.md Sample lines.
Method: clean archive of ab67c6c. Build x identity checked first-hand: the recipe of gen_tb_local.sh on the archive gives a48917a3f74eeea3
under the UTF-8 sort, equal to the 21 run headers, the compile log and the sha256 of the retained per-file list gen_fu_l8_sources_sha256_x.txt;
the two py files that differ between the retained build-s and committed lists are not in gen_tb.f (no .py line). One unnamed subagent (an
evidence audit of the 121 files, told the fence, kept out of dv/auto_dv/reviews/), its findings re-checked in the blobs. EXPOSURE: the
Orchestrator's hand-off named the landing-7 cross-model artifact's two mediums (the ut_mv_miss_expected copy; the CR-6 M-3 / M-4 rows
reading DONE against my Section 7 widenings; no rows for L-8 / L-9 / L-10) and the subject of commit 6133c77 names that artifact's verdict
level; each item was judged from the code and the logs before the artifact was read. Sections 1-6 were composed before the artifact
was read; their write script failed on a syntax error and was re-run unchanged after the read (disclosed); Section 7 reconciles.

CRITIC VERDICT: REQUEST-CHANGES. Landing 7 closes tb_l6 M-1 and M-2 as mechanisms and the vector half of M-3 and the red half of M-4 with
retained reds on an identified build; three mediums stand: the self-test's exclusion copies the whole run's miss count so the new referee
line cannot fire in the unit-test runs, and the two Section 7 widenings (the unit test's own red; every counted group refereed) are not
built while their rows read DONE. All three are small; the FM11 build already in hand gives the unit test its red.

## 1. What was verified

| item | as built | evidence |
|---|---|---|
| build x identity (tb_l6 M-1) | per-file list retained beside the compile log; the s and committed lists retained, differing in gen_fcov_codegen.py and gen_ut_fcov_codegen.py only (lines 45 and 63), both outside gen_tb.f | recipe = a48917a3f74eeea3 = list sha = 21 headers = gen_fu_l8_compile_x.log:1153; all 67 list lines equal the ab67c6c blobs; the committed list equals the 61c97c1 blobs (audit) |
| move-pair miss counter (tb_l6 M-2) | gen_fcov_pkg.sv:588-591: a legal pair whose second micro-op closes with uop_count_ok na counts n_mv_miss, one GEN_FCOV_MV info per miss; FCOV_QUERY 12; `move pairs:` report line; :1036 referee `n_mv_miss > ut_mv_miss_expected` | red FM11 (the expansion expected with swapped registers: 130 sampled, 68 misses, one GEN_FCOV_REF error, build 1def4880d2bdaa6c = compile log = headers), ablation `+gen_fcov_en=0` PASS; unmutated x: 130 sampled, 0 misses; original sha fa524e76105e9eee = committed blob |
| unit-test vectors (tb_l6 M-3, vector half) | :1019-1024 and the divisor / n_imm / cm.mvsa01 s2,s3 cases: 27 cases | five runs `self-test: 27 cases, 0 failures`; the cases named in the row are the OK lines of gen_fu_l8_ut_isa_cov_zcmp_minstret_stdout_excerpt.log:40-54 |
| referee red (tb_l6 M-4, red half) | :1038 `n_br > 0 && br_cg.get_coverage() == 0.0` | red FM10 (br_cg.sample removed, n_br kept: `gen_isa_branch_cg sampled without coverage`, 1 error, build 1094004eeaa5f94b), ablation PASS |
| proofs on x | 12 manifests re-checked on fresh vdbs | 128 / 122 / 52 / 46 / 38 / 26 / 29 / 65 / 65 / 65 / 22 / 29, every count equal to the l6 result line (audit, line by line) |
| anti_vacuity notes (tb_l6 L-3) | derived from the plan's Sample lines, key set equal to the bins list in all 20 manifests | 14 distinct strings, 1059 notes (my count on the archive) |
| L-1, L-2, L-4, L-5, L-7 | record corrections; the cp_dmem_delay statement; 2^31 and the trap reset of sb_prev_binv (:875); CR-5 rows; the zcb red narrated as unretained | the diff f255b04..ab67c6c, read line by line |

## 2. Closure of gen_critic_tb_l6.md, item by item

- M-1 CLOSED (first-hand above). M-2 CLOSED as a mechanism with FM11; its self-test exclusion is M-1 below.
- M-3: the vector half CLOSED (27 cases, the two divisor pairs, n_imm across the synthetic cm.push, s2 / s3); the Section 7 half OPEN:
  no retained run shows the unit test failing (M-2 below). M-4: the red half CLOSED (FM10); the Section 7 half OPEN: 6 of 14 counted
  groups are refereed (M-3 below).
- L-1, L-2, L-3, L-4, L-5, L-7 CLOSED; L-6 is the plan owner's and is routed. L-8, L-9, L-10 (Section 7 adoptions) have no CR-6 row:
  L-8 not addressed, L-9 closed in substance, L-10 not addressed (L-3 below).

## 3. Findings

### M-1 (medium) [S6 a referee that cannot fail; S4 an undisclosed claim] The self-test exclusion copies the whole run's miss count

gen_fcov_pkg.sv:1025 `ut_mv_miss_expected = n_mv_miss;` runs inside self_test(), which the unit test issues AFTER the program has
retired (gen_component_api_fcov.md Section 9: "boots a program, waits for +gen_ut_boot_retire ... then issues FCOV_SELFTEST";
gen_fu_l8_ut_isa_cov_zc_stdout_excerpt.log:53 self-test at 310500 after 100 retirements, finish at 311500). Every miss the program
produced before the self-test is therefore copied into the expectation, and the referee at :1036 compares the same counter with itself
at report: it cannot fire in any of the five unit-test runs, and the report line "(1 of them the self-test's)" is the copy, not a
measurement. The code comment ("the self-test's own miss is not the run's"), the CR-6 M-2 row and gen_mut_fcov.md say the opposite.
In lockstep runs the self-test never runs and the referee is live (FM11), so the defect is confined to the runs LOG-058 relies on.
Required: count only the self-test's own misses (`ut_mv_miss_expected += n_mv_miss - miss0;`), and retain one unit-test run on the
FM11 build showing the referee fire beside the failing vector cases (that run is also M-2's red).

### M-2 (medium) [S6 trust triad, tb_l6 M-3 widened] The unit test has still not been seen red

The CR-6 M-3 row reads DONE; gen_critic_tb_l6.md Section 7 required, with M-3, a retained run of gen_ut_isa_cov on a sampler-mutant
build (FM4 was named) failing on its vector table. No gen_fu_l8_* log is such a run (the audit found none; the record's "red" is the
in-run vector case "one counted miss", a green assertion). A vector table that has passed on every build it ever ran on is the
unexercised check of S6. Required: the test on FM11 (its cases "cm.mvsa01 s2, s3: the pair over x18 / x19 is well-formed" and the
s7 / s6 case fail by construction) or on FM4, retained with header and verdict, cited in the FM row and in the API doc Section 9.

### M-3 (medium) [S6 mutation-proof, tb_l6 M-4 widened] Eight counted groups are still fed without a referee

gen_fcov_pkg.sv:1036-1042 referees the move-pair misses and six groups (mul, br, zcmp pushpop, csr, sbit, zcb); div, alu_reg, zba_zbb,
alu_imm, shift, bit_count, zca and the zcmp_mv coverage itself are counted (n_div, n_alu_reg, ... in the isa samples line) and never
judged. gen_critic_tb_l6.md Section 7 required "every counted group, and the red"; the CR-6 M-4 row reads DONE on the red alone.
FM10 proves the form; the eight lines are the remaining work. Required: the lines (no further red needed for the same form), and the
row worded as what was built.

### L-1 (low) [S4 record] Record slips

CR-6 L-3 says "1070 notes" where the 20 manifests hold 1059 (1070 is the f255b04 total; the same row says the ablation manifests dropped
notes for removed bins, which is where the eleven went); the quoted unit-test report line "move pairs: 5 sampled, 1 with mismatching
micro-ops" (gen_tdd_fcov.md Section 6, gen_mut_fcov.md) holds for the zc run only, the other four print 3 sampled; the five unit-test
excerpt headers say "(26 vector cases)" against the body's 27; FM10's first compile failed (gen_fu_l8_oot_mutation_batch_fm.log:2) and
the retained catch is the re-run in the fm10 batch, which the record does not say; two build-x runs FAIL in gen_fu_l8_x_driver.log
(lockstep_zcmp_dummy_popret, 9408 errors, the B8 vehicle; lockstep_zcmp_mv_res, 32 errors, the B4 finding's program) with no l8
header or mention in Section 6 (both are reds by design at earlier landings; say so beside the driver log).

### L-2 (low) [S6 retention] Two sentences of the CR-6 M-1 row have no retained line

"landing 2c's shared-tree canary hashed identically to its final build" and "--check up to date on the committed tree" are not backed
by a gen_fu_l8_* or gen_fu_l7_* line (the only --check line, gen_fu_l8_ut_fcov_codegen.log:1, does not name its tree). The second
sentence is true: I ran --check on the 61c97c1 archive for tb_l6. Retain the line or drop the sentence.

### L-3 (low) [S4 record; S5 comments] The Section 7 adoptions have no rows

L-8: the ten comment lines that narrate review history are still there (gen_fcov_pkg.sv:115, 120-121, 687, 955, 970, 975, 979, 989:
"H-1(a) of the landing-4 review", "ruling L5R-1", "the landing-3 major", "LOG-058"); the intent-only rule of the comment standard.
L-9: closed in substance by the API doc's sentence at :205 (the pin read follows the write's commit by GEN_CSR_WRITE_TO_RVFI_OFFSET
cycles), and the constant exists (LOG-072); a row saying so is owed. L-10: Section 9 still does not say that FCOV_QUERY returns the
sampler's counters and the vector table asserts shadow copies of the sample arguments, not covergroup bin state, and its index list
stops at 11 (12, the miss counter, is undocumented).

### L-4 (low) [schema] A plan status marker inside 65 evidence notes

The CG-CSR-002 notes of slice3c and its inv / off variants copy the plan's "(UNBUILT at the Section 0a concordance)" verbatim
(gen_fcov_proof_slice3c.fcov.yaml:71 and 64 more). A status word in an evidence file goes stale silently when gen_chk_csr_readback
lands; derive the note without the status parenthesis, or regenerate the notes with the plan.

### L-5 (low) [S6 mutation hygiene] The canary line does not watch the mutated file

Both fcov batches print `source tree untouched: cc8bc78d76a57505`, the shared tree's gen_rvfi_pkg.sv, per the convention of
gen_tdd_step2b.md:377-380; for a gen_fcov_pkg.sv mutant the file worth watching is the shared tree's gen_fcov_pkg.sv. The original
sha lines identify the mutated copies, so nothing is in doubt here; make the canary the mutated file's shared-tree copy from the next
batch on.

### Informational

- I-1: the FM11 build is a ready-made red vehicle for the unit test (M-2) and for M-1's referee at once.
- I-2: the referee line numbers in the mutant errors (1036, 1038) equal the unmutated file's, consistent with sample-line removals
  that do not shift the referee block.

## 4. Principles check

dv-principles-check (docs/dv/dv_principles.md d9c27db18f511411): S6 trust triad: FM10 / FM11 with ablations on identified builds
(conforming); one referee line vacuous in the unit-test runs (M-1); the unit test without a red (M-2); eight groups without a referee
(M-3). S4 honesty: the DONE rows on the widened items and the exclusion comment contradict the code (M-1, M-2, M-3); the record slips
of L-1. S5 comments: L-3 (L-8 carried). One-line verdict: FAIL on M-1..M-3 until fixed.

## 5. Required for re-review

1. M-1: the exclusion counts the self-test's own misses only; a unit-test run on FM11 retained (referee fires, vector cases fail).
2. M-2: that run, or one on FM4, cited as the unit test's red.
3. M-3: referee lines for the eight remaining groups; the CR-6 M-4 row worded as built.
4. L-1..L-5 with the same touch (record edits; the canary from the next batch on).

## 6. Verdict

CRITIC VERDICT: REQUEST-CHANGES (M-1, M-2, M-3). tb_l6 M-1 and M-2 are closed; M-3 and M-4 are closed in the halves Section 3 of tb_l6
asked for and open in the halves its Section 7 added. The landing's evidence is identified file by file and its reds are real.

## 7. Reconciliation with the cross-model artifact (dv/auto_dv/reviews/2026-09-03-claude-diff-f255b04a-ab67c6c9.md, read after Sections 1-6 were composed)

APPROVE-WITH-CHANGES, two mediums and four lows. Its verification of FM10, FM11 and the vector cases agrees with Section 1.

- Its first medium is my M-1 (the same line, the same fix `ut_mv_miss_expected += n_mv_miss - miss0`); it adds that the five retained
  unit-test runs happen to have no real miss, so nothing is hidden today, which I accept and which does not change the level: the
  referee is vacuous by construction in those runs and the row says otherwise.
- Its second medium is my M-2 and M-3 together (the CR-6 M-3 / M-4 rows DONE against the Section 7 widenings, the referee block
  judging six groups, the FM4 row without a unit-test run) and names the missing L-8 row, my L-3.
- Its four lows are inside my L-1 (1070 against 1059; the "26 vector cases" headers and the "5 sampled" quote; FM10's failed first
  compile; the dummy_popret run absent from Section 6). I add the zcmp_mv_res run to the last.
- Not in the artifact: L-2 (the two unretained sentences), L-4 (the UNBUILT marker in 65 notes), L-5 (the canary file), the L-9 /
  L-10 parts of L-3.
- Verdict disagreement, stated: the artifact approves with changes; I hold REQUEST-CHANGES because two mediums of the base verdict
  remain open while their rows read DONE, and a REQUEST-CHANGES stands until every medium is addressed. The changes both verdicts
  ask for are the same three lines of work.
