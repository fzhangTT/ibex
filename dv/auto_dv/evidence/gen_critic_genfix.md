# Critic verdict: feature group generator-fixes, range 2897920..4017573

Artifacts (sha256 first 16 at the range end 4017573 unless stated):
- dv/auto_dv/tests/gen_programs/gen_bit_ratified_prog.py 14405978b07de2a4 (first 12: 14405978b07d, the pinned digest)
- dv/auto_dv/tests/gen_programs/gen_cmp_zca_prog.py b31555f595b4ab35 (first 12: b31555f595b4, pinned)
- dv/auto_dv/tests/gen_programs/gen_pmp_csr_warl_prog.py 964e232edfb4d294 (first 12: 964e232edfb4, pinned)
- dv/auto_dv/evidence/gen_tdd_logs/test_writer/gen_fu_generator_fix_sweep.log 27fb3e6254861058
- dv/auto_dv/evidence/gen_tdd_logs/test_writer/gen_fu_shape_check.log f4a432647ba0c3fc
- dv/auto_dv/evidence/gen_tdd_logs/test_writer/gen_fu_irq_red_observability.log d205fa17cedb62e9
- dv/auto_dv/evidence/gen_tdd_logs/test_writer/gen_fu_warl_res_backstop.log 97eee2f4d94593d1
- dv/auto_dv/evidence/gen_generator_sweep/gen_index.md (de60b81) 8d719e17d10fadb4
- dv/auto_dv/tests/gen_fixtures/gen_run_fixture.sh (7751329) ace92ec2a8dad911
- dv/auto_dv/evidence/gen_tdd_batch3.md (Section 16 and the corrigenda) 1a0a70e7b0a82956
Date: 2026-09-05T09:00:53Z. Role: Critic (the reviewer other than the author). Range named by the Orchestrator: 2897920..4017573; the
group is 0b16018 (the retirement-floor identity, judged within the irq-entry group at gen_critic_irq_entry.md Sections
2 and 7 and taken as approved here), 7751329 (the fixture's cocotb-config refusal), de60b81 (the Runtime Manager's
retention of the two sweeps) and 4017573 (the three generators, five retained logs, Section 16, three review rows).
Other commits inside the range belong to other groups and take no verdict here. Method: every diff read in full; the
retained logs' figures re-derived from the primary artifacts they cite (the 94 + 80 run directories under
/proj_soc/user_dev/fzhang/ibex_dv_out/regress_gensweep2 and regress_gsfix2, the two probe roots, each run's own urg
report); the retained scripts extracted from the logs and re-run; the generators run from a detached worktree of
4017573 and from an archive of 8559958; my logs under dv/auto_dv/work/critic/genfix/. Exposure: the Orchestrator's
messages summarised rev55's rows (one Medium on the shapes verified at model level only, three Lows, one Info) before I
read the diff; every finding below is my own measurement, and rev55 itself is read only in Section 6.
dv_principles.md sha256 d9c27db18f511411, unchanged.

## 1. The headline claim, reproduced from the run directories

The claim: the nine thin declared bins (seven of gen_test_bit_ratified, two of gen_test_cmp_zca) are hit at every one
of forty seeds with the fixed generators, on seed sets byte-identical to the pre-fix sweep, and the committed generator
blobs hash to the digests the re-run was pinned to, so the measurement transfers to 4017573.
- The pinned digests: the three committed blobs at 4017573 hash to 14405978b07d, b31555f595b4 and 964e232edfb4, and
  the same three files inside the built post-fix root /proj_soc/user_dev/fzhang/ibex_dv_probe/gensweep_fix hash the
  same; the pre-fix root holds 7f3ec33390c2, aaa8e29f7370 and 964e232edfb4, as the sweep log states.
- grade.py and integrity.py, extracted from the sweep log, hash to the log's 44d75d6f6a88 and b8005d90a5b9 (with the
  trailing newline). Run as retained over regress_gsfix2: 80 runs, 0 provenance problems, one manifest md5 per entry
  equal to the committed manifests (62d640791b30..., 9348080762...), bit_ratified 40 of 40 PASS with 617 declared
  bins and 0 missed on any seed, cmp_zca 40 of 40 with 300 and 0 missed; the seven bins' per-run count ranges are the
  log's to the digit (1/5, 1/6, 2/6, 1/6, 1/7, 1/7, 2/7); UVM_ERROR 0, UVM_FATAL 0, cocotb failed 0, timed out 0,
  marker 40/40 for both. The same scripts pointed at regress_gensweep2: cmp_zca 25 PASS 15 FAIL with c_swsp_x8_15
  unhit on 9 and c_swsp_x3_7 on 6; bit_ratified 23 FAIL and the seven bins unhit on 12, 8, 5, 4, 3, 3 and 2 seeds with
  the log's count ranges. The out-tree holds 41 bit_ratified result files, the 41st a fixedroute_1909560559 probe run
  of a sweep seed (PASS, same root), which the log's "40 runs" excludes without saying so (L-2).
- The two withdrawn-guard measurements the index carries by bin name: read with the flow's own checker over the forty
  pre-fix reports, cr_op_rs1.zext_h_pos_rand HIT in 28 of 40 (1 to 4 per run) and cp_single_pos.p16 in 40 of 40 (3 to
  5). Both exact.
- The testbench-delta control: the three covergroup blocks are byte-identical between the two roots' rendered include
  (my extraction hashes 003d35170d67, a8c3d25f8681, 3aa819083eae in both), while the roots' TB-source identities
  differ as the log says. The caveat is disclosed in the log, the index and Section 16.
- The retention: the three index files hash to the sha256 the index table gives; the five new logs' sizes and md5s
  match their manifest rows; every file of the four commits is ASCII-clean.

## 2. The declared-bin fixes, traced

- bit_ratified. _plain_rand rejects the six named exact values and any value whose bits 7 and 15 differ, which is the
  sampler's classification of the rs1 class (the six exact classes and byte_msb/half_msb), so pos_rand/neg_rand draws
  land in the class the label says. The directed five-bit cpop operand gives result 5, in no other cp_result bin. The
  pack family's reference matches rtl/ibex_alu.sv:565-567 (packu {b[31:16], a[31:16]}, packh {16'h0, b[7:0], a[7:0]},
  pack {b[15:0], a[15:0]}). X0_RATIFIED now excludes the three pack mnemonics that X0_DRAFT already probes; the sweep
  shows no declared bin lost by it (0 missed of 617).
- cmp_zca. One directed sp_ls unit places a c.swsp source in each register range (x3-x4, x8-x15, x16-x27), which is the
  two cr_insn_rdfull legs; the n16 clones and the n16_ct unit are additive and every original keeps its 32-bit report
  store as successor, as the comments state and the 0-missed sweep confirms for the n32 legs.
- PMP WARL backstop. My own 301-seed comparison (the failing seed 230969025 then 300 from 218090305), running the
  generator at 8559958 (blob 7f062657722d) and at 4017573 side by side from archives: the old asserts at exactly the
  four seeds the log names with the log's phases (230969025 mml0, 218090405 mml1, 218090460 mml0, 218090484 mml0),
  the new asserts nowhere, and the other 297 programs are byte-identical. The WARL leg's 14 pre-fix-root runs are
  14 PASS in the run directories.

## 3. The model-level instruments, run and weighed

- gen_shape_check.py, extracted from its log: red on an archive of 8559958 (RED: 56 failure(s), exit 1) and green on
  the 4017573 worktree (exit 0), as the log states. What the instrument measures is another matter; see Section 5 M-1.
- gen_irq_red_check.py, extracted from its log: green at 40 seeds on the 4017573 worktree, "checks 4600, failures 0,
  RED-OBSERVABILITY: PASS"; the MUT-NOCHECK control on an archive of 4017573 with the mcause fact removed: "checks 575,
  failures 20", twenty lines "the red vector's failing facts are []", exit 1, the log's figures to the digit. The
  irq entry's L-6 model half is real; its simulated half stays with the round-2 wave as disclosed.
- gen_fu_mepc_identity_sidecar.md: the symbols-block digest 70f98779d358 is the one my own build reported in
  gen_critic_irq_entry.md 7.4; the companion cites it as a cross-check and not a source. L-7 of that verdict is closed.
- gen_run_fixture.sh at 7751329: with a PATH holding only the site Python 3.9 and the venv linked into the worktree,
  the script refuses "cocotb-config resolves to /tools_soc/.../python-3.9/bin/cocotb-config, outside
  /localdev/fzhang/ws/ibex-challenge/.venv" and exits 2; with the clone's venv on PATH it passes the check and fails
  later for the expected other reason (no simv); the pre-fix script on the same stripped PATH runs on silently to
  "simv_exit=127" and exits 0. Red and green as the log states.
- gen_test_lib.py --self-test PASS at 4017573; py_compile of the three generators and the library passes.

## 4. Conformance (dv_principles.md, re-hashed)

Stimulus additions are directed where a declared bin must hold per run and random elsewhere; the collected mechanism
that decides a run (the coverage check) is what refused the pre-fix runs and passed the post-fix ones, not a script's
reading; the record keeps the two instruments apart in Section 16. The gap is in Section 5: a claim of settlement by
simulation that the simulation artifacts contradict, and a generator comment that the emitted program contradicts.

## 5. Rows

- M-1 (Medium, records and manifests; Test Writer, with the DV Lead for the manifests). The shape-check log says "The
  bins themselves are settled by simulation in the companion retained log gen_fu_generator_fix_sweep.log, where both
  entries hit every declared bin". The 46 stimulus-class shapes it targets are the manifests' "# not_hit ... stimulus:"
  comment lines (24 bit_ratified, 22 cmp_zca), not declared bins, so no run's fcov_check.log carries a line for them
  and the sweep settles nothing about them. I read them out of every run's own urg report with the flow's checker
  (ci/check_fcov_expectations.py --report-dir on the retained variable-form report, a synthetic manifest naming the 46):
  44 of 46 are HIT in 40 of 40 runs BEFORE the fix and 40 of 40 after; 2 of 46 are UNHIT in 40 of 40 both before and
  after (gen_bit_sbit_cg.cp_binv_twice.yes, gen_cmp_imm_edges_cg.cp_cj_off.self). Raw report attribution: in the
  pre-fix run gen_test_bit_ratified_100600133 the gen_bit_zba_zbb_ops_cg group reads cr_op_same 42 of 42 covered and
  cp_same_regs 3 of 3, and a cmp_zca pre-fix report reads c_add_n16 3, c_beqz_n16 1, c_sw_n16 1. So (a) the manifests'
  not_hit reasons "never pairs", "never applies", "at some seeds only" are wrong for 44 bins that this stimulus hit at
  every seed of both sweeps, and those bins are undeclared coverage the round will not credit; (b) the shape-check red
  at 8559958 (35 shapes at 0 of 40 seeds, 10 rare) is not a measurement of the bins: the pre-fix program at seed
  100600133 contains 13 r-form Zb instructions with rd == rs1 == rs2 (one per op: andn, xnor, orn, sh2add, packu,
  sh3add, packh, min, max, maxu, minu, sh1add, pack) where the reader reports max_all_same at 1 of 40 seeds, so the
  reader misses an emission path of the generator it models. Fix: re-render both manifests from a 40-seed block so the
  44 become declared bins; correct the sentence and the Section 16 "settled by simulation" framing by corrigendum;
  before the shape checker is used as evidence again, calibrate it against a simulated block (the second calibration
  arm Section 14 itself prescribes for the withdrawn mapper).
- M-2 (Medium, generator; Test Writer). _binv_twice_pair's docstring says "the two ops are adjacent and operate on one
  register", and the shape check books the pair at 40 of 40 seeds. The emitted program at seed 100600133 places the
  first binvi's report store between the two: "binvi ... / sw x13, 0(x6) / binvi ...". The sampler's rule at
  gen_fcov_pkg.sv:1573 is "binv / binvi right after binv / binvi on the same rd and index" over consecutive records,
  so the store defeats it and cp_binv_twice.yes is UNHIT in 40 of 40 post-fix runs (Section 5 M-1's measurement). The
  fix the shape check "proves" does not reach its bin. Fix: emit the second binvi before the first's report (or report
  once after the pair) and prove it on a run's own urg report, the way the declared bins were proved. cp_cj_off.self
  (0 of 40, "not measurable here" to the reader) needs the same simulated proof if it is claimed.
- L-1 (Low, tooling). The refusal at 7751329 resolves the venv as $ROOT/.venv, the script's own tree, so the documented
  detached-archive method (an export root plus a tools/spike link) now exits 2 "no .venv under <archive>" until a
  .venv link is added beside it; my runs needed that link. State the requirement in the script's header beside the
  spike one, or accept the clone venv through GEN_TB_PYROOT.
- L-2 (Low, records). The sweep log's pre-fix census says "gen_test_bit_ratified: 40 runs" while regress_gensweep2/runs
  holds 41 result files for that test (fixedroute_1909560559, a probe run of a sweep seed, PASS, same root); the
  seed-set figures are right, the run census should name the extra directory.
- L-3 (Low, records). The shape-check log's class table calls ten shapes "produced but rare" and says their manifest
  reasons "reason says never ... which the measurement contradicts"; the measurement it means is the reader's own,
  which Section 5 M-1 shows is not a measurement of what the bins classify. Withdraw or re-base that paragraph with the
  corrigendum.
- Info. The floor identity (0b16018) is judged at gen_critic_irq_entry.md Sections 2 and 7 and stands; the fixture
  refusal and the sweep retention are approved above; the cocotb-config refusal's other three consumers are stated as
  others' in the log.

CRITIC VERDICT: REQUEST-CHANGES, confined to M-1 and M-2 (the 46-shape leg: the "settled by simulation" claim, the
manifests' not_hit lines that the sweeps contradict, and the binv pair that does not reach its bin). APPROVED within
the group: the nine declared-bin fixes and their 80-run measurement, reproduced from the run directories with the
retained scripts; the digest transfer to 4017573; the WARL backstop, reproduced over 301 seeds; the red-observability
assertion with its control, reproduced to the digit; the sidecar identity companion; the fixture refusal, red and
green reproduced; the Runtime Manager's retention with its two guard measurements, reproduced. Re-review on the
manifest re-render and the binv pair; the shape checker's next use as evidence needs a simulated calibration.

## 6. Reconciliation with the cross-model range review rev55 (written 2026-09-05T09:02:31Z)

Artifact: dv/auto_dv/reviews/2026-09-05-claude-diff-2897920f-40175738.md, committed d2f34d4, sha256 d898d07bb0d348e1,
50 lines, verdict APPROVE-WITH-CHANGES, read after Sections 1-5 were written.

Agreement. rev55 verifies the same digest transfer, retention rows, root cause (bit_rs1_cls by value against
_plain_rand), cpop, PACK_REF against the ALU arms, the c.swsp ranges, the WARL backstop, the seed identity and the
bounded testbench delta, the floor identity and the fixture refusal, all of which Sections 1-3 reproduce from the
primary artifacts. Its Medium is my M-1's claim half: the 46 stimulus-class shapes are not_hit comment lines, not
declared bins, so "settled by simulation" is over-broad and the manifests must be re-rendered from a 40-seed block and
credited then. My M-1 adds what the retained runs say about those shapes (44 hit at 40 of 40 before and after, 2
unhit at 40 of 40 after) and that the shape reader misses the generator's own emissions, which is why my verdict word
is REQUEST-CHANGES where rev55 routes the same defect as a Medium under APPROVE-WITH-CHANGES. Its Info (the
red-observability stream is synthetic and disclosed) matches Section 3.

Disagreement, one row. rev55 states "binv_twice matches the sampler ... the generator's pair is chained and shares rd
and imm", judged from the generator's Op structure. The emitted program at seed 100600133 places the first binvi's
report store between the two binvi (Section 5 M-2), the sampler's rule at gen_fcov_pkg.sv:1573 is over consecutive
records, and cp_binv_twice.yes is UNHIT in all 40 post-fix runs of the retained sweep. The pair does not reach its
bin; M-2 stands.

Rows adopted from rev55, each with the mechanism verified:
- L-4 (Low, records; adopted from rev55 Low 1, verified). The simulated "before" generators are the pre-fix root's
  7f3ec33390c2 and aaa8e29f7370 (measured inside /proj_soc/user_dev/fzhang/ibex_dv_probe/gensweep), which are neither
  the parent 8559958's blobs (c1580d22a361, 125ef1a1cf5d, the ones the shape-check red reads) nor the handed ones, and
  the delta between them and the committed generators is retained nowhere; the index says only "a commit plus three
  uncommitted generator files". Retain that diff or name what differed.
- L-5 (Low, code comment; adopted from rev55 Low 2, verified). gen_run_fixture.sh:16-17 says "an unchecked assignment
  links the wrong cocotb and says nothing", the claim the LOG-099 third corrigendum at 65982e8 (inside this range)
  withdrew: a wrong-toolchain compile fails loudly inside vcs and the refusal is a diagnostic. Reword the comment to the
  diagnostic framing the corrigendum states.
- L-6 (Low, maintenance; adopted from rev55 Low 3, verified). _NAMED_EXACT hand-mirrors the six exact constants and the
  bit-7/bit-15 rule of bit_rs1_cls (gen_fcov_pkg.sv:925-939); a later classifier edit re-opens the seven bins with no
  red anywhere. A cross-reference beside the classifier, or a unit check that the generator's rule agrees with the
  sampler's constants, would make a drift visible.
Verdict unchanged: REQUEST-CHANGES confined to M-1 and M-2; L-1..L-6 owed as disclosed.
