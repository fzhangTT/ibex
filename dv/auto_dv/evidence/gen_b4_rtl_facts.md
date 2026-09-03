# B4 RTL facts: cm.mvsa01 with r1s' == r2s' (T-237)

Owner: rtl-arch. Written 2026-09-03T20:02Z from rtl/ibex_compressed_decoder.sv, rtl/ibex_core.sv, rtl/ibex_register_file_ff.sv,
the Zc chapter of the ISA manual in this clone (tools/specs/riscv-isa-manual/src/unpriv/zcmp.adoc) and the upstream Spike
source in this clone (tools/riscv-isa-sim, revision 4ffd6ba8 of 2026-09-02; an allowed upstream project, docs/dv/FENCE.md:65-66).
Scope: the RTL-side facts behind bug candidate B4 (dv/auto_dv/docs/gen_bug_log.md:60). The DV consequence (the manifest bin,
the comparator's isa_trap / isa_rd / isa_pc_next rows) is the DV Lead's ruling and is kept out of this note; the owner item is
whether Ibex's behaviour stands. RTL is read-only; no fix proposal.

## 1. Verdict

Ibex accepts the cm.mvsa01 encoding with r1s' == r2s' and executes it as two register moves into the same register, the second
(a1 -> r2s') winning. The Zc specification reserves that encoding (zcmp.adoc:1163, :1174) and upstream Spike raises an
illegal-instruction exception on it (cm_mvsa01.h:2). The compressed decoder has no comparison of the two sreg fields anywhere
in its cm.mvsa01 arm, so no illegal_instr_o is raised. It is the only Zcmp encoding the decoder accepts that the specification
reserves (section 4).

## 2. The decoder path (rtl/ibex_compressed_decoder.sv)

| Step | RTL | Anchor |
|---|---|---|
| Group select | C2 quadrant, funct3 101, `unique casez (instr_i[12:8])`; pattern 5'b011?? is the move pair | :622, :778 |
| Instruction select | instr_i[6:5] = 01 is cm.mvsa01, 11 is cm.mva01s; 00 and 10 are illegal (default) | :781, :809, :835 |
| Fields used | r1s' = instr_i[9:7], r2s' = instr_i[4:2]; nothing compares them | :788, :797 (the only reads of the two fields in the arm) |
| sreg -> xreg mapping | dst = {(rs[2:1] > 0), (rs[2:1] == 0), rs}: s0/s1 -> x8/x9, s2..s7 -> x18..x23 | :156 (cm_mvsa01), :162 (cm_mva01s) |
| Micro-op 1 (CmIdle) | `addi r1s', a0, 0` built by cm_mvsa01(a01 = 0, rs = instr_i[9:7]) via cm_mv_reg; tagged INSTR_EXPANDED_COMMIT; FSM -> CmMvSecondReg when ID accepts it | :788, :790, :791; helpers :153-158 and :129-137 |
| Micro-op 2 (CmMvSecondReg) | `addi r2s', a1, 0` built by cm_mvsa01(a01 = 1, rs = instr_i[4:2]); tagged INSTR_EXPANDED_LAST; FSM -> CmIdle | :797, :800 |
| Illegal terms in the arm | none: the only illegal_instr_o assignments of the funct3-101 group are the instr_i[6:5] default (:835), the instr_i[12:8] default (:839) and the reserved rlist tests of push/pop (:635, :703) | :835, :839, :635, :703 |

## 3. Why the second write wins

- The two micro-ops are ordinary `addi rd, rs, 0` instructions issued to ID one after the other (:788 then :797); the
  FSM presents the second only after the first has been accepted (:791), so they retire in order through the single
  register-file write port (rtl/ibex_wb_stage.sv:303 rf_we_wb_o; rtl/ibex_register_file_ff.sv:252 we_a_dec per address).
- With r1s' == r2s' both micro-ops carry the same rd. The first writes a0's value, the second writes a1's value to the same
  register one retirement later; the register holds a1 afterwards (tb-infra's observation s0 = a1 for r1s' = r2s' = s0).
- The COMMIT tag on the first micro-op (:790) blocks interrupts between the two (rtl/ibex_controller.sv:498-500) and the
  debug gates block entry on both tags (:474-477), so the pair is atomic as the specification requires for the legal case
  (zcmp.adoc:1175); the atomicity is what makes the intermediate state (register = a0) unobservable by software.
- RVFI shows two records for the one halfword, both with rvfi_ext_expanded_insn_valid, the second with
  rvfi_ext_expanded_insn_last, both with rvfi_rd_addr = the mapped sreg; rvfi_rd_wdata is a0 on the first and a1 on the second
  (rtl/ibex_core.sv:2270-2280, :2340-2346). rvfi_trap = 0 on both. A model that traps sees one trap record instead, which is
  the comparator's first divergence.

## 4. Other Zcmp reserved forms: does the decoder share the pattern?

| Form | Specification | RTL | Verdict |
|---|---|---|---|
| cm.mvsa01 with r1s' == r2s' | reserved: "For the encoding to be legal r1s' != r2s'" (zcmp.adoc:1163); "r1s' and r2s' must be different" (:1174) | no comparison, executed (section 2) | ACCEPTED-BUT-RESERVED (the B4 case) |
| cm.mva01s with r1s' == r2s' | not reserved: the description (:1242) and the pseudo-code (:1263-1268) carry no such constraint; a0 and a1 both receive the same sreg | executed as two moves into a0 and a1 (:816, :825) | LEGAL, no issue; Spike agrees (cm_mva01s.h has no require) |
| cm.push / cm.pop / cm.popret / cm.popretz with rlist 0..3 | reserved for a future EABI variant (zcmp.adoc:385, :579, :771, :968) | illegal_instr_o when cm_rlist_d <= 3 (:635, :703) | REFUSED, matches the spec |
| RV32E with r1s' / r2s' above s1 | reserved under RV32E only (zcmp.adoc:1198, :1266) | not applicable: RV32E = 0 in the opentitan configuration (ibex_configs.yaml:43); the regular decoder performs the RV32E register checks (:351) | N/A |
| instr_i[12:8] patterns other than 11000, 11010, 11100, 11110, 011?? (including the Zcmt cm.jt / cm.jalt encodings 000??) | not Zcmp encodings; Zcmt is not implemented in this build | default illegal (:839) | REFUSED |
| instr_i[6:5] = 00 or 10 inside the 011?? group | not Zcmp encodings | default illegal (:835) | REFUSED |
| spimm (instr_i[3:2]) for push/pop | all four values legal (stack adjust base + spimm * 16, zcmp.adoc pseudo-code) | consumed by cm_stack_adj (:55-57) for every value | LEGAL, no issue |

Conclusion: cm.mvsa01 with equal registers is the only Zcmp encoding the decoder accepts that the specification reserves.

## 5. The reserved-encoding rule, quoted

- tools/specs/riscv-isa-manual/src/unpriv/zcmp.adoc:1163: "For the encoding to be legal r1s' != r2s'." (norm cm-mvsa01_res)
- tools/specs/riscv-isa-manual/src/unpriv/zcmp.adoc:1174: "moves a0 into r1s' and a1 into r2s'. r1s' and r2s' must be different."
- tools/specs/riscv-isa-manual/src/unpriv/zcmp.adoc:1175: "The execution is atomic, so it is not possible to observe state where only one of r1s' or r2s' has been updated."
- tools/riscv-isa-sim/riscv/insns/cm_mvsa01.h:1-4: `require_extension(EXT_ZCMP); require(insn.rvc_r1sc() != insn.rvc_r2sc()); WRITE_REG(RVC_R1S, READ_REG(X_A0)); WRITE_REG(RVC_R2S, READ_REG(X_A1));` (the require raises an illegal-instruction trap with the instruction bits as tval).
- tools/riscv-isa-sim/riscv/insns/cm_mva01s.h:1-3: no register-pair check.
- The general rule for reserved encodings, tools/specs/riscv-isa-manual/src/unpriv/rv32.adoc:124-130: "The behavior upon decoding a reserved instruction is UNSPECIFIED." and, in the note that follows, "Some platforms may require that opcodes reserved for standard use raise an illegal-instruction exception. Other platforms may permit reserved opcode space be used for non-conforming extensions."
- tools/specs/riscv-isa-manual/src/unpriv/intro.adoc:307-309: "Reserved encodings are currently not defined but are saved for future standard extensions; once thus used, they become standard encodings."
- So the specification makes the behaviour of the reserved cm.mvsa01 encoding UNSPECIFIED at the ISA level and leaves the
  trap requirement to the platform; Spike traps, Ibex executes both moves. Whether Ibex's behaviour stands is the owner's
  decision; the RTL facts above are what it is.

## 6. Anchors table

| Fact | Anchor |
|---|---|
| Move-pair group and instruction select | rtl/ibex_compressed_decoder.sv:622, :778, :781, :809 |
| Field reads, no comparison | :788, :797 |
| sreg mapping | :156, :162 |
| Expansion order and tags | :788, :790, :791, :797, :800 |
| Illegal terms of the group | :835, :839, :635, :703 |
| Atomicity gates | rtl/ibex_controller.sv:474-477, :498-500 |
| Register write ordering | rtl/ibex_wb_stage.sv:303; rtl/ibex_register_file_ff.sv:252 |
| RVFI records | rtl/ibex_core.sv:2270-2280, :2340-2346 |
| Specification | tools/specs/riscv-isa-manual/src/unpriv/zcmp.adoc:1163, :1174-1175, :1242, :385/:579/:771/:968 |
| Reference model | tools/riscv-isa-sim/riscv/insns/cm_mvsa01.h:2, cm_mva01s.h |
