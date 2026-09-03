"""One home for the plan's measurement-hold discovery (gen_test_plan.md sections "## 1.<n> Items under the T-<xxx> measurement hold"),
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
