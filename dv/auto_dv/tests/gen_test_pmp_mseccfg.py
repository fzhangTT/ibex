"""gen_test_pmp_mseccfg: the mseccfg register of the opentitan configuration (Smepmp: MML, MMWP, RLB; PMPNumRegions 16).

Group gen_pmp_mseccfg (dv/auto_dv/docs/gen_test_plan.md, AREA PMP). Items built, one fire-check method each:
  TP-PMP-011 mseccfg exposes MML/MMWP/RLB, bits 31:3 read zero (fire_tp_pmp_011)        F-PMP-021
  TP-PMP-012 mseccfgh reads zero after any write, mseccfg unchanged (fire_tp_pmp_012)    F-PMP-022
  TP-PMP-022 MML sticky (fire_tp_pmp_022)                                                F-PMP-023
  TP-PMP-023 MMWP sticky (fire_tp_pmp_023)                                               F-PMP-024
  TP-PMP-024 RLB free while no entry is locked (fire_tp_pmp_024)                         F-PMP-025
  TP-PMP-025 RLB writes ignored with RLB=0 and a locked entry (fire_tp_pmp_025)          F-PMP-026
  TP-PMP-026 clearing RLB with locks present is permanent (fire_tp_pmp_026)              F-PMP-027
  TP-PMP-027 MML=1 RLB=0: M-exec locked rows dropped per entry (fire_tp_pmp_027)         F-PMP-029
  TP-PMP-028 the suppression also with A=OFF (fire_tp_pmp_028)                           F-PMP-030
  TP-PMP-029 locked non-exec rows accepted (fire_tp_pmp_029)                             F-PMP-031 -> FOLDED into F-PMP-029
  TP-PMP-030 MML=1 RLB=1 lifts the suppression (fire_tp_pmp_030)                         F-PMP-032 -> FOLDED into F-PMP-029
  TP-PMP-031 setting MML keeps the stored entries, changes their interpretation (fire_tp_pmp_031)   F-PMP-033
Canonical feature IDs covered (gen_feature_list.md Section 3): F-PMP-021, F-PMP-022, F-PMP-023, F-PMP-024, F-PMP-025,
F-PMP-026, F-PMP-027, F-PMP-029, F-PMP-030, F-PMP-033. Items not built: TP-PMP-108 (below).

TP-PMP-108 not built: the plan's walk restarts from a wrapper reset to revisit the low states and asserts all 8 states
per seed; the bridge has no reset command, so one power-on walks one monotone path (MML and MMWP never clear, RLB never
returns to 1 once a lock exists with RLB=0): s000->s101, s000->s111, s010->s111 need MML set while RLB goes 0->1, but an
M-mode program needs a locked M-exec rule before MML=1 and that lock pins RLB at 0, and s000->s100, s000->s110, s001->s100,
s001->s110, s010->s110, s011->s110 enter MML=1 with RLB=0, which leaves no (1,x,1) state for TP-PMP-030 in the same
power-on. The item stays not_built until a mid-run reset command exists (TB ask filed by the Test Writer); its CG-PMP-003
cr_state_trans / cp_pre / cp_post bins are not declared. The program keeps the per-seed walk as stimulus (path drawn by the
seed: mmwp_first, mml_first_rlb or mml_first_late; every read-back is checked in lock-step by gen_isa_compare), not credited
to the item.
Other stated deviations: TP-PMP-023's MML=0 precondition is a safety precondition (MMWP must not fault the program);
in the mml_first paths MMWP is set under MML=1 over the complete M-mode table (code, MMIO page and .data covered by
L=1 rules), so the walk reaches s10x. TP-PMP-026's set/lock happen under MML=0 and its clear/attempt under MML=1
(the clear must follow TP-PMP-030). TP-PMP-027's offending rows use csrrw and csrrs: csrrc cannot produce L=1 on an
unlocked (L=0) entry, so a csrrc write never carries an offending byte. TP-PMP-011's "last iterations set MML and
MMWP" are the 022/023 set writes (their own items).

The items' "RVFI:" fire-check wording is realised through the program report channel: every csrr read-back, every
handler record (mcause, MPP, index) and every probe value is a report word the program stores to the EOT MMIO
register; rvfi_trap = 0 on the M-mode CSR writes is implied by the program reaching its end (an unexpected M-mode
trap ends it with the fail code); the denied probes' mcause 5 records with the handler's marker are the trap
observations. Every read-back is compared with the generator's PmpModel prediction (gen_chk_csr_readback and
gen_chk_pmp are unbuilt; gen_isa_compare is the always-on cross-check).

Program: dv/auto_dv/tests/gen_programs/gen_pmp_mseccfg_prog.py, one program per run seed; plan(seed) is the single
source of the report count and every expectation. Layout-relative pmpaddr expectations (U code area, pool words,
.data base) resolve from the image's symbol table, and fire_program_layout checks the program's own base reports
against it.

Red fixtures (generator --red [--red-item TP-PMP-0nn], one per item, expectations unchanged; the pinned red of
the entry is TP-PMP-011, check name fire_tp_pmp_011): see the generator docstring; each red fails exactly its
item's fire_tp_pmp_<nnn>.

Knobs: the items name program-side markers (knob:instr_mix csr_heavy, knob:pmp_regime mml_on) that describe this
generated program; they are not scheduled. schedulable = the timing-only regime knobs. Always-on checkers relied on:
the ISA comparator rows (the shim runs Spike with Smepmp, PMPNumRegions 16, PMPGranularity 0), rvfi_proto, the bus
protocol checkers. declare_bins() takes the template default (the plan's bins of the items the fire_tp methods
name minus bins_not_hit, checked against the rendered manifest in finish()).
MODULE=dv.auto_dv.tests.gen_test_pmp_mseccfg, TOPLEVEL=gen_tb_top.
"""
import cocotb

from dv.auto_dv.gen_tb.gen_knobs import MEMORY_MAP
from dv.auto_dv.tests import gen_test_lib as lib
from dv.auto_dv.tests.gen_test_template import GenTest
from dv.auto_dv.tests.gen_programs import gen_pmp_mseccfg_prog as prog
from dv.auto_dv.tests.gen_programs import gen_pmp_csr_warl_prog as warl


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


def lane_byte(word, lane):
    return (word >> (8 * lane)) & 0xFF


def word(reports, idx):
    return reports[idx] if idx < len(reports) else None


def bit(reports, idx, mask):
    w = word(reports, idx)
    return None if w is None else int(bool(w & mask))


class PmpMseccfg(GenTest):
    name = "gen_test_pmp_mseccfg"
    schedulable = lib.TIMING_ONLY_KNOBS
    # items of the plan group this test does not check, with the reason (two-sided against the group by the structure check)
    not_built = {
        "TP-PMP-108": "the plan's state-machine walk needs a wrapper reset to revisit the low states; the bridge has no reset command (TB ask filed)",
    }
    # every declared bin is hit by every seed; the TP-PMP-108 transition bins are not declared (the item is not built)
    bins_not_hit = {}

    def report_count(self):
        return prog.plan(self.seed).k

    def fire_check(self):
        self.fire_program_verdict()
        self.fire_program_layout()
        self.fire_tp_pmp_011()
        self.fire_tp_pmp_012()
        self.fire_tp_pmp_022()
        self.fire_tp_pmp_023()
        self.fire_tp_pmp_024()
        self.fire_tp_pmp_025()
        self.fire_tp_pmp_026()
        self.fire_tp_pmp_027()
        self.fire_tp_pmp_028()
        self.fire_tp_pmp_029()
        self.fire_tp_pmp_030()
        self.fire_tp_pmp_031()

    def fire_program_verdict(self):
        code = int(self.h.b.evt_eot_code.value)
        floor = lib.program_min_retired(self.image)
        got = self.retired()
        plan = prog.plan(self.seed)
        n, bad = compare(plan, self.reports, bases_of(self), plan.item_indices("setup"))
        self.check("fire_program_verdict", code == lib.TOHOST_PASS and got >= floor and not bad and len(self.reports) == plan.k,
                   f"tohost code 0x{code:08x} (pass = {lib.TOHOST_PASS}); retired {got} (floor {floor}); "
                   f"reports {len(self.reports)} (k {plan.k}); path {plan.path}; " + summary(n, bad, "entry 0 cleared, survival table L=0 part"))

    def fire_program_layout(self):
        """The layout the model relies on, from the symbol table: U code area NAPOT-aligned inside .text, the pool inside
        the 1 KiB .data NAPOT, everything inside the program window; the program's own base reports agree."""
        plan = prog.plan(self.seed)
        bases = bases_of(self)
        n, bad = compare(plan, self.reports, bases, plan.item_indices("bases"))
        lo, hi = MEMORY_MAP["boot_page"], MEMORY_MAP["boot_page"] + MEMORY_MAP["prog_size"]
        pool, ucode, text_end, data = (bases[k] for k in ("pool", "ucode", "text_end", "data"))
        usize, dsize = 1 << warl.UCODE_ALIGN_BITS, 1 << prog.DATA_ALIGN_BITS
        ok = not bad and all(lo <= v < hi for v in (pool, ucode, text_end, data)) and ucode % usize == 0 \
            and text_end >= ucode + usize and data >= text_end and data % dsize == 0 and data <= pool and pool + 8 <= data + dsize
        self.check("fire_program_layout", ok, summary(n, bad, f"symbols: ucode 0x{ucode:08x} text_end 0x{text_end:08x} data 0x{data:08x} "
                                                             f"pool 0x{pool:08x} (window 0x{lo:08x}..0x{hi:08x}, U code NAPOT {usize}, .data NAPOT {dsize})"))

    def fire_tp_pmp_011(self):
        plan = prog.plan(self.seed)
        meta = plan.items["TP-PMP-011"]
        n, bad = compare(plan, self.reports, bases_of(self), plan.item_indices("TP-PMP-011"))
        hi_zero = all(word(self.reports, i) is not None and word(self.reports, i) & prog.HI_MASK == 0 for i, *_r in meta["writes"])
        classes = {c for _i, _f, c, _p, _w in meta["writes"]}
        pre = {p for _i, _f, _c, p, _w in meta["writes"]}
        wr = {w for *_r, w in meta["writes"]}
        forms = {f for _i, f, _c, _p, _w in meta["writes"]}
        ok = not bad and hi_zero and classes == {"nonzero", "zero"} and pre == {0, 1} and wr == {0, 1} and "csrrw" in forms
        self.check("fire_tp_pmp_011", ok, summary(n, bad, f"{len(meta['writes'])} mseccfg writes (hi classes {sorted(classes)}, forms {sorted(forms)}, "
                                                        f"pre RLB {sorted(pre)}, written RLB {sorted(wr)}); bits 31:3 read zero in every read-back: {hi_zero}"))

    def fire_tp_pmp_012(self):
        plan = prog.plan(self.seed)
        meta = plan.items["TP-PMP-012"]
        n, bad = compare(plan, self.reports, bases_of(self), plan.item_indices("TP-PMP-012"))
        forms = {f for _a, _b, f in meta["writes"]}
        zero = all(word(self.reports, a) == 0 for a, _b, _f in meta["writes"])
        ok = not bad and forms == set(prog.ALL_FORMS) and zero
        self.check("fire_tp_pmp_012", ok, summary(n, bad, f"{len(meta['writes'])} mseccfgh writes over forms {sorted(forms)}; mseccfgh read zero after each: {zero}; "
                                                        f"mseccfg read back unchanged after each (compared)"))

    def fire_sticky(self, item, mask, what):
        plan = prog.plan(self.seed)
        meta = plan.items[item]
        n, bad = compare(plan, self.reports, bases_of(self), plan.item_indices(item))
        held = [bit(self.reports, i, mask) for i, _f in meta["attempts"]]
        forms = {f for _i, f in meta["attempts"]}
        set_ok = bit(self.reports, meta["set_idx"], mask) == 1
        ok = not bad and set_ok and held and all(h == 1 for h in held) and {"csrrw", "csrrc"} <= forms
        self.check(what, ok, summary(n, bad, f"set read back {what[-3:]}=1: {set_ok}; {len(held)} clear attempts (forms {sorted(forms)}) all read back 1: "
                                             f"{all(h == 1 for h in held)}"))

    def fire_tp_pmp_022(self):
        self.fire_sticky("TP-PMP-022", warl.MSECCFG_MML, "fire_tp_pmp_022")

    def fire_tp_pmp_023(self):
        self.fire_sticky("TP-PMP-023", warl.MSECCFG_MMWP, "fire_tp_pmp_023")

    def fire_tp_pmp_024(self):
        plan = prog.plan(self.seed)
        meta = plan.items["TP-PMP-024"]
        n, bad = compare(plan, self.reports, bases_of(self), plan.item_indices("TP-PMP-024"))
        follows = all(bit(self.reports, i, warl.MSECCFG_RLB) == w for i, _p, w, _f in meta["writes"])
        combos = {(p, w) for _i, p, w, _f in meta["writes"]}
        ok = not bad and follows and combos == {(0, 0), (0, 1), (1, 0), (1, 1)}
        self.check("fire_tp_pmp_024", ok, summary(n, bad, f"{len(meta['writes'])} RLB writes with no lock, (pre, written) combos {sorted(combos)}, "
                                                        f"read-back bit 2 follows the written value: {follows}"))

    def fire_tp_pmp_025(self):
        plan = prog.plan(self.seed)
        meta = plan.items["TP-PMP-025"]
        n, bad = compare(plan, self.reports, bases_of(self), plan.item_indices("TP-PMP-025"))
        stays = all(bit(self.reports, i, warl.MSECCFG_RLB) == 0 for i, _f, _t in meta["attempts"])
        set_forms = {f for _i, f, t in meta["attempts"] if t}
        clears = sum(1 for _i, _f, t in meta["attempts"] if not t)
        modes = {a for _e, a in meta["locks"]}
        ok = not bad and stays and set_forms == {"csrrw", "csrrs"} and clears >= 1 and len(meta["locks"]) >= 1 and modes - {warl.A_OFF}
        self.check("fire_tp_pmp_025", ok, summary(n, bad, f"{len(meta['attempts'])} writes with {len(meta['locks'])} locked entries (A modes {sorted(modes)}), "
                                                        f"bit 2 = 1 forms {sorted(set_forms)}, {clears} bit 2 = 0 writes; RLB read back 0 after each: {stays}"))

    def fire_tp_pmp_026(self):
        plan = prog.plan(self.seed)
        meta = plan.items["TP-PMP-026"]
        n, bad = compare(plan, self.reports, bases_of(self), plan.item_indices("TP-PMP-026"))
        set_rb, clear_rb, att_rb = (bit(self.reports, meta[k], warl.MSECCFG_RLB) for k in ("set_idx", "clear_idx", "attempt_idx"))
        ok = not bad and set_rb == 1 and clear_rb == 0 and att_rb == 0 and len(meta["locks"]) >= 1 and len(meta["locks_at_attempt"]) >= 1
        self.check("fire_tp_pmp_026", ok, summary(n, bad, f"RLB set read back {set_rb} (no lock), {len(meta['locks'])} entries locked, clear read back {clear_rb}, "
                                                        f"set attempt read back {att_rb} with {len(meta['locks_at_attempt'])} locked entries"))

    def fire_tp_pmp_027(self):
        plan = prog.plan(self.seed)
        meta = plan.items["TP-PMP-027"]
        n, bad = compare(plan, self.reports, bases_of(self), plan.item_indices("TP-PMP-027"))
        suppressed = changed = 0
        for w in meta["writes"]:
            got = word(self.reports, w["idx"])
            if got is None:
                continue
            if all(lane_byte(got, ln) == lane_byte(w["pre"], ln) != lane_byte(w["value"], ln) for ln in w["offend"]):
                suppressed += 1
            if any(lane_byte(got, ln) == lane_byte(w["value"], ln) != lane_byte(w["pre"], ln) for ln in w["ordinary"]):
                changed += 1
        words = {w["n"] for w in meta["writes"]}
        forms = {w["form"] for w in meta["writes"]}
        modes = {m for w in meta["writes"] for m in w["modes"]}
        rows = {tuple(r) for w in meta["writes"] for r in w["rows"]}
        ok = not bad and meta["writes"] and suppressed == changed == len(meta["writes"]) and words == set(range(warl.NUM_CFG_CSRS)) \
            and forms == {"csrrw", "csrrs"} and modes == set(prog.SUPPRESS_MODES) and rows == set(prog.EXEC_ROWS)
        self.check("fire_tp_pmp_027", ok, summary(n, bad, f"{len(meta['writes'])} word writes under MML=1 RLB=0 (words {sorted(words)}, forms {sorted(forms)}, "
                                                        f"A modes {sorted(modes)}, rows {len(rows)}/4): offending bytes unchanged in {suppressed}, "
                                                        f"an ordinary byte of the same word changed in {changed}"))

    def fire_tp_pmp_028(self):
        plan = prog.plan(self.seed)
        meta = plan.items["TP-PMP-028"]
        n, bad = compare(plan, self.reports, bases_of(self), plan.item_indices("TP-PMP-028"))
        unchanged = sum(1 for i, _n, ln, pre, b in meta["writes"]
                        if word(self.reports, i) is not None and lane_byte(word(self.reports, i), ln) == lane_byte(pre, ln) != b)
        ok = not bad and meta["writes"] and unchanged == len(meta["writes"])
        self.check("fire_tp_pmp_028", ok, summary(n, bad, f"{len(meta['writes'])} L=1 X=1 rows written with A=OFF under MML=1 RLB=0, {unchanged} read back unchanged"))

    def fire_tp_pmp_029(self):
        plan = prog.plan(self.seed)
        meta = plan.items["TP-PMP-029"]
        n, bad = compare(plan, self.reports, bases_of(self), plan.item_indices("TP-PMP-029"))
        stored = sum(1 for i, _n, ln, b in meta["writes"] if word(self.reports, i) is not None and lane_byte(word(self.reports, i), ln) == b)
        rows = {warl.byte_fields(b)[2:][::-1] for _i, _n, _ln, b in meta["writes"]}
        ok = not bad and rows == set(prog.NONEXEC_ROWS) and stored == len(meta["writes"])
        self.check("fire_tp_pmp_029", ok, summary(n, bad, f"{len(meta['writes'])} locked non-exec rows written under MML=1 RLB=0 ({len(rows)}/4 rows), {stored} read back as written"))

    def fire_tp_pmp_030(self):
        plan = prog.plan(self.seed)
        meta = plan.items["TP-PMP-030"]
        n, bad = compare(plan, self.reports, bases_of(self), plan.item_indices("TP-PMP-030"))
        before, after = word(self.reports, meta["msec_before"]), word(self.reports, meta["msec_after"])
        state_ok = before is not None and after is not None and before & prog.MSEC_MASK & (warl.MSECCFG_MML | warl.MSECCFG_RLB) == (warl.MSECCFG_MML | warl.MSECCFG_RLB) \
            and after & (warl.MSECCFG_MML | warl.MSECCFG_RLB) == warl.MSECCFG_MML
        stored = sum(1 for i, e, b in meta["rows"] if word(self.reports, i) is not None and lane_byte(word(self.reports, i), e % 4) == b)
        rows = {warl.byte_fields(b)[2:][::-1] for _i, _e, b in meta["rows"]}
        ri, re_, rpre = meta["repeat"]
        rep_ok = word(self.reports, ri) is not None and lane_byte(word(self.reports, ri), re_ % 4) == rpre
        ok = not bad and state_ok and stored == len(meta["rows"]) and rows == set(prog.EXEC_ROWS) and rep_ok
        self.check("fire_tp_pmp_030", ok, summary(n, bad, f"mseccfg MML=1 RLB=1 then RLB=0: {state_ok}; {stored}/{len(meta['rows'])} exec rows stored under RLB=1 "
                                                        f"({len(rows)}/4 rows); the repeat under RLB=0 suppressed: {rep_ok}"))

    def fire_tp_pmp_031(self):
        plan = prog.plan(self.seed)
        meta = plan.items["TP-PMP-031"]
        n, bad = compare(plan, self.reports, bases_of(self), plan.item_indices("TP-PMP-031"))
        pairs = list(zip(meta["csr_before"], meta["csr_after"]))
        identical = all(word(self.reports, a) is not None and word(self.reports, a) == word(self.reports, b) for a, b in pairs)
        mb, ma = meta["m_before"], meta["m_after"]
        m_ok = word(self.reports, mb[0]) == prog.NOTRAP_MARK and word(self.reports, ma[0]) == prog.CAUSE_LOAD_M_RECORD \
            and word(self.reports, ma[1]) == prog.LOAD_SENT and word(self.reports, mb[1]) not in (None, prog.LOAD_SENT)
        ub, ua = meta["u_before"], meta["u_after"]
        u_ok = word(self.reports, ua[0][0]) == warl.record(warl.CAUSE_LOAD, 0) and word(self.reports, ua[1]) == prog.LOAD_SENT \
            and len(ub[0]) == 1 and word(self.reports, ub[1]) not in (None, prog.LOAD_SENT)
        ok = not bad and len(pairs) == warl.NUM_CFG_CSRS + warl.NUM_REGIONS and identical and m_ok and u_ok and len(meta["mixed"]) >= 4
        self.check("fire_tp_pmp_031", ok, summary(n, bad, f"{len(pairs)} pmpcfg/pmpaddr read back identical before and after the MML write: {identical}; "
                                                        f"M-mode load of the L=0 RWX=111 word allowed then denied (mcause 5, MPP=M): {m_ok}; "
                                                        f"U-mode load of the L=1 RW word allowed then denied (mcause 5): {u_ok}; {len(meta['mixed'])} mixed rows"))




@cocotb.test()
async def gen_test_pmp_mseccfg(dut):
    await PmpMseccfg(dut).run()
