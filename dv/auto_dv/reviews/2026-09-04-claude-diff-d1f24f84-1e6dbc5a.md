# Cross-model review - committed diff d1f24f84..1e6dbc5a

**Reviewer:** claude CLI 2.1.260 (Claude Code); run-reported model: claude-fable-5-1,claude-haiku-4-5-20251001; requested effort: high (the CLI does not report the effective setting); fresh session 8bf9f876-ac9d-40d7-bbdc-ad3e349d02d7; sandbox: bubblewrap, working directory = detached read-only checkout of commit 1e6dbc5aac4bdc76eb31566c0ca5c2e0994e5d2f (the live working tree is not read), filesystem read-only except this run's own output directory, scratch HOME (no access to the executing model's settings, instructions or memory), private PID namespace; network open for the model API, web tools disallowed by policy (fallback reviewer per owner ruling A-001)
**Codex unavailable because:** ERROR: You hit your spend cap set by the owner of your workspace. Ask an owner to increase your spend cap to continue.
**Wrapper:** dv/auto_dv/tools/gen_cross_review.sh blob 713e8c09 (the copy executed; equals the wrapper committed at the reviewed commit); reviewed commit 1e6dbc5aac4bdc76eb31566c0ca5c2e0994e5d2f
**Date:** 2026-09-04
**Target:** committed diff d1f24f84..1e6dbc5a (echo at raw line 1)

---

TARGET: d1f24f84d33b38168883136f0cfdca84a40f9b20..1e6dbc5aac4bdc76eb31566c0ca5c2e0994e5d2f

Reviewer identity: claude-fable-5-1 (Claude Code CLI), fresh session, default reasoning, read-only detached checkout of 1e6dbc5. Scope confirmed from `git log`/`git diff --stat`: one commit, two files (gen_critic_response_fu2a.md +20/-1, gen_trace_tagwrite_history.py +13/-5). No SV, RTL, knob, rendered, flow or plan file, so no build identity moves. Both files ASCII.

**What I verified myself**

- Tool compiles (`compile()` of the source; `py_compile` cannot write `__pycache__` on this read-only tree). In a temp landing root holding the manifest, the duplicate-copies artifact and the committed tag-write artifact: no argument → usage, rc 2; landing root alone → "the scratch root is required unless --from-artifact is given" + usage, rc 2; `-h` → usage, rc 2; `<root> --from-artifact` → rc 0, artifact byte-identical (24188 bytes, md5 a7702922e3b65efc56b340e6ee2b1348), manifest unchanged, "indices [26, 27], 322 of 1564 tag-write lines kept"; `<root> /nonexistent` → REFUSED pointing at the flag, rc 1.
- Self-check: appending one `index=30` tag-write line → "REFUSED: the retained artifact holds 1 tag-write lines outside the indices [26, 27] it names", rc 1. Appending an `index=260` line is also refused, so the trailing space in `index=%d ` blocks prefix collisions.
- Per-site attribution for CM185-L-1: 8ce613d (landing 17) touched the tool's header text (the `NOT retained` line), 9168e6b (landing 18) touched gen_tdd_step2b.md's 1564 site. The rewritten CM182-l-4 cell and self-correction text at line 274 name each site with the right landing. True.
- CR-18-L-1 both rows: old docstring read `<landing root> <scratch root> [--from-artifact]` (scratch required, flag optional), which is the defect the Critic named; both docstring and USAGE now read `(<scratch root> | --from-artifact)`; the old form appears zero times. The "all three tools" audit claim holds: the figures tool (usage `<landing root>`, reads argv[1], flag only `-h/--help`) and the identity gate (three positionals, reads argv[1..3], flag only `-h/--help`) each match their docstrings and code.
- CM185-L-2: same defect as CR-18-L-1, fixed. CM185-I-1: the filter is present at line 64 with a count-naming refusal at 65-66; output unchanged at the same md5.

**Rubrics** (Zone A set): ai-slop-comments PASS (the two added comments at lines 30 and 61-62 state why, not history); rtl-purity PASS (no rtl/); magic-numbers PASS (no new literals; indices still derived from the artifact); forces-and-hier-access PASS (n/a); assertion-integrity PASS (a check was added, none removed or weakened).

**Findings**

[low][dv/auto_dv/evidence/gen_critic_response_fu2a.md:285] The paragraph's premise "every defect in them across three reviews has been usage or text rather than behaviour" is false against rows on the same page: CM182-l-5 (line 275, no from-tree regeneration path) and CM185-I-1 (line 296, kept lines not re-filtered, taken in this very landing) are behaviour findings on this tool - either correct the sentence to what the rows show (usage/text defects plus two behaviour gaps) or drop the generalisation and keep only the audit statement, which is the part that is a record.

[low][dv/auto_dv/evidence/gen_critic_response_fu2a.md:296] "so a hand-edited or mis-generated artifact fails instead of regenerating quietly" over-states the check. It catches only tag-write lines outside the named indices. A hand-edit that deletes or alters a line at index 26 or 27 passes (keep equals raw by construction), and an extra index appended to the duplicate-copies artifact regenerates quietly with a rewritten header (verified: "Indices 26, 27, 30", 322 lines, new md5 822c172b164f4432c95eb7143841e8e8, rc 0) - narrow the claim to "an artifact holding tag-write lines outside the indices the duplicate-copies artifact names".

[low][dv/auto_dv/tools/gen_trace_tagwrite_history.py:31] The usage line presents the two modes as exclusive alternatives, but the code accepts `<root> <scratch> --from-artifact` and `<root> --from-artifact <extra>` and silently ignores the scratch root (both verified rc 0, artifact byte-identical). The row at line 282 says only that the flag "no longer needs" a positional, which is true, but the usage text does not describe the accepted superset, and the prior review's documented call form `<root> /nonexistent --from-artifact` still runs without being documented - either reject a scratch root given together with the flag through `_usage`, or say in the docstring that a scratch root is ignored with the flag. Also, line 25 tests `sys.argv[2:]` while line 45 tests all of `sys.argv`; compute one `FROM_ARTIFACT` before the argument check and use it in both places (behaviour is currently correct: `--from-artifact` as the first argument falls to the line-25 message, rc 2, not a traceback).

[info][dv/auto_dv/tools/gen_trace_tagwrite_history.py:66] The refusal says "the indices %s it names", where "it" is the retained artifact, but `idx` is read from the duplicate-copies artifact at line 50, not from the retained header; when the two disagree the message misattributes the source. Say "the indices %s the duplicate-copies artifact names". Cosmetic: "1 tag-write lines".

[info][dv/auto_dv/evidence/gen_critic_response_fu2a.md:266] The section heading still reads "answered by landing 17" while the CM182-l-4 row under it now says landings 17 and 18; the row is self-describing, so this is not false at any site, but "answered by landings 17 and 18" would make the heading true too.

Dispositions judged: CR-18-L-1 both rows true; CM185-L-1 true at both sites and correctly attributed; CM185-L-2 true; CM185-I-1 taken and working for the case it names, with the record wording over-broad as noted. The filter comment states intent (why the re-filter exists), not history. The "why these tools keep drawing rows" paragraph is a record statement in the right file, but its central factual claim is wrong as written.

Final verdict: APPROVE-WITH-CHANGES
