# Critic verdict: tb-infra landing 3, T-205 slice 1 (commit a786543, diff base 0a2ffe4)

Artifacts reviewed (committed blobs at a786543; sha256 first 16 hex):

- dv/auto_dv/tb/gen_fcov_codegen.py  d4dd7fe2469942ca
- dv/auto_dv/env/gen_fcov_groups.svh  11e9ea8ab36cafb8
- dv/auto_dv/env/gen_fcov_pkg.sv  2c495abdb8920957
- dv/auto_dv/tb/unit/gen_ut_fcov_codegen.py  d6c2b6de97b95edc
- dv/auto_dv/evidence/gen_tdd_fcov.md  e12ef2ffefdfe9ca
- dv/auto_dv/mutations/gen_mut_fcov.md  ffd72ab87e1eb9ed
- dv/auto_dv/evidence/gen_fcov_proof_slice1.fcov.yaml  96e36de3e9b33e04
- dv/auto_dv/evidence/gen_fcov_proof_slice1b.fcov.yaml  afb1d3b287b7043e
- dv/auto_dv/stim/gen_directed/gen_alu_directed.S  bfa2d74222278396
- dv/auto_dv/stim/gen_directed/gen_muldiv_directed.S  6836d189cfe498d0
- dv/auto_dv/docs/gen_component_api_fcov.md  8e2651b9837b8ee0
- dv/auto_dv/evidence/gen_tdd_logs/gen_manifest.md  20df97604853e2ae
- the 39 added logs under dv/auto_dv/evidence/gen_tdd_logs/fcov/gen_fu_l3_* (manifest rows recomputed)

Date: 2026-09-03 (UTC). Role: Critic (reviewer other than the author). Basis: docs/dv/dv_principles.md d9c27db18f511411,
the fcov-expectation skill, DV_prompt.txt, gen_fcov_plan.md (CG-MUL-001, CG-MUL-003, CG-ISA-001/002/003, CG-BIT-001),
rtl-arch's evidence/gen_cg_sampling_anchors.md, the RISC-V ISA manual, this clone's RTL.
Method: clean archive of a786543; library self-test PASS, flow self-test PASS, gen_fcov_codegen --check up to date,
GEN_UT_FCOV_CODEGEN PASS on the archive; two unnamed subagents (an evidence audit of the 39 logs and the manifest, with a
read-only re-run of ci/check_fcov_expectations.py on the retained urg reports; a renderer / sampler derivation review),
both told the fence and kept out of dv/auto_dv/reviews/; every finding below checked first-hand in the blobs unless
marked audit-quoted. EXPOSURE: before this review the Orchestrator's queue message said the cross-model artifact had
found 'a one-bit cast major in the sampler'; I did not read the artifact before Sections 1-5, and H-1(a) below was
located by my own grep of the sampler for casts to one-bit types (gen_fcov_pkg.sv:337), which the derivation subagent
had not flagged. Section 6 is the reconciliation, written afterwards.

CRITIC VERDICT: REQUEST-CHANGES

The renderer is complete and proven, the sampler samples TB-side facts under the plan's conditions, and the proof
mechanism is the real checker on real urg reports. Three classifiers are wrong, so bins the proof reports as hit were
hit for the wrong operands (H-1); the sampler mutant was proven on a pre-landing sampler without a retained control
(M-1); and a retained urg report labelled as the fcov-off red carries full coverage data from a reused vdb (M-2).

## 1. What was verified

### 1.1 Renderer (gen_fcov_codegen.py -> gen_fcov_groups.svh)

- Bin completeness recomputed from the three sources: for each of the six covergroups the plan's coverpoint bins, the CSV's
  distinct (covergroup, coverpoint, bin) rows and the rendered `bins` agree: mul 46 / 390 cross, div 36 / 140, alu_reg
  46 / 294, zba_zbb 51 / 373, alu_imm 40 / 105, shift 31 / 101; 250 coverpoint bins and 1403 cross bins, 1653 named bins in
  all. No plan or CSV bin is unrendered; the only rendered bins outside the plan are the 46 `ignore_bins na = {-1}` (one per
  coverpoint, by design). Cross bins are named binsof conjunctions (`bins c_mul_no = binsof(cp_op.c_mul) && binsof(cp_rd_x0.no)`,
  svh:456-458); explicit tuples follow the plan's cross line; keyword bins are escaped (`bins \xor = {4}`, svh:717).
- Refusals: eleven die paths (bad columns, no plan header, no CSV bins, plan / CSV coverpoint or bin mismatch, names outside
  cp_/cr_, no cross line, component not a coverpoint, unsplittable cross bin, non-ASCII). --check compares the rendered text
  with the file and reports STALE. gen_fcov_pkg.sv includes the svh unconditionally and gen_tb.f lists the package
  unconditionally; the covergroups are instantiated only with fcov_en (default 1).
- Sample() argument order checked against all six rendered signatures: matches in every call.

### 1.2 Sampler (gen_isa_cov) against the plan's Sample lines and rtl-arch's anchors

Every value comes from the RVFI record the monitor published (insn, rs1/rs2_rdata, rs1/rs2/rd_addr, rd_wdata); `write()`
returns on `t.trap`; no DUT internal is read. Conditions, per group, equal the plan's and the anchors': mul = OP funct7
0000001 funct3[2] == 0 or the 16-bit c.mul word (fcov:380-386; anchors say c.mul MUST be decoded from the 16-bit form); div =
OP funct7 0000001 funct3[2] == 1 (:387); Zba/Zbb by the decoder arms with zext.h = pack with rs2 == x0 (:258-282); alu_imm =
OP-IMM funct3 not 001/101 (:396); shifts = OP-IMM / OP funct3 001/101 with funct7 0000000 / 0100000 (:405); alu_reg = OP
funct7 0000000 / 0100000 (sub only) funct3 not a shift (:412). Classifier precedence is stated in the code and in
gen_component_api_fcov.md:93-96 and matches the plan's bin lists. Zb draft, clmul, rol, sbclr, clz/ctz/cpop/rori/rev8/orc.b
fall out of every branch; compressed words other than c.mul never match. Sound classifiers checked: sign_pair, alu_wrap
(33-bit sum, unsigned compare, the plan's sub_ovf form), bit_wrap (truncated shift, anchors), imm sign-extension, imm_cls,
sh_amt_cls, sh_rs2_upper, the rd == x0 and rs1 == rs2 flags. Three classifiers are wrong: H-1.

### 1.3 Evidence audit

- Manifest: 39 added rows, md5 and byte size recomputed from the blobs, 39/39; no file without a row. Working-tree copies
  equal the blobs (39/39).
- Builds: three shas, each equal to a compile log: e39aa0e0c5bb99bf (wit g, three groups), 8452b39617094289 (wit h and the
  landed tree out_l3; the recipe of gen_tb_local.sh applied to the clean archive gives 8452b39617094289), a65d88c23c734972
  (FM1). Five run headers carry build_sources_sha256; the build-g runs and the landed canaries exist as driver lines only.
- Lock-step proof runs on build h: muldiv `ISA compare: records=10206 mismatches=0`, alu `records=22787 mismatches=0
  draft_b=980`; GEN_FCOV sample counts muldiv mul=2299 div=1210 alu_reg=3630, alu zba_zbb=5096 alu_imm=10586 shift=4312.
- urg reports retained for both runs; the 37 per-cross expected / covered values in the transcript all match the reports.
- Checker: gen_fu_l3_slice1_check.log has 128 `= HIT (count=N)` lines and `PASS -- all 128 declared bins hit`; slice1b 122
  and PASS. Re-running ci/check_fcov_expectations.py read-only on the retained grpinfo files reproduces both outputs
  line for line (the only difference is the checker's em dash, see L-1); crossing the manifests (slice1 against the alu
  report) gives 128 not hit, exit 2: the checker discriminates.
- The two proof manifests declare every coverpoint bin of their groups (128 = 36 + 46 + 46; 122 = 51 + 40 + 31) and no cross
  bin, as their headers say and as LOG-054 allows for interim proof manifests; every bin exists in the svh.
- Programs: gen_muldiv_directed.S walks 11 operand classes over every ordered pair for mul / mulh / mulhsu / mulhu / c.mul
  (`.2byte 0x9dd1`, decoded bitwise as c.mul a1, a2) / div / divu / rem / remu, with rd = x0 and the register-relation
  forms; gen_alu_directed.S walks 14 classes for the Zba/Zbb arms, shifts (amounts 0 / 1 / 7 / 31, register amounts 32 / 33 /
  0xFFFFFFE0) and the immediates 0 / 1 / -1 / 2047 / -2048 / 100 / -100; both end with the tohost store the TB's EOT
  convention requires. Spot checks of ten bins each landed on real instructions.
- Weakening scan (git diff 0a2ffe4 a786543 -- dv/auto_dv/env dv/auto_dv/tb): nothing removed, demoted or defaulted off;
  the only removed lines are a rewritten header comment and the package's position in gen_tb.f.

## 2. Findings

### H-1 (high) [S6 fcov-expectation; S2] Three classifiers assign the wrong bin, so declared bins the proof reports as hit were hit for the wrong operands

(a) gen_fcov_pkg.sv:337 `if (rs1 == logic'(32'(imm))) return ..._SLT_CASE_EQ;` -- `logic'(...)` is a cast to the one-bit type
    logic, so the comparison is `rs1 == imm[0]`: the `eq` bin of cp_slt_case fires for rs1 == 0 with any even immediate and
    for rs1 == 1 with any odd one, and never for a genuine equality such as rs1 == imm == 100. The alu program's table holds
    0, 1 and 100 with immediates 100 / -100, so the proof run hit `gen_isa_alu_imm_cg.cp_slt_case.eq` on false pairs and
    missed the true ones; the checker's `HIT (count=N)` for that bin is not evidence of the bin's intent.
(b) gen_fcov_pkg.sv:147-148 `logic [32:0] abs1 = rs1[31] ? (33'd0 - {1'b0, rs1}) : {1'b0, rs1};` (same for abs2) -- negating
    the zero-extended 33-bit value gives 2^33 - u, not |rs1|: every negative operand has a larger "abs" than every
    non-negative one. At :158 `if (abs2 > abs1) return ..._ABS_GT_DIVIDEND;` therefore fires for any negative unlisted divisor
    with a non-negative dividend and never for a positive divisor with a negative dividend. With the muldiv table (0x7FFFFFFF,
    0x9ABCDEF0, 0xFFFFFFFE, 0x12345678, 7 ...) the proof run sampled rs1 = 0x7FFFFFFF, rs2 = 0x9ABCDEF0 as abs_gt_dividend
    (true |rs2| = 0x65432110 < 0x7FFFFFFF: neg_rand) and rs1 = 0xFFFFFFFE, rs2 = 0x12345678 as pos_rand (should be
    abs_gt_dividend); cp_divisor.{abs_gt_dividend, neg_rand, pos_rand} and the crosses cr_op_divisor / cr_div0 carry wrong
    tuples in the very reports the proof cites.
(c) gen_fcov_pkg.sv:322-326 addi_wrap reads the sign of `res = t.rd_wdata`, which the RTL forces to 0 on rd = x0 (the file's
    own header :82 and anchors Section 0 say so): `addi x0, rs1 < 0, imm < 0` is classified neg_wrap with no wrap, and
    `addi x0, 0x7FFFFFFF, +imm` is `none`. gen_component_api_fcov.md:97 says "the wrap bins are recomputed from the operands";
    true for alu_wrap and bit_wrap, not for addi_wrap. The alu program issues only `addi x0, a1, 1`, so the proof did not
    trip it; random rd = x0 addi in the generated streams will.
- Why high: the fcov-expectation leg is the covergroup's only proof (gen_mut_fcov.md says so), and for these bins the PASS
  is not what it claims. The lock-step compare is unaffected (the model checked every result); only the coverage record is.
- Required: fix the three classifiers (32-bit compare for eq; abs from a 32-bit negation before extension, or a signed
  compare; addi_wrap from rs1 and imm alone, as alu_wrap does); a red per defect (a directed pair the current classifier
  mis-hits, shown as the wrong bin in urg or by a unit-level probe, then the right bin after the fix); re-run the two proof
  runs on the fixed sampler and re-generate the checker logs; state the three corrected precedences in the API doc.

### M-1 (medium) [S6 mutation-proof] FM1 was proven on a pre-landing sampler, and its control is not retained

FM1's build a65d88c23c734972 was compiled at 14:25:55 local (gen_fu_l3_FM1_build_compile.log), before build h (14:28:09),
and its "original sha256 612da58342b73445" (gen_fu_l3_FM1_check.log) is not the committed gen_fcov_pkg.sv (2c495abdb8920957);
the FM1 excerpt's GEN_FCOV line reports three groups only. gen_mut_fcov.md says "a scratch copy of the wit_root sources plus
the one edit" and gen_tdd_fcov.md cites it as the sampler mutant, without saying the sampler had three groups then. The
ablation ("the manifest without the c_mul bins passes") has no retained log and its manifest is not in the commit. The catch
itself is real and well-targeted (`gen_mul_ops_cg.cp_op.c_mul = UNHIT (count=0)`, `FAIL -- 1 declared bin(s) not hit`), but
under the mutation-proof standard the mutant must be built from the landed sources with the original sha equal to the
committed blob, with the control retained. Required: re-run FM1 on the fixed landed sampler (after H-1), retain the catch
and the ablation with their manifests and urg reports, and record the build and original shas.

### M-2 (medium) [S4 honesty over green] The retained fcov-off "red" is one four-line log, while a full urg report labelled nofcov carries coverage data from a reused vdb

gen_fu_l3_nofcov_check.log holds the red: `urg exit 0 grpinfo: ABSENT` and `PROTOCOL ERROR: ... grpinfo.txt: missing`, the
checker's exit-1 path (an unverifiable report, not a declared-but-unhit failure); no run header, verdict or urg dashboard of
that fresh-vdb run is retained. Beside it the commit retains gen_fu_l3_urg_slice1_nofcov_{grpinfo,dashboard,tests}.txt,
whose grpinfo lists gen_mul_ops_cg, gen_div_ops_cg and gen_isa_alu_reg_cg at 93-98 percent: the first attempt that reused
build g's vdb, which the transcript mentions in prose ("passed on the previous run's data") but whose manifest rows call it
only "urg -format text report". A reader finds a nofcov report full of coverage under a transcript sentence that says urg
wrote no grpinfo. Required: label the three files as the reused-vdb attempt (or drop them), retain the fresh-vdb red's run
header and verdict, and state in the transcript that the red is the protocol-error shape (round 0's) rather than an
unhit-bin FAIL; the unhit-bin red form exists in the FM1 catch and, after H-1, in the classifier reds.

### L-1 (low) [S4] Retained checker logs are not verbatim, and one log carries an in-line annotation

gen_manifest.md says every file is a verbatim copy; the checker prints an em dash in its PASS / FAIL line (ci/check_fcov_expectations.py:170-172)
and the retained copies carry `--` (slice1_check, slice1b_check, FM1_check) or `-` (shared_*_check, shared_driver). ASCII
normalisation is the right policy for the tree, but the manifest must say the copies are normalised. gen_fu_l3_shared_driver.log
holds a first landed-tree check with 112 `= UNHIT` lines and no summary, followed by a prose sentence inserted into the log
("the first check ran on a vdb the later canary runs had overwritten; the isolated re-runs below are the proof"); the
shared_*_check logs retain only the PASS lines. Move the annotation to the manifest's source column and retain the two
isolated re-runs' full outputs. Also every driver line says `uvm_err=1` while the verdict files say ERROR 0; the driver's
counting is not retained (audit-quoted).

### L-2 (low) [S4 record] Bin counts in the record are wrong

gen_tdd_fcov.md:15-16 and the commit subject say "1403 named bins (250 coverpoint bins, 1153 cross bins)"; the include has
250 coverpoint bins and 1403 cross bins (1653 named bins; the renderer's counter counts only lines starting with `bins `,
codegen:185). gen_component_api_fcov.md:106 gives CG-BIT-001 "51 / 380"; rendered and CSV: 373.

### L-3 (low) [S6 evidence] Two check logs are byte-identical under different attributions

gen_fu_l3_slice1_check.log (build h) and gen_fu_l3_slice1_check_build_g.log ("the first green check on build g") share md5
4629d71f... ; a deterministic run can reproduce identical counts, but no build-g urg report is retained to show a second
check happened. Retain the build-g report or drop the row.

### L-4 (low) [S2] Zcmp micro-ops are sampled as base OP-IMM instructions

RVFI exports a synthesized 32-bit word per Zcmp micro-op (anchors Section 0); cm.push / pop stack adjusts and cm.mvsa01 /
mva01s moves appear as addi words with OPCODE_OP_IMM, and the sampler never tests t.ext_exp_valid, so they land in
gen_isa_alu_imm_cg (cp_op.addi, cp_rs1_eq_rd.yes, cp_imm_class.zero). The plan's Sample line is silent. State in the plan
and the API doc whether expanded micro-ops count as OP-IMM samples, or exclude records with ext_exp_valid.

### L-5 (low) [S5, S4] Renderer hygiene

Three of the eleven die paths are unit-tested (plan / CSV bin mismatch, unsplittable cross bin, cross without a plan line);
the documented "group without a plan header" refusal (codegen docstring :14, API doc :86) is not. `--check` is run by the
unit test only and wired into no flow or ci gate. The LOG-054 cross-bin limitation is stated in the API doc, the plan, the
transcript and the intervention log but not in the svh header, where a reader of the include meets the cross bins.

### L-6 (low) [S2 collected mechanism] No TB-side referee for gen_isa_cov

report_phase prints `GEN_FCOV isa samples: ...` as info only; the witness covergroup has wit_referee. A sample-count
referee (a group's n_x > 0 iff its covergroup's sample count > 0, uvm_error otherwise) would catch a dropped sample
before urg does.

### L-7 (low) [schema] The proof manifests carry no anti_vacuity section

gen_fcov_proof_slice1.fcov.yaml and slice1b have `bins` only; gen_runtime_api.md Section 7c and every promoted manifest carry
one note per bin. The checker ignores the key, so nothing fails, but the proof manifests should follow the schema they
prove the renderer for.

### Informational

- I-1: cross coverage is read from urg's per-cross summaries, not by the checker, until Runtime's T-215 variable-form
  derivation lands (LOG-054); the six promoted manifests that name these groups would fail on their crosses today, and
  the record says so.
- I-2: the checker's discriminating behaviour was reproduced read-only (slice1 manifest against the alu report: 128 not hit,
  exit 2).

## 3. Answers to the Orchestrator's four questions

1. TB-side facts consistent with the anchors: yes for the sample conditions and the fields of all six groups; three
   classifiers compute the wrong class (H-1), one of them by a one-bit cast.
2. Every plan bin rendered, none dropped: yes, 250 + 1403 = plan = CSV; the record's counts are wrong (L-2).
3. A real fcov-expectation proof: in form yes (the real checker on real urg reports, per-bin HIT lines, reproduced from the
   retained reports); in substance not for the bins fed by the three defective classifiers, and for coverpoint bins only
   until T-215. The mutant is targeted at the sampler (the 16-bit c.mul decode) but proven on a pre-landing build without
   a retained control (M-1).
4. The cross-bin limitation is disclosed honestly in the API doc, the plan, the transcript and LOG-054; it is not stated in
   the include (L-5).

## 4. Principles check

dv-principles-check (docs/dv/dv_principles.md d9c27db18f511411): S1 not applicable (no stimulus policy change; the directed
programs are proof programs); S2 derive from intent: bins and conditions from the plan (conforming), three classifiers
wrong (H-1), Zcmp micro-ops unaddressed (L-4); S4 honesty: M-2, L-1, L-2, L-3; S5 single source: renderer from the CSV and
plan (conforming), --check unwired (L-5); S6 trust triad: TDD red is the protocol-error shape (M-2), mutation on a
pre-landing build (M-1), fcov-expectation proof real but partly false (H-1). One-line verdict: FAIL on H-1 until the
classifiers are fixed and re-proven.

## 5. Required for re-review

1. H-1: the three classifier fixes with a red each, the two proof runs re-run on the fixed sampler, checker logs regenerated.
2. M-1: FM1 re-run on the landed sampler with the ablation retained (build and original shas recorded).
3. M-2: the nofcov artifacts relabelled and the fresh-vdb red's header / verdict retained; the transcript's red sentence
   corrected.
4. Lows L-1..L-7 may close in slice 2; L-2 and L-3 are one-line record edits and should close with H-1.

## 6. Reconciliation with the cross-model artifact (dv/auto_dv/reviews/2026-09-03-claude-diff-0a2ffe48-a786543c.md, read after Sections 1-5 were written)

The artifact's verdict is APPROVE-WITH-CHANGES: one major, three minors, one nit. Its major is my H-1(a), the one-bit cast at
gen_fcov_pkg.sv:337. Adopted and verified from the retained logs: the count evidence -- gen_fu_l3_slice1b_check.log:85
`cp_slt_case.eq = HIT (count=168)` and gen_fu_l3_urg_slice1b_grpinfo.txt:3775/3778 `slti_eq 98` / `sltiu_eq 70`; the
artifact's arithmetic (168 under the one-bit compare, 84 under the plan's definition) is carried as its own and is the
number the re-proof must show. The artifact also names the promoted manifest that would earn false credit
(gen_test_isa_alu's cr_slt tuples). Its minors are my L-2 (the 1403 / 1653 count with the codegen:185 root cause, and the
"51 / 380" row) and the unretained FM1 ablation (part of my M-1). Its nit (opcodes hand-encoded as 7'b0110011 / 7'b0010011
while rtl/ibex_pkg.sv:75,78 define OPCODE_OP_IMM / OPCODE_OP) is adopted and verified as L-8.

Disagreements: the artifact states that the sampler's classifiers match the plan's definitions for cp_divisor and
cp_addi_wrap; H-1(b) and H-1(c) show they do not (the 33-bit negation of a zero-extended operand at :147-148; the forced-zero
rd_wdata at :322-326), with operand pairs from the proof program itself. It also treats FM1 as proof of the landed sampler
without noting the build predates build h (M-1), and reads the nofcov artifacts as the red without noting the retained
nofcov grpinfo carries coverage (M-2).

Mine that it does not carry: H-1(b), H-1(c), M-1 (pre-landing build), M-2, L-1, L-3, L-4, L-5, L-6, L-7. Its verifications
of the anchors (rvfi_insn 16-bit form, rd_wdata forced 0, shNadd truncated adder inputs, the decoder arms) agree with mine.

### L-8 (low, adopted from the artifact, verified) Opcodes hand-encoded

gen_fcov_pkg.sv:379 compares `t.insn[6:0]` with `7'b0110011` and `7'b0010011`; rtl/ibex_pkg.sv:75,78 name them OPCODE_OP_IMM
and OPCODE_OP and the package is already imported elsewhere in the TB. Use the enum for the two opcode compares.
