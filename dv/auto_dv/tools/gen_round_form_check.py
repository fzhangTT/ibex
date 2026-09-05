#!/usr/bin/env python3
"""Check a round request form's numbers against the sources they claim to come from.

Every value this tool checks is PARSED OUT OF THE FORM and compared with a value recomputed from the
regression manifest, the pre-flight record or arithmetic. Nothing is restated here, so a wrong figure in the
form fails instead of being repeated by its own checker. Prose claims are matched against a FLATTENED copy of
the form, so a sentence wrapped across lines is still one claim; table rows are matched line-anchored.

A claim the checker cannot find in the form is a FAILURE, never a skip: a form that drops a figure must fail
rather than pass with one fewer check.

SCOPE, stated because an overstatement in a checker is worse than one in prose: this checks the numbers listed
in run_checks, not every numeral in the document. The count it prints is the number of claims it compared.

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
# The committed copy of the round's regression manifest, byte-identical to the out-tree original, so the
# checker and its self-test run on a machine that cannot see the scratch filesystem.
MANIFEST_DEFAULT = R / 'dv/auto_dv/evidence/gen_round_0/gen_regress_manifest.yaml'


class Checker:
    def __init__(self, text, quiet=False):
        self.text = text
        self.flat = re.sub(r'\s+', ' ', text)
        self.bad = []
        self.ok = 0
        self.quiet = quiet

    def claim(self, what, pattern):
        hits = re.findall(pattern, self.flat)
        if len(hits) != 1:
            self.fail(f'{what}: {len(hits)} matches in the form, want exactly 1')
            return None
        return float(hits[0])

    def check(self, what, claimed, actual, tol=0.0):
        if isinstance(claimed, str):
            claimed = self.claim(what, claimed)
        if claimed is None:
            return
        if abs(float(claimed) - float(actual)) <= tol:
            self.ok += 1
            if not self.quiet:
                print(f'ok   {what}: form {float(claimed):g} vs source {float(actual):g}')
        else:
            self.fail(f'{what}: form {float(claimed):g} vs source {float(actual):g}')

    def same(self, what, claimed, actual):
        """Compare non-numeric claims, such as which entries the form names."""
        if claimed == actual:
            self.ok += 1
            if not self.quiet:
                print(f'ok   {what}: form {claimed} vs source {actual}')
        else:
            self.fail(f'{what}: form {claimed} vs source {actual}')

    def fail(self, msg):
        self.bad.append(msg)
        if not self.quiet:
            print(f'BAD  {msg}')


def per_entry_mean(runs, pred):
    by = collections.defaultdict(list)
    for r in runs:
        if pred(r):
            by[r['test']].append(r['wall_s'])
    return {t: sum(v) / len(v) for t, v in by.items()}


def bin_margins(runs):
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
        out[t] = (len(keys), n1, round(100 * n1 / len(keys), 1), statistics.median(mins.values()),
                  sum(1 for v in mins.values() if v <= 3), sum(len(d) for d in ds))
    return out


def named_entries(flat, pattern):
    """The short entry names the form lists in one sentence, as full entry names."""
    m = re.search(pattern, flat)
    if not m:
        return None
    return {'gen_test_' + n for n in re.findall(r'[a-z][a-z0-9_]*', m.group(1)) if n != 'and'}


def check_selection(c):
    """Section 1's restated table and Section 7's rows, recomputed by CALLING the flow.

    An import failure is a FAILURE and not a skip: a form whose selection figures cannot be verified must not
    pass on the strength of the ones that can.
    """
    sys.path.insert(0, str(R / 'dv/auto_dv/flow'))
    try:
        import gen_flow_util as U
        import gen_fcov as F
    except Exception as e:                                  # noqa: BLE001 - reported, never swallowed
        c.fail(f'selection checks: the flow would not import ({e})')
        return
    tl = U.load_testlist(R / 'dv/auto_dv/flow/gen_testlist.yaml')
    sel = U.select_tests(tl, 'full', None, None)
    base = 20260904
    seeds = {t['name']: len(U.seeds_for_test(t, None, base)) for t in sel}
    meas = sorted([t for t in sel if t.get('fcov_expectation_file')], key=lambda x: x['name'])
    rendered = set(re.findall(r'covergroup\s+(gen_\w+_cg)\b',
                              (R / 'dv/auto_dv/env/gen_fcov_groups.svh').read_text(encoding='utf-8')))
    for tier, label in (('smoke', 'smoke at 9c28944'), ('targeted', 'targeted at 9c28944')):
        ents = [t for t in sel if t['tier'] == tier]
        c.check(f'{label} entries', rf'\| {re.escape(label)} \| (\d+) \|', len(ents))
        c.check(f'{label} runs', rf'\| {re.escape(label)} \| \d+ \| (\d+) \|', sum(seeds[t['name']] for t in ents))
        c.check(f'{label} measured runs', rf'\| {re.escape(label)} \| \d+ \| \d+ \| (\d+) \|',
                sum(seeds[t['name']] for t in ents if t.get('fcov_expectation_file')))
    c.check("plan entries", r"\| THE ROUND'S PLAN AT \w+ \| (\d+) \|", len(sel))
    c.check("plan runs", r"\| THE ROUND'S PLAN AT \w+ \| \d+ \| (\d+) \|", sum(seeds.values()))
    c.check("plan measured runs", r"\| THE ROUND'S PLAN AT \w+ \| \d+ \| \d+ \| (\d+) \|",
            sum(seeds[t['name']] for t in meas))
    total = 0
    for t in meas:
        man, errs = F.validate_manifest(pathlib.Path(t['fcov_expectation_file']), t['name'])
        if man is None or errs:
            c.fail(f"{t['name']}: manifest does not validate ({'; '.join(errs)})")
            continue
        bins = man.get('bins') or []
        total += len(bins)
        cgs = sorted({b.split('.')[0] for b in bins})
        built = [g for g in cgs if g in rendered]
        n = re.escape(t['name'])
        # The four-column shape with its "N of M" built cell is unique to Section 7; a bare
        # "| <entry> | <seeds> |" also matches Section 3's per-entry tables, so it is not usable here.
        rows = re.findall(rf'\| {n} \| (\d+) \| (\d+) \| (\d+) of (\d+) \|', c.flat)
        if len(rows) != 1:
            c.fail(f"{t['name']} row: {len(rows)} Section 7 rows in the form, want exactly 1")
            continue
        s_seeds, s_decl, s_built, s_cgs = (int(x) for x in rows[0])
        c.check(f"{t['name']} seeds", s_seeds, seeds[t['name']])
        c.check(f"{t['name']} declared", s_decl, len(bins))
        c.check(f"{t['name']} built", s_built, len(built))
        c.check(f"{t['name']} covergroups", s_cgs, len(cgs))
    c.check('declared total', r'declared sets total (\d+) bins', total)


def run_checks(form_text, manifest, preflight_text, quiet=False):
    c = Checker(form_text, quiet)
    check_selection(c)
    runs = manifest['runs']
    walls = [r['wall_s'] for r in runs]
    summary = manifest.get('summary') or {}
    fcov = (manifest.get('fcov') or {}).get('totals') or {}

    # Section 4, the cost table
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

    # The preamble's round outcome, from the manifest's own summary
    c.check('runs clean, numerator', r'outcome (\d+) of \d+ runs clean', summary.get('pass', -1))
    c.check('runs clean, denominator', r'outcome \d+ of (\d+) runs clean', summary.get('planned', -1))
    c.check('fcov checks passing, numerator', r'and (\d+) of \d+ fcov checks passing', fcov.get('pass', -1))
    c.check('fcov checks passing, denominator', r'and \d+ of (\d+) fcov checks passing', fcov.get('checked', -1))

    margins = bin_margins(runs)
    meas = per_entry_mean(runs, lambda r: r.get('measured'))
    pmp = per_entry_mean(runs, lambda r: 'pmp' in r['test'])
    per_seed_all = sum(meas.values())
    per_seed_pmp = sum(pmp.values())

    # Which entries the form calls "with margin" is DERIVED from the shares, not taken on trust.
    ranked = sorted(margins, key=lambda t: (margins[t][2], t))
    four_src, eight_src = set(ranked[:4]), set(ranked[4:])
    four_form = named_entries(c.flat, r'the pre-flight\'s priority: ([a-z0-9_, and]+?), all')
    eight_form = named_entries(c.flat, r'before a re-measurement: ([a-z0-9_, and]+?), every one')
    if four_form is None or eight_form is None:
        c.fail('the four with margin / the eight without: sentence not found in the form')
    else:
        c.same('the four with the smallest zero-margin share', sorted(four_form), sorted(four_src))
        c.same('the eight without margin', sorted(eight_form), sorted(eight_src))
    four = sum(meas[t] for t in (four_form or four_src) if t in meas)

    c.check('one seed, the measured set', r'measured entries costs ([\d.]+) s', round(per_seed_all, 1), 0.05)
    c.check('one seed, the pmp entries', r'PMP entries costs ([\d.]+) s', round(per_seed_pmp, 1), 0.05)
    c.check('one seed, the four with margin', r'12 x ([\d.]+) = ', round(four, 1), 0.05)
    c.check('9 seeds on the pmp entries', r'three entries, about (\d+) s of run time', round(9 * per_seed_pmp), 0.5)
    c.check('9 seeds on the measured set', r'existing entries would cost about (\d+) s', round(9 * per_seed_all), 0.5)
    c.check('12-seed pre-flight, the twelve', r'is about (\d+) s of run time; a 40-seed', round(12 * per_seed_all), 0.5)
    c.check('40-seed pre-flight, the twelve', r'a 40-seed pre-flight is about (\d+) s', round(40 * per_seed_all), 0.5)
    c.check('12-seed pre-flight, the four (section 3)', r'12 x [\d.]+ = about (\d+) s', round(12 * four), 0.5)
    c.check('12-seed pre-flight, the four (section 4)', r'entries with margin costs about (\d+) s', round(12 * four), 0.5)
    c.check('12-seed pre-flight, the eight', r'over the eight without it, about (\d+) s',
            round(12 * (per_seed_all - four)), 0.5)
    c.check('parallel speedup', r'parallel speedup of about ([\d.]+) ', round(sum(walls) / manifest['wall_s'], 1), 0.05)

    # Section 3.2, the margin table and the prose that reads off it
    rows = re.findall(r'^\| (gen_test_\w+) \| (\d+) \| (\d+) \| ([\d.]+)% \| ([\d.]+) \|$', form_text, re.M)
    c.check('margin table row count', len(rows), len(margins))
    for name, nb, n1, pct, med in rows:
        got = margins.get(name)
        if got is None:
            c.fail(f'{name}: in the margin table and not in the manifest')
            continue
        c.check(f'{name} declared bins', float(nb), got[0])
        c.check(f'{name} bins hit once', float(n1), got[1])
        c.check(f'{name} share', float(pct), got[2], 0.05)
        c.check(f'{name} median smallest count', float(med), got[3])
    # Every per-run mean the form states in prose is checked, and the form must state at least one: a
    # sentence naming a cost was wrong and unparsed until this was added.
    quoted = re.findall(r'([a-z][a-z0-9_]*) at ([\d.]+) s per run', c.flat)
    if not quoted:
        c.fail('no per-run mean stated in prose: the form must name at least one and it is checked')
    for short, val in quoted:
        full = 'gen_test_' + short
        if full not in meas:
            c.fail(f'{short} at {val} s per run: not a measured entry of this round')
            continue
        c.check(f'{short} per-run mean in prose', float(val), round(meas[full], 1), 0.05)

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

    # Section 3.4, the pre-flight table quoted from its record
    srows = {n: (int(d), int(s), int(sd), int(u)) for n, d, s, sd, u in
             re.findall(r'^\| (gen_test_\w+) \| (\d+) \| 3 \| (\d+) \| (\d+) \| (\d+) \|$', preflight_text, re.M)}
    frows = re.findall(r'^\| (gen_test_\w+) \| (\d+) \| 3 \| (\d+) \| (\d+) \| (\d+) \|$', form_text, re.M)
    c.check('pre-flight rows quoted', float(len(frows)), len(srows))
    for n, d, s, sd, u in frows:
        got = srows.get(n)
        if got is None:
            c.fail(f'{n}: quoted from the pre-flight and not in it')
            continue
        for lbl, val, act in (('declared', d, got[0]), ('stable', s, got[1]),
                              ('seed-dependent', sd, got[2]), ('union', u, got[3])):
            c.check(f'{n} {lbl}', float(val), act)
    c.check('stable total', r'the (\d+) stable ones', sum(v[1] for v in srows.values()))
    c.check('seed-dependent total', r'The (\d+) seed-dependent bins sit', sum(v[2] for v in srows.values()))
    WORDS = {1: 'one', 2: 'two', 3: 'three', 4: 'four', 5: 'five', 6: 'six', 7: 'seven', 8: 'eight'}
    n_sd = sum(1 for v in srows.values() if v[2] > 0)
    said = re.search(r'seed-dependent bins sit on (\w+)', c.flat)
    c.same('entries carrying seed-dependent bins', said.group(1) if said else None, WORDS.get(n_sd))

    # Section 3.5, the confidence table
    rot = re.findall(r'^\| (\d+) \| ([\d.]+) \| ([\d.]+) \|$', form_text, re.M)
    if not rot:
        c.fail('rule-of-three table: no rows found')
    for n, ub, miss in rot:
        n = int(n)
        c.check(f'rate ruled out at n={n}', float(ub), round(1 - 0.05 ** (1.0 / n), len(ub.split('.')[1])), 5e-4)
        c.check(f'miss of a 0.25 bin at n={n}', float(miss), round(0.75 ** n, len(miss.split('.')[1])), 5e-6)
    c.check('lower bound at 3 of 3', r'per-seed rate of only ([\d.]+), since', round(0.05 ** (1.0 / 3), 3), 5e-4)
    return c


def self_test():
    """Drive run_checks itself, on the committed form and manifest, with the real code path rather than a
    private subset: the true form must pass, and each perturbation must fail."""
    form = FORM_DEFAULT.read_text(encoding='ascii')
    pre = PREFLIGHT_DEFAULT.read_text(encoding='ascii')
    man = yaml.safe_load(open(MANIFEST_DEFAULT))

    def bump(pattern, repl):
        out, n = re.subn(pattern, repl, form, count=1)
        if n != 1:
            print(f'SELF-TEST BAD  fixture {pattern!r} matched {n} times in the form')
            return None
        return out

    cases = [('the committed form passes', form, True)]
    for name, pat, rep in [
        ('a wrong declared-bin count fails', r'\| gen_test_isa_alu \| 563 \|', '| gen_test_isa_alu | 564 |'),
        ('a wrong wall clock fails', r'\| regression wall clock \| 362\.9 s', '| regression wall clock | 372.9 s'),
        ('a wrong share fails', r'\| gen_test_mul_mul \| 338 \| 244 \| 72\.2%', '| gen_test_mul_mul | 338 | 244 | 62.2%'),
        ('a dropped claim fails, it does not silently pass', r'\| runs \| 53 \|\n', ''),
        ('naming the wrong four with margin fails', r"priority: csr_access, isa_cti", "priority: mul_mul, isa_cti"),
    ]:
        t = bump(pat, rep)
        if t is not None:
            cases.append((name, t, False))

    ok = True
    for name, text, want_pass in cases:
        c = run_checks(text, man, pre, quiet=True)
        got_pass = not c.bad
        good = got_pass == want_pass
        ok = ok and good
        detail = '' if got_pass else f' ({c.bad[0]})'
        print(f'SELF-TEST {"ok " if good else "BAD"}  {name}: {"pass" if got_pass else "fail"}, '
              f'want {"pass" if want_pass else "fail"}{"" if good else detail}')
    print('gen_round_form_check --self-test:', 'PASS' if ok else 'FAIL')
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--form', default=str(FORM_DEFAULT))
    ap.add_argument('--manifest', default=str(MANIFEST_DEFAULT))
    ap.add_argument('--preflight', default=str(PREFLIGHT_DEFAULT))
    ap.add_argument('--self-test', action='store_true')
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    for p in (a.form, a.preflight, a.manifest):
        if not pathlib.Path(p).is_file():
            print(f'{p}: not a file')
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
    print(f'gen_round_form_check: PASS, {c.ok} claims compared and all reproduce')
    return 0


if __name__ == '__main__':
    sys.exit(main())
