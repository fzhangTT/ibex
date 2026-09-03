# Critic: DV-principles conformance check of the T-005 code (v1)

- Artifacts under review (committed, commit 44d94110413da4440504bb765d26825db8742e1e; no drift to
  HEAD 0b9c93c: `git diff --quiet 44d9411 HEAD -- <files>` returns 0):
  dv/auto_dv/tb/gen_dut_top.sv (sha256 first 16: 6ecf5197ed7af1cb), dv/auto_dv/tb/gen_smoke_tb_top.sv
  (5801b668174042a1), dv/auto_dv/tb/gen_tb_pkg.sv (aff6466533490706), dv/auto_dv/tb/gen_smoke_tb.f,
  dv/auto_dv/tb/gen_filelist.py, dv/auto_dv/tb/gen_rtl.f, dv/auto_dv/docs/gen_component_api_dut_top.md
  (2c5b2575222b75ec), dv/auto_dv/evidence/gen_t005_compile_log_excerpt.md (76e1259156ad2251)
- Standard: docs/dv/dv_principles.md (re-read in full for this check), applied per the
  dv-principles-check skill: conformance only, section citations, not a general code review.
  Cross-model post-execution review of the same diff: dv/auto_dv/reviews/2026-09-03-claude-diff-
  8e4a7c50-44d94110.md (APPROVE, two low findings, both still present at HEAD and cited below).
- Date (UTC): 2026-09-03 05:42
- Reviewer role: critic (Claude Fable 5.1). Verified on this host: the on-disk compile.log and
  sim.log under dv/auto_dv/work/tb-infra/out_t005/, `gen_filelist.py --check` (OK, 94 entries),
  the RTL lines the excerpt cites. Build configuration: opentitan. No fence event.

CRITIC VERDICT: REQUEST-CHANGES

Severity counts: high 0, medium 2, low 5, info 5. The two medium findings are the missing
red-run evidence for the smoke's two new checks (Section 6 trust triad rule 1) and the vacuous
pass of the smoke when RVFI is not defined (Section 4). Neither touches the DUT boundary or the
compile evidence; both are small follow-ups for tb-infra (or Runtime in T-010).

## Findings (format: [section bullet] file:line - what violates it - the conforming alternative)

### P-01 (medium) [S6 trust triad rule 1 TDD; S2 "Fail through a mechanism the flow actually collects ... prove it once (see S6)"]
dv/auto_dv/tb/gen_smoke_tb_top.sv:371 (`$fatal ... no RVFI retirement observed`) and :373
(`$fatal ... alert cycles observed`) - two new checks whose failure path has never been shown to
fire: dv/auto_dv/evidence/gen_t005_compile_log_excerpt.md records only the green run (Section 3,
GEN_SMOKE_PASS). "A check never exercised to fail is not trusted" (S6 self-proving checks);
docs/dv/TB_CONTRACT.md Section 3 asks for one forced red run per failure path. - Record one red
run per check in the evidence file: retirement check with a run that cannot retire (for example
`+gen_smoke_cycles=1`, or fetch_enable_i Off, showing the GEN_SMOKE_FAIL line and the nonzero
collected failure), alert check with a corrupted `nop_word` codeword (a one-bit TB-side flip of
the SECDED word raises alert_major_bus_o). State whether the smoke stays in a regression tier;
if it does, S6 rules 2 (named mutation + ablation) and 3 (fcov expectation) apply to it as well.

### P-02 (medium) [S4 "Don't hide failures" (never fake-pass or silently down-scope); TB_CONTRACT.md Section 6 vacuous-pass guard]
dv/auto_dv/tb/gen_smoke_tb_top.sv:355-357 and :370-372 - the retirement counter and its check
exist only under `ifdef RVFI`; a build without `+define+RVFI` prints GEN_SMOKE_PASS after
checking nothing but the alert count, under the same test name. The banner line `RVFI=0` would
be the only trace. - Make the dependence loud: `ifndef RVFI` -> `$fatal(1, "gen_smoke_tb_top
requires +define+RVFI")` at time 0 (or a compile-time `$error` in a generate scope), so the smoke
cannot pass vacuously.

### P-03 (low) [S2 fail through a collected mechanism; S5 self-sufficient docs; docs/dv/SIM_RECIPE.md Section 5 pass/fail contract]
dv/auto_dv/tb/gen_smoke_tb_top.sv:363-374 and dv/auto_dv/docs/gen_component_api_dut_top.md:130-133
("The wrapper has no checker and no runtime knob") - the smoke's pass/fail contract (tokens
GEN_SMOKE_PASS / GEN_SMOKE_FAIL, two `$fatal` sites, knob `+gen_smoke_cycles`) is documented
nowhere a log scanner can bind to; the driver script reports only the process exit, which
SIM_RECIPE Section 5 says is not the pass/fail signal. - Add a short "smoke contract" section
(tokens, knob, what fails it) to the API document or a smoke API note, and have the Runtime
Manager's scanner key on the tokens in T-010.

### P-04 (low) [S1 "the TB prints a config banner at time 0 so every log proves which configuration actually elaborated"; S6 banner as evidence]
dv/auto_dv/tb/gen_dut_top.sv:426-461 - the banner omits RndCnstLfsrSeed / RndCnstLfsrPerm
(declared :59-60 and forwarded :258-259; they select the dummy-instruction LFSR sequence, so they
matter for reproduction) and the three PMP reset parameters PMPRstCfg / PMPRstAddr / PMPRstMsecCfg
(rtl/ibex_core.sv:22-24), which the wrapper does not declare, so ibex_core's ibex_pkg defaults
apply without appearing in any log. - Print the seed and permutation (or a hash of them) and one
line naming the PMP reset parameters as "ibex_pkg default", or declare and forward them.

### P-05 (low) [S5 "Single source of truth"; S1 "Future-proof every count"]
dv/auto_dv/tb/gen_tb_pkg.sv:16 (`GEN_BOOT_FETCH_OFFSET = 8'h80`), :20-21 (`GEN_DATA_W = 32`,
`GEN_INTG_W = 7`) - re-typed RTL literals (rtl/ibex_if_stage.sv:243; MemDataWidth = 32 + 7 in
gen_dut_top.sv:71) with no consumer in the commit; cross-model review finding 2, still present.
- Drop them until a consumer exists; when one does, size against the wrapper's MemDataWidth
(pass it down or expose it through the package) rather than GEN_DATA_W + GEN_INTG_W.

### P-06 (low) [S5 "Self-sufficient docs and code" (expand a tag/ID on first use or link the defining doc)]
dv/auto_dv/tb/gen_dut_top.sv:5-14 - the header cites "Owner question Q-A", "Q-B", "Q-C", "Q-1"
with no defining document; the intervention log filed these as Q-002 (revised, absorbing
Q-A/Q-B/Q-C) and LOG-004 (Q-1), so the tags in the code no longer resolve. - Cite
dv/auto_dv/docs/gen_intervention_log.md Q-002 and LOG-004 (or gen_param_resolution.md section 4)
on first use.

### P-07 (low) [S4 "Evidence over inference"; S5 self-sufficient docs]
dv/auto_dv/docs/gen_component_api_dut_top.md:61-62 ("fatals at elaboration") and :86
("elaboration-time `$fatal`") versus dv/auto_dv/tb/gen_dut_top.sv:464-468, an `initial` block
that fires at simulation time 0 after ibex_register_file_ff has elaborated; cross-model review
finding 1, still present. - Put the guard in a generate scope (module-level `if (RegFile !=
RegFileFF) $fatal(...)` is an elaboration system task) or reword both sentences to "time-0".

### P-08 (info) [S1, S6] Evidence excerpt audit against the on-disk logs: the excerpt proves what the API document claims for compile, elaboration, banner and run
- Compile command: the excerpt's command equals dv/auto_dv/work/tb-infra/out_t005/compile.log:1-10
  and the config options equal `util/ibex_config.py opentitan vcs_opts` (config_opts.txt).
- Banner: excerpt lines 98-108 equal sim.log lines 5-15 verbatim. The values are the ELABORATED
  parameters (enum `.name()` and parameter values from gen_dut_top.sv:430-450), not the plusarg,
  and every value matches ibex_configs.yaml opentitan and gen_param_resolution.md (BaseIsa
  RV32IorCHERIoT, RV32MSingleCycle, RV32BOTEarlGrey, RV32ZcaZcbZcmp, RegFileFF, PMPNumRegions 16,
  MHPMCounterNum 10, MemDataWidth 39, TagSizeECC 28, LineSizeECC 78, RegFileCapEccWidth 35,
  RegFileECC 0, ResetAll 1, cheriot_enable Off, RVFI 1, GEN_DUT_SPLIT_INTG 0). The banner is the
  configuration that elaborated.
- Warnings: 32 `Warning-[SIOB]`, all with `rtl/ibex_core.sv` on the following line (count
  verified 32 of 32); the cited structure holds (rtl/ibex_core.sv:2142-2150 is the `else` arm of
  `if (i == 0)` indexing `[i-1]`, reported for the i == 0 iteration). 1 `LCA_FEATURES_ENABLED`.
  Zero errors. `$finish` at gen_smoke_tb_top.sv:375 as stated.
- Gaps the excerpt does not close: the failure path (P-01) and the RVFI-off vacuity (P-02).
- Working-file dependence: the driver script and out-tree are uncommitted (stated in the
  excerpt); the evidence therefore rests on the excerpt plus this check, which is acceptable
  for bring-up evidence and consistent with S6 "committed evidence".

### P-09 (info) [S3 "No-modify reuse of shared/vendored infra"]
dv/auto_dv/tb/gen_filelist.py:81-86 substitutes the two prim_xilinx paths with prim_generic files
of the same module name and appends rtl/ibex_register_file_ff.sv: a filelist selection, not an
edit of vendored code; the header of gen_rtl.f records both substitutions. `--check` re-run at
HEAD: OK (94 entries). Conformant.

### P-10 (info) [S1 "Realistic drive at the DUT boundary"; S5 no hierarchical drive]
gen_smoke_tb_top.sv drives only wrapper ports (legal idle levels, same-cycle grant, rvalid one
cycle after grant, SECDED-encoded NOP words through the vendored encoder, synchronous 1-cycle
cache RAM arrays, ic_scr_key_valid_i = 1); no force, no hierarchical access, no logic inside the
DUT hierarchy (gen_dut_top is wiring, a banner and a guard). Conformant for bring-up equipment;
it is not a test and claims no coverage.

### P-11 (info) [S5 "Toggleable debug"/plusargs declared once; S5 single source of truth]
gen_tb_pkg.sv:7-8 declare the two plusarg names once; both call sites (gen_dut_top.sv:428,
gen_smoke_tb_top.sv:363) build the query string from the constant. GEN_RV32_NOP (:24) is
composed from ibex_pkg::OPCODE_OP_IMM; cache geometry (:27-29) is imported from ibex_pkg. The
banner and the two GEN_SMOKE result lines are unconditional by design (S1 requires the banner;
the result lines are the pass/fail record, not debug). Conformant.

### P-12 (info) [S1 "Future-proof every count"]
gen_dut_top.sv:183-184 and gen_smoke_tb_top.sv:134-135 declare `rvfi_ext_mhpmcounters [10]` with a
literal 10: this mirrors the RTL port declaration (rtl/ibex_core.sv:174-175 hard-codes 10
independently of MHPMCounterNum), so it is a port mirror, not a re-typed count. Acceptable; if
the RTL ever parameterises the array the wrapper must follow.

## Summary
The wrapper, package, filelist derivation and evidence excerpt conform to Sections 1, 3 and 5
with the low-severity hygiene items above (P-04..P-07). The excerpt proves the compile, the
elaborated configuration (banner equals the opentitan config) and the green run against the
on-disk logs (P-08). The two medium findings concern the smoke's checks: their failure path has
not been shown to fire (P-01) and the retirement check disappears silently without RVFI (P-02).
REQUEST-CHANGES stands until P-01 and P-02 are addressed (a red-run evidence addendum and a
vacuous-pass guard); the low items may ride along in the same follow-up commit.
