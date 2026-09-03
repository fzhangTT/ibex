# Cross-model review - committed diff 5ff88f63..3f6d6beb

**Reviewer:** claude CLI 2.1.259 (Claude Code); run-reported model: claude-fable-5-1; requested effort: high (the CLI does not report the effective setting); fresh session 57d64af7-cc32-4e4e-913d-3adb61483489; sandbox: bubblewrap read-only filesystem (writes into the clone fail with EROFS), web tools disallowed (fallback reviewer per owner ruling A-001)
**Codex unavailable because:** ERROR: You hit your spend cap set by the owner of your workspace. Ask an owner to increase your spend cap to continue.
**Date:** 2026-09-03
**Target:** committed diff 5ff88f63..3f6d6beb (echo at raw line 1)

---

TARGET: 5ff88f634ec797a4e7b29c3bab05ac09108bf5d0..3f6d6beb0de4051bf367fb373d76ba07e32cad98

**Reviewer identity:** Claude Fable 5.1 (model ID claude-fable-5-1), Claude Code CLI, fresh non-interactive session launched by the wrapper under review. Process tree observed from inside: `systemd(1) - bash - timeout - bwrap - claude -p --model fable --effort high --permission-mode dontAsk --allowedTools Read,Grep,Glob,Bash --disallowedTools Write,Edit,MultiEdit,NotebookEdit,WebFetch,WebSearch,Agent`. Fallback reviewer per owner ruling A-001.

**Scope reviewed:** one commit (3f6d6be): `dv/auto_dv/tools/gen_cross_review.sh` (+10/-3) and the new artifact `dv/auto_dv/reviews/2026-09-03-claude-diff-0d06da4c-5ff88f63.md` (the REQUEST-CHANGES review that motivated the change).

**Sandbox self-test from this session (owner request), exact outcomes**

- `Bash` `touch gen_probe_write_test.tmp` at the clone root: `touch: cannot touch 'gen_probe_write_test.tmp': Read-only file system`, rc=1. Nothing created.
- `Write` tool on `/localdev/fzhang/ws/ibex-challenge/gen_probe_write_tool.tmp`: `Error: No such tool available: Write. Write is disabled for this session, in subagents as well as here.` Nothing created.
- `Bash` `git config --local gen.probe 1`: `error: could not lock config file .git/config: Read-only file system`, rc=255. `.git` is protected too.
- `git status`, `git log -1`, `git rev-parse HEAD`, `git diff`, `git show`: all rc=0 with correct output. `Read` tool on `CLAUDE.md`: works.
- Mount table confirms `/` and `/localdev` are `ro,nosuid,nodev` in a private mount namespace (`/proc/self/ns/mnt` differs from PID 1); `/tmp` is a writable tmpfs (touch rc=0, ephemeral).
- **Writable inside the clone:** `dv/auto_dv/work/orchestrator/review_tmp/` (the `--bind "$XR_TMP"`), touch rc=0. Listing showed this run's `prompt.Kl82Rg`, `raw.ien2a2{,.err,.json}` and the in-flight private script copy `self.Qs69mS.sh`, and `test -w` reports that script copy WRITABLE.
- **Writable outside the clone:** `~/.claude/CLAUDE.md`, `~/.claude/settings.json`, `~/.claude/projects/` (memory dir), `~/.claude.json` all WRITABLE; `touch ~/.claude/<probe>` rc=0. `~/.claude/settings.json` carries `permissions.allow: ["Bash(*)"]`, so Bash is unrestricted, as the design accepts.
- **Network:** `curl https://example.com` returned HTTP 200 from Bash; DNS resolves; `/proc/self/ns/net` equals PID 1's (no `--unshare-net`). PID namespace is also shared with the host.
- Sibling clones under `/localdev/fzhang/ws/` (`ibex`, `ibex-cleanroom`, ...) are readable, same as under codex `--sandbox read-only`; policy-enforced only, parity with codex, not a regression.

**Verified as claimed**

- `bwrap` 0.4.0 present; missing-bwrap path fails loud (line 96).
- The codex wrapper uses `codex exec --sandbox read-only` (its line 75); the bubblewrap sandbox matches it for the property the policy cares about: the reviewer cannot modify the tracked clone or `.git`.
- Tool disallow list removes `Write`/`Edit`/`MultiEdit`/`NotebookEdit`/`WebFetch`/`WebSearch`/`Agent` from the session (the Write probe confirms the mechanism, not just the RO fs).
- The committed artifact carries CLI version, model, session ID, codex error, exact TARGET echo and one verdict line.

**Rubric results**

- ai-slop-comments: PASS (lines 92-95 explain why and state what stays writable; no history narration).
- rtl-purity: PASS (no `rtl/` change).
- magic-numbers: PASS (filters exclude `dv/**/*.sh`).
- forces-and-hier-access: PASS.
- assertion-integrity: PASS (no checker touched).

**Findings**

- [high][dv/auto_dv/tools/gen_cross_review.sh:97] The `--bind "$XR_TMP" "$XR_TMP"` makes the wrapper's own in-flight private copy (`review_tmp/self.*.sh`, verified writable from this session) editable by the sandboxed reviewer; the parent bash outside bwrap reads that file incrementally (the script's lines 12-13 rely on exactly this behaviour) and will execute whatever the reviewer writes past line 101 with full write access after `claude` exits, so the reviewer can forge `VERDICT`, skip the protocol checks, or modify the clone by proxy. The sandbox is therefore escapable by the party it sandboxes. - Drop the `$XR_TMP` bind entirely: nothing inside needs it, since stdin comes from `$PROMPT_F` and stdout/stderr go to `$RAW.*` through fds the parent opened before `exec`; additionally keep the relocated copy outside any rw-bound path (or `chmod a-w` it after the `cp` at line 15) so it stays read-only even if a future bind is added.
- [high][dv/auto_dv/tools/gen_cross_review.sh:97] `--bind "$HOME/.claude" "$HOME/.claude"` (and `~/.claude.json`) gives the reviewer write access to the executing model's `~/.claude/settings.json` (hooks run arbitrary commands in the orchestrator's sessions, outside the sandbox), `~/.claude/CLAUDE.md` (global instructions) and `~/.claude/projects/.../memory/` (auto-loaded into every future session for this clone): three instruction/code-injection channels into the executing model, none of which exist under the codex wrapper. - Run the reviewer under a per-run scratch `CLAUDE_CONFIG_DIR` (or bind an empty scratch dir over `$HOME/.claude` and a copy of `~/.claude.json` over `$HOME/.claude.json`) seeded only with the credentials the CLI needs; delete it after the run. This also removes the inherited `Bash(*)` allow rule from the reviewer's settings.
- [medium][dv/auto_dv/tools/gen_cross_review.sh:138] The header states "writes into the clone fail with EROFS" and "web tools disallowed"; both are overstatements: writes into `dv/auto_dv/work/orchestrator/review_tmp/` inside the clone succeed (rc=0 verified), and Bash reaches the network (`curl` HTTP 200) so the fence's no-network rule is policy-enforced only. - State the residuals literally: "filesystem read-only except review_tmp and $HOME/.claude; network reachable from Bash (fence policy-enforced); WebFetch/WebSearch tools disabled". Fix the wording after fixing findings 1 and 2 so it matches the mechanism.
- [medium][dv/auto_dv/tools/gen_cross_review.sh:95] "Network stays up for the model API" is a necessary residual, but the codex read-only sandbox denies network to the commands the agent runs while the API traffic flows from the unsandboxed codex process; the claude equivalent does not exist here, so "mirrors the codex wrapper's --sandbox read-only" (line 93-94) is not accurate on the network axis. - Either add `--unshare-net` with a loopback egress proxy that only permits the Anthropic API endpoint, or reword the comment and header to name network as an explicit, accepted gap relative to codex.
- [low][dv/auto_dv/tools/gen_cross_review.sh:97] No `--unshare-pid`: the reviewer shares the host PID namespace and can signal the orchestrator's processes (e.g., `kill` the parent `timeout`/`bash`). - Add `--unshare-pid` (bwrap then provides `--proc /proc` inside the new namespace) unless the CLI needs host PIDs.
- [low][dv/auto_dv/tools/gen_cross_review.sh:100] `--disallowedTools` omits `Workflow`, which spawns subagents; it is available in this session while `Agent` is not. Impact is bounded by the sandbox but the intent (single reviewer, no delegation) is not fully expressed. - Add `Workflow` to the disallow list.
- [low][dv/auto_dv/tools/gen_cross_review.sh:89] Carry-over from the prior REQUEST-CHANGES artifact, NOT ADDRESSED in this diff: line 89 duplicates line 78 (`XR_TMP=...; mkdir -p`), line 40 `exec bash "$WRAP"` still bypasses the EXIT trap so `self.*.sh` leaks on the codex path, and line 146 `$ART.tmp` + `mv` is still non-atomic across concurrent runs. Findings 1 and 3 of that artifact are ADDRESSED (OS sandbox added, header reworded); finding 2 is moot now that `Bash` is unrestricted and the RO filesystem is the control. - Fold the three lows into the next wrapper change.

The change delivers the property the previous review demanded: from inside this session, neither Bash nor the Write tool can touch the tracked clone or `.git`, and git/Read work. It does not yet match the codex read-only contract: the sandboxed reviewer can rewrite the wrapper's own running script through the rw-bound temp directory and can plant hooks, global instructions and memories in the executing model's `~/.claude`, both of which execute outside the sandbox. Both holes have one-line-scale fixes (drop the temp bind; use a scratch config dir).

Final verdict: REQUEST-CHANGES
