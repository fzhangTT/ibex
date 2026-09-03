# RV32BOTEarlGrey: the exact bitmanip encodings the decoder accepts (opentitan configuration)

Committed reference (promoted 2026-09-03 from the rtl-arch working file
dv/auto_dv/work/rtl-arch/gen_rv32b_otearlgrey_encodings.md, same content). Source of truth: the
legality case statements in rtl/ibex_decoder.sv (OP-IMM :488-586, OP :588-651, ternary :592-593)
and the ALU-operator / multicycle selection (:1100-1352); Zcb expansions
rtl/ibex_compressed_decoder.sv:462-519. This file is the reference that the TB Infra encoding check
and the Spike shim's draft-B path use; when the working copy changes, this copy is re-promoted.
Owner: rtl-arch. ASCII only.


Owner: rtl-arch. Answers tb-infra Q-8 item 6. Source of truth: the legality case statements in
rtl/ibex_decoder.sv (OP-IMM :488-586, OP :588-651, ternary :592-593) and the ALU-operator /
multicycle selection (:1100-1352); Zcb expansions rtl/ibex_compressed_decoder.sv:462-519. Read
in full on 2026-09-03. Doc reference: doc/03_reference/instruction_decode_execute.rst:67-102
(OTEarlGrey = all sub-extensions except Zbe; Zba/Zbb/Zbc/Zbs at ratified 1.0.0, Zbe/Zbf/Zbp/
Zbr/Zbt at draft 0.93). RV32B = RV32BOTEarlGrey, RV32M = RV32MSingleCycle.

Notation: opcode OP-IMM = 0010011, OP = 0110011; f3 = instr[14:12]; f7 = instr[31:25];
hi5 = instr[31:27]; "any" = the decoder does not check those bits (lenient: reserved encodings
execute instead of trapping). "MC" = 2-cycle multi-cycle op (alu_multicycle_o = 1, result via
imd_val). L = legal in this configuration.

## 1. Register-register (OP, opcode 0110011)

| Mnemonic | Sub-ext | f7 | f3 | L | MC | Decoder legality / ALU op lines |
|---|---|---|---|---|---|---|
| sh1add / sh2add / sh3add | Zba 1.0 | 0010000 | 010 / 100 / 110 | Y | - | :601-603 / :1277-1279 |
| andn / orn / xnor | Zbb 1.0 | 0100000 | 111 / 110 / 100 | Y | - | :605-607 / :1272-1274 |
| rol / ror | Zbb 1.0 | 0110000 | 001 / 101 | Y | MC | :608-609 / :1249-1260 |
| min / max / minu / maxu | Zbb 1.0 | 0000101 | 100 / 110 / 101 / 111 | Y | - | :610-613 / :1263-1266 |
| pack / packu / packh | Zbp 0.93 (pack rd,rs1,x0 = ratified Zbb zext.h) | 0000100 / 0100100 / 0000100 | 100 / 100 / 111 | Y | - | :614-616 / :1268-1270 |
| bclr / bset / binv / bext | Zbs 1.0 | 0100100 / 0010100 / 0110100 / 0100100 | 001 / 001 / 001 / 101 | Y | - | :618-621 / :1296-1299 |
| bfp | Zbf 0.93 | 0100100 | 111 | Y | - (single cycle; doc says MC: doc defect EX-04) | :623 / :1302 |
| grev / gorc | Zbp 0.93 | 0110100 / 0010100 | 101 / 101 | Y | - | :625-626 / :1305-1306 |
| shfl / unshfl | Zbp 0.93 | 0000100 | 001 / 101 | Y | - | :627-628 / :1307-1312 |
| xperm.n / xperm.b / xperm.h | Zbp 0.93 | 0010100 | 010 / 100 / 110 | Y | - | :629-631 / :1313-1321 |
| slo / sro | Zbp 0.93 | 0010000 | 001 / 101 | Y | - | :632-633 / :1322-1327 |
| clmul / clmulr / clmulh | Zbc 1.0 | 0000101 | 001 / 010 / 011 | Y | - | :635-639 / :1330-1338 |
| bcompress / bdecompress | Zbe 0.93 | 0000100 / 0100100 | 110 / 110 | N (RV32BFull only) -> illegal instruction | MC in Full | :641-642 / :1341-1352 |
| cmix / cmov | Zbt 0.93 | instr[26:25] = 11, rs3 = instr[31:27] | 001 / 101 | Y | MC (rs3 read in cycle 2) | :592-593 / :1210-1229 |
| fsl / fsr | Zbt 0.93 | instr[26:25] = 10, rs3 = instr[31:27] | 001 / 101 | Y | MC | :592-593 / :1230-1245 |
| mul / mulh / mulhsu / mulhu / div / divu / rem / remu | M | 0000001 | 000..111 | Y | mulh* 2 cycles, div/rem 37 (2 on div-by-zero unless data_ind_timing) | :644-687 |

Legality detail for OP: the ternary check `{instr[26], instr[13:12]} == {1'b1, 2'b01}` (:592)
is taken before the f7/f3 case, so ANY instr[31:27] with instr[26] = 1 and f3 in {001, 101} is
legal and rs3 = instr[31:27]; instr[25] selects fsl/fsr (0) vs cmix/cmov (1) in the ALU decode
(:1210-1245). Every other f7/f3 combination not listed is illegal (:688-690).

## 2. Register-immediate (OP-IMM, opcode 0010011), f3 = 001 (shift-left group)

| Mnemonic | Sub-ext | hi5 = instr[31:27] | Extra bits checked | L | MC | Lines |
|---|---|---|---|---|---|---|
| slli | I | 00000 | instr[26:25] must be 00 (shamt < 32) | Y | - | :502 |
| sloi | Zbp 0.93 | 00100 | instr[26:25] NOT checked (lenient) | Y | - | :503-505 |
| bclri / bseti / binvi | Zbs 1.0 | 01001 / 00101 / 01101 | instr[26:25] must be 00 | Y | - | :506-509 |
| shfli | Zbp 0.93 | 00001 | instr[26] must be 0; instr[25] not checked | Y | - | :510-516 |
| clz / ctz / cpop | Zbb 1.0 | 01100 | instr[26:20] = 0000000 / 0000001 / 0000010 | Y | - | :517-523, :1104-1106 |
| sext.b / sext.h | Zbb 1.0 | 01100 | instr[26:20] = 0000100 / 0000101 | Y | - | :524-525, :1107-1108 |
| crc32.b / .h / .w | Zbr 0.93 | 01100 | instr[26:20] = 0010000 / 0010001 / 0010010 | Y | MC | :526-528, :1109-1126 |
| crc32c.b / .h / .w | Zbr 0.93 | 01100 | instr[26:20] = 0011000 / 0011001 / 0011010 | Y | MC | :529-533, :1127-1144 |
| any other hi5 or instr[26:20] | - | - | - | N | - | :534, :536 |

## 3. Register-immediate (OP-IMM, opcode 0010011), f3 = 101 (shift-right group)

| Mnemonic | Sub-ext | Condition | L | MC | Lines |
|---|---|---|---|---|---|
| fsri | Zbt 0.93 | instr[26] = 1 (any instr[31:27]; rs3 = instr[31:27]) | Y | MC | :541-543, :1157-1164 |
| srli / srai | I | instr[26] = 0, hi5 = 00000 / 01000, instr[26:25] must be 00 | Y | - | :545-546 |
| sroi | Zbp 0.93 | instr[26] = 0, hi5 = 00100, instr[25] not checked | Y | - | :548-550 |
| rori | Zbb 1.0 | instr[26] = 0, hi5 = 01100, instr[26:25] must be 00 | Y | MC | :551-553, :1174-1177 |
| bexti | Zbs 1.0 | instr[26] = 0, hi5 = 01001, instr[26:25] must be 00 | Y | - | :551-553, :1173 |
| grevi (incl. ratified rev8 = grevi imm 24) | Zbp 0.93 | instr[26] = 0, hi5 = 01101, instr[25:20] any | Y | - | :555-563, :1178 |
| gorci (incl. ratified orc.b = gorci imm 7) | Zbp 0.93 | instr[26] = 0, hi5 = 00101, instr[25:20] any | Y | - | :564-572, :1179 |
| unshfli | Zbp 0.93 | instr[26] = 0, hi5 = 00001, instr[25] not checked | Y | - | :573-579, :1181-1185 |
| any other hi5 | - | - | N | - | :581 |

Every OP-IMM with f3 in {000, 010, 011, 100, 110, 111} is legal (addi/slti/sltiu/xori/ori/andi,
:494-499).

## 4. Compressed Zcb (RV32ZC = RV32ZcaZcbZcmp; rtl/ibex_compressed_decoder.sv)

c.lbu, c.lhu, c.lh, c.sb, c.sh (C0 funct3 100, :266-326; c.sh with instr[6] = 1 illegal); c.mul
-> mul rsd', rsd', rs2' (:462-471); c.zext.b -> andi rsd', rsd', 0xff; c.sext.b -> sext.b;
c.zext.h -> pack rsd', rsd', x0; c.sext.h -> sext.h; c.not -> xori rsd', rsd', -1; c.zext.w
illegal (RV64 only); instr[4:2] = 110/111 illegal (:473-519). The sext/zext.h expansions are
legal because RV32B != None. Zcmp (cm.push/pop/popret/popretz/mvsa01/mva01s) is covered in
gen_behaviour_summaries.md EX-06..EX-08.

## 5. Consequences for the toolchain, riscv-dv target and ISA-model string

1. Assemble against THIS table, not against `-march=rv32imcb` acceptance: the lowRISC gcc 10.2
   B support is draft-era and the RTL is lenient on reserved bits for sloi/sroi/grevi/gorci/
   shfli/unshfli (rows marked "not checked"). Reserved-bit variants execute rather than trap:
   they are an illegal-encoding coverage item and must NOT be expected to raise cause 2.
2. Ratified-Zbb aliases the RTL implements only as their Zbp/Zbp-imm parents: zext.h (= pack
   rd, rs1, x0), rev8 (= grevi rd, rs1, 24), orc.b (= gorci rd, rs1, 7). The encodings coincide
   with the ratified ones, so an ISA model with Zbb decodes them; grevi/gorci with OTHER
   immediates are Zbp-only and no ratified-only model decodes them.
3. Not implemented (illegal, cause 2, mtval = instruction): Zbe bcompress/bdecompress; any
   f7/f3 outside the tables; shift immediates with instr[26:25] != 00 for slli/srli/srai/rori/
   bclri/bseti/binvi/bexti.
4. ISA string for a ratified-only model: rv32imc_zicsr_zifencei_zba_zbb_zbc_zbs (plus Zcb/Zcmp
   if the model has them). The draft sub-extensions Zbp, Zbr, Zbt, Zbf have no ratified
   successor and UNVERIFIED (tb-infra to check the cloned upstream Spike): they are believed
   absent from current upstream Spike, in which case grev/gorc (non-alias immediates), shfl/
   unshfl, xperm.*, slo/sro/sloi/sroi, pack (except zext.h), packu, packh, crc32*, cmix/cmov/
   fsl/fsr/fsri and bfp need a local reference model or must be excluded from random
   generation and tested with directed self-checking programs.
5. Timing for the pipeline model: MC rows take 2 cycles in ID (imd_val written in cycle 1);
   cmix/cmov/fsl/fsr/fsri read rs3 in cycle 2 (use_rs3, rtl/ibex_decoder.sv:172-181).
