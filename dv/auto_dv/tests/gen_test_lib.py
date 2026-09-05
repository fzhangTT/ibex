"""gen_test_lib: shared helpers for the Test Writer's cocotb tests (dv/auto_dv/tests/gen_test_*.py).

Owns the three randomization layers on the Python side (DV_prompt Section 6, architecture C9):
layer 1 weighted per-transaction draws (Weighted, the W-tables), layer 2 the regime-knob draw for
the knobs a test lets vary (draw_knobs), layer 3 the seed-derived regime schedule (Schedule) with
its command-line form +gen_regime_sched=<knob>:<value>@r<N>|c<N>,... (consumed when supplied).
Every name comes from the rendered dv/auto_dv/gen_tb/gen_knobs.py; every string that can be logged
is ASCII (TB_CONTRACT Section 4). Failures are Python asserts (the only Python-side failure path).

Self-test (host only, no simulator): python3 -m dv.auto_dv.tests.gen_test_lib --self-test from the clone root (works
with PYTHONPATH unset); the script form python3 dv/auto_dv/tests/gen_test_lib.py --self-test needs the clone root on PYTHONPATH
"""
import ast
import random
import re
import sys
from pathlib import Path

from dv.auto_dv.gen_tb import gen_knobs as _gk
from dv.auto_dv.gen_tb.gen_knobs import CMD, CONSTANTS, KNOB_CONSUMER, KNOB_IDS, PLUSARGS, plusarg
from dv.auto_dv.flow.gen_flow_const import JOB_ENV_SET as _JOB_ENV_SET

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

class CycleWaiters:
    """Which cycle-threshold waiters to wake, and what to arm the bridge with.

    The bridge has ONE cycle-threshold slot (evt_cycle_target / evt_cycle_arm / evt_cycle_hit) and
    every waiter shares it, so a caller that writes its own target destroys a pending one: a
    stimulus polling a near target once stole the schedule runner's far boundary and applied a
    whole phase group thousands of cycles early. This holds every pending target instead, arms
    only the earliest, and wakes only the waiters whose own target has been reached.

    Policy only, no cocotb: the caller owns the events and the bridge writes, so the waking rule
    is testable without a simulator.
    """

    def __init__(self):
        self._pending = []      # (target, key) in insertion order; keys are opaque to this class

    def add(self, target, key):
        self._pending.append((int(target), key))

    def add_arms(self, target, key):
        """Register a waiter and say whether the bridge slot must be re-armed for it.

        An arm edge suppresses that cycle's compare, so arming for a target the slot already
        carries can drop the hit a pending waiter is waiting for: only a new earliest target
        is worth an arm.
        """
        before = self.armed_target()
        self.add(target, key)
        return self.armed_target() != before

    def armed_target(self):
        """The target the bridge should carry: the earliest pending, or None when nothing waits."""
        return min((t for t, _ in self._pending), default=None)

    def on_hit(self, cycle):
        """A hit arrived at `cycle`: return the keys whose targets are reached, dropping them.

        Every reached target wakes, not just the armed one, because a hit at or past a later
        target satisfies it too and leaving it pending would wait for an edge that never comes.
        """
        woken = [k for t, k in self._pending if t <= cycle]
        self._pending = [(t, k) for t, k in self._pending if t > cycle]
        return woken

    def drop(self, key):
        """Remove a waiter that gave up (timeout, or the program ended)."""
        self._pending = [(t, k) for t, k in self._pending if k is not key]

    def __len__(self):
        return len(self._pending)


# CG-REG-007 duration classes (gen_fcov_plan.md Section 3.8): TB-side phase length in cycles.
# "long" ends at the schedule runner's per-trigger wait budget (GEN_ALIVE_TIMEOUT_CYCLES_DEFAULT): a longer phase would time the wait out.
DURATION_CLASSES = {"short": (500, 2000), "medium": (2001, 20000), "long": (20001, 100000)}
DEFAULT_DURATION_WEIGHTS = {"short": 6, "medium": 3, "long": 1}

# Statement shapes check_test_source refuses. The API doc lists exactly these (gen_test_template_api.md) and the self-test proves
# at least one refused red source per entry; anything not listed passes the lint; the list is frozen (a new refusal is a structural check beside it).
F_OVERRIDE = "a template method other than the four hooks overridden in the test class (directly, through an aliased base, an import alias, a mixin, a class-body assignment of the method name, or an instance rebinding from a method or helper, e.g. self.cmd = f), or an attribute reached through a template-owned name rebound from a method (an attribute chain rooted at self, e.g. self.bridge.cov_witness = f)"
F_LITERAL = "check() with a literal outcome"
F_NOCHECK = "fire_check() that records no check"
F_ITEMS = ("fire_tp_* items out of step with the plan group: a fire_tp_* method fire_check() never calls, a check name that does not start with "
           "its item's id, not_built missing or not a literal dict, an item both built and declared not built, an item neither built nor declared")
F_PATCH = "module-level assignment or setattr() over the test class, the library or the template"
F_NESTED = "the test class defined inside a function"
F_WITNESS = "the COV_WITNESS command issued from test code"
F_CYCLE = "cycle_clause_true outside a fire_tp_* method"
F_LAYERS = "layers_required = False without a measured: false testlist entry, or a non-literal value"
F_BASE = "a base class that is not GenTest by name: an unresolvable expression or an imported name"
F_RECORD = ("the verdict record (_results, results, failures, checks, witness_ids, applied, schedule, reports; reads of reports excepted) called into, "
            "aliased, bound by a walrus or tuple target, passed to a callee, captured by a lambda, item-assigned or deleted")
F_ASSIGN = "assignment through self to a template-assigned attribute"
F_INTROSPECT = "getattr(), setattr(), vars(), __dict__ or type() on the test object"
F_HELPER = "self passed to a module-level helper that touches a template-owned name, directly, through an alias inside the helper, or through an attribute chain rooted at the parameter"
F_ESCAPE = "self escaping as a bare name: an alias, a loop target or a keyword argument"
REFUSED_FORMS = (F_OVERRIDE, F_LITERAL, F_NOCHECK, F_ITEMS, F_PATCH, F_NESTED, F_WITNESS, F_CYCLE, F_LAYERS, F_BASE, F_RECORD, F_ASSIGN,
                 F_INTROSPECT, F_HELPER, F_ESCAPE)
API_DOC = "gen_test_template_api.md"
API_DOC_MARKER = "refuses exactly these statement shapes"


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


def program_min_retired(image, plan_min_retired=None):
    """Retirement floor of a program: riscv-dv +instr_cnt for a generated program, the program's own
    gen_min_retired word for a directed one (every directed test program declares it).

    plan_min_retired makes the read an IDENTITY. A directed program carries the number its generator
    computed, and the caller's plan recomputes it, so the two are equal unless the image and the
    Python checking it came from different versions of that generator. An inequality cannot see that:
    a newer, longer program clears an older floor and every later comparison is against another op's
    word. riscv-dv entries are exempt because their floor is an instruction count, not a plan value.
    """
    test = image.sidecar.get("test")
    if test:
        n = riscv_dv_instr_cnt(test)
        assert n is not None, f"GEN_TEST_LIB: riscv-dv test {test} has no +instr_cnt"
        return n
    word = program_symbol_word(image, "gen_min_retired")
    assert plan_min_retired is None or word == plan_min_retired, (
        f"GEN_TEST_LIB: the image's gen_min_retired is {word} and the plan recomputes "
        f"{plan_min_retired}; the program and the Python checking it came from different generator "
        f"versions, so no report word means what this test thinks it means")
    return word


FLOW_TESTLIST = REPO_ROOT / "dv/auto_dv/flow/gen_testlist.yaml"
STAGED_ENTRIES_ENV = "GEN_TEST_STAGED_ENTRIES"   # developer runs only: path of a staged-entries file (the flow never sets it)
FLOW_RUN_ENV = next(iter(_JOB_ENV_SET))         # the flow's one job marker (gen_flow_const.JOB_ENV_SET); a run carrying it refuses the developer variable
# COV_WITNESS codes per TP id, rendered by TB Infra with the SV table (plan v2f witness protocol); {} until then.
WITNESS_IDS = dict(getattr(_gk, "WITNESS_IDS", None) or {})
# the owner group of every witnessed item and the group index table (COV_WITNESS arg1), rendered with the SV witness ledger
WITNESS_GROUP_OF = dict(getattr(_gk, "WITNESS_GROUP_OF", None) or {})
WITNESS_GROUPS = dict(getattr(_gk, "WITNESS_GROUPS", None) or {})
# class name -> reason: the only other way than a `measured: false` entry to set layers_required = False.
LAYERS_OPTOUT_ALLOWLIST = {}


def testlist_entry(test_name):
    """The test's entry in the committed flow testlist; None when it has none. A developer run may name a staged
    file through GEN_TEST_STAGED_ENTRIES (consulted only when the committed testlist has no entry, announced on
    stderr); a committed test never reads uncommitted testlist facts otherwise."""
    import os
    import yaml
    staged = os.environ.get(STAGED_ENTRIES_ENV)
    for path in [FLOW_TESTLIST] + ([Path(staged)] if staged else []):
        if path.is_file():
            for e in (yaml.safe_load(path.read_text()) or {}).get("tests") or []:
                if e.get("name") == test_name:
                    if path != FLOW_TESTLIST:
                        print(f"GEN_TEST_LIB: {test_name}: entry taken from the staged file {path} (developer run)", file=sys.stderr)
                    return e
    return None


def test_group(test_name):
    """The plan group a test hosts (gen_test_<x> -> gen_<x>): the manifest generator's derivation, one home."""
    from dv.auto_dv.tests import gen_fcov_manifest as gm
    return gm.plan_group_of(test_name)


def witness_ids_of(test_name):
    """TP ids whose witness bins the entry allows this test to issue (`witness_ids`); () when none."""
    return tuple((testlist_entry(test_name) or {}).get("witness_ids") or ())


def tp_id_of(fire_name):
    """fire_tp_<area>_<nnn>[_suffix] -> TP-<AREA>-<nnn>; a fire-check outside that form has no item id."""
    from dv.auto_dv.tests import gen_fcov_manifest as gm
    tp = gm.tp_id_of_fire(fire_name)
    assert tp, f"GEN_TEST_LIB: {fire_name} is not a fire_tp_<area>_<nnn> item check"
    return tp


TEMPLATE_PY = Path(__file__).resolve().parent / "gen_test_template.py"
TEST_HOOKS = ("stimulus", "fire_check", "declare_bins", "report_count")


def _template_methods():
    import ast
    tree = ast.parse(TEMPLATE_PY.read_text())
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "GenTest":
            return {n.name for n in node.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))}
    raise AssertionError(f"GEN_TEST_LIB: no class GenTest in {TEMPLATE_PY}")


TEMPLATE_MODULE = "dv.auto_dv.tests.gen_test_template"
# the verdict record: aliasing these from test code is refused (reading self.reports through a local name stays allowed)
RECORD_ATTRS = frozenset({"_results", "results", "failures", "checks", "witness_ids", "applied", "schedule", "reports"})


def _template_attrs():
    """Instance names GenTest assigns (self.<name> = ...): template-owned, read-only for a test (a test's own
    self._cache is not among them)."""
    import ast
    tree = ast.parse(TEMPLATE_PY.read_text())
    cls = next(n for n in ast.walk(tree) if isinstance(n, ast.ClassDef) and n.name == "GenTest")
    names = set()
    for n in ast.walk(cls):
        targets = n.targets if isinstance(n, ast.Assign) else [n.target] if isinstance(n, (ast.AugAssign, ast.AnnAssign)) else []
        for tg in targets:
            if isinstance(tg, ast.Attribute) and isinstance(tg.value, ast.Name) and tg.value.id == "self":
                names.add(tg.attr)
    return frozenset(names | {"results", "witness_ids"})   # retired names stay refused so a stale test cannot revive them


def fire_fail_line(name, failures, xfail_bug=None):
    """The line a failed fire_check() raises; red_expect signatures match against it, so the self-test synthesizes it per check name."""
    tag = f"GEN_TEST_XFAIL {xfail_bug} " if xfail_bug else "GEN_TEST_FAIL "
    return tag + f"{name}: {len(failures)} fire-check failure(s): " + " | ".join(failures)


def api_doc_forms(path=None):
    """The refused-form bullets of the API doc: the lines after the marker sentence, a bullet per form, continuation lines indented."""
    text = Path(path or (REPO_ROOT / "dv/auto_dv/docs" / API_DOC)).read_text()
    lines = text.splitlines()
    start = next((i for i, l in enumerate(lines) if API_DOC_MARKER in l), None)
    assert start is not None, f"GEN_TEST_LIB: {API_DOC} lacks the marker sentence '{API_DOC_MARKER}'"
    forms, i = [], start + 1
    while i < len(lines) and i <= start + 6 and not lines[i].startswith("- "):   # the marker sentence may wrap before the list
        i += 1
    while i < len(lines):
        l = lines[i]
        if l.startswith("- "):
            forms.append(l[2:].strip())
        elif l.startswith("  ") and forms and l.strip():
            forms[-1] += " " + l.strip()
        else:
            break
        i += 1
    return forms


def _gm():
    from dv.auto_dv.tests import gen_fcov_manifest as gm
    return gm


def rebind_targets(node):
    """Every assignment target of a statement or clause, flattened: Assign / AugAssign / AnnAssign targets, for and with targets,
    comprehension targets, and the elements of tuple, list and starred targets."""
    if isinstance(node, ast.Assign): tops = list(node.targets)
    elif isinstance(node, (ast.AugAssign, ast.AnnAssign, ast.For, ast.AsyncFor, ast.comprehension)): tops = [node.target]
    elif isinstance(node, (ast.With, ast.AsyncWith)): tops = [i.optional_vars for i in node.items if i.optional_vars is not None]
    else: return []
    out = []
    def flat(t):
        if isinstance(t, (ast.Tuple, ast.List)): [flat(e) for e in t.elts]
        elif isinstance(t, ast.Starred): flat(t.value)
        else: out.append(t)
    for t in tops: flat(t)
    return out


def check_test_source(source, path="<source>", entry_lookup=None):
    """Host-side structure check of a test module (lint, run by the library self-test, not by the flow). Every test
    class (a class whose bases resolve to GenTest through module-level aliases, import aliases or module-local
    classes; any other base, a base expression, or a nested class is an error) overrides only the hooks (stimulus,
    fire_check, declare_bins, report_count) and per-item fire_* methods, in its own body and in its module-local
    mixins, never run/finish/check/setup or another template method; module-level writes to a test class, to the
    library or to the template (T.finish = f, setattr, lib.X = ...) are refused; test code never assigns to or
    calls into the instance names the template assigns (_template_attrs, e.g. _results, checks, failures); at least one self.check
    exists and none passes a literal ok; COV_WITNESS never appears; `cycle_clause_true=` is a keyword of
    self.check inside a fire_* method only; `layers_required` is a literal True/False, and False needs a testlist
    entry with `measured: false` for the class's `name` or an allowlisted reason. Returns the checked class names."""
    import ast
    tree = ast.parse(source, filename=str(path))
    protected = _template_methods() - set(TEST_HOOKS)
    lookup = entry_lookup or testlist_entry
    top = {n.name: n for n in tree.body if isinstance(n, ast.ClassDef)}
    gentest_names = {"GenTest"}
    imported = set()
    aliases = {}
    for n in tree.body:
        if isinstance(n, ast.ImportFrom):
            for a in n.names:
                local = a.asname or a.name
                imported.add(local)
                if n.module == TEMPLATE_MODULE and a.name == "GenTest":
                    gentest_names.add(local)
        elif isinstance(n, ast.Import):
            imported.update((a.asname or a.name).split(".")[0] for a in n.names)
        elif isinstance(n, ast.Assign) and isinstance(n.value, ast.Name):
            aliases.update({tg.id: n.value.id for tg in n.targets if isinstance(tg, ast.Name)})

    def resolve(name, seen=()):
        while name in aliases and name not in seen:
            seen, name = seen + (name,), aliases[name]
        return name

    def base_name(cls, b):
        if isinstance(b, ast.Name):
            return resolve(b.id)
        if isinstance(b, ast.Attribute):
            return resolve(b.attr)
        raise AssertionError(f"GEN_TEST_LIB: {path}: class {cls.name} has an unresolvable base expression at line {b.lineno}")

    def is_gentest(cls, seen=()):
        found = False
        for b in cls.bases:
            name = base_name(cls, b)
            if name in gentest_names:
                found = True
            elif name in top:
                found = found or (name not in seen and is_gentest(top[name], seen + (name,)))
            elif name in ("object",):
                continue
            else:
                raise AssertionError(f"GEN_TEST_LIB: {path}: class {cls.name} has an unknown or imported base {name} at line {b.lineno}; "
                                     f"only GenTest and module-local classes are allowed")
        return found

    tests = [c for c in ast.walk(tree) if isinstance(c, ast.ClassDef) and c.name not in gentest_names and is_gentest(c)]
    nested = [c.name for c in tests if c not in tree.body]
    assert not nested, f"GEN_TEST_LIB: {path}: test class(es) {nested} defined inside a function or class; test classes are module-level"
    test_names = {c.name for c in tests}
    guarded_modules = {"lib", "gen_test_lib", "gen_test_template"} | gentest_names | test_names
    for n in tree.body:
        targets = n.targets if isinstance(n, ast.Assign) else [n.target] if isinstance(n, (ast.AugAssign, ast.AnnAssign)) else []
        for tg in targets:
            if isinstance(tg, ast.Attribute) and isinstance(tg.value, ast.Name) and resolve(tg.value.id) in guarded_modules:
                raise AssertionError(f"GEN_TEST_LIB: {path}: module-level assignment to {tg.value.id}.{tg.attr} at line {n.lineno}; "
                                     f"test classes, the library and the template are not patched from test code")
        call = n.value if isinstance(n, ast.Expr) and isinstance(n.value, ast.Call) else None
        if call is not None and isinstance(call.func, ast.Name) and call.func.id in ("setattr", "delattr"):
            raise AssertionError(f"GEN_TEST_LIB: {path}: {call.func.id}() at module level (line {n.lineno}) is refused")
    for n in ast.walk(tree):
        tok = n.value if isinstance(n, ast.Constant) else n.attr if isinstance(n, ast.Attribute) else n.id if isinstance(n, ast.Name) else None
        assert tok != "COV_WITNESS", f"GEN_TEST_LIB: {path}: COV_WITNESS at line {n.lineno}; witnesses are issued by the template's finish() epilogue from fire-check results only"
    template_attrs = _template_attrs()

    def is_self_check(c):
        return isinstance(c.func, ast.Attribute) and c.func.attr == "check" and isinstance(c.func.value, ast.Name) and c.func.value.id == "self"

    READ_BUILTINS = {"len", "sorted", "list", "tuple", "enumerate", "zip", "sum", "any", "all", "min", "max", "set", "iter", "reversed", "str", "repr", "bool", "range"}
    helpers = {n.name for n in tree.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and not n.decorator_list}   # = helper_defs below: a decorated function is not a helper the test object may reach

    def check_escapes(body, obj_names, where):
        """`self` (or a helper parameter bound to the test) may only be read through attributes or passed to a module-level
        helper; binding it to a name, packing it, returning it, capturing it in a lambda, passing it to any other callee, or
        handing the verdict record to a callee (other than a read-only builtin) is refused; a Subscript target rooted at a
        template-owned attribute counts as an assignment."""
        parents = {}
        for node in ast.walk(body):
            for ch in ast.iter_child_nodes(node):
                parents[ch] = node
        for node in ast.walk(body):
            if isinstance(node, ast.Name) and node.id in obj_names and isinstance(node.ctx, ast.Load):
                par = parents.get(node)
                if isinstance(par, ast.Attribute) and par.value is node:
                    continue
                if isinstance(par, ast.Call) and node in par.args and isinstance(par.func, ast.Name) and par.func.id in helpers:
                    continue
                if isinstance(par, ast.Call) and par.args and par.args[0] is node and isinstance(par.func, ast.Name) and par.func.id in ("getattr", "setattr", "hasattr") \
                        and len(par.args) > 1 and isinstance(par.args[1], ast.Constant) and isinstance(par.args[1].value, str) and par.args[1].value not in template_attrs:
                    continue   # reflective access to the test's own cache attribute by a literal, non-template name
                if isinstance(par, ast.keyword) and isinstance(parents.get(par), ast.Call) and isinstance(parents[par].func, ast.Name) and parents[par].func.id in helpers:
                    continue
                raise AssertionError(f"GEN_TEST_LIB: {path}: {where}: the test object escapes as a bare name at line {node.lineno} (bound, packed, returned, captured or passed outside a module-level helper)")
            if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name) and node.value.id in obj_names and node.attr in RECORD_ATTRS - {"reports"}:
                par = parents.get(node)   # the report words are program observations a helper may read; the verdict record is not handed out
                if isinstance(par, ast.Call) and node in par.args and not (isinstance(par.func, ast.Name) and par.func.id in READ_BUILTINS):
                    raise AssertionError(f"GEN_TEST_LIB: {path}: {where}: the verdict record {node.value.id}.{node.attr} is passed to a callee at line {node.lineno}")
                if isinstance(par, ast.keyword):
                    raise AssertionError(f"GEN_TEST_LIB: {path}: {where}: the verdict record {node.value.id}.{node.attr} is passed to a callee at line {node.lineno}")
                if isinstance(par, ast.Lambda) or any(isinstance(p2, ast.Lambda) for p2 in _ancestors(node, parents)):
                    raise AssertionError(f"GEN_TEST_LIB: {path}: {where}: the verdict record {node.value.id}.{node.attr} is captured by a lambda at line {node.lineno}")
                if isinstance(par, (ast.NamedExpr, ast.Tuple, ast.List, ast.Return, ast.Yield)) or (isinstance(par, ast.Assign) and node is par.value):
                    raise AssertionError(f"GEN_TEST_LIB: {path}: {where}: the verdict record {node.value.id}.{node.attr} is bound to a name at line {node.lineno}")
            if isinstance(node, ast.Delete):
                for tg in node.targets:
                    root = tg
                    while isinstance(root, (ast.Subscript, ast.Attribute)) and not (isinstance(root, ast.Attribute) and isinstance(root.value, ast.Name) and root.value.id in obj_names):
                        root = root.value
                    if isinstance(root, ast.Attribute) and isinstance(root.value, ast.Name) and root.value.id in obj_names and root.attr in template_attrs:
                        raise AssertionError(f"GEN_TEST_LIB: {path}: {where}: del over {root.value.id}.{root.attr} at line {node.lineno}; template-owned names are read-only")
            if isinstance(node, (ast.Assign, ast.AugAssign, ast.AnnAssign)):
                for tg in (node.targets if isinstance(node, ast.Assign) else [node.target]):
                    root = tg
                    while isinstance(root, (ast.Subscript, ast.Attribute)) and not (isinstance(root, ast.Attribute) and isinstance(root.value, ast.Name) and root.value.id in obj_names):
                        root = root.value
                    if isinstance(tg, ast.Subscript) and isinstance(root, ast.Attribute) and isinstance(root.value, ast.Name) and root.value.id in obj_names and root.attr in template_attrs:
                        raise AssertionError(f"GEN_TEST_LIB: {path}: {where}: item assignment into {root.value.id}.{root.attr} at line {node.lineno}; template-owned names are read-only")

    def _ancestors(node, parents):
        out = []
        while node in parents:
            node = parents[node]; out.append(node)
        return out

    def owned(name):
        return name in template_attrs

    def local_methods(cls, seen=()):
        methods = [n for n in cls.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
        for b in cls.bases:
            name = base_name(cls, b)
            if name in top and name not in gentest_names and name not in seen:
                methods += local_methods(top[name], seen + (name,))
        return methods

    helper_defs = {n.name: n for n in tree.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and not n.decorator_list}   # the decorated cocotb entry takes the dut
    # parameters that stand for the test object: named test/self, read through a template-owned attribute, or bound to the
    # test object at a call site (helper(self, ...) from a method, helper(t) from another helper), to a fixpoint
    test_params = {name: {a.arg for a in fn.args.args + fn.args.kwonlyargs if a.arg in ("test", "self")
                          or any(isinstance(n, ast.Attribute) and isinstance(n.value, ast.Name) and n.value.id == a.arg and n.attr in template_attrs for n in ast.walk(fn))}
                   for name, fn in helper_defs.items()}
    changed = True
    while changed:
        changed = False
        for scope, names in [(m, {"self"}) for cls in tests for m in cls.body if isinstance(m, (ast.FunctionDef, ast.AsyncFunctionDef))] + \
                            [(fn, test_params[name]) for name, fn in helper_defs.items()]:
            for c in ast.walk(scope):
                if isinstance(c, ast.Call) and isinstance(c.func, ast.Name) and c.func.id in helper_defs:
                    callee = helper_defs[c.func.id]; pos = [a.arg for a in callee.args.args]
                    for i, a in enumerate(c.args):
                        if isinstance(a, ast.Name) and a.id in names and i < len(pos) and pos[i] not in test_params[c.func.id]:
                            test_params[c.func.id].add(pos[i]); changed = True
                    for k in c.keywords:
                        if isinstance(k.value, ast.Name) and k.value.id in names and k.arg and k.arg not in test_params[c.func.id]:
                            test_params[c.func.id].add(k.arg); changed = True
    for name, fn in helper_defs.items():
        params = test_params[name]
        check_escapes(fn, params, f"helper {fn.name}")
        for c in ast.walk(fn):
            for tg in rebind_targets(c):            # a template method rebound through any target form, tuple, starred, for or with included
                if isinstance(tg, ast.Attribute) and isinstance(tg.value, ast.Name) and tg.value.id in params and tg.attr in protected:
                    raise AssertionError(f"GEN_TEST_LIB: {path}: helper {fn.name} rebinds the template method {tg.value.id}.{tg.attr} on the instance at line {tg.lineno}; "
                                         f"a template method is overridden by no test")
            tgts = (c.targets if isinstance(c, ast.Assign) else [c.target] if isinstance(c, (ast.AugAssign, ast.AnnAssign)) else [])
            for tg in tgts:
                if isinstance(tg, ast.Attribute) and isinstance(tg.value, ast.Name) and tg.value.id in params and tg.attr in template_attrs:
                    raise AssertionError(f"GEN_TEST_LIB: {path}: helper {fn.name} assigns {tg.value.id}.{tg.attr} at line {c.lineno}; template-owned names are read-only")
                root, chain = tg, []                    # the same reach as the class-body rule: t.bridge.cov_witness = f inside a helper
                while isinstance(root, ast.Attribute):
                    chain.append(root.attr)
                    root = root.value
                if len(chain) > 1 and isinstance(root, ast.Name) and root.id in params and chain[-1] in template_attrs:
                    raise AssertionError(f"GEN_TEST_LIB: {path}: helper {fn.name} rebinds {root.id}.{'.'.join(reversed(chain))} at line {c.lineno}; "
                                         f"an attribute reached through a template-owned name is read-only for a test")
            if isinstance(c, ast.Call) and isinstance(c.func, ast.Attribute):
                chain, first = c.func.value, None
                while isinstance(chain, (ast.Attribute, ast.Subscript)):
                    first = chain.attr if isinstance(chain, ast.Attribute) else first
                    chain = chain.value
                if isinstance(chain, ast.Name) and chain.id in params and first in RECORD_ATTRS:
                    raise AssertionError(f"GEN_TEST_LIB: {path}: helper {fn.name} calls into {chain.id}.{first} at line {c.lineno}; the verdict record is read-only")
    checked = []
    for cls in tests:
        methods = local_methods(cls)
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
                for tg in rebind_targets(c):        # a template method rebound through any target form, tuple, starred, for or with included
                    if isinstance(tg, ast.Attribute) and isinstance(tg.value, ast.Name) and tg.value.id == "self" and tg.attr in protected:
                        raise AssertionError(f"GEN_TEST_LIB: {path}: class {cls.name} rebinds the template method self.{tg.attr} on the instance at line {tg.lineno}; "
                                             f"a template method is overridden by no test (F_OVERRIDE)")
                if isinstance(c, (ast.Assign, ast.AugAssign, ast.AnnAssign)):
                    for tg in (c.targets if isinstance(c, ast.Assign) else [c.target]):
                        if isinstance(tg, ast.Attribute) and isinstance(tg.value, ast.Name) and tg.value.id == "self" and owned(tg.attr):
                            raise AssertionError(f"GEN_TEST_LIB: {path}: class {cls.name} assigns self.{tg.attr} at line {c.lineno}; template-owned names are read-only for a test")
                        if isinstance(tg, ast.Attribute) and isinstance(tg.value, ast.Name) and resolve(tg.value.id) in guarded_modules:
                            raise AssertionError(f"GEN_TEST_LIB: {path}: class {cls.name} patches {tg.value.id}.{tg.attr} at line {c.lineno}")
                        # an attribute chain rooted at self (self.bridge.cov_witness = f) rebinds a template method behind a template-owned name
                        root, chain = tg, []
                        while isinstance(root, ast.Attribute):          # a subscript anywhere is the item-assignment rule's case
                            chain.append(root.attr)
                            root = root.value
                        if len(chain) > 1 and isinstance(root, ast.Name) and root.id == "self" and owned(chain[-1]):
                            raise AssertionError(f"GEN_TEST_LIB: {path}: class {cls.name} rebinds self.{'.'.join(reversed(chain))} at line {c.lineno}; "
                                                 f"an attribute reached through a template-owned name is read-only for a test")
                if isinstance(c, ast.Call):
                    f = c.func
                    if isinstance(f, ast.Attribute):
                        root = f.value
                        while isinstance(root, (ast.Attribute, ast.Subscript)):
                            root = root.value
                        chain = f.value
                        first = None
                        while isinstance(chain, (ast.Attribute, ast.Subscript)):
                            first = chain.attr if isinstance(chain, ast.Attribute) else first
                            chain = chain.value
                        if isinstance(chain, ast.Name) and chain.id == "self" and first in RECORD_ATTRS:
                            raise AssertionError(f"GEN_TEST_LIB: {path}: class {cls.name} calls into self.{first} at line {c.lineno}; the verdict record is read-only for a test")
                    if isinstance(f, ast.Name) and f.id in ("setattr", "delattr"):
                        raise AssertionError(f"GEN_TEST_LIB: {path}: class {cls.name} uses {f.id}() at line {c.lineno}")
        fire_tp = {m.name: _gm().tp_id_of_fire(m.name) for m in methods if m.name.startswith("fire_tp_")}
        by_name = {m.name: m for m in methods}
        called, todo, seen = set(), ["fire_check"], set()
        while todo:   # every fire_tp_* method is reached from fire_check through fire_* methods
            fn = todo.pop()
            if fn in seen or fn not in by_name:
                continue
            seen.add(fn)
            cs = {c.func.attr for c in ast.walk(by_name[fn]) if isinstance(c, ast.Call) and isinstance(c.func, ast.Attribute)
                  and isinstance(c.func.value, ast.Name) and c.func.value.id == "self"}
            called |= cs
            todo += [c for c in cs if c.startswith("fire_")]
        uncalled = sorted(n for n in fire_tp if n not in called)
        assert not uncalled, f"GEN_TEST_LIB: {path}: class {cls.name}: fire_tp method(s) {uncalled} never called from fire_check()"
        for m in methods:   # a check inside fire_tp_<item> names that item
            tp = fire_tp.get(m.name)
            if not tp:
                continue
            pre = "fire_tp_" + tp[3:].lower().replace("-", "_")
            for c in ast.walk(m):
                if isinstance(c, ast.Call) and is_self_check(c) and c.args:
                    w = c.args[0]
                    lit = w.value if isinstance(w, ast.Constant) else (w.values[0].value if isinstance(w, ast.JoinedStr) and w.values and isinstance(w.values[0], ast.Constant) else None)
                    assert lit is None or str(lit).startswith(pre), \
                        f"GEN_TEST_LIB: {path}: class {cls.name}: check '{lit}' inside {m.name} does not name its item ({pre}...)"
        for a in cls.body:   # a template method replaced by class-body assignment (finish = _f, check = lambda ...)
            if isinstance(a, (ast.Assign, ast.AnnAssign)):
                for tg in (a.targets if isinstance(a, ast.Assign) else [a.target]):
                    if isinstance(tg, ast.Name) and (tg.id in protected or tg.id in TEST_HOOKS or tg.id.startswith("fire_")):
                        raise AssertionError(f"GEN_TEST_LIB: {path}: class {cls.name} assigns method name {tg.id} in its body at line {a.lineno}")
        for m in methods:   # aliasing or reflective access to the test object
            for c in ast.walk(m):
                if isinstance(c, ast.Assign) and isinstance(c.value, ast.Attribute) and isinstance(c.value.value, ast.Name) and c.value.value.id == "self" and c.value.attr in RECORD_ATTRS - {"reports"}:   # a read alias of the report words is fine
                    raise AssertionError(f"GEN_TEST_LIB: {path}: class {cls.name} aliases self.{c.value.attr} at line {c.lineno}")
                if isinstance(c, ast.Call) and isinstance(c.func, ast.Name) and c.func.id in ("getattr", "setattr", "delattr", "hasattr", "vars", "type") \
                        and c.args and isinstance(c.args[0], ast.Name) and c.args[0].id == "self":
                    literal_own = (c.func.id in ("getattr", "setattr", "hasattr") and len(c.args) > 1 and isinstance(c.args[1], ast.Constant)
                                   and isinstance(c.args[1].value, str) and c.args[1].value not in template_attrs)
                    assert literal_own, f"GEN_TEST_LIB: {path}: class {cls.name} uses {c.func.id}(self, ...) at line {c.lineno}"
                if isinstance(c, ast.Attribute) and c.attr in ("__dict__", "__class__") and isinstance(c.value, ast.Name) and c.value.id == "self":
                    raise AssertionError(f"GEN_TEST_LIB: {path}: class {cls.name} touches self.{c.attr} at line {c.lineno}")
        for m in methods:
            check_escapes(m, {"self"}, f"class {cls.name}.{m.name}")
        attrs = {}
        for a in cls.body:
            if isinstance(a, ast.Assign):
                attrs.update({tg.id: a.value for tg in a.targets if isinstance(tg, ast.Name)})
            elif isinstance(a, ast.AnnAssign) and isinstance(a.target, ast.Name) and a.value is not None:
                attrs[a.target.id] = a.value
        lr = attrs.get("layers_required")
        if lr is not None:
            assert isinstance(lr, ast.Constant) and lr.value in (True, False), \
                f"GEN_TEST_LIB: {path}: class {cls.name}: layers_required must be a literal True or False (line {lr.lineno})"
        if isinstance(lr, ast.Constant) and lr.value is False:
            nm = attrs.get("name")
            test_name = nm.value if isinstance(nm, ast.Constant) else None
            entry = lookup(test_name) if test_name else None
            assert (entry is not None and entry.get("measured") is False) or cls.name in LAYERS_OPTOUT_ALLOWLIST, \
                (f"GEN_TEST_LIB: {path}: class {cls.name} sets layers_required = False without a testlist entry "
                 f"'{test_name}' carrying measured: false (a measured test takes its layers) and without an allowlist reason")
        nm = attrs.get("name")
        test_name = nm.value if isinstance(nm, ast.Constant) else None
        if test_name:
            nb_node = attrs.get("not_built")
            group = _gm().plan_group_of(test_name)
            if _gm().items_of_group(group, required=False):
                assert isinstance(nb_node, ast.Dict) and all(isinstance(k, ast.Constant) and isinstance(k.value, str) for k in nb_node.keys) \
                    and all(isinstance(v, ast.Constant) and isinstance(v.value, str) and v.value.strip() for v in nb_node.values), \
                    f"GEN_TEST_LIB: {path}: class {cls.name} needs a literal `not_built = {{'TP-...': 'reason'}}` (its plan group {group} has items)"
                _gm().check_items_two_sided(sorted(set(fire_tp.values()) - {None}), {k.value: v.value for k, v in zip(nb_node.keys, nb_node.values)},
                                            group, f"GEN_TEST_LIB: {path}: class {cls.name}")
        checked.append(cls.name)
    return checked


def check_test_module(path):
    """Structure rules, plus the file-level rule cocotb itself imposes.

    A module with no registered cocotb test compiles, passes every structural rule and simulates
    nothing: cocotb discovers no tests and the run reports time 0. The rule lives here rather than
    in check_test_source because it is a property of the FILE as cocotb loads it, and the source
    checker's own fixtures are minimal snippets with no entry point by design.
    """
    text = Path(path).read_text()
    checked = check_test_source(text, path)
    tree = ast.parse(text)
    reg = [n for n in ast.walk(tree) if isinstance(n, ast.AsyncFunctionDef)
           and any(isinstance(d, ast.Call) and isinstance(d.func, ast.Attribute) and d.func.attr == "test"
                   and isinstance(d.func.value, ast.Name) and d.func.value.id == "cocotb"
                   for d in n.decorator_list)]
    assert len(reg) == 1, (f"GEN_TEST_LIB: {path}: {len(reg)} @cocotb.test() entry point(s); a test module "
                           f"registers exactly one or cocotb discovers nothing and the run simulates nothing")
    for cls in [n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]:
        want = next((a.value.value for a in cls.body if isinstance(a, ast.Assign)
                     for tg in a.targets if isinstance(tg, ast.Name) and tg.id == "name"
                     and isinstance(a.value, ast.Constant)), None)
        if want and cls.name in checked:
            assert reg[0].name == want, \
                f"GEN_TEST_LIB: {path}: entry point {reg[0].name} does not match the class name attribute {want}"
    return checked


# Regime knobs whose events a program must be able to survive, by knob: a debug request needs a debug ROM in the DM window ("dbg"),
# an interrupt line or an internal NMI needs a returning handler ("irq"; the NMI is not masked by mstatus.MIE), an injected bus fault
# needs a trap handler ("exc": instruction/data access faults, an instruction integrity error). A knob absent here (latencies, the
# scramble key, program-side markers) needs nothing. INACTIVE_VALUE names the value under which a knob drives no event at all.
KNOB_HANDLER = {"knob_debug_req_regime": "dbg",
                "knob_irq_regime": "irq", "knob_irq_line_mix": "irq", "knob_irq_hold": "irq",
                "knob_imem_err_rate": "exc", "knob_dmem_err_rate": "exc", "knob_imem_intg_err_rate": "exc",
                "knob_dmem_intg_err_rate": "irq"}
INACTIVE_VALUE = {"knob_debug_req_regime": "none", "knob_irq_regime": "quiet", "knob_imem_err_rate": "none", "knob_dmem_err_rate": "none",
                  "knob_imem_intg_err_rate": "none", "knob_dmem_intg_err_rate": "none"}
NMI_LINE_MIX = "with_nmi"      # the one knob_irq_line_mix value that drives irq_nm
# the per-mille fault plusargs the bus agents honour outside the regime knobs; a nonzero value needs the same handler as the knob
RAW_FAULT_PLUSARGS = {"ibus_err_rate": "knob_imem_err_rate", "ibus_intg_err_rate": "knob_imem_intg_err_rate",
                      "dbus_err_rate": "knob_dmem_err_rate", "dbus_intg_err_rate": "knob_dmem_intg_err_rate"}
HANDLERS = tuple(sorted(set(KNOB_HANDLER.values())))
assert all(k in KNOB_CONSUMER for k in KNOB_HANDLER) and all(INACTIVE_VALUE[k] in PLUSARGS[k]["values"] for k in INACTIVE_VALUE) \
    and NMI_LINE_MIX in PLUSARGS["knob_irq_line_mix"]["values"] and all(r in PLUSARGS and k in KNOB_HANDLER for r, k in RAW_FAULT_PLUSARGS.items()), \
    "regime-handler rule: knob table changed under it"
# the converse: every irq / dbg consumer and every bus fault-injection knob of the table is mapped, and the defaults the NMI closure and
# the inactive values rely on hold (the regime quiet, the line mix not with_nmi, the debug regime none)
assert all(k in KNOB_HANDLER for k, c in KNOB_CONSUMER.items() if c in ("irq", "dbg") or (c == "bus" and "err_rate" in k)), \
    "regime-handler rule: a consumer knob of the table has no handler mapping"
assert PLUSARGS["knob_irq_regime"]["default"] == INACTIVE_VALUE["knob_irq_regime"] and PLUSARGS["knob_irq_line_mix"]["default"] != NMI_LINE_MIX \
    and PLUSARGS["knob_debug_req_regime"]["default"] == INACTIVE_VALUE["knob_debug_req_regime"], "regime-handler rule: knob defaults changed under it"


def regime_handler_violations(knobs, program_handlers, mie_stays_zero, values=None):
    """The regime knobs in play that a program with `program_handlers` cannot survive; [] when none. `knobs` are the
    knobs in play (a class's schedulable; at run time also the pinned knobs and the supplied schedule's); `values` maps a
    knob to the set of values it takes in the run (None = any value may be drawn, the structural form). A knob whose every
    value is its INACTIVE_VALUE needs nothing. mie_stays_zero exempts the irq knobs only while no NMI can be driven: an
    NMI escapes MIE, so knob_irq_regime (events) and knob_irq_line_mix (with_nmi) may not both be in play with active values."""
    knobs = list(dict.fromkeys(knobs))
    def vals(k):
        return set(values.get(k, ())) if values is not None else None
    def active(k):
        v = vals(k)
        return True if v is None or not v else any(x != INACTIVE_VALUE.get(k) for x in v)
    bad, nmi_said = [], False
    for k in knobs:
        need = KNOB_HANDLER.get(k)
        if need is None or need in program_handlers or not active(k):
            continue
        if need == "irq" and mie_stays_zero and k.startswith("knob_irq_"):
            events = "knob_irq_regime" in knobs and active("knob_irq_regime")
            mix = vals("knob_irq_line_mix")
            nmi_mix = "knob_irq_line_mix" in knobs and (mix is None or not mix or NMI_LINE_MIX in mix)
            if events and nmi_mix and not nmi_said:
                bad.append("knob_irq_regime with knob_irq_line_mix: mie_stays_zero exempts the irq knobs only while no NMI can be driven, "
                           f"but events flow and {NMI_LINE_MIX} is in play (irq_nm is not masked by MIE)")
                nmi_said = True
            continue
        bad.append(f"{k} needs a {need} handler the program does not declare"
                   + (" (or mie_stays_zero = True with no NMI in play)" if need == "irq" and k.startswith("knob_irq_") else ""))
    return bad


RULE_ATTRS = ("schedulable", "program_handlers", "mie_stays_zero")


def check_regime_handlers_source(source, path="<source>"):
    """Structural form of the regime-handler rule over a test module (the library self-test runs it on every committed test): every
    class with a `name` attribute is read by AST: `schedulable` a literal tuple of knob names (module-level constants and name
    elements resolved), `lib.TIMING_ONLY_KNOBS` or `GenTest.schedulable`; `program_handlers` a literal tuple drawn from HANDLERS;
    `mie_stays_zero` a literal True/False; absent attributes take the GenTest defaults (a base class's own value is not followed:
    a conservative refusal at worst, never an evasion). Refused as unreadable: any other value form, an annotated or tuple-target
    assignment of these names, and a decorated test class (a decorator may rewrite them; setup() is the run-time backstop).
    Returns the checked class names; refuses with the offending class, knob and missing declaration."""
    import ast
    tree = ast.parse(source, filename=str(path))
    from dv.auto_dv.tests import gen_test_template as _tpl
    consts = {n.targets[0].id: n.value for n in tree.body
              if isinstance(n, ast.Assign) and len(n.targets) == 1 and isinstance(n.targets[0], ast.Name)}

    def knob_names(node, seen=()):
        """A literal tuple of knob names, its elements or the whole tuple resolved through module-level constants; None otherwise."""
        if isinstance(node, ast.Name) and node.id in consts and node.id not in seen:
            return knob_names(consts[node.id], seen + (node.id,))
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            return (node.value,)
        if isinstance(node, ast.Tuple):
            parts = [knob_names(e, seen) for e in node.elts]
            return None if any(p is None for p in parts) else tuple(x for p in parts for x in p)
        return None

    def names_in(target):
        if isinstance(target, ast.Name):
            return {target.id}
        if isinstance(target, (ast.Tuple, ast.List)):
            return set().union(*(names_in(e) for e in target.elts))
        return set()

    checked = []
    for cls in tree.body:
        if not isinstance(cls, ast.ClassDef):
            continue
        attrs = {}
        for a in cls.body:
            if isinstance(a, ast.AnnAssign) and names_in(a.target) & set(RULE_ATTRS):
                raise AssertionError(f"GEN_TEST_LIB: {path}: class {cls.name}: {', '.join(sorted(names_in(a.target) & set(RULE_ATTRS)))} must be a plain assignment "
                                     f"(annotated at line {a.lineno}) so the regime-handler rule can read it")
            if isinstance(a, ast.Assign):
                if len(a.targets) == 1 and isinstance(a.targets[0], ast.Name):
                    attrs[a.targets[0].id] = a.value
                elif set().union(*(names_in(t) for t in a.targets)) & set(RULE_ATTRS):
                    raise AssertionError(f"GEN_TEST_LIB: {path}: class {cls.name}: {', '.join(sorted(set().union(*(names_in(t) for t in a.targets)) & set(RULE_ATTRS)))} "
                                         f"must be a plain assignment (tuple or chained target at line {a.lineno}) so the regime-handler rule can read it")
        for a in cls.body:
            if isinstance(a, ast.AugAssign) and names_in(a.target) & set(RULE_ATTRS):
                raise AssertionError(f"GEN_TEST_LIB: {path}: class {cls.name}: {', '.join(sorted(names_in(a.target) & set(RULE_ATTRS)))} must be a plain assignment "
                                     f"(augmented at line {a.lineno}) so the regime-handler rule can read it")
        if cls.keywords:
            raise AssertionError(f"GEN_TEST_LIB: {path}: class {cls.name} carries a class keyword (line {cls.lineno}; a metaclass may rewrite "
                                 f"{', '.join(RULE_ATTRS)} behind the regime-handler rule), so test classes and their bases take no class keywords (setup() re-checks at run time)")
        if "name" not in attrs:
            continue
        if cls.decorator_list:
            raise AssertionError(f"GEN_TEST_LIB: {path}: class {cls.name} carries a decorator (line {cls.decorator_list[0].lineno}); a decorator may rewrite "
                                 f"{', '.join(RULE_ATTRS)} behind the regime-handler rule, so test classes are undecorated (setup() re-checks at run time)")
        sched = attrs.get("schedulable")
        if sched is None:
            schedulable = tuple(_tpl.GenTest.schedulable)
        elif knob_names(sched) is not None and not isinstance(sched, ast.Constant):
            schedulable = knob_names(sched)
        elif isinstance(sched, ast.Attribute) and sched.attr == "TIMING_ONLY_KNOBS":
            schedulable = tuple(TIMING_ONLY_KNOBS)
        elif isinstance(sched, ast.Attribute) and sched.attr == "schedulable":
            schedulable = tuple(_tpl.GenTest.schedulable)
        else:
            raise AssertionError(f"GEN_TEST_LIB: {path}: class {cls.name}: schedulable must be a literal tuple of knob names, "
                                 f"lib.TIMING_ONLY_KNOBS or GenTest.schedulable (line {sched.lineno}) so the handler rule can read it")
        ph = attrs.get("program_handlers")
        if ph is None:
            handlers = tuple(_tpl.GenTest.program_handlers)
        elif isinstance(ph, ast.Tuple) and all(isinstance(e, ast.Constant) and e.value in HANDLERS for e in ph.elts):
            handlers = tuple(e.value for e in ph.elts)
        else:
            raise AssertionError(f"GEN_TEST_LIB: {path}: class {cls.name}: program_handlers must be a literal tuple drawn from {HANDLERS} (line {ph.lineno})")
        mz = attrs.get("mie_stays_zero")
        if mz is None:
            mie_zero = bool(_tpl.GenTest.mie_stays_zero)
        elif isinstance(mz, ast.Constant) and isinstance(mz.value, bool):
            mie_zero = mz.value
        else:
            raise AssertionError(f"GEN_TEST_LIB: {path}: class {cls.name}: mie_stays_zero must be a literal True or False (line {mz.lineno})")
        bad = regime_handler_violations(schedulable, handlers, mie_zero)
        assert not bad, f"GEN_TEST_LIB: {path}: class {cls.name} schedules a regime knob its program cannot survive: " + "; ".join(bad)
        checked.append(cls.name)
    return checked


def check_regime_handlers(path):
    return check_regime_handlers_source(Path(path).read_text(), path)


MMIO_MAP_H = Path(__file__).resolve().parent / "gen_programs" / "gen_mmio_map.h"
MMIO_MAP_H_KEYS = {"GEN_MM_SIG_ADDR": "sig_addr", "GEN_MM_IRQ_ACK_ADDR": "irq_ack_addr", "GEN_MM_EOT_ADDR": "eot_addr",
                   "GEN_MM_PHASE_MARK_ADDR": "phase_mark_addr", "GEN_MM_DM_HALT": "dm_halt", "GEN_MM_DM_EXCEPTION": "dm_exception"}


def check_mmio_map_header(path=MMIO_MAP_H, keys=None):
    """An assembler header carries exactly the rendered MEMORY_MAP values it names (keys: symbol -> MEMORY_MAP key;
    default the directed programs' gen_mmio_map.h)."""
    from dv.auto_dv.gen_tb.gen_knobs import MEMORY_MAP
    keys = keys or MMIO_MAP_H_KEYS
    got = dict(re.findall(r"^\.set (GEN_\w+), 0x([0-9a-fA-F]+)$", Path(path).read_text(), re.M))
    for sym, key in keys.items():
        assert sym in got, f"GEN_TEST_LIB: {path} lacks {sym}"
        assert int(got[sym], 16) == MEMORY_MAP[key], f"GEN_TEST_LIB: {path} {sym} = 0x{got[sym]} != MEMORY_MAP[{key}] 0x{MEMORY_MAP[key]:08x}"
    assert set(got) == set(keys), f"GEN_TEST_LIB: {path} carries unexpected symbols {sorted(set(got) - set(keys))}"
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


def fire_items(cls):
    """TP ids named by the class's fire_tp_<area>_<nnn> methods (inherited ones included): the items the test checks."""
    from dv.auto_dv.tests import gen_fcov_manifest as gm
    return sorted({i for i in (gm.tp_id_of_fire(n) for n in dir(cls) if n.startswith("fire_tp_")) if i})


def plan_bins(test_name, items, not_hit=()):
    """Bins the plan assigns to these items minus the test's bins_not_hit, derived by the manifest generator's own
    code so the test's declaration and the rendered file (gen_fcov_manifest.py --test-module) share one implementation."""
    from dv.auto_dv.tests import gen_fcov_manifest as gm
    return gm.plan_bins(test_name, items, tuple(not_hit))


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
    from dv.auto_dv.tests import gen_fcov_manifest as _gm
    seed = 12345
    names = list(TIMING_ONLY_KNOBS)   # the mechanics are tested independent of the consumer gate
    # CycleWaiters: the bridge has one cycle-threshold slot and every waiter shares it, so a near
    # target used to destroy a pending far one (a stimulus poll stole the schedule runner's c11664
    # boundary and applied a phase group at cycle 77). Two concurrent waiters, near and far:
    w = CycleWaiters()
    w.add(11664, "runner")
    w.add(85, "poll")
    assert w.armed_target() == 85, f"CycleWaiters arms the earliest, not {w.armed_target()}"
    woken = w.on_hit(85)
    assert "poll" in woken, "the near waiter must wake at its own target"
    assert "runner" not in woken, "the far waiter must NOT wake at the near waiter's hit"
    assert w.armed_target() == 11664, "the slot re-arms with the next earliest after a hit"
    assert "runner" in w.on_hit(11664), "the far waiter must wake at its own target"
    assert len(w) == 0 and w.armed_target() is None, "a woken waiter is dropped"
    w2 = CycleWaiters()
    w2.add(50, "a"); w2.add(60, "b")
    assert sorted(w2.on_hit(70)) == ["a", "b"], "a hit past several targets wakes all of them"
    w3 = CycleWaiters()
    k = object(); w3.add(9, k); w3.drop(k)
    assert len(w3) == 0 and w3.armed_target() is None, "a waiter that gave up is removed"
    # each waiter keeps its OWN budget: one whose target lies past the run's end times out alone,
    # and dropping it disturbs neither the others nor the service
    w4 = CycleWaiters()
    near, far = object(), object()
    w4.add(85, near); w4.add(10 ** 9, far)
    w4.drop(far)
    assert len(w4) == 1 and w4.armed_target() == 85, "dropping the far waiter leaves the near one armed"
    assert w4.on_hit(85) == [near], "the near waiter still wakes after the far one gave up"
    # an arm costs that cycle its compare, so only a new earliest target may arm; the rule the
    # template used, arming on every add, is the red here
    w5 = CycleWaiters()
    served = [w5.add_arms(t, object()) for t in (500, 900, 200)]
    naive = [True, True, True]
    assert served == [True, False, True], f"add_arms re-arms only for a nearer target, got {served}"
    assert served != naive, "arming on every add re-arms for a target the slot already carries"
    assert w5.armed_target() == 200, "the earliest of the three targets is the armed one"
    # program_min_retired: the image carries the number its generator computed and the caller's plan
    # recomputes it, so the two are equal by construction and an ordering cannot see a program and a
    # checker that came from different generator versions
    _addr = 0x80000100
    _img = type("_Img", (), {"sidecar": {"symbols": {"gen_min_retired": hex(_addr)}}, "words": {_addr // 4: 3332}})()
    assert program_min_retired(_img) == 3332, "no plan given: the floor is the image's own word"
    assert program_min_retired(_img, 3332) == 3332, "a matched plan passes"
    _caught = ""
    try:
        program_min_retired(_img, 3065)
    except AssertionError as _exc:
        _caught = str(_exc)
    assert "different generator versions" in _caught, f"a mismatched plan was accepted or raised {_caught!r}"
    _rv = type("_Img", (), {"sidecar": {"test": "gen_rand_smoke", "symbols": {}}, "words": {}})()
    assert program_min_retired(_rv, 1) == riscv_dv_instr_cnt("gen_rand_smoke"), \
        "a riscv-dv entry is exempt: its floor is an instruction count, not a plan value"
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
    # test-module structure check: the committed tests pass; every red source below is refused, and the forms they cover are
    # exactly REFUSED_FORMS, which the API doc must list verbatim
    proved = set()
    tests = [f for f in sorted(here.glob("gen_test_*.py")) if f.name not in ("gen_test_lib.py", "gen_test_template.py")]
    for f in tests:
        assert check_test_module(f), f"{f}: no GenTest subclass found"
        assert check_regime_handlers(f), f"{f}: no test class for the regime-handler rule"
    # regime-handler rule: red sources refused, green sources accepted (the check is structural, outside the frozen REFUSED_FORMS)
    rh_base = "from dv.auto_dv.tests.gen_test_template import GenTest\nclass T(GenTest):\n    name = 'gen_test_x'\n"
    rh_tail = "    def fire_check(self):\n        self.check('a', self.retired() > 0, 'x')\n"
    for red, why in ((rh_base + "    schedulable = ('knob_imem_gnt_delay', 'knob_debug_req_regime')\n" + rh_tail, "needs a dbg handler"),
                     (rh_base + "    schedulable = ('knob_irq_line_mix',)\n" + rh_tail, "needs a irq handler"),
                     (rh_base + "    schedulable = ('knob_irq_regime',)\n    mie_stays_zero = False\n" + rh_tail, "needs a irq handler"),
                     (rh_base + "    schedulable = ('knob_irq_regime', 'knob_irq_line_mix')\n    mie_stays_zero = True\n" + rh_tail, "with_nmi is in play"),
                     (rh_base + "    schedulable = ('knob_dmem_intg_err_rate',)\n    mie_stays_zero = True\n" + rh_tail, "needs a irq handler"),
                     (rh_base + "    schedulable = ('knob_imem_err_rate',)\n" + rh_tail, "needs a exc handler"),
                     (rh_base + "    schedulable = ('knob_debug_req_regime',)\n    program_handlers = HANDLERS\n" + rh_tail, "program_handlers must be a literal"),
                     (rh_base + "    schedulable = ('knob_irq_regime',)\n    mie_stays_zero = FLAG\n" + rh_tail, "literal True or False"),
                     (rh_base + "    schedulable = KNOBS\n" + rh_tail, "schedulable must be a literal"),
                     (rh_base + "    schedulable: tuple = ('knob_imem_gnt_delay',)\n" + rh_tail, "plain assignment"),
                     (rh_base + "    a, schedulable = 1, ('knob_imem_gnt_delay',)\n" + rh_tail, "plain assignment"),
                     (rh_base + "    schedulable = ('knob_imem_gnt_delay',)\n    schedulable += ('knob_debug_req_regime',)\n" + rh_tail, "plain assignment"),
                     ("from abc import ABCMeta\nfrom dv.auto_dv.tests.gen_test_template import GenTest\nclass T(GenTest, metaclass=ABCMeta):\n    name = 'gen_test_x'\n    schedulable = lib.TIMING_ONLY_KNOBS\n" + rh_tail, "class keyword"),
                     ("from abc import ABCMeta\nfrom dv.auto_dv.tests.gen_test_template import GenTest\nclass B(GenTest, metaclass=ABCMeta):\n    pass\nclass T(B):\n    name = 'gen_test_x'\n    schedulable = lib.TIMING_ONLY_KNOBS\n" + rh_tail, "class keyword"),
                     ("from dv.auto_dv.tests.gen_test_template import GenTest\ndef deco(c):\n    return c\n@deco\nclass T(GenTest):\n    name = 'gen_test_x'\n    schedulable = lib.TIMING_ONLY_KNOBS\n" + rh_tail, "carries a decorator"),
                     (rh_base + rh_tail, "needs a dbg handler")):          # the template default schedules every regime knob
        try:
            check_regime_handlers_source(red, "<rh-red>")
            raise AssertionError(f"regime-handler rule accepted a red source ({why})")
        except AssertionError as exc:
            assert why in str(exc), f"regime-handler rule: unexpected message for ({why}): {exc}"
    for green in (rh_base + "    schedulable = ('knob_irq_regime', 'knob_irq_hold')\n    mie_stays_zero = True\n" + rh_tail,
                  rh_base + "    schedulable = ('knob_irq_line_mix',)\n    mie_stays_zero = True\n" + rh_tail,
                  rh_base + "    schedulable = ('knob_debug_req_regime', 'knob_irq_regime', 'knob_irq_line_mix')\n    program_handlers = ('dbg', 'irq')\n" + rh_tail,
                  rh_base + "    schedulable = ('knob_imem_err_rate', 'knob_dmem_intg_err_rate')\n    program_handlers = ('exc', 'irq')\n" + rh_tail,
                  rh_base + "    schedulable = lib.TIMING_ONLY_KNOBS\n" + rh_tail,
                  "K = 'knob_scr_key_delay'\nKN = ('knob_imem_gnt_delay', K)\n" + rh_base + "    schedulable = KN\n" + rh_tail,
                  rh_base + "    program_handlers = ('dbg', 'exc', 'irq')\n" + rh_tail):
        assert check_regime_handlers_source(green, "<rh-green>") == ["T"]
    # the values-aware form: an inactive value needs nothing; the NMI hole needs both events and with_nmi in play
    both = ("knob_irq_regime", "knob_irq_line_mix")
    assert regime_handler_violations(("knob_debug_req_regime",), (), True) and not regime_handler_violations(("knob_irq_hold",), (), True)
    assert not regime_handler_violations(("knob_debug_req_regime",), (), False, {"knob_debug_req_regime": {"none"}})
    assert regime_handler_violations(("knob_debug_req_regime",), (), False, {"knob_debug_req_regime": {"storm"}})
    assert not regime_handler_violations(both, (), True, {"knob_irq_regime": {"quiet"}, "knob_irq_line_mix": {"with_nmi"}})
    assert not regime_handler_violations(both, (), True, {"knob_irq_regime": {"storm"}, "knob_irq_line_mix": {"single", "multi"}})
    assert regime_handler_violations(both, (), True, {"knob_irq_regime": {"storm"}, "knob_irq_line_mix": {"single", "with_nmi"}})
    assert not regime_handler_violations(both, ("irq",), True, {"knob_irq_regime": {"storm"}, "knob_irq_line_mix": {"with_nmi"}})
    base = "from dv.auto_dv.tests.gen_test_template import GenTest\nclass T(GenTest):\n    name = 'gen_test_x'\n"
    for form, red, why in ((F_OVERRIDE, base + "    def fire_check(self):\n        self.check('a', self.retired() > 0, 'x')\n    async def finish(self):\n        pass\n", "overrides"),
                           (F_LITERAL, base + "    def fire_check(self):\n        self.check('a', True, 'x')\n", "literal"),
                           (F_NOCHECK, base + "    def fire_check(self):\n        pass\n", "never calls")):
        accepted = False
        try:
            check_test_source(red, "<red>")
            accepted = True
        except AssertionError as exc:
            assert why in str(exc), (why, exc)
        assert not accepted, f"red source ({why}) accepted"
        proved.add(form)
    assert check_test_source(base + "    def fire_check(self):\n        self.fire_tp_x_001()\n    def fire_tp_x_001(self):\n        self.check('fire_tp_x_001', self.retired() > 0, 'x')\n") == ["T"]
    # parser: the automatic form is read and a commented-out test names no knob
    with tempfile.NamedTemporaryFile("w", suffix=".sv", delete=False) as tf:
        tf.write('function automatic void apply_knob(int id, int idx);\n  // if (name == "knob_scr_key_delay") ok = 1;\n'
                 '  /* name == "knob_dmem_gnt_delay" */\n  if (name == "knob_imem_gnt_delay") ok = 1;\nendfunction'); tfp = Path(tf.name)
    try:
        assert consumed_knobs_from_sv(tfp) == ("knob_imem_gnt_delay",), consumed_knobs_from_sv(tfp)
    finally:
        os.unlink(tfp)
    # structure check, second set: aliases, module-level writes, nesting, the witness command, the layers opt-out
    good = "    def fire_check(self):\n        self.fire_tp_x_001()\n    def fire_tp_x_001(self):\n        self.check('fire_tp_x_001', self.retired() > 0, 'x')\n"
    imp = "from dv.auto_dv.tests.gen_test_template import GenTest\n"
    # the alias of a template-owned attribute and a helper given that attribute are shapes the lint does not reach (the API doc lists
    # them); the SV ledger catches the write
    assert check_test_source(imp + "class T(GenTest):\n    name = 'gen_test_x'\n    async def stimulus(self):\n        b = self.bridge\n        b.cov_witness = None\n" + good) == ["T"]
    assert check_test_source(imp + "def _h(b):\n    b.cov_witness = None\nclass T(GenTest):\n    name = 'gen_test_x'\n    async def stimulus(self):\n        _h(self.bridge)\n" + good) == ["T"]
    entries = {"gen_test_x": {"name": "gen_test_x", "measured": False}, "gen_test_m": {"name": "gen_test_m", "measured": True}}
    look = entries.get
    for form, red, why in ((F_OVERRIDE, imp + "Base = GenTest\nclass T(Base):\n    name = 'gen_test_x'\n" + good + "    async def finish(self):\n        pass\n", "overrides"),
                           (F_PATCH, imp + "class T(GenTest):\n    name = 'gen_test_x'\n" + good + "def _f(self):\n    pass\nT.finish = _f\n", "module-level assignment"),
                           (F_PATCH, imp + "class T(GenTest):\n    name = 'gen_test_x'\n" + good + "setattr(T, 'finish', None)\n", "setattr"),
                           (F_NESTED, imp + "def mk():\n    class T(GenTest):\n        name = 'gen_test_x'\n" + good.replace("\n    ", "\n        ").replace("    def", "        def", 1) + "    return T\n", "inside a function"),
                           (F_WITNESS, imp + "class T(GenTest):\n    name = 'gen_test_x'\n    async def stimulus(self):\n        await self.cmd('COV_WITNESS', (1, 0, 0, 0))\n" + good, "COV_WITNESS"),
                           (F_CYCLE, imp + "class T(GenTest):\n    name = 'gen_test_x'\n    async def stimulus(self):\n        self.check('b', self.retired() > 0, 'x', cycle_clause_true=True)\n" + good, "cycle_clause_true outside"),
                           (F_LAYERS, imp + "class T(GenTest):\n    name = 'gen_test_m'\n    layers_required = False\n" + good, "measured: false"),
                           (F_LAYERS, imp + "class T(GenTest):\n    name = 'gen_test_none'\n    layers_required = False\n" + good, "measured: false")):
        accepted = False
        try:
            check_test_source(red, "<red>", entry_lookup=look)
            accepted = True
        except AssertionError as exc:
            assert why in str(exc), (why, exc)
        assert not accepted, f"red source ({why}) accepted"
        proved.add(form)
    assert check_test_source(imp + "class T(GenTest):\n    name = 'gen_test_x'\n    layers_required = False\n" + good, "<green>", entry_lookup=look) == ["T"]
    assert check_test_source(imp + "class T(GenTest):\n    name = 'gen_test_x'\n    def fire_check(self):\n        self.fire_tp_x_001()\n"
                             "    def fire_tp_x_001(self):\n        self.check('fire_tp_x_001', self.retired() > 0, 'x', cycle_clause_true=self.retired() > 1)\n", "<green>") == ["T"]
    assert tp_id_of("fire_tp_csr_001") == "TP-CSR-001" and tp_id_of("fire_tp_bit_016_gorci") == "TP-BIT-016"
    # structure check, third set (retention review): import alias, base expression, imported base, mixin bypass,
    # writes to template-owned names, patching the library, non-literal layers_required
    for form, red, why in ((F_OVERRIDE, f"from {TEMPLATE_MODULE} import GenTest as G\nclass T(G):\n    name = 'gen_test_x'\n" + good + "    async def finish(self):\n        pass\n", "overrides"),
                           (F_BASE, imp + "def mk():\n    return GenTest\nclass T(mk()):\n    name = 'gen_test_x'\n" + good, "unresolvable base"),
                           (F_BASE, imp + "from somewhere import Mixin\nclass T(Mixin, GenTest):\n    name = 'gen_test_x'\n" + good, "unknown or imported base"),
                           (F_OVERRIDE, imp + "class M:\n    async def finish(self):\n        pass\nclass T(M, GenTest):\n    name = 'gen_test_x'\n" + good, "overrides"),
                           (F_RECORD, imp + "class T(GenTest):\n    name = 'gen_test_x'\n    async def stimulus(self):\n        self.results.append(None)\n" + good, "calls into self.results"),
                           (F_ASSIGN, imp + "class T(GenTest):\n    name = 'gen_test_x'\n    async def stimulus(self):\n        self._results = []\n" + good, "assigns self._results"),
                           (F_ASSIGN, imp + "class T(GenTest):\n    name = 'gen_test_x'\n    async def stimulus(self):\n        self.witness_ids = ('TP-X-001',)\n" + good, "assigns self.witness_ids"),
                           (F_PATCH, imp + "from dv.auto_dv.tests import gen_test_lib as lib\nlib.WITNESS_IDS = {}\nclass T(GenTest):\n    name = 'gen_test_x'\n" + good, "module-level assignment to lib.WITNESS_IDS"),
                           (F_INTROSPECT, imp + "class T(GenTest):\n    name = 'gen_test_x'\n    async def stimulus(self):\n        setattr(self, 'checks', 9)\n" + good, "setattr"),
                           (F_LAYERS, imp + "FLAG = False\nclass T(GenTest):\n    name = 'gen_test_x'\n    layers_required = FLAG\n" + good, "literal True or False")):
        accepted = False
        try:
            check_test_source(red, "<red>", entry_lookup=look)
            accepted = True
        except AssertionError as exc:
            assert why in str(exc), (why, exc)
        assert not accepted, f"red source ({why}) accepted"
        proved.add(form)
    for form, red, why in ((F_OVERRIDE, imp + "def _ok(self):\n    pass\nclass T(GenTest):\n    name = 'gen_test_x'\n    finish = _ok\n" + good, "assigns method name finish"),
                           (F_OVERRIDE, imp + "async def _f(tp, g, timeout_cycles=200):\n    return 0\nclass T(GenTest):\n    name = 'gen_test_x'\n    async def stimulus(self):\n        self.bridge.cov_witness = _f\n" + good, "rebinds self.bridge.cov_witness"),
                           (F_OVERRIDE, imp + "async def _f(*a, **k):\n    return 0\nclass T(GenTest):\n    name = 'gen_test_x'\n    async def stimulus(self):\n        self.cmd = _f\n" + good, "rebinds the template method self.cmd"),
                           (F_OVERRIDE, imp + "async def _f(*a, **k):\n    return 0\nclass T(GenTest):\n    name = 'gen_test_x'\n    async def stimulus(self):\n        self.cmd, x = _f, 1\n" + good, "rebinds the template method self.cmd"),
                           (F_OVERRIDE, imp + "async def _f(*a, **k):\n    return 0\nclass T(GenTest):\n    name = 'gen_test_x'\n    async def stimulus(self):\n        *self.cmd, = (_f,)\n" + good, "rebinds the template method self.cmd"),
                           (F_OVERRIDE, imp + "async def _f(*a, **k):\n    return 0\nclass T(GenTest):\n    name = 'gen_test_x'\n    async def stimulus(self):\n        for self.cmd in (_f,):\n            pass\n" + good, "rebinds the template method self.cmd"),
                           (F_OVERRIDE, imp + "async def _f(*a, **k):\n    return 0\nclass T(GenTest):\n    name = 'gen_test_x'\n    async def stimulus(self):\n        with open('p') as self.cmd:\n            pass\n" + good, "rebinds the template method self.cmd"),
                           (F_OVERRIDE, imp + "async def _f(*a, **k):\n    return 0\nclass T(GenTest):\n    name = 'gen_test_x'\n    async def stimulus(self):\n        [0 for self.cmd in (_f,)]\n" + good, "rebinds the template method self.cmd"),
                           (F_OVERRIDE, imp + "async def _f(*a):\n    return 0\nclass T(GenTest):\n    name = 'gen_test_x'\n    async def stimulus(self):\n        self.bridge.h.b = _f\n" + good, "rebinds self.bridge.h.b"),
                           (F_RECORD, imp + "class T(GenTest):\n    name = 'gen_test_x'\n    async def stimulus(self):\n        rs = self._results\n" + good, "aliases self._results"),
                           (F_INTROSPECT, imp + "class T(GenTest):\n    name = 'gen_test_x'\n    async def stimulus(self):\n        getattr(self, '_results').append(1)\n" + good, "uses getattr(self"),
                           (F_INTROSPECT, imp + "class T(GenTest):\n    name = 'gen_test_x'\n    async def stimulus(self):\n        self.__dict__['failures'] = []\n" + good, "touches self.__dict__"),
                           (F_INTROSPECT, imp + "class T(GenTest):\n    name = 'gen_test_x'\n    async def stimulus(self):\n        type(self).finish = None\n" + good, "uses type(self"),
                           (F_HELPER, imp + "async def _f(*a):\n    return 0\ndef _h(t):\n    t.bridge.cov_witness = _f\nclass T(GenTest):\n    name = 'gen_test_x'\n    async def stimulus(self):\n        _h(self)\n" + good, "rebinds t.bridge.cov_witness"),
                           (F_HELPER, imp + "async def _f(*a, **k):\n    return 0\ndef _h(t):\n    t.cmd = _f\nclass T(GenTest):\n    name = 'gen_test_x'\n    async def stimulus(self):\n        _h(self)\n" + good, "rebinds the template method t.cmd"),
                           (F_HELPER, imp + "async def _f(*a, **k):\n    return 0\ndef _h(t):\n    t.cmd, x = _f, 1\nclass T(GenTest):\n    name = 'gen_test_x'\n    async def stimulus(self):\n        _h(self)\n" + good, "rebinds the template method t.cmd"),
                           (F_HELPER, imp + "async def _f(*a, **k):\n    return 0\ndef _h(t):\n    for t.cmd in (_f,):\n        pass\nclass T(GenTest):\n    name = 'gen_test_x'\n    async def stimulus(self):\n        _h(self)\n" + good, "rebinds the template method t.cmd"),
                           (F_ESCAPE, imp + "def deco(f):\n    return f\n@deco\ndef _h(t):\n    t.bridge = None\nclass T(GenTest):\n    name = 'gen_test_x'\n    async def stimulus(self):\n        _h(self)\n" + good, "escapes as a bare name"),
                           (F_HELPER, imp + "def _forge(t):\n    t._results.append(1)\nclass T(GenTest):\n    name = 'gen_test_x'\n    async def stimulus(self):\n        _forge(self)\n" + good, "helper _forge calls into t._results"),
                           (F_HELPER, imp + "def _forge(t):\n    t.failures = []\nclass T(GenTest):\n    name = 'gen_test_x'\n" + good, "helper _forge assigns t.failures")):
        accepted = False
        try:
            check_test_source(red, "<red>", entry_lookup=look)
            accepted = True
        except AssertionError as exc:
            assert why in str(exc), (why, exc)
        assert not accepted, f"red source ({why}) accepted"
        proved.add(form)
    for form, red, why in ((F_ESCAPE, imp + "class T(GenTest):\n    name = 'gen_test_x'\n    async def stimulus(self):\n        s = self\n" + good, "escapes as a bare name"),
                           (F_ESCAPE, imp + "class T(GenTest):\n    name = 'gen_test_x'\n    async def stimulus(self):\n        for s in (self,):\n            pass\n" + good, "escapes as a bare name"),
                           (F_RECORD, imp + "class T(GenTest):\n    name = 'gen_test_x'\n    async def stimulus(self):\n        (rs := self._results).clear()\n" + good, "bound to a name"),
                           (F_RECORD, imp + "class T(GenTest):\n    name = 'gen_test_x'\n    async def stimulus(self):\n        rs, = (self._results,)\n" + good, "bound to a name"),
                           (F_RECORD, imp + "class T(GenTest):\n    name = 'gen_test_x'\n    async def stimulus(self):\n        list.append(self._results, 1)\n" + good, "passed to a callee"),
                           (F_RECORD, imp + "class T(GenTest):\n    name = 'gen_test_x'\n    async def stimulus(self):\n        f = lambda: self._results\n" + good, "captured by a lambda"),
                           (F_RECORD, imp + "class T(GenTest):\n    name = 'gen_test_x'\n    async def stimulus(self):\n        self.failures[:] = []\n" + good, "item assignment into self.failures"),
                           (F_RECORD, imp + "class T(GenTest):\n    name = 'gen_test_x'\n    async def stimulus(self):\n        del self.failures[:]\n" + good, "del over self.failures"),
                           (F_ESCAPE, imp + "import x\nclass T(GenTest):\n    name = 'gen_test_x'\n    async def stimulus(self):\n        x.forge(t=self)\n" + good, "escapes as a bare name"),
                           (F_HELPER, imp + "def _h(t):\n    u = t\n    u.failures = []\nclass T(GenTest):\n    name = 'gen_test_x'\n    async def stimulus(self):\n        _h(self)\n" + good, "escapes as a bare name")):
        accepted = False
        try:
            check_test_source(red, "<red>", entry_lookup=look)
            accepted = True
        except AssertionError as exc:
            assert why in str(exc), (why, exc)
        assert not accepted, f"red source ({why}) accepted"
        proved.add(form)
    assert check_test_source(imp + "def _cmp(t, k):\n    return len(t.reports) > k\nclass T(GenTest):\n    name = 'gen_test_x'\n    def fire_check(self):\n        self.fire_tp_x_001()\n    def fire_tp_x_001(self):\n        self.check('fire_tp_x_001', _cmp(self, 0), 'x')\n", "<green>") == ["T"]
    assert check_test_source(imp + "class T(GenTest):\n    name = 'gen_test_x'\n    layers_required: bool = False\n" + good, "<green>", entry_lookup=look) == ["T"]
    assert check_test_source(imp + "class Mix:\n    def fire_tp_x_002(self):\n        self.check('fire_tp_x_002', self.retired() > 1, 'y')\nclass T(Mix, GenTest):\n    name = 'gen_test_x'\n" + good.replace("self.fire_tp_x_001()", "self.fire_tp_x_001(); self.fire_tp_x_002()"), "<green>") == ["T"]
    # rule (f) keys on the marker token; the plan's witness CSV must agree row by row
    import csv
    tps = _gm.tp_blocks()
    with open(_gm.DOCS / "gen_trace_witness_ids.csv", newline="") as f:
        wrows = list(csv.DictReader(f))
    assert wrows, "witness CSV empty"
    for r in wrows:
        if r["tp_item"] in tps:
            assert (r["marked"] == "1") == (_gm.CYCLE_CLAUSE_TOKEN in tps[r["tp_item"]]), f"witness CSV disagrees with the marker on {r['tp_item']}"
    # every program generator runs as a script with no PYTHONPATH from the clone root, as the flow runs it
    import os, subprocess
    env = {k: v for k, v in os.environ.items() if k not in ("PYTHONPATH", STAGED_ENTRIES_ENV)}
    with tempfile.TemporaryDirectory() as td:
        for gen in sorted((here / "gen_programs").glob("gen_*_prog.py")):
            r = subprocess.run([sys.executable, str(gen), "--seed", "1", "--out", f"{td}/{gen.stem}.S"], cwd=REPO_ROOT, env=env,
                               capture_output=True, text=True, timeout=120)
            assert r.returncode == 0, f"{gen.name} fails as a flow-style script: {(r.stderr.strip().splitlines() or ['?'])[-1][:160]}"
    # every red entry of a test module here: red_expect must match the harness line synthesized (fire_fail_line) from a check name
    # the module records, as the flow's regex meets it (a boundary after a suffixed id fails here too); and the retained pinned-red
    # log must pass the flow's own rule (gen_flow_util.red_signature_check): present, harness line matched; stale evidence is
    # reported until T-153 makes RED-OK mandatory
    import yaml as _yaml
    sys.path.insert(0, str(REPO_ROOT / "dv/auto_dv/flow"))
    import gen_flow_util as _fu
    import gen_flow_const as _fc
    assert len(_JOB_ENV_SET) == 1 and FLOW_RUN_ENV in _fc.JOB_ENV_SET
    entries = (_yaml.safe_load(FLOW_TESTLIST.read_text()) or {}).get("tests") or []
    staged = os.environ.get(STAGED_ENTRIES_ENV)
    if staged and Path(staged).is_file():
        entries += (_yaml.safe_load(Path(staged).read_text()) or {}).get("tests") or []
    checked_reds = 0
    for e in entries:
        modname = e.get("cocotb_module") or ""
        if not e.get("red_fixture") or not modname.startswith("dv.auto_dv.tests."):
            continue
        rx = e.get("red_expect") or ""
        mod = here / (modname.split(".")[-1] + ".py")
        assert rx and mod.exists(), f"red entry {e['name']}: red_expect {rx!r}, module {mod.name} {'present' if mod.exists() else 'missing'}"
        src = mod.read_text()
        tname = re.search(r"^\s+name = ['\"](gen_test_[a-z0-9_]+)['\"]", src, re.M).group(1)
        r = _fu.red_signature_check(e)
        assert r is not None, f"red entry {e['name']}: no retained pinned-red log under {'/'.join(_fc.RED_LOG_DIR_REL)}"
        # recorded check names: the literal ones in the source plus every GEN_TEST_FIRE name the retained pinned-red run recorded
        names = set(re.findall(r"self\.check\(\s*['\"](fire_[a-z0-9_]+)['\"]", src))
        names |= set(re.findall(r"GEN_TEST_FIRE (fire_[a-z0-9_]+) ok=", Path(r["log"]).read_text(errors="replace")))
        assert names, f"red entry {e['name']}: {mod.name} records no check name the self-test can see"
        assert any(re.search(rx, fire_fail_line(tname, [f"{n}: detail"])) for n in sorted(names)), \
            f"red entry {e['name']}: red_expect {rx!r} matches no harness line synthesized from the recorded check names {sorted(names)}"
        assert r["refuse"] is None, f"red entry {e['name']}: {r['refuse']} ({r['log']})"
        if r["stale_evidence"]:
            print(f"GEN_TEST_LIB notice: {e['name']}: retained pinned-red log is stale evidence ({r['reason'][:120]})", file=sys.stderr)
        checked_reds += 1
    assert checked_reds, "no red entry of a test module here was checked"
    # the rule's own red: over a fixed name list, a boundary form after a suffixed id matches no synthesized line while the
    # (?!\d) form does, and a longer id is rejected by both
    names_fixed = ["fire_tp_bit_014_ops", "fire_tp_bit_014_pattern", "fire_tp_bit_0140"]
    lines_fixed = [fire_fail_line("gen_test_x", [f"{n}: detail"]) for n in names_fixed[:2]]
    assert not any(re.search(r"\bfire_tp_bit_014\b", l) for l in lines_fixed), "boundary form accepted against suffixed check names"
    assert all(re.search(r"\bfire_tp_bit_014(?!\d)", l) for l in lines_fixed), "(?!\\d) form must match suffixed check names"
    assert not re.search(r"\bfire_tp_bit_014(?!\d)", fire_fail_line("gen_test_x", [f"{names_fixed[2]}: detail"])), "longer id accepted"
    # the fixture header re-types the EOT address: it must equal the rendered map too
    assert check_mmio_map_header(here / "gen_fixtures" / "gen_report_fixture_map.h", {"GEN_EOT_ADDR": "eot_addr"})
    # manifest cross-check: declared == rendered for every committed manifest; stale and missing fail loud
    for f in tests:   # every committed test's fire_tp_* items render exactly its committed manifest (or it has none)
        tn = f.stem
        items, not_built, group = _gm.module_items(f)
        not_hit = _gm.module_items.last_not_hit
        _gm.check_items_two_sided(items, not_built, group, str(f))
        declared = plan_bins(tn, items, not_hit)
        assert check_manifest_matches(tn, declared) or not declared, f"{tn}: {len(declared)} declared, manifest {load_manifest_bins(tn)}"
        if declared:   # and the committed file is byte-for-byte the current rendering (header lines included)
            text = _gm.build(tn, items, not_built, not_hit)[0]
            assert (FCOV_HOME / f"{tn}.fcov.yaml").read_text() == text, f"{tn}: manifest text stale (re-render with --test-module)"
    for mf in sorted(FCOV_HOME.glob("gen_test_*.fcov.yaml")):   # and every committed manifest belongs to a committed test module
        assert (here / (mf.name.replace(".fcov.yaml", ".py"))).exists(), f"manifest without a test module: {mf.name} (render manifests when the test lands)"
    good_items = ("class T(GenTest):\n    name = 'gen_test_cmp_zcb'\n    not_built = {}\n    def fire_check(self):\n        self.fire_tp_cmp_034(); self.fire_tp_cmp_036(); self.fire_tp_cmp_038()\n"
                  + "".join(f"    def fire_tp_cmp_{n}(self):\n        self.check('fire_tp_cmp_{n}', self.retired() > 0, 'x')\n" for n in ("034", "036", "038")))
    assert check_test_source(imp + good_items, "<green>") == ["T"]
    for form, red, why in ((F_ITEMS, imp + good_items.replace("    not_built = {}\n", ""), "needs a literal"),
                           (F_ITEMS, imp + good_items.replace("self.fire_tp_cmp_038()", "pass"), "never called from fire_check"),
                           (F_ITEMS, imp + good_items.replace("def fire_tp_cmp_038(self):\n        self.check('fire_tp_cmp_038'", "def fire_tp_cmp_038(self):\n        self.check('fire_tp_cmp_036'"), "does not name its item"),
                           (F_ITEMS, imp + good_items.replace("    not_built = {}\n", "    not_built = {'TP-CMP-038': 'x'}\n"), "overlap"),
                           (F_ITEMS, imp + good_items.replace("self.fire_tp_cmp_038()", "pass").replace("    def fire_tp_cmp_038(self):\n        self.check('fire_tp_cmp_038', self.retired() > 0, 'x')\n", ""), "unaccounted")):
        accepted = False
        try:
            check_test_source(red, "<red>")
            accepted = True
        except AssertionError as exc:
            assert why in str(exc), (why, exc)
        assert not accepted, f"red source ({why}) accepted"
        proved.add(form)
    # the refused forms proven above are exactly REFUSED_FORMS, and the API doc lists them verbatim (bullets after the marker line,
    # two-space continuation lines joined); the two cannot drift apart
    assert proved == set(REFUSED_FORMS), f"refused forms without a red source or unlisted: {proved ^ set(REFUSED_FORMS)}"
    assert api_doc_forms() == list(REFUSED_FORMS), f"API doc list differs from REFUSED_FORMS: {api_doc_forms()}"
    # the longest CG-REG-007 phase fits the schedule runner's per-trigger wait budget (equal today, named here)
    assert DURATION_CLASSES["long"][1] <= CONSTANTS["GEN_ALIVE_TIMEOUT_CYCLES_DEFAULT"], "a long phase can outlast the runner's wait budget"
    for declared, why in ((["x.y.z"], "no manifest"),):
        try:
            check_manifest_matches("gen_test_boot_retire", declared); raise AssertionError("missing-manifest case accepted")
        except AssertionError as exc:
            assert why in str(exc), exc
    # the manifest renderer's own self-test runs here too, so the two cannot go red apart
    r = subprocess.run([sys.executable, str(here / "gen_fcov_manifest.py"), "--self-test"], cwd=REPO_ROOT, env=env, capture_output=True, text=True, timeout=600)
    assert r.returncode == 0, f"gen_fcov_manifest.py --self-test failed: {(r.stderr.strip().splitlines() or ['?'])[-1][:200]}"
    print(f"GEN_TEST_LIB self-test PASS (consumed knobs now: {list(CONSUMED_KNOBS) or 'none'}; checked tests: {[f.name for f in tests]}; schedule k={s1.k}: {s1.text()})")
    return 0


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        sys.exit(_self_test())
    print(__doc__)
