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

**Gate:** Milestone A and B logs + `COCOTB=0` regression identity.

## Workstream 3 — Skills, cross-model layer, review policy

**Topology** (ws-tensix pattern, verbatim): canonical `.claude/skills/` + `CLAUDE.md` as single source of truth; `AGENTS.md` is a thin delegator ("read CLAUDE.md" + client-mechanics translation table); `.agents/skills/shared → ../../.claude/skills` symlink for codex discovery; `.codex/compat/validator.py` (adapted) enforces the contract; `.codex/config.toml` with `project_doc_fallback_filenames = ["CLAUDE.md"]` + MCP servers.

**Curated skill set:**

| Skill/asset | Source | Adaptation |
|---|---|---|
| `docs/dv/dv_principles.md` | ws-tensix `dv_principles.md` | generalized to ibex; SV/UVM + cocotb idioms; new trust section: every checker/assertion/covergroup must be proven to fire |
| `dv-principles-check` | `iis-principles-check` | conformance review against our doc (not code review) |
| `mutation-check` | new (inspired by beowulf `meta/mutations`) | inject a bug (RTL or TB), show the new test/checker catches it, revert — required evidence for any generated DV component |
| `cross-review` | new | see policy below |
| review rubrics `ci/reviews/` | beowulf Sentinel rubrics | keep: assertion-integrity, magic-numbers, ai-slop-comments, test-overlap, rtl-purity, forces-and-hier-access; model-neutral prompt files run locally |
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

**Gate:** `mex check` green; one `mex graph scope` query returning sensible context for a DV task.

## Order & verification

WS1 first (everything depends on a working sim). WS2/WS3/WS4/WS5 can proceed in parallel after WS1; WS6 last (wants the final file layout). Every workstream ends with its gate's *evidence* (logs, reports, committed artifacts), not claims. One branch, one commit series per workstream.

## Out of scope (follow-on specs)

- Test-plan generation and the coverage-closure agent loop (the actual challenge experiments).
- CHERIoT-enabled verification (needs a CHERIoT-aware reference model).
- Per-test LSF fan-out (phase 2, only if single-job parallelism is insufficient).
- Porting quasar's mako DPI generator (hand-written DPI exports suffice for milestone B).
