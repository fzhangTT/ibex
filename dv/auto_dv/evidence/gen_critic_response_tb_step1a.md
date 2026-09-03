# Response to the step-1a reviews (T-068): constants codegen

Responder: tb-infra (respawned instance), 2026-09-03. Reviews answered: Critic
`dv/auto_dv/docs/gen_critic_tb_step1a_dv_principles_v1.md` (REQUEST-CHANGES) and the cross-model review
`dv/auto_dv/reviews/2026-09-03-claude-diff-dc6de881-2d833d60.md` (APPROVE-WITH-CHANGES). Validating runs are
retained under `dv/auto_dv/evidence/gen_tdd_logs/knobs_codegen/` (manifest `gen_tdd_logs/gen_manifest.md`);
the transcript is `dv/auto_dv/evidence/gen_tdd_knobs_codegen.md` Section 7. Files: `dv/auto_dv/tb/gen_tb_knobs.yaml`,
`gen_knobs_codegen.py`, `unit/gen_ut_knobs_codegen.py`, the four rendered targets, `gen_tb_top.sv` (guard).

Status words: FIXED (change made, validating run named), DISPUTED (reason given), ROUTED (another role's file).

## Critic findings

| Finding | Status | Location / validating run |
|---|---|---|
| P-01 unknown yaml keys accepted; four descs split on commas | FIXED | Every `desc` quoted; `load()` refuses unknown keys in every section (`check_keys`), a non-string desc, `default` with `default_from`, unknown derivations, window values outside the enum set. Unit test: nine refused fixtures through `--src` (`OK loader refuses: unknown plusarg key`, `... unquoted comma in desc`, `... unknown constant key`, `... unknown memory_map key`, `... unknown register key`, `... unknown top-level key`, ...), `knobs_codegen_t068.log`, 674 OK, exit 0. The rendered descriptions are whole again (e.g. `PLUSARG_MEM_IMAGE_CRC32 ... CRC-32 over (index, word) pairs ...`). |
| P-02 re-typed derived values for Python/C | FIXED | `derive:` replaces `value:` on `GEN_IBUS_MAX_OUTSTANDING`, `GEN_IRQ_FAST_MASK` and the new `GEN_IRQ_FAST_W`; the renderer parses `rtl/ibex_pkg.sv` (`BUS_SIZE`, `IC_LINE_SIZE`, `irq_fast` width) and emits a `<NAME>_PY` mirror; `gen_tb_top` fatals at time 0 when SV expression and mirror differ (`GEN_WIDTH_GUARD`). Unit test re-parses ibex_pkg independently (`OK derived GEN_IBUS_MAX_OUTSTANDING == GEN_ICACHE_NUM_FB * IC_LINE_BEATS (ibex_pkg parse)`, `OK derived GEN_IRQ_FAST_W == irq_fast width`, `OK derived GEN_IRQ_FAST_MASK == ((1 << w) - 1) << 16`). No guard fired in the twelve T-068 sims (`runs_summary_t068.txt`). |
| P-03 `--check` never shown to fail mechanically | FIXED | Codegen gained `--root`; the unit test copies the four targets to a repo-local scratch tree, mutates one digit in each in turn and asserts `--check` exits 1 naming that file, then 0 after restoring (`OK --check fails on a mutated dv/auto_dv/tb/gen_tb_pkg.sv`, ... `gen_env_cfg_knobs.svh`, ... `gen_knobs.py`, ... `gen_isa_shim_map.h`); `knobs_codegen_t068.log`. The hand-typed Section 4 excerpt is labelled UNRETAINED in the transcript. Three helper-defect attempts are retained and explained (`_attempt1..3.log`). |
| P-04 duplicated defaults inside the source | FIXED | `default_from:` on `boot_addr` (memory_map.boot_addr_default), `mem_readback_words`, `alive_timeout`, `finish_timeout` (new constant `GEN_FINISH_TIMEOUT_CYCLES_DEFAULT`); resolved at render time; unit test `OK boot_addr default from memory_map.boot_addr_default`, `OK <knob> default from <constant>` x3, `OK cfg boot_addr default resolved to the memory-map literal`. |
| P-05 debug-only knobs without the flag | FIXED | `debug_only: true` on `rvfi_trace`, `isa_string`, `isa_log`, `sb_trace`; Runtime extended `debug_only_plusargs` to the five names (gen_testlist.yaml:42); unit test `OK <n> is debug_only` x5 and `OK Runtime debug_only_plusargs lists gen_<n>` x5. |
| P-06 GEN_KNOB_KNOB_ prefix; "509 checks" re-run unretained | FIXED (prefix, in efe2a3e) / labelled | The re-run is labelled UNRETAINED in transcript Section 7; the T-068 run (674 OK) covers the current tree. |
| P-07 A-23 needs the argument list from outside SV | n/a | Withdrawn by the Critic (step-1b verdict Section 5); `uvm_cmdline_processor::get_args` enumerates the arguments; proven red again in T-068 (`neg_unknown_plusarg_t068_sim.log`). |
| L-1 no exit-status line in the zc Spike log | labelled | Section 5's Spike exit status is labelled UNRETAINED; every new log ends with `exit=<rc>` (the T-068 logs do). |
| L-2 gen_program.py:52 stale comment; unit-test docstring narrates history | FIXED | Comment replaced by one line stating the ISA string and MMIO page come from the rendered mirror; the docstring keeps the transcript pointer and no "written before" clause. |

## Cross-model findings

| Finding | Status | Location / validating run |
|---|---|---|
| [medium] yaml desc commas, `load()` accepts unknown keys | FIXED | As P-01. |
| [medium] derived constants re-typed for Python/C | FIXED | As P-02. |
| [medium] duplicated defaults (`boot_addr`, `mem_readback_words`, `alive_timeout`) | FIXED | As P-04. |
| [medium] `--check` mutation only as a hand-typed excerpt | FIXED | As P-03. |
| [low] "230 checks" vs 261; "19 DV Lead regime knobs" comment | FIXED | The comment says 20 (`REG_KNOBS`); the API document states no count; the transcript quotes the retained log's count (674 OK today). The commit message of 2d833d6 cannot be edited. |
| [low] gen_program.py:52 "will emit ... until then" | FIXED | As L-2. |
| [low] `rvfi_trace`, `isa_string`, `isa_log` lack `debug_only` | FIXED | As P-05 (plus `sb_trace`, which the 2a review noted). |
| [low] `GEN_KNOB_KNOB_` double prefix | FIXED | Renamed to `GEN_ENUM_` in efe2a3e (verified by the 1b reviews). |
| [low] docstring "Written BEFORE ..." | FIXED | Removed; also in `gen_ut_handles.py`, `gen_ut_mem_model_top.sv`, `gen_ut_isa_shim.cc`, `gen_ut_lockstep.py`. |
| [info] retained logs live under gitignored `work/` | FIXED | Verbatim copies under `dv/auto_dv/evidence/gen_tdd_logs/<component>/` with a manifest (path, source, bytes, md5); the transcripts name them. |
| [info] test plan names `+gen_regime_seed` | ROUTED | DV Lead informed (2026-09-03 message); not a TB Infra file. |
| [info] `gen_flow_const.py` literal plusarg copies | ROUTED | Runtime's file; its `--check` guards the copies against the package. |
