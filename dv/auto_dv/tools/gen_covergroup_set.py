#!/usr/bin/env python3
"""The minimum covergroup set the promoted fcov manifests reference (T-204; TB Infra implements in rank order, T-205).

Reads the committed testlist (every entry with an fcov_expectation_file), its manifests (dv/auto_dv/fcov_expectations/*.fcov.yaml:
bins are gen_<x>_cg.<coverpoint>.<bin> tokens; "# not_hit" header lines are excluded bins) and gen_fcov_plan.md (headers
"### CG-<AREA>-<nnn>: gen_cg_<x>", implemented as gen_<x>_cg, architecture Section 5). Writes a markdown report and a CSV: one row per
covergroup the manifests reference, ranked by distinct bins unlocked, with its plan anchor, the coverpoints / crosses and bins referenced,
the manifests that reference it and how many bins each, and the ledger covergroup marked. A manifest becomes verifiable only when every
covergroup it references exists, so the report also lists per manifest the covergroups it needs and the cumulative rank at which it is
complete.

Usage: gen_covergroup_set.py (--label ROUND | --md OUT.md --csv OUT.csv) [--testlist F] [--fcov-dir D] [--fcov-plan F] [--plan-sha SHA] [--note TEXT]

--fcov-dir D redirects every manifest the tool reads, the testlist-named ones by basename and the extra scan, so a rehearsal directory
stands in for the tree. A named manifest whose testlist path is outside the manifest home (FCOV_HOME) is a proof manifest kept as
evidence, not a promotion manifest: the tool lists the entry (neither read nor counted) when the entry is unmeasured and outside the
testlist's fcov_manifest_required_tiers, and refuses with a non-zero exit when the entry is measured or in a required tier (measured
defaults to true, as the testlist schema and the loader read it). The header names the override directory and the printed regeneration
command carries it.
"""
import re, csv, sys, shlex, argparse, pathlib, collections, hashlib, yaml
R = pathlib.Path(__file__).resolve()
while not (R / 'dv/auto_dv/contract').is_dir():
    if R.parent == R: sys.exit('repo root not found (no dv/auto_dv/contract above this file)')
    R = R.parent
sys.path.insert(0, str(R / 'dv/auto_dv/flow')); sys.path.insert(0, str(R / 'dv/auto_dv/tests'))
from gen_flow_const import LEDGER_COVERGROUPS, WITNESS_CSV  # the ledger SV names and the witness CSV (gen_flow_const.py)
import gen_fcov_manifest
from gen_fcov_manifest import WITNESS_CG as LEDGER_PLAN, impl_cg_name, module_items, FCOV_HOME  # plan id, the plan-to-SV name rule, the manifest home
TESTS_HOME = pathlib.Path(gen_fcov_manifest.__file__).resolve().parent   # the test modules live beside the manifest generator
EVIDENCE_HOME = R / 'dv/auto_dv/evidence'

def out_paths(a):
    """The record's own location, from --label or from explicit paths. There is no default, so a bare run writes nowhere
    instead of over whichever record a default happens to name."""
    if a.label and (a.md or a.csv): sys.exit('--label and explicit --md / --csv are exclusive: pass one or the other')
    if a.label:
        if not re.fullmatch(r'[A-Za-z0-9_]+', a.label): sys.exit(f'--label {a.label!r}: the label becomes a file name, so letters, digits and underscore only')
        return str(EVIDENCE_HOME / f'gen_{a.label}_covergroup_set.md'), str(EVIDENCE_HOME / f'gen_{a.label}_covergroup_set.csv')
    if a.md and a.csv: return a.md, a.csv
    sys.exit('no output location: pass --label <team round name>, or both --md and --csv')

def clone_rel(p):
    q = pathlib.Path(p).resolve()
    return str(q.relative_to(R.resolve())) if q.is_relative_to(R.resolve()) else str(q)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--testlist', default=str(R / 'dv/auto_dv/flow/gen_testlist.yaml')); ap.add_argument('--fcov-dir', default=str(FCOV_HOME))
    ap.add_argument('--fcov-plan', default=str(R / 'dv/auto_dv/docs/gen_fcov_plan.md')); ap.add_argument('--md', default=None); ap.add_argument('--csv', default=None)
    ap.add_argument('--label', default=None, help='team round name; it names the record files gen_<label>_covergroup_set.md / .csv under dv/auto_dv/evidence (exclusive with --md / --csv, and there is no default)')
    ap.add_argument('--plan-sha', default='unlabelled', help='landing label printed in the header; not a claim about which commit was read (the header prints the input digest)')
    ap.add_argument('--note', default=None, help='provenance sentence printed in the header and echoed in the regeneration command; asserted by the invoker, not checked by the tool (the inputs digest is the checked part)')
    a = ap.parse_args()
    md_out, csv_out = out_paths(a)
    plan = pathlib.Path(a.fcov_plan).read_text()
    dig = hashlib.sha256(); dig.update(plan.encode()); dig.update(pathlib.Path(a.testlist).read_bytes())
    plan_of_impl = {}; anchor = {}
    for i, line in enumerate(plan.splitlines(), 1):
        m = re.match(r'^### (CG-[A-Z]+-\d{3}): (gen_cg_\w+)', line)
        if m: plan_of_impl[impl_cg_name(m.group(2))] = m.group(1); anchor[m.group(1)] = f'gen_fcov_plan.md:{i} {line.strip()}'
    ledger_impls = set(LEDGER_COVERGROUPS)
    tl = yaml.safe_load(open(a.testlist))
    entries = [e for e in tl['tests'] if e.get('fcov_expectation_file')]
    required_tiers = set(tl.get('fcov_manifest_required_tiers') or [])   # a measured or required-tier entry must keep its manifest under the home
    per_cg = collections.defaultdict(lambda: {'bins': set(), 'cps': collections.defaultdict(set), 'manifests': collections.Counter()})
    per_man = {}; declarers = collections.defaultdict(set)   # bin token -> manifests declaring it
    nh_all = set()   # distinct bins_not_hit tokens across the named manifests (a manifest named by two entries counts once)
    outside = []   # (entry, manifest path, tier, measured): entries whose manifest is outside the manifest home
    try: home_rel = pathlib.Path(FCOV_HOME).resolve().relative_to(R.resolve())
    except ValueError: sys.exit(f'manifest home {FCOV_HOME} is outside the clone root {R}')
    for e in sorted(entries, key=lambda e: e['name']):
        rel = pathlib.Path(e['fcov_expectation_file'])
        if rel.parent != home_rel:
            if e.get('measured', True) or e.get('tier') in required_tiers: sys.exit(f"{e['name']}: manifest {rel} is outside {home_rel} and the entry is measured or in a required tier ({e.get('tier')}, measured {e.get('measured', True)}): refused")   # absent measured reads true, the schema default
            outside.append((e['name'], str(rel), e.get('tier'), e.get('measured', True))); continue   # any unmeasured entry outside the required tiers: reported below, neither read nor counted
        p = pathlib.Path(a.fcov_dir) / rel.name   # named manifests are read from --fcov-dir too, so a rehearsal dir stands in for the tree
        if not p.exists(): sys.exit(f'{e["name"]}: manifest {p} missing')
        txt = p.read_text(); nh = set(re.findall(r'^# not_hit (\S+):', txt, re.M)); dig.update(txt.encode()); nh_all |= nh
        bins = list((yaml.safe_load(txt) or {}).get('bins') or [])
        cgs = collections.Counter()
        for b in bins:
            cg, cp, bn = b.split('.', 2)
            per_cg[cg]['bins'].add(f'{cp}.{bn}'); per_cg[cg]['cps'][cp].add(bn); per_cg[cg]['manifests'][e['name']] += 1; cgs[cg] += 1; declarers[b].add(e['name'])
        per_man[e['name']] = {'bins': len(bins), 'not_hit': len(nh), 'cgs': cgs, 'tier': e.get('tier'), 'measured': e.get('measured', True)}
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
    outside_names = {o[0] for o in outside}
    in_home = [e for e in entries if e['name'] not in outside_names]
    n_named, n_files = len(in_home), len({e['fcov_expectation_file'] for e in in_home})
    share_txt = '' if n_files == n_named else f', named by {n_named} testlist entries since some entries share a file'
    files_txt = f'{n_files} manifest file' + ('' if n_files == 1 else 's')
    default_dir = pathlib.Path(a.fcov_dir).resolve() == pathlib.Path(FCOV_HOME).resolve()
    dir_txt = 'dv/auto_dv/fcov_expectations/' if default_dir else f'{a.fcov_dir} (--fcov-dir override)'
    dir_arg = '' if default_dir else f' --fcov-dir {a.fcov_dir}'
    out_arg = f' --label {a.label}' if a.label else f' --md {md_out} --csv {csv_out}'
    note_arg = '' if not a.note else f' --note {shlex.quote(a.note)}'
    said = ([f'record label {a.label} (--label), written to {clone_rel(md_out)} and {clone_rel(csv_out)}'] if a.label else []) + ([a.note] if a.note else [])
    note_txt = '' if not said else '\nRECORD NOTE: ' + '; '.join(said) + '\n'
    hdr = f"""# Minimum covergroup set referenced by the promoted fcov manifests (T-204; implementation order for TB Infra, T-205)
{note_txt}
GENERATED by dv/auto_dv/tools/gen_covergroup_set.py from dv/auto_dv/flow/gen_testlist.yaml, the {files_txt} it names under
{dir_txt}{share_txt} and gen_fcov_plan.md as read at generation (inputs digest {dig.hexdigest()[:12]} over the fcov plan, the testlist and
the named manifests; landing label {a.plan_sha}, the --plan-sha argument alone, which claims nothing about which commit's plan was read).
Regeneration command, byte for byte from the commit that carries these inputs (copy the whole line; a quoted note may contain semicolons):
python3 dv/auto_dv/tools/gen_covergroup_set.py{out_arg} --plan-sha {a.plan_sha}{dir_arg}{note_arg}

Ranking: distinct bins referenced across the manifests (a bin is counted once per covergroup even when several
manifests declare it); bins under a manifest's "# not_hit" header are excluded and not counted. A manifest is verifiable only when every
covergroup it references exists (a missing covergroup makes the per-test URG report lack the group, LOG-046), so the column "manifests
completed at this rank" names the manifests that become fully verifiable once the covergroups ranked 1..N exist. The ledger covergroup
{LEDGER_PLAN} (gen_wit_cycle_clause_cg, T-179) is marked; its bins are witness bins, excluded from the score by name. Plan anchors are the
gen_fcov_plan.md headers (file:line). Covergroups without a plan header, counted over the {len(rows)} ranked here and not
plan-wide: {len(unknown)} ({', '.join(unknown) or 'none'}).

Totals: {len(rows)} covergroups, {total_bins} distinct referenced bins, {files_txt}{share_txt}: {declared_total} declarations in total, of which
{dup_decl} are duplicate declarations of a bin another manifest also declares ({multi} distinct bins are declared by more than one manifest); a further
{len(nh_all)} distinct bins_not_hit bins are not declared by any manifest (counted once across the named manifest files; the per-manifest table below lists each entry's own count).

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
        mt += "\nAn extra manifest leaves this list by one of two routes, and which route applies is a plan statement rather than something this tool derives: it ENTERS the ranking when its testlist entries are committed (a staged entry is not an input of this file), or it is RETIRED rather than ever being referenced when a ruling replaces it with per-entry manifests. The covergroup's record in gen_fcov_plan.md names the route for each manifest listed here.\n"
    else:
        mt += "None: every committed manifest is named by the committed testlist.\n"
    mt += "\n## Entries whose manifest lies outside the manifest home (not read, not counted)\n\n"
    if outside:
        mt += "| Entry | Tier | measured | Manifest named |\n|---|---|---|---|\n" + ''.join(f"| {n} | {tr} | {str(bool(m)).lower()} | {p} |\n" for n, p, tr, m in outside)
        mt += f"\nA manifest outside {home_rel} is a proof manifest kept as evidence, not a promotion manifest: its entry hosts no bins of this set until a manifest under the home names them. Only an unmeasured entry outside the required tiers ({', '.join(sorted(required_tiers))}) is listed; a measured or required-tier entry with such a manifest stops this tool.\n"
    else: mt += "None.\n"
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
    pathlib.Path(md_out).write_text(out)
    with open(csv_out, 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
    print(f'{len(rows)} covergroups, {total_bins} referenced bins, {len(entries) - len(outside)} manifests; extra committed manifests {len(extra)}; ledger in ranking {any(cg in ledger_impls for cg in per_cg)}; unknown {unknown}; wrote {md_out}, {csv_out}')

if __name__ == '__main__': main()
