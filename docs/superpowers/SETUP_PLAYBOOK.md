# Auto-DV platform setup playbook (repo-agnostic)

Distilled from this fork's build-out on `ibex` (branch `fzhang/auto-dv-setup`). Every claim below
traces to a source doc named inline. Use this to recreate the same platform — env entry point,
venv/toolchain builds, cocotb overlay, skills/cross-review layer, trust triad, SDD orchestration,
knowledge fence — on a different RTL/DV repo. It is a method, not a copy: adapt paths, configs,
and tool pins to the new repo's own reality; do not port literal values.

## 1. Env entry-point pattern

Single sourced entry point, `ci/env.sh` (this repo: `ci/env.sh`). Contract: source it, never
execute it, from a shell that already carries the site profile (login shell or equivalent) — it
loads additional Modules on top, it does not bootstrap a sanitized shell from nothing
(`ci/env.sh` header comment).

- **Central path authority.** Every tool path is an export from this one file — simulator,
  toolchain, ISS, MCP server binaries, venv activation. Nothing else in the repo hardcodes a tool
  path (`ci/env.sh` header: "Central authority for tool paths — nothing else in the repo hardcodes
  them"; `docs/dv/dv_principles.md` §5 "No hardcoded paths").
- **`module` exits 1 even on success.** If the site uses Environment Modules, never `&&`-chain a
  `module load` — check its real effect (a binary on PATH afterward), not its exit code
  (`ci/env.sh`: `module load ... 2>/dev/null || true`; `docs/dv/BUILD_AND_SIM.md` Gotchas;
  `CLAUDE.md` Site gotchas).
- **Fail-loud tail with a narrow opt-out.** End the script with a hard check of the tools it just
  set up (`command -v vcs`, the resolved toolchain gcc, `python3`) — WARN for debug-only tools
  (waveform viewer, a build-only dep), ERROR + `return 1` for anything the flow cannot run without.
  Give it one narrow, named opt-out env var for callers that only need the exports and never
  invoke the checked tools themselves (this repo: `IBEX_ENV_TOOLCHECK=off`, added when MCP server
  wrappers spawned under a stripped environment were killed by a vcs check they didn't need —
  `ci/env.sh`, `docs/dv/process-logs/ws5/progress.md` T3). Default behavior stays the loud check;
  the opt-out is per-caller, not global.
- **Re-sourcing must be idempotent and not silently clobber a real override.** Cache your own
  last auto-picked value in a private var so re-sourcing after a tool gets installed picks it up,
  without overwriting a user's explicit override (`ci/env.sh`'s `_IBEX_RV_TC_AUTO` pattern for
  `RISCV_TOOLCHAIN`).
- **A permanent runtime banner as proof the exports actually reached the tool under test** — print
  what got configured every run (this repo: `vcs=... gcc=... spike=...` at env-source time, and a
  DUT-side `TB-CONFIG:` banner in the sim log itself; see §4). Evidence over inference
  (`docs/dv/dv_principles.md` §4).

## 2. Venv + lockfile

- **One venv, created and populated by a dedicated script** (`ci/setup-venv.sh`), idempotent
  (safe to re-run), installing from a lockfile when present with a plain-requirements fallback
  (`docs/dv/BUILD_AND_SIM.md` One-time setup).
- **PYTHONPATH-clean pip.** A shell-profile-injected `PYTHONPATH` (e.g. from `~/.bashrc`) leaks
  unrelated package metadata into `pip freeze`/lock generation — clear `PYTHONPATH` around every
  pip operation (`CLAUDE.md` Site gotchas; memory `pythonpath-freeze-contamination`).
- **Lock enforcement is a real gate, not a suggestion.** A first-pass lockfile pulled in an
  unrelated package (`siliconpilot`) plus its transitive deps via an MCP-feature dependency chain
  — caught by whole-branch review, not the per-task review, and required an explicit
  contamination audit before it could be trusted (`docs/dv/process-logs/ws1/progress.md` final
  review + fix wave: "requirements.lock contaminated ... dependency-confusion vector"). Treat lock
  regeneration as security-sensitive: diff it, and adjudicate every unexpected top-level or
  transitive name before committing.

## 3. Toolchain / ISS builds

- **Workspace-local installs, outside the repo, at one exported root.** All built tools live under
  one writable directory outside the checkout (this repo: `IBEX_TOOLS_DIR`, default
  `/localdev/fzhang/ws/tools`), never installed into the repo tree (`ci/env.sh`;
  `docs/dv/BUILD_AND_SIM.md` One-time setup). Override the root by exporting the var *before*
  sourcing the env script.
- **The build script's pin is the pin of record — not a packaging file that also names a
  revision.** If the repo also carries a Nix flake (or similar) that pins the same dependency,
  that file's pin is not maintained in lockstep and will silently drift once the build script's
  pin moves — document this explicitly next to both pins, and never let an agent "fix" a stale
  build by copying the packaging file's number without checking which one is current
  (`ci/build-spike.sh`: "SPIKE_REV below is the pin of record ... flake.nix's spike rev is not
  maintained in lockstep with it"; `flake.nix:129` still carries the pre-fix revision after
  `ci/build-spike.sh`'s pin was advanced — verified by reading both files in this session).
- **pkg-config discovery, not hardcoded lib paths.** Export `PKG_CONFIG_PATH` pointing at the
  built install's `lib/pkgconfig`; let the TB/build system resolve libs by `.pc` name
  (`ci/env.sh`: `PKG_CONFIG_PATH="$SPIKE_INSTALL/lib/pkgconfig..."`; `docs/superpowers/specs/
  2026-09-01-auto-dv-setup-design.md` WS1: "discovered by the TB via `pkg-config`"). A site's
  pre-existing install of the same tool at a different path (without these `.pc` files) does not
  satisfy the build — verify the pinned revision actually builds and discovers correctly, don't
  assume a site copy suffices.
- **The stale-pin lesson (mcounteren): verify pins against upstream heads when a test first
  exercises an area, not only at initial bring-up.** A pinned reference-model revision one commit
  behind an upstream feature-reversal (`aadf648d`, "Enable ZIHPM unpriviledged performance
  counters", reverting an earlier disable) caused a real cosim divergence the first time a test
  touched that CSR area (`mcounteren_test`) — the DUT was correct, the pinned reference model was
  stale (`docs/dv/evidence/ws4-mcounteren-refix/summary.txt`). The fix was a one-line pin bump
  plus a rebuild, not a DUT or TB change. Generalize: when a new test class first exercises a
  reference-model area, re-check that pin against the upstream branch head before trusting a
  mismatch as a DUT bug.

## 4. Config-propagation audit (the IBEX_CFG class of bug)

A config generator can emit defines the TB never consumes — spelling or macro-name drift between
the two sides means every config silently builds with the TB's own default, not the one selected.
This repo's instance: the config generator emitted `+define+IBEX_CFG_BaseIsa`/`IBEX_CFG_RegFile`;
the TB guarded on `IBEX_CFG_BASE_ISA`/`IBEX_CFG_REG_FILE` — never matched, so every named config
silently elaborated with the TB's CHERIoT-capable defaults regardless of the requested config
(`docs/superpowers/specs/2026-09-01-auto-dv-setup-design.md` WS1 "Fork bug fix"; `docs/dv/
BUILD_AND_SIM.md` Gotchas, `IBEX_CFG_*` define-name mismatch, fixed commit `54e01775`).

- **Audit method: grep both sides, not one.** Grep the generator's emitted `+define+`/plusarg names
  and the TB's `` `ifdef``/`` `ifndef`` guards side by side; a name present on only one side is the bug.
- **Prove the fix, don't just believe it.** Add a permanent runtime banner naming the resolved
  config fields at elaboration time (this repo: `TB-CONFIG: BaseIsa=... RegFile=... RV32ZC=...` at
  time 0) so every future run carries independent evidence the requested config actually reached
  the DUT, not just that the Makefile knob was set (`docs/dv/BUILD_AND_SIM.md` Gotchas;
  `docs/dv/evidence/ws1-smoke-regr-note.txt`).
- Run this audit on any new config-selection mechanism before trusting a config-gated test result.

## 5. cocotb overlay recipe

Coexistence pattern: cocotb (or another Python co-simulation driver) is master, the existing
SV/UVM testbench stays fully active as a service layer underneath it — not replaced, not forked
into a separate flow (`docs/superpowers/specs/2026-09-01-auto-dv-setup-design.md` WS2
Architecture).

- **Strict opt-in flag; stock flow bit-identical when off.** One make/build knob (this repo:
  `COCOTB=1`, default `0`) compiles the overlay in; `COCOTB=0` compiles none of it, verified by a
  behavioral (not just filename) grep sweep of the compile/run surfaces for the overlay's own
  markers (`docs/dv/process-logs/ws2/progress.md` T6: "identity is BEHAVIORAL... zero hits for
  `COCOTB_SIM|+vpi|cocotb_pli|libcocotbvpi|MODULE=`", with the two filename parse-lines annotated
  as expected).
- **Tab-file access discipline: read + deposit, never force or dump.** Restrict the VPI access tab
  to `acc+=rw,wn:*` (read + deposit only) — never a blanket `-debug_access+all`
  (`docs/superpowers/specs/2026-09-01-auto-dv-setup-design.md` WS2: `cocotb_pli.tab`). If the
  stock compile already carries broader debug access for other reasons, the tab file still
  independently withholds force/dump by default; don't widen it to work around a one-off need.
- **Two-level test selection.** One env/knob picks the Python module cocotb imports; plusargs
  parameterize stimulus within it (`docs/dv/TB_CONTRACT.md` §1: `COCOTB_MODULE`, `+cocotb_*`
  plusargs). Keep both make knobs subject to the same stale-metadata caveat as any other top-level
  knob (§ "gotchas" below).
- **Dead-cocotb watchdog must fail loud, never `$finish` clean.** A lost/never-started Python side
  must produce a nonzero-exit, log-visible failure — `$fatal` at a short fixed deadline unless
  Python sets an alive bit — not `$finish`, which could masquerade as a pass
  (`docs/superpowers/specs/2026-09-01-auto-dv-setup-design.md` WS2: "a lost Python must FAIL the
  run with nonzero exit — `$finish` would end it cleanly and could masquerade as a pass").
  Distinguish this from the *different* failure class of a Python-side import error, which the
  Python framework itself may already log and end cleanly at time 0 — the SV watchdog guards a
  narrower class (total VPI/libpython load failure) and the two failure paths log differently
  (`docs/dv/BUILD_AND_SIM.md` cocotb Gotchas).
- **`finish_on_completion` must move to the Python side.** When cocotb (not UVM) owns ending the
  simulation, clear the UVM-side auto-finish — but that opens a window between the UVM summary and
  the Python side's own completion observation where DUT assertions can still fire on an unlucky
  seed; call the Python-side finish promptly, don't add unrelated delay before it
  (`docs/dv/TB_CONTRACT.md` §2 Hard rule 3; `docs/dv/BUILD_AND_SIM.md` cocotb Gotchas).
- **Event triggers are not queued — size spacing and count, don't assume delivery.** A trigger
  that arrives mid-response to a prior one is silently dropped; expose accounting counters and
  compare expected-vs-observed rather than trusting the call succeeded (`docs/dv/TB_CONTRACT.md`
  §3 Hard rule 4).
- **A vacuous-pass guard is mandatory wherever the overlay is opt-in per testlist entry.** The
  same testlist entry built without the overlay flag must `uvm_fatal` if it still carries the
  overlay's plusargs — otherwise the entry silently runs as a plain test under a name that claims
  coverage it never exercised (`docs/dv/TB_CONTRACT.md` §5 Hard rule 5a; found and fixed only at
  the post-execution cross-model review stage — `docs/dv/process-logs/ws2/progress.md` Task 7
  review, "vacuous-pass in stock regressions").
- **Timeouts don't auto-scale — size them to the program, not a framework default.** A
  minimal-program-sized default (e.g. 2ms) undersizes a real generated program's completion
  handshake and raises a spurious timeout on an otherwise-passing run (`docs/dv/TB_CONTRACT.md`
  §2 "timeout_ms sizing").

## 6. Skills topology + validator

Canonical instruction source lives in one file (this repo: `CLAUDE.md`) at repo root, referenced
by every agent-specific config rather than duplicated.

- **Canonical skills directory + a thin delegator for the second CLI.** Skills live under
  `.claude/skills/<name>/SKILL.md`; a second CLI (codex) discovers the same skills through a
  symlink (`.agents/skills/shared -> ../../.claude/skills`), and its own instruction file
  (`AGENTS.md`) is a thin pointer: "read CLAUDE.md" plus a client-mechanics translation table
  (tool-name equivalence, `$ARGUMENTS` mapping) — never a copy of CLAUDE.md's content
  (`CLAUDE.md`; `AGENTS.md`; `docs/superpowers/specs/2026-09-01-auto-dv-setup-design.md` WS3
  Topology).
- **Bound, hash-checked duplication for the few invariants that must survive even if the delegator
  is ignored.** A second CLI may fall back to a different project-doc file if the delegator is
  absent; mitigate by duplicating only the critical-invariants block verbatim in both files inside
  matched HTML-comment markers, and have a validator assert byte-identity
  (`docs/superpowers/specs/2026-09-01-auto-dv-setup-design.md` WS3 "Known caveat"; `AGENTS.md`
  Critical invariants block; `.codex/compat/validator.py`: `INV_BEGIN`/`INV_END` markers, and the
  same technique reused for the trust-triad block across every file that embeds it — `TRIAD_FILES`
  in `.codex/compat/validator.py`).
- **A compatibility validator enforces the contract mechanically**, not by convention: every
  skill's frontmatter `name` matches its directory, the symlink resolves, the invariant/triad
  blocks are byte-identical everywhere they appear, required `CLAUDE.md` sections and policy
  phrases are present, and (optionally, slower) a real launch of both CLIs from the repo root and
  a subdirectory is probed to assert the effective instructions actually loaded
  (`.codex/compat/validator.py` module docstring and `--probe` flag).
- **Curate ported skills with a classification report, not a blanket import.** For every candidate
  skill from a source library (this repo imported a curated subset from `riscv/ChipSmart`),
  classify as IMPORT / SKIP / BORDERLINE against the actual stack (does the tool it names exist
  here; is the workflow's calling convention real or aspirational; does an equivalent skill already
  exist) — commit the classification table with a one-line reason per skill, not just the final
  file list (`.superpowers/sdd/chipsmart-import-report.md`: 35 skills classified, 14 IMPORT / 4
  BORDERLINE / 17 SKIP, reasons given per row; BORDERLINE rows left for the human owner). For each
  IMPORT, strip source-specific frontmatter to the target repo's own convention and retarget every
  tool/agent/path reference named in the source skill to what actually exists in the new repo —
  a skill importing verbatim references to a nonexistent tool call is worse than not importing it.
- **Re-validate after every skills-index or file change** (`bash -lc 'source ci/env.sh
  >/dev/null 2>&1; python3 .codex/compat/validator.py'`) and keep `CLAUDE.md`'s skills-index line
  in sync with what actually landed.

## 7. Cross-model review policy + gating

The executing model never self-approves. Before execution, the plan/spec/testplan is reviewed by
the *other* model; after execution, the diff is reviewed by the other model
(`CLAUDE.md` Cross-model review policy; `docs/superpowers/specs/2026-09-01-auto-dv-setup-design.md`
WS3).

- **Machine-readable, fixed-header verdicts: `APPROVE` / `APPROVE-WITH-CHANGES` /
  `REQUEST-CHANGES`.** `REQUEST-CHANGES` is gating — no progress past it without a recorded
  re-review reaching `APPROVE`/`APPROVE-WITH-CHANGES` (`CLAUDE.md` Critical invariants #1).
- **Committed artifacts with a reviewer-identity header and an explicit review target.** Record
  CLI version, model ID, reasoning setting, and the exact commit-SHA range or diff scope reviewed
  — never an ambient default; commit every round, including superseded ones, as the trust-evidence
  trail (`CLAUDE.md`; `docs/superpowers/specs/...design.md` WS3 "Trust-evidence attribution").
  A wrapper script can enforce the target echo mechanically when the CLI's own flags can't combine
  with a custom prompt (`.claude/skills/cross-review/SKILL.md`: "the wrapper REFUSES an artifact
  that does not echo the exact target range").
- **Fallback-reviewer clause, identity recorded either way.** If the preferred reviewer model/CLI
  is unavailable (spend cap, outage, timeout), an equivalent-tier model from the other family, in
  a fresh session, is an acceptable substitute — record which was used and *why* the primary was
  unavailable, with the raw error kept in the artifact (`CLAUDE.md` Cross-model review policy;
  `.claude/skills/cross-review/SKILL.md` "When codex is unavailable"; exercised live this project
  when a spend cap made codex unavailable — `docs/superpowers/handoffs/2026-09-02-session2-
  handoff.md` "codex spend cap hit").
- **Scoped re-reviews (replan mode) for oversized plans.** A large plan can blow a fixed review
  timeout on full re-reads every round; when that happens, switch subsequent rounds to verifying
  prior findings plus the diff-since-last-round instead of re-reading the whole plan each time
  (`docs/superpowers/handoffs/2026-09-02-session2-handoff.md`: "the grown WS4 plan blew 60/90-min
  budgets three times ... next step is a scoped re-review mode").
- **Review-timeout sizing scales with plan/diff size — size it, don't fix it once.** This project's
  review wrapper timeout grew from an initial default to 150 minutes as plans grew
  (`docs/superpowers/handoffs/2026-09-02-session2-handoff.md` "cross-review wrapper timeout now
  150 min"); budget per review round based on the size of what's under review, and prefer
  splitting an oversized plan over stretching the timeout indefinitely.
- **Disagreements with a recorded controller ruling go to the human owner, not back into the
  review loop** — cap the number of adjudication rounds and escalate rather than looping forever
  (`CLAUDE.md`; exercised in `docs/dv/process-logs/ws3/progress.md`: "Loop closed at 5 gated
  rounds per declared cap ... surfaced to the human owner per policy").

## 8. Trust triad mechanics

Required for every new test, checker, assertion, or covergroup, human-written or generated
(`docs/dv/dv_principles.md` §6, canonical block; mirrored byte-identical into the skills that
execute it and validator-checked — §6 above).

1. **TDD — committed red→green transcript.** The behavior is specified by a failing check before
   the implementation that makes it pass; the transcript showing both states is part of the
   evidence, not an assertion that it was done (`docs/dv/dv_principles.md` §6.1).
2. **Mutation-proof, with inert referees and an ablation control.** Declare the mutation first (id,
   file:line, original, mutated, expected detector); apply it; run the covering test with hidden
   referees inert (this repo: `+disable_cosim=1`, a full-tree-TB plusarg — each repo names its own
  demote-the-referee mechanism) and
   confirm the failure signature belongs to the *named* checker, not something else silently
   catching it; then disable the named checker and rerun — the mutation must *survive* (an
   ablation where the mutation is still caught with the checker off voids the whole proof); revert
   both and confirm green (`.claude/skills/mutation-check/SKILL.md` Procedure;
   `docs/dv/dv_principles.md` §6.2). Attribution must be to the named checker specifically —
   crediting a coincidental catch by an unrelated mechanism is not evidence.
3. **fcov-expectation, per-test and pre-merge.** Every new test declares, in a manifest keyed to
   its exact testlist name, the functional-coverage bins it intends to hit; a declared-but-unhit
   bin fails the run. Query the *per-test* coverage slice before the cross-test merge — a merged
   database lets one test claim another's bins (`docs/dv/TB_CONTRACT.md` §7; `.claude/skills/
   fcov-expectation/SKILL.md`). Generated covergroups live in their own namespace, never folded
   into an existing human-authored covergroup. Apply an anti-vacuity review to every declared bin
   before declaring it: a bin hit by an always-true sampling condition proves nothing
   (`docs/dv/dv_principles.md` §6.3; `docs/dv/TB_CONTRACT.md` §7 "Anti-vacuity rule"). Note the
   known limitation: per-test enforcement under a parallel (`-j`) regression reading a shared
   coverage database while other tests still write it is unvalidated — treat concurrent
   enforcement as an open design point, not solved, until proven (`.claude/skills/
   fcov-expectation/SKILL.md` final warning).

## 9. SDD/watchdog orchestration practice

- **Fresh implementer per task/batch; match model tier to task shape.** A general-purpose or
  above-floor model for anything requiring real synthesis (a new python-cocotb protocol, a new
  checker); a lighter/faster model only for genuinely mechanical, fully-specified transcription —
  and even then, verify: one lighter-tier implementer produced plausible-but-dead async code on a
  python-cocotb task, corrected to "sonnet-floor implementers" for that class going forward
  (`docs/dv/process-logs/ws2/progress.md` Task 3: "Haiku implementer produced plausible-but-dead
  code — model-selection lesson").
- **Batch same-shape, disjoint-file tasks as parallel dispatches.** Independent tasks that touch
  non-overlapping paths can run as one batch of concurrent implementer dispatches
  (`docs/dv/process-logs/ws1/progress.md` Task 1+2: "dispatched as one batch (same-shape script
  tasks)"). At the workstream level, run whole workstreams in parallel worktrees when their file
  sets are disjoint by design, and run a pre-flight conflict scan naming every cross-task/
  cross-workstream produces-vs-consumes pair before dispatch (`docs/dv/process-logs/ws2/
  progress.md` header: "WS3 executes in parallel in worktree ../ibex-ws3 ... paths disjoint by
  design"; both ws1/ws2 ledgers open with a "Pre-flight conflict scan" table).
- **Explicit-pathspec commits in a shared tree.** When multiple tracks share one checkout, commit
  by explicit pathspec, not a blanket `git add -A`, so one track's in-flight edits can't leak into
  another's commit (general git-safety practice this project followed throughout; see the
  per-workstream disjoint-paths tables above as the planning-side half of the same discipline).
- **Per-task review, then a whole-branch/whole-workstream review before declaring the workstream
  closed.** Every task gets its own implementer-then-reviewer cycle with fix rounds
  (`docs/dv/process-logs/ws1/progress.md`, `ws2/progress.md`: "Task N: dispatched ... review ...
  fix round ... complete", repeated per task); the workstream only closes after a final
  whole-branch review and, per the cross-model policy, a codex post-execution review of the full
  range (`docs/dv/process-logs/ws2/progress.md`: "ALL WS2 TASKS COMPLETE. Final whole-branch
  review dispatching"; "Codex post-execution review 04: ... WS2 CLOSED").
- **Scoped re-reviews for fix rounds**, not full re-reads: after a fix wave, dispatch a re-review
  scoped to the fixed findings plus the new diff, escalating to a full package review only when the
  fix touched more than the flagged lines (`docs/dv/process-logs/ws1/progress.md`: "scoped
  re-review dispatched, haiku" pattern repeated per task; "CORRECTION: fix wave = 3 commits ...
  re-review redirected to full package review" when the fix wave grew).
- **Bounded watchdogs on everything dispatched** — background notifications are unreliable; size a
  timer to the work (this repo: ~10 min default; 45–60 min for full sims/regressions — size to the
  new repo's own runtimes) and verify progress from
  the filesystem/process table on firing, never from agent status alone (`CLAUDE.md` Site gotchas,
  Watchdog rule; exercised repeatedly, e.g. `docs/dv/process-logs/ws1/progress.md` Task 5:
  "Implementer stalled on lost notification again; nudged with poll-the-log instruction").
- **Nudge once, then reassign against working-tree state — verify before letting the reassignment
  run.** On a stall, nudge with concrete state first; if still dead after one nudge window,
  reassign, but check the tree state before the reassigned agent starts mutating — a reassigned
  agent that started before the nudged one's completion was caught and stopped before it could
  double-write (`CLAUDE.md` Watchdog rule; `docs/superpowers/handoffs/2026-09-02-session2-
  handoff.md`: "the reassigned one was TaskStop'd before mutating — check tree state before
  letting a reassignment run").
- **Ledgers that survive compaction.** Keep a running per-workstream ledger file (this repo:
  `docs/dv/process-logs/ws<N>/progress.md`) recording task dispatch, implementer result, review
  verdict, rulings (with cost-if-wrong), and fix-round outcomes as they happen — it is the
  authoritative state when a session's own context is lost or compacted, and it is what a
  handoff document points back to instead of re-deriving state
  (`docs/dv/process-logs/ws1/progress.md`, `ws2/progress.md`, `ws3/progress.md`; `docs/superpowers/
  handoffs/2026-09-02-session1-handoff.md`: "Status ledger" table pointing at these files).
- **Record every ruling with its cost-if-wrong**, inline in the ledger, at the moment it's made —
  not reconstructed later (every ruling line in `docs/dv/process-logs/ws1/progress.md` and
  `ws2/progress.md` follows this "Ruling: ... cost if wrong: ..." shape).

## 10. Fence design

*WS7 (this fork's fence implementation) had not executed as of this writing; the mechanics below
are the current binding design/amendment. Re-check `docs/dv/FENCE.md` once WS7 lands — it will be
the implemented authority and may refine details here.*

- **Fence the collateral, not the tools.** The fence's job is to keep prior DV collateral out of a
  generation session's reach — not to strip the generation session of the tools (MCP servers,
  skills) it needs to work effectively. A generation-side clone with its own out-tree has nothing
  fenced for a tool to read, by construction of the clone boundary — so tools travel with
  generation, scoped by data reach rather than removed (`docs/superpowers/specs/2026-09-02-zone-a-
  fence-scope-amendment.md` Decision + "Why the spec fenced the tools, and why that was the wrong
  cut").
- **Orphan-snapshot branch, single-branch clone, never a worktree.** Publish a branch whose history
  is a sequence of snapshot commits built only from an allowlist, with no ancestry to the full
  branch (orphan root) — a `git clone --single-branch` of it fetches only those objects, so fenced
  blobs are physically absent, not merely hidden. Never substitute a `git worktree` for this: a
  worktree shares the parent's object store, so fenced blobs remain retrievable even if not
  checked out (`docs/superpowers/specs/2026-09-01-auto-dv-setup-design.md` WS7 "Zone A — clean
  room").
- **Default-deny manifest, single source of truth, reject-unclassified.** Sensitive roots are
  denied wholesale; a path becomes visible only via an explicit file-level allowlist entry with a
  one-line rationale, and the sync step rejects any path it cannot classify — new files must be
  triaged into the manifest before they can enter a snapshot (`docs/superpowers/specs/2026-09-01-
  auto-dv-setup-design.md` WS7 "Fenced content — default-deny"). Periodically triage the fence line
  itself: a deny-by-root rule can over-catch generic mechanics bundled with real collateral (split
  them out) and under-catch collateral outside the obvious roots (e.g. a formal-proofs directory
  at repo root, a vendored fork's own test tree) — this project ran exactly this triage as an
  amendment pass (`docs/superpowers/specs/2026-09-02-zone-a-fence-scope-amendment.md` "Fence-line
  triage").
- **Zone A variants of tool-adjacent files, not deletions.** Any file that points at fenced paths
  or Zone-B-only config (env script, MCP client config, review rubrics, TB-contract doc) gets a
  parallel Zone A version pointed at the generation zone's own out-tree and a positive-list
  (not redacted) description of mechanics — asserted explicitly by name so a missing or extra one
  is loud, not silent (`docs/superpowers/specs/2026-09-02-zone-a-fence-scope-amendment.md` Required
  changes #2, #3).
- **Escape tests with an anti-vacuity negative control.** A scripted suite attempts real
  contamination paths from a generation-zone session (fetch the full branch, read a sibling clone,
  fetch upstream's own DV tree, resolve a fenced path from inside a skill) — each must fail or be
  flagged. Include at least one operation that *must* succeed (e.g. a generation-produced waveform
  opens fine) — a suite whose every probe fails passes vacuously and proves nothing
  (`docs/superpowers/specs/2026-09-02-zone-a-fence-scope-amendment.md` Required changes #4,
  citing `docs/dv/dv_principles.md` §6's anti-vacuity rule applied to the suite itself).
- **Launch preconditions, checked mechanically before any generation session starts.** Until the
  fence authority document, the Zone A variants of the instruction/contract files, and the
  manifest itself all exist and pass their own fence-integrity check, generation sessions are not
  permitted at all — fail closed, not "proceed with caution" (`CLAUDE.md` Critical invariants #2;
  `docs/superpowers/specs/2026-09-02-zone-a-fence-scope-amendment.md` Required changes #5).
