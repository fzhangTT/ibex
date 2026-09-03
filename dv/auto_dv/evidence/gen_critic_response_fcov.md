# Response rows: the T-205 covergroup landings' reviews

Owner: tb-infra, 2026-09-03. Rows keyed by the review artifact; every row says in which slice it is answered.

## Cross-model review of landing 3 (a786543, artifact 2026-09-03-claude-diff-0a2ffe48-a786543c.md, APPROVE-WITH-CHANGES)

| id | finding | status | as built |
|---|---|---|---|
| CM51-MAJ-1 | gen_fcov_pkg.sv: `rs1 == logic'(32'(imm))` casts the sign-extended immediate to one bit, so `cp_slt_case.eq` fired on `rs1 == imm[0]` (168 hits in the retained run where the plan's definition gives 84) | FIXED (slice 2) | `rs1 == 32'(imm)`; the slice-1b proof re-run on the corrected sampler (gen_fu_l4_slice1b_check.log: eq count 84); the whole sampler audited for the cast pattern (`grep logic'(` finds no other use; every other compare is between equal-width vectors or ints); mutant FM4 re-introduces the 1-bit cast: the checker's hit/unhit verdict cannot see a bin hit too often, so the catch is the eq count in the checker output (168 against 84), recorded as such in gen_mut_fcov.md. |
| CM51-MIN-1 | "1403 named bins (250 coverpoint bins, 1153 cross bins)" is wrong: 250 coverpoint + 1403 cross = 1653; the renderer's summary counted cross-bin lines only | FIXED (slice 2) | the renderer prints coverpoint bins and cross bins separately; the transcript's figures corrected (six groups 250 / 1403, nine groups 466 / 2044). |
| CM51-MIN-2 | gen_component_api_fcov.md: CG-BIT-001 "51 / 380" where the include has 373 cross bins | FIXED (slice 2) | 373. |
| CM51-MIN-3 | the FM1 row claims an ablation with no retained log | FIXED (slice 2) | gen_fcov_proof_slice1_fm1_ablation.fcov.yaml (the slice-1 manifest without the c_mul bins) against the FM1 report: PASS, 127 bins (gen_fu_l4_FM1_ablation_check.log, manifest row added). |
| CM51-NIT-1 | hand-encoded opcodes 7'b0110011 / 7'b0010011 | DONE (slice 2) | `ibex_pkg::OPCODE_OP` / `OPCODE_OP_IMM` in the sampler's compares. |

## Critic review of landing 4 (dv/auto_dv/docs/gen_critic_tb_l4.md, REQUEST-CHANGES; rows CR-4; fixes in landing 6)

| id | finding | status | response |
|---|---|---|---|
| CR-4-H-1a | cp_minstret_once compared the compressed-retire counter of the last micro-op record with the record before the sequence; a record's counter counts through its predecessor, so the bin measured the neighbour (yes 193 of 290) | FIXED (landing 6) | the sequence sample is pended to the record after it and the bin is that record's counter minus the first micro-op record's counter (gen_fcov_pkg.sv zcmp_flush); red: the landing-4 report gen_fu_l4_urg_lockstep_zcmp_grpinfo.txt (yes 193 of 290, the 97 misses the sequences entered from a 32-bit instruction); green: gen_fu_l6_urg_lockstep_zcmp_grpinfo.txt and the three regime runs, yes 290 of 290 each, `minstret_once no 0` on the summary line; the vector table (gen_ut_isa_cov) carries a synthetic sequence followed by a counter move of one (yes) and by an unchanged counter (na); the GEN_FCOV summary prints the no-count of every ok-coverpoint (adopted from the cross-model artifact). |
| CR-4-H-1b | gen_bit_count_cg cp_result sampled rd_wdata on rd = x0 records (r0 = 102 of 214) | FIXED (landing 6) | every result-class coverpoint of every group samples na on an rd = x0 record (the choice offered: na rather than a cross exclusion; stated in the API doc); green: gen_fu_l6_urg_lockstep_bitcnt_grpinfo.txt r0 = 11 with cp_rd_x0.yes = 91; the vector table pushes a clz x0 record (result na) and a clz ra record (class from rd_wdata); gen_ut_isa_cov on gen_bitcnt_directed.S asserts 91 rd = x0 records. |
| CR-4-H-1c | Zcmp micro-op records entered the base groups (alu_imm = 354 on the zcmp run) | FIXED (landing 6) | write() returns after the collector for every rvfi_ext_expanded_insn_valid record; green: the zcmp run's alu_imm count is the program's own OP-IMM count (gen_fu_l6_lockstep_zcmp_stdout_excerpt.log). |
| CR-4-M-1 | FM2 / FM3 proven on a pre-landing sampler without retained ablation controls | FIXED (landing 6) | FM2, FM3 (and FM5-FM9) re-run from the landed sampler (gen_mut_fcov.md names the original blob sha and each mutant build's sources sha); the ablation manifests gen_fcov_proof_slice2b_fm2_ablation.fcov.yaml, ..._slice2c_fm3_ablation..., and one per later mutant are in the tree with their checker logs (gen_fu_l6_FM<n>_ablation_check.log). |
| CR-4-M-2 | the commit message claimed a sampler unit test that did not exist | FIXED (landing 6) | withdrawn in gen_tdd_fcov.md Section 2; gen_ut_isa_cov (LOG-058) lands here with FCOV_SELFTEST (the classifier vector table) and FCOV_QUERY (eq count 84 on gen_alu_directed.S, minstret misses 0 over 290 sequences, 91 rd = x0 bit-count records); API doc Section 9. |
| CR-4-M-3 | cp_dmem_delay sampled the regime knob, not the observed latency class | FIXED (landing 6) | the sampler subscribes to the dbus agent's completed transactions and classifies the responses inside the sequence's window (min1 / short [2:4] / long [5:$] / mixed); green: the random-regime run now scores mixed 147, long 137, short 4, min1 2 over 290 sequences where the knob mapping scored mixed 290 (gen_fu_l6_urg_lockstep_zcmp_random_grpinfo.txt); the short / min1 / long runs score 290 in their class. |
| CR-4-L-1 | "466 coverpoint bins" counted the ignore_bins; the API table's 54 / 169 and 51 / 244 | FIXED (landing 6) | the renderer's summary excludes `ignore_bins` (regex `(?<![a-z_])bins`, unit-test case); the record says 395; the API table now carries the include's own per-group counts (46 / 250, 47 / 244). |
| CR-4-L-2 | build j named as the landed sources | FIXED (landing 6) | gen_tdd_fcov.md Section 2 names k 893384b8eec4e6d5 as landing 4's sources. |
| CR-4-L-3 | urg reports retained without their command line | FIXED (landing 6) | every retained report has a companion gen_fu_l6_urg_<run>.cmd.txt with the urg command, the -dir path and the vdb's test list (one run per vdb). |
| CR-4-L-4 | the dummy-enabled run's report retained without an exclusion statement | FIXED (landing 6) | its manifest row says it is the B8 record and not coverage evidence. |
| CR-4-L-5 | cp_rvfi_tags_ok is a weak proxy | STATED (landing 6) | the API doc names the reduced check (intermediate pc_wdata == pc_rdata, 32-bit synthesized words); the per-position word compare is not implemented. |
| CR-4-L-6 | HINT encodings sample as normal Zca bins | OPEN (plan question) | asked of the DV Lead; the API doc records the current behaviour (count by form) until the plan says count or exclude. |
| CR-4-L-7 | the operand-only exemption loosened without a fixture | FIXED (landing 6) | the exemption is gated on the plan line's `[operand-only:` marker (an unmarked coverpoint without CSV rows refuses); unit-test cases for the unmarked refusal and for the named-bin count. |
| CR-4-L-8 | checker logs normalised while the manifest says verbatim | FIXED (landing 6) | the manifest header says ASCII-normalised and how. |
| CR-4-L-9 | hand-coded jalr opcode | FIXED (landing 6) | ibex_pkg::OPCODE_JALR. |
| CR-4-L-10 | cpuctrlsts.dummy_instr_en hand-encoded as bit 2 | FIXED (landing 6) | GEN_CPUCTRLSTS_DUMMY_INSTR_EN_BIT in the yaml constants, used by the collector. |
| CR-4-I-4 | the landing-3 deferred defects (div_divisor_cls magnitude of a negative operand; addi_wrap from rd_wdata) | FIXED (landing 6) | |x| from the sign-extended value (|INT_MIN| = 2^32); addi_wrap from rs1 and the immediate alone; both in the vector table. |

## Cross-model review of landing 5 (a9b63ae, artifact 2026-09-03-claude-diff-50971ad4-a9b63aeb.md, REQUEST-CHANGES; rows CM81; fixes in landing 6)

| id | finding | status | response |
|---|---|---|---|
| CM81-H-1 | the commit subject claimed the abs / addi_wrap / cp_minstret_once fixes and the classifier unit test, none of which the diff carried (LOG-065: the subject was composed by the committer, not from the hand-off note) | FIXED (landing 6) | the three fixes and gen_ut_isa_cov land here with their reds (Section 5 of gen_tdd_fcov.md; CR-L4 rows above); the hand-off note for this landing lists each item with the file or artifact that carries it. |
| CM81-H-2 | the move-pair sampler mapped the Zcmp sreg field as x(8 + r); the encoding is s0 = x8, s1 = x9, s2..s7 = x18..x23, so cp_uop_count_ok.yes was hit by 10 of 130 pairs (both registers in s0 / s1) and the hazard tuples by the wrong registers | FIXED (landing 6) | zcmp_sreg() maps the field as rtl/ibex_compressed_decoder.sv:153-165 does, for the micro-op check and the hazard sources; red: the build-q report retained as gen_fu_l6_urg_red_q_lockstep_zcmp_mv_grpinfo.txt (cp_uop_count_ok.yes 10, cp_hazard_src alu_prev 33 / load_prev 2 / none 95); green: gen_fu_l6_urg_lockstep_zcmp_mv_grpinfo.txt (yes 130 of 130, the hazards by the program's writers); the vector table pushes a synthetic cm.mva01s s7, s6 (x23 / x22) and requires the well-formed pair. |
| CM81-M-1 | FM5-FM7 ablations not retained as checker runs; the record's counts (c_bnez 15, alu_prev 4) disagreed with the logs | FIXED (landing 6) | every mutant has an ablation manifest and its checker log (gen_fu_l6_FM<n>_ablation_check.log); the count claims are removed from the rows (the reports carry the counts). |
| CM81-M-2 | CSR addresses, BRANCH / SYSTEM opcodes and the mstatus bit positions hand-encoded | FIXED (landing 6) | ibex_pkg::CSR_MSTATUS .. CSR_MENVCFGH, OPCODE_BRANCH, OPCODE_SYSTEM, CSR_MSTATUS_*_BIT; the mstatus writable mask is built from the bit constants. |
| CM81-M-3 | the slice-3 reds narrated without retained logs | FIXED (landing 6) | the build-l reports and the final manifests' checker runs on them are retained (gen_fu_l6_urg_red_l_lockstep_{branch,zcmp_mv,csrwarl}_grpinfo.txt, gen_fu_l6_red_l_*_check.log: FAIL max_fwd, FAIL alu_prev; the csrwarl red is a cross-row red, the coverpoint manifest passes on it, stated in the record). |
| CM81-L-1 | cp_mtvec_base_w.low tested the whole value against 0x1000 where the plan classes mtvec[31:8] | RULED (L5R-2, landing 6) | the DV Lead rules the whole-value reading (mtvec[31:12] == 0); the sampler keeps `v < 0x1000`; the program's low patterns land in low under both readings. |
| CM81-L-2 | cp_mcen_gate samples the TB knob, not mcounteren_writable_i at the write | FIXED (landing 6) | the sampler holds the ctrl interface and records the pin as driven when the write record arrives (the DV Lead: TP-PMC-057 moves the pin inside a run); the API doc states the GEN_CSR_WRITE_TO_RVFI_OFFSET window. |
| CM81-L-3 | record details: 215 pairs not 214; the testlist entries file is under work/ (gitignored); the plan's Sample line names gen_chk_csr_readback, which does not exist | FIXED / STATED (landing 6) | 215 in the record; the entries files are Runtime's merge input and live under work/ by design (the merged testlist is the tree artifact); the API doc states that the pair tracker is independent and that the read-back compare rests on the lock-step comparator. |
| CM81-N-1 | cp_wrap as the plan defines it is 1 for every backward branch | RULED (L5R-1, landing 6) | the DV Lead redefines cp_wrap as the address-space wrap (the 33-bit signed target outside [0, 2^32)); the sampler implements it; cp_wrap.yes leaves the branch proof manifest (26 bins) as reachable only near the ends of the map. |

## Cross-model review of landing 4 (5b8a0fb, artifact 2026-09-03-claude-diff-24109b89-5b8a0fb0.md, APPROVE-WITH-CHANGES; rows CM66; fixes in landing 6)

| id | finding | status | response |
|---|---|---|---|
| CM66-MAJ-1 | cp_minstret_once measured the predecessor (the counter is captured before the record's own increment; yes 193 of 290) | FIXED (landing 6) | the same defect as CR-4-H-1a: the sample waits for the record after the sequence; red = the landing-4 report, green 290 of 290; vector-table rows for both outcomes. |
| CM66-MIN-1 | API table 54 / 169 and 51 / 244 against the include's 46 / 250 and 47 / 244 | FIXED (landing 6) | the table carries the include's per-group counts; CR-4-L-1. |
| CM66-MIN-2 | cpuctrlsts.dummy_instr_en hand-encoded as bit 2 | FIXED (landing 6) | GEN_CPUCTRLSTS_DUMMY_INSTR_EN_BIT in the yaml constants (CR-4-L-10). |
| CM66-MIN-3 | 7'b1100111 where ibex_pkg::OPCODE_JALR exists | FIXED (landing 6) | OPCODE_JALR (CR-4-L-9). |
| CM66-L-1 | the renderer's operand-only exemption ungated | FIXED (landing 6) | gated on the plan's `[operand-only:` marker with unit-test cases (CR-4-L-7). |
| CM66-L-2 | GEN_BUS_ERR_DRAIN_CYCLES derived as exactly 2 x 32 with no margin for the response-to-record lag | FIXED (landing 6) | 96 = grant window max + rvalid window max + 32 for the lag and margin, derived in the yaml desc and the scoreboard doc (CR-2Bv2-L-17). |

## Cross-model review of the CR-2B-M-3 docs delta (e534438, artifact 2026-09-03-claude-diff-2a414f64-e5344388.md, APPROVE-WITH-CHANGES; rows CM60) and the Critic's 2b re-review ids

| id | finding | status | response |
|---|---|---|---|
| CM60-L-1 / CR-2Bv2-L-16 | gen_component_api_scoreboard.md:86-87 kept ", no longer consistency-only" after the corrected clause | FIXED (landing 6) | the tail is deleted; the sentence ends at "(T-183, landing 2c)". |
| CM60-L-2 / CR-2Bv2-L-17 | the drain-window derivation named the wrong windows (the announcement is grant-stamped) | FIXED (landing 6) | GEN_BUS_ERR_DRAIN_CYCLES 96 = the second half's grant window (32) + its rvalid window (32) + the response-to-record lag with margin (32); yaml desc and scoreboard doc line 146. |
| CM60-L-3 | gen_mut_step2b.md did not name the owed mutant per uncovered SVA group | FIXED (landing 6) | the closing paragraph names MS-ICRAM, MS-IRQ, MS-DBG and MS-ALERT (icram, irq, dbg, alert) and the five proven groups; the mutants themselves are landing 2c's. |

## Critic review of landing 3 (dv/auto_dv/docs/gen_critic_tb_l3.md, REQUEST-CHANGES; rows CR-3; fixes in landings 4 and 6)

| id | finding | status | response |
|---|---|---|---|
| CR-3-H-1a | `rs1 == logic'(32'(imm))` cast the immediate to one bit (cp_slt_case.eq) | FIXED (landing 4, 5b8a0fb) | `32'(imm)`; the vector table's first two rows (eq on the whole compare, `rs1[0] == imm[0]` alone is other); eq = 84 on gen_alu_directed.S asserted by gen_ut_isa_cov. |
| CR-3-H-1b | the divisor magnitude from the zero-extended negative operand | FIXED (landing 6) | |x| from the sign-extended value (|INT_MIN| = 2^32); vector-table rows for -3 against 2 and -5, 3 against -5. |
| CR-3-H-1c | addi_wrap read rd_wdata, forced 0 on rd = x0 | FIXED (landing 6) | recomputed from rs1 and the immediate; vector-table rows for INT_MAX + 1, INT_MIN - 1 and 5 + 1. |
| CR-3-M-1 | FM1 built on a pre-landing sampler, its ablation not retained | FIXED (landing 6) | FM1 and FM4 re-run from the landed sampler with the FM1 ablation manifest's checker log retained (gen_fu_l6_FM1_*); FM4 stays informational, now caught by gen_ut_isa_cov's eq count. |
| CR-3-M-2 | the fcov-off red was a four-line log beside a full report from a reused vdb | FIXED (landing 6) | a real `+gen_fcov_en=0` run of gen_muldiv_directed.S on its own fresh vdb, urg on that vdb and the checker on the slice-1 manifest retained (gen_fu_l6_nofcov_*): the report carries no covergroup and the checker fails on every declared bin. |
| CR-3-L-1 | checker logs not verbatim; an annotation inside a log | FIXED (landing 6) | the manifest header says ASCII-normalised; the annotated shared-driver log is superseded by the isolated re-runs' full outputs (gen_fu_l4_*, gen_fu_l6_*). |
| CR-3-L-2 | bin counts in the record | FIXED (landings 4 and 6) | the record carries the include's counts (395 named coverpoint bins for nine groups; the renderer's summary excludes ignore_bins). |
| CR-3-L-3 | two byte-identical check logs under two attributions | STATED | the build-g check row is dropped from the record's claims; the build-h run stands as the proof. |
| CR-3-L-4 | Zcmp micro-ops sampled as OP-IMM | FIXED (landing 6) | write() returns after the collector for every expanded record (CR-4-H-1c): alu_imm 354 -> 16 on the zcmp run. |
| CR-3-L-5 | renderer hygiene (untested die path, --check not gated, LOG-054 not in the svh header) | PART (landing 6) | the operand-only and count cases added to the unit test; `--check` is in the Orchestrator's committer checks since landing 4; the svh header sentence on cross bins is owed with the next renderer touch. |
| CR-3-L-6 | no TB-side referee for gen_isa_cov | FIXED (landing 6) | report-phase referee GEN_FCOV_REF: a group the sampler fed with zero coverage is a uvm_error. |
| CR-3-L-7 | proof manifests without anti_vacuity | FIXED (landing 6) | every proof manifest carries an anti_vacuity note per bin (the lock-step compare of the run's every result). |
| CR-3-L-8 | hand-coded opcodes | FIXED (landings 4 and 6) | ibex_pkg opcodes and CSR constants throughout the sampler (CM81-M-2). |
