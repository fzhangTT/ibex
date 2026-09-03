# Response file: reviews of the counter CSR anchors note (dv/auto_dv/evidence/gen_counter_csr_anchors.md; commit f2b9272)

Owner: rtl-arch. Created 2026-09-03T20:07Z. Rows answer the cross-model review of f2b9272 (113 lines, sha256 daf32811888d;
verdict APPROVE-WITH-CHANGES, artifact committed d5ddbe2) and any later round on the same note. Rule: every finding gets
one row with ADDRESSED or DISPUTED, the changed line (reviewed copy f2b9272 and fixed copy at the hash in the Verdict
column, which names the work file dv/auto_dv/work/rtl-arch/gen_counter_csr_anchors.md promoted byte-identical), and the
RTL evidence.

## 1. Findings

Row ids: CM76-n = cross-model review findings on f2b9272 (daf32811888d); CM79-n = on 0c189eb (fb652266e3de; artifact dv/auto_dv/reviews/2026-09-03-claude-diff-979ba796-0c189eb1.md, APPROVE-WITH-CHANGES, committed 50971ad).

| # | Review | Finding (short) | Verdict | Evidence / action |
|---|---|---|---|---|
| CM76-M-1 | cross-model f2b9272 [medium] section 2 (fixed copy line 31, new row) | omitted: the instruction writing minstret is itself counted after the write | ADDRESSED at fb652266e3de | New row: write at ID/EX completion (rtl/ibex_id_stage.sv:747-749, rtl/ibex_cs_registers.sv:1020), the writer's increment one cycle later from WB (rtl/ibex_wb_stage.sv:208-209, rtl/ibex_core.sv:1549, cs_registers:1588), write-wins covers only the same cycle (rtl/ibex_counter.sv:44-47), so csrw minstret, V reads back V + 1; ISS convention from the clone's Spike: the bump after an explicit instret write is skipped (csrs.cc:1321-1333, execute.cc:353), so Spike reads back V; the shim must add one or the comparator expect V + 1. All anchors verified against the source. |
| CM76-L-1 | cross-model f2b9272 [low] section 3 (fixed copy line 40) and section 9 | "no effect / no-op" for an mhpmcounterXh write (3..12) imprecise | ADDRESSED at fb652266e3de | Reworded: we asserted (ibex_counter.sv:35), counter_d takes the old low word (:38-41) over counter_upd (:44-47), value held, an increment due that cycle is lost; the section-9 implicit row says the same. |
| CM76-L-2 | cross-model f2b9272 [low] section 9 (fixed copy line 97) | question list is an untracked work file; confirmations not reproducible from the commit | ADDRESSED at fb652266e3de | The four BLOCKER claims are quoted verbatim ahead of the verdict table; the header names the README as untracked. |
| CM76-I-1 | cross-model f2b9272 [info] section 7 (fixed copy line 82) | "any write form traps" for the 0xCxx aliases ignores the CSRRS/CSRRC rs1 = x0 demotion | ADDRESSED at fb652266e3de | Now: CSRRW / CSRRWI, or CSRRS / CSRRC with rs1 != x0 (immediate forms with uimm != 0) trap; the demoted forms are legal reads (rtl/ibex_decoder.sv:251-258). |
| CM79-L-1 | cross-model 0c189eb [low] section 10 (reviewed copy line 118; fixed copy lines 120, 121) | section 10 not updated: h-write "no-op" and no minstret bullet | ADDRESSED at a4e9aa9faae3 | Bullet reworded to "holds the stored value and drops an event increment due in that cycle"; new bullet for csrw minstret / minstreth (V + 1 when mcountinhibit[2] = 0, V when inhibited; Spike V in both cases). |
| CM79-L-2 | cross-model 0c189eb [low] section 2 (reviewed copy line 31; fixed copy line 33) and section 1 (line 17) | "+1" unqualified: mcountinhibit[2] = 1 masks the writer's increment (cs_registers:1643); Spike passes 0 when IR is inhibited (execute.cc:353); WritebackStage dependence not listed | ADDRESSED at a4e9aa9faae3 | Row and section-10 bullet qualified "when mcountinhibit[2] = 0", inhibited case stated (both read V), minstreth included; new section-1 row WritebackStage = 1 (ibex_configs.yaml:49) named as the basis of the one-cycle relation. |
| CM79-I-1 | cross-model 0c189eb [info] section 2 (fixed copy line 33) | quoted csr_op_en expression drops the CHERIoT-mode arm | ADDRESSED at a4e9aa9faae3 | Row notes the instr_first_cycle arm (id_stage:748) applies only with cheriot_enable_i On, tied Off at dv/auto_dv/tb/gen_dut_top.sv:206. |
| CM79-I-2 | cross-model 0c189eb [info] header (fixed copy line 5) | source list missing id_stage, wb_stage, decoder and the pinned Spike | ADDRESSED at a4e9aa9faae3 | Header lists rtl/ibex_id_stage.sv, rtl/ibex_wb_stage.sv, rtl/ibex_decoder.sv and the untracked Spike checkout at commit 4ffd6ba8 (2026-09-02); the commit is repeated beside the csrs.cc / execute.cc anchors in the row. |

## 2. State

- Work file dv/auto_dv/work/rtl-arch/gen_counter_csr_anchors.md at a4e9aa9faae3: 126 lines, ASCII-only; CM76 touched sections 2, 3, 7, 9 and the header; CM79 touches sections 1, 2, 10 and the header.
