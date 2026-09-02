# Agent Teams — offline reference (from code.claude.com/docs/en/agent-teams, fetched 2026-09-02, v2.1.178+ behavior)

Experimental. Enabled in this repo via `.claude/settings.json` → `env.CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS = "1"`.

## Essentials
- One session = team lead; teammates are full independent Claude Code sessions with own context windows; shared task list + mailboxes; teammates message each other directly.
- Spawn: ask in natural language; a NAMED subagent (Agent tool with `name`) launches as a teammate while teams are enabled — teams can form even without asking. Disable with the env var set to "0" (project settings override shell).
- Non-interactive (`-p`)/SDK sessions never spawn teammates (named subagents run as ordinary subagents).
- Model per teammate: spawn-prompt name > subagent-definition `model` > CLAUDE_CODE_SUBAGENT_MODEL > lead's model. Teammates inherit the lead's effort level. Permission mode inherits from the lead at spawn; prompts bubble to the lead's session.
- Subagent definitions (.claude/agents/*.md) are reusable as teammate roles: `tools` enforced (+SendMessage/Task tools for in-process), `model` applies, body appended to system prompt (in-process) or replaces it (split-pane); `skills` field NOT applied (teammates load project/user skills); `mcpServers` only for split-pane.
- Display: default in-process (agent panel: arrows select, Enter view/message, x stop, Ctrl+T task list); `teammateMode: "auto"|"tmux"|"iterm2"` for split panes (tmux available on this site).
- Tasks: shared list, three states, dependencies auto-unblock, file-locked claiming; lead assigns or teammates self-claim.
- Quality gates: hooks TeammateIdle / TaskCreated / TaskCompleted (exit 2 = block + feedback) — candidate mechanism for enforcing our review gates mechanically.
- Storage: ~/.claude/teams/{session-derived-name}/ (config, inboxes; removed at session end) and ~/.claude/tasks/{name}/ (persists). Don't hand-edit config.
- Messaging trust rules: receiving agents are told messages come from another session; no permission laundering; auto-mode classifier reviews inter-agent messages.

## Limitations (current)
- /resume does not restore in-process teammates (lead may message ghosts — respawn).
- Task status can lag; nudge or update manually.
- One team per session; no nested teams (teammates cannot spawn teammates); lead is fixed.
- In-process teammates cannot run background subagents (foreground only); background:true errors.
- Split panes need tmux or iTerm2.

## Best practices (doc's)
- 3-5 teammates; 5-6 tasks per teammate; self-contained deliverables; avoid same-file edits; give spawn prompts full task context (no history inheritance); start with research/review shapes; monitor and steer; lead may need "wait for teammates" or "keep going" nudges.

## Relevance to this repo (controller notes, 2026-09-02)
- Our SDD loops used background subagents + SendMessage; teams add the shared task list + direct teammate-to-teammate messaging — a fit for the WS8+ generation/execution phase (e.g. testplan-writer, test-generator, evaluator as roles) and for parallel review seats.
- CAUTION: with teams enabled, our named implementer dispatches (ws2-impl-*, etc.) become TEAMMATES, which cannot run background subagents and whose idle behavior differs — the SDD controller pattern (background + watchdogs) may need adaptation, or spawn UNNAMED subagents for the old behavior. Evaluate next session before relying on it mid-loop.
