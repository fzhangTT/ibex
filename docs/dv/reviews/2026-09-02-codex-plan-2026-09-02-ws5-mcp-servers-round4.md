# Cross-model review — plan/spec file(s): docs/superpowers/plans/2026-09-02-ws5-mcp-servers.md

**Reviewer:** codex-cli 0.149.1; run-reported: model: gpt-5.6-sol; reasoning effort: high
**Date:** 2026-09-02
**Target:** plan/spec file(s): docs/superpowers/plans/2026-09-02-ws5-mcp-servers.md

---

TARGET: docs/superpowers/plans/2026-09-02-ws5-mcp-servers.md@08b272d9

All supplied filtered rubrics PASS.

[major][docs/superpowers/plans/2026-09-02-ws5-mcp-servers.md:22] The wrapper recipe sources `ci/env.sh` but never adds `$VERDI_HOME/bin` to `PATH`, despite the WS5 spec requiring it. The installed fsdb-mcp 0.2.6 checks for `verdi` and `waveutils` on `PATH`; the current login environment masks this omission, while the VCS module loaded by `ci/env.sh` does not add Verdi — prepend `$VERDI_HOME/bin` centrally in `ci/env.sh` and verify the wrapper with the ambient Verdi path removed.

Final verdict: REQUEST-CHANGES
