# Response file: reviews of the B8 RTL facts note (dv/auto_dv/evidence/gen_b8_rtl_facts.md, commit 1eb2ede)

Owner: rtl-arch. Created 2026-09-03T19:14Z ahead of the findings. Rows answer the cross-model reviews of 1eb2ede
(gen_b8_rtl_facts.md, 140 lines, sha256 5abb0619b8391029) and of 53e8468 (154 lines, sha256 eac6bc028e8574b5;
artifact dv/auto_dv/reviews/2026-09-03-claude-diff-cb173d93-53e84680.md, APPROVE-WITH-CHANGES, committed 68b9af3). Rule: every
finding gets one row with ADDRESSED or DISPUTED, the changed line in the note (location column: the reviewed
copy's line numbers and the fixed copy's, the fixed copy being the work file at the hash in the Verdict column),
and the RTL evidence; a change to
the note is reported with its new hash for promotion.

## 1. Findings (filled as they arrive)

Row ids: CM59-n = cross-model review findings on 1eb2ede.

| # | Review | Finding (short) | Verdict | Evidence / action |
|---|---|---|---|---|
| CM59-M-1 | cross-model 1eb2ede [medium] section 5 (reviewed copy 1eb2ede lines 118-120; fixed copy line 112) | interrupt exposure overstated: handle_irq is gated on COMMIT only, debug gates on EXPANDED or COMMIT | ADDRESSED at eac6bc028e8574b5 | Section 5 restated: interrupts are admissible on every EXPANDED micro-op by design (rtl/ibex_controller.sv:498-500) and the restart is idempotent; the dummy's new interrupt exposure is only the COMMIT window (the micro-op after CmPopIncrSp / CmPopZeroA0 displaced, sp already incremented); the debug exposure (:474-477) is at every micro-op position. |
| CM59-M-2 | cross-model 1eb2ede [medium] section 3 (reviewed copy 1eb2ede lines 96-100; fixed copy line 83) | cm.mvsa01 / cm.mva01s paragraph contradicted the section-1 rule | ADDRESSED at eac6bc028e8574b5 | Rewritten: first move lost in CmIdle (:791 / :819) means no replay (second move carries LAST, buffer released) and the first destination stays unwritten, an architectural error; second move lost in CmMvSecondReg (:798 / :826) replays the pair, benign for both. |
| CM59-L-1 | cross-model 1eb2ede [low] section 4 (reviewed copy 1eb2ede lines 107-108; fixed copy line 99) | claimed dummies are excluded from minstret via a dummy_instr_id in cs_registers; no such signal | ADDRESSED at eac6bc028e8574b5 | Corrected: instr_perf_count_id_o (rtl/ibex_id_stage.sv:1218-1220) has no dummy term, wb_count_q latches it (rtl/ibex_wb_stage.sv:150, :169), perf_instr_ret_wb (:208-209) feeds instr_ret_i (rtl/ibex_core.sv:1549) into mhpmcounter_incr[2] (rtl/ibex_cs_registers.sv:1588); dummies increment minstret while rvfi_order holds, so the lock-step model expects minstret minus rvfi_order to grow by one per dummy. |
| CM59-L-2 | cross-model 1eb2ede [low] section 6 (reviewed copy 1eb2ede lines 122-123; fixed copy line 136) | proposed assertion lacked a validity qualifier and cm_sp_offset | ADDRESSED at eac6bc028e8574b5 | Assertion now qualified with if_id_pipe_reg_we (or valid_i && id_in_ready_i at the decoder) and extended with cm_sp_offset_d == cm_sp_offset_q; the signature bullet lists cm_sp_offset as well. |
| CM59-L-3 | cross-model 1eb2ede [low] reviewed copy 1eb2ede lines 39, 115, 135; fixed copy lines 39, 129, 151 | insert_dummy_instr assigned at rtl/ibex_dummy_instr.sv:115, cited :112 | ADDRESSED at eac6bc028e8574b5 | All three citations now :115. |
| CM64-L-1 | cross-model 53e8468 [low] section 5 (reviewed copy 53e8468 lines 114-116; fixed copy lines 116, 121) | restated interrupt rule omitted the third COMMIT site (first move of cm.mvsa01 / cm.mva01s) | ADDRESSED at 0eab3c5fb895abc2 | Rule now lists all three COMMIT-tagged micro-ops with their lines (rtl/ibex_compressed_decoder.sv:744, :760, :790, :818); the COMMIT-window list adds the second move of the pair, benign on restart per section 3. |
| CM64-L-2 | cross-model 53e8468 [low] CM59 rows, location column | mixed line-number frames (reviewed vs fixed copy) | ADDRESSED (this file) | Every CM59 row now gives both the reviewed copy's line numbers (1eb2ede) and the fixed copy's; the header states the rule. |

## 2. State

- Work file dv/auto_dv/work/rtl-arch/gen_b8_rtl_facts.md at 6283d7c2b1edec3e: 173 lines, ASCII-only; the evidence copy is promoted by the Orchestrator at this hash. Verdict unchanged: architectural bug, expansion FSM advancing on an id_in_ready without the dummy stall.
- Non-review change at 6283d7c2b1edec3e: tb-infra's row mapping of the retained reproducer (27 rows, all in section-3 cases) corrected the x18 = 00000000 attribution (a lost s2 store at push rl8 read back faithfully by pop rl8, not the CmPopRetRa replay; 800003ff stays with its source named) and is summarised in section 6; the verdict is unchanged.
