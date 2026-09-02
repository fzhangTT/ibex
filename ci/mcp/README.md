# MCP servers (WS5)

Both clients (`.mcp.json` for Claude Code, `.codex/config.toml` for codex) declare the same four
servers.

| Server | Version | Purpose |
|---|---|---|
| `siliconpilot` | 0.18.1 (`latest` symlink, resolved 2026-09-02) | HW-workflow agent tools |
| `fsdb-mcp-server` | 0.2.6 (pinned) | wave debug from FSDB |
| `verdi-cov-mcp` | v0.2.2 (pinned) | coverage DB queries — core tool for the coverage-closure loop |
| `atlassian` | remote (`https://mcp.atlassian.com/v1/mcp`) | optional, matches siblings |

## Client setup (one-time)

- **codex**: codex only merges a repo's `.codex/config.toml` MCP servers into its running config
  when that repo is marked trusted in the *global* config — add
  `[projects."<absolute-repo-path>"] trust_level = "trusted"` to `$CODEX_HOME/config.toml` first.
  Symptom otherwise: `codex mcp list` (or `codex doctor`) shows zero servers configured, with no
  error pointing at trust as the cause.
- **Claude Code**: project-scoped MCP servers (`.mcp.json`) need one-time approval per project —
  either accept the interactive trust prompt on first use, or, for non-interactive sessions, set
  `"enabledMcpjsonServers": ["siliconpilot", "fsdb-mcp-server", "verdi-cov-mcp", "atlassian"]` in
  `.claude/settings.local.json` (gitignored; each contributor sets their own).

## Wrapper pattern

Each local server has a thin launcher in this directory (`siliconpilot-mcp.sh`, `fsdb-mcp.sh`,
`verdi-cov-mcp.sh`): export `IBEX_ENV_TOOLCHECK=off` (these wrappers never invoke vcs/gcc/python3
themselves, so they skip `ci/env.sh`'s fail-loud toolchain check — see `ci/env.sh` for the flag),
source `ci/env.sh` with stdout silenced — the stdio MCP transport owns stdout, so only stderr
carries `env.sh` diagnostics — verify the wrapper's own real prerequisites (its `IBEX_MCP_*` var,
plus `VERDI_HOME` for the two Verdi-backed servers), then `exec` the pinned binary. `exec` keeps
the launcher out of the process tree so the client talks directly to the server. Both client
configs invoke the wrapper through a shell (`bash -c ...exec "$(git rev-parse --show-toplevel)/
ci/mcp/*.sh"`) so the absolute wrapper path resolves the same regardless of which directory the
client session was launched from. `$CLAUDE_PROJECT_DIR` is *not* used for this: in the installed
Claude Code CLI (2.1.258) it resolved to the directory the session started in, not to
`.mcp.json`'s location, so a session launched from a repo subdirectory (e.g. `dv/uvm/core_ibex/`)
failed all three local servers — a WS5 T3 gate finding
(`docs/dv/evidence/ws5-mcp-toollist-claude.txt`).

## Zone scoping

This MCP set is **Zone B / full-tree only**. `fsdb-mcp-server` and `verdi-cov-mcp` can read blind
evaluation data, and `siliconpilot --workspace` is not a sandbox — so the cleanroom ships its own
agent configs with **no MCP servers** (WS7's snapshot replaces `.mcp.json`/`.codex/config.toml` with
Zone A variants). Any future Zone A MCP addition requires a fence review.

## Wave-dump policy

FSDB dumping happens only on `WAVES=1` runs (the stock `vcs.tcl` flow gates this via `$VERDI_HOME`),
so the debug-access cost of `fsdb-mcp-server` is only paid when someone is actually debugging.
