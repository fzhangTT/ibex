# Cross-model review - committed diff 43b47dad..79ef3fa0

**Reviewer:** claude CLI 2.1.259 (Claude Code); run-reported model: claude-fable-5-1,claude-haiku-4-5-20251001; requested effort: high (the CLI does not report the effective setting); fresh session 0e682936-713d-4937-87ef-25dbf4cf6c23; sandbox: bubblewrap, working directory = detached read-only checkout of commit 79ef3fa0d2dbf7b7aed4c079aeb652882bfc8aea (the live working tree is not read), filesystem read-only except this run's own output directory, scratch HOME (no access to the executing model's settings, instructions or memory), private PID namespace; network open for the model API, web tools disallowed by policy (fallback reviewer per owner ruling A-001)
**Codex unavailable because:** ERROR: You hit your spend cap set by the owner of your workspace. Ask an owner to increase your spend cap to continue.
**Wrapper:** dv/auto_dv/tools/gen_cross_review.sh blob 713e8c09 (the copy executed; equals the wrapper committed at the reviewed commit); reviewed commit 79ef3fa0d2dbf7b7aed4c079aeb652882bfc8aea
**Date:** 2026-09-03
**Target:** committed diff 43b47dad..79ef3fa0 (echo at raw line 1)

---

TARGET: 43b47dad7729b490cd5ee7676ba9ddd948a59d95..79ef3fa0d2dbf7b7aed4c079aeb652882bfc8aea

Reviewer identity: Claude Fable 5.1 (claude-fable-5-1), fresh non-interactive session, read-only detached checkout of 79ef3fa; independent reviewer, not the author.

Scope reviewed: one commit (79ef3fa), 10 files, +702/-21. Content: plan v2r part 3 (Section 0 round-0 outcome and crediting rule, Section 1.7 embedded probe credit, TP-PMP-109 Notes rewrite), new tool `dv/auto_dv/tools/gen_round_credit.py`, generated evidence under `dv/auto_dv/evidence/gen_round0_credit/`, `gen_promotion_table.py` hold-section discovery plus regeneration command, Critic-response rows CM34/CM36/T-204, timestamp bumps in the feature list and fcov plan. No `rtl/**`, no `.sv/.svh`, no test code touched.

What I verified against the repository (not from the commit message):
- `gen_round_credit.py --self-test` exits 0 with all three cases ok.
- `gen_promotion_table.py --plan-sha 43b47da --out /tmp/x` reproduces `gen_round0_promotion_table.md` byte for byte at this commit, as the new header claims (CM34-I-1 / CM36-L-2 closed).
- Credit CSV has 162 data rows; the 15 hosted groups' item counts in the promotion table sum to 162; the seven held items (TP-CMP-011, CSR-029, CSR-035, ISA-016, ISA-026, PMP-006, RST-006) carry their T-136/T-137 tags in the CSV `hold` column, so real-plan hold parsing works. Witness bins 2 (TP-CSR-029, TP-ISA-024) match the summary line.
- The tool's manifest reads (`sim_stdout_log`, `fcov_check.bins[*].state`, `unmet_bins`, verdicts `PASS`/`XFAIL`) match the flow's schema in `gen_run.py`, `gen_fcov.py`, `gen_regress.py`, `gen_flow_const.py`; the `GEN_TEST_FIRE <name> ok=<bool>` pattern matches `gen_test_template.py:303`.
- gen_boot_zc and gen_ut_lockstep host no plan items (no `Test group:` references), consistent with the Section 0 text.
- Section 0 numbers (47 runs, 2 PASS, 45 FAIL = 44 unverifiable + 1 runaway in gen_test_csr_reset) are internally consistent with the embedded header and per-test table.
- No `## 1.6` heading exists in the plan; the new `## 1.7` heading does not match `HOLD_HDR`, so the promotion table's held column is unaffected.

Rubric results:
- ai-slop-comments: PASS. Added comments/docstrings explain intent ("match on the coverpoint.bin tail", "the hold sections present in the plan"); no restatement, filler, or pasted duplicates. The plan's record-keeping prose is a deliverable, not code comments.
- rtl-purity: PASS (no `rtl/**` in the diff).
- magic-numbers: PASS. The `/proj_soc/...` path in the generated report is manifest data echoed into an evidence file, not a hard-coded tool path; the tool takes the manifest path as an argument.
- forces-and-hier-access: PASS (no DUT handle drives; Python here is offline report generation).
- assertion-integrity: PASS. No assertion, checker, or manifest bin list removed or weakened; `gen_trace_tp_bin.csv` and all fcov manifests untouched in this range.

Findings:

[Low][dv/auto_dv/tools/gen_round_credit.py:19] `HOLDS` hard-codes `('1.6', 'T-181')` and the docstring (line 7) states "1.6 T-181: recorded, not credited", while the plan's Section 0 crediting rule (gen_test_plan.md:218) names only Sections 1.4 / 1.5 and records T-181 as LIFTED. This is the same defect CM36-L-2 just fixed in `gen_promotion_table.py`, reintroduced in the new tool. Latent hazard: the section regex `^## 1\.6 .*?\n(.*?)` matches any future `## 1.6` heading and would mark every `| TP-xxx-nnn | ... |` row in it as held under T-181; today no 1.6 exists, so the committed CSV is unaffected. - Recommendation: reuse the `HOLD_HDR` discovery pattern from `gen_promotion_table.py` (or import its `load_plan`) and drop the stale T-181 wording from the docstring; regenerate the evidence (output is unchanged today).

[Low][dv/auto_dv/tools/gen_round_credit.py:196] The summary filter strips the item-table header line (`| Item | Group | Test ...`) but not its `|---|...|` separator, leaving an orphan separator row at the end of `gen_round0_credit_summary.md:40` and, since the summary is embedded verbatim, at `gen_test_plan.md:819` inside Section 1.7. Renders as a malformed table. - Recommendation: also drop the separator that follows the stripped header (or build the summary without the item table instead of filtering lines), then regenerate the summary and re-embed.

[Low][dv/auto_dv/tools/gen_round_credit.py:80] Group-to-test attribution (`test_of_group.setdefault`) takes the first run in manifest order that emits the group's fire lines and never excludes red fixtures (`*_red`, `red_fixture: true`, verdict `RED-OK`). Nine reds in `gen_testlist.yaml` precede their main test (e.g. `gen_test_mul_div_red` at line 712 before `gen_test_mul_div` at 737). Reds are tier check and did not run in the probe (47 runs = 15×3 + 2), so the committed credit is correct; but any manifest that includes check-tier runs would attribute those groups to the red fixture and report every item NOT-RUN-CLEAN. - Recommendation: filter runs the same way `gen_promotion_table.py:218` filters testlist entries (skip `_red` names / `red_fixture` / `RED-OK`), and add a self-test case.

[Low][dv/auto_dv/docs/gen_test_plan.md:209] Section 0 cites "Runtime's probe record dv/auto_dv/evidence/gen_round_0_probe/" and the Critic-response row (gen_critic_response_plan_set_v1.md:410) says the probe is "retained by Runtime as" that path, but the directory does not exist at 79ef3fa (LOG-046 assigns it as open task T-207). The regression manifest and sim logs the Section 1.7 numbers derive from are therefore not in the tree; unlike the promotion table, the credit report prints no regeneration command. - Recommendation: mark the path as pending T-207 in both places, and have `gen_round_credit.py` print its exact invocation (manifest path, `--round`, `--heading`) in the report header so the evidence is reproducible once the probe record lands.

[Info][dv/auto_dv/tools/gen_round_credit.py:89] `fid` is computed and never used. - Recommendation: delete the line.

[Info][dv/auto_dv/docs/gen_test_plan.md:780] Section numbering jumps 1.5 to 1.7 (1.6 deleted in e93c880). Harmless for the tools (both match on heading text), but a reader may look for a missing 1.6. - Recommendation: either renumber to 1.6 or add a one-line note that 1.6 was the lifted T-181 hold.

Assessment: the substantive claims of the commit hold up on inspection (counts, hold tags, byte-identical promotion table regeneration, schema compatibility with the flow, honest zero-credit outcome). The findings are consistency and robustness defects in the new tool and generated text, none of which changes the recorded round-0 result.

Final verdict: APPROVE-WITH-CHANGES
