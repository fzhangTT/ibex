# Ruling: sva_rvfi_irq_valid_exclusive fires legitimately; the property changes, not the stimulus

Committed reference (promoted 2026-09-04 from the rtl-arch working file
dv/auto_dv/work/rtl-arch/gen_rvfi_irq_valid_exclusive_ruling.md, same content apart from this paragraph); when
the working copy changes, this copy is re-promoted, and the working copy is never copied over this one without
carrying this paragraph. The run and build paths below are tb-infra working paths, named as provenance for the
reproducer; the ruling in Section 1 rests on the RTL citations in Sections 2 to 4, which resolve in this
repository.

Owner: rtl-arch. Written 2026-09-04T16:25Z from the RTL in this clone (rtl/ibex_core.sv, rtl/ibex_wb_stage.sv,
ibex_configs.yaml) and the property as built (dv/auto_dv/tb/gen_protocol_props.sv:299). Build configuration:
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
shape never aligns. A notification raised a short delay after an interrupt entry leaves the pipeline refilling,
so a retirement can complete at C+3 and the port coincides at C+4. The 36 firings across the two knob values are
consistent with that alignment. Section 7 settles which alignment the run took and corrects a guess made here
before the wave was read: this text first named a handler retirement as the likely coincident record, and in the
run no handler executes at all.

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

## 7. The wave confirmation

Read 2026-09-04T16:45Z from the shape-matched wave run whose log is
dv/auto_dv/evidence/gen_tdd_logs/mutations/gen_fu_l31b_nmi_wave_run.log. The dump itself is not retained and is
not durable, named here as the Orchestrator ruled: waves.fsdb under the wave root that log names, 2501858 bytes,
md5 44730e24c59e75c97cfe5e2ad13eb6f1, full hierarchy with SVA from time zero, build sources sha256
96697a6fee7025b4 per both its compile log and its run header, seed 1, knob window with the delay swept 1..8 per
event, armed on the taken event. Eleven firings with the first at 3655000 ps, matching the reproducer exactly.
Times below are nanoseconds; the file's own scale unit is 10 ps.

- The coincidence, at signal level. rvfi_valid rises to 1 at 3645 and falls at 3655; rvfi_ext_irq_valid rises to 1
  at 3645. Both are therefore high through the cycle that begins at 3645, and the assertion reports at 3655
  because it samples that cycle's pre-edge values. Sampling exactly at 3655 shows rvfi_valid already 0, which is
  the post-edge value and not what the property saw.
- The four-cycle offset holds. The pulse condition held during the cycle beginning 3605, where every term of the
  :1965 guard reads true: instr_valid_id 0, new_debug_req 0, new_nmi 1, ready_wb 1, captured_valid 0, with
  new_irq 0 so the cause is the non-maskable one alone. Then rvfi_irq_valid is high 3615 to 3625,
  rvfi_ext_stage_irq_valid[0] from 3625, [1] from 3635, and [2], the port, from 3645. On the retirement side
  instr_done_wb is high 3635 to 3645, which sets rvfi_stage_valid[1] at 3645, matching Section 5's rule that
  rvfi_valid is high at C+4 exactly when rvfi_wb_done was high at C+3.
- The retiring instruction, named from the program's own disassembly rather than a decode: order 42, pc
  0x80000120, encoding 0xfe629fe3, which the listing gives as `bne t0,t1,8000011e <loop>`, the backward branch of
  the program's main loop. rvfi_intr is 0 on that record, so it is not a trap-handler entry.
- The alignment, and it corrects Section 5's guess. One notification pulse and no second one, and no handler runs
  at all: irq_nm_i is a one-cycle pulse high 3610 to 3620, nmi_mode never rises anywhere in the window, and the
  program keeps retiring the same loop (pc 0x8000011e at 3605, 0x80000120 at 3645, 0x8000011e at 3735). So the
  coincident record is an ordinary instruction and this is the notification-with-no-entry case the :2130 comment
  describes, which is what the notification exists for. The stimulus pulse was gone before the controller could
  take it.

One finding the wave adds, and it makes the exclusivity premise worse rather than better. The port element is not a
one-cycle pulse: it stays high from 3645 to 3735, nine cycles. The hop into it is guarded by
`rvfi_wb_done | rvfi_ext_stage_irq_valid[1]` (:2192), so once the middle element clears, only a cycle containing a
retirement can clear the port. Clearing the flag therefore requires the very event the property forbids beside it,
and any retirement inside that window coincides. Here one did, in the window's first cycle, and the next
retirement at 3735 is the cycle the flag clears.

For Section 6's candidate: at the port rvfi_ext_nmi is 1 and rvfi_ext_pre_mip is 0, and at the condition cycle
new_irq is 0. So the disjunction holds here only through its non-maskable term, and this firing is a case the
pending-interrupt term alone would not cover, which makes it a ready red-first case for the replacement.

## 8. What the retained runs confirm, re-derived

Runs, retained by landing 32 and citable from the commit:
dv/auto_dv/evidence/gen_tdd_logs/mutations/gen_fu_l31b_nmi_take_window_reproducer.log (11 firings) and
gen_fu_l31b_nmi_take_late_reproducer.log (25 firings), with the wave run's log beside them. Each carries every
firing line with its picosecond time, the UVM error times, the cycle list and the count equality, so the figures
below are re-derivable from the commit alone.

The shape is not committed and cannot be reproduced from the tree as it stands. The knob
gen_knob_nmi_after_irq_delay is not in the committed tree: the knob table carries it in the working tree only.
The committed knob arms on the raise of a non-NMI line, as its own knob-table description states, while these runs
arm on the bridge's taken event through a two-hunk working-tree diff, with the delay swept 1..8 per event. The
sweep width matters: the first attempt at the wave used 1..17 and produced 28 firings rather than 11. No committed
build identity applies to a never-committed shape, and the retained headers say so rather than claiming one.

Re-derived from those logs, not taken from a relay:

- 11 firings in the window run and 25 in the late run, 36 in total. Each run's error count equals its firing
  count, so this property is the only failing mechanism in either.
- The window run's firing cycles are 361, 1242, 2780, 4207, 4684, 6711, 11623, 13764, 15603, 16590 and 18076.
- The firing confirmed in full is the first, cycle 361 of the window run: the assertion at
  gen_protocol_props.sv:299 started and failed at 3655000 ps with the offending term `(!rvfi_valid)`.
- The cycle numbers are the TB counter and map to time as (cycle + 4.5) x 10000 ps on all 11 window firings
  without exception. The build compiles with `-timescale=1ns/10ps`, which is why the logs' 10 ps unit yields
  3655000 ps for cycle 361 and fixes the clock at 10 ns.

That the offending term is the `!rvfi_valid` half is the whole of the disputed question: the property failed
because rvfi_valid was high while rvfi_ext_irq_valid was high, not because the flag was spurious.

Review rows answered. CR-31-L-3 and CM208-Low-4 are both addressed here: the runs behind these figures are the
three retained paths named above rather than a gitignored working directory, the knob is stated as absent from the
committed tree, and the configuration file citation in the header now names ibex_configs.yaml at the repository
root rather than a path under rtl/.
