# B8 reproducer rows mapped to the RTL cases (T-225 companion to evidence/gen_b8_rtl_facts.md section 3)

Run: lockstep_zcmp_dummy on the T-205 slice-2 build (sources sha256 893384b8eec4e6d5), program
dv/auto_dv/stim/gen_directed/gen_zcmp_dummy_directed.S, retained as gen_tdd_logs/fcov/gen_fu_l4_lockstep_zcmp_dummy_{run_header.txt,
stdout_excerpt.log,verdict.txt,export.txt}. The program sets cpuctrlsts.dummy_instr_en with dummy_instr_mask = 0, runs four
cm.push / cm.pop pairs (rlist 4, 8, 12, 15; spimm 2; sp = stack_top = 0x80000230; plain cm.pop only: no popret, popretz or mv), and
the lock-step comparator raised 27 UVM_ERROR rows (isa_mem / isa_rd). Every row below is reconstructed from the export's RVFI records
whose pc_rdata is the cm.* PC (order in decimal; the export prints hex).

Dummy rate: the threshold is lfsr.cnt masked with {dummy_instr_mask, 2'b11} (rtl/ibex_dummy_instr.sv:97, TIMEOUT_CNT_W = 5), so with
mask 0 a dummy lands after 0 to 3 accepted instructions and the counter clears on every insertion (:99); consecutive thresholds of 0
insert consecutive dummies, which is why several adjacent micro-ops are lost in one expansion. The 40-cycle gaps between two records
(for example order 35 -> 36, 41 -> 42, 69 -> 70) are consistent with a multi-cycle dummy (DUMMY_DIV, :39) in the gap; not measured.

## Per expansion

Section-3 case names: I = first micro-op lost in CmIdle; SR = store lost in CmPushStoreReg; DS = addi lost in CmPushDecrSp (the whole
push replays); LR = load lost in CmPopLoadReg; IS = addi lost in CmPopIncrSp on a plain cm.pop (the whole pop replays). Slot = the
stack word the register belongs to; "stale" = the slot was never written by the push that should have written it, so the pop's load
is faithful to memory and the register receives what an earlier push left there.

| # | cm.* (pc) | model micro-ops | DUT records | lost micro-ops in order (case) | memory / register effect | comparator rows |
|---|---|---|---|---|---|---|
| 1 | push rl4 (0x800000fa) | st ra; addi | 2 st + addi (orders 32-34) | addi (DS) then replay: st ra again | none (same store twice at 0x8000022c) | stores model 1, dut 2 |
| 2 | pop rl4 (0x800000fc) | ld ra; addi | 2 ld + addi (35-37) | addi (IS) then replay: ld ra again | none | loads model 1, dut 2 |
| 3 | push rl8 (0x800000fe) | st s3,s2,s1,s0,ra; addi | 6 st + addi (38-44) | pass 1: s2 (SR), s1 (SR), addi (DS); pass 2: s2 (SR), ra (SR) | slot 0x80000228 (s2) never written, stays 0; every other slot correct (s1 from pass 2, ra from pass 1) | stores model 5, dut 6 |
| 4 | pop rl8 (0x80000100) | ld s3,s2,s1,s0,ra; addi | 7 ld + addi (45-52) | pass 1: s3 (I), s2 (LR), addi (IS); pass 2: s0 (LR) | x18 <- 0 from the stale slot of #3 (faithful load); s0 kept from pass 1; all others correct | x18 model 33333333 dut 00000000; loads model 5, dut 7 |
| 5 | push rl12 (0x80000102) | st s7..s0,ra; addi | 6 st + addi (53-59) | s7 (I), s4 (SR), s0 (SR); no replay | slots 0x8000022c (s7) and 0x80000220 (s4) keep #3's s3 = 44444444 and s0 = 11111111; slot 0x80000210 (s0) stays 0; s2 stored as 0 (its value since #4) | stores model 9, dut 6 |
| 6 | pop rl12 (0x80000104) | ld s7..s0,ra; addi | 11 ld + addi (60-71) | pass 1: s7 (I), s3 (LR), s0 (LR), ra (LR), addi (IS) [four consecutive]; pass 2: s5 (LR), s3 (LR), s0 (LR) | x23 <- 44444444 and x20 <- 11111111 (stale slots of #5), x18 <- 0; x8 and x19 never written; x21, x22, x9, x1 correct | 7 rows: registers model 10 dut 8; x8 not written; x18 0; x19 not written; x20 11111111; x23 44444444; loads model 9, dut 11 |
| 7 | push rl15 (0x80000106) | st s11..s0,ra; addi | 7 st + addi (72-79) | s11 (I), s8 (SR), s5 (SR), s3 (SR), s0 (SR), ra (SR); no replay | slots of s11 / s8 / s5 keep earlier data (44444444 / 11111111 / 22222222), slot of s0 (0x80000200) and ra stay 0; s7 and s4 stored with their already-corrupted values | stores model 13, dut 7 |
| 8 | pop rl15 (0x80000108) | ld s11..s0,ra; addi | 8 ld + addi (80-88) | s9 (LR), s7 (LR), s3 (LR), s1 (LR), ra (LR); no replay | x27 <- 44444444, x24 <- 11111111, x21 <- 22222222, x20 <- 11111111, x8 <- 0, x18 <- 0 (all faithful loads of stale or corrupted slots); x1, x9, x19, x23, x25 never written | 13 rows: registers model 14 dut 9; x1/x9/x19/x23/x25 not written; x8 0; x18 0; x20 11111111; x21 22222222; x24 11111111; x27 44444444; loads model 13, dut 8 |

Row count: 1 + 1 + 1 + 2 + 1 + 7 + 13 + 1 = 27, every row placed.

## Per-state tally

| Section-3 case | Events in this run | Expansions |
|---|---|---|
| CmIdle, first store lost | 2 | #5, #7 |
| CmPushStoreReg, store lost | 11 | #3 (4), #5 (2), #7 (5) |
| CmPushDecrSp, addi lost, push replays | 2 | #1, #3 |
| CmIdle, first load lost | 2 | #4, #6 |
| CmPopLoadReg, load lost | 13 | #4 (2), #6 (6), #8 (5) |
| CmPopIncrSp on plain cm.pop, addi lost, pop replays | 3 | #2, #4, #6 |
| CmPopIncrSp on popret/popretz, CmPopZeroA0, CmPopRetRa, cm.mv* | 0 | not in this program |

## Two corrections to the note's attribution

- The x18 = 00000000 of this run is not the CmPopRetRa replay: the program has no popret. It is a lost store (CmPushStoreReg, #3,
  both passes) followed by a faithful load of the never-written slot (#4). Every wrong register value in this run is of that kind:
  a lost store leaves a slot stale, or a lost load leaves the register unwritten; no load in this run reads above the frame.
- The x18 = 800003ff value comes from an earlier, unretained run of gen_zcmp_directed.S with dummy insertion still enabled (build j,
  lockstep_zcmp_dbg, pc 0x8000040a = a cm.popret tail): a return-address-like value in x18 is consistent with the CmPopRetRa replay
  from above the frame that the note describes. A popret / popretz variant of the reproducer is owed (landing 2c, beside the
  dummy-in-expansion assertion) so that case is retained too.
