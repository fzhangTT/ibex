#!/usr/bin/env python3
"""Hold the temporary "covergroup not built" manifest marks to their precondition, and the manifests to the
invariant behind them.

A per-run fcov manifest may not declare a bin of a covergroup that does not exist: the checker cannot judge it,
so every seed fails. The coverpoints THE REFERENCED MANIFESTS WOULD OTHERWISE DECLARE on such a covergroup
therefore carry `[covergroup not built, not in manifest]` on their plan line, which gen_fcov_manifest.py
honours. That is a subset of the unbuilt covergroups' coverpoints, not all of them: the mark exists to correct
a declaration, so a coverpoint no referenced manifest reaches is left alone (the population line below prints
both numbers, so this text cannot drift from the tree again). The mark is TEMPORARY, and a temporary plan state
rots silently: once the covergroup is built the mark would keep its bins out of every manifest with nobody
noticing. This tool makes the state self-clearing.

Two checks, both against the tree rather than against a list kept here:

  MARK  every coverpoint carrying the mark sits in a plan block whose implementation covergroup is absent from
        dv/auto_dv/env/gen_fcov_groups.svh. A built covergroup with a marked coverpoint FAILS: remove the mark
        and re-render the manifests that then gain its bins. This leg checks the mark's PRECONDITION, never its
        completeness: a MISSING mark is invisible here and is caught by DECL instead, one step later, when the
        manifest that would declare the bin is rendered and read.
  DECL  no manifest the testlist REFERENCES declares a bin whose covergroup is absent from that file. This is
        the property the marks exist to produce, checked independently of them. A manifest file no entry names
        cannot fail a run, so it is counted and reported but not judged: an entry whose whole declared set sits
        on unbuilt covergroups has no manifest to name until they are built, and its file stays as evidence.

Exit codes: 0 both checks pass; 1 a check failed; 2 a wrong call.
"""
import pathlib
import re
import sys

import yaml

MARK = "[covergroup not built, not in manifest]"
USAGE = "usage: gen_unbuilt_mark_check.py [--root <tree>] | --self-test"


def repo_root(start: pathlib.Path) -> pathlib.Path:
    r = start.resolve()
    while not (r / "dv/auto_dv/contract").is_dir():
        if r.parent == r:
            print("repo root not found (no dv/auto_dv/contract above this file)")
            sys.exit(2)
        r = r.parent
    return r


# Covergroups are not all in the rendered file: the witness ledger lives in the package beside it, so a reader
# that opens only gen_fcov_groups.svh calls a built covergroup unbuilt. Both files, and the rendered one must
# exist because its absence means the codegen has not run.
COVERGROUP_SOURCES = ("dv/auto_dv/env/gen_fcov_groups.svh", "dv/auto_dv/env/gen_fcov_pkg.sv")


def rendered_covergroups(root: pathlib.Path) -> set[str]:
    """Every covergroup name the TB actually builds, over all the files that define one."""
    required = root / COVERGROUP_SOURCES[0]
    if not required.is_file():
        print(f"{required}: not a file")
        sys.exit(2)
    names: set[str] = set()
    for rel in COVERGROUP_SOURCES:
        f = root / rel
        if f.is_file():
            # anchored: a comment that mentions a covergroup is prose, not a declaration
            names |= set(re.findall(r"^\s*covergroup\s+(\w+)", f.read_text(encoding="ascii"), re.M))
    return names


def marked_coverpoints(root: pathlib.Path) -> list[tuple[str, str, str, int]]:
    """(CG id, implementation covergroup, coverpoint, line number) per marked plan line."""
    plan = (root / "dv/auto_dv/docs/gen_fcov_plan.md").read_text(encoding="ascii").split("\n")
    out, cg, cid = [], None, None
    for i, line in enumerate(plan, 1):
        m = re.match(r"^### (CG-[A-Z]+-\d{3}): gen_cg_(\S+)", line)
        if m:
            cid, cg = m.group(1), f"gen_{m.group(2)}_cg"
        elif re.match(r"^### |^## |^# ", line):
            cid = cg = None
        if cg and MARK in line:
            mc = re.match(r"^\s*- (c[pr]_[a-z0-9_]+)\b", line)
            if mc:
                out.append((cid, cg, mc.group(1), i))
    return out


def unbuilt_population(root: pathlib.Path, built: set[str]) -> tuple[int, int]:
    """(coverpoint lines, covergroups) inside plan blocks whose covergroup is not rendered: the mark set's
    denominator, printed so no document has to carry the number in prose."""
    plan = (root / "dv/auto_dv/docs/gen_fcov_plan.md").read_text(encoding="ascii").split("\n")
    cps, cgs, cur = 0, set(), None
    for line in plan:
        m = re.match(r"^### (CG-[A-Z]+-\d{3}): gen_cg_(\S+)", line)
        if m:
            cur = f"gen_{m.group(2)}_cg"
        elif re.match(r"^### |^## |^# ", line):
            cur = None
        if cur and cur not in built and re.match(r"^\s*- c[pr]_", line):
            cps += 1
            cgs.add(cur)
    return cps, len(cgs)


def check(root: pathlib.Path) -> int:
    built = rendered_covergroups(root)
    bad = 0
    marks = marked_coverpoints(root)
    wrong = [(cid, cg, cp, ln) for cid, cg, cp, ln in marks if cg in built]
    pop_cps, pop_cgs = unbuilt_population(root, built)
    print(f"MARK {len(marks)} marked coverpoint(s) of {pop_cps} on {pop_cgs} unbuilt covergroup(s); "
          f"{len(built)} covergroup(s) rendered")
    print("MARK the marked set is what the referenced manifests would declare, not the whole population; "
          "a MISSING mark is caught by DECL, not here")
    for cid, cg, cp, ln in wrong:
        print(f"MARK FAIL gen_fcov_plan.md:{ln} {cid} {cp}: {cg} IS rendered; remove the mark and re-render")
    bad += len(wrong)
    home = root / "dv/auto_dv/fcov_expectations"
    tl_path = root / "dv/auto_dv/flow/gen_testlist.yaml"
    referenced = set()
    if tl_path.is_file():
        tl = yaml.safe_load(tl_path.read_text(encoding="ascii")) or {}
        for e in tl.get("tests") or []:
            ref = e.get("fcov_expectation_file")
            if ref:
                referenced.add(pathlib.Path(ref).name)
    files = sorted(home.glob("*.fcov.yaml"))
    judged = [f for f in files if not referenced or f.name in referenced]
    offenders = 0
    for f in judged:
        data = yaml.safe_load(f.read_text(encoding="ascii")) or {}
        for b in data.get("bins") or []:
            cgn = b.split(".")[0]
            if cgn not in built:
                print(f"DECL FAIL {f.name}: declares {b} on unrendered covergroup {cgn}")
                offenders += 1
    print(f"DECL {len(judged)} referenced manifest(s) judged of {len(files)} present; "
          f"{offenders} declaration(s) on an unrendered covergroup")
    bad += offenders
    print("gen_unbuilt_mark_check:", "PASS" if not bad else f"FAIL ({bad} problem(s))")
    return 1 if bad else 0


def _tree(td: pathlib.Path, plan: str, svh: str, manifests: dict[str, str], pkg: str = "") -> pathlib.Path:
    (td / "dv/auto_dv/docs").mkdir(parents=True)
    (td / "dv/auto_dv/env").mkdir(parents=True)
    (td / "dv/auto_dv/fcov_expectations").mkdir(parents=True)
    (td / "dv/auto_dv/docs/gen_fcov_plan.md").write_text(plan, encoding="ascii")
    (td / "dv/auto_dv/env/gen_fcov_groups.svh").write_text(svh, encoding="ascii")
    (td / "dv/auto_dv/env/gen_fcov_pkg.sv").write_text(pkg, encoding="ascii")
    for n, t in manifests.items():
        (td / "dv/auto_dv/fcov_expectations" / n).write_text(t, encoding="ascii")
    return td


def self_test() -> int:
    """Drive both checks over synthetic trees, so each failing path is proven rather than described."""
    import tempfile
    ok = True
    PLAN_MARKED = ("### CG-XXX-001: gen_cg_alpha\n"
                   f"  - cp_one = thing {MARK}: bins a{{0}}, b{{1}}\n"
                   "### CG-XXX-002: gen_cg_beta\n"
                   "  - cp_two = thing: bins c{0}\n")
    SVH_NEITHER = "covergroup gen_gamma_cg;\nendgroup\n"
    SVH_ALPHA = "covergroup gen_alpha_cg;\nendgroup\ncovergroup gen_gamma_cg;\nendgroup\n"
    MAN_CLEAN = "test: gen_test_x\nbins:\n  - gen_gamma_cg.cp_z.hit\n"
    MAN_DIRTY = "test: gen_test_y\nbins:\n  - gen_alpha_cg.cp_one.a\n"
    cases = [
        ("mark on an unbuilt covergroup passes", PLAN_MARKED, SVH_NEITHER, {"a.fcov.yaml": MAN_CLEAN}, 0, ""),
        ("mark on a BUILT covergroup fails", PLAN_MARKED, SVH_ALPHA, {"a.fcov.yaml": MAN_CLEAN}, 1, ""),
        # A covergroup defined in the package must read as BUILT; a reader of the rendered file alone misses it.
        ("mark on a covergroup built in the PACKAGE fails", PLAN_MARKED, SVH_NEITHER,
         {"a.fcov.yaml": MAN_CLEAN}, 1, "package gen_fcov_pkg;\ncovergroup gen_alpha_cg;\nendgroup\nendpackage\n"),
        # A covergroup NAMED IN PROSE is not declared, so the mark on it stays correct.
        ("a comment naming a covergroup does not make it built", PLAN_MARKED, SVH_NEITHER,
         {"a.fcov.yaml": MAN_CLEAN}, 0,
         "package gen_fcov_pkg;\n// the covergroup gen_alpha_cg is described here, not declared\nendpackage\n"),
        ("a manifest declaring an unrendered bin fails", PLAN_MARKED, SVH_NEITHER,
         {"a.fcov.yaml": MAN_CLEAN, "b.fcov.yaml": MAN_DIRTY}, 1, ""),
        ("no marks and clean manifests pass", "### CG-XXX-002: gen_cg_beta\n  - cp_two = t: bins c{0}\n",
         SVH_NEITHER, {"a.fcov.yaml": MAN_CLEAN}, 0, ""),
    ]
    for name, plan, svh, mans, want, pkg in cases:
        with tempfile.TemporaryDirectory(prefix="gen_unbuilt_mark_") as td:
            root = _tree(pathlib.Path(td), plan, svh, mans, pkg)
            got = check(root)
        good = got == want
        ok &= good
        print("SELF-TEST", "ok " if good else "BAD", f"{name}: exit {got}, want {want}")
    print("gen_unbuilt_mark_check --self-test:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


def main() -> int:
    args = sys.argv[1:]
    if "--self-test" in args:
        return self_test()
    root = None
    if args:
        if args[0] == "--root" and len(args) == 2:
            root = pathlib.Path(args[1])
        else:
            print(USAGE)
            return 2
    return check(root.resolve() if root else repo_root(pathlib.Path(__file__)))


if __name__ == "__main__":
    sys.exit(main())
