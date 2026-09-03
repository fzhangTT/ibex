# Cross-model review — plan/spec file(s): docs/superpowers/plans/2026-09-02-ws5-mcp-servers.md

**Reviewer:** codex-cli 0.149.1; run-reported: model: gpt-5.6-sol; reasoning effort: high
**Date:** 2026-09-02
**Target:** plan/spec file(s): docs/superpowers/plans/2026-09-02-ws5-mcp-servers.md

---

TARGET: docs/superpowers/plans/2026-09-02-ws5-mcp-servers.md@d32b7b64

All supplied filtered rubrics PASS on this documentation-only target.

[major][docs/superpowers/plans/2026-09-02-ws5-mcp-servers.md:112] The `.mcp.json` commands are repo-relative, but Claude Code resolves them from the session launch directory, so launching from a repository subdirectory breaks all three local servers; the root-only gate would conceal this — invoke each wrapper through `bash -c` using the server-runtime `$CLAUDE_PROJECT_DIR`, as documented by [Claude Code](https://code.claude.com/docs/en/debug-your-config).

[major][docs/superpowers/plans/2026-09-02-ws5-mcp-servers.md:171] `claude mcp list` does not approve new project-scoped servers; it reports them as pending, and the subsequent non-interactive `claude -p` session cannot perform the required approval — explicitly start an interactive `claude` session, approve the `.mcp.json` servers through `/mcp`, then run the list and one-shot evidence commands. [Claude Code MCP documentation](https://code.claude.com/docs/en/mcp).

[major][docs/superpowers/plans/2026-09-02-ws5-mcp-servers.md:195] The plan names `simv.daidir`, but this repository’s VCS flow emits `out_ws5_waves/build/tb/vcs_simv.daidir` (`rtl_simulation.yaml` names the executable `vcs_simv` and metadata fixes the TB directory at `build/tb`) — specify the actual path or an exact `vcs_simv.daidir` discovery command so the FSDB gate is executable.

[minor][docs/superpowers/plans/2026-09-02-ws5-mcp-servers.md:212] The review-disposition path does not exist; the committed artifact is named `2026-09-02-codex-plan-2026-09-02-ws5-mcp-servers-round1.md` — correct the reference so the remediation trail is resolvable.

Final verdict: REQUEST-CHANGES
