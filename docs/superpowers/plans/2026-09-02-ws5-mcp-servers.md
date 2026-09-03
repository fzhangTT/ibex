# WS5 — MCP Servers Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Declare the same four MCP servers (siliconpilot, fsdb-mcp-server, verdi-cov-mcp, atlassian) for both Claude Code (`.mcp.json`) and codex (`.codex/config.toml`), launched through pinned repo wrapper scripts, with the spec's gate evidence.

**Architecture:** Launch logic lives once in `ci/mcp/*.sh` wrappers (single source of truth — dv_principles §5); both client configs point at the wrappers. The pinned site-install paths are **exported by `ci/env.sh`** (`IBEX_MCP_SILICONPILOT`, `IBEX_MCP_FSDB_SERVER`, `IBEX_MCP_VERDI_COV`) — env.sh is the repo's single path authority — and the wrappers consume those variables after sourcing env.sh (which also provides VERDI_HOME). The whole server set is **Zone B / full-tree only** (spec WS5 zone-scoping amendment): the WS7 cleanroom snapshot replaces both client configs with no-MCP Zone A variants.

**Tech Stack:** MCP over stdio (JSON-RPC), bash wrappers, Claude Code `.mcp.json`, codex `config.toml`.

**Spec:** `docs/superpowers/specs/2026-09-01-auto-dv-setup-design.md` §Workstream 5.

## Global Constraints

- Recon'd site installs (verified on disk 2026-09-02):
  - siliconpilot: `/tools_risc/tt/siliconpilot/latest/bin/siliconpilot-mcp --workspace .` (spec-given launch line; resolve and record the `latest` symlink target version in the wrapper header comment at implementation time).
  - fsdb-mcp-server: environment module `fsdb-mcp-server/{0.2.1,0.2.5,0.2.6}` → `/tools_soc/tt/fsdb-mcp-server/<ver>/start_server.sh` (needs `VERDI_HOME`; `ci/env.sh:29` exports `/tools_vendor/synopsys/verdi/X-2025.06-SP2`). **Pin 0.2.6** by absolute path (no module load needed — the module only prepends PATH).
  - verdi-cov-mcp: `/tools_vendor/tt/verdi_cov_npi_mcp/v0.2.2/mcp_env_wrap.sh` (**pin v0.2.2**; `stable` symlink exists but the spec demands an exact pinned version).
  - atlassian: `https://mcp.atlassian.com/v1/mcp` (http; no wrapper).
- Spec pinning rule: fsdb and verdi-cov versions are **exact and recorded**; siliconpilot follows the spec's `latest` path with the resolved version recorded.
- **Path authority (dv_principles §5):** the pinned install paths live ONLY in `ci/env.sh` as `IBEX_MCP_*` exports (with the pin recorded in the adjacent comment); wrappers reference the variables (`${IBEX_MCP_FSDB_SERVER:?...}`) and never repeat a `/tools_*` literal.
- Wrappers: bash, `set -euo pipefail` is fine here (no post-failure reporting needed), compute `REPO_ROOT` from `BASH_SOURCE`, `source "$REPO_ROOT/ci/env.sh" >/dev/null` — **stdout only**: the MCP stdio stream owns stdout, but stderr stays visible so env.sh diagnostics surface on startup failures (never `&&`-chain `module`) — then `exec` the site entry point so signals pass through.
- Zone scoping is recorded wherever a config lives: comment in `.codex/config.toml`, section in `ci/mcp/README.md` (`.mcp.json` is JSON — no comments; README covers it).
- Error messages in ci scripts are an ASD-STE100 surface: short, imperative, unambiguous.
- Gate evidence under `docs/dv/evidence/ws5-*`; ledger `docs/dv/process-logs/ws5/progress.md`, one line per task.
- The gate item "the cleanroom clone demonstrates *no* MCP servers configured" **cannot be proven before WS7** (no cleanroom exists): WS5 therefore does NOT close as DONE from this plan. Its ledger end-state is **PARTIAL — gate item 3 pending WS7**; WS7's plan owns producing that evidence, and only then does WS5 flip to DONE (with the pointer recorded). The codex post-execution review at the end of this plan covers the executed scope.
- Run `.codex/compat/validator.py` after config/docs edits; must stay PASS.
- Commit after every task (`[ci]`/`[docs]` prefixes).

---

### Task 1: `ci/mcp/` wrapper scripts

**Files:**
- Modify: `ci/env.sh` (add the `IBEX_MCP_*` exports — the single path authority)
- Create: `ci/mcp/siliconpilot-mcp.sh`
- Create: `ci/mcp/fsdb-mcp.sh`
- Create: `ci/mcp/verdi-cov-mcp.sh`
- Create: `docs/dv/process-logs/ws5/progress.md` (ledger skeleton mirroring this plan's tasks, plus the PENDING-WS7 line for the cleanroom no-MCP gate item)

**Interfaces:**
- Consumes: site installs from Global Constraints; `ci/env.sh` (VERDI_HOME export).
- Produces: `IBEX_MCP_SILICONPILOT`/`IBEX_MCP_FSDB_SERVER`/`IBEX_MCP_VERDI_COV` exported by `ci/env.sh`; three executable wrappers, each launching one MCP server over stdio. Both client configs (Task 2) invoke exactly these wrapper paths.

- [ ] **Step 1: Add the pinned exports to `ci/env.sh`** (near the VERDI_HOME export; follow the file's existing comment style):

```bash
# --- MCP server installs (WS5; Zone B only — the cleanroom ships no MCP configs) ---
# Exact pins recorded here; wrappers in ci/mcp/ consume these (dv_principles §5).
export IBEX_MCP_SILICONPILOT=/tools_risc/tt/siliconpilot/latest/bin/siliconpilot-mcp  # latest -> <resolved version: record readlink -f output here>
export IBEX_MCP_FSDB_SERVER=/tools_soc/tt/fsdb-mcp-server/0.2.6/start_server.sh       # pinned 0.2.6
export IBEX_MCP_VERDI_COV=/tools_vendor/tt/verdi_cov_npi_mcp/v0.2.2/mcp_env_wrap.sh   # pinned v0.2.2
# fsdb-mcp needs verdi/waveutils as commands (an alias does not reach subprocesses).
case ":$PATH:" in *":$VERDI_HOME/bin:"*) ;; *) export PATH="$VERDI_HOME/bin:$PATH";; esac
```
Run `readlink -f /tools_risc/tt/siliconpilot/latest` and replace the placeholder with the actual resolved version string before committing. Place the PATH prepend AFTER the existing `VERDI_HOME` export (`ci/env.sh:29`); the guard keeps re-sourcing idempotent.

- [ ] **Step 2: Write the three wrappers**

`ci/mcp/fsdb-mcp.sh`:
```bash
#!/usr/bin/env bash
# fsdb-mcp-server launcher; pinned path exported by ci/env.sh (IBEX_MCP_FSDB_SERVER).
# Needs VERDI_HOME; ci/env.sh exports it. Zone B only — never ship to the cleanroom (spec WS5/WS7).
set -euo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
# stdout only: the MCP stdio stream owns stdout; keep stderr for env.sh diagnostics.
source "$REPO_ROOT/ci/env.sh" >/dev/null || { echo "ERROR: cannot source ci/env.sh" >&2; exit 1; }
SERVER="${IBEX_MCP_FSDB_SERVER:?ci/env.sh must export IBEX_MCP_FSDB_SERVER}"
[ -x "$SERVER" ] || { echo "ERROR: fsdb-mcp-server not found at $SERVER" >&2; exit 1; }
exec "$SERVER"
```

`ci/mcp/verdi-cov-mcp.sh` — same skeleton; `SERVER="${IBEX_MCP_VERDI_COV:?ci/env.sh must export IBEX_MCP_VERDI_COV}"`.

`ci/mcp/siliconpilot-mcp.sh` — same skeleton; `SERVER="${IBEX_MCP_SILICONPILOT:?ci/env.sh must export IBEX_MCP_SILICONPILOT}"`; launch `exec "$SERVER" --workspace "$REPO_ROOT"`.

Caveat to preserve: sourcing `ci/env.sh` with **stdout** silenced is required — MCP stdio protocol owns stdout; env.sh banner lines would corrupt the JSON-RPC stream. Stderr stays visible so startup failures carry their diagnostics.

- [ ] **Step 3: Startup smoke (failing first, then passing)** — before `chmod +x`, run one wrapper and watch it fail (permission); then `chmod +x ci/mcp/*.sh` and verify each starts and answers a raw JSON-RPC handshake over stdio:

```bash
for w in ci/mcp/*.sh; do
  echo "=== $w ==="
  printf '%s\n' \
    '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"probe","version":"0"}}}' \
    '{"jsonrpc":"2.0","method":"notifications/initialized"}' \
    '{"jsonrpc":"2.0","id":2,"method":"tools/list"}' \
    | timeout 120 "$w" | head -c 2000; echo
done
```
Expected per server: an `initialize` result and a `tools/list` result naming at least one tool. This is the wrapper-level sanity check; the client-level gate is Task 3. If a server needs a one-time `setup.sh`/venv step, STOP and record what it needs in the ledger before proceeding (do not run site-install setup scripts without recording them).

Then prove the fsdb wrapper does not lean on the ambient login PATH (the login shell has Verdi; a Jenkins or MCP-client environment may not): re-run the fsdb probe with the ambient Verdi stripped —
```bash
env PATH=/usr/bin:/bin bash -c 'printf "%s\n" "<the three JSON-RPC lines>" | timeout 120 ci/mcp/fsdb-mcp.sh | head -c 2000'
```
It must still answer (env.sh's own PATH prepend supplies `verdi`/`waveutils`), and `command -v verdi` inside a fresh `bash -c 'source ci/env.sh >/dev/null; command -v verdi'` must resolve under `$VERDI_HOME/bin`.

- [ ] **Step 4: Commit**

```bash
git add ci/env.sh ci/mcp docs/dv/process-logs/ws5
git commit -m "[ci] WS5: MCP path exports in env.sh + server wrappers (fsdb 0.2.6, verdi-cov v0.2.2)"
```

---

### Task 2: Client configs — `.mcp.json` + `.codex/config.toml`

**Files:**
- Create: `.mcp.json`
- Modify: `.codex/config.toml` (append `[mcp_servers.*]` tables; keep the existing keys untouched)
- Create: `ci/mcp/README.md`

**Interfaces:**
- Consumes: wrapper paths from Task 1.
- Produces: both clients configured with the same four servers; README documenting zone scoping and the wrapper pattern.

- [ ] **Step 1: Write `.mcp.json`** — Claude Code resolves server commands from the session **launch directory**, not the project root, so a bare repo-relative command breaks when a session starts in a subdirectory. Anchor through the server-runtime `$CLAUDE_PROJECT_DIR`:

```json
{
  "mcpServers": {
    "siliconpilot":    { "command": "bash", "args": ["-c", "exec \"$CLAUDE_PROJECT_DIR/ci/mcp/siliconpilot-mcp.sh\""] },
    "fsdb-mcp-server": { "command": "bash", "args": ["-c", "exec \"$CLAUDE_PROJECT_DIR/ci/mcp/fsdb-mcp.sh\""] },
    "verdi-cov-mcp":   { "command": "bash", "args": ["-c", "exec \"$CLAUDE_PROJECT_DIR/ci/mcp/verdi-cov-mcp.sh\""] },
    "atlassian":       { "type": "http", "url": "https://mcp.atlassian.com/v1/mcp" }
  }
}
```
The Task 3 gate must include one Claude session started from a repository **subdirectory** to prove the anchoring works.

- [ ] **Step 2: Append to `.codex/config.toml`** — codex may resolve relative commands against the launch cwd, not the repo root, so anchor via git:

```toml
# MCP servers (WS5). Zone B / full tree ONLY — the WS7 cleanroom snapshot ships a
# no-MCP variant of this file (spec §WS5 zone scoping). Launch logic lives in
# ci/mcp/*.sh (single source of truth); entries here only locate those wrappers.
[mcp_servers.siliconpilot]
command = "bash"
args = ["-c", "exec \"$(git rev-parse --show-toplevel)/ci/mcp/siliconpilot-mcp.sh\""]

[mcp_servers.fsdb-mcp-server]
command = "bash"
args = ["-c", "exec \"$(git rev-parse --show-toplevel)/ci/mcp/fsdb-mcp.sh\""]

[mcp_servers.verdi-cov-mcp]
command = "bash"
args = ["-c", "exec \"$(git rev-parse --show-toplevel)/ci/mcp/verdi-cov-mcp.sh\""]

[mcp_servers.atlassian]
url = "https://mcp.atlassian.com/v1/mcp"
```
Verify the exact table/key names against `codex mcp --help` / codex 0.149.1 docs at implementation time (TOML key syntax for http servers differs across versions); if a name with a dash is rejected as a TOML key, quote it (`[mcp_servers."fsdb-mcp-server"]`). Record what was verified in the ledger.

- [ ] **Step 3: Write `ci/mcp/README.md`** — sections: the four servers (one line each: purpose per spec table + pinned version); wrapper pattern (env.sh sourcing with stdout silenced — stdio protocol; exec); **Zone scoping** (Zone B only; why: fsdb/coverage servers can read blind evaluation data, `siliconpilot --workspace` is not a sandbox; cleanroom ships no-MCP configs — enforced by WS7's snapshot; any future Zone A MCP addition requires a fence review); wave-dump policy (FSDB only on `WAVES=1` runs — stock `vcs.tcl` + `$VERDI_HOME` gating, cost only paid when debugging).

- [ ] **Step 4: Run the validator** (`.codex/config.toml` changed) — expected PASS.

- [ ] **Step 5: Commit**

```bash
git add .mcp.json .codex/config.toml ci/mcp/README.md
git commit -m "[ci] WS5: declare MCP servers for Claude (.mcp.json) and codex (config.toml)"
```

---

### Task 3: Gate part 1 — tool-list from both clients

**Files:**
- Create: `docs/dv/evidence/ws5-mcp-toollist-claude.txt`
- Create: `docs/dv/evidence/ws5-mcp-toollist-codex.txt`

**Interfaces:**
- Consumes: Tasks 1–2 configs.
- Produces: the spec-gate evidence that each local server starts and answers a tool-list request from both a Claude Code and a codex session **in this repo**.

- [ ] **Step 1: Claude side** — project-scoped `.mcp.json` servers need approval first, and a non-interactive `claude -p` session cannot grant it. Approve non-interactively with an **explicit allowlist** in `.claude/settings.local.json` (gitignored, machine-local; record the setting in the evidence file): `"enabledMcpjsonServers": ["siliconpilot", "fsdb-mcp-server", "verdi-cov-mcp", "atlassian"]` — never `enableAllProjectMcpServers: true`, which would silently auto-approve any future `.mcp.json` addition and bypass the per-server trust gate. If the allowlist knob is unavailable in the installed CLI version, start an interactive `claude` session and approve via `/mcp`. Then run `claude mcp list` and a one-shot session: `claude -p 'For each connected MCP server, list its name and the names of its tools. Output text only.'` — once from the repo root and once from `dv/uvm/core_ibex/` (proves the `$CLAUDE_PROJECT_DIR` anchoring). Save the outputs (trimmed to the relevant lines) to `docs/dv/evidence/ws5-mcp-toollist-claude.txt` with the invocation lines. **The gate binds on the three local servers** — each must appear with ≥1 tool, and a local server that fails to start is a finding to fix, not to elide. Atlassian is spec-optional and OAuth-gated: record its configured state (and authentication state, if logged in) separately in the evidence; it does not block the gate.

- [ ] **Step 2: codex side** — `codex exec 'For each configured MCP server, list its name and the names of its tools. Output text only.'` from the repo root; save to `docs/dv/evidence/ws5-mcp-toollist-codex.txt`. Same gate scope as Step 1: the three local servers bind; atlassian's state is recorded separately. Watchdog both steps (~10 min each; servers that hang on startup count as failures).

- [ ] **Step 3: Commit** — tick T3 in the ledger.

```bash
git add docs/dv/evidence/ws5-mcp-toollist-claude.txt docs/dv/evidence/ws5-mcp-toollist-codex.txt docs/dv/process-logs/ws5/progress.md
git commit -m "[dv] WS5 gate: MCP tool-list evidence from Claude and codex sessions"
```

---

### Task 4: Gate part 2 — fsdb-mcp against a real WAVES=1 FSDB

**Files:**
- Create: `docs/dv/evidence/ws5-fsdb-demo.txt`

**Interfaces:**
- Consumes: `ci/jenkins/smoke.sh` (WS4) or the direct make flow; `ci/mcp/fsdb-mcp.sh`.
- Produces: spec-gate evidence that fsdb-mcp works against an FSDB produced by this repo's flow.

- [ ] **Step 1: Produce an FSDB** — `bash -lc 'source ci/env.sh && cd dv/uvm/core_ibex && make SIMULATOR=vcs IBEX_CONFIG=opentitan ISS=spike TEST=riscv_arithmetic_basic_test ITERATIONS=1 SEED=1 WAVES=1 OUT=out_ws5_waves'` (fresh OUT; watchdog 45 min). Locate the `.fsdb` under `out_ws5_waves/run/tests/`.

- [ ] **Step 2: Query it through fsdb-mcp** — fsdb-mcp 0.2.6 requires the VCS design database alongside the waveform: `create_fsdb_session(design_db, fsdb_file, ...)`. Locate the run's design DB at `out_ws5_waves/build/tb/vcs_simv.daidir` (this flow's VCS executable is `vcs_simv` in `build/tb` — `rtl_simulation.yaml`; fallback discovery: `find out_ws5_waves/build -maxdepth 3 -name '*.daidir' -type d`) and the `.fsdb` under `out_ws5_waves/run/tests/`, then — in a Claude session with the project servers loaded, or via raw JSON-RPC `tools/call` on the wrapper — create the session with BOTH absolute paths, capture the successful session creation, and query top-level scope + a signal value (e.g. the core clock) at a timestamp. Save the session-creation call, its result, and the query + response excerpt to `docs/dv/evidence/ws5-fsdb-demo.txt`. The demo must show real data from OUR fsdb (both paths echoed in the evidence), not just a successful tool registration (dv_principles §4: a mechanism explained but not observed is a guess).

- [ ] **Step 3: Commit** — tick T4; mark the WS5 gate line in the ledger (end-state PARTIAL — cleanroom item pending WS7).

```bash
git add docs/dv/evidence/ws5-fsdb-demo.txt docs/dv/process-logs/ws5/progress.md
git commit -m "[dv] WS5 gate: fsdb-mcp demonstrated against a WAVES=1 FSDB"
```

---

## Workstream close (controller, not a subagent task)

Run the `cross-review` skill for the codex post-execution review of the WS5 commit range; commit the artifact; set the ledger to **PARTIAL — gate item 3 (cleanroom no-MCP demo) pending WS7**. WS5 flips to DONE only when WS7 commits that evidence; WS7's plan must carry this as an explicit deliverable. If verdi-cov-mcp tool queries will be exercised heavily in the challenge's coverage-closure loop, note in the ledger that a deeper verdi-cov demo (query against a real merged.vdb from WS4's coverage.sh output) is available as follow-on evidence — not required by the WS5 gate.

## Review disposition (codex pre-review round 1 — REQUEST-CHANGES)

Findings from `docs/dv/reviews/2026-09-02-codex-plan-2026-09-02-ws5-mcp-servers-round1.md`, each addressed in this revision:
1. **[major] hardcoded site paths in wrappers** — pinned paths moved to `ci/env.sh` `IBEX_MCP_*` exports (Task 1 Step 1); wrappers consume the variables with `:?` guards and carry no `/tools_*` literals.
2. **[major] fsdb demo omits the design database** — Task 4 Step 2 now locates `simv.daidir`, passes absolute `design_db` + `fsdb_file` to `create_fsdb_session`, and captures the session creation before the signal query.
3. **[major] DONE while a spec gate item is deferred** — WS5 end-state changed to PARTIAL pending WS7's cleanroom evidence (Global Constraints + Workstream close); no spec amendment needed.
4. **[minor] stderr suppressed when sourcing env.sh** — wrappers silence stdout only; stderr preserved for diagnostics.

## Review disposition (codex pre-review round 2 — REQUEST-CHANGES)

Findings from `docs/dv/reviews/2026-09-02-codex-plan-2026-09-02-ws5-mcp-servers-round2.md`, each addressed in this revision:
1. **[major] `.mcp.json` relative commands resolve from the launch dir** — commands now anchor through server-runtime `$CLAUDE_PROJECT_DIR` via `bash -c`; the Task 3 gate adds a session launched from `dv/uvm/core_ibex/` to prove it.
2. **[major] project servers need approval `claude -p` cannot grant** — Task 3 Step 1 now approves via `"enableAllProjectMcpServers": true` in `.claude/settings.local.json` (or interactive `/mcp` if that knob is unavailable), recorded in the evidence.
3. **[major] wrong daidir path** — corrected to `out_ws5_waves/build/tb/vcs_simv.daidir` with a `find` fallback.
4. **[minor] stale artifact reference** — round-1 disposition now points at the `-round1.md` filename.

## Review disposition (codex pre-review round 3 — REQUEST-CHANGES)

Findings from `docs/dv/reviews/2026-09-02-codex-plan-2026-09-02-ws5-mcp-servers-round3.md`, each addressed in this revision:
1. **[major] `enableAllProjectMcpServers` over-approves future servers** — replaced with the explicit `enabledMcpjsonServers` four-server allowlist (CLI 2.1.258 supports it), interactive `/mcp` as fallback.
2. **[minor] atlassian is optional/OAuth-gated** — gate now binds on the three local servers only; atlassian's configured/auth state is recorded separately in both evidence files.

## Review disposition (codex pre-review round 4 — REQUEST-CHANGES)

Finding from `docs/dv/reviews/2026-09-02-codex-plan-2026-09-02-ws5-mcp-servers-round4.md`, addressed in this revision:
1. **[major] `$VERDI_HOME/bin` never reaches PATH** (env.sh only aliases `verdi`; fsdb-mcp 0.2.6 needs `verdi`/`waveutils` as commands; the login environment masked it) — `ci/env.sh` gains an idempotent `PATH` prepend after the `VERDI_HOME` export, and Task 1's startup smoke re-runs the fsdb probe with the ambient PATH stripped to prove the wrapper stands alone.
