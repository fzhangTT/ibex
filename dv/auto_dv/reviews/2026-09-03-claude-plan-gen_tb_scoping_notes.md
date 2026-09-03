# Cross-model review - plan/spec file(s): dv/auto_dv/work/tb-infra/gen_tb_scoping_notes.md dv/auto_dv/work/rtl-arch/gen_param_resolution.md

**Reviewer:** claude CLI 2.1.259 (Claude Code); run-reported model: claude-fable-5-1; effort: high; fresh session 8f8917fc-1a6d-4bb0-9444-7edc67204eca (fallback reviewer per owner ruling A-001)
**Codex unavailable because:** ERROR: You hit your spend cap set by the owner of your workspace. Ask an owner to increase your spend cap to continue.
**Date:** 2026-09-03
**Target:** plan/spec file(s): dv/auto_dv/work/tb-infra/gen_tb_scoping_notes.md dv/auto_dv/work/rtl-arch/gen_param_resolution.md

---

TARGET: dv/auto_dv/work/tb-infra/gen_tb_scoping_notes.md@312418d1
TARGET: dv/auto_dv/work/rtl-arch/gen_param_resolution.md@72b977d5

## Reviewer identity

- Reviewer: Claude Fable 5.1 (`claude-fable-5-1`), fresh session, independent of the authoring session. Codex fallback per intervention log A-001.
- Review target: the two untracked documents above, identified by SHA-256 prefix (both live under the gitignored `dv/auto_dv/work/`; the hashes were recomputed on disk and match). RTL and build files at HEAD `38a0c2d` (RTL unchanged since export `1908ddd`).
- Scope: pre-execution review for T-005. Gating sections: scoping notes a and h, and the whole of `gen_param_resolution.md`. Sections b and c commented on, not gated.

## What I verified against the repository

I re-ran the configuration script and the fusesoc setup, and read every cited RTL line for Sections a and h and for the parameter table.

- **Config output.** `util/ibex_config.py opentitan vcs_opts` output matches both documents verbatim. The five enum fields become `+define+`, the fourteen integer or bit fields become `-pvalue+`. The script code at `util/ibex_config.py:262-264` confirms the mechanics, and `doc/02_user/integration.rst:264-269` confirms the VCS enum-override limitation.
- **No RTL consumer of the enum macros.** A grep for the backticked names across `rtl/`, `vendor/lowrisc_ip`, and `examples/` finds only `examples/simple_system/rtl/ibex_simple_system.sv:59-62`. Both documents are correct that the wrapper must consume them.
- **Parameter table (`gen_param_resolution.md` Section 2).** Every value and derivation checked against `rtl/ibex_core.sv:17-59`, `rtl/ibex_top.sv:212-227` and `369-410`, `rtl/ibex_pkg.sv` (enum values, IC constants, LFSR defaults, MuBi constants), `rtl/ibex_cheriot_pkg.sv:28`, and `prim_secded_pkg.sv:275`. All correct, including: `RegFileECC=0`, `RegFileDataWidth=32`, `RegFileCapEccWidth=REGCAP_W` passed at `ibex_top.sv:400`, the lockstep-only use of the widened widths at `ibex_top.sv:1145-1148`, `ShadowCSR=0` at `ibex_core.sv:197`, `IC_TAG_SIZE=22`, `TagSizeECC=28`, `LineSizeECC=78`, `MemDataWidth=39`, and the reversed part-select hazard at `ibex_core.sv:1264/1271` if `RegFileECC=1` without widening.
- **Wrapper wiring and port list (scoping notes a.1, a.2).** Core-to-RF wiring matches `ibex_top.sv:437-448` and `534-559`. The port list is the complete `ibex_core` port set minus RF ports. `test_en_i` is provably unused in the FF register file (`assign unused_test_en` in both branches). `data_tag_o` is forced 0 and `data_tag_i` unused in `ibex_top`'s non-CHERIoT branch. `gen_regfile_ecc` at 1214, `rf_ecc_err_comb=0` at 1318, alert equations at 1337-1353, and the `cheriot_enable_mubi_err` generate block all check out. First fetch address `{boot_addr_i[31:8], 8'h80}` confirmed at `ibex_if_stage.sv:243`.
- **RVFI (a.4).** Port list matches `ibex_core.sv:136-181`. Spot-checked semantics all hold: `RVFI_STAGES` (1660), stage-1 valid from `rvfi_wb_done` (1871, 1894), dummy-instruction exclusion (1867, 1908), `rvfi_halt` constant 0 (2117), `rvfi_intr` latch condition (2395-2406).
- **Build constraints (h, and `gen_param_resolution.md` Section 3 items 6 and 7).** Confirmed: `dv_fcov_macros.svh` is included by seven RTL files; `DV_FCOV_SIGNAL` behaviour and `DV_FCOV_DISABLE` guard; `INC_ASSERT` defined by `prim_assert.sv:108/111`; `RVFI` set only by the `.core` lint and format targets (185, 200); `rtl/ibex_core.f` is stale (missing pmp, csr, wb_stage, dummy_instr, icache, branch_predict, cheriot_ex, cheriot_pkg and all prims); `prim_lfsr.sv:461` references `prim_cipher_pkg`; `prim_buf` exists only under `prim_generic` and `prim_xilinx`. Host claims confirmed: cocotb 1.9.2, fusesoc 2.4.3, Python 3.12.10, GCC 10.2.0 toolchain, dtc 1.7.2, VCS X-2025.06-SP2, no Spike on PATH, and `vcs -ID` without `-full64` fails with "Cannot find VCS compiler".
- **fusesoc.** I ran the exact command from Section h for `lowrisc:ibex:ibex_core`. It emits a `.scr` with work-root-relative paths and both `+incdir+` entries as described. It does pick `prim_xilinx` for two files. See finding 4 for the precision issue.

## Findings

Ordered by severity. None blocks T-005; two should be resolved before SV is written.

[medium][dv/auto_dv/work/tb-infra/gen_tb_scoping_notes.md:88-96] Q-1 proposes split `*_intg` ports as the executing default, but the owner ruling in `DV_prompt.txt` Section 2 says the wrapper "exposes the core's remaining ports", and Section 10 requires an owner answer before any boundary-changing decision. The document itself flags the question but then picks the non-literal reading as the default. - Recommendation: T-005 exposes `instr_rdata_i`, `data_rdata_i`, `data_wdata_o` exactly as `ibex_core` declares them (`MemDataWidth`-wide, integrity in bits [38:32] per `ibex_top.sv:355-366`). Do the split in the TB bus interface or agent, which is TB equipment. Switch the wrapper only if the owner answers Q-1 with "split". This keeps the wrapper literal to the ruling and removes the dependency on a pending owner answer.

[low][dv/auto_dv/work/tb-infra/gen_tb_scoping_notes.md:58-59] and [dv/auto_dv/work/rtl-arch/gen_param_resolution.md:114-115] The two documents disagree on `test_en_i`: scoping notes expose it as a wrapper input (Q-3), the parameter resolution says tie it to 0 inside the wrapper. The signal is dead in `ibex_register_file_ff` (verified: `assign unused_test_en = test_en_i` in both generate branches). - Recommendation: tie low inside `gen_dut_top`. An exposed dead input adds a DUT boundary port with no observable effect and invites a needless owner question. Reconcile both documents to one answer before T-005.

[low][dv/auto_dv/work/tb-infra/gen_tb_scoping_notes.md:142-144] The derived widths are written as unconditional constants (`BusSizeECC = 39`, `TagSizeECC = 28`), while `ibex_top.sv:221-225` conditions them on `ICacheECC`. Since `gen_dut_top` receives `ICacheECC` through `-pvalue+`, an unconditional derivation would silently mis-size the RAM ports if the parameter were ever overridden. The same paragraph cites `ibex_top.sv:44` for `ICacheTweakInfection`; the line is 45. - Recommendation: derive with the same `ICacheECC ? ... : ...` expressions as `ibex_top` (the parameter-resolution document already says this correctly in Section 3 item 3) and fix the cite.

[low][dv/auto_dv/work/tb-infra/gen_tb_scoping_notes.md:709-714] The fusesoc caveat overstates the substitution set for the `ibex_core` core. The emitted `.scr` for `lowrisc:ibex:ibex_core` picks `prim_xilinx` only for `prim_clock_gating.sv` and `prim_flop.sv`; `prim_ram_1p` and `prim_xilinx_pkg` appear only when generating for `ibex_top`. `prim_buf` already resolves to `prim_generic`. Neither xilinx module is instantiated by the DUT (`prim_clock_gating` is a `.core` dependency only, and `prim_flop` is instantiated in `ibex_top`, not below `ibex_core`). - Recommendation: scope the caveat to the two files and note the substitution is harmless either way. The checked-in filelist should still prefer `prim_generic` for consistency.

[low][dv/auto_dv/work/tb-infra/gen_tb_scoping_notes.md:90-91] The cite for the `data_wdata_o` split is `ibex_top.sv:1349-1352`; those lines are the non-TRVK through-connects. The actual split is `ibex_top.sv:861-869` (`trvk_wdata = data_wdata_core[31:0]` plus a `prim_buf` on the integrity bits). - Recommendation: fix the cite.

[low][dv/auto_dv/work/tb-infra/gen_tb_scoping_notes.md:695-734] Section h does not state whether the T-005 smoke top runs pure SV or already wires cocotb (`SIM_RECIPE.md` Section 4: `+define+COCOTB_SIM +vpi -P <tab> -load ...`). The TASKS.md acceptance criterion is "smoke run finishes". - Recommendation: state in the T-005 plan that the smoke is pure SV with the config banner and a bounded `$finish`, and that cocotb wiring is proven in T-010. This keeps T-005 thin, as risk R-1 asks.

[info][dv/auto_dv/work/rtl-arch/gen_param_resolution.md:82-86] and [dv/auto_dv/work/tb-infra/gen_tb_scoping_notes.md:132-137] Both documents correctly require `gen_tb_top` and `gen_dut_top` to declare `ICacheScramble` so the unchanged config command elaborates without a silent `-pvalue+` miss. VCS will warn about an unused parameter on `gen_dut_top`; that warning is expected and should be listed in the T-005 compile-log excerpt as accepted.

## Non-gating comments on Sections b and c

These are for the TB architecture document review, not this gate.

- **b.3 RAM model.** The claim that `prim_ram_1p` holds `rdata` until the next read is correct for the generic model and matters for the core's stall behaviour. Worth an explicit assertion in the RAM model's API document.
- **c.1 Spike as library.** The recommendation is sound. The C++20 requirement and the `-CFLAGS '--std=c99'` conflict (R-4) are real; a separately built shared object loaded via `-LDFLAGS` is the right shape and should be proven in T-010, not T-005.
- **c.3 legalization list.** Several rows are marked UNVERIFIED and routed to rtl-arch through Q-8. Good. The `mip` read semantics and `mtvec` reset value in particular decide the ISA shim's reset sequence, so T-014 should answer them before the shim is written.
- **b.9 boot stub.** The `+0x80` first-fetch offset is confirmed in RTL. The plan to serve a two-instruction stub and mirror it in Spike is workable, but the same stub must exist in both memories from one source (R-7 already says this).

## Rubric results

The five Zone A rubrics apply to `rtl/**`, `dv/**/*.sv|svh|py`, `ci/**`, and `docs/**` diff lines. The review target is two Markdown documents under `dv/auto_dv/work/`, outside every rubric's filter set, so no rubric has a qualifying line.

- ai-slop-comments: `{"status": "PASS"}`
- rtl-purity: `{"status": "PASS"}`
- magic-numbers: `{"status": "PASS"}`
- forces-and-hier-access: `{"status": "PASS"}`
- assertion-integrity: `{"status": "PASS"}`

One rubric-adjacent observation for the T-005 diff review: the parameter-resolution document (Section 5) and scoping notes (Section f) both commit to importing `ibex_pkg` constants rather than re-typing them, and to a single `gen_tb_pkg` home for plusarg names and the memory map. The post-execution magic-numbers review should hold the wrapper and smoke top to exactly that.

## Verdict rationale

Both documents are accurate against the RTL, the opentitan configuration, and `SIM_RECIPE.md`; every load-bearing value and derivation I checked is correct. The changes requested are: make the wrapper literal to the Section 2 ruling on the integrity ports until the owner rules otherwise, reconcile the two documents on `test_en_i`, keep the width derivations conditional on `ICacheECC`, and fix the three cite and scoping imprecisions. None changes the T-005 design; they remove an avoidable owner dependency and two inconsistencies before SV is written.

Final verdict: APPROVE-WITH-CHANGES
