# Critic verdict: tb-infra landing 8, T-235 counter CSRs in the ISA model (commit 158f5be, diff base 754bf42), reviewed as tb_l9

Artifacts reviewed (committed blobs at 158f5be; sha256 first 16 hex):

- dv/auto_dv/isa/gen_isa_shim.cc  34559ec691021abd
- dv/auto_dv/isa/gen_isa_shim.h  d856d6baa833892f
- dv/auto_dv/isa/gen_isa_shim_counters.cc  238f899ff36bdfc0
- dv/auto_dv/isa/gen_isa_shim_counters.h  a1fec0628276d19a
- dv/auto_dv/isa/gen_ut_isa_shim.cc  c30369dd144e93fa
- dv/auto_dv/isa/gen_isa_shim_build.sh  d8a8ce42d63bb012
- dv/auto_dv/isa/gen_isa_dpi_pkg.sv  5c5d2fbbe4eccfd2
- dv/auto_dv/env/gen_rvfi_pkg.sv  ae982e87b02d192a
- dv/auto_dv/evidence/gen_tdd_step2b.md  4b515eb373354f49
- dv/auto_dv/mutations/gen_mut_step2b.md  8607456a666b051f
- dv/auto_dv/evidence/gen_tdd_logs/gen_manifest.md  8cdf49f0437c5038
- dv/auto_dv/docs/gen_component_api_isa_shim.md  ddf864b8bbc587c5
- dv/auto_dv/docs/gen_component_api_scoreboard.md  12919480b8c5dd4b
- dv/auto_dv/evidence/gen_counter_csr_anchors.md  b16678949f12a59b
- dv/auto_dv/evidence/gen_tdd_logs/lockstep/gen_fu_l9_sources_sha256_z.txt  e845572967179ff0
- dv/auto_dv/evidence/gen_tdd_logs/lockstep/gen_fu_l9_gen_t235_hashes.txt  d10f4bb247f78bf8
- dv/auto_dv/evidence/gen_tdd_logs/lockstep/gen_fu_l9_gen_t235_README.md  4dc34ca22495e207
- dv/auto_dv/evidence/gen_tdd_logs/lockstep/gen_fu_l9_pmc_s1_program_provenance.txt  4a40819d34afe506
- the 61 gen_fu_l9_* files under dv/auto_dv/evidence/gen_tdd_logs/{lockstep,mutations}/ (manifest rows recomputed 61/61)

Date: 2026-09-03 (UTC). Role: Critic (reviewer other than the author). Basis: docs/dv/dv_principles.md d9c27db18f511411;
rtl/ibex_counter.sv:30-49; rtl/ibex_cs_registers.sv:304, :402-406, :580-640, :1553-1570, :1588, :1605-1618, :1622-1658; rtl/ibex_id_stage.sv:746-748,
:1213-1220; rtl/ibex_wb_stage.sv:107-115, :200-208; tools/riscv-isa-sim/riscv/csrs.cc:771-798, :1321-1345 (Spike's rv32 wrappers and the
written flag); doc/03_reference/performance_counters.rst; dv/auto_dv/evidence/gen_counter_csr_anchors.md section 10.
Method: clean archive of 158f5be. Build z identity checked first-hand: the recipe of gen_tb_local.sh on the archive gives e845572967179ff0
under the UTF-8 sort, equal to the 13 build-z run headers, the compile log and the sha256 of the retained per-file list (69 lines, byte-identical
to my recompute). Flow self-test, library self-test and both codegen --check runs PASS from a detached worktree of 158f5be (the Orchestrator's
recipe; this closes the flow self-test caveat of gen_critic_tb_l7.md's Method line). The RTL retirement timing below was traced by me before
the shim's rules were read against it. One unnamed subagent (an evidence audit of the 61 files, told the fence, kept out of dv/auto_dv/reviews/),
its findings re-checked in the blobs. EXPOSURE: the Orchestrator's hand-off named the landing's cross-model artifact's two majors (the write
half inferred from the value at gen_isa_shim.cc:238-240; the gap-1 rule on back-to-back writes) and its minor on the red log's test sha, and
the subject of commit d9f66c6 names the artifact's level; both corners were re-derived here from the RTL and Spike's sources before the
artifact was read (Section 7 reconciles). The DV Lead's A2c-1..7 rows on landing 2c are tb-infra's next touch, not this file's.

CRITIC VERDICT: REQUEST-CHANGES. The holders, the inhibit rule, the writer exclusion and the U-mode aliases are derived from the RTL and proven
(unit test red and green, MUT-CNT with ablation, 8000-record lock-step greens on an identified build). The two write corners the landing
says it decided are wrong in the canonical counter-clearing idiom `csrw minstret, x0; csrw minstreth, x0`: the written half is inferred
from the value and a back-to-back writer is treated as a counted retirement, each giving a false isa_rd miss. Two mediums, five lows.

## 1. What was verified

RTL timing (my trace). A CSR write lands when the instruction completes ID/EX (csr_op_en = csr_access & instr_executing & instr_id_done,
rtl/ibex_id_stage.sv:746-748), the counter is loaded at that edge and the load wins over an increment in the same cycle
(rtl/ibex_counter.sv:44-49). Retirement is counted one cycle later, when the instruction is done in WB (perf_instr_ret_wb = instr_done_wb &
wb_count_q, rtl/ibex_wb_stage.sv:200-208), gated by mcountinhibit[2] at that cycle (rtl/ibex_cs_registers.sv:1643). A minstret / minstreth
writer is excluded from counting altogether (instr_perf_count_id_o carries ~minstret_write, rtl/ibex_id_stage.sv:1213-1220). So: the
instruction retiring in a write cycle loses its increment; the writer itself adds nothing; an inhibit written by a csrw applies to that
csrw's own retirement (the state it leaves behind).

| rule | as built | RTL / spec anchor | evidence |
|---|---|---|---|
| mcountinhibit holder | mask 0x1FFD from GEN_MHPM_COUNTER_NUM, bit 1 and 31:13 read 0, reset 0; Spike's own inhibit untouched so Spike's minstret keeps counting | :304 (13 flops), :1553-1561 (bit 1 forced 0), :568 read | unit test 14 (23 rows) with the red on the pre-integration holder (mask rows FAIL, 0xfffffffd / 0x2004) |
| zero holders mhpmcounter13..31(h), mhpmevent13..31 | read 0, writes ignored, no trap in M | read mux :580-640 lists all 3..31 without illegal_csr; no write arm beyond MHPMCounterNum; mhpmevent 13..31 tied 0 (:1614-1618) | unit test 14 rows (csrw mhpmcounter13 / 31 retire, read 0) |
| inhibit rule (the state left behind) | g_inh += retired after the step when the holder's IR is set (gen_isa_shim.cc:520); Spike's counter minus g_inh is Ibex's value | the trace above (:1643 with the write one cycle before the writer's retirement) | pmc seed-1 image: 8000 / 8001 records, 0 mismatches, pin on and off, build z; MUT-CNT (the accounting removed): 91 isa_rd misses, first at order 2108 (csrr instret), ablation `+gen_chk_isa_rd=0` PASS, original sha = committed blob, build = its compile log |
| the writer not counted | Spike's written flag skips the writer's increment; retired forced to 1 for the writer (:519) | rtl/ibex_id_stage.sv:1213-1220 (~minstret_write, minstret and minstreth), also gen_counter_csr_anchors.md:33, :121 | unit test 15 "csrw minstret V reads V" (the red: 0x12345675) |
| retirement derivable under IR = 1 | Spike's counter keeps counting, retired = its delta | the holder replaces mcountinhibit in Spike's csrmap only | red row "a step under IR = 1 still retires got 0x0 exp 0x1", green |
| U-mode aliases | CSR_INSTRET / INSTRETH through Spike's counter_proxy_csr_t on the proxy: legal iff mcounteren.IR; hpmcounter13 in U traps | :622-623, :635-636 illegal_csr = (U) && !mcounteren[idx]; mcounteren bits above 12 do not exist (:1565-1568) | unit test 14 (mret to U, csrr hpmcounter13 traps, cause 2, mtval = insn) |
| the two write corners | gap 1 and IR clear at the write: high write g_inh = 1 (the low word reloaded pre-increment), low write on a just-wrapped Spike low word g_inh = 2^32 (the carry Ibex never took) | rtl/ibex_counter.sv:35-49; the gap = record cycle minus the previous record's (gen_rvfi_pkg.sv:453) | unit test 15 (four corner rows); no lock-step run writes minstret (the pmc image writes mcountinhibit / mcounteren and reads); see M-1, M-2 |
| retirement-gap DPI | gen_isa_set_retire_gap(t.cycle - last_cycle) before every step | rvfi records are stamped at WB done, so gap 1 = the previous instruction retired in the write cycle | the trace above |
| scoreboard doc row | minstret / instret are the model's own since T-235, other counters record-synced | code: only mcycle is synced (gen_isa_set_time) | consistent |

Regression greens on z (boot_zc, lockstep_zc / _s7 / _csrwarl / _irq_storm / _s7_dbg_storm / _zcmp_mv / _muldiv, intg_s7_allchk, ut_isa_cov_zc,
ut_witness) all PASS with verdicts retained; Runtime's counters.h / .cc hashes in gen_fu_l9_gen_t235_hashes.txt equal the committed files.

## 2. Findings

### M-1 (medium) [S2 derive from intent] The written half is inferred from the value, so a same-value minstreth write takes the wrong corner

gen_isa_shim.cc:239-240 `high_write = ((val ^ cur) >> 32) != 0`. Spike's rv32_high_csr_t hands the proxy a composed 64-bit value
({val, current low}, tools/riscv-isa-sim/riscv/csrs.cc:793-794), so a minstreth write of the value it already holds is indistinguishable
from a low write. The canonical clearing idiom `csrw minstreth, x0` with minstreth = 0 (every program that zeroes the counters) at
gap 1 then takes the low branch: g_inh = 0 (or 2^32 when Spike's low word had just wrapped) where the RTL reloads the low word with its
pre-increment value (rtl/ibex_counter.sv:40, :44-47), and the model reads one more than Ibex on the next csrr: a false isa_rd miss.
Both high-write rows of unit test 15 change the high word (0x12345678, then 5), so the case is untested. Required: know the half from
the wrapper (own rv32 low / high wrappers that tell the proxy which half is written, or compare against each half's written_value), a
same-value minstreth row in section 15, and a directed lock-step program with the idiom (the red before the fix, the green after).

### M-2 (medium) [S2] The gap-1 rule counts a back-to-back writer as a lost retirement

:242-244 subtract one retirement when the previous record retired in the write cycle, assuming Spike counted it and Ibex lost it. When
that record is itself a minstret / minstreth writer, neither counted it: Spike's written flag skipped it and Ibex excluded it
(rtl/ibex_id_stage.sv:1213-1220, wb_count_q = 0), so there was nothing to lose and the model reads one less than Ibex. The idiom
`csrw minstret, x0; csrw minstreth, x0` back to back hits it on the second write (and M-1 as well when minstreth is 0). Unit test 15
avoids it: its second minstreth write is at gap 0 ("csrw minstreth, x7 (gap 0)"). Required: skip the corner when the previous record was
a minstret writer (the previous step's g_minstret_written), the back-to-back pair at gap 1 in section 15, and the idiom in the directed
program of M-1.

### L-1 (low) [S6 identity] The reds run on unidentified files

Build y of gen_fu_l9_lockstep_pmc_s1_on_red / _off_red (e493e548da55b9ce) has no compile log, no sources list and no shim hash in the
archive; the unit-test red is stamped shim 1b51fec23d35a589 ("HEAD's gen_isa_shim.cc with an inert gap setter", the manifest says) and
test 36128fb905fc4f4e (17 rows in section 15 against the committed 24), neither a committed blob. The reds are real and their role is
the narrative; the mechanism's proof is MUT-CNT and the z greens, both identified. Retain the variants' diffs against the committed
files beside the red logs, as gen_critic_tb_l7.md L-7 asked for the shim red.

### L-2 (low) [S4 record] Figures and anchors

Section 15 is "28 rows" in gen_tdd_step2b.md, "21 rows" in the API doc and 24 in the log and the source; "8000 records, 0 mismatches,
pin on and off" (record, scoreboard doc, commit subject) where the pin-off run has 8001; "47 isa_rd (29 csrr minstret, 2 csrr instret,
the rest their consequences)", "every one DUT = model + 1" and "every record under IR = 1 an isa_trap mismatch" have no retained line
(the reds carry 60 and 52 errors with 12 kept each, isa_mem rows and +2 values among them); rtl/ibex_cs_registers.sv:1627 (record, API
doc, shim comment at :520) is mcycle's inhibit line, minstret's is :1643; the two pmc greens ran after the z driver's end line and are not
in it.

### L-3 (low) [S5 dead state] g_ir_at_step is assigned and never read

gen_isa_shim.cc:212, :285, :503: a leftover of the first form of the inhibit rule. Remove it, or use it in a row that shows the two forms
differ.

### L-4 (low) [S6 mutation hygiene] The canary and the mutated text

The MUT-CNT batch's `source tree untouched` line hashes gen_rvfi_pkg.sv, not the shared tree's gen_isa_shim.cc, and the mutated line the
row quotes (`else if (false) g_inh += retired`) is not retained. The same two points as gen_critic_tb_l8.md L-5; make the canary the
mutated file's shared-tree copy and retain the mutant diff from the next batch on.

### L-5 (low) [S4] Runtime's delivery claims carried as delivered

gen_fu_l9_gen_t235_README.md says "236 rows OK" for Runtime's out-of-tree run whose log (gen_t235_ut_run.log) is not retained, and the
committed test has 224 + 23 = 247 rows through section 14; Runtime's gen_ut_isa_shim.cc hash (a9baa213...) matches no committed file,
as expected for a merged section. One sentence in Section 12 saying the README's figures are Runtime's unretained claim.

### Informational

- I-1: the shim comment on the writer cites Spike's written flag only; the rule is Ibex's too (rtl/ibex_id_stage.sv:1213-1220, already in
  gen_counter_csr_anchors.md:33). Add the RTL anchor.
- I-2: a third sub-corner exists (a high write at gap 1 while Spike's low word had just wrapped: Ibex keeps 0xFFFFFFFF low, the model
  subtracts one) and is out of reach in practice; state it with the hazard variant.
- I-3: the flow self-test now passes for me from a detached worktree; the archive failure of gen_critic_tb_l7.md's Method line was the
  git-history case, as the Orchestrator said.

## 3. Principles check

dv-principles-check (docs/dv/dv_principles.md d9c27db18f511411): S2 derive from intent: holders, inhibit rule, writer exclusion and aliases
follow the RTL (conforming); the two write corners do not in the canonical idiom (M-1, M-2). S4 honesty: the unmodelled hazard variant and
dummy instructions are stated (conforming); the figures of L-2. S6 trust triad: red and green of the unit test, MUT-CNT with ablation on
an identified build (conforming); the reds' files unidentified (L-1). One-line verdict: FAIL on M-1 and M-2 until fixed.

## 4. Required for re-review

1. M-1: the half known from the wrapper; a same-value minstreth row; the idiom program red then green.
2. M-2: the corner skipped after a writer; the gap-1 pair row; the same program.
3. L-1..L-5 with the same touch.

## 5. Verdict

CRITIC VERDICT: REQUEST-CHANGES (M-1, M-2). The landing's rules are RTL-derived and proven where a run exercises them; the write corners
are decided on paper and wrong for the one idiom every counter test uses.

## 6. Reconciliation with the cross-model artifact (dv/auto_dv/reviews/2026-09-03-claude-diff-754bf42c-158f5bee.md, read after Sections 1-5 were written)

APPROVE-WITH-CHANGES, two majors and nine minors; no build or run performed by it either.

- Its two majors are my M-1 and M-2, re-derived here from rtl/ibex_id_stage.sv:1213-1220, rtl/ibex_counter.sv:35-49 and Spike's
  rv32_high_csr_t before the artifact was read; the same idiom, the same fixes. It adds the spurious 2^32 branch of the same-value case
  (model minstreth 0xFFFFFFFF against DUT 0), which is inside M-1's mechanism.
- Adopted and verified in the blobs, all lows, added to the list owed with the mediums:
  - last_cycle is updated only on the path that reaches gen_rvfi_pkg.sv:453; the folded Zcmp micro-op return (:388) and the draft-B
    returns (:417, :437) skip it, so a minstret(h) write right after a Zcmp sequence or a draft-B op measures its gap from an earlier
    record and misses its corner (verified: the three returns precede :453). Update last_cycle before any early return.
  - the carry test at :244 reads Spike's raw value (pre) where Ibex's visible low word is cur = pre - g_inh; after an inhibit episode the
    two wrap at different instants. Test cur.
  - the corner applies to a TB-side write too (:242 has no g_in_step guard); the unit test hides it with gen_isa_set_retire_gap(0) before
    every TB write. Skip the corner when !g_in_step.
  - gen_isa_shim.h:75: the gen_isa_set_status comment was cut from its line and appended after the gap setter's (verified in the diff).
  - the hazard-variant citation "(:1059-1062, :1120)" in the API doc follows an rtl/ibex_counter.sv citation but the lines are
    rtl/ibex_id_stage.sv's (instr_executing / stall_ld_hz; verified).
  - gen_rvfi_pkg.sv:451 still lists ctr_minstret among the record-synced consistency compares while the scoreboard doc now says
    minstret / instret are the model's own (verified).
- Its g_ir_at_step, :1627, row-count and red-test-sha minors are my L-3, L-2, L-2 and L-1. Its "counters knob" naming point I did not
  verify and do not adopt.
- Not in the artifact: L-1's build y without a compile log or list, L-2's unsupported 47 / 29 / 2 figures and the 8001-record pin-off
  run, L-4 (the canary), L-5 (Runtime's 236 rows), I-2 (the third sub-corner).
- Verdict disagreement, stated: the artifact approves with changes; I hold REQUEST-CHANGES because both corners fail the canonical
  idiom and no retained run exercises a minstret write against the DUT, so the landing's central claim ("the two write corners decided
  by the retirement gap") is unproven and, as coded, wrong for that idiom. The work both verdicts ask for is the same.
