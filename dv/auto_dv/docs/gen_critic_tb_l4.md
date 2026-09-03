# Critic verdict: tb-infra landing 4, T-205 slice 2 (commit 5b8a0fb, diff base 24109b8)

Artifacts reviewed (committed blobs at 5b8a0fb; sha256 first 16 hex):

- dv/auto_dv/tb/gen_fcov_codegen.py  43b2fe1b77cb2c90
- dv/auto_dv/env/gen_fcov_groups.svh  a03e5cb4e7f1faa8
- dv/auto_dv/env/gen_fcov_pkg.sv  551aacf81c6165b7
- dv/auto_dv/evidence/gen_tdd_fcov.md  44d3ce4d7e43c424
- dv/auto_dv/mutations/gen_mut_fcov.md  a74da3ec01faa9ed
- dv/auto_dv/evidence/gen_critic_response_fcov.md  7d58582636345171
- dv/auto_dv/evidence/gen_critic_response_fu1.md  2ffbfbb29d1ef976
- dv/auto_dv/evidence/gen_fcov_proof_slice2a.fcov.yaml  d62730d56effa2a9
- dv/auto_dv/evidence/gen_fcov_proof_slice2b.fcov.yaml  7a03d94f82020861
- dv/auto_dv/evidence/gen_fcov_proof_slice2c.fcov.yaml  f6bf73230b1294f3
- dv/auto_dv/evidence/gen_fcov_proof_slice1_fm1_ablation.fcov.yaml  ae458d610ec6cc66
- dv/auto_dv/stim/gen_directed/gen_zcmp_directed.S  b9fba227b43f63cf
- dv/auto_dv/stim/gen_directed/gen_zcmp_dummy_directed.S  9ff5f0f364191270
- dv/auto_dv/stim/gen_directed/gen_bitcnt_directed.S  9ed3e4d46a838b24
- dv/auto_dv/stim/gen_directed/gen_zca_directed.S  d507281685bd36b1
- dv/auto_dv/docs/gen_component_api_fcov.md  4220bdaa1f8809b9
- dv/auto_dv/evidence/gen_tdd_logs/gen_manifest.md  da7953b447a4510a
- the 84 added logs under dv/auto_dv/evidence/gen_tdd_logs/ (fcov/gen_fu_l4_*, gen_fu_l1c_MUTK_*, gen_fu_l1c_compile_e / e_driver, the two T-218 red1 excerpts; manifest rows recomputed)

Date: 2026-09-03 (UTC). Role: Critic (reviewer other than the author). Basis: docs/dv/dv_principles.md d9c27db18f511411,
the fcov-expectation skill, DV_prompt.txt, gen_fcov_plan.md (CG-BIT-002, CG-CMP-001, CG-CMP-006), rtl-arch's
evidence/gen_cg_sampling_anchors.md, the Zcmp specification via the anchors, this clone's RTL (rtl/ibex_core.sv,
rtl/ibex_cs_registers.sv, rtl/ibex_wb_stage.sv, rtl/ibex_id_stage.sv), LOG-054, LOG-058.
Method: clean archive of 5b8a0fb; library self-test, flow self-test, --check-red-signatures, gen_fcov_codegen --check,
gen_knobs_codegen --check and GEN_UT_FCOV_CODEGEN PASS on the archive; two unnamed subagents (an evidence audit of the
84 logs and the manifest with a read-only re-run of ci/check_fcov_expectations.py on every retained urg report against
every manifest; a renderer / sampler derivation review), both told the fence and kept out of dv/auto_dv/reviews/; the
findings below were checked first-hand in the blobs and the RTL. EXPOSURE: before this review the Orchestrator's messages
told me the cross-model artifact's major (cp_minstret_once compares the compressed-retire counter captured before the
record's own increment) and a git log subject line told me its verdict level; the mechanism was re-derived here from the
RTL and the sampler, and the artifact was not read before Sections 1-5. Section 6 reconciles.

CRITIC VERDICT: REQUEST-CHANGES

The three new covergroups render completely and the Zcmp collector samples only expanded-instruction records with the
sequence facts derived from the RVFI record; the proofs are real checker runs on the runs' own reports. Three bins are hit
by the wrong mechanism (H-1), of which cp_minstret_once never measures the instruction it is defined on; two sampler
mutants were proven on a pre-landing sampler without retained controls (M-1); the commit message claims a sampler unit
test that does not exist (M-2); cp_dmem_delay samples the knob instead of the plan's observed latency class (M-3).

## 1. What was verified

### 1.1 Renderer

Per group, plan coverpoint bins = rendered coverpoint bins, CSV cross bins = rendered cross bins: gen_bit_count_cg 52 / 147,
gen_cmp_zca_cg 46 / 250, gen_cmp_zcmp_pushpop_cg 47 / 244; nine groups 395 named coverpoint bins + 71 `ignore_bins na` and
2044 cross bins (the svh per-group headers agree; grep of `bins ` lines = 2044 cross bins, `ignore_bins` = 71). The two
coverpoints without CSV rows (cp_reg3 of CG-CMP-001, cp_dmem_delay of CG-CMP-006, both operand-only per the plan) render from
the plan line: the renderer's refusal changed from plan / CSV coverpoint-set equality to "CSV coverpoints without a plan bins
line" (gen_fcov_codegen.py:125-141). No plan or CSV bin is unrendered. --check up to date on the archive; the unit test PASS.

### 1.2 Zcmp collector (CG-CMP-006) samples TB-side facts from expanded-instruction records only

gen_fcov_pkg.sv:557-561: only records with t.ext_exp_valid reach zp_start / zp_step; a non-expanded record while a sequence
is open abandons it; a trap record abandons it; the sample fires on t.ext_exp_last (:534) for a kind decoded from the 16-bit
source word t.ext_exp_insn (:495-505: w[15:13] == 101, w[1:0] == 10, w[12:8] in {11000, 11010, 11100, 11110}), never from a
micro-op word. rlist / spimm / N / stack_adj follow zcmp.adoc through the anchors (:506-508); order and addresses from the
micro-ops' rs1_rdata (sp), rs2 / rd and the expected sp - 4k / sp + adj - 4k; ret alignment from the jalr micro-op's
rs1_rdata[1:0] (:532-533); dummy_en from the ISA model's cpuctrlsts bit 2 (:546); no DUT internal is read. cm.mvsa01 /
mva01s records enter with kind -1 and never sample. The plan's Sample line (gen_fcov_plan.md:706) and anchors Section CG-CMP-006
match this. Verified by the zcmp proof run: 290 sequences, abandoned 0, and cr_insn_rlist_spimm 192 / 192.

### 1.3 CG-BIT-002 and CG-CMP-001 samplers

bit count: OP-IMM funct3 001 with insn[31:20] in {0x600, 0x601, 0x602} (:577); classifiers in the plan's bin order. Zca: a
16-bit retirement that is not a micro-op (:564), the next record's length from the following record (:488), the straddle
coverpoint from 32-bit retirements (:573-575); HINT encodings are not excluded (L-6). The slice-1 cast fix is in (:346
`rs1 == 32'(imm)`; no `logic'(` cast remains) and the re-run alu proof counts eq 84 (gen_fu_l4_urg_slice1b_grpinfo.txt; the
old run counted 168). The two slice-1 defects deferred to slice 3 (div_divisor_cls abs at :156-157; addi_wrap on rd_wdata at
:331 / :605) are still present, as ruled (I-4).

### 1.4 Evidence audit

- Manifest: 84 rows, md5 and bytes recomputed from the blobs, 84/84; no file without a row; working-tree copies equal the blobs.
- Builds: i bf213aa0edb01c6a, j 33ee96f28834a162, k 893384b8eec4e6d5, FM2 0dc3381eb2ca0793, FM3 13317a26ec420c27, FM4
  d710be74d01d442a, MUTK 1b2501fd1b7197e3, l1c e 94bb3021a5c67974; every header sha equals a compile log's; the recipe of
  gen_tb_local.sh applied to the clean archive gives 893384b8eec4e6d5 = build k = every final run header (12 runs, 19:07-19:10Z).
- Proof runs on k: bitcnt 406 records / 0 mismatches; zca 439 / 0; zcmp 519 / 0 (290 sequences), the same program under min1,
  long and random (517-519 / 0), zcmp_mis 22 / 0; muldiv 10206 / 0 and alu 22787 / 0 re-run on the fixed sampler;
  zcmp_irq_sparse 1288 / 0 (abandoned 4, an entry split). The dummy-enabled run fails the comparator by design (27 rows; the
  B8 reproduction) and is retained with its export.
- urg reports: nine, each carrying the ten groups; the reports carry no urg command line, so "the run's own vdb" is
  corroborated by the counts only (each report's group counts equal exactly one run's GEN_FCOV sample counts, and no two
  reports agree) (L-3).
- Checker: slice2a PASS 52 / 52 (bit count), slice2b PASS 46 / 46 (Zca), slice2c PASS 38 / 38 (push/pop, coverpoint bins the
  short-regime run hits; the nine undeclared bins are named in the manifest with the reason); slice1 and slice1b re-run PASS
  128 / 122; FM1's ablation manifest (127 bins, slice1 minus c_mul) PASS. Read-only re-runs on the retained reports reproduce
  every retained PASS line after the em-dash normalisation (L-8), and each manifest passes only on its own run's report (the
  slice2c manifest fails on the min1 / long / random reports on cp_dmem_delay.short and on the dummy report with 22 unhit):
  the checker discriminates.
- Mutants FM2 (every Zca successor reported 16-bit -> cp_next_len.n32 unhit) and FM3 (cm.pop decoded as cm.push -> cp_insn.cm_pop
  unhit) are caught by the checker by bin name (gen_fu_l4_FM2_FM3_check.log); FM4 (the slice-1 cast re-introduced) is NOT caught
  (`PASS -- all 122 declared bins hit`, eq 168) and the record says so. MUTK is the CR-1C-L-4 without-export re-run of the
  landing-1c mutant (uvm_fatal at time 0, `emitted row scrkey/req has no registered writer`), on the 1c mutant build.
- CR-1C-L-1..L-5 rows in gen_critic_response_fu1.md: the c / d counts corrected to 9 and 8 (the retained excerpts count 9 and
  8), build e's compile and driver logs retained, the drain-window derivation and the grant-stamp comment (the derivation
  itself is wrong, see gen_critic_tb_l2b.md L-17, not repeated here), MUTK's without-export run retained. Accepted as the
  closure of my 1c lows except the derivation.
- T-218 canonical red excerpts gen_regime_refuse_red1_* and gen_witness_foreign_red1_* are byte copies of the existing
  retained excerpts (verified by cmp); the B8 reproducer run is gen_fu_l4_lockstep_zcmp_dummy_* with its export.
- Weakening scan (git diff 24109b8 5b8a0fb -- dv/auto_dv/env dv/auto_dv/tb dv/auto_dv/isa): nothing removed or defaulted off;
  the trap filter moved below the collector so trap records reach the abandon path and the Zca flush (by design); the yaml
  and gen_tb_pkg.sv changes are comment-only.

## 2. Findings

### H-1 (high) [S6 fcov-expectation; S2] Three declared or rendered bins are hit by the wrong mechanism

(a) cp_minstret_once (gen_fcov_pkg.sv:497, :544, :562) computes `t.ext_mhpmcounters[7] - zp_mhpm10_before` where t is the LAST
    micro-op record and zp_mhpm10_before the counter of the record BEFORE the first micro-op. RVFI captures mhpmcounter[10]
    at the record's ID-done (rtl/ibex_core.sv:2071-2073, :2122) through the read mux that adds the speculative increment of the
    instruction then in WB (rtl/ibex_cs_registers.sv:1687-1692; rtl/ibex_wb_stage.sv:206-207), so a record's value counts
    compressed retirements through its PREDECESSOR and never its own. A cm.* is counted once, at its LAST micro-op
    (rtl/ibex_id_stage.sv:1218-1220 excludes INSTR_EXPANDED and INSTR_EXPANDED_COMMIT only), which increments after the last
    record's capture. The delta is therefore 1 iff the instruction before the cm.* was a counted compressed instruction; the
    plan's bin `yes{1}` "minstret delta over the instruction == 1" (gen_fcov_plan.md:717) is hit by the neighbour. The zcmp proof
    run shows yes = 193 of 290 sequences (gen_fu_l4_urg_lockstep_zcmp_grpinfo.txt), the sequences preceded by a 16-bit
    instruction; the manifest slice2c declares the bin and the checker reports it HIT. Fix: take the delta between the first
    micro-op's record and the first non-expanded record after the sequence (or the next record's counter minus the last
    micro-op's), with a red showing the current expression scoring a cm.* preceded by a 32-bit instruction as unhit and the
    fixed one as hit for every sequence.
(b) gen_bit_count_cg cp_result is sampled from t.rd_wdata on rd = x0 records too (:580), where the RTL forces rd_wdata to 0
    (rtl/ibex_core.sv:2344-2346, the anchors' Section 0): five of the program's eleven bit-count instruction forms write x0, and
    the proof report counts cp_result.r0 = 102 of 214 samples (gen_fu_l4_urg_bitcnt_grpinfo.txt) where the genuine zero results
    are a handful. Same class as gen_critic_tb_l3.md H-1(c). Fix: result class -1 (no sample of that coverpoint) on rd = x0, or
    a cross that excludes rd_x0.yes, per the plan owner's choice.
(c) Zcmp micro-ops still enter the base groups: the chain at :583-624 has no ext_exp_valid guard, so the synthesized
    `addi sp, sp, imm` (the LAST micro-op) and `li a0, 0` (popretz) words are sampled into gen_isa_alu_imm_cg; the zcmp proof
    run reports alu_imm = 354 for a program whose own OP-IMM instructions are a few dozen (290 sp adjusts + 48 popretz words
    account for the rest). My gen_critic_tb_l3.md L-4 raised this as a plan question; with the counts in a proof run it is an
    over-count of cp_op.addi, cp_rs1_eq_rd.yes and cp_imm_class bins by instructions the program does not contain. Fix: guard
    the base chain on !t.ext_exp_valid (the collector owns those records), or the plan states that expanded micro-ops count.
- Why high: as in landing 3, the fcov-expectation proof is the covergroups' only proof, and for these bins the HIT is not what
  the plan defines; (a) is systematic (the bin can never measure its own instruction). LOG-058's classifier unit test over a
  directed operand table would have caught (a) and (b) on the first run.

### M-1 (medium) [S6 mutation-proof] FM2 and FM3 were proven on a pre-landing sampler without retained controls

gen_fu_l4_FM2_FM3_check.log: both mutants applied to a gen_fcov_pkg.sv with original sha256 86fa86e80dd8eb83, which is not the
committed blob 551aacf81c6165b7 (FM4's original is the committed blob); compiled 19:03-19:04Z, before build k (19:07Z). The
mutation record's ablation column asserts "the manifest without that bin passes" for both; no such manifest or log is in the
commit (FM1's ablation manifest is). This repeats gen_critic_tb_l3.md M-1 one landing later. Required: re-run FM2 and FM3 on
the landed sampler (after H-1) with the ablation manifests and checker logs retained; the record names the original and
build shas.

### M-2 (medium) [S4 honesty] The commit message claims a sampler unit test that does not exist

The commit subject says the fcov checker cannot catch over-counting and "the sampler unit test carries that check". No file
in the tree tests gen_isa_cov's classifiers (gen_isa_cov appears only in gen_fcov_pkg.sv and gen_env_pkg.sv; dv/auto_dv/tb/unit/
holds the renderer, handles, knobs-codegen and memory-model tests); gen_mut_fcov.md itself says "ablation: none: the proof
manifest has no count assertion" and "the renderer's unit test cannot help (the classifiers are hand-written)". The FM4
admission in the mutation record is honest; the commit message contradicts it. LOG-058 now requires a classifier unit test
over a directed operand table for every sampler landing from slice 3; for this landing the claim must be withdrawn in the
record (or the test landed), and the test, when it lands, must carry the eq count (84 on gen_alu_directed.S), the minstret
delta and the rd = x0 result class as cases.

### M-3 (medium) [S2 derive from intent] cp_dmem_delay samples the configured knob, not the observed latency class

gen_fcov_plan.md:719 defines cp_dmem_delay as "dbus monitor rvalid latency class during the sequence: min1{1}, short{[2:4]},
long{[5:$]}, mixed{varies}"; the sampler (:510-516) maps cfg.knob_dmem_rvalid_delay (min1 / short / long, anything else ->
mixed). Under the random regime every sequence is scored mixed whatever latencies it saw; under long a sequence that happened
to see delays of 5 scores long correctly only by construction of the regime. The four bins are hit in the four regime runs
for the wrong reason in the random case. Required: derive the class from the sequence's observed rvalid latencies (the bus
monitor / mem model records them) or amend the plan's definition to the regime with the DV Lead, and say which in the API doc.

### L-1 (low) [S4 record] Bin counts and the API doc table

"466 coverpoint bins" (commit subject, gen_tdd_fcov.md Section 2, gen_critic_response_fcov.md CM51-MIN-1 row) counts the 71
`ignore_bins na` with the 395 named bins: the new summary regex (gen_fcov_codegen.py:186) matches `ignore_bins na =` too, the
same class of error as the slice-1 count it replaced. gen_component_api_fcov.md:110-111 gives gen_cmp_zca_cg "54 / 169" and
gen_cmp_zcmp_pushpop_cg "51 / 244"; rendered: 46 / 250 and 47 / 244.

### L-2 (low) [S4 record] Build j named as the landed sources

gen_tdd_fcov.md Section 2 calls build j 33ee96f28834a162 "the landed sources" and, later, build k 893384b8eec4e6d5 the landed
sources; the archive's recipe hash is k. Correct the j sentence.

### L-3 (low) [S6 evidence] urg reports without their command line

The nine grpinfo files carry no urg invocation or -dir path; the "own vdb" claim rests on the counts matching one run each.
Retain the urg command line (or the dashboard's test path) with each report.

### L-4 (low) [S4] The dummy-enabled run's coverage report is retained without an exclusion statement

gen_fu_l4_urg_zcmp_dummy_grpinfo.txt records cp_dummy_en.on = 8 and other push/pop bins from the B8 reproduction run, which
fails the comparator by design. No proof manifest declares a bin from it and every manifest fails on it (checker matrix), so
it is out of the evidence in fact; the manifest row and the transcript should say that the report is retained as the B8
record and is not coverage evidence.

### L-5 (low) [S2] cp_rvfi_tags_ok is a weak proxy

The plan's tag check (rvfi_insn == the synthesized 32-bit word per micro-op, pc conventions) is implemented as pc_wdata ==
pc_rdata on non-last micro-ops and insn[1:0] == 11 (:522-523). State the reduced check in the API doc or implement the word
compare (the expected word is derivable from the source word and k).

### L-6 (low) [S2] HINT encodings sample as normal Zca bins

c.li / c.lui / c.mv / c.add / c.slli with rd = x0, c.addi with imm 0 and c.nop with nzimm are HINTs; the anchors flag them and
the plan is silent; the sampler classifies them by form. A plan sentence (count or exclude) settles it.

### L-7 (low) [S6] Renderer refusal loosened without a fixture

The plan / CSV coverpoint-set equality became one-directional to admit operand-only coverpoints; gen_ut_fcov_codegen.py is
unchanged and has no fixture for a plan coverpoint without CSV rows nor for the summary count. Add both.

### L-8 (low) [S4] Checker logs normalised while the manifest says verbatim

The eight retained checker logs carry `--` where ci/check_fcov_expectations.py prints an em dash; gen_manifest.md still calls
every file a verbatim copy (gen_critic_tb_l3.md L-1, persisting). Say "ASCII-normalised" in the manifest header.

### L-9 (low) [S5] Hand-coded jalr opcode

gen_fcov_pkg.sv:532 compares t.insn[6:0] with 7'b1100111 after CM51-NIT-1 introduced ibex_pkg::OPCODE_OP / OPCODE_OP_IMM
elsewhere; use ibex_pkg::OPCODE_JALR.

### Informational

- I-1: the T-218 canonical red excerpts are byte copies of the existing retained excerpts, as their manifest rows say.
- I-2: the B8 reproducer (gen_zcmp_dummy_directed.S) is retained with its export and fails the comparator on 27 rows; the
  cause is rtl-arch's evidence/gen_b8_rtl_facts.md (reviewed separately).
- I-3: dummy instructions emit no RVFI record (rtl/ibex_core.sv:1864, :1894), so the sampler needs no dummy-specific exclusion;
  cp_dummy_en comes from the ISA model's cpuctrlsts, as the plan says.
- I-4: the slice-1 deferred defects (div_divisor_cls abs; addi_wrap on rd_wdata) are present at 5b8a0fb and tracked to slice 3.

## 3. Answers to the Orchestrator's questions

1. The Zcmp collector samples from expanded-instruction records only: yes (Section 1.2); the base groups do not exclude those
   records (H-1(c)).
2. Every plan bin of the three groups is rendered, none dropped (Section 1.1); the record's coverpoint count is wrong (L-1).
3. The proofs are real: the checker on the run's own report, reproduced read-only, discriminating between manifests; for
   cp_minstret_once, cp_result.r0 of the bit-count group and the alu_imm bins the HIT is by the wrong mechanism (H-1); the
   push/pop manifest declares the coverpoint bins the short-regime run hits and names the nine it does not.
4. The mutants are targeted at the samplers (FM2 the successor length, FM3 the kind decode, FM4 the cast); FM2 / FM3 were built
   on a pre-landing sampler with no retained controls (M-1).
5. The FM4 admission in gen_mut_fcov.md is honest and accurate against ci/check_fcov_expectations.py (a bin hit too often is not
   a miss); the commit message's "the sampler unit test carries that check" is not (M-2).
6. The dummy-enabled program is kept out of every proof manifest and checker run; its urg report is retained without a
   statement (L-4).

## 4. Principles check

dv-principles-check (docs/dv/dv_principles.md d9c27db18f511411): S2 derive from intent: bins and conditions from the plan
(conforming); H-1 (three mechanisms), M-3 (knob for observed latency), L-5, L-6; S4 honesty: M-2, L-1, L-2, L-4, L-8; S5: L-9;
S6 trust triad: fcov-expectation proofs real but partly by the wrong mechanism (H-1), mutation evidence on a pre-landing
sampler (M-1), the classifier unit test LOG-058 requires absent (M-2). One-line verdict: FAIL on H-1 until the three
mechanisms are corrected and re-proven.

## 5. Required for re-review

1. H-1: the three fixes, a red each (the current expression's wrong bin shown, then the right one), the affected proof runs
   re-run and their checker logs and urg reports regenerated; the transcript's counts updated (eq 84 stays).
2. M-1: FM2 / FM3 re-run on the landed sampler with ablation manifests and logs retained.
3. M-2: the commit-message claim withdrawn in gen_tdd_fcov.md, and the LOG-058 classifier unit test landed with slice 3
   carrying the eq, minstret and rd = x0 cases.
4. M-3: cp_dmem_delay from observed latencies or a plan amendment, stated in the API doc.
5. Lows may close with slice 3; L-1 and L-2 are record edits and should close with H-1.

## 6. Reconciliation with the cross-model artifact (dv/auto_dv/reviews/2026-09-03-claude-diff-24109b89-5b8a0fb0.md, read after Sections 1-5 were written)

The artifact's verdict is APPROVE-WITH-CHANGES: one major, three minors, two lows. Its major is my H-1(a) with the same
evidence (yes = 193 of 290 in all four regime runs, the 97 misses the sequences entered from a 32-bit instruction, 7 of 8 in
the dummy run) and the same fix; adopted from it: the 97 samples fall into `ignore_bins na` silently, so the GEN_FCOV summary
line should print the "no" count of each ok-coverpoint (added to H-1(a)'s required change). Its first minor (the API doc
counts 54 / 169 and 51 / 244) is my L-1; its third minor (the hand-coded jalr opcode) is my L-9.

Adopted after verification:
- L-10 (low): gen_fcov_pkg.sv:546 hand-encodes cpuctrlsts.dummy_instr_en as bit [2] while the yaml constants home carries
  GEN_CPUCTRLSTS_SYNC_EXC_SEEN_BIT, GEN_CPUCTRLSTS_DOUBLE_FAULT_SEEN_BIT; add GEN_CPUCTRLSTS_DUMMY_INSTR_EN_BIT and use it
  (the dummy bit is absent from the yaml, verified).
- L-7 amended: the renderer's exemption for a plan coverpoint without CSV rows should be gated on the plan's explicit
  `[operand-only:` marker (11 occurrences in gen_fcov_plan.md) and keep dying otherwise, with a unit-test case for the
  unmarked case; my L-7 asked for the fixture only.
- Its second low (the drain-window derivation "2 x 32" equals the constant with no margin for the response-to-record lag) is
  the same defect as gen_critic_tb_l2b.md L-17 (where the announcement's grant stamp makes the bound too small by a grant
  window as well); carried there, not repeated.

Disagreement: the artifact confirms "466 coverpoint bins" by recounting with the renderer's own regex; that regex matches
`ignore_bins na =` as well, so the figure counts the 71 exclusion bins with the 395 named bins (L-1); urg's Variables tables
report the named counts (52, 46, 47 for the three groups).

Mine that the artifact does not carry: H-1(b) (cp_result.r0 on rd = x0 records), H-1(c) (Zcmp micro-ops in the base groups),
M-1 (FM2 / FM3 on a pre-landing sampler without controls), M-2 (the commit message's sampler unit test), M-3 (cp_dmem_delay
from the knob), L-2, L-3, L-4, L-5, L-6, L-8.
