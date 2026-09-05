"""gen_test_pmp_lock: PMP lock, TOR-lock and RLB rules of the opentitan configuration (PMPNumRegions 16, PMPGranularity 0).

Group gen_pmp_lock (dv/auto_dv/docs/gen_test_plan.md Section 4.4). Items, all built, one fire-check method each:
  TP-PMP-013 locked pmpcfg byte ignored, unlocked bytes of the word update (fire_tp_pmp_013)   F-PMP-007, F-PMP-019 -> FOLDED into F-PMP-007
  TP-PMP-014 locked entry: pmpaddr(i) write ignored (fire_tp_pmp_014)                          F-PMP-008
  TP-PMP-015 locked TOR i+1 protects pmpaddr(i), pmpcfg(i) stays writable (fire_tp_pmp_015)   F-PMP-009
  TP-PMP-016 pmpaddr(i) writable under a locked non-TOR i+1 (fire_tp_pmp_016)                  F-PMP-010 -> FOLDED into F-PMP-009
  TP-PMP-017 pmpaddr(i) writable under an unlocked TOR i+1 (fire_tp_pmp_017)                   F-PMP-011 -> FOLDED into F-PMP-009
  TP-PMP-018 pmpaddr(PMPNumRegions-1) depends on its own lock only (fire_tp_pmp_018)           F-PMP-012
  TP-PMP-019 L=1 with A=OFF locks the entry and blocks RLB (fire_tp_pmp_019)                   F-PMP-013
  TP-PMP-020 lock evaluated on the pre-write state, back-to-back second write ignored (fire_tp_pmp_020)   F-PMP-020, F-PMP-100 -> FOLDED into F-PMP-007
  TP-PMP-021 RLB=1 bypasses every lock effect on PMP CSR writes (fire_tp_pmp_021)              F-PMP-028
  TP-PMP-112 RLB cleared with locks present, adjacent locked write ignored (fire_tp_pmp_112)   F-PMP-027, F-PMP-028, F-PMP-007, F-PMP-008, F-PMP-009
Canonical feature IDs covered (gen_feature_list.md Section 3): F-PMP-007, F-PMP-008, F-PMP-009, F-PMP-012, F-PMP-013,
F-PMP-020, F-PMP-027, F-PMP-028. Items blocked: none.

The items' "RVFI:" fire-check wording is realised through the program report channel: every csrr read-back after a
PMP CSR write and the TP-PMP-019 probe load are report words the program stores to the EOT MMIO register, and the
program's own pass verdict is the tohost code; rvfi_trap = 0 on every write is implied by the program reaching its
end with no handler record (an M-mode trap ends the program with the fail code). Adjacency ("adjacent rvfi_order")
is by construction of the generated program: the two writes are consecutive instructions with no read-back in
between (RVFI export needed to observe the order numbers).

Program: dv/auto_dv/tests/gen_programs/gen_pmp_lock_prog.py, one program per run seed; plan(seed) is the single
source of the report count and of every expectation. Expectations come from the lock rules of the privileged spec
(machine.adoc "Locking and Privilege Mode", the mseccfg RLB rules of smepmp.adoc) as the shared PmpModel of
gen_pmp_csr_warl_prog states them; the RTL is a cross-check, never a source. Two expectations are layout-relative
(pmpaddr0 = end of .text, TP-PMP-019's pmpaddr = a probe-pool word) and resolve from the image's symbol table
(prog.sym.json); fire_program_layout checks the program's own report of those addresses against the same table.

One run has no wrapper reset, so the lock state only grows and the phase order is forced (generator docstring):
RLB=1 phase (021), the one RLB clear (112), then the RLB=0 items with MML=0, then an MML=1 tail on half of the
seeds. Dropped clauses, owner plan (no wrapper reset in one run): TP-PMP-112 variant C (a locked TOR at the clear
would break TP-PMP-019's all-locks-OFF condition later in the same run) and its repeated RLB clears; TP-PMP-019
runs with the clear set's A=OFF locks present (the bin condition, every locked entry A=OFF, holds); MML is 0 at
the clear; MMWP is never set; TP-PMP-112's adjacent write is the pmpcfg variant on every seed (one clear per power-on,
so one variant per test). bins_not_hit names the bins whose precondition this test does not apply, with the reason.

Red fixtures (generator --red [--red-item TP-PMP-0nn], one per item, expectations unchanged): at one site a write is
replaced by a read of the same CSR and the planned state is restored afterwards: 013 a lock-mix word write; 014, 015,
018 (second half), 019, 020 the lock-setting write so the follow-up write lands; 016, 017, 018 (first half), 021 a
write that should land; 112 the RLB clear so the adjacent locked write lands. A site is drawn only where the model says
the skipped write changes the read-back (013: a write that changes an unlocked lane; the generator asserts it), so each
red fails exactly its item's fire_tp_pmp_<nnn> and none is vacuous; the pinned red of the testlist entry is TP-PMP-013
(check name fire_tp_pmp_013).

Knobs: the items name knob:instr_mix csr_heavy (program-side region marker: this program is CSR-heavy by
construction) and, for 020 and 112, knob:imem_gnt_delay / knob:imem_rvalid_delay random, which are among the
timing-only regime knobs declared here. schedulable = lib.TIMING_ONLY_KNOBS (bus latencies, outstanding cap,
scramble-key delay), which the program tolerates; nothing is pinned.

Always-on checkers relied on: the ISA comparator (isa_rd carries every csrr read-back: the shim runs Spike with
PMPNumRegions 16, PMPGranularity 0 and Smepmp, PMP CSRs zeroed at reset; a nonzero UVM_ERROR count is reported,
never masked), rvfi_proto and the bus protocol checkers. gen_chk_csr_readback and gen_chk_pmp are unbuilt (plan
Section 0a), so the read-back comparisons are carried by the fire-checks here. declare_bins() takes the template
default (the plan's bins of the built items minus bins_not_hit, checked against the rendered manifest in finish()).
MODULE=dv.auto_dv.tests.gen_test_pmp_lock, TOPLEVEL=gen_tb_top.
"""
import cocotb

from dv.auto_dv.gen_tb.gen_knobs import MEMORY_MAP
from dv.auto_dv.tests import gen_test_lib as lib
from dv.auto_dv.tests.gen_test_template import GenTest
from dv.auto_dv.tests.gen_programs import gen_pmp_lock_prog as prog


def bases_of(test):
    """Layout bases of the running image from its symbol table (never from DUT-reported words)."""
    return prog.bases_from_symbols(test.image.sidecar.get("symbols", {}))


def compare(plan, reports, bases, idxs):
    """Compare the observed report words at idxs with the plan; returns (compared, [mismatch strings])."""
    bad = []
    for i in idxs:
        exp = plan.expected(i, bases)
        if i >= len(reports):
            bad.append(f"idx {i} missing")
        elif reports[i] != exp:
            bad.append(f"idx {i} [{plan.reports[i].label}] expected 0x{exp:08x} got 0x{reports[i]:08x}")
    return len(idxs), bad


def summary(compared, bad, facts):
    head = f"{compared} words compared, {len(bad)} mismatches"
    if bad:
        head += " (first: " + "; ".join(bad[:3]) + ")"
    return head + "; " + facts


def word(reports, idx):
    return reports[idx] if 0 <= idx < len(reports) else None


def lane_byte(w, lane):
    return None if w is None else (w >> (8 * lane)) & 0xFF


def unchanged(plan, reports, idx, pre):
    """A write the plan says is ignored: the read-back equals the pre-write value (rel-kind words are compared by the plan)."""
    w = word(reports, idx)
    return w is not None and (plan.reports[idx].kind != "abs" or w == pre)


def changed(reports, idx, pre):
    w = word(reports, idx)
    return w is not None and w != pre


def locked(b):
    """L of a pmpcfg byte read-back (None = no word)."""
    return b is not None and prog.byte_fields(b)[0] == 1


def mode(b):
    """A of a pmpcfg byte read-back."""
    return prog.byte_fields(b)[1]


class PmpLock(GenTest):
    name = "gen_test_pmp_lock"
    schedulable = lib.TIMING_ONLY_KNOBS
    # items of the plan group this test does not check, with the reason (two-sided against the group by the structure check)
    not_built = {}
    # bins of built items whose precondition this test does not apply (rule (g)), with the reason; left out of the manifest
    bins_not_hit = {
        "gen_pmp_addr_write_cg.cr_self_lock.locked_rlb1_written":
            "declaration: the sampler sets self_locked from the entry's lock bit AND NOT mseccfg.RLB "
            "(gen_fcov_pkg.sv), so cp_self_lock.locked and cp_rlb.rlb1 are mutually exclusive by construction and "
            "no stimulus reaches this cross bin; this entry does rewrite locked entries under RLB=1, and the "
            "classifier does not label those samples locked",
        "gen_pmp_addr_write_cg.cr_tor_lock.nl_tor_rlb1_written":
            "declaration: the sampler sets next_locked from the next entry's lock bit AND NOT mseccfg.RLB "
            "(gen_fcov_pkg.sv), so cp_next_cfg.next_locked_tor and cp_rlb.rlb1 are mutually exclusive by "
            "construction and no stimulus reaches this cross bin",
    }

    def report_count(self):
        return prog.plan(self.seed).k

    def fire_check(self):
        self.fire_program_verdict()
        self.fire_program_layout()
        self.fire_tp_pmp_013()
        self.fire_tp_pmp_014()
        self.fire_tp_pmp_015()
        self.fire_tp_pmp_016()
        self.fire_tp_pmp_017()
        self.fire_tp_pmp_018()
        self.fire_tp_pmp_019()
        self.fire_tp_pmp_020()
        self.fire_tp_pmp_021()
        self.fire_tp_pmp_112()

    def fire_program_verdict(self):
        code = int(self.h.b.evt_eot_code.value)
        floor = lib.program_min_retired(self.image, prog.plan(self.seed).min_retired)
        got = self.retired()
        plan = prog.plan(self.seed)
        n, bad = compare(plan, self.reports, bases_of(self), plan.item_indices("setup") + plan.item_indices("tail"))
        tail = plan.items["tail"]
        tail_ok = True
        if tail["drawn"]:
            mml = word(self.reports, tail["mml_idx"])
            rlb = word(self.reports, tail["rlb_idx"])
            tail_ok = mml is not None and mml & prog.MSECCFG_MML and rlb is not None and not rlb & prog.MSECCFG_RLB \
                and all(unchanged(plan, self.reports, i, pre) for i, _c, pre in tail["ignored"]) \
                and all(lane_byte(word(self.reports, i), ln) == b for i, _e, ln, b in tail["landed"])
        self.check("fire_program_verdict", code == lib.TOHOST_PASS and got >= floor and not bad and len(self.reports) == plan.k and tail_ok,
                   f"tohost code 0x{code:08x} (pass = {lib.TOHOST_PASS}); retired {got} (floor {floor}); reports {len(self.reports)} (k {plan.k}); "
                   + summary(n, bad, f"MML=1 tail drawn: {tail['drawn']}" + (f", {len(tail['ignored'])} locked writes ignored under MML=1, "
                                                                            f"{len(tail['landed'])} unlocked write landed, RLB stays 0: {tail_ok}" if tail["drawn"] else "")))

    def fire_program_layout(self):
        """The layout the expectations rely on, from the symbol table: pool and end of .text inside the program window, the
        pool after the text; the program's own reports of the two addresses must agree with the table."""
        plan = prog.plan(self.seed)
        bases = bases_of(self)
        setup = plan.items["setup"]
        n, bad = compare(plan, self.reports, bases, [setup["pool"], setup["text_end"]])
        lo, hi = MEMORY_MAP["boot_page"], MEMORY_MAP["boot_page"] + MEMORY_MAP["prog_size"]
        pool, text_end = bases["pool"], bases["text_end"]
        ok = not bad and lo < text_end < hi and lo < pool < hi and pool >= text_end and pool % 4 == 0
        self.check("fire_program_layout", ok, summary(n, bad, f"symbols: pool 0x{pool:08x} text_end 0x{text_end:08x} (window 0x{lo:08x}..0x{hi:08x})"))

    def fire_tp_pmp_013(self):
        plan = prog.plan(self.seed)
        meta = plan.items["TP-PMP-013"]
        n, bad = compare(plan, self.reports, bases_of(self), plan.item_indices("TP-PMP-013"))
        kept = total_locked = updated = 0
        mixes, some_forms = set(), set()
        for idx, cfg_n, form, mix, locked_lanes, pre in meta["writes"]:
            rb = word(self.reports, idx)
            mixes.add(mix)
            if mix == "some":
                some_forms.add(form)
            for ln in locked_lanes:
                total_locked += 1
                kept += lane_byte(rb, ln) == lane_byte(pre, ln)
            updated += sum(1 for ln in range(4) if ln not in locked_lanes and rb is not None and lane_byte(rb, ln) != lane_byte(pre, ln))
        ok = not bad and mixes == {"none", "some", "all"} and some_forms == {"csrrw", "csrrs", "csrrc"} and kept == total_locked and updated > 0
        self.check("fire_tp_pmp_013", ok, summary(n, bad, f"{len(meta['writes'])} pmpcfg writes, lock mixes {sorted(mixes)}, op classes on partially locked words "
                                                        f"{sorted(some_forms)}; locked bytes kept {kept}/{total_locked}, unlocked bytes updated {updated}"))

    def fire_tp_pmp_014(self):
        plan = prog.plan(self.seed)
        meta = plan.items["TP-PMP-014"]
        n, bad = compare(plan, self.reports, bases_of(self), plan.item_indices("TP-PMP-014"))
        lock_lane = lane_byte(word(self.reports, meta["lock_idx"]), meta["own"] % 4)
        modes = {a for _i, _e, _f, a, _p in meta["writes"]}
        entries = {e for _i, e, _f, _a, _p in meta["writes"]}
        forms = {f for _i, _e, f, _a, _p in meta["writes"]}
        ign = sum(1 for i, _e, _f, _a, pre in meta["writes"] if unchanged(plan, self.reports, i, pre))
        ok = not bad and locked(lock_lane) and modes == set(prog.A_MODES) and ign == len(meta["writes"]) and len(meta["writes"]) >= 4
        self.check("fire_tp_pmp_014", ok, summary(n, bad, f"own lock of entry {meta['own']} read back L=1: {locked(lock_lane)}; "
                                                        f"{len(meta['writes'])} pmpaddr writes to {len(entries)} locked entries (modes {sorted(prog.A_NAMES[a] for a in modes)}, "
                                                        f"ops {sorted(forms)}), {ign} read back unchanged"))

    def fire_tp_pmp_015(self):
        plan = prog.plan(self.seed)
        meta = plan.items["TP-PMP-015"]
        n, bad = compare(plan, self.reports, bases_of(self), plan.item_indices("TP-PMP-015"))
        i, t = meta["pair"]
        nb = lane_byte(word(self.reports, meta["lock_idx"]), t % 4)
        next_locked_tor = locked(nb) and mode(nb) == prog.A_TOR
        addr_ign = sum(1 for idx, _f, pre in meta["addr_writes"] if unchanged(plan, self.reports, idx, pre))
        forms = {f for _i, f, _p in meta["addr_writes"]}
        cidx, lane, pre_b = meta["cfg_i"]
        cfg_changed = lane_byte(word(self.reports, cidx), lane) not in (None, pre_b)
        ok = not bad and next_locked_tor and addr_ign == len(meta["addr_writes"]) and forms == {"csrrw", "csrrs", "csrrc"} and cfg_changed
        self.check("fire_tp_pmp_015", ok, summary(n, bad, f"entry {t} read back locked TOR: {bool(next_locked_tor)}; {addr_ign}/{len(meta['addr_writes'])} pmpaddr{i} writes "
                                                        f"({sorted(forms)}) read back unchanged; pmpcfg entry {i} changed: {cfg_changed}"))

    def fire_tp_pmp_016(self):
        plan = prog.plan(self.seed)
        meta = plan.items["TP-PMP-016"]
        n, bad = compare(plan, self.reports, bases_of(self), plan.item_indices("TP-PMP-016"))
        good = 0
        modes = set()
        for idx, _i, e, a, lane_e, cfg_idx, pre in meta["pairs"]:
            nb = lane_byte(word(self.reports, cfg_idx), lane_e)
            locked_other = locked(nb) and mode(nb) != prog.A_TOR
            modes.add(a)
            good += bool(locked_other and changed(self.reports, idx, pre))
        ok = not bad and meta["pairs"] and good == len(meta["pairs"])
        self.check("fire_tp_pmp_016", ok, summary(n, bad, f"{good}/{len(meta['pairs'])} pmpaddr(i) writes landed under a locked non-TOR entry i+1 "
                                                        f"(neighbour modes {sorted(prog.A_NAMES[a] for a in modes)})"))

    def fire_tp_pmp_017(self):
        plan = prog.plan(self.seed)
        meta = plan.items["TP-PMP-017"]
        n, bad = compare(plan, self.reports, bases_of(self), plan.item_indices("TP-PMP-017"))
        good = 0
        for idx, _i, _e, lane_e, cfg_idx, pre in meta["pairs"]:
            nb = lane_byte(word(self.reports, cfg_idx), lane_e)
            unlocked_tor = nb is not None and not locked(nb) and mode(nb) == prog.A_TOR
            good += bool(unlocked_tor and changed(self.reports, idx, pre))
        ok = not bad and meta["pairs"] and good == len(meta["pairs"])
        self.check("fire_tp_pmp_017", ok, summary(n, bad, f"{good}/{len(meta['pairs'])} pmpaddr(i) writes landed under an unlocked TOR entry i+1"))

    def fire_tp_pmp_018(self):
        plan = prog.plan(self.seed)
        meta = plan.items["TP-PMP-018"]
        n, bad = compare(plan, self.reports, bases_of(self), plan.item_indices("TP-PMP-018"))
        e = meta["entry"]
        first = sum(1 for idx, _f, pre in meta["first"] if changed(self.reports, idx, pre))
        lb = lane_byte(word(self.reports, meta["lock_idx"]), e % 4)
        second = sum(1 for idx, _f, pre in meta["second"] if unchanged(plan, self.reports, idx, pre))
        ok = not bad and e == prog.NUM_REGIONS - 1 and first == len(meta["first"]) and locked(lb) and second == len(meta["second"])
        self.check("fire_tp_pmp_018", ok, summary(n, bad, f"pmpaddr{e}: {first}/{len(meta['first'])} unlocked writes changed, lock read back L=1 "
                                                        f"({prog.A_NAMES[mode(lb)] if lb is not None else '-'}), {second}/{len(meta['second'])} locked writes unchanged"))

    def fire_tp_pmp_019(self):
        plan = prog.plan(self.seed)
        meta = plan.items["TP-PMP-019"]
        n, bad = compare(plan, self.reports, bases_of(self), plan.item_indices("TP-PMP-019"))
        e = meta["entry"]
        lb = lane_byte(word(self.reports, meta["lock_idx"]), e % 4)
        locked_off = locked(lb) and mode(lb) == prog.A_OFF
        ign = sum(1 for idx, _c, pre in meta["rewrites"] if unchanged(plan, self.reports, idx, pre))
        ms = word(self.reports, meta["mseccfg_idx"])
        probe = word(self.reports, meta["probe_idx"])
        ok = not bad and locked_off and ign == len(meta["rewrites"]) and ms is not None and not ms & prog.MSECCFG_RLB \
            and probe is not None and probe == (prog.POOL_PATTERN | meta["pool_word"])
        self.check("fire_tp_pmp_019", ok, summary(n, bad, f"entry {e} read back L=1 A=OFF: {bool(locked_off)}; {ign}/{len(meta['rewrites'])} follow-up writes unchanged; "
                                                        f"mseccfg after the RLB attempt 0x{ms if ms is not None else 0:x} (RLB bit clear: {ms is not None and not ms & prog.MSECCFG_RLB}); "
                                                        f"M-mode load of the entry's word returned the pool pattern: {probe == (prog.POOL_PATTERN | meta['pool_word'])}"))

    def fire_tp_pmp_020(self):
        plan = prog.plan(self.seed)
        meta = plan.items["TP-PMP-020"]
        n, bad = compare(plan, self.reports, bases_of(self), plan.item_indices("TP-PMP-020"))
        kinds0 = {ep["kind"] for ep in meta["episodes"] if ep["gap"] == 0}
        good = 0
        for ep in meta["episodes"]:
            lb = lane_byte(word(self.reports, ep["lock_idx"]), ep["lane"])
            sec = word(self.reports, ep["second_idx"])
            good += bool(locked(lb) and sec is not None and sec == ep["pre_second"] and (ep["kind"] != "rlb" or not sec & prog.MSECCFG_RLB))
        rows = set()
        for idx, e, _b in meta["lock_events"]:
            lb = lane_byte(word(self.reports, idx), e % 4)
            if locked(lb):
                _l, _a, x, w, r = prog.byte_fields(lb)
                rows.add((r, w, x))
        gaps = sorted({ep["gap"] for ep in meta["episodes"]})
        ok = not bad and kinds0 == set(prog.BB_KINDS) and good == len(meta["episodes"]) and set(prog.LOCK_ROWS) <= rows
        self.check("fire_tp_pmp_020", ok, summary(n, bad, f"{good}/{len(meta['episodes'])} episodes: lock read back L=1 and the second write unchanged; kinds at gap 0 "
                                                        f"{sorted(kinds0)}, gaps {gaps}; L=1 rows read back over {len(meta['lock_events'])} lock writes: {len(rows & set(prog.LOCK_ROWS))}/6"))

    def fire_tp_pmp_021(self):
        plan = prog.plan(self.seed)
        meta = plan.items["TP-PMP-021"]
        n, bad = compare(plan, self.reports, bases_of(self), plan.item_indices("TP-PMP-021"))
        rlb_words = [word(self.reports, i) for i in meta["rlb_idx"]]
        rlb_on = all(w is not None and w & prog.MSECCFG_RLB for w in rlb_words[:-1]) and rlb_words[-1] is not None and not rlb_words[-1] & prog.MSECCFG_RLB
        locks = sum(1 for idx, e, _p in meta["lock_writes"] if locked(lane_byte(word(self.reports, idx), e % 4)))
        rw_cfg = [x for x in meta["rewrites"] if x[2] == "cfg"]
        rw_addr = [x for x in meta["rewrites"] if x[2] == "addr"]
        rw_ok = sum(1 for idx, _e, _k, pre in meta["rewrites"] if changed(self.reports, idx, pre))
        tor_ok = sum(1 for idx, _j, pre in meta["tor_below"] if changed(self.reports, idx, pre))
        post_ok = sum(1 for idx, _c, pre in meta["post_clear"] if unchanged(plan, self.reports, idx, pre))
        ok = not bad and rlb_on and locks == len(meta["lock_writes"]) and rw_cfg and rw_addr and rw_ok == len(meta["rewrites"]) \
            and meta["tor_below"] and tor_ok == len(meta["tor_below"]) and post_ok == len(meta["post_clear"])
        self.check("fire_tp_pmp_021", ok, summary(n, bad, f"mseccfg read back RLB=1 through the phase then 0 after the clear: {rlb_on}; {locks} entries locked under RLB=1; "
                                                        f"{rw_ok}/{len(meta['rewrites'])} rewrites of locked state changed ({len(rw_cfg)} pmpcfg, {len(rw_addr)} pmpaddr); "
                                                        f"{tor_ok}/{len(meta['tor_below'])} pmpaddr writes below the locked TOR changed; {post_ok}/{len(meta['post_clear'])} repeated writes after the clear unchanged"))

    def fire_tp_pmp_112(self):
        plan = prog.plan(self.seed)
        meta = plan.items["TP-PMP-112"]
        n, bad = compare(plan, self.reports, bases_of(self), plan.item_indices("TP-PMP-112"))
        clr = word(self.reports, meta["clear_idx"])
        adj = word(self.reports, meta["adj_idx"])
        late_ok = sum(1 for idx, _c, pre, _g in meta["late"] if unchanged(plan, self.reports, idx, pre))
        att = word(self.reports, meta["rlb_attempt_idx"])
        ok = not bad and clr is not None and not clr & prog.MSECCFG_RLB and adj == meta["adj_pre"] and meta["gap"] == 0 \
            and late_ok == len(meta["late"]) and att is not None and not att & prog.MSECCFG_RLB
        self.check("fire_tp_pmp_112", ok, summary(n, bad, f"RLB clear by {meta['clear_form']} read back 0x{clr if clr is not None else 0:x}; adjacent {meta['variant']} write to locked "
                                                        f"entry {meta['entry']} at gap {meta['gap']} read back unchanged: {adj == meta['adj_pre']}; {late_ok}/{len(meta['late'])} later locked writes "
                                                        f"(gaps 1..3) unchanged; later RLB set attempt read back 0x{att if att is not None else 0:x}"))


@cocotb.test()
async def gen_test_pmp_lock(dut):
    await PmpLock(dut).run()
