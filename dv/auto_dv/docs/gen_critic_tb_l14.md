# Critic verdict: tb-infra landing 13, Slice B (commit 3bf3d6b, diff base c4a5fd5), reviewed as tb_l14

Scope (the Orchestrator's): the five Slice B covergroups CG-ISA-004 gen_isa_lui_auipc_cg, CG-ISA-005 gen_isa_hint_x0_cg, CG-ISA-006 gen_isa_jump_cg,
CG-MUL-004 gen_div_timing_cg and CG-CMP-002 gen_cmp_imm_edges_cg with their trust triad on build sb3; six directed programs; the rows CR-13 (my
tb_l13), CR-12 (my tb_l12), CM148, CM149, CM150; the new unit test gen_ut_intg_store. This is the recorded re-review of gen_critic_tb_l13.md
(9946323ce45e55ae, REQUEST-CHANGES: M-1) on landing 12.

Artifacts reviewed (committed blobs at 3bf3d6b; sha256 first 16 hex):

- dv/auto_dv/env/gen_fcov_pkg.sv  05f130a4502aae58
- dv/auto_dv/env/gen_fcov_groups.svh  c1010396ca7ff672
- dv/auto_dv/tb/gen_fcov_codegen.py  fc39a3fa5d3cb6f8
- dv/auto_dv/env/gen_rvfi_pkg.sv  a95a7fb5318c2b2c
- dv/auto_dv/tb/gen_tb_pkg.sv  c521436bd9d7ad95
- dv/auto_dv/tb/gen_icache_ram.sv  8b8f800a1a91f128
- dv/auto_dv/isa/gen_isa_shim.cc  3b40d309ccb652ce
- dv/auto_dv/isa/gen_ut_isa_shim.cc  02197e67b25a8412
- dv/auto_dv/gen_tb/gen_tests/gen_ut_intg_store.py  9e37130681b5e34f
- dv/auto_dv/stim/gen_directed/gen_lui_auipc_directed.S  8ae760a66f3044e7
- dv/auto_dv/stim/gen_directed/gen_hint_x0_directed.S  fb0d2bb03d7b302f
- dv/auto_dv/stim/gen_directed/gen_isa_jump_directed.S  f95956e8ef7b6470
- dv/auto_dv/stim/gen_directed/gen_div_timing_directed.S  baf74f7633ba903d
- dv/auto_dv/stim/gen_directed/gen_cmp_imm_edges_directed.S  88039f59c3f0f9eb
- dv/auto_dv/stim/gen_directed/gen_intg_store_directed.S  3ebe16f510c6d23c
- dv/auto_dv/evidence/gen_fcov_proof_slice6a.fcov.yaml  f2c77043c50ab0da
- dv/auto_dv/evidence/gen_fcov_proof_slice6b.fcov.yaml  379242eb66259d99
- dv/auto_dv/evidence/gen_fcov_proof_slice6c.fcov.yaml  caf061d427b06179
- dv/auto_dv/evidence/gen_fcov_proof_slice6d.fcov.yaml  c1faf930e38f2bd9
- dv/auto_dv/evidence/gen_fcov_proof_slice6e.fcov.yaml  9ebca549c2604beb
- dv/auto_dv/evidence/gen_fcov_proof_slice6e2.fcov.yaml  9aa6cdf345ced646
- dv/auto_dv/evidence/gen_fcov_proof_slice6e3.fcov.yaml  31d49bbe2e06ad2c
- dv/auto_dv/evidence/gen_fcov_proof_slice6e4.fcov.yaml  334521b1672a29eb
- dv/auto_dv/evidence/gen_tdd_fcov.md  dc327152b002a7de
- dv/auto_dv/evidence/gen_tdd_step2b.md  92a84d43395a0e70
- dv/auto_dv/mutations/gen_mut_fcov.md  91d85e05e2d9d8c4
- dv/auto_dv/mutations/gen_mut_step2b.md  0545a4ad8a915cf6
- dv/auto_dv/evidence/gen_critic_response_fcov.md  005779124779f106
- dv/auto_dv/evidence/gen_critic_response_fu2a.md  adae9e0a9986fdda
- dv/auto_dv/docs/gen_component_api_fcov.md  cf9a7ca47cccc644
- dv/auto_dv/docs/gen_component_api_isa_shim.md  22c3283c1ce0d6ad
- dv/auto_dv/docs/gen_component_api_scoreboard.md  0b793ab881f1cff8
- dv/auto_dv/evidence/gen_tdd_logs/gen_manifest.md  d4a9b519fd3ef755
- dv/auto_dv/evidence/gen_tdd_logs/fcov/gen_fu_l15_sources_sha256_sb3.txt  98518617fecfcf64
- dv/auto_dv/docs/gen_fcov_plan.md  c0013f6da8dbc522
- the 280 gen_fu_l15_* files under dv/auto_dv/evidence/gen_tdd_logs/{fcov,mutations,lockstep}/ (manifest rows recomputed 280/280) and the re-noted gen_fu_l14_lockstep_zcmp_dummy excerpt

Date: 2026-09-04 (UTC). Role: Critic (reviewer other than the author). Basis: docs/dv/dv_principles.md d9c27db18f511411; gen_fcov_plan.md
CG-ISA-004 (:383), CG-ISA-005 (:399), CG-ISA-006 (:410), CG-MUL-004 (:588), CG-CMP-002 (:646) and CG-CMP-009 (:785); tools/specs/riscv-isa-manual (the CJ, CB, CI,
CIW, CL / CS and CSS immediate bit orders; the J and I immediates; the HINT encodings); rtl/ibex_multdiv_fast.sv:426-503 (MD_IDLE to MD_FINISH on a zero
divisor without data-independent timing, the 31-count otherwise); rtl/ibex_icache.sv:1236-1246 (INVAL_CACHE writes consecutive indices on consecutive
cycles); rtl/ibex_decoder.sv:1111-1135 (alu_multicycle_o); rtl/ibex_load_store_unit.sv:258.
Method: detached git worktree of 3bf3d6b. Build sb3 identity first-hand: the recipe of gen_tb_local.sh on the tree gives 98518617fecfcf64 under the
UTF-8 sort, equal to the 47 sb3 run headers, the compile log and the sha256 of the retained 74-line list, byte-identical to my recompute: the landing's
build is the committed tree. Library and flow self-tests PASS; both codegen --check up to date; both codegen unit tests PASS; 24 covergroups and 3116
cross bins counted in the svh. The five samplers' decoders were checked by me against the compressed immediate bit orders (CJ, CIW, CL / CS, CSS, CI,
CB), the J and I immediates and the HINT encodings; the FM17-FM21 catch and ablation stamps, the hazard re-proof count, the unit-test case lines,
the red runs' images and the check logs were read in the logs. One unnamed subagent (an evidence audit of the 280 files, told the fence, kept out of
dv/auto_dv/reviews/), its findings re-checked where they carry weight. EXPOSURE: none beyond the Orchestrator's sha-and-scope message and the git log
subjects naming review levels; the CM150 rows quote the landing-12 artifact I had read for tb_l13. The landing-13 cross-model artifact was not read
before Sections 1-5; Section 6 reconciles.

CRITIC VERDICT: APPROVE. The REQUEST-CHANGES of tb_l13 on landing 12 is lifted: the store_same_slot_then_pop bin now means the plan owner's pattern
(the store record immediately before the pop) and re-proves at 1. The five Slice B covergroups follow their plan Sample lines with the same
approximations the multiply group states, their proofs run on the committed tree, each has a mutant caught with a stamped ablation and a retained
diff, and the deferred CM148 items are built with reds. Six lows (one adopted from the cross-model artifact after verification, Section 6), five of
them on the records.

## 1. What was verified

| item | as built | intent anchor | evidence |
|---|---|---|---|
| tb_l13 M-1 (CM150-M-1, CR-13-M-1) | store_same_slot_then_pop: the record immediately before the sequence is a plain store to one of the pop's load words (hz_prev_st_valid / hz_prev_st_addr at the sequence start; the 64-store queue removed) | the plan owner's ruling (plan v3r): the plan's bin, F-CMP-068 and TP-CMP-069 say a pop right after the store; narrower than the frame bound I proposed, and the ruling governs | count 1 on gen_zcmp_hazard_directed.S in all three regimes (3 before); slice5e / 5e2 / 5e3 PASS 26 / 26 / 24 on sb3, now stamped |
| tb_l13 L-5 / CM150-M-2 | prev_seq_kind cleared at every sequence start after the pair test reads it: only a sampled push / pop immediately before pairs | the plan's back-to-back | the b2b counts unchanged (2 / 3) |
| tb_l13 L-7 / CM150-L-3, L-4 | zp_addi_cycle removed; HZ_LAT_MIN1 / HZ_LAT_SHORT_MAX feed lat_cls, zp_delay_cls and hz_delay_cls; hz_delay_of maps the pushpop class by name (mixed to no bin); zp_regs and zcmp_sreg read one list zcmp_sx | tb_l13 | the unit rows on zp_regs unchanged and passing |
| tb_l13 L-2 | gen_ut_isa_cov on the FM16 build fails the rlist-class row (84 cases, 1 failure) and on the FM17 build the lui msb row (129 cases, 1 failure) | the classifier rows' red | gen_fu_l15_FM16_ut_isa_cov_zc_*, gen_fu_l15_FM17_ut_isa_cov_zc_* |
| tb_l13 L-1, L-3, L-4, L-6, L-8 | the shim doc counts section 15 by check calls (46); item 3's writer-rule wording fixed; the misattributed sentence dropped; the dummy excerpt header names the B8 red (row refreshed); the ablation derivation drops a removed bin's note (five Slice B ablations one note per bin; the checker's refusal is the flow owner's); every sb3 proof and re-check log stamped, the driver logs retained, each program's source sha256 beside its image crc (gen_fu_l15_program_*.txt, all equal to the committed .S blobs); cp_redirect_once.yes named; the .S rationale on scope | tb_l13 | the diff and the logs |
| gen_isa_lui_auipc_cg (CG-ISA-004) | lu_sample: cp_imm20 extremes then rand; pc_align from pc_rdata[1]; pc_region low / high / mid; cp_wrap for auipc as the 33-bit signed sum leaving [0, 2^32); rd_x0 | the plan block :383 | slice6a 13 bins PASS; FM17 (msb boundary moved) fails cp_imm20.msb, ablation 12 PASS |
| gen_isa_hint_x0_cg (CG-ISA-005) | hx_sample pended to the next record: an rd = x0 record of an rd-writing class (hx_writer_cls, the two-cycle bit ops by rtl/ibex_decoder.sv's alu_multicycle set; the compressed hints); hx_hint_cls the 32-bit HINT encodings (the canonical nop; the semihosting slli 0x1f / srai 7); cp_x0_read from the successor's encoding naming x0 in a field it has (hx_rs_field: Ibex reports 0 for absent fields) with rdata 0 | the plan block :399 | slice6b 42 bins PASS, cr_writer_read 42 / 42; FM18 (the semihost shamt moved) fails slli_x0_semihost, ablation 41 PASS |
| gen_isa_jump_cg (CG-ISA-006) | jp_sample: jal / jalr (funct3 0) / c.j / c.jal / c.jr / c.jalr; the J immediate {31, 19:12, 20, 30:21, 0} and the CJ offset {12, 8, 10:9, 6, 7, 2, 11, 5:3, 0} (both checked against the spec); cp_jalr_imm with 2047 as max_pos before the parity bin; cp_jalr_rs1 x0 / eq_rd / other; target align from pc_wdata[1], target odd from (rs1 + imm)[0]; cp_wrap on pc or rs1; pc_region zero_page / high / mid; cp_link_len | the plan block :410 | slice6c 29 bins PASS; FM19 (max_pos moved) fails cp_jalr_imm.max_pos, ablation 28 PASS |
| gen_div_timing_cg (CG-MUL-004) | dt_sample at the divide, dt_flush at the next record: cp_delta d2 / d37 / other iff neither wb_defer nor fetch_stall (the multiply group's ID-entry approximation); cp_dit tracked from the cpuctrlsts write records by op form (GEN_CPUCTRLSTS_DATA_IND_TIMING_BIT); div0 from rs2_rdata; cp_event_mid the first asserted edge of an irq line, the NMI line or debug_req strictly inside the window, from the irq / debug drivers' events; cp_prev / cp_next classes; cp_irq_latency le37 / gt37 | the plan block :588; rtl/ibex_multdiv_fast.sv:434 / :445 (MD_IDLE to MD_FINISH on a zero divisor without DIT: the d2 class), the 31-count path (d37) | slice6e / 6e2 / 6e3 / 6e4 PASS 24 / 24 / 28 / 25 under the default, long, irq-storm-with-NMI and sparse-debug regimes; FM20 (the full count moved to 36) fails cp_delta.d37, ablation 23 PASS |
| gen_cmp_imm_edges_cg (CG-CMP-002) | ie_sample per format: c.addi4spn nzuimm {10:7, 12:11, 5, 6, 00}, c.lw / c.sw {5, 12:10, 6, 00}, c.lwsp {3:2, 12, 6:4, 00} / c.swsp {8:7, 12:9, 00}, the CI imm6, c.lui, c.addi16sp {12, 4:3, 5, 2, 6, 0000}, the shifts (shamt 0 sampling nothing), the CJ and CB offsets, cp_sp_wrap, cp_link (all bit orders checked) | the plan block :646 | slice6d 46 bins PASS; FM21 (the addi4spn maximum moved) fails cp_addi4spn_imm.max, ablation 45 PASS |
| red first | on the landing-12 build (57e0518a803da03b, identified by the l14 list and compile log) the groups do not exist: each proof manifest checked against that build's report fails with every bin MISSING-FROM-REPORT (13 / 42 / 29 / 46 / 24); the unit-test reds above | the new-group red form used since Slice A | gen_fu_l15_slice6*_red_check_b12x.log (unstamped, L-3), gen_fu_l15_red_b12x_* |
| CM148-L-2 grace rule | a sweep write is an all-ways write at index 0 or at the index after the previous all-ways write one cycle later; the tag RAM passes its index; a correction's all-ways write opens no grace | rtl/ibex_icache.sv:1241-1246 (INVAL_CACHE increments the index every cycle, verified) | the same injections on both builds: 870 judged, qualified 682 (landing 12) against 866 (sb3), 0 missing on both: the 184 injections the old rule excused all pulsed; the index-0 correction left as the one misclassification (stated) |
| CM148-L-5 store half | a store record whose first word is the pending announced word replaces it with its own address (mtval = the LSU's last address for stores too) | rtl/ibex_load_store_unit.sv:258 | red on the landing-12 build with gen_ut_intg_store: isa_rd on the handler's mtval read (model 800002d0, DUT 800002d2) and 11 crash_dump rows, 21 lines; green on sb3: one internal NMI, 31 records, 0 mismatches |
| CM148-L-3 / L-4, CM149, CR-12 | the shim comments on their lines; review ids out of the unit-test comments, the section-9 title, the four .S headers and two test docstrings; the plain gen_ut_lockstep_icache_en run retained; the firing-count and sha rules stated under the mutant table; MUT-WIN described as the shifted slice with the b0h red cited and its diff retained; the corrected shas (b5c7b2b602d2087a, 68c8d74dfaacb9a8) and order 242; the window's upper edge "1 observed, 2 declared"; b0 / b0h / b2r lists and compile logs re-retained, nt3_b0 / sup3c_b0 stated lost | tb_l12, CM148, CM149 | the diff; the retained files |
| regression | 20 of 21 names PASS on sb3 (lockstep_zcmp_dummy the B8 red by design); the fourteen earlier proofs re-run and re-checked PASS, stamped; the sampler unit test 129 cases 0 failures | the landing's claim | the driver logs and verdicts |

## 2. Closure of the base verdicts

- gen_critic_tb_l13.md: M-1 CLOSED per the plan owner's ruling and the re-proof; L-1..L-8 CLOSED (L-3 in part: the checker's refusal of a note
  without a bin belongs to the flow owner, stated). The REQUEST-CHANGES on landing 12 is lifted.
- gen_critic_tb_l12.md: L-1..L-6 CLOSED (L-6 in part: the nt3_b0 / sup3c_b0 lists are gone and the L11-F3 FSDB was never kept, both stated).
- CM148 L-2..L-5, CM149, CM150 CLOSED as their rows say and the artifacts show.

## 3. Findings

### L-1 (low) [S4 record] "Not reached" bins that the manifests declare and the checks hit

gen_tdd_fcov.md Section 10 and the fcov API doc list cp_jal_off.self, cp_cj_off.self and cp_irq_latency.gt37 among the bins not reached, and the
two programs' headers say the jump to itself "is a loop and is not reached"; slice6c declares gen_isa_jump_cg.cp_jal_off.self and the check hits
it 19 times, slice6d declares cp_cj_off.self (22 hits) and slice6e3 declares cp_irq_latency.gt37 (35 hits, beside le37's 72). The self jumps are
the end-of-test spin loops, which do run; the manifests are right and the prose is wrong (gen_tdd_fcov.md's "slice6e3, 28 bins: ... cp_irq_latency
le37" omits gt37 although 28 = 24 + irq + nmi + le37 + gt37). Correct the three sentences and the two program headers.

### L-2 (low) [S4 record] The per-file list named as gen_fu_l15_sources_sha256_sb2.txt

gen_tdd_fcov.md Section 10 and gen_tdd_step2b.md Section 15 name the list "gen_fu_l15_sources_sha256_sb2.txt"; the retained file is
gen_fu_l15_sources_sha256_sb3.txt (the one that hashes to 98518617fecfcf64). A one-word fix in two places.

### L-3 (low) [S6 retention] The five red checks carry no stamp while the record says every check does

gen_fu_l15_slice6*_red_check_b12x.log open with a bin line and name no manifest, report or build; gen_tdd_step2b.md Section 15 says "Every proof
check log of this landing carries a stamp line" and the CR-13-L-4 row "every proof and re-check log opens with a stamp line". The b12x urg reports
also have no cmd file. Stamp the reds as the proofs are stamped, or word the claim as the proofs and re-checks only.

### L-4 (low) [S4 record] Two reds ran an earlier image

"Each program was run on that build (b12x, fresh vdb)": the lui, hint and jump reds carry the committed programs' images (crc c2902e02 / 36e063ab /
8efa1ef3), but the imm red ran crc bce0125e (1376 words) against the committed 9febc33b (1380) and the divt red fac56381 (240) against d1988ff5
(328). The red does not depend on the program (the group is absent), so nothing is in doubt; the sentence is inexact. Say which image each red ran.

### L-5 (low) [S4 record] The debug regime named as a storm

The fcov API doc's stimulus sentence says the divide program ran "under ... the debug-request storm"; gen_tdd_fcov.md Section 10 says the storm did
not finish (two attempts, not retained) and the sparse regime carries the debug event, and the retained header is +gen_knob_debug_req_regime=sparse.
Align the API doc.

### Informational

- I-1: gen_ut_isa_shim.cc changed (comments and a section title only) and no unit-test run on sb3 is retained; "the shim unit test is unchanged
  (293 rows)" rests on the landing-11 log and the source diff. Acceptable for a comment-only change; a re-run costs a minute.
- I-2: gen_fu_l15_driver_ecc.log stamps its end at 04:01:56Z, before its three runs' headers (04:01:57Z to 04:02:07Z): the driver's end line is
  written before the runs it launched finish. Worth a look in the driver.
- I-3: my tb_l13 M-1 asked for a frame-bounded window; the plan owner ruled the narrower "immediately before" pattern. The ruling is recorded in
  the row and the API doc, and the re-proof shows the one intended instance. The disagreement is settled the right way.
- I-4: slice6e and slice6e2 (the long bus regime) hit the same 24 bins with identical counts; the long regime adds nothing to the divide group's
  declared bins, as the record says of the deferred start.

## 4. Principles check

dv-principles-check (docs/dv/dv_principles.md d9c27db18f511411): S2 derive from intent: the five samplers follow their Sample lines and the bin
definitions, their approximations stated as the multiply group's are, the decoders correct against the spec (conforming). S6 trust triad: proofs on
the committed build, a mutant with a stamped ablation and a retained diff per group, the unit rows with two reds, the new-group red form
(conforming; the red checks unstamped, L-3). S4 honesty: the CM148 / CM150 / CR-12 / CR-13 rows true of the artifacts (conforming); the
not-reached sentences and the file name (L-1, L-2, L-4, L-5). One-line verdict: PASS with the lows.

## 5. Verdict

CRITIC VERDICT: APPROVE. tb_l13 is lifted. Lows L-1..L-5 to tb-infra's next record touch; L-6 (Section 6) to its next sampler touch.

## 6. Reconciliation with the cross-model artifact (dv/auto_dv/reviews/2026-09-04-claude-diff-c4a5fd56-3bf3d6bf.md, read after Sections 1-5 were written)

APPROVE-WITH-CHANGES: three lows and one informational.

- Its first two lows are my L-1 (the not-reached sentences against the declared and hit self / gt37 bins, with the same 19 / 22 / 35 counts and the
  same spin-loop cause) and my L-2 (the sb2 file name), found independently.
- Adopted and verified, as L-6 (low) [S2 classification]: hx_rs_field returns i[11:7] as the rs1 of every quadrant-01 funct3 011 encoding, and
  insn_has_rs1 admits that funct3 for the quadrant; only c.addi16sp (rd == 2) reads a register there, c.lui has no rs1, so a `c.lui x0, nzimm` retiring
  after an x0 writer would sample cp_x0_read.rs1_zero although nothing read x0 (verified in the diff: the quadrant-01 list includes 3'b011 and the
  default branch returns the rd field). No retained proof depends on it (the directed program's c.lui x0 follows a non-writer). Return -1 for c.lui in
  both helpers and add a vector row.
- Adopted as I-5: the "not the first retirement after reset" guard reads have_last, which is set once and never cleared, so only the initial reset is
  honoured (the multiply group shares the pattern); no mid-run reset regime exists yet (WP-11 NOT BUILT). State it beside cp_delta, and clear the
  neighbour state on the reset event when WP-11 lands.
- Not in the artifact: L-3 (the unstamped red checks against the "every check stamped" claim), L-4 (the two reds on earlier images), L-5 (the
  debug regime named as a storm), I-1..I-4.
- Verdict levels agree in substance: no medium open; the artifact's lows and mine are the same record touch plus one small sampler fix.
