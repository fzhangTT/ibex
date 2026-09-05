#!/usr/bin/env python3
"""Check a round request form's numbers against the sources they claim to come from.

Every claimed value is PARSED OUT OF THE FORM and compared with a value recomputed from the regression
manifest, the pre-flight record or arithmetic. Nothing is restated here, so a wrong figure in the form fails
instead of being repeated by its own checker. Prose claims are matched against a FLATTENED copy of the form,
so a sentence wrapped across lines is still one claim; table rows are matched line-anchored.

A claim the checker cannot find in the form is a FAILURE, never a skip: a form that drops a figure must fail
rather than pass with one fewer check.

Usage: gen_round_form_check.py [--form F] [--manifest F] [--preflight F] [--self-test]
Exit: 0 every claim reproduces; 1 a claim does not; 2 a wrong call.
"""
import re
import sys
import argparse
import pathlib
import collections
import statistics

import yaml

R = pathlib.Path(__file__).resolve()
while not (R / 'dv/auto_dv/contract').is_dir():
    if R.parent == R:
        sys.exit('repo root not found (no dv/auto_dv/contract above this file)')
    R = R.parent

FORM_DEFAULT = R / 'dv/auto_dv/evidence/gen_round2_request.md'
PREFLIGHT_DEFAULT = R / 'dv/auto_dv/evidence/gen_r1_preflight_classification.md'
MANIFEST_DEFAULT = '/proj_soc/user_dev/fzhang/ibex_dv_out/regress_round_1/manifest.yaml'

# The four entries the form calls "with margin"; the split itself is checked against the measured shares.
MARGIN_FOUR = ('gen_test_csr_access', 'gen_test_isa_cti', 'gen_test_isa_alu', 'gen_test_csr_trap_setup')


class Checker:
    def __init__(self, text: str, quiet: bool = False):
        self.text = text
        self.flat = re.sub(r'\s+', ' ', text)
        self.bad: list[str] = []
        self.ok = 0
        self.quiet = quiet

    def claim(self, what: str, pattern: str):
        hits = re.findall(pattern, self.flat)
        if len(hits) != 1:
            self._fail(f'{what}: {len(hits)} matches in the form, want exactly 1')
            return None
        return float(hits[0])

    def check(self, what: str, claimed, actual, tol: float = 0.0):
        if isinstance(claimed, str):
            claimed = self.claim(what, claimed)
        if claimed is None:
            return
        if abs(float(claimed) - float(actual)) <= tol:
            self.ok += 1
            if not self.quiet:
                print(f'ok   {what}: form {float(claimed):g} vs source {float(actual):g}')
        else:
            self._fail(f'{what}: form {float(claimed):g} vs source {float(actual):g}')

    def _fail(self, msg: str):
        self.bad.append(msg)
        if not self.quiet:
            print(f'BAD  {msg}')


def per_entry_mean(runs, pred) -> dict[str, float]:
    by = collections.defaultdict(list)
    for r in runs:
        if pred(r):
            by[r['test']].append(r['wall_s'])
    return {t: sum(v) / len(v) for t, v in by.items()}


def bin_margins(runs) -> dict[str, tuple[int, int, float, int, int, int]]:
    """Per measured entry: declared bins, bins whose smallest hit count over the entry's runs is 1, that
    share, the median smallest count, bins at 3 or fewer, and the number of bin checks."""
    by = collections.defaultdict(list)
    for r in runs:
        if r.get('measured') and (r.get('fcov_check') or {}).get('bins'):
            by[r['test']].append(r['fcov_check']['bins'])
    out = {}
    for t, ds in by.items():
        keys = set().union(*[set(d) for d in ds])
        mins = {k: min(int(d[k]['count']) if k in d else 0 for d in ds) for k in keys}
        n1 = sum(1 for v in mins.values() if v == 1)
        srt = sorted(mins.values())
        out[t] = (len(keys), n1, round(100 * n1 / len(keys), 1), srt[len(srt) // 2],
                  sum(1 for v in mins.values() if v <= 3), sum(len(d) for d in ds))
    return out


def run_checks(form_text: str, manifest: dict, preflight_text: str, quiet: bool = False) -> Checker:
    c = Checker(form_text, quiet)
    runs = manifest['runs']
    walls = [r['wall_s'] for r in runs]

    c.check('regression wall_s', r'\| regression wall clock \| ([\d.]+) s', round(manifest['wall_s'], 1), 0.05)
    c.check('runs', r'\| runs \| (\d+) \|', len(runs))
    c.check('sum of per-run wall', r'\| sum of per-run wall \| ([\d.]+) s', round(sum(walls), 1), 0.05)
    c.check('measured sum', r'sum of per-run wall \| [\d.]+ s \(measured ([\d.]+),',
            round(sum(r['wall_s'] for r in runs if r.get('measured')), 1), 0.05)
    c.check('unmeasured sum', r'unmeasured ([\d.]+)\)',
            round(sum(r['wall_s'] for r in runs if not r.get('measured')), 1), 0.05)
    c.check('mean per-run wall', r'\| per-run wall \| mean ([\d.]+) s', round(statistics.mean(walls), 1), 0.05)
    c.check('min per-run wall', r'per-run wall \| mean [\d.]+ s, min ([\d.]+) s', round(min(walls), 1), 0.05)
    c.check('max per-run wall', r'min [\d.]+ s, max ([\d.]+) s', round(max(walls), 1), 0.05)

    meas = per_entry_mean(runs, lambda r: r.get('measured'))
    pmp = per_entry_mean(runs, lambda r: 'pmp' in r['test'])
    per_seed_12 = sum(meas.values())
    per_seed_pmp = sum(pmp.values())
    four = sum(meas[t] for t in MARGIN_FOUR if t in meas)

    c.check('one seed, the measured set', r'twelve measured entries costs ([\d.]+) s', round(per_seed_12, 1), 0.05)
    c.check('one seed, the pmp entries', r'PMP entries costs ([\d.]+) s', round(per_seed_pmp, 1), 0.05)
    c.check('one seed, the four with margin', r'12 x ([\d.]+) = ', round(four, 1), 0.05)
    c.check('9 seeds on the pmp entries', r'three entries, about (\d+) s of run time', round(9 * per_seed_pmp), 0.5)
    c.check('9 seeds on the measured set', r'existing entries would cost about (\d+) s', round(9 * per_seed_12), 0.5)
    c.check('12-seed pre-flight, the twelve', r'is about (\d+) s of run time; a 40-seed', round(12 * per_seed_12), 0.5)
    c.check('40-seed pre-flight, the twelve', r'a 40-seed pre-flight is about (\d+) s', round(40 * per_seed_12), 0.5)
    c.check('12-seed pre-flight, the four', r'entries with margin costs about (\d+) s', round(12 * four), 0.5)
    c.check('12-seed pre-flight, the eight', r'over the eight without it, about (\d+) s',
            round(12 * (per_seed_12 - four)), 0.5)
    c.check('parallel speedup', r'parallel speedup of about ([\d.]+) ', round(sum(walls) / manifest['wall_s'], 1), 0.05)

    margins = bin_margins(runs)
    rows = re.findall(r'^\| (gen_test_\w+) \| (\d+) \| (\d+) \| ([\d.]+)% \| (\d+) \|$', form_text, re.M)
    c.check('margin table row count', len(rows), len(margins))
    for name, nb, n1, pct, med in rows:
        got = margins.get(name)
        if got is None:
            c._fail(f'{name}: in the margin table and not in the manifest')
            continue
        c.check(f'{name} declared bins', float(nb), got[0])
        c.check(f'{name} bins hit once', float(n1), got[1])
        c.check(f'{name} share', float(pct), got[2], 0.05)
        c.check(f'{name} median smallest count', float(med), got[3])

    tot_bins = sum(v[0] for v in margins.values())
    tot_n1 = sum(v[1] for v in margins.values())
    tot_le3 = sum(v[4] for v in margins.values())
    tot_checks = sum(v[5] for v in margins.values())
    c.check('margin table total bins', r'\| ALL TWELVE \| (\d+) \|', tot_bins)
    c.check('margin table total hit once', r'\| ALL TWELVE \| \d+ \| (\d+) \|', tot_n1)
    c.check('margin table total share', r'\| ALL TWELVE \| \d+ \| \d+ \| ([\d.]+)%',
            round(100 * tot_n1 / tot_bins, 1), 0.05)
    c.check('prose bins hit once', r'(\d+) of the \d+ declared bins, a third', tot_n1)
    c.check('prose declared bins', r'of the (\d+) declared bins, a third', tot_bins)
    c.check('bin checks', r'and (\d+) of \d+ bin checks', tot_checks)
    c.check('bins hit three or fewer', r'(\d+) of them, [\d.]+ percent, were hit three times or fewer', tot_le3)
    c.check('share hit three or fewer', r'of them, ([\d.]+) percent, were hit three times or fewer',
            round(100 * tot_le3 / tot_bins, 1), 0.05)

    states = collections.Counter()
    for r in runs:
        for v in ((r.get('fcov_check') or {}).get('bins') or {}).values():
            states[v.get('state')] += 1
    c.check('bin states that are not HIT', 0.0, sum(v for k, v in states.items() if k != 'HIT'))

    srows = {n: (int(d), int(s), int(sd), int(u)) for n, d, s, sd, u in
             re.findall(r'^\| (gen_test_\w+) \| (\d+) \| 3 \| (\d+) \| (\d+) \| (\d+) \|$', preflight_text, re.M)}
    frows = re.findall(r'^\| (gen_test_\w+) \| (\d+) \| 3 \| (\d+) \| (\d+) \| (\d+) \|$', form_text, re.M)
    c.check('pre-flight rows quoted', float(len(frows)), len(srows))
    for n, d, s, sd, u in frows:
        got = srows.get(n)
        if got is None:
            c._fail(f'{n}: quoted from the pre-flight and not in it')
            continue
        for lbl, val, act in (('declared', d, got[0]), ('stable', s, got[1]),
                              ('seed-dependent', sd, got[2]), ('union', u, got[3])):
            c.check(f'{n} {lbl}', float(val), act)
    c.check('stable total', r'the (\d+) stable ones', sum(v[1] for v in srows.values()))
    c.check('seed-dependent total', r'The (\d+) seed-dependent bins sit', sum(v[2] for v in srows.values()))
    c.check('entries with seed-dependent bins', 4.0, sum(1 for v in srows.values() if v[2] > 0))

    rot = re.findall(r'^\| (\d+) \| ([\d.]+) \| ([\d.]+) \|$', form_text, re.M)
    if not rot:
        c._fail('rule-of-three table: no rows found')
    for n, ub, miss in rot:
        n = int(n)
        c.check(f'rate ruled out at n={n}', float(ub), round(1 - 0.05 ** (1.0 / n), len(ub.split('.')[1])), 5e-4)
        c.check(f'miss of a 0.25 bin at n={n}', float(miss), round(0.75 ** n, len(miss.split('.')[1])), 5e-6)
    c.check('lower bound at 3 of 3', r'per-seed rate of only ([\d.]+), since', round(0.05 ** (1.0 / 3), 3), 5e-4)
    return c


SYNTH_MANIFEST = {
    'wall_s': 100.0,
    'runs': [
        {'test': 'gen_test_a', 'measured': True, 'wall_s': 10.0,
         'fcov_check': {'bins': {'x.cp.a': {'state': 'HIT', 'count': '1'}, 'x.cp.b': {'state': 'HIT', 'count': '7'}}}},
        {'test': 'gen_test_a', 'measured': True, 'wall_s': 20.0,
         'fcov_check': {'bins': {'x.cp.a': {'state': 'HIT', 'count': '4'}, 'x.cp.b': {'state': 'HIT', 'count': '9'}}}},
        {'test': 'gen_test_b', 'measured': False, 'wall_s': 30.0},
    ],
}
SYNTH_FORM = """| regression wall clock | 100.0 s (x to y) |
| runs | 3 |
| sum of per-run wall | 60.0 s (measured 30.0, unmeasured 30.0) |
| per-run wall | mean 20.0 s, min 10.0 s, max 30.0 s |
| entry | declared bins | hit once | share | median |
|---|---|---|---|---|
| gen_test_a | 2 | 1 | 50.0% | 7 |
| ALL TWELVE | 2 | 1 | 50.0% | - |
1 of the 2 declared bins, a third of it, were thin, and 4 of 4 bin checks passed.
1 of them, 50.0 percent, were hit three times or fewer.
"""


def self_test() -> int:
    """The machinery, on a synthetic manifest and form: a true form passes, a perturbed one fails, and a
    form that drops a claim fails rather than passing with one fewer check."""
    def run(form: str):
        c = Checker(form, quiet=True)
        runs = SYNTH_MANIFEST['runs']
        walls = [r['wall_s'] for r in runs]
        c.check('wall', r'\| regression wall clock \| ([\d.]+) s', round(SYNTH_MANIFEST['wall_s'], 1), 0.05)
        c.check('runs', r'\| runs \| (\d+) \|', len(runs))
        c.check('sum', r'\| sum of per-run wall \| ([\d.]+) s', round(sum(walls), 1), 0.05)
        c.check('mean', r'\| per-run wall \| mean ([\d.]+) s', round(statistics.mean(walls), 1), 0.05)
        m = bin_margins(runs)
        for name, nb, n1, pct, med in re.findall(r'^\| (gen_test_\w+) \| (\d+) \| (\d+) \| ([\d.]+)% \| (\d+) \|$', form, re.M):
            got = m.get(name)
            if got is None:
                c._fail(f'{name} absent')
                continue
            c.check(f'{name} bins', float(nb), got[0])
            c.check(f'{name} hit once', float(n1), got[1])
            c.check(f'{name} share', float(pct), got[2], 0.05)
            c.check(f'{name} median', float(med), got[3])
        c.check('checks', r'and (\d+) of \d+ bin checks', sum(v[5] for v in m.values()))
        return c

    cases = [
        ('a true form passes', SYNTH_FORM, True),
        ('a wrong bin count fails', SYNTH_FORM.replace('| gen_test_a | 2 |', '| gen_test_a | 3 |'), False),
        ('a wrong wall clock fails', SYNTH_FORM.replace('| 100.0 s', '| 101.0 s'), False),
        ('a wrong share fails', SYNTH_FORM.replace('50.0% | 7 |', '90.0% | 7 |'), False),
        ('a dropped claim fails, it does not silently pass', SYNTH_FORM.replace('| runs | 3 |\n', ''), False),
        ('an entry the manifest lacks fails', SYNTH_FORM.replace('| gen_test_a | 2 |', '| gen_test_zz | 2 |'), False),
    ]
    ok = True
    for name, form, want_pass in cases:
        c = run(form)
        got_pass = not c.bad
        good = got_pass == want_pass
        ok = ok and good
        print(f'SELF-TEST {"ok " if good else "BAD"}  {name}: {"pass" if got_pass else "fail"}, want '
              f'{"pass" if want_pass else "fail"}')
    print('gen_round_form_check --self-test:', 'PASS' if ok else 'FAIL')
    return 0 if ok else 1


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--form', default=str(FORM_DEFAULT))
    ap.add_argument('--manifest', default=MANIFEST_DEFAULT)
    ap.add_argument('--preflight', default=str(PREFLIGHT_DEFAULT))
    ap.add_argument('--self-test', action='store_true')
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    for p in (a.form, a.preflight):
        if not pathlib.Path(p).is_file():
            print(f'{p}: not a file')
            return 2
    if not pathlib.Path(a.manifest).is_file():
        print(f'{a.manifest}: not a file (the form cannot be checked without the round it cites)')
        return 2
    c = run_checks(pathlib.Path(a.form).read_text(encoding='ascii'),
                   yaml.safe_load(open(a.manifest)),
                   pathlib.Path(a.preflight).read_text(encoding='ascii'))
    print()
    if c.bad:
        print(f'gen_round_form_check: FAIL, {len(c.bad)} claim(s) did not reproduce')
        for b in c.bad:
            print(f'  {b}')
        return 1
    print(f'gen_round_form_check: PASS, {c.ok} numeric claims parsed from the form all reproduce')
    return 0


if __name__ == '__main__':
    sys.exit(main())
