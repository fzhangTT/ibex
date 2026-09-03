# Cross-model review - committed diff d5ddbe28..ab3cb316

**Reviewer:** claude CLI 2.1.259 (Claude Code); run-reported model: claude-fable-5-1,claude-haiku-4-5-20251001; requested effort: high (the CLI does not report the effective setting); fresh session 8f88ba16-4708-4df8-8fbc-17fa1b58f45f; sandbox: bubblewrap, working directory = detached read-only checkout of commit ab3cb316a976b00d6229a9fa77c9b1d0adf66310 (the live working tree is not read), filesystem read-only except this run's own output directory, scratch HOME (no access to the executing model's settings, instructions or memory), private PID namespace; network open for the model API, web tools disallowed by policy (fallback reviewer per owner ruling A-001)
**Codex unavailable because:** ERROR: You hit your spend cap set by the owner of your workspace. Ask an owner to increase your spend cap to continue.
**Wrapper:** dv/auto_dv/tools/gen_cross_review.sh blob 713e8c09 (the copy executed; equals the wrapper committed at the reviewed commit); reviewed commit ab3cb316a976b00d6229a9fa77c9b1d0adf66310
**Date:** 2026-09-03
**Target:** committed diff d5ddbe28..ab3cb316 (echo at raw line 3)

---

Verification is complete. Writing the review now.

TARGET: d5ddbe28ed77b5c302922a6f187a5fba3bca7ffe..ab3cb316a976b00d6229a9fa77c9b1d0adf66310

Scope confirmed: one commit, one new file `dv/auto_dv/evidence/gen_b4_rtl_facts.md`, 85 insertions, no other path touched. The blob's SHA-256 begins 3a060d916b12 and matches the hand-off hash. The file is pure ASCII.

Verification performed in this checkout (RTL, config, fence, bug log) and, for the untracked `tools/` tree that no commit contains, in the clone's upstream spec and Spike copies only (fence-allowed upstream projects, FENCE.md:65-66; nothing else in that working tree was read):

- Decoder path holds. C2 funct3-101 casez at :622, arms 11000 (:624), 11010/11100/11110 (:687-689), 011?? (:778); instr_i[6:5] select 01 at :781, 11 at :809, default illegal :835; casez default illegal :839. Field reads :788 (instr_i[9:7]) and :797 (instr_i[4:2]) are the only sreg reads in the arm and nothing compares them. Tags COMMIT :790, LAST :800, state advance :791. Helper mapping :153-158 / :160-165 matches the spec pseudo-code (zcmp.adoc:1269). Zcmt cannot be enabled (ibex_pkg rv32zc_e has no Zcmt member).
- Atomicity holds. handle_irq blocks on COMMIT (controller :498-500); debug gates block on EXPANDED and COMMIT (:474-477); IRQ_TAKEN and DBG_TAKEN_IF save pc_if (:732, :773), so the trap lands after the LAST micro-op completes. Write path anchors wb_stage:303 and register_file_ff:252 are correct.
- RVFI anchors :2271-2281 and :2339-2348 in ibex_core.sv are correct.
- Spec quotes verified verbatim: zcmp.adoc:1163, :1174, :1175, :1242, :1263-1268, :385/:579/:771/:968, :1198/:1266; rv32.adoc:124-130; intro.adoc:307-309. Spike: cm_mvsa01.h:2 has the require, cm_mva01s.h has none, require throws trap_illegal_instruction(insn.bits()) (insn_macros.h:7); Spike HEAD is 4ffd6ba8 dated 2026-09-02 as stated; push/pop use require_zcmp_pushpop.
- Reserved-form sweep: every `reserved` in zcmp.adoc is rlist 0..3, RV32E sreg above s1, or the equal-register cm.mvsa01. The note covers all three; no missed or misjudged form. cm.mva01s with equal registers is correctly called legal.
- DV consequence: the manifest bin and comparator rows are not ruled on; see the Info item below for one borderline sentence.

Rubrics (Zone A set): ai-slop-comments PASS, rtl-purity PASS, magic-numbers PASS, forces-and-hier-access PASS, assertion-integrity PASS. The diff contains only a Markdown evidence note outside every rubric filter; no code, comment, force, constant, or assertion changed.

Findings:

[Low][dv/auto_dv/evidence/gen_b4_rtl_facts.md:28] The row says the only illegal_instr_o assignments of the funct3-101 group are :835, :839, :635, :703, but :635 and :703 are the `if (cm_rlist_d <= 5'd3)` tests (assignments at :637, :705), and the group has two more assignments, :620 (BaseIsaRV32IorCHERIoT with cheriot_enable_i On) and :843 (Zcmp not enabled). Neither compares the sreg fields, so the verdict stands - reword to "encoding-level illegal terms", cite :637/:705, and state the preconditions cheriot_enable_i = IbexMuBiOff (gen_dut_top.sv:206) and RV32ZC = RV32ZcaZcbZcmp (ibex_configs.yaml:46). Same fix for the anchors row at :80.

[Low][dv/auto_dv/evidence/gen_b4_rtl_facts.md:4] The ISA manual line anchors are cited against an untracked tree with no revision pinned, while Spike is pinned to 4ffd6ba8 - record the manual's on-disk revision (fa794b6, 2026-09-02) beside the path so the :1163/:1174 anchors stay reproducible.

[Info][dv/auto_dv/evidence/gen_b4_rtl_facts.md:38] "the debug gates block entry on both tags" reads as the two micro-op tags, but the gated set is {INSTR_EXPANDED, INSTR_EXPANDED_COMMIT} and the second micro-op carries INSTR_EXPANDED_LAST; atomicity holds because the trap saves pc_if after that op retires (controller :732, :773) - name the tag set and the pc_if save so the reasoning is checkable.

[Info][dv/auto_dv/evidence/gen_b4_rtl_facts.md:42] "A model that traps sees one trap record instead, which is the comparator's first divergence" is a DV-consequence sentence in a note whose header excludes DV consequence - either drop it or mark it as an observation for the DV Lead, not a row proposal.

Final verdict: APPROVE-WITH-CHANGES
