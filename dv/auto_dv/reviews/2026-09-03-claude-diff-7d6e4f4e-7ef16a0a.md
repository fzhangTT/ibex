# Cross-model review - committed diff 7d6e4f4e..7ef16a0a

**Reviewer:** claude CLI 2.1.259 (Claude Code); run-reported model: claude-fable-5-1,claude-haiku-4-5-20251001; requested effort: high (the CLI does not report the effective setting); fresh session 5588fd77-f0b7-4274-a350-c97ce83d2836; sandbox: bubblewrap, working directory = detached read-only checkout of commit 7ef16a0a861be2f030beffd88582538fcffb5c8d (the live working tree is not read), filesystem read-only except this run's own output directory, scratch HOME (no access to the executing model's settings, instructions or memory), private PID namespace; network open for the model API, web tools disallowed by policy (fallback reviewer per owner ruling A-001)
**Codex unavailable because:** ERROR: You hit your spend cap set by the owner of your workspace. Ask an owner to increase your spend cap to continue.
**Wrapper:** dv/auto_dv/tools/gen_cross_review.sh blob 713e8c09 (the copy executed; equals the wrapper committed at the reviewed commit); reviewed commit 7ef16a0a861be2f030beffd88582538fcffb5c8d
**Date:** 2026-09-03
**Target:** committed diff 7d6e4f4e..7ef16a0a (echo at raw line 1)

---

TARGET: 7d6e4f4e85e0394a53099a97efed8fcad3bf8659..7ef16a0a861be2f030beffd88582538fcffb5c8d

Reviewer: Claude Fable 5.1 (claude-fable-5-1), fresh session, read-only detached checkout of 7ef16a0; every result below is mine, run in this checkout after `source ci/env.sh`.

**What I ran and what it showed**

- Library self-test (`python3 -m dv.auto_dv.tests.gen_test_lib --self-test`, PYTHONPATH = checkout): PASS in 7.2 s, 16 test modules checked, no stale-evidence notice printed.
- `gen_flow_util.py --check-red-signatures` from this checkout: 16 RED-OK rows, harness match True on each, no STALE row, overall PASS. The 17th committed red entry (gen_ut_lockstep_forced_red) is reported `skip: no retained pinned-red log`; it is a UVM fixture, not a test-module red, so it is outside the self-test's rule.
- Priority 1 (CM14-H-1): `gen_mul_div_prog.py --seed 1` regenerated OK. Filler-shaped lines naming x5..x7: 0. Lines on x29..x31: 144 (3 `li` inits + 141 fillers). Seed 2: 0 and 102 (99 fillers). The import-time assertion is present at gen_mul_div_prog.py:80 and FILLER_TEMPLATES render from FILLER_REGS. The retained l8_mul_div s1/s2 are PASS with UVM_ERROR 0, red_014 fails on fire_tp_mul_014; md5s equal the transcript. CR-B2-L-8 row now reads "FIXED (3e); the 3d row was false" and names it an honesty defect under LOG-024d (c).
- Priority 2 (CM14-H-2 / CR5-M-1): I applied the committed rule (synthesize `lib.fire_fail_line` per recorded name from source literals plus GEN_TEST_FIRE names of the retained log) to the bit_ratified and bit_draft red entries. Committed `(?!\d)` forms match; the boundary forms `...\bfire_tp_bit_014\b` and `...\bfire_tp_bit_016\b` (both as full harness regex and bare) return no match, so the self-test would refuse them. The template now raises `lib.fire_fail_line(...)` (one producer).
- Priority 3 (LOG-024d): `len(lib.REFUSED_FORMS) == 15`, `lib.api_doc_forms() == list(lib.REFUSED_FORMS)`. The API doc carries "Everything else passes; the lint is not a guarantee" and lists the probed passing forms. I extracted the red-source tuples from the self-test at 7f78c41 and 7ef16a0 with an AST walk: 44 sources each, lists byte-identical, so there is no lint growth beyond 7f78c41.
- Priority 4: all seven verdict files (boot_retire, rst_boot, csr_reset, csr_trap_setup, pmp_csr_warl, b2_cmp_zca, b2_isa_cti) read `verdict: RED-OK` with the harness line as evidence. `git diff --stat a8dfec4 b95d6d2 -- dv/auto_dv/gen_tb dv/auto_dv/tb dv/auto_dv/env dv/auto_dv/isa` is empty, so out_head5 is HEAD-equal as claimed; ce33b4f, a8dfec4 and b95d6d2 are ancestors of the reviewed commit.
- Priority 5: `grep layers_required` over the 16 test modules returns nothing; gen_test_csr_trap_setup never carried it. All 16 gen_l9g_* logs: GEN_TEST_PASS, UVM_ERROR : 0, `fire_schedule_applied ok=True`, GEN_TEST_PHASE lines present, no `not_applied`; md5s equal the Section 11 table. gen_test_csr_access `schedulable` no longer names knob_instr_mix, and gen_tb_knobs.yaml marks that knob `regime_set_consumer: program`. The commit touches no testlist (`git diff --name-only | grep -i testlist` empty); the staging file under dv/auto_dv/work is untracked.
- Priority 6: I extracted `git archive 26969205` and `7f78c41` to scratch and ran check_test_source on `def _h(t): u = t; u.failures = []` called as `_h(self)`: ACCEPTED at 26969205, refused at 7f78c41. So "one rule was missing and was added in 3d" (gen_tdd_test_template.md 9.3, CM3c-H-1 row, CM14-M-3 row) is true. The bit_draft docstring now says generator growth is the blocker and agrees with its not_built reasons.
- Priority 7: manifest rows 461, directory files 461 (excluding the manifest), every row's size and md5 equal the retained copy, no file without a row. Deletions with `--no-renames`: 11, set-equal to the header's drop list (git shows 7 of them as l7->l8 renames). 76 per-item red excerpts start with `# run <name>: <timestamp> ...`; the remaining 9 excerpt files are the pre-existing T-102-era sim excerpts (start with `Command:`), untouched.
- Priority 8: the CM14-L-1 fragment is fixed (the isa_alu paragraph now stands alone after a blank line; "After the" is a line wrap). CM14-L-2 (ODD_PLAN_MIN in detail and docstring), CM14-L-3 (FLOW_RUN_ENV from JOB_ENV_SET with a one-key assertion), CM14-L-4 (missing module/red_expect fails loud) verified in the diff.

**Rubrics**

- ai-slop-comments: PASS (one borderline phrase, listed as low below; not certain enough to fail the rubric).
- rtl-purity: PASS (no rtl/ change).
- magic-numbers: PASS (the FLOW_RUN_ENV literal was removed; the duration/timeout relation is asserted against CONSTANTS).
- forces-and-hier-access: PASS (no new drives; the `.value = 1` text is an API-doc example of a passing lint shape, not code).
- assertion-integrity: PASS (the old red_expect rule is replaced by a stricter one, the `continue` exemptions are removed, layers_required opt-outs are removed which strengthens setup; no checker weakened).

**Findings**

[medium][dv/auto_dv/tests/gen_test_lib.py:932] The new red_expect rule has no committed red: the negative check (boundary forms `\bfire_tp_bit_014\b` / `\bfire_tp_bit_016\b` failing the synthesized-line match) exists only as a transcript record (gen_tdd_batch1.md:510) from a staged, uncommitted testlist copy, while gen_critic_response_batch1.md:187 says "a red source backs the rule (the staged copy that fails)". Trust-triad rule 2 and LOG-024d (c) want the red rerunnable from the tree - add an in-self-test negative (a fixed name list plus the boundary regex asserted to produce no match through `fire_fail_line`) and reword the CR5-M-1 row to say the red is in the self-test; this is a red_expect-rule red, not check_test_source growth, so LOG-024d (a) is untouched.

[low][dv/auto_dv/tests/gen_test_cmp_zca.py:59] Docstring narrates history: "the Spike-based model reports 0 too since the shim's R10 row, so the run is UVM_ERROR-free" - state the present fact only (model and DUT both report mtval 0 after c.ebreak); the R10 row belongs in the transcript.

[info][dv/auto_dv/evidence/gen_tdd_batch1.md:163] The 16 promotion greens are proven on an export of ce33b4f; the reviewed commit's TB directories differ from ce33b4f in five files (gen_knobs.py, gen_tb_knobs.yaml, gen_env_cfg_knobs.svh, gen_tb_pkg.sv, gen_rvfi_pkg.sv). The owner's brief already accepts a local ce33b4f build; the first Runtime wave on HEAD is the HEAD-equal proof.

Final verdict: APPROVE-WITH-CHANGES
