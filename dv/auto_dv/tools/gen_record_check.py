#!/usr/bin/env python3
"""Check declared CONTRADICTION PAIRS in the plan records: two statements that cannot both be true.

A per-phrase check cannot find this class, because each phrase is individually true; CM205-Medium-1 was a
record asserting both that the fcov leg had run all nine entries and that no entry had been exercised by a
flow run. Each pair below names a record, the two phrases, and why they conflict. Text is FLATTENED before
matching, so a clause wrapped across lines is still seen, and EXACTLY ONE of the pair must be present, so
a pair whose phrases were both edited away fails instead of passing vacuously.

Usage: gen_record_check.py [--root DIR] [--self-test]
Exit: 0 all pairs hold; 1 a pair is violated; 2 a wrong call.
"""
import argparse, pathlib, re, sys, tempfile

# record, phrase A, phrase B, why they cannot both be true
PAIRS = [
    ("dv/auto_dv/docs/gen_fcov_plan.md",
     "no entry of the nine has yet been exercised by a flow run",
     "Both owed counts are now CONFIRMED THROUGH THE FLOW",
     "CM205-Medium-1: the promotion clause's unmeasured sense against the leg's first exercise"),
    ("dv/auto_dv/docs/gen_test_plan.md",
     "the counted-only rows below point at the entry carrying it",
     "nothing\n  in those rows points at one",
     "CR-30b-M-1: a correction added while the clause it corrects still stood, in the touch that shipped this tool"),
    ("dv/auto_dv/docs/gen_test_plan.md",
     "so that case stays OWED",
     "so that case is CLOSED by the cap rule",
     "landing 31 left the retirement-stall rule out: the record must not say both owed and closed when the rule lands"),
]


def repo_root():
    """the clone root, found the way the other tools find it: the directory holding dv/auto_dv/contract"""
    r = pathlib.Path(__file__).resolve()
    while not (r / "dv/auto_dv/contract").is_dir():
        if r.parent == r:
            print("gen_record_check: repo root not found (no dv/auto_dv/contract above this file)")
            sys.exit(2)
        r = r.parent
    return r


def flat(t):
    return " ".join(t.split())


def check(root, pairs=PAIRS, out=print):
    bad = 0
    for rel, a, b, why in pairs:
        p = pathlib.Path(root) / rel
        if not p.is_file():
            out(f"MISSING {rel}"); bad += 1; continue
        t = flat(p.read_text())
        ha, hb = flat(a) in t, flat(b) in t
        if ha and hb:
            out(f"CONTRADICTION {rel}: both phrases present ({why})"); bad += 1
        elif not (ha or hb):
            out(f"VACUOUS {rel}: neither phrase present, so the pair guards nothing ({why})"); bad += 1
        else:
            out(f"ok {rel}: exactly one of the pair present ({'A' if ha else 'B'})")
    return bad


def self_test():
    cases, fails = 0, 0
    with tempfile.TemporaryDirectory() as d:
        rel = "r.md"
        pairs = [(rel, "the leg ran all nine", "no entry has run", "self-test pair")]
        for name, text, want in (
            ("exactly one (A)", "prose the leg ran all nine prose", 0),
            ("exactly one (B)", "prose no entry has run prose", 0),
            ("both present", "the leg ran all nine and no entry has run", 1),
            ("neither present", "unrelated prose", 1),
            ("A wrapped across lines", "prose the leg ran\n   all nine prose", 0),
            ("both, one wrapped", "the leg ran\n  all nine ... no entry has run", 1),
        ):
            (pathlib.Path(d) / rel).write_text(text)
            got = check(d, pairs, out=lambda *_: None)
            cases += 1
            ok = (got > 0) == (want > 0)
            print(f"SELF-TEST {'ok  ' if ok else 'FAIL'} {name}")
            fails += 0 if ok else 1
        got = check(d, [("absent.md", "x", "y", "missing record")], out=lambda *_: None)
        cases += 1
        ok = got > 0
        print(f"SELF-TEST {'ok  ' if ok else 'FAIL'} a missing record fails")
        fails += 0 if ok else 1
    print(f"GEN_RECORD_CHECK {'PASS' if fails == 0 else 'FAIL'} ({cases} cases, {fails} failed)")
    return 1 if fails else 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=str(repo_root()))
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    bad = check(a.root)
    print(f"gen_record_check: {len(PAIRS)} declared pair(s), {bad} problem(s)")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
