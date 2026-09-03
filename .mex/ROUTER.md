---
name: router
description: Session bootstrap and navigation hub. Read at the start of every session before any task. Contains project state, routing table, and behavioural contract.
edges:
  - target: context/architecture.md
    condition: when working on system design, integrations, or understanding how components connect
  - target: context/stack.md
    condition: when working with specific technologies, libraries, or making tech decisions
  - target: context/conventions.md
    condition: when writing new code, reviewing code, or unsure about project patterns
  - target: context/decisions.md
    condition: when making architectural choices or understanding why something is built a certain way
  - target: context/setup.md
    condition: when setting up the dev environment or running the project for the first time
  - target: patterns/INDEX.md
    condition: when starting a task — check the pattern index for a matching pattern file
  - target: patterns/rtl-lint-clean-change.md
    condition: when making an RTL change under rtl/ that must stay lint-clean
  - target: patterns/add-skill-or-agent.md
    condition: when adding or editing a .claude/skills or .claude/agents file
  - target: patterns/mex-fence-aware-wiki-edit.md
    condition: when editing anything under .mex/ (context, patterns, ROUTER.md, AGENTS.md)
  - target: patterns/debug-env-and-mex-failures.md
    condition: when the module command, pip freeze, or a mex command fails
last_updated: 2026-09-02
---

# Session Bootstrap

If you haven't already read `AGENTS.md`, read it now — it contains the project identity, non-negotiables, and commands.

Then read this file fully before doing anything else in this session.

## Current Project State

**Working:**
- The Ibex RTL (`rtl/`) and its reference builds (`make build-all`,
  `lint-core-tracing`, `python-lint`).
- The agent-tooling layer: `CLAUDE.md`/`AGENTS.md`, `.claude/skills/`,
  cross-model review policy, `.codex/compat/validator.py`.
- This `.mex/` scaffold: a full-tree code graph (TypeScript/JavaScript/
  Python/Rust; 217 source files at initial index) and a fence-aware wiki
  (this file + `context/` + `patterns/`).

**Not yet built:**
- WS7's clean-room clone and its own, independent `mex setup` (deliberately a
  separate `mex-agent` instance, built only from files visible in that clone).
- A mex-native ignore-glob configuration surface — mex-agent 0.8.0 has none;
  see the Fence section in `AGENTS.md` for how this scaffold compensates.

**Known issues:**
- The site's default Node 22.14 build cannot run `mex setup`/`mex graph
  rebuild` (`no such module: fts5`); use a build with SQLite's `fts5`
  extension, e.g. `/tools_soc/opensrc/node.js/v24.14.0/bin` prepended to
  `PATH`. Full repro: `docs/dv/evidence/ws6-mex/summary.txt`.
- `mex check` flags one pre-existing false positive on `CLAUDE.md:59`
  (`DEAD_COMMAND: make clean`) — its checker only reads the repo-root
  `Makefile`, but that line refers to the (fenced) `dv/uvm/core_ibex/Makefile`,
  which does have a `clean` target. Not fixable without editing `CLAUDE.md`
  outside this task's scope; documented, not silently swept under the rug.

## Routing Table

Load the relevant file based on the current task. Always load `context/architecture.md` first if not already in context this session.

| Task type | Load |
|-----------|------|
| Understanding how the system works | `context/architecture.md` |
| Working with a specific technology | `context/stack.md` |
| Writing or reviewing code | `context/conventions.md` |
| Making a design decision | `context/decisions.md` |
| Setting up or running the project | `context/setup.md` |
| Any specific task | Check `patterns/INDEX.md` for a matching pattern |

## Behavioural Contract

For every task, follow this loop:

1. **CONTEXT** — Load the relevant context file(s) from the routing table above. Check `patterns/INDEX.md` for a matching pattern. If one exists, follow it. Narrate what you load: "Loading architecture context..."
2. **BUILD** — Do the work. If a pattern exists, follow its Steps. If you are about to deviate from an established pattern, say so before writing any code — state the deviation and why.
3. **VERIFY** — Load `context/conventions.md` and run the Verify Checklist item by item. State each item and whether the output passes. Do not summarise — enumerate explicitly.
4. **DEBUG** — If verification fails or something breaks, check `patterns/INDEX.md` for a debug pattern. Follow it. Fix the issue and re-run VERIFY.
5. **GROW** — After meaningful work, run this binary checklist:
   - **Ground:** What changed in reality? Name the changed behavior, system, command, dependency, or workflow.
   - **Record:** If project state changed, update the "Current Project State" section above. If documented facts changed, update the relevant `context/` file surgically.
   - **Orient:** If this task can recur and no pattern exists, create one in `patterns/` using `patterns/README.md`, then add it to `patterns/INDEX.md`. If a pattern exists but you learned a gotcha, update it.
   - **Write:** Bump `last_updated` in every scaffold file you changed. If the why matters, run `mex log --type decision "<what changed and why>"` or `mex log "<note>"`.
