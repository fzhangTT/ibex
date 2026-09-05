## 1.7 Round-1 credit, the first measured coverage run (the flow indexes it as measured round 0: evidence gen_round_0, regression tag round_1) (generated from the regression manifest and sim logs; 185 items in 17 hosted groups)

RECORD NOTE: Team round 1 = flow measured round 0 (evidence dv/auto_dv/evidence/gen_round_0, regression tag round_1), regenerated inside a detached archive of 4a00702, the pinned commit of the round; supersedes nothing in dv/auto_dv/evidence/gen_round0_credit/, which stays as committed: that directory holds the round-0 PROBE record of a different event and is not regenerated. Provenance the invoker asserts and the tool does not check; the inputs digest below is the checked part.

Invocation, byte for byte from the commit that carries these inputs (copy the whole line below; a quoted heading or note may contain semicolons):
python3 dv/auto_dv/tools/gen_round_credit.py --regress-manifest /proj_soc/user_dev/fzhang/ibex_dv_out/regress_round_1/manifest.yaml --plan-sha regen-round1-at-4a00702 --round 0 --heading-id round1-measured --csv dv/auto_dv/evidence/gen_round1_credit/gen_round1_credit.csv --md dv/auto_dv/evidence/gen_round1_credit/gen_round1_credit.md --note 'Team round 1 = flow measured round 0 (evidence dv/auto_dv/evidence/gen_round_0, regression tag round_1), regenerated inside a detached archive of 4a00702, the pinned commit of the round; supersedes nothing in dv/auto_dv/evidence/gen_round0_credit/, which stays as committed: that directory holds the round-0 PROBE record of a different event and is not regenerated. Provenance the invoker asserts and the tool does not check; the inputs digest below is the checked part.'

Regression manifest sha256 c8a2cd5bec60757d9feb4ff8546ddd5618074a0db9beedb28d428f00d05d15bf; plan inputs read (item headers with group / tier / expected, hold sections, carve-out sections and rows with item / tag / until / reason, gen_trace_tp_bin.csv, gen_trace_witness_ids.csv) digest 282949a36e21; carve-out rows read 2 (0 hosted in this round; the UNCREDITED / COUNTED-ONLY columns count carved items that would otherwise have credited, a carved item that is UNHIT or NOT-RUN-CLEAN keeps that state and shows its tag in the Carve-out column); landing label regen-round1-at-4a00702 (the --plan-sha argument, a label only, not the commit whose plan was read). Regression /proj_soc/user_dev/fzhang/ibex_dv_out/regress_round_1: status done, source {'mode': 'head', 'source_root': '/proj_soc/user_dev/fzhang/ibex_dv_mirror_head/4a0070285557', 'head_sha': '4a0070285557a2a7dfb50cea9390597143b984b0', 'worktree_dirty': None}, git 4a0070285557a2a7dfb50cea9390597143b984b0; 53 runs: pass 53, fail 0, xfail 0, red_ok 0, timeout 0, not_run 0; fcov checks {'checked': 36, 'pass': 36, 'unmet': 0, 'unverifiable': 0}; covergroups_exist True; clean regression (gen_round.py hard rule): yes.

| Area | Items hosted | CREDITED | UNCREDITED | COUNTED-ONLY | HELD | UNHIT | FIRE-FAIL | NOT-FIRED | NOT-RUN-CLEAN | UNVERIFIED |
|---|---|---|---|---|---|---|---|---|---|---|
| BIT | 33 | 5 | 0 | 0 | 0 | 13 | 0 | 1 | 0 | 14 |
| CMP | 42 | 27 | 0 | 0 | 0 | 14 | 0 | 1 | 0 | 0 |
| CSR | 21 | 4 | 0 | 0 | 0 | 10 | 0 | 1 | 0 | 6 |
| ISA | 26 | 16 | 0 | 0 | 0 | 6 | 0 | 4 | 0 | 0 |
| MUL | 21 | 14 | 0 | 0 | 0 | 4 | 0 | 3 | 0 | 0 |
| PMP | 31 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 31 |
| RST | 9 | 0 | 0 | 0 | 0 | 3 | 0 | 6 | 0 | 0 |
| RVFI | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 |
| SEC | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 |

Total: 185 items hosted; credited 66; uncredited (carve-out) 0; counted-only 0; held 0; unhit 50; fire-fail 0; not fired 18; not run clean 0; unverified 51.
Witness bins of hosted items: 2 (unscored until T-179; listed, never credited).

Per test (every run of the regression, red fixtures included; the item table below excludes red fixtures, which host no items):

| Test | Seeds | Verdicts | Distinct reasons |
|---|---|---|---|
| gen_boot_zc | 1 | PASS | no collected failure mechanism; end marker and config banner |
| gen_test_bit_draft | 3 | PASS | no collected failure mechanism; end marker and config banner |
| gen_test_bit_ratified | 3 | PASS | no collected failure mechanism; end marker and config banner |
| gen_test_cmp_zca | 3 | PASS | no collected failure mechanism; end marker and config banner |
| gen_test_cmp_zcb | 3 | PASS | no collected failure mechanism; end marker and config banner |
| gen_test_cmp_zcmp_basic | 3 | PASS | no collected failure mechanism; end marker and config banner |
| gen_test_csr_access | 3 | PASS | no collected failure mechanism; end marker and config banner |
| gen_test_csr_reset | 3 | PASS | no collected failure mechanism; end marker and config banner |
| gen_test_csr_trap_setup | 3 | PASS | no collected failure mechanism; end marker and config banner |
| gen_test_isa_alu | 3 | PASS | no collected failure mechanism; end marker and config banner |
| gen_test_isa_cti | 3 | PASS | no collected failure mechanism; end marker and config banner |
| gen_test_isa_shift | 3 | PASS | no collected failure mechanism; end marker and config banner |
| gen_test_mul_div | 3 | PASS | no collected failure mechanism; end marker and config banner |
| gen_test_mul_mul | 3 | PASS | no collected failure mechanism; end marker and config banner |
| gen_test_pmp_csr_warl | 3 | PASS | no collected failure mechanism; end marker and config banner |
| gen_test_pmp_lock | 3 | PASS | no collected failure mechanism; end marker and config banner |
| gen_test_pmp_mseccfg | 3 | PASS | no collected failure mechanism; end marker and config banner |
| gen_test_rst_boot | 3 | PASS | no collected failure mechanism; end marker and config banner |
| gen_ut_lockstep | 1 | PASS | no collected failure mechanism; end marker and config banner |

| Item | Group | Test | Seeds | Verdicts | Fired | Bins | Unhit | Hold | Carve-out | Status |
|---|---|---|---|---|---|---|---|---|---|---|
| TP-BIT-001 | gen_bit_ratified | gen_test_bit_ratified | 3 | PASS | none | 59 | 59 | - | - | NOT-FIRED (no fire line: not built or not reached) |
| TP-BIT-002 | gen_bit_ratified | gen_test_bit_ratified | 3 | PASS | yes | 71 | 2 | - | - | UNHIT (2 of 71 bins) |
| TP-BIT-003 | gen_bit_ratified | gen_test_bit_ratified | 3 | PASS | yes | 99 | 24 | - | - | UNHIT (24 of 99 bins) |
| TP-BIT-004 | gen_bit_ratified | gen_test_bit_ratified | 3 | PASS | yes | 73 | 3 | - | - | UNHIT (3 of 73 bins) |
| TP-BIT-005 | gen_bit_ratified | gen_test_bit_ratified | 3 | PASS | yes | 51 | 0 | - | - | CREDITED |
| TP-BIT-006 | gen_bit_ratified | gen_test_bit_ratified | 3 | PASS | yes | 145 | 0 | - | - | CREDITED |
| TP-BIT-007 | gen_bit_ratified | gen_test_bit_ratified | 3 | PASS | yes | 109 | 3 | - | - | UNHIT (3 of 109 bins) |
| TP-BIT-008 | gen_bit_ratified | gen_test_bit_ratified | 3 | PASS | yes | 65 | 3 | - | - | UNHIT (3 of 65 bins) |
| TP-BIT-009 | gen_bit_ratified | gen_test_bit_ratified | 3 | PASS | yes | 6 | 0 | - | - | CREDITED |
| TP-BIT-010 | gen_bit_ratified | gen_test_bit_ratified | 3 | PASS | yes | 22 | 1 | - | - | UNHIT (1 of 22 bins) |
| TP-BIT-011 | gen_bit_draft | gen_test_bit_draft | 3 | PASS | none | 83 | 83 | - | - | UNVERIFIED (no fcov check with per-bin results in the round) |
| TP-BIT-014 | gen_bit_ratified | gen_test_bit_ratified | 3 | PASS | yes | 13 | 10 | - | - | UNHIT (10 of 13 bins) |
| TP-BIT-015 | gen_bit_ratified | gen_test_bit_ratified | 3 | PASS | yes | 3 | 3 | - | - | UNHIT (3 of 3 bins) |
| TP-BIT-016 | gen_bit_draft | gen_test_bit_draft | 3 | PASS | yes | 15 | 15 | - | - | UNVERIFIED (no fcov check with per-bin results in the round) |
| TP-BIT-017 | gen_bit_ratified | gen_test_bit_ratified | 3 | PASS | yes | 33 | 0 | - | - | CREDITED |
| TP-BIT-018 | gen_bit_ratified | gen_test_bit_ratified | 3 | PASS | yes | 48 | 0 | - | - | CREDITED |
| TP-BIT-019 | gen_bit_ratified | gen_test_bit_ratified | 3 | PASS | yes | 16 | 5 | - | - | UNHIT (5 of 16 bins) |
| TP-BIT-020 | gen_bit_ratified | gen_test_bit_ratified | 3 | PASS | yes | 43 | 37 | - | - | UNHIT (37 of 43 bins) |
| TP-BIT-021 | gen_bit_ratified | gen_test_bit_ratified | 3 | PASS | yes | 15 | 11 | - | - | UNHIT (11 of 15 bins) |
| TP-BIT-022 | gen_bit_draft | gen_test_bit_draft | 3 | PASS | none | 51 | 51 | - | - | UNVERIFIED (no fcov check with per-bin results in the round) |
| TP-BIT-023 | gen_bit_draft | gen_test_bit_draft | 3 | PASS | none | 27 | 27 | - | - | UNVERIFIED (no fcov check with per-bin results in the round) |
| TP-BIT-024 | gen_bit_draft | gen_test_bit_draft | 3 | PASS | none | 10 | 10 | - | - | UNVERIFIED (no fcov check with per-bin results in the round) |
| TP-BIT-025 | gen_bit_draft | gen_test_bit_draft | 3 | PASS | none | 43 | 43 | - | - | UNVERIFIED (no fcov check with per-bin results in the round) |
| TP-BIT-026 | gen_bit_draft | gen_test_bit_draft | 3 | PASS | none | 18 | 18 | - | - | UNVERIFIED (no fcov check with per-bin results in the round) |
| TP-BIT-027 | gen_bit_draft | gen_test_bit_draft | 3 | PASS | none | 46 | 46 | - | - | UNVERIFIED (no fcov check with per-bin results in the round) |
| TP-BIT-028 | gen_bit_draft | gen_test_bit_draft | 3 | PASS | none | 80 | 80 | - | - | UNVERIFIED (no fcov check with per-bin results in the round) |
| TP-BIT-029 | gen_bit_draft | gen_test_bit_draft | 3 | PASS | none | 11 | 11 | - | - | UNVERIFIED (no fcov check with per-bin results in the round) |
| TP-BIT-030 | gen_bit_draft | gen_test_bit_draft | 3 | PASS | none | 54 | 54 | - | - | UNVERIFIED (no fcov check with per-bin results in the round) |
| TP-BIT-031 | gen_bit_draft | gen_test_bit_draft | 3 | PASS | none | 10 | 10 | - | - | UNVERIFIED (no fcov check with per-bin results in the round) |
| TP-BIT-032 | gen_bit_draft | gen_test_bit_draft | 3 | PASS | none | 70 | 70 | - | - | UNVERIFIED (no fcov check with per-bin results in the round) |
| TP-BIT-033 | gen_bit_draft | gen_test_bit_draft | 3 | PASS | none | 5 | 5 | - | - | UNVERIFIED (no fcov check with per-bin results in the round) |
| TP-BIT-038 | gen_bit_ratified | gen_test_bit_ratified | 3 | PASS | yes | 196 | 99 | - | - | UNHIT (99 of 196 bins) |
| TP-BIT-040 | gen_bit_ratified | gen_test_bit_ratified | 3 | PASS | yes | 4 | 4 | - | - | UNHIT (4 of 4 bins) |
| TP-CMP-001 | gen_cmp_zca | gen_test_cmp_zca | 3 | PASS | yes | 137 | 21 | - | - | UNHIT (21 of 137 bins) |
| TP-CMP-002 | gen_cmp_zca | gen_test_cmp_zca | 3 | PASS | yes | 12 | 0 | - | - | CREDITED |
| TP-CMP-004 | gen_cmp_zca | gen_test_cmp_zca | 3 | PASS | yes | 5 | 0 | - | - | CREDITED |
| TP-CMP-005 | gen_cmp_zca | gen_test_cmp_zca | 3 | PASS | yes | 20 | 2 | - | - | UNHIT (2 of 20 bins) |
| TP-CMP-008 | gen_cmp_zca | gen_test_cmp_zca | 3 | PASS | yes | 13 | 0 | - | - | CREDITED |
| TP-CMP-010 | gen_cmp_zca | gen_test_cmp_zca | 3 | PASS | yes | 12 | 0 | - | - | CREDITED |
| TP-CMP-011 | gen_cmp_zca | gen_test_cmp_zca | 3 | PASS | yes | 7 | 1 | - | - | UNHIT (1 of 7 bins) |
| TP-CMP-012 | gen_cmp_zca | gen_test_cmp_zca | 3 | PASS | yes | 6 | 0 | - | - | CREDITED |
| TP-CMP-014 | gen_cmp_zca | gen_test_cmp_zca | 3 | PASS | yes | 6 | 0 | - | - | CREDITED |
| TP-CMP-016 | gen_cmp_zca | gen_test_cmp_zca | 3 | PASS | yes | 12 | 0 | - | - | CREDITED |
| TP-CMP-017 | gen_cmp_zca | gen_test_cmp_zca | 3 | PASS | yes | 12 | 1 | - | - | UNHIT (1 of 12 bins) |
| TP-CMP-018 | gen_cmp_zca | gen_test_cmp_zca | 3 | PASS | yes | 17 | 0 | - | - | CREDITED |
| TP-CMP-020 | gen_cmp_zca | gen_test_cmp_zca | 3 | PASS | yes | 12 | 0 | - | - | CREDITED |
| TP-CMP-021 | gen_cmp_zca | gen_test_cmp_zca | 3 | PASS | yes | 36 | 0 | - | - | CREDITED |
| TP-CMP-023 | gen_cmp_zca | gen_test_cmp_zca | 3 | PASS | yes | 30 | 0 | - | - | CREDITED |
| TP-CMP-024 | gen_cmp_zca | gen_test_cmp_zca | 3 | PASS | yes | 26 | 0 | - | - | CREDITED |
| TP-CMP-026 | gen_cmp_zca | gen_test_cmp_zca | 3 | PASS | yes | 11 | 0 | - | - | CREDITED |
| TP-CMP-028 | gen_cmp_zca | gen_test_cmp_zca | 3 | PASS | yes | 6 | 0 | - | - | CREDITED |
| TP-CMP-030 | gen_cmp_zca | gen_test_cmp_zca | 3 | PASS | yes | 11 | 0 | - | - | CREDITED |
| TP-CMP-032 | gen_cmp_zca | gen_test_cmp_zca | 3 | PASS | yes | 5 | 0 | - | - | CREDITED |
| TP-CMP-033 | gen_cmp_zca | gen_test_cmp_zca | 3 | PASS | yes | 12 | 12 | - | - | UNHIT (12 of 12 bins) |
| TP-CMP-034 | gen_cmp_zcb | gen_test_cmp_zcb | 3 | PASS | yes | 45 | 0 | - | - | CREDITED |
| TP-CMP-036 | gen_cmp_zcb | gen_test_cmp_zcb | 3 | PASS | yes | 41 | 6 | - | - | UNHIT (6 of 41 bins) |
| TP-CMP-038 | gen_cmp_zcb | gen_test_cmp_zcb | 3 | PASS | yes | 24 | 8 | - | - | UNHIT (8 of 24 bins) |
| TP-CMP-039 | gen_cmp_zcmp_basic | gen_test_cmp_zcmp_basic | 3 | PASS | yes | 72 | 4 | - | - | UNHIT (4 of 72 bins) |
| TP-CMP-040 | gen_cmp_zcmp_basic | gen_test_cmp_zcmp_basic | 3 | PASS | yes | 5 | 0 | - | - | CREDITED |
| TP-CMP-041 | gen_cmp_zcmp_basic | gen_test_cmp_zcmp_basic | 3 | PASS | yes | 5 | 0 | - | - | CREDITED |
| TP-CMP-042 | gen_cmp_zcmp_basic | gen_test_cmp_zcmp_basic | 3 | PASS | yes | 10 | 0 | - | - | CREDITED |
| TP-CMP-043 | gen_cmp_zcmp_basic | gen_test_cmp_zcmp_basic | 3 | PASS | yes | 11 | 0 | - | - | CREDITED |
| TP-CMP-045 | gen_cmp_zcmp_basic | gen_test_cmp_zcmp_basic | 3 | PASS | yes | 67 | 0 | - | - | CREDITED |
| TP-CMP-046 | gen_cmp_zcmp_basic | gen_test_cmp_zcmp_basic | 3 | PASS | yes | 5 | 0 | - | - | CREDITED |
| TP-CMP-047 | gen_cmp_zcmp_basic | gen_test_cmp_zcmp_basic | 3 | PASS | yes | 71 | 49 | - | - | UNHIT (49 of 71 bins) |
| TP-CMP-048 | gen_cmp_zcmp_basic | gen_test_cmp_zcmp_basic | 3 | PASS | yes | 71 | 50 | - | - | UNHIT (50 of 71 bins) |
| TP-CMP-049 | gen_cmp_zcmp_basic | gen_test_cmp_zcmp_basic | 3 | PASS | yes | 8 | 3 | - | - | UNHIT (3 of 8 bins) |
| TP-CMP-050 | gen_cmp_zcmp_basic | gen_test_cmp_zcmp_basic | 3 | PASS | yes | 76 | 0 | - | - | CREDITED |
| TP-CMP-052 | gen_cmp_zcmp_basic | gen_test_cmp_zcmp_basic | 3 | PASS | yes | 81 | 0 | - | - | CREDITED |
| TP-CMP-053 | gen_cmp_zcmp_basic | gen_test_cmp_zcmp_basic | 3 | PASS | yes | 8 | 0 | - | - | CREDITED |
| TP-CMP-055 | gen_cmp_zcmp_basic | gen_test_cmp_zcmp_basic | 3 | PASS | yes | 3 | 0 | - | - | CREDITED |
| TP-CMP-066 | gen_cmp_zcmp_basic | gen_test_cmp_zcmp_basic | 3 | PASS | yes | 36 | 16 | - | - | UNHIT (16 of 36 bins) |
| TP-CMP-068 | gen_cmp_zcmp_basic | gen_test_cmp_zcmp_basic | 3 | PASS | none | 10 | 6 | - | - | NOT-FIRED (no fire line: not built or not reached) |
| TP-CMP-069 | gen_cmp_zcmp_basic | gen_test_cmp_zcmp_basic | 3 | PASS | yes | 39 | 20 | - | - | UNHIT (20 of 39 bins) |
| TP-CMP-073 | gen_cmp_zcmp_basic | gen_test_cmp_zcmp_basic | 3 | PASS | yes | 22 | 10 | - | - | UNHIT (10 of 22 bins) |
| TP-CSR-001 | gen_csr_access | gen_test_csr_access | 3 | PASS | yes | 29 | 29 | - | - | UNHIT (29 of 29 bins) |
| TP-CSR-002 | gen_csr_access | gen_test_csr_access | 3 | PASS | yes | 21 | 20 | - | - | UNHIT (20 of 21 bins) |
| TP-CSR-003 | gen_csr_access | gen_test_csr_access | 3 | PASS | yes | 19 | 14 | - | - | UNHIT (14 of 19 bins) |
| TP-CSR-004 | gen_csr_access | gen_test_csr_access | 3 | PASS | yes | 15 | 13 | - | - | UNHIT (13 of 15 bins) |
| TP-CSR-005 | gen_csr_access | gen_test_csr_access | 3 | PASS | none | 3 | 3 | - | - | NOT-FIRED (no fire line: not built or not reached) |
| TP-CSR-012 | gen_csr_access | gen_test_csr_access | 3 | PASS | yes | 21 | 21 | - | - | UNHIT (21 of 21 bins) |
| TP-CSR-023 | gen_csr_trap_setup | gen_test_csr_trap_setup | 3 | PASS | yes | 36 | 0 | - | - | CREDITED |
| TP-CSR-024 | gen_csr_trap_setup | gen_test_csr_trap_setup | 3 | PASS | yes | 24 | 9 | - | - | UNHIT (9 of 24 bins) |
| TP-CSR-025 | gen_csr_trap_setup | gen_test_csr_trap_setup | 3 | PASS | yes | 6 | 0 | - | - | CREDITED |
| TP-CSR-027 | gen_csr_trap_setup | gen_test_csr_trap_setup | 3 | PASS | yes | 22 | 1 | - | - | UNHIT (1 of 22 bins) |
| TP-CSR-028 | gen_csr_trap_setup | gen_test_csr_trap_setup | 3 | PASS | yes | 34 | 3 | - | - | UNHIT (3 of 34 bins) |
| TP-CSR-029 | gen_csr_trap_setup | gen_test_csr_trap_setup | 3 | PASS | yes | 37 | 1 | - | - | UNHIT (1 of 37 bins) |
| TP-CSR-030 | gen_csr_trap_setup | gen_test_csr_trap_setup | 3 | PASS | yes | 8 | 0 | - | - | CREDITED |
| TP-CSR-035 | gen_csr_trap_setup | gen_test_csr_trap_setup | 3 | PASS | yes | 37 | 9 | - | - | UNHIT (9 of 37 bins) |
| TP-CSR-036 | gen_csr_trap_setup | gen_test_csr_trap_setup | 3 | PASS | yes | 23 | 0 | - | - | CREDITED |
| TP-CSR-037 | gen_csr_reset | gen_test_csr_reset | 3 | PASS | yes | 12 | 12 | - | - | UNVERIFIED (no fcov check with per-bin results in the round) |
| TP-CSR-105 | gen_csr_reset | gen_test_csr_reset | 3 | PASS | yes | 19 | 19 | - | - | UNVERIFIED (no fcov check with per-bin results in the round) |
| TP-CSR-106 | gen_csr_reset | gen_test_csr_reset | 3 | PASS | yes | 5 | 5 | - | - | UNVERIFIED (no fcov check with per-bin results in the round) |
| TP-CSR-107 | gen_csr_reset | gen_test_csr_reset | 3 | PASS | yes | 15 | 15 | - | - | UNVERIFIED (no fcov check with per-bin results in the round) |
| TP-CSR-108 | gen_csr_reset | gen_test_csr_reset | 3 | PASS | yes | 20 | 20 | - | - | UNVERIFIED (no fcov check with per-bin results in the round) |
| TP-CSR-109 | gen_csr_reset | gen_test_csr_reset | 3 | PASS | yes | 13 | 13 | - | - | UNVERIFIED (no fcov check with per-bin results in the round) |
| TP-ISA-001 | gen_isa_alu | gen_test_isa_alu | 3 | PASS | yes | 130 | 0 | - | - | CREDITED |
| TP-ISA-002 | gen_isa_alu | gen_test_isa_alu | 3 | PASS | yes | 4 | 0 | - | - | CREDITED |
| TP-ISA-003 | gen_isa_alu | gen_test_isa_alu | 3 | PASS | yes | 15 | 0 | - | - | CREDITED |
| TP-ISA-004 | gen_isa_alu | gen_test_isa_alu | 3 | PASS | yes | 30 | 0 | - | - | CREDITED |
| TP-ISA-005 | gen_isa_alu | gen_test_isa_alu | 3 | PASS | yes | 26 | 0 | - | - | CREDITED |
| TP-ISA-006 | gen_isa_alu | gen_test_isa_alu | 3 | PASS | yes | 13 | 2 | - | - | UNHIT (2 of 13 bins) |
| TP-ISA-007 | gen_isa_alu | gen_test_isa_alu | 3 | PASS | yes | 224 | 0 | - | - | CREDITED |
| TP-ISA-008 | gen_isa_alu | gen_test_isa_alu | 3 | PASS | yes | 15 | 0 | - | - | CREDITED |
| TP-ISA-009 | gen_isa_alu | gen_test_isa_alu | 3 | PASS | yes | 127 | 13 | - | - | UNHIT (13 of 127 bins) |
| TP-ISA-010 | gen_isa_shift | gen_test_isa_shift | 3 | PASS | yes | 57 | 0 | - | - | CREDITED |
| TP-ISA-011 | gen_isa_shift | gen_test_isa_shift | 3 | PASS | yes | 22 | 0 | - | - | CREDITED |
| TP-ISA-013 | gen_isa_shift | gen_test_isa_shift | 3 | PASS | yes | 39 | 0 | - | - | CREDITED |
| TP-ISA-014 | gen_isa_shift | gen_test_isa_shift | 3 | PASS | yes | 27 | 0 | - | - | CREDITED |
| TP-ISA-015 | gen_isa_cti | gen_test_isa_cti | 3 | PASS | yes | 22 | 0 | - | - | CREDITED |
| TP-ISA-016 | gen_isa_cti | gen_test_isa_cti | 3 | PASS | none | 40 | 28 | - | - | NOT-FIRED (no fire line: not built or not reached) |
| TP-ISA-017 | gen_isa_cti | gen_test_isa_cti | 3 | PASS | yes | 17 | 0 | - | - | CREDITED |
| TP-ISA-018 | gen_isa_cti | gen_test_isa_cti | 3 | PASS | yes | 18 | 4 | - | - | UNHIT (4 of 18 bins) |
| TP-ISA-019 | gen_isa_cti | gen_test_isa_cti | 3 | PASS | yes | 10 | 0 | - | - | CREDITED |
| TP-ISA-020 | gen_isa_cti | gen_test_isa_cti | 3 | PASS | yes | 13 | 0 | - | - | CREDITED |
| TP-ISA-022 | gen_isa_cti | gen_test_isa_cti | 3 | PASS | none | 15 | 9 | - | - | NOT-FIRED (no fire line: not built or not reached) |
| TP-ISA-023 | gen_isa_cti | gen_test_isa_cti | 3 | PASS | yes | 122 | 0 | - | - | CREDITED |
| TP-ISA-024 | gen_isa_cti | gen_test_isa_cti | 3 | PASS | none | 9 | 9 | - | - | NOT-FIRED (no fire line: not built or not reached) |
| TP-ISA-026 | gen_isa_cti | gen_test_isa_cti | 3 | PASS | none | 70 | 62 | - | - | NOT-FIRED (no fire line: not built or not reached) |
| TP-ISA-027 | gen_isa_cti | gen_test_isa_cti | 3 | PASS | yes | 74 | 10 | - | - | UNHIT (10 of 74 bins) |
| TP-ISA-052 | gen_isa_alu | gen_test_isa_alu | 3 | PASS | yes | 60 | 26 | - | - | UNHIT (26 of 60 bins) |
| TP-ISA-053 | gen_isa_cti | gen_test_isa_cti | 3 | PASS | yes | 30 | 4 | - | - | UNHIT (4 of 30 bins) |
| TP-MUL-001 | gen_mul_mul | gen_test_mul_mul | 3 | PASS | yes | 63 | 0 | - | - | CREDITED |
| TP-MUL-002 | gen_mul_mul | gen_test_mul_mul | 3 | PASS | yes | 268 | 0 | - | - | CREDITED |
| TP-MUL-003 | gen_mul_mul | gen_test_mul_mul | 3 | PASS | none | 6 | 1 | - | - | NOT-FIRED (no fire line: not built or not reached) |
| TP-MUL-004 | gen_mul_mul | gen_test_mul_mul | 3 | PASS | yes | 291 | 0 | - | - | CREDITED |
| TP-MUL-005 | gen_mul_mul | gen_test_mul_mul | 3 | PASS | yes | 6 | 0 | - | - | CREDITED |
| TP-MUL-006 | gen_mul_mul | gen_test_mul_mul | 3 | PASS | yes | 267 | 0 | - | - | CREDITED |
| TP-MUL-007 | gen_mul_mul | gen_test_mul_mul | 3 | PASS | yes | 6 | 0 | - | - | CREDITED |
| TP-MUL-008 | gen_mul_mul | gen_test_mul_mul | 3 | PASS | yes | 290 | 0 | - | - | CREDITED |
| TP-MUL-012 | gen_mul_div | gen_test_mul_div | 3 | PASS | none | 33 | 11 | - | - | NOT-FIRED (no fire line: not built or not reached) |
| TP-MUL-013 | gen_mul_div | gen_test_mul_div | 3 | PASS | yes | 39 | 0 | - | - | CREDITED |
| TP-MUL-014 | gen_mul_div | gen_test_mul_div | 3 | PASS | yes | 27 | 1 | - | - | UNHIT (1 of 27 bins) |
| TP-MUL-015 | gen_mul_div | gen_test_mul_div | 3 | PASS | yes | 39 | 0 | - | - | CREDITED |
| TP-MUL-016 | gen_mul_div | gen_test_mul_div | 3 | PASS | yes | 79 | 25 | - | - | UNHIT (25 of 79 bins) |
| TP-MUL-017 | gen_mul_div | gen_test_mul_div | 3 | PASS | yes | 57 | 16 | - | - | UNHIT (16 of 57 bins) |
| TP-MUL-018 | gen_mul_div | gen_test_mul_div | 3 | PASS | yes | 11 | 0 | - | - | CREDITED |
| TP-MUL-019 | gen_mul_div | gen_test_mul_div | 3 | PASS | yes | 27 | 0 | - | - | CREDITED |
| TP-MUL-020 | gen_mul_div | gen_test_mul_div | 3 | PASS | yes | 57 | 0 | - | - | CREDITED |
| TP-MUL-021 | gen_mul_div | gen_test_mul_div | 3 | PASS | yes | 26 | 0 | - | - | CREDITED |
| TP-MUL-022 | gen_mul_div | gen_test_mul_div | 3 | PASS | none | 23 | 12 | - | - | NOT-FIRED (no fire line: not built or not reached) |
| TP-MUL-026 | gen_mul_div | gen_test_mul_div | 3 | PASS | yes | 44 | 2 | - | - | UNHIT (2 of 44 bins) |
| TP-MUL-027 | gen_mul_mul | gen_test_mul_mul | 3 | PASS | yes | 4 | 0 | - | - | CREDITED |
| TP-PMP-001 | gen_pmp_csr_warl | gen_test_pmp_csr_warl | 3 | PASS | yes | 113 | 113 | - | - | UNVERIFIED (no fcov check with per-bin results in the round) |
| TP-PMP-002 | gen_pmp_csr_warl | gen_test_pmp_csr_warl | 3 | PASS | yes | 44 | 44 | - | - | UNVERIFIED (no fcov check with per-bin results in the round) |
| TP-PMP-003 | gen_pmp_csr_warl | gen_test_pmp_csr_warl | 3 | PASS | yes | 4 | 4 | - | - | UNVERIFIED (no fcov check with per-bin results in the round) |
| TP-PMP-004 | gen_pmp_csr_warl | gen_test_pmp_csr_warl | 3 | PASS | yes | 7 | 7 | - | - | UNVERIFIED (no fcov check with per-bin results in the round) |
| TP-PMP-005 | gen_pmp_csr_warl | gen_test_pmp_csr_warl | 3 | PASS | yes | 3 | 3 | - | - | UNVERIFIED (no fcov check with per-bin results in the round) |
| TP-PMP-006 | gen_pmp_csr_warl | gen_test_pmp_csr_warl | 3 | PASS | yes | 7 | 7 | - | - | UNVERIFIED (no fcov check with per-bin results in the round) |
| TP-PMP-007 | gen_pmp_csr_warl | gen_test_pmp_csr_warl | 3 | PASS | yes | 91 | 91 | - | - | UNVERIFIED (no fcov check with per-bin results in the round) |
| TP-PMP-008 | gen_pmp_csr_warl | gen_test_pmp_csr_warl | 3 | PASS | yes | 11 | 11 | - | - | UNVERIFIED (no fcov check with per-bin results in the round) |
| TP-PMP-011 | gen_pmp_mseccfg | gen_test_pmp_mseccfg | 3 | PASS | yes | 11 | 11 | - | - | UNVERIFIED (no fcov check with per-bin results in the round) |
| TP-PMP-012 | gen_pmp_mseccfg | gen_test_pmp_mseccfg | 3 | PASS | yes | 10 | 10 | - | - | UNVERIFIED (no fcov check with per-bin results in the round) |
| TP-PMP-013 | gen_pmp_lock | gen_test_pmp_lock | 3 | PASS | yes | 10 | 10 | - | - | UNVERIFIED (no fcov check with per-bin results in the round) |
| TP-PMP-014 | gen_pmp_lock | gen_test_pmp_lock | 3 | PASS | yes | 7 | 7 | - | - | UNVERIFIED (no fcov check with per-bin results in the round) |
| TP-PMP-015 | gen_pmp_lock | gen_test_pmp_lock | 3 | PASS | yes | 3 | 3 | - | - | UNVERIFIED (no fcov check with per-bin results in the round) |
| TP-PMP-016 | gen_pmp_lock | gen_test_pmp_lock | 3 | PASS | yes | 2 | 2 | - | - | UNVERIFIED (no fcov check with per-bin results in the round) |
| TP-PMP-017 | gen_pmp_lock | gen_test_pmp_lock | 3 | PASS | yes | 2 | 2 | - | - | UNVERIFIED (no fcov check with per-bin results in the round) |
| TP-PMP-018 | gen_pmp_lock | gen_test_pmp_lock | 3 | PASS | yes | 4 | 4 | - | - | UNVERIFIED (no fcov check with per-bin results in the round) |
| TP-PMP-019 | gen_pmp_lock | gen_test_pmp_lock | 3 | PASS | yes | 4 | 4 | - | - | UNVERIFIED (no fcov check with per-bin results in the round) |
| TP-PMP-020 | gen_pmp_lock | gen_test_pmp_lock | 3 | PASS | yes | 11 | 11 | - | - | UNVERIFIED (no fcov check with per-bin results in the round) |
| TP-PMP-021 | gen_pmp_lock | gen_test_pmp_lock | 3 | PASS | yes | 6 | 6 | - | - | UNVERIFIED (no fcov check with per-bin results in the round) |
| TP-PMP-022 | gen_pmp_mseccfg | gen_test_pmp_mseccfg | 3 | PASS | yes | 10 | 10 | - | - | UNVERIFIED (no fcov check with per-bin results in the round) |
| TP-PMP-023 | gen_pmp_mseccfg | gen_test_pmp_mseccfg | 3 | PASS | yes | 10 | 10 | - | - | UNVERIFIED (no fcov check with per-bin results in the round) |
| TP-PMP-024 | gen_pmp_mseccfg | gen_test_pmp_mseccfg | 3 | PASS | yes | 5 | 5 | - | - | UNVERIFIED (no fcov check with per-bin results in the round) |
| TP-PMP-025 | gen_pmp_mseccfg | gen_test_pmp_mseccfg | 3 | PASS | yes | 4 | 4 | - | - | UNVERIFIED (no fcov check with per-bin results in the round) |
| TP-PMP-026 | gen_pmp_mseccfg | gen_test_pmp_mseccfg | 3 | PASS | yes | 5 | 5 | - | - | UNVERIFIED (no fcov check with per-bin results in the round) |
| TP-PMP-027 | gen_pmp_mseccfg | gen_test_pmp_mseccfg | 3 | PASS | yes | 9 | 9 | - | - | UNVERIFIED (no fcov check with per-bin results in the round) |
| TP-PMP-028 | gen_pmp_mseccfg | gen_test_pmp_mseccfg | 3 | PASS | yes | 1 | 1 | - | - | UNVERIFIED (no fcov check with per-bin results in the round) |
| TP-PMP-029 | gen_pmp_mseccfg | gen_test_pmp_mseccfg | 3 | PASS | yes | 4 | 4 | - | - | UNVERIFIED (no fcov check with per-bin results in the round) |
| TP-PMP-030 | gen_pmp_mseccfg | gen_test_pmp_mseccfg | 3 | PASS | yes | 5 | 5 | - | - | UNVERIFIED (no fcov check with per-bin results in the round) |
| TP-PMP-031 | gen_pmp_mseccfg | gen_test_pmp_mseccfg | 3 | PASS | yes | 6 | 6 | - | - | UNVERIFIED (no fcov check with per-bin results in the round) |
| TP-PMP-108 | gen_pmp_mseccfg | gen_test_pmp_mseccfg | 3 | PASS | none | 49 | 49 | - | - | UNVERIFIED (no fcov check with per-bin results in the round) |
| TP-PMP-112 | gen_pmp_lock | gen_test_pmp_lock | 3 | PASS | yes | 11 | 11 | - | - | UNVERIFIED (no fcov check with per-bin results in the round) |
| TP-RST-001 | gen_rst_boot | gen_test_rst_boot | 3 | PASS | none | 3 | 3 | - | - | NOT-FIRED (no fire line: not built or not reached) |
| TP-RST-002 | gen_rst_boot | gen_test_rst_boot | 3 | PASS | none | 10 | 9 | - | - | NOT-FIRED (no fire line: not built or not reached) |
| TP-RST-003 | gen_rst_boot | gen_test_rst_boot | 3 | PASS | yes | 3 | 1 | - | - | UNHIT (1 of 3 bins) |
| TP-RST-004 | gen_rst_boot | gen_test_rst_boot | 3 | PASS | none | 5 | 5 | - | - | NOT-FIRED (no fire line: not built or not reached) |
| TP-RST-005 | gen_rst_boot | gen_test_rst_boot | 3 | PASS | none | 3 | 3 | - | - | NOT-FIRED (no fire line: not built or not reached) |
| TP-RST-006 | gen_rst_boot | gen_test_rst_boot | 3 | PASS | yes | 3 | 1 | - | - | UNHIT (1 of 3 bins) |
| TP-RST-007 | gen_rst_boot | gen_test_rst_boot | 3 | PASS | yes | 3 | 1 | - | - | UNHIT (1 of 3 bins) |
| TP-RST-008 | gen_rst_boot | gen_test_rst_boot | 3 | PASS | none | 3 | 3 | - | - | NOT-FIRED (no fire line: not built or not reached) |
| TP-RST-027 | gen_rst_boot | gen_test_rst_boot | 3 | PASS | none | 1 | 1 | - | - | NOT-FIRED (no fire line: not built or not reached) |
| TP-RVFI-036 | gen_rst_boot | gen_test_rst_boot | 3 | PASS | none | 2 | 2 | - | - | NOT-FIRED (no fire line: not built or not reached) |
| TP-SEC-031 | gen_rst_boot | gen_test_rst_boot | 3 | PASS | none | 10 | 10 | - | - | NOT-FIRED (no fire line: not built or not reached) |
