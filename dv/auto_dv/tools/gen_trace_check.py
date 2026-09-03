#!/usr/bin/env python3
"""Traceability / completeness check for the Ibex auto-DV plan set (DV_prompt.txt Section 4).

Inputs (dv/auto_dv/docs/): gen_feature_list.md, gen_test_plan.md, gen_fcov_plan.md,
gen_trace_feature_tp.csv, gen_trace_tp_bin.csv, gen_trace_witness_ids.csv; the rendered export event table
dv/auto_dv/tb/gen_tb_knobs.yaml (export_events) and, optionally, one build's build_manifest.yaml.
Exits 1 on any violation. Deterministic.

Options:
  --knobs <path>           export event table (default dv/auto_dv/tb/gen_tb_knobs.yaml); a row whose event is
                           "<name>" is a wildcard and counts as ABSENT (gen_test_plan.md Section 0)
  --build-manifest <path>  a build's build_manifest.yaml; its export_sources list ("<source> <event>" strings) decides
                           the cycle-clause sunset (C-3): a still-marked item whose export rows are all present FAILS.
                           Without it the tool reports the sunset input as unknown and does not fail on it.
"""
import re, csv, sys, argparse, collections, pathlib
R = pathlib.Path(__file__).resolve().parents[1]; D = R / 'docs'
ap = argparse.ArgumentParser()
ap.add_argument('--knobs', default=str(R / 'tb' / 'gen_tb_knobs.yaml'))
ap.add_argument('--build-manifest', default=None)
args = ap.parse_args()
TOKEN = '[CYCLE-CLAUSE coverage-only until the event export lands]'
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
# reverse of condition 2 (Critic W-4): every ACTIVE feature is named by at least one non-ledger covergroup's Features field
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
marked = {}; wit_errors = []
for tid, b in tps.items():
    if TOKEN not in b: continue
    m = re.search(r'\[export-rows: (.*?)\]', b)
    if not m: wit_errors.append(f'{tid}: marked item without [export-rows: ...]'); marked[tid] = []; continue
    rows = split_rows(m.group(1))
    for tok in rows:
        if not (tok.startswith('none (') or re.fullmatch(r'(ibus|dbus|pin|alert|misc|icram|scrkey|regime) [a-z_0-9<>]+', tok)):
            wit_errors.append(f'{tid}: export row "{tok}" is not "<source> <event>" or "none (<why>)"')
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
# rendered export rows: the yaml table minus wildcard rows
import yaml
knobs = yaml.safe_load(open(args.knobs))
yaml_rows = set(); wildcard_rows = set()
for row in knobs.get('export_events', []):
    src = row['source']; ev = str(row['event'])
    (wildcard_rows if '<' in ev else yaml_rows).add(f'{src} {ev}')
def present(tok, rows):
    if tok == 'pin irq_fast': return any(re.fullmatch(r'pin irq_fast\d*', r) for r in rows)
    return tok in rows
in_yaml = [tid for tid, rows in marked.items() if rows and all(present(t, yaml_rows) for t in rows)]
sunset_fail = []; export_sources = None; sunset_note = ''
if args.build_manifest:
    man = yaml.safe_load(open(args.build_manifest)) or {}
    if 'export_sources' not in man:
        sunset_note = f'export sources unknown: {args.build_manifest} has no export_sources field (Runtime request, gen_test_plan.md Section 2a WP-6)'
    else:
        export_sources = {str(x) for x in (man['export_sources'] or [])}
        sunset_fail = [tid for tid, rows in marked.items() if rows and all(present(t, export_sources) for t in rows)]
        sunset_note = f'export sources from {args.build_manifest}: {len(export_sources)} rows; {len(sunset_fail)} still-marked items have every export row present'
else:
    sunset_note = f'export sources unknown: no --build-manifest given; {args.knobs} renders {len(yaml_rows)} exact rows and {len(wildcard_rows)} wildcard rows (absent); {len(in_yaml)} of {len(marked)} marked items have every export row rendered in the yaml and would be checked against a build'
for lst, msg in [(no_tp, 'ACTIVE feature without TP item'), (no_bin, 'ACTIVE feature without bin'), (tp_no_bin, 'TP item without bins'), (tp_no_feat, 'TP item without feature'), (cg_bad, 'covergroup mapping'), (unnamed, 'ACTIVE feature named by no non-ledger covergroup (condition 2 reverse, Critic W-4)'), (bin_missing, 'CSV bin not declared in the plan'), (adopted_bad, 'adopted=1 bin in a covergroup without an Adopted source'), (wit_errors, 'witness ledger'), (sunset_fail, 'sunset: still-marked item whose export rows are all present in the build (remove the token, gen_test_plan.md Section 0)')]:
    errors += [f'{msg}: {x}' for x in lst]
wit_bins = [b for b in bins if b[0] == 'CG-WIT-001']
ncg = len(cgs) - (1 if 'CG-WIT-001' in cgs else 0)
print(f'features {len(feats)} (ACTIVE {len(active)}, ALIAS {sum(1 for s in status.values() if s=="ALIAS")}, FOLDED {sum(1 for s in status.values() if s=="FOLDED")}); TP items {len(tps)}; covergroups {ncg} (plus the ledger CG-WIT-001); bins referenced {len(bins)-len(wit_bins)} (adopted {len(adopted)}, spec-derived {len(bins)-len(adopted)-len(wit_bins)}; ledger bins {len(wit_bins)} counted separately)')
print(f'completeness: ACTIVE->TP {len(active)-len(no_tp)}/{len(active)}, ACTIVE->bin (spec-derived and adopted bins only, CG-WIT-001 excluded) {len(active)-len(no_bin)}/{len(active)} (with witness bins counted: {len(active)-len(no_bin_incl_wit)}/{len(active)}), bins->feature {ncg-len(cg_bad)}/{ncg} covergroups (ledger excluded), ACTIVE named by a covergroup {len(active)-len(unnamed)}/{len(active)}, CSV bins declared {len(bins)-len(bin_missing)}/{len(bins)}')
print(f'witness ledger: {len(wit_bins)} CG-WIT-001 bins excluded from the functional gate and from ACTIVE->bin; spec-derived bins {len(bins)-len(adopted)-len(wit_bins)}, adopted {len(adopted)}; gen_trace_witness_ids.csv {len(witness_csv)} rows, marked {sum(1 for r in witness_csv if r["marked"]=="1")}')
print(f'cycle-clause marked items {len(marked)} (witness bins excluded from manifests while marked, rule (f)); export rows named {sum(len(v) for v in marked.values())} over {len(set(t for v in marked.values() for t in v))} distinct rows; no-export-row items {sum(1 for v in marked.values() if not v)}')
print(f'sunset (C-3): {sunset_note}')
print(f'coverpoints declared {sum(len(v) for v in cg_cps.values())}, owned by an item {len(owned_cps)}, regression-level (no item) {len(unowned)} (listed in gen_fcov_plan.md Section 1.1; reported, not failed)')
if errors:
    print(f'FAIL: {len(errors)} violations'); [print('  ' + e) for e in errors[:60]]; sys.exit(1)
print('PASS')
