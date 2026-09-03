# TDD transcript: T-102 lock-step comparator and shim conventions (tb-infra, 2026-09-03)

Assignment (TASKS.md T-102, 11:08Z): the four batch-1 tests blocked by comparator UVM_ERRORs (gen_test_rst_boot,
gen_test_csr_reset, gen_test_csr_trap_setup, gen_test_pmp_csr_warl) reach PASS; lock-step regression green; red first.
Edit pass announced to Runtime 11:12Z (with the T-080 exact-row half), mutation sub-window 11:46Z, closing message after
the canary. Build: dv/auto_dv/work/tb-infra/out_t102/tb (compile log retained as
gen_tdd_logs/lockstep/gen_compile_t102.log, vcs exit 0).

## 1. Red: what the four blocked tests showed (Test Writer runs on the d58bdeb tree)

Filtered copies (banner and comparator lines) in gen_tdd_logs/lockstep/gen_t102_red_<test>_comparator.log; source
dv/auto_dv/work/test-writer/out_head/<test>_s1/stdout.log. Classes by first-failing instruction:

| Test | UVM_ERROR | Classes (model vs DUT) |
|---|---|---|
| gen_test_rst_boot | 8 | csrr cpuctrlsts: 0 vs 0x100 (bit 8 ic_scr_key_valid); csrrwi tdata1: 0xf0000000 vs 0x28001048; mret isa_pc_next model=target vs dut=pc+4; isa_prv on mret (0 vs 3) and on a U-mode csrrs mstatus (3 vs 0); downstream store-data misses |
| gen_test_csr_reset | 42 | csrr marchid 5 vs 22; csrr cycle 0xbf vs 0x2d8; csrr mhpmcounter3..8 0 vs event counts; csrr mhpmevent5 0 vs 4; downstream store-data misses |
| gen_test_csr_trap_setup | 407 | mret isa_pc_next (70) and isa_prv on mret/ecall (46); csrr mstatus 0x80239888 vs 0x00221888 (XS=3 and SD set in the model after an all-ones WARL write) |
| gen_test_pmp_csr_warl | 532 | mret isa_pc_next (218); isa_prv on mret, U-mode ecall, U-mode faulting loads/stores and illegal CSR accesses (314) |

Root causes found from the code, not guessed: (1) `isa_prv` compared the model's privilege AFTER the step with
rvfi_mode, which is the mode the instruction executed in (mret: 0 vs 3; a U-mode trap: 3 vs 0). (2) `isa_pc_next` was
compared on mret/dret records whose `rvfi_pc_wdata` is pc + 4 (plan C-1; the same F-RVFI-010 skip already existed for trap
records). (3) The shim never received the DUT's counters or status: `gen_isa_set_time` had NO call site (and its two-write
form trips Spike's `wide_counter_csr_t` assert, found by the unit test), mhpmcounters were Spike's constant 0, cpuctrlsts
bit 8 was always 0. (4) Spike's reset values differ from Ibex's for marchid (5), mhpmevent (0), tdata1 (disabled trigger
0xf0000000; Ibex writes tdata1/tdata2 in debug mode only, rtl/ibex_cs_registers.sv:1777-1780) and mstatus keeps XS (Spike
sets the XS write mask for any custom extension, csrs.cc:595; the genibex extension is one). (5) The draft-B reference
served only grev/gorc (TP-BIT-011/022..033 blocked, batch-1 transcript).

## 2. Red first: the shim unit test (gen_ut_isa_shim.cc sections 5 and 6)

Section 5 added first, against the T-068 shim: 41 FAIL (marchid, mhpmevent3/12, tdata1 read and ignored write, tdata2,
mstatus XS/SD, every draft-B vector, is_draft_b(pack)), then Spike's assert on the second write of `gen_isa_set_time`
(gen_tdd_logs/isa_shim/gen_t102_red1_ut_isa_shim.log; 92 OK from the existing sections). Two test-side corrections during
the red: `gen_isa_is_draft_b` was a DPI-only symbol and is now declared in gen_isa_shim.h; the section-6 program grants
U-mode PMP access (pmp0 TOR RWX) so the U-mode ecall is an ecall and not an instruction access fault (cause 1, plan C-2).
Green after the implementation: 150 OK, 0 FAIL (gen_t102_green_ut_isa_shim.log). The draft-B vectors are literal
(CRC-32 table entries 0x77073096 / 0xee0e612c, CRC-32C 0xf26b8303, zip/unzip 0x0000ffff <-> 0x55555555, the plan's
named slo/sro/fsl/bfp corner cases); the `.h` = `.b` twice check is structural.

## 3. What changed

- gen_isa_shim.h/.cc: step record gains `prv_before`; `gen_isa_set_hpm(idx, lo, hi)`, `gen_isa_set_status(v)`;
  `gen_isa_set_time` writes the 64-bit counter once; `legalize_after_reset` installs marchid (`GEN_CSR_MARCHID_VALUE`),
  mhpmevent3..31 (bit i-3 below `GEN_MHPM_COUNTER_NUM`, 0 beyond), writable mhpmcounter holders with the U-mode aliases,
  the mstatus view without XS/SD (read and write), the tdata1/tdata2 views (debug-mode-only writes, Ibex's fixed mcontrol
  read `GEN_TDATA1_IBEX_RDATA` plus the execute bit); cpuctrlsts carries the status bit; the reference covers pack/packu/
  packh, slo/sro(i), shfl/unshfl(i), xperm.n/b/h, cmov/cmix, fsl/fsr/fsri, bfp, crc32/crc32c .b/.h/.w with rev8, orc.b and
  zext.h excluded as ratified aliases; the custom CSR addresses come from the rendered `GEN_CSR_CPUCTRLSTS/SECURESEED`.
- gen_isa_dpi_pkg.sv: the step import gains `prv_before`; two new imports. Every call site changed in the same edit.
- gen_rvfi_pkg.sv: `step()` returns `prv_b`; before each record step the model receives `t.ext_mcycle`, the
  `GEN_MHPM_COUNTER_NUM` counter pairs and `t.ext_ic_scr_key_valid`; `isa_prv` compares `prv_b`; `isa_pc_next` skips
  `GEN_INSN_MRET`/`GEN_INSN_DRET` records; the draft-B path reads rs3 = insn[31:27] for the R4 forms, compares
  `rvfi_rs3_addr/rdata` and passes it to the reference; the monitor samples the counter words on every record.
- gen_tb_knobs.yaml / gen_knobs_codegen.py: derivations `csr_marchid_value`, `csr_addr_cpuctrlsts`, `csr_addr_secureseed`
  from ibex_pkg (guarded in gen_tb_top like the irq width); literals `GEN_MHPM_COUNTER_NUM` (guarded against
  `u_dut.MHPMCounterNum`), `GEN_INSN_MRET`, `GEN_INSN_DRET`, `GEN_TDATA1_IBEX_RDATA`; codegen unit test PASS (0 failures).
  gen_ut_export.py takes the mret/dret encodings from `CONSTANTS`.
- API documents: gen_component_api_scoreboard.md (rules, sync paragraph, rs3), gen_component_api_isa_shim.md (API,
  Section 4a rows), gen_component_api_rvfi_monitor.md (counters sampled always), gen_component_api_constants_handles.md.

## 4. Green runs on out_t102/tb (all local, seed 1; retained as gen_tdd_logs/<lockstep|export>/gen_<run>_t102_*)

Images: Zc directed (gen_zc_directed.S, 204 words, crc32 cf0cb3b8); riscv-dv seed 7 regenerated for this build (28943
words, crc32 0d384389; the T-068 s7 image, 29375 words / 5c209be0, was not retained and the regeneration is not
byte-identical); the four test programs from the Test Writer's generators, seed 1.

| Run | Verdict | UVM_ERROR | ISA compare |
|---|---|---|---|
| boot_zc | PASS | 0 | records=148 mismatches=0 folded=21 draft_b=0 traps=0 |
| lockstep_zc | PASS | 0 | records=148 mismatches=0 folded=21 draft_b=0 traps=0 |
| bridge_zc | PASS | 0 | records=0 mismatches=0 folded=0 draft_b=0 traps=0 |
| export_zc | PASS | 0 | records=154 mismatches=0 folded=21 draft_b=0 traps=0 |
| export_zc_counters | PASS | 0 | records=154 mismatches=0 folded=21 draft_b=0 traps=0 |
| lockstep_s7 | PASS | 0 | records=2002 mismatches=0 folded=0 draft_b=0 traps=1 |
| export_s7 | PASS | 0 | records=2008 mismatches=0 folded=0 draft_b=0 traps=1 |
| test_rst_boot | PASS | 0 | records=119 mismatches=0 folded=0 draft_b=0 traps=1 |
| test_csr_reset | PASS | 0 | records=282 mismatches=0 folded=0 draft_b=0 traps=0 |
| test_csr_trap_setup | PASS | 0 | records=5189 mismatches=0 folded=0 draft_b=0 traps=70 |
| test_pmp_csr_warl | PASS | 0 | records=7965 mismatches=0 folded=0 draft_b=0 traps=157 |

The four blocked tests carry their own fire-checks (green before and after); their comparator errors went from 8 / 42 /
407 / 532 to 0 with mismatches=0 on 119 / 282 / 5189 / 7965 compared records.

## 5. Mutations

dv/auto_dv/mutations/gen_mut_t102.md (P1..P9): 8 of 8 DUT-run mutations caught with ablation PASS; P8 (cmix)
caught by the unit test. Run artifacts under gen_tdd_logs/mutations/gen_t102_*.

## 6. Not done and owed

- RTL-level mutation halves per isa_* id (Critic D-3) remain owed; `isa_csr` is a later landing.
- The new reference functions have unit vectors only; their DUT-level exercise is the Test Writer's TP-BIT-022..033.
- The step-2b re-application and the T-080 event writers wait behind the v4b verdict (unchanged).
- Debug-mode privilege: rvfi_mode reports `priv_lvl_q` in debug mode (rtl/ibex_cs_registers.sv:996) and Spike keeps
  `prv` across debug entry, so `isa_prv` needs no special case; not yet exercised by a debug test.

## 7. Closing canary (edit pass closed)

After the last mutation revert (both files at their pre-mutation sha256, gen_mut_t102.md) a fresh compile of the tree
(dv/auto_dv/work/tb-infra/out_t102/close; gen_tdd_logs/lockstep/gen_close_compile_t102.log, vcs exit 0) ran boot_zc,
lockstep_zc, lockstep_s7 and export_zc: all PASS, UVM_ERROR 0 (gen_tdd_logs/<lockstep|export>/gen_close_*_t102_*). The
retained-log manifest (gen_tdd_logs/gen_manifest.md) carries one row per retained file (bytes, md5, source); no file
under gen_tdd_logs lacks the gen_ prefix.
