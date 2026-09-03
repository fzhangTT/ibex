"""One definition of the cycle-clause marker token and the export-row wildcard rule (gen_test_plan.md Section 0), imported by
dv/auto_dv/tools/gen_trace_check.py and dv/auto_dv/tools/gen_token_sunset.py (the Test Writer's gen_fcov_manifest.py may import it
the same way). gen_trace_check.py parses argv at import time, so the shared definitions live here rather than in it (CM20-L-4).
"""
import re
TOKEN = '[CYCLE-CLAUSE coverage-only until the event export lands]'
WILDCARD_TOKENS = {'pin irq_fast'}  # stands for any irq_fast<n> row
def present(tok, rows):
    """True when the export row token is in rows; the wildcard 'pin irq_fast' matches any 'pin irq_fast<n>' row."""
    if tok == 'pin irq_fast': return any(re.fullmatch(r'pin irq_fast\d*', r) for r in rows)
    return tok in rows
