#!/usr/bin/env python3
"""Census the identifiers on comment and docstring lines, so a count in a record is reproducible by running it.

A record that says "N citations" is only as good as the search behind it, and a hand search fails in ways that
return a plausible number rather than an error: it anchors on a word boundary after the digits and cannot see a
suffixed id (LOG-028a); it reads leading comments and misses a comment trailing code; it scans the whole line
and counts an id that is really inside a string. Each of those has cost this repository a wrong figure in a
committed record. A record cites this tool instead of a number.

Scanned text is the COMMENT ITSELF, never the line holding it. Python comments and docstrings come from the
parse, so a "#" inside a string is not a comment and a docstring's continuation lines are. For yaml and tcl the
comment is the first "#" that is not inside quotes and stands at line start or after whitespace, so a yaml
value carrying a "#" is not a comment while a comment after a value is one; for .f it is "//".

An id is an uppercase letter group, a dash, digits and an optional lowercase suffix. Lowercase words with
digits (utf-8, purpose-4) are not ids, and a dash-less name (P6, a probe register) is outside the shape by
design. A version's dotted tail (X-2025.06) excludes it. Plan ids are excluded by prefix, except the F family,
which both the feature list and the intervention log use: an F id is an intervention-log identifier when the
log defines it under that heading and a plan id otherwise, decided by lookup rather than by shape.

Classes: intervention-log ruling ids (what the log defines: LOG-n, A-n, F-n, R-n), question ids (Q-n, which
the log also defines but the comment rule sweeps), task ids (T-n), exclusion classes (EC-n), and every other id
of the shape. Rulings cited by date are not ids and are counted separately, discriminated by adjacency from
dates that merely timestamp an observation, and both are reported so no date is dropped in silence.

Usage: gen_comment_census.py [--root DIR] [--verbose] [--self-test]
Exit: 0 the census ran (a census has no pass or fail); 1 the self-test failed; 2 a file could not be parsed or
the intervention log is unreadable, which is a refusal and never a short census.
"""
import re
import ast
import sys
import io
import pathlib
import argparse
import tokenize
import subprocess

R = pathlib.Path(__file__).resolve()
while not (R / 'dv/auto_dv/contract').is_dir():
    if R.parent == R:
        sys.exit('repo root not found (no dv/auto_dv/contract above this file)')
    R = R.parent

DEFAULT_ROOT = 'dv/auto_dv/flow'
INTERVENTION_LOG = R / 'dv/auto_dv/docs/gen_intervention_log.md'
EXTS = ('.py', '.yaml', '.tcl', '.f')

LABEL = re.compile(r'(?<![A-Za-z0-9_-])([A-Z]{1,4})-(\d+)([a-z]?)(?![A-Za-z0-9])')
VERSION_TAIL = re.compile(r'^\.\d')
SHORTHAND_TAIL = re.compile(r'^/\d+[a-z]?')
LOG_HEADING = re.compile(r'^##\s+([A-Z]{1,4}-\d+[a-z]?)\b', re.M)
PLAN_PREFIXES = ('TP', 'CG', 'WIT')
AMBIGUOUS_PREFIXES = ('F', 'R')
DATE = re.compile(r'\b(?:19|20)\d\d-\d\d-\d\d\b')
RULING_WORD = re.compile(r'\brul(?:ing|ed|es)\b', re.IGNORECASE)
# A ruling citation puts the word beside the date; a line mentioning a ruling elsewhere is timestamping
# something else, so the class is decided by adjacency and not by the line's vocabulary.
RULING_WINDOW = 24

CLASS_RULING = 'intervention-log ruling ids (LOG-n, A-n, F-n, R-n)'
CLASS_QUESTION = 'question ids (Q-n)'
CLASS_TASK = 'task ids (T-n)'
CLASS_EXCL = 'exclusion classes (EC-n)'
CLASS_PROCESS = 'process pointers (every other id of the shape)'
CLASS_DATED_RULING = 'rulings cited by date'
CLASS_DATED_OTHER = 'dates that timestamp an observation, not a ruling'
CLASSES = (CLASS_RULING, CLASS_QUESTION, CLASS_TASK, CLASS_EXCL, CLASS_PROCESS,
           CLASS_DATED_RULING, CLASS_DATED_OTHER)


def logged_ids(path=INTERVENTION_LOG):
    """The identifiers the intervention log defines, which is what makes an F id a ruling and not a feature."""
    try:
        return set(LOG_HEADING.findall(path.read_text(encoding='utf-8')))
    except OSError as exc:
        raise SystemExit(f'{path}: the census cannot classify without the intervention log ({exc})')


def unquoted_comment(line, mark):
    """The comment on one line of a quoted format, or None: the first mark outside quotes, at a word start."""
    quote = None
    for i, ch in enumerate(line):
        if quote:
            if ch == quote:
                quote = None
            continue
        if ch in '"\'':
            quote = ch
            continue
        if line.startswith(mark, i) and (i == 0 or line[i - 1].isspace()):
            return line[i:]
    return None


def comment_spans(path, text=None):
    """[(line number, the comment's own text)] for every comment and docstring line in one file."""
    text = path.read_text(encoding='utf-8') if text is None else text
    lines = text.splitlines()
    spans = []
    if path.suffix == '.py':
        for tok in tokenize.generate_tokens(io.StringIO(text).readline):
            if tok.type == tokenize.COMMENT:
                spans.append((tok.start[0], tok.string))
        for node in ast.walk(ast.parse(text)):
            if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
                first = node.body[0] if node.body else None
                if (isinstance(first, ast.Expr) and isinstance(first.value, ast.Constant)
                        and isinstance(first.value.value, str)):
                    for n in range(first.lineno, first.end_lineno + 1):
                        spans.append((n, lines[n - 1]))
    else:
        mark = '//' if path.suffix == '.f' else '#'
        for n, line in enumerate(lines, 1):
            found = unquoted_comment(line, mark)
            if found is not None:
                spans.append((n, found))
    return sorted(spans)


def classify(token, prefix, logged):
    if token in logged:
        return CLASS_QUESTION if prefix == 'Q' else CLASS_RULING
    if prefix in PLAN_PREFIXES or prefix in AMBIGUOUS_PREFIXES:
        return None
    if prefix == 'T':
        return CLASS_TASK
    if prefix == 'EC':
        return CLASS_EXCL
    return CLASS_PROCESS


def census_text(text, logged):
    """(hits, shorthand) over one comment's own text: hits are (class, token), shorthand the "LOG-007/008" form."""
    hits, shorthand = [], []
    for m in LABEL.finditer(text):
        prefix, digits, suffix = m.groups()
        tail = text[m.end():]
        if VERSION_TAIL.match(tail):
            continue
        token = f'{prefix}-{digits}{suffix}'
        cls = classify(token, prefix, logged)
        if cls is None:
            continue
        hits.append((cls, token))
        cont = SHORTHAND_TAIL.match(tail)
        if cont:
            shorthand.append(token + cont.group(0))
    date = DATE.search(text)
    if date:
        window = text[max(0, date.start() - RULING_WINDOW):date.end() + RULING_WINDOW]
        hits.append((CLASS_DATED_RULING if RULING_WORD.search(window) else CLASS_DATED_OTHER, date.group(0)))
    return hits, shorthand


def census(root, exts=EXTS):
    """{class: [(path, line, token)]} over the tracked files under root, and the shorthand sites."""
    logged = logged_ids()
    out = {c: [] for c in CLASSES}
    shorthand = []
    listed = subprocess.run(['git', 'ls-files', str(root)], capture_output=True, text=True, cwd=R)
    if listed.returncode:
        raise SystemExit(f'{root}: not a git checkout, or the path is untracked')
    for rel in listed.stdout.split():
        if not rel.endswith(exts):
            continue
        path = R / rel
        try:
            spans = comment_spans(path)
        except (SyntaxError, tokenize.TokenError) as exc:
            raise SystemExit(f'{rel}: cannot parse, so the census would silently skip it ({exc})')
        for line, text in spans:
            hits, short = census_text(text, logged)
            for cls, token in hits:
                out[cls].append((rel, line, token))
            shorthand.extend((rel, line, s) for s in short)
    return out, shorthand


def report(found, shorthand, verbose=False):
    for cls in CLASSES:
        sites = found[cls]
        print(f'{len(sites):3d} occurrences on {len({(p, n) for p, n, _ in sites}):3d} lines  {cls}')
        if verbose:
            for path, line, token in sites:
                print(f'      {path}:{line}  {token}')
    for path, line, token in shorthand:
        print(f'  NOTE {path}:{line} writes {token}: a reader counts two ids where this shape sees one')


FIXTURE_PY = '''\
"""Module docstring citing LOG-028a, a suffixed id a word-boundary search does not see."""
# A comment citing LOG-067 and LOG-076 together, two occurrences on one line.
VALUE = "a string citing P-02, which is program output and not a comment"
OTHER = 1   # trailing comment citing T-215 and the plan id TP-CMP-065, which is excluded
VERSION = 2  # VCS X-2025.06-SP2 is a tool version, not an id
LOWER = 3   # utf-8 and purpose-4 are not ids, and P6 has no dash
MIXED = "F-1 in a string"   # F-001 is an intervention-log id; the F-1 beside it is not a comment


def f():
    """Docstring citing owner ruling A-002 and the ruling of 2026-09-03."""
    return "CM103-m-2"   # a label in a string stays


# Measured on soc-l-11 at 2026-09-03 08:35Z, a timestamp and not a ruling.
'''

FIXTURE_YAML = '''\
# A yaml comment citing LOG-007/008.
tests:
  - name: t
    description: a description citing T-205, which is a value and not a comment
    measured: false   # a trailing comment citing LOG-039
    pattern: "a quoted value with a # inside it and Q-017 after it"
'''


def _self_test():
    """A negative fixture for each fault the tool exists to prevent, every one with its control."""
    ok = True
    logged = {'LOG-028a', 'LOG-067', 'LOG-076', 'LOG-007', 'LOG-039', 'A-002', 'F-001', 'Q-017'}

    import tempfile
    with tempfile.TemporaryDirectory() as d:
        py = pathlib.Path(d) / 'fixture.py'
        py.write_text(FIXTURE_PY, encoding='utf-8')
        yml = pathlib.Path(d) / 'fixture.yaml'
        yml.write_text(FIXTURE_YAML, encoding='utf-8')

        found = {c: [] for c in CLASSES}
        shorthand = []
        for path in (py, yml):
            for line, text in comment_spans(path):
                hits, short = census_text(text, logged)
                for cls, token in hits:
                    found[cls].append((path.name, line, token))
                shorthand.extend((path.name, line, s) for s in short)

        rulings = [t for _, _, t in found[CLASS_RULING]]
        want = ['LOG-028a', 'LOG-067', 'LOG-076', 'F-001', 'A-002', 'LOG-007', 'LOG-039']
        good = rulings == want
        ok = ok and good
        print(f'SELF-TEST {"ok  " if good else "BAD "} suffixed, doubled, docstring and trailing-comment ids '
              f'all count: {rulings}')

        good = ('fixture.yaml', 5, 'LOG-039') in found[CLASS_RULING]
        ok = ok and good
        print(f'SELF-TEST {"ok  " if good else "BAD "} a comment TRAILING a yaml value is a comment: '
              f'{good} (the fault that cost the record a figure)')

        quoted = [t for c in CLASSES for _, _, t in found[c] if t.startswith(('Q-', 'P-', 'CM'))]
        good = quoted == []
        ok = ok and good
        print(f'SELF-TEST {"ok  " if good else "BAD "} a "#" inside a quoted value opens no comment and ids in '
              f'strings are not comments: {quoted} (want none)')

        tasks = [t for _, _, t in found[CLASS_TASK]]
        good = tasks == ['T-215']
        ok = ok and good
        print(f'SELF-TEST {"ok  " if good else "BAD "} a task id in a trailing comment counts, one in a yaml '
              f'value does not: {tasks} (want the trailing one alone)')

        excluded = [t for c in CLASSES for _, _, t in found[c] if t.startswith(('TP-', 'X-', 'F-1'))]
        good = excluded == []
        ok = ok and good
        print(f'SELF-TEST {"ok  " if good else "BAD "} a plan id, a tool version and an F the log does not '
              f'define are excluded: {excluded} (want none)')

        dated = [t for _, _, t in found[CLASS_DATED_RULING]]
        other = [t for _, _, t in found[CLASS_DATED_OTHER]]
        good = dated == ['2026-09-03'] and other == ['2026-09-03']
        ok = ok and good
        print(f'SELF-TEST {"ok  " if good else "BAD "} a dated ruling and a dated observation are separated: '
              f'ruling {dated}, observation {other}')

        good = [s[2] for s in shorthand] == ['LOG-007/008']
        ok = ok and good
        print(f'SELF-TEST {"ok  " if good else "BAD "} the "LOG-007/008" shorthand is reported, not counted '
              f'twice in silence: {[s[2] for s in shorthand]}')

    real = logged_ids()
    good = 'F-001' in real and 'LOG-030' in real and 'A-002' in real
    ok = ok and good
    print(f'SELF-TEST {"ok  " if good else "BAD "} the real intervention log defines the ids the classes rest '
          f'on: {len(real)} ids, F-001 {"F-001" in real}, LOG-030 {"LOG-030" in real}')

    print('gen_comment_census --self-test:', 'PASS' if ok else 'FAIL')
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--root', default=DEFAULT_ROOT, help='directory to census (default: %(default)s)')
    ap.add_argument('--verbose', action='store_true', help='print every site with its id')
    ap.add_argument('--self-test', action='store_true')
    a = ap.parse_args()
    if a.self_test:
        return _self_test()
    found, shorthand = census(a.root)
    print(f'GEN_COMMENT_CENSUS: comment and docstring lines under {a.root} over ' + ', '.join(EXTS))
    report(found, shorthand, a.verbose)
    return 0


if __name__ == '__main__':
    sys.exit(main())
