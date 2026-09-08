"""gen_test_pmc_ctrl: mcountinhibit / mcounteren control of the counters (opentitan configuration, MHPMCounterNum 10).

Group gen_pmc_ctrl (dv/auto_dv/docs/gen_test_plan.md, AREA PMC). Items built, one fire-check method each:
  TP-PMC-022 mcountinhibit WARL (fire_tp_pmc_022)                                          F-PMC-020
  TP-PMC-023 each inhibit bit freezes exactly its counter (fire_tp_pmc_023)                F-PMC-021
  TP-PMC-024 IR=1 removes the speculative +1 of minstret / mhpmcounter10 (fire_tp_pmc_024) F-PMC-022
  TP-PMC-025 counter written while inhibited resumes from the value (fire_tp_pmc_025)      F-PMC-023
  TP-PMC-026 M-mode counter CSRs illegal in U-mode (fire_tp_pmc_026)                      F-PMC-024
  TP-PMC-027 mcounteren WARL, reset 0 (fire_tp_pmc_027)                                    F-PMC-025
  TP-PMC-028 mcounteren writes dropped without a trap unless the pin is On (fire_tp_pmc_028)   F-PMC-026
  TP-PMC-029 U-mode alias reads gated per bit by mcounteren (fire_tp_pmc_029)              F-PMC-027
  TP-PMC-030 aliases above HPM_LAST illegal in U, 0 in M (fire_tp_pmc_030)                 F-PMC-028
  TP-PMC-031 write ops to the alias ranges illegal in M and U (fire_tp_pmc_031)            F-PMC-029
  TP-PMC-032 time/timeh unimplemented, TM reads 0 (fire_tp_pmc_032)                        F-PMC-030
  TP-PMC-033 inhibited but enabled alias readable in U with the frozen value (fire_tp_pmc_033)   F-PMC-031
  TP-PMC-056 inhibit set and cleared inside an event window (fire_tp_pmc_056)              F-PMC-021, F-PMC-001
Canonical feature IDs covered (gen_feature_list.md Section 3): F-PMC-001, F-PMC-020..F-PMC-031. Not built: TP-PMC-057
(mcounteren_writable_i transitions between two writes): the pin is driven from the static plusarg knob
knob_mcounteren_writable (gen_ctrl_if.sv, regime_set_consumer none), no bridge command changes it mid-run (TB ask filed by
the Test Writer); its cr_pin_tr_effect bins are not declared.

Program: dv/auto_dv/tests/gen_programs/gen_pmc_ctrl_prog.py, one program per run seed; plan(seed, pin=<knob value>) is the
single source of the report count and of every expectation. The pin value (+gen_knob_mcounteren_writable, default on) is
read through lib.plus and handed to the plan: it changes the expectations of the mcounteren writes and of everything
gated by mcounteren (applied when on, dropped without a trap when off or invalid), never the program text, so the
default entry (on) and the check-tier entry gen_test_pmc_ctrl_pin_off (+gen_knob_mcounteren_writable=off) run the same
image. Under off / invalid the per-seed floors of 027, 029 and 033 change to their dropped-branch form (the writes read
back unchanged, every gated U-mode read traps, the frozen-value clause is not exercised): the fire-checks state which
branch they proved. The manifest is keyed by test name, so both entries name this one manifest, which declares the pin-on
bins (the pin-off run cannot hit cp_pin.on, cp_effect.applied, the *_on_app crosses, the *_u_set_ok alias bins); the
dropped-branch bins (cp_pin.off, cr_en_pin_effect.en_off_drop and their kin) are declared by no manifest, so under measured
false the pin-off entry's declared set is this manifest's, and before the group is promoted to measured declare_bins()
becomes pin-aware and the pin-off entry gets its own manifest (a joint landing, the covergroup set reads every manifest).

Every expectation is a report word compared with the generator's model: csrr read-backs of mcountinhibit / mcounteren,
counter deltas the program computes (after minus before) per window, the handler's trap records (mcause << 16 | MPP << 8 |
instruction index from the armed block base) and difference words (xor / sub / sltu of two counter reads). Raw counter
values are never expected (they are the comparator's consistency compares, value verification pending the ctr_* checkers).
Exactness (plan TP-PMC-023): minstret, loads, stores, jumps, branches (separated from a preceding load/store by an
ALU instruction), taken branches and compressed retirements are exact per window; mcycle and the mul/div wait counters
are bound class (lower bound one cycle per instruction / one stall per mulh / div, upper bound the window's mcycle
delta); the IF stall counter is bound class with floor 1 when the window has a taken control transfer (the fetch
bubble); the LSU stall counter is bound class without a floor (a fast grant/response regime showed 0 stall cycles over
10+ memory ops), so 023's 'moved' clause is not asserted for it. An inhibited counter's delta is exact 0. The items' RVFI wording (rvfi_trap items) is realised through the record stream: a missing or extra trap moves every
later record, the positional compare and fire_program_verdict's count catch it; rvfi_trap = 0 on the M-mode control writes
is implied by the program reaching its end (an unarmed M-mode trap ends it with the fail code).

Stated deviations: the debug-window variants of 022 / 027 / 032 are not built (no debug entry in this group); 024's WB
coincidence (the csrr committing in the load's retire cycle) is the item's export-row clause, witnessed only through the
template when the export lands; this test proves the RVFI-only fallback (every read under IR=1 equals the frozen value
across lw;csrr, add;csrr, csrr runs and the c.lw;csrr mhpmcounter10 form, two passes for a warm icache; under IR=0 the
read pair's difference equals the instructions retired between them). 028's pin monitor clause is the same kind of
export clause: the fallback is the read-back under the run's pin value. 033's counter N is drawn from the memory-free
classes (cycle, instret, jumps, branches, taken, mul wait, div wait): U-mode has no data region. 056's CY variant checks
mcycle as bound class (the cycles outside the inhibited segment are not observable through the report channel).

Red fixtures (generator --red [--red-item TP-PMC-0nn], one per built item, expectations unchanged; the pinned red of the
entry is TP-PMC-022, check name fire_tp_pmc_022): see the generator docstring; each red fails exactly its item's
fire_tp_pmc_<nnn>. An explicit --red-item TP-PMC-057 is refused by the generator (not a built item).

Knobs: the items name instr_mix / priv_regime (program-side markers of this generated program) and the imem / dmem
rvalid delays; schedulable = lib.TIMING_ONLY_KNOBS; knob_mcounteren_writable is a static pin knob (never scheduled),
knob_debug_req_regime and knob_irq_regime are never declared (no debug ROM, no interrupt handler). Always-on checkers
relied on: gen_isa_compare (lock-step; its uvm_error fails the flow and is reported, never masked), rvfi_proto, the bus
protocol checkers; gen_chk_csr_readback and gen_chk_counters are unbuilt (plan Section 0a), their compares are carried
by the fire-checks here. gen_isa_compare follows this program with the ISA shim's counter model (dv/auto_dv/docs/gen_component_api_isa_shim.md): a step under mcountinhibit.IR = 1 retires instead of being synthesised as a trap,
minstret is served as Spike's count minus what Ibex did not count, mcountinhibit is masked and mhpmcounter13..31 / mhpmevent13..31
read as zero; what that record leaves unmodelled (the hazard variant of the high-word write corner, dummy instructions under the
counters knob) this program does not rely on for its checks. declare_bins() takes the template default (the plan's
bins of the built items minus bins_not_hit, checked against the rendered manifest in finish()).
MODULE=dv.auto_dv.tests.gen_test_pmc_ctrl, TOPLEVEL=gen_tb_top.
"""
import cocotb

from dv.auto_dv.tests import gen_test_lib as lib
from dv.auto_dv.tests.gen_test_template import GenTest
from dv.auto_dv.tests.gen_programs import gen_pmc_ctrl_prog as prog

PIN_KNOB = "knob_mcounteren_writable"


def pin_value():
    return str(lib.plus(PIN_KNOB, lib.knob_default(PIN_KNOB)))


def plan_of(test):
    """The seed's plan under the run's pin value (the program text is pin-independent)."""
    return prog.plan(test.seed, pin=pin_value())


def compare(plan, reports, idxs):
    """Compare the observed report words at idxs with the plan (abs / range / bound kinds); (compared, [mismatches])."""
    bad = []
    for i in idxs:
        if i >= len(reports):
            bad.append(f"idx {i} missing")
        elif not plan.matches(i, reports[i], reports):
            bad.append(f"idx {i} [{plan.reports[i].label}] expected {plan.describe(i)} got 0x{reports[i]:08x}")
    return len(idxs), bad


def summary(compared, bad, facts):
    head = f"{compared} words compared, {len(bad)} mismatches"
    if bad:
        head += " (first: " + "; ".join(bad[:3]) + ")"
    return head + "; " + facts


def word(reports, idx):
    return reports[idx] if idx is not None and 0 <= idx < len(reports) else None


def bit_seen(reports, idxs, b):
    return any(word(reports, i) is not None and (word(reports, i) >> b) & 1 for i in idxs)


class PmcCtrl(GenTest):
    name = "gen_test_pmc_ctrl"
    schedulable = lib.TIMING_ONLY_KNOBS
    # items of the plan group this test does not check, with the reason (two-sided against the group by the structure check)
    not_built = {
        "TP-PMC-057": "mcounteren_writable_i is a static plusarg knob (regime_set_consumer none); no mid-run pin driver exists (TB ask filed)",
    }
    # bins of built items one run cannot hit: no debug window in this group; the pin is static per run (the default entry
    # runs on: the off / invalid bins are declared by no manifest until the pin-off entry gets its own); 024's WB coincidence and 028's pin monitor are export
    # clauses witnessed through the template only (this test never issues a witness)
    bins_not_hit = {
        "gen_pmc_ctrl_csr_cg.cr_reg_mode_result.inh_dbg_ok": "no debug window in this group",
        "gen_pmc_ctrl_csr_cg.cr_reg_mode_result.en_dbg_ok": "no debug window in this group",
        "gen_pmc_ctrl_csr_cg.cp_mode.dbg": "no debug window in this group",
        "gen_pmc_alias_cg.cp_mode.dbg": "no debug window in this group",
        "gen_pmc_alias_cg.cr_alias_gate.cyc_dbg_ok": "no debug window in this group",
        "gen_pmc_alias_cg.cr_alias_gate.ir_dbg_ok": "no debug window in this group",
        "gen_pmc_alias_cg.cr_alias_gate.hf_dbg_ok": "no debug window in this group",
        "gen_pmc_ctrl_csr_cg.cp_pin.off": "the pin is a static per-run knob; the default entry runs on (the pin-off entry hits it but no manifest declares it until that entry has its own)",
        "gen_pmc_ctrl_csr_cg.cp_pin.invalid": "the pin is a static per-run knob; the default entry runs on (no invalid entry staged)",
        "gen_pmc_ctrl_csr_cg.cr_en_pin_effect.inh_off_app": "the pin is a static per-run knob; the default entry runs on",
        "gen_pmc_ctrl_csr_cg.cr_en_pin_effect.inh_inv_app": "the pin is a static per-run knob; the default entry runs on",
        "gen_pmc_ctrl_csr_cg.cr_en_pin_effect.en_off_drop": "the pin is a static per-run knob; the default entry runs on (the pin-off entry hits it but no manifest declares it until that entry has its own)",
        "gen_pmc_ctrl_csr_cg.cr_en_pin_effect.en_inv_drop": "the pin is a static per-run knob; the default entry runs on",
        "gen_pmc_minstret_cg.cr_inhibit_coh.on_retiring": "the csrr-in-the-load's-retire-cycle coincidence is 024's export-row clause (dbus rvalid), not observable through the report channel",
        "gen_pmc_minstret_cg.cr_inhibit_coh.off_retiring": "the csrr-in-the-load's-retire-cycle coincidence is 024's export-row clause (dbus rvalid), not observable through the report channel",
        "gen_pmc_minstret_cg.cp_coherence.wb_retiring": "the WB coincidence is 024's export-row clause, not observable through the report channel",
        "gen_wit_cycle_clause_cg.cp_clause.w_tp_pmc_024": "the export-row clause is checked through the template's witness only when the export lands; this test proves the RVFI-only fallback",
        "gen_wit_cycle_clause_cg.cp_clause.w_tp_pmc_028": "the pin monitor clause is checked through the template's witness only when the export lands; this test proves the read-back fallback",
    }

    def report_count(self):
        return plan_of(self).k

    def fire_check(self):
        self.fire_program_verdict()
        self.fire_tp_pmc_022()
        self.fire_tp_pmc_023()
        self.fire_tp_pmc_024()
        self.fire_tp_pmc_025()
        self.fire_tp_pmc_026()
        self.fire_tp_pmc_027()
        self.fire_tp_pmc_028()
        self.fire_tp_pmc_029()
        self.fire_tp_pmc_030()
        self.fire_tp_pmc_031()
        self.fire_tp_pmc_032()
        self.fire_tp_pmc_033()
        self.fire_tp_pmc_056()

    def fire_program_verdict(self):
        code = int(self.h.b.evt_eot_code.value)
        floor = lib.program_min_retired(self.image, plan_of(self).min_retired)
        got = self.retired()
        plan = plan_of(self)
        n, bad = compare(plan, self.reports, plan.item_indices("setup"))
        self.check("fire_program_verdict", code == lib.TOHOST_PASS and got >= floor and not bad and len(self.reports) == plan.k,
                   f"tohost code 0x{code:08x} (pass = {lib.TOHOST_PASS}); retired {got} (floor {floor}); reports {len(self.reports)} (k {plan.k}); "
                   f"pin {plan.pin}; " + summary(n, bad, "counter-phase setup writes"))

    def fire_warl(self, item, what):
        """022 / 027: every read-back per the WARL model; pattern x op classes; walking one over 32 bits; the writable bits
        read back 1 at least once (when the writes apply), TM and the bits above HPM_LAST never; the plain read first."""
        plan = plan_of(self)
        meta = plan.items[item]
        n, bad = compare(plan, self.reports, plan.item_indices(item))
        writes = meta["writes"]
        classes = {(p, prog.OP_CLASS[f]) for _i, f, p, _pre, _post, _op in writes}
        walk_bits = {op.bit_length() - 1 for _i, _f, p, _pre, _post, op in writes if p == "walking"}
        idxs = [i for i, *_r in writes]
        applies = item == "TP-PMC-022" or plan.applied()
        writable = all(bit_seen(self.reports, idxs, b) for b in prog.COUNTERS) if applies else not any(bit_seen(self.reports, idxs, b) for b in range(32))
        never = not bit_seen(self.reports, idxs, prog.TM) and not any(bit_seen(self.reports, idxs, b) for b in range(prog.HPM_LAST + 1, 32))
        plain = word(self.reports, meta["read_idx"])
        reset_ok = plain == 0
        ok = not bad and len(classes) >= 10 and walk_bits == set(range(32)) and writable and never and reset_ok and word(self.reports, meta["final_idx"]) == 0
        self.check(what, ok, summary(n, bad, f"{len(writes)} writes over {len(classes)} pattern x op classes, walking one over {len(walk_bits)} bits; "
                                             f"{'writable bits CY/IR/HPM read back 1' if applies else 'pin ' + plan.pin + ': every read-back 0 (writes dropped)'}: {writable}; "
                                             f"TM and bits above {prog.HPM_LAST} never 1: {never}; plain read 0x{plain if plain is not None else 0:x}; final restore 0"))

    def fire_tp_pmc_022(self):
        self.fire_warl("TP-PMC-022", "fire_tp_pmc_022")

    def fire_tp_pmc_027(self):
        self.fire_warl("TP-PMC-027", "fire_tp_pmc_027")

    def fire_tp_pmc_023(self):
        plan = plan_of(self)
        meta = plan.items["TP-PMC-023"]
        n, bad = compare(plan, self.reports, plan.item_indices("TP-PMC-023"))
        singles = {tuple(w["bits"]) for w in meta["windows"] if len(w["bits"]) == 1}
        multi = [w for w in meta["windows"] if len(w["bits"]) >= 2]
        frozen = moved = floors = 0
        for w in meta["windows"]:
            for c in prog.COUNTERS:
                d = word(self.reports, w["deltas"][c])
                if c in w["bits"]:
                    frozen += d == 0
                    floors += c in (prog.CY, prog.IR) or w["events"][c] >= 5 or c in (3, 4)
                elif c != 3:                       # the LSU stall counter has no floor (bound 0..cycles, compared above)
                    moved += d is not None and d > 0
        n_inh = sum(len(w["bits"]) for w in meta["windows"])
        n_free = sum(len(prog.COUNTERS) - len(w["bits"]) - (0 if 3 in w["bits"] else 1) for w in meta["windows"])
        ok = not bad and singles == {(c,) for c in prog.COUNTERS} and len(multi) >= 1 and frozen == floors == n_inh and moved == n_free
        self.check("fire_tp_pmc_023", ok, summary(n, bad, f"{len(meta['windows'])} windows ({len(singles)}/12 single-bit, {len(multi)} multi-bit): "
                                                        f"{frozen}/{n_inh} inhibited counters delta 0 with >= 5 independent events ({floors}), "
                                                        f"{moved}/{n_free} other counters moved (LSU stall counter: bound 0..cycles, no floor); exact classes compared, bound classes within [floor, mcycle delta]"))

    def fire_tp_pmc_024(self):
        plan = plan_of(self)
        meta = plan.items["TP-PMC-024"]
        n, bad = compare(plan, self.reports, plan.item_indices("TP-PMC-024"))
        forms = {f for _i, f in meta["frozen"]}
        equal = sum(1 for i, _f in meta["frozen"] + meta["hpm10"] if word(self.reports, i) == 0)
        ctrl = sum(1 for i, _f, d in meta["control"] if word(self.reports, i) == d)
        ok = not bad and forms == {"lw_csrr", "run", "add_csrr"} and len(meta["hpm10"]) >= 2 and equal == len(meta["frozen"]) + len(meta["hpm10"]) \
            and ctrl == len(meta["control"]) >= 3
        self.check("fire_tp_pmc_024", ok, summary(n, bad, f"IR=1: {len(meta['frozen'])} minstret reads over forms {sorted(forms)} (two passes) and "
                                                        f"{len(meta['hpm10'])} c.lw;csrr mhpmcounter10 reads under bit 10 all equal the frozen value: {equal}; "
                                                        f"IR=0 control: {ctrl}/{len(meta['control'])} read-pair differences equal the retired instructions"))

    def fire_tp_pmc_025(self):
        plan = plan_of(self)
        meta = plan.items["TP-PMC-025"]
        n, bad = compare(plan, self.reports, plan.item_indices("TP-PMC-025"))
        kinds = {e["kind"] for e in meta["episodes"]}
        frozen = sum(1 for e in meta["episodes"] if e["frozen_idx"] is None or word(self.reports, e["frozen_idx"]) == e["x"])
        above = sum(1 for e in meta["episodes"] if word(self.reports, e["final_idx"]) is not None and word(self.reports, e["final_idx"]) > e["x"])
        ld = any(e["ctr"] == 5 for e in meta["episodes"])
        ok = not bad and kinds == {"mcycle_inh_resume", "minstret_inh_resume", "hpm_inh_resume", "hpm_noinh"} and frozen == above == len(meta["episodes"]) and ld
        self.check("fire_tp_pmc_025", ok, summary(n, bad, f"{len(meta['episodes'])} episodes {sorted(kinds)} (counters {[prog.CTR_NAMES[e['ctr']] for e in meta['episodes']]}): "
                                                        f"frozen read equals the written value {frozen}, final read above it {above} (exact = written + events for "
                                                        f"minstret / HPM, bound for mcycle); loads counter among them: {ld}"))

    def fire_tp_pmc_026(self):
        plan = plan_of(self)
        meta = plan.items["TP-PMC-026"]
        n, bad = compare(plan, self.reports, plan.item_indices("TP-PMC-026"))
        acc = meta["accesses"]
        classes = {c for c, _w, _f in acc}
        rw = {w for _c, w, _f in acc}
        ok = not bad and len(acc) >= 12 and len(classes) == 9 and rw == {False, True} and len(meta["rec_idx"]) == len(acc) + 1
        self.check("fire_tp_pmc_026", ok, summary(n, bad, f"{len(acc)} U-mode accesses over {len(classes)} CSR classes (reads and writes {sorted(rw)}), "
                                                        f"{len(meta['rec_idx']) - 1} illegal-instruction records (mcause 2, MPP U) plus the ecall; "
                                                        f"mcountinhibit / mcounteren read back unchanged after the episode (compared)"))

    def fire_tp_pmc_028(self):
        plan = plan_of(self)
        meta = plan.items["TP-PMC-028"]
        n, bad = compare(plan, self.reports, plan.item_indices("TP-PMC-028"))
        applied = plan.applied()
        if applied:
            eff = sum(1 for i, _f, pre, post, _op in meta["writes"] if word(self.reports, i) == post)
            changed = sum(1 for i, _f, pre, post, _op in meta["writes"] if word(self.reports, i) == post != pre)
        else:
            eff = sum(1 for i, _f, pre, _post, _op in meta["writes"] if word(self.reports, i) == pre)
            changed = 0
        forms = {f for _i, f, *_r in meta["writes"]}
        legal = {leg for _recs, reads in meta["u_reads"] for _a, leg in reads}
        ok = not bad and eff == len(meta["writes"]) >= 3 and (changed >= 1 or not applied) and {"csrrw", "csrrs", "csrrc"} <= forms \
            and (legal == {True, False} if applied else legal == {False})
        self.check("fire_tp_pmc_028", ok, summary(n, bad, f"pin {plan.pin}: {len(meta['writes'])} mcounteren writes ({sorted(forms)}) "
                                                        f"{'applied (read-back == post-op value)' if applied else 'dropped without a trap (read-back == pre value)'}: {eff}" + (f" ({changed} changing the value)" if applied else "") + "; "
                                                        f"U-mode alias reads after each write followed the {'applied' if applied else 'unchanged'} value (legal set {sorted(legal)})"))

    def fire_tp_pmc_029(self):
        plan = plan_of(self)
        meta = plan.items["TP-PMC-029"]
        n, bad = compare(plan, self.reports, plan.item_indices("TP-PMC-029"))
        masks = {m["mask"] for m in meta["masks"]}
        legal_seen, illegal_seen = set(), set()
        for m in meta["masks"]:
            for a, h in m["reads"]:
                (legal_seen if (m["mask"] >> a) & 1 else illegal_seen).add((a, h))
        aliases = {(a, h) for a in prog.COUNTERS for h in (False, True)}
        marks = sum(1 for m in meta["masks"] if word(self.reports, m["mark_idx"]) == prog.MARK_029)
        if plan.applied():
            floor = {prog.HPM_CTRL_MASK, 0} <= masks and len(masks) >= 3 and legal_seen == aliases and illegal_seen == aliases
        else:
            floor = masks == {0} and illegal_seen == aliases and not legal_seen
        ok = not bad and floor and marks == len(meta["masks"])
        self.check("fire_tp_pmc_029", ok, summary(n, bad, f"pin {plan.pin}: {len(meta['masks'])} masks {[hex(m) for m in sorted(masks)]}; per alias (12 low + 12 high) "
                                                        f">= 1 U read with the bit set and no trap: {len(legal_seen)}/24, >= 1 with the bit clear trapping (mcause 2): "
                                                        f"{len(illegal_seen)}/24; M-mode reads of every alias under every mask without trap: {marks}/{len(meta['masks'])}"))

    def fire_tp_pmc_030(self):
        plan = plan_of(self)
        meta = plan.items["TP-PMC-030"]
        n, bad = compare(plan, self.reports, plan.item_indices("TP-PMC-030"))
        zeros = sum(1 for i, _k, _h in meta["m_reads"] if word(self.reports, i) == 0)
        halves = {h for _i, _k, h in meta["m_reads"]}
        ok = not bad and meta["u_n"] >= 12 and zeros == len(meta["m_reads"]) >= 12 and halves == {False, True}
        self.check("fire_tp_pmc_030", ok, summary(n, bad, f"{meta['u_n']} U-mode reads of hpmcounter{prog.HPM_LAST + 1}..31(h) trapped (mcause 2); "
                                                        f"{zeros}/{len(meta['m_reads'])} M-mode reads returned 0 (both halves: {halves == {False, True}})"))

    def fire_tp_pmc_031(self):
        plan = plan_of(self)
        meta = plan.items["TP-PMC-031"]
        n, bad = compare(plan, self.reports, plan.item_indices("TP-PMC-031"))
        m_forms = {f for _a, _h, f in meta["m_ops"]}
        u_forms = {f for _a, _h, f in meta["u_ops"]}
        ok = not bad and m_forms == set(prog.ALL_FORMS) and u_forms == set(prog.ALL_FORMS) and meta["n_ctrl"] >= 1 \
            and len(meta["m_idx"]) == len(meta["m_ops"]) and len(meta["u_idx"]) == len(meta["u_ops"]) + 1
        self.check("fire_tp_pmc_031", ok, summary(n, bad, f"{len(meta['m_ops'])} M-mode and {len(meta['u_ops'])} U-mode write ops to the alias ranges "
                                                        f"(forms M {sorted(m_forms)}, U {sorted(u_forms)}) all trapped (mcause 2); {meta['n_ctrl']} control reads "
                                                        f"(csrrs/csrrc x0 / uimm 0) in M without trap (no record between the ops)"))

    def fire_tp_pmc_032(self):
        plan = plan_of(self)
        meta = plan.items["TP-PMC-032"]
        n, bad = compare(plan, self.reports, plan.item_indices("TP-PMC-032"))
        tm = word(self.reports, meta["tm_idx"])
        tm_zero = tm is not None and not (tm >> prog.TM) & 1
        m_traps = sum(1 for _a, r in meta["m_body"] if r is not None)
        ok = not bad and m_traps == 4 and len(meta["m_idx"]) == 4 and len(meta["u_idx"]) == 4 and tm_zero
        self.check("fire_tp_pmc_032", ok, summary(n, bad, f"time / timeh: {m_traps} M-mode accesses (read and write form each) and 3 U-mode accesses trapped (mcause 2); "
                                                        f"mcounteren after csrs bit 1 read 0x{tm if tm is not None else 0:x} (TM 0: {tm_zero})"))

    def fire_tp_pmc_033(self):
        plan = plan_of(self)
        meta = plan.items["TP-PMC-033"]
        n, bad = compare(plan, self.reports, plan.item_indices("TP-PMC-033"))
        eps = {e["kind"]: e for e in meta["episodes"]}
        inh, noinh = eps["inh"], eps["noinh"]
        legal = inh["legal"]
        frozen = word(self.reports, inh["obs_idx"]) == (0 if legal else prog.SENT_A ^ prog.SENT_B)
        counting = word(self.reports, noinh["obs_idx"]) == 1
        ok = not bad and frozen and counting and inh["events"] >= 5 and len(inh["recs"]) == (1 if legal else 3)
        self.check("fire_tp_pmc_033", ok, summary(n, bad, f"pin {plan.pin}, counter {prog.CTR_NAMES[meta['n']]} enabled in mcounteren: "
                                                        + (f"two U-mode reads without trap with {inh['events']} events between them under the inhibit read equal: {frozen}; "
                                                           f"control with the inhibit clear: second read above the first: {counting}" if legal else
                                                           f"the writes were dropped, both U reads trapped (mcause 2) as modelled: {len(inh['recs']) == 3}; the frozen-value clause "
                                                           f"is proven by the pin-on entry")
                                                        + (f"; mcounteren bit cleared afterwards: the U read trapped" if meta["later_clear"] else "")))

    def fire_tp_pmc_056(self):
        plan = plan_of(self)
        meta = plan.items["TP-PMC-056"]
        n, bad = compare(plan, self.reports, plan.item_indices("TP-PMC-056"))
        shapes = {(w["n"], w["cleared"]) for w in meta["windows"]}
        partial = sum(1 for w in meta["windows"] if word(self.reports, w["delta_idx"]) == w["expected"] < w["total"])
        floors = all(w["e1"] >= 2 and w["e2"] >= 2 and (not w["cleared"] or w["e3"] >= 2) for w in meta["windows"])
        cy = [w for w in meta["windows"] if w["cy"]]
        ok = not bad and {(5, False), (6, False), (8, True), (10, False)} <= shapes and partial == len(meta["windows"]) and floors and len(cy) >= 1
        self.check("fire_tp_pmc_056", ok, summary(n, bad, f"{len(meta['windows'])} windows (counter, cleared) {sorted(shapes)}: {partial} deltas == E1 (+ E3 after the clear) and below the window's raw event total, "
                                                        f"E1 / E2 (/ E3) >= 2: {floors}; {len(cy)} CY variant(s) with mcycle bound class; mcountinhibit read back after each"))


@cocotb.test()
async def gen_test_pmc_ctrl(dut):
    await PmcCtrl(dut).run()
