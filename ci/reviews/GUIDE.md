# Review rubrics (Zone A set)

fence-integrity: PASS — 2026-09-02

Model-neutral prompt files consumed by the `cross-review` skill (and any LLM reviewer). Each
rubric reviews ONE dimension of a diff and answers with the JSON contract below. Severity in the
header is the rubric's ceiling, not every finding's level.

The Zone A rubric set is exactly these five files plus this GUIDE: `ai-slop-comments.md`,
`rtl-purity.md`, `magic-numbers.md`, `forces-and-hier-access.md`, `assertion-integrity.md`.
The cross-review wrapper asserts this exact set and fails loud on a missing or extra rubric —
never add or remove a rubric without a fence review.

Response contract (all rubrics): `{"status": "PASS"}` when nothing qualifies, else
`{"status": "FAIL", "summary": "...", "comments": [{"file", "line", "quote?", "comment", "confidence"}]}`.
Every finding cites a real diff line; confidence 90+ only when certain; when in doubt, PASS.
