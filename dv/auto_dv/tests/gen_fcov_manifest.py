#!/usr/bin/env python3
"""gen_fcov_manifest: render a test's fcov-expectation manifest from the plan's traceability CSV.

A test hosts one test-plan group (dv/auto_dv/docs/gen_test_plan.md Section 3); its declared bins are
the union of its items' bins in dv/auto_dv/docs/gen_trace_tp_bin.csv (columns tp_item, covergroup,
coverpoint, bin, adopted), written as gen_<name>_cg.<coverpoint>.<bin> tokens with one anti-vacuity
note per bin taken from the covergroup's Sample line in gen_fcov_plan.md (schema:
dv/auto_dv/docs/gen_runtime_api.md Section 7c).

Manifest rule of gen_fcov_plan.md Section 0 (DV Lead acceptance of the Test Writer plan, change 1):
excluded are (a) the bins of informational items (`- Expected: informational`), (b) every bin of an
item whose `- Manifest:` field says `not in manifest` (probe-gated items), (c) bins of a coverpoint
whose plan line carries `not in manifest` (probe-gated coverpoints), (d) bins named as a bug witness
in the plan (`<bin> is the B<n> witness bin`, `the <bins> are the B<n> witnesses`), (e) the
regression-level coverpoints of gen_fcov_plan.md Section 1.1 (owned by no item). The CSV already
lists every auto-cross bin expanded; the generator EXPANDS NOTHING, it validates each `_`-joined cross
bin against the very `segmentable` rule of dv/auto_dv/tools/gen_trace_check.py (loaded from that
file's source, never re-implemented here); a bin that fails it is a plan-vs-CSV drift and stops the
generator. The excluded-coverpoint count printed by --self-test depends on the plan version in the
tree (recorded with the SHA in the evidence).

Plan covergroup ids (CG-<AREA>-<nnn>) map to implementation names through the plan header
`### CG-<AREA>-<nnn>: gen_cg_<area>_<name>` and the architecture rule (Section 5): plan
`gen_cg_<x>` = implementation `gen_<x>_cg`; confirmed against URG's grpinfo.txt at the first
covergroup.

Usage (host, no simulator):
    gen_fcov_manifest.py --group gen_isa_alu --test gen_test_isa_alu [--write]   # print or write
    gen_fcov_manifest.py --items TP-ISA-001,TP-ISA-002 --test gen_test_x [--write]
    gen_fcov_manifest.py --self-test
"""
import argparse
import ast
import csv
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
DOCS = REPO_ROOT / "dv/auto_dv/docs"
TP_BIN_CSV = DOCS / "gen_trace_tp_bin.csv"
TEST_PLAN = DOCS / "gen_test_plan.md"
FCOV_PLAN = DOCS / "gen_fcov_plan.md"
TRACE_CHECK = REPO_ROOT / "dv/auto_dv/tools/gen_trace_check.py"
FCOV_HOME = REPO_ROOT / "dv/auto_dv/fcov_expectations"
OWNER = "test-writer"
NOT_IN_MANIFEST = "not in manifest"


def cg_blocks():
    """CG id -> its plan block text (same block rule as gen_trace_check.py)."""
    text = FCOV_PLAN.read_text()
    return {m.group(1): m.group(2) for m in
            re.finditer(r"^### (CG-[A-Z]+-\d{3}):(.*?)(?=^### |^## |^# |\Z)", text, re.M | re.S)}


def tp_blocks():
    text = TEST_PLAN.read_text()
    return {m.group(1): m.group(2) for m in
            re.finditer(r"^### (TP-[A-Z]+-\d{3}):(.*?)(?=^### |^## |^# |\Z)", text, re.M | re.S)}


def plan_cg_names():
    """CG-<AREA>-<nnn> -> plan SV name (gen_cg_<area>_<name>) from the coverage plan headers."""
    names = {}
    for m in re.finditer(r"^### (CG-[A-Z]+-\d+): (gen_cg_\w+)", FCOV_PLAN.read_text(), re.M):
        names[m.group(1)] = m.group(2)
    assert names, f"{FCOV_PLAN}: no covergroup headers found"
    return names


def impl_cg_name(plan_name):
    """Architecture Section 5: plan gen_cg_<x> is implemented as gen_<x>_cg (confirmed at build)."""
    assert plan_name.startswith("gen_cg_"), plan_name
    return "gen_" + plan_name[len("gen_cg_"):] + "_cg"


def cg_sample_notes(blocks):
    """CG id -> the anti-vacuity sentence of its Sample line (the note every bin of the group carries)."""
    notes = {}
    for cg, blk in blocks.items():
        m = re.search(r"^- Sample:(.*)$", blk, re.M)
        if m:
            av = re.search(r"anti-vacuity:\s*(.+)$", m.group(1))
            notes[cg] = (av.group(1) if av else m.group(1)).strip().rstrip(".")
    return notes


def load_segmentable():
    """The `segmentable` rule exactly as gen_trace_check.py defines it: its function source is taken
    from that file's AST and compiled here, so the manifest and the plan cannot drift apart."""
    tree = ast.parse(TRACE_CHECK.read_text())
    fns = [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name == "segmentable"]
    if len(fns) != 1:
        raise SystemExit(f"GEN_FCOV_MANIFEST_INPUT_VERSION: {TRACE_CHECK} defines {len(fns)} segmentable() functions; this "
                         "generator needs the DV Lead's plan-set version with exactly one (the cross-bin rule). Wrong tree version.")
    code = compile(ast.Module(body=[fns[0]], type_ignores=[]), str(TRACE_CHECK), "exec")

    def make(words):
        ns = {"words": words}
        exec(code, ns)
        return ns["segmentable"]
    return make


def excluded_coverpoints(blocks):
    """(CG id, coverpoint) pairs excluded by rule (c) and (e), plus (CG id, bin) pairs by rule (d)."""
    cps = set()
    bins = set()
    for cg, blk in blocks.items():
        for line in blk.splitlines():
            m = re.match(r"^\s*- (c[pr]_[a-z0-9_]+)\b(.*)$", line)
            if m and NOT_IN_MANIFEST in m.group(2):
                # a per-bin marker (`not in manifest: <bin>`) excludes those bins only
                mb = re.search(r"not in manifest:\s*([a-z0-9_, ]+)", m.group(2))
                if mb:
                    for b in re.split(r"[,\s]+", mb.group(1).strip()):
                        if b:
                            bins.add((cg, b))
                else:
                    cps.add((cg, m.group(1)))
        for m in re.finditer(r"\b([a-z][a-z0-9_]*) is the B\d+ witness bin", blk):
            bins.add((cg, m.group(1)))
        for m in re.finditer(r"the ([a-z0-9_*]+) bins are the B\d+ witnesses", blk):
            bins.add((cg, m.group(1)))   # glob form (`*_odd_b1`) matched below
    # rule (e): Section 1.1 table rows `| CG-... | cp_... | owners |`
    text = FCOV_PLAN.read_text()
    sec = re.search(r"^# 1\.1 .*?(?=^# 2\.)", text, re.M | re.S)
    if not sec:
        raise SystemExit(f"GEN_FCOV_MANIFEST_INPUT_VERSION: {FCOV_PLAN} has no Section 1.1 (regression-level coverpoints); this "
                         "generator needs the DV Lead's plan-set version that lists them. Wrong tree version.")
    rows = re.findall(r"^\| (CG-[A-Z]+-\d{3}) \| (c[pr]_[a-z0-9_]+) \|", sec.group(0), re.M)
    if not rows:
        raise SystemExit(f"GEN_FCOV_MANIFEST_INPUT_VERSION: {FCOV_PLAN} Section 1.1 has no coverpoint rows. Wrong tree version.")
    for cg, cp in rows:
        cps.add((cg, cp))
    return cps, bins


def bin_excluded(cg, b, ex_bins):
    for ecg, eb in ex_bins:
        if ecg != cg:
            continue
        if eb == b or ("*" in eb and re.fullmatch(eb.replace("*", "[a-z0-9_]+"), b)):
            return True
    return False


def items_of_group(group, tps=None):
    """TP ids whose `- Test group:` line names the group (test plan Section 4 items)."""
    tps = tps or tp_blocks()
    items = [t for t, blk in tps.items() if re.search(rf"^- Test group:\s*{re.escape(group)}\b", blk, re.M)]
    assert items, f"no test-plan item names group {group}"
    return items


def item_excluded(blk):
    """Rules (a) and (b): the whole item contributes no manifest bin."""
    if re.search(r"^- Expected:\s*informational", blk, re.M):
        return "informational"
    m = re.search(r"^- Manifest:(.*)$", blk, re.M)
    if m and NOT_IN_MANIFEST in m.group(1):
        return "probe-gated item"
    return None


def bins_of_items(items, tps, blocks, make_segmentable):
    """[(cg_id, coverpoint, bin, adopted)] after the manifest rule; drift stops the generator."""
    want = {}
    dropped = []
    for t in items:
        why = item_excluded(tps[t])
        if why:
            dropped.append((t, "*", "*", why))
        else:
            want[t] = True
    ex_cps, ex_bins = excluded_coverpoints(blocks)
    rows = []
    seen = set()
    words_of = {}
    with open(TP_BIN_CSV, newline="") as f:
        for r in csv.DictReader(f):
            if r["tp_item"] not in want:
                continue
            cg, cp, b = r["covergroup"], r["coverpoint"], r["bin"]
            key = (cg, cp, b)
            if key in seen:
                continue
            seen.add(key)
            if (cg, cp) in ex_cps:
                dropped.append((r["tp_item"], f"{cg}.{cp}", b, "probe-gated or regression-level coverpoint"))
                continue
            if bin_excluded(cg, b, ex_bins):
                dropped.append((r["tp_item"], f"{cg}.{cp}", b, "witness or probe-gated bin"))
                continue
            blk = re.sub(r"\n\s+", " ", blocks[cg])
            if cp.startswith("cr_") and not re.search(r"\b" + re.escape(b) + r"\b", blk):
                if cg not in words_of:
                    words_of[cg] = set(re.findall(r"\b[a-z][a-z0-9_]*\b", blk))
                assert make_segmentable(words_of[cg])(b), \
                    f"plan drift: cross bin {cg}.{cp}.{b} (item {r['tp_item']}) does not segment into declared bins of {cg}"
            rows.append((cg, cp, b, r["adopted"] == "1"))
    assert rows, f"no manifest bins left for {sorted(want)}"
    return rows, dropped


def render(test, rows, notes, names):
    tokens = []
    for cg, cp, b, adopted in rows:
        tok = f"{impl_cg_name(names[cg])}.{cp}.{b}"
        note = notes.get(cg, "see the covergroup's Sample line")
        tokens.append((tok, cg, note + ("; adopted from riscv-dv, counted separately" if adopted else "")))
    out = [f"test: {test}", f"owner: {OWNER}", "bins:"]
    out += [f"  - {t}" for t, _, _ in tokens]
    out.append("anti_vacuity:")
    # notes are YAML double-quoted scalars: escape backslashes and double quotes taken from the plan text
    out += ['  {}: "{}"'.format(t, f"{cg}: {n}".replace("\\", "\\\\").replace('"', '\\"')) for t, cg, n in tokens]
    text = "\n".join(out) + "\n"
    assert all(ord(c) < 128 for c in text), "manifest text is not ASCII"
    return text


def build(test, items):
    tps = tp_blocks()
    blocks = cg_blocks()
    rows, dropped = bins_of_items(items, tps, blocks, load_segmentable())
    return render(test, rows, cg_sample_notes(blocks), plan_cg_names()), rows, dropped


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--group")
    ap.add_argument("--items")
    ap.add_argument("--test")
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        import subprocess
        head = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=REPO_ROOT, capture_output=True, text=True).stdout.strip()
        dirty = subprocess.run(["git", "status", "--short", "--", str(TRACE_CHECK), str(FCOV_PLAN), str(TEST_PLAN), str(TP_BIN_CSV)],
                               cwd=REPO_ROOT, capture_output=True, text=True).stdout.strip().splitlines()
        print(f"GEN_FCOV_MANIFEST inputs at git HEAD {head}; working-tree modified inputs: {[d.split()[-1] for d in dirty] or 'none'}")
        tps = tp_blocks()
        items = items_of_group("gen_reg_schedule", tps)
        assert "TP-REG-018" in items and "TP-REG-019" in items, items
        text, rows, dropped = build("gen_test_reg_schedule", items)
        assert "gen_reg_schedule_cg.cp_phase_count.k2" in text, text[:400]
        assert any(cg == "CG-REG-007" and cp == "cp_phase_count" for cg, cp, _, _ in rows)
        # rule (a): an informational item contributes nothing
        info_items = items_of_group("gen_isa_illegal_info", tps)
        try:
            build("gen_test_isa_illegal_info", info_items)
            raise AssertionError("informational item produced manifest bins")
        except AssertionError as exc:
            assert "no manifest bins left" in str(exc), exc
        # rule (b): a probe-gated item (gen_xif_dummy, `- Manifest: ... not in manifest`) contributes nothing
        try:
            build("gen_test_xif_dummy", items_of_group("gen_xif_dummy", tps))
            raise AssertionError("probe-gated item produced manifest bins")
        except AssertionError as exc:
            assert "no manifest bins left" in str(exc), exc
        # rule (e): a Section 1.1 coverpoint is dropped (CG-MUL-002.cp_dmem_delay is regression-level)
        ex_cps, _ = excluded_coverpoints(cg_blocks())
        assert ("CG-MUL-002", "cp_dmem_delay") in ex_cps
        # the segmentation rule is the trace checker's own
        seg = load_segmentable()({"same_cycle", "min1", "short"})
        assert seg("same_cycle_min1") and seg("short_short") and not seg("same_cycle_max")
        print(f"GEN_FCOV_MANIFEST self-test PASS ({len(rows)} bins for gen_reg_schedule, {len(dropped)} dropped; "
              f"{len(ex_cps)} excluded coverpoints)")
        return 0
    if not a.test or not (a.group or a.items):
        ap.error("--test and one of --group / --items are required")
    tps = tp_blocks()
    items = items_of_group(a.group, tps) if a.group else a.items.split(",")
    text, rows, dropped = build(a.test, items)
    for d in dropped:
        print(f"# dropped {d[0]} {d[1]} {d[2]}: {d[3]}", file=sys.stderr)
    if a.write:
        FCOV_HOME.mkdir(parents=True, exist_ok=True)
        path = FCOV_HOME / f"{a.test}.fcov.yaml"
        path.write_text(text)
        print(f"wrote {path} ({len(rows)} bins, {len(dropped)} dropped by the manifest rule)")
    else:
        sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
