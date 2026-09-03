# Response file: reviews of the counter CSR anchors note (dv/auto_dv/evidence/gen_counter_csr_anchors.md; commit f2b9272)

Owner: rtl-arch. Created 2026-09-03T20:07Z. Rows answer the cross-model review of f2b9272 (113 lines, sha256 daf32811888d;
verdict APPROVE-WITH-CHANGES, artifact committed d5ddbe2) and any later round on the same note. Rule: every finding gets
one row with ADDRESSED or DISPUTED, the changed line (reviewed copy f2b9272 and fixed copy at the hash in the Verdict
column, which names the work file dv/auto_dv/work/rtl-arch/gen_counter_csr_anchors.md promoted byte-identical), and the
RTL evidence.

## 1. Findings

Row ids: CM76-n = cross-model review findings on f2b9272 (daf32811888d).

| # | Review | Finding (short) | Verdict | Evidence / action |
|---|---|---|---|---|
| CM76-M-1 | cross-model f2b9272 [medium] section 2 (fixed copy line 31, new row) | omitted: the instruction writing minstret is itself counted after the write | ADDRESSED at fb652266e3de | New row: write at ID/EX completion (rtl/ibex_id_stage.sv:747-749, rtl/ibex_cs_registers.sv:1020), the writer's increment one cycle later from WB (rtl/ibex_wb_stage.sv:208-209, rtl/ibex_core.sv:1549, cs_registers:1588), write-wins covers only the same cycle (rtl/ibex_counter.sv:44-47), so csrw minstret, V reads back V + 1; ISS convention from the clone's Spike: the bump after an explicit instret write is skipped (csrs.cc:1321-1333, execute.cc:353), so Spike reads back V; the shim must add one or the comparator expect V + 1. All anchors verified against the source. |
| CM76-L-1 | cross-model f2b9272 [low] section 3 (fixed copy line 40) and section 9 | "no effect / no-op" for an mhpmcounterXh write (3..12) imprecise | ADDRESSED at fb652266e3de | Reworded: we asserted (ibex_counter.sv:35), counter_d takes the old low word (:38-41) over counter_upd (:44-47), value held, an increment due that cycle is lost; the section-9 implicit row says the same. |
| CM76-L-2 | cross-model f2b9272 [low] section 9 (fixed copy line 97) | question list is an untracked work file; confirmations not reproducible from the commit | ADDRESSED at fb652266e3de | The four BLOCKER claims are quoted verbatim ahead of the verdict table; the header names the README as untracked. |
| CM76-I-1 | cross-model f2b9272 [info] section 7 (fixed copy line 82) | "any write form traps" for the 0xCxx aliases ignores the CSRRS/CSRRC rs1 = x0 demotion | ADDRESSED at fb652266e3de | Now: CSRRW / CSRRWI, or CSRRS / CSRRC with rs1 != x0 (immediate forms with uimm != 0) trap; the demoted forms are legal reads (rtl/ibex_decoder.sv:251-258). |

## 2. State

- Work file dv/auto_dv/work/rtl-arch/gen_counter_csr_anchors.md at fb652266e3de: 123 lines, ASCII-only; the four CM76 changes touch sections 2, 3, 7, 9 and the header.
