# Cross-model review - committed diff 5aafaf11..8ddd7f65

**Reviewer:** claude CLI 2.1.259 (Claude Code); run-reported model: claude-fable-5-1,claude-haiku-4-5-20251001; requested effort: high (the CLI does not report the effective setting); fresh session 474cd7eb-71c7-4792-8908-367cc09c34b1; sandbox: bubblewrap, working directory = detached read-only checkout of commit 8ddd7f65dbb2338c4d0af375b0649fab35a36cf9 (the live working tree is not read), filesystem read-only except this run's own output directory, scratch HOME (no access to the executing model's settings, instructions or memory), private PID namespace; network open for the model API, web tools disallowed by policy (fallback reviewer per owner ruling A-001)
**Codex unavailable because:** ERROR: You hit your spend cap set by the owner of your workspace. Ask an owner to increase your spend cap to continue.
**Wrapper:** dv/auto_dv/tools/gen_cross_review.sh blob 713e8c09 (the copy executed; equals the wrapper committed at the reviewed commit); reviewed commit 8ddd7f65dbb2338c4d0af375b0649fab35a36cf9
**Date:** 2026-09-03
**Target:** committed diff 5aafaf11..8ddd7f65 (echo at raw line 1)

---

TARGET: 5aafaf117c58f7b898b77c75bf494bcdbdb603d2..8ddd7f65dbb2338c4d0af375b0649fab35a36cf9

**Reviewer identity:** Claude Fable 5.1 (claude-fable-5-1), Claude Code CLI, fresh session, independent reviewer, not the author. Read-only, nothing modified. Working directory: detached read-only checkout of 8ddd7f6. The live clone was not read.

**Scope reviewed:** one commit (8ddd7f6), two files, +10/-6 lines. `dv/auto_dv/evidence/gen_counter_csr_anchors.md` changes line 33 (section-2 write row) and lines 121-122 (section-10 minstret and minstreth bullets). `dv/auto_dv/evidence/gen_critic_response_counter.md` changes the title, the row-id legend, adds four CM97 rows and updates the state line.

**Reproduction of the hand-off claims (from this checkout):**
- The anchors note at 8ddd7f6 hashes to sha256 b16678949f12..., 127 lines. At 5aafaf1 it hashes to 95b0c048ba97..., 127 lines. Both values match the response file's legend, its CM97 "ADDRESSED at" cells and its state line. Both touched files are ASCII-only.
- The work file under `dv/auto_dv/work/rtl-arch/` is untracked, so "promoted byte-identical" is checked only through the evidence-file hash equalling the hash the response file names. Consistent.
- The CM97 legend names artifact 29d01e7 (`dv/auto_dv/reviews/2026-09-03-claude-diff-812ed54e-833a78c9.md`, APPROVE-WITH-CHANGES, target 812ed54..833a78c whose result file hashes 95b0c048ba97, i.e. the CM95 touch). That artifact has exactly two [low] and two [info] findings. CM97-L-1, L-2, I-1, I-2 answer them one to one with the right line references (33, 121, 122).

**Anchors in the changed text, read against the RTL:**
- `rtl/ibex_counter.sv:36` `counter_load[63:32] = counter[63:32]`, `:37` `counter_load[31:0] = counter_val_i`: the low-write load path, high word kept, low word = V. Correct for the carry clause. `:40` `counter_load[31:0] = counter[31:0]` sits inside `if (counterh_we_i)` (`:38-41`), so it is the high-write reload only. The Anchor column now labels `:36-37 (low write), :40 (high write), :44-47` correctly. `:44-47` `if (we) counter_d = counter_load ... else if (counter_inc_i)`: the write wins over the increment. Correct.
- `rtl/ibex_id_stage.sv:1059-1062` `instr_executing = instr_valid_i & ~instr_kill & ~stall_ld_hz & ~outstanding_memory_access`; `:1120` `stall_ld_hz = outstanding_load_wb_i & (rf_rd_a_hz | rf_rd_b_hz)`. The load-hazard exception added to the section-10 minstreth bullet is anchored correctly, and `:747-749` (csr_op_en needs instr_executing) makes the deferral of the CSR commit follow.
- Unchanged anchors spot-checked and still right: `rtl/ibex_id_stage.sv:1210-1220` (~minstret_write term with the quoted comment), `rtl/ibex_wb_stage.sv:115-116, :150, :169, :185, :193-194, :200, :208-209`, `rtl/ibex_cs_registers.sv:1020, :1588, :1643`, `rtl/ibex_core.sv:1549`.
- `tools/riscv-isa-sim` is absent from the checkout, so the Spike ordering behind the carry corner remains unverifiable from the commit, as CM97-I-2 records. No action.

**Consistency of the shim obligation across sections 1, 2 and 10 (the owner's ask):**
- Low write (csrw minstret): section 2 line 33 now reads "No shim action for the low write except the carry corner below (subtract the carry from the high word when mcountinhibit[2] = 0, an instruction retires in the write cycle and the pre-write low word was 0xFFFFFFFF)". Section 10 line 121 reads "none in general; in the carry corner (mcountinhibit[2] = 0, the trace shows an instruction retiring in the write cycle, and the pre-write low word was 0xFFFFFFFF) ... the shim subtracts one from the high word after the explicit minstret write". Same three conditions, same action, same RTL anchors (:36-37, :44-47). The RTL supports the claim: with we and counter_inc_i both set and counter[31:0] = 0xFFFFFFFF, counter_d = {counter[63:32], V}, so Ibex holds {H, V}.
- High write (csrw minstreth): section 2 and section 10 line 122 both state the dropped increment on the back-to-back case, the load-hazard deferral (now in both, with :1059-1062, :1120), no divergence on an empty WB or mcountinhibit[2] = 1, and the shim action "subtract one from the low word when mcountinhibit[2] = 0 and an instruction retires in the write cycle". Section 1 line 17 names the same three conditions and points at the section-2 row. Consistent.

**Rubrics (Zone A set):** ai-slop-comments, rtl-purity, magic-numbers, forces-and-hier-access, assertion-integrity: all `{"status": "PASS"}`. No rubric filter matches `dv/**/*.md`; no RTL, TB SV, Python or ci lines are touched; nothing disabled, forced, hand-encoded or narrated as history in a code comment.

**Findings:** none. Every changed sentence traces to the cited RTL lines, the CM97 response rows match the review artifact's findings one to one, and the three sections now state one rule per write case.

Final verdict: APPROVE
