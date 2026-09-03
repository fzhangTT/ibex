# Cross-model review - committed diff a5f03ff5..1cbbcfcd

**Reviewer:** claude CLI 2.1.259 (Claude Code); run-reported model: claude-fable-5-1,claude-haiku-4-5-20251001; requested effort: high (the CLI does not report the effective setting); fresh session fc6baa46-caf1-484f-a052-97c010c516f3; sandbox: bubblewrap, working directory = detached read-only checkout of commit 1cbbcfcd5ae642f9be0db1e200fe17b1664bf4e6 (the live working tree is not read), filesystem read-only except this run's own output directory, scratch HOME (no access to the executing model's settings, instructions or memory), private PID namespace; network open for the model API, web tools disallowed by policy (fallback reviewer per owner ruling A-001)
**Codex unavailable because:** ERROR: You hit your spend cap set by the owner of your workspace. Ask an owner to increase your spend cap to continue.
**Wrapper:** dv/auto_dv/tools/gen_cross_review.sh blob 713e8c09 (the copy executed; equals the wrapper committed at the reviewed commit); reviewed commit 1cbbcfcd5ae642f9be0db1e200fe17b1664bf4e6
**Date:** 2026-09-03
**Target:** committed diff a5f03ff5..1cbbcfcd (echo at raw line 1)

---

TARGET: a5f03ff5bf13da7feca84455378a69f5b0e93838..1cbbcfcd5ae642f9be0db1e200fe17b1664bf4e6

Reviewer: Claude Fable 5.1 (claude-fable-5-1), fresh session, detached read-only checkout of 1cbbcfc. Two commits reviewed: 79c2708 (DV Lead plan v2n) and 1cbbcfc (Test Writer landing 3f). Everything below was verified against the tree, not the commit messages.

**What I reproduced**

- Non-table lines of every area's Test groups section at 1cbbcfc versus bc4ede6: ISA, CSR, DBG, MEM, SEC, XCUT, REG identical. EXC/IRQ and PMP identical except one added blank line each. The runtime-class definitions, the CSR T-053 fold, the expected-fail / doc-mismatch paragraphs, and the MEM totals paragraph are all back.
- Table lines per area at bc4ede6 versus 1cbbcfc: ISA 38/38, CSR 29/32, EXC/IRQ 26/52, PMP 23/46, DBG 34/35, MEM 36/39, SEC 41/41, REG 12/12. EXC/IRQ and PMP doubled (see M-1 below).
- `gen_trace_check.py --build-manifest dv/auto_dv/evidence/gen_sunset_pass2/gen_build_manifest_979350a.yaml`: PASS, exit 0, "marked 19", 0 would un-mark, completeness 705/705, 207/207, 16045/16045. The shared `present` / `TOKEN` / `WILDCARD_TOKENS` import works from the tree.
- `gen_token_sunset.py --dry --build-manifest <same>`: dies with a raw `FileNotFoundError` on `dv/auto_dv/work/dv-lead/parts6/tp_isa.md` (gitignored `work/`), as the docstring predicts.
- Library self-test from the clean checkout with PYTHONPATH unset: `GEN_TEST_LIB self-test PASS`, exit 0.
- Inverted the boundary assertion (`assert not any(...)` to `assert any(...)`) in an in-memory copy of gen_test_lib.py executed against the tree: `AssertionError: boundary form accepted against suffixed check names`. The red is real and lives in the self-test. `fire_fail_line` emits `GEN_TEST_FAIL <name>: N fire-check failure(s): ...`, so the three fixed names exercise exactly the `\b` versus `(?!\d)` distinction the CM3e-M-1 finding asked for.
- gen_test_cmp_zca.py docstring: no "R10", "R11", "since", "previously" left; the isa_pc_next comparator row it cites exists (gen_tb_pkg.sv PLUSARG_ISA_PC_NEXT_MASK_B13, gen_chk_isa_pc_next).
- CM20-L-1 row: at e420c7e the removal of `layers_required = False` from gen_test_csr_trap_setup.py is in the joint diff; 7ef16a0 (3e, landed after e420c7e) touches the module's evidence and its commit message and gen_tdd_batch1.md Section 11 (l9g_csr_trap_setup PASS, 168 bins) state the 16-test drop. The row's account (3e's staged tree was picked up by the joint commit) is consistent with the history.
- LOG-036-2 row: dv/auto_dv/fcov_expectations/gen_test_csr_trap_setup.fcov.yaml has 168 bins and five `# not_hit` header lines, the fifth being `gen_wit_cycle_clause_cg.cp_clause.w_tp_csr_029` with the irq-agent reason. Accurate.
- CM3e-I-1 row matches the review's info finding (ce33b4f export; HEAD-equal proof deferred to Runtime's first head-mode wave). I could not tie "entries 049..064" to ids in the committed gen_testlist.yaml (entries there are keyed differently); the statement is forward-looking, not a present claim, so no finding.
- CM20-L-2 (pass-1 README sentence), CM20-L-3 (landing-3b row supersession, Consequence row naming TP-CSR-029 as the test's item and TP-CSR-031 as gen_csr_trap_setup_irq's), and the fu1 credit Notes line on exactly TP-IRQ-014/015/016/031/038/045 all present and consistent with LOG-037b ("credits priority-pick items only from runs where the entry's claim was decidable").
- gen_fcov_manifest.py:50 still carries its own `CYCLE_CLAUSE_TOKEN`; the batch1 row records it as OPEN pending the Test Writer's import. Noted, not a defect of this range.

**Rubrics**

- ai-slop-comments: `{"status":"FAIL"}` on one low, see L-3 below (finding IDs as history anchors in code comments).
- rtl-purity: `{"status":"PASS"}` (no rtl/ changes).
- magic-numbers: `{"status":"PASS"}` (the token literal moved to one home; no new hand-encoded authority values).
- forces-and-hier-access: `{"status":"PASS"}`.
- assertion-integrity: `{"status":"PASS"}` (three assertions added; `present` and `observed_ok` moved with identical semantics; nothing disabled or weakened).

**Findings**

[medium][dv/auto_dv/docs/gen_test_plan.md:9322] The EXC/IRQ area now carries two Test groups tables: the regenerated capitalized-header table (line 9291 on) and, restored from the parts as "prose", bc4ede6's original lowercase-header table (`| group | items | phase | tier | runtime class |`, 26 rows). Same at PMP: dv/auto_dv/docs/gen_test_plan.md:11072 (`| group | items | phase | tier | estimated runtime class |`, 23 rows). The two copies disagree: gen_exc_mret / gen_exc_double_fault / gen_irq_lines / gen_irq_nmi / gen_irq_nmi_int / gen_irq_wfi read "smoke (050) / targeted" in the old table and "smoke/targeted" in the new; gen_exc_priority_info carries the "(informational; own `_info` test, C-15)" note only in the old; gen_pmp_perm_mml1 is "full/targeted" versus "targeted/full"; the PMP old table spells every id in full. Cause: the regen's table-block detector keys on the capitalized header row, so the parts' lowercase tables were classified as prose and re-emitted. The CM20-M-1 row's "verified line-for-line against bc4ede6 for every area" holds for non-table lines only; table lines went 26→52 and 23→46. No tool reads these tables (gen_trace_check.py consumes `- Test group:` lines; the CSV is unaffected), so nothing gates on it, but the deliverable now states two different tier assignments for the same groups - Recommendation: make the block detector header-case-agnostic (or match on `| gen_` rows plus the separator), regenerate, confirm one table per area against bc4ede6's row count, and add the doubled-table event to the CM20-M-1 row.

[low][dv/auto_dv/evidence/gen_critic_response_plan_set_v1.md:355] The CM20-M-1 row says "the deletion existed only in e420c7e's gen_test_plan.md", but the prose was also absent at d0e6a71 and a5f03ff (this diff is what adds it back), and the 79c2708 commit message itself names e420c7e/d0e6a71 - Recommendation: reword to "from e420c7e through a5f03ff, restored in v2n".

[low][dv/auto_dv/tools/gen_token_sunset.py:24] A committed tool that cannot run from a clean checkout: `--dry` fails with a bare Python traceback (`FileNotFoundError ... work/dv-lead/parts6/tp_isa.md`) because `W` points at the gitignored work tree and `gen_build_docs.py` is not committed. Keeping it committed is acceptable (it is the DV Lead's operator tool, each pass retains its output and the reproducible proof is gen_trace_check.py, which does run), but the failure mode should be a refusal, not a traceback - Recommendation: after computing `W`, exit with one line naming the missing parts6 / gen_build_docs.py dependency when either is absent.

[low][dv/auto_dv/tools/gen_plan_marker.py:3] Review-finding IDs used as anchors in code comments: `(CM20-L-4)` in the module docstring and in the trailing comments `# one definition (CM20-L-4)` at gen_trace_check.py:23 and gen_token_sunset.py:23. The repo's comment rule is intent-only; the finding ID is history that lives in the review artifact and Section 17 - Recommendation: keep "one definition" and drop the ID.

[info][dv/auto_dv/tests/gen_fcov_manifest.py:50] Third copy of the marker token (`CYCLE_CLAUSE_TOKEN`) remains, tracked as OPEN in gen_critic_response_batch1.md for the Test Writer's next landing; no action in this range.

Final verdict: APPROVE-WITH-CHANGES
