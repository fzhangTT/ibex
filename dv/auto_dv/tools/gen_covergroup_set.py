#!/usr/bin/env python3
"""The minimum covergroup set the promoted fcov manifests reference (T-204; TB Infra implements in rank order, T-205).

Reads the committed testlist (every entry with an fcov_expectation_file), its manifests (dv/auto_dv/fcov_expectations/*.fcov.yaml:
bins are gen_<x>_cg.<coverpoint>.<bin> tokens; "# not_hit" header lines are excluded bins) and gen_fcov_plan.md (headers
"### CG-<AREA>-<nnn>: gen_cg_<x>", implemented as gen_<x>_cg, architecture Section 5). Writes a markdown report and a CSV: one row per
covergroup the manifests reference, ranked by distinct bins unlocked, with its plan anchor, the coverpoints / crosses and bins referenced,
the manifests that reference it and how many bins each, and the ledger covergroup marked. A manifest becomes verifiable only when every
covergroup it references exists, so the report also lists per manifest the covergroups it needs and the cumulative rank at which it is
complete.

Usage: gen_covergroup_set.py [--testlist F] [--fcov-dir D] [--fcov-plan F] [--md OUT.md] [--csv OUT.csv] [--plan-sha SHA]
"""
import re, csv, sys, argparse, pathlib, collections, hashlib, yaml
R = pathlib.Path(__file__).resolve()
while not (R / 'dv/auto_dv/contract').is_dir():
    if R.parent == R: sys.exit('repo root not found (no dv/auto_dv/contract above this file)')
    R = R.parent
sys.path.insert(0, str(R / 'dv/auto_dv/flow')); sys.path.insert(0, str(R / 'dv/auto_dv/tests'))
from gen_flow_const import LEDGER_COVERGROUPS, WITNESS_CSV  # the ledger SV names and the witness CSV (gen_flow_const.py)
import gen_fcov_manifest
from gen_fcov_manifest import WITNESS_CG as LEDGER_PLAN, impl_cg_name, module_items, FCOV_HOME  # plan id, the plan-to-SV name rule, the manifest home
TESTS_HOME = pathlib.Path(gen_fcov_manifest.__file__).resolve().parent   # the test modules live beside the manifest generator

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--testlist', default=str(R / 'dv/auto_dv/flow/gen_testlist.yaml')); ap.add_argument('--fcov-dir', default=str(FCOV_HOME))
    ap.add_argument('--fcov-plan', default=str(R / 'dv/auto_dv/docs/gen_fcov_plan.md')); ap.add_argument('--md', default=str(R / 'dv/auto_dv/evidence/gen_round0_covergroup_set.md'))
    ap.add_argument('--csv', default=str(R / 'dv/auto_dv/evidence/gen_round0_covergroup_set.csv')); ap.add_argument('--plan-sha', default='working tree')
    a = ap.parse_args()
    plan = pathlib.Path(a.fcov_plan).read_text()
    dig = hashlib.sha256(); dig.update(plan.encode()); dig.update(pathlib.Path(a.testlist).read_bytes())
    plan_of_impl = {}; anchor = {}
    for i, line in enumerate(plan.splitlines(), 1):
        m = re.match(r'^### (CG-[A-Z]+-\d{3}): (gen_cg_\w+)', line)
        if m: plan_of_impl[impl_cg_name(m.group(2))] = m.group(1); anchor[m.group(1)] = f'gen_fcov_plan.md:{i} {line.strip()}'
    ledger_impls = set(LEDGER_COVERGROUPS)
    tl = yaml.safe_load(open(a.testlist))
    entries = [e for e in tl['tests'] if e.get('fcov_expectation_file')]
    per_cg = collections.defaultdict(lambda: {'bins': set(), 'cps': collections.defaultdict(set), 'manifests': collections.Counter()})
    per_man = {}; declarers = collections.defaultdict(set)   # bin token -> manifests declaring it
    for e in sorted(entries, key=lambda e: e['name']):
        p = R / e['fcov_expectation_file']
        if not p.exists(): sys.exit(f'{e["name"]}: manifest {p} missing')
        txt = p.read_text(); nh = set(re.findall(r'^# not_hit (\S+):', txt, re.M)); dig.update(txt.encode())
        bins = list((yaml.safe_load(txt) or {}).get('bins') or [])
        cgs = collections.Counter()
        for b in bins:
            cg, cp, bn = b.split('.', 2)
            per_cg[cg]['bins'].add(f'{cp}.{bn}'); per_cg[cg]['cps'][cp].add(bn); per_cg[cg]['manifests'][e['name']] += 1; cgs[cg] += 1; declarers[b].add(e['name'])
        per_man[e['name']] = {'bins': len(bins), 'not_hit': len(nh), 'cgs': cgs, 'tier': e.get('tier'), 'measured': e.get('measured')}
    named = {pathlib.Path(e['fcov_expectation_file']).name for e in entries}
    extra = []
    for p in sorted(pathlib.Path(a.fcov_dir).glob('*.fcov.yaml')):
        if p.name in named: continue
        txt = p.read_text(); bins = list((yaml.safe_load(txt) or {}).get('bins') or []); cgs = collections.Counter(b.split('.', 1)[0] for b in bins)
        extra.append((p.name, len(bins), len(re.findall(r'^# not_hit ', txt, re.M)), cgs))
    ranked = sorted(per_cg.items(), key=lambda kv: (-len(kv[1]['bins']), kv[0]))
    rank_of = {cg: i + 1 for i, (cg, _) in enumerate(ranked)}
    complete_at = {m: max(rank_of[cg] for cg in d['cgs']) if d['cgs'] else 0 for m, d in per_man.items()}
    unknown = [cg for cg, _ in ranked if cg not in plan_of_impl]
    rows = []
    for rk, (cg, d) in enumerate(ranked, 1):
        pid = plan_of_impl.get(cg, 'UNKNOWN (no plan header)')
        done_here = sorted(m for m, r in complete_at.items() if r == rk)
        rows.append({'rank': rk, 'covergroup': cg, 'plan_id': pid, 'ledger': 'yes' if cg in ledger_impls else 'no', 'bins_referenced': len(d['bins']),
                     'coverpoints_referenced': len(d['cps']), 'coverpoints': '; '.join(f"{cp} ({len(bs)})" for cp, bs in sorted(d['cps'].items())),
                     'manifests': len(d['manifests']), 'manifest_bins': '; '.join(f"{m} ({n})" for m, n in sorted(d['manifests'].items())),
                     'manifests_completed_at_this_rank': '; '.join(done_here) or '-', 'plan_anchor': anchor.get(pid, '-')})
    total_bins = sum(r['bins_referenced'] for r in rows)
    declared_total = sum(d['bins'] for d in per_man.values()); multi = sum(1 for b, ms in declarers.items() if len(ms) > 1); dup_decl = declared_total - total_bins
    hdr = f"""# Minimum covergroup set referenced by the promoted fcov manifests (T-204; implementation order for TB Infra, T-205)

GENERATED by dv/auto_dv/tools/gen_covergroup_set.py from dv/auto_dv/flow/gen_testlist.yaml, the {len(entries)} manifests it names under
dv/auto_dv/fcov_expectations/ and gen_fcov_plan.md as read at generation (inputs digest {dig.hexdigest()[:12]} over the fcov plan, the testlist and
the named manifests; landing label {a.plan_sha}; regeneration command, byte for byte from the commit that carries these inputs: python3
dv/auto_dv/tools/gen_covergroup_set.py --plan-sha {a.plan_sha}; the label is the --plan-sha argument alone and claims nothing about which commit's
plan was read). Ranking: distinct bins referenced across the manifests (a bin is counted once per covergroup even when several
manifests declare it); bins under a manifest's "# not_hit" header are excluded and not counted. A manifest is verifiable only when every
covergroup it references exists (a missing covergroup makes the per-test URG report lack the group, LOG-046), so the column "manifests
completed at this rank" names the manifests that become fully verifiable once the covergroups ranked 1..N exist. The ledger covergroup
{LEDGER_PLAN} (gen_wit_cycle_clause_cg, T-179) is marked; its bins are witness bins, excluded from the score by name. Plan anchors are the
gen_fcov_plan.md headers (file:line). Covergroups without a plan header: {len(unknown)} ({', '.join(unknown) or 'none'}).

Totals: {len(rows)} covergroups, {total_bins} distinct referenced bins, {len(entries)} manifests: {declared_total} declarations in total, of which
{dup_decl} are duplicate declarations of a bin another manifest also declares ({multi} distinct bins are declared by more than one manifest); a further
{sum(d['not_hit'] for d in per_man.values())} bins_not_hit bins are not declared by any manifest.

| Rank | Covergroup (SV) | Plan id | Ledger | Bins referenced | Coverpoints / crosses referenced (bins each) | Manifests (bins each) | Manifests completed at this rank | Plan anchor |
|---|---|---|---|---|---|---|---|---|
"""
    body = ''.join(f"| {r['rank']} | {r['covergroup']} | {r['plan_id']} | {r['ledger']} | {r['bins_referenced']} | {r['coverpoints']} | {r['manifest_bins']} | {r['manifests_completed_at_this_rank']} | {r['plan_anchor']} |\n" for r in rows)
    mt = "\n## Per manifest\n\n| Manifest (test) | Tier | measured | Declared bins | bins_not_hit | Covergroups needed | Complete at rank |\n|---|---|---|---|---|---|---|\n"
    for m, d in sorted(per_man.items(), key=lambda kv: (complete_at[kv[0]], kv[0])):
        mt += f"| {m} | {d['tier']} | {str(bool(d['measured'])).lower()} | {d['bins']} | {d['not_hit']} | {len(d['cgs'])}: {'; '.join(f'{cg} ({n})' for cg, n in sorted(d['cgs'].items()))} | {complete_at[m]} |\n"
    # committed manifests the committed testlist does not name yet: excluded from the ranking, stated with what they add
    mt += "\n## Committed manifests not yet named by the committed testlist (excluded from the ranking)\n\n"
    if extra:
        mt += "| Manifest file | Declared bins | bins_not_hit | Covergroups (bins each) | New to the set above |\n|---|---|---|---|---|\n"
        for name, nb, nh, cgs in extra:
            new = [cg for cg in cgs if cg not in per_cg]
            cg_txt = '; '.join(cg + ' (' + str(n) + ')' for cg, n in sorted(cgs.items()))
            new_txt = '; '.join(cg + ' (' + plan_of_impl.get(cg, 'UNKNOWN') + ', ' + anchor.get(plan_of_impl.get(cg), '-').split(' ')[0] + ')' for cg in new) or 'none'
            mt += '| ' + name + ' | ' + str(nb) + ' | ' + str(nh) + ' | ' + cg_txt + ' | ' + new_txt + ' |\n'
        mt += "\nThese enter the ranking the moment their testlist entries are committed (a staged entry is not an input of this file).\n"
    else:
        mt += "None: every committed manifest is named by the committed testlist.\n"
    # the ledger covergroup: derived from the witness CSV and the promoted tests' manifests and modules
    wit_rows = list(csv.DictReader(open(WITNESS_CSV, newline='')))
    hosted = {re.sub(r'^gen_test_', 'gen_', e['name']): e for e in entries}
    released_hosted = []
    for w in wit_rows:
        if w['marked'] == '1' or w['test_group'] not in hosted: continue
        e = hosted[w['test_group']]; test = e['name']; mp = R / e['fcov_expectation_file']; mod = TESTS_HOME / (test + '.py')
        mtxt = mp.read_text() if mp.exists() else ''
        nh = set(re.findall(r'^# not_hit (\S+):', mtxt, re.M)); declared_bins = (yaml.safe_load(mtxt) or {}).get('bins') or [] if mtxt else []
        if any(x.endswith('.' + w['bin']) for x in nh): why = 'bins_not_hit'
        elif mod.exists() and w['tp_item'] in (module_items(mod)[1] or {}): why = 'not_built'
        elif any(x.endswith('.' + w['bin']) for x in declared_bins): why = 'DECLARED (the ledger is then in the ranking above)'
        else: why = 'absent (neither declared, bins_not_hit nor not_built)'
        released_hosted.append((w['tp_item'], test, why))
    mt += f"\n## Ledger covergroup\n\n{LEDGER_PLAN} ({', '.join(sorted(ledger_impls))}, {anchor.get(LEDGER_PLAN, '-')}) is "
    if any(cg in ledger_impls for cg in per_cg): mt += "in the ranking above (a promoted manifest declares a witness bin).\n"
    else:
        mt += ("referenced by NO promoted manifest today: the released witness bins belong to unbuilt groups except "
               + (', '.join(f"{t} ({test}: {why})" for t, test, why in released_hosted) or 'none') +
               ". It enters this set the moment a promoted manifest declares a witness bin; its implementation is T-179 regardless, because the witness score (gen_test_plan.md Section 0) depends on it.\n")
    out = hdr + body + mt
    assert not [c for c in out.encode() if c > 127]
    pathlib.Path(a.md).write_text(out)
    with open(a.csv, 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
    print(f'{len(rows)} covergroups, {total_bins} referenced bins, {len(entries)} manifests; extra committed manifests {len(extra)}; ledger in ranking {any(cg in ledger_impls for cg in per_cg)}; unknown {unknown}; wrote {a.md}, {a.csv}')

if __name__ == '__main__': main()
