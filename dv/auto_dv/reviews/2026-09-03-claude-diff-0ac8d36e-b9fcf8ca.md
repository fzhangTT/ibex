# Cross-model review - committed diff 0ac8d36e..b9fcf8ca

**Reviewer:** claude CLI 2.1.259 (Claude Code); run-reported model: claude-fable-5-1,claude-haiku-4-5-20251001; requested effort: high (the CLI does not report the effective setting); fresh session fc8db3b7-e915-4a50-8722-f82fb9d3db53; sandbox: bubblewrap, working directory = detached read-only checkout of commit b9fcf8ca41b23ff0921f8c90037f73a044a048c3 (the live working tree is not read), filesystem read-only except this run's own output directory, scratch HOME (no access to the executing model's settings, instructions or memory), private PID namespace; network open for the model API, web tools disallowed by policy (fallback reviewer per owner ruling A-001)
**Codex unavailable because:** ERROR: You hit your spend cap set by the owner of your workspace. Ask an owner to increase your spend cap to continue.
**Wrapper:** dv/auto_dv/tools/gen_cross_review.sh blob 713e8c09 (the copy executed; equals the wrapper committed at the reviewed commit); reviewed commit b9fcf8ca41b23ff0921f8c90037f73a044a048c3
**Date:** 2026-09-03
**Target:** committed diff 0ac8d36e..b9fcf8ca (echo at raw line 1)

---

TARGET: 0ac8d36ef8b08a5d4be9ac2d3b94d97877f7deca..b9fcf8ca41b23ff0921f8c90037f73a044a048c3

Scope: one commit (b9fcf8c), one file, `dv/auto_dv/flow/gen_mirror.py` (+9/-5), inside `self_test()`. The change wraps the "head trees are keyed by sha under one family dir" case in an `if site_mirror_root() is None` guard that prints a `SELF-TEST skip` line instead of calling `head_mirror_root()`.

Verification performed (read-only checkout untouched; work done in a throwaway clone of the reviewed commit under /tmp, since deleted):

- Before the change, `head_mirror_root()` (gen_mirror.py:104-109) calls `U.die(...)` → `sys.exit(1)` when `site_mirror_root()` is None, so in a clean checkout the self-test aborted mid-run with exit 1 rather than reporting. The commit message's premise is correct.
- `C.SITE_YAML` resolves to `dv/auto_dv/work/runtime/gen_site.yaml`, and `git check-ignore` confirms it is ignored via `dv/auto_dv/.gitignore:4` (`work/`). A clean checkout indeed has no site pointer; this reviewed checkout has no `dv/auto_dv/work` at all.
- Ran `gen_mirror.py --self-test` (python 3.12, `PYTHONPATH=` cleared) in the clean throwaway clone: all other cases print `ok`, the guarded case prints `SELF-TEST skip ... (.../gen_site.yaml absent in this checkout)`, final `SELF-TEST: PASS`, exit 0.
- Re-ran with a synthetic `gen_site.yaml` (`mirror_root:` pointing at a temp path): the guarded case executes and reports `ok  head trees are keyed by sha under one family dir: site_mirror_head/aaaaaaaaaaaa vs bbbbbbbbbbbb`, exit 0. The check is not dead code; it still bites when the site pointer exists.
- The second half of the removed comment's claim ("a pinned status never consults the moving HEAD") is still covered unconditionally by the `status(tiny, pinned_head=...)` case that follows (gen_mirror.py:448-451), so no assertion coverage is lost by the skip.

Rubric results:

- ai-slop-comments: PASS. The added two-line comment states the invariant and the why of the skip (site pointer git-ignored). No history narration, no restatement.
- rtl-purity: PASS (no `rtl/` files in range).
- magic-numbers: PASS. Uses `C.SITE_YAML` and `C.HEAD_MIRROR_SUFFIX`; no hand-encoded paths or values.
- forces-and-hier-access: PASS (no SV/cocotb drives).
- assertion-integrity: PASS. A self-test check is made conditional, but only on a precondition without which the function under test cannot run at all (it would `die`), the skip is announced on stdout with its reason rather than silently counted as ok, and the guarded assertion is unchanged and still executes when the precondition holds (verified above).

Findings:

[low][dv/auto_dv/flow/gen_mirror.py:437] Skip message says "`gen_site.yaml` absent in this checkout", but `site_mirror_root()` (line 88-95) also returns None when the file exists yet has no `mirror_root:` line; in that case the message misdescribes the cause - consider wording it "no `mirror_root:` in {C.SITE_YAML} (file absent or key missing)". Cosmetic; does not affect exit status or correctness.

[low][dv/auto_dv/flow/gen_mirror.py:437] The `skip` marker is a third token form alongside `ok `/`BAD`, and the final `SELF-TEST: PASS` line does not count skips; a consumer grepping only the summary line cannot tell a full pass from a pass-with-skip. Optional: append a skipped count to the summary line. Not blocking; the skip is visible in the per-case output.

Final verdict: APPROVE
