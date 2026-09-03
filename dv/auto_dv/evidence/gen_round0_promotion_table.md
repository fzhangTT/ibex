# Per-entry tier ruling for the 16 built tests (DV Lead; applied by the Test Writer's landing 3e at 7ef16a0 and Runtime's promotion landing 3e6f1b2; LOG-024e, LOG-039)

Committed with plan v2p part 2 as the tracked source of the promotion (the work-tree original was the file the landings relied on). gen_ut_lockstep (tb-infra's lock-step check, no plan items, no manifest) is measured: false in the promotion landing per LOG-039 and is not a row of this table.

Rules applied (gen_test_plan.md b8332f9 + bc4ede6): a testlist entry's tier is the LOWEST tier among its plan group's items,
because the testlist runs a tier-T entry in every higher tier too (gen_testlist.yaml header); an entry with no plan group stays
in tier check, measured: false. The plan sets no per-tier seed count: round 0 runs the declared 3 seeds per entry (the plan's
"per seed" fire-check floors hold per seed by construction) and the closure rounds raise seeds where bins stay unhit
(gen_fcov_plan.md Section 1 closure rule). measured: true for every promoted entry; fcov_expectation_file wired to the
per-item manifest of the entry's class (gen_fcov_manifest.py --test-module); fcov_manifest_required_tiers: [smoke, targeted].
Held items (plan Sections 1.4 and 1.5, generated at bc4ede6) run measured but their results are excluded from crediting
until the hold lifts; the earlier message named TP-CSR-023 as held, which is wrong: TP-CSR-023's irq-cause bins are
bins_not_hit (rule (g)), the T-136 item in gen_csr_trap_setup is TP-CSR-035.

| Entry (gen_test_<x>) | Plan group | Items (smoke / targeted) | Tier ruling | Seeds | Held items excluded from crediting |
|---|---|---|---|---|---|
| gen_test_boot_retire | none (flow boot / retire check, no plan items) | - | check (unchanged), measured: false | 3 | - |
| gen_test_rst_boot | gen_rst_boot | 11 (9 / 2) | smoke | 3 | TP-RST-006 (T-136) |
| gen_test_csr_reset | gen_csr_reset | 6 (6 / 0) | smoke | 3 | - |
| gen_test_csr_access | gen_csr_access | 6 (5 / 1) | smoke | 3 | - |
| gen_test_csr_trap_setup | gen_csr_trap_setup (9 items: TP-CSR-029 stays after the landing review; only 026 and 031 moved to gen_csr_trap_setup_irq) | 9 (8 / 1) | smoke | 3 | TP-CSR-035 (T-136); TP-CSR-023's irq-cause bins and TP-CSR-029's irq case are bins_not_hit, not holds; TP-CSR-029's witness bin stays excluded while marked (gated) |
| gen_test_cmp_zcb | gen_cmp_zcb | 3 (3 / 0) | smoke | 3 | - |
| gen_test_cmp_zcmp_basic | gen_cmp_zcmp_basic | 18 (6 / 12) | smoke | 3 | - |
| gen_test_bit_draft | gen_bit_draft | 14 (0 / 14) | targeted | 3 | - (TP-BIT-011, 022..033 not_built until the shim extension is confirmed) |
| gen_test_pmp_csr_warl | gen_pmp_csr_warl | 8 (3 / 5) | smoke | 3 | TP-PMP-006 (T-137) |
| gen_test_mul_div | gen_mul_div | 12 (4 / 8) | smoke | 3 | - |
| gen_test_mul_mul | gen_mul_mul | 9 (4 / 5) | smoke | 3 | - |
| gen_test_isa_cti | gen_isa_cti | 12 (3 / 9) | smoke | 3 | TP-ISA-016, TP-ISA-026 (T-136); TP-ISA-016 / 022 / 026 also not_built on WP-9 |
| gen_test_isa_shift | gen_isa_shift | 4 (2 / 2) | smoke | 3 | - |
| gen_test_isa_alu | gen_isa_alu | 10 (3 / 7) | smoke | 3 | - (TP-ISA-006 high / low bins not_built on WP-9) |
| gen_test_bit_ratified | gen_bit_ratified | 19 (13 / 6) | smoke | 3 | - |
| gen_test_cmp_zca | gen_cmp_zca | 21 (18 / 3) | smoke | 3 | TP-CMP-011 (T-136) |

Totals: 15 entries promoted (14 smoke, 1 targeted), 1 stays check; 6 held items over 5 groups (T-136: 5, T-137: 1).
Round-0 request text (after the promotion is committed and Runtime's check-tier acceptance 049..064 passes):
gen_round.py --round 0 --label "Phase 1 gate" --elfile dv/auto_dv/excl/gen_exclusions.el --requester dv-lead, source
mode head at the promotion sha, seeds per entry from the testlist, exclusion file pass 13 (9ebf2d9), plan sha bc4ede6.
