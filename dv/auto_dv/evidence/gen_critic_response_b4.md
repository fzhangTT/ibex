# Response file: reviews of the B4 RTL facts note (dv/auto_dv/evidence/gen_b4_rtl_facts.md; commit ab3cb31)

Owner: rtl-arch. Created 2026-09-03T20:16Z. Rows answer the cross-model review of ab3cb31 (85 lines, sha256 3a060d916b12;
verdict APPROVE-WITH-CHANGES, artifact dv/auto_dv/reviews/2026-09-03-claude-diff-d5ddbe28-ab3cb316.md, committed 50971ad)
and any later round on the same note. Rule: every finding gets one row with ADDRESSED or DISPUTED, the changed line
(reviewed copy ab3cb31 and fixed copy at the hash in the Verdict column, the work file promoted byte-identical), and the
RTL evidence.

## 1. Findings

Row ids: CM78-n = cross-model review findings on ab3cb31 (3a060d916b12).

| # | Review | Finding (short) | Verdict | Evidence / action |
|---|---|---|---|---|
| CM78-L-1 | cross-model ab3cb31 [low] section 2 (reviewed copy line 28; fixed copy line 28) | illegal-term list cited the rlist tests (:635, :703) instead of the assignments and omitted :620 / :843 | ADDRESSED at 3b0f7aed4462 | Reworded as encoding-level terms :835, :839, :637 (under :635), :705 (under :703); configuration-level :620 (cheriot_enable_i On, tied Off at dv/auto_dv/tb/gen_dut_top.sv:206) and :843 (Zcmp absent; build is RV32ZcaZcbZcmp) stated as preconditions. Section 6 row aligned. |
| CM78-L-2 | cross-model ab3cb31 [low] header and section 6 (fixed copy line 4) | ISA-manual anchors unpinned while Spike is pinned | ADDRESSED at 3b0f7aed4462 | On-disk revision fa794b6 (2026-09-02) recorded beside the path in the header and the anchors table; marked as an untracked local copy. |
| CM78-I-1 | cross-model ab3cb31 [info] section 3 (reviewed copy line 38; fixed copy line 38) | "debug gates block entry on both tags" ambiguous | ADDRESSED at 3b0f7aed4462 | Names the gated set {INSTR_EXPANDED, INSTR_EXPANDED_COMMIT} (:474-477), notes the second micro-op carries INSTR_EXPANDED_LAST, and states that a trap accepted on it saves pc_if after that micro-op completes (controller csr_save_if_o :732 IRQ_TAKEN, :773 DBG_TAKEN_IF). |
| CM78-I-2 | cross-model ab3cb31 [info] section 3 (reviewed copy line 42; fixed copy line 45) | DV-consequence sentence in an RTL note | ADDRESSED at 3b0f7aed4462 | Kept as a parenthetical explicitly marked "Observation for the DV Lead, not an RTL fact". |

## 2. State

- Work file dv/auto_dv/work/rtl-arch/gen_b4_rtl_facts.md at 3b0f7aed4462: 88 lines, ASCII-only. Verdict unchanged.
