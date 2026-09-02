#!/usr/bin/env python3
"""Cross-model compatibility validator for the ibex auto-DV fork.

Contract (see CLAUDE.md / docs/superpowers plans, WS3):
  - every .claude/skills/<dir>/SKILL.md has well-formed frontmatter whose `name` == <dir>
  - .agents/skills/shared is a symlink whose literal target is ../../.claude/skills and resolves
  - the CRITICAL-INVARIANTS block is byte-identical between CLAUDE.md and AGENTS.md
  - no non-invariant duplicated run of >120 chars between CLAUDE.md and AGENTS.md
  - CLAUDE.md carries the required sections and cross-model policy clauses
  - the TRUST-TRIAD-CANONICAL block is byte-identical across every file that embeds it
  - .codex/config.toml carries the required keys
  - --probe additionally launches bounded live codex runs from the repo root and one
    subdirectory and asserts the effective instructions loaded (slow; CI-optional)

Exit 0 on success, 1 on any violation (all violations reported, not just the first).

Runs on the bare site python (3.9) as well as the repo venv.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

INV_BEGIN = "<!-- CRITICAL-INVARIANTS-BEGIN -->"
INV_END = "<!-- CRITICAL-INVARIANTS-END -->"
TRIAD_BEGIN = "<!-- TRUST-TRIAD-CANONICAL-BEGIN -->"
TRIAD_END = "<!-- TRUST-TRIAD-CANONICAL-END -->"

# Files that must embed the canonical triad block once they exist (Tasks land in order).
TRIAD_FILES = [
    "docs/dv/dv_principles.md",
    ".claude/skills/mutation-check/SKILL.md",
    ".claude/skills/fcov-expectation/SKILL.md",
    ".claude/agents/ibex-test-generator.md",
]

REQUIRED_CLAUDE_SECTIONS = [
    "## Environment & flow",
    "## DV principles",
    "## Cross-model review policy",
    "## Critical invariants",
    "## Site gotchas",
    "## Skills index",
]

# Grep-detectable phrases for each binding policy clause.
REQUIRED_POLICY_CLAUSES = [
    "never self-approves",
    "docs/dv/reviews/",
    "reviewer-identity header",
    "explicit review target",
    "REQUEST-CHANGES",
    "recorded re-review",
    "human owner",
]

REQUIRED_CODEX_KEYS = ["project_doc_fallback_filenames", "project_doc_max_bytes"]

errors: list[str] = []


def err(msg: str) -> None:
    errors.append(msg)


def extract_block(text: str, begin: str, end: str, who: str) -> str | None:
    if begin not in text or end not in text:
        err(f"{who}: missing {begin}/{end} block")
        return None
    return text.split(begin, 1)[1].split(end, 1)[0]


def check_skills(root: Path) -> None:
    skills = root / ".claude" / "skills"
    if not skills.is_dir():
        err(".claude/skills/ missing")
        return
    for d in sorted(p for p in skills.iterdir() if p.is_dir()):
        sk = d / "SKILL.md"
        if not sk.is_file():
            err(f"{d}: no SKILL.md")
            continue
        text = sk.read_text(encoding="utf-8")
        m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
        if not m:
            err(f"{sk}: missing/malformed frontmatter")
            continue
        try:
            import yaml  # from the venv lock; regex fallback below is a warned degradation
        except ImportError:
            print(f"WARNING: pyyaml unavailable — {sk} frontmatter checked by regex only")
            if not re.search(r"^name:\s*\S+", m.group(1), re.M):
                err(f"{sk}: frontmatter has no name:")
            continue
        try:
            fm = yaml.safe_load(m.group(1))
        except yaml.YAMLError as e:
            err(f"{sk}: frontmatter is not valid YAML: {e}")
            continue
        if not isinstance(fm, dict):
            err(f"{sk}: frontmatter did not parse to a mapping")
            continue
        if fm.get("name") != d.name:
            err(f"{sk}: frontmatter name '{fm.get('name')}' != dir '{d.name}'")
        if not str(fm.get("description") or "").strip():
            err(f"{sk}: frontmatter has no non-empty description")


def check_symlink(root: Path) -> None:
    link = root / ".agents" / "skills" / "shared"
    if not link.is_symlink():
        err(".agents/skills/shared is not a symlink")
        return
    import os

    target = os.readlink(link)
    if target != "../../.claude/skills":
        err(f".agents/skills/shared target is '{target}', want '../../.claude/skills'")
    if not link.resolve().is_dir():
        err(".agents/skills/shared does not resolve (dangling)")


def check_invariants(root: Path) -> None:
    cl = (root / "CLAUDE.md").read_text(encoding="utf-8")
    ag = (root / "AGENTS.md").read_text(encoding="utf-8")
    a = extract_block(cl, INV_BEGIN, INV_END, "CLAUDE.md")
    b = extract_block(ag, INV_BEGIN, INV_END, "AGENTS.md")
    if a is not None and b is not None and a != b:
        err("CRITICAL-INVARIANTS blocks differ between CLAUDE.md and AGENTS.md")
    # Non-invariant duplication: any common substring run > 120 chars outside the blocks.
    cl_rest = cl.replace(a or "", "")
    ag_rest = ag.replace(b or "", "")
    for i in range(0, max(0, len(ag_rest) - 120)):
        chunk = ag_rest[i : i + 121]
        if len(chunk) == 121 and chunk in cl_rest:
            err(f"AGENTS.md duplicates >120 chars of CLAUDE.md outside invariants: '{chunk[:60]}…'")
            break
    for section in REQUIRED_CLAUDE_SECTIONS:
        if section not in cl:
            err(f"CLAUDE.md: required section missing: '{section}'")
    for clause in REQUIRED_POLICY_CLAUSES:
        if clause not in cl:
            err(f"CLAUDE.md: required policy clause not found: '{clause}'")


def check_triad(root: Path) -> None:
    blocks = {}
    for rel in TRIAD_FILES:
        p = root / rel
        if not p.exists():
            continue  # tasks land in order; absent files are not yet in scope
        blk = extract_block(p.read_text(encoding="utf-8"), TRIAD_BEGIN, TRIAD_END, rel)
        if blk is not None:
            blocks[rel] = blk
    if "docs/dv/dv_principles.md" not in blocks:
        err("docs/dv/dv_principles.md must carry the canonical TRUST-TRIAD block")
        return
    canon = blocks["docs/dv/dv_principles.md"]
    for rel, blk in blocks.items():
        if blk != canon:
            err(f"{rel}: TRUST-TRIAD block differs from canonical (dv_principles.md)")


def check_codex_config(root: Path) -> None:
    cfg = root / ".codex" / "config.toml"
    if not cfg.is_file():
        err(".codex/config.toml missing")
        return
    text = cfg.read_text(encoding="utf-8")
    for key in REQUIRED_CODEX_KEYS:
        if key not in text:
            err(f".codex/config.toml: missing key {key}")


def probe(root: Path) -> None:
    """Live codex launches asserting effective instruction loading (bounded)."""
    for cwd, marker in [(root, "root"), (root / "docs" / "dv", "subdir")]:
        try:
            r = subprocess.run(
                ["codex", "exec", "--sandbox", "read-only", "--skip-git-repo-check",
                 "In one line: which repository instruction file governs you here, and name "
                 "one Critical Invariant from it."],
                cwd=cwd, capture_output=True, text=True, timeout=300,
            )
            out = (r.stdout + r.stderr).lower()
            if "claude.md" not in out and "self-approve" not in out and "fence" not in out:
                err(f"probe[{marker}]: effective instructions not evidenced in codex output")
        except FileNotFoundError:
            err("probe: codex CLI not found on PATH")
            return
        except subprocess.TimeoutExpired:
            err(f"probe[{marker}]: codex probe timed out")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", default=".")
    ap.add_argument("--probe", action="store_true", help="run live codex probes (slow)")
    args = ap.parse_args()
    root = Path(args.repo_root).resolve()

    check_skills(root)
    check_symlink(root)
    check_invariants(root)
    check_triad(root)
    check_codex_config(root)
    if args.probe:
        probe(root)

    if errors:
        print("VALIDATOR: FAIL")
        for e in errors:
            print(f"  - {e}")
        return 1
    print("VALIDATOR: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
