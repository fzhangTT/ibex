# Cross-model review - committed diff 04dea6be..7a468ec7

**Reviewer:** claude CLI 2.1.259 (Claude Code); run-reported model: claude-fable-5-1,claude-haiku-4-5-20251001; requested effort: high (the CLI does not report the effective setting); fresh session 8622ec6f-848b-46d7-b04a-6d60b34617fd; sandbox: bubblewrap, working directory = detached read-only checkout of commit 7a468ec7523ae2eef23279ba3b265b1f4934752d (the live working tree is not read), filesystem read-only except this run's own output directory, scratch HOME (no access to the executing model's settings, instructions or memory), private PID namespace; network open for the model API, web tools disallowed by policy (fallback reviewer per owner ruling A-001)
**Codex unavailable because:** ERROR: You hit your spend cap set by the owner of your workspace. Ask an owner to increase your spend cap to continue.
**Wrapper:** dv/auto_dv/tools/gen_cross_review.sh blob 713e8c09 (the copy executed; equals the wrapper committed at the reviewed commit); reviewed commit 7a468ec7523ae2eef23279ba3b265b1f4934752d
**Date:** 2026-09-03
**Target:** committed diff 04dea6be..7a468ec7 (echo at raw line 1)

---

TARGET: 04dea6be40560219501df39b9c7e5206c07c6240..7a468ec7523ae2eef23279ba3b265b1f4934752d

Reviewer identity: Claude Fable 5.1 (claude-fable-5-1), fresh detached session, read-only checkout of 7a468ec. Scope: the single commit 7a468ec (five files: gen_regress.py, gen_flow_util.py, gen_testlist.yaml, gen_runtime_api.md, gen_critic_response_flow.md).

## What I verified against the repository

**(1) fcov_policy_failures exempts measured: false.** The guard at gen_regress.py:243 now reads `t["tier"] in required and t.get("measured", True) and not t.get("fcov_expectation_file") and r["verdict"] == PASS`. Reproduced on the committed testlist with `select_tests(tl, "smoke", None, None)`: 16 tests selected, including gen_boot_zc and gen_ut_lockstep (both measured: false, no manifest). Fabricated PASS runs through the function with the committed header `[smoke, targeted]`: nothing flipped with covergroups_exist False or True. With gen_test_isa_alu's manifest set to null: it FAILs with reason `no fcov_expectation_file on tier smoke (fcov_manifest_required_tiers)` in both covergroup states. gen_test_bit_draft (targeted) with its manifest removed: FAIL. Header emptied plus covergroups_exist=True: the measured smoke entry FAILs with the rule-3 reason, the unmeasured ones stay PASS. An entry with the `measured` key absent is treated as measured (consistent with the loader at gen_flow_util.py:841 and the run path at gen_regress.py:104). The self-test fixture gen_d (smoke, measured: false) is asserted PASS in both the covergroups-exist and the header cases. `python3 gen_regress.py --self-test`: PASS, exit 0. Docstring and the testlist Policies comment match the code.

**(2) Flow-style re-emission.** The testlist at 04dea6b and at 7a468ec are yaml-equal (`yaml.safe_load` equality True). `git diff -U0 3e6f1b2~1..HEAD -- gen_testlist.yaml` contains only `tier:`, `measured:`, `fcov_expectation_file:` lines plus the header value and header comment lines; the negative filter for anything else returns nothing. Loader (`--dump-testlist gen_testlist.yaml`) exit 0, 45 entries, every entry carries `measured`.

**(3) red_check_line / red_check_summary.** Both are module-level functions; the `__main__` block calls them and exits with the returned code. `python3 gen_flow_util.py --self-test`: 59 ok, PASS, exit 0; the new "red check CLI builders" line is among them. `--check-red-signatures` on the committed testlist: PASS, exit 0. Behaviour vs the old inline code is unchanged for every reachable input: red_signature_check can never return both `refuse` and `stale_cause` (refuse=RED_STALE_REFUSE only when `allow is None`, stale_cause only when `allow is not None`; a mismatch refusal forces `stale` False).

**(4) CM23 rows.** H-1, I-1 and the folded docstring row are accurate against the review file's findings and the landing; the "tier smoke selects 16 tests" proof matches. LOG-039a's ruling (fix, self-test with the measured field, docstring, flow style, red-check builders as functions) is fully landed. One count in L-1 is off (below).

**Rubrics.** ai-slop-comments: PASS (added comments are intent-level; no history narration in code; the evidence table is the sanctioned history surface). magic-numbers: PASS. forces-and-hier-access: PASS (no signal drives). rtl-purity: PASS (no rtl/ change). assertion-integrity: PASS (self-test conditions re-indexed and strengthened, nothing removed or weakened; the deleted `bad`/`stale` counters are replaced by `sum()` over the same dicts).

## Findings

[Low][dv/auto_dv/docs/gen_runtime_api.md:262-264] Section 3 still ends the header-policy sentence with "once the first covergroup exists", so it says the named-tier FAIL is gated on covergroups. The code applies the header-named tiers unconditionally (reproduced: a measured smoke entry without a manifest FAILs with covergroups_exist=False), and Section 7 and the testlist Policies comment describe it that way. The diff edited exactly this sentence and kept the stale trailing clause. - Drop "once the first covergroup exists" from the Section 3 sentence, or reword to "on the named tiers at merge time, and on every measured tier once the first covergroup exists".

[Low][dv/auto_dv/evidence/gen_critic_response_flow.md:508] CM23-L-1 says the promotion diff "is now 47/47 lines". `git diff --numstat 3e6f1b2~1..HEAD -- gen_testlist.yaml` is 50 added / 49 removed (99 changed lines); 47/47 omits the Policies comment block (2 removed / 3 added). The substantive claim (no changed line outside tier / measured / fcov_expectation_file / header) is correct. - Correct the count to 49-/50+ or state that the comment lines are excluded.

[Info][dv/auto_dv/flow/gen_flow_util.py:440] The "refused line without a stale suffix" case builds the refused entry with `stale_cause=None`, so the `"first collected" not in l_ref` assertion passes trivially and does not exercise the `if refuse / elif stale_cause` exclusion the label claims. The combination is unreachable from red_signature_check, so this is a fixture weakness, not a defect. - Set `stale_cause=C.RED_STALE_TEXT.format(task="T-1")` on the l_ref fixture so the assertion proves the guard.

Final verdict: APPROVE-WITH-CHANGES
