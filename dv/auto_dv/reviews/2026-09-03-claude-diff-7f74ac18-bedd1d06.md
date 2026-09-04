# Cross-model review - committed diff 7f74ac18..bedd1d06

**Reviewer:** claude CLI 2.1.260 (Claude Code); run-reported model: claude-fable-5-1,claude-haiku-4-5-20251001; requested effort: high (the CLI does not report the effective setting); fresh session 82838c24-9721-4256-8a57-98437ab6d8cb; sandbox: bubblewrap, working directory = detached read-only checkout of commit bedd1d0627ba656d05e4cb8569f8d2f92e15e670 (the live working tree is not read), filesystem read-only except this run's own output directory, scratch HOME (no access to the executing model's settings, instructions or memory), private PID namespace; network open for the model API, web tools disallowed by policy (fallback reviewer per owner ruling A-001)
**Codex unavailable because:** ERROR: You hit your spend cap set by the owner of your workspace. Ask an owner to increase your spend cap to continue.
**Wrapper:** dv/auto_dv/tools/gen_cross_review.sh blob 713e8c09 (the copy executed; equals the wrapper committed at the reviewed commit); reviewed commit bedd1d0627ba656d05e4cb8569f8d2f92e15e670
**Date:** 2026-09-03
**Target:** committed diff 7f74ac18..bedd1d06 (echo at raw line 1)

---

TARGET: 7f74ac18df4cf0e84d4dc213aeb51bb18ad98766..bedd1d0627ba656d05e4cb8569f8d2f92e15e670

Reviewer identity: Claude Fable 5.1 (claude-fable-5-1), fresh session, detached read-only checkout of bedd1d0; independent reviewer, not the author.

Scope confirmed: one commit, seven files, 67 insertions / 5 deletions. No RTL, no SV, no forces, no assertion changes. All added lines ASCII; the new file carries the gen_ prefix.

**What I verified myself**

- Testlist: `git diff --numstat 3320214 bedd1d0` on gen_testlist.yaml is exactly 3/3, the three fcov_expectation_file lines to null; the 7f74ac1 testlist equals 3320214's. The sibling gen_ut_lockstep_zcmp already carries null in tier check. The three descriptions still name the proof slices. The three evidence manifests remain tracked. The pin_off entry (line 1828) is unchanged and still names the group manifest.
- Loader on the 3320214 testlist: refused, rc 1, message `ERROR: ... test gen_ut_lockstep_zcmp_hz fcov_expectation_file dv/auto_dv/evidence/... is outside dv/auto_dv/fcov_expectations/ ...`. HEAD loader dumps 85 entries. `--check-red-signatures` PASS. `gen_flow_const.py --check` PASS. Both .py compile.
- Self-test on a writable git-archive of bedd1d0: the five CM153 cases print ok; the only BAD is build-input gate case 13 (no .git in an archive), identical to the retained red's disclosed unrelated BAD.
- Red discrimination: with the 13-line rule removed from the archive and nothing else changed, the three refuse cases print BAD and the two positive cases print ok. This matches the retained log. The red is discriminating.
- Retained log md5 d9b3f5d436f98fdeea13fb7342227d6c and 1142 bytes match the manifest row.
- gen_covergroup_set.py at 3320214 (line 50) does `sys.exit(... is not under ...)` on the first outside entry before writing; at HEAD (post-v3p) it tolerates and lists. Running the HEAD tool on the HEAD testlist completes: 57 covergroups, 19 manifests, the outside-the-home section reads None. The TL-L12 amendment and the CM153-Major row describe this sequence accurately.
- Rule scope vs validate_manifest (gen_fcov.py:79-83): the stem/test/entry equality is enforced only when `check_test` runs, which gen_run gates on fcov_check and a vdb, i.e. measured runs. Applying stem equality only to `measured` entries is consistent with the consumer; requiring it for unmeasured entries would refuse the committed pin_off entry accepted at c0d12f4. The default `t.get("measured", True)` matches the R-01, LOG-067 and LOG-077 rules directly above it.
- Exit path and message form: `die(f"{path}: test {t['name']} ...")` matches the LOG-067 (line 1338) and LOG-077 (line 1341) refusals and the P6 debug_only refusal (line 1433); same die(), same rc 1, ERROR prefix, message names the field.

**Rubrics**

- ai-slop-comments: PASS. The two added comments state intent; the `# CM153-L-1, the positive side:` form follows the file's existing `# LOG-077, the positive side:` convention.
- rtl-purity: PASS (no rtl/ files).
- magic-numbers: PASS. The literal manifest paths in the self-test are test-local fixture inputs; the rule itself derives the home from FCOV_EXPECT_DIR and the suffix from FCOV_MANIFEST_SUFFIX.
- forces-and-hier-access: PASS (no SV, no handle drives).
- assertion-integrity: PASS. Checks were added, none removed or weakened; no manifest bin list changed.

**Findings**

[Low][dv/auto_dv/flow/gen_flow_util.py:1351] The refusal message says the manifest home is "the only mirrored place a head-mode run reads", and the TL-L12 row says a head-mode measured run "would not have found the files". The consumer does not read from the mirror: `gen_fcov.manifest_path` (gen_fcov.py:72-74) resolves `C.REPO_ROOT / f`, and in head mode gen_regress re-executes the clone's own script path (gen_regress.py:469), so REPO_ROOT stays the clone while SOURCE_ROOT is the mirror. A head-mode run would have found the evidence manifests in the clone; the loader now checks existence under SOURCE_ROOT while the reader resolves against REPO_ROOT. The new rule is still correct on schema grounds, but the stated premise is not what the code does. - Reword the message and the TL-L12 sentence to the schema/home argument, and file a follow-on for gen_fcov.manifest_path to resolve via SOURCE_ROOT (outside this diff).

[Low][dv/auto_dv/flow/gen_testlist.yaml:25] The in-file schema header still reads `dv/auto_dv/fcov_expectations/<name>.fcov.yaml or null`, while the enforced rule (and gen_runtime_api.md Section 7) allows an unmeasured entry to name a group manifest in the home. The header is the schema line the prior review cited; it now disagrees with the loader. - Extend the header line: `<name>.fcov.yaml` required when measured; an unmeasured entry may name a group manifest in the home; null otherwise.

[Low][dv/auto_dv/evidence/gen_tdd_logs/flow/gen_cm153_fcov_home_red.log:3] The retained red log is width-truncated at 190 columns: two of the three BAD lines (lines 3 and 5) lose the `(message names 'fcov_expectation_file')` tail, and line 8 is cut mid-message. The BAD verdicts are still legible and the md5 matches the manifest, so the evidence stands, but it is not the self-test's actual output. - Re-retain the log without the column cut (and update the manifest row), or add one sentence to the manifest paragraph disclosing the truncation.

[Info][dv/auto_dv/flow/gen_flow_util.py:433] All three refuse cases use the same want token `fcov_expectation_file`, which every one of the three sub-rules prints, so the self-test cannot tell which sub-rule refused (e.g. the stem case would also pass if the outside-home check fired). - Use a sub-rule-specific token per case: `is outside`, `does not exist under`, `must be`.

[Info][dv/auto_dv/flow/gen_flow_util.py:472] The positive group-manifest case depends on the committed gen_test_pmc_ctrl.fcov.yaml existing under the home; a rename of that manifest would break this self-test for an unrelated reason. - Pick the manifest from a listing of the home or note the coupling in the label.

[Info][dv/auto_dv/evidence/gen_critic_response_flow.md:869] The prior review's Low asked for "file tracked"; the rule checks `is_file()` only. In head mode an untracked manifest is absent from the git-archive mirror and is refused as missing, so the gap is closed there; in worktree mode an untracked manifest loads. The CM153-L-1 row does not say the tracked check was left out. - One clause in the row disclosing the choice.

Final verdict: APPROVE-WITH-CHANGES
