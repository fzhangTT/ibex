# Codex compatibility wrapper

Read and follow `./CLAUDE.md`; it is the canonical repository instruction source. Preserve the
intent, ordering, safety gates, and expected outputs of Claude-oriented instructions and skills.

Translate client mechanics at execution time:

- Shared skills live at `.agents/skills/shared/<name>/SKILL.md` (a symlink to `.claude/skills`);
  `/skill-name` means follow the matching shared skill.
- `$ARGUMENTS` means the user's arguments for the selected skill.
- A Claude user-question tool means ask the same concise question through the interaction
  mechanism currently available; if none, state the assumption you proceeded with in your output.
- Background or delegated work means use the available codex execution model only when
  higher-priority instructions and the user's authorization allow it; otherwise do the work inline.
- A Claude-specific MCP tool name means select the semantically equivalent tool from the
  configured MCP server; do not change the workflow's requested action.

Do not copy general guidance from `CLAUDE.md` into this file. The one sanctioned duplication is
the Critical Invariants block below, mirrored verbatim and hash-checked by
`.codex/compat/validator.py`.

## Critical invariants

<!-- CRITICAL-INVARIANTS-BEGIN -->
1. The executing model never self-approves: plans get a pre-execution review and diffs get a
   post-execution review by the other model; a `REQUEST-CHANGES` verdict blocks progress until a
   recorded re-review reaches `APPROVE`/`APPROVE-WITH-CHANGES`.
2. Knowledge-fence: generation sessions must not read fenced DV collateral. Fence rules live in
   `docs/dv/FENCE.md` once WS7 lands; until a fence authority exists, generation sessions are
   NOT permitted at all (fail closed), and infra sessions never paste fenced content into
   allowed files.
<!-- CRITICAL-INVARIANTS-END -->
