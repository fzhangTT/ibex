# Cross-model review - committed diff e6ed6d8c..7fb1aeb8

**Reviewer:** claude CLI 2.1.261 (Claude Code); run-reported model: claude-fable-5-1,claude-haiku-4-5-20251001; requested effort: high (the CLI does not report the effective setting); fresh session 72393d13-d717-4eac-a95b-643ab781c645; sandbox: bubblewrap, working directory = detached read-only checkout of commit 7fb1aeb8284f51dae41eec928c7cef57d593a8c2 (the live working tree is not read), filesystem read-only except this run's own output directory, scratch HOME (no access to the executing model's settings, instructions or memory), private PID namespace; network open for the model API, web tools disallowed by policy (fallback reviewer per owner ruling A-001)
**Codex unavailable because:** ERROR: You hit your spend cap set by the owner of your workspace. Ask an owner to increase your spend cap to continue.
**Wrapper:** dv/auto_dv/tools/gen_cross_review.sh blob 713e8c09 (the copy executed; equals the wrapper committed at the reviewed commit); reviewed commit 7fb1aeb8284f51dae41eec928c7cef57d593a8c2
**Date:** 2026-09-05
**Target:** committed diff e6ed6d8c..7fb1aeb8 (echo at raw line 1)

---

TARGET: e6ed6d8c375d6052f4136ea54259b387736eda6d..7fb1aeb8284f51dae41eec928c7cef57d593a8c2

Reviewer identity: Claude Fable 5.1 (claude-fable-5-1), fresh session, detached read-only checkout of 7fb1aeb. Scope: one commit, five files, nothing under rtl/.

**What I verified against the repository (not the commit message)**

- Retained constfile: the committed gz has mtime 0 and no FNAME field (header 1f8b 0800 0000 0000 02ff). It decompresses to sha256 d84de5fc...6160f6, 369118 bytes, 7051 lines. The out-tree source named in gen_build_manifest_gen_tb.yaml:58 has the same sha256. Running the tree's own gzip_n() over the decompressed text gives 13285 bytes, sha256 fbf29436..., identical to the committed file, so the retention is byte-reproducible through the pass.
- Join file: 21839 bytes, sha256 6431104931c6...e122, 189 Block rows, footer NO-OP 105 / EFFECTIVE 84 / 0 / 0 / 0, matching the README section 3 table.
- .el untouched: sha256 91dbc8c7ff9c...; 495 ANNOTATION_BEGIN lines; 1424 entries (3 Assert, 189 Block, 83 Branch, 667 Condition, 2 Fsm, 5 State, 463 Toggle, 12 Transition), equal to the README counts block. The ibex_if_stage Condition entries carry ids 25/25/37/40/43 as the README note 8 says.
- Self-test: ran `gen_excl_f1_pass.py --self-test` on a git-archive copy of 7fb1aeb with ci/env.sh sourced. All seven checks ok, "5 renumbered by this build, 3 class-D arms held out, 0 unexplained", PASS, exit 0. The entry-set diff shows exactly the three class-D Blocks (controller 149, LSU 142, multdiv 37) and the five if_stage Conditions renumbered 25/37/40/43 to 21/33/36/39. gen_precheck/ listing before and after the rehearsal is identical (the SF-1 claim holds). delta_self_test() passes standalone.
- Rubrics: ai-slop-comments PASS (added comments state why; no history or review ids in code); rtl-purity PASS (no rtl/ files); magic-numbers PASS (EC3_HELD_OUT_BLOCKS carries its reason; paths come from gen_flow_const); forces-and-hier-access PASS (no signal drives); assertion-integrity PASS (the "entry set identical" self-test check was replaced by a stricter classifier with three refusal cases; `same` is still computed and recorded). ASCII only in all five files; all new files carry the gen_ prefix.

**Findings**

[Medium][dv/auto_dv/excl/gen_excl_f1_pass.py:515] The review request states the finish step "is no longer hardwired to pass 14 and refuses a duplicate pass label" and that the README states pass-label rules; none of that is in this range. There is no pass-label check anywhere in dv/auto_dv/excl (`--pass-label` defaults to "<pass>" and is only printed), and retained artifacts are keyed by round tag only, so a second non-rehearsal pass on the same round dir silently overwrites gen_precheck_noop_join_<tag>.md, the urg log, the dashboard and the constfile gz (measured: two constfiles() calls with tag round_0 overwrite without complaint; harmless for the constfile because the bytes are identical, not guaranteed for the join whose sha256 the README cites). Across round dirs the tags differ, so no collision. - Either add the refusal (fail when a retained file for the tag exists with different bytes, or when the README pass table already carries the label) or correct the group-completion text so it does not claim a rule the code lacks.

[Low][dv/auto_dv/evidence/gen_critic_response_exclusions.md:21] The CR-FF-M1 row, the commit subject and the constfiles() docstring at gen_excl_f1_pass.py:344 say every one of the 495 annotations cites the constfile as EC-2. Measured on the committed .el: 270 of 495 ANNOTATION_BEGIN lines contain "EC-2 constfile" (272 cite EC-2 at all); the 217 cheriot-out-of-scope groups and six others cite no EC-2. The figure was carried over from the Critic's M-1 text, not measured. - State 270 of 495 in the row and make the docstring say "the annotations that cite EC-2 name it".

[Low][dv/auto_dv/excl/gen_exclusions_README.md:141] "the pass writes it gzip -n, so the same constfile always gives the same bytes" reads as the gzip CLI; the CLI `gzip -n` over the same text gives different bytes (sha256 99f7de65..., XFL differs). Only the pass's gzip_n() reproduces the committed file. The verification command given (gzip -dc | sha256sum) is correct. Same wording at :304. - Say "gzip with no name or mtime header, written by gzip_n() in gen_excl_f1_pass.py; reproduce through the helper".

[Low][dv/auto_dv/excl/gen_excl_f1_pass.py:97] entry_set_delta() classifies any missing Block on an unmeasured round as held out, not only the three class-D arms. Probe: one class-D arm wrongly emitted plus one unrelated Block dropped gives held_out 1, unexplained 0, so with two more arms held out the count is still 3 and the self-test passes. - Match held-out entries by the checksum/text of the three class-D arms (stable across builds per README note 8) or by the generator's HELD OUT report lines.

[Low][dv/auto_dv/excl/gen_excl_f1_pass.py:359] In a non-rehearsal pass a missing constfile source records copy None / retained None and the pass continues, so the retention this commit exists to guarantee can silently lapse if the out-tree is cleaned. - die() when `not a.dry_run` and the build manifest's constfile is absent.

Known Low (--work-dir outside the clone root, :492) confirmed still present and out of scope here.

Final verdict: APPROVE-WITH-CHANGES
