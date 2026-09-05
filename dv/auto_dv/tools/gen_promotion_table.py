#!/usr/bin/env python3
"""Generate the per-round tier-ruling table dv/auto_dv/evidence/gen_<label>_promotion_table.md from the plan and the testlist (the held-items
column is derived from the hold sections present in gen_test_plan.md ("## 1.<n> Items under the T-<xxx> measurement hold"), never written by hand).

Per built testlist entry (gen_test_<x>, red fixtures excluded; gen_test_boot_retire stays at tier check): the plan group
gen_<x> of gen_test_<x>, its items with the smoke / targeted split, the tier ruling (the LOWEST tier among the group's items,
because the testlist runs a tier-T entry in every higher tier), the seeds, and the held items = the group's items listed in the
plan's hold tables (whichever hold sections the plan carries at generation; a lifted hold's section is gone), recorded in a round and never credited.

Usage: gen_promotion_table.py (--label ROUND | --out <path>) [--plan-dir dv/auto_dv/docs] [--testlist dv/auto_dv/flow/gen_testlist.yaml] [--plan-sha <sha>] [--note TEXT]
"""
import re, sys, shlex, argparse, pathlib, collections, hashlib, yaml
R = pathlib.Path(__file__).resolve()
while not (R / 'dv/auto_dv/contract').is_dir():
    if R.parent == R: sys.exit('repo root not found (no dv/auto_dv/contract above this file)')
    R = R.parent
sys.path.insert(0, str(R / 'dv/auto_dv/tools')); from gen_plan_holds import hold_items  # one home for the hold-section discovery
TIER_ORDER = {'smoke': 0, 'targeted': 1, 'full': 2}
EVIDENCE_HOME = R / 'dv/auto_dv/evidence'

def out_path(a):
    """The record's own location, from --label or from an explicit path. There is no default, so a bare run writes nowhere
    instead of over whichever record a default happens to name."""
    if a.label and a.out: sys.exit('--label and --out are exclusive: pass one or the other')
    if a.label:
        if not re.fullmatch(r'[A-Za-z0-9_]+', a.label): sys.exit(f'--label {a.label!r}: the label becomes a file name, so letters, digits and underscore only')
        return str(EVIDENCE_HOME / f'gen_{a.label}_promotion_table.md')
    if a.out: return a.out
    sys.exit('no output location: pass --label <team round name>, or --out <path>')

def clone_rel(p):
    q = pathlib.Path(p).resolve()
    return str(q.relative_to(R.resolve())) if q.is_relative_to(R.resolve()) else str(q)
# hand-kept notes on not_built clauses (the Test Writer's modules state them); they never affect the held column
NOTES = {'gen_test_bit_draft': 'TP-BIT-011, 022..033 not_built until the shim extension is confirmed',
         'gen_test_isa_cti': 'TP-ISA-016 / 022 / 026 also not_built on WP-9',
         'gen_test_isa_alu': 'TP-ISA-006 high / low bins not_built on WP-9'}

def load_plan(plan_dir):
    plan = (plan_dir / 'gen_test_plan.md').read_text()
    items = {}
    for m in re.finditer(r'^### (TP-[A-Z]+-\d{3}):(.*?)(?=^### |^## |^# |\Z)', plan, re.M | re.S):
        b = m.group(2); g = re.search(r'^- Test group: (\S+)', b, re.M); t = re.search(r'^- Tier: (\w+)', b, re.M)
        items[m.group(1)] = (g.group(1) if g else '-', t.group(1) if t else '?')
    holds, secs = hold_items(plan); sections = [f'{sec} {tag}' for sec, tag in secs]
    return items, holds, sections

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--plan-dir', default=str(R / 'dv/auto_dv/docs')); ap.add_argument('--testlist', default=str(R / 'dv/auto_dv/flow/gen_testlist.yaml'))
    ap.add_argument('--out', default=None); ap.add_argument('--plan-sha', default=None)
    ap.add_argument('--label', default=None, help='team round name; it names the record file gen_<label>_promotion_table.md under dv/auto_dv/evidence (exclusive with --out, and there is no default)')
    ap.add_argument('--note', default=None, help='provenance sentence printed in the header and echoed in the regeneration command; asserted by the invoker, not checked by the tool (the inputs digest is the checked part)')
    a = ap.parse_args()
    out_file = out_path(a)
    items, holds, sections = load_plan(pathlib.Path(a.plan_dir))
    tl = yaml.safe_load(open(a.testlist))
    entries = [e for e in tl.get('tests', []) if str(e.get('name', '')).startswith('gen_test_') and not str(e['name']).endswith('_red') and not e.get('red_fixture') and not e.get('red_expect')]  # the built tests, not their red fixtures
    sha = a.plan_sha or 'unlabelled'   # a label for the landing, never a claim about which commit's plan was read
    plan_bytes = (pathlib.Path(a.plan_dir) / 'gen_test_plan.md').read_bytes(); tl_bytes = pathlib.Path(a.testlist).read_bytes()
    digest = f"inputs read: gen_test_plan.md sha256 {hashlib.sha256(plan_bytes).hexdigest()[:12]}, gen_testlist.yaml sha256 {hashlib.sha256(tl_bytes).hexdigest()[:12]}"
    rows = []; held_total = 0; held_groups = set(); held_by_tag = collections.Counter()
    for e in entries:  # testlist order
        name = e['name']; group = re.sub(r'^gen_test_', 'gen_', name)
        gitems = sorted(t for t, (g, _) in items.items() if g == group)
        seeds = e.get('seeds'); seeds = len(seeds) if isinstance(seeds, list) else seeds
        if not gitems:
            rows.append(f"| {name} | none (flow boot / retire check, no plan items) | - | {e.get('tier', 'check')} (unchanged), measured: {str(bool(e.get('measured', False))).lower()} | {seeds} | - |"); continue
        tiers = collections.Counter(items[t][1] for t in gitems)
        ruling = min((items[t][1] for t in gitems), key=lambda x: TIER_ORDER.get(x, 9))
        held = [(t, holds[t]) for t in gitems if t in holds]
        held_txt = '; '.join(f"{t} ({', '.join(tags)})" for t, tags in held) or '-'
        for t, tags in held:
            held_total += 1; held_groups.add(group)
            for tag in tags: held_by_tag[tag] += 1
        note = NOTES.get(name)
        if note: held_txt = f'- ({note})' if held_txt == '-' else f'{held_txt}; {note}'
        listed = e.get('tier', '?')
        if listed == 'check' and not e.get('measured', False): ruling, flag = f'check (first landing, measured: false; promotion candidate {ruling})', ''
        else: flag = '' if listed == ruling else f' (TESTLIST SAYS {listed})'
        rows.append(f"| {name} | {group} | {len(gitems)} ({tiers.get('smoke', 0)} / {tiers.get('targeted', 0)}) | {ruling}{flag} | {seeds} | {held_txt} |")
    out_arg = f' --label {a.label}' if a.label else f' --out {out_file}'
    note_arg = '' if not a.note else f' --note {shlex.quote(a.note)}'
    said = ([f'record label {a.label} (--label), written to {clone_rel(out_file)}'] if a.label else []) + ([a.note] if a.note else [])
    note_txt = '' if not said else '\nRECORD NOTE: ' + '; '.join(said) + '\n'
    hdr = f"""# Per-entry tier ruling for the {len(entries)} built tests (DV Lead; applied by the Test Writer's landing 3e at 7ef16a0 and Runtime's promotion landing 3e6f1b2; LOG-024e, LOG-039)
{note_txt}
GENERATED by dv/auto_dv/tools/gen_promotion_table.py from gen_test_plan.md and dv/auto_dv/flow/gen_testlist.yaml as read at generation ({digest};
landing label {sha}, the --plan-sha argument alone, which claims nothing about which commit's plan was read).
Regeneration command, byte for byte from the commit that carries these inputs (copy the whole line; a quoted note may contain semicolons):
python3 dv/auto_dv/tools/gen_promotion_table.py{out_arg} --plan-sha {sha}{note_arg}

The group of
gen_test_<x> is gen_<x>; the item counts and the smoke / targeted split come from the items' Tier fields; the tier ruling is the LOWEST tier
among the group's items, because the testlist runs a tier-T entry in every higher tier too (gen_testlist.yaml header); an entry with no plan
group stays at tier check, measured: false; the seeds are the testlist's. The "Held items" column is derived from the plan's hold sections
present at generation ({', '.join('Section ' + x for x in sections) or 'none'}; a lifted hold's section is gone), never written by hand (Critic v9 CR9-M-1): {held_total} held items over
{len(held_groups)} groups today ({', '.join(f'{k}: {v}' for k, v in sorted(held_by_tag.items()))}); held items run measured but their
results are recorded, not credited, until the hold lifts. Parenthesised not_built notes are the Test Writer's module statements, kept by
hand; they do not affect the held column. gen_ut_lockstep (tb-infra's lock-step check, no plan items, no manifest) is measured: false in
the promotion landing per LOG-039 and is not a row of this table.

| Entry (gen_test_<x>) | Plan group | Items (smoke / targeted) | Tier ruling | Seeds | Held items excluded from crediting |
|---|---|---|---|---|---|
"""
    out = hdr + '\n'.join(rows) + '\n'
    assert not [c for c in out.encode() if c > 127]
    pathlib.Path(out_file).write_text(out)
    print(f'{out_file}: {len(rows)} entries; held {held_total} items over {len(held_groups)} groups {dict(held_by_tag)}; plan {sha}')

if __name__ == '__main__': main()
