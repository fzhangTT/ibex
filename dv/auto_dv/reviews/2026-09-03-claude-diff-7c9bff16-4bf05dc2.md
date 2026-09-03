# Cross-model review - committed diff 7c9bff16..4bf05dc2

**Reviewer:** claude CLI 2.1.259 (Claude Code); run-reported model: claude-fable-5-1,claude-haiku-4-5-20251001; requested effort: high (the CLI does not report the effective setting); fresh session 077c06db-141e-4eb2-9221-27ea79bb1ec3; sandbox: bubblewrap, working directory = detached read-only checkout of commit 4bf05dc2b796a47e8135bc779aeab832bc491a54 (the live working tree is not read), filesystem read-only except this run's own output directory, scratch HOME (no access to the executing model's settings, instructions or memory), private PID namespace; network open for the model API, web tools disallowed by policy (fallback reviewer per owner ruling A-001)
**Codex unavailable because:** 2026-09-03T15:40:42.035799Z ERROR codex_core::shell_snapshot: Shell snapshot validation failed: Snapshot command exited with status exit status: 2: /home/fzhang/.codex/shell_snapshots/01a067ed-d5ac-7101-9946-770ac10616ca.tmp-1788450035267937434: line 1266: syntax error near unexpected token `('
**Wrapper:** dv/auto_dv/tools/gen_cross_review.sh blob 713e8c09 (the copy executed; equals the wrapper committed at the reviewed commit); reviewed commit 4bf05dc2b796a47e8135bc779aeab832bc491a54
**Date:** 2026-09-03
**Target:** committed diff 7c9bff16..4bf05dc2 (echo at raw line 1)

---

TARGET: 7c9bff16604391de4b2467a925939721631bf987..4bf05dc2b796a47e8135bc779aeab832bc491a54

Reviewer: Claude Fable 5.1 (claude-fable-5-1), fresh session, read-only detached checkout of 4bf05dc; reasoning effort: default. Scope: one commit, one file, +4/-1 in dv/auto_dv/excl/gen_excl_select.py (load_config).

What I verified against the repository (not the author's claims):

- **One root.** `gen_flow_const.py:18,43,67` define REPO_ROOT from the file location, SOURCE_ROOT as GEN_DV_SOURCE_ROOT or REPO_ROOT, and CONFIG_SCRIPT as SOURCE_ROOT/util/ibex_config.py. The new line 572 derives the script as REPO_ROOT / (CONFIG_SCRIPT relative to SOURCE_ROOT), and line 574 keeps cwd=REPO_ROOT. Both now come from REPO_ROOT, which is also the root every other read in the selector uses (lines 523, 544, 560, 672, 878). CM16-I-1 (review 2026-09-03-claude-diff-5f530a87-356790d6.md line 40) is closed as recommended.
- **Relative path is the flow's, not re-typed.** No new literal appears; the relative path is computed from the same CONFIG_SCRIPT constant gen_build.py:31 uses. I confirmed with GEN_DV_SOURCE_ROOT=/tmp that CONFIG_SCRIPT becomes /tmp/util/ibex_config.py while the derived path still resolves to REPO_ROOT/util/ibex_config.py and exists, so the derivation is correct in head mode too and relative_to cannot raise (CONFIG_SCRIPT is defined as a child of SOURCE_ROOT).
- **Comment is intent-only.** No history narration, no code restatement. The claim "the selector never runs on a head tree" holds: the only invoker is dv/auto_dv/excl/gen_excl_f1_pass.py:128 (manual tool); gen_round.py mentions the selector only in a comment.
- **Runs from outside the clone root.** From cwd /tmp, `gen_excl_select.py --help` returned rc 0, which exercises the module-level load_config() call (line 580) before argparse.
- **Byte-identical regeneration.** From cwd /tmp/cm16_review I ran the selector on the round-0 dump named by the committed manifest (dv/auto_dv/evidence/gen_round_0_rebaseline/gen_regress_manifest.yaml, unmeasured.full_exclusions_dump under /proj_soc/user_dev/fzhang/ibex_dv_out/regress_round_0_rebaseline/cov_unmeasured/full_exclusions) with the three README-listed attempts logs. Output md5 9b642ef57393d8b3af8de9485a8f6f88, `cmp` against the committed dv/auto_dv/excl/gen_exclusions.el: identical. No behaviour change on the clone.
- **f1 self-test.** Not fully reproduced here: the review checkout is a read-only filesystem, so I had to pass --work-dir /tmp/..., and the driver then crashed at gen_excl_f1_pass.py:428 (`el.relative_to(ROOT)` on a work dir outside the clone). That crash is in a file outside this diff and is unrelated to the change; before it, iteration 1 reported "generator rc 0; strict load rc 0 UCAPI w/e 0/0", i.e. the reviewed load_config path worked under the driver from an outside cwd. The Orchestrator's claim (default work dir inside the clone) is consistent with this but I could not run it verbatim.
- Working tree clean after all runs (`git status --porcelain` empty).

Rubrics (all diff_only): ai-slop-comments PASS; magic-numbers PASS on the diff's new content (see low below on a retained literal); forces-and-hier-access PASS (no drives); rtl-purity N/A (no rtl/ files); assertion-integrity PASS (no assertion or checker added, removed, or weakened).

Findings:

[low][dv/auto_dv/excl/gen_excl_select.py:573] The changed invocation still re-types the configuration name "opentitan" while the flow's gen_build.py:31 takes it from C.BUILD_CONFIG (gen_flow_const.py:139); if BUILD_CONFIG ever changes, the selector's class-P parameter values and the build silently diverge, contrary to line 16's "no literals here" and the docstring's "never re-typed" - recommendation: pass C.BUILD_CONFIG (pre-existing, not part of CM16-I-1; a follow-up, not a block).

[info][dv/auto_dv/excl/gen_excl_f1_pass.py:428] Outside this diff: `--self-test --work-dir <outside clone>` raises ValueError at el.relative_to(ROOT), so the self-test cannot be rehearsed from a read-only checkout - recommendation: guard the join-file header with a fallback to the absolute path, so reviewers can reproduce the self-test without writing into the clone.

Final verdict: APPROVE
