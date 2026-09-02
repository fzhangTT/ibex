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
- [ ] T3: Gate part 1 — tool-list evidence from both a Claude Code and a codex session.
- [ ] T4: Gate part 2 — fsdb-mcp demonstrated against a real `WAVES=1` FSDB.

PENDING-WS7: gate item 3 (the cleanroom clone demonstrates *no* MCP servers configured) cannot be
proven before WS7 exists. WS5 does not close DONE from this plan; end-state stays
**PARTIAL — gate item 3 pending WS7** until WS7's plan produces that evidence and flips this line.
