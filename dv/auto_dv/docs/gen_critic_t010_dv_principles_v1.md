# Critic: DV-principles conformance check of the T-010 regression flow (v1)

- Artifacts under review (committed, commit 8fa6b7a0955aafe2e58c6ce01cc5b69f1ee7d00f; no drift to
  HEAD 6b8d0ed: `git diff --quiet 8fa6b7a HEAD -- <files>` returns 0): dv/auto_dv/flow/
  gen_flow_const.py, gen_flow_util.py, gen_verdict.py, gen_build.py, gen_run.py, gen_regress.py,
  gen_cov_report.py, gen_serve_requests.py, gen_dashboard.py, gen_testlist.yaml, gen_cm_hier.cfg,
  gen_pli.tab, gen_dump.tcl; dv/auto_dv/docs/gen_runtime_api.md, gen_dashboard.md;
  dv/auto_dv/evidence/gen_t010_compile_path.md.
- Standard: docs/dv/dv_principles.md (re-read for this check), per the dv-principles-check skill:
  conformance only, section citations, not a general code review. Related Critic rulings applied:
  dv/auto_dv/docs/gen_critic_exclusions_draft_v1.md R-5 (flow rules for exclusions).
- Date (UTC): 2026-09-03 05:50
- Reviewer role: critic (Claude Fable 5.1). Verified on this host: `gen_verdict.py --self-test`
  (12/12 PASS), `gen_flow_const.py --check` (PASS), the on-disk artifacts under the shared out
  root /proj_soc/user_dev/fzhang/ibex_dv_out (regress_t010_smoke, regress_req_runtime-001,
  t010_smoke_cov) and dv/auto_dv/work/runtime/results, the gen_dump.tcl rendering, ci/env.sh's
  IBEX_ENV_TOOLCHECK handling, and prim_assert's ASSERT_ERROR path. Build configuration:
  opentitan. No LSF command was issued by the Critic. No fence event.

CRITIC VERDICT: REQUEST-CHANGES

Severity counts: high 0, medium 4, low 6, info 6. The flow is well built: one constants home
with a machine check against the SV package, one seed recorded at time zero on both sides,
verdicts from collected mechanisms with a self-tested scanner, purpose-gated run requests,
deterministic manifests, and an evidence file whose claims I could confirm on disk. The four
medium findings are: the failure path has only been proven on fabricated log lines, never on a
real failing simulation (P-01); a marker-present run with a non-zero exit code or a missing
$finish still passes (P-02); the documented --waves path raises a Python exception before any
simulation (P-03); two committed documents disagree on the coverage scope, and the difference is
2420 duplicated toggle objects in the gate denominator (P-04).

## Findings (format: [section bullet] file:line - what violates it - the conforming alternative)

### P-01 (medium) [S6 trust triad rule 1 TDD and "Self-proving checks"; S2 "Know your failure path and prove it once"]
dv/auto_dv/flow/gen_verdict.py:87-117 and dv/auto_dv/evidence/gen_t010_compile_path.md - the
self-test drives `scan_log` with fabricated lines (for example `Fatal: "tb.sv", 371: tb: at
time 5`); it proves the scanner's logic, not that a real VCS failure produces those lines. Every
verdict on disk is PASS (9 result records under the out root, 0 FAIL/TIMEOUT); no red run has
been through gen_run.py, no TIMEOUT (rc 124 / `timeout -k`) has been observed, and the LSF
kill path (`killed_reason`) has never fired. The evidence file therefore proves the green path
only. - Record one real red run per mechanism reachable today, through gen_run.py on LSF, in an
evidence addendum: (a) an SV `$fatal` (gen_smoke with `--plusarg +gen_smoke_cycles=1`, which
retires nothing) showing the real `Fatal:` line and `GEN_SMOKE_FAIL` classified FAIL with the
`reason` field; (b) a TIMEOUT (`--timeout-s 1` on gen_smoke) showing rc 124 and verdict TIMEOUT;
(c) a missing end marker (a run whose pass_marker is set to a string the TB never prints). Add
the three real log excerpts as self-test cases so the scanner is pinned to the true formats.
UVM_ERROR/UVM_FATAL and assertion-failure red runs follow when a UVM top and a DUT assertion
trigger exist (prim_assert.sv:27-30: under +define+UVM an RTL assertion failure becomes a
uvm_report_error, so the UVM_ERROR pattern is the one that must be proven for assertions).

### P-02 (medium) [S2 "Fail through a mechanism the flow actually collects"; S4 "Don't hide failures"; TB_CONTRACT.md Section 6 vacuous-pass guard]
dv/auto_dv/flow/gen_verdict.py:58-64 and :107 (self-test case "marker but no finish" wants PASS),
dv/auto_dv/flow/gen_run.py:184 - with a `pass_marker` set, PASS requires only that the marker
string occurs somewhere in sim.log; `$finish` is not required and the exit code is never used.
A simulation that prints the marker and then dies without a message in sim.log (a simv crash,
signal 11 or 9 reported only in lsf.err / run.log, an LSF wall-limit kill on a local run) is
recorded PASS with `exit_code: 139` beside it. SIM_RECIPE Section 5 forbids deciding from the
exit code ALONE; it does not forbid using a non-zero exit code as an additional failure signal,
and a false PASS is the failure mode both documents guard against. The marker match is also a
substring match (`pass_marker in line`), so a diagnostic that quotes the marker counts as the
marker. - Rules: PASS requires marker AND (`$finish` seen OR exit code 0); a non-zero exit code
with no collected mechanism is FAIL "unexplained exit code <rc>"; match the marker as a whole
line (or line prefix); scan lsf.err and run.log for `Segmentation fault|Killed|core dumped|
Aborted`; flip self-test case 12 to FAIL and add the exit-code and stderr cases.

### P-03 (medium) [S4 "Evidence over inference" (a mechanism explained but not observed is a guess); S6 evidence over prose]
dv/auto_dv/flow/gen_run.py:56-61 with dv/auto_dv/flow/gen_dump.tcl:3-9, documented as working in
dv/auto_dv/docs/gen_runtime_api.md:101-102 - the template is rendered with `str.format`, but the
Tcl body contains literal braces (`if { [info exists ::env(VERDI_HOME)] } {`, `dump -add {
{tb_top} }`, bare `}`); rendering raises `KeyError: ' '` before any simulation starts (reproduced
on this host with the exact code path). Because gen_regress.py:245-246 calls `f.result()` on the
worker future, a `--waves` regression would abort without writing `status: done`. The out-root
directory `t010_dump_probe` holds URG full_exclusions dumps, not a wave probe: the --waves path
was never run. - Escape the Tcl braces (`{{`/`}}`) or use `string.Template`/`str.replace` on
the four `{name}` fields only; run one `--waves` repro (purpose 3) and record the FSDB/VPD file
in the evidence; state in the API document which paths are evidenced and which are not.

### P-04 (medium) [S5 "Single source of truth"; S4 "Evidence over inference"]
dv/auto_dv/flow/gen_cm_hier.cfg:4 and gen_testlist.yaml:34 (`+tree gen_smoke_tb_top.u_dut`: the
wrapper instance) versus dv/auto_dv/docs/gen_component_api_dut_top.md:87-88 (coverage scope is
`+tree <tb_top>.<dut>.u_ibex_core` and `+tree <tb_top>.<dut>.u_register_file`) - two committed
documents state different coverage scopes. The difference is measurable: the URG report shows
module gen_dut_top with TOGGLE 312/2420 and no other objects (report/modinfo.txt:3147-3150), so
the wrapper's own ports, each a wire to an ibex_core port, add 2420 objects (9 percent) to the
toggle denominator of 26958 and count every core-port toggle twice. Either scope is defensible
under DV_prompt Section 2 (the wrapper is the DUT by ruling, and it contains no logic); the
choice changes the gate number and must be one recorded decision. - The DV Lead rules (run-scope
owner); the testlist build entry (`dut_instance`) and the cm_hier template become the single
source and gen_component_api_dut_top.md Section 4 is corrected to match; if the wrapper ports
stay in scope, the exclusion file records why they are not excluded (or excludes them as
duplicates with the reviewer's approval, DV_prompt Section 4).

### P-05 (low) [Critic ruling gen_critic_exclusions_draft_v1.md R-5 item 1; DV_prompt Section 4 exclusions]
dv/auto_dv/flow/gen_cov_report.py:37-44 - `merge()` passes `-elfile` through without
`-excl_strict`; an exclusion entry that hides a covered object would load silently. No exclusion
file exists yet, so nothing is hidden today. - Add `-excl_strict` whenever an elfile is given
(and `-excl_embed` for the measured merge), and record the URG "Excluded" and "Unreachable"
counts from dashboard.txt in `coverage.totals`.

### P-06 (low) [S5 "Single source of truth"]
dv/auto_dv/flow/gen_flow_const.py:207-219 (`check_sv_constants`) - the SV/Python name check exists
and passes, but no flow step calls it; drift between gen_tb_pkg.sv and the Python constants
would surface only when someone runs `--check` by hand. Also gen_testlist.yaml:49 re-types the
plusarg name `gen_smoke_cycles` as YAML text with no validation against `PLUSARG_SMOKE_CYCLES`,
and gen_run.py:104 re-types the exit-code contract of ci/check_fcov_expectations.py
(`{0: PASS, 2: UNHIT, 1: PROTOCOL_ERROR}`). - Call `check_sv_constants()` at the start of
gen_build.py and gen_regress.py (die on mismatch); have `load_testlist` validate every
`+name=` in `plusargs` against the known plusarg set (TB constants plus the simulator/UVM names);
import or cite the checker's exit-code table from its module docstring.

### P-07 (low) [S6 trust triad rule 3 fcov-expectation; S4 "Don't hide failures"]
dv/auto_dv/flow/gen_regress.py:108-127 and gen_testlist.yaml:51 - a test with
`fcov_expectation_file: null` is silently exempt from the declared-bins check; the regression
summary does not say how many runs carried no expectation manifest. The smoke legitimately has
none today, but once covergroups exist a null manifest on a targeted or full-tier test is a
missing trust-triad artefact that would pass unnoticed. - Count `runs_without_fcov_manifest` in
`summary`, print it in the one-line summary and the dashboard, and make a null manifest a
FAIL for tiers other than smoke once the first covergroup lands (a testlist-level policy switch).

### P-08 (low) [S6 evidence: the config and tool record]
dv/auto_dv/flow/gen_build.py:106 - `re.search(r"Compiler version (\S+)")` never matches the VCS
compile.log (the file has no "Compiler version" line), so `compile_summary.compiler_version` is
null in every build manifest; the version is present through `tools.vcs` from `vcs -ID`, so
nothing is lost. - Drop the field or match the log's own header (`Chronologic VCS ... Version`).

### P-09 (low) [S1 "the TB prints a config banner at time 0"; S6]
dv/auto_dv/flow/gen_verdict.py and gen_run.py - the banner is passed as `+gen_build_config=
opentitan` and appears in every sim.log, but the verdict does not check for it. A build that
elaborated a different configuration, or a TB top without the banner, would still PASS. -
Require the `GEN_CONFIG_BANNER build_config=<C.BUILD_CONFIG>` line in sim.log for PASS and copy
the banner block into result.yaml (the banner is the S1/S6 proof of the elaborated configuration
per run, not per build).

### P-10 (low) [S5 "No hardcoded paths"; S4 documented limitation]
dv/auto_dv/flow/gen_flow_const.py:39-51 - the out root is taken from an environment variable or
from dv/auto_dv/work/runtime/gen_site.yaml, an uncommitted working file; a fresh clone without
either falls back to work/runtime/out, which LSF hosts cannot see (the flow only warns,
gen_regress.py:190-192). The design is sound for this site (the user path cannot be committed)
and gen_runtime_api.md Section 0 documents it. - Turn the warning into a refusal for non-local
regressions (`path_is_shared` false -> die), and add the pointer contents to every manifest
(`out_root`, its filesystem type) so a reader of the committed evidence knows the root in use.

### P-11 (info) [S1, S6 one seed] Conformant
gen_run.py:42, :62, :83, :154-155 - one integer goes to `+ntb_random_seed` and to `RANDOM_SEED`;
it is written to run.log before the simulation starts (verified: `GEN_RUN_SEED test=gen_smoke
seed=330815564 ntb_random_seed=330815564 RANDOM_SEED=330815564` at 05:32:44Z), echoed by
run_cmd.sh into lsf.out at job start, and present in the `Command:` head of sim.log. Seeds are
bounded to [1, 2^31-1] (gen_flow_const.py:84-85) and derived deterministically from a recorded
base seed (gen_flow_util.py:156-165; `scope.base_seed` in the manifest). The SV side's own
time-0 seed print (TB_CONTRACT Section 1) is the TB's duty and does not exist yet.

### P-12 (info) [S5 single source of truth, no hardcoded tool paths] Conformant
All tool invocations resolve through PATH after `source ci/env.sh` (gen_flow_util.py:119-130,
`require_env`); the LSF job sources a staged copy of ci/env.sh whose sha256 is recorded in the
build manifest and equals the current ci/env.sh (bf1452b462e62f24); `IBEX_ENV_TOOLCHECK=off` is a
documented switch of ci/env.sh:85-88. Plusarg names, markers, LSF defaults, schema keys and
purposes live in gen_flow_const.py only; `--check` against gen_tb_pkg.sv passes. Hierarchy
references (`+tree`, `fsdbDumpSVA`) are rendered from the one build entry. Configuration comes
from `util/ibex_config.py opentitan vcs_opts` at build time (gen_build.py:28-33).

### P-13 (info) [S2 collected mechanisms] Scanner coverage, verified against the RTL macro path
gen_flow_const.py:189-200 - UVM_FATAL/UVM_ERROR summary counts and message lines, `Fatal:` and
`$fatal`, `GEN_*_FAIL`, `Error-[...]`/`Error:`, cocotb CRITICAL and summary, `Offending` (VCS SVA
failure) are all scanned; prim_assert.sv:27-30 routes RTL assertion failures to uvm_report_error
under +define+UVM, so they are caught by the UVM_ERROR rules. Expected-fail handling (XFAIL,
unexpected PASS -> FAIL) matches S4 "write the test to the intended behaviour, mark it as a
known expected-fail". Subject to P-01 and P-02.

### P-14 (info) [S6 evidence over prose] Evidence excerpt audit against the on-disk out-tree
Verified: regress_t010_smoke/manifest.yaml (status done, 1 planned / 1 pass, lsf_cost jobs 1
cpu_s 1.3 slot_s 14.6 pend_s 1.4, lsf_jobs_left [], git 0b9c93c, base_seed 1); run
gen_smoke_330815564 PASS, cm_name test_gen_smoke_330815564, LSF job 10930323 on soc-c-11, lsf.out
job report "CPU time : 1.32 sec", "Run time : 18 sec", "Successfully completed"; sim.log
Command line with `-cm line+cond+tgl+assert+fsm+branch -cm_dir .../build.vdb -cm_name
test_gen_smoke_330815564`, GEN_CONFIG_BANNER build_config=opentitan, GEN_SMOKE_PASS, `$finish`;
cm_hier.cfg `+tree gen_smoke_tb_top.u_dut`; dashboard.txt Total Coverage Summary exactly as
quoted (37.82 / 55.09 2397/4351 / 37.41 3579/9566 / 7.40 1994/26958 / 6.98 6/86 / 41.03 992/2418
/ 79.01 143/181, Number of tests: 1); hierarchy.txt u_dut row (38.04 ... 80.34 143/178);
modinfo.txt: five "FSM Coverage for Module" sections (compressed_decoder, controller, LSU,
multdiv_fast, icache; the LSU section carries two FSMs, consistent with "six state machines");
module gen_dut_top TOGGLE 312/2420 only; build_manifest.yaml (95 sources, tools, 0 errors, SIOB
32, LCA 1, cov_scope); runtime-001 report "Number of tests: 2" with both cm_names; runtime-002
refused with the quoted reason; runtime-003 repro with coverage null; t010_smoke_cov/constfile.txt
lists `instance gen_smoke_tb_top.u_dut.u_ibex_core, expression cheriot_enable_i[0], declaration
rtl/ibex_core.sv:67, value 0 always, location dv/auto_dv/tb/gen_dut_top.sv:274, input
CheriotEnable` (480 occurrences of "cheriot"); `gen_cov_report.py unreachable` on cov2 reproduces
5 line rows, 54 condition vectors, 22 toggle rows, 132 marks for ibex_cheriot_ex. Not verified
by me: the "673 constant entries / 441 mention cheriot" counts (the file is YAML, entries span
lines; the flow should count entries by parsing it). Gaps the excerpt states honestly: cocotb
not exercised; coverage numbers are smoke-only. Gaps it does not state: no red run (P-01), no
--waves run (P-03), no --fcov-check run (no manifest exists yet), no -elfile merge.

### P-15 (info) [S4 "Don't hide failures"] Conformant
gen_regress.py:280-281 exits non-zero on any FAIL/TIMEOUT/NOT_RUN; builds that fail mark their
runs NOT_RUN with the reason; gen_serve_requests.py writes refusals with the reason into the
manifest (runtime-002 verified); a repro silently drops coverage but records the note in the
scope (gen_serve_requests.py:122-123) and the API document says so. `limited_design` from the
URG merge log is recorded (the "Limited design loaded" lesson, evidence Section 3).

### P-16 (info) [S5 "Concise code comments", "Self-sufficient docs"] Conformant
Module docstrings and comments state intent and cite SIM_RECIPE sections; the one history note
("Lesson recorded in the flow ... Limited design") lives in the evidence file, where it belongs.
gen_dashboard.md is ASCII-checked at write time (gen_dashboard.py:206-207).

## Summary
The flow conforms to Sections 1, 3 and 5 and to the seed, constants-home and purpose-gating
rules of the team prompt (P-11, P-12, P-15, P-16), and the evidence excerpt is true to the
on-disk artefacts (P-14). REQUEST-CHANGES stands on the four medium items: prove the verdict's
red paths on real failing runs (P-01); close the marker/exit-code vacuity (P-02); fix and
evidence the --waves path (P-03); settle the coverage scope in one place (P-04, DV Lead ruling).
The low items (strict exclusion loading, wiring the constants check, fcov-null accounting, the
compiler-version field, banner check per run, out-root refusal) can ride in the same follow-up.
