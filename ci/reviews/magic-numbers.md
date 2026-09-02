# Magic-Numbers Check

**Severity:** Critical
**Context:** diff_only
**Filters:** rtl/**/*.sv, dv/**/*.sv, dv/**/*.svh, dv/**/*.py, dv/cocotb/**/*.py, ci/**/*.sh

Flag added/changed lines that hand-encode values whose authority lives elsewhere:
- config parameter values duplicated outside `ibex_configs.yaml` / `ibex_pkg` (import/derive, don't
  re-type — the `IBEX_CFG_*` define path exists so the TB never re-encodes config);
- CSR addresses/fields outside `ibex_pkg`/`csr_description.yaml`;
- tool paths outside `ci/env.sh` (the path-centralization rule from WS1);
- test lists / iteration counts duplicated outside the testlist yamls;
- DUT hierarchy path strings scattered in tests instead of the central handles home
  (`dv/cocotb/common/` for cocotb; the bind files for fcov).

Test-local arbitrary stimulus values (delays, toggle patterns, seeds) are fine when a comment says
so. Respond `{"status": "PASS"}` or the FAIL JSON per `GUIDE.md`.
