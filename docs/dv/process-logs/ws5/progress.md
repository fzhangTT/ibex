# WS5 ledger — plan: docs/superpowers/plans/2026-09-02-ws5-mcp-servers.md

Spec: docs/superpowers/specs/2026-09-01-auto-dv-setup-design.md §Workstream 5 (binding).
Pre-execution gate: codex APPROVE round 5 (docs/dv/reviews/2026-09-02-codex-plan-2026-09-02-ws5-mcp-servers.md, commit d04e5bba).

## Task status

- [x] T1: `ci/mcp/` wrapper scripts — `ci/env.sh` `IBEX_MCP_*` exports + `$VERDI_HOME/bin` PATH prepend;
      `ci/mcp/{siliconpilot-mcp,fsdb-mcp,verdi-cov-mcp}.sh`. siliconpilot `latest` resolved to `0.18.1`
      (`readlink -f`, 2026-09-02). Startup smoke: failing-first (pre-chmod, permission denied) then all
      three answer `initialize` + `tools/list` over stdio; fsdb probe re-verified with ambient PATH
      stripped. Finding (not a defect, recorded for T3/T4 probe design): fsdb-mcp-server's first
      `tools/list` call is slow (lazy import, observed ~15-20s) — a probe that closes stdin right after
      writing the request races the response and can drop it; the wrapper does nothing to cause or fix
      this, and a real MCP client's stdin stays open for the session so this does not surface there.
- [x] T2: Client configs — `.mcp.json` + `.codex/config.toml` (append) + `ci/mcp/README.md`. Codex
      config schema verified against the installed 0.149.1 binary two ways: (1) `codex mcp add --help`
      confirms the `--url` (http) vs positional-command (stdio) split; (2) `strings` on the standalone
      binary surfaced the live `codex mcp list`/`get` field order (`command`/`args`/`cwd`/`env` for
      stdio, `url`/`bearer_token_env_var`/`http_headers`/... for http, no `type` key) — matches the
      brief's TOML verbatim, so no dash-quoting was needed for `fsdb-mcp-server` (TOML bare keys allow
      `-`). Round-tripped live: `codex mcp add` against a scratch `CODEX_HOME` proved `[mcp_servers.*]`
      is the real table name (`tomllib` also parses our exact file); test entries removed after.
      Finding for T3 (not a defect, load-bearing for the gate): codex only merges a repo's local
      `.codex/config.toml` into the running config when that repo path is marked `trust_level =
      "trusted"` in the *global* `$CODEX_HOME/config.toml`'s `[projects."<repo>"]` table — confirmed
      by temporarily trusting `/localdev/fzhang/ws/ibex` (reverted after) and watching `codex mcp list`
      go from "no MCP servers configured" to listing all four servers with the exact command/args/url
      we wrote. Untrusted, `codex doctor` reports `MCP servers 0` even though the repo file parses
      fine — T3's codex-session gate must run from a trusted project (the normal one-time trust prompt)
      or it will read as a false negative. Validator: `VALIDATOR: PASS` after the `.codex/config.toml`
      edit. `.mcp.json` parses (`json.load`).
- [x] T3: Gate part 1 — tool-list evidence from both a Claude Code and a codex session.
      `docs/dv/evidence/ws5-mcp-toollist-{claude,codex}.txt`. Applied durably (per Task 2's finding):
      `[projects."/localdev/fzhang/ws/ibex"] trust_level = "trusted"` in the global codex config.
      Claude side: full PASS both launch dirs, after a fix — `$CLAUDE_PROJECT_DIR` does not anchor to
      the repo root (it's the *session launch dir*, confirmed against Claude Code's own docs), so a
      session started from `dv/uvm/core_ibex/` broke all three local servers; `.mcp.json` now uses
      `$(git rev-parse --show-toplevel)` (matches codex's mechanism) instead. `ci/mcp/README.md`
      updated to match. Codex side: two real defects found and fixed durably in `.codex/config.toml` —
      (1) codex's default `shell_environment_policy` strips the site-profile inheritance
      `ci/env.sh`'s own contract requires (`module load synopsys/vcs/...` silently no-ops, `vcs
      missing` fails closed) — fixed with `[shell_environment_policy] inherit = "all"`; (2) the
      default 10s `startup_timeout_sec` is tight against `ci/env.sh`'s module-load cost plus fsdb's
      lazy-import latency — bumped to 60s for all three local servers. A direct MCP protocol probe
      (initialize + tools/list under the same corrected environment) proves all three servers answer
      correctly (tool lists match Claude's exactly) — but `codex exec`'s own model-facing tool
      registry (`ALL_TOOLS`, dumped in full: 84 entries) never surfaces project stdio
      `[mcp_servers.*]` tools regardless, across 5 independent sessions and multiple mitigation
      attempts (feature-flag toggling, self-knowledge query for a tool-search mechanism) — recorded
      as an apparent codex-cli 0.149.1 product limitation (installed build is behind latest 0.152.1
      per `codex doctor`), not a wrapper/env/timeout defect. Atlassian: configured on both clients,
      not authenticated on either (Claude carries a pre-existing user-level OAuth session and answers
      fully; codex has none) — optional/non-blocking per the brief either way.
- [ ] T4: Gate part 2 — fsdb-mcp demonstrated against a real `WAVES=1` FSDB.

PENDING-WS7: gate item 3 (the cleanroom clone demonstrates *no* MCP servers configured) cannot be
proven before WS7 exists. WS5 does not close DONE from this plan; end-state stays
**PARTIAL — gate item 3 pending WS7** until WS7's plan produces that evidence and flips this line.
