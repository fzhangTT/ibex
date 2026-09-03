# Retained logs of the Runtime flow (owner: runtime)

Each row is a byte copy of the work-tree artifact in the source column (md5 of the copy, equal to the source at copy time); the
work-tree paths under dv/auto_dv/work/runtime/ are gitignored. gen_gate_rule_red.log is the TDD red of the build-input gate
(dv/auto_dv/docs/gen_build_input_gate_rule.md): both flow self-tests run with the gate cases in place and no implementation, the
NameError (gen_flow_util, classify_delta) and the TypeError (gen_serve_requests, case 12) they died with, and rc=1 each.
gen_t235_ut_run.log is the out-of-tree verification run of T-235 part R (2026-09-03 21:10:25Z, soc-l-11): the ISA shim unit test
GEN_UT_ISA_SHIM PASS with 0 failures and 236 rows OK (its first line names the sources by sha256 prefix). It ran on the shim
gen_isa_shim.cc of commit 9e912bb plus the three install lines tb-infra later landed (the verification copy, sha256 af8e42f362a5),
the unit test gen_ut_isa_shim.cc of commit d752fb3 plus section 14 (the handed file, sha256 a9baa21394c8; 23 of the 236 rows), the
holders gen_isa_shim_counters.h a1fec0628276 and .cc 238f899ff36b (landed byte-identical at 158f5be), and the gen_boot_zc program
image of work/runtime/out/tick_canary_2057. It is not a run of the landed shim (34559ec69102) or unit test (c30369dd144e).

| evidence path | source | bytes | md5 |
|---|---|---|---|
| dv/auto_dv/evidence/gen_tdd_logs/flow/gen_gate_rule_red.log | dv/auto_dv/work/runtime/gate_rule_red.log | 926 | 78b72aae6509d2776a43c9314808b01b |
| dv/auto_dv/evidence/gen_tdd_logs/flow/gen_t235_ut_run.log | dv/auto_dv/work/runtime/t235/gen_t235_ut_run.log | 17932 | 642eb85258afe2f6a0dbe38169ae9fb0 |
