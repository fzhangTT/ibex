# Cross-model review - committed diff ae0ce2f1..e2f3f65d

**Reviewer:** claude CLI 2.1.260 (Claude Code); run-reported model: claude-fable-5-1,claude-haiku-4-5-20251001; requested effort: high (the CLI does not report the effective setting); fresh session 9dc3d7e0-f400-4025-812f-aece1d8c8aa1; sandbox: bubblewrap, working directory = detached read-only checkout of commit e2f3f65dd46b1c2624abe57cf461d08d2e389444 (the live working tree is not read), filesystem read-only except this run's own output directory, scratch HOME (no access to the executing model's settings, instructions or memory), private PID namespace; network open for the model API, web tools disallowed by policy (fallback reviewer per owner ruling A-001)
**Codex unavailable because:** ERROR: You hit your spend cap set by the owner of your workspace. Ask an owner to increase your spend cap to continue.
**Wrapper:** dv/auto_dv/tools/gen_cross_review.sh blob 713e8c09 (the copy executed; equals the wrapper committed at the reviewed commit); reviewed commit e2f3f65dd46b1c2624abe57cf461d08d2e389444
**Date:** 2026-09-04
**Target:** committed diff ae0ce2f1..e2f3f65d (echo at raw line 1)

---

TARGET: ae0ce2f1e02f51bbe4b10299d94d9572fd561f8c..e2f3f65dd46b1c2624abe57cf461d08d2e389444

Scope: one commit (e2f3f65), 10 files, +850/-11. No SV, RTL, knob, rendered, flow or CI file in the diff (verified from `git diff --stat`), so no build identity moves.

**Verified against the repository (independent of the records):**
- Tag-write artifact: md5 12fe9260…/23802 bytes and diff artifact 07303af8…/2483 bytes match their manifest rows; manifest has 3459 rows. The artifact holds exactly 322 `ICTRACE tagwrite` lines, all parseable, cycle-monotone, indices {26, 27}, taken from the retained duplicate-copies log (17 at index 26 + 3 at 27 = the 20 announced two-way-valid injections). I replayed the reconstruction myself from the retained raw lines with an independent script: 16 episodes, 13 at index 26 and 3 at 27, tag 00100000, every episode's `added_way` is the way of the write that completed coexistence while the other way already held the same tag valid (asserted per episode), all 16 into way 0, and the 16 generated episode rows are byte-identical to the committed ones. Every episode ends on a same-cycle two-way valid=0 write, consistent with `ecc_correction_ways_d` at rtl/ibex_icache.sv:590-592. The added-way field is derived from the raw writes, not assumed.
- Mutant diff: three added `$display` lines, no removal, `git apply --check` succeeds against the committed gen_tb_pkg.sv. The trace17 per-file list differs from the w18 list in gen_tb_pkg.sv alone; the run header and compile log carry sources sha 74c372d4823c6bc1.
- Figures tool: positive control from the committed tree exits 0 with 0 problems and reproduces 904/554 and 619/174 (Section 5a and the API row), and the six re-run totals 988, 494, 483, 830, 930, 13. Negative control on a /tmp copy (count line pulled out of the comment block) exits 1 naming `BITS BITS_catch_ecc_tag_two`. The 13 w16 GEN_MISC lines at a28d1ae are 400-character cuts and match the current lines over those 400 characters, 13 of 13; the a28d1ae verdict files carry the w16 `uvm_counts` ERROR totals, so the "from the retained verdict files" wording holds.
- Landing-15 commit accounting: 58 A, 77 M, 10 D, 11 R (= 21 retirements). `dv/auto_dv/.gitignore:4` excludes `work/`, so the CR-16-L-1 correction is right. The retired gen_fu_l16_TRACE_index26.log is no longer cited by the plan or the feature list (CR-16-I-1 disposition holds); the feature list at 5eb7ddb^ did carry "13 duplicates", so "reproduces the figure the plan had carried" is fair. DATAWAY far probe-off shows site 660 = 1 (CR-16-I-3). Identity tool's 13-root map includes TRACE17, matching "13 roots, 13 matches".
- Dispositions CM179-m-1, m-3, m-4, m-5 and CR-16-L-2..L-5, I-2, I-3 answer their findings without overstating. CM179-m-2 / CR-16-L-1 are incomplete on one site (finding 1).

**Findings**

[minor][dv/auto_dv/evidence/gen_critic_response_fu2a.md:204] The CM173-M-1 row still reads "re-derived from the retained line by scratchpad/gen_l15_figures.py", a site the Critic's L-1 named explicitly ("the CM173-M-1 row name[s] … gen_l15_figures.py"), while the CM179-m-2 row (line 233) and CR-16-L-1 row (line 243) claim the untracked-script citations are answered - re-point that row to dv/auto_dv/tools/gen_icache_ecc_figures.py (or mark it as the landing-15 name, now committed as …), so the DONE claim is true on every site the reviews named.

[low][dv/auto_dv/tools/gen_icache_ecc_figures.py:1] Docstring usage line names the tool `gen_l15_figures.py <landing root>`, the scratchpad name, not the committed one - rename in the usage line.

[low][dv/auto_dv/tools/gen_mutant_build_identity.py:1] Usage line lists four positionals `<landing root> <build> <scratch root> <build>` but the code reads argv[1..3] - drop the trailing `<build>`.

[low][dv/auto_dv/evidence/gen_tdd_logs/mutations/gen_fu_l16_trace17_tagwrite_history.log:3] The header presents the causal mechanism as what the file evidences ("…after an ECC-correction refetch, because each fill captures its way in the IC1 cycle … while the correction's invalidation write lands later, and no comparator …"), yet the file shows only tag writes: coexistence and the added way. The narrowing sentence (line 16) bounds only the way-selection policy, not the causal link - in the generator's head strings (gen_trace_tagwrite_history.py:46-50) mark the "because" clause as derived from rtl/ibex_icache.sv:534-535, 590-592 and say the file evidences coexistence and direction per episode only. The raw writes are consistent with that RTL story (single-way valid=0 before each episode, a two-way valid=0 ending it), which is worth stating as consistency, not causation.

[low][dv/auto_dv/evidence/gen_tdd_logs/mutations/gen_fu_l16_trace17_tagwrite_history.log:9] "322 tag-write lines at those indices of 1564 in the run" and gen_tdd_step2b.md:833 "out of the trace run's 1564": the 1564 total has no retained source; the retained trace17 stdout excerpt holds 0 tagwrite lines and the stdout.log is scratch - either retain a count line or word the total as taken from the unretained stdout.

[low][dv/auto_dv/tools/gen_trace_tagwrite_history.py:28] The committed tool refuses to run unless the scratch `mut_root/TRACE17/out/trace_align_dup/stdout.log` exists, so a reader of the tree cannot re-run the reconstruction even though the committed artifact carries all 322 raw writes it reads; the record's "regenerates its artifact byte-identically" is checkable only with the scratch root - add a mode that re-derives the episode block from the retained artifact's raw lines (my independent replay confirms it would reproduce the 16 rows exactly).

[low][dv/auto_dv/tools/gen_trace_tagwrite_history.py:3] (ai-slop-comments) docstring history narration: "The earlier tag-write trace was retired with landing 15 because its build had no per-file sources list; this one comes from the trace session on the landing build, which retains both." - keep the docstring to intent (what the tool derives and from what); the history is in gen_tdd_step2b.md Section 18.

**Rubrics**
- ai-slop-comments: `{"status": "FAIL", "summary": "one history-narration docstring", "comments": [{"file": "dv/auto_dv/tools/gen_trace_tagwrite_history.py", "line": 3, "quote": "The earlier tag-write trace was retired with landing 15 because its build had no per-file sources list", "comment": "history narration in a docstring; intent-only rule", "confidence": 60}]}`
- rtl-purity: `{"status": "PASS"}` (no rtl/ files in the diff)
- magic-numbers: `{"status": "PASS"}` (mutation-to-file map, run-name lists and scratch layout paths are tool-local evidence bookkeeping, not config, CSR, tool-path or hierarchy authority)
- forces-and-hier-access: `{"status": "PASS"}` (no SV or cocotb drive code in the diff)
- assertion-integrity: `{"status": "PASS"}` (no assertion or checker touched; the figures tool's identity checks are strengthened, not weakened)

Final verdict: APPROVE-WITH-CHANGES
