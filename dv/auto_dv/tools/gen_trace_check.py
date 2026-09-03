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
cg_bad = []; cg_cps = {}; cg_adopted = {}
for c, b in cgs.items():
    m = re.search(r'^- Features: (.*)$', b, re.M); ids = re.findall(r'F-[A-Z]+-\d{3}', m.group(1)) if m else []
    if not ids: cg_bad.append(f'{c}: no Features')
    for i in ids:
        if i not in status: cg_bad.append(f'{c}: unknown feature {i}')
    cg_cps[c] = set(re.findall(r'^\s*- (c[pr]_[a-z0-9_]+)\b', b, re.M))
    ad = re.search(r'^- Adopted \(riscv-dv\): (.*)$', b, re.M); cg_adopted[c] = bool(ad and not ad.group(1).strip().lower().startswith('none'))
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
for lst, msg in [(no_tp, 'ACTIVE feature without TP item'), (no_bin, 'ACTIVE feature without bin'), (tp_no_bin, 'TP item without bins'), (tp_no_feat, 'TP item without feature'), (cg_bad, 'covergroup mapping'), (bin_missing, 'CSV bin not declared in the plan'), (adopted_bad, 'adopted=1 bin in a covergroup without an Adopted source')]:
    errors += [f'{msg}: {x}' for x in lst]
print(f'features {len(feats)} (ACTIVE {len(active)}, ALIAS {sum(1 for s in status.values() if s=="ALIAS")}, FOLDED {sum(1 for s in status.values() if s=="FOLDED")}); TP items {len(tps)}; covergroups {len(cgs)}; bins referenced {len(bins)} (adopted {len(adopted)}, spec-derived {len(bins)-len(adopted)})')
print(f'completeness: ACTIVE->TP {len(active)-len(no_tp)}/{len(active)}, ACTIVE->bin {len(active)-len(no_bin)}/{len(active)}, bins->feature {len(cgs)-len(cg_bad)}/{len(cgs)} covergroups, CSV bins declared {len(bins)-len(bin_missing)}/{len(bins)}')
print(f'coverpoints declared {sum(len(v) for v in cg_cps.values())}, owned by an item {len(owned_cps)}, regression-level (no item) {len(unowned)} (listed in gen_fcov_plan.md Section 1.1; reported, not failed)')
if errors:
    print(f'FAIL: {len(errors)} violations'); [print('  ' + e) for e in errors[:60]]; sys.exit(1)
print('PASS')
