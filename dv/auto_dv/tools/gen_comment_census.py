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
design. A version's dotted tail (X-2025.06) excludes it, and so does a dot before the letters: 1..K-1 is a range
tail, not a citation (the same letters without the dot still count, since the shape cannot tell arithmetic from
an id there). Plan ids are excluded by prefix, except the F family,
which both the feature list and the intervention log use: an F id is an intervention-log identifier when the
log defines it under that heading and a plan id otherwise, decided by lookup rather than by shape.

Classes: intervention-log ruling ids (what the log defines: LOG-n, A-n, F-n, R-n), question ids (Q-n, which
the log also defines but the comment rule sweeps), task ids (T-n), exclusion classes (EC-n), and every other id
of the shape. Rulings cited by date are not ids and are counted separately, discriminated by adjacency from
dates that merely timestamp an observation, and both are reported so no date is dropped in silence.

Files are the ones git tracks under --root; where git lists nothing (a gitignored work directory, or a root outside
the work tree such as a detached archive) the census walks the filesystem instead, and the header line NAMES the
enumeration either way, so a record quoting a count says how its files were found. A root under which neither
lists a file is refused: every class at zero with exit 0 was a vacuous green once.

Usage: gen_comment_census.py [--root DIR] [--verbose] [--self-test]
Exit: 0 the census ran (a census has no pass or fail); 1 the self-test failed; 2 a file could not be parsed, the
intervention log is unreadable, or no file was found to census, each a refusal and never a short census.
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

LABEL = re.compile(r'(?<![A-Za-z0-9_.-])([A-Z]{1,4})-(\d+)([a-z]?)(?![A-Za-z0-9])')
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


def refuse(msg):
    """A refusal exits 2 with its reason on stderr: SystemExit('<text>') would exit 1 and read as a failed census."""
    print(msg, file=sys.stderr)
    raise SystemExit(2)


def logged_ids(path=INTERVENTION_LOG):
    """The identifiers the intervention log defines, which is what makes an F id a ruling and not a feature."""
    try:
        return set(LOG_HEADING.findall(path.read_text(encoding='utf-8')))
    except OSError as exc:
        refuse(f'{path}: the census cannot classify without the intervention log ({exc})')


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


def enumerate_files(root, exts=EXTS):
    """([(path, name to report)], mode): the files git tracks under root, else a filesystem walk; the mode is
    returned so the census names its enumeration, and a root with no file is refused rather than censused as zero."""
    rootp = pathlib.Path(root)
    rootp = rootp if rootp.is_absolute() else R / rootp
    listed = subprocess.run(['git', 'ls-files', str(rootp)], capture_output=True, text=True, cwd=R)
    files = [(R / rel, rel) for rel in listed.stdout.split() if rel.endswith(exts)] if listed.returncode == 0 else []
    mode = f'{len(files)} tracked file(s) by git ls-files'
    if not files:
        if not rootp.is_dir():
            refuse(f'{root}: git lists nothing under it and it is not a directory to walk; refused')
        walked = sorted(p for p in rootp.rglob('*') if p.is_file() and p.suffix in exts)
        files = [(p, str(p.relative_to(R)) if R in p.parents else str(p)) for p in walked]
        mode = (f'{len(files)} file(s) by filesystem walk: git lists nothing under {root} (a gitignored directory, or a '
                f'root outside the work tree such as a detached archive)')
    if not files:
        refuse(f'{root}: no {", ".join(exts)} file under it by git or by walk; a census of nothing is refused')
    return files, mode


def census(root, exts=EXTS):
    """({class: [(path, line, token)]}, the shorthand sites, the enumeration mode) over the files under root."""
    logged = logged_ids()
    out = {c: [] for c in CLASSES}
    shorthand = []
    files, mode = enumerate_files(root, exts)
    for path, rel in files:
        try:
            spans = comment_spans(path)
        except (SyntaxError, tokenize.TokenError) as exc:
            refuse(f'{rel}: cannot parse, so the census would silently skip it ({exc})')
        for line, text in spans:
            hits, short = census_text(text, logged)
            for cls, token in hits:
                out[cls].append((rel, line, token))
            shorthand.extend((rel, line, s) for s in short)
    return out, shorthand, mode


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
PHASES = 4   # phases 1..K-1 change a subset: a range tail, not an id; the bare K-1 in this clause is one


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

        ks = [(n, t) for _, n, t in found[CLASS_PROCESS] if t == 'K-1']
        good = len(ks) == 1
        ok = ok and good
        print(f'SELF-TEST {"ok  " if good else "BAD "} a dot-preceded arithmetic tail (1..K-1) is not an id while '
              f'the bare K-1 beside it is: {len(ks)} K-1 site(s), want 1')

        # enumeration: this directory is outside the work tree, so git lists nothing under it and the census must walk
        walked, _, mode = census(d)
        seen = {pathlib.Path(p).name for c in CLASSES for p, _, _ in walked[c]}
        good = seen == {'fixture.py', 'fixture.yaml'} and 'walk' in mode
        ok = ok and good
        print(f'SELF-TEST {"ok  " if good else "BAD "} a root git lists nothing under is censused by a filesystem walk '
              f'that names itself: files {sorted(seen)}, mode {mode!r}')

        empty = pathlib.Path(d) / 'empty'
        empty.mkdir()
        try:
            census(empty)
            good = False
        except SystemExit as exc:
            good = exc.code == 2
        ok = ok and good
        print(f'SELF-TEST {"ok  " if good else "BAD "} a root with no file to census is refused, never reported as '
              f'zero of every class, and the refusal exits 2: {good}')

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
    found, shorthand, mode = census(a.root)
    print(f'GEN_COMMENT_CENSUS: comment and docstring lines under {a.root} over ' + ', '.join(EXTS) + f'; {mode}')
    report(found, shorthand, a.verbose)
    return 0


if __name__ == '__main__':
    sys.exit(main())
