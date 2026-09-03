# MCP servers (Zone A cleanroom)

Both clients (`.mcp.json` for Claude Code, `.codex/config.toml` for codex) declare the same three
LOCAL servers. This clone ships no remote MCP server, and adding any server requires a fence
review (`docs/dv/FENCE.md`).

| Server | Version | Purpose |
|---|---|---|
| `siliconpilot` | 0.18.1 (pinned) | HW-workflow agent tools (incl. `cone_of_influence` for exclusion arguments) |
| `fsdb-mcp-server` | 0.2.6 (pinned) | wave debug from FSDB |
| `verdi-cov-mcp` | v0.2.2 (pinned) | coverage DB queries — core tool for the coverage-closure loop |

## Zone scoping

Point these tools only at THIS clone's own out-tree artifacts — the FSDBs, coverage databases,
and logs your own runs produce (advisory rule; the fence authority is `docs/dv/FENCE.md`).
Nothing produced outside this clone is a legal input.

## Client setup (one-time)

- **codex**: codex only merges a repo's `.codex/config.toml` MCP servers into its running config
  when that repo is marked trusted in the *global* config — add
  `[projects."<absolute-repo-path>"] trust_level = "trusted"` to `$CODEX_HOME/config.toml` first.
  Symptom otherwise: `codex mcp list` (or `codex doctor`) shows zero servers configured, with no
  error pointing at trust as the cause.
- **Claude Code**: project-scoped MCP servers (`.mcp.json`) need one-time approval per project —
  either accept the interactive trust prompt on first use, or, for non-interactive sessions, set
  `"enabledMcpjsonServers": ["siliconpilot", "fsdb-mcp-server", "verdi-cov-mcp"]` in
  `.claude/settings.local.json` (gitignored; each contributor sets their own).

## Wrapper pattern

Each server has a thin launcher in this directory (`siliconpilot-mcp.sh`, `fsdb-mcp.sh`,
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
`.mcp.json`'s location, so a session launched from a repo subdirectory (e.g. `dv/auto_dv/`)
failed all three local servers.

## Wave-dump policy

FSDB dumping happens only on wave-enabled runs (gate it via `$VERDI_HOME` plus your dump tcl —
`docs/dv/SIM_RECIPE.md` §6), so the debug-access cost of `fsdb-mcp-server` is only paid when
someone is actually debugging.
