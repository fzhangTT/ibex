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
      the repo root (it's the *session launch dir*, observed on the installed CLI, 2.1.258), so a
      session started from `dv/uvm/core_ibex/` broke all three local servers; `.mcp.json` now uses
      `$(git rev-parse --show-toplevel)` (matches codex's mechanism) instead. `ci/mcp/README.md`
      updated to match. Codex side (fix round 1, after cross-review found the first pass's causal
      claim doubtful): only one real config defect survives — the default 10s `startup_timeout_sec`
      is tight against `ci/env.sh`'s module-load cost plus fsdb's lazy-import latency, fixed with
      `startup_timeout_sec = 60` on the three local servers. The originally-claimed second defect
      (`[shell_environment_policy] inherit = "all"`) was a no-op — 0.149.1 already ships that as its
      default (confirmed by removing the block and reproducing the identical `vcs missing` failure
      byte-for-byte) — and has been removed from `.codex/config.toml`. That `vcs missing` failure,
      specifically in codex's own eager MCP-server-spawn path, remains unexplained by anything in
      this repo's control on either 0.149.1 or 0.152.1. The literal gate itself now PASSES: per
      controller ruling, `bash -lc 'codex update'` upgraded 0.149.1 -> 0.152.1, and a plain re-run of
      the brief's exact `codex exec` prompt (no overrides) answered with real tool names for all
      three local servers, matching the Claude side exactly. Atlassian: configured on both clients,
      not authenticated on either (Claude carries a pre-existing user-level OAuth session and answers
      fully; codex has none) — optional/non-blocking per the brief either way.
- [x] T4: Gate part 2 — fsdb-mcp demonstrated against a real `WAVES=1` FSDB.
      `docs/dv/evidence/ws5-fsdb-demo.txt`. Produced a fresh FSDB with the verified flow
      (`make SIMULATOR=vcs IBEX_CONFIG=opentitan ISS=spike TEST=riscv_arithmetic_basic_test
      ITERATIONS=1 SEED=1 WAVES=1 OUT=out_ws5_waves`, 100% PASS, well inside the 45-min
      watchdog). Drove `ci/mcp/fsdb-mcp.sh` over raw JSON-RPC stdio with both absolute paths
      (`out_ws5_waves/build/tb/vcs_simv.daidir`, `out_ws5_waves/run/tests/
      riscv_arithmetic_basic_test.1/waves.fsdb`): `create_fsdb_session` opened a real session
      (session_id, `mode: waveform`, correct `file_info.max_time`/`scale_unit`, 7-8s elapsed —
      a real NPI/Verdi open, not a stub); `get_child_modules(scope="")` returned the real
      top-level scope listing including `core_ibex_tb_top` (matches
      `tb/core_ibex_tb_top.sv` exactly); `get_internal_signals` found `core_ibex_tb_top.clk`;
      `sample_signals_at_time` returned a real value at 500000ns; `get_time_range` over the
      first 50ns returned 3 real clock-bring-up transitions (x -> 0 @16.76ns -> 1 @44.35ns) as
      extra non-guessable corroboration. Two protocol findings (not wrapper/config defects,
      recorded in the evidence file): the fsdb-digger/PyNPI session-open path writes a stray
      non-JSON diagnostic line straight to stdout (`logDir = ...`), and fastmcp answers
      concurrent `tools/call` requests out of send order — any raw-JSON-RPC probe must skip
      non-JSON stdout lines and match responses by their `"id"` field, not by arrival order.

Gate part 1 (T3) and gate part 2 (T4) are both closed. Gate item 3 remains open per below.

PENDING-WS7: gate item 3 (the cleanroom clone demonstrates *no* MCP servers configured) cannot be
proven before WS7 exists. WS5 does not close DONE from this plan; end-state stays
**PARTIAL — gate item 3 (cleanroom no-MCP demo) pending WS7** until WS7's plan produces that
evidence and flips this line.
