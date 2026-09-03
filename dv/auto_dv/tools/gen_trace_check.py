#!/usr/bin/env python3
"""Traceability / completeness check for the Ibex auto-DV plan set (DV_prompt.txt Section 4).

Inputs (dv/auto_dv/docs/): gen_feature_list.md, gen_test_plan.md, gen_fcov_plan.md,
gen_trace_feature_tp.csv, gen_trace_tp_bin.csv. Exits 1 on any violation. Deterministic; no options.
"""
import re, csv, sys, collections, pathlib
D = pathlib.Path(__file__).resolve().parents[1] / 'docs'
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
tp2bin = collections.defaultdict(set); bins = set(); adopted = set()
for r in csv.DictReader(open(D/'gen_trace_tp_bin.csv')):
    if r['tp_item'] not in tps: errors.append(f"trace: unknown TP item {r['tp_item']} in bin table")
    if r['covergroup'] not in cgs: errors.append(f"trace: unknown covergroup {r['covergroup']}")
    b = (r['covergroup'], r['coverpoint'], r['bin']); tp2bin[r['tp_item']].add(b); bins.add(b)
    if r['adopted'] == '1': adopted.add(b)
active = [f for f, s in status.items() if s == 'ACTIVE']
no_tp = [f for f in active if not f2tp.get(f)]
no_bin = [f for f in active if not any(t in tp2bin for t in f2tp.get(f, ()))]
tp_no_bin = [t for t in tps if t not in tp2bin]
tp_no_feat = [t for t in tps if not any(t in s for s in f2tp.values())]
cg_bad = []
for c, b in cgs.items():
    m = re.search(r'^- Features: (.*)$', b, re.M); ids = re.findall(r'F-[A-Z]+-\d{3}', m.group(1)) if m else []
    if not ids: cg_bad.append(f'{c}: no Features'); 
    for i in ids:
        if i not in status: cg_bad.append(f'{c}: unknown feature {i}')
for lst, msg in [(no_tp, 'ACTIVE feature without TP item'), (no_bin, 'ACTIVE feature without bin'), (tp_no_bin, 'TP item without bins'), (tp_no_feat, 'TP item without feature'), (cg_bad, 'covergroup mapping')]:
    errors += [f'{msg}: {x}' for x in lst]
print(f'features {len(feats)} (ACTIVE {len(active)}, ALIAS {sum(1 for s in status.values() if s=="ALIAS")}, FOLDED {sum(1 for s in status.values() if s=="FOLDED")}); TP items {len(tps)}; covergroups {len(cgs)}; bins referenced {len(bins)} (adopted {len(adopted)}, spec-derived {len(bins)-len(adopted)})')
print(f'completeness: ACTIVE->TP {len(active)-len(no_tp)}/{len(active)}, ACTIVE->bin {len(active)-len(no_bin)}/{len(active)}, bins->feature {len(cgs)-len(cg_bad)}/{len(cgs)} covergroups')
if errors:
    print(f'FAIL: {len(errors)} violations'); [print('  ' + e) for e in errors[:50]]; sys.exit(1)
print('PASS')
