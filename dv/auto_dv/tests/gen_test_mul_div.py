"""gen_test_mul_div: plan group gen_mul_div (dv/auto_dv/docs/gen_test_plan.md AREA MUL, plan version 2 of 2026-09-03
12:43 UTC at the committed tree the Test Writer named).

Items built and their canonical features (gen_feature_list.md Section 3): TP-MUL-013 divu (F-MUL-013), TP-MUL-014 rem
(F-MUL-014), TP-MUL-015 remu (F-MUL-015), TP-MUL-016 division by zero returns all ones (F-MUL-016), TP-MUL-017 remainder
by zero returns the dividend (F-MUL-017), TP-MUL-018 signed overflow INT_MIN / -1 (F-MUL-018), TP-MUL-019 div/rem sign
combinations (F-MUL-019 is FOLDED into F-MUL-012, bin CG-MUL-003.cr_op_sign.auto), TP-MUL-020 divu/remu with MSB-set
operands (F-MUL-020), TP-MUL-021 divide corner values (F-MUL-021), TP-MUL-026 M-extension decode forms with rd = x0
(F-MUL-026; value clause).
Items NOT built (not_built below): TP-MUL-012 div and its 37-cycle latency (F-MUL-012; the latency clause is the item's
subject) and TP-MUL-022 data_ind_timing = 1 forces the full latency (F-MUL-022; a cycle fact): both need the RVFI cycle /
bus records (the record export is not part of this batch; the event export is not built).
Clauses of built items NOT asserted here, with the missing channel named: the retire-delta clauses (TP-MUL-016/017 delta 2
fast path, TP-MUL-018 delta 37, TP-MUL-026 rd = x0 div delta 37: RVFI cycle / bus records) and the per-record RVFI field
clauses (rvfi_rs2_rdata = 0, rvfi_rd_wdata, rvfi_trap = 0: the RVFI record export, plan Section 6 item 5). Until those land
the clauses rest on the always-on checkers whose uvm_error the flow collects: the ISA comparator rows (isa_insn, isa_rd,
isa_trap, isa_pc) and rvfi_proto; the program taking no trap and reaching tohost 1 is fire_program_verdict's.
Program: the per-seed generator dv/auto_dv/tests/gen_programs/gen_mul_div_prog.py (testlist `program: {generator: ...,
seed: run}`) draws the ops, operands, registers, order and the ALU fillers between units from the run seed, computes every
expected report word from the RV32M specification (m-st-ext.adoc: truncating division, the divide-by-zero and
signed-overflow table) and stores the RAW observations to GEN_MM_EOT_ADDR: rd after every op, x0 read back after an rd = x0
form. Red fixtures: `--red [--red-item <item>]` emits one op of that item with another funct3 of its family or one operand
bit flipped while the expectation keeps the true program, so exactly that item's fire-check fails; without --red-item the
seed draws the item.
Fire-checks, one per item over the report words the plan attributes to it, plus the per-seed floor the item's Fire-check
says "every ..." about and the item's intent checks on the REPORTED values: fire_tp_mul_013 / 015 (every CG-MUL-003
dividend and divisor class for divu / remu), fire_tp_mul_014 (every sign pair; dividend == divisor * quotient + remainder
mod 2^32 over the reported div/rem pairs), fire_tp_mul_016 (every dividend class by zero; explicit reported word ==
0xFFFFFFFF, sub-checks _div signed and _divu unsigned), fire_tp_mul_017 (reported word == dividend; sub-checks _rem and
_remu), fire_tp_mul_018 (explicit div(INT_MIN, -1) == INT_MIN and rem == 0 signed, divu(INT_MIN, all ones) == 0 and remu ==
INT_MIN unsigned; sub-checks _signed and _unsigned), fire_tp_mul_019 (the four pinned quadrant pairs and every sign pair for
div and rem; quotient sign == xor of the operand signs and remainder sign == dividend sign for non-zero reported results),
fire_tp_mul_020 (the four listed rows for divu and remu; INT_MAX, 0, INT_MIN and 1 among the reported results),
fire_tp_mul_021 (every corner divisor class and the zero dividend for each of the four ops), fire_tp_mul_026 (all eight
funct3 with rd = x0 and rd != x0; x0 read back 0 after every rd = x0 form). An rd = x0 draw outside TP-MUL-026 (W4, 1 in
16 of the extras) is reported as the x0 read-back and counted apart from the observations (the detail names the count).
fire_program_verdict (not a plan item, so it declares no bins) asserts the program's own verdict: tohost code ==
lib.TOHOST_PASS, retirements at the end-of-test store >= the program's gen_min_retired floor, report count == the plan's k.
Knobs (the items' Knobs lines): knob:imem_rvalid_delay, knob:imem_gnt_delay; schedulable = lib.TIMING_ONLY_KNOBS; nothing
is pinned.
declare_bins() is not overridden: the template declares the plan bins of the ten items the fire_tp_mul_* methods name (the
manifest is rendered from this module). MODULE=dv.auto_dv.tests.gen_test_mul_div.
"""
import cocotb

from dv.auto_dv.tests import gen_test_lib as lib
from dv.auto_dv.tests.gen_programs import gen_mul_div_prog as prog
from dv.auto_dv.tests.gen_test_template import GenTest


def _plan(test):
    """The seed's program plan, built once per test instance: the generator is the single origin of the program's
    intent and of the expected report words."""
    if getattr(test, "_mul_div_plan", None) is None:
        test._mul_div_plan = prog.plan(test.seed)
    return test._mul_div_plan


def _compare(test, item, detail):
    """(ok, detail) of one item: every report word the plan attributes to it equals its expectation."""
    p = _plan(test)
    idxs = p.items[item]
    bad = [(i, p.reports[i]) for i in idxs if i >= len(test.reports) or test.reports[i] != p.reports[i].expect]
    vac = sum(1 for u in p.units if u.kind == "op" and u.item == item and u.vacuous)
    text = f"{len(idxs)} report words ({detail}" + (f"; {vac} rd = x0 read-backs counted apart" if vac else "") + ")"
    if bad:
        i, r = bad[0]
        got = f"0x{test.reports[i]:08x}" if i < len(test.reports) else "missing"
        text += f": {len(bad)} mismatch(es), first idx={i} {r.label} expected 0x{r.expect:08x} got {got}"
    else:
        text += " all match"
    return bool(idxs) and not bad, text


def _word(test, i):
    """A reported word, or None when the program stored fewer words than the plan."""
    return test.reports[i] if i < len(test.reports) else None


def _units(test, item, op=None, observed=True):
    return prog.op_units(_plan(test), item, op, observed)


def _classes_ok(test, item, op):
    """TP-MUL-013 / 015 floor: every CG-MUL-003 dividend class (divisor non-zero) and divisor class realized by an
    observed op of the item; the classes come from the plan's operands (the intent)."""
    us = _units(test, item, op)
    dividends = {prog.classify_dividend(u.a) for u in us if u.b != 0}
    divisors = set().union(*(prog.classify_divisor(u.b, u.a, prog.SIGNED[op]) for u in us)) if us else set()
    miss_a = sorted(set(prog.DIVIDEND_CLASSES) - dividends)
    miss_b = sorted(set(prog.DIVISOR_CLASSES) - divisors)
    return not miss_a and not miss_b, f"{len(us)} {op} observed, dividend classes {len(dividends)}/{len(prog.DIVIDEND_CLASSES)}" \
        + (f" missing {miss_a}" if miss_a else "") + f", divisor classes {len(divisors)}/{len(prog.DIVISOR_CLASSES)}" + (f" missing {miss_b}" if miss_b else "")


def _pairs(test, item):
    """(unit, reported quotient, reported remainder) of the item's div/rem pairs."""
    return [(u, _word(test, u.idx[0]), _word(test, u.idx[1])) for u in _units(test, item) if len(u.ops) == 2]


class MulDiv(GenTest):
    name = "gen_test_mul_div"
    schedulable = lib.TIMING_ONLY_KNOBS
    # items of the plan group this test does not check, with the reason (two-sided against the group by the structure check)
    not_built = {"TP-MUL-012": "latency/cycle clause: RVFI cycle / bus records, event export",
                 "TP-MUL-022": "latency/cycle clause: RVFI cycle / bus records, event export"}

    def report_count(self):
        return _plan(self).k

    def fire_check(self):
        self.fire_program_verdict()
        self.fire_tp_mul_013()
        self.fire_tp_mul_014()
        self.fire_tp_mul_015()
        self.fire_tp_mul_016()
        self.fire_tp_mul_017()
        self.fire_tp_mul_018()
        self.fire_tp_mul_019()
        self.fire_tp_mul_020()
        self.fire_tp_mul_021()
        self.fire_tp_mul_026()

    def fire_program_verdict(self):
        code = int(self.h.b.evt_eot_code.value)
        floor = lib.program_min_retired(self.image)
        got = self.eot_retired
        n, k = len(self.reports), _plan(self).k
        self.check("fire_program_verdict", code == lib.TOHOST_PASS and got >= floor and n == k,
                   f"tohost code 0x{code:08x} (pass {lib.TOHOST_PASS}); retired at eot {got} (floor {floor}); reports {n} (k {k})")

    def fire_tp_mul_013(self):
        ok_c, cls = _classes_ok(self, prog.I_DIVU, "divu")
        ok, detail = _compare(self, prog.I_DIVU, cls)
        self.check("fire_tp_mul_013", ok and ok_c, detail)

    def fire_tp_mul_014(self):
        pairs = _pairs(self, prog.I_REM)
        signs = {prog.sign_pair(u.a, u.b) for u, _, _ in pairs}
        # the spec identity on the REPORTED quotient and remainder, mod 2^32 (it also holds on the by-zero and overflow rows)
        broken = [(u, q, r) for u, q, r in pairs if q is None or r is None or (u.b * q + r) & prog.MASK32 != u.a]
        ok, detail = _compare(self, prog.I_REM, f"{len(pairs)} div/rem pairs, sign pairs {sorted(signs)}, identity dividend == "
                              f"divisor * quotient + remainder broken on {len(broken)}"
                              + (f" (first 0x{broken[0][0].a:08x}/0x{broken[0][0].b:08x} q={broken[0][1]} r={broken[0][2]})" if broken else ""))
        self.check("fire_tp_mul_014", ok and signs == set(prog.SIGN_PAIRS) and not broken, detail)

    def fire_tp_mul_015(self):
        ok_c, cls = _classes_ok(self, prog.I_REMU, "remu")
        ok, detail = _compare(self, prog.I_REMU, cls)
        self.check("fire_tp_mul_015", ok and ok_c, detail)

    def fire_tp_mul_016(self):
        us = _units(self, prog.I_DIV0)
        classes = {(u.ops[0], prog.classify_dividend(u.a) if u.a in prog.DIVIDEND_NAMED.values() else "rand") for u in us}
        want = {(op, c) for op in ("div", "divu") for c in prog.DIV0_DIVIDEND_CLASSES}
        ok, detail = _compare(self, prog.I_DIV0, f"{len(us)} divides by zero, op x dividend class {len(classes & want)}/{len(want)}")
        self.check("fire_tp_mul_016", ok and want <= classes, detail)
        for op in ("div", "divu"):     # the explicit row of the table: the quotient of a division by zero has all bits set
            words = [(u, _word(self, u.idx[0])) for u in _units(self, prog.I_DIV0, op)]
            bad = [(u, w) for u, w in words if w != prog.ALL_ONES]
            self.check(f"fire_tp_mul_016_{op}", bool(words) and not bad,
                       f"{len(words)} {op} by zero reported 0xffffffff" + (f"; {len(bad)} did not, first dividend 0x{bad[0][0].a:08x} got {bad[0][1]}" if bad else ""))

    def fire_tp_mul_017(self):
        us = _units(self, prog.I_REM0)
        classes = {(u.ops[0], prog.classify_dividend(u.a) if u.a in prog.DIVIDEND_NAMED.values() else "rand") for u in us}
        want = {(op, c) for op in ("rem", "remu") for c in prog.DIV0_DIVIDEND_CLASSES}
        ok, detail = _compare(self, prog.I_REM0, f"{len(us)} remainders by zero, op x dividend class {len(classes & want)}/{len(want)}")
        self.check("fire_tp_mul_017", ok and want <= classes, detail)
        for op in ("rem", "remu"):     # the explicit row of the table: the remainder of a division by zero equals the dividend
            words = [(u, _word(self, u.idx[0])) for u in _units(self, prog.I_REM0, op)]
            bad = [(u, w) for u, w in words if w != u.a]
            self.check(f"fire_tp_mul_017_{op}", bool(words) and not bad,
                       f"{len(words)} {op} by zero reported the dividend" + (f"; {len(bad)} did not, first dividend 0x{bad[0][0].a:08x} got {bad[0][1]}" if bad else ""))

    def fire_tp_mul_018(self):
        us = _units(self, prog.I_OVF)
        ok, detail = _compare(self, prog.I_OVF, f"{len(us)} ops with dividend INT_MIN and a negative divisor")
        self.check("fire_tp_mul_018", ok, detail)
        # the explicit overflow row, signed: div(INT_MIN, -1) == INT_MIN and rem(INT_MIN, -1) == 0
        row = {op: [_word(self, u.idx[0]) for u in _units(self, prog.I_OVF, op) if u.a == prog.INT_MIN and u.b == prog.ALL_ONES] for op in prog.DIV_OPS}
        want = {"div": prog.INT_MIN, "rem": 0, "divu": 0, "remu": prog.INT_MIN}
        for tag, ops in (("signed", ("div", "rem")), ("unsigned", ("divu", "remu"))):
            got = {op: row[op] for op in ops}
            self.check(f"fire_tp_mul_018_{tag}", all(got[op] and all(w == want[op] for w in got[op]) for op in ops),
                       "; ".join(f"{op}(INT_MIN, all ones) reported {[hex(w) if w is not None else None for w in got[op]]} expected 0x{want[op]:08x}" for op in ops))

    def fire_tp_mul_019(self):
        pairs = _pairs(self, prog.I_SIGN)
        signs = {prog.sign_pair(u.a, u.b) for u, _, _ in pairs}
        pinned = {(prog.to_signed(u.a), prog.to_signed(u.b)) for u, _, _ in pairs}
        missing = sorted(set(prog.SIGN_PINNED.values()) - pinned)
        # the program's sign checks on the REPORTED values: quotient sign = xor of the operand signs, remainder sign = dividend sign
        bad_q = [u for u, q, _ in pairs if q is None or (q != 0 and prog.sign_bit(q) != (prog.sign_bit(u.a) ^ prog.sign_bit(u.b)))]
        bad_r = [u for u, _, r in pairs if r is None or (r != 0 and prog.sign_bit(r) != prog.sign_bit(u.a))]
        ok, detail = _compare(self, prog.I_SIGN, f"{len(pairs)} div/rem pairs, quadrants {sorted(signs)}, pinned rows missing {missing}, "
                              f"quotient-sign violations {len(bad_q)}, remainder-sign violations {len(bad_r)}")
        self.check("fire_tp_mul_019", ok and signs == set(prog.SIGN_PAIRS) and not missing and not bad_q and not bad_r, detail)

    def fire_tp_mul_020(self):
        us = _units(self, prog.I_MSB)
        rows = {op: {(u.a, u.b) for u in _units(self, prog.I_MSB, op)} for op in ("divu", "remu")}
        missing = sorted((op, f"0x{a:08x}/0x{b:08x}") for op in rows for a, b in set(prog.MSB_ROWS) - rows[op])
        results = {_word(self, u.idx[0]) for u in us}
        unseen = sorted(set(prog.MSB_RESULTS) - results)
        ok, detail = _compare(self, prog.I_MSB, f"{len(us)} divu/remu with MSB-set operands, listed rows missing {missing}, "
                              f"results INT_MAX/0/INT_MIN/1 unseen {[hex(v) for v in unseen]}")
        self.check("fire_tp_mul_020", ok and not missing and not unseen, detail)

    def fire_tp_mul_021(self):
        us = _units(self, prog.I_CORNER)
        missing = []
        for op in prog.DIV_OPS:
            ops = _units(self, prog.I_CORNER, op)
            seen = set().union(*(prog.classify_divisor(u.b, u.a, prog.SIGNED[op]) for u in ops)) if ops else set()
            missing += [(op, c) for c in prog.CORNER_DIVISOR_CLASSES if c not in seen]
            if not any(u.a == 0 for u in ops):
                missing.append((op, "dividend_zero"))
        ok, detail = _compare(self, prog.I_CORNER, f"{len(us)} corner divides over the four ops, op x divisor corner missing {missing}")
        self.check("fire_tp_mul_021", ok and not missing, detail)

    def fire_tp_mul_026(self):
        us = _units(self, prog.I_DECODE, observed=False)
        forms = {(u.ops[0], u.rds[0] == 0) for u in us}
        missing = sorted((op, "rd_x0" if x0 else "rd") for op in prog.M_OPS for x0 in (True, False) if (op, x0) not in forms)
        x0_words = [(u, _word(self, u.idx[0])) for u in us if u.rds[0] == 0]
        bad_x0 = [(u, w) for u, w in x0_words if w != 0]
        ok, detail = _compare(self, prog.I_DECODE, f"{len(us)} M ops over the eight funct3, forms missing {missing}, {len(x0_words)} rd = x0 forms "
                              f"read x0 back" + (f" with {len(bad_x0)} non-zero (first {bad_x0[0][0].ops[0]} got {bad_x0[0][1]})" if bad_x0 else " as 0"))
        self.check("fire_tp_mul_026", ok and not missing and bool(x0_words) and not bad_x0, detail)


@cocotb.test()
async def gen_test_mul_div(dut):
    await MulDiv(dut).run()
