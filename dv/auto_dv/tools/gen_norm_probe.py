"""gen_norm_probe.py [--root <tree>] [--group CG-XXX-nnn] [--self-test]: list the coverage-plan bullets the covergroup
renderer's own loader captures no coverpoint or cross for, which is the trigger step of per-group normalisation.

The loader is the authority on what parses, so the probe calls gen_fcov_codegen.load_plan and compares its capture
against the plan's own bullet lines rather than re-implementing the grammar; a grammar copied here would drift from
the one that matters. A bullet whose value BEGINS with RETIRED is reported separately, because a retired coverpoint or
cross SHOULD fail to parse and normalising one would resurrect it; a line that merely mentions retired bins is a live
declaration and is not counted as retired.

Each actionable refusal is classified so a group's cost is visible before the prose is touched, and the two
parenthesis constructs are told apart because they need different work. A MARKER line glues the parenthesis to a
component and names a bin of that coverpoint, so both normalisation rules apply: the marker leaves the component
list, and every explicit bin names one token per component in component order. A SCOPE line carries a parenthetical
on the whole component list, scoping the cross in prose and naming no component bin, so rule 2 has nothing to move
and the work is one rule plus a sentence, with no tuple arithmetic and no arity risk. A GUARD line's parentheses sit
inside an iff guard, which is a different family and outside this convention. OTHER lines need a decision. A
marker line is split again by whether rule 1 alone suffices, since a short brace tuple needs rule 2 as well and a
line with no tuple at all is outside both rules.

A census is only meaningful against a named tree: --root defaults to this clone's working tree, which may hold another
role's uncommitted plan edits, so pass an archive of a commit when the figure is going into a record.

Exit codes: 0 listed, or the self-test passed; 1 the self-test failed; 2 a wrong call."""
import importlib.util
import pathlib
import re
import sys

USAGE = "usage: gen_norm_probe.py [--root <tree>] [--group CG-XXX-nnn] [--self-test]"
REL_CODEGEN = "dv/auto_dv/tb/gen_fcov_codegen.py"


def _usage(msg=None):
    """A wrong call is answered, not crashed: the tools are read by reviewers who have not seen them before."""
    if msg:
        print(msg)
    print(USAGE)
    sys.exit(2)


def load_loader(root: pathlib.Path):
    """The renderer's own module, loaded against the given tree."""
    path = root / REL_CODEGEN
    if not path.is_file():
        _usage("no renderer under %s" % root)
    spec = importlib.util.spec_from_file_location("gen_fcov_codegen_probe", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def joined_lines(text):
    """The plan as the loader parses it: a bullet wrapping over indented lines is one logical line.

    Mirrors gen_fcov_codegen.load_plan's own joining. Reading first physical lines instead would test a wrapped
    line's tuple arity against half of it.
    """
    out = []
    for raw in text.splitlines():
        if out and raw.startswith("    ") and not raw.lstrip().startswith("- ") and raw.strip():
            out[-1] = out[-1].rstrip() + " " + raw.strip()
        else:
            out.append(raw)
    return out


def plan_bullets(root: pathlib.Path, rel_plan):
    """(group, name, line) for every coverpoint and cross bullet, in file order."""
    out = []
    cur = None
    for line in joined_lines((root / rel_plan).read_text()):
        head = re.match(r"^### (CG-[A-Z]+-\d{3}): gen_cg_[a-z0-9_]+\s*$", line)
        if head:
            cur = head.group(1)
            continue
        if line.startswith("### ") or line.startswith("## "):
            cur = None
            continue
        if cur is None:
            continue
        bullet = re.match(r"^\s+- (cp_[a-z0-9_]+|cr_[a-z0-9_]+)", line)
        if bullet:
            out.append((cur, bullet.group(1), line))
    return out


def classify(name: str, line: str) -> tuple[str, str]:
    """(kind, detail) for a refused bullet: retired, marker with which rules it needs, or other."""
    value = line.split(":", 1)[1].strip() if ":" in line else ""
    if value.startswith("RETIRED"):
        return "retired", "refusal by intent"
    comps = re.match(r"^\s+- cr_[a-z0-9_]+ = ([^:]*):", line)
    if not (name.startswith("cr_") and comps and "(" in comps.group(1)):
        return "other", "needs a decision"
    # a guard is an iff OUTSIDE any parenthetical; the word inside a trailing note is prose, not a guard
    if " iff " in re.sub(r"\([^)]*\)", "", comps.group(1)):
        return "guard", "parentheses in the iff guard: a different family"
    glued = re.search(r"cp_[a-z0-9_]+\(", comps.group(1))
    if not glued:
        # a parenthetical on the whole list scopes the cross in prose and names no component bin, so rule 2 has
        # nothing to move: the note becomes trailing prose after the bins and the tuples are untouched
        return "scope", "rule 1 plus a sentence"
    ncomp = len(re.findall(r"cp_[a-z0-9_]+", comps.group(1)))
    rest = line.split(":", 1)[1] if ":" in line else ""
    tuples = re.findall(r"[a-z0-9_]+\{([^}]*)\}", rest)
    if not tuples:
        return "marker", "no brace tuple: outside both rules, needs a decision"
    short = [t for t in tuples if len(t.split(",") if "," in t else t.split()) != ncomp]
    return "marker", ("rules 1 and 2" if short else "rule 1 alone")


def refusals(root, want=None):
    """group -> [(name, kind, detail, line)] for bullets the loader captured nothing for.

    No 3.10-only syntax anywhere in this file: a reviewer runs it from a bare archive of a commit, where no
    virtualenv exists and the interpreter is the site python, so the tool keeps to syntax the oldest one accepts."""
    mod = load_loader(root)
    captured = mod.load_plan(root)
    found: dict[str, list] = {}
    for group, name, line in plan_bullets(root, mod.REL_PLAN):
        if want and group != want:
            continue
        cap = captured.get(group, {"cps": {}, "crosses": {}})
        if name.startswith("cp_") and name in cap["cps"]:
            continue
        if name.startswith("cr_") and name in cap["crosses"]:
            continue
        kind, detail = classify(name, line)
        found.setdefault(group, []).append((name, kind, detail, line.strip()))
    return found


def self_test(from_tree) -> int:
    """A fabricated plan with one bullet of every outcome, plus an all-parsing negative control.

    The renderer is copied from the tree the caller pointed at, so --self-test --root exercises that tree's loader
    rather than the clone's.
    """
    import shutil
    import tempfile
    src = pathlib.Path(from_tree) / REL_CODEGEN
    if not src.is_file():
        _usage("no renderer under %s" % from_tree)
    root = pathlib.Path(tempfile.mkdtemp(prefix="gen_norm_probe_selftest_"))
    ok = True
    try:
        (root / "dv/auto_dv/docs").mkdir(parents=True)
        (root / "dv/auto_dv/tb").mkdir(parents=True)
        shutil.copy(src, root / REL_CODEGEN)
        plan = [
            "### CG-TST-001: gen_cg_probe_selftest",
            "- Coverpoints:",
            "  - cp_a = a value: bins one{1}, two{2}",
            "  - cp_b = b value: values 1, 2",
            "- Crosses:",
            "  - cr_ok = cp_a x cp_b: bins both{one 1}",
            "  - cr_mark_full = cp_a(one) x cp_b: bins m1{one 1}, m2{one 2}",
            "  - cr_mark_short = cp_a(one) x cp_b: bins s1{1}, s2{2}",
            "  - cr_mark_none = cp_a(one) x cp_b: n1, n2",
            "  - cr_gone: RETIRED (merged elsewhere, the plan's own form: no component list)",
            "  - cr_kept = cp_a x cp_b: RETIRED (a component list keeps it parsing, so the loader captures it)",
            "  - cp_bins_note = a value (the wide bins are RETIRED, S-7): bins one{1}",
            "  - cr_scope = cp_a x cp_b (one only, enumerated): bins sc1{one 1}, sc2{two 2}",
            "  - cr_guard = cp_a x cp_b iff (a_valid || b_valid): bins g1{one 1}",
            "  - cr_note_iff = cp_a x cp_b (one only, via the iff on cp_b): bins ni1{one 1}",
            "  - cr_wrapped = cp_a(one) x cp_b: bins w1{one 1},",
            "    w2{2}",
            "  - cr_odd: a cross with no component list at all",
            "",
        ]
        (root / "dv/auto_dv/docs/gen_fcov_plan.md").write_text("\n".join(plan), encoding="ascii")
        got = refusals(root)
        rows = {name: (kind, detail) for name, kind, detail, _ in got.get("CG-TST-001", [])}

        def case(label, cond):
            nonlocal ok
            ok &= bool(cond)
            print("SELF-TEST", "ok " if cond else "BAD", label)

        case("a parsing cross is not reported", "cr_ok" not in rows)
        case("a parsing coverpoint is not reported", "cp_a" not in rows)
        case("a values-form coverpoint is reported as other",
             rows.get("cp_b", ("", ""))[0] == "other")
        case("a retired cross in the plan's form is reported as retired",
             rows.get("cr_gone", ("", ""))[0] == "retired")
        case("a retired cross that keeps its component list is CAPTURED, so not reported",
             "cr_kept" not in rows)
        case("a live coverpoint that merely mentions retired bins is not called retired",
             "cp_bins_note" not in rows or rows["cp_bins_note"][0] != "retired")
        case("a marker line with full tuples needs rule 1 alone",
             rows.get("cr_mark_full") == ("marker", "rule 1 alone"))
        case("a marker line with a short tuple needs both rules",
             rows.get("cr_mark_short") == ("marker", "rules 1 and 2"))
        case("a marker line with no tuple is outside both rules",
             rows.get("cr_mark_none", ("", ""))[1].startswith("no brace tuple"))
        case("a cross with no component list is other", rows.get("cr_odd", ("", ""))[0] == "other")
        case("a parenthetical on the whole component list is a scope line, not a marker",
             rows.get("cr_scope") == ("scope", "rule 1 plus a sentence"))
        case("parentheses in an iff guard are their own family, not scope",
             rows.get("cr_guard", ("", ""))[0] == "guard")
        case("a trailing note that merely mentions iff is scope, not a guard",
             rows.get("cr_note_iff", ("", ""))[0] == "scope")
        case("a WRAPPED marker line is judged on the whole bullet, so its short tuple needs rule 2",
             rows.get("cr_wrapped") == ("marker", "rules 1 and 2"))

        # negative control: a plan whose every bullet parses reports nothing at all
        (root / "dv/auto_dv/docs/gen_fcov_plan.md").write_text("\n".join([
            "### CG-TST-002: gen_cg_probe_clean",
            "  - cp_a = a value: bins one{1}",
            "  - cr_ok = cp_a x cp_a: bins both{one one}",
            "",
        ]), encoding="ascii")
        case("an all-parsing plan reports no refusal", refusals(root) == {})
    finally:
        assert "gen_norm_probe_selftest_" in root.name
        shutil.rmtree(root)
    print("GEN_NORM_PROBE %s" % ("PASS" if ok else "FAIL"))
    return 0 if ok else 1


root = pathlib.Path(__file__).resolve().parents[3]
want = None
selftest = False
args = sys.argv[1:]
while args:
    a = args.pop(0)
    if a in ("-h", "--help"):
        print(USAGE)
        sys.exit(0)
    elif a == "--self-test":
        selftest = True
    elif a == "--root":
        if not args:
            _usage("--root needs a value")
        root = pathlib.Path(args.pop(0)).resolve()
    elif a == "--group":
        if not args:
            _usage("--group needs a value")
        want = args.pop(0)
    else:
        _usage("unknown argument: %s" % a)

if selftest:
    sys.exit(self_test(root))

found = refusals(root, want)
counts: dict[str, int] = {}
detail_counts: dict[str, int] = {}
for group in sorted(found):
    print("%s: %d refused" % (group, len(found[group])))
    for name, kind, detail, line in found[group]:
        print("    %-16s %-8s %-46s %s" % (name, kind, detail, line[:100]))
        counts[kind] = counts.get(kind, 0) + 1
        if kind == "marker":
            detail_counts[detail] = detail_counts.get(detail, 0) + 1
print()
print("tree                     %s" % root)
print("groups with a refusal    %d" % len(found))
for kind in ("retired", "marker", "scope", "guard", "other"):
    if counts.get(kind):
        print("%-24s %d" % (kind, counts[kind]))
for detail in sorted(detail_counts):
    print("   marker, %-40s %d" % (detail, detail_counts[detail]))
