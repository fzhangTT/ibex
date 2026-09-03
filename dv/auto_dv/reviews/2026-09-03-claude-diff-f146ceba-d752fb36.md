# Cross-model review - committed diff f146ceba..d752fb36

**Reviewer:** claude CLI 2.1.259 (Claude Code); run-reported model: claude-fable-5-1,claude-haiku-4-5-20251001; requested effort: high (the CLI does not report the effective setting); fresh session b2cab71f-7ab4-462e-ae8b-2109aaefe310; sandbox: bubblewrap, working directory = detached read-only checkout of commit d752fb3693fde391b32ceb8e6e190fe18e81816d (the live working tree is not read), filesystem read-only except this run's own output directory, scratch HOME (no access to the executing model's settings, instructions or memory), private PID namespace; network open for the model API, web tools disallowed by policy (fallback reviewer per owner ruling A-001)
**Codex unavailable because:** ERROR: You hit your spend cap set by the owner of your workspace. Ask an owner to increase your spend cap to continue.
**Wrapper:** dv/auto_dv/tools/gen_cross_review.sh blob 713e8c09 (the copy executed; equals the wrapper committed at the reviewed commit); reviewed commit d752fb3693fde391b32ceb8e6e190fe18e81816d
**Date:** 2026-09-03
**Target:** committed diff f146ceba..d752fb36 (echo at raw line 1)

---

TARGET: f146cebad7b5de0cb52d5e5eb84ffd543b13fd61..d752fb3693fde391b32ceb8e6e190fe18e81816d

Scope reviewed: one commit (d752fb3), 261 files, 23 modified / 238 added. No file under `rtl/` changes. Verified against the checkout: `gen_knobs_codegen.py --check` reports up to date at d752fb3; `gen_protocol_props.sv` holds exactly 50 `P_ASSERT` and 20 `P_COVER` rows in nine groups as claimed; 229 retained-log files added and 229 manifest rows added; all nine mutants (MUT-M, MUT-N, RM1–RM4, WM1, MB13, MB14) have a FAIL catch verdict and a PASS ablation verdict, with isolation via `+gen_chk_all=0 +gen_chk_<id>=1` (the sanctioned inert-referee mechanism); final/shared canary runs all PASS except the by-design red fixture `gen_ut_witness_foreign`. The tainted first RM batch (shared-tree RTL mutated through a symlink) is disclosed and only the private-copy re-run is cited.

Rubric results:
- rtl-purity: PASS (no `rtl/**` lines in the range).
- forces-and-hier-access: PASS (`gen_binds.sv:18-19` are read-only absolute paths to TB-owned interface flags, justified by the adjacent comment; Python reads `.value` only).
- assertion-integrity: PASS (nothing disabled or deleted; the removed lines in `gen_tb_pkg.sv:531-532` and `gen_rvfi_pkg.sv:338-341` are comments only; `gen_ut_isa_shim.cc:417` swaps literal 5 for Spike's `CAUSE_LOAD_ACCESS` of equal value).
- magic-numbers: FAIL (findings below).
- ai-slop-comments: PASS with one low.

Findings:

[medium][dv/auto_dv/tb/gen_protocol_props.sv:341] `sva_alert_minor_window` hand-codes a two-cycle window (`$past(...,1) || $past(...,2)`) while the module's `ICACHE_ECC_WINDOW` parameter (line 15, bound to `GEN_ICACHE_ECC_WINDOW = 1` in gen_binds.sv:13) is never referenced, so the bind's knob is dead and the assertion is looser than the yaml's documented window - express the window through the parameter (or a `##[1:N]`-style range built from it), or raise the yaml constant to 2 with the reason and let the property use it.

[low][dv/auto_dv/tb/gen_protocol_props.sv:307] `sva_icram_widths` pins `28` / `78` as literals (also the parameter defaults at lines 87-88); these are config-derived (`IC_TAG_SIZE + IC_TAG_ECC_SIZE`, `BusSizeECC * IC_LINE_BEATS`, exactly how gen_dut_top.sv:80-81 derives them) - derive the expected widths from `ibex_pkg` the same way instead of re-typing the numbers.

[low][dv/auto_dv/tb/gen_protocol_props.sv:161-162] the plusarg names are re-typed as string literals (`"gen_chk_sva_"`, `"gen_chk_all=%d"`) rather than `gen_tb_pkg::PLUSARG_CHK_ALL` / `PLUSARG_CHK_SVA_*`; the rendered `cfg.chk_sva_*` fields (gen_env_cfg_knobs.svh:168-185) consequently have no consumer, so two parsers own one knob - build the names from the `PLUSARG_*` parameters (the module can import gen_tb_pkg; the bind already does) or note in the yaml desc that the cfg mirror is unconsumed.

[low][dv/auto_dv/env/gen_checkers_pkg.sv:273] `dcsr_q[1:0]` hand-slices the `dcsr.prv` field with no named authority (ibex_pkg has no dcsr struct; only the xdebugver constants) - name the field once (localparam or the shim map) and reference it.

[low][dv/auto_dv/env/gen_fcov_pkg.sv:71-72] the `wit_referee` check has no mutation evidence: WM1 was caught by the Python assert and the sim ended before report_phase (`uvm_counts: {}` in the WM1 catch verdict), so the referee's own firing is only shown incidentally in the wit/b TDD red - add a referee-targeted mutant (e.g. sample a different index than the one bookkept) with the Python assert inert, per trust-triad rule 2.

[low][dv/auto_dv/mutations/gen_mut_step2b.md:113-115] RM1..RM3 share `build 68a36e6ac32db967` because the RTL copy is outside the sources hash (disclosed in the text), so the build column cannot distinguish the three RTL mutants - record the mutated RTL file's sha per RM row (the rerun log already prints the originals) so each row is independently attributable.

[low][dv/auto_dv/tb/gen_protocol_props.sv:73-74] the header cites `dv/auto_dv/work/rtl-arch` and `gen_protocol_props_draft.sv` / `gen_protocol_props_table.md`, none of which are tracked at this commit (`git ls-files` finds neither), and line 277's "(landing 2b)" is history narration - keep the deviation list (it is intent) but drop the untracked-path provenance and the landing tag; the mutation record and TDD file already carry the history.

[low][dv/auto_dv/gen_tb/gen_tests/gen_ut_witness_foreign.py:1] the new tb-infra unit test shares its module basename with the pre-existing Test Writer red fixture `dv/auto_dv/tests/gen_fixtures/gen_ut_witness_foreign.py` (different package, different purpose); the retained-log names `gen_fu_l2b_*_ut_witness_foreign_*` do not say which - rename one (e.g. `gen_ut_cov_witness_foreign`) or state the module path in the manifest rows.

Final verdict: APPROVE-WITH-CHANGES
