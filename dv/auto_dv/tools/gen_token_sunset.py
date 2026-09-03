#!/usr/bin/env python3
"""Cycle-clause sunset (gen_test_plan.md Section 0, operational rule): remove the marker token from every marked item whose
export rows were ALL OBSERVED in a retained run of the pinned build (the build manifest's export_rows_observed list, LOG-028a;
export_sources_emitted only bounds the candidate set), then regenerate and prove gen_trace_check.py passes against that manifest.
The DV Lead runs it once per observed-list landing; each pass retains its manifest copy, this RELEASED / GATED output and the
tool's before / after output under dv/auto_dv/evidence/gen_sunset_pass<n>/; the Test Writer regenerates the affected manifests (rule (f)).

Usage: gen_token_sunset.py --build-manifest <path> [--observed-field <key>] [--observed-rows "a b; c d"] [--exclude-rows "a b; c d"] [--dry | --rehearse]
  LOG-028a: an item loses the token only when EVERY one of its [export-rows: ...] was OBSERVED in a retained run of the pinned
  build (Runtime's per-row first-seen list in the build manifest, T-140); exclusion is by row, never by source; with no
  observed list the sunset is refused (never the rendered table, never the emitted declaration alone).
  --observed-field  manifest key of the observed-row list (default export_rows_observed; entries {source, event, ...} or strings)
  --observed-rows   rehearsal override: the observed rows as a semicolon-separated list (accepted only with --dry or --rehearse)
  --exclude-rows    rehearsal override: observed = the emitted rows minus these (accepted only with --dry or --rehearse)
  --dry             list, per item, RELEASED with its rows or GATED with the rows not observed; write nothing
  --rehearse        apply to scratch copies of the parts, generate into the scratchpad, run the tool there with the manifest
Output: one line per marked item whose rows are all emitted, RELEASED or GATED with the gating rows (retained under
dv/auto_dv/evidence/gen_sunset_pass<n>/ with the landing). The plan parts it edits live under dv/auto_dv/work/dv-lead (gitignored).
"""
import os, sys, re, pathlib, shutil, subprocess, yaml
R = next(p for p in pathlib.Path(__file__).resolve().parents if (p / 'dv/auto_dv/contract').is_dir()); W = R / 'dv/auto_dv/work/dv-lead'
S = pathlib.Path(os.environ.get('GEN_SCRATCH', str(W / 'scratch_sunset')))  # rehearsal copies; never the docs directory
TOKEN = '[CYCLE-CLAUSE coverage-only until the event export lands]'
AREAS = ['isa', 'csr', 'exc_irq', 'pmp', 'dbg_trg_pmc', 'mem_fetch_icache', 'sec_rst_rvfi_cheri', 'xcut']
args = sys.argv[1:]; manifest = None; dry = '--dry' in args; rehearse = '--rehearse' in args
if '--build-manifest' in args: manifest = pathlib.Path(args[args.index('--build-manifest') + 1])
obs_field = args[args.index('--observed-field') + 1] if '--observed-field' in args else 'export_rows_observed'
obs_override = args[args.index('--observed-rows') + 1] if '--observed-rows' in args else None
excl_override = args[args.index('--exclude-rows') + 1] if '--exclude-rows' in args else None
if not manifest or not manifest.exists(): sys.exit('usage: --build-manifest <existing path>')
if (obs_override is not None or excl_override is not None) and not (dry or rehearse): sys.exit('REHEARSAL OVERRIDE REFUSED: --observed-rows / --exclude-rows stand in for the observed list only with --dry or --rehearse; a real release reads the manifest')
man = yaml.safe_load(open(manifest)) or {}
if 'export_sources_emitted' not in man: sys.exit('manifest has no export_sources_emitted field: nothing sunsets on the rendered table')
emitted = {(x['row'] if isinstance(x, dict) and 'row' in x else (f"{x['source']} {x['event']}" if isinstance(x, dict) else str(x))) for x in (man['export_sources_emitted'] or [])}
def present(tok): return any(re.fullmatch(r'pin irq_fast\d*', r) for r in emitted) if tok == 'pin irq_fast' else tok in emitted
def split_rows(txt):
    out = []; depth = 0; cur = ''
    for ch in txt:
        if ch == '(': depth += 1
        if ch == ')': depth -= 1
        if ch == ';' and depth == 0: out.append(cur.strip()); cur = ''
        else: cur += ch
    if cur.strip(): out.append(cur.strip())
    return out
def rowset(v):  # entries: {row: "<source> <event>", first_run, first_line} (Runtime T-140), {source, event[, fields]} or "<source> <event>"
    return {(x['row'] if 'row' in x else f"{x['source']} {x['event']}") if isinstance(x, dict) else str(x) for x in (v or [])}
if obs_override is not None: observed = {r.strip() for r in obs_override.split(';') if r.strip()}; obs_origin = 'rehearsal override (--observed-rows)'
elif excl_override is not None: observed = emitted - {r.strip() for r in excl_override.split(';') if r.strip()}; obs_origin = 'rehearsal override: emitted minus --exclude-rows'
elif obs_field in man: observed = rowset(man[obs_field]); obs_origin = f'manifest key {obs_field}'
else: sys.exit(f'SUNSET REFUSED: the manifest has export_sources_emitted ({len(emitted)} rows) but no observed-row list ({obs_field}, T-140); no item loses its token on a declaration')
def observed_ok(tok): return any(re.fullmatch(r'pin irq_fast\d*', r) for r in observed) if tok == 'pin irq_fast' else tok in observed
plan = []; gated = []
for a in AREAS:
    p = W / f'parts6/tp_{a}.md'; t = p.read_text(); edits = []
    for m in re.finditer(r'^### (TP-[A-Z]+-\d{3}):(.*?)(?=^### |^## |\Z)', t, re.M | re.S):
        b = m.group(2); tid = m.group(1)
        if TOKEN not in b: continue
        er = re.search(r'\[export-rows: (.*?)\]', b)
        rows = [r for r in split_rows(er.group(1)) if not r.startswith('none')] if er else []
        g = re.search(r'^- Test group: (\S+)', b, re.M); g = g.group(1) if g else '-'
        if not rows: continue  # no export row: never released by the tool
        not_emitted = [r for r in rows if not present(r)]
        not_observed = [r for r in rows if not observed_ok(r)]
        if not not_observed:
            edits.append((tid, g, rows))
        elif not not_emitted:
            gated.append((tid, g, not_observed))  # emitted (declared) but never observed: LOG-028a keeps the token
    plan.append((p, edits))
items = [(tid, g, rows) for _, e in plan for tid, g, rows in e]
groups = {}
for tid, g, _ in items: groups[g] = groups.get(g, 0) + 1
print(f'manifest {manifest}: emitted {len(emitted)} rows; observed {len(observed)} rows ({obs_origin}); never observed among the emitted: {sorted(emitted - observed)}')
print(f'WOULD UN-MARK {len(items)} marked items across {len(groups)} groups (every row observed); GATED {len(gated)} items whose rows are all emitted but include a row never observed')
for tid, g, rows in items: print(f'  RELEASED {tid}  {g}  rows: {"; ".join(rows)}')
for tid, g, rows in gated: print(f'  GATED    {tid}  {g}  rows never observed: {"; ".join(rows)}')
if dry: sys.exit(0)
def apply(parts_root):
    n = 0
    for p, edits in plan:
        q = parts_root / 'parts6' / p.name; t = q.read_text()
        for tid, _, _ in edits:
            m = re.search(r'^### ' + tid + r':(.*?)(?=^### |^## |\Z)', t, re.M | re.S); blk = m.group(0)
            assert TOKEN in blk
            blk2 = blk.replace(' ' + TOKEN, '', 1) if ' ' + TOKEN in blk else blk.replace(TOKEN, '', 1)
            t = t[:m.start()] + blk2 + t[m.end():]; n += 1
        q.write_text(t)
    return n
if rehearse:
    S.mkdir(parents=True, exist_ok=True)
    for d in ('parts_dry', 'docs_dry'):
        shutil.rmtree(S / d, ignore_errors=True); (S / d).mkdir()
    shutil.copytree(W / 'parts', S / 'parts_dry' / 'parts'); shutil.copytree(W / 'parts6', S / 'parts_dry' / 'parts6')
    shutil.copy(R / 'dv/auto_dv/docs/gen_bug_log.md', S / 'docs_dry' / 'gen_bug_log.md')
    print('rehearsal: tokens removed', apply(S / 'parts_dry'))
    bs = (W / 'gen_build_docs.py').read_text().replace("W = ROOT/'dv/auto_dv/work/dv-lead'; D = ROOT/'dv/auto_dv/docs'", f"W = pathlib.Path('{S}/parts_dry'); D = pathlib.Path('{S}/docs_dry')", 1)
    assert 'parts_dry' in bs; (S / 'gen_build_docs_rehearse.py').write_text(bs)
    r = subprocess.run(['python3', str(S / 'gen_build_docs_rehearse.py')], capture_output=True, text=True)
    print('rehearsal build:', (r.stdout.strip().splitlines() or [''])[-1], '| stderr:', r.stderr.strip()[-300:] or 'none')
    if r.returncode: sys.exit('rehearsal build FAILED')
    tool = (R / 'dv/auto_dv/tools/gen_trace_check.py').read_text().replace("R = pathlib.Path(__file__).resolve().parents[1]; D = R / 'docs'", f"R = pathlib.Path('{R}/dv/auto_dv'); D = pathlib.Path('{S}/docs_dry')", 1)
    (S / 'gen_trace_check_rehearse.py').write_text(tool)
    r = subprocess.run(['python3', str(S / 'gen_trace_check_rehearse.py'), '--build-manifest', str(manifest)], capture_output=True, text=True)
    lines = r.stdout.strip().splitlines()
    print('rehearsal tool with the manifest:', [l for l in lines if l.startswith(('sunset', 'cycle-clause', 'PASS', 'FAIL'))], '| exit', r.returncode)
    wit = (S / 'docs_dry' / 'gen_trace_witness_ids.csv').read_text().splitlines()[1:]
    print('  witness CSV marked=1:', sum(1 for l in wit if l.endswith(',1')), 'marked=0:', sum(1 for l in wit if l.endswith(',0')))
    sys.exit(r.returncode)
print('tokens removed', apply(W))
print(subprocess.run(['python3', str(W / 'gen_build_docs.py')], capture_output=True, text=True).stdout.splitlines()[-1])
r = subprocess.run(['python3', str(R / 'dv/auto_dv/tools/gen_trace_check.py'), '--build-manifest', str(manifest)], capture_output=True, text=True)
print([l for l in r.stdout.splitlines() if l.startswith(('sunset', 'cycle-clause', 'PASS', 'FAIL'))]); sys.exit(r.returncode)
