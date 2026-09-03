# Forces / Hierarchical-Access Check

**Severity:** Critical
**Context:** diff_only
**Filters:** dv/**/*.sv, dv/**/*.svh, dv/**/*.py

Reviewing **added lines** for signal forces / hierarchical pokes bypassing the proper driving path.

**FLAG when added without a clear in-code reason (a justifying comment on/within 2 lines):**
- SV: `force`/`release` on a hierarchical signal.
- cocotb: a value deposit bypassing the TB's own contract APIs — `<handle>.value = ...`,
  `.setimmediatevalue(...)`, deep `dut.<hierarchy>` drives instead of the central handles module
  the TB defines under `dv/auto_dv/` (the TB's own documented handshake bits are contract API,
  not violations — see `docs/dv/TB_CONTRACT.md`).

**Do NOT flag:** justified forces (the comment explains what it models and why no real path
exists); read-only handle access (`.value` reads, `==` compares).

The rule: drive through the contract; a raw force/poke must be explained. Bias toward PASS.
Respond `{"status": "PASS"}` or the FAIL JSON per `GUIDE.md`.
