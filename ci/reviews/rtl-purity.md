# RTL-Purity Check

**Severity:** Critical
**Context:** diff_only
**Filters:** rtl/**/*.sv, rtl/**/*.svh

`rtl/` is the DUT. Flag ANY added/changed line under `rtl/` that introduces TB constructs:
- `force`/`release` statements, or `bind` statements written INSIDE `rtl/` (DV-side bind files
  living under `dv/auto_dv/` that bind INTO rtl are the correct pattern and out of scope);
- TB/sim conditional guards (`COCOTB_SIM`, coverage-only macros, test-only `ifdef`s);
- `tb_`/`gen_`-prefixed signals, shadow muxes, observability-only ports;
- DPI imports/exports serving testbench purposes.

All of these belong under `dv/auto_dv/`. Intent-level violations count too (an RTL port added
only for TB observability). Respond `{"status": "PASS"}` or the FAIL JSON per `GUIDE.md`.
