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

from dv.auto_dv.gen_tb import gen_knobs as _gk
from dv.auto_dv.gen_tb.gen_knobs import CMD, CONSTANTS, KNOB_IDS, PLUSARGS, plusarg

REPO_ROOT = Path(__file__).resolve().parents[3]
RISCV_DV_TESTLIST = REPO_ROOT / "dv/auto_dv/stim/gen_riscv_dv_target/gen_testlist.yaml"
FCOV_HOME = REPO_ROOT / "dv/auto_dv/fcov_expectations"
PASS_MARKER = "GEN_TEST_PASS"
KNOB_PREFIX = "knob_"

REGIME_KNOBS = tuple(KNOB_IDS)   # every layer-2/3 knob (the 20 of gen_tb_knobs.yaml)
GEN_ENV_PKG = REPO_ROOT / "dv/auto_dv/env/gen_env_pkg.sv"


def consumed_knobs_from_sv(path=GEN_ENV_PKG):
    """Regime knobs the build's REGIME_SET dispatcher consumes, read from gen_cmd_dispatch::apply_knob in
    gen_env_pkg.sv (prefix tests `name.substr(...) == "knob_x_"` and exact tests `name == "knob_x"`, comments
    ignored, `function [automatic] void`); an absent apply_knob means no consumer. Pre-codegen fallback only:
    the rendered REGIME_SET_CONSUMED is the sole trusted source once TB Infra renders it."""
    text = path.read_text()
    m = re.search(r"function\s+(?:automatic\s+)?void\s+apply_knob\b(.*?)endfunction", text, re.S)
    if not m:
        return ()
    body = re.sub(r"//[^\n]*", "", re.sub(r"/\*.*?\*/", "", m.group(1), flags=re.S))
    prefixes = re.findall(r'name\.substr\([^)]*\)\s*==\s*"(knob_\w+?_)"', body)
    exact = re.findall(r'name\s*==\s*"(knob_\w+)"', body)
    return tuple(n for n in REGIME_KNOBS if n in exact or any(n.startswith(px) for px in prefixes))


# Knobs with a REGIME_SET consumer in this tree: the rendered constant when the codegen provides it
# (TB Infra renders REGIME_SET_CONSUMED from gen_tb_knobs.yaml in the same commit as the new dispatcher,
# whose guard uses the same rendering), else parsed from the parked step-2b dispatcher idiom; the parser
# is the pre-codegen fallback only and is not consulted once the constant exists.
CONSUMED_KNOBS = tuple(_gk.REGIME_SET_CONSUMED) if hasattr(_gk, "REGIME_SET_CONSUMED") else consumed_knobs_from_sv()
SCHEDULABLE_KNOBS = CONSUMED_KNOBS
# Regime knobs whose values only shift bus and key timing; a program needs no handler for them.
TIMING_ONLY_KNOBS = ("knob_imem_gnt_delay", "knob_imem_rvalid_delay", "knob_imem_outstanding_cap",
                     "knob_dmem_gnt_delay", "knob_dmem_rvalid_delay", "knob_scr_key_delay")
# End-of-test codes of the riscv-dv / tohost convention (gen_program.py, gen_directed/gen_zc_directed.S).
TOHOST_PASS = 1
TOHOST_FAIL = 3

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
        kinds = {p.kind for p in self.phases}
        assert len(kinds) <= 1, f"GEN_TEST_LIB: a schedule uses one trigger kind (c or r), got {sorted(kinds)}"

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


FLOW_TESTLIST = REPO_ROOT / "dv/auto_dv/flow/gen_testlist.yaml"
STAGED_ENTRIES = REPO_ROOT / "dv/auto_dv/work/test-writer/gen_testlist_entries.yaml"
# COV_WITNESS codes per TP id, rendered by TB Infra with the SV table (plan v2f witness protocol); {} until then.
WITNESS_IDS = dict(getattr(_gk, "WITNESS_IDS", None) or {})
# class name -> reason: the only other way than a `measured: false` entry to set layers_required = False.
LAYERS_OPTOUT_ALLOWLIST = {}


def testlist_entry(test_name):
    """The test's testlist entry: the committed flow testlist first, the Test Writer's staged entries second (a
    test in bring-up before Runtime copied its entry); None when neither names it."""
    import yaml
    for path in (FLOW_TESTLIST, STAGED_ENTRIES):
        if path.is_file():
            for e in (yaml.safe_load(path.read_text()) or {}).get("tests") or []:
                if e.get("name") == test_name:
                    return e
    return None


def witness_ids_of(test_name):
    """TP ids whose witness bins the entry allows this test to issue (`witness_ids`); () when none."""
    return tuple((testlist_entry(test_name) or {}).get("witness_ids") or ())


def tp_id_of(fire_name):
    """fire_tp_<area>_<nnn>[_suffix] -> TP-<AREA>-<nnn>; a fire-check outside that form has no item id."""
    m = re.match(r"fire_tp_([a-z]+)_(\d+)", fire_name)
    assert m, f"GEN_TEST_LIB: {fire_name} is not a fire_tp_<area>_<nnn> item check"
    return f"TP-{m.group(1).upper()}-{m.group(2)}"


TEMPLATE_PY = Path(__file__).resolve().parent / "gen_test_template.py"
TEST_HOOKS = ("stimulus", "fire_check", "declare_bins", "report_count")


def _template_methods():
    import ast
    tree = ast.parse(TEMPLATE_PY.read_text())
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "GenTest":
            return {n.name for n in node.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))}
    raise AssertionError(f"GEN_TEST_LIB: no class GenTest in {TEMPLATE_PY}")


def check_test_source(source, path="<source>", entry_lookup=None):
    """Host-side structure check of a test module. Every GenTest subclass (bases resolved through module-level
    aliases; nested classes are refused) overrides only the hooks (stimulus, fire_check, declare_bins,
    report_count) and per-item fire_* methods, never run/finish/check/setup or another template method;
    module-level writes to a test class (T.finish = f, setattr) are refused; at least one self.check(...) exists
    and none passes a literal ok; COV_WITNESS never appears (the template's finish() epilogue owns it) and
    `cycle_clause_true=` is a keyword of self.check inside a fire_* method only; `layers_required = False`
    needs a testlist entry with `measured: false` for the class's `name` or an allowlisted reason. Returns
    the checked class names; raises AssertionError on a violation."""
    import ast
    tree = ast.parse(source, filename=str(path))
    protected = _template_methods() - set(TEST_HOOKS)
    lookup = entry_lookup or testlist_entry
    top = {n.name: n for n in tree.body if isinstance(n, ast.ClassDef)}
    aliases = {}
    for n in tree.body:
        if isinstance(n, ast.Assign) and isinstance(n.value, ast.Name):
            aliases.update({tg.id: n.value.id for tg in n.targets if isinstance(tg, ast.Name)})

    def resolve(name, seen=()):
        while name in aliases and name not in seen:
            seen, name = seen + (name,), aliases[name]
        return name

    def base_name(b):
        return b.id if isinstance(b, ast.Name) else (b.attr if isinstance(b, ast.Attribute) else "")

    def is_gentest(cls, seen=()):
        for b in cls.bases:
            name = resolve(base_name(b))
            if name == "GenTest":
                return True
            if name in top and name not in seen and is_gentest(top[name], seen + (name,)):
                return True
        return False

    tests = [c for c in ast.walk(tree) if isinstance(c, ast.ClassDef) and c.name != "GenTest" and is_gentest(c)]
    nested = [c.name for c in tests if c not in tree.body]
    assert not nested, f"GEN_TEST_LIB: {path}: test class(es) {nested} defined inside a function or class; test classes are module-level"
    test_names = {c.name for c in tests}
    for n in tree.body:
        targets = n.targets if isinstance(n, ast.Assign) else [n.target] if isinstance(n, (ast.AugAssign, ast.AnnAssign)) else []
        for tg in targets:
            if isinstance(tg, ast.Attribute) and isinstance(tg.value, ast.Name) and resolve(tg.value.id) in test_names:
                raise AssertionError(f"GEN_TEST_LIB: {path}: module-level assignment to {tg.value.id}.{tg.attr} at line {n.lineno}; a test class takes methods in its body only")
        call = n.value if isinstance(n, ast.Expr) and isinstance(n.value, ast.Call) else None
        if call is not None and isinstance(call.func, ast.Name) and call.func.id in ("setattr", "delattr"):
            raise AssertionError(f"GEN_TEST_LIB: {path}: {call.func.id}() at module level (line {n.lineno}) is refused")
    for n in ast.walk(tree):
        tok = n.value if isinstance(n, ast.Constant) else n.attr if isinstance(n, ast.Attribute) else n.id if isinstance(n, ast.Name) else None
        assert tok != "COV_WITNESS", f"GEN_TEST_LIB: {path}: COV_WITNESS at line {n.lineno}; witnesses are issued by the template's finish() epilogue from fire-check results only"

    def is_self_check(c):
        return isinstance(c.func, ast.Attribute) and c.func.attr == "check" and isinstance(c.func.value, ast.Name) and c.func.value.id == "self"

    checked = []
    for cls in tests:
        methods = [n for n in cls.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
        bad = [m.name for m in methods if m.name in protected]
        assert not bad, f"GEN_TEST_LIB: {path}: class {cls.name} overrides template method(s) {bad}; only {TEST_HOOKS} and fire_* are hooks"
        extra = [m.name for m in methods if m.name not in TEST_HOOKS and not m.name.startswith("fire_")]
        assert not extra, f"GEN_TEST_LIB: {path}: class {cls.name} defines non-hook method(s) {extra}"
        calls = [n for n in ast.walk(cls) if isinstance(n, ast.Call) and is_self_check(n)]
        assert calls, f"GEN_TEST_LIB: {path}: class {cls.name} never calls self.check(...)"
        for c in calls:
            ok = c.args[1] if len(c.args) > 1 else next((k.value for k in c.keywords if k.arg == "ok"), None)
            assert ok is not None and not isinstance(ok, ast.Constant), \
                f"GEN_TEST_LIB: {path}: class {cls.name} passes a literal as the ok argument of self.check at line {c.lineno}"
        for m in methods:
            for c in ast.walk(m):
                if isinstance(c, ast.Call) and any(k.arg == "cycle_clause_true" for k in c.keywords):
                    assert m.name.startswith("fire_") and is_self_check(c), \
                        f"GEN_TEST_LIB: {path}: class {cls.name}: cycle_clause_true outside a fire_* method's self.check at line {c.lineno}"
        attrs = {tg.id: a.value for a in cls.body if isinstance(a, ast.Assign) for tg in a.targets if isinstance(tg, ast.Name)}
        lr = attrs.get("layers_required")
        if isinstance(lr, ast.Constant) and lr.value is False:
            nm = attrs.get("name")
            test_name = nm.value if isinstance(nm, ast.Constant) else None
            entry = lookup(test_name) if test_name else None
            assert (entry is not None and entry.get("measured") is False) or cls.name in LAYERS_OPTOUT_ALLOWLIST, \
                (f"GEN_TEST_LIB: {path}: class {cls.name} sets layers_required = False without a testlist entry "
                 f"'{test_name}' carrying measured: false (a measured test takes its layers) and without an allowlist reason")
        checked.append(cls.name)
    return checked


def check_test_module(path):
    return check_test_source(Path(path).read_text(), path)


MMIO_MAP_H = Path(__file__).resolve().parent / "gen_programs" / "gen_mmio_map.h"
MMIO_MAP_H_KEYS = {"GEN_MM_SIG_ADDR": "sig_addr", "GEN_MM_IRQ_ACK_ADDR": "irq_ack_addr", "GEN_MM_EOT_ADDR": "eot_addr",
                   "GEN_MM_PHASE_MARK_ADDR": "phase_mark_addr", "GEN_MM_DM_HALT": "dm_halt", "GEN_MM_DM_EXCEPTION": "dm_exception"}


def check_mmio_map_header(path=MMIO_MAP_H):
    """The assembler header the directed programs include carries exactly the rendered MEMORY_MAP values."""
    from dv.auto_dv.gen_tb.gen_knobs import MEMORY_MAP
    got = dict(re.findall(r"^\.set (GEN_MM_\w+), 0x([0-9a-fA-F]+)$", Path(path).read_text(), re.M))
    for sym, key in MMIO_MAP_H_KEYS.items():
        assert sym in got, f"GEN_TEST_LIB: {path} lacks {sym}"
        assert int(got[sym], 16) == MEMORY_MAP[key], f"GEN_TEST_LIB: {path} {sym} = 0x{got[sym]} != MEMORY_MAP[{key}] 0x{MEMORY_MAP[key]:08x}"
    assert set(got) == set(MMIO_MAP_H_KEYS), f"GEN_TEST_LIB: {path} carries unexpected symbols {sorted(set(got) - set(MMIO_MAP_H_KEYS))}"
    return True


def load_manifest_bins(test_name):
    """Declared bins of dv/auto_dv/fcov_expectations/<test>.fcov.yaml (None when absent)."""
    import yaml
    path = FCOV_HOME / f"{test_name}.fcov.yaml"
    if not path.is_file():
        return None
    data = yaml.safe_load(path.read_text())
    assert data.get("test") == test_name, f"GEN_TEST_LIB: {path} test field != {test_name}"
    return list(data.get("bins") or [])


def plan_bins(test_name, group=None):
    """Bins the plan assigns to the test (default group: gen_test_<x> hosts gen_<x>), derived by the manifest
    generator's own code so the test's declaration and the rendered file share one implementation."""
    from dv.auto_dv.tests import gen_fcov_manifest as gm
    return gm.plan_bins(test_name, group or re.sub(r"^gen_test_", "gen_", test_name))


def check_manifest_matches(test_name, declared):
    """The test's declare_bins() and its manifest file list the same bins; a test that declares bins must have a
    rendered manifest (a stale or missing file fails the run, never a silent skip)."""
    bins = load_manifest_bins(test_name)
    if bins is None:
        assert not declared, (f"GEN_TEST_LIB: {test_name} declares {len(declared)} bins but has no manifest "
                              f"{FCOV_HOME.name}/{test_name}.fcov.yaml (render it with gen_fcov_manifest.py --write)")
        return False
    missing = sorted(set(declared) - set(bins))
    extra = sorted(set(bins) - set(declared))
    assert not missing and not extra, (
        f"GEN_TEST_LIB: manifest of {test_name} differs from declare_bins(): {len(bins)} in the manifest, "
        f"{len(declared)} declared; not in the manifest {missing[:3]}, only in the manifest {extra[:3]} "
        f"(re-render with gen_fcov_manifest.py --write)")
    return True


def _self_test():
    seed = 12345
    names = list(TIMING_ONLY_KNOBS)   # the mechanics are tested independent of the consumer gate
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
    try:
        Schedule.parse("imem_gnt_delay:long@c0,imem_gnt_delay:short@r50")
        raise AssertionError("mixed trigger kinds accepted")
    except AssertionError as exc:
        assert "one trigger kind" in str(exc), exc
    assert riscv_dv_instr_cnt("gen_rand_smoke") == 300
    assert CMD["REGIME_SET"] and CONSTANTS["GEN_CLK_PERIOD_NS"] > 0 and plusarg("regime_sched", "x").startswith("+gen_")
    here = Path(__file__).resolve().parent
    for f in sorted(here.glob("gen_test_*.py")) + sorted((here / "gen_programs").glob("*.S")) + sorted((here / "gen_programs").glob("*.py")) + sorted((here / "gen_programs").glob("*.h")):
        check_ascii(f)
    check_mmio_map_header()
    # consumed-knob derivation: the SV parse works on a fixture and agrees with the rendered constant when present
    sv_fixture = ('function void apply_knob(int id, int idx);\n  if (name.substr(0, 9) == "knob_imem_") ok = 1;\n'
                  '  else if (name == "knob_scr_key_delay") ok = 1;\nendfunction')
    import tempfile, os
    with tempfile.NamedTemporaryFile("w", suffix=".sv", delete=False) as tf:
        tf.write(sv_fixture); tfp = Path(tf.name)
    try:
        got = consumed_knobs_from_sv(tfp)
        assert set(got) == {n for n in REGIME_KNOBS if n.startswith("knob_imem_")} | {"knob_scr_key_delay"}, got
        assert consumed_knobs_from_sv(TEMPLATE_PY) == (), "a file without apply_knob must yield no consumer"
    finally:
        os.unlink(tfp)
    if hasattr(_gk, "REGIME_SET_CONSUMED"):
        assert set(CONSUMED_KNOBS) <= set(REGIME_KNOBS), "rendered REGIME_SET_CONSUMED names an unknown knob"
    # test-module structure check: the committed tests pass, three red sources are refused
    tests = [f for f in sorted(here.glob("gen_test_*.py")) if f.name not in ("gen_test_lib.py", "gen_test_template.py")]
    for f in tests:
        assert check_test_module(f), f"{f}: no GenTest subclass found"
    base = "from dv.auto_dv.tests.gen_test_template import GenTest\nclass T(GenTest):\n    name = 'gen_test_x'\n"
    for red, why in ((base + "    def fire_check(self):\n        self.check('a', self.retired() > 0, 'x')\n    async def finish(self):\n        pass\n", "overrides"),
                     (base + "    def fire_check(self):\n        self.check('a', True, 'x')\n", "literal"),
                     (base + "    def fire_check(self):\n        pass\n", "never calls")):
        try:
            check_test_source(red, "<red>")
            raise AssertionError(f"red source ({why}) accepted")
        except AssertionError as exc:
            assert why in str(exc), exc
    assert check_test_source(base + "    def fire_check(self):\n        self.fire_tp_x_001()\n    def fire_tp_x_001(self):\n        self.check('a', self.retired() > 0, 'x')\n") == ["T"]
    # parser: the automatic form is read and a commented-out test names no knob
    with tempfile.NamedTemporaryFile("w", suffix=".sv", delete=False) as tf:
        tf.write('function automatic void apply_knob(int id, int idx);\n  // if (name == "knob_scr_key_delay") ok = 1;\n'
                 '  /* name == "knob_dmem_gnt_delay" */\n  if (name == "knob_imem_gnt_delay") ok = 1;\nendfunction'); tfp = Path(tf.name)
    try:
        assert consumed_knobs_from_sv(tfp) == ("knob_imem_gnt_delay",), consumed_knobs_from_sv(tfp)
    finally:
        os.unlink(tfp)
    # structure check, second set: aliases, module-level writes, nesting, the witness command, the layers opt-out
    good = "    def fire_check(self):\n        self.fire_tp_x_001()\n    def fire_tp_x_001(self):\n        self.check('a', self.retired() > 0, 'x')\n"
    imp = "from dv.auto_dv.tests.gen_test_template import GenTest\n"
    entries = {"gen_test_x": {"name": "gen_test_x", "measured": False}, "gen_test_m": {"name": "gen_test_m", "measured": True}}
    look = entries.get
    for red, why in ((imp + "Base = GenTest\nclass T(Base):\n    name = 'gen_test_x'\n" + good + "    async def finish(self):\n        pass\n", "overrides"),
                     (imp + "class T(GenTest):\n    name = 'gen_test_x'\n" + good + "def _f(self):\n    pass\nT.finish = _f\n", "module-level assignment"),
                     (imp + "class T(GenTest):\n    name = 'gen_test_x'\n" + good + "setattr(T, 'finish', None)\n", "setattr"),
                     (imp + "def mk():\n    class T(GenTest):\n        name = 'gen_test_x'\n" + good.replace("\n    ", "\n        ").replace("    def", "        def", 1) + "    return T\n", "inside a function"),
                     (imp + "class T(GenTest):\n    name = 'gen_test_x'\n    async def stimulus(self):\n        await self.cmd('COV_WITNESS', (1, 0, 0, 0))\n" + good, "COV_WITNESS"),
                     (imp + "class T(GenTest):\n    name = 'gen_test_x'\n    async def stimulus(self):\n        self.check('b', self.retired() > 0, 'x', cycle_clause_true=True)\n" + good, "cycle_clause_true outside"),
                     (imp + "class T(GenTest):\n    name = 'gen_test_m'\n    layers_required = False\n" + good, "measured: false"),
                     (imp + "class T(GenTest):\n    name = 'gen_test_none'\n    layers_required = False\n" + good, "measured: false")):
        try:
            check_test_source(red, "<red>", entry_lookup=look)
            raise AssertionError(f"red source ({why}) accepted")
        except AssertionError as exc:
            assert why in str(exc), (why, exc)
    assert check_test_source(imp + "class T(GenTest):\n    name = 'gen_test_x'\n    layers_required = False\n" + good, "<green>", entry_lookup=look) == ["T"]
    assert check_test_source(imp + "class T(GenTest):\n    name = 'gen_test_x'\n    def fire_check(self):\n        self.fire_tp_x_001()\n"
                             "    def fire_tp_x_001(self):\n        self.check('fire_tp_x_001', self.retired() > 0, 'x', cycle_clause_true=self.retired() > 1)\n", "<green>") == ["T"]
    assert tp_id_of("fire_tp_csr_001") == "TP-CSR-001" and tp_id_of("fire_tp_bit_016_gorci") == "TP-BIT-016"
    # manifest cross-check: declared == rendered for every committed manifest; stale and missing fail loud
    for mf in sorted(FCOV_HOME.glob("gen_test_*.fcov.yaml")):
        tn = mf.stem.replace(".fcov", "")
        assert check_manifest_matches(tn, plan_bins(tn)), tn
    for declared, why in ((plan_bins("gen_test_boot_retire") + ["x.y.z"], "no manifest"),):
        try:
            check_manifest_matches("gen_test_boot_retire", declared); raise AssertionError("missing-manifest case accepted")
        except AssertionError as exc:
            assert why in str(exc), exc
    print(f"GEN_TEST_LIB self-test PASS (consumed knobs now: {list(CONSUMED_KNOBS) or 'none'}; checked tests: {[f.name for f in tests]}; schedule k={s1.k}: {s1.text()})")
    return 0


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        sys.exit(_self_test())
    print(__doc__)
