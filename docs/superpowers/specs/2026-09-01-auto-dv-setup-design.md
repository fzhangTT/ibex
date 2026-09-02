# Auto-DV Infrastructure Setup — Design Spec

**Date:** 2026-09-01
**Branch:** `fzhang/auto-dv-setup`
**Context:** [AI_Transformation_Assigments.md](../../../AI_Transformation_Assigments.md) — Auto-DV on RISC-V cores (VCS/Verdi). Automate test-plan creation and FCOV/CCOV closure while minimizing human review of generated infrastructure. The experiment must test *how we can trust generated DV*, not merely whether AI can generate test code.

This spec covers the infrastructure setup only — the foundation the auto-DV experiments run on. Test-plan generation and coverage-closure loops are follow-on work with their own specs.

## Approved decisions

| Decision | Choice |
|---|---|
| Regression flow | Jenkins + LSF shell scripts (tt-regress: written assessment only) |
| Skills port | Curated core, each skill reviewed against ibex reality; emphasis on coding standards, reviews, TDD, mutation ("prove it fires") |
| Standard config | `opentitan` (the DV default) |
| cocotb version | 1.9.2 pinned (proven VCS+UVM recipe on this site; official stable is 2.1 — migration is a contained later step because the integration layer is deliberately thin) |
| GitHub auth | Done — `gh` 2.53.0 (`/tools_vendor/FOSS/gh/2.53.0/bin`), account `fzhangTT`, credential helper wired |
| Cross-model review | Mandatory: the executing model never self-approves (see WS3) |

## Workstream 1 — VCS bring-up

**Goal:** one riscv-dv test passing end-to-end under VCS with spike cosim, then the same with `COV=1`, and verified written instructions.

- `ci/env.sh` — single environment entry point sourced by everything: `module load synopsys/vcs/X-2025.06-SP2` (matches Verdi on PATH), `RISCV_TOOLCHAIN`/`RISCV_GCC`/`RISCV_OBJCOPY`, `SPIKE_PATH` + `PKG_CONFIG_PATH`, gh bin dir, repo-local Python venv activate.
- **Spike:** build lowRISC's fork (`ibex_cosim` branch, rev pinned in `flake.nix`: `4b973966`) via `ci/build-spike.sh` — `--enable-commitlog --enable-misaligned`, installed to `/localdev/fzhang/ws/tools/spike-ibex-cosim` (workspace-local, outside the repo; path centralized in `ci/env.sh`), discovered by the TB via `pkg-config` (`riscv-riscv`, `riscv-disasm`, `riscv-fdt`, `riscv-fesvr`). Site spike installs (`/tools_risc/tt/spike`) do not provide these libs. Verify the pinned rev builds with gcc-toolset-11 on RHEL8.
- **Cosim deep-dive:** the checker is in-repo at `dv/cosim/` (`spike_cosim.cc` step-and-compare via DPI; this fork already customizes it — e.g. mcounteren behavior). Deliverable `docs/dv/COSIM.md`: architecture (what is compared, how mismatches surface in `rtl_sim.log`/`trr.yaml`), what lowRISC patched in spike, what this fork added, and augmentation gaps — notably **spike has no CHERIoT knowledge**: fine today (`cheriot_enable_i` tied to `IbexMuBiOff` in the TB), flagged as the blocker for CHERIoT-enabled verification (CHERIoT projects use a Sail reference model; out of scope).
- **Toolchain:** prefer the lowRISC `rv32imcb` release tarball (`lowrisc-toolchain-gcc-rv32imcb-20220210-1`); fallback is the site riscv64-elf multilib (`/tools_risc/opensrc/latest/newlib`) with `-march=rv32imc` and bitmanip tests filtered until the real toolchain lands.
- **Fork bug fix:** `util/ibex_config.py` emits `+define+IBEX_CFG_BaseIsa` / `IBEX_CFG_RegFile` but `core_ibex_tb_top.sv` expects `IBEX_CFG_BASE_ISA` / `IBEX_CFG_REG_FILE` — every config silently builds the CHERIoT-capable DUT. Fix on the side with the smallest consumer blast radius (grep first), with a mutation-style proof: show a `small` build actually loses CHERIoT before/after.
- **Deliverable:** `docs/dv/BUILD_AND_SIM.md` — verified commands (single test, regression, coverage), the 8-config table (`small`, `opentitan`, `maxperf`, `maxperf-pmp`, `maxperf-pmp-bmbalanced`, `maxperf-pmp-bmfull`, `maxperf-pmp-bmfull-icache`, `experimental-branch-predictor`; DV default `opentitan`, top-level Makefile default `small`), and gotchas: stale `metadata.pickle` (`make clean` after editing testlists/configs), riscv-dv generator is also VCS-compiled (two licenses per fresh build), `-l` log redirect quirk, `.vRefine` waivers not auto-applied by the urg merge.

**Gate:** passing `make SIMULATOR=vcs IBEX_CONFIG=opentitan TEST=riscv_arithmetic_basic_test ITERATIONS=1 SEED=1` log + a `COV=1` run producing a merged vdb and report.

## Workstream 2 — cocotb integration

**Architecture:** quasar_soc's coexistence pattern (cocotb is master; SV-UVM stays fully active as a service layer) + ws-tensix's debug-access discipline, as a **strictly opt-in overlay**: `COCOTB=1` make knob; stock UVM flow is bit-identical when off.

SV side (all under `` `ifdef COCOTB_SIM``):
- `core_ibex_cocotb_if.sv` — `cocotb_active`, `uvm_finished`, `uvm_ready` (listener-armed handshake), compile-time-macro flag bits, and a dead-cocotb watchdog: `$fatal` at 100ns unless Python sets the alive bit (ruling: a lost Python must FAIL the run with nonzero exit — `$finish` would end it cleanly and could masquerade as a pass; supersedes the earlier `$finish` wording).
- A `uvm_component` objection holder: raises in `run_phase` while `cocotb_active`, drops when Python finishes; `final_phase` sets `uvm_finished`; `finish_on_completion = 0` when cocotb is master. cocotb polls `uvm_finished` before exiting so UVM shutdown completes.

VCS flags added only when `COCOTB=1`:
- `+define+COCOTB_SIM +vpi -P cocotb_pli.tab -load $(cocotb-config --lib-name-path vpi vcs)`
- `cocotb_pli.tab` = `acc+=rw,wn:*` (read + deposit; **no force, no dump**). Never `-debug_access+all`. Ibex's stock compile already carries `-debug_access+pp -debug_access+f`, so VPI force is available if a test genuinely needs it — the tab still withholds it by default.

Python side:
- `dv/cocotb/` package; repo venv pins `cocotb==1.9.2`; `LIBPYTHON_LOC=$(cocotb-config --libpython)` exported in `ci/env.sh`.
- Two-level test selection (ws-tensix pattern): `MODULE` env var picks the test module; plusargs select/parameterize stimulus. Seeds: `+ntb_random_seed` for SV, `RANDOM_SEED` for cocotb, recorded together.

Milestones:
- **A (hello world):** cocotb prints, reads a DUT signal, the UVM test runs to completion — both frameworks visibly active in one log; stock flow (`COCOTB=0`) re-verified unchanged.
- **B (cocotb as the sequence):** Python drives stimulus through existing UVM TB components — first target the **irq agent** (Python decides when/which interrupts fire) via 1–2 hand-written DPI-exported UVM tasks / `uvm_event` triggers (quasar's mechanism; the mako DPI generator is not ported yet).

**TB contract doc (fence-aware):** `docs/dv/TB_CONTRACT.md` — the *allowed-path* description of everything a generated test may use: cocotb entry points, plusarg conventions, how to start stimulus on TB agents, seeds — plus the **checking obligation**: a generated test/TB deliverable must carry its own checking strategy (self-checking stimulus, generated SVA, and/or its own reference-model integration built from *upstream* open-source imports) and declared functional-coverage expectations; it may not assume any hidden referee catches what its own checks miss. Interfaces visible, internals fenced (see WS7).

**Gate:** Milestone A and B logs + `COCOTB=0` regression identity.

## Workstream 3 — Skills, cross-model layer, review policy

**Topology** (ws-tensix pattern, verbatim): canonical `.claude/skills/` + `CLAUDE.md` as single source of truth; `AGENTS.md` is a thin delegator ("read CLAUDE.md" + client-mechanics translation table); `.agents/skills/shared → ../../.claude/skills` symlink for codex discovery; `.codex/compat/validator.py` (adapted) enforces the contract; `.codex/config.toml` with `project_doc_fallback_filenames = ["CLAUDE.md"]` + MCP servers. **Known caveat:** codex consults the fallback only when `AGENTS.md` is *absent* — with the delegator present, correctness depends on the model following it. Mitigations: the few critical invariants (fence rules, review gate) are duplicated verbatim in `AGENTS.md` (bounded, validator-checked duplication), and the validator launches codex from the root and a representative subdirectory to assert the effective instructions actually loaded.

**Curated skill set:**

| Skill/asset | Source | Adaptation |
|---|---|---|
| `docs/dv/dv_principles.md` | ws-tensix `dv_principles.md` | generalized to ibex; SV/UVM + cocotb idioms; new trust-triad section: (1) TDD, (2) mutation-proof — every checker/assertion shown to fire, (3) fcov-expectation — every new test declares the fcov bins it intends to hit and fails if they are unhit |
| `dv-principles-check` | `iis-principles-check` | conformance review against our doc (not code review) |
| `mutation-check` | new (inspired by beowulf `meta/mutations`) | inject a bug (RTL or TB), show the new test/checker catches it, revert — required evidence for any generated DV component |
| `fcov-expectation` check | new | per-test declared-bins manifest + post-run coverage-DB query wired into the check stage: a test that misses its declared bins fails; the stimulus side of the trust triad (mutation proves the checker fires; this proves the stimulus got there) |
| `cross-review` | new | see policy below |
| review rubrics `ci/reviews/` | beowulf Sentinel rubrics | keep: assertion-integrity, magic-numbers, ai-slop-comments, test-overlap, rtl-purity, forces-and-hier-access; model-neutral prompt files run locally |
| `fence-integrity` rubric | new (WS7) | generated artifacts and their history contain no fenced-path references; test-overlap similarity check runs in Zone B only, findings go to humans, never back to the generator |
| `sim-debug` | beowulf | retargeted to `out/run/tests/<t>.<s>/` (rtl_sim.log, trr.yaml, cosim trace) |
| agents `ibex-debug-analyzer`, `ibex-test-generator` | beowulf agents | rewritten for riscv-dv testlist + directed + cocotb test shapes; generator mandates TDD + mutation proof |
| `simple-english` | beowulf (vendored ASD-STE100) | rescope surfaces to ibex docs |
| `lint-check` | beowulf | retargeted to ibex `lint/` (verilator/verible) |
| `regress` | new thin skill | wraps `ci/jenkins` scripts, reads `regr.log`/`report.html` |

Deliberately **not** ported: iis test-scaffolding skills (ibex test creation differs — riscv-dv testlist entries, directed tests, cocotb sequences; the test-generator agent encodes our shape), beowulf's GitLab/Jira/Confluence skills, template-sync.

**Trust-evidence attribution** (the triad's evidence must be attributable, not just present): a mutation counts as *caught* only when detected by the **named generated checker** (run with hidden referees inert — otherwise the existing cosim silently takes credit), with a checker-ablation negative control (checker disabled ⇒ mutation survives); fcov-expectation checks query **per-test, pre-merge** coverage (merged VDBs let one test claim another's bins), generated covergroups live in an isolated namespace, and sampling conditions get an anti-vacuity review (a bin hit by an always-true sample proves nothing).

**Cross-model review policy** (in `CLAUDE.md` + `AGENTS.md`; the `cross-review` skill executes it):
- The executing model never self-approves.
- **Before execution:** plan/spec/testplan reviewed by the other model — Claude executing ⇒ `codex exec` reviews against the rubrics + `dv_principles.md`; codex executing ⇒ `claude -p` reviews.
- **After execution:** diff review by the other model — `codex exec review` for the codex direction; `claude -p` + rubrics for the reverse.
- Review artifacts (verdict + findings) are committed under `docs/dv/reviews/` — this doubles as the challenge's trust-evidence trail. Each artifact records **reviewer identity** (CLI version, model ID, reasoning setting) and the **exact review target** (commit SHAs or explicit diff scope — `codex exec review` invoked with an explicit `--base`/`--commit`/uncommitted target, never an ambient default).
- The verdict is **machine-readable** (APPROVE / APPROVE-WITH-CHANGES / REQUEST-CHANGES in a fixed header) and **gating**: CI (and the executing agent) must not proceed past a REQUEST-CHANGES without a recorded re-review. Review artifacts live under the fence (WS7) — they discuss DV content.
- codex CLI verified: `codex-cli 0.149.1` (model `gpt-5.6-sol`), non-interactive `codex exec [PROMPT]` and `codex exec review`.

**Gate:** validator green; one skill exercised end-to-end from each of Claude and codex; one full cross-review cycle demonstrated on a real change from this branch.

## Workstream 4 — Regression: Jenkins + LSF

- `ci/jenkins/{smoke,nightly,coverage}.sh` — self-contained (source `ci/env.sh`, run the make flow, nonzero exit on failure), runnable by hand or by Jenkins.
  - smoke: a few fast tests (~15 min budget)
  - nightly: `TEST=all` at testlist iterations
  - coverage: nightly with `COV=1` + urg merged vdb + report archived
- **LSF phase 1:** each regression is one LSF job (`bsub -n N` + `make -jN`) — the ibex flow parallelizes per-test stages under make. **Phase 2 (only if needed):** per-test `bsub` fan-out after shared build stages; feasibility vs. the `metadata.pickle` single-writer design assessed and documented during implementation.
- `Jenkinsfile` (declarative): Build → Smoke/Regress → Coverage; junit ingestion of `regr_junit.xml`; archive `report.html` + coverage report.
- Additional job: **cleanroom sync** — on every `master` push, run `ci/sync-cleanroom.sh` to refresh the `cleanroom` branch (see WS7).
- `ci/jenkins/README.md` — Jenkins setup info: repo `https://github.com/fzhangTT/ibex.git`, branch spec, node requirements (LSF submit host, environment-modules, `/tools_vendor` + `/tools_risc` visibility), credentials (gh token or a machine PAT).
- `docs/dv/tt-regress-assessment.md` — the assessment: reusable YAML/DAG orchestrator skeleton, but build/run backends are Bazel/bzsim-only, scheduling delegated to LSF `bsub -w`, results assume internal Simscope (hard exit on unknown repos); raw-`command:` escape hatch exists but not pursued.

**Gate:** all three scripts executed successfully by hand at least once (smoke fully; nightly/coverage on a reduced test set with the mechanism proven).

## Workstream 5 — MCP servers

`.mcp.json` (Claude) and `.codex/config.toml` (codex) declare the same servers:

| Server | Launch | Purpose |
|---|---|---|
| `siliconpilot` | `/tools_risc/tt/siliconpilot/latest/bin/siliconpilot-mcp --workspace .` | HW-workflow agent tools (from ws-tensix `.codex/config.toml`) |
| `fsdb-mcp-server` | repo wrapper script (beowulf pattern: module-load, put `$VERDI_HOME/bin` on PATH, exec the site `start_server.sh`) — **exact version pinned in the wrapper at implementation time and recorded** | wave debug from FSDB — requires the cocotb/UVM runs to dump FSDB when waves are requested |
| `verdi-cov-mcp` | `/tools_vendor/tt/verdi_cov_npi_mcp/<pinned>/mcp_env_wrap.sh` — **exact version pinned and recorded** | coverage DB queries — core tool for the coverage-closure loop |
| `atlassian` | `https://mcp.atlassian.com/v1/mcp` (http) | optional, matches siblings |

Wave-dump policy stays deliberate: FSDB dumping only on `WAVES=1` runs (the stock flow already gates via `vcs.tcl` + `$VERDI_HOME`), so debug access/instrumentation cost is only paid when debugging.

**Zone scoping (WS7):** this MCP set is **Zone B / full-tree only**. FSDB and coverage servers can read blind evaluation data, and `siliconpilot --workspace .` is not a sandbox — so the cleanroom ships its own agent configs with **no MCP servers** (the snapshot replaces `.mcp.json`/`.codex/config.toml` with Zone A variants). Any future Zone A MCP addition requires a fence review.

**Gate:** each local MCP server starts and answers a tool-list request from **both a Claude Code and a codex session** in this repo; fsdb-mcp demonstrated against an FSDB produced by a `WAVES=1` run; the cleanroom clone demonstrates *no* MCP servers configured.

## Workstream 6 — mex

`npm install -g mex-agent` (user npm-global dir already on PATH; Node 22.14 ≥ 22.5) → `mex setup` → wiki populated from the repo → mex's CLAUDE.md anchor section merged into our canonical `CLAUDE.md` (delegator `AGENTS.md` unchanged). Known limit documented: the code graph parses Python/TS/JS/Rust only — no SystemVerilog — so the graph covers the DV/python side; RTL/TB knowledge is curated wiki pages kept honest by `mex check` in the review cadence.

**Fence interaction (WS7): two mex instances.** The full tree's mex carries `ci/fence.yaml`'s globs in its ignore config **and** a wiki-authoring rule: no page may paraphrase fenced content (a summary of the existing testlist in an allowed page would defeat the fence). The clean-room clone gets its **own** `mex setup` — its graph and wiki are built only from visible files, so fenced knowledge cannot enter by construction.

**Gate:** `mex check` green; one `mex graph scope` query returning sensible context for a DV task.

## Workstream 7 — Knowledge fence (clean-room generation)

**Requirement:** the auto-DV generation phase (testplan, tests, TB components) must not use existing DV collateral — including local modifications to open-source imports. Upstream open-source tools (spike, riscv-dv) and the RTL itself remain fair game. Multiple people will work in this model; the fence must be persistent, pullable, and documented.

**Threat model (stated honestly):** the fence targets *accidental contamination by cooperative-but-fallible agents and humans*, not adversarial exfiltration. A Zone A shell could in principle `git fetch` other branches, read a sibling clone, or fetch upstream ibex's public DV tree — so enforcement is layered (physical clone + agent runtime profile + audit + review), each layer verified by **escape tests** (scripted attempts to reach fenced content from a Zone A session must fail or be flagged). Container-level isolation is documented as optional hardening if the team later wants stronger guarantees.

**Generated-code namespace:** Zone A writes only under `dv/auto_dv/**` (tests, TB components, its own fcov, its own testlist) plus a versioned contract package `dv/auto_dv/contract/` (compilable interface stubs + `TB_CONTRACT.md`). The landing validator enforces this: ancestry from an approved snapshot, changed paths confined to the namespace, no symlinks/renames/deletes outside it.

**Fenced content — default-deny** (single source of truth: `ci/fence.yaml`). Sensitive roots are denied wholesale; visibility requires an explicit file-level **allowlist entry with a one-line rationale**, and the sync script **rejects any path it cannot classify** (new files must be triaged into the manifest before entering a snapshot). Deny roots and notable cases:
- `dv/**` — all existing DV: tests, testlists, `riscv_dv_extension/`, `directed_tests/`, `fcov/` (human coverage model), `env/`, `common/`, `dv/cosim/`, verilator/formal collateral. Allowlisted back in: the `dv/auto_dv/**` namespace, and interface-defining files needed to compile against the TB contract (sequence items, virtual interface definitions, hook/API packages — they carry no stimulus/checking/coverage knowledge; where a file mixes both, extract an interface package into an allowed path).
- Verification-describing documentation: `doc/03_reference/{testplan,coverage_plan,verification,verification_stages,cosim}.rst`, `doc/01_overview/verification_overview.rst` (names tests, describes coverage strategy), TB diagrams (`doc/03_reference/images/tb*.svg`), `dv/uvm/core_ibex/README.md`.
- `vendor/patches/**` **and their applied results**: the checked-in `vendor/google_riscv-dv/` already has local patches applied (`google_riscv-dv.vendor.hjson`), so the snapshot **replaces it with pristine upstream at the locked revision** (`71666eba`, from the lock file) — or omits it and Zone A imports upstream riscv-dv itself.
- The lowRISC spike fork (`ibex_cosim` branch, built by WS1) — Zone B equipment only; Zone A may build its own reference-model integration from **upstream** `riscv/riscv-isa-sim`.
- **Derived/infra documents that paraphrase fenced knowledge:** `docs/dv/COSIM.md`, `docs/dv/BUILD_AND_SIM.md` (names existing tests), `docs/dv/evidence/**`, `docs/dv/reviews/**`, `docs/superpowers/**` (specs/plans discuss existing DV), the full tree's `.mex/**`, `ci/reviews/**` where rubrics reference existing DV (e.g. test-overlap). The cleanroom's declassified doc set is explicit: `docs/dv/TB_CONTRACT.md`, `docs/dv/FENCE.md`, contract-package docs.

**Zone A — clean room (generation).** A published **`cleanroom` branch with orphan snapshot history**: `ci/sync-cleanroom.sh` builds a tree of allowed paths only (from the manifest) and appends it as a snapshot commit (orphan root; no ancestry to `master`), then pushes; it fails if any fenced glob would enter the snapshot. Because no commit in the branch's history ever contained a fenced blob, a clean clone is airtight:

```
git clone --single-branch --branch cleanroom https://github.com/fzhangTT/ibex.git ibex-cleanroom
```

`--single-branch` fetches only that branch's objects — fenced blobs are absent from the clone entirely, not merely hidden. Updates are plain `git pull` (append-only snapshots, no force-push). **User entry point:** `ci/make-cleanroom.sh` automates the whole thing from a freshly pulled `master` — it performs the single-branch clone into a sibling dir (default `../ibex-cleanroom`, configurable), verifies zero fenced files anywhere in the clone (history included), and leaves the user checked out on `cleanroom` ready to `git checkout -b cleanroom/<topic>`. It is deliberately a **separate clone, never `git worktree`** — worktrees share the parent's object store, so fenced blobs would remain retrievable. Note `cleanroom` reflects `master` as of the last sync (Jenkins job or manual `ci/sync-cleanroom.sh`). **Sync integrity:** syncs are serialized (lock; the branch ref is protected against non-sync pushes), each snapshot commit records the source `master` SHA + the manifest digest in its message, and every sync audits the *entire existing snapshot history* against the current manifest — not just the new tree. **Revocation:** if a leak is found or a file is reclassified as fenced, append-only history is abandoned — the sync generates a new orphan root (`cleanroom` generation N+1, force-rotated), and Zone B/landing reject work based on retired generations, forcing fresh clones. Generation work happens on branches off `cleanroom`; `ci/land-from-cleanroom.sh` lands finished work onto a `master`-based branch for normal PR review, and the landing validator checks ancestry from an approved snapshot and confines changed paths to `dv/auto_dv/**` (no symlinks, renames, or deletes outside it). A sparse-checkout script (`ci/make-cleanroom-sparse.sh`) is provided as a *human convenience only*, documented with its caveat: the local object store still contains fenced history, so it is a view, not a boundary.

**Zone A local validation.** The cleanroom is self-sufficient for static validation of its own code: `ci/cleanroom-compile.sh` runs (1) verilator `--lint-only` against `rtl/` (fast, no license), (2) VCS analysis/elaboration of generated units + DUT (no simv run), (3) python checks (venv import/collect). Design rule: **if Zone A code cannot compile without fenced sources, the coupling exceeds the contract — fix the contract/interface files, never grant a fence exception.**

**Zone B — execution/evaluation (full tree).** Runs generated artifacts on trusted infra; trusted infra is never read by generators. Cleanroom users reach it only by submission: `ci/zoneb-submit.sh [--compile-only]` (run from the cleanroom) pushes the `cleanroom/<topic>` branch and triggers Zone B execution — the Jenkins job when available, or the documented fallback of running `ci/zoneb-run.sh <branch>` in a sibling full clone. `--compile-only` is the fast feedback path (does the overlay build against the full TB?); its report redacts fenced paths from compile logs (error text kept, fenced file paths replaced by `<fenced>`; errors anchored in Zone A files return in full detail). For humans operating both zones, `FENCE.md` states the honor-system boundary: what returns to generation work is the sanitized report, nothing else; agent sessions get this enforced (they only ever see the report file).
- `ci/zoneb-run.sh <cleanroom-branch>` — overlays the Zone A diff onto a full `master` tree, runs the stock flow. The existing cosim (lowRISC spike fork + `dv/cosim`) still executes — it is Zone B *equipment* — but it is an **evaluation-only measurement, not a referee the AI may rely on**: the AI's deliverable must carry its own checking (TB contract, WS2), re-derived from upstream imports as part of the challenge.
- **Dual-run architecture** (log scraping cannot reliably attribute failures — `check_logs.py` lumps all UVM errors into one class and copies arbitrary excerpts): Zone B runs each submission twice. The **visible run** executes with the hidden referees inert (existing cosim comparison and human fcov disabled or ignored) and returns a **strict structured schema** — registered generated-checker IDs with verdicts, generated-fcov results, code-coverage summary — never arbitrary log excerpts (excerpts are extracted only from messages emitted by registered Zone A components). The **blind run** executes the full flow (cosim referee + human fcov) in an isolated job whose exit status, timing, and artifacts cannot influence the visible report; its findings go to the human evaluation report only. Noninterference is tested with canaries (a seeded blind-only failure must not perturb the visible report). Whether Zone A ever receives a minimal binary "blind referee flagged this" signal is a challenge-phase decision — default off. Coverage follows the **three-scope policy**:
  1. **Code coverage** (line/toggle/branch/FSM) — feeds back freely; derives from the DUT.
  2. **Generated functional coverage** (Zone A's own model) — full feedback loop, including the fcov-expectation check (declared-but-unhit bins fail the test).
  3. **Human fcov model** — evaluation-only blind benchmark, run in Zone B for humans; never returned to Zone A (even bin names would contaminate the generator's coverage-model design).

**Enforcement stack (defense in depth):** (1) physical — the cleanroom clone; (2) **Zone A agent runtime profile** — the cleanroom ships its own agent configs: **no MCP servers**, permission rules denying network fetches of ibex upstream/fork URLs and `git fetch`/`remote`-mutation, codex runs sandboxed with network restricted; a `PreToolUse` hook keyed on `IBEX_DV_FENCE=1` additionally blocks Read/Grep/Glob on manifest globs for full-tree sessions that must be fenced; (3) CI — the sync script's validation, the landing validator, plus a `fence-integrity` review rubric (WS3); (4) advisory — CLAUDE.md/AGENTS.md challenge-mode section; (5) **escape tests** — a scripted suite of contamination attempts (fetch master, read sibling clone, fetch upstream ibex DV, query an MCP) run from a Zone A session; each must fail or be flagged, and the suite is part of the WS7 gate. **Session hygiene:** generation experiments run in fresh sessions seeded only from Zone A — infra sessions (like this one) are contaminated by design and never do generation; persistent memory stays free of DV-content specifics.

**Docs:** `docs/dv/FENCE.md` — what is fenced and why, the one-command clone, update/branch/land workflows, the Zone B protocol, and the rules for humans and agents.

**Gate:** `cleanroom` branch published and re-synced by CI; `ci/make-cleanroom.sh` produces a clone containing zero manifest-glob files (`git log --all` included); the escape-test suite passes from a Zone A session; one full round-trip demonstrated — a dummy artifact authored in Zone A under `dv/auto_dv/**`, executed via `ci/zoneb-run.sh`, results returned through the dual-run structured report (an AI-check failure comes back; a canary blind-only finding is withheld and appears only in the evaluation report), landed on a `master` branch through the landing validator.

## Order & verification

WS1 first (everything depends on a working sim). WS2/WS3/WS4/WS5 can proceed in parallel after WS1; WS7 after WS2/WS3 (needs the TB contract and the rubric/hook homes); WS6 last (wants the final file layout, and the clean-room mex needs WS7's branch). Every workstream ends with its gate's *evidence* (logs, reports, committed artifacts), not claims. One branch, one commit series per workstream.

## Out of scope (follow-on specs)

- Test-plan generation and the coverage-closure agent loop (the actual challenge experiments).
- CHERIoT-enabled verification (needs a CHERIoT-aware reference model).
- Per-test LSF fan-out (phase 2, only if single-job parallelism is insufficient).
- Porting quasar's mako DPI generator (hand-written DPI exports suffice for milestone B).
