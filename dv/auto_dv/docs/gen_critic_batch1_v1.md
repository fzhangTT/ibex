# Critic verdict: Phase 1 batch 1 (commit cb3d7eb, Test Writer), eight tests, dv-principles check and mutation audit

Artifacts at commit cb3d7eb (sha256 first 16 hex, lines / bins):
- gen_test_rst_boot.py 817bd6cb678800ea 169 | gen_rst_boot_prog.py 540cb40cf2ca8799 345 | manifest 55d23e38e372982a 42 bins
- gen_test_csr_reset.py f2b03e3d5c79a276 175 | gen_csr_reset_prog.py 057e57e9e674fa34 407 | manifest 1b2f5dc1a524eb84 81 bins
- gen_test_csr_access.py 7d327b2ee82dacf4 112 | gen_csr_access_prog.py 2bcdc3761851347b 774 | manifest 9a8fcb766fdeb8cd 83 bins
- gen_test_csr_trap_setup.py 503010aa481d0f97 150 | gen_csr_trap_setup_prog.py 51df9dffd025602e 769 | manifest 24a69b30eed575e4 206 bins
- gen_test_cmp_zcb.py f0fca632e5525a1e 90 | gen_cmp_zcb_prog.py 001b2d161ff87b15 394 | manifest d81aa81aaab1ab26 110 bins
- gen_test_cmp_zcmp_basic.py 2f072ddba4462a82 273 | gen_cmp_zcmp_basic_prog.py f2bc123f95b63a7b 714 | manifest f67d659b10a46741 479 bins
- gen_test_bit_draft.py 83c5876ba3419697 85 | gen_bit_draft_prog.py 9587627900af197d 331 | manifest b943b27b1992ca14 480 bins
- gen_test_pmp_csr_warl.py ebce2982682e641a 226 | gen_pmp_csr_warl_prog.py 8d5e18a17838a556 1030 | manifest 6a53bd359c4d8243 266 bins
- gen_test_template.py and gen_test_lib.py changes (report_count hook; gen_mmio_map.h check), gen_fcov_manifest.py (YAML
  quoting), gen_programs/gen_mmio_map.h (10 lines). Local runs (untracked, the retention commit is to copy them):
  dv/auto_dv/work/test-writer/out_head/<group>_{s1,s2,red1}/ (24 runs) and batch1/<group>/ (program generation).
Date: 2026-09-03T11:23Z   Role: Critic. Method: docs/dv/dv_principles.md read fresh; two delegated read-only passes (four tests each,
unnamed subagents, fence stated) produced candidate findings with file:line; every finding below marked (V) was re-read
by me in the committed text or verified against a log, those marked (D) rest on the delegated pass and were
spot-checked in pattern only. LOG-018 read. No test was run by me (Runtime runs tests); the 24 local runs were audited.

CRITIC VERDICT: REQUEST-CHANGES (one high on the committed tree's self-consistency; four mediums; the T-102 attribution
to the TB is RIGHT on all three heads, section 2)

## 1. Cross-cutting findings

### H-1 (high) [S6 fcov-expectation; S4 evidence over prose]: the committed tree cannot pass its own finish() (V)

- Every test's declare_bins() returns [] (gen_test_rst_boot.py:163, csr_reset:169, csr_access:106, csr_trap_setup:144,
  cmp_zcb:84, cmp_zcmp_basic:267, bit_draft:79, pmp_csr_warl:91, each with "no covergroup exists yet"), while the same
  commit adds dv/auto_dv/fcov_expectations/gen_test_<group>.fcov.yaml with 42 / 81 / 83 / 206 / 110 / 479 / 480 / 266
  bins. The template's finish() (gen_test_template.py:314-315) calls lib.check_manifest_matches whenever a manifest file
  exists, and gen_test_lib.py:326-331 asserts the manifest equals declare_bins(). On the committed tree every one of the
  eight tests therefore raises "GEN_TEST_LIB: manifest of <test> differs from declare_bins()" before its PASS marker.
- The 24 local runs did not see this because they predate the manifests: run logs 06:17:43 to 06:49:08 local, the
  eight manifests written 06:54:40-42, the commit at 06:58:09 (all -0400). Every run logs GEN_TEST_BINS n=0 and no
  manifest message. So "green on seeds 1 and 2" (LOG-018) is true of a tree that was never committed, and the
  committed tree has never been run.
- Required: declare_bins() returns lib.load_manifest_bins(self.name) or [] in every test (or the manifests are not
  committed until gen_fcov_pkg exists, and the docstrings say so), and one green run per test on the committed tree is
  retained with the manifest present. Until covergroups exist the manifests must also be excluded from the flow's
  fcov check (fcov_expectation_file: null in the entries), which the Test Writer plan already states.

### M-1 (medium) [S6 rule 3: declared-but-unhit bins fail the run] (D, counts from the delegated pass)

The manifests are rendered for the whole plan group while each test builds a subset of its items: rst_boot 34 of 42
bins belong to unbuilt items (cp_hart_id, boot_addr_change, cp_reset_kind, ...), csr_reset 34 dcsr/dpc/dscratch/mip
bins, csr_access the f3_100 and secureseed-gap bins, csr_trap_setup the TP-CSR-026/031 bins, bit_draft 13 of 14 items
unbuilt, cmp_zcmp_basic TP-CMP-068. When the covergroups land these tests cannot be green against their own
manifests. Required: render the manifest for the built items only (--items) and list the excluded items with the
reason in the test docstring, or split the groups (the plan permits it) and update Section 3.

### M-2 (medium) [plan Section 0 witness rule] (V)

gen_test_csr_trap_setup.fcov.yaml carries gen_wit_cycle_clause_cg.cp_clause.w_tp_csr_029 and w_tp_csr_031 (4 lines)
although both items carry the marker token, which Section 0 says excludes the witness bin from the manifest.
gen_fcov_manifest.py has rules (a)-(e) and no token rule. Required: the token exclusion in the generator, the manifest
re-rendered (the other seven manifests carry no witness bin).

### M-3 (medium) [S6 self-proving checks] (V)

Each red fixture trips exactly one fire-check: rst_boot fire_tp_rst_006, csr_reset fire_tp_csr_106, csr_access
fire_tp_csr_001 (see the test section: it can trip all five on half the seeds), csr_trap_setup fire_tp_csr_036,
cmp_zcb fire_tp_cmp_036, cmp_zcmp_basic fire_tp_cmp_039 (+2 related), bit_draft fire_tp_bit_016_gorci,
pmp_csr_warl fire_tp_pmp_001. The other 40-odd fire_* checks in the batch have never been seen failing. Required:
--red <item> selecting a per-item deviation, one red run per fire_* method, retained (may land with the retention
commit; the count per test is listed in section 3).

### M-4 (medium) [S4 don't hide failures / silent down-scope] (V)

Stimulus bent around TB defects instead of reporting them: gen_csr_access_prog.py:589-590 and :615-620 read marchid,
cycle and hpmcounter3..12 with rd = x0 ("value not comparable against the shim") so the wrong shim values never reach
the comparator and no checker observes the value at all; gen_pmp_csr_warl_prog.py:576-577 refuses LRWX = 1111 under
MML with RLB = 0 because "shim legalisation not pinned". Both are T-102 items. Required: read with rd != x0 and let the
comparator show the shim gap (the four failing tests already do exactly that), or mark the clause blocked on T-102 in
the docstring and the plan; never shape the program to avoid an observation.

### Lows

- L-1 layers_required = False on all eight tests (bring-up escape hatch); acceptable only with measured: false entries,
  which exist as staged requests (batch1/requests_staged) but not yet in gen_testlist.yaml at cb3d7eb (Runtime copies).
- L-2 [S5 single source] CSR address tables, W-tables, MSTATUS reset, the build-config name and the tohost codes are
  re-typed per generator (D; CONFIG_NAME and GP_PASS/GP_FAIL in gen_pmp_csr_warl_prog.py:42, :98 verified against
  lib.TOHOST_PASS). One gen_programs constants module.
- L-3 gen_test_csr_access.py:11 and gen_csr_access_prog.py:34 carry "passed 82/82 in bring-up" (history in a docstring).
- L-4 The Zcmp and Zcb docstrings cite "rvfi_insn = the 16-bit encoding" for c.* records; consistent with
  rtl/ibex_core.sv:2263-2264 and with C-12 for non-Zcmp; fine, noted only because C-12 gives the expansion for Zcmp
  micro-ops.

## 2. T-102 attribution: are the four flow FAILs the TB's? YES, on all three heads (V)

The four tests (rst_boot, csr_reset, csr_trap_setup, pmp_csr_warl) log GEN_TEST_PASS at cocotb level with
UVM_ERROR totals 8 / 42 / 407 (s2 477) / 532 (s2 556) from the lock-step comparator, so the flow verdict is FAIL
(uvm_error), which is the collected-mechanism behaviour I asked for in step 1b. Classified from the s1 logs:

1. mret target: every isa_pc_next miss in csr_trap_setup_s1 (70 of 70) is on insn 30200073 (mret) with dut pc_wdata
   equal to pc + 4 and the model at the mepc target. RTL: rtl/ibex_core.sv:2084 captures pc_wdata as
   `pc_set ? branch_target_ex : pc_if` when the instruction leaves ID, and the mret's pc_set comes one cycle later in
   FLUSH (rtl/ibex_controller.sv:953-965); plan convention C-1 says the same. The comparator (gen_rvfi_pkg.sv:366)
   compares the model's post-step pc for every non-trap record. TB defect: treat mret and dret like traps (:333-338),
   i.e. compare the NEXT record's pc_rdata against the model pc. The plan and the tests are right.
2. isa_prv: 61 of 65 misses in pmp_csr_warl_s1 are on ecall (00000073) and the rest on mret; the pattern is
   "priv model=0 dut mode=3" on mret and the inverse on ecall. rvfi_mode is priv_mode_id captured when the instruction
   leaves ID (rtl/ibex_core.sv:2078), the privilege the instruction EXECUTED in; the comparator (gen_rvfi_pkg.sv:369-370)
   compares the model's privilege AFTER the step. TB defect: compare the pre-step privilege (or the previous step's).
3. Shim CSR gaps: isa_rd misses on 7c006bf3 (cpuctrlsts read, dut 0x100 = ic_scr_key_valid bit 8, model 0: the shim
   masks 0x7C0 with 0xFF, gen_isa_shim.cc:142), 7a1024f3 (tdata1, dut 28001048 = the Ibex reset value, model f0000000),
   32502973 (mhpmevent5, dut 4 = 1 << (5-3) per D20, model 0), and 160 of 207 isa_rd misses in csr_trap_setup_s1 on
   0x300 (mstatus reads). The isa_mem misses are the report stores of those same values (consequential). The test
   expectations for these values were checked against the RTL by the delegated pass (marchid 22, tdata1 0x28001048,
   cpuctrlsts bit 8, D20) and hold. TB (shim) defects; some are already DEFERRED rows of the shim API section 4a
   (tdata, mhpmevent masks); cpuctrlsts bit 8, marchid and the mstatus read value are not declared there and must be.

The attribution stands. The one thing the Test Writer got wrong is the response in M-4: two tests avoid the
observation instead of letting the comparator report the gap.

## 3. Per test

### 3.1 gen_test_rst_boot (group gen_rst_boot, 3 of 11 items built; s1/s2 cocotb PASS, UVM_ERROR 8; red1 fails fire_tp_rst_006)
- Fire-checks (V): fire_tp_rst_003 mtvec report = boot page | 1 from +gen_boot_addr and MEMORY_MAP; fire_tp_rst_006
  mstatus/mie/trap cause/mepc/pad result from the program; fire_tp_rst_007 30 shuffled reset reads vs constants and the
  key-regime-derived cpuctrlsts bit 8. Not built: TP-SEC-031, TP-RST-001/002/004/005/008/027, TP-RVFI-036 (listed with
  reasons). Red: MPIE flipped in the stored mstatus word, real intent failure, rng-aligned (V).
- Findings: M-1 (34 of 42 bins unbuilt). (D) gen_rst_boot_prog.py:61 PMP_REGIONS = 16 and the zero PMP reset table
  re-typed where the sibling generators read PMPNumRegions from ibex_configs.yaml [S1 future-proof] (medium-low).
  (V) gen_test_rst_boot.py:79 knob values "immediate"/"delayed" as string literals; a renamed value turns the bit-8
  expectation into None, i.e. permanently ungated [S2 predict-and-check, S5] (medium-low): derive from lib.knob_values.
  (D) TP-RST-006's "interrupt line held high" and "rvfi_mode = 3" clauses dropped without being listed (low).
  (D) failure detail dumps every report word (low).
- Verified OK (D): MSTATUS reset 0x80, TDATA1 0x28001048, mtvec reset, cpuctrlsts bit 8 against rtl/ibex_cs_registers.sv.

### 3.2 gen_test_csr_reset (group gen_csr_reset, 6 of 6; s1/s2 PASS, UVM_ERROR 42; red1 fails fire_tp_csr_106)
- Fire-checks (D): one per item over prog.bounds() (spec/doc constants, boot address, hart id, key regime, cycle and
  instret windows from the program index); TP-CSR-037 mtvec stability; TP-CSR-107 counter pair relations. Red: non-zero
  csrw to mscratch replacing a setup instruction, rng-aligned (D).
- Findings: (V) gen_test_csr_reset.py:59-68 derives the key regime from the command line default and ignores the
  layer-2 draw (test.knobs) that rst_boot's _knob_regimes handles [S2 predict from sampled config] (medium): once
  REGIME_SET lands a seed drawing withheld_then_valid fails for the wrong reason; "never + 2" unexplained. (D) plan
  TP-CSR-105/106/109 "within the first 16 (40) retirements" neither programmed nor asserted although Report.idx gives
  the retirement position [S4] (medium). (D) mip expected 0 while knob_irq_line_mix is declared schedulable (low).
  (D) MCYCLE_SLACK/INSTRET_SKEW literals without a shared home (low). M-1 (34 bins).
- Verified OK (D): MISA 0x40901104, MARCHID 22, MCONFIGPTR 0, counter map, mcountinhibit bit 1, mstatush/menvcfg read 0.

### 3.3 gen_test_csr_access (group gen_csr_access, 5 of 6; s1/s2 PASS, UVM_ERROR 0; red1 fails fire_tp_csr_001)
- Fire-checks (D): five items over prog.evaluate (rd = pre-op value, read-back = Zicsr op + WARL legalisation, minstret
  exact, mhartid, mvendorid/mimpid from gen_dut_top parameters); the final trap-count word under TP-CSR-001. TP-CSR-005
  not built (the comparator C-1 row, correctly attributed).
- Findings: (V) gen_csr_access_prog.py:422-426 red forces op = "csrrw" after the green draw; when the drawn op was an
  immediate form the red build takes the register branch and consumes different rng draws, so every later block
  diverges from the green plan the test evaluates and all five fire-checks fail, not the named one [S6 rule 1]
  (medium; the retained red1 shows 1 failure, so seed 1 drew a register form). Fix: keep the drawn op and flip one
  writable operand bit. (V) M-4 rd = x0 reads (:589-590, :615-620). (D) :214-221 constrain(pmpcfg) forces R when W, so
  the W-dropped legalisation branch is never exercised (low). (D) TP-CSR-001 "every op class at least once" not
  asserted (low). (V) L-3 history in the docstring. (D) HANDLER_LEN and tolerance literals (low).
- Verified OK (D): mstatus MPP legalisation, mtvec, mcause model, pmpcfg W rule, mie mask from GEN_IRQ_FAST_MASK.

### 3.4 gen_test_csr_trap_setup (group gen_csr_trap_setup, 9 of 11; s1/s2 PASS, UVM_ERROR 407/477; red1 fails fire_tp_csr_036)
- Fire-checks (D): nine items plus fire_program_integrity (trap count 0, last cause 0, retired >= floor, tohost = pass);
  U-mode entry observed as ecall cause 8 vs 11 (intent-derived proxy); directed pins inside the random stream for
  missed corners. Red: bit 8 of one absolute csrrw operand flipped in the program only, single item (D).
- Findings: M-2 (witness bins). (D) TP-CSR-035 handler copies all inside the image, so the low / boot base classes are
  unreachable and not listed as dropped [S4] (medium). (D) invented equal weights for the TP-CSR-027/028 patterns
  where W-PAT applies (low). (D) csrrsi operand limited for the standalone Spike run (low, documented).
- Verified OK (D): MST_MASK bit positions, mret MPRV/MPIE/MPP, mie and mtvec legalisation, Sym alignment assert.

### 3.5 gen_test_cmp_zcb (group gen_cmp_zcb, 3 of 3; s1/s2 PASS, UVM_ERROR 0; red1 fails fire_tp_cmp_036)
- Fire-checks (D): three items via _compare over report words; expectations from a Python byte-memory model and ALU;
  the store checks are real round-trips (c.sb/c.sh then lw). Red: one ALU op re-emitted as another form.
- Findings: M-3 (red covers 036 only). (D) no program-verdict check (tohost code, retirement floor) unlike the other
  seven [S2 verify every transaction] (low). (D) rvfi_mem_rmask/wmask and split-access clauses handed to always-on
  checkers without naming the export dependency (low).
- Verified OK (D): weighted per-seed draws plus exhaustive shuffled must-cover sets; sensitizing operands; no comparator
  reliance.

### 3.6 gen_test_cmp_zcmp_basic (group gen_cmp_zcmp_basic, 17 of 18; s1/s2 PASS, UVM_ERROR 0; red1 fails 3 related fire-checks)
- Fire-checks (D): fire_program_verdict plus one per built item over frame words, sp, all rlist registers, ret markers,
  minstret pairs, with the expectation from the emitter's Zcmp model and the image symbol table. TP-CMP-068 not built
  (reason stated). minstret delta 2 across csrr; cm.*; csrr matches the plan (TP-CMP-055) and rtl/ibex_id_stage.sv:1218-1220.
- Findings: M-3. (D) TP-CMP-039 "each combination >= 3 times" emitted once (low). (D) b2b push/pop with the same rlist
  restores every register, so the register records cannot detect a pop that loads nothing (low): pop a different rlist
  at equal stack_adj. (D) csrwi 0x320 literal and plan-pinned combos typed in the test (low). (D) icache precondition of
  TP-CMP-066/073 not programmed and not stated (low).

### 3.7 gen_test_bit_draft (group gen_bit_draft, 1 of 14; s1/s2 PASS, UVM_ERROR 0; red1 fails fire_tp_bit_016_gorci)
- Fire-checks (V): fire_tp_bit_016 emits per-base value compares, alias, report count, retired floor and tohost; the
  reference is a Python grev32/gorc32 from the draft definition; 13 items BLOCKED on the shim's C5.5 references.
- Findings: (V) plan TP-BIT-016 requires every immediate 0..31 and every rs2[4:0] value observed; the generator draws
  36-44 ops with random controls and the test asserts nothing about control coverage while items["controls"],
  single_bit_ops, nonzero_upper_ops and chained_ops (gen_bit_draft_prog.py:263-268) are computed and never read
  [S1 the directed floor inside the random stream; S6] (medium). (D) rd = x0 and zero-operand ops give vacuous 0 == 0
  compares counted as ops (low). (D) the 13 blocked items name no owner or alternative (low). M-3.

### 3.8 gen_test_pmp_csr_warl (group gen_pmp_csr_warl, 8 of 8; s1/s2 PASS, UVM_ERROR 532/556; red1 fails fire_tp_pmp_001)
- Fire-checks (D): fire_program_verdict, fire_program_layout and one per item over report words (WARL read-backs, RMW
  rd, handler trap records, probe results) against a Python PmpModel; counts from ibex_configs.yaml with a G = 0
  assertion. Red: A[0] flipped on one csrrw, real WARL mismatch.
- Findings: (V) M-4 LRWX refusal. (D) gen_pmp_csr_warl_prog.py:5-8, :125-130 cite the RTL g_pmp_registers as a source
  of the model's rules [S2 derive from intent, never from an RTL net] (low-medium): the rules are spec-derivable
  (machine.adoc, smepmp.adoc, cs_registers.rst) and the citations should say so, RTL "cross-checked" only.
  (D) layout-relative pmpaddr expectations resolved from DUT-reported base words instead of the symbol table (low).
  (D) C-2's U-RW data region not programmed and not stated (low). (D) "granularity 4" wording for G = 0 (nit).

## 4. Evidence audit

24 local runs under work/test-writer/out_head, stdout.log mtimes 06:17:43 to 06:49:08 local, each with sim.log:
s1/s2 of every test log GEN_TEST_PASS and GEN_TEST_BINS n=0; red1 of every test raises GEN_TEST_FAIL with exactly one
named fire-check (three for cmp_zcmp_basic); the four comparator-failing tests carry the UVM_ERROR totals above. All
of it is untracked; the retention commit must copy the 24 runs (stdout.log, sim.log, run header, verdict) with a
manifest, and after H-1 is fixed a fresh green per test on the committed tree.

## 5. Required before re-review

1. H-1: declare_bins() returns the manifest (or no manifest is committed), one committed green per test on that tree.
2. M-2: token exclusion in gen_fcov_manifest.py; csr_trap_setup manifest re-rendered.
3. M-1: manifests rendered for built items (or groups split), exclusions listed.
4. M-4: rd = x0 dodges and the LRWX refusal removed or declared blocked on T-102 in the docstrings and plan.
5. M-3: per-item red fixtures, retained (may land with the retention commit).
6. The mediums of 3.1 (knob literals), 3.2 (layer-2 draw), 3.7 (control enumeration) and the lows as time allows.
The T-102 fixes are tb-infra's; the four blocked tests re-run after them without changes on the test side.
