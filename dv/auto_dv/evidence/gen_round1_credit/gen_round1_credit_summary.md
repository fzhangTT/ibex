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
