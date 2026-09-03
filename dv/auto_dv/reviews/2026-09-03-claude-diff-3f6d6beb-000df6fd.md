# Cross-model review - committed diff 3f6d6beb..000df6fd

**Reviewer:** claude CLI 2.1.259 (Claude Code); run-reported model: claude-fable-5-1,claude-haiku-4-5-20251001; requested effort: high (the CLI does not report the effective setting); fresh session 87a0812b-dbb6-4ff4-b2dd-d5cb6b108270; sandbox: bubblewrap, filesystem read-only except this run's own output directory, scratch HOME (no access to the executing model's settings, instructions or memory), private PID namespace; network open for the model API, web tools disallowed by policy (fallback reviewer per owner ruling A-001)
**Codex unavailable because:** ERROR: You hit your spend cap set by the owner of your workspace. Ask an owner to increase your spend cap to continue.
**Date:** 2026-09-03
**Target:** committed diff 3f6d6beb..000df6fd (echo at raw line 1)

---

TARGET: 3f6d6beb0de4051bf367fb373d76ba07e32cad98..000df6fd0cd27a592416b9687309946dd990d610

**Reviewer identity:** Claude Fable 5.1 (model ID claude-fable-5-1), Claude Code CLI 2.1.259, fresh non-interactive session launched by the wrapper under review (session 87a0812b-dbb6-4ff4-b2dd-d5cb6b108270). Process tree seen from inside: `bwrap(1) - claude(2) -p --model fable --effort high --permission-mode dontAsk --allowedTools Read,Grep,Glob,Bash --disallowedTools Write,Edit,MultiEdit,NotebookEdit,WebFetch,WebSearch,Agent,Workflow`. Fallback reviewer per owner ruling A-001.

**Scope reviewed:** one commit (000df6f): `dv/auto_dv/tools/gen_cross_review.sh` (+21/-15) and the new artifact `dv/auto_dv/reviews/2026-09-03-claude-diff-5ff88f63-3f6d6beb.md` (the REQUEST-CHANGES review that motivated the change). Working tree at HEAD 000df6f has no local change to the script.

**Sandbox self-test from this session (owner request), exact outcomes**

- `touch` at the clone root: `touch: cannot touch '/localdev/fzhang/ws/ibex-challenge/.probe_rw_288': Read-only file system`, rc=1. `/`, `/localdev`, `/home` all mounted `ro,nosuid,nodev` in the private mount namespace.
- `$HOME/.claude/settings.json`: does not exist. `$HOME/.claude/CLAUDE.md`: does not exist. `$HOME` is the scratch directory bound over `/home/fzhang` (mount table: `.../review_tmp/run.QWUjbv/home` on `/home/fzhang`, rw); the real `~/.claude` is not reachable by any path I could find (`/proj_soc/user_dev/fzhang/home-storage/.claude` absent; no other mount of the real home).
- `$HOME/.claude/projects/-localdev-fzhang-ws-ibex-challenge/memory`: exists and is writable, but it is the scratch copy created by this session (contains only this run's 287 KB transcript and an empty `memory/`); it is destroyed with the run directory, so nothing reaches the executing model's memory.
- In-flight script copy `dv/auto_dv/work/orchestrator/review_self/self.ubvo1n.sh`: `test -w` false; append attempt: `Read-only file system`. Not writable.
- `ps -p 1`: PID 1 is `bwrap`; 10 processes visible, all sandbox-internal (claude, three project MCP servers from `.mcp.json`, my shell). No host processes. Private PID namespace confirmed.
- Network: residual, reachable. DNS resolved `api.anthropic.com`; a bare TCP connect to 8.8.8.8:53 succeeded; host routes and interfaces are visible. Nothing was fetched.
- Still writable inside the clone tree: this run's directory `dv/auto_dv/work/orchestrator/review_tmp/run.QWUjbv/` (touch and unlink rc=0), including `prompt.txt`, `raw.json`, `raw.err` (all `test -w` true; `/proc/2/fd/1` -> `raw.json`). The directory is git-ignored (`dv/auto_dv/.gitignore:4 work/`).
- Copied into the scratch HOME: `.claude.json` (mode 644, carries user-scope `mcpServers: atlassian, glean-gleen`) and `.credentials.json` (mode 600, keys `claudeAiOauth`, `mcpOAuth` with atlassian and glean entries). Those two MCP servers plus the three project servers are loaded in this session; I did not exercise any of them.
- Environment is inherited wholesale from the orchestrator (`CLAUDECODE=1`, `SSH_AUTH_SOCK`, `REVIEW_FOCUS`, PATH). No API-key or token-named variables present.

**Prior artifact findings (dv/auto_dv/reviews/2026-09-03-claude-diff-5ff88f63-3f6d6beb.md)**

1. [high] writable in-flight script copy via the `$XR_TMP` bind — **ADDRESSED.** Line 15 relocates the copy to `review_self/`, outside every rw bind; verified EROFS on append. The recommended removal of the `$XR_TMP` bind itself was not applied (line 103 still binds it); residual carried as new finding 3 below.
2. [high] `~/.claude` and `~/.claude.json` bound writable — **ADDRESSED.** Lines 98-100, 103 bind a per-run scratch HOME seeded with credentials and `.claude.json` only; verified settings.json/CLAUDE.md absent and real home masked. Residual: the copy carries user-scope MCP servers and their OAuth (new finding 4).
3. [medium] header overstates the sandbox — **ADDRESSED.** Line 144 now states literally: read-only except the run's output directory, scratch HOME, private PID namespace, network open, web tools disallowed by policy. Matches every probe above.
4. [medium] "mirrors codex" on the network axis — **ADDRESSED** by the reword option: lines 92-93 name network as "a residual the codex sandbox does not have"; the "mirrors" claim is gone. No egress proxy (accepted alternative).
5. [low] no `--unshare-pid` — **ADDRESSED.** Line 103 adds it; PID 1 is bwrap from inside.
6. [low] `Workflow` not disallowed — **ADDRESSED.** Line 106 lists it; confirmed in the live process arguments.
7. [low] carry-overs: duplicate `XR_TMP` — **ADDRESSED** (line 89 is now `RAW="$XR_TMP/raw"`); codex-path self-copy leak — **ADDRESSED** (line 40 removes the copy before `exec`); `$ART.tmp`+`mv` non-atomic across concurrent runs — **NOT ADDRESSED** (line 152 unchanged, `ART` chosen at line 77 up to an hour before the write).

**Verified as claimed in the delta**

- `mktemp -d` per run (line 78) gives each run its own 0700 directory; `rm -rf "$XR_TMP"` (line 153) replaces the per-file cleanup.
- `CLAUDE_BIN` resolves to `/home/fzhang/.local/share/claude/versions/2.1.259`, reachable inside via the `--ro-bind "$HOME/.local"` (line 104); a missing CLI fails loud (line 102).
- `[ -f ... ] && cp` lines 99-100, 104 are safe under `set -e` (non-final commands in an AND-list).
- The committed artifact carries CLI version, model, session ID, codex spend-cap error, exact TARGET echo and one verdict line, and its self-test claims match the mechanism at 3f6d6be.

**Rubric results**

- ai-slop-comments: PASS (`dv/**/*.sh` outside filters; the added comments at lines 91-93, 95-97, 101 explain why and name residuals, no history narration).
- rtl-purity: PASS (no `rtl/` change).
- magic-numbers: PASS (`dv/**/*.sh` outside filters; nothing hand-encoded).
- forces-and-hier-access: PASS (no SV/py).
- assertion-integrity: PASS (no checker touched).

**Findings**

- [medium][dv/auto_dv/tools/gen_cross_review.sh:100] The live OAuth copy `home/.claude/.credentials.json` (and any token the CLI refreshes into it) is removed only on the success path (line 153); every protocol-error, timeout and `set -e` exit deliberately keeps `$XR_TMP` ("raw kept at"), so credentials persist under the clone's work tree on shared storage. Verified the file exists at that path during this run. - Add `rm -rf "$RUN_HOME"` to the EXIT trap (line 18) so raw.* is retained for debugging but the scratch HOME never outlives the run.
- [medium][dv/auto_dv/tools/gen_cross_review.sh:153] `rm -rf "$XR_TMP"` deletes the reviewer's session transcript (`home/.claude/projects/<slug>/<SESSION>.jsonl`, 287 KB present now); the artifact header cites a session ID that no longer resolves to anything, an auditability regression from v1 where the transcript survived in the real HOME. - Copy the transcript into an ignored retained directory (e.g. `work/orchestrator/review_logs/<SESSION>.jsonl`) before the `rm -rf`, and mention that path in the header.
- [medium][dv/auto_dv/tools/gen_cross_review.sh:103] `--bind "$XR_TMP" "$XR_TMP"` is still present although nothing inside needs it (stdin/stdout/stderr fds are opened by the parent before `bwrap`; `RUN_HOME` has its own bind). The run directory is writable and unlinkable from inside (verified), so the reviewer can `rm raw.json` and recreate it by path; the parent then parses a reviewer-authored file at line 110-121 (forged `modelUsage`, `session_id`, `is_error`), defeating the identity checks that exist precisely to not trust the sandboxed party. - Drop the bind, as the prior finding 1 recommended.
- [low][dv/auto_dv/tools/gen_cross_review.sh:99] The copied `.claude.json` carries the user-scope MCP servers (atlassian, glean-gleen) and line 100 their OAuth grants (`mcpOAuth`), so the reviewer session loads external services with write-capable tools (Jira/Confluence create/update) and enterprise search; the comment at line 95-97 says only "credentials and account state". Gating is the dontAsk permission layer only. - Strip `mcpServers` from the copy (python one-liner) and pass `--strict-mcp-config` (optionally `--mcp-config .mcp.json` if the project servers are wanted for RTL review), or use `--tools` to pin the built-in tool set instead of a disallow list.
- [low][dv/auto_dv/tools/gen_cross_review.sh:152] Carry-over NOT ADDRESSED: `$ART.tmp` + `mv` with `ART` chosen at line 77 is not safe against two concurrent runs of the same target on the same day. - Reserve the artifact name atomically (e.g. `set -o noclobber; : >"$ART"`) at line 77.
- [low][dv/auto_dv/tools/gen_cross_review.sh:122] `CLI_VER` is taken from PATH `claude` while the sandboxed run executes `$CLAUDE_BIN`; the two can diverge after an update mid-run and the header would misreport the version. - Use `"$CLAUDE_BIN" --version`.
- [low][dv/auto_dv/tools/gen_cross_review.sh:100] If the CLI rotates the OAuth refresh token during a review, the rotation lands in the throwaway copy and is discarded; whether that invalidates the orchestrator's own credentials is not verifiable from inside the sandbox. - Check the executing session's login still works after one wrapper run, and document the outcome next to line 95.

The two high findings that drove REQUEST-CHANGES are closed by mechanism, not by wording: from inside this session the clone, `.git`, the in-flight script copy and the executing model's `~/.claude` are all unreachable for writing, the PID namespace is private, and the header describes exactly what I observed. The remaining items are cleanup and hardening on the same design (credentials lifetime, transcript retention, the unnecessary run-directory bind, MCP inheritance) and none re-opens an execution or instruction channel into the executing model.

Final verdict: APPROVE-WITH-CHANGES
