#!/usr/bin/env python3
"""Traceability / completeness check for the Ibex auto-DV plan set (DV_prompt.txt Section 4).

Inputs (dv/auto_dv/docs/): gen_feature_list.md, gen_test_plan.md, gen_fcov_plan.md,
gen_trace_feature_tp.csv, gen_trace_tp_bin.csv, gen_trace_witness_ids.csv; the rendered export event table
dv/auto_dv/tb/gen_tb_knobs.yaml (export_events) and, optionally, one build's build_manifest.yaml.
Exits 1 on any violation. Deterministic.

Options (export_sources entries may be "<source> <event>" strings or {source, event} maps):
  --knobs <path>           export event table (default dv/auto_dv/tb/gen_tb_knobs.yaml); a row whose event is
                           "<name>" is a wildcard and counts as ABSENT (gen_test_plan.md Section 0)
  --observed-field <key>   manifest key of Runtime's per-row first-seen list (T-140; default export_rows_observed): the sunset
                           un-marks an item only when EVERY export row is observed (LOG-028a); absent list = sunset refused
  --build-manifest <path>  a build's build_manifest.yaml. Its export_sources_emitted list (the rows the build's registered writers
                           emit; "<source> <event>" strings or {source, event} maps) only BOUNDS the cycle-clause sunset: it
                           sorts the marked items into renderable / emitted / gated. The observed-row list (--observed-field) DECIDES
                           it: a still-marked item whose export rows are all OBSERVED fails. export_sources (the rendered table)
                           only reports how many marked items are renderable.
                           Without it the tool reports the sunset input as unknown and does not fail on it.
"""
import re, csv, sys, argparse, collections, pathlib
R = pathlib.Path(__file__).resolve().parents[1]; D = R / 'docs'
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent)); from gen_plan_marker import TOKEN, WILDCARD_TOKENS, present  # one definition of the marker token and the wildcard rule
ap = argparse.ArgumentParser()
ap.add_argument('--knobs', default=str(R / 'tb' / 'gen_tb_knobs.yaml'))
ap.add_argument('--build-manifest', default=None)
# LOG-028a (the rule's text is gen_test_plan.md Section 0): an item sunsets only when every one of its export rows was OBSERVED
# in a retained run of the pinned build, from Runtime's per-row first-seen list; exclusion is by row, never by source; no list
# means refused.
ap.add_argument('--observed-field', default='export_rows_observed', help='manifest key of the observed-row list (T-140)')
ap.add_argument('--exclude-rows', default=None, help='rehearsal only, refused when the manifest carries the observed list: treat the emitted rows minus these (semicolon-separated) as the observed list')
args = ap.parse_args()
def blocks(text, prefix):
    return {m.group(1): m.group(2) for m in re.finditer(r'^### (' + prefix + r'-[A-Z]+-\d{3}):(.*?)(?=^### |^## |^# |\Z)', text, re.M | re.S)}
fl = (D/'gen_feature_list.md').read_text(); tp = (D/'gen_test_plan.md').read_text(); fc = (D/'gen_fcov_plan.md').read_text()
feats = blocks(fl, 'F'); tps = blocks(tp, 'TP'); cgs = blocks(fc, 'CG')
status = {}; target = {}
for f, b in feats.items():
    m = re.search(r'^- Status: (ACTIVE|ALIAS of (F-[A-Z]+-\d{3})|FOLDED into (F-[A-Z]+-\d{3}))', b, re.M)
    status[f] = m.group(1).split()[0] if m else 'MISSING'; target[f] = (m.group(2) or m.group(3)) if m else None
def canon(f):
    seen = set()
    while f in status and status[f] != 'ACTIVE' and f not in seen: seen.add(f); f = target[f]
    return f
errors = []
for f, s in status.items():
    if s == 'MISSING': errors.append(f'{f}: no Status field')
    elif target[f] and (target[f] not in status or status[target[f]] != 'ACTIVE'): errors.append(f'{f}: {s} target {target[f]} is not an ACTIVE feature')
f2tp = collections.defaultdict(set)
for r in csv.DictReader(open(D/'gen_trace_feature_tp.csv')):
    if r['feature'] not in status: errors.append(f"trace: unknown feature {r['feature']}")
    if r['tp_item'] not in tps: errors.append(f"trace: unknown TP item {r['tp_item']}")
    f2tp[canon(r['feature'])].add(r['tp_item'])
tp2bin = collections.defaultdict(set); bins = set(); adopted = set(); wit_order = []
for r in csv.DictReader(open(D/'gen_trace_tp_bin.csv')):
    if r['tp_item'] not in tps: errors.append(f"trace: unknown TP item {r['tp_item']} in bin table")
    if r['covergroup'] not in cgs: errors.append(f"trace: unknown covergroup {r['covergroup']}")
    b = (r['covergroup'], r['coverpoint'], r['bin']); tp2bin[r['tp_item']].add(b); bins.add(b)
    if r['adopted'] == '1': adopted.add(b)
    if r['covergroup'] == 'CG-WIT-001': wit_order.append((r['tp_item'], r['bin']))
active = [f for f, s in status.items() if s == 'ACTIVE']
no_tp = [f for f in active if not f2tp.get(f)]
no_bin = [f for f in active if not any(any(b[0] != 'CG-WIT-001' for b in tp2bin.get(t, ())) for t in f2tp.get(f, ()))]
no_bin_incl_wit = [f for f in active if not any(t in tp2bin for t in f2tp.get(f, ()))]
tp_no_bin = [t for t in tps if t not in tp2bin]
tp_no_feat = [t for t in tps if not any(t in s for s in f2tp.values())]
cg_bad = []; cg_cps = {}; cg_adopted = {}; named = set()
for c, b in cgs.items():
    if c == 'CG-WIT-001':
        cg_cps[c] = set(re.findall(r'^\s*- (c[pr]_[a-z0-9_]+)\b', b, re.M)); cg_adopted[c] = False; continue  # ledger: outside traceability condition 2
    m = re.search(r'^- Features: (.*)$', b, re.M); ids = re.findall(r'F-[A-Z]+-\d{3}', m.group(1)) if m else []
    if not ids: cg_bad.append(f'{c}: no Features')
    for i in ids:
        if i not in status: cg_bad.append(f'{c}: unknown feature {i}')
        else: named.add(canon(i))
    cg_cps[c] = set(re.findall(r'^\s*- (c[pr]_[a-z0-9_]+)\b', b, re.M))
    ad = re.search(r'^- Adopted \(riscv-dv\): (.*)$', b, re.M); cg_adopted[c] = bool(ad and not ad.group(1).strip().lower().startswith('none'))
# reverse of condition 2: every ACTIVE feature is named by at least one non-ledger covergroup's Features field
unnamed = [f for f in active if f not in named]
# per-bin rule: every CSV bin name occurs in its covergroup block (after joining wrapped lines); array bins name[N] match name[
bin_missing = []; adopted_bad = []
for (c, cp, bn) in bins:
    blk = re.sub(r'\n\s+', ' ', cgs.get(c, ''))
    base = re.sub(r'\[\d+\]$', '[', bn)
    if not (re.search(r'\b' + re.escape(bn) + r'\b', blk) or (base.endswith('[') and base in blk)):
        # cross bins may be referenced as '_'-joined operand bin names (gen_fcov_plan.md Section 0); accept when the
        # cross is declared and the name segments into declared bin names of that covergroup
        words = set(re.findall(r'\b[a-z][a-z0-9_]*\b', blk))
        def segmentable(name):
            parts = name.split('_'); n = len(parts)
            ok = [False] * (n + 1); ok[0] = True
            for i in range(1, n + 1):
                ok[i] = any(ok[j] and '_'.join(parts[j:i]) in words for j in range(i))
            return ok[n]
        if not (cp.startswith('cr_') and re.search(r'\b' + re.escape(cp) + r'\b', blk) and segmentable(bn)):
            bin_missing.append(f'{c}.{cp}.{bn}')
    if (c, cp, bn) in adopted and not cg_adopted.get(c): adopted_bad.append(f'{c}.{cp}.{bn}')
# coverpoints owned by no item (regression-level): report, not fail
owned_cps = {(b[0], b[1]) for b in bins}
unowned = sorted(f'{c}.{cp}' for c, cps in cg_cps.items() for cp in cps if (c, cp) not in owned_cps)
# ---- cycle-clause marker, export rows, witness ledger CSV, sunset (gen_test_plan.md Section 0) ----
def split_rows(txt):
    out = []; depth = 0; cur = ''
    for ch in txt:
        if ch == '(': depth += 1
        if ch == ')': depth -= 1
        if ch == ';' and depth == 0: out.append(cur.strip()); cur = ''
        else: cur += ch
    if cur.strip(): out.append(cur.strip())
    return out
PLAN_DEMANDED_ROWS = {'icram lookup', 'icram tag_write', 'icram fill_write'}  # gen_test_plan.md Section 0, WP-8
tok_check = []
marked = {}; wit_errors = []
for tid, b in tps.items():
    if TOKEN not in b: continue
    m = re.search(r'\[export-rows: (.*?)\]', b)
    if not m: wit_errors.append(f'{tid}: marked item without [export-rows: ...]'); marked[tid] = []; continue
    rows = split_rows(m.group(1))
    for tok in rows:
        if not tok.startswith('none ('): tok_check.append((tid, tok))
    marked[tid] = [t for t in rows if not t.startswith('none')]
witness_csv = list(csv.DictReader(open(D/'gen_trace_witness_ids.csv')))
if [(r['tp_item'], r['bin']) for r in witness_csv] != wit_order:
    wit_errors.append('gen_trace_witness_ids.csv rows are not the CG-WIT-001 rows of gen_trace_tp_bin.csv in file order')
for i, r in enumerate(witness_csv):
    if r['index'] != str(i): wit_errors.append(f'gen_trace_witness_ids.csv: index {r["index"]} at row {i}')
    if (r['marked'] == '1') != (r['tp_item'] in marked): wit_errors.append(f'gen_trace_witness_ids.csv: marked={r["marked"]} disagrees with the token for {r["tp_item"]}')
    g = re.search(r'^- Test group: (\S+)', tps.get(r['tp_item'], ''), re.M)
    if not g or g.group(1) != r['test_group']: wit_errors.append(f'gen_trace_witness_ids.csv: test_group {r["test_group"]} disagrees with the item for {r["tp_item"]}')
for tid in marked:
    if tid not in {r['tp_item'] for r in witness_csv}: wit_errors.append(f'{tid}: marked item without a CG-WIT-001 row')
# the rendered witness table (TB Infra codegen) equals the CSV whenever it exists; the digest guard that would make the two
# provably one artefact is not built, so this compare is what stands in for it
gk = R / 'gen_tb' / 'gen_knobs.py'
if gk.exists() and re.search(r'^WITNESS_IDS\s*=', gk.read_text(), re.M):
    ns = {}
    try:
        exec(compile(re.search(r'^WITNESS_IDS\s*=.*?(?=^\w|\Z)', gk.read_text(), re.M | re.S).group(0), str(gk), 'exec'), ns)
        rendered = {str(k): int(v) for k, v in (ns.get('WITNESS_IDS') or {}).items()}
        expected = {r['tp_item']: int(r['index']) for r in witness_csv}
        if rendered != expected: wit_errors.append(f'gen_knobs.py WITNESS_IDS differs from gen_trace_witness_ids.csv ({len(rendered)} vs {len(expected)} entries)')
    except Exception as exc:  # a table that cannot be read is a violation, not a skip
        wit_errors.append(f'gen_knobs.py WITNESS_IDS unreadable: {exc}')
# rendered export rows: the yaml table minus wildcard rows
import yaml
knobs = yaml.safe_load(open(args.knobs))
yaml_rows = set(); wildcard_rows = set()
for row in knobs.get('export_events', []):
    src = row['source']; ev = str(row['event'])
    (wildcard_rows if '<' in ev else yaml_rows).add(f'{src} {ev}')
VOCAB = yaml_rows | PLAN_DEMANDED_ROWS | WILDCARD_TOKENS  # a yaml row cannot drift from the list: the list is the yaml
for tid, tok in tok_check:
    if tok not in VOCAB: wit_errors.append(f'{tid}: export row "{tok}" is neither a rendered yaml row nor a plan-demanded row (gen_test_plan.md Section 0)')
in_yaml = [tid for tid, rows in marked.items() if rows and all(present(t, yaml_rows) for t in rows)]
sunset_fail = []; export_sources = None; sunset_note = ''
if args.build_manifest and not pathlib.Path(args.build_manifest).exists():
    sunset_note = f'export sources unknown: {args.build_manifest} not found'
    wit_errors.append(f'build manifest given but not found: {args.build_manifest} (an explicit path must exist; omit the option for the unknown note)')
elif args.build_manifest:
    man = yaml.safe_load(open(args.build_manifest)) or {}
    rowset = lambda v: {(x['row'] if 'row' in x else f"{x['source']} {x['event']}") if isinstance(x, dict) else str(x) for x in (v or [])}  # {row}, {source, event} or string entries (T-140 shape: row, first_run, first_line)
    rendered = rowset(man.get('export_sources')) if 'export_sources' in man else None
    if 'export_sources_emitted' in man:  # the rows the build's registered writers emit (Runtime, from the canary export header sources=)
        export_sources = rowset(man['export_sources_emitted'])
        if args.exclude_rows is not None and args.observed_field in man: sys.exit(f'REHEARSAL FLAG REFUSED: {args.build_manifest} carries {args.observed_field}; --exclude-rows may only stand in for a missing observed list')
        if args.exclude_rows is not None: observed = export_sources - {r.strip() for r in args.exclude_rows.split(';') if r.strip()}; obs_origin = 'REHEARSAL (no observed list in the manifest): emitted minus --exclude-rows; this run cannot gate a sunset'
        elif args.observed_field in man: observed = rowset(man[args.observed_field]); obs_origin = f'manifest key {args.observed_field}'
        else: observed = None; obs_origin = f'no observed-row list ({args.observed_field}, T-140): sunset refused, no item un-marks on a declaration'
        obs_ok = (lambda t: present(t, observed)) if observed is not None else (lambda t: False)
        sunset_fail = [tid for tid, rows in marked.items() if rows and all(obs_ok(t) for t in rows)]
        sunset_gated = [tid for tid, rows in marked.items() if rows and all(present(t, export_sources) for t in rows) and not all(obs_ok(t) for t in rows)]
        renderable = len([tid for tid, rows in marked.items() if rows and rendered is not None and all(present(t, rendered) for t in rows)])
        sunset_note = f'export sources from {args.build_manifest}: emitted {len(export_sources)} rows (export_sources_emitted), rendered {len(rendered) if rendered is not None else "n/a"}; observed {len(observed) if observed is not None else 0} rows ({obs_origin}); never observed among the emitted: {sorted(export_sources - observed) if observed is not None else "all"}; {len(sunset_fail)} still-marked items have every export row OBSERVED (they must lose the token); {len(sunset_gated)} still-marked items have every row emitted but a row never observed (LOG-028a, they keep the token); {renderable} have every row rendered'
        sunset_note += f'. Sunset count: would un-mark {len(sunset_fail)} items on the OBSERVED rows ({renderable} have every row rendered, {len(sunset_gated)} gated by an unobserved row)'
    elif rendered is not None:
        renderable = [tid for tid, rows in marked.items() if rows and all(present(t, rendered) for t in rows)]
        sunset_note = f'export sources unknown: {args.build_manifest} carries export_sources (the rendered table, {len(rendered)} rows; {len(renderable)} marked items renderable) but no export_sources_emitted field, the rows the build\'s writers emit (Runtime request, gen_test_plan.md Section 2a WP-6); no item sunsets on rendered rows alone'
    else:
        sunset_note = f'export sources unknown: {args.build_manifest} has neither export_sources_emitted nor export_sources (Runtime request, gen_test_plan.md Section 2a WP-6)'
else:
    sunset_note = f'export sources unknown: no --build-manifest given; {args.knobs} renders {len(yaml_rows)} exact rows and {len(wildcard_rows)} wildcard rows (absent); {len(in_yaml)} of {len(marked)} marked items have every export row rendered in the yaml and would be checked against a build'
# The prose totals are derived from this CSV, so they are checked against it. A missing cell is a violation too:
# a check that passes when the table is renamed would be worse than no check.
count_bad = []
_wit = [b for b in bins if b[0] == 'CG-WIT-001']
_ncg = len(cgs) - (1 if 'CG-WIT-001' in cgs else 0)
_want_bins, _want_adopted = len(bins) - len(_wit), len(adopted)
for _rel, _pat, _fields in [
        ('gen_fcov_plan.md',
         r'^\| Distinct bins referenced by TP items \(spec-derived and adopted\) \| (\d+) \|$',
         [('distinct bins', lambda g: int(g[0]), lambda: _want_bins)]),
        ('gen_test_plan.md',
         r'^\| Covergroups \(spec-derived and adopted\) / distinct bins referenced / adopted bins \| (\d+) / (\d+) / (\d+) \|$',
         [('covergroups', lambda g: int(g[0]), lambda: _ncg),
          ('distinct bins', lambda g: int(g[1]), lambda: _want_bins),
          ('adopted bins', lambda g: int(g[2]), lambda: _want_adopted)])]:
    _m = re.search(_pat, (D/_rel).read_text(encoding='ascii'), re.M)
    if not _m:
        count_bad.append(f'{_rel}: the counts row this check reads is absent or reworded ({_pat})')
        continue
    for _name, _get, _want in _fields:
        if _get(_m.groups()) != _want():
            count_bad.append(f'{_rel}: {_name} says {_get(_m.groups())}, gen_trace_tp_bin.csv gives {_want()}')

for lst, msg in [(no_tp, 'ACTIVE feature without TP item'), (no_bin, 'ACTIVE feature without bin'), (tp_no_bin, 'TP item without bins'), (tp_no_feat, 'TP item without feature'), (cg_bad, 'covergroup mapping'), (unnamed, 'ACTIVE feature named by no non-ledger covergroup (condition 2 reverse, Critic W-4)'), (bin_missing, 'CSV bin not declared in the plan'), (adopted_bad, 'adopted=1 bin in a covergroup without an Adopted source'), (wit_errors, 'witness ledger'), (sunset_fail, 'sunset: still-marked item whose export rows are all present in the build (remove the token, gen_test_plan.md Section 0)'), (count_bad, 'stated total disagrees with the traceability CSV')]:
    errors += [f'{msg}: {x}' for x in lst]
wit_bins = [b for b in bins if b[0] == 'CG-WIT-001']
ncg = len(cgs) - (1 if 'CG-WIT-001' in cgs else 0)
print(f'features {len(feats)} (ACTIVE {len(active)}, ALIAS {sum(1 for s in status.values() if s=="ALIAS")}, FOLDED {sum(1 for s in status.values() if s=="FOLDED")}); TP items {len(tps)}; covergroups {ncg} (plus the ledger CG-WIT-001); bins referenced {len(bins)-len(wit_bins)} (adopted {len(adopted)}, spec-derived {len(bins)-len(adopted)-len(wit_bins)}; ledger bins {len(wit_bins)} counted separately)')
print(f'completeness: ACTIVE->TP {len(active)-len(no_tp)}/{len(active)}, ACTIVE->bin (spec-derived and adopted bins only, CG-WIT-001 excluded) {len(active)-len(no_bin)}/{len(active)} (with witness bins counted: {len(active)-len(no_bin_incl_wit)}/{len(active)}), bins->feature {ncg-len(cg_bad)}/{ncg} covergroups (ledger excluded), ACTIVE named by a covergroup {len(active)-len(unnamed)}/{len(active)}, CSV bins declared {len(bins)-len(bin_missing)}/{len(bins)}')
print(f'witness ledger: {len(wit_bins)} CG-WIT-001 bins excluded from the functional gate and from ACTIVE->bin; spec-derived bins {len(bins)-len(adopted)-len(wit_bins)}, adopted {len(adopted)}; gen_trace_witness_ids.csv {len(witness_csv)} rows, marked {sum(1 for r in witness_csv if r["marked"]=="1")}')
print(f'cycle-clause marked items {len(marked)} (witness bins excluded from manifests while marked, rule (f)); export rows named {sum(len(v) for v in marked.values())} over {len(set(t for v in marked.values() for t in v))} distinct rows; no-export-row items {sum(1 for v in marked.values() if not v)}')
print(f'sunset (cycle-clause tokens against the build): {sunset_note}')
print(f'coverpoints declared {sum(len(v) for v in cg_cps.values())}, owned by an item {len(owned_cps)}, regression-level (no item) {len(unowned)} (listed in gen_fcov_plan.md Section 1.1; reported, not failed)')
if errors:
    sunset_msgs = [e for e in errors if e.startswith('sunset:')]; other = [e for e in errors if not e.startswith('sunset:')]
    print(f'FAIL: {len(errors)} violations ({len(sunset_msgs)} sunset, {len(other)} other)'); [print('  ' + e) for e in other[:60]]
    if len(other) > 60: print(f'  ... {len(other) - 60} more')
    [print('  ' + e) for e in sunset_msgs]  # the operator removes these tokens: print all of them
    sys.exit(1)
print('PASS')
