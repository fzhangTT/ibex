# Critic verdict: T-102, lock-step comparator and shim conventions (commit d0c0d15, tb-infra)

Artifacts at commit d0c0d15 (sha256 first 16 hex, lines):
- dv/auto_dv/env/gen_rvfi_pkg.sv               d43ccf8d9a562c78  388
- dv/auto_dv/isa/gen_isa_shim.cc               8b7e1a24522d7ddc  632;  gen_isa_shim.h  c3259228f374e27a  81;  gen_isa_dpi_pkg.sv  35ba981b84f88b9b  49
- dv/auto_dv/isa/gen_ut_isa_shim.cc            47533748534e0061  295 (sections 5 and 6 added)
- dv/auto_dv/tb/gen_tb_knobs.yaml              142767ffeb8dd282  243;  gen_knobs_codegen.py  b72da17ad2faa701  624;  gen_tb_top.sv (guards :73-78)
- dv/auto_dv/mutations/gen_mut_t102.md         b883091360ca065d   30 (P1..P9)
- dv/auto_dv/evidence/gen_tdd_t102.md          cc1b21f90bfe365e  105
- dv/auto_dv/evidence/gen_t102_rtl_facts.md    fdb5296b84bb0a71   45 (rtl-arch)
- dv/auto_dv/evidence/gen_tdd_logs/gen_manifest.md: 103 t102 rows (lockstep, isa_shim, export, mutations), all md5 and byte counts verified
Date: 2026-09-03T11:58Z   Role: Critic   Asked: judge T-102 as the checker-side half of the trust triad for the isa ids; rule on the
mret/dret skip (a gap or not) and on the record-synchronised model state under dv_principles Section 2. The cross-model
review of this commit was not read. My batch-1 verdict attributed the four failures to these conventions.

CRITIC VERDICT: APPROVE (checker-side half for isa_prv, isa_pc_next and the isa_rd read paths; D-2 closed), with one
medium on the synchronised state that must be answered before the counter and status reads are counted as checked.

## 1. The fixes, verified against the code and the logs

- isa_prv: step() returns prv_before; the compare is 'prv_b[1:0] != t.mode' (gen_rvfi_pkg.sv, T-102 hunk), matching
  rvfi_mode = priv_mode_id captured at ID exit (rtl/ibex_core.sv:2078). P1 re-installs the post-step compare: FAIL with
  UVM_ERROR 314 on gen_test_pmp_csr_warl under +gen_chk_all=0 +gen_chk_isa=1 +gen_chk_isa_prv=1; ablation (row off)
  PASS, UVM_ERROR 0. Debug mode: rvfi_mode reports priv_lvl_q (rtl/ibex_cs_registers.sv:996), Spike keeps prv; no special
  case needed, not yet exercised (transcript section 6).
- isa_pc_next: skipped when t.insn is GEN_INSN_MRET (0x30200073) or GEN_INSN_DRET (0x7B200073), rendered constants. P2
  removes the skip: FAIL, 70 misses on csr_trap_setup, first on the mret at 80004264 with dut pc_wdata 80004268; ablation
  PASS. Ruling on the skip: NOT a gap in DUT checking. The comparator compares every record's pc_rdata against the model's
  pc (gen_rvfi_pkg.sv:338, miss("isa_pc", "pc model=... dut=...")), so a wrong mret or dret target shows on the next
  record under isa_pc (and SB_DESYNC after GEN_SB_DESYNC_RECORDS). What the skip drops is the check of the RVFI
  convention itself (pc_wdata == pc + 4 on those records, plan C-1). L-1 below asks for that one-line compare.
- Shim views: marchid from the rendered GEN_CSR_MARCHID_VALUE (parsed from ibex_pkg CSR_MARCHID_VALUE = {1'b0, 31'd22});
  mhpmevent3.. = bit i-3 for i < GEN_MHPM_COUNTER_NUM, 0 beyond (rtl/ibex_cs_registers.sv MHPMCOUNTER_BASE = 3, D20);
  mstatus view without XS/SD; tdata1/tdata2 views (debug-mode writes only, read GEN_TDATA1_IBEX_RDATA 0x28001048 plus the
  execute bit; rtl/ibex_cs_registers.sv:1848-1864 tmatch_control_rdata type 2, dmode 1); cpuctrlsts bit 8 from the fed
  status. P3, P7, P9 remove marchid, XS/SD and tdata1 views: FAIL 1 / 206 / 1 under isa_rd, ablations PASS.
- Synchronisation: before every record step the model receives t.ext_mcycle, the GEN_MHPM_COUNTER_NUM counter pairs and
  t.ext_ic_scr_key_valid (monitor samples the counter words on every record now). P4, P5, P6 remove each: FAIL 2 / 6 / 1
  under isa_rd, ablations PASS. See section 2 for what these compares mean.
- Draft-B: rs3 = insn[31:27] for the R4 forms, compared with rvfi_rs3_addr/rdata and passed to the reference; the
  reference covers pack/packu/packh, slo/sro(i), shfl/unshfl(i), xperm.n/b/h, cmov/cmix, fsl/fsr/fsri, bfp, crc32/crc32c
  .b/.h/.w with literal vectors in gen_ut_isa_shim.cc section 5 (150 OK after 41 FAIL red; retained
  gen_t102_red1_ut_isa_shim.log / gen_t102_green_ut_isa_shim.log). P8 (cmix mask not inverted) caught by the unit test.
  DUT-level exercise waits for TP-BIT-022..033 (Test Writer).
- The four blocked tests on the fixed build: PASS, UVM_ERROR 0, ISA compare mismatches 0 on 119 / 282 / 5189 / 7965
  records, own fire-checks green (retained excerpts and verdicts). Closing canary after the last revert: boot_zc,
  lockstep_zc, lockstep_s7, export_zc PASS on a fresh compile; every mutation revert printed the pre-mutation sha256.
- Retention and hygiene: 103 manifest rows match md5 and bytes; every run header carries the isolation knobs; all files
  gen_-prefixed. Isolation is real: every catch run has +gen_chk_all=0 +gen_chk_isa=1 +gen_chk_isa_<row>=1 and every
  ablation the same with the row set to 0.

## 2. The synchronised state under dv_principles Section 2 (M-1, medium)

- What the sync does: the model's mcycle, mhpmcounter3..12 and cpuctrlsts bit 8 are overwritten from the DUT's own record
  before each step, so a csrr of cycle, mhpmcounterN or cpuctrlsts compares the DUT against itself. The scoreboard API
  says "the model's read equals the DUT's exactly", which is true and is exactly the point: under isa_rd these reads
  are no longer an independent check of the DUT, they are consistency compares (record value == read value). P4/P5/P6
  prove the sync is needed for the compare to pass, not that the compare has teeth.
- Is the anchor justified? Section 2 allows an internal anchor "only when the quantity's starting state is genuinely
  unknowable from intent, and document it". mcycle at cycle precision and the HPM event counts are microarchitectural
  and qualify, PROVIDED the independent checkers the architecture assigns to them exist (ctr_mcycle, ctr_minstret,
  ctr_hpm_exact, ctr_hpm_bound; ids rendered, no implementation in env/ at d0c0d15, step 2d). ic_scr_key_valid does NOT
  qualify: the TB drives ic_scr_key_valid_i itself (the scramble-key responder), so the intended value at every sample
  point is knowable; the responder API already promises the check (gen_component_api_scrkey_responder.md row
  scrkey_proto: cpuctrlsts.ic_scr_key_valid equals the driven value) and nothing in env/ implements it yet. Today a DUT
  that reported bit 8 wrongly would pass every check.
- Required: (a) the scoreboard API and gen_rvfi_pkg.sv comment state that isa_rd on cycle, mhpmcounterN and cpuctrlsts
  bit 8 is a consistency compare against the record, not an independent check, and name the checker that owns each
  quantity; (b) scrkey_proto's status row lands (record bit 8 versus the driven value at the ID-exit sample, with the
  registration delay) before any cpuctrlsts read is credited; (c) ctr_* land with step 2d before counter reads are
  credited. None of this blocks the four tests, whose own fire-checks carry their pass criteria; it blocks counting
  those isa_rd compares as coverage of counter or status correctness.

## 3. D-2 closed

The two custom CSR addresses and marchid are rendered from ibex_pkg (codegen derivations csr_marchid_value,
csr_addr_cpuctrlsts, csr_addr_secureseed) with the time-0 GEN_WIDTH_GUARD in gen_tb_top.sv:73-76; GEN_MHPM_COUNTER_NUM
is a literal guarded against u_dut.MHPMCounterNum (:77-78, the D-1 pattern); the shim unit test checks misa 0x40901104,
mstatus reset 0x80, marchid == GEN_CSR_MARCHID_VALUE and the XS/SD masking. What I asked for in the T-068 verdict is met.

## 4. Lows

- L-1 mret/dret convention check: add 't.pc_wdata == t.pc_rdata + 4' for GEN_INSN_MRET / GEN_INSN_DRET records under
  isa_pc_next (both are 32-bit encodings), so the RVFI convention the plan relies on (C-1) is itself under a check.
- L-2 P1's message prints prv_b while the mutated compare used prv (the record admits it); harmless, the catch is real.
- L-3 The new reference functions have unit vectors only; the DUT-level exercise is TP-BIT-022..033 (Test Writer), and
  the RTL-level mutation halves per isa id (my D-3) remain owed, as the transcript says.

## 5. Effect on earlier verdicts

Batch-1 T-102 attribution confirmed by the fix: the four tests pass with 0 comparator errors and no test-side change. My
batch-1 M-4 (rd = x0 reads that dodged the shim) can now be reverted by the Test Writer: the shim reads marchid, cycle
and the HPM counters as the DUT does, so the observations can be restored.
