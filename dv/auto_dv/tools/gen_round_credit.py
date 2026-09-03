#!/usr/bin/env python3
"""Per-item credit of a measured round (gen_test_plan.md Section 0 crediting rules; DV Lead).

An item of a group hosted by a test in the round is CREDITED when every seed of that test passed (verdict PASS; XFAIL for an
expected-fail item), its fire check fired in every seed (GEN_TEST_FIRE fire_tp_<area>_<nnn> ok=True in the sim stdout), every
bin of the item was HIT in the round's fcov checks (a bins_not_hit bin of the test's manifest counts as unhit, rule (g)) and the
item is under no measurement hold (whichever hold sections the plan carries, discovered by gen_plan_holds; a held item is recorded,
not credited). Red fixtures (names ending in _red, red_fixture / red_expect entries, RED-OK verdicts) host no items and are excluded from the
item credit; the per-test table lists every run, reds included. Everything else is recorded with its reason. Witness bins (CG-WIT-001) are listed, never credited, until the covergroup exists (T-179).

Usage:
  gen_round_credit.py --regress-manifest <outdir>/manifest.yaml [--plan-dir dv/auto_dv/docs] [--fcov-dir dv/auto_dv/fcov_expectations]
                      [--csv <out.csv>] [--md <out.md>] [--round <n>]
  gen_round_credit.py --self-test        # synthetic runs: credited / held / unhit / fire-fail / not-run cases
"""
import re, csv, sys, argparse, pathlib, collections, hashlib, shlex, yaml
R = pathlib.Path(__file__).resolve()
while not (R / 'dv/auto_dv/contract').is_dir():
    if R.parent == R: sys.exit('repo root not found (no dv/auto_dv/contract above this file)')
    R = R.parent
sys.path.insert(0, str(R / 'dv/auto_dv/tools')); from gen_plan_holds import hold_items  # one home for the hold-section discovery
WIT_CG_PLAN = 'CG-WIT-001'
HEADINGS = {  # fixed heading texts by id, so the printed invocation carries the id instead of quoted free text (a semicolon inside quotes broke a naive copy)
    'round0-probe': 'Round-0 PROBE crediting (probe of 37c7ecb refused as a round, LOG-046; 0 credited, every hosted item NOT-RUN-CLEAN)',
}

def plan_inputs_digest(plan_dir):
    """sha256 (first 12) over exactly what this tool reads from the plan set: the item headers with their Test group, Tier and Expected fields, the
    hold sections, gen_trace_tp_bin.csv and gen_trace_witness_ids.csv. Independent of the plan's embedded Section 1.7, so a report reproduces
    from the commit that embeds it."""
    plan = (plan_dir / 'gen_test_plan.md').read_text(); h = hashlib.sha256()
    for m in re.finditer(r'^### (TP-[A-Z]+-\d{3}):(.*?)(?=^### |^## |^# |\Z)', plan, re.M | re.S):
        b = m.group(2)
        for f in ('Test group', 'Tier', 'Expected'):
            fm = re.search(r'^- ' + f + r': ([^\n]*)', b, re.M); h.update((m.group(1) + '|' + f + '|' + (fm.group(1).strip() if fm else '') + '\n').encode())
    for sec, tag in hold_items(plan)[1]: h.update((sec + ' ' + tag + '\n').encode())
    for tid, tags in sorted(hold_items(plan)[0].items()): h.update((tid + ':' + ','.join(tags) + '\n').encode())
    h.update((plan_dir / 'gen_trace_tp_bin.csv').read_bytes()); h.update((plan_dir / 'gen_trace_witness_ids.csv').read_bytes())
    return h.hexdigest()[:12]

def load_plan(plan_dir):
    plan = (plan_dir / 'gen_test_plan.md').read_text()
    items = {}
    for m in re.finditer(r'^### (TP-[A-Z]+-\d{3}):(.*?)(?=^### |^## |^# |\Z)', plan, re.M | re.S):
        b = m.group(2)
        g = re.search(r'^- Test group: (\S+)', b, re.M); e = re.search(r'^- Expected: ([^\n]*)', b, re.M); t = re.search(r'^- Tier: (\w+)', b, re.M)
        items[m.group(1)] = {'group': g.group(1) if g else '-', 'expected': (e.group(1).strip() if e else ''), 'tier': t.group(1) if t else '?'}
    holds, _sections = hold_items(plan)
    bins = collections.defaultdict(list)
    with open(plan_dir / 'gen_trace_tp_bin.csv', newline='') as f:
        for r in csv.DictReader(f): bins[r['tp_item']].append((r['covergroup'], r['coverpoint'], r['bin']))
    marked = {}
    with open(plan_dir / 'gen_trace_witness_ids.csv', newline='') as f:
        for r in csv.DictReader(f): marked[r['tp_item']] = r['marked'] == '1'
    return items, holds, bins, marked

def manifest_not_hit(fcov_dir, test):
    p = fcov_dir / f'{test}.fcov.yaml'
    if not p.exists(): return None, set()
    nh = set(); declared = set()
    for line in p.read_text().splitlines():
        m = re.match(r'# not_hit (\S+):', line)
        if m: nh.add(m.group(1))
    data = yaml.safe_load(p.read_text()) or {}
    for b in data.get('bins') or []: declared.add(b)
    return declared, nh

def fire_results(run):
    """{fire_tp_id: ok} from the run's sim stdout (GEN_TEST_FIRE lines); None when the log is unreadable."""
    p = run.get('sim_stdout_log') or run.get('sim_log')
    if not p or not pathlib.Path(p).exists(): return None
    out = {}
    for line in open(p, errors='replace'):
        m = re.search(r'GEN_TEST_FIRE (fire_tp_[a-z]+_\d{3}(?:_[a-z0-9_]+)?) ok=(True|False)', line)
        if m: out[m.group(1)] = (m.group(2) == 'True') and out.get(m.group(1), True)
    return out

def tp_of_fire(name):
    """fire_tp_<area>_<nnn>[_suffix] -> TP-<AREA>-<nnn> (the manifest generator's form; an item may have several suffixed checks)."""
    m = re.match(r'fire_tp_([a-z]+)_(\d{3})(?:_|$)', name); return f'TP-{m.group(1).upper()}-{m.group(2)}' if m else None

def is_red_fixture(run):
    """A red fixture never hosts plan items: name ending in _red, a red_fixture / red_expect entry, or a RED-OK verdict."""
    return str(run.get('test', '')).endswith('_red') or bool(run.get('red_fixture')) or bool(run.get('red_expect')) or run.get('verdict') == 'RED-OK'

def credit(items, holds, bins, marked, runs, fcov_of, fires_of):
    """runs: list of regression run dicts; fcov_of(test) -> (declared, not_hit); fires_of(run) -> {fire id: ok} or None."""
    by_test = collections.defaultdict(list)
    for r in runs:
        if not is_red_fixture(r): by_test[r['test']].append(r)
    rows = []; groups_seen = set()
    test_of_group = {}
    for test, rs in by_test.items():
        fired_items = set()
        for r in rs:
            fr = fires_of(r) or {}
            for k in fr:
                t = tp_of_fire(k)
                if t: fired_items.add(t)
        for t in fired_items:
            if t in items: test_of_group.setdefault(items[t]['group'], test)
    for tid, it in sorted(items.items()):
        g = it['group']; test = test_of_group.get(g)
        if not test: continue
        groups_seen.add(g); rs = by_test[test]
        seeds = [r['seed'] for r in rs]; verdicts = [r.get('verdict') for r in rs]
        xfail = it['expected'].startswith('expected-fail')
        run_ok = all(v == ('XFAIL' if xfail else 'PASS') for v in verdicts)
        fires = [fires_of(r) for r in rs]
        seen = [f for f in fires if f is not None and any(tp_of_fire(k) == tid for k in f)]
        fired = len(seen) == len(rs) and all(all(v for k, v in f.items() if tp_of_fire(k) == tid) for f in seen)
        declared, nh = fcov_of(test)
        unmet = set()
        for r in rs:
            fc = r.get('fcov_check') or {}
            for b, v in (fc.get('bins') or {}).items():
                if isinstance(v, dict) and v.get('state') != 'HIT': unmet.add(b)
            for b in fc.get('unmet_bins') or []: unmet.add(b)
        hit_all = set()
        for r in rs:
            fc = r.get('fcov_check') or {}
            for b, v in (fc.get('bins') or {}).items():
                if isinstance(v, dict) and v.get('state') == 'HIT': hit_all.add(b)
        item_bins = [(cg, cp, b) for cg, cp, b in bins.get(tid, []) if cg != WIT_CG_PLAN]
        wit_bins = [b for cg, cp, b in bins.get(tid, []) if cg == WIT_CG_PLAN]
        checked = any(isinstance((r.get('fcov_check') or {}).get('bins'), dict) and (r.get('fcov_check') or {}).get('bins') for r in rs)
        unhit = []
        for cg, cp, b in item_bins:
            tok = f'{cg}.{cp}.{b}'; tail = f'.{cp}.{b}'   # manifests name bins gen_<impl>_cg.<cp>.<bin>: match on the coverpoint.bin tail
            if any(x.endswith(tail) for x in nh): unhit.append(tok + ' (bins_not_hit)'); continue
            if declared is not None and not any(x.endswith(tail) for x in declared): unhit.append(tok + ' (not declared)'); continue
            if not any(x.endswith(tail) for x in hit_all): unhit.append(tok)   # a bin is credited only when a seed's fcov check reports it HIT
        held = holds.get(tid, [])
        reasons = sorted({(r.get('reason') or '')[:70] for r in rs if r.get('verdict') != ('XFAIL' if xfail else 'PASS')})
        if not run_ok: status = 'NOT-RUN-CLEAN (' + '; '.join(reasons)[:140] + ')'
        elif not checked: status = 'UNVERIFIED (no fcov check with per-bin results in the round)'
        elif not seen: status = 'NOT-FIRED (no fire line: not built or not reached)'
        elif not fired: status = 'FIRE-FAIL'
        elif held: status = 'HELD (' + ', '.join(held) + ')'
        elif unhit: status = f'UNHIT ({len(unhit)} of {len(item_bins)} bins)'
        else: status = 'CREDITED'
        rows.append({'item': tid, 'group': g, 'test': test, 'tier': it['tier'], 'seeds': len(seeds), 'verdicts': '/'.join(sorted(set(str(v) for v in verdicts))),
                     'fired': 'yes' if fired else ('no' if seen else 'none'), 'bins': len(item_bins), 'bins_unhit': len(unhit), 'unhit_list': '; '.join(unhit),
                     'witness_bins': len(wit_bins), 'witness_marked': 'yes' if marked.get(tid) else 'no', 'hold': ','.join(held), 'status': status})
    return rows, groups_seen

def round_header(man, runs, invocation=''):
    su = man.get('summary') or {}; fc = man.get('fcov') or {}; g = man.get('git') or {}
    head = g.get('head') or g.get('sha') or str(g)[:40]
    return (invocation + f"Regression {man.get('outdir') or man.get('tag')}: status {man.get('status')}, source {man.get('source') or 'head mode'}, git {head}; {len(runs)} runs: pass {su.get('pass')}, "
            f"fail {su.get('fail')}, xfail {su.get('xfail')}, red_ok {su.get('red_ok')}, timeout {su.get('timeout')}, not_run {su.get('not_run')}; fcov checks {fc.get('totals')}; covergroups_exist {fc.get('covergroups_exist')}; "
            f"clean regression (gen_round.py hard rule): {'yes' if su.get('fail') in (0, '0') and su.get('timeout') in (0, '0') and su.get('not_run') in (0, '0') else 'NO'}.")

def render_md(rows, round_no, header='', tests=None, heading=None):
    areas = collections.defaultdict(lambda: collections.Counter())
    for r in rows: areas[r['item'].split('-')[1]][r['status'].split(' ')[0]] += 1
    title = heading or f'Round-{round_no} credit'
    L = [f'## 1.7 {title} (generated from the regression manifest and sim logs; {len(rows)} items in {len({r["group"] for r in rows})} hosted groups)', '', header, '',
         '| Area | Items hosted | CREDITED | HELD | UNHIT | FIRE-FAIL | NOT-FIRED | NOT-RUN-CLEAN | UNVERIFIED |', '|---|---|---|---|---|---|---|---|---|']
    for a, c in sorted(areas.items()):
        L.append(f"| {a} | {sum(c.values())} | {c['CREDITED']} | {c['HELD']} | {c['UNHIT']} | {c['FIRE-FAIL']} | {c['NOT-FIRED']} | {c['NOT-RUN-CLEAN']} | {c['UNVERIFIED']} |")
    tot = collections.Counter(r['status'].split(' ')[0] for r in rows)
    L += ['', f"Total: {len(rows)} items hosted; credited {tot['CREDITED']}; held {tot['HELD']}; unhit {tot['UNHIT']}; fire-fail {tot['FIRE-FAIL']}; not fired {tot['NOT-FIRED']}; not run clean {tot['NOT-RUN-CLEAN']}; unverified {tot['UNVERIFIED']}.",
          f"Witness bins of hosted items: {sum(r['witness_bins'] for r in rows)} (unscored until T-179; listed, never credited).", '']
    if tests:
        L += ['Per test (every run of the regression, red fixtures included; the item table below excludes red fixtures, which host no items):', '', '| Test | Seeds | Verdicts | Distinct reasons |', '|---|---|---|---|'] + [f"| {t} | {n} | {v} | {rs} |" for t, n, v, rs in tests] + ['']
    L += ['| Item | Group | Test | Seeds | Verdicts | Fired | Bins | Unhit | Hold | Status |', '|---|---|---|---|---|---|---|---|---|---|']
    for r in rows: L.append(f"| {r['item']} | {r['group']} | {r['test']} | {r['seeds']} | {r['verdicts']} | {r['fired']} | {r['bins']} | {r['bins_unhit']} | {r['hold'] or '-'} | {r['status']} |")
    return '\n'.join(L) + '\n'

def self_test():
    items = {'TP-AA-001': {'group': 'gen_aa', 'expected': 'pass', 'tier': 'smoke'}, 'TP-AA-002': {'group': 'gen_aa', 'expected': 'pass', 'tier': 'smoke'},
             'TP-AA-003': {'group': 'gen_aa', 'expected': 'pass', 'tier': 'smoke'}, 'TP-AA-004': {'group': 'gen_aa', 'expected': 'pass', 'tier': 'smoke'},
             'TP-BB-001': {'group': 'gen_bb', 'expected': 'pass', 'tier': 'smoke'}, 'TP-CC-001': {'group': 'gen_cc', 'expected': 'pass', 'tier': 'smoke'}}
    holds = {'TP-AA-003': ['T-136']}
    bins = {'TP-AA-001': [('CG-AA-001', 'cp_x', 'b0')], 'TP-AA-002': [('CG-AA-001', 'cp_x', 'b1')], 'TP-AA-003': [('CG-AA-001', 'cp_x', 'b2')], 'TP-AA-004': [('CG-AA-001', 'cp_x', 'b3'), (WIT_CG_PLAN, 'cp_clause', 'w_tp_aa_004')],
            'TP-BB-001': [('CG-BB-001', 'cp_y', 'b0')], 'TP-CC-001': []}
    marked = {'TP-AA-004': False}
    fc = {'status': 'UNHIT', 'bins': {'gen_aa_cg.cp_x.b0': {'state': 'HIT'}, 'gen_aa_cg.cp_x.b1': {'state': 'UNHIT'}, 'gen_aa_cg.cp_x.b2': {'state': 'HIT'}, 'gen_aa_cg.cp_x.b3': {'state': 'HIT'}}, 'unmet_bins': ['gen_aa_cg.cp_x.b1']}
    runs = [{'test': 'gen_test_aa', 'seed': 1, 'verdict': 'PASS', 'fcov_check': fc}, {'test': 'gen_test_aa', 'seed': 2, 'verdict': 'PASS', 'fcov_check': fc},
            {'test': 'gen_test_bb', 'seed': 1, 'verdict': 'FAIL', 'fcov_check': {}}]
    fires = {('gen_test_aa', 1): {'fire_tp_aa_001': True, 'fire_tp_aa_002': True, 'fire_tp_aa_003': True, 'fire_tp_aa_004': False},
             ('gen_test_aa', 2): {'fire_tp_aa_001': True, 'fire_tp_aa_002': True, 'fire_tp_aa_003': True, 'fire_tp_aa_004': True}, ('gen_test_bb', 1): {'fire_tp_bb_001': True}}
    rows, _ = credit(items, holds, bins, marked, runs, lambda t: ({'gen_aa_cg.cp_x.b0', 'gen_aa_cg.cp_x.b1', 'gen_aa_cg.cp_x.b2', 'gen_aa_cg.cp_x.b3'}, set()) if t == 'gen_test_aa' else (set(), set()), lambda r: fires[(r['test'], r['seed'])])
    got = {r['item']: r['status'].split(' ')[0] for r in rows}
    want = {'TP-AA-001': 'CREDITED', 'TP-AA-002': 'UNHIT', 'TP-AA-003': 'HELD', 'TP-AA-004': 'FIRE-FAIL', 'TP-BB-001': 'NOT-RUN-CLEAN'}
    ok = got == want and 'TP-CC-001' not in got
    print('SELF-TEST', 'ok ' if ok else 'BAD', got, '| unhosted item excluded:', 'TP-CC-001' not in got)
    # a bins_not_hit bin counts as unhit even when the checker never saw it
    rows2, _ = credit(items, holds, bins, marked, runs[:2], lambda t: ({'gen_aa_cg.cp_x.b1', 'gen_aa_cg.cp_x.b2', 'gen_aa_cg.cp_x.b3'}, {'gen_aa_cg.cp_x.b0'}), lambda r: fires[(r['test'], r['seed'])])
    r1 = [r for r in rows2 if r['item'] == 'TP-AA-001'][0]
    ok2 = r1['status'].startswith('UNHIT') and 'bins_not_hit' in r1['unhit_list']
    print('SELF-TEST', 'ok ' if ok2 else 'BAD', 'rule (g): a bins_not_hit bin is unhit for the plan:', r1['status'], r1['unhit_list'])
    rows3, _ = credit(items, holds, bins, marked, [{'test': 'gen_test_aa', 'seed': 1, 'verdict': 'PASS', 'fcov_check': None}], lambda t: (set(), set()), lambda r: fires[('gen_test_aa', 1)])
    ok3 = all(r['status'].startswith('UNVERIFIED') for r in rows3 if r['item'] in ('TP-AA-001', 'TP-AA-002'))
    print('SELF-TEST', 'ok ' if ok3 else 'BAD', 'no fcov check in the round: UNVERIFIED, never credited:', {r['item']: r['status'][:10] for r in rows3})
    return 0 if ok and ok2 and ok3 else 1

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--regress-manifest'); ap.add_argument('--plan-dir', default=str(R / 'dv/auto_dv/docs')); ap.add_argument('--fcov-dir', default=str(R / 'dv/auto_dv/fcov_expectations'))
    ap.add_argument('--csv'); ap.add_argument('--md'); ap.add_argument('--round', type=int, default=0); ap.add_argument('--plan-sha', default='unlabelled', help='landing label printed in the report header; not a claim about which commit was read (the header prints the input digest)'); ap.add_argument('--heading', default=None, help='section title override (free text; prefer --heading-id, whose id prints in the invocation)'); ap.add_argument('--heading-id', default=None, choices=sorted(HEADINGS), help='a fixed heading from the HEADINGS table'); ap.add_argument('--self-test', action='store_true')
    a = ap.parse_args()
    if a.self_test: sys.exit(self_test())
    if not a.regress_manifest: sys.exit('usage: --regress-manifest <manifest.yaml> or --self-test')
    items, holds, bins, marked = load_plan(pathlib.Path(a.plan_dir))
    man = yaml.safe_load(open(a.regress_manifest)); runs = man.get('runs') or []
    fdir = pathlib.Path(a.fcov_dir)
    rows, groups = credit(items, holds, bins, marked, runs, lambda t: manifest_not_hit(fdir, t), fire_results)
    by_test = collections.defaultdict(list)
    for r in runs: by_test[r['test']].append(r)
    tests = [(t, len(rs), '/'.join(sorted({str(r.get('verdict')) for r in rs})), '; '.join(sorted({(r.get('reason') or '-')[:60] for r in rs}))) for t, rs in sorted(by_test.items())]
    if a.heading_id: a.heading = HEADINGS[a.heading_id]
    def rel(p):  # the invocation names the files it wrote, clone-relative when they live in the clone
        q = pathlib.Path(p).resolve()
        return str(q.relative_to(R.resolve())) if q.is_relative_to(R.resolve()) else str(q)
    inv = (f"Invocation, byte for byte (copy the whole line; a quoted heading may contain semicolons): python3 dv/auto_dv/tools/gen_round_credit.py --regress-manifest {shlex.quote(a.regress_manifest)} --plan-sha {shlex.quote(a.plan_sha)} --round {a.round}"
           + (f" --heading-id {a.heading_id}" if a.heading_id else (f" --heading {shlex.quote(a.heading)}" if a.heading else ''))
           + (f" --csv {shlex.quote(rel(a.csv))}" if a.csv else '') + (f" --md {shlex.quote(rel(a.md))}" if a.md else '') + f"; regression manifest sha256 {hashlib.sha256(open(a.regress_manifest, 'rb').read()).hexdigest()}; plan inputs read (item headers with group / tier / expected, hold sections, gen_trace_tp_bin.csv, gen_trace_witness_ids.csv) digest {plan_inputs_digest(pathlib.Path(a.plan_dir))}; landing label {a.plan_sha} (the --plan-sha argument, a label only, not the commit whose plan was read). ")
    hdr = round_header(man, runs, inv)
    md = render_md(rows, a.round, hdr, tests, a.heading)
    if a.md:
        lines = md.splitlines(); summ = []; skip_sep = False
        for l in lines:
            if l.startswith('| Item | Group | Test'): skip_sep = True; continue
            if skip_sep and l.startswith('|---'): skip_sep = False; continue
            if l.startswith('| TP-'): continue
            summ.append(l)
        while summ and not summ[-1].strip(): summ.pop()
        pathlib.Path(a.md).with_name(pathlib.Path(a.md).stem + '_summary.md').write_text('\n'.join(summ).rstrip('\n') + '\n')
    if a.csv:
        with open(a.csv, 'w', newline='') as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0].keys()) if rows else ['item']); w.writeheader(); w.writerows(rows)
    if a.md: pathlib.Path(a.md).write_text(md)
    print(md.splitlines()[0]); print([l for l in md.splitlines() if l.startswith('Total:')][0])
    print(f'plan: {len(items)} items, holds {sum(len(v) for v in holds.values())} entries, runs {len(runs)} over {len({r["test"] for r in runs})} tests, hosted groups {len(groups)}')

if __name__ == '__main__': main()
