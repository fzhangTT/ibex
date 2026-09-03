---
name: decisions
description: Key architectural and technical decisions with reasoning. Load when making design choices or understanding why something is built a certain way.
triggers:
  - "why do we"
  - "why is it"
  - "decision"
  - "alternative"
  - "we chose"
edges:
  - target: context/architecture.md
    condition: when a decision relates to system structure
  - target: context/stack.md
    condition: when a decision relates to technology choice
# Decisions usually ground sparsely; add only symbols that implement the decision.
# Entry shape: { node: "function:<tier-1-id>", fingerprint: "mh:64:<hex>" }
grounds_to: []
last_updated: 2026-09-02
---

# Decisions

## Decision Log

<!-- mex:entity
id: mx_01M1JCXQA3T5KEVDGBFW1SZA4R
type: decision
status: promoted
revision: 1
-->
### Cross-model review for every plan and diff
**Date:** 2026-09-01
**Status:** Active
**Decision:** The executing model (Claude or codex) never self-approves its own
plan or diff; the other model reviews before execution (plan) and after
(diff), with a gating machine-readable verdict.
**Reasoning:** Two independently-trained models catch different classes of
mistakes than either does alone, and neither can rubber-stamp its own work.
**Alternatives considered:** Single-model self-review (rejected — no
independent check); human review of every diff (rejected — too slow for the
iteration rate this fork needs).
**Consequences:** Every workstream needs a recorded review artifact under
`docs/dv/reviews/` before it can land past `REQUEST-CHANGES`; the `cross-review`
skill exists to make this the default path instead of an ad hoc invocation.

<!-- mex:entity
id: mx_01M1JCXQ9W43SV47QKZWYV6X4Z
type: decision
status: promoted
revision: 1
-->
### Knowledge fence for generated-DV work (WS7)
**Date:** 2026-09-01
**Status:** Active (rollout in progress)
**Decision:** A separate "clean-room" clone, published as an orphan-history
`cleanroom` branch, is the boundary between existing DV collateral and future
AI-generated DV work; the generation namespace is `dv/auto_dv/**` only.
**Reasoning:** The auto-DV challenge is invalid if the generator can read the
existing testbench/tests it is meant to reproduce from the spec and RTL alone;
a physical clone (not a worktree, not a permission rule alone) is the only
boundary that survives an agent that can read arbitrary files.
**Alternatives considered:** Permission rules only (rejected — a single missed
rule leaks everything); a worktree-based split (rejected — worktrees share the
parent object store, so fenced blobs stay retrievable).
**Consequences:** Any file this scaffold (`.mex/`) or its wiki describes must
not paraphrase fenced content, since `.mex/` itself is a tracked, full-tree
artifact — see the Fence section in `.mex/AGENTS.md`.

<!-- mex:entity
id: mx_01M1JCXQ9M23T66EVJPZS9V0Z8
type: decision
status: promoted
revision: 1
-->
### mex-agent adopted for the full-tree code graph and wiki (WS6)
**Date:** 2026-09-02
**Status:** Active
**Decision:** `mex-agent` (npm global install) provides this repo's code graph
(tree-sitter based) and wiki (`.mex/`), built over the full tree, with its own
fence-awareness layered on top procedurally (see below) since the installed
version exposes no ignore-glob configuration surface.
**Reasoning:** A structured, source-backed context tool reduces re-reading cost
for both models; the spec (`docs/superpowers/specs/2026-09-01-auto-dv-setup-design.md`
§WS6) calls for it on the full tree, with a second, independent `mex setup` on
the clean-room clone once WS7 lands.
**Alternatives considered:** None — the task brief requires `mex-agent`
specifically and directs reporting BLOCKED rather than substituting a
different tool if it does not work; it did work, with two caveats below.
**Consequences:**
1. The site's default Node 22.14 build's embedded SQLite lacks the `fts5`
   extension both the code graph and wiki require; the site's v24.14.0 build
   has it and was used instead (still ≥22.5 per spec). Full repro in
   `docs/dv/evidence/ws6-mex/summary.txt`.
2. `mex-agent` 0.8.0 has no ignore-glob configuration surface for its graph or
   wiki corpus scan (verified by inspecting the installed package's bundled
   `dist/cli.js` — no config file, CLI flag, or environment variable exists
   for this). Fence enforcement for this full-tree instance is therefore:
   (a) structural — `.mex/graph.db` and `.mex/wiki.db` are never git-tracked
   (`.mex/.gitignore`), so a locally-indexed fenced Python file cannot leak via
   a commit, and the code graph's supported-language allowlist (TypeScript,
   JavaScript, Python, Rust) already excludes SystemVerilog, so RTL/TB source
   cannot enter it regardless; (b) authorial — the wiki-authoring rule in
   `.mex/AGENTS.md` binds every session that edits `.mex/context/`,
   `.mex/patterns/`, or `.mex/ROUTER.md` to the same deny list used by
   `ci/make-cleanroom.sh`. The clean-room clone's own future `mex setup`
   remains fence-safe by construction regardless of this gap, since fenced
   files are physically absent from that clone.
