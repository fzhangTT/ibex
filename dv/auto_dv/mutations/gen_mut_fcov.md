# Mutation record: the plan's covergroups (T-205)

Owner: tb-infra, 2026-09-03. Format: dv/auto_dv/mutations/gen_README.md. A covergroup has no checker to fire; its proof is the
fcov-expectation check (trust triad rule 3) and a sampler mutant is caught by that check: the mutant run PASSES the simulation
and `ci/check_fcov_expectations.py` on the slice's proof manifest names the bins the mutant leaves unhit. Out of tree (a scratch
copy of the wit_root sources plus the one edit; rtl untouched); `build` is the mutant build's `sources sha256`.

| mutant | what is broken | run | build | catch | ablation |
|---|---|---|---|---|---|
| FM1 | gen_fcov_pkg.sv (gen_isa_cov): c.mul is never decoded from its 16-bit RVFI form (`is_cmul = 0`) | gen_ut_lockstep on gen_muldiv_directed.S, urg, checker on gen_fcov_proof_slice1.fcov.yaml | a65d88c23c734972 | simulation PASS; checker `FAIL -- 1 declared bin(s) not hit: gen_mul_ops_cg.cp_op.c_mul` (and every c_mul cross tuple uncovered in urg) | the manifest without the c_mul bins passes on the same report |

Exact edit: `bit is_cmul = (t.insn[1:0] == 2'b01 && t.insn[15:10] == 6'b100111 && t.insn[6:5] == 2'b10);` -> `bit is_cmul = 1'b0;`.
Red of the slice (not a mutant): the proof run with `+gen_fcov_en=0` on a fresh vdb has no covergroup, urg writes no grpinfo.txt
and the checker fails on the missing report (gen_fu_l3_nofcov_check.log).
