## 1.7 Round-0 PROBE crediting (probe of 37c7ecb refused as a round, LOG-046; 0 credited, every hosted item NOT-RUN-CLEAN) (generated from the regression manifest and sim logs; 162 items in 15 hosted groups)

Regression /proj_soc/user_dev/fzhang/ibex_dv_out/regress_round_0: status done, source {'mode': 'head', 'source_root': '/proj_soc/user_dev/fzhang/ibex_dv_mirror_head/37c7ecb6dbe0', 'head_sha': '37c7ecb6dbe023e6f6b098e932367e339a24735a', 'worktree_dirty': None}, git 37c7ecb6dbe023e6f6b098e932367e339a24735a; 47 runs: pass 2, fail 45, xfail 0, red_ok 0, timeout 0, not_run 0; fcov checks {'checked': 44, 'pass': 0, 'unmet': 0, 'unverifiable': 44}; covergroups_exist False; clean regression (gen_round.py hard rule): NO.

| Area | Items hosted | CREDITED | HELD | UNHIT | FIRE-FAIL | NOT-FIRED | NOT-RUN-CLEAN | UNVERIFIED |
|---|---|---|---|---|---|---|---|---|
| BIT | 33 | 0 | 0 | 0 | 0 | 0 | 33 | 0 |
| CMP | 42 | 0 | 0 | 0 | 0 | 0 | 42 | 0 |
| CSR | 21 | 0 | 0 | 0 | 0 | 0 | 21 | 0 |
| ISA | 26 | 0 | 0 | 0 | 0 | 0 | 26 | 0 |
| MUL | 21 | 0 | 0 | 0 | 0 | 0 | 21 | 0 |
| PMP | 8 | 0 | 0 | 0 | 0 | 0 | 8 | 0 |
| RST | 9 | 0 | 0 | 0 | 0 | 0 | 9 | 0 |
| RVFI | 1 | 0 | 0 | 0 | 0 | 0 | 1 | 0 |
| SEC | 1 | 0 | 0 | 0 | 0 | 0 | 1 | 0 |

Total: 162 items hosted; credited 0; held 0; unhit 0; fire-fail 0; not fired 0; not run clean 162; unverified 0.
Witness bins of hosted items: 2 (unscored until T-179; listed, never credited).

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

|---|---|---|---|---|---|---|---|---|---|
