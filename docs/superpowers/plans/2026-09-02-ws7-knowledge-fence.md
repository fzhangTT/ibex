# WS7+WS6 — Export-Path Cleanroom Fence + mex Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Status:** v2 (export path) — **owner directive 2026-09-02**: the snapshot-branch design (v1 of this
plan, commit 86eba26e) takes too long to set up; re-cut to the fastest path that sections out
previous DV collateral, and fold WS6 (mex) in. The deferred v1 machinery is listed in FENCE.md
(Task 5) so it can be built later if the challenge runs long.

**Goal:** A one-script exported cleanroom (fenced collateral absent by construction), the Zone A
overlay (SIM_RECIPE + doc/config/skill variants), mex on both trees, and the executed
compile-and-run gate — generation sessions become permitted (CLAUDE.md Critical Invariant 2 lifts).

**Architecture:** `ci/make-cleanroom.sh` exports `git archive HEAD` into a fresh single-commit git
repo, deletes fenced paths per an inline deny list (the amendment's triage tables), overlays Zone A
variant files from `ci/cleanroom-overlay/`, and self-verifies (no fenced paths/artifacts/identifiers,
no remote MCP, planted-canary anti-vacuity). No published branch, no sync automation: updates are
re-exports. Landing is a 30-line `dv/auto_dv/**`-only patch check plus human review.

**Tech Stack:** bash, git archive, mex-agent (npm), the existing validator/skills topology.

**Spec:** `docs/superpowers/specs/2026-09-01-auto-dv-setup-design.md` §WS6+§WS7 as amended by
`docs/superpowers/specs/2026-09-02-zone-a-fence-scope-amendment.md` (v2.1, BINDING — its Required
changes 1–6, triage tables, and supersession list are the fence-line authority). Handoff items 1–2.
`DV_prompt.txt` Section 12 (untracked, owner-delivered; cite structurally, never edit its sign-off).

## Global Constraints

- The amendment is the fence-line authority: deny lists, Zone A variant set, rubric set, escape
  checks, and launch preconditions come from it verbatim — this plan only re-shapes the DELIVERY
  MECHANISM (export script instead of snapshot branch + sync automation).
- Rulings carried from the v1 draft (ledgered; still binding): precondition-6 is already split in
  `DV_prompt.txt` — verify-and-record, don't edit; identifier scans that would disclose identifiers
  run OUTSIDE the export (the script scans before/while building; nothing identifier-bearing ships
  in); codex network stays on in Zone A (needed to clone upstream spike; advisory discipline via
  AGENTS.md); ChipSmart-imported skills carrying `dv/uvm/core_ibex`/`BUILD_AND_SIM` strings get
  minimal Zone A variants; `DV_prompt.txt` stays owner-delivered and untracked; landing enforces the
  `gen_` prefix only.
- Deferred to FENCE.md's "if needed later" list (owner speed directive): published snapshot branch +
  `sync-cleanroom.sh` + append-only history/rotation; standalone `ci/fence.yaml` (the deny list
  lives in `make-cleanroom.sh` for now — one authority, promoted later); the full escape-test
  harness beyond the script's self-verify; `zoneb-run.sh` referee attachment (built at the Phase-1
  evaluation gate); `land-from-cleanroom.sh` automation beyond the patch check.
- `source ci/env.sh` for flow commands; module gotcha; fresh OUT; watchdogs on long work; validator
  PASS after CLAUDE.md/skills edits; STE for FENCE.md/SIM_RECIPE.md/script error messages; evidence
  as raw artifacts + repro metadata; red→green transcripts for new checks (committed under
  `docs/dv/evidence/ws7-selftest-tdd/`).
- Concurrent-tree discipline: explicit-pathspec commits; ledger `docs/dv/process-logs/ws7/progress.md`
  (created in Task 1) owned by Task 1's agent during Wave 1 — Wave-1 agents for Tasks 2–3 do NOT
  touch it (controller ticks).
- Waves: Tasks 1+2+3 parallel (disjoint files); Task 4 (gate) serial after all three; Task 5 (docs +
  closures) last.

---

### Task 1: `ci/make-cleanroom.sh` + landing check + selftest

**Files:**
- Create: `ci/make-cleanroom.sh`
- Create: `ci/check-landing.sh`
- Create: `ci/cleanroom-selftest.sh`
- Create: `docs/dv/process-logs/ws7/progress.md` (ledger skeleton: T1–T5 checkboxes + the deferred-machinery note + carried rulings)

**Interfaces:**
- Consumes: the amendment's triage tables (deny list); `ci/cleanroom-overlay/` (Task 2 populates it;
  this script only requires the directory to exist and copies its tree verbatim over the export —
  overlay paths mirror repo-root-relative destinations).
- Produces: `ci/make-cleanroom.sh [DEST]` (default `../ibex-cleanroom`) — builds the export and
  self-verifies, exit nonzero on ANY verify failure; `ci/check-landing.sh <base> <head>` — exit 0
  iff every changed path in the range is under `dv/auto_dv/**`, with no renames/deletes/symlinks
  outside it and every new test/TB/module name matching `gen_*`.

- [ ] **Step 1: Write the failing selftest** — `ci/cleanroom-selftest.sh` (license-free): builds an
  export into a temp dir and asserts: (a) exit 0; (b) DENY-LIST ABSENCE — none of the fenced roots
  exist in the export (`dv/uvm`, `dv/cosim`, `dv/verilator`, `dv/formal`, `dv/riscv_compliance`,
  `formal/`, `vendor/riscv-isa-sim`, `vendor/patches`, `vendor/google_riscv-dv`,
  `docs/dv/BUILD_AND_SIM.md`, `docs/dv/COSIM.md`, `docs/dv/evidence`, `docs/dv/reviews`,
  `docs/dv/process-logs`, `docs/superpowers`, `ci/jenkins`, `ci/build-spike.sh`, `ci/setup-cosim.sh`,
  `ci/run-cosim-test.sh`, `ci/reviews/fence-integrity.md`, `ci/reviews/test-overlap.md`, the six
  verification RSTs under `doc/`, `doc/03_reference/images/tb*.svg`, `.mex/`); (c) ARTIFACT ABSENCE —
  `find` returns no `*.fsdb`, `*.vdb`, `*.daidir`; (d) IDENTIFIER ABSENCE — grep for a fixed probe
  set of fenced identifiers (`riscv_arithmetic_basic_test`, `core_ibex_tb_top`, `ibex_cosim`,
  `spike_cosim`, `mcounteren_test`, `+disable_cosim`) over the export returns nothing;
  (e) NO REMOTE MCP — the export's `.mcp.json`/`.codex/config.toml` list exactly
  siliconpilot/fsdb-mcp-server/verdi-cov-mcp and no `http`/`url` entries; (f) PLANTED CANARY
  (anti-vacuity) — rerun the export with `CLEANROOM_CANARY=1` (script plants a file
  `dv/auto_dv/.canary_fenced_ref` containing a fenced identifier into the staging tree before
  verification) and assert the build FAILS; (g) LANDING CHECK — `check-landing.sh` accepts a
  synthetic `dv/auto_dv/gen_foo.sv` commit range and rejects (i) a change outside `dv/auto_dv/`,
  (ii) a `dv/auto_dv/` file named without `gen_`, (iii) a symlink. Run it: expect FAIL (script
  missing), capture red transcript.
- [ ] **Step 2: Implement `ci/make-cleanroom.sh`.** Shape: `set -uo pipefail`; `DENY=(...)` array
  (the single authority — one entry per deny item above, each with a trailing `# why` comment drawn
  from the amendment tables); `git archive --format=tar HEAD | tar -x -C "$STAGE"`; delete deny
  paths; copy `ci/cleanroom-overlay/` tree over the stage (overlay wins); if `CLEANROOM_CANARY=1`,
  plant the canary; VERIFY phase = checks b–e above implemented in the script itself (shared shell
  functions with the selftest where practical), loud named failure per check; then `git init` +
  single commit `Cleanroom export of <source SHA> (deny list: make-cleanroom.sh)` in DEST; print the
  export SHA + verify summary. STE error messages.
- [ ] **Step 3: Implement `ci/check-landing.sh`** — `git diff --name-status --find-renames <base>..<head>`:
  reject any path outside `dv/auto_dv/`, any `R`/`D` status outside it, any symlink (`git ls-files -s`
  mode 120000 in the range), any added `dv/auto_dv/` file whose basename does not start with `gen_`
  (exempt: `dv/auto_dv/.gitignore`, `dv/auto_dv/contract/**`). Loud named failures.
- [ ] **Step 4: Selftest green** — note Task 2 must land before the full export verifies (overlay
  variants absent ⇒ check (e) fails on the stock configs still present). Until then run the selftest
  in `--pre-overlay` mode (skips (e), still proves a–d, f, g); capture red→green transcripts to
  `docs/dv/evidence/ws7-selftest-tdd/t1-{red,green}.txt` (pipefail+tee+exit pattern).
- [ ] **Step 5: Commit** — `[ci] WS7: cleanroom export builder + landing check + selftest` with
  explicit pathspecs (the 3 scripts + ledger + evidence dir).

---

### Task 2: Zone A overlay (`ci/cleanroom-overlay/`)

**Files:**
- Create: `ci/cleanroom-overlay/` mirroring destination paths — every file below.
- Modify (full tree): `docs/dv/dv_principles.md` (one Zone A scoping sentence in §6, OUTSIDE the
  hash-anchored TRUST-TRIAD block; run the validator after), `DV_prompt.txt` (Section 12 item 9
  extension ONLY — add `AGENTS.md` + `.codex/config.toml` to its scanned set and the asserted Zone A
  rubric list; verify precondition 6 already reads riscv-isa-sim-absent and record that in the
  ledger; touch nothing else in the file).

**Interfaces:**
- Consumes: amendment changes 2+3 (the variant list and positive rubric set — authoritative);
  `DV_prompt.txt` Sections 8, 11, 12.
- Produces (overlay contents, each a small authored file):
  - `CLAUDE.md` + `AGENTS.md` pair (Zone A: keep Critical Invariants shape — invariant 2 becomes
    "generation permitted in this clone only"; point flow guidance at `docs/dv/SIM_RECIPE.md`; skills
    index = the Zone A set; the validator-checked duplication block kept byte-identical between the
    two files).
  - `docs/dv/TB_CONTRACT.md` — positive-list rewrite: seeding (`+ntb_random_seed`/`RANDOM_SEED`
    recorded together), cocotb-master handshake PATTERN (alive-bit watchdog fails loud; objection
    holder; finish polling) described generically, failure path (Python assert/raised exception fails
    the run; a bare log line fails nothing), ASCII-only logging. NO existing-TB module/event names,
    no manifest paths, no `check_logs.py` behavior.
  - `docs/dv/SIM_RECIPE.md` — authored per the amendment change-6 allowlist: VCS compile/elab
    mechanics + flags (from the flow's verified command shape, no TB file lists), how to hook a new
    TB top (-top, filelists the team writes), +vpi/cocotb wiring flags, run/env contract
    (`source ci/env.sh`), LSF submission (`bsub -K -q regress -n N -R "span[hosts=1]"`), urg
    coverage-merge/report invocation, site gotchas (module exit code, fresh outdirs, license count),
    Zone B submission = push the `cleanroom/<topic>` branch + notify (mechanical ack only). Excluded
    per allowlist: test names, testlist schema, cosim/fcov-bind mechanics, metadata.pickle. Marked
    "execution gate: Task 4".
  - `.mcp.json` + `.codex/config.toml` — three local servers only (same wrapper paths; wrappers ship
    in the export since `ci/mcp/**` is not denied), no atlassian, config.toml keeps the
    project-doc fallback keys; header comments say Zone A.
  - `ci/env.sh` variant — spike-fork/cosim disclosure removed (`SPIKE_*` exports,
    `build-spike.sh` references); toolchain/VCS/MCP exports and PATH prepend kept; toolcheck
    fail-loud kept.
  - `ci/mcp/README.md` variant — worked example path swapped to `dv/auto_dv/`.
  - Skills (Zone A variants, path substitutions to SIM_RECIPE/`dv/auto_dv`): `regress`, `sim-debug`,
    `fcov-expectation` (manifests under `dv/auto_dv/fcov_expectations/`), `mutation-check` (Zone A
    inert-referee operationalization sentence per DV_prompt Section 8), `cross-review` (artifacts to
    `dv/auto_dv/reviews/`; wrapper asserts the positive rubric list), `simple-english` (surfaces:
    SIM_RECIPE + Zone A docs), and minimal variants of the ChipSmart imports that carry
    `dv/uvm/core_ibex`/`BUILD_AND_SIM` strings (grep them; substitute or mark N/A).
  - Agents: `ibex-debug-analyzer.md`, `ibex-test-generator.md` Zone A variants (artifact paths under
    `dv/auto_dv`, SIM_RECIPE references).
  - Rubrics `ci/reviews/` (Zone A set): `ai-slop-comments.md` copied as-is; `rtl-purity.md`,
    `magic-numbers.md`, `forces-and-hier-access.md` rewritten against `dv/auto_dv/` homes;
    `assertion-integrity.md` with the Zone A inert-referee sentence; GUIDE.md variant listing exactly
    these five. (fence-integrity/test-overlap intentionally absent — the overlay REPLACES the
    directory: make-cleanroom denies the two Zone B rubrics and the overlay supplies the variants.)
  - `dv/auto_dv/.gitignore` (`out*/`, sim junk) + `dv/auto_dv/contract/README.md` stub naming the
    namespace rule (`gen_` prefix, landing check).

- [ ] **Step 1:** Author every overlay file per the Produces list (grep the full tree first for the
  ChipSmart-import hits: `grep -rl 'dv/uvm/core_ibex\|BUILD_AND_SIM' .claude/skills/`).
- [ ] **Step 2:** Apply the two full-tree edits (dv_principles sentence outside the anchored block;
  DV_prompt item-9 extension + precondition-6 verification note in the ledger... ledger is Task 1's
  file — write the note into your report instead; controller transfers it).
- [ ] **Step 3:** Verify: `bash -lc 'source ci/env.sh >/dev/null 2>&1; python3 .codex/compat/validator.py'`
  ⇒ PASS (full tree unchanged in validator scope except dv_principles — its § numbering must not
  shift); grep the OVERLAY tree for `dv/uvm/core_ibex`, `BUILD_AND_SIM`, `COSIM.md`,
  `+disable_cosim`, `spike` ⇒ zero hits (self-check before Task 4's gate).
- [ ] **Step 4: Commit** — `[dv] WS7: Zone A cleanroom overlay (SIM_RECIPE, doc/config/skill variants)`
  with explicit pathspecs (`ci/cleanroom-overlay docs/dv/dv_principles.md DV_prompt.txt`)... note:
  `DV_prompt.txt` is intentionally untracked (owner-delivered) — do NOT `git add` it; state its edit
  in the report.

---

### Task 3: mex (WS6) — full tree

**Files:**
- Create: `.mex/` config as `mex setup` produces + fenced-glob ignore config; Modify: `CLAUDE.md`
  (mex anchor section merged, per spec §WS6; `AGENTS.md` unchanged).

**Interfaces:**
- Consumes: spec §WS6 verbatim (npm global dir on PATH, Node 22.14 ≥ 22.5); the deny list from
  Task 1's script (mirror those globs into mex's ignore config).
- Produces: full-tree mex with wiki; gate evidence.

- [ ] **Step 1:** `bash -lc 'npm install -g mex-agent'` (bounded `timeout 600`; if the package name
  or registry differs, STOP and report BLOCKED with the npm error — do not guess names).
- [ ] **Step 2:** `mex setup` from the repo root (bounded 900s; watchdog rule); configure its ignore
  list with the fenced globs (same entries as Task 1's DENY array) BEFORE the first graph/wiki build
  so fenced content never enters; add the wiki-authoring rule from spec §WS6 (no page may paraphrase
  fenced content) wherever mex keeps its authoring guidance.
- [ ] **Step 3:** Merge mex's CLAUDE.md anchor section into the canonical `CLAUDE.md` (keep our
  content authoritative; validator PASS after). Document the known limit (SV not parsed; graph
  covers the Python/DV side; RTL knowledge = curated wiki pages kept honest by `mex check`).
- [ ] **Step 4: Gate evidence** — `mex check` green; one `mex graph scope` query returning sensible
  context for a DV task (e.g. scope the `ci/jenkins` flow); save both raw outputs to
  `docs/dv/evidence/ws6-mex/` with a `summary.txt` (versions, invocations, SHA).
- [ ] **Step 5: Commit** — `[ci] WS6: mex on the full tree (fence-aware ignore config, wiki rule)`
  explicit pathspecs; do not commit anything mex generates that embeds fenced content into tracked
  files (check `git status` and the diff before committing).

---

### Task 4: GATE — export, verify, compile+run, cleanroom mex (serial, after 1–3)

**Files:**
- Create: `docs/dv/evidence/ws7-gate/` (raw self-verify output, SIM_RECIPE run log excerpts,
  cleanroom-mex check output, `summary.txt` with SHAs/wall-clocks).
- Modify: `docs/dv/process-logs/ws5/progress.md` (close gate item 3 against the amendment's
  replacement criterion), `docs/dv/process-logs/ws7/progress.md` (tick T4, record gate results).

- [ ] **Step 1:** `bash ci/make-cleanroom.sh /localdev/fzhang/ws/ibex-cleanroom` — full verify green
  (all checks a–e; canary mode separately re-proven). Save raw verify output.
- [ ] **Step 2 (the irreducible gate):** in the export, following ONLY `docs/dv/SIM_RECIPE.md`,
  write a minimal `gen_smoke_tb.sv` (clock gen + `gen_dut_top` instantiation per the amendment's DUT
  ruling + one bind-free assertion + `$finish`) under `dv/auto_dv/`, compile and run it with VCS via
  the recipe's commands (fresh out dir inside the export; `timeout 2700`; watchdog). PASS = clean
  elaboration + simulation exit 0 + the assertion exercised (force a bench-level stimulus toggle).
  If the recipe is insufficient to get this working WITHOUT consulting fenced docs, that is a
  RECIPE defect: fix `ci/cleanroom-overlay/docs/dv/SIM_RECIPE.md` (never the fence), re-export,
  re-run — record each iteration honestly.
- [ ] **Step 3:** cleanroom mex: `mex setup` inside the export (its own instance; graph/wiki from
  visible files only), `mex check` green; save output.
- [ ] **Step 4:** Close WS5 gate item 3 in `docs/dv/process-logs/ws5/progress.md`: the export's
  client configs list exactly the three local servers, no remote ones (cite the verify-check (e)
  output) — WS5 flips PARTIAL → DONE.
- [ ] **Step 5: Commit** — `[dv] WS7 gate: cleanroom export verified; SIM_RECIPE compile+run green;
  cleanroom mex up; WS5 closed` (evidence + both ledgers; the export directory itself is never
  committed to this repo).

---

### Task 5: `docs/dv/FENCE.md` + supersessions + close-out docs

**Files:**
- Create: `docs/dv/FENCE.md`
- Modify: `ci/mcp/README.md`, `ci/mcp/{siliconpilot-mcp,fsdb-mcp,verdi-cov-mcp}.sh` header comments,
  `.codex/config.toml` header, `ci/env.sh` MCP-block comment (amendment supersession list: retire
  the "Zone B only / no MCP in cleanroom" wording → "cleanroom ships the three local servers; see
  FENCE.md"); `CLAUDE.md` Critical Invariant 2 (fence authority now exists: generation sessions
  permitted only in a verified cleanroom export; `FENCE.md` is the rule file); session handoff.

- [ ] **Step 1:** Write `FENCE.md` (STE): what is fenced and why (point at the deny array as the
  single list); the one-command export + update-by-re-export workflow; landing workflow
  (`check-landing.sh` + human review); Zone B evaluation protocol (single evaluation run, nothing
  returns — mechanical ack only); the honor rules for humans operating both zones; the
  **deferred-machinery list** (snapshot branch + sync automation, fence.yaml promotion, full escape
  harness, zoneb-run referee attachment — with the amendment/spec sections that specify each).
- [ ] **Step 2:** Apply the supersession edits (each one line); validator PASS (CLAUDE.md changed).
- [ ] **Step 3:** Update the session-2 handoff (WS7+WS6 state, deferred list, the export path
  decision with the owner directive cited).
- [ ] **Step 4: Commit** — `[docs] WS7: FENCE.md, supersession updates, invariant-2 lift` explicit
  pathspecs.

---

## Workstream close (controller)

Post-execution review of the full WS7+WS6 range (opus fallback, sanity-scoped unless findings
suggest otherwise), artifact committed; ledgers to DONE; SDD workspace cleanup. The v1 plan
(16-task snapshot design) remains in git history at 86eba26e as the reference for the deferred
machinery.
