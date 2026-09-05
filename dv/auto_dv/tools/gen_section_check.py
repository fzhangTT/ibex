#!/usr/bin/env python3
"""Check a record's numbered section headers: "## N." lines at column 0 must number consecutively, and no
header or table row may sit indented (markdown renders an indented block as code, and a header check that
matches column 0 then cannot see the section, so a numbered header indented by a patch script hides a gap).

Usage: gen_section_check.py RECORD [--from N | --indent-only] [--self-test]
  --from N        start the sequence at N; numbered headers below N are ignored (the earlier part of a
                  record may be numbered by another rule). Default: the first numbered header found.
  --indent-only   the record has no numbered sections (a response file): check indentation alone.
Exit: 0 headers consecutive and nothing indented; 1 a defect, each printed with its line number, or no
numbered header found at all (an unobservable record is not a pass); 2 a wrong call.
"""
import argparse, pathlib, re, sys, tempfile

HEADER = re.compile(r"^## (\d+)\.")
INDENTED = re.compile(r"^[ \t]+(## |\| )")


def check(lines, start=None, out=print, indent_only=False):
    """defect strings for the record's lines; empty means the record passes"""
    defects, seq = [], []
    for n, line in enumerate(lines, 1):
        if INDENTED.match(line):
            defects.append(f"line {n}: indented header or table row: {line.strip()[:60]}")
        m = HEADER.match(line)
        if m:
            seq.append((n, int(m.group(1))))
    if indent_only:
        for d in defects:
            out(f"gen_section_check: {d}")
        return defects
    if start is not None:
        seq = [(n, k) for n, k in seq if k >= start]
    if not seq:
        defects.append("no numbered '## N.' header at column 0" + (f" from {start}" if start is not None else ""))
    if seq and start is not None and seq[0][1] != start:
        defects.append(f"line {seq[0][0]}: first numbered header is {seq[0][1]}, expected {start}")
    for (n0, k0), (n1, k1) in zip(seq, seq[1:]):
        if k1 != k0 + 1:
            kind = "repeat" if k1 <= k0 else "gap"
            defects.append(f"line {n1}: header {k1} after {k0} at line {n0} ({kind})")
    for d in defects:
        out(f"gen_section_check: {d}")
    return defects


def self_test():
    ok = lambda s, **kw: check(s.splitlines(), out=lambda *_: None, **kw)
    good = "## 17. a\nx\n## 18. b\n| t | t |\n|---|---|\n## 19. c\n"
    assert ok(good) == [], "consecutive headers must pass"
    assert ok(good, start=17) == [] and ok(good, start=18) == [], "--from selects the start and ignores lower"
    assert ok(good, start=20) and "no numbered" in ok(good, start=20)[0], "--from above every header is not a pass"
    assert any("expected 17" in d for d in ok("## 18. b\n## 19. c\n", start=17)), "a missing start header fails"
    # two numbered headers at column 0 with the one between them indented four spaces: both defects, in order
    d = ok("## 19. a\n    ## 20. b\n## 21. c\n")
    assert len(d) == 2 and "indented" in d[0] and "gap" in d[1], d
    d = ok("## 19. a\n    | r | s |\n## 20. b\n")
    assert len(d) == 1 and "table row" in d[0], d
    assert any("repeat" in x for x in ok("## 17. a\n## 18. b\n## 18. c\n")), "a repeated number fails"
    assert any("gap" in x for x in ok("## 17. a\n## 19. b\n")), "a skipped number fails"
    assert "no numbered" in ok("plain text\n### 3. sub\n")[0], "no header at all fails, not passes"
    assert ok("## 1. a\n## 2. b\n\tsome code\n") == [], "indented plain text is not a defect"
    assert ok("## Review of x\n| a | b |\n", indent_only=True) == [], "--indent-only passes an unnumbered record"
    assert "table row" in ok("## Review of x\n    | a | b |\n", indent_only=True)[0], "--indent-only still sees indentation"
    with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as f:
        f.write(good); path = f.name
    assert run(path, None, out=lambda *_: None) == 0, "a passing file exits 0"
    print("GEN_SECTION_CHECK self-test PASS (14 cases: consecutive, --from, missing start, indented middle header, "
          "indented table, repeat, gap, no header, indented prose, --indent-only both ways, file run)")
    return 0


def run(path, start, out=print, indent_only=False):
    p = pathlib.Path(path)
    if not p.is_file():
        out(f"gen_section_check: not a file: {path}")
        return 2
    defects = check(p.read_text().splitlines(), start, out, indent_only)
    if not defects:
        what = "nothing indented" if indent_only else "headers consecutive" + (f" from {start}" if start is not None else "") + ", nothing indented"
        out(f"gen_section_check: {path}: {what}")
    return 1 if defects else 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("record", nargs="?")
    ap.add_argument("--from", dest="start", type=int, default=None)
    ap.add_argument("--indent-only", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    if not a.record or (a.indent_only and a.start is not None):
        ap.print_usage(); return 2
    return run(a.record, a.start, indent_only=a.indent_only)


if __name__ == "__main__":
    sys.exit(main())
