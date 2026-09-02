# Cross-model review — plan/spec file(s): docs/superpowers/plans/2026-09-02-ws5-mcp-servers.md

**Reviewer:** codex-cli 0.149.1; run-reported: model: gpt-5.6-sol; reasoning effort: high
**Date:** 2026-09-02
**Target:** plan/spec file(s): docs/superpowers/plans/2026-09-02-ws5-mcp-servers.md

---

TARGET: docs/superpowers/plans/2026-09-02-ws5-mcp-servers.md@6a280caa

All supplied filtered rubrics PASS on this documentation-only target.

[major][docs/superpowers/plans/2026-09-02-ws5-mcp-servers.md:53] The planned wrappers hard-code site tool paths outside `ci/env.sh`, contradicting `dv_principles.md` §5 and `ci/env.sh`’s central-authority contract; lines 58 and 60 repeat the pattern — export the pinned MCP paths from `ci/env.sh`, reference those variables in the wrappers, and record resolved versions in wrapper comments and the README.

[major][docs/superpowers/plans/2026-09-02-ws5-mcp-servers.md:181] The FSDB demonstration omits the required design database: installed fsdb-mcp 0.2.6 requires `create_fsdb_session(design_db, fsdb_file, ...)`, so an FSDB path alone cannot open a waveform session — locate the corresponding `simv.daidir`, pass absolute `design_db` and `fsdb_file` paths, and capture successful session creation before the signal query.

[major][docs/superpowers/plans/2026-09-02-ws5-mcp-servers.md:194] The plan marks WS5 `DONE` while explicitly deferring the spec-mandated cleanroom no-MCP gate — keep WS5 pending until WS7 commits that evidence and then perform final closure/review, or amend the authoritative spec before execution.

[minor][docs/superpowers/plans/2026-09-02-ws5-mcp-servers.md:52] `>/dev/null 2>&1` suppresses stderr despite line 62 saying stderr may remain visible, hiding useful `ci/env.sh` diagnostics — redirect stdout only and preserve stderr for startup failures.

Final verdict: REQUEST-CHANGES
