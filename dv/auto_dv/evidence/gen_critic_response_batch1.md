# Response: Critic verdict on Phase 1 batch 1 (cb3d7eb) and the cross-model review of 7594017..d58bdeb

Critic: `dv/auto_dv/docs/gen_critic_batch1_v1.md` (REQUEST-CHANGES: H-1, M-1..M-4, L-1..L-4, per-test Section 3).
Cross-model: `dv/auto_dv/reviews/2026-09-03-claude-diff-75940174-d58bdeb2.md` (REQUEST-CHANGES; the Test Writer rows are
the [Major] red_expect finding and the [Minor] note on the four comparator-blocked reds; the rest is Runtime's flow).
Author: test-writer, 2026-09-03 12:20 UTC. Evidence: `dv/auto_dv/evidence/gen_tdd_batch1.md` Sections 6, 7 and 8; retained
logs `dv/auto_dv/evidence/gen_tdd_logs/test_writer/gen_manifest.md`. Row prefixes: CR- Critic, CM- cross-model.

## Cross-cutting

| # | Severity | Finding | Disposition | Change and evidence |
|---|---|---|---|---|
| CR-H-1 | high | the committed tree cannot pass its own finish(): declare_bins() [] vs committed manifests | FIXED (38d1262, T-109) then tightened here | declare_bins() default is the plan's bins of the items named by the class's fire_tp_<area>_<nnn> methods (lib.fire_items / lib.plan_bins, the manifest generator's own derivation); a missing manifest with declared bins FAILS, a stale one FAILS naming the tokens (fixtures gen_ut_manifest_missing / gen_ut_manifest_stale, batch-1 Section 6). Greens on the committed template with the manifests present: Section 8.1, one per test on seeds 1 and 2 (GEN_TEST_BINS 9/81/80/172/110/473/15/266). Wave 2 (Section 7) proved the four clean tests in the flow: 11 of 12 PASS, 4 of 4 RED-OK. |
| CR-M-1 | medium | manifests rendered for whole groups while tests build subsets | FIXED | `gen_fcov_manifest.py --test-module <test.py> --test <name> --write` renders exactly the items the fire_tp_* methods name; the eight manifests re-rendered (rst_boot 9, csr_reset 81, csr_access 80, csr_trap_setup 172, cmp_zcb 110, cmp_zcmp_basic 473, bit_draft 15, pmp_csr_warl 266 bins); unbuilt items are listed in each docstring with the missing component (already, now with owners). The generator self-test checks gen_test_cmp_zcb.py yields TP-CMP-034/036/038. |
| CR-M-2 | medium | witness bins of marked items in the csr_trap_setup manifest | FIXED | Rule (f): an item carrying `[CYCLE-CLAUSE coverage-only until the event export lands]` contributes no CG-WIT-001 bin (gen_fcov_manifest.CYCLE_CLAUSE_TOKEN, WITNESS_CG); self-test on TP-CSR-029; csr_trap_setup re-rendered (0 gen_wit bins; the self-test's gen_reg_schedule case now drops 1). |
| CR-M-3 | medium | one red per test only | FIXED | Every generator: `--red [--red-item <TP>]`, one program-only deviation per built item (the seed draws the item without --red-item; expectations unchanged, asserted per generator). 53 red runs at seed 1, one per fire_tp item, each tripping the intended item (Section 8.2; supersets named). Flow red entries pin one item each. |
| CR-M-4 | medium | stimulus bent around TB defects (csr_access rd = x0 reads; pmp LRWX refusal) | FIXED | csr_access: the rd = x0 reads of marchid, cycle/cycleh, hpmcounter3..12 are removed and the TP-CSR-001 clause for them is declared BLOCKED on T-102 in both docstrings (no discarded-result read stands in). pmp_csr_warl: the LRWX = 1111 refusal is removed; the pattern is programmed with the spec-derived expectation (smepmp.adoc) and seed 25, which draws it, PASSes with 0 isa_csr rows (rem_pmp_csr_warl_s25). rst_boot, csr_reset, csr_trap_setup: no dodge existed (every read lands in rd != x0; the comparator reports the T-102 gaps, 8 / 42 / 408 rows). |
| CR-L-1 | low | layers_required = False without measured: false entries | FIXED | Entries are in gen_testlist.yaml since d58bdeb with measured: false; the structure check now refuses layers_required = False without such an entry (retention landing). |
| CR-L-2 | low | CSR tables, values, config name, tohost codes re-typed per generator | FIXED | dv/auto_dv/tests/gen_programs/gen_prog_const.py (61 CSR names, PMP/HPM bases and helpers, MSTATUS_RESET, MISA_VALUE, MCONFIGPTR_VALUE, TOHOST codes re-exported from gen_test_lib, CONFIG_NAME from gen_flow_const.BUILD_CONFIG); cross-checked against every generator's former table; the generators import it. W-tables stay per generator with the plan section cited (each is one item's table). |
| CR-L-3 | low | history in docstrings | FIXED | Removed in all eight tests and generators. |
| CR-L-4 | low | Zcmp/Zcb docstrings on rvfi_insn | NOTED | Consistent with rtl/ibex_core.sv and C-12; no change. |
| CM-Major | major | red_expect generic (`[0-9]+ fire-check failure`) although the fire id is on the same line | FIXED | Red entries: `generator_args: [--red, --red-item, <TP>]`, `red_expect: 'GEN_TEST_FAIL gen_test_<g>: [0-9]+ fire-check failure\(s\): fire_tp_<item>'` (gen_testlist_entries.yaml, Runtime re-copies). |
| CM-Minor | minor | four reds cannot reach RED-OK until T-102 | ACKNOWLEDGED | Their first evidence line is the comparator's; entries kept; re-filed after T-102 (TB Infra). |

## Per test (Critic Section 3; details in each subagent's table, re-verified by the Test Writer from the run logs)

| Test | Items | Disposition |
|---|---|---|
| 3.1 gen_test_rst_boot | PMP_REGIONS / zero table re-typed; knob value literals; dropped TP-RST-006 clauses; verbose detail | FIXED: PMPNumRegions from ibex_configs.yaml, pmpcfg()/pmpaddr(); KEY_REGIMES = lib.knob_values("knob_scr_key_delay") with a loud table assert; blocked clauses (irq line held, rvfi_mode records, ecall vector, dcsr/dpc/dscratch) named per item with the missing channel; detail = counts plus 3 mismatches. Reds 003/006/007. |
| 3.2 gen_test_csr_reset | key regime from the command line; 105/106/109 position unasserted; mip vs irq_line_mix; slack literals | FIXED: regime from the layer-2 draw (_knob_regimes); "never + 2" removed with the derivation; one bounded lead item per seed (W_EARLY) with the retirement position asserted from Report.idx; mip gating derived from the irq regime; INSTRET_SKEW removed (exact), MCYCLE_SLACK derived. Reds 037/105/106/107/108/109. |
| 3.3 gen_test_csr_access | red diverges the rng; M-4; constrain(pmpcfg); op-class floor; literals; history | FIXED: red keeps the drawn op and flips one writable bit (one instruction line differs); W-without-R patterns drawn; every op class asserted per seed; literals given a home; M-4 as above. Reds 001/002/003/004/012 (rem_csr_access_v2_*; the first set was clobbered by a scratchpad collision and superseded). |
| 3.4 gen_test_csr_trap_setup | TP-CSR-035 base classes unreachable; W-PAT weights; csrrsi limitation | FIXED: low class reached with a handler copy in the program's .debug_rom at DmHaltAddr + 0x100, boot class via the boot-page base write + read-back, all three classes asserted per seed; W-PAT rand 30 / all1 10 / all0 10 / msb 5; csrrsi limitation removed (installs carry random bits 7:0). Reds 023/024/025/027/028/029/030/035/036. |
| 3.5 gen_test_cmp_zcb | no program-verdict check; export dependency unnamed | FIXED: fire_program_verdict (tohost, retirement floor, report count); the rmask/wmask and split-access clauses named as blocked on the RVFI record export / bus records. Reds 034/036/038; 500-plan sweep clean. |
| 3.6 gen_test_cmp_zcmp_basic | 039 >= 3x; b2b pop invisible; literals; icache precondition | FIXED: 48 combos x 3 shuffled and asserted; b2b pop uses a longer rlist at equal stack_adj (the 066 red proves a no-load pop is caught); csr_hex / one pinned table; icache precondition stated (cpuctrlsts reset 0, never written). fire_tp_cmp_043 narrowed to its sp words (it duplicated 039+045). Program 1.6x longer (program_budget_cycles = 3 x default). 17 reds. |
| 3.7 gen_test_bit_draft | controls unasserted; vacuous compares; blocked items without owner | FIXED: directed floor of 128 (base, control) pairs plus extras, asserted per seed (fire_tp_bit_016_controls / _single_bit / _rs2_upper); rd = x0 and 0 / all-ones operands counted apart; 13 blocked items named with owner TB Infra (T-102 item 4). Reds :imm and :ctrl (the second proves the coverage check fires). |
| 3.8 gen_test_pmp_csr_warl | M-4 LRWX; RTL cited as rule source; DUT-reported bases; U-RW region; wording | FIXED: LRWX programmed (spec-derived), rules re-cited to machine.adoc / smepmp.adoc / cs_registers.rst with RTL as cross-check, bases from prog.sym.json and the DUT words checked against them, U-RW region stated as not programmed with the reason, "4-byte grain" wording. Reds 001..008; 50-seed sweep clean. |

## Not changed, stated

The four comparator-blocked tests still FAIL the flow verdict through uvm_error until TB Infra's T-102; nothing in them
avoids the observation. The per-item red runs are local (retained with md5); the flow carries one pinned red entry per test.

## Cross-model review of 38d1262 (APPROVE-WITH-CHANGES, `dv/auto_dv/reviews/2026-09-03-claude-diff-8ad2d627-38d12626.md`)

| # | Severity | Finding | Disposition | Change and evidence |
|---|---|---|---|---|
| CM-T109-M-1 | medium | plan_bins raises for a group whose items rules (a)/(b) exclude entirely | FIXED | gen_fcov_manifest.plan_bins returns [] with a stderr line naming the exclusions (bins_of_items required=False); rendering a manifest with zero bins stays an error. |
| CM-T109-M-2 | medium | default declaration is the whole group including blocked items | FIXED (2d72b4a) | Declared bins are the plan bins of exactly the items the class's fire_tp_* methods name; manifests rendered with --test-module; blocked items contribute no bin and are listed in the docstring. |
| CM-T109-L-1 | low | gen_test_cmp_zcb.py docstring says declare_bins() returns [] | FIXED (2d72b4a) | Docstring rewritten by the remediation. |
| CM-T109-L-2 | low | plan and API must state the new semantics and the override-with-reason rule | FIXED (landing 3) | gen_test_writer_plan.md Section 1 row "bins of a test" and Section 2 bullet; API Sections 2, 3, 7, 9. |
| CM-T109-L-3 | low | gen_ut_manifest_stale.fcov.yaml is a static copy that drifts | FIXED (landing 3) | The fixture derives its stale manifest at import from the current gen_test_cmp_zcb manifest minus its last bin; the static file is deleted. |
| CM-T109-I-1 | info | a test whose name does not match a plan group declares [] and skips the check | STATED | Now moot: the declaration keys on fire_tp_* items, not on the name; a test with no fire_tp_* method declares nothing (bring-up tests, fixtures) and the entry's fcov_manifest_required_tiers gate is Runtime's. |
| CM-T109-I-2 | info | set-difference compare misses a doubly-declared bin | NO ACTION | As the reviewer said. |

## Cross-model review of cb3d7eb (batch 1, `dv/auto_dv/reviews/2026-09-03-claude-diff-d5afa0fd-cb3d7eb0.md`), status after 2d72b4a and landing 3

| # | Severity | Finding | Disposition | Change and evidence |
|---|---|---|---|---|
| CM-B1-H | high | committing the manifests wired them into finish() at once | FIXED (38d1262 + 2d72b4a) | Answered by the declare_bins mechanism (CR-H-1): the default declaration comes from the same code that renders the manifest, so a committed manifest can only fail a run when it is stale against the plan or covers items the test does not check. |
| CM-B1-M-1 | medium | manifests rendered for the whole group | FIXED (2d72b4a) | Per built item set (CR-M-1). |
| CM-B1-M-2 | medium | CSR addresses re-typed in five generators | FIXED (2d72b4a) | gen_programs/gen_prog_const.py (CR-L-2); a rendered table from the shim's CSR map can replace its literals when TB Infra renders one. |
| CM-B1-L-1 | low | irq-agent preconditions silently reduced (TP-CSR-023/029, TP-RST-006) | FIXED (landing 3) | Docstrings carry "Precondition not applied: irq agent absent (step 2b)" per item, and the fire-checks log GEN_TEST_INFO with the same label so the item is not counted as fully built. |
| CM-B1-L-2 | low | docstrings cite entries and a transcript outside the reviewed range | FIXED (landing 3) | The layers line cites d58bdeb (entries); the T-102 status cites d0c0d15 and 50256f0. |
| CM-B1-L-3 | low | layers_required block pasted into eight docstrings | FIXED (landing 3) | One line per test pointing at API Section 3; one standard class-level comment. |

## Critic verdict on T-102 (`dv/auto_dv/docs/gen_critic_tb_t102.md`), Test Writer caveat

| # | Finding | Disposition | Change and evidence |
|---|---|---|---|
| CR-T102-1 | revert the M-4 dodges; counter and cpuctrlsts reads are consistency compares until ctr_*/scrkey_proto exist | FIXED (landing 3) | gen_test_csr_access restores the marchid/cycle/hpm reads with rd != x0 and labels them "checked for consistency; value verification pending ctr_*/scrkey_proto"; gen_test_pmp_csr_warl programs LRWX = 1111 (2d72b4a); csr_reset, rst_boot state the same caveat for their counter and cpuctrlsts bit 8 read-backs. The four tests' "blocked on T-102" wording is replaced by the T-102 status citing d0c0d15/50256f0. |

## Acceptance wave 3 (2d72b4a) and the generator import defect

| # | Finding | Disposition | Change and evidence |
|---|---|---|---|
| TW-W3-1 | test-writer-033/037 NOT_RUN: gen_cmp_zcmp_basic_prog.py imports gen_prog_const without the sys.path guard, so the flow's script invocation dies with ModuleNotFoundError | FIXED (landing 3) | Guard added (seed-1 source byte-identical); the library self-test now runs every generator as a script with no PYTHONPATH from the clone root, the flow's form, so the class of defect is caught before a commit. Re-filed as wave 3b after the landing. |
