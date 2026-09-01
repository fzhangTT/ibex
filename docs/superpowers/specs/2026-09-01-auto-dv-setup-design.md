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
- `core_ibex_cocotb_if.sv` — `cocotb_active`, `uvm_finished`, compile-time-macro flag bits, and a dead-cocotb watchdog: `$finish` at 100ns unless Python sets the alive bit (a Python import error fails in nanoseconds, not a hung LSF slot).
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

**Topology** (ws-tensix pattern, verbatim): canonical `.claude/skills/` + `CLAUDE.md` as single source of truth; `AGENTS.md` is a thin delegator ("read CLAUDE.md" + client-mechanics translation table); `.agents/skills/shared → ../../.claude/skills` symlink for codex discovery; `.codex/compat/validator.py` (adapted) enforces the contract; `.codex/config.toml` with `project_doc_fallback_filenames = ["CLAUDE.md"]` + MCP servers.

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

**Cross-model review policy** (in `CLAUDE.md` + `AGENTS.md`; the `cross-review` skill executes it):
- The executing model never self-approves.
- **Before execution:** plan/spec/testplan reviewed by the other model — Claude executing ⇒ `codex exec` reviews against the rubrics + `dv_principles.md`; codex executing ⇒ `claude -p` reviews.
- **After execution:** diff review by the other model — `codex exec review` for the codex direction; `claude -p` + rubrics for the reverse.
- Review artifacts (verdict + findings) are committed under `docs/dv/reviews/` — this doubles as the challenge's trust-evidence trail.
- codex CLI verified: `codex-cli 0.149.1`, non-interactive `codex exec [PROMPT]` and `codex exec review`.

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
| `fsdb-mcp-server` | repo wrapper script (beowulf pattern: module-load, put `$VERDI_HOME/bin` on PATH, exec `/tools_soc/tt/fsdb-mcp-server/0.2.1/start_server.sh` — take latest available at implementation time) | wave debug from FSDB — requires the cocotb/UVM runs to dump FSDB when waves are requested |
| `verdi-cov-mcp` | `/tools_vendor/tt/verdi_cov_npi_mcp/v0.2.2/mcp_env_wrap.sh` (latest available) | coverage DB queries — core tool for the coverage-closure loop |
| `atlassian` | `https://mcp.atlassian.com/v1/mcp` (http) | optional, matches siblings |

Wave-dump policy stays deliberate: FSDB dumping only on `WAVES=1` runs (the stock flow already gates via `vcs.tcl` + `$VERDI_HOME`), so debug access/instrumentation cost is only paid when debugging.

**Gate:** each local MCP server starts and answers a tool-list request from a Claude Code session in this repo; fsdb-mcp demonstrated against an FSDB produced by a `WAVES=1` run.

## Workstream 6 — mex

`npm install -g mex-agent` (user npm-global dir already on PATH; Node 22.14 ≥ 22.5) → `mex setup` → wiki populated from the repo → mex's CLAUDE.md anchor section merged into our canonical `CLAUDE.md` (delegator `AGENTS.md` unchanged). Known limit documented: the code graph parses Python/TS/JS/Rust only — no SystemVerilog — so the graph covers the DV/python side; RTL/TB knowledge is curated wiki pages kept honest by `mex check` in the review cadence.

**Fence interaction (WS7): two mex instances.** The full tree's mex carries `ci/fence.yaml`'s globs in its ignore config **and** a wiki-authoring rule: no page may paraphrase fenced content (a summary of the existing testlist in an allowed page would defeat the fence). The clean-room clone gets its **own** `mex setup` — its graph and wiki are built only from visible files, so fenced knowledge cannot enter by construction.

**Gate:** `mex check` green; one `mex graph scope` query returning sensible context for a DV task.

## Workstream 7 — Knowledge fence (clean-room generation)

**Requirement:** the auto-DV generation phase (testplan, tests, TB components) must not use existing DV collateral — including local modifications to open-source imports. Upstream open-source tools (spike, riscv-dv) and the RTL itself remain fair game. Multiple people will work in this model; the fence must be persistent, pullable, and documented.

**Fenced content** (single source of truth: `ci/fence.yaml`, globs + one-line rationale each; first cut):
- `dv/uvm/core_ibex/tests/**`, `riscv_dv_extension/**`, `directed_tests/**` — existing test content
- `dv/uvm/core_ibex/fcov/**` — human coverage model
- `dv/uvm/core_ibex/env/**`, `common/**` agent internals — interfaces exposed via `docs/dv/TB_CONTRACT.md` instead. **Curated at file granularity:** interface-defining files (sequence items, virtual interface definitions, hook/API packages) are marked *allowed* so Zone A code can compile against them — they carry no stimulus/checking/coverage knowledge; drivers, monitors, scoreboards, sequences, tests stay fenced. Where a file mixes both, extract an interface package into an allowed path.
- `doc/03_reference/testplan.rst`, `coverage_plan.rst`, `verification.rst` — human answers
- `vendor/patches/**`, `dv/cosim/**` — local modifications to open-source imports
- the lowRISC spike fork (`ibex_cosim` branch, built by WS1) — Zone B equipment only; Zone A may build its own reference-model integration from **upstream** `riscv/riscv-isa-sim`
- `docs/dv/COSIM.md` — documents local-mod internals
(Exact list finalized at implementation; the manifest is the auditable artifact.)

**Zone A — clean room (generation).** A published **`cleanroom` branch with orphan snapshot history**: `ci/sync-cleanroom.sh` builds a tree of allowed paths only (from the manifest) and appends it as a snapshot commit (orphan root; no ancestry to `master`), then pushes; it fails if any fenced glob would enter the snapshot. Because no commit in the branch's history ever contained a fenced blob, a clean clone is airtight:

```
git clone --single-branch --branch cleanroom https://github.com/fzhangTT/ibex.git ibex-cleanroom
```

`--single-branch` fetches only that branch's objects — fenced blobs are absent from the clone entirely, not merely hidden. Updates are plain `git pull` (append-only snapshots, no force-push). **User entry point:** `ci/make-cleanroom.sh` automates the whole thing from a freshly pulled `master` — it performs the single-branch clone into a sibling dir (default `../ibex-cleanroom`, configurable), verifies zero fenced files anywhere in the clone (history included), and leaves the user checked out on `cleanroom` ready to `git checkout -b cleanroom/<topic>`. It is deliberately a **separate clone, never `git worktree`** — worktrees share the parent's object store, so fenced blobs would remain retrievable. Note `cleanroom` reflects `master` as of the last sync (Jenkins job or manual `ci/sync-cleanroom.sh`). Generation work happens on branches off `cleanroom`; `ci/land-from-cleanroom.sh` lands finished work onto a `master`-based branch (paths are disjoint from fenced ones — mechanical diff apply) for normal PR review. A sparse-checkout script (`ci/make-cleanroom-sparse.sh`) is provided as a *human convenience only*, documented with its caveat: the local object store still contains fenced history, so it is a view, not a boundary.

**Zone A local validation.** The cleanroom is self-sufficient for static validation of its own code: `ci/cleanroom-compile.sh` runs (1) verilator `--lint-only` against `rtl/` (fast, no license), (2) VCS analysis/elaboration of generated units + DUT (no simv run), (3) python checks (venv import/collect). Design rule: **if Zone A code cannot compile without fenced sources, the coupling exceeds the contract — fix the contract/interface files, never grant a fence exception.**

**Zone B — execution/evaluation (full tree).** Runs generated artifacts on trusted infra; trusted infra is never read by generators. Cleanroom users reach it only by submission: `ci/zoneb-submit.sh [--compile-only]` (run from the cleanroom) pushes the `cleanroom/<topic>` branch and triggers Zone B execution — the Jenkins job when available, or the documented fallback of running `ci/zoneb-run.sh <branch>` in a sibling full clone. `--compile-only` is the fast feedback path (does the overlay build against the full TB?); its report redacts fenced paths from compile logs (error text kept, fenced file paths replaced by `<fenced>`; errors anchored in Zone A files return in full detail). For humans operating both zones, `FENCE.md` states the honor-system boundary: what returns to generation work is the sanitized report, nothing else; agent sessions get this enforced (they only ever see the report file).
- `ci/zoneb-run.sh <cleanroom-branch>` — overlays the Zone A diff onto a full `master` tree, runs the stock flow. The existing cosim (lowRISC spike fork + `dv/cosim`) still executes — it is Zone B *equipment* — but it is an **evaluation-only measurement, not a referee the AI may rely on**: the AI's deliverable must carry its own checking (TB contract, WS2), re-derived from upstream imports as part of the challenge.
- `ci/zoneb-report.sh` — the deterministic result filter; the only channel back to Zone A. It **classifies failure sources**: failures from the AI's *own* checks return to Zone A in full detail (verdicts from `trr.yaml`/`regr.log`, log excerpts, its own fcov results); **existing-cosim findings and human-fcov results route to the human evaluation report only**. Whether Zone A ever receives a minimal binary "blind referee flagged this test" signal is a challenge-phase decision — default off (even the existence bit leaks "your checker missed something here"). Coverage follows the **three-scope policy**:
  1. **Code coverage** (line/toggle/branch/FSM) — feeds back freely; derives from the DUT.
  2. **Generated functional coverage** (Zone A's own model) — full feedback loop, including the fcov-expectation check (declared-but-unhit bins fail the test).
  3. **Human fcov model** — evaluation-only blind benchmark, run in Zone B for humans; never returned to Zone A (even bin names would contaminate the generator's coverage-model design).

**Enforcement stack (defense in depth):** (1) physical — the cleanroom clone; (2) tool-level — a `PreToolUse` hook keyed on `IBEX_DV_FENCE=1` blocks Read/Grep/Glob on manifest globs for full-tree sessions that must be fenced (codex equivalent via sandbox config where possible); (3) CI — the sync script's validation plus a `fence-integrity` review rubric (WS3); (4) advisory — CLAUDE.md/AGENTS.md challenge-mode section. **Session hygiene:** generation experiments run in fresh sessions seeded only from Zone A — infra sessions (like this one) are contaminated by design and never do generation; persistent memory stays free of DV-content specifics.

**Docs:** `docs/dv/FENCE.md` — what is fenced and why, the one-command clone, update/branch/land workflows, the Zone B protocol, and the rules for humans and agents.

**Gate:** `cleanroom` branch published and re-synced by CI; `ci/make-cleanroom.sh` produces a clone containing zero manifest-glob files (`git log --all` included); one full round-trip demonstrated — a dummy artifact authored in Zone A, executed via `ci/zoneb-run.sh`, results returned through `ci/zoneb-report.sh` with verdict routing shown (an AI-check failure comes back; an injected existing-cosim finding is withheld and appears only in the evaluation report), landed on a `master` branch.

## Order & verification

WS1 first (everything depends on a working sim). WS2/WS3/WS4/WS5 can proceed in parallel after WS1; WS7 after WS2/WS3 (needs the TB contract and the rubric/hook homes); WS6 last (wants the final file layout, and the clean-room mex needs WS7's branch). Every workstream ends with its gate's *evidence* (logs, reports, committed artifacts), not claims. One branch, one commit series per workstream.

## Out of scope (follow-on specs)

- Test-plan generation and the coverage-closure agent loop (the actual challenge experiments).
- CHERIoT-enabled verification (needs a CHERIoT-aware reference model).
- Per-test LSF fan-out (phase 2, only if single-job parallelism is insufficient).
- Porting quasar's mako DPI generator (hand-written DPI exports suffice for milestone B).
