# Critic verdict: Test Writer batch 3 (gen_pmp_mseccfg, gen_pmp_lock), v2 FINAL on the consolidated touch 5e6186c (diff base ae5e58a)

Review chain: batch3 v1 on e7a0941 (gen_critic_tests_batch3_v1.md, REQUEST-CHANGES); v2 interim on 36e2694 (this file's earlier,
uncommitted text, REQUEST-CHANGES, held for the consolidated touch; its verdict line and finding ids are recorded in Section 6);
this FINAL on 5e6186c supersedes the interim.

Artifacts reviewed (committed blobs at 5e6186c; sha256 first 16 hex):

- dv/auto_dv/tests/gen_programs/gen_pmp_lock_prog.py  56ef5fe5f695106b
- dv/auto_dv/tests/gen_test_pmp_lock.py  29c1be4e19212597
- dv/auto_dv/fcov_expectations/gen_test_pmp_lock.fcov.yaml  4969c88e9f8cdc14
- dv/auto_dv/tests/gen_programs/gen_pmp_mseccfg_prog.py  672078f2f97512f8
- dv/auto_dv/tests/gen_test_pmp_mseccfg.py  98111e02e4a0edcb
- dv/auto_dv/tests/gen_fixtures/gen_run_fixture.sh  36f35d3610e709e9
- dv/auto_dv/tests/gen_test_csr_reset.py  f2aaf03af727ca30
- dv/auto_dv/evidence/gen_tdd_batch3.md  a377acfa9b560d61
- dv/auto_dv/evidence/gen_critic_response_batch3.md  0c99ef24f92178a9
- dv/auto_dv/evidence/gen_critic_response_batch1.md  4cd78aee58ee0141
- dv/auto_dv/evidence/gen_tdd_logs/test_writer/gen_manifest.md  5cb24c84ec8a8c91
- the 83 added logs under dv/auto_dv/evidence/gen_tdd_logs/test_writer/ (gen_b3_pmp_lock_*, gen_b3_pmp_mseccfg_*; manifest rows recomputed)

Date: 2026-09-03 (UTC). Role: Critic (reviewer other than the author). Basis: docs/dv/dv_principles.md d9c27db18f511411,
DV_prompt.txt, gen_test_plan.md items TP-PMP-011..030 / 108 / 112, the Smepmp specification (tools/specs/riscv-isa-manual/src/priv/machine.adoc
:2383-2462, :3541-3549), rtl/ibex_cs_registers.sv:1463-1514, my v1 and interim v2 findings.
Method: clean archive of 5e6186c; library self-test PASS (the structure check of both modules), flow self-test PASS, --check-red-signatures
PASS; both fcov manifests byte-identical to a --test-module re-render; my own reproduction with the archived generators: the new
gen_pmp_lock_prog plan() over seeds 1..150 green and seed-drawn red plus --red-item TP-PMP-013 over seeds 1..60 (360 plans, 0
assertion failures), the ae5e58a generator asserting at exactly seeds 36, 57, 79, 91, 100; the gen_pmp_mseccfg programs at 5e6186c
byte-identical to 36e2694's for seeds 1..3 and seed 1 with --red-item TP-PMP-027 / 028 / 029 (so the retained mseccfg red runs stay
valid), and different at seed 18 --red-item TP-PMP-028 (the gated site). One unnamed subagent audited the 83 logs, the manifest and
the sweep files, told the fence and kept out of dv/auto_dv/reviews/. The cross-model artifact for this commit was not read before
Sections 1-4 (no exposure to it: the git log listings I saw earlier predate the commit); Section 5 reconciles.

CRITIC VERDICT: APPROVE, with three lows. Both mediums of the interim and the medium of v1 are closed by mechanism and proven
on retained runs; every low of v1 and the interim is closed or truthfully stated.

## 1. Closure of my earlier findings (verified in the blobs and the logs)

| id | finding | closure | verified how |
|---|---|---|---|
| v1 M-1 / CR-B3-M-1 | the seed-drawn mseccfg red could pick the not-built TP-PMP-108 (inert at seeds 8, 27) while the docstrings said every red fails its own item | mechanism in 3j (RED_ITEMS; an explicit TP-PMP-108 red fails through fire_program_verdict); the docstring completed here | gen_pmp_mseccfg_prog.py docstring names RED_ITEMS and the 108 path; gen_b3_pmp_mseccfg_sweep30.log: 450 runs, 0 failures, seed_drawn_108=0, generator sha 672078f2f97512f8 = the committed file |
| interim M-1 / CR-B3v2-M-1 | the TP-PMP-013 red replaced a write to an all-locked word (19 of 40 seeds) or a no-op RMW by a read, unobservable by the spec | a 013 site only where the write changes an unlocked lane (`changed` lane filter, gen_pmp_lock_prog.py); `csr_op` asserts for EVERY skipped write of every item that the modelled read-back moves | code read; the assertion caught a vacuous TP-PMP-021 site in the before-fix sweep (gen_b3_pmp_lock_sweep800_before_fix_err.log: "red TP-PMP-021 rlb1 rewrite cfg csrrs: the skipped write changes nothing"); 40 pinned-red runs r013_s1..s40 each fail on fire_tp_pmp_013 alone (4 none-lock-mix / 36 some-lock-mix seeds), 37 greens g4..g40 plus s1..s3 PASS, all on out_head14 with sources 893384b8eec4e6d5, template abbe6fcb78e53a27 and the new test_sha 29c1be4e19212597 = gen_test_pmp_lock.py at 5e6186c |
| interim M-2 / CR-B3v2-M-2 / CM38-MAJ-1 | plan() raised "TP-PMP-016: the reserved locked non-TOR neighbour is not available" at seeds 36, 57, 79, 91, 100 | the ntor role drawn only from kept locks whose lower neighbour is not the other kept lock, asserted; two further planner defects fixed with it (a TOR lock above TP-PMP-015 / 017's entry freezing its pmpaddr; the TOR roles kept below the top entry) | my reproduction: the ae5e58a generator asserts at exactly those five seeds; the 5e6186c generator has 0 assertion failures over 360 plans; the retained sweep gen_b3_pmp_lock_sweep800.log: 2200 plan runs (800 seeds x green + red, 10 items x seeds 1..60), 0 failures, generator sha 56ef5fe5f695106b = the committed file |
| interim L-1 / CR-B3v2-L-1 | both docstrings claimed every red fails its own item | each docstring now names the rule that makes the claim true (RED_ITEMS; the observable-site rule and the assertion) | read |
| v1 L-2 / interim L-2 | the two reachable transitions the walk never generates unnamed | named with the reason (every walk write toggles one bit) in gen_test_pmp_mseccfg.py and gen_tdd_batch3.md Section 3 | read |
| v1 L-1 / interim L-3 | sweeps and generator hashes prose only | gen_b3_pmp_mseccfg_sweep30.log, gen_b3_pmp_lock_sweep800.log, the before-fix sweep and its stderr, gen_b3_pmp_lock_h13_run_summary.log retained with manifest rows; headers carry the generator shas | manifest 641/641 rows recompute (83 added); the generator shas equal the committed files |
| interim L-4 | two bins_not_hit entries were per-seed variants, not rule (g) preconditions | TP-PMP-112's adjacent write is the pmpcfg variant on every seed (one RLB clear per power-on); rlbclr_then_cfg declared and hit every seed (bins 50), rlbclr_then_addr a rule (g) entry naming the precondition the test does not apply | manifest re-render identical; the 40 greens report bins=50 |
| interim L-5 / CM38-MIN-1 | MMWP hand-encoded as 2 | MSECCFG_MMWP imported | read |
| interim I-1 | "seeds 1 and 2" schedule wording | Section 4 states each seed's reached / applied | read (s1 6 of 6, s2 6 of 15, s3 12 of 12 with 6 mid-run phases, matching the logs) |
| interim I-3 / CM38-MIN-2 | raw pmpcfg decoding in nine places | locked() / mode() helpers over prog.byte_fields | grep: no raw L or A mask left in gen_test_pmp_lock.py |
| v1 L-3 / CR-B3-L-3 | TP-PMP-108 read-backs uncompared | fire_program_verdict compares them as program integrity (3j) | unchanged since the interim |

TP-PMP-112 is pinned to the pmpcfg variant (CLR_VARIANT = "cfg") and its red fails on fire_tp_pmp_112 with the adjacent-cfg mismatch
(red_112 excerpt). The run header now carries test_sha beside template_sha (gen_run_fixture.sh), which closes my
gen_critic_batch1_v8.md L-2 for this family of runs.

## 2. New evidence checked

- 91 simulation runs on out_head14 (an export of 2ea81ac; the TB paths unchanged through d4b5933 per the transcript, sources
  893384b8eec4e6d5 = the landing-4 build k recipe hash I verified in gen_critic_tb_l4.md): 40 greens PASS with UVM_ERROR 0 and
  GEN_TEST_BINS n=50; 51 reds each with exactly one ok=False line naming the run's own item; the pinned red retained in full
  (gen_pmp_lock_red1_stdout.log / _sim.log) and RED-OK under --check-red-signatures. Every header's seed equals the file name's
  and the GEN_TEST_SEED line's.
- The mseccfg red excerpts are the 36e2694 runs (out_head8, no test_sha); they stay valid because the programs are byte-identical
  (my reproduction, and the sweep header's statement); the seed-18 TP-PMP-028 red changed with the gating, as the retained
  probe log shows (the ungated generator asserts "lane 0 of pmpcfg2: the deviated write reads back as the planned one").
- The staged testlist entries (gen_test_pmp_mseccfg, gen_test_pmp_lock at tier check, measured false, reds pinned to TP-PMP-011
  and TP-PMP-013) are still in the work tree by agreement (CR-B3-I-3); they merge after this verdict and the flow's
  red_signature_check re-verifies red_expect against the retained pinned reds then.

## 3. Findings

### L-1 (low) [S4 record] Three of the four pre-fix green defects are prose only

gen_tdd_batch3.md Section 5 describes green failures at seeds 7, 17, 29 and 35 of the 36e2694 generator ("7 of 8, 8 of 9",
"entry 10 read back locked TOR: False"); the only retained failing line is the r35 plan() assertion in the before-fix sweep's
stderr. Retain the failing lines of the other three (or state that they were observed in unretained runs).

### L-2 (low) [S6 evidence identity] The before-fix sweep's generator is an intermediate text

gen_b3_pmp_lock_sweep800_before_fix.log names generator sha256 7fead94e4693c62a, which is neither the 36e2694 file
(8d203d15091624a2) nor the committed one (56ef5fe5f695106b): the sweep ran on an intermediate generator that already had the ntor
fix. State that in the transcript sentence that cites it (the sweep proves the csr_op assertion fires, not the state of 36e2694).

### L-3 (low) [S6 reproducibility] The random and flow-derived seed lists are not retained

The sweep header gives the RNG specification (random.Random(2026); gen_flow_util.derive_seeds('gen_test_pmp_lock', 200, 20260903))
but not the 400 seeds themselves; a reader must re-derive them to reproduce failed_seeds=[]. Retain the list in the log.

### Informational

- I-1: the csr_op assertion is a generator self-check that fires on a vacuous site; it was exercised (the r35 TP-PMP-021 site),
  so it is a tested guard, not a declared one.
- I-2: the 2200 figure is generator plan() runs (800 seeds x green and seed-drawn red, plus 10 items x seeds 1..60), not
  simulations; the transcript says "generator sweep", and the 91 simulation runs are the sim evidence.
- I-3: gen_test_csr_reset.py's Knobs sentence now says debug_req_regime belongs to TP-CSR-108 alone (my gen_critic_batch1_v8.md L-3).

## 4. Principles check

dv-principles-check (docs/dv/dv_principles.md d9c27db18f511411): S1 stimulus: the planner explores its state space without
aborting (0 of 360 plans here, 0 of 2200 retained); S4 honesty: the docstrings now state the red rule that holds; the sweeps
and their generator shas are retained (L-1, L-2 are record-precision items); S6 trust triad: every red proven non-vacuous by
construction (the assertion) and by 51 retained red runs each failing on its own item; the fcov manifest declares 50 bins hit
by every retained green and one rule (g) exclusion with its precondition. One-line verdict: PASS.

## 5. Reconciliation with the cross-model artifact (dv/auto_dv/reviews/2026-09-03-claude-diff-ae5e58ab-5e6186c0.md, read after Sections 1-4 were written)

APPROVE-WITH-CHANGES: one low, three infos; no medium or high. Its reproductions agree with mine (the ae5e58a generator aborts at
seeds 36, 57, 79, 91, 100; the HEAD generator builds every plan; the mseccfg programs byte-identical for the retained runs; the
seed-18 TP-PMP-028 site moved by the gating; the 013 mix 4 none / 36 some over seeds 1..40), and its reading of every red site
of both generators through csr_op / the observable filter matches Section 1.

- Its low: gen_tdd_batch3.md:183 attributes the seed-7 defect to the 36e2694 generator, which did not exhibit it (the hazard
  surfaced only after the variant pin changed the post-P2 draws). Adopted as L-4 (record precision; the same class as my L-1 and
  L-2): reword to "36e2694 carried the 021 no-op rewrite and the latent TOR-above hazard".
- Its first info: the generator docstring's "csr_op asserts it for every skip" overstates, since the TP-PMP-112 skip in
  p2_rlb_clear emits the csrr directly (verified, gen_pmp_lock_prog.py:391-400) and the artifact reads the TP-PMP-020 skip the
  same way (artifact-quoted); both are observable by construction. Adopted as L-5: say "every csr_op skip; 020 and 112 by
  construction".
- Its second info (the class comment "one run cannot reach" vs the docstring's "precondition this test does not apply") and its
  third (the rlbclr_then_cfg bin's adjacency assumption for the future cp_bb sampler, to be counted over consecutive PMP CSR
  writes rather than consecutive records) are carried as its own; the third is a note for the covergroup author.

Mine that the artifact does not carry: L-3 (the random and flow-derived seed lists not retained).

## 6. The superseded interim (36e2694), for the record

CRITIC VERDICT (held for the CM32 / CR-B3 rows touch): REQUEST-CHANGES on two mediums. The mechanism half of my batch3 v1 M-1 is closed (the seed-drawn red targets built items only, an explicit --red-item TP-PMP-108 now fails on fire_program_verdict, which compares the 108 read-backs, and the red is retained), and the new module gen_test_pmp_lock is built as claimed with intent-derived checks, 11 reds and three greens. Two things stop an APPROVE: the pmp_lock red form has the defect batch3 v1 found in its sibling, in a seed-dependent form (the TP-PMP-013 red replaces a write to an all-locked word by a read on about half the seeds, which the spec says changes nothing, so that red passes green), and the pmp_lock planner raises an assertion on some seeds before any stimulus runs. Three items of v1 are not done although the landing says they are: the two docstrings still claim every red fails its own item, the two reachable-but-never-generated transitions are not named, and the sweep and generator hash remain prose.
- M-1 (medium) [S6 a check never exercised to fail is not trusted; S4 honesty] The pmp_lock red for TP-PMP-013 replaces "a lock-mix word write" by a read of the same CSR; on 19 of the 40 seeds I enumerated (2, 3, 4, 6, 7, 8, 11, 12, 15, 16, 17, 18, 20, 22, 24, 25, 31, 33, 38) the drawn site is a write to a word whose lock mix is "all" (the generator's own red_note, e.g. seed 3: "the csrrc to pmpcfg3 (all lock mix) is replaced by a read (idx 83)"), and machine.adoc:3541-3542 says such a write is ignored, so the read-back equals the green expectation and the red passes; the subagent's instrumented model adds two seeds where a csrrc with no unlocked lane set is a no-op (14, 19), 21 of 39 buildable seeds in all (D). The retained pinned red at seed 1 hit a "some" site and failed correctly, so the committed evidence is valid but seed-fragile, and gen_test_pmp_lock.py:41-42 ("Each red fails exactly its item's fire_tp_pmp_<nnn>") is false for 013 on those seeds. This is the class batch3 v1 M-1 found in the sibling generator, one landing later. Required: the 013 red draws a site whose write changes at least one unlocked lane (a "some" or "none" mix with a non-empty operand), asserted in the generator, with the docstring's claim made true; the same audit for every red site of both generators (a red whose deviation the spec makes unobservable is not a red).
- M-2 (medium) [S1 a test explores its state space; S6] gen_pmp_lock_prog.plan(seed) raises "AssertionError: TP-PMP-016: the reserved locked non-TOR neighbour is not available" for seeds 36, 57, 79, 91 and 100 of 1..100 (reproduced from the archive); report_count() calls plan(self.seed), so those seeds abort in the template before any stimulus. Cause (D): assign_roles draws the non-TOR neighbour from the "clear" set and protects only its lower entry, so two adjacent clear entries leave no candidate. The transcript's 30-seed sweep stops one seed short of the first failure. Required: the role assignment excludes the case (or retries the draw) with a sweep that covers it, and the sweep is retained (L-3).
- L-1 (low) [S4 honesty; v1 M-1 wording half] The two docstrings still make the claim the v1 medium showed false: gen_pmp_mseccfg_prog.py:31-32 "so exactly that item's fire-check fails" and gen_test_pmp_mseccfg.py:48-49 "each red fails exactly its item's fire_tp_pmp_<nnn>" (the 108 red fails on fire_program_verdict, not an item's method); the only corrected sentence is the 108 read-back one at :25-27. The landing message says the docstrings were corrected; they were not.
- L-2 (low) [S4 record; v1 L-2] The two reachable transitions the walk never generates (s001 -> s111, s101 -> s110) are named nowhere in the generator, the test, the plan or the transcript (grep over all four); only the nine unreachable ones are listed. The Orchestrator's relay listed this among the 3j items; it is not done.
- L-3 (low) [S6 evidence is committed; v1 L-1] No sweep log, no sweep summary and no generator hash is in the commit for either module (the transcript cites batch3/gen_pmp_mseccfg/sweep.log and batch3/gen_pmp_lock/gen_sweep30.log under the git-ignored work tree; "byte-identical before and after" names no digest); the manifest has no such row (D). The landing message says the sweep and hash were retained; they were not. Counts as nothing; retain the logs with the generators' sha256 or drop the numbers.
- L-4 (low) [S4 FCOV; rule (g)] Two of the five bins_not_hit entries (gen_pmp_recfg_cg.cp_bb.rlbclr_then_cfg / _then_addr, "one RLB clear per run; the adjacent-write variant is drawn per seed") are not preconditions the test does not apply: the test applies the clear on every seed and hits one of the two bins per seed. The reason is honest, but rule (g) (gen_fcov_plan.md:39-43) is written for a precondition a test never applies; either rule (g) gains a per-seed-variant clause or the variant is split so each seed's bin is declared. The other three (MML = 0 at the clear; MMWP never set, twice) are rule (g) cases as written. (D)
- I-1 (info) The retained pmp_lock greens ran at seeds 1..3; seed 2's nine later schedule entries fall after the end of test (the transcript's "seeds 1 and 2" wording includes seed 1, which reached all six of six). (D)
- I-2 (info) The eight sim.log files carry no run header (the VCS Command line names the build directory and the seed but no sources sha); the stdout headers do. Fine as long as the pair is read together.
