"""gen_test_cmp_zcmp_basic: Zcmp cm.push / cm.pop / cm.popret / cm.popretz / cm.mvsa01 / cm.mva01s
architectural effects (plan group gen_cmp_zcmp_basic, gen_test_plan.md AREA CMP).

Program: dv/auto_dv/tests/gen_programs/gen_cmp_zcmp_basic_prog.py at the run seed (testlist
`program: {generator: ..., seed: run}`; red fixtures `generator_args: ["--red", "--red-item", "TP-CMP-nnn"]`,
one deviation per built item, prog.RED_ITEMS). plan(seed) draws the scenario list (all 48 (rlist, spimm)
prog.PUSH_REPEATS times for push and once for pop in random order, all 56 cm.mvsa01 pairs, all 64
cm.mva01s pairs, popret/popretz with rlist prog.RET_PINNED_RLIST pinned plus random combinations at word
and half aligned targets, one hazard producer per pattern, one minstret-wrapped cm.* per kind, four
back-to-back patterns, one fall-through cm.* per kind after a ret) and computes every expectation from
the Zcmp specification; the program stores RAW observations to the EOT register (report channel), this
test compares them. Nothing here re-derives the program's intent a second way: report_count() is plan.k;
the plan pins (pinned pop combinations, the ret rlist, the push repeat count) are the generator's named
tables, cited there to the plan section.

Items built (fire_tp_cmp_<nnn>), each on its per-seed architectural observable:
  TP-CMP-039 cm.push over all 48 (rlist, spimm), each >= PUSH_REPEATS times per seed: frame words ==
             predicted registers (list top at sp-4, ra at sp-4N), poison slots untouched,
             sp_new == sp_old - stack_adj.
  TP-CMP-040 rlist 4, all spimm: one word (ra) at sp-4, rest of the frame untouched, sp -= 16+16*spimm.
  TP-CMP-041 rlist 15, all spimm: x27..x18, x9, x8, x1 at sp-4..sp-52, sp -= 64+16*spimm.
  TP-CMP-042 rlist 5..14: rlist-3 words in the predicted register order, slot N+1 untouched.
  TP-CMP-043 push and pop: sp_old/sp_new words, sp delta == base(rlist) + 16*spimm, all seven stack_adj
             values observed (the frame words of the same scenarios are 039's and 045's).
  TP-CMP-045 cm.pop over all 48: list registers == frame words at sp + stack_adj - 4k, non-list
             registers unchanged, sp += stack_adj.
  TP-CMP-046 pinned (8,1): s3 == 44(sp), ra == 28(sp), sp += 48; (15,3): x27 == 108(sp) .. x1 == 60(sp),
             sp += 112.
  TP-CMP-047 cm.popret: the target's marker store, registers, sp; targets at both alignments.
  TP-CMP-048 cm.popretz: as 047 plus a0 == 0 at the target (a0 nonzero before).
  TP-CMP-049 the ret uses the loaded ra: the stale x1 points at a decoy block whose marker never shows;
             rlist 4 for popret and popretz.
  TP-CMP-050 cm.mvsa01 all 56 pairs: the two sreg' == a0, a1, the other six unchanged.
  TP-CMP-052 cm.mva01s all 56 distinct pairs: a0, a1 == the mapped sources.
  TP-CMP-053 cm.mva01s r1s' == r2s' (8): a0 == a1 == the source, program continues (no trap).
  TP-CMP-055 minstret once per cm.*: csrr before / csrr after one cm.* of each kind, delta == 2.
  TP-CMP-066 back-to-back push;pop, pop;push, mvsa01;mva01s, mva01s;mvsa01: architectural results; the
             push;pop pops a longer rlist at the same stack_adj so a register the push never stored is
             loaded (a same-rlist pop would restore every register to its own value and a pop that loads
             nothing would be invisible).
  TP-CMP-069 hazards: sw slot then cm.pop, ALU write then cm.push, load then cm.push, load then
             cm.mva01s: the micro-op consumed the producer's value.
  TP-CMP-073 a cm.* halfword at the ret's PC+2, every kind once: the ret reached its target (marker), the
             fall-through cm.* executed later through a jump produced its full effect.
Deferred halves (not buildable at HEAD, need TB Infra ASK 5 RVFI export / ASK 4 bus records): the
rvfi_ext_expanded_insn_valid/_last tags and micro-op counts (039-048, 055, 066), rvfi_insn 0x00008067 and
rvfi_pc_wdata of the ret (047, 048), the addi deferral delta 1+W and dbus timing (049, 066), the single
ibus redirect and ret-once (073), the per-delay-class repetition (069; layers are off at HEAD). The
cpuctrlsts.icache_enable = 0 precondition of TP-CMP-066/073 serves those bus-derived halves; it is not
programmed: the CSR resets to 0 (doc/03_reference/cs_registers.rst, cpuctrlsts) and the program never
writes cpuctrlsts, so the icache stays disabled for the whole run without a CSR access.
Item NOT built: TP-CMP-068 (cm.push with sp near 0 / cm.pop near 0xFFFFFFFF): the TB memory map has no
writable words at 0x0..0x40 or 0xFFFFFF00..0xFFFFFFFF and the store-address observation is a dbus
monitor record (ASK 4).
Canonical feature IDs covered (gen_feature_list.md Section 3): F-CMP-039 (TP-039; TP-042 F-CMP-042 and
TP-043 F-CMP-043 FOLDED into it; TP-066 F-CMP-065 FOLDED into it), F-CMP-040, F-CMP-041, F-CMP-045
(TP-046 F-CMP-046 FOLDED into it), F-CMP-047, F-CMP-048, F-CMP-049, F-CMP-050, F-CMP-052 (TP-053
F-CMP-053 FOLDED into it), F-CMP-055, F-CMP-068 (TP-069), F-CMP-070 (TP-073); F-CMP-067 (TP-068) not
covered. Odd return addresses are left out: rvfi_pc_wdata bit 0 is bug candidate B13 (its _xfail group).
Knobs: knob_dmem_rvalid_delay, knob_dmem_gnt_delay, knob_imem_rvalid_delay, knob_imem_gnt_delay (the
items' Knobs lines; all timing-only, no program handler needed).
Checkers relied on (always on): the ISA comparator with Zcmp micro-op folding (gen_isa_compare rows),
gen_chk_rvfi_proto, the bus protocol checkers; the fire-checks here are the test-level compare that
gen_test_plan.md Section 0a assigns to gen_chk_zcmp_seq. declare_bins() takes the template default (the plan's bins of the items the fire_tp methods name, checked against the
rendered manifest in finish(); the entry stays unwired until gen_fcov_pkg lands).
MODULE=dv.auto_dv.tests.gen_test_cmp_zcmp_basic, TOPLEVEL=gen_tb_top.
"""
import cocotb

from dv.auto_dv.tests import gen_test_lib as lib
from dv.auto_dv.tests.gen_programs import gen_cmp_zcmp_basic_prog as prog
from dv.auto_dv.tests.gen_test_template import GenTest

_PLANS = {}


def _plan(seed):
    """The program's plan for this run seed (built once; the generator is deterministic per seed)."""
    if seed not in _PLANS:
        _PLANS[seed] = prog.plan(seed)
    return _PLANS[seed]


def _symbols(image):
    """Global symbols of the linked program (label -> address) from the image sidecar."""
    return {k: int(v, 16) for k, v in image.sidecar.get("symbols", {}).items()}


def _detail(scs, words, bad, extra=""):
    s = f"{len(scs)} scenarios, {words} report words checked, {len(bad)} mismatches"
    if extra:
        s += "; " + extra
    if bad:
        s += "; first: " + bad[0]
    return s


class CmpZcmpBasic(GenTest):
    name = "gen_test_cmp_zcmp_basic"
    # The items' Knobs lines (dmem/imem rvalid and gnt delay regimes), all timing-only.
    schedulable = ("knob_dmem_rvalid_delay", "knob_dmem_gnt_delay", "knob_imem_rvalid_delay", "knob_imem_gnt_delay")
    # items of the plan group this test does not check, with the reason (two-sided against the group by the structure check)
    # bins this test does not guarantee per run, with the reason and its class (gen_test_template.bins_not_hit)
    bins_not_hit = {
        "gen_cmp_zcmp_hazard_cg.cp_hazard.popret_ra_deferred":
            "seed-dependent: hit at some seeds and not others, so this test does not guarantee it per run; PLANNED in traceability, credited from the merged report",
        "gen_cmp_zcmp_hazard_cg.cp_hazard.popretz_ft_cm":
            "seed-dependent: hit at 39 of 40 seeds in the wave at 4017573 (gen_wave_4017573/gen_wave_census.txt), so this test does not guarantee it per run; PLANNED in traceability, credited from the merged report",
        "gen_cmp_zcmp_hazard_cg.cp_rlist_class.r15":
            "seed-dependent: hit at some seeds and not others, so this test does not guarantee it per run; PLANNED in traceability, credited from the merged report",
        "gen_cmp_zcmp_hazard_cg.cr_ft_kind.popret_ft_cm_cm_mva01s":
            "seed-dependent: hit at some seeds and not others, so this test does not guarantee it per run; PLANNED in traceability, credited from the merged report",
        "gen_cmp_zcmp_hazard_cg.cr_ft_kind.popret_ft_cm_cm_mvsa01":
            "seed-dependent: hit at some seeds and not others, so this test does not guarantee it per run; PLANNED in traceability, credited from the merged report",
        "gen_cmp_zcmp_hazard_cg.cr_ft_kind.popret_ft_cm_cm_pop":
            "stimulus: the program does not generate this first-then instruction pair",
        "gen_cmp_zcmp_hazard_cg.cr_ft_kind.popret_ft_cm_cm_popret":
            "seed-dependent: hit at some seeds and not others, so this test does not guarantee it per run; PLANNED in traceability, credited from the merged report",
        "gen_cmp_zcmp_hazard_cg.cr_ft_kind.popret_ft_cm_cm_popretz":
            "seed-dependent: hit at some seeds and not others, so this test does not guarantee it per run; PLANNED in traceability, credited from the merged report",
        "gen_cmp_zcmp_hazard_cg.cr_ft_kind.popret_ft_cm_cm_push":
            "seed-dependent: hit at 21 of 40 seeds in the wave at 4017573 (gen_wave_4017573/gen_wave_census.txt), so this test does not guarantee it per run; PLANNED in traceability, credited from the merged report",
        "gen_cmp_zcmp_hazard_cg.cr_ft_kind.popretz_ft_cm_cm_mva01s":
            "seed-dependent: hit at some seeds and not others, so this test does not guarantee it per run; PLANNED in traceability, credited from the merged report",
        "gen_cmp_zcmp_hazard_cg.cr_ft_kind.popretz_ft_cm_cm_mvsa01":
            "seed-dependent: hit at some seeds and not others, so this test does not guarantee it per run; PLANNED in traceability, credited from the merged report",
        "gen_cmp_zcmp_hazard_cg.cr_ft_kind.popretz_ft_cm_cm_pop":
            "seed-dependent: hit at 16 of 40 seeds in the wave at 4017573 (gen_wave_4017573/gen_wave_census.txt), so this test does not guarantee it per run; the cross follows its component cp_hazard.popretz_ft_cm, itself under the bar at 39 of 40; PLANNED in traceability, credited from the merged report",
        "gen_cmp_zcmp_hazard_cg.cr_ft_kind.popretz_ft_cm_cm_popret":
            "seed-dependent: hit at some seeds and not others, so this test does not guarantee it per run; PLANNED in traceability, credited from the merged report",
        "gen_cmp_zcmp_hazard_cg.cr_ft_kind.popretz_ft_cm_cm_popretz":
            "seed-dependent: hit at some seeds and not others, so this test does not guarantee it per run; PLANNED in traceability, credited from the merged report",
        "gen_cmp_zcmp_hazard_cg.cr_ft_kind.popretz_ft_cm_cm_push":
            "stimulus: the program does not generate this first-then instruction pair",
        "gen_cmp_zcmp_hazard_cg.cr_hazard_delay.load_pushed_reg_then_push_long":
            "seed-dependent: hit at some seeds and not others, so this test does not guarantee it per run; PLANNED in traceability, credited from the merged report",
        "gen_cmp_zcmp_hazard_cg.cr_hazard_delay.load_pushed_reg_then_push_min1":
            "seed-dependent: hit at some seeds and not others, so this test does not guarantee it per run; PLANNED in traceability, credited from the merged report",
        "gen_cmp_zcmp_hazard_cg.cr_hazard_delay.load_pushed_reg_then_push_short":
            "stimulus: the program does not generate this hazard shape at this delay",
        "gen_cmp_zcmp_hazard_cg.cr_hazard_delay.load_then_mva01s_long":
            "stimulus: the program does not generate this hazard shape at this delay",
        "gen_cmp_zcmp_hazard_cg.cr_hazard_delay.load_then_mva01s_min1":
            "seed-dependent: hit at some seeds and not others, so this test does not guarantee it per run; PLANNED in traceability, credited from the merged report",
        "gen_cmp_zcmp_hazard_cg.cr_hazard_delay.load_then_mva01s_short":
            "seed-dependent: hit at some seeds and not others, so this test does not guarantee it per run; PLANNED in traceability, credited from the merged report",
        "gen_cmp_zcmp_hazard_cg.cr_hazard_delay.popret_ra_deferred_long":
            "seed-dependent: hit at some seeds and not others, so this test does not guarantee it per run; PLANNED in traceability, credited from the merged report",
        "gen_cmp_zcmp_hazard_cg.cr_hazard_delay.popret_ra_deferred_short":
            "seed-dependent: hit at some seeds and not others, so this test does not guarantee it per run; PLANNED in traceability, credited from the merged report",
        "gen_cmp_zcmp_hazard_cg.cr_hazard_delay.store_same_slot_then_pop_long":
            "stimulus: the program does not generate this hazard shape at this delay",
        "gen_cmp_zcmp_hazard_cg.cr_hazard_delay.store_same_slot_then_pop_min1":
            "seed-dependent: hit at some seeds and not others, so this test does not guarantee it per run; PLANNED in traceability, credited from the merged report",
        "gen_cmp_zcmp_hazard_cg.cr_hazard_delay.store_same_slot_then_pop_short":
            "seed-dependent: hit at some seeds and not others, so this test does not guarantee it per run; PLANNED in traceability, credited from the merged report",
        "gen_cmp_zcmp_hazard_cg.cr_hazard_delay.write_pushed_reg_then_push_long":
            "seed-dependent: hit at some seeds and not others, so this test does not guarantee it per run; PLANNED in traceability, credited from the merged report",
        "gen_cmp_zcmp_hazard_cg.cr_hazard_delay.write_pushed_reg_then_push_min1":
            "seed-dependent: hit at some seeds and not others, so this test does not guarantee it per run; PLANNED in traceability, credited from the merged report",
        "gen_cmp_zcmp_hazard_cg.cr_hazard_delay.write_pushed_reg_then_push_short":
            "stimulus: the program does not generate this hazard shape at this delay",
        "gen_cmp_zcmp_hazard_cg.cr_hazard_rlist.load_pushed_reg_then_push_r15":
            "stimulus: the program does not generate this hazard shape with this rlist",
        "gen_cmp_zcmp_hazard_cg.cr_hazard_rlist.load_pushed_reg_then_push_r4":
            "stimulus: the program does not generate this hazard shape with this rlist",
        "gen_cmp_zcmp_hazard_cg.cr_hazard_rlist.store_same_slot_then_pop_r15":
            "stimulus: the program does not generate this hazard shape with this rlist",
        "gen_cmp_zcmp_hazard_cg.cr_hazard_rlist.store_same_slot_then_pop_r4":
            "stimulus: the program does not generate this hazard shape with this rlist",
        "gen_cmp_zcmp_hazard_cg.cr_hazard_rlist.store_same_slot_then_pop_r5_14":
            "seed-dependent: hit at 32 of 40 seeds in the wave at 4017573 (gen_wave_4017573/gen_wave_census.txt), so this test does not guarantee it per run; PLANNED in traceability, credited from the merged report",
        "gen_cmp_zcmp_hazard_cg.cr_hazard_rlist.write_pushed_reg_then_push_r15":
            "stimulus: the program does not generate this hazard shape with this rlist",
        "gen_cmp_zcmp_hazard_cg.cr_hazard_rlist.write_pushed_reg_then_push_r4":
            "stimulus: the program does not generate this hazard shape with this rlist",
        "gen_cmp_zcmp_hazard_cg.cr_hazard_rlist.write_pushed_reg_then_push_r5_14":
            "seed-dependent: hit at 34 of 40 seeds in the wave at 4017573 (gen_wave_4017573/gen_wave_census.txt), so this test does not guarantee it per run; PLANNED in traceability, credited from the merged report",
        "gen_cmp_zcmp_mv_cg.cr_insn_hazard.cm_mvsa01_load_prev":
            "stimulus: the program does not generate this move-instruction hazard shape",
        "gen_cmp_zcmp_pushpop_cg.cp_ret_align.odd":
            "stimulus: the program keeps the stack pointer even, so an odd return alignment is not generated",
        "gen_cmp_zcmp_pushpop_cg.cr_insn_delay.cm_pop_long":
            "seed-dependent: hit at some seeds and not others, so this test does not guarantee it per run; PLANNED in traceability, credited from the merged report",
        "gen_cmp_zcmp_pushpop_cg.cr_insn_delay.cm_pop_min1":
            "seed-dependent: hit at some seeds and not others, so this test does not guarantee it per run; PLANNED in traceability, credited from the merged report",
        "gen_cmp_zcmp_pushpop_cg.cr_insn_delay.cm_pop_mixed":
            "seed-dependent: hit at some seeds and not others, so this test does not guarantee it per run; PLANNED in traceability, credited from the merged report",
        "gen_cmp_zcmp_pushpop_cg.cr_insn_delay.cm_pop_short":
            "seed-dependent: hit at some seeds and not others, so this test does not guarantee it per run; PLANNED in traceability, credited from the merged report",
        "gen_cmp_zcmp_pushpop_cg.cr_insn_delay.cm_popret_long":
            "seed-dependent: hit at some seeds and not others, so this test does not guarantee it per run; PLANNED in traceability, credited from the merged report",
        "gen_cmp_zcmp_pushpop_cg.cr_insn_delay.cm_popret_min1":
            "seed-dependent: hit at some seeds and not others, so this test does not guarantee it per run; PLANNED in traceability, credited from the merged report",
        "gen_cmp_zcmp_pushpop_cg.cr_insn_delay.cm_popret_mixed":
            "seed-dependent: hit at some seeds and not others, so this test does not guarantee it per run; PLANNED in traceability, credited from the merged report",
        "gen_cmp_zcmp_pushpop_cg.cr_insn_delay.cm_popret_short":
            "seed-dependent: hit at some seeds and not others, so this test does not guarantee it per run; PLANNED in traceability, credited from the merged report",
        "gen_cmp_zcmp_pushpop_cg.cr_insn_delay.cm_popretz_long":
            "seed-dependent: hit at some seeds and not others, so this test does not guarantee it per run; PLANNED in traceability, credited from the merged report",
        "gen_cmp_zcmp_pushpop_cg.cr_insn_delay.cm_popretz_min1":
            "seed-dependent: hit at some seeds and not others, so this test does not guarantee it per run; PLANNED in traceability, credited from the merged report",
        "gen_cmp_zcmp_pushpop_cg.cr_insn_delay.cm_popretz_mixed":
            "seed-dependent: hit at some seeds and not others, so this test does not guarantee it per run; PLANNED in traceability, credited from the merged report",
        "gen_cmp_zcmp_pushpop_cg.cr_insn_delay.cm_popretz_short":
            "stimulus: the program does not generate this instruction with this delay class",
        "gen_cmp_zcmp_pushpop_cg.cr_insn_delay.cm_push_long":
            "seed-dependent: hit at some seeds and not others, so this test does not guarantee it per run; PLANNED in traceability, credited from the merged report",
        "gen_cmp_zcmp_pushpop_cg.cr_insn_delay.cm_push_min1":
            "seed-dependent: hit at some seeds and not others, so this test does not guarantee it per run; PLANNED in traceability, credited from the merged report",
        "gen_cmp_zcmp_pushpop_cg.cr_insn_delay.cm_push_mixed":
            "seed-dependent: hit at some seeds and not others, so this test does not guarantee it per run; PLANNED in traceability, credited from the merged report",
        "gen_cmp_zcmp_pushpop_cg.cr_insn_delay.cm_push_short":
            "seed-dependent: hit at some seeds and not others, so this test does not guarantee it per run; PLANNED in traceability, credited from the merged report",
        "gen_cmp_zcmp_pushpop_cg.cr_insn_rlist_spimm.cm_popret_r10_s0":
            "seed-dependent: hit at some seeds and not others, so this test does not guarantee it per run; PLANNED in traceability, credited from the merged report",
        "gen_cmp_zcmp_pushpop_cg.cr_insn_rlist_spimm.cm_popret_r10_s1":
            "seed-dependent: hit at some seeds and not others, so this test does not guarantee it per run; PLANNED in traceability, credited from the merged report",
        "gen_cmp_zcmp_pushpop_cg.cr_insn_rlist_spimm.cm_popret_r10_s2":
            "seed-dependent: hit at some seeds and not others, so this test does not guarantee it per run; PLANNED in traceability, credited from the merged report",
        "gen_cmp_zcmp_pushpop_cg.cr_insn_rlist_spimm.cm_popret_r10_s3":
            "stimulus: the program draws a subset of the rlist and spimm space per run, so this combination of the full product is not generated",
        "gen_cmp_zcmp_pushpop_cg.cr_insn_rlist_spimm.cm_popret_r11_s0":
            "stimulus: the program draws a subset of the rlist and spimm space per run, so this combination of the full product is not generated",
        "gen_cmp_zcmp_pushpop_cg.cr_insn_rlist_spimm.cm_popret_r11_s1":
            "stimulus: the program draws a subset of the rlist and spimm space per run, so this combination of the full product is not generated",
        "gen_cmp_zcmp_pushpop_cg.cr_insn_rlist_spimm.cm_popret_r11_s2":
            "stimulus: the program draws a subset of the rlist and spimm space per run, so this combination of the full product is not generated",
        "gen_cmp_zcmp_pushpop_cg.cr_insn_rlist_spimm.cm_popret_r11_s3":
            "stimulus: the program draws a subset of the rlist and spimm space per run, so this combination of the full product is not generated",
        "gen_cmp_zcmp_pushpop_cg.cr_insn_rlist_spimm.cm_popret_r12_s0":
            "seed-dependent: hit at some seeds and not others, so this test does not guarantee it per run; PLANNED in traceability, credited from the merged report",
        "gen_cmp_zcmp_pushpop_cg.cr_insn_rlist_spimm.cm_popret_r12_s1":
            "stimulus: the program draws a subset of the rlist and spimm space per run, so this combination of the full product is not generated",
        "gen_cmp_zcmp_pushpop_cg.cr_insn_rlist_spimm.cm_popret_r12_s2":
            "stimulus: the program draws a subset of the rlist and spimm space per run, so this combination of the full product is not generated",
        "gen_cmp_zcmp_pushpop_cg.cr_insn_rlist_spimm.cm_popret_r12_s3":
            "seed-dependent: hit at some seeds and not others, so this test does not guarantee it per run; PLANNED in traceability, credited from the merged report",
        "gen_cmp_zcmp_pushpop_cg.cr_insn_rlist_spimm.cm_popret_r13_s0":
            "stimulus: the program draws a subset of the rlist and spimm space per run, so this combination of the full product is not generated",
        "gen_cmp_zcmp_pushpop_cg.cr_insn_rlist_spimm.cm_popret_r13_s1":
            "seed-dependent: hit at some seeds and not others, so this test does not guarantee it per run; PLANNED in traceability, credited from the merged report",
        "gen_cmp_zcmp_pushpop_cg.cr_insn_rlist_spimm.cm_popret_r13_s2":
            "stimulus: the program draws a subset of the rlist and spimm space per run, so this combination of the full product is not generated",
        "gen_cmp_zcmp_pushpop_cg.cr_insn_rlist_spimm.cm_popret_r13_s3":
            "seed-dependent: hit at some seeds and not others, so this test does not guarantee it per run; PLANNED in traceability, credited from the merged report",
        "gen_cmp_zcmp_pushpop_cg.cr_insn_rlist_spimm.cm_popret_r14_s0":
            "stimulus: the program draws a subset of the rlist and spimm space per run, so this combination of the full product is not generated",
        "gen_cmp_zcmp_pushpop_cg.cr_insn_rlist_spimm.cm_popret_r14_s1":
            "seed-dependent: hit at some seeds and not others, so this test does not guarantee it per run; PLANNED in traceability, credited from the merged report",
        "gen_cmp_zcmp_pushpop_cg.cr_insn_rlist_spimm.cm_popret_r14_s2":
            "stimulus: the program draws a subset of the rlist and spimm space per run, so this combination of the full product is not generated",
        "gen_cmp_zcmp_pushpop_cg.cr_insn_rlist_spimm.cm_popret_r14_s3":
            "stimulus: the program draws a subset of the rlist and spimm space per run, so this combination of the full product is not generated",
        "gen_cmp_zcmp_pushpop_cg.cr_insn_rlist_spimm.cm_popret_r15_s0":
            "seed-dependent: hit at some seeds and not others, so this test does not guarantee it per run; PLANNED in traceability, credited from the merged report",
        "gen_cmp_zcmp_pushpop_cg.cr_insn_rlist_spimm.cm_popret_r15_s1":
            "stimulus: the program draws a subset of the rlist and spimm space per run, so this combination of the full product is not generated",
        "gen_cmp_zcmp_pushpop_cg.cr_insn_rlist_spimm.cm_popret_r15_s2":
            "stimulus: the program draws a subset of the rlist and spimm space per run, so this combination of the full product is not generated",
        "gen_cmp_zcmp_pushpop_cg.cr_insn_rlist_spimm.cm_popret_r15_s3":
            "stimulus: the program draws a subset of the rlist and spimm space per run, so this combination of the full product is not generated",
        "gen_cmp_zcmp_pushpop_cg.cr_insn_rlist_spimm.cm_popret_r4_s0":
            "stimulus: the program draws a subset of the rlist and spimm space per run, so this combination of the full product is not generated",
        "gen_cmp_zcmp_pushpop_cg.cr_insn_rlist_spimm.cm_popret_r4_s1":
            "seed-dependent: hit at 11 of 40 seeds in the wave at 4017573 (gen_wave_4017573/gen_wave_census.txt), so this test does not guarantee it per run; PLANNED in traceability, credited from the merged report",
        "gen_cmp_zcmp_pushpop_cg.cr_insn_rlist_spimm.cm_popret_r4_s2":
            "seed-dependent: hit at some seeds and not others, so this test does not guarantee it per run; PLANNED in traceability, credited from the merged report",
        "gen_cmp_zcmp_pushpop_cg.cr_insn_rlist_spimm.cm_popret_r4_s3":
            "seed-dependent: hit at some seeds and not others, so this test does not guarantee it per run; PLANNED in traceability, credited from the merged report",
        "gen_cmp_zcmp_pushpop_cg.cr_insn_rlist_spimm.cm_popret_r5_s0":
            "stimulus: the program draws a subset of the rlist and spimm space per run, so this combination of the full product is not generated",
        "gen_cmp_zcmp_pushpop_cg.cr_insn_rlist_spimm.cm_popret_r5_s1":
            "stimulus: the program draws a subset of the rlist and spimm space per run, so this combination of the full product is not generated",
        "gen_cmp_zcmp_pushpop_cg.cr_insn_rlist_spimm.cm_popret_r5_s2":
            "seed-dependent: hit at some seeds and not others, so this test does not guarantee it per run; PLANNED in traceability, credited from the merged report",
        "gen_cmp_zcmp_pushpop_cg.cr_insn_rlist_spimm.cm_popret_r5_s3":
            "stimulus: the program draws a subset of the rlist and spimm space per run, so this combination of the full product is not generated",
        "gen_cmp_zcmp_pushpop_cg.cr_insn_rlist_spimm.cm_popret_r6_s0":
            "stimulus: the program draws a subset of the rlist and spimm space per run, so this combination of the full product is not generated",
        "gen_cmp_zcmp_pushpop_cg.cr_insn_rlist_spimm.cm_popret_r6_s1":
            "stimulus: the program draws a subset of the rlist and spimm space per run, so this combination of the full product is not generated",
        "gen_cmp_zcmp_pushpop_cg.cr_insn_rlist_spimm.cm_popret_r6_s2":
            "seed-dependent: hit at some seeds and not others, so this test does not guarantee it per run; PLANNED in traceability, credited from the merged report",
        "gen_cmp_zcmp_pushpop_cg.cr_insn_rlist_spimm.cm_popret_r6_s3":
            "seed-dependent: hit at some seeds and not others, so this test does not guarantee it per run; PLANNED in traceability, credited from the merged report",
        "gen_cmp_zcmp_pushpop_cg.cr_insn_rlist_spimm.cm_popret_r7_s0":
            "seed-dependent: hit at some seeds and not others, so this test does not guarantee it per run; PLANNED in traceability, credited from the merged report",
        "gen_cmp_zcmp_pushpop_cg.cr_insn_rlist_spimm.cm_popret_r7_s1":
            "stimulus: the program draws a subset of the rlist and spimm space per run, so this combination of the full product is not generated",
        "gen_cmp_zcmp_pushpop_cg.cr_insn_rlist_spimm.cm_popret_r7_s2":
            "seed-dependent: hit at some seeds and not others, so this test does not guarantee it per run; PLANNED in traceability, credited from the merged report",
        "gen_cmp_zcmp_pushpop_cg.cr_insn_rlist_spimm.cm_popret_r7_s3":
            "seed-dependent: hit at some seeds and not others, so this test does not guarantee it per run; PLANNED in traceability, credited from the merged report",
        "gen_cmp_zcmp_pushpop_cg.cr_insn_rlist_spimm.cm_popret_r8_s0":
            "stimulus: the program draws a subset of the rlist and spimm space per run, so this combination of the full product is not generated",
        "gen_cmp_zcmp_pushpop_cg.cr_insn_rlist_spimm.cm_popret_r8_s1":
            "seed-dependent: hit at some seeds and not others, so this test does not guarantee it per run; PLANNED in traceability, credited from the merged report",
        "gen_cmp_zcmp_pushpop_cg.cr_insn_rlist_spimm.cm_popret_r8_s2":
            "stimulus: the program draws a subset of the rlist and spimm space per run, so this combination of the full product is not generated",
        "gen_cmp_zcmp_pushpop_cg.cr_insn_rlist_spimm.cm_popret_r8_s3":
            "stimulus: the program draws a subset of the rlist and spimm space per run, so this combination of the full product is not generated",
        "gen_cmp_zcmp_pushpop_cg.cr_insn_rlist_spimm.cm_popret_r9_s0":
            "seed-dependent: hit at some seeds and not others, so this test does not guarantee it per run; PLANNED in traceability, credited from the merged report",
        "gen_cmp_zcmp_pushpop_cg.cr_insn_rlist_spimm.cm_popret_r9_s1":
            "stimulus: the program draws a subset of the rlist and spimm space per run, so this combination of the full product is not generated",
        "gen_cmp_zcmp_pushpop_cg.cr_insn_rlist_spimm.cm_popret_r9_s2":
            "stimulus: the program draws a subset of the rlist and spimm space per run, so this combination of the full product is not generated",
        "gen_cmp_zcmp_pushpop_cg.cr_insn_rlist_spimm.cm_popret_r9_s3":
            "stimulus: the program draws a subset of the rlist and spimm space per run, so this combination of the full product is not generated",
        "gen_cmp_zcmp_pushpop_cg.cr_insn_rlist_spimm.cm_popretz_r10_s0":
            "stimulus: the program draws a subset of the rlist and spimm space per run, so this combination of the full product is not generated",
        "gen_cmp_zcmp_pushpop_cg.cr_insn_rlist_spimm.cm_popretz_r10_s1":
            "stimulus: the program draws a subset of the rlist and spimm space per run, so this combination of the full product is not generated",
        "gen_cmp_zcmp_pushpop_cg.cr_insn_rlist_spimm.cm_popretz_r10_s2":
            "stimulus: the program draws a subset of the rlist and spimm space per run, so this combination of the full product is not generated",
        "gen_cmp_zcmp_pushpop_cg.cr_insn_rlist_spimm.cm_popretz_r10_s3":
            "stimulus: the program draws a subset of the rlist and spimm space per run, so this combination of the full product is not generated",
        "gen_cmp_zcmp_pushpop_cg.cr_insn_rlist_spimm.cm_popretz_r11_s0":
            "stimulus: the program draws a subset of the rlist and spimm space per run, so this combination of the full product is not generated",
        "gen_cmp_zcmp_pushpop_cg.cr_insn_rlist_spimm.cm_popretz_r11_s1":
            "seed-dependent: hit at some seeds and not others, so this test does not guarantee it per run; PLANNED in traceability, credited from the merged report",
        "gen_cmp_zcmp_pushpop_cg.cr_insn_rlist_spimm.cm_popretz_r11_s2":
            "seed-dependent: hit at some seeds and not others, so this test does not guarantee it per run; PLANNED in traceability, credited from the merged report",
        "gen_cmp_zcmp_pushpop_cg.cr_insn_rlist_spimm.cm_popretz_r11_s3":
            "seed-dependent: hit at some seeds and not others, so this test does not guarantee it per run; PLANNED in traceability, credited from the merged report",
        "gen_cmp_zcmp_pushpop_cg.cr_insn_rlist_spimm.cm_popretz_r12_s0":
            "stimulus: the program draws a subset of the rlist and spimm space per run, so this combination of the full product is not generated",
        "gen_cmp_zcmp_pushpop_cg.cr_insn_rlist_spimm.cm_popretz_r12_s1":
            "stimulus: the program draws a subset of the rlist and spimm space per run, so this combination of the full product is not generated",
        "gen_cmp_zcmp_pushpop_cg.cr_insn_rlist_spimm.cm_popretz_r12_s2":
            "stimulus: the program draws a subset of the rlist and spimm space per run, so this combination of the full product is not generated",
        "gen_cmp_zcmp_pushpop_cg.cr_insn_rlist_spimm.cm_popretz_r12_s3":
            "seed-dependent: hit at some seeds and not others, so this test does not guarantee it per run; PLANNED in traceability, credited from the merged report",
        "gen_cmp_zcmp_pushpop_cg.cr_insn_rlist_spimm.cm_popretz_r13_s0":
            "seed-dependent: hit at some seeds and not others, so this test does not guarantee it per run; PLANNED in traceability, credited from the merged report",
        "gen_cmp_zcmp_pushpop_cg.cr_insn_rlist_spimm.cm_popretz_r13_s1":
            "stimulus: the program draws a subset of the rlist and spimm space per run, so this combination of the full product is not generated",
        "gen_cmp_zcmp_pushpop_cg.cr_insn_rlist_spimm.cm_popretz_r13_s2":
            "stimulus: the program draws a subset of the rlist and spimm space per run, so this combination of the full product is not generated",
        "gen_cmp_zcmp_pushpop_cg.cr_insn_rlist_spimm.cm_popretz_r13_s3":
            "seed-dependent: hit at some seeds and not others, so this test does not guarantee it per run; PLANNED in traceability, credited from the merged report",
        "gen_cmp_zcmp_pushpop_cg.cr_insn_rlist_spimm.cm_popretz_r14_s0":
            "stimulus: the program draws a subset of the rlist and spimm space per run, so this combination of the full product is not generated",
        "gen_cmp_zcmp_pushpop_cg.cr_insn_rlist_spimm.cm_popretz_r14_s1":
            "seed-dependent: hit at some seeds and not others, so this test does not guarantee it per run; PLANNED in traceability, credited from the merged report",
        "gen_cmp_zcmp_pushpop_cg.cr_insn_rlist_spimm.cm_popretz_r14_s2":
            "seed-dependent: hit at some seeds and not others, so this test does not guarantee it per run; PLANNED in traceability, credited from the merged report",
        "gen_cmp_zcmp_pushpop_cg.cr_insn_rlist_spimm.cm_popretz_r14_s3":
            "stimulus: the program draws a subset of the rlist and spimm space per run, so this combination of the full product is not generated",
        "gen_cmp_zcmp_pushpop_cg.cr_insn_rlist_spimm.cm_popretz_r15_s0":
            "stimulus: the program draws a subset of the rlist and spimm space per run, so this combination of the full product is not generated",
        "gen_cmp_zcmp_pushpop_cg.cr_insn_rlist_spimm.cm_popretz_r15_s1":
            "stimulus: the program draws a subset of the rlist and spimm space per run, so this combination of the full product is not generated",
        "gen_cmp_zcmp_pushpop_cg.cr_insn_rlist_spimm.cm_popretz_r15_s2":
            "seed-dependent: hit at some seeds and not others, so this test does not guarantee it per run; PLANNED in traceability, credited from the merged report",
        "gen_cmp_zcmp_pushpop_cg.cr_insn_rlist_spimm.cm_popretz_r15_s3":
            "stimulus: the program draws a subset of the rlist and spimm space per run, so this combination of the full product is not generated",
        "gen_cmp_zcmp_pushpop_cg.cr_insn_rlist_spimm.cm_popretz_r4_s0":
            "seed-dependent: hit at some seeds and not others, so this test does not guarantee it per run; PLANNED in traceability, credited from the merged report",
        "gen_cmp_zcmp_pushpop_cg.cr_insn_rlist_spimm.cm_popretz_r4_s1":
            "stimulus: the program draws a subset of the rlist and spimm space per run, so this combination of the full product is not generated",
        "gen_cmp_zcmp_pushpop_cg.cr_insn_rlist_spimm.cm_popretz_r4_s2":
            "seed-dependent: hit at some seeds and not others, so this test does not guarantee it per run; PLANNED in traceability, credited from the merged report",
        "gen_cmp_zcmp_pushpop_cg.cr_insn_rlist_spimm.cm_popretz_r4_s3":
            "seed-dependent: hit at some seeds and not others, so this test does not guarantee it per run; PLANNED in traceability, credited from the merged report",
        "gen_cmp_zcmp_pushpop_cg.cr_insn_rlist_spimm.cm_popretz_r5_s0":
            "seed-dependent: hit at some seeds and not others, so this test does not guarantee it per run; PLANNED in traceability, credited from the merged report",
        "gen_cmp_zcmp_pushpop_cg.cr_insn_rlist_spimm.cm_popretz_r5_s1":
            "stimulus: the program draws a subset of the rlist and spimm space per run, so this combination of the full product is not generated",
        "gen_cmp_zcmp_pushpop_cg.cr_insn_rlist_spimm.cm_popretz_r5_s2":
            "seed-dependent: hit at some seeds and not others, so this test does not guarantee it per run; PLANNED in traceability, credited from the merged report",
        "gen_cmp_zcmp_pushpop_cg.cr_insn_rlist_spimm.cm_popretz_r5_s3":
            "stimulus: the program draws a subset of the rlist and spimm space per run, so this combination of the full product is not generated",
        "gen_cmp_zcmp_pushpop_cg.cr_insn_rlist_spimm.cm_popretz_r6_s0":
            "stimulus: the program draws a subset of the rlist and spimm space per run, so this combination of the full product is not generated",
        "gen_cmp_zcmp_pushpop_cg.cr_insn_rlist_spimm.cm_popretz_r6_s1":
            "seed-dependent: hit at some seeds and not others, so this test does not guarantee it per run; PLANNED in traceability, credited from the merged report",
        "gen_cmp_zcmp_pushpop_cg.cr_insn_rlist_spimm.cm_popretz_r6_s2":
            "stimulus: the program draws a subset of the rlist and spimm space per run, so this combination of the full product is not generated",
        "gen_cmp_zcmp_pushpop_cg.cr_insn_rlist_spimm.cm_popretz_r6_s3":
            "stimulus: the program draws a subset of the rlist and spimm space per run, so this combination of the full product is not generated",
        "gen_cmp_zcmp_pushpop_cg.cr_insn_rlist_spimm.cm_popretz_r7_s0":
            "stimulus: the program draws a subset of the rlist and spimm space per run, so this combination of the full product is not generated",
        "gen_cmp_zcmp_pushpop_cg.cr_insn_rlist_spimm.cm_popretz_r7_s1":
            "stimulus: the program draws a subset of the rlist and spimm space per run, so this combination of the full product is not generated",
        "gen_cmp_zcmp_pushpop_cg.cr_insn_rlist_spimm.cm_popretz_r7_s2":
            "stimulus: the program draws a subset of the rlist and spimm space per run, so this combination of the full product is not generated",
        "gen_cmp_zcmp_pushpop_cg.cr_insn_rlist_spimm.cm_popretz_r7_s3":
            "stimulus: the program draws a subset of the rlist and spimm space per run, so this combination of the full product is not generated",
        "gen_cmp_zcmp_pushpop_cg.cr_insn_rlist_spimm.cm_popretz_r8_s0":
            "seed-dependent: hit at some seeds and not others, so this test does not guarantee it per run; PLANNED in traceability, credited from the merged report",
        "gen_cmp_zcmp_pushpop_cg.cr_insn_rlist_spimm.cm_popretz_r8_s1":
            "seed-dependent: hit at some seeds and not others, so this test does not guarantee it per run; PLANNED in traceability, credited from the merged report",
        "gen_cmp_zcmp_pushpop_cg.cr_insn_rlist_spimm.cm_popretz_r8_s2":
            "stimulus: the program draws a subset of the rlist and spimm space per run, so this combination of the full product is not generated",
        "gen_cmp_zcmp_pushpop_cg.cr_insn_rlist_spimm.cm_popretz_r8_s3":
            "seed-dependent: hit at some seeds and not others, so this test does not guarantee it per run; PLANNED in traceability, credited from the merged report",
        "gen_cmp_zcmp_pushpop_cg.cr_insn_rlist_spimm.cm_popretz_r9_s0":
            "seed-dependent: hit at some seeds and not others, so this test does not guarantee it per run; PLANNED in traceability, credited from the merged report",
        "gen_cmp_zcmp_pushpop_cg.cr_insn_rlist_spimm.cm_popretz_r9_s1":
            "stimulus: the program draws a subset of the rlist and spimm space per run, so this combination of the full product is not generated",
        "gen_cmp_zcmp_pushpop_cg.cr_insn_rlist_spimm.cm_popretz_r9_s2":
            "stimulus: the program draws a subset of the rlist and spimm space per run, so this combination of the full product is not generated",
        "gen_cmp_zcmp_pushpop_cg.cr_insn_rlist_spimm.cm_popretz_r9_s3":
            "stimulus: the program draws a subset of the rlist and spimm space per run, so this combination of the full product is not generated",
        "gen_cmp_zcmp_pushpop_cg.cr_ret_align.cm_popret_odd":
            "stimulus: depends on an odd return alignment, which the program does not generate",
        "gen_cmp_zcmp_pushpop_cg.cr_ret_align.cm_popretz_odd":
            "stimulus: depends on an odd return alignment, which the program does not generate",
    }
    not_built = {
        "TP-CMP-068": "needs writable low addresses and the bus records of the event export",
    }

    def report_count(self):
        return _plan(self.seed).k

    def fire_check(self):
        self.plan = _plan(self.seed)
        self.syms = _symbols(self.image)
        self.fire_program_verdict()
        self.fire_tp_cmp_039()
        self.fire_tp_cmp_040()
        self.fire_tp_cmp_041()
        self.fire_tp_cmp_042()
        self.fire_tp_cmp_043()
        self.fire_tp_cmp_045()
        self.fire_tp_cmp_046()
        self.fire_tp_cmp_047()
        self.fire_tp_cmp_048()
        self.fire_tp_cmp_049()
        self.fire_tp_cmp_050()
        self.fire_tp_cmp_052()
        self.fire_tp_cmp_053()
        self.fire_tp_cmp_055()
        self.fire_tp_cmp_066()
        self.fire_tp_cmp_069()
        self.fire_tp_cmp_073()

    def fire_program_verdict(self):
        code = int(self.h.b.evt_eot_code.value)
        floor = lib.program_min_retired(self.image, self.plan.min_retired)
        got = self.retired()
        have_base = "gen_stack" in self.syms
        ok = code == lib.TOHOST_PASS and len(self.reports) == self.plan.k and got >= floor and have_base
        self.check("fire_program_verdict", ok,
                   f"tohost code 0x{code:08x} (pass {lib.TOHOST_PASS}), reports {len(self.reports)} (plan {self.plan.k}), "
                   f"retired {got} (floor {floor}), gen_stack symbol {'present' if have_base else 'missing'}")

    def fire_tp_cmp_039(self):
        scs, words, bad = prog.audit(self.plan, self.reports, self.syms, lambda sc: sc.kind == "push")
        count = {c: 0 for c in prog.ALL_COMBOS}
        for sc in scs:
            count[(sc.rlist, sc.spimm)] += 1
        covered = {c for c, n in count.items() if n >= prog.PUSH_REPEATS}
        self.check("fire_tp_cmp_039", words > 0 and not bad and covered == prog.ALL_COMBOS,
                   _detail(scs, words, bad, f"cm.push over {len(covered)}/48 (rlist, spimm) each >= {prog.PUSH_REPEATS} "
                                            f"times (min {min(count.values())}); expected frame words == the predicted "
                                            "registers, poison slots untouched, sp_new == sp_old - stack_adj"))

    def fire_tp_cmp_040(self):
        scs, words, bad = prog.audit(self.plan, self.reports, self.syms, lambda sc: sc.kind == "push" and sc.rlist == 4)
        spimms = {sc.spimm for sc in scs}
        self.check("fire_tp_cmp_040", words > 0 and not bad and spimms == set(prog.SPIMMS),
                   _detail(scs, words, bad, f"cm.push {{ra}} spimm {sorted(spimms)}; expected ra at sp-4 as the only written "
                                            "word, sp -= 16+16*spimm"))

    def fire_tp_cmp_041(self):
        scs, words, bad = prog.audit(self.plan, self.reports, self.syms, lambda sc: sc.kind == "push" and sc.rlist == 15)
        spimms = {sc.spimm for sc in scs}
        self.check("fire_tp_cmp_041", words > 0 and not bad and spimms == set(prog.SPIMMS),
                   _detail(scs, words, bad, f"cm.push {{ra, s0-s11}} spimm {sorted(spimms)}; expected x27..x18, x9, x8, x1 at "
                                            "sp-4..sp-52, sp -= 64+16*spimm"))

    def fire_tp_cmp_042(self):
        scs, words, bad = prog.audit(self.plan, self.reports, self.syms, lambda sc: sc.kind == "push" and 5 <= sc.rlist <= 14)
        rlists = {sc.rlist for sc in scs}
        self.check("fire_tp_cmp_042", words > 0 and not bad and rlists == set(range(5, 15)),
                   _detail(scs, words, bad, f"cm.push rlist {sorted(rlists)}; expected rlist-3 words from the top register "
                                            "(3+rlist for 5..6, 11+rlist for 7..14) down to x1, slot N+1 untouched"))

    def fire_tp_cmp_043(self):
        # The sp words only: the frame words of the same scenarios are TP-CMP-039's and TP-CMP-045's observables.
        scs, words, bad = prog.audit(self.plan, self.reports, self.syms, lambda sc: sc.kind in ("push", "pop"),
                                     tags=("sp_old", "sp_new"))
        seen = {}
        for sc in scs:
            adj = prog.sp_adjust(self.plan, self.reports, sc)
            seen.setdefault(adj, set()).add((sc.kind, sc.rlist, sc.spimm))
            if adj != prog.stack_adj(sc.rlist, sc.spimm):
                bad.append(f"{prog.describe(sc)}: sp delta {adj} expected {prog.stack_adj(sc.rlist, sc.spimm)}")
        values = set(seen) & prog.STACK_ADJ_VALUES
        self.check("fire_tp_cmp_043", words > 0 and not bad and values == prog.STACK_ADJ_VALUES,
                   _detail(scs, words, bad, f"sp words; stack_adj values observed {sorted(values)} (expected all of "
                                            f"{sorted(prog.STACK_ADJ_VALUES)}); each sp delta == base(rlist) + 16*spimm"))

    def fire_tp_cmp_045(self):
        scs, words, bad = prog.audit(self.plan, self.reports, self.syms, lambda sc: sc.kind == "pop")
        combos = {(sc.rlist, sc.spimm) for sc in scs}
        self.check("fire_tp_cmp_045", words > 0 and not bad and combos == prog.ALL_COMBOS,
                   _detail(scs, words, bad, f"cm.pop over {len(combos)}/48 (rlist, spimm); expected list registers == the "
                                            "frame words at sp + stack_adj - 4k, other registers unchanged, sp += stack_adj"))

    def fire_tp_cmp_046(self):
        pins = set(prog.POP_PINNED_COMBOS)
        scs, words, bad = prog.audit(self.plan, self.reports, self.syms,
                                     lambda sc: sc.kind == "pop" and (sc.rlist, sc.spimm) in pins)
        combos = {(sc.rlist, sc.spimm) for sc in scs}
        self.check("fire_tp_cmp_046", words > 0 and not bad and combos == pins,
                   _detail(scs, words, bad, f"pinned cm.pop {sorted(combos)}; expected (8,1): s3 == 44(sp) .. ra == 28(sp), "
                                            "sp += 48; (15,3): x27 == 108(sp) .. x1 == 60(sp), sp += 112"))

    def fire_tp_cmp_047(self):
        scs, words, bad = prog.audit(self.plan, self.reports, self.syms, lambda sc: sc.kind == "popret")
        aligns = {self.syms.get(sc.target, 1) % 4 for sc in scs}
        self.check("fire_tp_cmp_047", words > 0 and not bad and aligns == {0, 2},
                   _detail(scs, words, bad, f"cm.popret target alignments {sorted(aligns)} (expected word and half); "
                                            "expected the target's marker, restored registers, sp += stack_adj"))

    def fire_tp_cmp_048(self):
        scs, words, bad = prog.audit(self.plan, self.reports, self.syms, lambda sc: sc.kind == "popretz")
        aligns = {self.syms.get(sc.target, 1) % 4 for sc in scs}
        self.check("fire_tp_cmp_048", words > 0 and not bad and aligns == {0, 2},
                   _detail(scs, words, bad, f"cm.popretz target alignments {sorted(aligns)} (expected word and half); "
                                            "expected a0 == 0 at the target, marker, registers, sp += stack_adj"))

    def fire_tp_cmp_049(self):
        scs = [sc for sc in self.plan.scenarios if sc.kind in prog.RET_KINDS]
        markers = [(sc, i) for sc in scs for i in sc.reports if self.plan.reports[i].tag == "ret_marker"]
        got = {i: (self.reports[i] if i < len(self.reports) else None) for _, i in markers}
        stale = [prog.describe(sc) for sc, i in markers if got[i] == sc.decoy_mark]
        fell = [prog.describe(sc) for sc, i in markers if got[i] == sc.bad]
        other = [prog.describe(sc) for sc, i in markers if got[i] != sc.good and got[i] not in (sc.decoy_mark, sc.bad)]
        r4 = {sc.kind for sc in scs if sc.rlist == prog.RET_PINNED_RLIST}
        self.check("fire_tp_cmp_049", bool(markers) and not stale and not fell and not other and r4 == set(prog.RET_KINDS),
                   f"{len(markers)} ret markers: stale-ra (decoy) {len(stale)}, fall-through {len(fell)}, other {len(other)}; "
                   f"rlist {prog.RET_PINNED_RLIST} present for {sorted(r4)} (expected popret and popretz); expected every "
                   "marker == the target's"
                   + (f"; first: {(stale + fell + other)[0]}" if stale or fell or other else ""))

    def fire_tp_cmp_050(self):
        scs, words, bad = prog.audit(self.plan, self.reports, self.syms, lambda sc: sc.kind == "mvsa01")
        pairs = {(sc.r1s, sc.r2s) for sc in scs}
        want = {(a, b) for a in prog.SREGS for b in prog.SREGS if a != b}
        self.check("fire_tp_cmp_050", words > 0 and not bad and pairs == want,
                   _detail(scs, words, bad, f"cm.mvsa01 over {len(pairs)}/56 pairs; expected r1s' == a0, r2s' == a1, the "
                                            "other sreg' unchanged"))

    def fire_tp_cmp_052(self):
        scs, words, bad = prog.audit(self.plan, self.reports, self.syms, lambda sc: sc.kind == "mva01s" and sc.r1s != sc.r2s)
        pairs = {(sc.r1s, sc.r2s) for sc in scs}
        want = {(a, b) for a in prog.SREGS for b in prog.SREGS if a != b}
        self.check("fire_tp_cmp_052", words > 0 and not bad and pairs == want,
                   _detail(scs, words, bad, f"cm.mva01s over {len(pairs)}/56 distinct pairs; expected a0 == r1s', a1 == r2s'"))

    def fire_tp_cmp_053(self):
        scs, words, bad = prog.audit(self.plan, self.reports, self.syms, lambda sc: sc.kind == "mva01s" and sc.r1s == sc.r2s)
        regs = {sc.r1s for sc in scs}
        self.check("fire_tp_cmp_053", words > 0 and not bad and regs == set(prog.SREGS),
                   _detail(scs, words, bad, f"cm.mva01s r1s' == r2s' over {len(regs)}/8 sreg'; expected a0 == a1 == the source "
                                            "and the program continued (no trap)"))

    def fire_tp_cmp_055(self):
        deltas = prog.minstret_deltas(self.plan, self.reports)
        kinds = {sc.kind for sc, _ in deltas}
        bad = [f"{prog.describe(sc)}: minstret delta {d}" for sc, d in deltas if d != 2]
        self.check("fire_tp_cmp_055", bool(deltas) and not bad and kinds == set(prog.CM_KINDS),
                   f"{len(deltas)} minstret-wrapped cm.* over kinds {sorted(kinds)} (expected all six); expected delta 2 "
                   f"(csrr + one retirement per cm.*), {len(bad)} deviations" + (f"; first: {bad[0]}" if bad else ""))

    def fire_tp_cmp_066(self):
        scs, words, bad = prog.audit(self.plan, self.reports, self.syms, lambda sc: sc.kind in prog.B2B_KINDS)
        kinds = {sc.kind for sc in scs}
        # push;pop is only a check of the pop when its list is longer than the push's at the same stack_adj.
        visible = all(sc.aux["rlist2"] > sc.rlist and prog.stack_adj(sc.aux["rlist2"], sc.aux["spimm2"])
                      == prog.stack_adj(sc.rlist, sc.spimm) for sc in scs if sc.kind == "b2b_push_pop")
        self.check("fire_tp_cmp_066", words > 0 and not bad and kinds == set(prog.B2B_KINDS) and visible,
                   _detail(scs, words, bad, f"back-to-back patterns {sorted(kinds)} (expected all four), push;pop loads a "
                                            f"register the push never stored: {visible}; expected sp, registers and "
                                            "frame words of both instructions"))

    def fire_tp_cmp_069(self):
        scs, words, bad = prog.audit(self.plan, self.reports, self.syms, lambda sc: sc.variant in prog.HAZ_VARIANTS)
        variants = {sc.variant for sc in scs}
        self.check("fire_tp_cmp_069", words > 0 and not bad and variants == set(prog.HAZ_VARIANTS),
                   _detail(scs, words, bad, f"hazard patterns {sorted(variants)} (expected all four); expected the micro-op "
                                            "consumed the immediately preceding producer's value"))

    def fire_tp_cmp_073(self):
        scs, words, bad = prog.audit(self.plan, self.reports, self.syms, lambda sc: sc.variant == "ft")
        inner = {sc.inner.kind for sc in scs}
        self.check("fire_tp_cmp_073", words > 0 and not bad and inner == set(prog.CM_KINDS),
                   _detail(scs, words, bad, f"fall-through cm.* kinds {sorted(inner)} (expected all six); expected the ret's "
                                            "target marker and the full effect of the fall-through cm.* executed later"))


@cocotb.test()
async def gen_test_cmp_zcmp_basic(dut):
    await CmpZcmpBasic(dut).run()
