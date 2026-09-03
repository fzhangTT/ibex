# Magic-Numbers Check

**Severity:** Critical
**Context:** diff_only
**Filters:** rtl/**/*.sv, dv/**/*.sv, dv/**/*.svh, dv/**/*.py, ci/**/*.sh

Flag added/changed lines that hand-encode values whose authority lives elsewhere:
- config parameter values duplicated outside `ibex_configs.yaml` / `ibex_pkg` (import or derive
  via `util/ibex_config.py`, don't re-type);
- CSR addresses/fields outside `ibex_pkg` / the team's single CSR-map home under `dv/auto_dv/`;
- tool paths outside `ci/env.sh` (the path-centralization rule);
- test lists / iteration counts duplicated outside the team's testlist yaml;
- DUT hierarchy path strings scattered in tests instead of the central handles home the TB
  defines under `dv/auto_dv/` (one per language domain — `dv_principles.md` §5).

Test-local arbitrary stimulus values (delays, toggle patterns, seeds) are fine when a comment says
so. Respond `{"status": "PASS"}` or the FAIL JSON per `GUIDE.md`.
