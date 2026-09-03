"""One home for the plan's measurement-hold discovery (gen_test_plan.md sections "## 1.<n> Items under the T-<xxx> measurement hold")
and for the crediting carve-out record ("## 1.<n> Items carved out of crediting (LOG-nnn)", rows | TP id | UNCREDITED or COUNTED-ONLY | until | reason |),
shared by dv/auto_dv/tools/gen_promotion_table.py and dv/auto_dv/tools/gen_round_credit.py so that a lifted hold (its section gone) drops out
of both tools without a code change, and no tool carries a literal section number.
"""
import re, collections
HOLD_HDR = re.compile(r'^## (1\.\d+) Items under the (T-\d+) measurement hold', re.M)
ROW = re.compile(r'^\| (TP-[A-Z]+-\d{3}) \| \S+ \| [^|]*\|', re.M)

def hold_sections(plan_text):
    """[(section number, hold tag)] for every hold section present in the plan text, in document order."""
    return [(m.group(1), m.group(2)) for m in HOLD_HDR.finditer(plan_text)]

def hold_items(plan_text):
    """(items, sections): items maps TP id -> [hold tags] from the tables of every hold section present; sections as hold_sections()."""
    items = collections.defaultdict(list); sections = hold_sections(plan_text)
    for sec, tag in sections:
        m = re.search(r'^## ' + re.escape(sec) + r' .*?\n(.*?)(?=^## |^# |\Z)', plan_text, re.M | re.S)
        for row in ROW.finditer(m.group(1)): items[row.group(1)].append(tag)
    return dict(items), sections

CARVE_HDR = re.compile(r'^## (1\.\d+) Items carved out of crediting \((LOG-\d+)\)', re.M)
CARVE_ROW = re.compile(r'^\| (TP-[A-Z]+-\d{3}) \| (UNCREDITED|COUNTED-ONLY) \| ([^|]*?) \| ([^|]*?) \|', re.M)

def carveout_sections(plan_text):
    """[(section number, LOG tag)] for every crediting carve-out section present in the plan text, in document order."""
    return [(m.group(1), m.group(2)) for m in CARVE_HDR.finditer(plan_text)]

def carveout_items(plan_text):
    """(items, sections): items maps TP id -> (tag, until, reason) from the tables of every carve-out section present; the crediting tool applies the
    tag (UNCREDITED never credits and COUNTED-ONLY counts without crediting until the named task lands); sections as carveout_sections()."""
    items = {}; sections = carveout_sections(plan_text)
    for sec, tag in sections:
        m = re.search(r'^## ' + re.escape(sec) + r' .*?\n(.*?)(?=^## |^# |\Z)', plan_text, re.M | re.S)
        for row in CARVE_ROW.finditer(m.group(1)): items[row.group(1)] = (row.group(2), row.group(3).strip(), row.group(4).strip())
    return items, sections
