# Retained logs of the Runtime flow (owner: runtime)

Each row is a byte copy of the work-tree artifact in the source column (md5 of the copy, equal to the source at copy time); the
work-tree paths under dv/auto_dv/work/runtime/ are gitignored. gen_gate_rule_red.log is the TDD red of the build-input gate
(dv/auto_dv/docs/gen_build_input_gate_rule.md): both flow self-tests run with the gate cases in place and no implementation, the
NameError (gen_flow_util, classify_delta) and the TypeError (gen_serve_requests, case 12) they died with, and rc=1 each.
gen_t235_ut_run.log is the out-of-tree verification run of T-235 part R (2026-09-03 21:10:25Z, soc-l-11): the ISA shim unit test
GEN_UT_ISA_SHIM PASS with 0 failures and 236 rows OK; the facts the log itself carries are its first line's four sha256 prefixes
(counters.h, counters.cc, ut, shim-scratch) and its rows. Per Runtime's README it ran on the shim gen_isa_shim.cc of commit 9e912bb
plus the three install lines of gen_t235_install_verification.diff (retained below): applying that diff to the committed file of
9e912bb reproduces the verification copy, sha256 af8e42f362a5, the hash the first line names as shim-scratch (checked with patch),
the unit test gen_ut_isa_shim.cc of commit d752fb3 plus section 14 (the handed file, sha256 a9baa21394c8; 23 of the 236 rows), the
holders gen_isa_shim_counters.h a1fec0628276 and .cc 238f899ff36b (landed byte-identical at 158f5be), and, per the README (the log does not
name the image), the gen_boot_zc program image of work/runtime/out/tick_canary_2057. It is not a run of the landed shim
(34559ec69102) or unit test (c30369dd144e).
gen_b8_probe_refusal_red.log is the TDD red of the LOG-067 refusal (the B8 probe knob chk_sva_b8 on a measured entry): the util and
round self-tests with the new cases in place and no implementation die with AttributeError on the missing constants (rc=1); the
serve self-test still passed because its fixture gained the new manifest key only with the implementation.

| evidence path | source | bytes | md5 |
|---|---|---|---|
| dv/auto_dv/evidence/gen_tdd_logs/flow/gen_gate_rule_red.log | dv/auto_dv/work/runtime/gate_rule_red.log | 926 | 78b72aae6509d2776a43c9314808b01b |
| dv/auto_dv/evidence/gen_tdd_logs/flow/gen_t235_ut_run.log | dv/auto_dv/work/runtime/t235/gen_t235_ut_run.log | 17932 | 642eb85258afe2f6a0dbe38169ae9fb0 |
| dv/auto_dv/evidence/gen_tdd_logs/flow/gen_t235_install_verification.diff | dv/auto_dv/work/runtime/t235/scratch/gen_isa_shim_install_verification.diff | 1733 | 426d1881834219787850d7acd9e47338 |
| dv/auto_dv/evidence/gen_tdd_logs/flow/gen_b8_probe_refusal_red.log | dv/auto_dv/work/runtime/b8_probe_refusal_red.log | 669 | 79c2e3e5ad16318c78ea72c156e17b02 |
