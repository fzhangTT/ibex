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
gen_cm167_vcs_probe.log is the second run of the same probe (the CM162 simv) on the CM167 forms: `=1` followed by LF, CR or CR LF,
`=` LF `1`, and the sign-position forms `_-1`, `+-1`, `--1`, `-`, `+`, `1-`, `-_-1`, `_+1`; every one reads set with u=0, `=1` reads 1;
the forms script is appended as the trailer.
gen_cm167_newline_red.log is the TDD red of the CM167-L-1 fix on a detached archive of 12411be: ten new cases against the CM162 reader;
the LF-after-the-digit case (the regex's `$` before a trailing newline) and the LF-before-the-digit case (plusarg_name's `.*` stopping
at the newline, a hole found while writing the red) print BAD while CR, CR LF and the six sign forms pass (a discriminating red); the gate
case 13 BAD line is again the archive's missing .git; then fullmatch and the `[\s\S]*` value group make all ten pass (139 ok).
gen_cm168_testlist_whitespace_red.log is the TDD red of the CM168-I-1 fix on a detached archive of ce1bda0: four new
cases append a plusarg whose value carries a space, a tab, a trailing LF and a CR to an entry; all four print BAD against
the unfixed loader while every one of the 139 pre-existing cases passes (a discriminating red: the four are the only new
failures, confirmed against a pristine control archive of the same commit, which shows 139 ok and the same single BAD);
the gate case 13 BAD line is the archive's missing .git (git ls-files), not part of the red, and is kept because the
excerpt filter keeps every BAD line; then the loader refuses whitespace inside a testlist plusarg token and all four
pass (143 ok, case 13 the only BAD in the archive). The excerpt is the redirected output of
`command grep -E 'CM168-I-1|^SELF-TEST BAD|^SELF-TEST: ' red_full.log`, never retyped; that command reproduces the
retained bytes exactly, and the 139 / 143 counts above are its own, re-derived with command grep rather than the
shell's ugrep wrapper.

gen_cm174_data_ecc_condition_red.log is the TDD red of the second MEASURED_KNOB_CONDITIONS row on a detached archive of
dde456f: seven new helper cases and three new gen_run cases for the data-RAM ECC rate. The three helper refuse cases (rate
rare with the alert_minor row off, rate frequent with the master enable off and the row unmentioned, tag rate none while the
data rate is rare) and the one gen_run refuse case print BAD against the single-row table, while the four helper accept cases
and the two gen_run accept cases pass, so the red discriminates the missing row rather than the whole condition path. The
seventh helper case is an accept and stays one: the bit-count knob at two with both rates at their default none must run,
because the bit count injects nothing by itself. The gate case 13 BAD line is the archive's missing .git. With the row in
place all ten pass (helper 150 ok, gen_run 24 ok). The excerpt is the redirected output of
`command grep -h -E 'data-RAM rate|tag rate none but data rate|bit count at two|LOG-077 data half|^SELF-TEST BAD|^SELF-TEST: ' red_util.log red_run.log`,
never retyped, and the -h keeps the two source names out of the retained lines.

gen_f1_probe_measured_red.log is the TDD red of the widened P6 condition on a detached archive of dde456f: four new
gen_run cases for a debug-only knob in a measured run. The two coverage-off refuse cases (the stub knob and the P9
icache lookup probe) print BAD against the measured-and-coverage condition, while the coverage-on refuse case and the
unmeasured accept case pass, so the red discriminates the coverage term rather than the whole P6 path. With the term
dropped all four pass (gen_run 28 ok) and no other self-test moves. The excerpt is the redirected output of
`command grep -h -E 'P6 \(F1\)|^SELF-TEST BAD|^SELF-TEST: ' red_run.log`, never retyped.

gen_l14_merge_verify.log is the merge verification of the gen_l14 touch, retained on CR-F14-L-1 because the response
row cited it while it lived only in the gitignored work tree. It is the redirected output of the commands it names,
never retyped: the merged testlist digest, the constant drift check, the eight flow self-tests, the loader entry
count, the red-signature check, the excerpt tool self-test, and both testlist tools, followed by the eleven gate
readings across the loader and the run path and the seven appended entries run through the run-path gate as authored.
Three of its self-test lines report a failure and are expected: gen_flow_util at rc=2 with BAD=1 (build-input gate
case 13), gen_serve_requests at rc=2 with BAD=1 (its case 12) and gen_mirror at rc=1 with ok=0. All three are
git-dependent (git ls-files, a HEAD-to-HEAD delta, and a git archive of HEAD) and fail only because a detached
archive carries no .git; on the tracked tree all three pass. The log is not an unexplained red.
Two of its lines name absolute scratch paths: those are the throwaway output destinations the two testlist tools were
given so they never write into evidence, and they are part of the commands' own output rather than added afterwards.
The readings it carries are independently pinned by the committed self-tests, which is the alternative CR-F14-L-1
offered; both now hold.

gen_log084_cross_parse.log is the LOG-084 corroboration the Orchestrator asked for: whether the fcov checker's
grpinfo parser keys cross bins under their cross. Measured on a real report rather than read off the parser, using
the checker's own urg invocation against tb-infra's WP-8 part-1 database with the per-test isolation confirmed at one
test, then running the checker's own parser on that report. It carries the three elements asked for: the report
excerpt showing the group, coverpoint and cross heading kinds; the parser's emitted key count; and the attribution
observed. Both halves hold: of 3959 emitted keys none carries any of the 96 cross names (so a declared cross bin
always reads unhit), and 3130 cross bins across 119 group-and-cross pairs are keyed under the group's last-seen
coverpoint, 56 of them with non-zero counts, one reporting 1200 hits that belong to a cross. The single name
collision found has zero on both sides here, so the summing mechanism is proven while an inflation for that key is
not demonstrated. The checker is the owner's file and was not edited. Its measurement sections are the redirected
output of the parser run rather than retyped text; the header lines that name the database and its build are written
by hand. That header names the build it claims: the sources were uncommitted in the shared tree when the report was
taken, and those contents landed afterwards as landing 23, all 75 entries of the build's own sources_sha256.txt
equalling their f0723d6 versions, so a later reader reproduces the report from a commit rather than guessing at its
tree. The parser defect stands regardless of the build, and three of the five live mis-attributions lie in covergroups
committed well before it.

gen_cr23_manifest_stem_red.log is the CR-23-L-1 red: the loader accepted an entry whose manifest declares a different
test, a wiring the per-entry check can never pass because gen_fcov validates the manifest against the entry name
before it reads coverage. Three sections, the first two the redirected self-test output and the third the rule run
against the committed testlist. It carries a control the other flow reds do not need: the red and green sections use
a fabricated entry, so section 3 loads the real committed testlist of e754a83 and shows the rule refusing
gen_test_pmc_ctrl_pin_off by name, which is the wiring that existed in the tree. Taken on an archive with that field
already nulled, so the red is the new case alone; without that the eight reverted entries would have refused too and
the red would not have isolated anything.

gen_cm202_manifest_test_field_red.log is the red for the loader's third equality, the named manifest's own declared
test against the entry name. Four sections: the cases against a stub helper that returns None, the same cases with
the helper implemented, a control on a REAL committed manifest because the first two use fabricated files, and the
committed testlist still loading with the rule in place. Two scope statements the log makes rather than leaves
implied: the helper reads one field and the manifest's full schema stays the directory sweep's business, and the red
sits on the helper rather than the loader because the loader refuses a manifest outside the manifest home before it
could read the field, so a loader-level fixture would mean writing a bad manifest into a committed directory during
a self-test. The rule is defense in depth against drift, not a hole being closed: a mismatch it catches needs the
sweep's equality and the stem rule both already satisfied.

gen_l25_fcov_exercised.log is the first execution of the fcov-expectation leg: until this run it was declared and
bound but had never run, which two roles found independently. Five sections: the nine verdicts from the isolated
form, the shared-root cross-check, the keyed output read bin by bin against a parser of the urg report written for
the purpose rather than against the checker's verdict line, the two owed bins that no manifest declares and that
only a direct reading finds, and a section saying what the run does not establish. Two forms were run and the log
says which figures come from which: one shared output root on my own judgment about the flow's isolation, then the
literal one-directory-and-database-per-entry form the Orchestrator asked for. The build identity in the header was
read against the source root the runs used rather than against the clone.

gen_l25_fcov_exercised_corrigendum.log carries everything added after gen_l25_fcov_exercised.log committed, because a
retained log's bytes and md5 do not move once its row is committed. It opens with the corrigendum: that log's header
claims the shared and isolated forms agreed on all nine verdicts and all 78 bins, and at the moment it committed that
claim rested on two entries of the nine. The claim is now measured over all nine and holds. The rest is that
measurement, the per-entry isolation evidence, every declared bin with its count, and the prefix-glob near-miss that
nearly reported the opposite. Nothing in the committed log is corrected beyond that one header sentence's provenance.

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
| dv/auto_dv/evidence/gen_tdd_logs/flow/gen_cm167_vcs_probe.log | (runtime scratchpad) l13/probe167.log + cm162/probe/run_probe167.sh | 1720 | bb0ad1b719b38c26c462ce04bcb4cc3f |
| dv/auto_dv/evidence/gen_tdd_logs/flow/gen_cm167_newline_red.log | (runtime scratchpad) l13/red167.log | 2245 | fd340befe73f21baa64c30030da0dbc6 |
| dv/auto_dv/evidence/gen_tdd_logs/flow/gen_cm168_testlist_whitespace_red.log | (runtime scratchpad) cm168/red_full.log | 870 | 17ce1af6f42a6a07ceb08ce9b14f4d78 |
| dv/auto_dv/evidence/gen_tdd_logs/flow/gen_cm174_data_ecc_condition_red.log | (runtime scratchpad) cm174/red_util.log + cm174/red_run.log | 1785 | c17a82573242002de87fa9f88921adc8 |
| dv/auto_dv/evidence/gen_tdd_logs/flow/gen_f1_probe_measured_red.log | (runtime scratchpad) f1/red_run.log | 594 | 4ffa5560c95bb2187ca21c2610339e06 |
| dv/auto_dv/evidence/gen_tdd_logs/flow/gen_l14_merge_verify.log | (runtime scratchpad) l14b/gen_l14_merge_verify.log | 4440 | 5e428524195514ac8d949a2565940955 |
| dv/auto_dv/evidence/gen_tdd_logs/flow/gen_log084_cross_parse.log | (runtime scratchpad) log084/gen_log084_cross_parse.log | 3728 | 4aeb2ea5928a7b87a1d5db89343374e9 |
| dv/auto_dv/evidence/gen_tdd_logs/flow/gen_cr23_manifest_stem_red.log | (runtime scratchpad) rt30/gen_cr23_manifest_stem_red.log | 2885 | 65b16eef885b324b9b9997c5ebe6c891 |
| dv/auto_dv/evidence/gen_tdd_logs/flow/gen_cm202_manifest_test_field_red.log | (runtime scratchpad) rt32/gen_cm202_manifest_test_field_red.log | 2838 | 383168720e28c1bacb84072cd346e9d8 |
| dv/auto_dv/evidence/gen_tdd_logs/flow/gen_l25_fcov_exercised.log | (runtime scratchpad) rt33/gen_l25_fcov_exercised.log | 8866 | d7ebcb05197e73e149655108a5c96ac3 |
| dv/auto_dv/evidence/gen_tdd_logs/flow/gen_l25_fcov_exercised_corrigendum.log | (runtime scratchpad) rt34a/gen_l25_fcov_exercised_corrigendum.log | 10240 | d9fadbf3e1e6dd7a6807fc704c4906b0 |
