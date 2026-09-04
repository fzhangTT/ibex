# Cross-model review - committed diff 12411bea..b92bfbe3

**Reviewer:** claude CLI 2.1.260 (Claude Code); run-reported model: claude-fable-5-1,claude-haiku-4-5-20251001; requested effort: high (the CLI does not report the effective setting); fresh session af3f1988-03bc-441c-9542-d3af540a720f; sandbox: bubblewrap, working directory = detached read-only checkout of commit b92bfbe3cffa9aeb0ce096660c68339fd615052f (the live working tree is not read), filesystem read-only except this run's own output directory, scratch HOME (no access to the executing model's settings, instructions or memory), private PID namespace; network open for the model API, web tools disallowed by policy (fallback reviewer per owner ruling A-001)
**Codex unavailable because:** ERROR: You hit your spend cap set by the owner of your workspace. Ask an owner to increase your spend cap to continue.
**Wrapper:** dv/auto_dv/tools/gen_cross_review.sh blob 713e8c09 (the copy executed; equals the wrapper committed at the reviewed commit); reviewed commit b92bfbe3cffa9aeb0ce096660c68339fd615052f
**Date:** 2026-09-04
**Target:** committed diff 12411bea..b92bfbe3 (echo at raw line 1)

---

TARGET: 12411bea6a9ea84dae992e2a6cb7fc2423cfc3c3..b92bfbe3cffa9aeb0ce096660c68339fd615052f

Reviewer identity: Claude (claude-fable-5-1, Fable 5.1), fresh session, detached read-only checkout of b92bfbe; codex substitute per CLAUDE.md preference clause. Scope: the one commit b92bfbe, seven files, 268 insertions, 11 deletions.

**What I verified myself (not from the author's statement)**

- Testlist. Loaded the merged file: 94 tests, the nine new names present, each tier `check`, `measured: false`, `fcov_expectation_file: null`, no red fixture key, every plusarg a string, every program path an existing directed `.S`. No measured entry carries `+gen_knob_icache_ecc_err_rate` (count 0), so the LOG-077 load-time rule has nothing to refuse. The two-line single-quoted description of gen_ut_intg_store folds to one line with a space, as intended. Knob names and enum values (`long`, `storm`, `with_nmi`, `sparse`) are all members of the rendered knob table in gen_knobs.py. Both cocotb modules exist and read `ut_boot_retire` and `fetch_en_at_reset` via the PLUSARGS table; gen_ut_intg_store additionally requires `export_file`, which its entry carries. The nine entries match the retained landing-13 run headers under gen_tdd_logs/fcov and gen_tdd_logs/lockstep byte-for-byte on retire targets and regime knobs (40, 150, 150, 120, 800 x4, 30; long/long/long; storm+with_nmi+export; sparse), and every retained run prints its PASS marker with zero mismatches. The retire targets are reachable: retired counts in those runs are 40, 151, 150, 120, 880, 879, 1104, 884, 31.
- gen_ut_irq_nmi_long. The module hard-codes 200 and never reads `gen_ut_boot_retire` (only `fetch_en_at_reset`, `export_file` family reads), so the drop is inert to behaviour; tb-infra's CM149-I-2 row in gen_critic_response_fu2a.md:185 records the decision as stated.
- Tools. From a writable archive of b92bfbe with a fresh `git init`: util self-test rc 0, 140 ok, zero BAD; gen_run self-test PASS; gen_flow_const `--check` PASS; `--check-red-signatures` PASS on the merged list; `--dump-testlist` 94 entries; gen_covergroup_set.py rc 0 (57 covergroups, 4093 bins, 19 manifests, unknown []); gen_promotion_table.py rc 0 (20 entries). Manifest md5/bytes for both new logs match (bb0ad1b7…/1720, fd340bef…/2245). The diff is pure ASCII.
- Regex semantics. Re-executed both old and new patterns: `"1\n"` matched the old `$`-anchored regex (the hole) and fails `fullmatch` now; `"\n1"` returned `None` from the old `plusarg_name` and `row` from the new one; CR, CR LF, and the six sign forms were already 0 under the old regex, so the red's 2 BAD / 8 ok split is exactly what the author reports. `checker_knob_state` now returns `(set=True, on=False)` for both newline placements, matching the probe's u=0. The retained probe log shows all 12 non-canonical forms `set=1 u=0` and `+x=1` reading 1, on the same simv as the CM162 probe, with the forms loop appended.
- Other readers of `plusarg_name`. gen_run `effective_plusargs` (name-based operator replacement), gen_run `export_check`, gen_regress export-file collection, and the loader's plusarg validation. The only behaviour change is that a token with a newline before its value is now recognised as a named plusarg rather than unnamed; for the first three readers this is harmless or strictly more faithful to VCS. For the loader it is a slight acceptance widening, noted below.

**Rubrics**

- ai-slop-comments: PASS. Both added code comments state why (VCS prefix-match semantics, what the whole remainder is); case labels carrying CM tags are strings in the existing self-test convention, not comments.
- rtl-purity: PASS (no rtl/ files).
- magic-numbers: PASS (the retire/regime values live in the testlist, which is the authority).
- forces-and-hier-access: PASS (no drives).
- assertion-integrity: PASS. Ten refuse cases added, none removed or weakened; the dropped plusarg is unread by its module and disables nothing.

**Findings**

[Info][dv/auto_dv/flow/gen_flow_util.py:1512] The widened value group makes the loader accept a testlist plusarg whose value contains an embedded newline: I appended `+gen_chk_alert_minor=1\n` to an entry and `load_testlist` accepted it (the old `(=.*)?$` already accepted a trailing LF, so this is a small widening of an existing gap, not a new class). The gate reads it correctly as set-with-0, so no hole, but no author ever intends whitespace inside a testlist token. - Consider a loader-side refusal of any whitespace inside a plusarg token (`re.search(r"\s", pa)`), keeping the VCS-faithful reader for operator argv as is.

[Info][dv/auto_dv/flow/gen_flow_util.py:1519] `plusarg_enabled` still calls `.strip()` on the value, so `+gen_chk_sva_b8=1\n` and `+gen_rvfi_trace=1\n` read on in the flow while VCS reads 0. Both users (gen_run.py:202 debug-only refusal, :206 and util :1398 the B8 probe refusal) sit on the over-refusal side, so this is not a gate hole and is pre-existing, but Section 2's "VCS converts no whitespace" now describes only the checker-knob reader. - Either route `plusarg_enabled` through the same decimal rule or add one sentence to Section 2 scoping the whitespace claim to `checker_knob_state`.

[Info][dv/auto_dv/evidence/gen_critic_response_flow.md:930] The staging file the TL-L13 row cites (work/tb-infra/gen_l13_testlist_entries.yaml, sha256 c48dbf8c…) is not in the tree, so the "verbatim from staging" claim is unverifiable from the commit alone. I verified the nine entries instead against the retained landing-13 run headers, which agree on every plusarg; no action needed beyond noting the proof rests on those headers, not the digest.

Final verdict: APPROVE-WITH-CHANGES
