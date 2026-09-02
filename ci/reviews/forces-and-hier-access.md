# Forces / Hierarchical-Access Check

**Severity:** Critical
**Context:** diff_only
**Filters:** dv/**/*.sv, dv/**/*.svh, dv/cocotb/**/*.py

Reviewing **added lines** for signal forces / hierarchical pokes bypassing the proper driving path.

**FLAG when added without a clear in-code reason (a justifying comment on/within 2 lines):**
- SV: `force`/`release` on a hierarchical signal.
- cocotb: a value deposit bypassing the contract APIs — `<handle>.value = ...`,
  `.setimmediatevalue(...)`, deep `dut.<hierarchy>` drives instead of the `dv/cocotb/common/`
  handles + TB_CONTRACT interfaces (the handshake bits `cctb_alive`/`cocotb_active` are contract
  API, not violations).

**Do NOT flag:** justified forces (the comment explains what it models and why no real path
exists); read-only handle access (`.value` reads, `==` compares).

The rule: drive through the contract; a raw force/poke must be explained. Bias toward PASS.
Respond `{"status": "PASS"}` or the FAIL JSON per `GUIDE.md`.
