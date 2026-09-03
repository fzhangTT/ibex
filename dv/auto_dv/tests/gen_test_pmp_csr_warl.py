"""gen_test_pmp_csr_warl: PMP CSR WARL rules of the opentitan configuration (PMPNumRegions 16, PMPGranularity 0).

Group gen_pmp_csr_warl (dv/auto_dv/docs/gen_test_plan.md Section 4.4). Items, all built, one fire-check
method each:
  TP-PMP-001 pmpcfg0..3 per-entry packing (fire_tp_pmp_001)      F-PMP-001
  TP-PMP-002 pmpaddr0..15 store all 32 bits at G = 0 (fire_tp_pmp_002)   F-PMP-002, F-PMP-014
  TP-PMP-003 pmpcfg bits 6:5 read as zero (fire_tp_pmp_003)      F-PMP-003 -> FOLDED into F-PMP-001
  TP-PMP-004 MML=0: RW=01 legalised to W=0, X/L/A kept (fire_tp_pmp_004)   F-PMP-004
  TP-PMP-005 MML=1: RW=01 stored verbatim (fire_tp_pmp_005)      F-PMP-005 -> FOLDED into F-PMP-001 (via F-PMP-004)
  TP-PMP-006 A = OFF/TOR/NA4/NAPOT selectable and behave as their mode (fire_tp_pmp_006)   F-PMP-006
  TP-PMP-007 csrrs/csrrc and immediate forms go through the WARL rules (fire_tp_pmp_007)   F-PMP-018
  TP-PMP-008 PMP and mseccfg CSR access from U-mode is illegal, no write (fire_tp_pmp_008)   F-PMP-016
Canonical feature IDs covered (gen_feature_list.md Section 3): F-PMP-001, F-PMP-002, F-PMP-004, F-PMP-006,
F-PMP-014, F-PMP-016, F-PMP-018. Items blocked: none. The items' "RVFI:" fire-check wording is realised
through the program report channel: every csrr read-back, every RMW rd value, every trap record (mcause,
mstatus.MPP, trapping instruction index, stored by the M-mode handler) and every probe result is a report
word the program stores to the EOT MMIO register, and the program's own pass verdict is the tohost code.
rvfi_trap = 0 on the M-mode writes is implied by the program reaching its end with no handler record from
M-mode (a trap from M ends the program with the fail code). Report-channel limit: a U-mode trap record
carries cause, MPP and index, not the CSR the trapping instruction named (RVFI export needed for that).

Program: dv/auto_dv/tests/gen_programs/gen_pmp_csr_warl_prog.py, one program per run seed; plan(seed) is
the single source of the report count and of every expectation. Expectations come from the WARL rules of
the privileged spec (machine.adoc PMP and mseccfg sections, smepmp.adoc) and of doc/03_reference/
cs_registers.rst as the generator's PmpModel states them; the RTL is a cross-check, never a source.
Layout-relative pmpaddr expectations (probe pool, U code area, end of .text) resolve from the image's
symbol table (prog.sym.json, global labels of the program); the program reports the same three addresses
and fire_program_layout checks them against that table. Every LRWX pattern the draw produces is programmed,
LRWX=1111 under MML=1 with RLB=0 included (smepmp.adoc: a locked shared read-only data region, no execute
privilege, so stored); a shim that legalises it differently shows up as an isa_csr comparator row, never
as a program change.
U-mode regions (plan C-2): only the U-executable code region is programmed. No U-RW data/stack region: the
U stubs use no stack and touch no data except the probe words whose per-mode verdict TP-PMP-006 checks (an
R/W region over the pool would decide every load/store probe); the handler's report store runs in M-mode.

Red fixtures (generator --red [--red-item TP-PMP-00X], one per item, expectations unchanged): items 001..007
deviate one CSR write of the item (A[0] of the entry for 001 and 006, one pmpaddr bit for 002, the X bit for
003/004/005, the first outcome-changing stored bit for 007) and restore the planned value after the reported
read-back; item 008 lets one attempted write land after the return to M (no-write clause) and restores it.
Each red fails exactly its item's fire_tp_pmp_<nnn>.

Flow verdict at HEAD: the program enters U-mode by mret and traps back to M, so the ISA comparator rows
isa_pc_next (mret records) and isa_prv (records executed in U) raise uvm_error until TB Infra's T-102 lands;
the flow verdict is FAIL while the cocotb marker is GEN_TEST_PASS, and the program is not shaped to avoid it.

Knobs: the items name program-side region markers (knob:instr_mix csr_heavy, knob:pmp_regime off / mml_on,
knob:priv_regime alternating / u_heavy) that describe this generated program; they are not scheduled here.
schedulable = the timing-only regime knobs (bus latencies, outstanding cap, scramble-key delay), which the
program tolerates. layers_required = False (bring-up opt-out, API doc Section 3; entry measured: false).

Always-on checkers relied on: the ISA comparator (isa_csr and the other C4.7 rows; the shim runs Spike with
PMPNumRegions 16, PMPGranularity 0 (4-byte grain, NA4 selectable) and Smepmp, PMP CSRs zeroed at reset),
rvfi_proto, and the bus protocol checkers. declare_bins() takes the template default (the plan's bins of the items the fire_tp methods name, for
the group, checked against the rendered manifest in finish(); the entry stays unwired until gen_fcov_pkg
lands). MODULE=dv.auto_dv.tests.gen_test_pmp_csr_warl, TOPLEVEL=gen_tb_top.
"""
import cocotb

from dv.auto_dv.gen_tb.gen_knobs import MEMORY_MAP
from dv.auto_dv.tests import gen_test_lib as lib
from dv.auto_dv.tests.gen_test_template import GenTest
from dv.auto_dv.tests.gen_programs import gen_pmp_csr_warl_prog as prog


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


class PmpCsrWarl(GenTest):
    name = "gen_test_pmp_csr_warl"
    schedulable = lib.TIMING_ONLY_KNOBS
    # Bring-up opt-out while no REGIME_SET consumer exists (API doc Section 3; entry measured: false).
    layers_required = False
    # items of the plan group this test does not check, with the reason (two-sided against the group by the structure check)
    not_built = {}

    def report_count(self):
        return prog.plan(self.seed).k

    def fire_check(self):
        self.fire_program_verdict()
        self.fire_program_layout()
        self.fire_tp_pmp_001()
        self.fire_tp_pmp_002()
        self.fire_tp_pmp_003()
        self.fire_tp_pmp_004()
        self.fire_tp_pmp_005()
        self.fire_tp_pmp_006()
        self.fire_tp_pmp_007()
        self.fire_tp_pmp_008()

    def fire_program_verdict(self):
        code = int(self.h.b.evt_eot_code.value)
        floor = lib.program_min_retired(self.image)
        got = self.retired()
        plan = prog.plan(self.seed)
        n, bad = compare(plan, self.reports, bases_of(self), plan.item_indices("setup"))
        self.check("fire_program_verdict", code == lib.TOHOST_PASS and got >= floor and not bad and len(self.reports) == plan.k,
                   f"tohost code 0x{code:08x} (pass = {lib.TOHOST_PASS}); retired {got} (floor {floor}); "
                   f"reports {len(self.reports)} (k {plan.k}); " + summary(n, bad, "entry 0 cleared at start"))

    def fire_program_layout(self):
        """The layout the model relies on, taken from the symbol table: bases inside the program window, U code
        area aligned to its NAPOT, the probe pool outside it (a pool inside the U-executable region would change
        every probe verdict); the program's own reports of the three addresses must agree with the table."""
        plan = prog.plan(self.seed)
        bases = bases_of(self)
        n, bad = compare(plan, self.reports, bases, plan.item_indices("bases"))
        lo, hi = MEMORY_MAP["boot_page"], MEMORY_MAP["boot_page"] + MEMORY_MAP["prog_size"]
        pool, ucode, text_end = (bases[k] for k in ("pool", "ucode", "text_end"))
        size = 1 << prog.UCODE_ALIGN_BITS
        ok = not bad and all(lo <= v < hi for v in (pool, ucode, text_end)) and ucode % size == 0 \
            and text_end >= ucode + size and pool >= text_end and pool % (1 << prog.POOL_ALIGN_BITS) == 0
        self.check("fire_program_layout", ok, summary(n, bad, f"symbols: pool 0x{pool:08x} ucode 0x{ucode:08x} text_end 0x{text_end:08x} "
                                                             f"(window 0x{lo:08x}..0x{hi:08x}, U code NAPOT {size} bytes)"))

    def fire_tp_pmp_001(self):
        plan = prog.plan(self.seed)
        meta = plan.items["TP-PMP-001"]
        n, bad = compare(plan, self.reports, bases_of(self), plan.item_indices("TP-PMP-001"))
        csrs, lanes = set(), set()
        for idx, cfg_n in meta["cfg_readbacks"]:
            if idx < len(self.reports):
                csrs.add(cfg_n)
                lanes.update(ln for ln in range(4) if (lane_byte(self.reports[idx], ln) >> 3) & 3)
        ok = not bad and csrs == set(range(prog.NUM_CFG_CSRS)) and lanes == set(range(4))
        self.check("fire_tp_pmp_001", ok, summary(n, bad, f"pmpcfg CSRs written {sorted(csrs)}; byte lanes with a non-zero A read back {sorted(lanes)}; "
                                                        f"{len(meta['cfg_readbacks'])} csrrw/csrr pairs"))

    def fire_tp_pmp_002(self):
        plan = prog.plan(self.seed)
        meta = plan.items["TP-PMP-002"]
        n, bad = compare(plan, self.reports, bases_of(self), plan.item_indices("TP-PMP-002"))
        hi = {e for idx, e, _c in meta["addr_readbacks"] if idx < len(self.reports) and self.reports[idx] & (3 << 30)}
        written = {e for _i, e, _c in meta["addr_readbacks"]}
        ok = not bad and hi == set(range(prog.NUM_REGIONS)) and written == set(range(prog.NUM_REGIONS))
        self.check("fire_tp_pmp_002", ok, summary(n, bad, f"entries written {len(written)}/{prog.NUM_REGIONS}; entries with bit 31 or 30 read back {len(hi)}/{prog.NUM_REGIONS}; "
                                                        f"{len(meta['addr_readbacks'])} pmpaddr writes, modes randomised {len(meta['mode_readbacks'])} times"))

    def fire_tp_pmp_003(self):
        plan = prog.plan(self.seed)
        meta = plan.items["TP-PMP-003"]
        n, bad = compare(plan, self.reports, bases_of(self), plan.item_indices("TP-PMP-003"))
        res_zero = all(idx < len(self.reports) and all(lane_byte(self.reports[idx], ln) & 0x60 == 0 for ln in range(4))
                       for idx, _n, _lanes, _mml in meta["res_writes"])
        mml_states = {mml for _i, _n, _l, mml in meta["res_writes"]}
        ok = not bad and res_zero and mml_states == {0, 1}
        self.check("fire_tp_pmp_003", ok, summary(n, bad, f"{len(meta['res_writes'])} writes with bits 6:5 set (MML states {sorted(mml_states)}), "
                                                        f"bits 6:5 read back zero in every lane: {res_zero}"))

    def fire_tp_pmp_004(self):
        plan = prog.plan(self.seed)
        meta = plan.items["TP-PMP-004"]
        n, bad = compare(plan, self.reports, bases_of(self), plan.item_indices("TP-PMP-004"))
        rows = meta["rw01_bytes"] + meta.get("lock_bytes", [])
        kept = 0
        for idx, _n, ln, b in rows:
            if idx < len(self.reports):
                got = lane_byte(self.reports[idx], ln)
                l, a, x, _w, _r = prog.byte_fields(b)
                if prog.byte_fields(got) == (l, a, x, 0, 0):
                    kept += 1
        locked_rows = len(meta.get("lock_bytes", []))
        ok = not bad and rows and kept == len(rows)
        self.check("fire_tp_pmp_004", ok, summary(n, bad, f"{len(rows)} RW=01 bytes written under MML=0 ({locked_rows} with L=1), "
                                                        f"{kept} read back W=0 with X/L/A kept"))

    def fire_tp_pmp_005(self):
        plan = prog.plan(self.seed)
        meta = plan.items["TP-PMP-005"]
        n, bad = compare(plan, self.reports, bases_of(self), plan.item_indices("TP-PMP-005"))
        mi = meta["mseccfg_idx"]
        mml_seen = mi < len(self.reports) and bool(self.reports[mi] & prog.MSECCFG_MML)
        stored = 0
        for idx, _n, ln, b in meta["rw01_bytes"]:
            if idx < len(self.reports):
                got = lane_byte(self.reports[idx], ln)
                l, a, x, _w, _r = prog.byte_fields(b)
                if prog.byte_fields(got) == (l, a, x, 1, 0):
                    stored += 1
        ok = not bad and mml_seen and meta["rw01_bytes"] and stored == len(meta["rw01_bytes"])
        self.check("fire_tp_pmp_005", ok, summary(n, bad, f"mseccfg read back MML=1: {mml_seen} (RLB {plan.rlb}); {len(meta['rw01_bytes'])} RW=01 bytes written, "
                                                        f"{stored} read back with W=1 stored"))

    def fire_tp_pmp_006(self):
        plan = prog.plan(self.seed)
        meta = plan.items["TP-PMP-006"]
        n, bad = compare(plan, self.reports, bases_of(self), plan.item_indices("TP-PMP-006"))
        per_a = {a: set() for a in prog.A_NAMES}
        for idx, e, a in meta["a_readbacks"]:
            if idx < len(self.reports) and (lane_byte(self.reports[idx], e % 4) >> 3) & 3 == a:
                per_a[a].add(e)
        denied = sum(2 - sum(ep["allowed"]) for ep in meta["episodes"])
        allowed = sum(sum(ep["allowed"]) for ep in meta["episodes"])
        types = {ep["ptype"] for ep in meta["episodes"]}
        ok = not bad and all(len(s) >= 4 for s in per_a.values()) and denied > 0 and allowed > 0
        self.check("fire_tp_pmp_006", ok, summary(n, bad, "entries reading back each A: " + " ".join(f"{prog.A_NAMES[a]}={len(s)}" for a, s in per_a.items())
                                                        + f"; {len(meta['episodes'])} U probe episodes ({sorted(types)}), {allowed} probes allowed, {denied} denied with the modelled cause"))

    def fire_tp_pmp_007(self):
        plan = prog.plan(self.seed)
        meta = plan.items["TP-PMP-007"]
        n, bad = compare(plan, self.reports, bases_of(self), plan.item_indices("TP-PMP-007"))
        combos = {(form, cls) for _o, _r, form, cls, _p in meta["ops"]}
        want = {(f, c) for f in prog.W_OP_FORM_RMW for c in ("pmpcfg", "pmpaddr", "mseccfg")}
        phases = {p for _o, _r, _f, _c, p in meta["ops"]}
        ok = not bad and want <= combos
        self.check("fire_tp_pmp_007", ok, summary(n, bad, f"{len(meta['ops'])} RMW ops with rd and read-back, form x class combos {len(combos & want)}/{len(want)}, "
                                                        f"phases {sorted(phases)}"))

    def fire_tp_pmp_008(self):
        plan = prog.plan(self.seed)
        meta = plan.items["TP-PMP-008"]
        n, bad = compare(plan, self.reports, bases_of(self), plan.item_indices("TP-PMP-008"))
        recs = [self.reports[i] for i in meta["records"] if i < len(self.reports)]
        illegal_from_u = sum(1 for r in recs if (r >> 16) == prog.CAUSE_ILLEGAL and ((r >> 8) & 3) == 0)
        classes = {(cls, w) for _f, cls, w in meta["attempts"]}
        want = {(c, w) for c in ("pmpcfg", "pmpaddr", "mseccfg", "mseccfgh") for w in (True, False)}
        ok = not bad and illegal_from_u == len(meta["records"]) and len(recs) == len(meta["records"]) and want <= classes
        self.check("fire_tp_pmp_008", ok, summary(n, bad, f"{illegal_from_u}/{len(meta['records'])} U attempts trapped illegal (cause 2) with MPP=U; "
                                                        f"read and write attempts on all 4 classes: {want <= classes}; {len(meta['readbacks'])} CSRs read back unchanged"))


@cocotb.test()
async def gen_test_pmp_csr_warl(dut):
    await PmpCsrWarl(dut).run()
