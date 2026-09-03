# Mutation record: T-102 comparator conventions and shim legalization (P1..P9)

Owner: tb-infra, 2026-09-03. Build under mutation: dv/auto_dv/work/tb-infra/out_t102/mut (base compile of the green tree;
SV mutations recompile into out_t102/mut/<id>, shim mutations rebuild only the shared library into out_t102/mut/base/lib).
Every mutation is applied by the scratch script (one exact string replacement), the catch run and the ablation run are
made, the file is restored from its saved bytes and its sha256 is printed after the revert; the printed sha256 per file
across the batch: dv/auto_dv/env/gen_rvfi_pkg.sv: d43ccf8d9a562c78; dv/auto_dv/isa/gen_isa_shim.cc: 8b7e1a24522d7ddc (one value per file = every revert restored the pre-mutation bytes). Hidden referees are inert
in every run (`+gen_chk_all=0`), only `chk_isa` and the named row are on; the ablation turns the named row off and the
same mutated build must PASS (the row, not a side effect, catches the defect). Programs: the Test Writer's seed-1
per-test generators (dv/auto_dv/tests/gen_programs/gen_<g>_prog.py) built with gen_program.py --directed.

| Id | Mutation | Catching run and knobs | Catch result | Ablation |
|---|---|---|---|---|
| P1 | gen_rvfi_pkg.sv: isa_prv compares the post-step privilege `prv` again (the pre-T-102 form) | gen_test_pmp_csr_warl seed 1, `+gen_chk_all=0 +gen_chk_isa=1 +gen_chk_isa_prv=1` | FAIL (UVM_ERROR 314); first: - | `+gen_chk_isa_prv=0`: PASS (UVM_ERROR 0) |
| P2 | gen_rvfi_pkg.sv: isa_pc_next no longer skips mret/dret records (C-1) | gen_test_csr_trap_setup seed 1, `+gen_chk_all=0 +gen_chk_isa=1 +gen_chk_isa_pc_next=1` | FAIL (UVM_ERROR 70); first: `isa_pc_next` pc_next model=80000404 dut=80004268 (order 212, pc 80004264, insn 30200073) | `+gen_chk_isa_pc_next=0`: PASS (UVM_ERROR 0) |
| P3 | gen_isa_shim.cc: marchid legalization removed (Spike's 5 stands) | gen_test_csr_reset seed 1, `+gen_chk_all=0 +gen_chk_isa=1 +gen_chk_isa_rd=1` | FAIL (UVM_ERROR 1); first: `isa_rd` rd model=x8/00000005 dut=x8/00000016 (order 57, pc 80000160, insn f1202473) | `+gen_chk_isa_rd=0`: PASS (UVM_ERROR 0) |
| P4 | gen_rvfi_pkg.sv: mcycle sync `gen_isa_set_time` removed before the step | gen_test_csr_reset seed 1, `+gen_chk_all=0 +gen_chk_isa=1 +gen_chk_isa_rd=1` | FAIL (UVM_ERROR 2); first: `isa_rd` rd model=x9/00000069 dut=x9/000001d1 (order 106, pc 80000224, insn b00024f3) | `+gen_chk_isa_rd=0`: PASS (UVM_ERROR 0) |
| P5 | gen_rvfi_pkg.sv: hpm counter sync `gen_isa_set_hpm` removed | gen_test_csr_reset seed 1, `+gen_chk_all=0 +gen_chk_isa=1 +gen_chk_isa_rd=1` | FAIL (UVM_ERROR 6); first: `isa_rd` rd model=x23/00000000 dut=x23/00000047 (order 35, pc 80000108, insn b0402bf3) | `+gen_chk_isa_rd=0`: PASS (UVM_ERROR 0) |
| P6 | gen_rvfi_pkg.sv: ic_scr_key_valid status sync `gen_isa_set_status` removed | gen_test_rst_boot seed 1, `+gen_chk_all=0 +gen_chk_isa=1 +gen_chk_isa_rd=1` | FAIL (UVM_ERROR 1); first: `isa_rd` rd model=x23/00000000 dut=x23/00000100 (order 20, pc 80000148, insn 7c006bf3) | `+gen_chk_isa_rd=0`: PASS (UVM_ERROR 0) |
| P7 | gen_isa_shim.cc: mstatus XS/SD view removed (Spike's XS stands) | gen_test_csr_trap_setup seed 1, `+gen_chk_all=0 +gen_chk_isa=1 +gen_chk_isa_rd=1` | FAIL (UVM_ERROR 206); first: `isa_rd` rd model=x13/80239888 dut=x13/00221888 (order 1127, pc 800009c2, insn 300026f3) | `+gen_chk_isa_rd=0`: PASS (UVM_ERROR 0) |
| P9 | gen_isa_shim.cc: tdata1 view removed (Spike's disabled-trigger 0xf0000000 stands) | gen_test_rst_boot seed 1, `+gen_chk_all=0 +gen_chk_isa=1 +gen_chk_isa_rd=1` | FAIL (UVM_ERROR 1); first: `isa_rd` rd model=x19/f0000000 dut=x19/28001048 (order 68, pc 80000208, insn 7a1079f3) | `+gen_chk_isa_rd=0`: PASS (UVM_ERROR 0) |
| P8 | gen_isa_shim.cc: cmix reference computes `(rs1 & rs2) | (rs3 & rs2)` (mask not inverted) | the shim unit test gen_ut_isa_shim (the consumer of the reference functions; no DUT test exercises cmix yet, TP-BIT-027 is the Test Writer's) | FAIL (1 failures): cmix | not applicable (a unit check has no knob); the same build passes with the mutation reverted (green log) |

| P10 | gen_rvfi_pkg.sv (scoreboard): the record after an mret is compared with pc_rdata + 4 (a wrong redirect target as reported) | gen_test_csr_trap_setup seed 1, `+gen_chk_all=0 +gen_chk_isa=1 +gen_chk_isa_pc=1`, OUT OF TREE | FAIL (UVM_ERROR 100); first: `isa_pc` pc model=80001700 dut=80001704 (order 1437) | `+gen_chk_isa_pc=0`: PASS (UVM_ERROR 0) |
| P11 | gen_rvfi_pkg.sv: the mret record's pc_wdata is compared off by 4 (a wrong C-1 convention value as reported) | gen_test_csr_trap_setup seed 1, `+gen_chk_all=0 +gen_chk_isa=1 +gen_chk_isa_pc_next=1`, OUT OF TREE | FAIL (UVM_ERROR 100); first: `isa_pc_next` mret/dret record pc_wdata=1a110968 != pc + 4 (order 1436) | `+gen_chk_isa_pc_next=0`: PASS (UVM_ERROR 0) |
| P12 | gen_rvfi_pkg.sv: the trap-record offset rule re-typed to `insn_len(t.insn)` for every trap record (the pre-fix form: pc + 4 on the expanded encoding of a trapping Zcmp micro-op, whose correct offset is 0); a rule-constant mutation showing the check fires on the real record, not a monitor-side defect | gen_ut_zcmp_trap on gen_zcmp_trap_directed.S, `+gen_chk_all=0 +gen_chk_isa=1 +gen_chk_isa_pc_next=1`, OUT OF TREE (T-102c) | FAIL (UVM_ERROR 1: `isa_pc_next` trap record pc_wdata=8000013c != pc + 4 (C-1) on order 17, the trapping cm.push store) | `+gen_chk_isa_pc_next=0`: PASS (UVM_ERROR 0) |
| P13 | gen_isa_shim.cc: the model loses its pmpaddr0 after every step (`put_csr(CSR_PMPADDR0, 0)` after the Spike step), so the locked PMP entry never covers the buffer and the model never denies the access (the Critic's T-102c red: a dropped PMP configuration on a PMP-denial program) | gen_ut_lockstep on gen_pmp_deny_directed.S, `+gen_chk_all=0 +gen_chk_isa=1 +gen_chk_isa_trap=1`, OUT OF TREE (landing 2a) | FAIL (UVM_ERROR 20: `isa_trap dut trapped, model retired 1 trap=0 cause=00000000` at every denied load and store) | `+gen_chk_isa_trap=0`: PASS (UVM_ERROR 0) |

Out-of-tree rule (Critic T-080 landing-1 L-1, adopted by the Orchestrator): P10 and P11 were built from a scratch copy of
dv/auto_dv (every other clone entry symlinked; runner prints the shared tree's gen_rvfi_pkg.sv sha256 after the batch,
0dd85c87f99c314b unchanged; gen_tdd_logs/mutations/gen_t102_oot_mutation_batch.log). P1..P9 had run in the shared tree
under the announce-and-revert rule before the L-1 rule reached tb-infra; disclosed here and in README.md.

Summary: 12 of 12 DUT-run mutations (P1..P7, P9, P10, P11, P12, P13) caught with the ablation passing; P13 shows that under the conditioned arming (T-137) a DUT trap the model's own PMP does not reproduce is a miss, which the pre-T-137 unconditional arming would have accepted; P8 caught by the
unit test. P4, P5 and P6 show that each sync is LOAD-BEARING for the compare (remove it and the read mismatches); they do
not show that a wrong DUT counter or status bit would be detected, since the synced value is the DUT's own record (a
consistency compare, Critic T-102 M-1); detection of a wrong count is the counter checkers' (ctr_*) and of a wrong bit 8
the scramble-key responder's (scrkey_proto), both owed. P1's message text still prints `prv_b` (the mutation changes only the compared operand), so its first line
reads "priv model=3 (before the step) dut mode=3" while the compare that fired used the post-step privilege 0.
Not covered by a mutation: the draft-B references other than cmix (unit-tested with literal vectors in
gen_ut_isa_shim.cc section 5, no DUT-level exercise until the Test Writer's TP-BIT-022..033 tests), the counter sync's
exact sample point beyond the reads the four programs make, and the RTL-level halves of every isa_* id (Critic D-3,
still owed).

## Appendix: original and mutated text per P row (CR8 fu2a L-4)

P1..P9 were applied by an earlier form of the driver that kept descriptions only; their text blocks were not retained and
cannot be reconstructed from a log. P10..P13 are reproduced from the driver table as applied. Each per-mutant `shared tree
untouched` line hashes the SHARED tree's dv/auto_dv/env/gen_rvfi_pkg.sv (MB12 / P13) or gen_agents_pkg.sv, gen_export.py and
gen_ut_export.py (MUT-L), not the mutated file; the mutated file's identity is the `applied to ... original sha256` line, and
the batch's start / end tree lines cover the rest. The first MUT-L attempt (batch log 16:01-16:02Z) FAILed its ablation because
the mutant then also inverted the writer's row registration, which no knob ablates; the retained 16:05Z pair is the
re-run with the mutation confined to the driven value.

### P10 (dv/auto_dv/env/gen_rvfi_pkg.sv)

original:
```
      pc_expect = t.pc_rdata; insn_expect = t.insn;
```
mutated:
```
      pc_expect = t.pc_rdata + (mut_after_mret ? 32'h4 : 32'h0); insn_expect = t.insn; mut_after_mret = (t.insn == GEN_INSN_MRET);
```

original:
```
    bit          dbg_q = 0;
```
mutated:
```
    bit          dbg_q = 0;
    bit          mut_after_mret = 0;
```

### P11 (dv/auto_dv/env/gen_rvfi_pkg.sv)

original:
```
          if (t.pc_wdata != t.pc_rdata + insn_len(t.insn))
            miss("isa_pc_next", $sformatf("mret/dret record
```
mutated:
```
          if (t.pc_wdata + 32'h4 != t.pc_rdata + insn_len(t.insn))
            miss("isa_pc_next", $sformatf("mret/dret record
```

### P12 (dv/auto_dv/env/gen_rvfi_pkg.sv)

original:
```
        if (trap && cause != 1 && t.pc_wdata != t.pc_rdata + (t.ext_exp_valid ? 0 : insn_len(t.insn)))
```
mutated:
```
        if (trap && cause != 1 && t.pc_wdata + 32'h2 != t.pc_rdata + (t.ext_exp_valid ? 0 : insn_len(t.insn)))   // P12: the trap record's pc_wdata reported off by 2
```

### P13 (dv/auto_dv/isa/gen_isa_shim.cc)

original:
```
  g_fault.armed = false;   // an armed bus fault applies to one step
```
mutated:
```
  g_fault.armed = false;   // an armed bus fault applies to one step
  g_proc->put_csr(CSR_PMPADDR0, 0);   // P13: the model loses its pmpaddr0 after every step (the PMP entry never covers the buffer)
```
