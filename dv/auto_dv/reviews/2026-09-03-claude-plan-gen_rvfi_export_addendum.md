# Cross-model review - plan/spec file(s): dv/auto_dv/docs/gen_rvfi_export_addendum.md

**Reviewer:** claude CLI 2.1.259 (Claude Code); run-reported model: claude-fable-5-1,claude-haiku-4-5-20251001; requested effort: high (the CLI does not report the effective setting); fresh session 03ed3aed-23fc-47fc-968e-f3dd691156a1; sandbox: bubblewrap, filesystem read-only except this run's own output directory, scratch HOME (no access to the executing model's settings, instructions or memory), private PID namespace; network open for the model API, web tools disallowed by policy (fallback reviewer per owner ruling A-001)
**Codex unavailable because:** ERROR: You hit your spend cap set by the owner of your workspace. Ask an owner to increase your spend cap to continue.
**Date:** 2026-09-03
**Target:** plan/spec file(s): dv/auto_dv/docs/gen_rvfi_export_addendum.md (echo at raw line 3)

---

Checks done. Writing the review now.

TARGET: dv/auto_dv/docs/gen_rvfi_export_addendum.md@f428486b

Note on the target: `f428486b` resolves to neither a commit nor a blob in this clone. The review is of the file at HEAD 4c0ba11 (blob 648d9790), which is the commit the owner named. Verified against gen_rvfi_pkg.sv, gen_env_pkg.sv, gen_bridge_if.sv, gen_rvfi_if.sv, gen_tb_knobs.yaml, gen_knobs_codegen.py, gen_bridge.py, gen_test_template.py, gen_run.py, gen_tb_local.sh, gen_probe_register.md, TB_CONTRACT.md, dv_principles.md §6, DV_prompt.txt Sections 7 and 8, gen_test_writer_plan.md ask 5.

Rubric results (all five): PASS. The diff is a markdown design document; no SV/Python/RTL lines are added, no assertions are touched, no forces, no magic numbers, no rtl/ changes. The header's version narration is document status, not a code comment.

**(1) Scope rules.** Correct. The probe register lists RVFI as `boundary` (gen_probe_register.md:21), the architecture states it (gen_tb_architecture.md:82), and the probe rule lives in DV_prompt Section 7 ("Modelling and checking"), so the addendum's "Section 7" citation is right and the owner's "Section 8" is a misreference (Section 8 is bug injection). A-01 holds: one bridge command, one awaited `cmd_ack` edge, one file read in `fire_check()` before the finish handshake (TB_CONTRACT Section 2 ordering satisfied; GenTest.finish at gen_test_template.py:285-295 runs checks first).

**(2) Flush protocol.** The ack ordering claim is confirmed by code: gen_env_pkg.sv:56-61 calls `cmd_ap.write(item)` (dispatcher, synchronous) before `@(posedge vif.clk)` and the `cmd_ack` toggle. The marker equality (`records == evt_retired_count`) holds because the flush executes from the `@(vif.cmd_valid)` wake after cocotb's deferred write, i.e. after the NBA region in which gen_bridge_if.sv:52 lands the count, while the monitor's `records++` (gen_rvfi_pkg.sv:102) is active-region at the same posedge. The document's justification ("settle in the same time step") is thinner than that and hides a constraint. Two real defects remain (findings 1 and 4).

**(3) File format.** Field list covers everything the owner enumerated. It does not cover "every gen_rvfi_txn field" as §2 and §7(2) claim (finding 3). Column-order stability through the yaml origin is sound in principle, but the codegen schema is closed (`top` key set, gen_knobs_codegen.py:36) and needs extension.

**(4) Failure behaviour.** Open failure is fatal (good). Write failure, UVM fatal, alive `$fatal`, and cocotb timeout are not addressed (findings 4, 5).

**(5) Cost.** Disk size stated; no measured wall-clock cost exists (the commit message says "measured-run cost", the document says no code exists). Retention of up to 200 MB per run in a regression is unaddressed (finding 7).

**(6) Trust triad.** TDD and truncation mutation are there; dropped-record and reordered-record mutations and a program-contradicting red fixture are missing, and the consumer-side enforcement is not pinned to `read()` (finding 2). fcov N/A for a check-tier unit test matches repo precedent (gen_testlist.yaml unit entries carry `fcov_expectation_file: null`, `fcov_manifest_required_tiers: []`).

Findings:

[medium][dv/auto_dv/docs/gen_rvfi_export_addendum.md:51-56] §3 "requires the last line to be a flush or end marker" contradicts the acknowledged one-posedge window: the ack toggles at the posedge after the flush (gen_env_pkg.sv:59-61), and at that same posedge the monitor can `$fwrite` record N+1 (gen_rvfi_pkg.sv:100-113). That line sits in the simulator's buffer and reaches the OS file on any buffer-full flush, so Python can read a complete or partial R line after the marker and fail spuriously, seed-dependent. - Specify `read()` as: locate the last complete flush marker, parse only the prefix before it, ignore trailing bytes, and check the parsed R-line count equals the marker's `records=<n>`; drop the "last line must be a marker" rule (keep it only for the `end` marker in post-run diagnostic reads).

[medium][dv/auto_dv/docs/gen_rvfi_export_addendum.md:87-90] §5.2 has one field mutation and one truncation; it has no dropped-record mutation (the monitor's `records++` runs but one R line is skipped), no reordered-record mutation (two adjacent lines swapped), and no red fixture where the record set contradicts the program. §2:36 leans on "the existing rvfi_order check", but that check is off in isolation runs (`+gen_chk_all=0`, gen_rvfi_pkg.sv:104) and is not the consumer. - State that `read()` itself enforces: R-line count == marker `records`, `order` strictly +1 across R lines, field count per line == header count; add MUT rows for drop, swap and a Zc-program contradiction (e.g. expected count of one opcode or the boot-page first pc), each caught by `read()`/the fixture check with the ablation control, hidden referees inert.

[medium][dv/auto_dv/docs/gen_rvfi_export_addendum.md:24,38,107] §2 and §7(2) claim the R line carries every `gen_rvfi_txn` field. gen_rvfi_pkg.sv:18-19,28 also has `halt`, `ixl`, `ext_ic_scr_key_valid`, none in the field list; `ext_ic_scr_key_valid` is a checker input in the architecture's `scrkey_proto` row (gen_tb_architecture.md:571) and a plausible fire-check fact. Also, `ext_mhpmcounters[10]`/`ext_mhpmcountersh[10]` exist in gen_rvfi_if.sv:20-21 but not in `gen_rvfi_txn`, so the counters knob requires a txn (or vif-direct) change §4 does not list. - Add the three missing fields (or state the omission and drop the "every field" claim) and add the `gen_rvfi_txn` counter extension to the §4 table.

[medium][dv/auto_dv/docs/gen_rvfi_export_addendum.md:44-63] §3 is silent on abnormal ends: `uvm_fatal` (UVM `$finish`es before `final_phase`, so no end marker, no `$fclose`), the alive watchdog `$fatal`, and a Python `with_timeout` on the RVFI_FLUSH ack (gen_bridge.py:31-34 raises). The owner asked for this explicitly. - State: on any abnormal end the file is diagnostic only and is guaranteed complete only through the last `$fflush`; the RVFI_FLUSH timeout fails the test through GenBridge.cmd; optionally `$fflush` on every I line or every N records behind a debug-only knob for triage.

[low][dv/auto_dv/docs/gen_rvfi_export_addendum.md:46-50] "cannot be written" is not covered: `$fwrite` reports nothing; only `$fopen` is checked. - After `$fflush` in `flush()` and before `$fclose`, check `$ferror(fd)` and raise `uvm_error GEN_RVFI_EXPORT` on nonzero; note that the Python completeness check is the second line of defence.

[low][dv/auto_dv/docs/gen_rvfi_export_addendum.md:52-55] The "same instant" argument omits the constraint that makes it true: `flush()` runs from the `@(vif.cmd_valid)` wake (gen_env_pkg.sv:50) after the posedge's NBA region, never from a clocked process. Dispatching RVFI_FLUSH at the ack posedge would break the equality by one. - Record this as an explicit design constraint with the gen_env_pkg.sv citation.

[low][dv/auto_dv/docs/gen_rvfi_export_addendum.md:14,62] §1 says the template passes the knob for every test; §3 says "a long measured test declares the knob per entry". No retention rule for up to 200 MB per run across a regression, and no measured wall-clock delta despite the commit message. - Pick one (template default with a per-entry opt-out, or opt-in), state the flow's retention (e.g. delete on PASS, keep on FAIL), and add the with/without wall-clock measurement on the Zc program to the TDD evidence.

[low][dv/auto_dv/docs/gen_rvfi_export_addendum.md:24,30-33,78] Format and origin details: `image=<path>` breaks whitespace tokenising if a path has spaces; `%h` renders X/Z and the reader's behaviour is unspecified; the yaml keys need the codegen `top` schema (gen_knobs_codegen.py:36) and gen_ut_knobs_codegen.py extended; the API document target "Section 8" is "At build" in gen_component_api_rvfi_monitor.md, while the knob table is Section 3 and the failure path Section 6. - Parse `image=` as rest-of-line or fatal at open on whitespace; state X handling (reader fails loud); list the codegen schema change in §4; point the API update at Sections 3 and 6.

[low][dv/auto_dv/docs/gen_rvfi_export_addendum.md:28,59] `final_phase` is a top-down function phase, so gen_base_test's `finish_ack` toggle (gen_env_pkg.sv:261-264) precedes the monitor's end marker and `$fclose` in the same sweep. Harmless today because nothing yields in between, but undocumented. - Write the end marker and `$fclose` in `extract_phase` (bottom-up, before the UVM report) or state the ordering.

Final verdict: APPROVE-WITH-CHANGES
