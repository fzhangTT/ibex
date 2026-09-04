## 1.7 Round-0 PROBE crediting (probe of 37c7ecb refused as a round, LOG-046; 0 credited, every hosted item NOT-RUN-CLEAN) (generated from the regression manifest and sim logs; 162 items in 15 hosted groups)

Invocation, byte for byte (copy the whole line; a quoted heading may contain semicolons): python3 dv/auto_dv/tools/gen_round_credit.py --regress-manifest /proj_soc/user_dev/fzhang/ibex_dv_out/regress_round_0/manifest.yaml --plan-sha v4q-on-a6ae390 --round 0 --heading-id round0-probe --csv dv/auto_dv/evidence/gen_round0_credit/gen_round0_credit.csv --md dv/auto_dv/evidence/gen_round0_credit/gen_round0_credit.md; regression manifest sha256 4c9a21df00d6adf6ea092d1dda930c952836737b57c9e0e39d20e2737c8bf587; plan inputs read (item headers with group / tier / expected, hold sections, carve-out sections and rows with item / tag / until / reason, gen_trace_tp_bin.csv, gen_trace_witness_ids.csv) digest 282949a36e21; carve-out rows read 2 (0 hosted in this round; the UNCREDITED / COUNTED-ONLY columns count carved items that would otherwise have credited, a carved item that is UNHIT or NOT-RUN-CLEAN keeps that state and shows its tag in the Carve-out column); landing label v4q-on-a6ae390 (the --plan-sha argument, a label only, not the commit whose plan was read). Regression /proj_soc/user_dev/fzhang/ibex_dv_out/regress_round_0: status done, source {'mode': 'head', 'source_root': '/proj_soc/user_dev/fzhang/ibex_dv_mirror_head/37c7ecb6dbe0', 'head_sha': '37c7ecb6dbe023e6f6b098e932367e339a24735a', 'worktree_dirty': None}, git 37c7ecb6dbe023e6f6b098e932367e339a24735a; 47 runs: pass 2, fail 45, xfail 0, red_ok 0, timeout 0, not_run 0; fcov checks {'checked': 44, 'pass': 0, 'unmet': 0, 'unverifiable': 44}; covergroups_exist False; clean regression (gen_round.py hard rule): NO.

| Area | Items hosted | CREDITED | UNCREDITED | COUNTED-ONLY | HELD | UNHIT | FIRE-FAIL | NOT-FIRED | NOT-RUN-CLEAN | UNVERIFIED |
|---|---|---|---|---|---|---|---|---|---|---|
| BIT | 33 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 33 | 0 |
| CMP | 42 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 42 | 0 |
| CSR | 21 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 21 | 0 |
| ISA | 26 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 26 | 0 |
| MUL | 21 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 21 | 0 |
| PMP | 8 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 8 | 0 |
| RST | 9 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 9 | 0 |
| RVFI | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 |
| SEC | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 |

Total: 162 items hosted; credited 0; uncredited (carve-out) 0; counted-only 0; held 0; unhit 0; fire-fail 0; not fired 0; not run clean 162; unverified 0.
Witness bins of hosted items: 2 (unscored until T-179; listed, never credited).

Per test (every run of the regression, red fixtures included; the item table below excludes red fixtures, which host no items):

| Test | Seeds | Verdicts | Distinct reasons |
|---|---|---|---|
| gen_boot_zc | 1 | PASS | no collected failure mechanism; end marker and config banner |
| gen_test_bit_draft | 3 | FAIL | fcov expectation unverifiable: per-test urg report has no gr |
| gen_test_bit_ratified | 3 | FAIL | fcov expectation unverifiable: per-test urg report has no gr |
| gen_test_cmp_zca | 3 | FAIL | fcov expectation unverifiable: per-test urg report has no gr |
| gen_test_cmp_zcb | 3 | FAIL | fcov expectation unverifiable: per-test urg report has no gr |
| gen_test_cmp_zcmp_basic | 3 | FAIL | fcov expectation unverifiable: per-test urg report has no gr |
| gen_test_csr_access | 3 | FAIL | fcov expectation unverifiable: per-test urg report has no gr |
| gen_test_csr_reset | 3 | FAIL | cocotb_summary at sim_stdout.log:112; fcov expectation unverifiable: per-test urg report has no gr |
| gen_test_csr_trap_setup | 3 | FAIL | fcov expectation unverifiable: per-test urg report has no gr |
| gen_test_isa_alu | 3 | FAIL | fcov expectation unverifiable: per-test urg report has no gr |
| gen_test_isa_cti | 3 | FAIL | fcov expectation unverifiable: per-test urg report has no gr |
| gen_test_isa_shift | 3 | FAIL | fcov expectation unverifiable: per-test urg report has no gr |
| gen_test_mul_div | 3 | FAIL | fcov expectation unverifiable: per-test urg report has no gr |
| gen_test_mul_mul | 3 | FAIL | fcov expectation unverifiable: per-test urg report has no gr |
| gen_test_pmp_csr_warl | 3 | FAIL | fcov expectation unverifiable: per-test urg report has no gr |
| gen_test_rst_boot | 3 | FAIL | fcov expectation unverifiable: per-test urg report has no gr |
| gen_ut_lockstep | 1 | PASS | no collected failure mechanism; end marker and config banner |

| Item | Group | Test | Seeds | Verdicts | Fired | Bins | Unhit | Hold | Carve-out | Status |
|---|---|---|---|---|---|---|---|---|---|---|
| TP-BIT-001 | gen_bit_ratified | gen_test_bit_ratified | 3 | FAIL | none | 59 | 59 | - | - | NOT-RUN-CLEAN (fcov expectation unverifiable: per-test urg report has no grpinfo.txt ) |
| TP-BIT-002 | gen_bit_ratified | gen_test_bit_ratified | 3 | FAIL | yes | 71 | 71 | - | - | NOT-RUN-CLEAN (fcov expectation unverifiable: per-test urg report has no grpinfo.txt ) |
| TP-BIT-003 | gen_bit_ratified | gen_test_bit_ratified | 3 | FAIL | yes | 99 | 99 | - | - | NOT-RUN-CLEAN (fcov expectation unverifiable: per-test urg report has no grpinfo.txt ) |
| TP-BIT-004 | gen_bit_ratified | gen_test_bit_ratified | 3 | FAIL | yes | 73 | 73 | - | - | NOT-RUN-CLEAN (fcov expectation unverifiable: per-test urg report has no grpinfo.txt ) |
| TP-BIT-005 | gen_bit_ratified | gen_test_bit_ratified | 3 | FAIL | yes | 51 | 51 | - | - | NOT-RUN-CLEAN (fcov expectation unverifiable: per-test urg report has no grpinfo.txt ) |
| TP-BIT-006 | gen_bit_ratified | gen_test_bit_ratified | 3 | FAIL | yes | 145 | 145 | - | - | NOT-RUN-CLEAN (fcov expectation unverifiable: per-test urg report has no grpinfo.txt ) |
| TP-BIT-007 | gen_bit_ratified | gen_test_bit_ratified | 3 | FAIL | yes | 109 | 109 | - | - | NOT-RUN-CLEAN (fcov expectation unverifiable: per-test urg report has no grpinfo.txt ) |
| TP-BIT-008 | gen_bit_ratified | gen_test_bit_ratified | 3 | FAIL | yes | 65 | 65 | - | - | NOT-RUN-CLEAN (fcov expectation unverifiable: per-test urg report has no grpinfo.txt ) |
| TP-BIT-009 | gen_bit_ratified | gen_test_bit_ratified | 3 | FAIL | yes | 6 | 6 | - | - | NOT-RUN-CLEAN (fcov expectation unverifiable: per-test urg report has no grpinfo.txt ) |
| TP-BIT-010 | gen_bit_ratified | gen_test_bit_ratified | 3 | FAIL | yes | 22 | 22 | - | - | NOT-RUN-CLEAN (fcov expectation unverifiable: per-test urg report has no grpinfo.txt ) |
| TP-BIT-011 | gen_bit_draft | gen_test_bit_draft | 3 | FAIL | none | 83 | 83 | - | - | NOT-RUN-CLEAN (fcov expectation unverifiable: per-test urg report has no grpinfo.txt ) |
| TP-BIT-014 | gen_bit_ratified | gen_test_bit_ratified | 3 | FAIL | yes | 13 | 13 | - | - | NOT-RUN-CLEAN (fcov expectation unverifiable: per-test urg report has no grpinfo.txt ) |
| TP-BIT-015 | gen_bit_ratified | gen_test_bit_ratified | 3 | FAIL | yes | 3 | 3 | - | - | NOT-RUN-CLEAN (fcov expectation unverifiable: per-test urg report has no grpinfo.txt ) |
| TP-BIT-016 | gen_bit_draft | gen_test_bit_draft | 3 | FAIL | yes | 15 | 15 | - | - | NOT-RUN-CLEAN (fcov expectation unverifiable: per-test urg report has no grpinfo.txt ) |
| TP-BIT-017 | gen_bit_ratified | gen_test_bit_ratified | 3 | FAIL | yes | 33 | 33 | - | - | NOT-RUN-CLEAN (fcov expectation unverifiable: per-test urg report has no grpinfo.txt ) |
| TP-BIT-018 | gen_bit_ratified | gen_test_bit_ratified | 3 | FAIL | yes | 48 | 48 | - | - | NOT-RUN-CLEAN (fcov expectation unverifiable: per-test urg report has no grpinfo.txt ) |
| TP-BIT-019 | gen_bit_ratified | gen_test_bit_ratified | 3 | FAIL | yes | 16 | 16 | - | - | NOT-RUN-CLEAN (fcov expectation unverifiable: per-test urg report has no grpinfo.txt ) |
| TP-BIT-020 | gen_bit_ratified | gen_test_bit_ratified | 3 | FAIL | yes | 43 | 43 | - | - | NOT-RUN-CLEAN (fcov expectation unverifiable: per-test urg report has no grpinfo.txt ) |
| TP-BIT-021 | gen_bit_ratified | gen_test_bit_ratified | 3 | FAIL | yes | 15 | 15 | - | - | NOT-RUN-CLEAN (fcov expectation unverifiable: per-test urg report has no grpinfo.txt ) |
| TP-BIT-022 | gen_bit_draft | gen_test_bit_draft | 3 | FAIL | none | 51 | 51 | - | - | NOT-RUN-CLEAN (fcov expectation unverifiable: per-test urg report has no grpinfo.txt ) |
| TP-BIT-023 | gen_bit_draft | gen_test_bit_draft | 3 | FAIL | none | 27 | 27 | - | - | NOT-RUN-CLEAN (fcov expectation unverifiable: per-test urg report has no grpinfo.txt ) |
| TP-BIT-024 | gen_bit_draft | gen_test_bit_draft | 3 | FAIL | none | 10 | 10 | - | - | NOT-RUN-CLEAN (fcov expectation unverifiable: per-test urg report has no grpinfo.txt ) |
| TP-BIT-025 | gen_bit_draft | gen_test_bit_draft | 3 | FAIL | none | 43 | 43 | - | - | NOT-RUN-CLEAN (fcov expectation unverifiable: per-test urg report has no grpinfo.txt ) |
| TP-BIT-026 | gen_bit_draft | gen_test_bit_draft | 3 | FAIL | none | 18 | 18 | - | - | NOT-RUN-CLEAN (fcov expectation unverifiable: per-test urg report has no grpinfo.txt ) |
| TP-BIT-027 | gen_bit_draft | gen_test_bit_draft | 3 | FAIL | none | 46 | 46 | - | - | NOT-RUN-CLEAN (fcov expectation unverifiable: per-test urg report has no grpinfo.txt ) |
| TP-BIT-028 | gen_bit_draft | gen_test_bit_draft | 3 | FAIL | none | 80 | 80 | - | - | NOT-RUN-CLEAN (fcov expectation unverifiable: per-test urg report has no grpinfo.txt ) |
| TP-BIT-029 | gen_bit_draft | gen_test_bit_draft | 3 | FAIL | none | 11 | 11 | - | - | NOT-RUN-CLEAN (fcov expectation unverifiable: per-test urg report has no grpinfo.txt ) |
| TP-BIT-030 | gen_bit_draft | gen_test_bit_draft | 3 | FAIL | none | 54 | 54 | - | - | NOT-RUN-CLEAN (fcov expectation unverifiable: per-test urg report has no grpinfo.txt ) |
| TP-BIT-031 | gen_bit_draft | gen_test_bit_draft | 3 | FAIL | none | 10 | 10 | - | - | NOT-RUN-CLEAN (fcov expectation unverifiable: per-test urg report has no grpinfo.txt ) |
| TP-BIT-032 | gen_bit_draft | gen_test_bit_draft | 3 | FAIL | none | 70 | 70 | - | - | NOT-RUN-CLEAN (fcov expectation unverifiable: per-test urg report has no grpinfo.txt ) |
| TP-BIT-033 | gen_bit_draft | gen_test_bit_draft | 3 | FAIL | none | 5 | 5 | - | - | NOT-RUN-CLEAN (fcov expectation unverifiable: per-test urg report has no grpinfo.txt ) |
| TP-BIT-038 | gen_bit_ratified | gen_test_bit_ratified | 3 | FAIL | yes | 196 | 196 | - | - | NOT-RUN-CLEAN (fcov expectation unverifiable: per-test urg report has no grpinfo.txt ) |
| TP-BIT-040 | gen_bit_ratified | gen_test_bit_ratified | 3 | FAIL | yes | 4 | 4 | - | - | NOT-RUN-CLEAN (fcov expectation unverifiable: per-test urg report has no grpinfo.txt ) |
| TP-CMP-001 | gen_cmp_zca | gen_test_cmp_zca | 3 | FAIL | yes | 137 | 137 | - | - | NOT-RUN-CLEAN (fcov expectation unverifiable: per-test urg report has no grpinfo.txt ) |
| TP-CMP-002 | gen_cmp_zca | gen_test_cmp_zca | 3 | FAIL | yes | 12 | 12 | - | - | NOT-RUN-CLEAN (fcov expectation unverifiable: per-test urg report has no grpinfo.txt ) |
| TP-CMP-004 | gen_cmp_zca | gen_test_cmp_zca | 3 | FAIL | yes | 5 | 5 | - | - | NOT-RUN-CLEAN (fcov expectation unverifiable: per-test urg report has no grpinfo.txt ) |
| TP-CMP-005 | gen_cmp_zca | gen_test_cmp_zca | 3 | FAIL | yes | 20 | 20 | - | - | NOT-RUN-CLEAN (fcov expectation unverifiable: per-test urg report has no grpinfo.txt ) |
| TP-CMP-008 | gen_cmp_zca | gen_test_cmp_zca | 3 | FAIL | yes | 13 | 13 | - | - | NOT-RUN-CLEAN (fcov expectation unverifiable: per-test urg report has no grpinfo.txt ) |
| TP-CMP-010 | gen_cmp_zca | gen_test_cmp_zca | 3 | FAIL | yes | 12 | 12 | - | - | NOT-RUN-CLEAN (fcov expectation unverifiable: per-test urg report has no grpinfo.txt ) |
| TP-CMP-011 | gen_cmp_zca | gen_test_cmp_zca | 3 | FAIL | yes | 7 | 7 | - | - | NOT-RUN-CLEAN (fcov expectation unverifiable: per-test urg report has no grpinfo.txt ) |
| TP-CMP-012 | gen_cmp_zca | gen_test_cmp_zca | 3 | FAIL | yes | 6 | 6 | - | - | NOT-RUN-CLEAN (fcov expectation unverifiable: per-test urg report has no grpinfo.txt ) |
| TP-CMP-014 | gen_cmp_zca | gen_test_cmp_zca | 3 | FAIL | yes | 6 | 6 | - | - | NOT-RUN-CLEAN (fcov expectation unverifiable: per-test urg report has no grpinfo.txt ) |
| TP-CMP-016 | gen_cmp_zca | gen_test_cmp_zca | 3 | FAIL | yes | 12 | 12 | - | - | NOT-RUN-CLEAN (fcov expectation unverifiable: per-test urg report has no grpinfo.txt ) |
| TP-CMP-017 | gen_cmp_zca | gen_test_cmp_zca | 3 | FAIL | yes | 12 | 12 | - | - | NOT-RUN-CLEAN (fcov expectation unverifiable: per-test urg report has no grpinfo.txt ) |
| TP-CMP-018 | gen_cmp_zca | gen_test_cmp_zca | 3 | FAIL | yes | 17 | 17 | - | - | NOT-RUN-CLEAN (fcov expectation unverifiable: per-test urg report has no grpinfo.txt ) |
| TP-CMP-020 | gen_cmp_zca | gen_test_cmp_zca | 3 | FAIL | yes | 12 | 12 | - | - | NOT-RUN-CLEAN (fcov expectation unverifiable: per-test urg report has no grpinfo.txt ) |
| TP-CMP-021 | gen_cmp_zca | gen_test_cmp_zca | 3 | FAIL | yes | 36 | 36 | - | - | NOT-RUN-CLEAN (fcov expectation unverifiable: per-test urg report has no grpinfo.txt ) |
| TP-CMP-023 | gen_cmp_zca | gen_test_cmp_zca | 3 | FAIL | yes | 30 | 30 | - | - | NOT-RUN-CLEAN (fcov expectation unverifiable: per-test urg report has no grpinfo.txt ) |
| TP-CMP-024 | gen_cmp_zca | gen_test_cmp_zca | 3 | FAIL | yes | 26 | 26 | - | - | NOT-RUN-CLEAN (fcov expectation unverifiable: per-test urg report has no grpinfo.txt ) |
| TP-CMP-026 | gen_cmp_zca | gen_test_cmp_zca | 3 | FAIL | yes | 11 | 11 | - | - | NOT-RUN-CLEAN (fcov expectation unverifiable: per-test urg report has no grpinfo.txt ) |
| TP-CMP-028 | gen_cmp_zca | gen_test_cmp_zca | 3 | FAIL | yes | 6 | 6 | - | - | NOT-RUN-CLEAN (fcov expectation unverifiable: per-test urg report has no grpinfo.txt ) |
| TP-CMP-030 | gen_cmp_zca | gen_test_cmp_zca | 3 | FAIL | yes | 11 | 11 | - | - | NOT-RUN-CLEAN (fcov expectation unverifiable: per-test urg report has no grpinfo.txt ) |
| TP-CMP-032 | gen_cmp_zca | gen_test_cmp_zca | 3 | FAIL | yes | 5 | 5 | - | - | NOT-RUN-CLEAN (fcov expectation unverifiable: per-test urg report has no grpinfo.txt ) |
| TP-CMP-033 | gen_cmp_zca | gen_test_cmp_zca | 3 | FAIL | yes | 12 | 12 | - | - | NOT-RUN-CLEAN (fcov expectation unverifiable: per-test urg report has no grpinfo.txt ) |
| TP-CMP-034 | gen_cmp_zcb | gen_test_cmp_zcb | 3 | FAIL | yes | 45 | 45 | - | - | NOT-RUN-CLEAN (fcov expectation unverifiable: per-test urg report has no grpinfo.txt ) |
| TP-CMP-036 | gen_cmp_zcb | gen_test_cmp_zcb | 3 | FAIL | yes | 41 | 41 | - | - | NOT-RUN-CLEAN (fcov expectation unverifiable: per-test urg report has no grpinfo.txt ) |
| TP-CMP-038 | gen_cmp_zcb | gen_test_cmp_zcb | 3 | FAIL | yes | 24 | 24 | - | - | NOT-RUN-CLEAN (fcov expectation unverifiable: per-test urg report has no grpinfo.txt ) |
| TP-CMP-039 | gen_cmp_zcmp_basic | gen_test_cmp_zcmp_basic | 3 | FAIL | yes | 72 | 72 | - | - | NOT-RUN-CLEAN (fcov expectation unverifiable: per-test urg report has no grpinfo.txt ) |
| TP-CMP-040 | gen_cmp_zcmp_basic | gen_test_cmp_zcmp_basic | 3 | FAIL | yes | 5 | 5 | - | - | NOT-RUN-CLEAN (fcov expectation unverifiable: per-test urg report has no grpinfo.txt ) |
| TP-CMP-041 | gen_cmp_zcmp_basic | gen_test_cmp_zcmp_basic | 3 | FAIL | yes | 5 | 5 | - | - | NOT-RUN-CLEAN (fcov expectation unverifiable: per-test urg report has no grpinfo.txt ) |
| TP-CMP-042 | gen_cmp_zcmp_basic | gen_test_cmp_zcmp_basic | 3 | FAIL | yes | 10 | 10 | - | - | NOT-RUN-CLEAN (fcov expectation unverifiable: per-test urg report has no grpinfo.txt ) |
| TP-CMP-043 | gen_cmp_zcmp_basic | gen_test_cmp_zcmp_basic | 3 | FAIL | yes | 11 | 11 | - | - | NOT-RUN-CLEAN (fcov expectation unverifiable: per-test urg report has no grpinfo.txt ) |
| TP-CMP-045 | gen_cmp_zcmp_basic | gen_test_cmp_zcmp_basic | 3 | FAIL | yes | 67 | 67 | - | - | NOT-RUN-CLEAN (fcov expectation unverifiable: per-test urg report has no grpinfo.txt ) |
| TP-CMP-046 | gen_cmp_zcmp_basic | gen_test_cmp_zcmp_basic | 3 | FAIL | yes | 5 | 5 | - | - | NOT-RUN-CLEAN (fcov expectation unverifiable: per-test urg report has no grpinfo.txt ) |
| TP-CMP-047 | gen_cmp_zcmp_basic | gen_test_cmp_zcmp_basic | 3 | FAIL | yes | 71 | 71 | - | - | NOT-RUN-CLEAN (fcov expectation unverifiable: per-test urg report has no grpinfo.txt ) |
| TP-CMP-048 | gen_cmp_zcmp_basic | gen_test_cmp_zcmp_basic | 3 | FAIL | yes | 71 | 71 | - | - | NOT-RUN-CLEAN (fcov expectation unverifiable: per-test urg report has no grpinfo.txt ) |
| TP-CMP-049 | gen_cmp_zcmp_basic | gen_test_cmp_zcmp_basic | 3 | FAIL | yes | 8 | 8 | - | - | NOT-RUN-CLEAN (fcov expectation unverifiable: per-test urg report has no grpinfo.txt ) |
| TP-CMP-050 | gen_cmp_zcmp_basic | gen_test_cmp_zcmp_basic | 3 | FAIL | yes | 76 | 76 | - | - | NOT-RUN-CLEAN (fcov expectation unverifiable: per-test urg report has no grpinfo.txt ) |
| TP-CMP-052 | gen_cmp_zcmp_basic | gen_test_cmp_zcmp_basic | 3 | FAIL | yes | 81 | 81 | - | - | NOT-RUN-CLEAN (fcov expectation unverifiable: per-test urg report has no grpinfo.txt ) |
| TP-CMP-053 | gen_cmp_zcmp_basic | gen_test_cmp_zcmp_basic | 3 | FAIL | yes | 8 | 8 | - | - | NOT-RUN-CLEAN (fcov expectation unverifiable: per-test urg report has no grpinfo.txt ) |
| TP-CMP-055 | gen_cmp_zcmp_basic | gen_test_cmp_zcmp_basic | 3 | FAIL | yes | 3 | 3 | - | - | NOT-RUN-CLEAN (fcov expectation unverifiable: per-test urg report has no grpinfo.txt ) |
| TP-CMP-066 | gen_cmp_zcmp_basic | gen_test_cmp_zcmp_basic | 3 | FAIL | yes | 36 | 36 | - | - | NOT-RUN-CLEAN (fcov expectation unverifiable: per-test urg report has no grpinfo.txt ) |
| TP-CMP-068 | gen_cmp_zcmp_basic | gen_test_cmp_zcmp_basic | 3 | FAIL | none | 10 | 10 | - | - | NOT-RUN-CLEAN (fcov expectation unverifiable: per-test urg report has no grpinfo.txt ) |
| TP-CMP-069 | gen_cmp_zcmp_basic | gen_test_cmp_zcmp_basic | 3 | FAIL | yes | 39 | 39 | - | - | NOT-RUN-CLEAN (fcov expectation unverifiable: per-test urg report has no grpinfo.txt ) |
| TP-CMP-073 | gen_cmp_zcmp_basic | gen_test_cmp_zcmp_basic | 3 | FAIL | yes | 22 | 22 | - | - | NOT-RUN-CLEAN (fcov expectation unverifiable: per-test urg report has no grpinfo.txt ) |
| TP-CSR-001 | gen_csr_access | gen_test_csr_access | 3 | FAIL | yes | 29 | 29 | - | - | NOT-RUN-CLEAN (fcov expectation unverifiable: per-test urg report has no grpinfo.txt ) |
| TP-CSR-002 | gen_csr_access | gen_test_csr_access | 3 | FAIL | yes | 21 | 21 | - | - | NOT-RUN-CLEAN (fcov expectation unverifiable: per-test urg report has no grpinfo.txt ) |
| TP-CSR-003 | gen_csr_access | gen_test_csr_access | 3 | FAIL | yes | 19 | 19 | - | - | NOT-RUN-CLEAN (fcov expectation unverifiable: per-test urg report has no grpinfo.txt ) |
| TP-CSR-004 | gen_csr_access | gen_test_csr_access | 3 | FAIL | yes | 15 | 15 | - | - | NOT-RUN-CLEAN (fcov expectation unverifiable: per-test urg report has no grpinfo.txt ) |
| TP-CSR-005 | gen_csr_access | gen_test_csr_access | 3 | FAIL | none | 3 | 3 | - | - | NOT-RUN-CLEAN (fcov expectation unverifiable: per-test urg report has no grpinfo.txt ) |
| TP-CSR-012 | gen_csr_access | gen_test_csr_access | 3 | FAIL | yes | 21 | 21 | - | - | NOT-RUN-CLEAN (fcov expectation unverifiable: per-test urg report has no grpinfo.txt ) |
| TP-CSR-023 | gen_csr_trap_setup | gen_test_csr_trap_setup | 3 | FAIL | yes | 36 | 36 | - | - | NOT-RUN-CLEAN (fcov expectation unverifiable: per-test urg report has no grpinfo.txt ) |
| TP-CSR-024 | gen_csr_trap_setup | gen_test_csr_trap_setup | 3 | FAIL | yes | 24 | 24 | - | - | NOT-RUN-CLEAN (fcov expectation unverifiable: per-test urg report has no grpinfo.txt ) |
| TP-CSR-025 | gen_csr_trap_setup | gen_test_csr_trap_setup | 3 | FAIL | yes | 6 | 6 | - | - | NOT-RUN-CLEAN (fcov expectation unverifiable: per-test urg report has no grpinfo.txt ) |
| TP-CSR-027 | gen_csr_trap_setup | gen_test_csr_trap_setup | 3 | FAIL | yes | 22 | 22 | - | - | NOT-RUN-CLEAN (fcov expectation unverifiable: per-test urg report has no grpinfo.txt ) |
| TP-CSR-028 | gen_csr_trap_setup | gen_test_csr_trap_setup | 3 | FAIL | yes | 34 | 34 | - | - | NOT-RUN-CLEAN (fcov expectation unverifiable: per-test urg report has no grpinfo.txt ) |
| TP-CSR-029 | gen_csr_trap_setup | gen_test_csr_trap_setup | 3 | FAIL | yes | 37 | 37 | - | - | NOT-RUN-CLEAN (fcov expectation unverifiable: per-test urg report has no grpinfo.txt ) |
| TP-CSR-030 | gen_csr_trap_setup | gen_test_csr_trap_setup | 3 | FAIL | yes | 8 | 8 | - | - | NOT-RUN-CLEAN (fcov expectation unverifiable: per-test urg report has no grpinfo.txt ) |
| TP-CSR-035 | gen_csr_trap_setup | gen_test_csr_trap_setup | 3 | FAIL | yes | 37 | 37 | - | - | NOT-RUN-CLEAN (fcov expectation unverifiable: per-test urg report has no grpinfo.txt ) |
| TP-CSR-036 | gen_csr_trap_setup | gen_test_csr_trap_setup | 3 | FAIL | yes | 23 | 23 | - | - | NOT-RUN-CLEAN (fcov expectation unverifiable: per-test urg report has no grpinfo.txt ) |
| TP-CSR-037 | gen_csr_reset | gen_test_csr_reset | 3 | FAIL | no | 12 | 12 | - | - | NOT-RUN-CLEAN (cocotb_summary at sim_stdout.log:112; fcov expectation unverifiable: per-test urg report has no grpinfo.txt ) |
| TP-CSR-105 | gen_csr_reset | gen_test_csr_reset | 3 | FAIL | no | 19 | 19 | - | - | NOT-RUN-CLEAN (cocotb_summary at sim_stdout.log:112; fcov expectation unverifiable: per-test urg report has no grpinfo.txt ) |
| TP-CSR-106 | gen_csr_reset | gen_test_csr_reset | 3 | FAIL | no | 5 | 5 | - | - | NOT-RUN-CLEAN (cocotb_summary at sim_stdout.log:112; fcov expectation unverifiable: per-test urg report has no grpinfo.txt ) |
| TP-CSR-107 | gen_csr_reset | gen_test_csr_reset | 3 | FAIL | no | 15 | 15 | - | - | NOT-RUN-CLEAN (cocotb_summary at sim_stdout.log:112; fcov expectation unverifiable: per-test urg report has no grpinfo.txt ) |
| TP-CSR-108 | gen_csr_reset | gen_test_csr_reset | 3 | FAIL | no | 20 | 20 | - | - | NOT-RUN-CLEAN (cocotb_summary at sim_stdout.log:112; fcov expectation unverifiable: per-test urg report has no grpinfo.txt ) |
| TP-CSR-109 | gen_csr_reset | gen_test_csr_reset | 3 | FAIL | no | 13 | 13 | - | - | NOT-RUN-CLEAN (cocotb_summary at sim_stdout.log:112; fcov expectation unverifiable: per-test urg report has no grpinfo.txt ) |
| TP-ISA-001 | gen_isa_alu | gen_test_isa_alu | 3 | FAIL | yes | 130 | 130 | - | - | NOT-RUN-CLEAN (fcov expectation unverifiable: per-test urg report has no grpinfo.txt ) |
| TP-ISA-002 | gen_isa_alu | gen_test_isa_alu | 3 | FAIL | yes | 4 | 4 | - | - | NOT-RUN-CLEAN (fcov expectation unverifiable: per-test urg report has no grpinfo.txt ) |
| TP-ISA-003 | gen_isa_alu | gen_test_isa_alu | 3 | FAIL | yes | 15 | 15 | - | - | NOT-RUN-CLEAN (fcov expectation unverifiable: per-test urg report has no grpinfo.txt ) |
| TP-ISA-004 | gen_isa_alu | gen_test_isa_alu | 3 | FAIL | yes | 30 | 30 | - | - | NOT-RUN-CLEAN (fcov expectation unverifiable: per-test urg report has no grpinfo.txt ) |
| TP-ISA-005 | gen_isa_alu | gen_test_isa_alu | 3 | FAIL | yes | 26 | 26 | - | - | NOT-RUN-CLEAN (fcov expectation unverifiable: per-test urg report has no grpinfo.txt ) |
| TP-ISA-006 | gen_isa_alu | gen_test_isa_alu | 3 | FAIL | yes | 13 | 13 | - | - | NOT-RUN-CLEAN (fcov expectation unverifiable: per-test urg report has no grpinfo.txt ) |
| TP-ISA-007 | gen_isa_alu | gen_test_isa_alu | 3 | FAIL | yes | 224 | 224 | - | - | NOT-RUN-CLEAN (fcov expectation unverifiable: per-test urg report has no grpinfo.txt ) |
| TP-ISA-008 | gen_isa_alu | gen_test_isa_alu | 3 | FAIL | yes | 15 | 15 | - | - | NOT-RUN-CLEAN (fcov expectation unverifiable: per-test urg report has no grpinfo.txt ) |
| TP-ISA-009 | gen_isa_alu | gen_test_isa_alu | 3 | FAIL | yes | 127 | 127 | - | - | NOT-RUN-CLEAN (fcov expectation unverifiable: per-test urg report has no grpinfo.txt ) |
| TP-ISA-010 | gen_isa_shift | gen_test_isa_shift | 3 | FAIL | yes | 57 | 57 | - | - | NOT-RUN-CLEAN (fcov expectation unverifiable: per-test urg report has no grpinfo.txt ) |
| TP-ISA-011 | gen_isa_shift | gen_test_isa_shift | 3 | FAIL | yes | 22 | 22 | - | - | NOT-RUN-CLEAN (fcov expectation unverifiable: per-test urg report has no grpinfo.txt ) |
| TP-ISA-013 | gen_isa_shift | gen_test_isa_shift | 3 | FAIL | yes | 39 | 39 | - | - | NOT-RUN-CLEAN (fcov expectation unverifiable: per-test urg report has no grpinfo.txt ) |
| TP-ISA-014 | gen_isa_shift | gen_test_isa_shift | 3 | FAIL | yes | 27 | 27 | - | - | NOT-RUN-CLEAN (fcov expectation unverifiable: per-test urg report has no grpinfo.txt ) |
| TP-ISA-015 | gen_isa_cti | gen_test_isa_cti | 3 | FAIL | yes | 22 | 22 | - | - | NOT-RUN-CLEAN (fcov expectation unverifiable: per-test urg report has no grpinfo.txt ) |
| TP-ISA-016 | gen_isa_cti | gen_test_isa_cti | 3 | FAIL | none | 40 | 40 | - | - | NOT-RUN-CLEAN (fcov expectation unverifiable: per-test urg report has no grpinfo.txt ) |
| TP-ISA-017 | gen_isa_cti | gen_test_isa_cti | 3 | FAIL | yes | 17 | 17 | - | - | NOT-RUN-CLEAN (fcov expectation unverifiable: per-test urg report has no grpinfo.txt ) |
| TP-ISA-018 | gen_isa_cti | gen_test_isa_cti | 3 | FAIL | yes | 18 | 18 | - | - | NOT-RUN-CLEAN (fcov expectation unverifiable: per-test urg report has no grpinfo.txt ) |
| TP-ISA-019 | gen_isa_cti | gen_test_isa_cti | 3 | FAIL | yes | 10 | 10 | - | - | NOT-RUN-CLEAN (fcov expectation unverifiable: per-test urg report has no grpinfo.txt ) |
| TP-ISA-020 | gen_isa_cti | gen_test_isa_cti | 3 | FAIL | yes | 13 | 13 | - | - | NOT-RUN-CLEAN (fcov expectation unverifiable: per-test urg report has no grpinfo.txt ) |
| TP-ISA-022 | gen_isa_cti | gen_test_isa_cti | 3 | FAIL | none | 15 | 15 | - | - | NOT-RUN-CLEAN (fcov expectation unverifiable: per-test urg report has no grpinfo.txt ) |
| TP-ISA-023 | gen_isa_cti | gen_test_isa_cti | 3 | FAIL | yes | 122 | 122 | - | - | NOT-RUN-CLEAN (fcov expectation unverifiable: per-test urg report has no grpinfo.txt ) |
| TP-ISA-024 | gen_isa_cti | gen_test_isa_cti | 3 | FAIL | none | 9 | 9 | - | - | NOT-RUN-CLEAN (fcov expectation unverifiable: per-test urg report has no grpinfo.txt ) |
| TP-ISA-026 | gen_isa_cti | gen_test_isa_cti | 3 | FAIL | none | 70 | 70 | - | - | NOT-RUN-CLEAN (fcov expectation unverifiable: per-test urg report has no grpinfo.txt ) |
| TP-ISA-027 | gen_isa_cti | gen_test_isa_cti | 3 | FAIL | yes | 74 | 74 | - | - | NOT-RUN-CLEAN (fcov expectation unverifiable: per-test urg report has no grpinfo.txt ) |
| TP-ISA-052 | gen_isa_alu | gen_test_isa_alu | 3 | FAIL | yes | 60 | 60 | - | - | NOT-RUN-CLEAN (fcov expectation unverifiable: per-test urg report has no grpinfo.txt ) |
| TP-ISA-053 | gen_isa_cti | gen_test_isa_cti | 3 | FAIL | yes | 30 | 30 | - | - | NOT-RUN-CLEAN (fcov expectation unverifiable: per-test urg report has no grpinfo.txt ) |
| TP-MUL-001 | gen_mul_mul | gen_test_mul_mul | 3 | FAIL | yes | 63 | 63 | - | - | NOT-RUN-CLEAN (fcov expectation unverifiable: per-test urg report has no grpinfo.txt ) |
| TP-MUL-002 | gen_mul_mul | gen_test_mul_mul | 3 | FAIL | yes | 268 | 268 | - | - | NOT-RUN-CLEAN (fcov expectation unverifiable: per-test urg report has no grpinfo.txt ) |
| TP-MUL-003 | gen_mul_mul | gen_test_mul_mul | 3 | FAIL | none | 6 | 6 | - | - | NOT-RUN-CLEAN (fcov expectation unverifiable: per-test urg report has no grpinfo.txt ) |
| TP-MUL-004 | gen_mul_mul | gen_test_mul_mul | 3 | FAIL | yes | 291 | 291 | - | - | NOT-RUN-CLEAN (fcov expectation unverifiable: per-test urg report has no grpinfo.txt ) |
| TP-MUL-005 | gen_mul_mul | gen_test_mul_mul | 3 | FAIL | yes | 6 | 6 | - | - | NOT-RUN-CLEAN (fcov expectation unverifiable: per-test urg report has no grpinfo.txt ) |
| TP-MUL-006 | gen_mul_mul | gen_test_mul_mul | 3 | FAIL | yes | 267 | 267 | - | - | NOT-RUN-CLEAN (fcov expectation unverifiable: per-test urg report has no grpinfo.txt ) |
| TP-MUL-007 | gen_mul_mul | gen_test_mul_mul | 3 | FAIL | yes | 6 | 6 | - | - | NOT-RUN-CLEAN (fcov expectation unverifiable: per-test urg report has no grpinfo.txt ) |
| TP-MUL-008 | gen_mul_mul | gen_test_mul_mul | 3 | FAIL | yes | 290 | 290 | - | - | NOT-RUN-CLEAN (fcov expectation unverifiable: per-test urg report has no grpinfo.txt ) |
| TP-MUL-012 | gen_mul_div | gen_test_mul_div | 3 | FAIL | none | 33 | 33 | - | - | NOT-RUN-CLEAN (fcov expectation unverifiable: per-test urg report has no grpinfo.txt ) |
| TP-MUL-013 | gen_mul_div | gen_test_mul_div | 3 | FAIL | yes | 39 | 39 | - | - | NOT-RUN-CLEAN (fcov expectation unverifiable: per-test urg report has no grpinfo.txt ) |
| TP-MUL-014 | gen_mul_div | gen_test_mul_div | 3 | FAIL | yes | 27 | 27 | - | - | NOT-RUN-CLEAN (fcov expectation unverifiable: per-test urg report has no grpinfo.txt ) |
| TP-MUL-015 | gen_mul_div | gen_test_mul_div | 3 | FAIL | yes | 39 | 39 | - | - | NOT-RUN-CLEAN (fcov expectation unverifiable: per-test urg report has no grpinfo.txt ) |
| TP-MUL-016 | gen_mul_div | gen_test_mul_div | 3 | FAIL | yes | 79 | 79 | - | - | NOT-RUN-CLEAN (fcov expectation unverifiable: per-test urg report has no grpinfo.txt ) |
| TP-MUL-017 | gen_mul_div | gen_test_mul_div | 3 | FAIL | yes | 57 | 57 | - | - | NOT-RUN-CLEAN (fcov expectation unverifiable: per-test urg report has no grpinfo.txt ) |
| TP-MUL-018 | gen_mul_div | gen_test_mul_div | 3 | FAIL | yes | 11 | 11 | - | - | NOT-RUN-CLEAN (fcov expectation unverifiable: per-test urg report has no grpinfo.txt ) |
| TP-MUL-019 | gen_mul_div | gen_test_mul_div | 3 | FAIL | yes | 27 | 27 | - | - | NOT-RUN-CLEAN (fcov expectation unverifiable: per-test urg report has no grpinfo.txt ) |
| TP-MUL-020 | gen_mul_div | gen_test_mul_div | 3 | FAIL | yes | 57 | 57 | - | - | NOT-RUN-CLEAN (fcov expectation unverifiable: per-test urg report has no grpinfo.txt ) |
| TP-MUL-021 | gen_mul_div | gen_test_mul_div | 3 | FAIL | yes | 26 | 26 | - | - | NOT-RUN-CLEAN (fcov expectation unverifiable: per-test urg report has no grpinfo.txt ) |
| TP-MUL-022 | gen_mul_div | gen_test_mul_div | 3 | FAIL | none | 23 | 23 | - | - | NOT-RUN-CLEAN (fcov expectation unverifiable: per-test urg report has no grpinfo.txt ) |
| TP-MUL-026 | gen_mul_div | gen_test_mul_div | 3 | FAIL | yes | 44 | 44 | - | - | NOT-RUN-CLEAN (fcov expectation unverifiable: per-test urg report has no grpinfo.txt ) |
| TP-MUL-027 | gen_mul_mul | gen_test_mul_mul | 3 | FAIL | yes | 4 | 4 | - | - | NOT-RUN-CLEAN (fcov expectation unverifiable: per-test urg report has no grpinfo.txt ) |
| TP-PMP-001 | gen_pmp_csr_warl | gen_test_pmp_csr_warl | 3 | FAIL | yes | 113 | 113 | - | - | NOT-RUN-CLEAN (fcov expectation unverifiable: per-test urg report has no grpinfo.txt ) |
| TP-PMP-002 | gen_pmp_csr_warl | gen_test_pmp_csr_warl | 3 | FAIL | yes | 44 | 44 | - | - | NOT-RUN-CLEAN (fcov expectation unverifiable: per-test urg report has no grpinfo.txt ) |
| TP-PMP-003 | gen_pmp_csr_warl | gen_test_pmp_csr_warl | 3 | FAIL | yes | 4 | 4 | - | - | NOT-RUN-CLEAN (fcov expectation unverifiable: per-test urg report has no grpinfo.txt ) |
| TP-PMP-004 | gen_pmp_csr_warl | gen_test_pmp_csr_warl | 3 | FAIL | yes | 7 | 7 | - | - | NOT-RUN-CLEAN (fcov expectation unverifiable: per-test urg report has no grpinfo.txt ) |
| TP-PMP-005 | gen_pmp_csr_warl | gen_test_pmp_csr_warl | 3 | FAIL | yes | 3 | 3 | - | - | NOT-RUN-CLEAN (fcov expectation unverifiable: per-test urg report has no grpinfo.txt ) |
| TP-PMP-006 | gen_pmp_csr_warl | gen_test_pmp_csr_warl | 3 | FAIL | yes | 7 | 7 | - | - | NOT-RUN-CLEAN (fcov expectation unverifiable: per-test urg report has no grpinfo.txt ) |
| TP-PMP-007 | gen_pmp_csr_warl | gen_test_pmp_csr_warl | 3 | FAIL | yes | 91 | 91 | - | - | NOT-RUN-CLEAN (fcov expectation unverifiable: per-test urg report has no grpinfo.txt ) |
| TP-PMP-008 | gen_pmp_csr_warl | gen_test_pmp_csr_warl | 3 | FAIL | yes | 11 | 11 | - | - | NOT-RUN-CLEAN (fcov expectation unverifiable: per-test urg report has no grpinfo.txt ) |
| TP-RST-001 | gen_rst_boot | gen_test_rst_boot | 3 | FAIL | none | 3 | 3 | - | - | NOT-RUN-CLEAN (fcov expectation unverifiable: per-test urg report has no grpinfo.txt ) |
| TP-RST-002 | gen_rst_boot | gen_test_rst_boot | 3 | FAIL | none | 10 | 10 | - | - | NOT-RUN-CLEAN (fcov expectation unverifiable: per-test urg report has no grpinfo.txt ) |
| TP-RST-003 | gen_rst_boot | gen_test_rst_boot | 3 | FAIL | yes | 3 | 3 | - | - | NOT-RUN-CLEAN (fcov expectation unverifiable: per-test urg report has no grpinfo.txt ) |
| TP-RST-004 | gen_rst_boot | gen_test_rst_boot | 3 | FAIL | none | 5 | 5 | - | - | NOT-RUN-CLEAN (fcov expectation unverifiable: per-test urg report has no grpinfo.txt ) |
| TP-RST-005 | gen_rst_boot | gen_test_rst_boot | 3 | FAIL | none | 3 | 3 | - | - | NOT-RUN-CLEAN (fcov expectation unverifiable: per-test urg report has no grpinfo.txt ) |
| TP-RST-006 | gen_rst_boot | gen_test_rst_boot | 3 | FAIL | yes | 3 | 3 | - | - | NOT-RUN-CLEAN (fcov expectation unverifiable: per-test urg report has no grpinfo.txt ) |
| TP-RST-007 | gen_rst_boot | gen_test_rst_boot | 3 | FAIL | yes | 3 | 3 | - | - | NOT-RUN-CLEAN (fcov expectation unverifiable: per-test urg report has no grpinfo.txt ) |
| TP-RST-008 | gen_rst_boot | gen_test_rst_boot | 3 | FAIL | none | 3 | 3 | - | - | NOT-RUN-CLEAN (fcov expectation unverifiable: per-test urg report has no grpinfo.txt ) |
| TP-RST-027 | gen_rst_boot | gen_test_rst_boot | 3 | FAIL | none | 1 | 1 | - | - | NOT-RUN-CLEAN (fcov expectation unverifiable: per-test urg report has no grpinfo.txt ) |
| TP-RVFI-036 | gen_rst_boot | gen_test_rst_boot | 3 | FAIL | none | 2 | 2 | - | - | NOT-RUN-CLEAN (fcov expectation unverifiable: per-test urg report has no grpinfo.txt ) |
| TP-SEC-031 | gen_rst_boot | gen_test_rst_boot | 3 | FAIL | none | 10 | 10 | - | - | NOT-RUN-CLEAN (fcov expectation unverifiable: per-test urg report has no grpinfo.txt ) |
