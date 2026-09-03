# Codex compatibility layer

`validator.py` enforces the cross-model contract (see CLAUDE.md "Critical invariants" and the
WS3 plan). Fast path: `python3 .codex/compat/validator.py --repo-root .`
Live probes (slow, launches codex): add `--probe`.
