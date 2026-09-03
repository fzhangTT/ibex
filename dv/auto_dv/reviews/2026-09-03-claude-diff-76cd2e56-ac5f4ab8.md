# Cross-model review - committed diff 76cd2e56..ac5f4ab8

**Reviewer:** claude CLI 2.1.259 (Claude Code); run-reported model: claude-fable-5-1,claude-haiku-4-5-20251001; requested effort: high (the CLI does not report the effective setting); fresh session ccd41bec-5ad5-478c-b664-a12d1caaf7e9; sandbox: bubblewrap, working directory = detached read-only checkout of commit ac5f4ab8d5a36c527bc3f92a7fb77306f772c2d7 (the live working tree is not read), filesystem read-only except this run's own output directory, scratch HOME (no access to the executing model's settings, instructions or memory), private PID namespace; network open for the model API, web tools disallowed by policy (fallback reviewer per owner ruling A-001)
**Codex unavailable because:** ERROR: You hit your spend cap set by the owner of your workspace. Ask an owner to increase your spend cap to continue.
**Wrapper:** dv/auto_dv/tools/gen_cross_review.sh blob 713e8c09 (the copy executed; equals the wrapper committed at the reviewed commit); reviewed commit ac5f4ab8d5a36c527bc3f92a7fb77306f772c2d7
**Date:** 2026-09-03
**Target:** committed diff 76cd2e56..ac5f4ab8 (echo at raw line 3)

---

Verification is complete. I'm writing up the review now.

TARGET: 76cd2e56e2afac1dea6da6cb89ecdff7feb704c0..ac5f4ab8d5a36c527bc3f92a7fb77306f772c2d7

**Scope reviewed.** One commit, one file: `dv/auto_dv/flow/gen_testlist.yaml`, 116 added lines, five new `check`-tier entries for the lock-step family (`gen_ut_lockstep_bitcnt`, `_zca`, `_zcmp`, `_zcmp_misaligned`, `_zcmp_dummy`). No RTL, SV, Python, or ci changes.

**What I verified against the tree**

- The committed testlist loads cleanly through `load_testlist` in `dv/auto_dv/flow/gen_flow_util.py`. It reports 56 tests, matching the commit message. All five entries use only keys in `TEST_REQUIRED_KEYS` / `TEST_OPTIONAL_KEYS` (`notes` and `keep_artifacts` are declared optional keys), tier `check` with `measured: false` satisfies the Critic R-01 rule, and `expected_fail: true` is not combined with `red_fixture`.
- All five directed programs exist under `dv/auto_dv/stim/gen_directed/`. Their contents match the descriptions: bitcnt runs clz/ctz/cpop over a 9-entry operand table plus a 32-step walking one with rd=x0 variants; zca covers the RVC forms at word- and half-aligned starts with 16/32 successors and a straddle; zcmp iterates rlist 4..15 x spimm 0..3 for push/pop and popret/popretz through calls with word-, half-aligned, and one odd return; misaligned offsets sp by 1, 2, 3 cumulatively; dummy sets bit 2 of CSR 0x7C0 (cpuctrlsts.dummy_instr_en) around four push/pop pairs.
- The plusargs match the retained evidence runs in `dv/auto_dv/evidence/gen_tdd_logs/fcov/gen_fu_l4_lockstep_{bitcnt,zca,zcmp,zcmp_mis,zcmp_dummy}_run_header.txt` (boot_retire 100/100/100/10/10). The four non-xfail runs are retained PASS; the dummy run is retained FAIL with evidence `UVM_ERROR ... [isa_mem] Zcmp stores: model 1, dut 2`, consistent with the entry's description and with `expected_fail: true` semantics in `gen_verdict.py` (FAIL becomes XFAIL, PASS becomes FAIL "unexpected PASS of an expected-fail test").
- The covergroups named in the descriptions exist in `dv/auto_dv/env/gen_fcov_groups.svh` (`gen_bit_count_cg` :1862, `gen_cmp_zca_cg` :2073, `gen_cmp_zcmp_pushpop_cg` :2390 with `cp_ret_align` :2402 and `cr_insn_delay` :2405). The knob `+gen_knob_dmem_rvalid_delay` exists in `gen_knobs.py`. TP-CMP-065 and B8 are recorded in `gen_bug_log.md` and `gen_fcov_plan.md`. `evidence/gen_b8_rtl_facts.md` exists.
- The `fcov_expectation_file: null` is consistent with the sibling `gen_ut_lockstep_muldiv` / `_alu` entries and exempt for tier `check` per the file's own policy header.

**Rubric results**

- ai-slop-comments: PASS (no comment lines added in a filtered path; the yaml descriptions are intent-bearing, not history narration).
- rtl-purity: PASS (no `rtl/` change).
- magic-numbers: PASS (the testlist is the authority for test entries; plusarg values are per-entry stimulus knobs consistent with the retained runs).
- forces-and-hier-access: PASS (no SV/Python added).
- assertion-integrity: PASS. `expected_fail: true` on a new entry does not disable or weaken any checker; the lock-step comparator still fires and the flow records XFAIL, and an unexpected PASS is turned into FAIL by `gen_verdict.py:130-134`.

**Findings**

[Minor][dv/auto_dv/flow/gen_testlist.yaml:1420] The `notes` field points at `evidence/gen_b8_row_mapping.md`, which does not exist anywhere in the tree (`git ls-files` finds no such file; `gen_b8_rtl_facts.md:147` says it "lands with tb-infra's next landing"). A committed testlist should not cite an artifact that is not yet committed - either land the mapping file in the same change or reword the note to point at the existing `dv/auto_dv/evidence/gen_b8_rtl_facts.md` §6 (Reproduction status) until the mapping lands.

[Minor][dv/auto_dv/flow/gen_testlist.yaml:1420] The two paths in the same `notes` line use different roots: `gen_tdd_logs/fcov/gen_fu_l4_lockstep_zcmp_dummy_*` is relative to `dv/auto_dv/evidence/`, while `evidence/gen_b8_row_mapping.md` is relative to `dv/auto_dv/`. The rest of the file uses clone-relative paths (e.g. `program.directed`). Make both clone-relative.

[Info][dv/auto_dv/flow/gen_testlist.yaml:1416] `expected_fail` is untyped in the flow: any FAIL (including a read-back mismatch, a missing tohost store, or a comparator-count mismatch unrelated to B8) is reported as XFAIL, so the reproducer cannot distinguish "still red for the B8 reason" from "broken for another reason". The retained evidence line is a stable `[isa_mem]`/`[isa_rd]` UVM_ERROR; consider recording that signature in the entry's description or `notes` so a future triager can compare, or extending the flow with an xfail signature. Not a blocker for this diff; a flow-level limitation.

[Info][dv/auto_dv/flow/gen_testlist.yaml:1417] `keep_artifacts: true` has no effect unless the entry names an export plusarg (retention prunes only the file named by `+gen_export_file`, per `gen_flow_const.py` and `gen_regress.py:289`). The retained dummy run did pass `+gen_export_file=gen_export.txt` but the testlist entry does not. Harmless and consistent with the existing muldiv/alu entries, noted for accuracy only.

Final verdict: APPROVE-WITH-CHANGES
