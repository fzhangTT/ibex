---
name: add-skill-or-agent
description: Adding or editing a .claude/skills/<name>/SKILL.md (or .claude/agents/<name>.md) so the cross-model validator stays green.
triggers:
  - "add a skill"
  - "new skill"
  - "add an agent"
  - "SKILL.md"
edges:
  - target: context/conventions.md
    condition: for the skill-naming convention and the validator contract
grounds_to: []
last_updated: 2026-09-02
mex:
  id: mx_01M1JCXQBX7GGV9K9JMB8ZGAC8
  type: pattern
  status: promoted
  revision: 2
  title: add-skill-or-agent
  relations:
    - type: related_to
      target: mx_01M1JCXQ9BS63RWRR6ZXZK0EVJ
      note: for the skill-naming convention and the validator contract
---

# Add a skill or agent

## Context
Skills live in `.claude/skills/<name>/SKILL.md`; codex discovers the same
files through the `.agents/skills/shared` symlink (must resolve to
`../../.claude/skills`). Both are checked by `.codex/compat/validator.py`.

## Steps
1. Create `.claude/skills/<name>/SKILL.md` with YAML frontmatter: `name:
   <name>` (must equal the directory name exactly) and a non-empty
   `description:`.
2. Write the skill body; keep it model-neutral if it is meant to run under
   both Claude and codex.
3. If the skill embeds the TRUST-TRIAD-CANONICAL block (mutation-check,
   fcov-expectation, and similar), copy it byte-identical from
   `docs/dv/dv_principles.md` between the `<!-- TRUST-TRIAD-CANONICAL-BEGIN
   -->`/`-END-->` markers — the validator diffs every embedding against that
   canonical copy.
4. Add the skill's name to the Skills index in `CLAUDE.md` (`## Skills
   index`).

## Gotchas
- A skill whose frontmatter `name:` does not match its directory fails the
  validator with no partial credit.
- Do not duplicate more than 120 characters of prose between `CLAUDE.md` and
  `AGENTS.md` outside the Critical Invariants block — the validator flags any
  such run.

## Verify
- [ ] `source ci/env.sh` then
      `python3 .codex/compat/validator.py` prints `VALIDATOR: PASS`.
- [ ] The new skill appears in `CLAUDE.md`'s `## Skills index`.
- [ ] Any TRUST-TRIAD block embedded is byte-identical to
      `docs/dv/dv_principles.md`'s canonical copy.

## Debug
If the validator fails on `CRITICAL-INVARIANTS blocks differ`, the edit
touched `AGENTS.md`'s mirrored block instead of (or in addition to)
`CLAUDE.md`'s — the two must stay byte-identical, edit `CLAUDE.md` and
re-mirror.

## Update Scaffold
- [ ] Update `.mex/ROUTER.md` "Current Project State" if what's working/not
      built has changed
- [ ] Update `.mex/context/conventions.md` if the skill introduces a new
      convention
- [ ] If this is a new task type without a pattern, create one in
      `.mex/patterns/` and add it to `INDEX.md`
