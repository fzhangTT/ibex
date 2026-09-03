# Critic verdict: tb-infra landing 5, T-205 slice 3 (commit a9b63ae, diff base 50971ad), reviewed as tb_l5 alone

Scope note: the commit subject claims the abs, addi_wrap and cp_minstret_once classifier fixes and the LOG-058 classifier unit test;
the diff carries none of them and tb-infra's transcript does not claim them (LOG-065 records the subject as the Orchestrator's
error). This file therefore judges the three new covergroups, the renderer change, the B4 reproducer and the B8 mapping; the
gen_critic_tb_l3.md and gen_critic_tb_l4.md re-reviews wait for landing 6.

Artifacts reviewed (committed blobs at a9b63ae; sha256 first 16 hex):

- dv/auto_dv/env/gen_fcov_pkg.sv  17e8e582968cb01e
- dv/auto_dv/env/gen_fcov_groups.svh  222f415428fa1937
- dv/auto_dv/tb/gen_fcov_codegen.py  ba9721c112e359fa
- dv/auto_dv/tb/unit/gen_ut_fcov_codegen.py  87f85975c6b7110f
- dv/auto_dv/evidence/gen_tdd_fcov.md  5f7eb06c79f33f2b
- dv/auto_dv/mutations/gen_mut_fcov.md  912afe7b36644b77
- dv/auto_dv/docs/gen_component_api_fcov.md  4f9edf5449a581f3
- dv/auto_dv/evidence/gen_b8_row_mapping.md  94256c3971a6b8f7
- dv/auto_dv/evidence/gen_fcov_proof_slice3a.fcov.yaml  f6a078db98ec623c
- dv/auto_dv/evidence/gen_fcov_proof_slice3b.fcov.yaml  cb025bbb65affa11
- dv/auto_dv/evidence/gen_fcov_proof_slice3c.fcov.yaml  89b617431c2e2499
- dv/auto_dv/stim/gen_directed/gen_zcmp_mv_directed.S  a7093edad6c9a1b2
- dv/auto_dv/stim/gen_directed/gen_zcmp_mv_reserved_directed.S  25973e6f0f231160
- dv/auto_dv/stim/gen_directed/gen_branch_directed.S  020b7b9760a01190
- dv/auto_dv/stim/gen_directed/gen_csr_warl_directed.S  45f22cb64106d22e
- dv/auto_dv/evidence/gen_tdd_logs/gen_manifest.md  5a27e75d6b50ea69
- the 85 added logs under dv/auto_dv/evidence/gen_tdd_logs/fcov/gen_fu_l5_* (manifest rows recomputed, 85/85)

Date: 2026-09-03 (UTC). Role: Critic (reviewer other than the author). Basis: docs/dv/dv_principles.md d9c27db18f511411,
the fcov-expectation skill, gen_fcov_plan.md (CG-CMP-007, CG-CSR-002, CG-ISA-007), rtl-arch's evidence/gen_cg_sampling_anchors.md
sections 8-10, the Zc specification (tools/specs/riscv-isa-manual/src/unpriv/zcmp.adoc), rtl/ibex_compressed_decoder.sv,
rtl/ibex_cs_registers.sv, LOG-054, LOG-058, LOG-065.
Method: clean archive of a9b63ae; library and flow self-tests, gen_fcov_codegen --check, gen_knobs_codegen --check and
GEN_UT_FCOV_CODEGEN PASS on the archive; two unnamed subagents (an evidence audit of the 85 logs with read-only checker re-runs; a
renderer / sampler derivation review), both told the fence and kept out of dv/auto_dv/reviews/; the findings below checked
first-hand in the blobs, the spec, the RTL and the retained urg report. EXPOSURE: the Orchestrator's queue message named the
cross-model artifact's H-2 (the Zcmp sreg field mapped as x(8 + r)) before this review; H-1 below was re-derived from the
sampler, the specification and the RTL, and the artifact was not read before Sections 1-5. Section 6 reconciles.

CRITIC VERDICT: REQUEST-CHANGES (H-1; M-1; M-2 adopted from the artifact and verified)

The three groups render completely, the branch and CSR-WARL samplers derive from the plan and the RTL, and the proofs are real
checker runs on the runs' own reports with the automatic cross bins gone. The move-pair collector maps the Zcmp sreg field
wrongly for six of its eight values, so its ok and hazard bins are hit for the wrong reason and 120 of 130 legal pairs fall
silently into the ignore bin (H-1); the FM6 record misstates the un-mutated counts (M-1).

## 1. What was verified

### 1.1 Renderer

Per group, plan coverpoint bins = CSV = rendered and CSV cross bins = rendered: gen_cmp_zcmp_mv_cg 29 / 134, gen_csr_trap_setup_warl_cg
67 / 143, gen_isa_branch_cg 28 / 180; twelve groups 519 named coverpoint bins + 100 `ignore_bins na` and 2501 cross bins (my count
of the svh). Every coverpoint's bin order equals the plan's (the sample-argument order). The tuple parser now accepts comma- or
space-separated tuples and maps a 1-bit value part to `b<value>` (two unit-test cases added). `option.cross_auto_bin_max = 0` is in
all twelve groups; the ten build-m urg reports carry no "Automatically Generated" section, where every landing-4 report carried 40
(the slice-1a report 52 automatic rows), and the earlier five proof manifests still PASS on build m (128 / 122 / 52 / 46 / 38).

### 1.2 Samplers against the plan, the anchors and the RTL

- gen_isa_branch_cg: BRANCH with funct3 not 01x, or the 16-bit c.beqz / c.bnez form, trap-free; taken = pc_wdata != pc + len; the
  B-type and CB immediates assembled in the correct bit order and sign-extended; offset classes exact at the 13- and 9-bit extremes
  (4094 / -4096, 254 / -256; the program's raw words decode to them); signed and unsigned compares by form; target alignment on every
  record, wrap only when taken (the plan's literal carry-out). 218 samples, 27 of 28 coverpoint bins (cp_offset.self undeclared).
- gen_csr_trap_setup_warl_cg: a pair tracker over the eight CSRs; a CSR-op record with rd != x0 closes an open pair; writes open one
  (csrrw / csrrwi always, the set / clear forms only with a non-zero operand, as the decoder demotes the rest); the WARL masks equal the
  RTL (mstatus 0x00221888 = ibex_pkg.sv:701-706 and cs_registers.sv:774-787; mie 0x7FFF0888; mtvec 0xFFFFFF00 with mode 01 per
  cs_registers.sv:742-743; mcounteren bit 0 and 2..12 gated by mcounteren_writable_i) and the doc; the three proof runs differ only
  in the mcounteren gate knob, and cp_mcen_gate is the TB's drive, as the plan says. 215 pairs, 0 replaced, 65 of 67 coverpoint
  bins per run (the gate bin varies).
- gen_cmp_zcmp_mv_cg: the move forms recognised from the 16-bit source word (w[12:10] = 011, w[6:5] = 01 / 11), the two micro-ops
  collected under ext_exp_valid and checked as `addi dst, src, 0` with the register pair of their position, source values from the
  micro-ops' rs1_rdata, a boundary tracker for the neighbour facts. The register expectation is wrong: H-1.

### 1.3 Evidence audit

- Manifest 85 rows recompute; working-tree copies equal the blobs. Seventeen run headers, all with build shas: 86c7caf1d034cdec (build m,
  14 runs) equals the recipe hash of the clean archive under the tree's locale; FM5 / FM6 / FM7 shas equal their compile logs and the
  mutants' original gen_fcov_pkg.sv sha (17e8e582968cb01e) equals the committed blob. Ten urg reports, each on its own run (the
  covered-bin sums match exactly one run's GEN_FCOV counts).
- Lock-step: branch 8000 records / 0 mismatches, zcmp_mv 870 / 0 (130 sequences), csrwarl x3 3001 / 0, and the slice-1 / 2 programs
  re-run on build m with 0 mismatches. Checker: slice3a PASS 27, slice3b PASS 29, slice3c / _inv / _off PASS 65 each; the five earlier
  manifests PASS; read-only re-runs reproduce every retained line (each manifest passes only on its own report).
- FM5 (c.bnez as c.beqz -> cp_op.c_bnez unhit), FM6 (hazard tracker inert -> alu_prev and load_prev unhit) and FM7 (immediate CSR forms as
  register forms -> csrrci / csrrsi / csrrwi unhit) are built from the landed sampler and caught by name; the un-mutated proof is
  declared the ablation (no separate control runs).
- B4: gen_zcmp_mv_reserved_directed.S executes cm.mvsa01 with r1s' == r2s' (word 0xAC22), which zcmp.adoc:1174 makes illegal; the DUT
  retires two moves into x8 while the model traps (`isa_trap dut retired, model retired 0 trap=1 cause=00000002 tval=0000ac22`);
  retained as a red with its export and labelled a DUT finding. The B8 row mapping reconstructs the 27 comparator rows of the
  landing-4 dummy run from the export; the cause is rtl-arch's (reviewed separately).
- Weakening scan: nothing removed or defaulted off; the renderer's refusals stand.

## 2. Findings

### H-1 (high) [S2 derive from intent; S6 fcov-expectation] The move-pair collector maps the Zcmp sreg field as x(8 + r) for every r

- Code: gen_fcov_pkg.sv:521 `(32'h1 << (8 + mv_r1)) | (32'h1 << (8 + mv_r2))` (the hazard sources of cm.mva01s) and :543
  `logic [4:0] sreg = 5'(8 + (zp_count == 1 ? mv_r1 : mv_r2))` (the expected rd of cm.mvsa01 / rs1 of cm.mva01s).
- Specification and RTL: zcmp.adoc:1201-1202 `xreg1 = {r1sc[2:1]>0, r1sc[2:1]==0, r1sc[2:0]}`, i.e. s0 = x8, s1 = x9, s2..s7 =
  x18..x23; rtl/ibex_compressed_decoder.sv:156 and :162 expand exactly that; rtl-arch's anchors state the same mapping. The sampler is
  right for r in {0, 1} and wrong for r in 2..7 (it expects x10..x15).
- Effect, from the retained proof report gen_fu_l5_urg_lockstep_zcmp_mv_grpinfo.txt: cp_uop_count_ok.yes = 10 of 130
  pairs (the pairs with both fields in {0, 1}); the other 120 legal pairs fail the register expectation inside mv_ok and sample the
  coverpoint as na, with no counter and no error ("nothing silently dropped" is violated); cp_hazard_src.alu_prev = 33 where
  the program's genuine ALU hazards number a handful: the phantom sources x10 / x11 for r = 2 / 3 collide with the a0 / a1 the previous
  move wrote, so cr_insn_hazard.cm_mva01s_alu_prev (28) is hit for the wrong reason and the one genuine cm.mva01s ALU hazard
  (`addi s2, s2, 1; mva01s 2, 3`) scores none. cp_insn, cp_r1s, cp_r2s, cp_equal, cp_src_values and cp_b2b are unaffected.
- The slice3b manifest declares cp_uop_count_ok.yes and the hazard bins; the checker reports them HIT; the plan's anti-vacuity
  sentence ("a hit proves both moves retired with the sampled register pair") does not hold for 120 of 130 pairs. Same class as
  gen_critic_tb_l3.md H-1 and gen_critic_tb_l4.md H-1: a classifier defect a unit test over a directed table would have caught.
- Required: the spec mapping (`r < 2 ? 8 + r : 16 + r`) at :521 and :543 with a red (the current expectation scoring `mva01s 2, 3` as
  na, then yes); a counted, collected failure when a legal pair's micro-ops do not match the expectation (mv_ok == 0 on a non-reserved
  pair is a sampler or DUT defect, not a bin miss); the slice3b proof re-run expecting cp_uop_count_ok.yes = 130 and the hazard counts
  reconciled with the program (alu_prev 6, load_prev 2); FM6 re-run on the fixed sampler. This lands with the LOG-058 unit test in
  landing 6, and the sreg mapping is a case for that test.

### M-1 (medium) [S6 mutation record; S4] The FM6 record misstates the un-mutated counts and proves the tracker on mis-mapped sources

gen_mut_fcov.md's FM6 ablation column says the un-mutated run hits load_prev 2 and alu_prev 4 times; the retained report counts
alu_prev 33 (and FM5's column says c_bnez 15 where the check log counts 17). With H-1, the 28 cm_mva01s_alu_prev hits are
artefacts of the wrong source registers, so FM6 shows the tracker fires, not that it fires on the right registers. The record's
sentence that a build-l FM6 run named only load_prev has no retained log. Required: correct the counts from the retained logs, and
re-run FM6 after H-1 with the ablation manifest retained (as landing 4 did for FM1).

### L-1 (low) [S4 record] Counts and references in the transcript

gen_tdd_fcov.md Section 3: "619 coverpoint bins" counts the 100 `ignore_bins na` (519 named; urg's Variables tables report 519),
the same class as gen_critic_tb_l4.md L-1; "214 write / read-back pairs" where every csrwarl run reports csr_pairs=215; "Ruling
B4-R1 (DV Lead, gen_bug_log.md)" cites a ruling that gen_bug_log.md does not carry at a9b63ae (the file is unchanged there; B4-R1
appears at a later commit); the testlist entries file dv/auto_dv/work/tb-infra/gen_l5_testlist_entries.yaml is a work-tree path, not
in the commit; the build-l reds (26 of 28 bins, the unhit alu_prev and mtvec bins) have no retained report.

### L-2 (low) [S4] Retained checker logs normalised to a single hyphen

The thirteen check logs and the FM driver log carry `-` where ci/check_fcov_expectations.py prints an em dash (landing 4 used
`--`); the manifest header still calls every file a verbatim copy. Two different normalisations across two landings and no
statement. Say "ASCII-normalised" once in the manifest header and use one form.

### L-3 (low) [S6] The option line is untested and removes a diagnostic

gen_ut_fcov_codegen.py has no case for `option.cross_auto_bin_max = 0` (the "type-based" check counts only per_instance). The
automatic bins the option removes were also the only place where a sample outside the CSV's tuples left a trace (a B4 tuple, a
mis-classified pair); nothing collects those now. Add the unit-test case, and consider a per-cross catch-all bin or a TB-side count
of samples that fall into no named cross bin.

### L-4 (low) [plan] misa_legal / misa_illegal are unreachable and not ignored

The plan's ignore clause for CG-CSR-002 covers mstatush / menvcfg / menvcfgh with legal_only / illegal_only but not misa, whose
mask has no writable bit, so cr_csr_wpat.misa_legal and misa_illegal stay permanently uncovered in every report (2 of the 6
uncovered tuples of the On run). A plan question for the DV Lead: add misa to the ignore clause.

### L-5 (low) [schema] Proof manifests without anti_vacuity

The five slice-3 manifests, like the earlier five, have `bins` only; the promoted manifests carry an anti_vacuity note per bin
(gen_runtime_api.md Section 7c). Persisting from gen_critic_tb_l3.md L-7.

### Informational

- I-1: the commit subject's claim of the classifier fixes and the unit test is the Orchestrator's error (LOG-065); the three
  deferred defects are unchanged at a9b63ae (div_divisor_cls :166-167, addi_wrap :791, cp_minstret_once :507 / :577) and no test of
  gen_isa_cov exists; both are owed to landing 6 with the tb_l3 and tb_l4 re-reviews.
- I-2: the B4 reproducer's sampler treatment: the reserved (s0, s0) pair matches the x8 mapping, so on that run cp_uop_count_ok
  would score yes and cr_insn_equal.cm_mvsa01_yes would be hit; no proof manifest declares it and the lock-step proof shows it at 0;
  the promoted gen_test_cmp_zcmp_basic manifest declares it, which the B4 ruling moves to TP-CMP-051's expected-fail test.
- I-3: the FM catch runs have no separate ablation logs; the record declares the un-mutated proof the ablation, which is acceptable
  when the un-mutated report is retained (it is) and its counts are quoted correctly (M-1).

## 6. Reconciliation with the cross-model artifact (dv/auto_dv/reviews/2026-09-03-claude-diff-50971ad4-a9b63aeb.md, read after Sections 1-5 were written)

REQUEST-CHANGES: two highs, three mediums, three lows, one nit. Its second high is my H-1 with the same mechanism and the same
counts (10 of 130 ok pairs; 28 spurious cm_mva01s_alu_prev hits; the one genuine case scored none) and the same fix. Its first high
is the commit subject's classifier-fix claim, which I record as I-1 under LOG-065 (the Orchestrator's error, not the landing's);
adopted from it as L-6: the transcript should disown the subject's claim in words, so the record and the commit history agree,
and the LOG-058 rider items (FM1 rebuilt on the final sampler with its ablation; the fcov-off red as a real run) are still owed
with the classifier fixes to landing 6.

Adopted after verification:
- M-2 (medium, from its third medium): the three slice-3 TDD reds (build l: cp_offset.max_fwd and cr_op_align.c_bnez_word unhit;
  cp_hazard_src.alu_prev unhit; cr_mtvec_mode_lo.v01_nz and cr_mtvec_base_op.high_csrrs unhit) are narrated in gen_tdd_fcov.md
  Section 3 with no build-l check log or urg report retained (the l driver logs carry verdict lines only). Under the evidence rule
  an unretained red counts as nothing, so the TDD leg of this slice is asserted, not evidenced; I had this under L-1 and raise it
  to a medium, consistent with gen_critic_tb_l3.md M-2. Required: retain the red check logs and reports with the fix, as slices 1
  and 2 did.
- M-1 widened (its first medium): the FM6 driver log's one-bin catch is on the landed sampler's sha (17e8e582968cb01e), so the
  mutation record's "build l" explanation for it is wrong (the stale element was the manifest); and the reduced-manifest checker
  runs on the mutant reports are not retained for FM5-FM7 (FM1 had one). Both go into M-1's required change.
- L-7 (low, its second medium kept low here): CSR addresses hand-encoded at gen_fcov_pkg.sv:650 (12'h300 ... 12'h31A), opcodes at
  :625 (7'b1100011) and :708 (7'b1110011), the mstatus bit positions at :688, while ibex_pkg.sv defines CSR_MSTATUS (:472),
  OPCODE_BRANCH (:80), OPCODE_SYSTEM (:83) and CSR_MSTATUS_*_BIT (:701-706), and this file already imports ibex_pkg opcodes elsewhere
  (verified). Same class as gen_critic_tb_l4.md L-9; kept low because the values are right and single-sourced in the RTL package.
- L-8 (low, its first low): cp_mtvec_base_w.low tests the whole value (`v < 32'h1000`, :691) where the plan (gen_fcov_plan.md:1221)
  defines the coverpoint over mtvec[31:8] with low{< 0x1000}; the program's low patterns fall under both readings, so no retained
  count is wrong; align the classifier and the plan on one threshold.
- L-9 (low, its second low): cp_mcen_gate samples the TB knob string, not mcounteren_writable_i at the write as the plan says; the
  API doc discloses it and the knob is static per run, so the value is right; the same knob-for-observation pattern as
  gen_critic_tb_l4.md M-3, recorded as a plan deviation to be stated in the plan or read from the control interface.
- Its third low agrees with my L-1 (215 pairs; the work-tree testlist file) and adds that the plan's Sample line names a
  gen_chk_csr_readback pair completion while the sampler is an independent tracker (no such checker exists), so the anti-vacuity
  claim rests on the lock-step comparator: adopted into L-1 as a sentence for the API doc.
- Its nit (cp_wrap as the plan's literal carry-out is set for every backward branch and does not measure an address-space wrap) is
  carried as its own for the plan owner; the API doc already flags it.

Mine that the artifact does not carry: L-2 (the single-hyphen normalisation), L-3 (the untested option line and the lost
diagnostic), L-4 (misa legal / illegal unreachable and not ignored), L-5 (anti_vacuity absent), I-2 (the reserved pair's sampler
treatment).

## 3. Answers to the Orchestrator

The three groups are rendered completely and the renderer's automatic-bin removal is verified in the reports. The branch and
CSR-WARL samplers derive from the plan, the anchors and the RTL with no cast or width hazard found. The move-pair collector's
register mapping contradicts the specification and the RTL for six of eight sreg values, which the retained proof report shows as
10 of 130 pairs scoring ok; that is H-1 and the reason for REQUEST-CHANGES. The B4 red is retained and labelled a DUT finding; the
B8 mapping is consistent with the landing-4 export. The classifier fixes and the unit test are not in this commit, as LOG-065 says.

## 4. Principles check

dv-principles-check (docs/dv/dv_principles.md d9c27db18f511411): S2 derive from intent: two of three samplers conforming, the
move-pair register expectation contradicts the spec (H-1); S4 honesty: L-1, L-2, M-1's counts; S6 trust triad: fcov-expectation
proofs real (ten reports, checker reproduced) but the move group's ok bin is hit by the wrong pairs (H-1), sampler mutants caught on
the landed sampler (FM5-FM7) with the FM6 record wrong (M-1); the LOG-058 unit test still absent (owed, I-1). One-line verdict: FAIL on
H-1 until the mapping is fixed and re-proven.

## 5. Required for re-review

1. H-1: the mapping fix with its red, the collected failure for a non-matching legal pair, slice3b and FM6 re-run with the counts
   reconciled to the program; the sreg mapping as a case of the LOG-058 unit test.
2. M-1: the FM5 / FM6 counts corrected from the retained logs; FM6's ablation retained.
3. L-1 and L-2 are record edits and should close with H-1; L-3 with landing 6; L-4 is the DV Lead's; L-5 persists.
