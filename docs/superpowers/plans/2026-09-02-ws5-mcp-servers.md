# WS5 — MCP Servers Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Declare the same four MCP servers (siliconpilot, fsdb-mcp-server, verdi-cov-mcp, atlassian) for both Claude Code (`.mcp.json`) and codex (`.codex/config.toml`), launched through pinned repo wrapper scripts, with the spec's gate evidence.

**Architecture:** Launch logic lives once in `ci/mcp/*.sh` wrappers (single source of truth — dv_principles §5); both client configs point at the wrappers. Wrappers pin exact site-install versions and source `ci/env.sh` for environment (VERDI_HOME etc.). The whole server set is **Zone B / full-tree only** (spec WS5 zone-scoping amendment): the WS7 cleanroom snapshot replaces both client configs with no-MCP Zone A variants.

**Tech Stack:** MCP over stdio (JSON-RPC), bash wrappers, Claude Code `.mcp.json`, codex `config.toml`.

**Spec:** `docs/superpowers/specs/2026-09-01-auto-dv-setup-design.md` §Workstream 5.

## Global Constraints

- Recon'd site installs (verified on disk 2026-09-02):
  - siliconpilot: `/tools_risc/tt/siliconpilot/latest/bin/siliconpilot-mcp --workspace .` (spec-given launch line; resolve and record the `latest` symlink target version in the wrapper header comment at implementation time).
  - fsdb-mcp-server: environment module `fsdb-mcp-server/{0.2.1,0.2.5,0.2.6}` → `/tools_soc/tt/fsdb-mcp-server/<ver>/start_server.sh` (needs `VERDI_HOME`; `ci/env.sh:29` exports `/tools_vendor/synopsys/verdi/X-2025.06-SP2`). **Pin 0.2.6** by absolute path (no module load needed — the module only prepends PATH).
  - verdi-cov-mcp: `/tools_vendor/tt/verdi_cov_npi_mcp/v0.2.2/mcp_env_wrap.sh` (**pin v0.2.2**; `stable` symlink exists but the spec demands an exact pinned version).
  - atlassian: `https://mcp.atlassian.com/v1/mcp` (http; no wrapper).
- Spec pinning rule: fsdb and verdi-cov versions are **exact and recorded**; siliconpilot follows the spec's `latest` path with the resolved version recorded.
- Wrappers: bash, `set -euo pipefail` is fine here (no post-failure reporting needed), compute `REPO_ROOT` from `BASH_SOURCE`, `source "$REPO_ROOT/ci/env.sh"` (never `&&`-chain `module`), then `exec` the site entry point so signals pass through.
- Zone scoping is recorded wherever a config lives: comment in `.codex/config.toml`, section in `ci/mcp/README.md` (`.mcp.json` is JSON — no comments; README covers it).
- Error messages in ci scripts are an ASD-STE100 surface: short, imperative, unambiguous.
- Gate evidence under `docs/dv/evidence/ws5-*`; ledger `docs/dv/process-logs/ws5/progress.md`, one line per task.
- The gate item "the cleanroom clone demonstrates *no* MCP servers configured" **cannot be proven before WS7** (no cleanroom exists): record it in the ledger as DEFERRED-TO-WS7 with a pointer to spec §WS7; WS7's plan must pick it up.
- Run `.codex/compat/validator.py` after config/docs edits; must stay PASS.
- Commit after every task (`[ci]`/`[docs]` prefixes).

---

### Task 1: `ci/mcp/` wrapper scripts

**Files:**
- Create: `ci/mcp/siliconpilot-mcp.sh`
- Create: `ci/mcp/fsdb-mcp.sh`
- Create: `ci/mcp/verdi-cov-mcp.sh`
- Create: `docs/dv/process-logs/ws5/progress.md` (ledger skeleton mirroring this plan's tasks, plus the DEFERRED-TO-WS7 line for the cleanroom no-MCP gate item)

**Interfaces:**
- Consumes: site installs from Global Constraints; `ci/env.sh` (VERDI_HOME export).
- Produces: three executable wrappers, each launching one MCP server over stdio. Both client configs (Task 2) invoke exactly these paths.

- [ ] **Step 1: Write the three wrappers**

`ci/mcp/fsdb-mcp.sh`:
```bash
#!/usr/bin/env bash
# fsdb-mcp-server, pinned 0.2.6 (site module fsdb-mcp-server/0.2.6, PATH-only).
# Needs VERDI_HOME; ci/env.sh exports it. Zone B only — never ship to the cleanroom (spec WS5/WS7).
set -euo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
source "$REPO_ROOT/ci/env.sh" >/dev/null 2>&1 || { echo "ERROR: cannot source ci/env.sh" >&2; exit 1; }
SERVER=/tools_soc/tt/fsdb-mcp-server/0.2.6/start_server.sh
[ -x "$SERVER" ] || { echo "ERROR: fsdb-mcp-server 0.2.6 not found at $SERVER" >&2; exit 1; }
exec "$SERVER"
```

`ci/mcp/verdi-cov-mcp.sh` — same skeleton; `SERVER=/tools_vendor/tt/verdi_cov_npi_mcp/v0.2.2/mcp_env_wrap.sh`; header comment "pinned v0.2.2".

`ci/mcp/siliconpilot-mcp.sh` — same skeleton; `SERVER=/tools_risc/tt/siliconpilot/latest/bin/siliconpilot-mcp`; launch `exec "$SERVER" --workspace "$REPO_ROOT"`; header comment records the resolved `latest` target (run `readlink -f /tools_risc/tt/siliconpilot/latest` at implementation time and write the version string into the comment).

Caveat to preserve: sourcing `ci/env.sh` with stdout silenced is required — MCP stdio protocol owns stdout; env.sh banner lines would corrupt the JSON-RPC stream. Stderr may stay visible.

- [ ] **Step 2: Startup smoke (failing first, then passing)** — before `chmod +x`, run one wrapper and watch it fail (permission); then `chmod +x ci/mcp/*.sh` and verify each starts and answers a raw JSON-RPC handshake over stdio:

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

- [ ] **Step 3: Commit**

```bash
git add ci/mcp docs/dv/process-logs/ws5
git commit -m "[ci] WS5: pinned MCP server wrappers (siliconpilot, fsdb 0.2.6, verdi-cov v0.2.2)"
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

- [ ] **Step 1: Write `.mcp.json`** (project scope — Claude Code launches project MCP servers from the repo root, so repo-relative commands are safe):

```json
{
  "mcpServers": {
    "siliconpilot":    { "command": "ci/mcp/siliconpilot-mcp.sh" },
    "fsdb-mcp-server": { "command": "ci/mcp/fsdb-mcp.sh" },
    "verdi-cov-mcp":   { "command": "ci/mcp/verdi-cov-mcp.sh" },
    "atlassian":       { "type": "http", "url": "https://mcp.atlassian.com/v1/mcp" }
  }
}
```

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

- [ ] **Step 1: Claude side** — from the repo root run `claude mcp list` (approves/starts project servers; if it prompts for project-server trust, approve). Then a one-shot session: `claude -p 'For each connected MCP server, list its name and the names of its tools. Output text only.'`. Save both outputs (trimmed to the relevant lines) to `docs/dv/evidence/ws5-mcp-toollist-claude.txt` with the invocation lines. Every local server must appear with ≥1 tool; a server that fails to start is a finding to fix, not to elide.

- [ ] **Step 2: codex side** — `codex exec 'For each configured MCP server, list its name and the names of its tools. Output text only.'` from the repo root; save to `docs/dv/evidence/ws5-mcp-toollist-codex.txt`. Watchdog both steps (~10 min each; servers that hang on startup count as failures).

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

- [ ] **Step 2: Query it through fsdb-mcp** — in a Claude session with the project servers loaded, ask fsdb-mcp to open that FSDB and report top-level scope + a signal value (e.g. the core clock) at a timestamp; alternatively drive the wrapper with raw JSON-RPC `tools/call`. Save the query + response excerpt to `docs/dv/evidence/ws5-fsdb-demo.txt`. The demo must show real data from OUR fsdb (path echoed in the evidence), not just a successful tool registration (dv_principles §4: a mechanism explained but not observed is a guess).

- [ ] **Step 3: Commit** — tick T4; mark the WS5 gate line in the ledger (with the cleanroom item still DEFERRED-TO-WS7).

```bash
git add docs/dv/evidence/ws5-fsdb-demo.txt docs/dv/process-logs/ws5/progress.md
git commit -m "[dv] WS5 gate: fsdb-mcp demonstrated against a WAVES=1 FSDB"
```

---

## Workstream close (controller, not a subagent task)

Run the `cross-review` skill for the codex post-execution review of the WS5 commit range; commit the artifact; update the ledger to DONE (cleanroom no-MCP item explicitly handed to WS7's plan). If verdi-cov-mcp tool queries will be exercised heavily in the challenge's coverage-closure loop, note in the ledger that a deeper verdi-cov demo (query against a real merged.vdb from WS4's coverage.sh output) is available as follow-on evidence — not required by the WS5 gate.
