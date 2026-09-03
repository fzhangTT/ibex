# Cross-model review - committed diff edacfb10..eccc461c

**Reviewer:** claude CLI 2.1.259 (Claude Code); run-reported model: claude-fable-5-1; effort: high; fresh session a1fc58ce-b01a-43be-bff7-e19e3112ea86 (fallback reviewer per owner ruling A-001)
**Codex unavailable because:** ERROR: You hit your spend cap set by the owner of your workspace. Ask an owner to increase your spend cap to continue.
**Date:** 2026-09-03
**Target:** committed diff edacfb10..eccc461c (echo at raw line 1)

---

TARGET: edacfb1010d3cc93ec4e1b270a2ff578bf977a4d..eccc461ce6eab46e509257b9928b0bbe58fcc5be

Reviewer: Claude (model ID claude-fable-5-1, Claude Code CLI), fresh session, read-only, fallback reviewer per the recorded ruling A-001. Scope: five commits d0a8a1c, d31f08c, d449af7, 4bd806a, eccc461 (38 files, +1812/-107, all under `dv/auto_dv/**`, all new files `gen_`-prefixed; no `rtl/`, `ci/` or `docs/` file touched). Verified against the committed tree at eccc461, the out-trees under `dv/auto_dv/work/tb-infra/` and `/proj_soc/user_dev/fzhang/ibex_dv_out`, LSF history (`bhist`), the RTL, and by running the committed `gen_verdict.py --self-test` from a `git archive` of eccc461 in a private temp directory. Host clock is EDT; times below converted where the evidence uses UTC.

## Scope note on the owner's focus list

Three named items are not in this range and were not reviewed:
- The `gen_cross_review.sh` hardening (target-echo tolerance 46c4af7, private-copy execution 522a836) is descendant of eccc461. No file under `dv/auto_dv/tools/` changes in the range, so the protocol check (exact TARGET echo still required and recorded) must be done against a later range.
- Intervention-log entries in range are LOG-008a, LOG-005a and F-001 only. LOG-005, LOG-006, LOG-007, LOG-008 are already in edacfb1; LOG-009 is after eccc461.
- No Critic verdict file (`gen_critic_*`) is added or changed in the range. The Critic rulings the new probe register encodes live in a gitignored work file (finding 3).

## What was verified

**T-038 follow-up (d0a8a1c) matches its stated fixes.**
- `decide()` self-tests: five file-based cases plus the missing-sim.log timeout case added (`gen_verdict.py:200-223`). Run from the eccc461 archive: 11 cases ok, `SELF-TEST: PASS`, rc 0.
- Retained DBG_UCLI_DEP artifact: `<out root>/t038_evidence_ucli/` exists (02:26 local = 06:26 UTC as stated), `compile.log` carries `Error-[DBG_UCLI_DEP]`, `build_manifest.yaml` has `vcs_rc: 0`, `error_classes`, `status: failed`.
- Mirror venv lock hash: `requirements_hash()` over `ci/requirements.lock`, `ci/requirements-cocotb.txt`, `ci/setup-venv.sh`; `status()` reports `stale_venv` when the clone's hash differs from the one the venv was built from; `--check` returns 1 for any state other than `fresh` (`gen_mirror.py:227`).
- Unmeasured cov-dir refusal: `gen_run.py:183-197` computes `measured` first, defaults an unmeasured run to `<outdir>/cov_unmeasured/<build>.vdb` seeded by `copytree` (same layout and seeding as `gen_regress.py:77-79`), and dies when the target equals `build_vdb`. Manifest keys `outdir`/`build`/`build_vdb` exist (`gen_build.py:240-248`).
- Recomputed mirror hash: `check_mirror_for_run` now requires manifest == build record == live `tree_hash(root)`.
- `render_fields` docstring now matches the body (only a known-name leftover raises; `gen_flow_util.py:190-194`).
- Doc sentences: `gen_runtime_api.md:40` (`--no-diag-noconst`), `:48` (`-ucli` run-time only) and the `gen_run.py:59` die text are fixed. One of the four listed sentences is not (finding 4).

**Review artifact (d31f08c)** has the identity header (CLI version, model ID, effort, session, codex-unavailable reason), an explicit target range, and a machine-readable verdict. LOG-008a's provenance correction agrees with that review's finding at `gen_intervention_log.md:289`.

**LOG-005a facts hold on disk.** `out_t029/smoke/` holds `sim/`, `red1/`, `red2/`, `green2/` with `sim.log` mtimes 01:55:04.615, 01:55:05.963, 01:55:07.253, 01:55:08.847 local; md5 and `Command:` lines differ between `sim/sim.log` and `green2/sim.log`. The earlier review artifact (`...881a771a-3c623e54.md:33`) did state "there is no `green2/` directory" and did cite `out_t029/red1/`, so the amendment's account is accurate. No fenced content.

**T-036 evidence (d449af7) is artifact-backed.** `out_t036/smoke/runs_summary.txt` matches the committed block character for character; the four `sim.log` mtimes are 02:22:19.4 / 24.4 / 33.3 / 38.0 local; each green log has exactly one `GEN_SMOKE_PASS` and a `CPU Time` line; the compile CPU-time line matches. `gen_smoke_run.sh` reproduces the T-005 flag set exactly. `gen_smoke_tb_top.sv` defines both plusargs and both `$fatal` tokens the driver checks. Stim sidecars: `s7` seed_used 7, `debug_rom_bytes` 1748, `s8` seed_used 8, `memory_map` as quoted; `gen_run/seed.yaml` is `gen_rand_smoke_0: '7'`, which the new regex in `generate()` matches (riscv-dv writes it with `yaml.dump`, `run.py:347`). `check_link_constants` derives the DM budget 0x800 from the wrapper parameters and `check_debug_rom_budget` measures the PT_LOAD at DmHaltAddr (ELF `.debug_rom` is 0x6d4, within budget). T-027's `bhist -l 10930445` quote reproduces verbatim.

**F-001** names no test identifier and quotes no report content. The only fenced-adjacent string is the sibling workspace path, which is the location the honor rule asks to record; it discloses nothing beyond a directory name FENCE.md's own `dv/**` glob already names. See finding 1 for a citation problem.

## Findings

[minor][dv/auto_dv/docs/gen_intervention_log.md:333] F-001 says the mitigation is "already in the flow" and cites `gen_fcov.run_checker` setting `TMPDIR` and `gen_t045_fcov_wiring.md` Section 3, but neither file exists at eccc461 (02:37:23 local); both first land in 24f3dc0 at 02:39:07. The claims are true there (`gen_fcov.py:97-101` sets `TMPDIR` to the run dir; evidence §3 lines 32-38 record the event without content). - A log entry should cite committed state or say the change is pending in the next landing; add a one-line amendment naming 24f3dc0.

[minor][dv/auto_dv/stim/gen_riscv_dv_target/gen_testlist.yaml:27] The comment says a seed-7 ROM "with +gen_debug_section=1 and one sub-program is already 0x726 bytes". The retained T-036 seed-7 run with exactly those two knobs is 0x6d4 (1748) bytes, as `gen_t025_stim_tooling.md` §7 states in the same commit; 0x726 is the T-029 `dbgprog` run, which also carried `+enable_debug_single_step=1 +set_dcsr_ebreak=1`. - Cite the run and its full knob set, or use 0x6d4; the budget conclusion is unchanged.

[minor][dv/auto_dv/docs/gen_probe_register.md:3] The register's statuses are "set to the Critic's binding rulings in `dv/auto_dv/work/critic/gen_critic_tb_arch_components_v1.md`", and all 20 component API docs cite `dv/auto_dv/work/tb-infra/gen_tb_arch_component_sections.md` as their source; `dv/auto_dv/.gitignore:4` ignores `work/`, so the rulings that make P1 accepted, P4 conditional, P6 off cannot be verified from the repository, unlike the T-005/T-010 Critic reports committed under `docs/`. - Commit the Critic report (and the component-sections source if it is the authority) under `dv/auto_dv/docs/` or `dv/auto_dv/reviews/` with an identity header.

[minor][dv/auto_dv/evidence/gen_t010_compile_path.md:235] The "doc sentences" fix is three of four: this row still quotes the verdict reason `"nonzero exit with clean log"`, while `gen_verdict.py:115-117` emits `unexplained exit code <rc> ...`; the previous review's minor 7 listed it. - Update the quoted reason string.

[minor][dv/auto_dv/stim/gen_program.py:53] Magic numbers: the changed `SPIKE_OPTS` line still hand-encodes `--pmpregions=16 --pmpgranularity=4`, which mirror the opentitan config's `PMPNumRegions=16` / `PMPGranularity=0` (authority `util/ibex_config.py`), while the same change correctly derived the `-m` windows from the SV parameters. A config change would silently desynchronise Spike from the DUT. - Derive both from `util/ibex_config.py opentitan` (or `sv_param` on the wrapper) the way `spike_mem_opts` does. Confidence 70.

[info][dv/auto_dv/evidence/gen_t029_smoke_red_runs.md:77] The run_01 and run_04 excerpts are textually identical; run distinctness rests on the timestamp list and `runs_summary.txt` (both verified). LOG-005a's new standing rule asks the excerpt itself to quote identifying lines (command path, VCS stamp, CPU time); the rule postdates this commit. - Add one identifying line per run block on the next touch.

[info][dv/auto_dv/flow/gen_mirror.py:218] `--sync` without `--venv` now carries over `prev.get("venv")` only; a mirror whose manifest has no venv record but whose `.venv` exists reports `venv MISSING` until `--venv` runs. This is the fail-safe direction (a freshly computed hash would mask a stale venv), but the usage text does not say so. - Add "run `--venv` once after a manifest without a venv record" to the usage block.

[info][dv/auto_dv/docs/gen_probe_register.md:72] RTL anchor `rtl/ibex_core.sv:1867` for the dummy-instruction RVFI exclusion resolves to lines 1864 and 1894 today; every other anchor checked (`ibex_cs_registers.sv:1044-1045`, `:408-412`, `ibex_controller.sv:498`, `:725`, `:436-438`, `:1085-1095`) resolves. - Correct the one line number.

[info][dv/auto_dv/reviews/2026-09-03-claude-diff-8c22fe5e-edacfb10.md:1] The owner's focus items that are outside this range (tooling hardening 46c4af7/522a836, LOG-006..LOG-009, Critic verdict files) still need a post-execution review targeted at the range that contains them. - Re-run the cross-review with a range ending at or after 522a836.

## Rubric results

- ai-slop-comments: `{"status": "PASS"}`. Added comments state intent (`gen_run.py:188-189`, `gen_mirror.py:37`, `gen_program.py:49-56`, `gen_smoke_run.sh:2-9`); the "(T-027 review)" tags are anchors, not history narration.
- rtl-purity: `{"status": "PASS"}` (no `rtl/` files in the diff).
- magic-numbers: `{"status": "FAIL", "summary": "changed SPIKE_OPTS line re-types PMP config values", "comments": [{"file": "dv/auto_dv/stim/gen_program.py", "line": 53, "quote": "\"--pmpregions=16\", \"--pmpgranularity=4\"", "comment": "PMPNumRegions/PMPGranularity duplicated outside ibex_configs.yaml; derive like spike_mem_opts", "confidence": 70}]}`.
- forces-and-hier-access: `{"status": "PASS"}`. No SV or cocotb deposits; the shell driver passes plusargs only.
- assertion-integrity: `{"status": "PASS"}`. Nothing disabled or weakened: `check_link_constants` gains a DM LENGTH check, `check_debug_rom_budget` and the seed cross-check are new fail paths, `gen_run.py` adds a refusal, `check_mirror_for_run` adds a third hash equality, `gen_verdict.py` adds six self-test cases. The dropped `venv_info` fallback is not a check.

Summary: the T-038 follow-up code does what its commit message says and its new self-tests pass; the retained DBG_UCLI_DEP artifact, the T-036 smoke sequence, the seed-bound stim runs and the T-027 LSF record all exist on disk and match the committed text; LOG-005a and LOG-008a state verified facts with paths; F-001 contains no fenced content. Open: F-001 cites two files that did not exist at its commit, one wrong ROM-size figure in a committed comment, Critic rulings for the probe register held only in a gitignored work file, one stale reason string, and re-typed PMP values in `SPIKE_OPTS`. The tooling-hardening and later log entries the owner named are outside this range and remain unreviewed. No blocker.

Final verdict: APPROVE-WITH-CHANGES
