# Critic verdict: TB architecture component sections, v2 re-review (T-011 part 1 v2)

Artifacts under review:
- dv/auto_dv/work/tb-infra/gen_tb_arch_component_sections.md (version 2, 842 lines)  sha256 d8202876b9bef393
- dv/auto_dv/work/tb-infra/gen_critic_response_tb_arch_v1.md                          sha256 69d7e74e02310608
  (working path; the committed copy will be dv/auto_dv/evidence/gen_critic_response_tb_arch.md, which
  is the path future verdicts cite)
Freeze note: the sections file carries TB Infra's "(link test 2)" edits (six marks: C5.1 A-16 done,
C5.2 debug-entry row, C5.3a genibex row, C5.4 byte-wise MMIO, open items) and was frozen at the hash
above; re-hashed unchanged at 07:02Z before this file was finalized. rtl-arch's eight T-051 corrections
are not in the sections file; they live in the DV Lead's T-048 draft, subsection 6.13, binding until
folded as v3 of the sections. This verdict judges the sections file on its own text and treats 6.13 as
the known pending amendment (Section 4).
This verdict is retained as dv/auto_dv/evidence/gen_critic_tb_arch_components_v2.md (identical copy).
Inputs read alongside:
- dv/auto_dv/reviews/2026-09-03-claude-plan-gen_tb_arch_component_sections.md (XM findings) sha256 33c9fbc657c22880
- dv/auto_dv/evidence/gen_t046_spike_linktest2.md (link test 2)                       sha256 0a7853fb9100a21b
- dv/auto_dv/work/rtl-arch/gen_arch_v2_rtl_factcheck.md (T-051, treated as input)       sha256 ea0f321a3b09f7ba
- tools/riscv-isa-sim/riscv/{csrs.h, csrs.cc, processor.h, processor.cc, execute.cc, mmu.cc} at the pinned
  revision; rtl/ibex_core.sv, ibex_if_stage.sv, ibex_load_store_unit.sv, ibex_icache.sv, ibex_id_stage.sv,
  ibex_cs_registers.sv for the fact-check rows I re-verified.
Date: 2026-09-03 (UTC)
Role: Critic (reviewer other than the author; probe approvals and polling waivers are the Critic's duty)
Supersedes: dv/auto_dv/work/critic/gen_critic_tb_arch_components_v1.md (REQUEST-CHANGES, A-01..A-25, C8)

CRITIC VERDICT: APPROVE

Scope of this approval. Every v1 finding (A-01..A-25) and every cross-model finding (XM-M1..M5, L1..L6,
I1) is addressed in the v2 text and, where it rests on a tool fact, verified by me in the pinned Spike
source and backed by the retained link-test-2 artifact. The architecture is feasible as written and
component SV may open. Two conditions attach, both from rtl-arch's fact-check that landed one minute
after v2 (T-051, Section 4 below): the five checker rows it corrects (core_busy, ctr_hpm_exact events
5/6, irq_pending and crash_dump offsets, alert_bus data class, irq/dbg entry bound derivation) are
coded only after TB Infra folds those corrections into the v2 text; and the stale sentences in N-01 are
fixed in the same edit. Everything else opens now. One of the corrected rules (core_busy) implements
wording my v1 finding A-10 asked for; the error is mine as much as TB Infra's, and it is recorded here.

## 1. Disposition of the v1 findings

| v1 | Sev | v2 answer | My check |
|---|---|---|---|
| A-01 evt_retired counter awaited from Python | medium | C2: `evt_retired_target`/`evt_cycle_target` written by Python, single-bit `evt_thresh_hit` toggle awaited once per threshold; counts read once at finish; explicit "no per-cycle Python polling exists, no waiver requested"; C9 layer 3 rewritten | FIXED. The waiver question is closed: none is requested and none is granted. See N-02 for a one-bit ambiguity |
| A-02 ASCII Python strings | low | Conventions bullet with a gen_tests unit check | FIXED |
| A-04 literal caps | low | `GEN_IBUS_MAX_OUTSTANDING = GEN_ICACHE_NUM_FB * IC_LINE_BEATS` (= 8, NUM_FB re-type cited to rtl/ibex_icache.sv:72), `GEN_DBUS_MAX_OUTSTANDING` = 2 cited to the split rule, irq width `$bits(irqs_t)` | FIXED; rtl-arch row 8 and 2.3 confirm 8 and 2 |
| A-05 icram init default | low | C3.4 default `random` with rationale | FIXED |
| A-07 read-back of the backdoor load | low | C3.3: SV CRC-32 digest plus MEM_PEEK read-back of `GEN_MEM_READBACK_WORDS` seeded addresses compared by Python | FIXED; the CRC definition matches `gen_elf2mem.checksum()` (stim/gen_elf2mem.py:112-117: zlib crc32 over `<II` (index, word) in ascending index order) |
| A-08 checker direction on spec-violation items | medium | C5.3a (RTL-defined) / C5.3b (B1, B2/BUG-01, BUG-03, B3, B5 with spec direction, expected_fail, bug id); `pmp_data` and `dbg_dret` rules carry the spec direction; `dcsr.ebreaks` not legalized | FIXED as required. rtl-arch rows 33, 51, 52 confirm the RTL side of B2, B1, B3 |
| A-09 cycle-exact compares vs an RVFI-timed model | medium | Exactness class per checker (Conventions) and table C4.8 with named constants measured at bring-up | FIXED in shape. The constants' values and classes are corrected by T-051 (Section 4, F-01..F-04) |
| A-10 core_busy WAIT_SLEEP dip | low | C4.2 `core_busy`: "Off for exactly one cycle after every retired WFI" | Implemented as I asked, and as I asked it is wrong: see F-01 |
| A-11 ISA comparator mutation rows | low | C4.7 table `isa_pc..isa_csr` with loci and per-field knobs under the `+gen_chk_isa` master | FIXED |
| A-13 self-check accounting | low | Conventions: TB self-checks not counted as DUT checkers; `ibus_order`/`dbus_queue` agent-internal | FIXED |
| A-14 mie fast bits and priority | medium | `gen_mie_csr_t : mie_csr_t` overriding `write_mask()`, installed in `state.mie` and `csrmap[CSR_MIE]`; Spike's default priority chain accepted as Ibex's; `taken_cause` compared after the entry step | FIXED and verified (Section 3.1). My v1 route (shadow via `write_with_mask`) was wrong for the reason XM-M1 gave; the v2 route is right |
| A-15 misaligned byte order | low | C5.4 rewritten from `mmu_t::mmio` (byte split, stop at first failure) with the `mtval` override | FIXED and verified (Section 3.3) |
| A-16 second link test | info | DONE, 98 checks, artifact retained | Verified (Section 3.4) |
| A-17 time(h) | low | trapping `csr_t` in csrmap for 0xC01/0xC81 | FIXED |
| A-18 draft-B references | low | Q-003 dependence and Q-DL-2 fallback stated; reference functions are checkers with TDD and mutation duty | FIXED |
| A-19 CSR plan conditions | info | C6 item 6: sweep-frequency and write-to-read-gap bins; csrr only; mip from rvfi_ext | ACCEPTED |
| A-20 shim self-validation | low | C6 item 4 reworded | FIXED |
| A-21 code-coverage scope restated | low | C7 defers to the DV Lead's decision and Runtime's cm_hier | FIXED |
| A-23 unknown plusarg | low | `uvm_fatal GEN_UNKNOWN_PLUSARG` at time 0 | FIXED |
| A-24 binds home note for Runtime | info | relayed; Runtime's --rtl-root exists (T-038) | CLOSED |
| A-25 site dependency | info | C11 states Q-012 and the interim mode | FIXED |
| A-03, A-06, A-12, A-22 | info | no change needed | - |
| C8 rulings | binding | C8 table and gen_probe_register.md carry all conditions verbatim | VERIFIED (also in gen_critic_probe_register_v1.md) |

## 2. Disposition of the cross-model findings

| XM | v2 answer | My check |
|---|---|---|
| M1 mie fallback does not work | see A-14 | FIXED, verified in csrs.h (Section 3.1) |
| M2 one step per record false for interrupt/trigger records | C5.2 step table per record class; `gen_isa_step` returns the retired count | FIXED; execute.cc:244-248, 314-318, 338-346 confirm the interrupt is taken inside the try block and `n = instret` ends the step with zero retired |
| M3 image contract stale | C3.3 CRC-32 definition and knob `+gen_mem_image_crc32`, routine named | FIXED, matches gen_elf2mem.py |
| M4 VPI read-back of an SV class | MEM_PEEK bridge command and `peek_data` | FIXED |
| M5 irq_pending false-fails around mie writes | settle window `GEN_CSR_COMMIT_TO_RVFI_OFFSET` | FIXED in shape; value corrected by T-051 (F-03) |
| L1 alert_bus on unconsumed fetch beats | split by source; fetch exact | FIXED; data side corrected by T-051 to exact (F-04) |
| L2 ISA string | one `GEN_ISA_STRING` in the codegen output | FIXED; the link test used the same string plus `_xgenibex` |
| L3 ibus_order without mutation | agent-internal assert | FIXED |
| L4 ctr_minstret depends on P1 | bound check while dummies enabled; P1 coverage-only | FIXED in the C4.6 row; the C4.6 purpose text still carries the old sentence (N-01) |
| L5 regime_sched only for the log | Python consumes a supplied schedule | FIXED |
| L6 stale scoping-notes passages | six "[SUPERSEDED: ...]" marks | FIXED (six marks counted) |
| I1 extension_t::get_csrs | `genibex` extension, CSRs added by `reset()` | FIXED and proved by link test 2 case 2 |

## 3. Feasibility facts verified in the pinned Spike source

3.1 The `write_mask()` override point. csrs.h:373-385: `mip_or_mie_csr_t` declares `unlogged_write`
`override final` (protected) and `write_mask()` as a private pure virtual; csrs.h:403-408: `mie_csr_t`
is not final and its `write_mask()` is `override` without `final`. C++ lets a derived class override a
private virtual, so `gen_mie_csr_t : public mie_csr_t` with its own `write_mask()` is legal and the
final `unlogged_write` dispatches to it (csrs.cc:951-952 calls `write_with_mask(write_mask(), val)`).
`state.mie` is `mie_csr_t_p` = `shared_ptr<mie_csr_t>` (processor.h:109) and `state.csrmap` is public
(processor.h:90), so the instance can be installed in both, which `take_interrupt` (reads `state.mie`)
and CSR instructions (read `csrmap`) both need. The link test does exactly this
(gen_spike_linktest2.cc:75-79, :125). Verified: the override point is virtual, not final.

3.2 Priority. processor.cc:258-262: bits above IRQ_LCOF (13) are selected first, then `ctz` picks the
lowest set bit (processor.cc:335); standard order MEI, MSI, MTI. That equals Ibex's fast lowest-id >
external > software > timer for causes 16..30, 11, 3, 7. NMI is not in Ibex's `mip` at all
(cs_registers.sv:408-412 assembles sw, timer, external, fast only), so the model never sees bit 31
and the shim's NMI emulation stands outside this chain; see N-03 for the wording.

3.3 Misaligned MMIO. mmu.cc:168-184: a power-of-two, naturally aligned access is one `sim->mmio_*`
call; otherwise a byte loop that returns at the first failing byte. C5.4 now states this correctly and
the `mtval` override (`put_csr(CSR_MTVAL)`, link test :320) is the right fix for Ibex's aligned
second-word rule (BS MEM-13, rtl-arch row 32 AGREE).

3.4 Link test 2 artifact (audit rule). gen_spike_linktest2.cc mtime 06:42:20Z; out_linktest2/
gen_spike_linktest2 and linktest2.log 06:42:25Z; the log ends "GEN_SPIKE_LINKTEST2 PASS (0
failures)" and its last checks are the `mtval` lines quoted in the evidence. Source, binary and log
are distinct retained artifacts in a consistent order. Evidence claims verified.

## 4. Corrections from rtl-arch's fact-check (T-051) that the v2 text must take before coding

I re-read the RTL behind each DISAGREE row. Severity is for the rule as written in v2.

F-01 (medium) C4.2 `core_busy`. v2 says core_busy_o is Off for exactly one cycle after every retired
WFI. core_busy_o is the OR of ctrl_busy, if_busy and lsu_busy (rtl/ibex_core.sv:496-522, per-bit
buffered copies under SecureIbex); if_busy is the prefetcher's busy (icache.sv:1304: invalidation
active or fill beats outstanding) and lsu_busy is `ls_fsm_cs != IDLE` (lsu.sv:762). The ctrl_busy dip
in WAIT_SLEEP (controller.sv:598-604) reaches the port only when both are 0; after a WFI the
prefetcher usually has beats in flight and for 256 cycles after reset or fence.i the invalidation holds
the port On. The exact rule as written would fail on most WFIs. Required: rtl-arch item 1 wording
("in WAIT_SLEEP core_busy_o == Off iff no instruction-bus beat is outstanding, no invalidation is
active and the LSU is idle"). My v1 A-10 named the ctrl_busy fact and asked for the port rule; that was
my error.

F-02 (medium) C4.6 events 5/6. v2 counts a misaligned load or store as 2. perf_load_o/perf_store_o are
set only in request-issue arms (lsu.sv:456-457, :474-475), not in the misaligned second-half states, so
a misaligned access counts 1 (my T-007 finding C-11 said the same; rtl-arch row 42). `ctr_hpm_exact`
as written false-fails on every misaligned access. Required: 1 per instruction.

F-03 (medium) C4.4 `irq_pending`, C4.2 `crash_dump`, C4.8. v2 says the offset is "at least 2, more when
WB stalls" and uses one constant for CSR-write and trap records. The CSR write commits at the edge the
instruction leaves ID (id_stage.sv:747-749 selects instr_id_done_o, :1130; cs_registers.sv:1020) and
the record follows two cycles later; a WB stall delays both together, so the offset is a fixed 2 for
CSR-write records and 1 for trap, mret and dret records (rtl-arch 2.1). Required: two constants or a
per-class table; keep the bring-up measurement as confirmation of the predicted 2 and 1.

F-04 (low) C4.2 `alert_bus` data side. load/store_resp_intg_err_o is combinational on the response
(lsu.sv:756-757), so the data side is exact like the fetch side; `GEN_ALERT_BUS_WINDOW` = 0 or removed.

F-05 (low) C4.4 `irq_entry`, C4.5 `dbg_entry` bound derivation. Add the Zcmp sequence in ID (up to 16
micro-op records, each its own record; rtl-arch row 44) and the WFI wake path: nominal 2 records, worst
case 17. A bound derived only from the divide would false-fail when a cm.popretz is in flight.

F-06 (low) C3.4 `icram_inval_sweep` anchor: with `+gen_key_reset_valid=0` the 256 writes start at the
key-valid edge, not at reset release (icache.sv:1229-1240).

F-07 (info) C5.5 BUG-04 policy: adopt rtl-arch's wording (the WB error's trap record now, the ID
instruction's own record later when it re-executes); no "lost" record is modelled either way.

F-08 (info) C5.2: the Zcmp `rvfi_order` UNVERIFIED mark can become "static-agreed, sim confirms"
(rtl-arch row 44; core.sv:1905).

## 5. New findings on the v2 text

N-01 (low, stale text contradicting the fixed rows). Three sentences survived from v1: C4.6 purpose
text ":398 exact only with dummies off or with probe P1" contradicts the XM-L4 row; C11 ":815 Runtime's
gen_testlist.yaml (currently tier: smoke)" is superseded (gen_smoke is tier check, R-01 closed); Open
items ":831 A-14: write_with_mask shadow" names the route XM-M1 showed does not work. Fix all three in
the F-01..F-05 edit.

N-02 (low). `evt_thresh_hit` is one toggle for two thresholds (retired and cycle). If Python arms both,
one edge cannot say which fired. Either two bits or a stated rule that only one threshold is armed at a
time (the schedule of C9 uses one trigger per entry, so the rule costs nothing).

N-03 (info). C5.3a mie row and C5 head describe Spike's chain as "NMI-slot > fast lowest-id > ...".
Spike ranks bit 31 lowest among the nonstandard bits (ctz), but the model never sees it because Ibex's
mip has no NMI bit; state the chain as "fast lowest-id > external > software > timer, NMI emulated
outside".

N-04 (info). C5.3b calls the dret/MPRV item B1 while rtl-arch's fact-check and T-041 call it BUG-06; the
testlist `expected_fail` rows need one id.

N-05 (info). C6 items are numbered 1, 2, 3, 4, 6, 5.

## 6. What opens now and what waits

- Opens now: all agents (C3), bridge and TB top (C2), memory and RAM models, scrkey responder, RVFI
  monitor, scoreboard framework and ISA shim (C5, all three link-test-2 consequences included), PMP
  model, debug checker, counter model except events 5/6, binds home and cover-props integration (C10),
  constants home and codegen (C11), probe binds per gen_probe_register.md.
- Waits for the F-01..F-05 text fold (TB Infra, small edit; rtl-arch's Section 4 is the checklist):
  `core_busy`, `ctr_hpm_exact` events 5/6, `irq_pending` and `crash_dump` offset constants,
  `alert_bus` data class, `GEN_IRQ_ENTRY_BOUND_RECORDS` / `GEN_DBG_ENTRY_BOUND_RECORDS` derivation.
  No re-review is needed for that fold: I will check the five rows when the component SV that
  implements them comes for its dv-principles check.
- Bring-up owes the C4.8 constants with rtl-arch's predicted values as the expectation (2 and 1 for
  the commit offsets; 2 + W for `GEN_RVFI_ID_EXIT_OFFSET`; 1 from the corrupted-rdata cycle for the
  ECC window; 0 for the alert bus; 17 records worst case for the entry bounds).

## 7. Fence and method record

Inputs as listed in the header. Spike facts were read in tools/riscv-isa-sim (upstream clone, allowed);
no Ibex DV collateral was read or recalled. The link-test-2 artifact was audited for identity (source,
binary, log stamps and final line). No LSF command. No fence event.
