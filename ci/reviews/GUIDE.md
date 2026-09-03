# Review rubrics

Model-neutral prompt files consumed by the `cross-review` skill (and any LLM reviewer). Each
rubric reviews ONE dimension of a diff and answers with the JSON contract below. Severity in the
header is the rubric's ceiling, not every finding's level.

Response contract (all rubrics): `{"status": "PASS"}` when nothing qualifies, else
`{"status": "FAIL", "summary": "...", "comments": [{"file", "line", "quote?", "comment", "confidence"}]}`.
Every finding cites a real diff line; confidence 90+ only when certain; when in doubt, PASS.
