# Critic verdict: tb-infra landing 6 (commit 61c97c1, diff base f660470): the tb_l3, tb_l4 and tb_l5 re-reviews (part A) and slice 4a (part B)

Base verdicts re-reviewed here: gen_critic_tb_l3.md (57b5e5022c00474c, REQUEST-CHANGES), gen_critic_tb_l4.md (6ba44a44964afa40, REQUEST-CHANGES),
gen_critic_tb_l5.md (b0be37eac33d0ec1, REQUEST-CHANGES). The CM60 scoreboard delta of this commit is judged in gen_critic_tb_l2b_v3.md.

Artifacts reviewed (committed blobs at 61c97c1; sha256 first 16 hex):

- dv/auto_dv/env/gen_fcov_pkg.sv  68ba3dfd8d3c4205
- dv/auto_dv/env/gen_fcov_groups.svh  1e1c4bc1ecf8db64
- dv/auto_dv/env/gen_env_pkg.sv  9bfaa56f8e273ce5
- dv/auto_dv/tb/gen_fcov_codegen.py  0ab1eaba79b8940d
- dv/auto_dv/tb/unit/gen_ut_fcov_codegen.py  defad7ec6b2a86c5
- dv/auto_dv/gen_tb/gen_tests/gen_ut_isa_cov.py  898a3a2c68353196
- dv/auto_dv/gen_tb/gen_bridge.py  d220992016efbc37
- dv/auto_dv/gen_tb/gen_knobs.py  a7da764c78c0f400
- dv/auto_dv/tb/gen_tb_knobs.yaml  ccfa81ae18dfb171
- dv/auto_dv/tb/gen_tb_pkg.sv  792452e36eb09b39
- dv/auto_dv/tb/gen_tb_top.sv  ef7c9a9e1193794b
- dv/auto_dv/evidence/gen_tdd_fcov.md  29bf826a6aa11eb6
- dv/auto_dv/mutations/gen_mut_fcov.md  cf3bb4b32d9f6f89
- dv/auto_dv/evidence/gen_critic_response_fcov.md  97fb1b4119519771
- dv/auto_dv/docs/gen_component_api_fcov.md  76cedb4553d51649
- dv/auto_dv/stim/gen_directed/gen_sbit_directed.S  b8b821a862214b2e
- dv/auto_dv/stim/gen_directed/gen_zcb_directed.S  fe3a5d9a2a50ec95
- dv/auto_dv/evidence/gen_fcov_proof_slice4a.fcov.yaml  3dec27ede8e4a383
- dv/auto_dv/evidence/gen_fcov_proof_slice4b.fcov.yaml  58c8da1dfd48541d
- dv/auto_dv/evidence/gen_tdd_logs/gen_manifest.md  c40f8b6508463198
- the 199 added logs under dv/auto_dv/evidence/gen_tdd_logs/fcov/gen_fu_l6_* and the 20 proof / ablation manifests (rows recomputed 199/199)

Date: 2026-09-03 (UTC). Role: Critic (reviewer other than the author). Basis: docs/dv/dv_principles.md d9c27db18f511411,
the fcov-expectation and mutation-check skills, LOG-058, LOG-065, the Zc specification (tools/specs/riscv-isa-manual/src/unpriv/zcmp.adoc:1201-1202),
rtl/ibex_compressed_decoder.sv, rtl/ibex_core.sv, rtl/ibex_cs_registers.sv, the three base verdicts.
Method: clean archive of 61c97c1; library and flow self-tests, gen_fcov_codegen --check, gen_knobs_codegen --check and GEN_UT_FCOV_CODEGEN PASS on
the archive; two unnamed subagents (an evidence audit of the 199 logs with read-only checker re-runs of every manifest against every retained
report; a code review of each fix against my items), both told the fence and kept out of dv/auto_dv/reviews/; the decisive facts re-checked
first-hand in the blobs (the sampler's fix lines, the recipe hash of the sources, the counts in the retained reports). The cross-model artifact
for this commit (2026-09-03-claude-diff-f660470d-61c97c1e.md) was not read before Sections 1-6; Section 7 reconciles.

CRITIC VERDICT: REQUEST-CHANGES

Every mechanism the three base verdicts required is fixed in the committed sampler and re-proven in retained reports with the counts I asked for,
and the LOG-058 unit test exists and runs. Four mediums remain: the final build's source identity does not reproduce from the commit (M-1); a
malformed move pair still samples silently (M-2, my tb_l5 H-1's second half); the unit test's divisor vectors do not discriminate the fix it
guards and the micro-op exclusion is not asserted (M-3); the new report referee has no red (M-4). Part B (slice 4a) is sound with two lows.

## 1. What was verified (part A, the fixes)

| item | fix in the committed sampler (gen_fcov_pkg.sv) | re-proof in the retained reports |
|---|---|---|
| tb_l4 H-1(a) cp_minstret_once | the first micro-op's counter is kept (:528) and the sample is pended to the first record AFTER the sequence: `nxt.ext_mhpmcounters[7] - zp_mhpm10_first == 32'd1` (:560-566); a miss is counted (n_zcmp_minstret_no) and queryable | yes 290 of 290 in the short / min1 / long / random zcmp runs (was 193); minstret misses = 0 asserted by gen_ut_isa_cov on gen_zcmp_directed.S |
| tb_l4 H-1(b) result classes on rd = x0 | every rd_wdata-fed result class samples na on rd = x0 (:891, :900, :904, :909, :917, :927, :938) | bit-count cp_result.r0 = 11 (was 102) with cp_rd_x0.yes = 91 |
| tb_l4 H-1(c) / tb_l3 L-4 micro-ops in the base groups | `if (t.ext_exp_valid) ... return;` before the base chain (:883) | alu_imm = 16 in the zcmp run (was 354) |
| tb_l5 H-1 sreg decode | `zcmp_sreg(r) = (r < 2) ? 8 + r : 16 + r` (:622-624) used for the expected registers (:575-577) and the hazard sources (:542); = zcmp.adoc:1201 and rtl/ibex_compressed_decoder.sv:156, :162 | cp_uop_count_ok.yes 130 of 130 (was 10); cp_hazard_src alu_prev 6, load_prev 2, none 122 (was 33 / 2 / 95); the build-q red report retained (10 / 33) |
| tb_l3 H-1(b) divisor magnitude | `33'd0 - {rs1[31], rs1}` (sign-extended, :186-187) | rs1 = 0x7FFFFFFF, rs2 = 0x9ABCDEF0 -> neg_rand and rs1 = 0xFFFFFFFE, rs2 = 0x12345678 -> abs_gt_dividend (checked by script); cp_divisor counts in the muldiv report |
| tb_l3 H-1(c) addi_wrap | from rs1 and imm alone (:361-367, call :918) | cp_addi_wrap pos 70 / neg 42 / none 1654 in the alu run |
| tb_l4 M-3 cp_dmem_delay | classified from the dbus agent's completed responses inside the sequence's window (:551-558, subscriber :128-131) | short 290 / min1 290 / long 290 in the fixed regimes; random: mixed 147, long 137, short 4, min1 2 (was mixed 290 from the knob) |
| tb_l5 L-9 cp_mcen_gate | mcounteren_writable_i read from the ctrl interface at the write record (:111, :773; gen_tb_top.sv:279) | on 34 / off 34 / invalid 34 in the three csrwarl runs |
| cp_wrap (L5R-1) | the 33-bit signed target outside [0, 2^32) (:681-685) | cp_wrap.yes 0 (declared out of the branch proof, 26 bins) |
| tb_l4 L-9, tb_l5 L-7 constants | ibex_pkg OPCODE_JALR / OPCODE_BRANCH / OPCODE_SYSTEM / CSR_* / CSR_MSTATUS_*_BIT; GEN_CPUCTRLSTS_DUMMY_INSTR_EN_BIT | read |
| tb_l3 M-1, tb_l4 M-1, tb_l5 M-1 mutants | FM1-FM9 applied to the committed sampler (original blob 68ba3dfd8d3c4205 = the 61c97c1 blob), each build sha equal to its compile logs, each with an ablation manifest and checker log (FM4 informational, by design) | catch lines by bin name; ablation PASS 127 / 45 / 37 / 25 / 27 / 62 / 21 / 28; catch and ablation counts agree bin for bin |
| tb_l3 M-2 fcov-off red | a real `+gen_fcov_en=0` run of gen_muldiv_directed.S on a fresh vdb: header, verdict, urg command, the checker's protocol error on the missing report | retained gen_fu_l6_nofcov_* |
| tb_l5 M-2 build-l reds | the three slice-3 build-l reports retained with checker runs (FAIL max_fwd; FAIL alu_prev; the csrwarl cross rows) | retained gen_fu_l6_urg_red_l_* |
| tb_l3 L-1 / tb_l4 L-8 / tb_l5 L-2 | the manifest header states ASCII normalisation (bytes above 127 written as '-') | read |
| tb_l3 L-7 / tb_l5 L-5 | every proof manifest carries an anti_vacuity note per bin | present (one boilerplate sentence for every bin, see L-3) |
| tb_l4 L-3 | every urg report has a companion .cmd.txt naming the command and the vdb | 17 cmd files |
| tb_l3 L-6 | GEN_FCOV_REF report-phase referee: a group the sampler fed with zero coverage is a uvm_error (:1007-1014) | no red (M-4) |

Evidence audit: 199 manifest rows recompute; 36 run headers with build shas; the 12 proof manifests PASS on exactly their own reports
and the 8 ablation manifests on the un-mutated reports (read-only checker matrix, 400 cells, every retained PASS reproduced); the
16 lock-step re-runs report 0 mismatches. gen_ut_isa_cov: five runs PASS, 18 vector cases 0 failures each, FCOV_QUERY asserting eq = 84
(alu), sequences = 290 and minstret misses = 0 (zcmp), rd = x0 bit-count records = 91 (bitcnt). The unit test's synthetic records go
through write() itself and read TB-side values only.

## 2. Closure of the base verdicts, item by item

- gen_critic_tb_l3.md: H-1(a) closed (landing 4); H-1(b) closed; H-1(c) closed; M-1 closed (FM1 on the committed sampler with its
  ablation); M-2 closed (the real fcov-off run); L-1 closed (normalisation statement); L-2 closed (counts corrected: 395 named
  coverpoint bins for nine groups); L-3 stated (the build-g check row withdrawn); L-4 closed; L-5 partly (unit-test cases added, --check
  in the committer's checks per the response; the svh header sentence on cross bins owed); L-6 built, unproven (M-4); L-7 closed in form
  (L-3 below); L-8 closed.
- gen_critic_tb_l4.md: H-1(a), (b), (c) closed; M-1 closed; M-2 closed (the claim withdrawn in the transcript, the test exists); M-3
  closed with a caveat (L-4 below); L-1 closed (395; the API table corrected); L-2 closed; L-3 closed; L-4 closed (the dummy report row
  says it is the B8 record); L-5 stated; L-6 open as a plan question; L-7 closed (gated on the operand-only marker, fixtures); L-8 closed;
  L-9 closed; L-10 closed.
- gen_critic_tb_l5.md: H-1 closed for the decode, the proof counts and the hazard sources; its second required change (a collected
  failure when a legal pair's micro-ops do not match) is not delivered (M-2); M-1 closed (counts removed from the record, ablations
  retained); M-2 closed (the build-l reds retained); L-1 closed (215; the record); L-2 closed; L-3 partly (the summary and operand-only
  cases are unit-tested; the cross_auto_bin_max line itself is not); L-4 not answered (misa legal / illegal still rendered and
  unreachable; a plan question, not in the response rows); L-5 closed; L-6 closed (CM81-H-1 row); L-7 closed; L-8 ruled (L5R-2; the
  code was already the whole-value test at f660470, so the record's "fix" wording is a record item); L-9 closed. The response file
  carries no CR-5 rows: the tb_l5 items are answered only through the CM81 rows that overlap them (L-5 below).

## 3. Findings (part A)

### M-1 (medium) [S6 evidence identity] The final build's sources are not the committed sources

The 27 landing-6 proof, unit-test and red runs and the 9 mutant catches carry build_sources_sha256 = 9f123de2aa16eb21 (build s), and the
transcript calls build s "the landed sources". The recipe of gen_tb_local.sh:35-36 (one sha256 per file under dv/auto_dv/env, tb, isa
and gen_tb, then one over the sorted list) applied to the clean 61c97c1 archive gives d1bfc2720e665c94 under the UTF-8 sort and
887ec0d219ab2ef0 under the C sort; the same recipe on the f660470 tree gives 86c7caf1d034cdec, the landing-5 build, so the recipe and the
locale are validated. At least one hashed file of the committed tree therefore differs from build s, and the commit does not say which:
the per-file list (sources_sha256.txt) is not retained with the compile log. The sampler itself is identified independently (the FM
mutants' original blob 68ba3dfd8d3c4205 equals the committed gen_fcov_pkg.sv) and the rendered include equals the committed renderer's
output (--check up to date), so the difference is most likely a Python, yaml or shell file edited after the build; but "most likely"
is not evidence, and the transcript's "every proof re-run on it" describes a source set the commit does not carry. Required: retain
sources_sha256.txt beside every compile log from now on (the recipe already writes it), state which files changed after build s and
that none of them enters the simv, or re-run the proofs on the committed tree.

### M-2 (medium) [S2; S6 collected failure] A malformed move pair still samples silently

gen_critic_tb_l5.md H-1 required "a counted, collected failure when a legal pair's micro-ops do not match the expectation". At 61c97c1 a
mismatch only clears mv_ok (:577) and cp_uop_count_ok samples na (:585); there is no counter (FCOV_QUERY 10 returns the pairs seen, not
the misses), no report line and no uvm_error, unlike the push / pop collector's n_zcmp_uop_no / order_no / tags_no. The only guard is
vector case 18 (cm.mva01s s7, s6). A regression of the decode for one register value would again show as fewer yes hits and nothing
else. Required: a miss counter reported at report_phase and queryable, and a uvm_error (or the GEN_FCOV_REF referee) when a legal
pair mismatches, with a vector case for the miss.

### M-3 (medium) [S6 LOG-058] The unit test does not discriminate two of the fixes it exists to guard

The three divisor vectors (-3 against 2, -3 against -5, 3 against -5) return the same class under the old formula (33'd0 - {1'b0, x})
and the new one; a case with |negative| < |positive| (the pairs of my tb_l3 H-1(b): rs1 = 0x7FFFFFFF, rs2 = 0x9ABCDEF0 -> neg_rand;
rs1 = 0xFFFFFFFE, rs2 = 0x12345678 -> abs_gt_dividend) is what separates them. The Zcmp micro-op exclusion (tb_l4 H-1(c)) is not
asserted: the synthetic `addi sp, sp, -48` micro-op would feed the immediate group if the guard regressed and no case checks n_imm or
the group's last sample around it. The sreg cases cover s7 / s6 only (the same formula branch as s2..s5). Required: the two divisor
pairs above, an assertion on the immediate-group counter across the synthetic sequence, and one s2..s5 pair.

### M-4 (medium) [S6 mutation-proof] The GEN_FCOV_REF referee has no red

The report-phase referee (a group the sampler fed with zero coverage is a uvm_error, :1007-1014) is a new checker with no retained
firing: no run, mutant or vector shows it raising. A sampler mutant that feeds a group's counter without sampling it (or a run with the
covergroup instantiated but the sample call removed) is the natural red. Owed with the next sampler touch.

### L-1 (low) [S4 record] Numbers and citations in the record

gen_tdd_fcov.md Section 5 says "the vector table 15 cases" where the logs and the commit say 18; gen_mut_fcov.md's FM5 ablation says
"all 26 declared bins" where the log and manifest say 25; Section 5 cites build-q check results "(128 / ... / 27 / ...)" with
gen_fu_l6_*_check.log, which are the build-s logs (27 is the pre-L5R-1 count; the retained slice3a log says 26); Section 4 says the
slice-4a proofs are "build q" where the retained artifacts are build s; the FM_all_driver.log FM5 line reports two unhit bins
(c_bnez and cp_wrap.yes, the 27-bin manifest) while gen_fu_l6_FM5_check.log reports one (the 26-bin manifest) without the re-check
recorded; the manifest row for gen_fu_l6_nofcov_check.log names a manifest gen_fcov_proof_nofcov.fcov.yaml that does not exist (the
transcript says the slice-1 manifest); gen_mut_fcov.md's slice-1 paragraph still cites the landing-3 nofcov log for the red; the
mtvec low threshold is listed among the landing-6 fixes while the code was already the whole-value test at f660470; the zcb "red
first" (cr_load_sign 3 of 6) has no retained report.

### L-2 (low) [S6 cycle bases] cp_dmem_delay classifies the responder's drawn delay against two cycle counters

The class comes from the dbus driver's transaction (its drawn rvalid_delay, not a measured rvalid-minus-grant), and the sequence
window is bounded by the RVFI interface's posedge counter while the transactions carry the driver's negedge counter, whose base the
driver itself notes differs from the export's. The in-order rule can delay an actual response beyond the drawn delay when two
transactions are outstanding. Neither is shown to move a class in the retained runs (the fixed regimes score 290 each); state the
sources and the bases in the API doc, or measure the latency at the pins.

### L-3 (low) [schema] The anti_vacuity notes are one sentence repeated

Every note in all 20 manifests is the same boilerplate ("a lock-step run: every result of the program is compared against the ISA
model ..."). It satisfies the schema; it does not say what a hit of that bin proves. The promoted manifests derive the note from the
plan's Sample line per covergroup; do the same here.

### L-4 (low) [S4] The comment on |INT_MIN|

gen_fcov_pkg.sv:186 and the API doc say |INT_MIN| = 2^32; the expression yields 2^31, which is the right value; correct the words. Also a
trap record between two binv does not reset the pair tracker (sb_prev_binv), contrary to the doc's "any other record in between".

### L-5 (low) [S4 record] No CR-5 rows

gen_critic_response_fcov.md answers my tb_l5 items only through the CM81 rows that overlap them; L-3 (the untested option line), L-4
(misa legal / illegal ignore, a plan question) and L-8 (the mtvec threshold's ruling) have no row of their own. Add the CR-5 rows.

## 4. Part B: slice 4a (gen_bit_sbit_cg, gen_cmp_zcb_cg)

- Renderer: plan coverpoint bins = rendered (sbit 22 / 100 cross; zcb 30 / 65 cross); fourteen groups 571 named coverpoint bins and
  2666 cross bins; --check up to date; the renderer's new forms (nested-brace values, `any`, `or`, the operand-only gate) leave the
  twelve earlier renders byte-identical and have unit-test cases (18 OK lines).
- Samplers: sbit by exact funct7 / insn[31:27] with index, upper bits, prior bit, operand class, rd = x0 and the binv-twice pair; zcb by
  form with the uimm, the loaded data's sign from mem_rdata, alignment from mem_addr[1:0], the c.mul register relation; both sample only
  non-trap, non-micro-op records; c.mul also feeds gen_mul_ops_cg. No cast or width hazard found; the result classes are not
  rd_wdata-fed.
- Proofs: gen_sbit_directed.S 1001 records / 0 mismatches, sbit = 182, slice4a PASS 22 (every coverpoint bin), crosses 100 / 100;
  gen_zcb_directed.S 301 / 0, zcb = 71, slice4b PASS 29 (every bin but cp_alu_operand.rand), crosses 59 / 65; FM8 (bext as bclr ->
  cp_op.bext unhit) and FM9 (c.lh as c.lhu -> cp_insn.c_lh unhit) caught with ablations 21 / 28.
- L-6 (low) [plan]: gen_fcov_plan.md:693 defines cp_alu_operand "iff ALU forms" while the CSV and the rendered cr_alu_operand include six
  c_mul tuples and the sampler follows the CSV; and cp_alu_operand.rand with its six cross bins is unreachable by construction (the five
  classes partition every value), admitted in the manifest header. Plan owner: align the Sample text with the CSV and ignore the
  dead bins.
- L-7 (low) [S6 record]: the zcb red first (registers s2 / s3 / s4 where the compressed fields are a0 / a1 / a2) is narrated without a
  retained report.

## 5. Principles check

dv-principles-check (docs/dv/dv_principles.md d9c27db18f511411): S2 derive from intent: every classifier the base verdicts faulted now
follows the spec, the RTL or the ruling (conforming); S4 honesty: L-1, L-5, and the "landed sources" sentence that M-1 shows unproven;
S6 trust triad: reds retained (build l, build q, the fcov-off run), mutants on the identified sampler with ablations (conforming), the
LOG-058 test present but not discriminating two fixes (M-3), a new referee without a red (M-4), the build identity of the proof set not
reproducible (M-1). One-line verdict: FAIL on M-1 until the source identity is stated or the proofs re-run on the committed tree.

## 6. Required for re-review

1. M-1: sources_sha256.txt retained with the compile log and the post-build edits named (or the proofs re-run on the committed tree).
2. M-2: the move-pair miss counter, report line and collected error, with a vector case.
3. M-3: the two divisor pairs, the immediate-group assertion across the synthetic sequence, one s2..s5 pair.
4. M-4: a red for GEN_FCOV_REF.
5. L-1 and L-5 are record edits and should close with M-1; L-2, L-3, L-4 with the next sampler touch; L-6 is the plan owner's; L-7 with
   the next slice.

## 7. Reconciliation with the cross-model artifact (dv/auto_dv/reviews/2026-09-03-claude-diff-f660470d-61c97c1e.md, read after Sections 1-6 were written)

APPROVE-WITH-CHANGES: three mediums, five lows; rubric ai-slop-comments FAIL. Its verifications of the fixes (the sreg decode against the
RTL, the na guard in all seven result-class samples, the micro-op guard at :883, the minstret pend, the observed dbus latencies, the
FM1-FM9 catch and ablation pairs, the real nofcov red, the build-l reds) agree with Section 1. It does not test the build identity
(my M-1) and reads build s as the landed sources.

Adopted after verification:
- M-3 widened (its second medium): gen_ut_isa_cov has no retained red of its own; the FM4 build (6df309833d045c69) is in hand and a run
  of the test on it with query 0 expecting 84 would fail on the FCOV_QUERY assertion and the "slti rs1[0] == imm[0] alone is not eq"
  row. Required with M-3: that run retained as the test's red and cited in the FM4 row.
- M-4 widened (its last low): GEN_FCOV_REF referees 6 groups (br, csr_pairs, mul, sbit, zcb, zcmp) of the
  fourteen the sampler counts (my count of the uvm_error lines at gen_fcov_pkg.sv:1007-1014); div, alu_reg, zba_zbb, alu_imm, shift,
  bit_count, zca and zcmp_mv are fed but never refereed. Required with M-4: every counted group, and the red.
- L-8 (low, its first medium kept low here): 10 comment lines in gen_fcov_pkg.sv narrate review history or cite review and log ids
  (lines 113, 118, 119, 681, 949, 964, 969, 973, 983, 992: "H-1(a) of the landing-4 review", "ruling L5R-1", "the landing-3 major", "LOG-058"), against the
  intent-only comment rule; the hand-off's claim that none exist is false. Rewrite as intent (what the classifier measures and why); the
  history stays in the transcript and the response rows. Kept low: comments do not change what is checked.
- L-9 (low, its third medium kept low here): cp_mcen_gate samples the pin when the write's RVFI record arrives, not in the write's
  W-DEC window as the plan asks; the two coincide while the pin is static per run, which it is today (nothing moves it after
  build_phase), and the offset the API doc names (GEN_CSR_WRITE_TO_RVFI_OFFSET) exists in no code or yaml. Record the mechanism as a
  deviation owed to the in-run pin command (WP-10) and add the constant where the doc names it, or drop the name.
- L-10 (low, its first low): FCOV_QUERY returns the sampler's counters and the vector table asserts the shadow copies of the sample
  arguments, not covergroup bin state; API doc Section 9 should say so, with the codegen unit test and the proof manifests as the
  bin-side evidence.
- Its "15 cases" low is my L-1; its anti_vacuity low is my L-3; its binv-trap low is my L-4.

Mine that the artifact does not carry: M-1 (the build identity), M-2 (the silent malformed pair), the vector-discrimination half of M-3,
L-2, L-5, L-6, L-7.
