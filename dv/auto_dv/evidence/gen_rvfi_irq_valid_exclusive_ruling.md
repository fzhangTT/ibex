# Ruling: sva_rvfi_irq_valid_exclusive fires legitimately; the property changes, not the stimulus

Committed reference (promoted 2026-09-04 from the rtl-arch working file
dv/auto_dv/work/rtl-arch/gen_rvfi_irq_valid_exclusive_ruling.md, same content apart from this paragraph); when
the working copy changes, this copy is re-promoted, and the working copy is never copied over this one without
carrying this paragraph. The run and build paths below are tb-infra working paths, named as provenance for the
reproducer; the ruling in Section 1 rests on the RTL citations in Sections 2 to 4, which resolve in this
repository.

Owner: rtl-arch. Written 2026-09-04T16:25Z from the RTL in this clone (rtl/ibex_core.sv, rtl/ibex_wb_stage.sv,
rtl/ibex_configs.yaml) and the property as built (dv/auto_dv/tb/gen_protocol_props.sv:299). Build configuration:
opentitan, so WritebackStage = 1 (ibex_configs.yaml:49) and RVFI_STAGES = 2 (rtl/ibex_core.sv:1660). RTL is
read-only. Question put by the Orchestrator: can the DUT legitimately assert rvfi_ext_irq_valid and rvfi_valid in
the same cycle, or is tb-infra's firing run a DUT finding for the B8 facts. The assignment relayed five firings;
the retained runs hold 36, re-derived in Section 8.

## 1. Ruling

The DUT can legitimately assert both in one cycle. Exclusivity is not a design invariant, it is not enforced
anywhere in the RVFI logic, and the RTL states the opposite intent in words. So the property's premise from the
T-017 3.2 static analysis is too narrow: the property changes and the stimulus is not constrained. This is not a
bug candidate and there is no B8 row. The two signals are not the same event and are not read from the same place.

## 2. The two signals are read one pipeline stage apart

The RVFI tracking pipeline carries the retirement record in arrays of RVFI_STAGES entries and the interrupt-side
ext group in an array of RVFI_STAGES + 1 entries:

- `logic rvfi_ext_stage_irq_valid [RVFI_STAGES+1];` (rtl/ibex_core.sv:1763), one entry longer than
  `logic rvfi_stage_valid [RVFI_STAGES];` (:1662).
- `assign rvfi_valid = rvfi_stage_valid[RVFI_STAGES-1];` (:1775), the last retirement stage.
- `assign rvfi_ext_irq_valid = rvfi_ext_stage_irq_valid[RVFI_STAGES];` (:1837), one index beyond it.

The same asymmetry applies to the rest of the interrupt-side group, `rvfi_ext_nmi`, `rvfi_ext_nmi_int` and
`rvfi_ext_debug_req` at index RVFI_STAGES (:1829-1831) against `rvfi_ext_debug_mode` and the counters at
RVFI_STAGES-1 (:1832-1836). So the notification is deliberately published from a different depth than the record
it may or may not accompany.

## 3. The RTL states the dual role in words, twice

At both hops of the ext group the same comment appears, at :2130-2133 in the `i == 0` branch and again at
:2188-2191 in the `i == 1` branch: "Some of the rvfi_ext_* signals are used to provide an interrupt notification
(signalled via rvfi_ext_irq_valid) when there isn't a valid retired instruction as well as providing information
along with a retired instruction. Move these up the rvfi pipeline for both cases."

The code matches the comment. Each hop is an OR, so the flag advances whether or not a retirement is moving:

- `if (rvfi_id_done | rvfi_ext_stage_irq_valid[i])` guards the [0] to [1] hop (:2134), carrying
  `rvfi_ext_stage_irq_valid[i+1] <= rvfi_ext_stage_irq_valid[i]` (:2140).
- `if (rvfi_wb_done | rvfi_ext_stage_irq_valid[i])` guards the [1] to [2] hop (:2192), carrying the same
  assignment (:2198).

Because the flag supplies its own advance term, once set it reaches the output on the next cycle at each hop,
independent of retirement traffic.

## 4. Nothing couples the two, in either direction

- The retirement side carries no interrupt term: `rvfi_stage_valid_d[1] = rvfi_wb_done` (:1868), with
  `rvfi_wb_done = rvfi_stage_valid[0] & (instr_done_wb | rvfi_stage_trap[0])` (:1890) and
  `rvfi_stage_valid_d[0] = (rvfi_id_done & ~dummy_instr_id) | (rvfi_stage_valid[0] & ~rvfi_wb_done)` (:1864-1865),
  registered by `rvfi_stage_valid[i] <= rvfi_stage_valid_d[i]` (:2069). No term mentions irq_valid.
- The notification side constrains only the cycle of its own pulse, not the cycle it is published in. The pulse is
  `if (~instr_valid_id & ~new_debug_req & (new_irq | new_nmi | new_nmi_int) & ready_wb & ~captured_valid)
  rvfi_irq_valid <= 1'b1; else rvfi_irq_valid <= 1'b0;` (:1965-1970), with
  `new_debug_req = (debug_req_i & ~debug_mode)` (:1928), `new_nmi = irq_nm_i & ~nmi_mode & ~debug_mode` (:1929),
  `new_nmi_int = id_stage_i.controller_i.irq_nm_int & ~nmi_mode & ~debug_mode` (:1930) and
  `new_irq = irq_pending_o & (csr_mstatus_mie || (priv_mode_id == PRIV_LVL_U)) & ~nmi_mode & ~debug_mode`
  (:1931-1932). It enters the pipeline as `rvfi_ext_stage_irq_valid[0] <= rvfi_irq_valid` (:2002) under the enable
  `(if_stage_i.instr_valid_id_d & if_stage_i.instr_new_id_d) | rvfi_irq_valid` (:1992), where the second disjunct
  is the flag admitting itself with no instruction in ID.
- The "pipeline has emptied" precondition is about the ID stage, not about the RVFI pipeline being quiet, and it
  explicitly tolerates an instruction completing writeback in the same cycle:
  `ready_wb_o = ~wb_valid_q | wb_done` (rtl/ibex_wb_stage.sv:185) while
  `instr_done_wb_o = wb_valid_q & wb_done` (:200). So the pulse cycle itself may be a cycle in which
  rvfi_wb_done is true, which is the retirement side's own trigger.

## 5. Why the two can land together, and why the shape matters

With RVFI_STAGES = 2 the flag takes four cycles from its condition to the port. If the pulse condition holds
during cycle C, then rvfi_irq_valid is high during C+1 (:1967), irq_valid[0] during C+2 (:2002), irq_valid[1]
during C+3 (:2140) and irq_valid[2], which is the port, during C+4 (:2198, :1837). rvfi_valid is high during C+4
exactly when rvfi_wb_done was high during C+3 (:1868, :2069). Nothing in Section 4 prevents that, so the
coincidence is a timing alignment, not an illegal state.

This is why the trigger shape decides whether the property fires. A notification raised at the same time as the
interrupt drains the pipeline and leaves the four following cycles empty of retirements, so the raise-triggered
shape never aligns. A notification raised a short delay after an interrupt entry leaves the first handler
instructions in flight, so a retirement can complete at C+3 and the port coincides at C+4. The 36 firings
across the two knob values are
consistent with that alignment; which of the two alignments each firing took, a handler retirement four cycles
after one pulse or a second pulse overlapping an earlier record, is a waveform question and is open in
Section 7. Neither alternative changes the ruling.

## 6. What to assert instead

The property should state what the RTL guarantees rather than exclusivity. The candidate at the boundary is that
the notification never appears without a cause: `rvfi_ext_irq_valid |-> (rvfi_ext_nmi | rvfi_ext_nmi_int |
(|rvfi_ext_pre_mip))`. Its basis is that the pulse requires `(new_irq | new_nmi | new_nmi_int)` (:1965) and that
the cause fields are captured in the same cycle as the flag (:1993-2002) and advance with it in the same guarded
block (:2135-2140, :2193-2198), so the group is coherent at the port.

Two cautions I will not paper over. `new_irq` also needs `csr_mstatus_mie` or user mode (:1931-1932), which is not
visible in `rvfi_ext_pre_mip` alone, so the disjunction is the weaker claim that some cause bit is set, not that
the taken cause is identifiable from the port. And the property is new, so under the trust triad it needs its own
red-first evidence and a named mutation before it is adopted; it is a recommendation to tb-infra, not a drop-in.

Keeping `sva_rvfi_irq_valid_seen` as a cover (gen_protocol_props.sv:304) remains right, and a cover of the
coincidence itself is worth adding, since it is now a known reachable alignment rather than an error.

## 7. What is not confirmed, and what a confirmation needs

No waveform has been read, because neither retained run holds one: a search of the whole build directory for
fsdb, vcd and vpd files returns nothing, and the two run directories hold only results.xml, run_header.txt,
sim.log, stdout.log, ucli.key and verdict.txt. So the cycle-level detail behind Section 5 is not confirmed: which
instruction's writeback completion coincided with the port, and whether the four-cycle offset from the pulse
condition holds in the run.

What a confirmation needs is one rerun of the same build, seed and program with wave dumping enabled, plus the
knob's arm moved back to the taken-event branch, since tb-infra states the tree today arms it on the raise and
that shape does not fire. The rerun belongs to Runtime, the arm change to tb-infra; both have been asked. The
coincidence itself does not depend on it, for the reason in Section 8.

## 8. What the retained runs do confirm, re-derived here

Runs: dv/auto_dv/work/tb-infra/wit/l32a/irq_nmi_window/ and .../irq_nmi_late/, build
dv/auto_dv/work/tb-infra/wit/l32a with build_sources_sha256 cc08c9729184adc5 in both run headers, seed 1, module
dv.auto_dv.gen_tb.gen_tests.gen_ut_lockstep, image prog.vmem of 156 words with crc32 0x8e882c5b verified at time
0, gen_knob_nmi_after_irq_delay = window and late respectively, with gen_knob_irq_regime = storm and
gen_knob_irq_line_mix = multi.

Re-derived from the retained sim.log of each run, not taken from the relay:

- 11 firings in the window run and 25 in the late run, 36 in total. Each run's UVM error count equals its firing
  count (11 and 25 in the verdict files), so every error in both runs is this property and nothing else failed.
- The window run's firing cycles are 361, 1242, 2780, 4207, 4684, 6711, 11623, 13764, 15603, 16590 and 18076.
  The first four match the four cycles the assignment relayed.
- The firing I confirmed in full is the first one, cycle 361 of the window run: the assertion at
  gen_protocol_props.sv:299 started and failed at 3655000 ps, and the reported offending term is `(!rvfi_valid)`.
- The cycle numbers are the TB counter, and they map to simulation time as (cycle + 4.5) times 10000 ps on all 11
  window firings without exception, which fixes the clock at 10 ns and places every firing on a clock edge.

That the offending term is the `!rvfi_valid` half is the whole of the disputed question: the property failed
because rvfi_valid was high while rvfi_ext_irq_valid was high, not because the flag was spurious. So the
coincidence is confirmed on retained evidence at a named cycle, and Sections 2 to 4 say it is legal. What the
missing waveform would add is which instruction retired and whether the offset is the four cycles Section 5
derives, neither of which changes the ruling.

One fact here is tb-infra's and I did not verify it: that the failing build arms the NMI pulse on the bridge's
taken event while the tree today arms it on the raise. What I did verify is the knob value in each run header.
