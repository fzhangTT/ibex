# Sidecar to gen_fu_bit_ratified_rev58.log: the script behind it, the red seeds, the comparison it ran (rev67)

WHY A SIDECAR. gen_fu_bit_ratified_rev58.log is retained and is never reopened; rev67 found that a reader of the log alone
cannot tell what comparison was run, at which red seeds, or by which script, and that one emitted comment line in its
Section D is cut mid-word. This file carries all three. The log's Sections A-D are the output of the script below, run in
the clone at HEAD df490cc with the committed generator loaded from the export dv/auto_dv/work/test-writer/head_export19
(git archive of 9c28944; its gen_bit_ratified_prog.py is the block's pin 70f318080711...) and the candidate from the clone.

THE COMPARISON, exactly. For every seed the script builds both plans, `H.plan(seed)` and `C.plan(seed)`, and compares (a)
the full emitted program text, `H.emit(ph) == C.emit(pc)`, comment lines included; (b) the report word list, k and
min_retired as a tuple; (c) each item's ops list: the candidate's must equal the committed list minus its no-report
member, disjoint from the new "unreported" list. Section A runs this at 80 green seeds (1..40 and the block's forty from
gen_pairfix_seeds.txt). Section B runs the red forms: for every one of the 18 built items (BUILT_ITEMS) at seeds 1, 2 and 3,
`plan(seed, red=True, red_item=item)`, comparing the emitted text and the report words: 54 (item, seed) pairs. A program
that differed in any byte, or a report stream that differed in any word, would fail the equality and the log would say
FAIL; it says PASS because none did.

THE THREE RED SEEDS: 1, 2, 3, for each of TP-BIT-002, 003, 004, 005, 006, 007, 008, 009, 010, 014, 015, 017, 018, 019,
020, 021, 038, 040 (the generator's BUILT_ITEMS in order).

SECTION D'S COMMENT LINE, whole (the log prints its first 90 characters):
  # op 432: TP-BIT-018 binvi imm=0 floor rs1=distinct_lanes 0xcf49bd28 -> 0xcf49bd29 (not reported: the next op must retire immediately after this one)

## The script, as run (sha256 b506527906b8329452c845ba4e913dff3976a40b5016245a40c8e1dc56500753)

```python
"""Build gen_fu_bit_ratified_rev58.log: the rev58 follow-up leaves every emitted bit_ratified program byte-identical to the
generator the block measured (blob 70f31808, HEAD's), at the block's forty seeds and 1..40, green and every red item, so the
entry's block authority is untouched; the no-report op is counted apart in the plan's items and the test's _ok needs a
report word. Exit 0 only when every expectation holds."""
import hashlib, importlib.util, sys, datetime, subprocess
from pathlib import Path
CLONE = Path("/localdev/fzhang/ws/ibex-challenge")
EXPORT = CLONE / "dv/auto_dv/work/test-writer/head_export19"     # git archive of 9c28944; its bit_ratified generator is HEAD's blob
PIN = "70f318080711d7845c88341a012461bd21d57695536daf2db33189a675a3b8d0"
fails = []
def expect(c, m):
    print(("  ok    " if c else "  FAIL  ") + m)
    if not c: fails.append(m)
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def git(*a): return subprocess.check_output(["git", "-C", str(CLONE), *a], text=True)
def load(name, root):
    sys.path.insert(0, str(root))
    spec = importlib.util.spec_from_file_location(name, root / "dv/auto_dv/tests/gen_programs/gen_bit_ratified_prog.py")
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod); sys.path.pop(0); return mod
head = git("rev-parse", "HEAD").strip()
now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
print("# gen_fu_bit_ratified_rev58: the rev58 follow-up on gen_bit_ratified_prog.py and gen_test_bit_ratified.py leaves every emitted program byte-identical")
print(f"written {now} by the Test Writer; clone HEAD {head[:7]} ({head}); python {sys.version.split()[0]}")
G_HEAD = EXPORT / "dv/auto_dv/tests/gen_programs/gen_bit_ratified_prog.py"; G_CAND = CLONE / "dv/auto_dv/tests/gen_programs/gen_bit_ratified_prog.py"
print(f"committed generator (the export's copy) sha256 {sha(G_HEAD)}; candidate {sha(G_CAND)[:12]}")
expect(sha(G_HEAD) == PIN and git("show", "HEAD:dv/auto_dv/tests/gen_programs/gen_bit_ratified_prog.py").encode() == G_HEAD.read_bytes(),
       "the export's generator is HEAD's blob and the block's pin 70f31808")
H = load("bit_head", EXPORT); C = load("bit_cand", CLONE)
seeds_block = [int(x) for x in (CLONE / "dv/auto_dv/evidence/gen_bit_ratified_pairfix/gen_pairfix_seeds.txt").read_text().split()]
seeds = list(range(1, 41)) + seeds_block
print(f"\n## A. GREEN PROGRAMS at {len(seeds)} seeds (1..40 and the block's forty from gen_pairfix_seeds.txt): emitted text, reports, k, min_retired")
same_text = same_rep = 0; unreported = 0; ops_diff = 0
for s in seeds:
    ph, pc = H.plan(s), C.plan(s)
    same_text += (H.emit(ph) == C.emit(pc))
    same_rep += ((ph.reports, ph.k, ph.min_retired) == (pc.reports, pc.k, pc.min_retired))
    unreported += sum(len(v["unreported"]) for v in pc.items.values())
    # the only bookkeeping change: each item's ops = the committed ops minus its no-report members
    for it in pc.items:
        h_ops = set(ph.items[it]["ops"]); c_ops = set(pc.items[it]["ops"]); un = set(pc.items[it]["unreported"])
        if h_ops != c_ops | un or (c_ops & un): ops_diff += 1
expect(same_text == len(seeds), f"emitted program byte-identical at {same_text} of {len(seeds)} seeds")
expect(same_rep == len(seeds), f"report words, k and min_retired identical at {same_rep} of {len(seeds)} seeds")
expect(unreported == len(seeds), f"exactly one no-report op per program counted apart ({unreported} over {len(seeds)} seeds: the binv pair's first)")
expect(ops_diff == 0, "every item's ops list is the committed list minus its no-report member, nothing else moved")
print("\n## B. RED FORMS: every red item at three seeds, emitted text and reports identical")
same_red = total = 0
for item in C.BUILT_ITEMS:
    for s in (1, 2, 3):
        total += 1
        ph, pc = H.plan(s, red=True, red_item=item), C.plan(s, red=True, red_item=item)
        same_red += (H.emit(ph) == C.emit(pc) and ph.reports == pc.reports)
expect(same_red == total, f"red programs byte-identical at {same_red} of {total} (item, seed) pairs")
print("\n## C. THE TEST'S MATCH RULE: the no-report op never enters _ok, before and after, on the plan's own report stream")
import re
src_c = (CLONE / "dv/auto_dv/tests/gen_test_bit_ratified.py").read_text()
expect("if op.expects and op.rep + len(op.expects) <= len(got)" in src_c, "gen_test_bit_ratified.py: _ok requires a report word")
p = C.plan(seeds_block[0]); got = p.reports
old_ok = {op.idx for op in p.ops if op.rep + len(op.expects) <= len(got) and got[op.rep:op.rep + len(op.expects)] == op.expects}
new_ok = {op.idx for op in p.ops if op.expects and op.rep + len(op.expects) <= len(got) and got[op.rep:op.rep + len(op.expects)] == op.expects}
nr = [op.idx for op in p.ops if op.no_report]
expect(len(nr) == 1 and nr[0] in old_ok and nr[0] not in new_ok and old_ok - new_ok == set(nr),
       f"at seed {seeds_block[0]} the committed rule admits the no-report op {nr} on an empty slice; the new rule does not, and nothing else changes")
print("\n## D. THE COMMENT SPELLING: the emitted comment names the chained value in plain text in both versions")
line_h = [l for l in H.emit(H.plan(seeds_block[0])).splitlines() if "not reported" in l]
expect(len(line_h) == 1 and "chr(" not in C.emit(C.plan(seeds_block[0])) and "chr(118)" not in (CLONE / "dv/auto_dv/tests/gen_programs/gen_bit_ratified_prog.py").read_text(),
       "the chr()-spelled key is gone from the source; the emitted comment line is unchanged: " + (line_h[0].strip()[:90] if line_h else "?"))
print("\nRESULT: " + ("PASS, every expectation above holds" if not fails else f"FAIL: " + "; ".join(fails)))
sys.exit(1 if fails else 0)
```
