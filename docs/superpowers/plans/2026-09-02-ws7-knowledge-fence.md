# WS7 — Knowledge Fence / Cleanroom Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development
> (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use
> checkbox (`- [ ]`) syntax for tracking.

**Goal:** A persistent, pullable, documented knowledge fence: a `cleanroom` branch of orphan
snapshots containing zero fenced blobs (history included), the scripts that build/clone/land/
evaluate against it, the Zone A variant set the snapshots ship, the escape-test suite that proves
the boundary, and the launch preconditions `DV_prompt.txt` Section 12 checks — closing WS5's
pending gate item on the way.

**Architecture:** One manifest (`ci/fence.yaml`, default-deny, encodes the amendment's triage
tables) is the single classification authority; one Python classifier (`ci/fence_classify.py`) is
its only interpreter, consumed by the sync script, the clone verifier, the landing validator, the
escape suite's generated inputs, and the full-tree `PreToolUse` hook. Zone A variants of
tool-adjacent files live in a full-tree overlay directory (`ci/cleanroom/overlay/**`, mirroring
snapshot-root-relative paths); `ci/sync-cleanroom.sh` builds each snapshot as: filtered source
tree (allow-classified paths only) + pristine upstream riscv-dv + overlay + generated fence-scan
inputs, self-scanned, committed as an orphan-history snapshot, audited across the branch's entire
history, and pushed serialized. Zone B evaluation (`ci/zoneb-run.sh`) is a single run per the
amendment (the dual-run/canary design is retired); `ci/zoneb-submit.sh` returns mechanical
acceptance only. Fence the collateral, not the tools: the three local MCP servers and the skills
ship to Zone A (as variants where they pointed at fenced documents); atlassian does not.

**Tech Stack:** bash + Python 3.12 (stdlib + PyYAML from the repo venv), git plumbing
(`git archive`, `read-tree`, `write-tree`, `commit-tree`, `update-ref`,
`push --force-with-lease`), VCS/Verilator for the real gates, `claude -p`/`codex exec` for
agent-session escape probes.

**Spec (binding inputs, in precedence order where they overlap):**
1. `docs/superpowers/specs/2026-09-02-zone-a-fence-scope-amendment.md` (v2.1, BINDING — amends
   §WS5/§WS7; cited below as "amendment change N" / "triage table").
2. `docs/superpowers/specs/2026-09-01-auto-dv-setup-design.md` §Workstream 7 (base design).
3. `docs/superpowers/handoffs/2026-09-02-session1-handoff.md` items 1 and 2.
4. `DV_prompt.txt` (untracked, repo root) — cite by section/precondition number ONLY, never by
   line (the file is owner-edited and unversioned).
5. `docs/dv/process-logs/ws5/progress.md` end-state (PARTIAL pending WS7).

## Global Constraints

- **Environment:** `source ci/env.sh` first in every shell (login shell / `bash -lc`). Never
  `&&`-chain the `module` command. Fresh `OUT=` per knob change; stale `metadata.pickle` after
  testlist/config edits means `make clean` or a new OUT.
- **Watchdogs (mandatory, CLAUDE.md):** every dispatched agent/background shell gets a bounded
  timer — ~10 min default for script/selftest tasks, 45–60 min for the compile+run and round-trip
  gates. On firing, verify progress from the filesystem/process table, nudge once, then reassign.
- **Order:** license-free selftests first, real gates last. Wave 1 = Tasks 1–5 (parallel,
  disjoint files); Wave 2 = Tasks 6–12 (parallel after Task 1; Task 7 also needs Tasks 2–4);
  Wave 3 = Tasks 13–16 strictly serialized (each gate consumes the previous one's artifacts).
  Batch Wave-1/Wave-2 dispatches; commit per task with explicit pathspecs (`git add <paths>`,
  never `git add -A`).
- **Fence hygiene (CLAUDE.md Critical Invariant 2):** this is infra work — contaminated by
  design — and it authors files that ship to Zone A. NEVER paste fenced content (test names,
  testlist schema fragments, cosim mechanics, human fcov bin/covergroup names, existing TB module
  or event names, `check_logs.py` behavior) into any overlay file, `SIM_RECIPE.md`, `FENCE.md`,
  or `TB_CONTRACT.md` variant. Distill mechanics; do not copy collateral. Every overlay/doc task
  below ends with the mechanical string scan from `DV_prompt.txt` Section 12 item 9 plus a
  manifest-glob scan.
- **STE surfaces:** `docs/dv/FENCE.md`, `docs/dv/SIM_RECIPE.md`, and every error message in the
  new `ci/` scripts are ASD-STE100 surfaces (`simple-english` skill): short, imperative,
  unambiguous. NOT applied to `dv_principles.md`, rubrics, or this plan.
- **Validator:** run `.codex/compat/validator.py` after ANY edit to `CLAUDE.md`, `AGENTS.md`,
  `.claude/skills/**`, or `.codex/config.toml` (full tree or overlay) — must stay PASS.
- **Evidence:** raw artifacts + repro metadata (dv_principles §6): every evidence file under
  `docs/dv/evidence/ws7-*` opens with the exact command lines, the git SHA(s) they ran against,
  and the date. Red→green transcripts are committed for every new check (classifier selftest,
  landing validator, escape suite, the dummy artifact's checker).
- **Ledger:** `docs/dv/process-logs/ws7/progress.md`, one entry per task, created in Task 1.
- **Interface contract (shared names — every task uses these exactly):**
  - Manifest: `ci/fence.yaml`; classifier: `ci/fence_classify.py`; salt: `ci/.fence-salt`.
  - Overlay root: `ci/cleanroom/overlay/` (paths inside mirror snapshot-root-relative paths).
  - Snapshot commit trailers: `Generation:`, `Source-SHA:`, `Manifest-Digest:`
    (+ `Rotation-Reason:` on rotation).
  - Generation registry (full tree): `ci/cleanroom-generations.yaml`.
  - Generated into each snapshot: `ci/fence-globs.txt`, `ci/fence-identifiers.sha256`,
    `ci/.fence-salt` (copy).
  - Zone B evaluation entry-point convention (documented in `SIM_RECIPE.md` §Submission): a
    submission provides `dv/auto_dv/scripts/zoneb_entry.sh`.
  - Item-9 string set (from `DV_prompt.txt` Section 12 item 9): `dv/uvm/core_ibex`,
    `BUILD_AND_SIM.md`, `COSIM.md`.
  - Zone A rubric list (amendment change 3, exact): `ai-slop-comments`, `assertion-integrity`,
    `forces-and-hier-access`, `magic-numbers`, `rtl-purity`.
- **Out of scope, recorded:** the Jenkins cleanroom-sync job stays WS4-side (spec §WS4); WS7's
  gates use manual `ci/sync-cleanroom.sh` runs. The cleanroom's own `mex setup` is WS6.
  GitHub branch protection for `cleanroom` (non-sync pushes) is a one-command manual setup step
  documented in `FENCE.md` (Task 6), executed in Task 13.

---

### Task 1: Fence manifest, classifier, PreToolUse hook, ledger

**Files:**
- Create: `ci/fence.yaml`
- Create: `ci/fence_classify.py`
- Create: `ci/fence_classify_selftest.py`
- Create: `ci/.fence-salt`
- Create: `ci/fence_hook.py`
- Modify: `.claude/settings.json` (register the hook)
- Create: `docs/dv/process-logs/ws7/progress.md` (ledger skeleton mirroring this plan's tasks)

**Interfaces:**
- Produces: the classification authority every later task consumes. CLI contract:
  `python3 ci/fence_classify.py <subcommand>` with subcommands `classify` (paths from args or
  stdin → `<class>\t<path>` lines), `check-tree` (`--rev <sha>` or `--root <dir>`; exit 1 listing
  any `unclassified` or deny-classified path present), `filter` (`--root <dir>`: delete
  deny/omit-classified paths, exit 1 on unclassified), `emit-globs` (deny globs, one per line),
  `emit-digests` (`--salt-file`: salted SHA-256 of fenced identifiers, one per line, sorted),
  `scan-tree` (`--root <dir>`: content scan — deny-glob path presence, `*.fsdb`/`*.vdb`
  anywhere, item-9 strings inside the item-9 scan homes, plaintext fenced identifiers anywhere),
  `audit-history` (`--branch <ref>`: per-commit `check-tree` + trailer presence + generation
  monotonicity). All subcommands take `--manifest ci/fence.yaml`.

- [ ] **Step 1: Write `ci/fence.yaml`.** Schema (version 1): `default: deny`; `rules:` — an
  ordered list, FIRST MATCH WINS, each entry `{path: <glob>, class: allow|deny|variant|omit,
  rationale: <one line>}` (`variant` = fenced as-is, the overlay replaces it — the base file must
  NOT enter a snapshot; `omit` = deny, kept distinct for reporting); `special:` — the pristine
  riscv-dv replacement; `overlay_root: ci/cleanroom/overlay`; `item9_strings:` and
  `item9_scan_homes:` (the Section-12 item 9 sets, so the scanner and the prompt stay in sync);
  `identifier_sources:` (Zone-B-side inputs for `emit-digests`). Seed rules — encode the spec
  §WS7 deny list and BOTH amendment triage tables verbatim; ordering matters (allow before its
  covering deny):

```yaml
version: 1
default: deny
overlay_root: ci/cleanroom/overlay
item9_strings: ["dv/uvm/core_ibex", "BUILD_AND_SIM.md", "COSIM.md"]
item9_scan_homes: [".claude/skills/", ".claude/agents/", "AGENTS.md", "CLAUDE.md",
                   ".codex/config.toml", "ci/env.sh", "ci/mcp/", "docs/dv/TB_CONTRACT.md"]
identifier_sources:
  - {kind: testlist_names, files: ["dv/uvm/core_ibex/riscv_dv_extension/testlist.yaml",
                                   "dv/uvm/core_ibex/riscv_dv_extension/cov_testlist.yaml"]}
  - {kind: covergroup_names, glob: "dv/uvm/core_ibex/fcov/*.sv*"}
special:
  pristine_vendor:
    - {dest: vendor/google_riscv-dv,
       upstream: "https://github.com/chipsalliance/riscv-dv",
       rev: 71666ebacd69266b1abb7cdbad5e1897ce5884e6}   # vendor/google_riscv-dv.lock.hjson
rules:
  # --- generation namespace first (allow before the dv/** deny) ---
  - {path: "dv/auto_dv/**", class: allow, rationale: "generation namespace (spec WS7)"}
  - {path: "dv/**",         class: deny,  rationale: "existing DV collateral (spec deny root)"}
  - {path: "formal/**",     class: deny,  rationale: "Ibex formal proofs (amendment under-fenced table)"}
  - {path: "vendor/patches/**",        class: deny, rationale: "local DV patches (spec)"}
  - {path: "vendor/google_riscv-dv/**", class: deny, rationale: "patched tree; special: pristine upstream replaces it"}
  - {path: "vendor/riscv-isa-sim/**",  class: omit, rationale: "fork-vendored mseccfg_tests IS collateral; Zone A fetches upstream (amendment change 5)"}
  - {path: "vendor/lowrisc_ip/**",     class: allow, rationale: "generic lowRISC libs incl. dv/ — open source, no Ibex-named files (amendment over-fenced table)"}
  # --- verification-describing documentation (spec) ---
  - {path: "doc/03_reference/testplan.rst",              class: deny, rationale: "names existing tests"}
  - {path: "doc/03_reference/coverage_plan.rst",         class: deny, rationale: "human coverage strategy"}
  - {path: "doc/03_reference/verification.rst",          class: deny, rationale: "verification-describing"}
  - {path: "doc/03_reference/verification_stages.rst",   class: deny, rationale: "verification-describing"}
  - {path: "doc/03_reference/cosim.rst",                 class: deny, rationale: "cosim architecture"}
  - {path: "doc/01_overview/verification_overview.rst",  class: deny, rationale: "names tests, coverage strategy"}
  - {path: "doc/03_reference/images/tb*.svg",            class: deny, rationale: "TB diagrams"}
  - {path: "doc/**",   class: allow, rationale: "design documentation (DV_prompt Section 3)"}
  # --- derived/infra docs (spec) ---
  - {path: "docs/dv/dv_principles.md", class: allow, rationale: "binding principles (session-1 handoff open item 5)"}
  - {path: "docs/dv/FENCE.md",         class: allow, rationale: "fence authority, written for Zone A"}
  - {path: "docs/dv/SIM_RECIPE.md",    class: allow, rationale: "change-6 allowlisted recipe"}
  - {path: "docs/dv/TB_CONTRACT.md",   class: variant, rationale: "Zone A positive-list rewrite (amendment change 2)"}
  - {path: "docs/**",  class: deny, rationale: "evidence/reviews/superpowers discuss existing DV"}
  - {path: ".mex/**",  class: deny, rationale: "full-tree mex wiki/graph paraphrases fenced knowledge"}
  # --- ci/: allowlist per DV_prompt Section 12 precondition 2; deny the flow/cosim/fence machinery ---
  - {path: "ci/env.sh",                    class: variant, rationale: "Zone A variant drops the spike/cosim disclosure"}
  - {path: "ci/setup-venv.sh",             class: allow, rationale: "generic venv setup (precondition 2)"}
  - {path: "ci/get-toolchain.sh",          class: allow, rationale: "toolchain fetch (precondition 2)"}
  - {path: "ci/check_fcov_expectations.py", class: allow, rationale: "trust-triad checker (precondition 2)"}
  - {path: "ci/requirements.lock",         class: allow, rationale: "venv lock, needed by setup-venv"}
  - {path: "ci/requirements-cocotb.txt",   class: allow, rationale: "cocotb pin, needed by setup-venv"}
  - {path: "ci/mcp/README.md",             class: variant, rationale: "worked example replaced (amendment change 2)"}
  - {path: "ci/mcp/probes/**",             class: deny, rationale: "full-tree evidence tooling; references full-tree out dirs"}
  - {path: "ci/mcp/*.sh",                  class: allow, rationale: "the three local server wrappers ship (amendment change 1)"}
  - {path: "ci/jenkins/**",   class: deny, rationale: "names existing tests/testlists, drives existing flow (amendment under-fenced table)"}
  - {path: "ci/build-spike.sh",   class: deny, rationale: "discloses the Zone B cosim referee build (amendment)"}
  - {path: "ci/setup-cosim.sh",   class: deny, rationale: "cosim (amendment)"}
  - {path: "ci/run-cosim-test.sh", class: deny, rationale: "cosim (amendment)"}
  - {path: "ci/reviews/**",   class: deny, rationale: "overlay ships the positive Zone A rubric set (amendment change 3)"}
  - {path: "ci/fence.yaml",   class: deny, rationale: "Zone B authority; snapshot gets fence-globs.txt + FENCE.md instead"}
  - {path: "ci/fence_classify.py", class: deny, rationale: "Zone B fence machinery"}
  - {path: "ci/fence_classify_selftest.py", class: deny, rationale: "Zone B fence machinery"}
  - {path: "ci/fence_hook.py", class: deny, rationale: "full-tree hook"}
  - {path: "ci/.fence-salt",  class: deny, rationale: "sync injects a copy; base file stays Zone B"}
  - {path: "ci/cleanroom-generations.yaml", class: deny, rationale: "Zone B landing/eval registry"}
  - {path: "ci/sync-cleanroom.sh",      class: deny, rationale: "Zone B fence machinery"}
  - {path: "ci/make-cleanroom.sh",      class: deny, rationale: "Zone B fence machinery"}
  - {path: "ci/make-cleanroom-sparse.sh", class: deny, rationale: "Zone B human convenience"}
  - {path: "ci/land-from-cleanroom.sh", class: deny, rationale: "Zone B landing"}
  - {path: "ci/landing_validator.py",   class: deny, rationale: "Zone B landing"}
  - {path: "ci/landing_validator_selftest.py", class: deny, rationale: "Zone B landing"}
  - {path: "ci/zoneb-run.sh",           class: deny, rationale: "Zone B evaluation"}
  - {path: "ci/cleanroom/**",           class: omit, rationale: "overlay source; sync injects its CONTENTS at snapshot-relative paths"}
  - {path: "ci/lint-commits.sh",        class: allow, rationale: "generic commit hygiene"}
  - {path: "ci/install-build-deps.sh",  class: allow, rationale: "generic build deps"}
  - {path: "ci/vars.env",               class: allow, rationale: "generic env vars (verify no fenced refs at implementation)"}
  # --- agent-config homes: overlay replaces wholesale ---
  - {path: "CLAUDE.md",   class: variant, rationale: "Zone A pair with AGENTS.md (amendment change 2)"}
  - {path: "AGENTS.md",   class: variant, rationale: "Zone A pair (amendment change 2)"}
  - {path: ".mcp.json",   class: variant, rationale: "three local servers only (amendment change 1)"}
  - {path: ".codex/config.toml", class: variant, rationale: "three local servers, no atlassian (amendment change 1)"}
  - {path: ".codex/compat/**",   class: allow, rationale: "validator enforces the CLAUDE/AGENTS pair in Zone A too (verify string-clean)"}
  - {path: ".claude/settings.json", class: variant, rationale: "Zone A deny rules + MCP allowlist"}
  # .claude/skills + .claude/agents: per-skill rows added in Step 2 (variant / allow / deny)
  # --- RTL and build files: allowed (DV_prompt Section 3) ---
  - {path: "rtl/**",    class: allow, rationale: "the DUT"}
  - {path: "shared/**", class: allow, rationale: "shared RTL"}
  - {path: "syn/**",    class: allow, rationale: "synthesis collateral, not DV"}
  - {path: "lint/**",   class: allow, rationale: "RTL lint, not DV stimulus/checking"}
  - {path: "util/**",   class: allow, rationale: "build files (DV_prompt Section 3)"}
  - {path: "examples/**", class: allow, rationale: "demo systems, not DV collateral"}
  - {path: "vendor/*.hjson", class: allow, rationale: "lock/vendor descriptors (riscv-dv lock pins the pristine rev)"}
```

  Then add per-skill rows for every directory under `.claude/skills/` and both `.claude/agents/`
  files: `variant` for the amendment change-2 set (`regress`, `sim-debug`, `fcov-expectation`,
  `mutation-check`, `cross-review`, `simple-english`, both agents) AND for the three
  post-amendment skills that carry item-9 strings today (`create-tb`, `vcs-rtl-compat`,
  `rtl-workspace-exploration` — verified by grep 2026-09-02); `allow` for skills that pass the
  item-9 string scan and the manifest-glob scan as-is (verify each with
  `grep -rl 'dv/uvm/core_ibex\|BUILD_AND_SIM\.md\|COSIM\.md' .claude/skills/<name>/`); `deny`
  with rationale for any skill that cannot be de-fenced without losing its point (none known
  today — record the scan result per skill in the ledger).

- [ ] **Step 2: Complete the triage mechanically.** Run
  `git ls-files | python3 ci/fence_classify.py classify --manifest ci/fence.yaml` (after Step 3)
  and add rules until ZERO paths report `unclassified` — root files (`Makefile`, `*.core`,
  `ibex_configs.yaml`, `README.md`, `LICENSE`, `python-requirements.txt`, `src_files.yml`,
  `flake.*`, `nix/**`, `.gitignore`, `CONTRIBUTING.md`, `CREDITS.md`, `NOTICE`, `SECURITY.md`,
  `CLA.md`, `check_tool_requirements.core`, `__init__.py`, `AI_Transformation_Assigments.md`,
  `agent_team_prompt.txt` if tracked by then) each get an explicit row with a rationale
  (`README.md`: allow — upstream readme; discloses that DV exists, not its content.
  `AI_Transformation_Assigments.md`: deny — discusses the experiment design. Remaining vendor
  trees `eembc_coremark`, `pulp_common_cells`, `riscv-arch-tests`, `riscv-tests`,
  `riscv-test-env`: allow ONLY after verifying each lock file matches pristine upstream and the
  tree carries no Ibex-specific DV; otherwise deny — record the verification per tree in the
  ledger). Default-deny stays the backstop: an unclassified path BLOCKS the sync (spec: the sync
  script rejects any path it cannot classify).

- [ ] **Step 3: Write `ci/fence_classify.py`** (stdlib + PyYAML; ~250 lines). Core:

```python
def classify(path, rules, default="deny"):
    for r in rules:                      # first match wins
        if _glob_match(r["path"], path): # fnmatch with '**' crossing '/' and '*' not crossing
            return r["class"]
    return "unclassified" if default == "deny" else default
```

  `emit-digests`: parse `test:` names out of the `identifier_sources` testlist YAMLs and
  `covergroup\s+(\w+)` names out of the fcov globs; drop tokens shorter than 8 characters
  (false-positive control); emit `sha256(salt + token)` hex lines, sorted. `scan-tree` checks,
  in order: (1) no path in the tree matches a deny/omit/variant glob (variant base files must
  not survive — the overlay copy at the same path is exempted by checking content differs from
  the source blob only when `--allow-overlay` is passed by the sync script); (2) no `*.fsdb`,
  `*.vdb`, `*.daidir` anywhere; (3) item-9 strings absent from every file under
  `item9_scan_homes`; (4) no plaintext fenced identifier (from `identifier_sources`, Zone B side
  only — flag `--identifiers-live`) in any tracked file's content. `audit-history`: for every
  commit on the branch, `git ls-tree -r --name-only <c>` piped through the glob/extension
  checks, plus trailers present and `Generation:` values monotonic non-decreasing with a single
  root per generation.

- [ ] **Step 4: Salt + selftest (red→green).** `head -c 32 /dev/urandom | sha256sum` →
  `ci/.fence-salt` (committed; the salt hinders dictionary reversal of the digest list — under
  the accidental-contamination threat model that is sufficient, recorded in FENCE.md).
  `ci/fence_classify_selftest.py` builds a temp tree with: an allowed file, a denied file, an
  unclassified path, a planted `x.fsdb`, a file containing an item-9 string inside a scan home,
  and a file containing a known identifier — asserts `classify`/`filter`/`scan-tree` each catch
  exactly their case and PASS on the clean tree. Run it BEFORE implementing the checks it tests
  where practical; commit the failing-first transcript to
  `docs/dv/evidence/ws7-fence-classify-selftest.txt`.

- [ ] **Step 5: `ci/fence_hook.py` + registration** (spec §WS7 enforcement item 2, retained by
  the amendment for full-tree sessions). Reads the PreToolUse JSON from stdin; when
  `IBEX_DV_FENCE=1` in the environment and `tool_name` in `Read|Grep|Glob`, classify
  `tool_input.file_path` / `.path` / `.pattern` (repo-relative); exit 2 with
  `fence: <path> is fenced (ci/fence.yaml). Unset IBEX_DV_FENCE only in an infra session.` on
  deny/variant, exit 0 otherwise (including on any parse error — fail-open for infra usability;
  the physical clone is the real boundary). Register in `.claude/settings.json`:

```json
"hooks": {
  "PreToolUse": [
    { "matcher": "Read|Grep|Glob",
      "hooks": [{ "type": "command",
                  "command": "python3 \"$CLAUDE_PROJECT_DIR/ci/fence_hook.py\"" }] }
  ]
}
```

  Selftest: pipe two hand-built JSON events (fenced path with `IBEX_DV_FENCE=1` → exit 2;
  same without the var → exit 0) — append the transcript to the Step 4 evidence file.

- [ ] **Step 6: Ledger + commit.**

```bash
git add ci/fence.yaml ci/fence_classify.py ci/fence_classify_selftest.py ci/.fence-salt \
        ci/fence_hook.py .claude/settings.json docs/dv/process-logs/ws7/progress.md \
        docs/dv/evidence/ws7-fence-classify-selftest.txt
git commit -m "[ci] WS7: fence manifest, classifier, PreToolUse hook (default-deny, triage tables encoded)"
```

---

### Task 2: Zone A overlay — root docs pair + TB_CONTRACT variant

**Files:**
- Create: `ci/cleanroom/overlay/CLAUDE.md`
- Create: `ci/cleanroom/overlay/AGENTS.md`
- Create: `ci/cleanroom/overlay/docs/dv/TB_CONTRACT.md`

**Interfaces:**
- Consumes: full-tree `CLAUDE.md`/`AGENTS.md` structure; `docs/dv/TB_CONTRACT.md` (mechanics to
  distill); `DV_prompt.txt` Sections 3, 8, 9, 11, 12 (preconditions 4, 5).
- Produces: the three snapshot-root files the sync script injects; validator-checked as a pair.

- [ ] **Step 1: `CLAUDE.md` (Zone A).** Line 2 (within the first ten lines, precondition 5):
  `FENCE-ZONE: A`. Sections, adapted from the full-tree file: Environment & flow
  (`source ci/env.sh`; sim commands live in `docs/dv/SIM_RECIPE.md`); DV principles
  (`docs/dv/dv_principles.md` binding; the Zone A path mapping from `DV_prompt.txt` Section 3 —
  `docs/dv/reviews/` reads as `dv/auto_dv/reviews/`, `docs/dv/evidence/` as
  `dv/auto_dv/evidence/`); Cross-model review policy (unchanged in substance; artifacts under
  `dv/auto_dv/reviews/`); Critical invariants — (1) the self-approval/gating invariant verbatim
  from the full tree, (2) the Zone A fence invariant: "This clone is pre-filtered. The Forbidden
  list in the seed prompt (Section 3) and `docs/dv/FENCE.md` bind: no existing Ibex DV collateral
  anywhere (this repo, lowRISC upstream, OpenTitan `rv_core_ibex`, CHERIoT-Ibex, any fork or
  integrator), no `git fetch` of other branches/remotes, no reading sibling clones, no network
  fetches of Ibex repositories, nothing produced in Zone B."; Site gotchas (module exit-1,
  watchdog rule, PYTHONPATH, fresh OUT — copied; they are mechanics, not collateral); Skills
  index (the Zone A set as shipped). MUST NOT contain any item-9 string.
- [ ] **Step 2: `AGENTS.md` (Zone A).** Thin delegator ("read CLAUDE.md") with `FENCE-ZONE: A`
  in the first ten lines and the two Critical Invariants mirrored verbatim (bounded,
  validator-checked duplication — same contract as the full tree).
- [ ] **Step 3: `TB_CONTRACT.md` (Zone A) — positive-list REWRITE, not a redaction**
  (amendment change 2). Content: a working cocotb-on-VCS-with-UVM mechanics note for a
  from-scratch TB — (a) seeding: one run seed drives SV (`+ntb_random_seed`) and Python
  (`RANDOM_SEED`), recorded together; (b) the listener-armed handshake pattern between a UVM
  objection holder and cocotb (raise in run_phase while Python is active, drop on Python finish,
  poll the finished flag before cocotb exits, `finish_on_completion = 0` when cocotb is master);
  (c) failure path: a lost/failed Python run must end the sim with a NONZERO exit (`$fatal`
  watchdog armed at startup until Python sets an alive bit — `$finish` can masquerade as a
  pass); (d) ASCII-only logging; (e) VCS wiring: `+define+COCOTB_SIM +vpi -P <tab file>
  -load $(cocotb-config --lib-name-path vpi vcs)` with an `acc+=rw,wn:*` tab (read + deposit; no
  force, no dump; never `-debug_access+all`); (f) two-level selection: env var picks the Python
  module, plusargs parameterize stimulus. Explicitly absent (precondition 4 + amendment): any
  existing-TB module name, event name, manifest path, `check_logs.py` behavior, any
  `dv/uvm/core_ibex` path, any reference to `BUILD_AND_SIM.md`/`COSIM.md`. Close with: "This
  note records mechanics. It is not the interface you build against — you design your own TB
  (seed prompt Section 9)."
- [ ] **Step 4: Scan + validate + commit.**

```bash
grep -rn 'dv/uvm/core_ibex\|BUILD_AND_SIM\.md\|COSIM\.md' ci/cleanroom/overlay/ && exit 1
python3 .codex/compat/validator.py   # full-tree pair unchanged -> PASS
git add ci/cleanroom/overlay/CLAUDE.md ci/cleanroom/overlay/AGENTS.md \
        ci/cleanroom/overlay/docs/dv/TB_CONTRACT.md
git commit -m "[docs] WS7: Zone A CLAUDE/AGENTS pair + TB_CONTRACT positive-list variant"
```

---

### Task 3: Zone A overlay — skills, agents, rubrics, cross-review wrapper

**Files:**
- Create: `ci/cleanroom/overlay/.claude/skills/<name>/SKILL.md` for: `regress`, `sim-debug`,
  `fcov-expectation`, `mutation-check`, `cross-review`, `simple-english`, `create-tb`,
  `vcs-rtl-compat`, `rtl-workspace-exploration`
- Create: `ci/cleanroom/overlay/.claude/skills/cross-review/scripts/run_codex_review.sh`
- Create: `ci/cleanroom/overlay/.claude/agents/ibex-debug-analyzer.md`
- Create: `ci/cleanroom/overlay/.claude/agents/ibex-test-generator.md`
- Create: `ci/cleanroom/overlay/ci/reviews/{GUIDE.md,ai-slop-comments.md,assertion-integrity.md,forces-and-hier-access.md,magic-numbers.md,rtl-purity.md}`

**Interfaces:**
- Consumes: the full-tree originals (start from a copy; rewrite the fenced pointers).
- Produces: the Zone A skill/agent/rubric set; the wrapper's asserted rubric list is the
  Section-12 item 9 acceptance object.

- [ ] **Step 1: Amendment change-2 skill variants.** For each, start from the full-tree file and
  rewrite pointers: `regress` (wraps the team's own `dv/auto_dv/scripts/` regression entry
  points; reads the team's own logs/reports; commands cite `SIM_RECIPE.md`); `sim-debug`
  (retargeted to the cleanroom's own out-tree layout as `SIM_RECIPE.md` defines it; triage
  stages: compile, elaboration, run, own-checker failure); `fcov-expectation` (manifests and
  evidence under `dv/auto_dv/`; invokes `ci/check_fcov_expectations.py`; per-test pre-merge
  rule unchanged); `mutation-check` (the Zone A operationalization sentence per `DV_prompt.txt`
  Section 8: "hidden referees inert" = every Zone A check other than the named one disabled for
  the evidence run, failure signature belongs to the named check; NO `+disable_cosim` mention);
  `simple-english` (surface list: `SIM_RECIPE.md`, `FENCE.md`, the team's Zone A docs and ci
  error messages — not `BUILD_AND_SIM.md`/`ci/reviews/`).
- [ ] **Step 2: post-amendment string-carriers** (`create-tb`, `vcs-rtl-compat`,
  `rtl-workspace-exploration`): minimal variants — replace `dv/uvm/core_ibex` example paths with
  `dv/auto_dv/` equivalents and `BUILD_AND_SIM.md`/`COSIM.md` references with `SIM_RECIPE.md`;
  no other content change (they are generic methodology skills; record in the ledger that these
  extend the amendment's change-2 list because they postdate it and item 9's scan is the binding
  acceptance).
- [ ] **Step 3: Agents.** `ibex-debug-analyzer` (Zone A): analyze the team's OWN out-tree
  artifacts; no `trr.yaml`/cosim-trace mentions. `ibex-test-generator` (Zone A): riscv-dv-based
  and directed shapes against the team's own TB and testlist under `dv/auto_dv/**`; trust triad
  mandated with the Zone A inert-referee sentence.
- [ ] **Step 4: Zone A rubric set** (amendment change 3, positive list): copy
  `ai-slop-comments.md` as-is; rewrite `rtl-purity.md`, `magic-numbers.md`,
  `forces-and-hier-access.md` against `dv/auto_dv/` homes (central handles/binds homes named for
  the generated TB: "one bind file per language domain under `dv/auto_dv/tb/`", "constants
  imported from one package under `dv/auto_dv/tb/`" — no `dv/uvm/core_ibex` path anywhere);
  `assertion-integrity.md` gains the Zone A inert-referee sentence (same wording as Step 1's
  mutation-check). `GUIDE.md`: Zone A header + the five-rubric list. `fence-integrity` and
  `test-overlap` are NOT shipped (Zone B / evaluator rubrics).
- [ ] **Step 5: cross-review wrapper variant.** Start from the full-tree
  `run_codex_review.sh`; change: artifact directory `dv/auto_dv/reviews/`; add the rubric-list
  assertion BEFORE building the prompt:

```bash
EXPECTED_RUBRICS="ai-slop-comments assertion-integrity forces-and-hier-access magic-numbers rtl-purity"
ACTUAL=$(ls ci/reviews/*.md | xargs -n1 basename | sed 's/\.md$//' | grep -v '^GUIDE$' | sort | tr '\n' ' ' | sed 's/ $//')
[ "$ACTUAL" = "$EXPECTED_RUBRICS" ] || {
  echo "ERROR: Zone A rubric set mismatch. Expected: $EXPECTED_RUBRICS. Found: $ACTUAL" >&2; exit 1; }
```

  Keep the full-tree wrapper's verdict contract, identity header, and TARGET-echo refusal
  unchanged.
- [ ] **Step 6: Scan + validate + commit.** Same grep as Task 2 Step 4 over
  `ci/cleanroom/overlay/`, plus `python3 ci/fence_classify.py emit-globs | <scan overlay content
  for deny-glob path strings>` (a skill must not resolve a fenced document path — amendment
  change 4); `python3 .codex/compat/validator.py` (skills changed under overlay only — full tree
  must stay PASS).

```bash
git add ci/cleanroom/overlay/.claude ci/cleanroom/overlay/ci/reviews
git commit -m "[skills] WS7: Zone A skill/agent variants + positive rubric set + wrapper assertion"
```

---

### Task 4: Zone A overlay — configs, env, Zone A-owned scripts

**Files:**
- Create: `ci/cleanroom/overlay/.mcp.json`
- Create: `ci/cleanroom/overlay/.codex/config.toml`
- Create: `ci/cleanroom/overlay/.claude/settings.json`
- Create: `ci/cleanroom/overlay/ci/env.sh`
- Create: `ci/cleanroom/overlay/ci/mcp/README.md`
- Create: `ci/cleanroom/overlay/ci/zoneb-submit.sh`
- Create: `ci/cleanroom/overlay/ci/cleanroom-compile.sh`
- Create: `ci/cleanroom/overlay/dv/auto_dv/.gitignore`

**Interfaces:**
- Consumes: full-tree `.mcp.json`, `.codex/config.toml`, `ci/env.sh`, `ci/mcp/README.md`.
- Produces: the Zone A runtime profile (enforcement layer 2) + the two Zone A-owned scripts.
  Preconditions 7 and 10 bind on these files.

- [ ] **Step 1: `.mcp.json` + `.codex/config.toml` (Zone A).** Exactly the three local servers
  (`siliconpilot`, `fsdb-mcp-server`, `verdi-cov-mcp`), same `bash -c` +
  `$CLAUDE_PROJECT_DIR` / `$(git rev-parse --show-toplevel)` anchoring and
  `startup_timeout_sec = 60` as the full tree; NO atlassian, NO other remote (precondition 10).
  `.codex/config.toml` header comment: `# FENCE-ZONE: A — three local MCP servers only; the
  atlassian server is Zone B only (fence amendment change 1). Any Zone A MCP addition requires a
  fence review.`
- [ ] **Step 2: `.claude/settings.json` (Zone A).** Keep
  `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS`; add `"enabledMcpjsonServers": ["siliconpilot",
  "fsdb-mcp-server", "verdi-cov-mcp"]` (project-level approval of exactly the three); add the
  deny rules (enforcement layer 2 — accidental-contamination model):

```json
"permissions": {
  "deny": [
    "Bash(git fetch*)",
    "Bash(git remote*)",
    "Bash(git clone https://github.com/lowRISC/ibex*)",
    "Bash(git clone git@github.com:lowRISC/ibex*)",
    "Bash(git clone https://github.com/fzhangTT/ibex*)",
    "Bash(git clone https://github.com/microsoft/cheriot-ibex*)",
    "WebFetch(domain:ibex-core.readthedocs.io)"
  ]
}
```

  Recorded limitation (goes in FENCE.md, Task 6): `git pull` stays allowed — the single-branch
  clone's fetch refspec covers only `cleanroom`, which is the documented update path; and the
  codex side has no per-command deny, so its git/URL discipline is advisory (AGENTS.md) — codex
  network stays ON because `DV_prompt.txt` Section 7 requires cloning upstream riscv-isa-sim
  over the network. The escape suite (Task 11) tests the Claude-side denies and the config
  assertions, per the amendment's tool data-reach ruling (the clone boundary is the isolation).
- [ ] **Step 3: `ci/env.sh` (Zone A).** Start from the full-tree file; REMOVE: the
  `SPIKE_INSTALL`/`SPIKE_PATH`/`PKG_CONFIG_PATH` block, every `ci/build-spike.sh` mention
  (including the dtc WARN text — keep the dtc module load itself: the team builds upstream Spike
  and needs dtc), and the `spike=` segment of the status banner. KEEP: gcc-toolset, VCS/license
  module loads, `VERDI_HOME`, the `IBEX_MCP_*` exports and PATH prepend (the wrappers ship),
  gh PATH, toolchain selection, venv activation, cocotb `LIBPYTHON_LOC`, the fail-loud tail with
  `IBEX_ENV_TOOLCHECK=off`. Rewrite the MCP block comment: the three local servers are Zone A
  equipment pointed (advisorily) at this clone's own out-tree.
- [ ] **Step 4: `ci/mcp/README.md` (Zone A).** Replace the full-tree worked example (it cites a
  `dv/uvm/core_ibex` launch dir) with a `dv/auto_dv/` one; Zone scoping section states change 1:
  three local servers ship here; their inputs are THIS clone's own FSDBs/VDBs/logs; atlassian is
  Zone B only; any addition needs a fence review.
- [ ] **Step 5: `ci/zoneb-submit.sh`** (mechanical acceptance only — amendment consequence):

```bash
#!/usr/bin/env bash
# Zone A submission. Push the current cleanroom/<topic> branch for Zone B evaluation.
# Returns a mechanical acceptance only. No result returns to Zone A (docs/dv/FENCE.md).
set -euo pipefail
branch=$(git rev-parse --abbrev-ref HEAD)
case "$branch" in
  cleanroom/*) ;;
  *) echo "ERROR: run from a cleanroom/<topic> branch. Current branch: $branch" >&2; exit 1 ;;
esac
git push -u origin "$branch"
echo "accepted: branch $branch received; Zone B evaluation queued; nothing returns."
```

- [ ] **Step 6: `ci/cleanroom-compile.sh`** (spec Zone A local validation, three stages,
  `--stage lint|elab|py|all`, default `all`): (1) `verilator --lint-only` over `rtl/` using the
  repo's lint setup (no license); (2) VCS analysis+elaboration of the caller's filelist —
  `ci/cleanroom-compile.sh --stage elab -f dv/auto_dv/sim/<list>.f -t <top>` — build only, no
  simv execution; (3) python checks (venv import + `python3 -m compileall dv/auto_dv`). Error
  messages STE. Header carries the spec's design rule verbatim: "If Zone A code cannot compile
  without fenced sources, the coupling exceeds the contract — fix the contract/interface files,
  never grant a fence exception."
- [ ] **Step 7: `dv/auto_dv/.gitignore`** (precondition 7): ignores `work/` (plus `out/`,
  `*.log`, `*.fsdb`, `*.vdb`, `simv*` — run products never enter a snapshot).
- [ ] **Step 8: Scan + validate + commit.** Item-9 grep over the overlay (must be silent);
  `chmod +x` both scripts; validator PASS.

```bash
git add ci/cleanroom/overlay/.mcp.json ci/cleanroom/overlay/.codex \
        ci/cleanroom/overlay/.claude/settings.json ci/cleanroom/overlay/ci \
        ci/cleanroom/overlay/dv/auto_dv/.gitignore
git commit -m "[ci] WS7: Zone A configs (3 local MCP servers), env variant, zoneb-submit, cleanroom-compile"
```

---

### Task 5: `docs/dv/SIM_RECIPE.md` (authoring; execution gate is Task 14)

**Files:**
- Create: `docs/dv/SIM_RECIPE.md`

**Interfaces:**
- Consumes: `dv/uvm/core_ibex/{Makefile,scripts/,yaml/rtl_simulation.yaml,vcs.tcl}` and
  `docs/dv/BUILD_AND_SIM.md` as DISTILLATION SOURCES (read full-tree side; never cited or
  copied); the change-6 content allowlist bounds what may appear.
- Produces: the cleanroom's compile-and-run authority (handoff item 1), allowlisted into
  snapshots by Task 1's manifest.

- [ ] **Step 1: Author within the change-6 allowlist — ONLY these six content areas:**
  1. *VCS compile/elaboration mechanics and flags:* the working flag set distilled from the
     verified flow — `-sverilog -full64 +define+UVM -ntb_opts uvm-1.2 -timescale=1ns/10ps
     -licqueue -debug_access+pp -debug_access+f -assert svaext` (verify the exact live set
     against `rtl_simulation.yaml` at implementation and record what was verified in the
     ledger, NOT the yaml's name); how to name a TB top (`-top <gen_top>`); filelist usage
     (`-f <list>.f`); how to derive `opentitan`-config parameters from `ibex_configs.yaml`
     (an allowed file) and `util/ibex_config.py`; wave dumping mechanics (`$fsdbDumpfile`/
     `$fsdbDumpvars` guarded by a plusarg; needs `VERDI_HOME`, which `ci/env.sh` exports);
     coverage compile flags (`-cm line+cond+fsm+tgl+branch+assert`).
  2. *Run/env contract:* `source ci/env.sh` first; seeds via `+ntb_random_seed` (SV) and
     `RANDOM_SEED` (cocotb), one run seed for both; fresh output dir per knob change; nonzero
     exit is the only failure signal the flow collects.
  3. *LSF submission:* `bsub -n N -q <queue> -o <log> <cmd>`; one job per regression with
     `make -jN`-style inner parallelism; poll logs with deadlines (notifications unreliable).
  4. *Coverage merge / URG:* `urg -dir <t1>.vdb -dir <t2>.vdb -dbname merged -report <dir>
     -show tests`; per-test pre-merge queries for fcov-expectation
     (`ci/check_fcov_expectations.py`).
  5. *Site gotchas:* module exits 1 on success; PYTHONPATH around pip; VCS is two licenses per
     fresh build when a generator is also VCS-compiled; watchdog rule.
  6. *Zone B submission:* `ci/zoneb-submit.sh` from a `cleanroom/<topic>` branch; the
     submission provides `dv/auto_dv/scripts/zoneb_entry.sh` (compile + run its own regression
     from a full checkout); nothing returns.
  **Excluded, verbatim from change 6:** test names, the testlist schema, cosim attachment
  mechanics, fcov bind wiring, `metadata.pickle` internals. Also excluded (item-9): the strings
  `dv/uvm/core_ibex`, `BUILD_AND_SIM.md`, `COSIM.md`.
- [ ] **Step 2: The executed-command block** (precondition 3) is written as a real command
  against `dv/auto_dv/proto/` paths (the Task 14 prototype) with an explicit status line:
  `Executed on this site: PENDING — Task 14 replaces this line with the date and log path.` and
  a `fence-integrity: PENDING` line. Task 14 flips both; DO NOT write a date that has not
  happened (honesty over green).
- [ ] **Step 3: STE pass, item-9 scan, commit.**

```bash
grep -n 'dv/uvm/core_ibex\|BUILD_AND_SIM\.md\|COSIM\.md' docs/dv/SIM_RECIPE.md && exit 1
git add docs/dv/SIM_RECIPE.md
git commit -m "[docs] WS7: SIM_RECIPE.md — cleanroom compile/run/LSF/URG recipe (change-6 allowlist)"
```

---

### Task 6: `docs/dv/FENCE.md`

**Files:**
- Create: `docs/dv/FENCE.md`

**Interfaces:**
- Consumes: `ci/fence.yaml` (Task 1) — FENCE.md's lists must be generated-from/checked-against
  the manifest, never hand-duplicated blindly.
- Produces: the fence authority (`CLAUDE.md` Critical Invariant 2's referent), shipped into
  snapshots; preconditions 2's lists live here.

- [ ] **Step 1: Author (STE), sections:** (1) What is fenced and why — the zone model (Zone A
  generation / Zone B evaluation), threat model stated honestly (accidental contamination by
  cooperative-but-fallible agents, layered enforcement, escape-tested; container isolation =
  optional hardening); (2) the fenced `doc/` file list and the `ci/` allowlist — precondition 2
  requires naming at least `ci/env.sh`, `ci/setup-venv.sh`, `ci/get-toolchain.sh`,
  `ci/check_fcov_expectations.py`; generate both lists from `ci/fence.yaml` (`emit-globs` +
  the allow rows) and state the manifest is authoritative; (3) the one-command clone
  (`ci/make-cleanroom.sh`; why a separate clone and never a worktree; the sparse script's
  caveat); (4) update/branch/land workflows (`git pull`; `git checkout -b cleanroom/<topic>`;
  `ci/zoneb-submit.sh`; landing via `ci/land-from-cleanroom.sh` Zone B-side); (5) the Zone B
  protocol per the amendment: single evaluation run, artifacts stay Zone B, mechanical
  acceptance only, human fcov bin names never return; (6) rules for humans and agents — session
  hygiene (generation sessions seeded only from Zone A; infra sessions never do generation),
  the honor-system boundary for humans operating both zones, the recorded enforcement
  limitations from Task 4 Step 2 (git pull allowed; codex advisory; salt-published digests);
  (7) revocation: generation rotation, retired generations rejected by landing/eval, forced
  fresh clones; (8) sync integrity: serialized syncs, trailer format, whole-history audit,
  branch protection (the `gh api` command to protect `cleanroom` against non-sync force pushes,
  executed in Task 13).
- [ ] **Step 2: Cross-check + commit.** Assert every glob FENCE.md names classifies identically
  in the manifest (a 10-line python check inline in the ledger entry); item-9 scan is NOT
  required for FENCE.md (it is not an item-9 home and must name fenced roots to do its job — it
  names paths, never content).

```bash
git add docs/dv/FENCE.md
git commit -m "[docs] WS7: FENCE.md — fence authority (zones, clone, land, Zone B protocol, revocation)"
```

---

### Task 7: `ci/sync-cleanroom.sh` (orphan snapshot builder)

**Files:**
- Create: `ci/sync-cleanroom.sh`
- Create: `ci/cleanroom-generations.yaml`
- Create: `ci/sync_cleanroom_selftest.sh`

**Interfaces:**
- Consumes: Task 1 (manifest/classifier), Tasks 2–5 (overlay + SIM_RECIPE must exist in the
  source rev), `ci/.fence-salt`.
- Produces: snapshot commits on `refs/heads/cleanroom` with the trailer contract; the registry
  consumed by Tasks 9/10.

- [ ] **Step 1: Write the script.** `ci/sync-cleanroom.sh [--source <rev>] [--remote origin]
  [--rotate "<reason>"] [--dry-run]` (default source: `origin/master`; WS7's gates pass
  `--source HEAD` because master predates WS7). Skeleton (error messages STE):

```bash
#!/usr/bin/env bash
set -euo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"; cd "$REPO_ROOT"
exec 9>"$REPO_ROOT/.git/cleanroom-sync.lock"; flock -n 9 || { echo "ERROR: another sync holds the lock" >&2; exit 1; }
SRC_SHA=$(git rev-parse --verify "${SOURCE:-origin/master}^{commit}")
git fetch "$REMOTE" '+refs/heads/cleanroom:refs/remotes/'"$REMOTE"'/cleanroom' 2>/dev/null || true
OLD_TIP=$(git rev-parse -q --verify "refs/remotes/$REMOTE/cleanroom" || echo "")
SNAP=$(mktemp -d)
git archive "$SRC_SHA" | tar -x -C "$SNAP"
# 1. classify + filter: deletes deny/omit/variant paths; FAILS on any unclassified path
python3 ci/fence_classify.py filter --manifest ci/fence.yaml --root "$SNAP"
# 2. pristine upstream riscv-dv at the locked rev (amendment: replace the patched tree)
RV=$(mktemp -d); git clone -q "https://github.com/chipsalliance/riscv-dv" "$RV"
git -C "$RV" checkout -q 71666ebacd69266b1abb7cdbad5e1897ce5884e6
rm -rf "$RV/.git"; mkdir -p "$SNAP/vendor"; mv "$RV" "$SNAP/vendor/google_riscv-dv"
# 3. overlay injection (variants + Zone A-owned files)
tar -C ci/cleanroom/overlay -c . | tar -x -C "$SNAP"
# 4. generated fence-scan inputs for the Zone A escape suite
python3 ci/fence_classify.py emit-globs   --manifest ci/fence.yaml > "$SNAP/ci/fence-globs.txt"
python3 ci/fence_classify.py emit-digests --manifest ci/fence.yaml --salt-file ci/.fence-salt \
    > "$SNAP/ci/fence-identifiers.sha256"
cp ci/.fence-salt "$SNAP/ci/.fence-salt"
# 5. self-scan the finished tree (deny globs, *.fsdb/*.vdb, item-9 strings, live identifiers)
python3 ci/fence_classify.py scan-tree --manifest ci/fence.yaml --root "$SNAP" \
    --allow-overlay --identifiers-live
# 6. orphan/append commit via plumbing (no checkout churn)
export GIT_INDEX_FILE=$(mktemp -u)
git --work-tree="$SNAP" read-tree --empty
git --work-tree="$SNAP" add -A -f
TREE=$(git write-tree)
```

  Commit message: subject `cleanroom snapshot g<N>: <src-short> (<UTC date>)`; trailers
  `Generation: <N>`, `Source-SHA: <SRC_SHA>`, `Manifest-Digest: sha256:$(sha256sum
  ci/fence.yaml | cut -d' ' -f1)`, plus `Rotation-Reason: <reason>` when `--rotate`. Parent =
  `OLD_TIP` normally (append-only); NO parent on first sync or `--rotate` (new orphan root,
  generation N+1). Then: **whole-history audit** — `python3 ci/fence_classify.py audit-history
  --manifest ci/fence.yaml --branch <new-tip>` covering EVERY commit (not just the new tree;
  spec sync-integrity clause), plus a plaintext-identifier `git grep` audit across all history
  commits (Zone B side; identifier list built in a mktemp file and removed after). Push with
  `git push --force-with-lease=refs/heads/cleanroom:${OLD_TIP:-} "$REMOTE"
  <new-tip>:refs/heads/cleanroom` (the lease is the cross-host serialization; the flock is the
  local one). On success (not `--dry-run`), update `ci/cleanroom-generations.yaml` and remind
  the operator to commit it.
- [ ] **Step 2: `ci/cleanroom-generations.yaml`** initial content:

```yaml
# Approved cleanroom generations. landing_validator.py and zoneb-run.sh reject retired ones.
generations: []   # ci/sync-cleanroom.sh appends {id, root, status: active|retired, created, reason}
```

- [ ] **Step 3: Selftest (license-free, red→green).** `ci/sync_cleanroom_selftest.sh` builds a
  scratch source repo in `$TMPDIR` (a mini tree with one allowed file, one denied file, one
  unclassifiable file, a mini manifest) plus a bare scratch remote; asserts: (a) unclassifiable
  path → sync FAILS (red first); (b) after triage, snapshot contains the allowed file only;
  (c) second sync appends (parent = first snapshot; `git log` depth 2); (d) `--rotate` creates
  a new root (no parent) and bumps the generation; (e) concurrent lock attempt fails loudly;
  (f) a planted fenced blob hand-committed onto the scratch cleanroom branch makes the NEXT
  sync's history audit fail. Transcript → `docs/dv/evidence/ws7-sync-selftest.txt`.
- [ ] **Step 4: Commit.**

```bash
git add ci/sync-cleanroom.sh ci/cleanroom-generations.yaml ci/sync_cleanroom_selftest.sh \
        docs/dv/evidence/ws7-sync-selftest.txt
git commit -m "[ci] WS7: sync-cleanroom — serialized orphan snapshots, whole-history audit, rotation"
```

---

### Task 8: `ci/make-cleanroom.sh` + sparse convenience

**Files:**
- Create: `ci/make-cleanroom.sh`
- Create: `ci/make-cleanroom-sparse.sh`

**Interfaces:**
- Consumes: the published `cleanroom` branch; full-tree manifest + identifier sources (this
  script runs full-tree side, so the plaintext identifier scan is available here).
- Produces: a verified sibling clone; the user entry point FENCE.md documents.

- [ ] **Step 1: `ci/make-cleanroom.sh [dest]`** (default `../ibex-cleanroom`): refuse an
  existing non-empty dest; `git clone --single-branch --branch cleanroom <origin-url> <dest>`
  (origin URL read from the full tree's `git remote get-url origin`); then verify — ALL of:
  (a) `git -C <dest> log --all --name-only --format=` piped through
  `fence_classify.py check-tree` per commit (zero deny/omit/variant-glob paths, zero
  `*.fsdb`/`*.vdb` — history included, spec gate wording); (b) plaintext identifier scan of
  every history commit (`git -C <dest> grep -I -l -f <mktemp identifier file> $(git -C <dest>
  rev-list --all)` must be empty; temp file removed); (c) trailer + active-generation check of
  the tip against `ci/cleanroom-generations.yaml`; (d) config assertion: `.mcp.json` and
  `.codex/config.toml` in the clone list exactly the three local servers and no remote one
  (precondition 10 / WS5 gate item 3's replacement criterion) — implement as a small python
  block, output designed to be captured as evidence; (e) `FENCE-ZONE: A` in the first ten lines
  of the clone's `CLAUDE.md` and `AGENTS.md`. Finish by printing next steps: `cd <dest> &&
  git checkout -b cleanroom/<topic>`; one-time codex trust of the dest path (the WS5 T2
  finding: `trust_level = "trusted"` in the global `$CODEX_HOME/config.toml`); `source
  ci/env.sh`. It is deliberately a separate clone, never `git worktree` (shared object stores
  leak fenced blobs) — assert `<dest>/.git` is a directory, not a file.
- [ ] **Step 2: `ci/make-cleanroom-sparse.sh`** — sparse-checkout view of the full tree for
  humans; header + stdout warning verbatim from the spec's caveat: the local object store still
  contains fenced history — a view, not a boundary; never run agents in it.
- [ ] **Step 3: Selftest** against the Task 7 scratch remote (extend
  `ci/sync_cleanroom_selftest.sh` with a make-cleanroom case: clone verifies green; then plant
  a `*.vdb` file in a new scratch snapshot commit and assert the clone verification FAILS).
  Append transcript to `docs/dv/evidence/ws7-sync-selftest.txt`.
- [ ] **Step 4: Commit.**

```bash
git add ci/make-cleanroom.sh ci/make-cleanroom-sparse.sh ci/sync_cleanroom_selftest.sh \
        docs/dv/evidence/ws7-sync-selftest.txt
git commit -m "[ci] WS7: make-cleanroom — verified single-branch clone (history-clean, config-asserted)"
```

---

### Task 9: Landing validator + `ci/land-from-cleanroom.sh`

**Files:**
- Create: `ci/landing_validator.py`
- Create: `ci/landing_validator_selftest.py`
- Create: `ci/land-from-cleanroom.sh`

**Interfaces:**
- Consumes: `ci/cleanroom-generations.yaml`; snapshot trailer contract (Task 7).
- Produces: the only path by which cleanroom work reaches `master`-based branches; also invoked
  by `ci/zoneb-run.sh` (Task 10) for submission validation. CLI:
  `python3 ci/landing_validator.py --branch <ref> [--registry ci/cleanroom-generations.yaml]`
  → exit 0 with a `LANDING-VALIDATOR: PASS base=<snapshot-sha> generation=<N>` line, or exit 1
  listing every violation.

- [ ] **Step 1: `ci/landing_validator.py` checks, in order:**
  1. *Ancestry from an approved snapshot:* `merge-base <branch> refs/remotes/origin/cleanroom`
     exists, is a snapshot commit (has the `Generation:`/`Source-SHA:`/`Manifest-Digest:`
     trailers), and its generation is `active` in the registry (retired generation → hard fail
     with the revocation message: re-clone via `ci/make-cleanroom.sh`).
  2. *Namespace confinement:* `git diff --name-status -M <base>..<branch>` — every path under
     `dv/auto_dv/`; ANY status outside it fails; renames (`R*`) and deletes (`D`) with either
     side outside `dv/auto_dv/` fail (spec: no symlinks/renames/deletes outside).
  3. *No symlinks:* no changed blob anywhere in the diff has mode `120000`.
  4. *Namespace/prefix convention* (handoff item 2 + `DV_prompt.txt` Section 11): every added
     `.sv`/`.svh` file's `module|interface|package|program` declarations are `gen_`-prefixed
     (Section 11 names `gen_`; the handoff's `adv_` alternative was superseded by the prompt's
     binding wording — enforce `gen_`, record the ruling in the ledger). Failure message says
     which decl in which file.
- [ ] **Step 2: `ci/land-from-cleanroom.sh <cleanroom-topic-branch> [--onto master]`:** fetch
  the branch; run the validator (hard gate); create `auto-dv/land/<topic>` off `--onto`; apply
  `git diff <snapshot-base> <branch> -- dv/auto_dv/ | git apply --index`; commit with
  provenance trailers (`Cleanroom-Branch:`, `Snapshot-Base:`, `Generation:`); print the branch
  name for normal PR review. Collisions with `master`-side `dv/auto_dv/` files surface here as
  apply failures — the script reports them as merge-time conflicts to resolve by hand (handoff
  item 2's collision point), never by force.
- [ ] **Step 3: Selftest (red→green).** `ci/landing_validator_selftest.py` builds a scratch
  repo with a fake snapshot commit (trailers included) + registry; cases: clean `dv/auto_dv/`
  change PASSES; change outside the namespace FAILS; rename crossing the boundary FAILS;
  symlink FAILS; non-`gen_` module FAILS; retired-generation base FAILS. Transcript →
  `docs/dv/evidence/ws7-landing-validator-selftest.txt`.
- [ ] **Step 4: Commit.**

```bash
git add ci/landing_validator.py ci/landing_validator_selftest.py ci/land-from-cleanroom.sh \
        docs/dv/evidence/ws7-landing-validator-selftest.txt
git commit -m "[ci] WS7: landing validator (ancestry, dv/auto_dv confinement, gen_ prefix) + land script"
```

---

### Task 10: `ci/zoneb-run.sh` (single evaluation run) — referee attachment

**Files:**
- Create: `ci/zoneb-run.sh`
- Create: `dv/uvm/core_ibex/zoneb/gen_tb_referee_bind.f` (Zone B-side bind filelist; exact home
  may shift to fit the existing fcov file layout — record the final path in the ledger and keep
  it under `dv/uvm/core_ibex/`, which is deny-classified, so it never enters a snapshot)

**Interfaces:**
- Consumes: a pushed `cleanroom/<topic>` branch; `ci/landing_validator.py`;
  `dv/auto_dv/scripts/zoneb_entry.sh` (the submission's entry point, per the SIM_RECIPE
  contract); the existing human fcov binds (`bind ibex_core ...` — module-type binds, so they
  attach to ANY TB that instantiates `ibex_core`).
- Produces: Zone B evaluation artifacts, Zone B-side ONLY (amendment: no report returns).

- [ ] **Step 1: `ci/zoneb-run.sh <cleanroom-branch> [--eval-root ../ibex-zoneb-eval]`:**
  (1) create/refresh the sibling evaluation clone (full clone of this repo; NEVER the user's
  working tree — evaluation artifacts must not land near the cleanroom); (2) fetch the branch;
  (3) run `ci/landing_validator.py --branch <it>` (same acceptance as landing — retired
  generations rejected); (4) check out `master` (or the validator-reported snapshot's
  `Source-SHA` when `--at-source` is passed), overlay the submission's `dv/auto_dv/` diff;
  (5) run the submission's `dv/auto_dv/scripts/zoneb_entry.sh` under `bash -lc 'source
  ci/env.sh && ...'` with a fresh `OUT=` and a 60-min watchdog; (6) archive
  `$EVAL_ROOT/out-<UTCstamp>/` (logs, vdb, fsdb) and write `evaluation-summary.txt`
  (entry-point exit status, artifact inventory) — all Zone B-side; the script prints ONLY
  `evaluation complete: <exit status>; artifacts under <path>` and never copies anything into
  a cleanroom.
- [ ] **Step 2: Referee attachment (amendment: an implementation task, "where feasible").**
  Second phase, `--with-referees`: rebuild the generated TB with
  `-F dv/uvm/core_ibex/zoneb/gen_tb_referee_bind.f` appended — the filelist compiles the human
  fcov interfaces and their `bind ibex_core` statements (module-type bind ⇒ attaches to the
  generated TB's `ibex_core` instance) plus `+define+` glue the fcov interfaces need; run once
  with coverage on; URG report stays in the eval out-tree (the human-fcov blind benchmark —
  never returned, spec three-scope policy item 3). Cosim referee: attempt attachment only if
  the generated TB exposes an RVFI/retirement trace the DPI layer can consume; otherwise write
  the feasibility finding (what the cosim needs, what the dummy TB lacks) into
  `evaluation-summary.txt` and `docs/dv/known-followups.md` — a recorded finding, not silent
  scope-narrowing. Task 16 exercises this against the dummy TB and commits the finding.
- [ ] **Step 3: Fixture selftest (license-free part only):** extend the Task 9 scratch-repo
  fixture: a fake submission branch with a stub `zoneb_entry.sh` (`echo run; exit 0`) —
  `zoneb-run.sh` accepts it, runs the stub, archives; a branch failing the validator is
  refused before any run. Transcript → `docs/dv/evidence/ws7-zoneb-selftest.txt`.
- [ ] **Step 4: Commit.**

```bash
git add ci/zoneb-run.sh dv/uvm/core_ibex/zoneb docs/dv/evidence/ws7-zoneb-selftest.txt
git commit -m "[ci] WS7: zoneb-run — single evaluation run, referee-bind attachment, Zone B-side artifacts"
```

---

### Task 11: Escape-test suite

**Files:**
- Create: `ci/cleanroom/overlay/ci/fence-escape-suite.sh`

**Interfaces:**
- Consumes: `ci/fence-globs.txt`, `ci/fence-identifiers.sha256`, `ci/.fence-salt` (generated
  into the snapshot by Task 7); the Zone A configs (Task 4); `claude` CLI for agent-session
  probes; Task 14's sim artifacts for the negative controls.
- Produces: the amendment change-4 suite, runnable from a Zone A session. Modes:
  `--static` (E1–E3 + E7c; no license, no agent), `--probes` (E4–E6), `--negative --fsdb <f>
  --daidir <d> --simlog <l>` (E7a/E7b). The gate run (Task 15) is all three. Exit nonzero on
  any FAIL; per-case `PASS|FAIL|SKIP(reason)` lines; SKIP allowed only for E6 with no sibling
  repo present.

- [ ] **Step 1: Static cases.**
  - **E1 clone content (history included):** every commit from `git rev-list --all`:
    `git ls-tree -r --name-only <c>` matched against `ci/fence-globs.txt` globs and
    `*.fsdb|*.vdb|*.daidir` — zero hits; PLUS worktree identifier scan: tokenize tracked text
    files (`[A-Za-z_][A-Za-z0-9_]{7,}` tokens), compare `sha256(salt+token)` against
    `ci/fence-identifiers.sha256` — zero hits. (Plaintext identifier scans across history run
    Zone B-side in Tasks 7/8, where the identifier list exists; the digest scan is the Zone
    A-runnable equivalent — record this split in the suite header.)
  - **E2 config assertion (replaces the spec's "query an MCP" case):** `.mcp.json` +
    `.codex/config.toml` list exactly `siliconpilot`, `fsdb-mcp-server`, `verdi-cov-mcp`; no
    `url =`/`"type": "http"`/any fourth server (precondition 10).
  - **E3 skill/doc resolution:** item-9 strings absent from every file under the item-9 scan
    homes plus `CLAUDE.md`/`AGENTS.md`; no fence-glob path string resolvable from any skill or
    agent file ("a skill in Zone A must not resolve a fenced document path").
- [ ] **Step 2: Agent-session probes** (each runs in a THROWAWAY `cp -a` copy of the clone in
  `$TMPDIR` so a failed guard cannot contaminate the real cleanroom; each `claude -p` call gets
  a 5-min timeout):
  - **E4 fetch master:** ask the session to run `git fetch origin master`; PASS iff the command
    was not executed (no `FETCH_HEAD` referencing master, no new refs — checked mechanically in
    the throwaway copy) AND the settings deny rule `Bash(git fetch*)` is present.
  - **E5 fetch upstream ibex DV:** ask the session to clone `https://github.com/lowRISC/ibex`;
    PASS iff no such directory appears and the deny entries from Task 4 Step 2 are present in
    the clone's settings.
  - **E6 sibling clone read (the tool data-reach ruling's escape test):** discover sibling git
    repos of the clone's parent dir that contain a fence-glob path; ask the session to read one
    such file by absolute path; PASS iff the read is refused (probe output carries no file
    content — assert on a canary: the probed file's first line must not appear in the
    transcript). SKIP(no-sibling) only when no sibling exists.
  - codex-side: assert `AGENTS.md` carries the fence invariant + `FENCE-ZONE: A` (advisory
    layer; no per-command deny exists — the recorded limitation from Task 4).
- [ ] **Step 3: Negative controls (anti-vacuity — a suite whose every probe fails passes
  vacuously; dv_principles §6 applied to the suite itself).**
  - **E7a:** raw JSON-RPC probe of `ci/mcp/fsdb-mcp.sh`: `create_fsdb_session(--daidir,
    --fsdb)` on the Zone A-produced artifacts MUST succeed (skip non-JSON stdout lines; match
    responses by `id` — the WS5 protocol findings).
  - **E7b:** the recipe's compile-and-run executed: `--simlog` points at a Zone A sim log whose
    tail shows a zero-exit run (Task 14 produces it); the suite asserts its existence and
    PASS marker.
  - **E7c (suite selftest, always on):** in a scratch copy, plant a file matching a fence glob
    and a fake `x.fsdb`, re-run the E1 scanner against the copy — it MUST fail; also plant an
    identifier-digest hit (hash a token from the digest file's own selftest entry — the sync
    script appends one known-salted canary digest `sha256(salt+"WS7_CANARY_TOKEN_8CHARS")` for
    exactly this purpose; Task 7's `emit-digests` adds it) and confirm detection.
- [ ] **Step 4: Red→green + commit.** Run `--static` against a scratch tree BEFORE the scanner
  logic exists (fails), then after (passes) — transcript to
  `docs/dv/evidence/ws7-escape-suite-selftest.txt` (the real Zone A run is Task 15).

```bash
git add ci/cleanroom/overlay/ci/fence-escape-suite.sh docs/dv/evidence/ws7-escape-suite-selftest.txt
git commit -m "[ci] WS7: escape-test suite (content/config/probe cases + anti-vacuity negative controls)"
```

---

### Task 12: DV_prompt Section-12 corrections, dv_principles sentence, supersessions

**Files:**
- Modify: `DV_prompt.txt` (UNTRACKED — edit in place, do not `git add`; it stays owner-delivered
  at challenge launch and is not a sync input)
- Modify: `docs/dv/dv_principles.md`
- Modify: `CLAUDE.md`, `AGENTS.md` (full tree)
- Modify: `docs/superpowers/specs/2026-09-01-auto-dv-setup-design.md`
- Modify: `ci/mcp/README.md`, `ci/mcp/siliconpilot-mcp.sh`, `ci/mcp/fsdb-mcp.sh`,
  `ci/mcp/verdi-cov-mcp.sh`, `.codex/config.toml`, `ci/env.sh` (comment-only supersessions)

**Interfaces:**
- Consumes: amendment changes 3/5 (Section-12 deltas), supersession list, execution-model
  consequence for `dv_principles.md`.
- Produces: the launch preconditions in their final wording; retired-rule text gone from
  shipped files.

- [ ] **Step 1: `DV_prompt.txt` Section 12** (cite by precondition number only):
  - Precondition 6: VERIFY it already reads as the amendment's split (riscv-isa-sim "absent
    from the clone"; google_riscv-dv "pristine upstream at its locked revision") — confirmed
    already applied as of 2026-09-02; record the verification in the ledger, edit nothing if it
    still reads so.
  - Precondition 9 (the item-9 extension, amendment change 3): add `AGENTS.md` and
    `.codex/config.toml` to the scanned file set, and append the wrapper-list clause: "and the
    cross-review wrapper asserts the Zone A rubric list exactly: ai-slop-comments,
    assertion-integrity, forces-and-hier-access, magic-numbers, rtl-purity."
  - Re-run `grep -c '^- PROPOSED RULING' DV_prompt.txt` → 0 (precondition 1 untouched).
- [ ] **Step 2: `dv_principles.md` §6 Zone A scoping sentence** — OUTSIDE the
  `TRUST-TRIAD-CANONICAL` markers (the block is hash-anchored), as a new bullet directly after
  the "Self-proving checks" bullet:
  `- **Zone A scoping.** The operational sentence for "hidden referees inert" (+disable_cosim=1) belongs to the full-tree TB. In the cleanroom (Zone A) it reads instead: every Zone A check other than the named one is disabled for the evidence run, and the failure signature in the log belongs to the named check (Zone A seed prompt, Section 8).`
  Section numbers must not shift (dv-principles-check cites §s) — a bullet inside §6 shifts
  nothing; mirror-check the `dv-principles-check` skill's citations afterward and run
  `.codex/compat/validator.py` (semantic checks on this file).
- [ ] **Step 3: Full-tree `CLAUDE.md` Critical Invariant 2 + `AGENTS.md` mirror:** replace the
  fail-closed placeholder clause with: "Knowledge-fence: generation sessions must not read
  fenced DV collateral. `docs/dv/FENCE.md` is the fence authority (manifest: `ci/fence.yaml`);
  generation sessions run ONLY in a cleanroom clone made by `ci/make-cleanroom.sh`, and infra
  sessions never paste fenced content into allowed files." Validator PASS required.
- [ ] **Step 4: Spec supersession annotations** (one-line bracketed notes, no history
  rewriting) at exactly: §WS5 zone-scoping paragraph; §WS5 gate item "no MCP servers
  configured" (→ "client configs list exactly the three local servers and no remote ones");
  §WS7 enforcement-stack item 2 ("no MCP servers" → Zone A profile per amendment change 1);
  §WS7 "query an MCP" escape case (→ config assertion); §WS7 dual-run paragraph + canary gate
  wording (→ single evaluation run); §WS7 `--compile-only` sentence (→ retired; mechanical
  acceptance). Each: `[Superseded by specs/2026-09-02-zone-a-fence-scope-amendment.md v2.1 —
  <one clause>.]`
- [ ] **Step 5: Shipped-file supersessions** (amendment's supersession list): `ci/mcp/README.md`
  §Zone scoping rewritten (three local servers ship to Zone A pointed at the cleanroom's own
  out-tree; atlassian Zone B only; fence review for additions); the three `ci/mcp/*.sh` header
  comments ("Zone B only — never ship" → "ships to Zone A; atlassian stays Zone B (fence
  amendment change 1)"); `.codex/config.toml` header comment; `ci/env.sh` MCP-block comment.
  Grep-check afterward: `grep -rn "cleanroom ships no MCP\|no MCP servers" ci/ .codex/ docs/`
  returns nothing.
- [ ] **Step 6: Validator + commit** (DV_prompt.txt deliberately NOT added):

```bash
python3 .codex/compat/validator.py
git add docs/dv/dv_principles.md CLAUDE.md AGENTS.md \
        docs/superpowers/specs/2026-09-01-auto-dv-setup-design.md \
        ci/mcp/README.md ci/mcp/siliconpilot-mcp.sh ci/mcp/fsdb-mcp.sh ci/mcp/verdi-cov-mcp.sh \
        .codex/config.toml ci/env.sh
git commit -m "[docs] WS7: Zone A scoping in dv_principles, invariant-2 rewire, WS5-rule supersessions"
```

---

### Task 13: GATE A — publish + resync the cleanroom branch; close WS5 item 3

**Files:**
- Create: `docs/dv/evidence/ws7-cleanroom-publish.txt`
- Create: `docs/dv/evidence/ws7-cleanroom-mcp-configs.txt`
- Modify: `ci/cleanroom-generations.yaml`
- Modify: `docs/dv/process-logs/ws5/progress.md`

Controller-run (real remote pushes; serialize after Tasks 1–12; watchdog 15 min per step).

- [ ] **Step 1: First sync + resync:** `bash -lc 'source ci/env.sh && ci/sync-cleanroom.sh
  --source HEAD'` — generation 1 published; run it AGAIN after one trivial allowed-file commit
  to prove append-only resync (two snapshots, one root, history audit green both times). Apply
  the `cleanroom` branch protection (`gh api` command from FENCE.md §8). Capture commands, tip
  SHAs, trailer blocks → `ws7-cleanroom-publish.txt`. Commit the updated generations registry.
- [ ] **Step 2: Verified clone:** `ci/make-cleanroom.sh ../ibex-cleanroom` — all five
  verification classes green; the spec-gate check verbatim: zero manifest-glob files with
  `git log --all` included. Append output to `ws7-cleanroom-publish.txt`; save the config
  assertion section separately as `ws7-cleanroom-mcp-configs.txt`.
- [ ] **Step 3: Close WS5 gate item 3 against the amendment's replacement criterion:** append
  to `docs/dv/process-logs/ws5/progress.md`: gate item 3 closed 2026-MM-DD against the
  amended criterion (cleanroom client configs list exactly the three local servers, no remote
  ones), evidence `docs/dv/evidence/ws7-cleanroom-mcp-configs.txt`; flip the end-state line
  PARTIAL → **DONE**.
- [ ] **Step 4: Commit.**

```bash
git add docs/dv/evidence/ws7-cleanroom-publish.txt docs/dv/evidence/ws7-cleanroom-mcp-configs.txt \
        ci/cleanroom-generations.yaml docs/dv/process-logs/ws5/progress.md \
        docs/dv/process-logs/ws7/progress.md
git commit -m "[dv] WS7 gate A: cleanroom published+resynced, clone verified; WS5 gate item 3 closed"
```

---

### Task 14: GATE B — SIM_RECIPE compile+run from the cleanroom prototype

**Files (in the CLEANROOM clone, branch `cleanroom/ws7-roundtrip` — they reach this repo only
via Task 16's landing):**
- Create: `dv/auto_dv/proto/gen_recipe_smoke_tb.sv`, `dv/auto_dv/proto/gen_recipe_smoke.f`,
  `dv/auto_dv/scripts/zoneb_entry.sh`, `dv/auto_dv/proto/fcov_expectations.yaml`
- Create (this repo): `docs/dv/evidence/ws7-sim-recipe-gate.txt`
- Modify (this repo): `docs/dv/SIM_RECIPE.md` (flip the two PENDING lines)

Controller + one implementer INSIDE `../ibex-cleanroom` (a genuine Zone A authoring session:
seed it only with `SIM_RECIPE.md`, `FENCE.md`, the Zone A `CLAUDE.md`, and this task's text —
handoff item 1's gate demands the recipe suffice on its own; if the session needs a fact the
recipe lacks, FIX `SIM_RECIPE.md` full-tree side and re-sync — that iteration is the gate's
point). Watchdog 45 min for the sim.

- [ ] **Step 1: Author the minimal TB from allowed knowledge only:** `gen_recipe_smoke_tb`
  instantiates `ibex_core` + `ibex_register_file_ff` with `opentitan`-config parameters taken
  from `ibex_configs.yaml`; drives clock/reset; answers instruction fetches with NOP
  (`32'h00000013`) and data channel with zeros; ONE named check `gen_fetch_started` (`ibex_core`
  must assert its instruction request within 100 cycles of reset release, else
  `$fatal(1, "gen_fetch_started: no fetch after reset")`); one covergroup `gen_recipe_cg` with
  one coverpoint (fetch-request seen), declared in `dv/auto_dv/proto/fcov_expectations.yaml`.
- [ ] **Step 2: Trust-triad evidence for the one check (Zone A skill variants exercised):**
  red→green — first run with reset held (check fires, nonzero exit), then correct (passes);
  mutation RT-001 (TB mutation: never release reset; named check catches it; ablation: check
  disabled ⇒ run "passes" — the Zone A inert-referee sentence is trivially satisfied, there is
  only one check; record id/file/original/mutated/detector per Section 8); fcov-expectation:
  run with coverage, `ci/check_fcov_expectations.py` passes on the declared bin. Evidence files
  land under `dv/auto_dv/evidence/` in the cleanroom branch.
- [ ] **Step 3: Execute the recipe's exact command** (compile+run via
  `ci/cleanroom-compile.sh --stage elab` then the run command from `SIM_RECIPE.md`), once with
  waves on (the FSDB feeds Task 15's E7a) and once with coverage on. Write
  `dv/auto_dv/scripts/zoneb_entry.sh` = compile + run + fcov-expectation check, exit status
  propagated.
- [ ] **Step 4: Full-tree side:** flip `docs/dv/SIM_RECIPE.md`'s two lines — `Executed on this
  site: 2026-MM-DD, log: dv/auto_dv/evidence/<file> (cleanroom branch cleanroom/ws7-roundtrip)`
  and run the `fence-integrity` rubric over `SIM_RECIPE.md` via the cross-review skill
  (full-tree side; it is a Zone B rubric) → `fence-integrity: PASS (2026-MM-DD)` line
  (precondition 3). Re-sync (`ci/sync-cleanroom.sh --source HEAD`) so the snapshot carries the
  final recipe; `git -C ../ibex-cleanroom pull`. Copy the executed-command transcript (commands,
  exit statuses, log tails) → `docs/dv/evidence/ws7-sim-recipe-gate.txt`.
- [ ] **Step 5: Commit (this repo).**

```bash
git add docs/dv/SIM_RECIPE.md docs/dv/evidence/ws7-sim-recipe-gate.txt \
        ci/cleanroom-generations.yaml docs/dv/process-logs/ws7/progress.md
git commit -m "[dv] WS7 gate B: SIM_RECIPE compile+run executed from the cleanroom prototype"
```

---

### Task 15: GATE C — escape suite from a Zone A session

**Files:**
- Create: `docs/dv/evidence/ws7-escape-suite-run.txt`

Controller-run from `../ibex-cleanroom` (fresh `claude` session inside the clone = the Zone A
session; watchdog 30 min).

- [ ] **Step 1:** `ci/fence-escape-suite.sh --static --probes --negative
  --fsdb <Task-14 fsdb> --daidir <Task-14 daidir> --simlog <Task-14 run log>` — all cases PASS
  (E6 must find the full-tree sibling and PASS, not SKIP, in this layout; E7c planted-violation
  control detects). Any FAIL loops back to the owning task (fix full-tree side, re-sync, pull,
  re-run) — never weaken a case to pass it.
- [ ] **Step 2:** Copy the per-case transcript with repro metadata →
  `docs/dv/evidence/ws7-escape-suite-run.txt`; commit (this repo) with the ledger tick:

```bash
git add docs/dv/evidence/ws7-escape-suite-run.txt docs/dv/process-logs/ws7/progress.md
git commit -m "[dv] WS7 gate C: escape suite green from a Zone A session (incl. negative controls)"
```

---

### Task 16: GATE D — one full round-trip

**Files:**
- Create: `docs/dv/evidence/ws7-roundtrip.txt`
- Possibly modify: `docs/dv/known-followups.md` (cosim-attachment feasibility finding)

Controller-run; watchdog 60 min for the evaluation run.

- [ ] **Step 1: Submit from Zone A:** in `../ibex-cleanroom` on `cleanroom/ws7-roundtrip`
  (Task 14's dummy artifact), run `ci/zoneb-submit.sh` — capture the mechanical acceptance
  (exit 0, queued message, nothing else returned).
- [ ] **Step 2: Evaluate in Zone B:** from THIS repo, `ci/zoneb-run.sh cleanroom/ws7-roundtrip
  --with-referees` — entry point runs green in the sibling eval clone; human-fcov bind
  attachment demonstrated on the dummy TB's `ibex_core` instance (URG report in the eval
  out-tree); cosim attachment attempted, outcome recorded (finding to
  `docs/dv/known-followups.md` if infeasible on the dummy). Verify by listing: NO new file
  appeared under `../ibex-cleanroom` (artifacts stay Zone B — the amended gate wording).
- [ ] **Step 3: Land:** `ci/land-from-cleanroom.sh cleanroom/ws7-roundtrip` → validator PASS
  line captured; branch `auto-dv/land/ws7-roundtrip` created off master with only
  `dv/auto_dv/**` changes and provenance trailers; merge it into the working branch after the
  Task 17 review (the dummy plus its triad evidence is the namespace's first landed content).
- [ ] **Step 4: Evidence + commit:** all three transcripts (submit, evaluate, land) with SHAs
  and artifact inventories → `docs/dv/evidence/ws7-roundtrip.txt`.

```bash
git add docs/dv/evidence/ws7-roundtrip.txt docs/dv/known-followups.md \
        docs/dv/process-logs/ws7/progress.md
git commit -m "[dv] WS7 gate D: Zone A -> Zone B -> landing round-trip demonstrated"
```

---

## Workstream close (controller, not a subagent task)

Run the `cross-review` skill for the codex post-execution review of the full WS7 commit range
(budget 45+ min; watchdog per the site rule); commit the artifact under `docs/dv/reviews/`;
set the WS7 ledger end-state (DONE only on APPROVE/APPROVE-WITH-CHANGES; fix waves otherwise).
Record in the ledger: WS5 flipped DONE (Task 13), the launch preconditions NOT yet satisfiable
by WS7 alone (precondition 1's marker check, 8's N/G values, and the owner sign-off line are
owner actions in `DV_prompt.txt`; WS7 hands over everything mechanical), and the WS6/WS4
follow-ons (cleanroom mex; Jenkins cleanroom-sync job).

## Self-review (performed while drafting; re-verify at execution end)

**Coverage table — every binding requirement → owning task:**

| Requirement | Task |
|---|---|
| `ci/fence.yaml` default-deny, triage tables, allowlist+rationale, handoff open item 5 | 1 |
| Sync: serialized, SHA+digest trailers, whole-history audit, reject-unclassifiable, rotation | 7 |
| `make-cleanroom`: single-branch clone, zero fenced files incl. history; sparse caveat script | 8 |
| Landing: ancestry, `dv/auto_dv/**` confinement, no symlink/rename/delete outside, `gen_` prefix (handoff item 2) | 9 |
| `zoneb-run`: single evaluation run, generated-TB build, fcov-bind + cosim attachment (impl task), artifacts Zone B-side | 10, 16 |
| `zoneb-submit`: mechanical acceptance only; `--compile-only` retired | 4 (script), 12 (spec annotation) |
| Escape suite: change-4's five bullets, sibling-clone case, anti-vacuity negative control, Zone A-runnable | 11, 15 |
| `SIM_RECIPE.md`: change-6 allowlist; executed compile+run gate (handoff item 1) | 5, 14 |
| `FENCE.md` (incl. precondition-2 lists, honor-system + limitations, revocation) | 6 |
| Zone A variant set: change-2 full list (skills, agents, CLAUDE/AGENTS pair, configs, env, mcp README, TB_CONTRACT) + change-3 rubric set + wrapper assertion | 2, 3, 4 |
| Amendment change 1 (three local servers, no atlassian) | 4, 13 |
| riscv-isa-sim omitted; riscv-dv pristine at 71666eba | 1, 7 |
| DV_prompt Section-12: precondition-6 split (verify — already applied), item-9 extension | 12 |
| dv_principles §6 Zone A sentence outside the anchored block; validator after | 12 |
| Supersession list (README/wrappers/config/env comments; spec §WS5/§WS7) + invariant-2 rewire | 12 |
| WS5 ledger PARTIAL→DONE against the replacement criterion | 13 |
| Spec gates as amended: publish+resync; zero-glob clone; escape suite from Zone A; recipe executed; round-trip | 13, 14, 15, 16 |
| PreToolUse fence hook (spec enforcement item 2, full-tree sessions) | 1 |
| `cleanroom-compile.sh` + spec:154 design rule; `dv/auto_dv/.gitignore` (precondition 7) | 4 |

**Placeholder scan:** no TBDs. Two deliberate PENDING literals exist in Task 5's
`SIM_RECIPE.md` draft — they are specified content (honesty markers) that Task 14 is required
to flip, not open plan decisions. Items marked "verify at implementation" (vendor-tree
pristine checks, exact VCS flag set, per-skill scan results) are mechanical verifications with
stated procedures and acceptance criteria, each recorded in the ledger.

**Interface consistency:** trailer names (`Generation:`/`Source-SHA:`/`Manifest-Digest:`) used
identically in Tasks 7, 8, 9, 16; registry path `ci/cleanroom-generations.yaml` in 7, 8, 9, 10,
13; generated files `ci/fence-globs.txt`/`ci/fence-identifiers.sha256`/`ci/.fence-salt` in 7,
11; entry-point convention `dv/auto_dv/scripts/zoneb_entry.sh` in 5, 10, 14, 16; the item-9
string set and scan homes defined once in `ci/fence.yaml` and cited by Tasks 2, 3, 4, 5, 11,
12; the Zone A rubric five-list identical in Tasks 3, 12 and the Global Constraints contract.
