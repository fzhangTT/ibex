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
serve self-test still passed because its fixture gained the new manifest key only with the implementation. That red is a
missing-constant crash raised while the case tuples are built, before any case runs (CM136-L-3): it shows the tests could not pass
without the implementation, not that the cases discriminate a missing refusal from a present one.
gen_b8_probe_refusal_red2.log is the TDD red of the CM136 follow-up: the gen_run cases run against the factored measured_refusal
before the LOG-067 rule was added to it and print BAD for the three B8 cases while the P6 cases pass (a discriminating red); the
util, serve and round cases of the same touch are again missing-constant crashes (B8_PROBE_SV_DEFAULT_KEY, CANARY_REFUSED_B8_PROBE).
gen_log077_red.log is the TDD red of the LOG-077 enforcement (plan-owner ruling Q-018): the constants, the knob-table helpers and
the cases in place, measured_knob_condition_refusal a stub returning None and no loader or gen_run rule; the five refuse cases print
BAD while the positive cases and the const check pass, a discriminating red; then the rule was written and all cases pass.
gen_log077_red2.log is the TDD red of the CM152-M-1 fix: the required checker row was judged without the TB's master enable
(gen_chk_en: chk_all ? val : (set && val)), so the three chk_all cases print BAD before the fix while the isolation-mode case
(chk_all off, the row set on) and the operator-restores case pass; then checker_row_on mirrors the precedence and all pass.
gen_cm153_fcov_home_red.log is the TDD red of the CM153-L-1 loader rule on fcov_expectation_file, run on a detached archive of
daf27d0 with the handed CM152 flow files and the three l12 fields null: the cases in place and no rule, the three refuse cases
(a manifest outside dv/auto_dv/fcov_expectations, a missing file, a measured entry with another test's stem) print BAD while the
two positive cases (an unmeasured group manifest in the home, null) pass; the build-input gate case 13 BAD is the archive's
missing .git, not part of this red. Then the rule was written and all pass. Re-retained at CM157-L-3 without the 190-column cut
of the first copy (the refuse cases carry the distinct want tokens of CM157-I-1), from the loader with the rule block removed;
like every red here it is the self-test's output filtered to the case lines and the verdict (grep -E on CM153, the two positive
labels, SELF-TEST BAD, Error and SELF-TEST:), byte-exact within that filter, not the whole 112-line output (CM160-I-1).
gen_cm155_checker_value_red.log is the TDD red of the CM155 value-parsing fix (the review of the CM152 gate fix): the cases in
place and the old parsing (a bare +row counted as set, =00 counted as on): the four refuse cases print BAD (a bare row under
the master enable off, +gen_chk_all=00, +row=00, a non-numeric row value under the master enable off) while the non-numeric
master case passes; then checker_knob_state reads the knobs as the SV's =%d parse does and all pass. That fifth case
(+gen_chk_all=x runs) passed under the old and the new reader alike and is wrong by VCS's actual conversion; CM159-M-1 flips it
to a refuse case (see gen_cm159_vcs_value_red.log).
gen_cm159_vcs_value_red.log is the TDD red of the CM159 fix: VCS's $value$plusargs("name=%d") matches on the name= prefix and
converts a non-decimal remainder to 0 (yes, off, false, empty, 0x1, 1abc all read set with value 0; a bare +name never matches;
u is 32 bits), while the CM155 reader called those unset and fell to the table default 1: eight cases print BAD before the fix
(the flipped fifth case, =false, = empty, =0x1, =1abc, +gen_chk_all=false, =4294967296, the bare-then-= ordering) and four pass
(=off and =yes under the master enable off, which the unset path already refused; =-1 runs; =0 before =1 refuses).

gen_cm162_vcs_probe.log is Runtime's own VCS probe (X-2025.06-SP2) of `$value$plusargs("x=%d", u)` with `int unsigned u`, run
before the CM162 fix was coded: 29 FORM lines, each one simv run with the form as one argv token (whitespace, underscore,
sign, empty, non-decimal, wrap and first-occurrence forms), followed by the probe source; the retained copy is the log plus
that source trailer, so its md5 is not the bare run log's.
gen_cm162_whitespace_underscore_red.log is the TDD red of the CM162-L-1 and L-2 fix: the ten new cases against the CM159
reader on a detached archive of 3bf3d6b; the three whitespace cases and the four underscore run cases print BAD while the
three underscore refuse cases pass (a discriminating red); the gate case 13 BAD line is the archive's missing .git (git
ls-files), not part of the red, and is kept because the excerpt filter keeps every BAD line; then the strip was dropped, the
regex widened and all ten pass (129 ok, case 13 the only BAD in the archive).
| evidence path | source | bytes | md5 |
|---|---|---|---|
| dv/auto_dv/evidence/gen_tdd_logs/flow/gen_gate_rule_red.log | dv/auto_dv/work/runtime/gate_rule_red.log | 926 | 78b72aae6509d2776a43c9314808b01b |
| dv/auto_dv/evidence/gen_tdd_logs/flow/gen_t235_ut_run.log | dv/auto_dv/work/runtime/t235/gen_t235_ut_run.log | 17932 | 642eb85258afe2f6a0dbe38169ae9fb0 |
| dv/auto_dv/evidence/gen_tdd_logs/flow/gen_t235_install_verification.diff | dv/auto_dv/work/runtime/t235/scratch/gen_isa_shim_install_verification.diff | 1733 | 426d1881834219787850d7acd9e47338 |
| dv/auto_dv/evidence/gen_tdd_logs/flow/gen_b8_probe_refusal_red.log | dv/auto_dv/work/runtime/b8_probe_refusal_red.log | 669 | 79c2e3e5ad16318c78ea72c156e17b02 |
| dv/auto_dv/evidence/gen_tdd_logs/flow/gen_b8_probe_refusal_red2.log | dv/auto_dv/work/runtime/b8_probe_refusal_red2.log | 2231 | d9c707ba179d81930b8edb06f3440db0 |
| dv/auto_dv/evidence/gen_tdd_logs/flow/gen_log077_red.log | dv/auto_dv/work/runtime/log077_red.log | 2027 | f6a061ae1b4f3a7f9ff24004975ecafb |
| dv/auto_dv/evidence/gen_tdd_logs/flow/gen_log077_red2.log | dv/auto_dv/work/runtime/log077_red2.log | 1239 | cc6584b37c1fe68356a5aeefeeb98ec9 |
| dv/auto_dv/evidence/gen_tdd_logs/flow/gen_cm153_fcov_home_red.log | (runtime scratchpad) cm157/red_full.log | 1344 | 6c86dc2d8b7ae805107a85d5235ebe43 |
| dv/auto_dv/evidence/gen_tdd_logs/flow/gen_cm155_checker_value_red.log | (runtime scratchpad) cm155/red.log | 1266 | 492bf8cda8363303c4dda4a34fd93821 |
| dv/auto_dv/evidence/gen_tdd_logs/flow/gen_cm159_vcs_value_red.log | dv/auto_dv/work/runtime/cm159_red.log | 2244 | 5230a37ea1af24d47533598d49a2d3c4 |
| dv/auto_dv/evidence/gen_tdd_logs/flow/gen_cm162_vcs_probe.log | (runtime scratchpad) cm162/probe/probe.log + gen_knob_probe.sv | 2390 | 7f3cccd42a44567dd75ae3ac4f448d70 |
| dv/auto_dv/evidence/gen_tdd_logs/flow/gen_cm162_whitespace_underscore_red.log | (runtime scratchpad) cm162/red.log | 2176 | 9b2ee182f9e500422e5dc0a057e0fd7d |
