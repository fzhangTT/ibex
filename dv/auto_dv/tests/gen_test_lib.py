"""gen_test_lib: shared helpers for the Test Writer's cocotb tests (dv/auto_dv/tests/gen_test_*.py).

Owns the three randomization layers on the Python side (DV_prompt Section 6, architecture C9):
layer 1 weighted per-transaction draws (Weighted, the W-tables), layer 2 the regime-knob draw for
the knobs a test lets vary (draw_knobs), layer 3 the seed-derived regime schedule (Schedule) with
its command-line form +gen_regime_sched=<knob>:<value>@r<N>|c<N>,... (consumed when supplied).
Every name comes from the rendered dv/auto_dv/gen_tb/gen_knobs.py; every string that can be logged
is ASCII (TB_CONTRACT Section 4). Failures are Python asserts (the only Python-side failure path).

Self-test (host only, no simulator): python3 dv/auto_dv/tests/gen_test_lib.py --self-test
"""
import random
import re
import sys
from pathlib import Path

from dv.auto_dv.gen_tb.gen_knobs import CMD, CONSTANTS, KNOB_IDS, PLUSARGS, plusarg

REPO_ROOT = Path(__file__).resolve().parents[3]
RISCV_DV_TESTLIST = REPO_ROOT / "dv/auto_dv/stim/gen_riscv_dv_target/gen_testlist.yaml"
FCOV_HOME = REPO_ROOT / "dv/auto_dv/fcov_expectations"
PASS_MARKER = "GEN_TEST_PASS"
KNOB_PREFIX = "knob_"

# Regime knobs with a REGIME_SET consumer in gen_env_pkg::gen_cmd_dispatch; every other knob is a
# collected uvm_error there, so only these are schedulable at run time. HEAD has no consumer (TB
# Infra's step 2b is parked under work/tb-infra/step2b_wip during T-068): set both tuples to the
# step-2b set (prefixes knob_imem_, knob_dmem_, knob_irq_; names knob_debug_req_regime,
# knob_scr_key_delay) when it lands, and to every knob when the remaining consumers land.
REGIME_SET_CONSUMED_PREFIXES = ()
REGIME_SET_CONSUMED_NAMES = ()
SCHEDULABLE_KNOBS = tuple(n for n in KNOB_IDS
                          if n.startswith(REGIME_SET_CONSUMED_PREFIXES) or n in REGIME_SET_CONSUMED_NAMES)
# Regime knobs whose values only shift bus and key timing; a program needs no handler for them.
TIMING_ONLY_CANDIDATES = ("knob_imem_gnt_delay", "knob_imem_rvalid_delay", "knob_imem_outstanding_cap",
                          "knob_dmem_gnt_delay", "knob_dmem_rvalid_delay", "knob_scr_key_delay")
TIMING_ONLY_KNOBS = tuple(n for n in TIMING_ONLY_CANDIDATES if n in SCHEDULABLE_KNOBS)

# Bridge argument encodings of gen_env_pkg::gen_cmd_dispatch / gen_agents_pkg (step 2b). Mirror
# kept here until gen_knobs_codegen.py renders them into gen_knobs.py (asked of TB Infra, plan
# Section 6 item 1); a drift shows up as a collected GEN_CMD_DISPATCH error, never silently.
IRQ_LINE_BIT = {"software": 0, "timer": 1, "external": 2, "nm": 18}
IRQ_FAST_BIT0 = 3
IRQ_HOLD = {"cycles": 0, "until_ack": 1, "until_taken": 2, "sticky": 3}
DBG_HOLD = {"cycles": 0, "until_debug_mode": 1, "sticky": 2}
MEM_ERR_BUS = {"ibus": 0, "dbus": 1}
MEM_ERR_KIND = {"err": 1, "intg": 2}

# CG-REG-007 duration classes (gen_fcov_plan.md Section 3.8): TB-side phase length in cycles.
DURATION_CLASSES = {"short": (500, 2000), "medium": (2001, 20000), "long": (20001, 100000)}
DEFAULT_DURATION_WEIGHTS = {"short": 6, "medium": 3, "long": 1}


def check_ascii(path):
    """Every byte of a test source is ASCII (a non-ASCII log string crashes cocotb's failure path)."""
    data = Path(path).read_bytes()
    bad = [i for i, b in enumerate(data) if b > 0x7F]
    assert not bad, f"GEN_TEST_LIB: non-ASCII byte at offset {bad[0]} in {path}"
    return True


def plus(name, default=None):
    """Value of +gen_<name> from the simulator command line, by its rendered name."""
    import cocotb  # imported here so the host self-test needs no simulator
    return cocotb.plusargs.get(PLUSARGS[name]["plusarg"], default)


def plus_int(name, default=None):
    v = plus(name, default)
    return None if v is None else int(v)


def knob_is_pinned(name):
    """A regime knob supplied on the command line is pinned for the run (architecture C9)."""
    import cocotb
    return PLUSARGS[name]["plusarg"] in cocotb.plusargs


def knob_values(name):
    return list(PLUSARGS[name]["values"])


def knob_default(name):
    return PLUSARGS[name]["default"]


def short_knob(name):
    """Plan-side knob name (gen_fcov_plan.md Section REG): the yaml name without the knob_ prefix."""
    return name[len(KNOB_PREFIX):] if name.startswith(KNOB_PREFIX) else name


def long_knob(short):
    return short if short.startswith(KNOB_PREFIX) else KNOB_PREFIX + short


def sub_rng(seed, tag):
    """A deterministic stream per purpose from the one run seed (str seeding hashes with sha512)."""
    return random.Random(f"{int(seed)}:{tag}")


class Weighted:
    """Layer 1: a weighted choice over named classes ({name: weight}) from a given rng."""

    def __init__(self, table):
        assert table and all(w > 0 for w in table.values()), "GEN_TEST_LIB: empty or non-positive weight table"
        self.names = list(table)
        self.weights = [table[n] for n in self.names]

    def draw(self, rng):
        return rng.choices(self.names, weights=self.weights, k=1)[0]


def draw_knobs(seed, names, tag="knobs"):
    """Layer 2: a value per knob in `names` drawn from the run seed (pinned knobs are excluded by the
    caller); returns {knob: value}."""
    rng = sub_rng(seed, tag)
    return {n: rng.choice(knob_values(n)) for n in names}


class Phase:
    """One schedule entry: at trigger (kind 'c' cycles or 'r' retirements, absolute count) set knob to value."""

    def __init__(self, idx, kind, count, knob, value):
        assert kind in ("c", "r"), f"GEN_TEST_LIB: bad trigger kind {kind}"
        assert knob in KNOB_IDS, f"GEN_TEST_LIB: {knob} is not a regime knob"
        assert value in knob_values(knob), f"GEN_TEST_LIB: {value} is not a value of {knob}"
        self.idx, self.kind, self.count, self.knob, self.value = idx, kind, int(count), knob, value
        self.applied_cycle = None

    def text(self):
        return f"{short_knob(self.knob)}:{self.value}@{self.kind}{self.count}"


class Schedule:
    """Layer 3: the regime schedule of one run. Derived from the run seed (derive) or consumed from
    +gen_regime_sched (parse); the text form is what the banner echoes and what reproduces it."""

    def __init__(self, phases, source):
        self.phases = list(phases)
        self.source = source   # "derived" or "supplied"

    @property
    def k(self):
        """Phase count as CG-REG-007 counts it: distinct trigger points (phase 0 included)."""
        return len({(p.kind, p.count) for p in self.phases})

    def text(self):
        return ",".join(p.text() for p in self.phases)

    def knobs(self):
        return sorted({p.knob for p in self.phases}, key=lambda n: KNOB_IDS[n])

    @staticmethod
    def derive(seed, names, k_range=(1, 5), duration_weights=None, initial=None):
        """Phase 0 at c0 sets every knob in `names` to its layer-2 value (`initial` or drawn); phases
        1..K-1 each change a random non-empty subset of the knobs at a cycle boundary drawn from the
        CG-REG-007 duration classes; K is drawn from k_range (inclusive)."""
        names = list(names)
        rng = sub_rng(seed, "sched")
        initial = dict(initial) if initial is not None else draw_knobs(seed, names)
        current = dict(initial)
        phases = [Phase(0, "c", 0, n, initial[n]) for n in names]
        if not names:
            return Schedule(phases, "derived")
        k = rng.randint(k_range[0], k_range[1])
        dur_pick = Weighted(duration_weights or DEFAULT_DURATION_WEIGHTS)
        cycle = 0
        for idx in range(1, k):
            lo, hi = DURATION_CLASSES[dur_pick.draw(rng)]
            cycle += rng.randint(lo, hi)
            changed = rng.sample(names, rng.randint(1, len(names)))
            for n in changed:
                others = [v for v in knob_values(n) if v != current[n]]
                if not others:
                    continue
                current[n] = rng.choice(others)
                phases.append(Phase(idx, "c", cycle, n, current[n]))
        return Schedule(phases, "derived")

    @staticmethod
    def parse(text):
        """+gen_regime_sched=<knob>:<value>@r<N>|c<N>,... (knob = plan-side name or yaml name)."""
        phases = []
        idx_of = {}
        for tok in text.split(","):
            tok = tok.strip()
            if not tok:
                continue
            m = re.fullmatch(r"([A-Za-z_]\w*):([A-Za-z_]\w*)@([rc])(\d+)", tok)
            assert m, f"GEN_TEST_LIB: bad schedule token {tok!r} (want knob:value@r<N> or @c<N>)"
            knob = long_knob(m.group(1))
            key = (m.group(3), int(m.group(4)))
            idx = idx_of.setdefault(key, len(idx_of))
            phases.append(Phase(idx, m.group(3), m.group(4), knob, m.group(2)))
        return Schedule(phases, "supplied")

    def regime_set_args(self, phase):
        """REGIME_SET command arguments: arg0 knob id, arg1 value index (gen_cmd_dispatch::apply_knob)."""
        return (KNOB_IDS[phase.knob], knob_values(phase.knob).index(phase.value), 0, 0)


def irq_mask(lines=(), fast=()):
    """IRQ_SET/IRQ_CLR line mask: named lines (software, timer, external, nm) plus fast ids 0..14."""
    m = 0
    for name in lines:
        m |= 1 << IRQ_LINE_BIT[name]
    for i in fast:
        assert 0 <= i < 15, f"GEN_TEST_LIB: fast interrupt id {i} out of range"
        m |= 1 << (IRQ_FAST_BIT0 + i)
    return m


def riscv_dv_instr_cnt(test_name):
    """+instr_cnt of a riscv-dv entry in the team target testlist (the program's generated instruction
    count, the lower bound of its retirements); None when the entry has no instr_cnt."""
    import yaml
    for entry in yaml.safe_load(RISCV_DV_TESTLIST.read_text()):
        if entry.get("test") == test_name:
            m = re.search(r"\+instr_cnt=(\d+)", entry.get("gen_opts", ""))
            return int(m.group(1)) if m else None
    raise AssertionError(f"GEN_TEST_LIB: riscv-dv test {test_name} not in {RISCV_DV_TESTLIST}")


def program_symbol_word(image, symbol):
    """Value of a data word the program defines (global symbol -> the image word at its address)."""
    syms = image.sidecar.get("symbols", {})
    assert symbol in syms, f"GEN_TEST_LIB: program defines no symbol {symbol}"
    addr = int(syms[symbol], 16)
    assert addr % 4 == 0 and (addr // 4) in image.words, f"GEN_TEST_LIB: symbol {symbol} at 0x{addr:08x} is not an image word"
    return image.words[addr // 4]


def program_min_retired(image):
    """Retirement floor of a program: riscv-dv +instr_cnt for a generated program, the program's own
    gen_min_retired word for a directed one (every directed test program declares it)."""
    test = image.sidecar.get("test")
    if test:
        n = riscv_dv_instr_cnt(test)
        assert n is not None, f"GEN_TEST_LIB: riscv-dv test {test} has no +instr_cnt"
        return n
    return program_symbol_word(image, "gen_min_retired")


def load_manifest_bins(test_name):
    """Declared bins of dv/auto_dv/fcov_expectations/<test>.fcov.yaml (None when absent)."""
    import yaml
    path = FCOV_HOME / f"{test_name}.fcov.yaml"
    if not path.is_file():
        return None
    data = yaml.safe_load(path.read_text())
    assert data.get("test") == test_name, f"GEN_TEST_LIB: {path} test field != {test_name}"
    return list(data.get("bins") or [])


def check_manifest_matches(test_name, declared):
    """The test's declare_bins() and its manifest file list the same bins (host-side unit check)."""
    bins = load_manifest_bins(test_name)
    if bins is None:
        return False
    assert sorted(bins) == sorted(declared), f"GEN_TEST_LIB: manifest of {test_name} differs from declare_bins()"
    return True


def _self_test():
    seed = 12345
    names = list(TIMING_ONLY_CANDIDATES)   # the mechanics are tested independent of the consumer gate
    empty = Schedule.derive(seed, [])
    assert empty.k == 0 and empty.text() == "" and empty.phases == [], "empty schedule"
    s1 = Schedule.derive(seed, names)
    s2 = Schedule.derive(seed, names)
    assert s1.text() == s2.text(), "schedule not deterministic"
    s3 = Schedule.derive(seed + 1, names)
    assert s3.text() != s1.text(), "schedule does not depend on the seed"
    p = Schedule.parse(s1.text())
    assert p.text() == s1.text() and p.source == "supplied", "schedule text round trip"
    assert s1.k >= 1 and all(ph.kind == "c" for ph in s1.phases), "phase kinds"
    for ph in s1.phases:
        a = s1.regime_set_args(ph)
        assert a[0] == KNOB_IDS[ph.knob] and knob_values(ph.knob)[a[1]] == ph.value
    d = draw_knobs(seed, names)
    assert set(d) == set(names) and all(d[n] in knob_values(n) for n in names)
    assert irq_mask(["software", "nm"], [0, 14]) == (1 << 0) | (1 << 18) | (1 << 3) | (1 << 17)
    assert riscv_dv_instr_cnt("gen_rand_smoke") == 300
    assert CMD["REGIME_SET"] and CONSTANTS["GEN_CLK_PERIOD_NS"] > 0 and plusarg("regime_sched", "x").startswith("+gen_")
    here = Path(__file__).resolve().parent
    for f in sorted(here.glob("gen_test_*.py")) + sorted((here / "gen_programs").glob("*.S")):
        check_ascii(f)
    print(f"GEN_TEST_LIB self-test PASS (schedule k={s1.k}: {s1.text()})")
    return 0


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        sys.exit(_self_test())
    print(__doc__)
