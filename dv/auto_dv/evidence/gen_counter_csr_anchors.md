# Counter CSR set as this clone builds it: RTL anchors for the ISA shim (T-236)

Owner: rtl-arch. Written 2026-09-03T19:55Z from rtl/ibex_cs_registers.sv, rtl/ibex_counter.sv, rtl/ibex_pkg.sv, rtl/ibex_core.sv,
rtl/ibex_id_stage.sv, rtl/ibex_wb_stage.sv, rtl/ibex_decoder.sv and dv/auto_dv/tb/gen_dut_top.sv in this clone, plus the clone's
untracked upstream Spike checkout tools/riscv-isa-sim at commit 4ffd6ba8 (2026-09-02) for the ISS convention. Purpose: the Ibex-specific counter behaviour that tb-infra's gen_isa_shim
configuration (T-235) must reproduce so gen_isa_compare stops raising rows on it. Question list: the Test Writer's measured
reading in dv/auto_dv/work/test-writer/batch3/gen_pmc_ctrl/README_state.md (items 1-4 of its BLOCKER, an untracked work file;
the four claims are quoted verbatim in section 9 so the confirmations can be checked from the committed tree). Doc sentences: doc/03_reference/performance_counters.rst and
doc/03_reference/cs_registers.rst. RTL is read-only; no fix proposal.

## 1. Parameters as resolved for the build

| Item | Value / behaviour | Anchor |
|---|---|---|
| MHPMCounterNum | 10 for the opentitan configuration | ibex_configs.yaml:59; passed as -pvalue+ by util/ibex_config.py opentitan vcs_opts (docs/dv/SIM_RECIPE.md:50, :69-71; dv/auto_dv/flow/gen_flow_const.py:77) |
| MHPMCounterWidth | 32 for the opentitan configuration | ibex_configs.yaml:60 |
| WritebackStage | 1: retirement increments come from the WB stage, so the instruction preceding a csrw minstreth retires in the write cycle and its increment is dropped by the h-write reload (section 2, minstret / minstreth write row) | ibex_configs.yaml:49 |
| Parameter path | gen_dut_top parameter (default 0 / 40, overridden by -pvalue+) -> ibex_core -> ibex_cs_registers | dv/auto_dv/tb/gen_dut_top.sv:43-44, :244-245; rtl/ibex_core.sv:25-26, :1438-1439; rtl/ibex_cs_registers.sv:21-22 |
| Banner | the DUT top prints both values at start of simulation, the run log is the proof of the resolved value | dv/auto_dv/tb/gen_dut_top.sv:441-443 |
| MHPMCOUNTER_BASE | 3: mhpmcounter3 is index 3 of the 32-entry counter array; indices 0 (mcycle) and 2 (minstret) are the fixed counters, index 1 is reserved | rtl/ibex_cs_registers.sv:185 |
| Implemented event counters | indices 3..12 (10 counters); indices 13..31 are unimplemented | rtl/ibex_cs_registers.sv:1667-1670 (gen_cntrs / gen_imp for i < MHPMCounterNum), :1699-1700 (gen_unimp: value 0) |
| CSR index decode | mhpmcounter_idx = csr_addr[4:0] for every counter/event/alias address, so 0xB03/0xB83/0xC03/0xC83/0x323 all select index 3 | rtl/ibex_cs_registers.sv:400 |

## 2. mcycle(h), minstret(h) (0xB00/0xB80, 0xB02/0xB82)

| Field | RTL behaviour | Anchor |
|---|---|---|
| Width | 64 bits, always present | rtl/ibex_cs_registers.sv:1622-1633 (mcycle, CounterWidth 64), :1637-1648 (minstret, CounterWidth 64) |
| Increment | mcycle every cycle; minstret on instr_ret_i; both gated by ~mcountinhibit[idx] | :1586 (incr[0] = 1), :1588 (incr[2] = instr_ret_i), :1627 / :1643 (& ~mcountinhibit) |
| Read value of minstret | includes the instruction in WB when it will retire (instr_ret_spec_i selects minstret_next), so a csrr minstret sees the count including the instruction retiring in the same cycle | :1651-1658 |
| Write | low word via mhpmcounter_we[idx] (0xB00/0xB02), high word via mhpmcounterh_we[idx] (0xB80/0xB82); a write wins over an increment in that cycle | :850-858, :863-871; rtl/ibex_counter.sv:33-51 |
| Increment path (minstret) | instr_ret_i = perf_instr_ret_wb from the WB stage; retired-count rules, dummy instructions included | dv/auto_dv/evidence/gen_cg_sampling_anchors.md sections 21 and 47; dv/auto_dv/evidence/gen_b8_rtl_facts.md section 4 (not repeated here) |
| Write of minstret / minstreth by an instruction (CORRECTED under CM93; the CM76/CM86 wording claimed a V + 1 read-back, which this RTL does not do) | The writer is NOT counted: instr_perf_count_id_o carries a ~minstret_write term, minstret_write = csr_access & (op in WRITE/SET/CLEAR) & (addr in {MINSTRET, MINSTRETH}) (rtl/ibex_id_stage.sv:1210-1220, comment "Writes to minstret/minstreth themselves are also excluded to avoid incrementing right after a write"); that value is latched into wb_count_q when the writer enters WB (rtl/ibex_wb_stage.sv:150, :169), and perf_instr_ret_wb = instr_done_wb & wb_count_q & ~(lsu error) (:208-209) is therefore 0 for the writer, so instr_ret_i (rtl/ibex_core.sv:1549 -> mhpmcounter_incr[2] cs_registers:1588) never pulses for it. Result: `csrw minstret, V` reads back V in both mcountinhibit[2] states, matching Spike (whose bump skips the increment after an explicit instret write, wide_counter_csr_t::bump, tools/riscv-isa-sim/riscv/csrs.cc:1321-1333, excerpted below). No shim action for the low write. The real divergence is on the HIGH write: the CSR write commits when the writer completes ID/EX (csr_op_en = csr_access & instr_executing & instr_id_done, rtl/ibex_id_stage.sv:747-749, instr_id_done = en_wb & ready_wb :1130; csr_we_int cs_registers:1020) and an h write reloads the low word with its PRE-increment value (counter_load[31:0] = counter[31:0], rtl/ibex_counter.sv:40; we wins over the increment :44-47), so a retirement increment due in that same cycle is dropped. With WritebackStage = 1 the preceding instruction retires in exactly that cycle in the back-to-back case (ready_wb = ~wb_valid_q | wb_done, rtl/ibex_wb_stage.sv:185; wb_done for a non-load completes immediately :115-116; instr_done_wb = wb_valid_q & wb_done :200; a load/store in WB completes in the cycle its response arrives, which is also the cycle the stalled csrw completes), giving Ibex {minstreth, minstret} = {V, L} against Spike {V, L + 1}, where L is the count before the preceding instruction; no divergence when WB is empty in the write cycle (a bubble before the csrw) or when mcountinhibit[2] = 1 (the increment is masked, :1643, so nothing is dropped). The low write drops the same increment but the low word is overwritten with V anyway, so it reads V on both sides. Same mechanism as the mhpmcounterXh write in section 3 (and mcycleh, whose dropped cycle is invisible to a CPI-1 model only by coincidence). Excerpted (elisions marked "..."), csrs.cc:1321-1333: `void wide_counter_csr_t::bump(const reg_t howmuch) noexcept { if (written) { ... assert(howmuch <= 1); // The ISA mandates that explicit writes to instret take precedence over the instret, so simply skip the increment. written = false; } else if (is_counting_enabled()) { val += howmuch; ... } }`; execute.cc:353: `state.minstret->bump((mcountinhibit & MCOUNTINHIBIT_IR) ? 0 : instret);`. Reconciled with dv/auto_dv/evidence/gen_hpm_event_defs.md:48, which already quotes the ~minstret_write term. | rtl/ibex_id_stage.sv:1210-1220, :747-749, :1130; rtl/ibex_wb_stage.sv:115-116, :150, :169, :185, :200, :208-209; rtl/ibex_core.sv:1549; rtl/ibex_cs_registers.sv:1020, :1588, :1643; rtl/ibex_counter.sv:40, :44-47; tools/riscv-isa-sim/riscv/csrs.cc:1321-1333, riscv/execute.cc:353 |
| Index 1 (0xB01/0xB81) | not a CSR: no read case, so illegal in every mode (default arm) | :702-703; rtl/ibex_pkg.sv has no enum entry between CSR_MCYCLE :564 and CSR_MINSTRET :565 |

## 3. mhpmcounter3..31(h) (0xB03-0xB1F, 0xB83-0xB9F)

| Field | RTL behaviour | Anchor |
|---|---|---|
| 3..12 read | low word = counter[31:0]; high word = counter[63:32] which is 0 because CounterWidth = 32 | rtl/ibex_cs_registers.sv:580-591 (:590), :593-604 (:603); rtl/ibex_counter.sv:86-90 (bits above CounterWidth read 0) |
| 3..12 write, low word | stored (32 bits), write wins over increment | rtl/ibex_cs_registers.sv:858; rtl/ibex_counter.sv:33-45 |
| 3..12 write, high word (0xB83-0xB8C) | the write enable is asserted (we = counter_we_i or counterh_we_i, rtl/ibex_counter.sv:35) and counter_d takes counter_load[31:0], which for an h write is the OLD low word (:38-41), in preference to counter_upd (:44-47): the stored value is held, and an event increment due in that same cycle is lost; bits 63:32 have no storage (:86-90) | rtl/ibex_cs_registers.sv:871; rtl/ibex_counter.sv:35, :38-41, :44-47, :86-90 |
| 13..31 read | 0 (both halves) | rtl/ibex_cs_registers.sv:1699-1700 |
| 13..31 write | ignored: the write enables exist but are tied off as unused | :1716-1717 |
| Events counted (3..12) | hardwired: 3 dside_wait, 4 iside_wait, 5 loads, 6 stores, 7 jumps, 8 branches, 9 taken branches, 10 compressed retired, 11 mul_wait, 12 div_wait | :1589-1598; definitions in dv/auto_dv/evidence/gen_hpm_event_defs.md |
| Counter 10 read value | includes the compressed instruction retiring in the same cycle (instr_ret_compressed_spec_i), like minstret | :1687-1692 |
| Reset | 0 | rtl/ibex_counter.sv:69, :78 (both flop variants), all instances |

## 4. mhpmevent3..31 (0x323-0x33F)

| Field | RTL behaviour | Anchor |
|---|---|---|
| Read 3..12 | hardwired one-hot: mhpmevent[i] has bit (i - 3) set, i.e. mhpmevent3 = 0x1, mhpmevent4 = 0x2, ... mhpmevent12 = 0x200 | rtl/ibex_cs_registers.sv:1605-1611, read :569-578 (:577) |
| Read 13..31 | 0 | :1615-1618 |
| Write | ignored in every case: no CSR_MHPMEVENT arm in the write-enable case statement whose counter arms are :845-872, no storage | :845-872 (absence); doc/03_reference/cs_registers.rst:21-25 lists them WARL |
| Privilege | M-level addresses (csr[9:8] = 11): U access illegal | :403 |

## 5. mcounteren (0x306)

| Field | RTL behaviour | Anchor |
|---|---|---|
| Storage width | MHPMCounterNum + 3 = 13 bits (bits 12:0) | rtl/ibex_cs_registers.sv:309 |
| Write, kept bits | bits 12:0 of the write data, then bit 1 (TM) forced 0: CY (0), IR (2), HPM3..HPM12 (3..12) are writable; bits 31:13 dropped | :1564-1571 (:1566 slice, :1567 bit 1 = 0) |
| Read | zero-extended stored word: bit 1 = 0, bits 31:13 = 0 | :1732 (MHPMCounterNum < 29 branch), read :464 |
| Write gate | mcounteren_we asserted only when mcounteren_writable_i == IbexMuBiOn; any other encoding (Off or invalid) makes the write a silent no-op, no trap | :845; the pin is a top-level input passed through gen_dut_top (dv/auto_dv/tb/gen_dut_top.sv:198, :390) |
| Register instance | ibex_csr, Width 13, ShadowCopy 0, ResetValue 0, wr_en_i = mcounteren_we | :1736-1748 |
| Effect | gates U-mode reads of the aliases per bit (section 7); no effect on M-mode reads | :618, :632 |

## 6. mcountinhibit (0x320)

| Field | RTL behaviour | Anchor |
|---|---|---|
| Storage width | 13 bits (bits 12:0) | rtl/ibex_cs_registers.sv:304 |
| Write, kept bits | bits 12:0 of the write data, bit 1 forced 0; bits 31:13 dropped; no writability pin, always writable in M | :1554-1561 (:1556 slice, :1557 bit 1 = 0), write enable :846 |
| Read | zero-extended stored word | :1714, read :568 |
| Reset | 0 (all counters count from reset) | :1723-1728 |
| Effect | bit i masks the increment of counter i (0 mcycle, 2 minstret, 3..12 events); bits 13..31 read 0 and gate nothing | :1627, :1643, :1679 (counter_inc_i = incr & ~mcountinhibit) |

## 7. U-mode aliases cycle(h), instret(h), hpmcounter3..31(h) (0xC00-0xC1F, 0xC80-0xC9F)

| Field | RTL behaviour | Anchor |
|---|---|---|
| Value | the same counter word as the M-mode CSR of the same index (aliases, not copies) | rtl/ibex_cs_registers.sv:607-619 (:617 low), :621-633 (:631 high) |
| Legality in M | always legal (read); the addresses are read-only by encoding (csr[11:10] = 11), so CSRRW, CSRRWI, or CSRRS / CSRRC with rs1 != x0 (CSRRSI / CSRRCI with uimm != 0) traps in every mode, while CSRRS / CSRRC with rs1 = x0 and the zero-immediate forms are demoted to reads by the decoder and are legal | :618 / :632 (rule applies only when priv_lvl_q == U); :404 (illegal_csr_write, csr_wr from the op); rtl/ibex_decoder.sv:251-258 (CSR_OP_READ demotion) |
| Legality in U | legal only when mcounteren[idx] = 1; for idx 13..31 mcounteren reads 0 (section 5), so hpmcounter13..31(h) is always illegal in U; cycle/instret/hpmcounter3..12 follow the stored bit; time is index 1, whose bit is forced 0 | :618, :632, :1732 |
| Trap | illegal instruction (cause 2), mtval = the instruction | :405-406 (illegal_csr_insn_o), controller mtval rtl/ibex_controller.sv:868 |
| Doc | performance_counters.rst:66-77 (mcounteren gating, illegal instruction on a clear bit) | doc/03_reference/performance_counters.rst:69-75 |

## 8. time / timeh (0xC01 / 0xC81) and mtime

| Field | RTL behaviour | Anchor |
|---|---|---|
| time, timeh | no CSR_TIME / CSR_TIMEH enum entry and no read case: the address falls into the default arm, illegal_csr = 1, in EVERY privilege mode including M and debug; mcounteren bit 1 is irrelevant | rtl/ibex_pkg.sv:630-631 (CSR_CYCLE 0xC00 then CSR_INSTRET 0xC02, nothing at 0xC01), :661-662 (0xC80 then 0xC82); rtl/ibex_cs_registers.sv:702-703 |
| Why bit 1 is forced 0 | the RTL comment states it: no time CSR implemented | :1565, :1555 |
| mtime | not a CSR in Ibex; a platform memory-mapped timer (the TB's timer model) | doc/03_reference/cs_registers.rst:598-600 |

## 9. The Test Writer's claims (README_state.md BLOCKER items), confirmed or corrected

Verbatim from the README (2026-09-03 19:5xZ state), items 1-4 of its BLOCKER paragraph:

1. "mcountinhibit / mcounteren WARL masks: Ibex keeps CY, IR and bits 3..12 (MHPMCounterNum 10), TM reads 0, bits above 12 read 0; Spike keeps TM (mcounteren) and bits 3..31."
2. "U-mode alias gating: Ibex traps (cause 2) on hpmcounter13..31 (mcounteren bits above 12 read 0) and on time/timeh; Spike gates by its writable mcounteren and returns time."
3. "time/timeh (0xC01/0xC81): Ibex traps in every mode; Spike returns the time CSR in M-mode"
4. "mcounteren_writable_i off: Ibex drops mcounteren writes; Spike stores them"

Verdicts:

| Claim | Verdict | RTL |
|---|---|---|
| 1. mcountinhibit / mcounteren keep CY, IR and bits 3..12; TM reads 0; bits above 12 read 0 | CONFIRMED | sections 5 and 6 (:1556-1557, :1566-1567, :1714, :1732) |
| 2. hpmcounter13..31 trap (cause 2) in U because mcounteren bits above 12 read 0 | CONFIRMED, with the addition that in M-mode hpmcounter13..31 read 0 legally, and mhpmcounter13..31 read 0 / ignore writes in M | section 7 (:618, :632), section 3 (:1699-1700, :1716-1717) |
| 3. time / timeh trap in every mode | CONFIRMED (default arm, no enum entry); also in debug mode | section 8 |
| 4. mcounteren writes dropped when mcounteren_writable_i is off | CONFIRMED; add: any encoding other than IbexMuBiOn is "off", the write is a silent no-op with no trap, and the read-back returns the old value | section 5 (:845) |
| (implicit) mhpmevent writes | not in the list but needed by the shim: every mhpmevent write is ignored and reads are the hardwired one-hot for 3..12, 0 for 13..31 | section 4 |
| (implicit) mhpmcounterXh writes for 3..12 | needed by the shim: the high-word write holds the stored value (CounterWidth = 32) and drops an event increment due in that cycle | section 3 (rtl/ibex_counter.sv:35, :38-41, :44-47, :86-90) |
| (implicit) minstret read includes the retiring WB instruction | needed by a lock-step model that reads minstret: see sections 21 / 47 of the sampling anchors and :1648-1658 | section 2 |

## 10. Shim configuration summary (what the model must do, one line each)

- Counters: mcycle/minstret 64-bit; mhpmcounter3..12 32-bit with hardwired events (an mhpmcounterXh write holds the stored value and drops an event increment due in that cycle; mhpmcounterXh reads 0); mhpmcounter13..31 and mhpmevent13..31 read 0, writes ignored; mhpmevent3..12 read one-hot (i - 3), writes ignored.
- csrw minstret, V: the writer itself is not counted (instr_perf_count_id_o excludes minstret / minstreth writes, rtl/ibex_id_stage.sv:1210-1220), so the next read returns V in both mcountinhibit[2] states, as Spike does. Shim action: none.
- csrw minstreth, V: the writer adds nothing, but the h write reloads the low word with its pre-increment value (rtl/ibex_counter.sv:40, :44-47), so a retirement due in the write cycle is dropped; with WritebackStage = 1 that is the immediately preceding instruction in the back-to-back case, giving Ibex {V, L} where Spike has {V, L + 1}; no divergence when WB is empty in the write cycle or when mcountinhibit[2] = 1. Shim action: when mcountinhibit[2] = 0 and the trace shows an instruction retiring in the write cycle, subtract one from the low word after an explicit minstreth write (or the testlist keeps a bubble before csrw minstreth); otherwise none. The same rule covers mhpmcounterXh (3..12) writes with their own event.
- mcounteren: bits 0, 2..12 writable, bit 1 and 31:13 read 0; writes dropped (no trap) unless the mcounteren_writable pin is IbexMuBiOn.
- mcountinhibit: bits 0, 2..12 writable, bit 1 and 31:13 read 0; reset 0.
- U-mode aliases: legal iff mcounteren bit set; hpmcounter13..31(h) never legal in U; all legal in M (read-only by address).
- time / timeh: illegal instruction in every mode.
- minstret value seen by a read includes the instruction retiring in WB in that cycle; dummy instructions count.
