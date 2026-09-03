# AI-Slop Comment Check

**Severity:** Error
**Context:** diff_only
**Filters:** rtl/**/*.sv, dv/**/*.sv, dv/**/*.svh, dv/**/*.py, ci/**, docs/**

You are reviewing **added comments/docstrings only** (lines the diff adds whose added content is
comment text). Never flag pure code/import lines; for trailing comments judge only the comment text.

**FLAG when clearly one of:**
- Restates the code (`i += 1  # increment i`).
- Filler/hedging boilerplate ("Note that", "Basically", "for completeness", "obviously").
- History narration — "previously X, now Y", "moved from", commit SHAs, changelog-in-comments (this
  repo's comment rule is intent-only; history lives in git).
- The same multi-line explanatory block pasted verbatim more than once in the diff.

**Do NOT flag (default PASS):** comments that explain WHY, a gotcha, a workaround with its return
condition, spec/ISA section anchors with a short gloss, dense information-rich headers.

Bias strongly toward PASS; quote the offending text verbatim in each finding.
Respond `{"status": "PASS"}` or the FAIL JSON per `GUIDE.md`.
