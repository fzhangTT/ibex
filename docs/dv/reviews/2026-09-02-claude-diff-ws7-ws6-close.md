# Cross-model post-execution review — WS7+WS6 close (export-path fence + mex)

**Reviewer:** claude CLI 2.1.258 (subagent); model: claude-opus-5; extended reasoning; SUBSTITUTE per CLAUDE.md fallback — codex unavailable (spend cap); sanity-scoped per owner directive + controller ruling
**Date:** 2026-09-02
**Target:** committed range `2bfea931..07ed7ded` (11 commits, 104 files, +8553/-30); package `.superpowers/sdd/2026-09-02-ws7-knowledge-fence/review-ws7-close.diff`; final-state acceptance authority `DV_prompt.txt` Section 12 as recorded in `docs/dv/evidence/ws7-gate/section12-final.txt` (10 PASS / 1 BLOCKED)
**Authorities:** `ci/reviews/GUIDE.md` + all 7 rubrics; `docs/dv/FENCE.md`; `ci/make-cleanroom.sh` DENY (declared single machine-readable authority); rulings ledger `.superpowers/sdd/2026-09-02-ws7-knowledge-fence/progress.md`

---

TARGET: 2bfea931..07ed7ded (WS7+WS6)

Scope: this is the policy's final gate and the SDD whole-branch review, run SANITY-SCOPED. Every
task in the range already had a deep per-task review with independent re-execution; none of that is
re-audited. This pass sweeps only for what task-scoped reviews structurally cannot see: cross-cutting
inconsistency in the FINAL tree state, rubric violations across the whole range, and range-level
evidence-chain gaps. Recorded controller rulings are treated as decisions, not findings.

## Findings

**[Major][.mex/AGENTS.md:55-71 + docs/dv/evidence/ws6-mex/05-deny-list-consistency.txt:10-19]** The
`.mex/` deny mirror is stale and its consistency evidence now asserts a falsehood. The ledger
recorded the follow-up explicitly at Task 3 close — "mirror framed as snapshot-of-a-rule; will need
one refresh after T1's fix (tooling self-deny) lands — folded into T4's gate step (re-check the
diff)" — and the refresh never happened: `.mex/AGENTS.md` was last touched at `6b1fe99f`, while
`DENY` grew at `f9ac6933` and again at `59a65144` (19 rows at mirror time, 28 at HEAD). Seven rows
are missing from a bullet that claims to mirror the array *verbatim*: `ci/vars.env`,
`ci/install-build-deps.sh`, `flake.nix`, `ci/lint-commits.sh`, `ci/check-landing.sh`,
`ci/cleanroom-selftest.sh`, `ci/cleanroom-inventory.txt`, `ci/cleanroom-overlay`. The first three are
precisely the cosim-referee-disclosing files `59a65144` was created to fence. The mirror's
default-deny escape hatch does not cover them: it is scoped to "a `dv/*` or `docs/dv/*` entry added
after this file was last updated", not to plain-deny additions. Because `.mex/` fence enforcement is
procedural (mex-agent 0.8.0 has no ignore-glob surface) and keyed off this list, a wiki author
consulting it today would not know those paths are fenced. Compounding: the committed evidence
`05-deny-list-consistency.txt` still reports "19 rows in `DENY=(...)`", "36 entries / 36 entries",
and three empty diffs with `RESULT: PASS` — an exact-match claim that no longer holds at HEAD, in the
one artifact a future reader would consult to confirm the mirror is current. No leak exists in the
committed `.mex/` prose (swept: no page paraphrases the newly denied files), so this is drift and
false attestation, not disclosure. — Regenerate the mirror from HEAD's arrays and re-run the `05`/`09`
evidence pair at HEAD; or, if the mirror is to stay a snapshot, delete the word "verbatim", widen the
default-deny sentence to cover plain-deny additions, and date-stamp the snapshot so its staleness is
self-evident.

**[Major][ci/make-cleanroom.sh:335-380 + docs/dv/evidence/ws7-gate/export-verify-final.txt:1-9]** The
riscv-dv precondition-6 pristine test only runs on a cold cache, and the shipped export was built
warm — so nothing executed it for the export Section 12 was run against. Both verifications (fetched
SHA `==` locked rev, and no file containing `Ibex Specific`) live inside `if [ ! -d "$cache" ]` at
:336-376; :380 then does `cp -a "$cache" ...` unconditionally. On every subsequent export on the same
machine the cached tree under `${TMPDIR:-/tmp}/ibex-cleanroom-riscvdv-cache/$rev` is trusted without
re-checking, and it is verified by nothing else: the whole-export identifier scan carves out
`--exclude-dir=google_riscv-dv` by controller ruling, on the stated basis that "precondition 6 (rev
match + no 'Ibex Specific') remains its gate". This finding does not re-litigate that ruling — it
reports that the gate the ruling relies on does not fire. Confirmed empirically: the cache exists at
`/tmp/ibex-cleanroom-riscvdv-cache/71666eba...`, and neither `export-verify-final.txt` (source
`ebf47c1a`, export `32084c74` — the shipped one) nor `export-verify-raw.txt` contains the
`Fetching pristine upstream riscv-dv` / `Fetched riscv-dv commit: <sha> (locked rev: <sha>)` lines the
cold path emits. Consequence for the evidence chain: `docs/dv/FENCE.md:64-72`'s
`riscv-dv-verified-on` attestation — "The exported tree is that revision, so a tree diff against
upstream at that revision is empty" — has no executed proof for the shipped export, and the export
carries no `.git` for `vendor/google_riscv-dv/`, so it cannot be verified post hoc either. Section 12
item 6's independently-run sub-checks do cover the *content* claim (0 files contain `Ibex Specific`,
lock rev recorded); only the rev-identity claim is unproven. Secondary, same function: `--exclude-dir`
matches the basename `google_riscv-dv` at any depth, not just under `vendor/`, so a Zone A directory
of that name would be silently exempt from the whole-export scan. — Hoist both checks out of the
cold-cache branch so they run against the cache (or the stage) on every export; stamp the verified
SHA into the export so the attestation is checkable after the fact; re-capture
`export-verify-final.txt` from a run that shows the attestation line. Consider anchoring the carve-out
to the `vendor/google_riscv-dv` path rather than the bare directory name.

**[Minor][docs/dv/FENCE.md:53]** "Inside an export, `ci/` is default-deny" is not what the builder
implements, and contradicts FENCE.md's own §"What is fenced" at :23-32, which names exactly two
default-deny roots — `dv/**` and `docs/dv/**`. In `ci/make-cleanroom.sh`, `ALLOW=("dv/auto_dv")` and
`DOCS_DV_ALLOWED` back the `rm -rf "$stage/dv" "$stage/docs/dv"` at :396; `ci/` has no allowlist
mechanism at all — it is allow-by-default minus 12 enumerated `DENY` rows, and no verify function
checks it (`cleanroom_check_reviews_set` covers `ci/reviews/` only; Section 12 item 11's positive-list
`ls` covers `dv/`, `docs/`, `docs/dv/`, not `ci/`). The three-way agreement holds today and I
confirmed it end to end: all 20 tracked top-level `ci/` entries are accounted for as 8 allowlisted + 12
denied, and the live export at `../ibex-cleanroom/ci/` contains exactly the 8 FENCE.md lists. But the
agreement is coincidence maintained by hand, not enforcement: a `ci/` file added later ships silently,
since the inventory tripwire is depth-1 only and `ci` is already an inventory entry. FENCE.md declares
itself the tie-breaker ("Where another document and this file disagree, this file wins"), which makes
an internal self-contradiction in the rulebook worth closing on its own terms. — Either add a
`CI_ALLOWED` check mirroring the `DOCS_DV_ALLOWED` pattern (the data is already written down at
:55-62), or reword :53 to "deny-by-enumeration" and add `ci/` allowlist enforcement as a seventh entry
under §Deferred machinery, where the depth-granularity gap is already acknowledged.

**[Nit][ci/make-cleanroom.sh:97]** `"ibex-cosim" "ibex_cosim"  # the cosim referee's package/agent
identifiers (owner final-check fix set)` — the parenthetical is provenance narration, the class the
repo's own `ci/reviews/ai-slop-comments.md` names ("history narration ... changelog-in-comments") and
that the global comment rule bars. The rest of the clause is good intent-level content. — Drop
"(owner final-check fix set)".

## Sweep summary

**Rubrics.** `rtl-purity`: passes trivially — the range touches no `rtl/` path. `test-overlap`: passes
trivially — no testlist entry, directed test, or `dv/auto_dv/**` test is added. `forces-and-hier-access`
and `assertion-integrity`: pass on substance rather than by filter. Their filters (`dv/**/*.sv`) miss
the range's only SystemVerilog, which sits at `docs/dv/evidence/ws7-gate/gen_{dut_top,smoke_tb}.sv`, so
I read those directly: no `force`/`release`, no hierarchical poke, and the assertions move the right
way — `a_gen_magic_store_value` plus the alert and timeout checks are added, with a real on-disk
red→green transcript, and nothing in the range disables or weakens an existing check.
`magic-numbers`: passes on substance. `ci/**/*.sh` is in filter and the builder is full of literal
lists, but each sits at its declared authority — `DENY` is the single machine-readable deny authority
by FENCE.md:23, and the riscv-dv rev/url are parsed out of `vendor/google_riscv-dv.lock.hjson` at
:328-329 rather than re-typed. `ITEM9_STRINGS`/`ITEM9_FILES` duplicate `DV_prompt.txt` Section 12,
which is untracked and owner-delivered, so duplication is unavoidable and is comment-anchored.
`ai-slop-comments`: passes but for the Nit above; I probed every added comment line under `ci/` for
history narration and the rest are authority citations or gotchas-with-conditions.
`fence-integrity`: the range creates the fence rather than being governed by it, so I applied its
spirit to the final full-tree state — does any committed WS7 file leak what FENCE.md denies? No. Every
range file carrying a fenced identifier (`CLAUDE.md`, `ci/mcp/README.md`, `docs/dv/FENCE.md`,
`ci/make-cleanroom.sh`, `ci/cleanroom-selftest.sh`, `.mex/**`) is either plain-denied from the export
or superseded at its destination path by an overlay Zone A variant, and the item-9 plus whole-export
scans cover the result. The Zone A `FENCE.md` (97 lines) is a genuine variant of the Zone B one (163
lines), not a copy.

**`git diff --check`:** 8 hits, all trailing whitespace or blank-EOF inside
`docs/dv/evidence/ws7-gate/{section12-final.txt,sim-green.log,spike-build.txt}`. These are verbatim
tool transcripts (VCS banner, `g++` link lines, a generated `ls` line); normalizing them would damage
the evidence. Not a finding.

**Spot-checks (6).** (1) `ci/` three-way agreement — Minor above; agreement holds, enforcement does
not. (2) Invariant 2 wording — the new text lands the amendment's substance (generation permitted only
inside a verified export; full tree contaminated by design; FENCE.md named as the rule file), the
`CLAUDE.md` and `AGENTS.md` copies are consistent, and `.codex/compat/validator.py` reports PASS on
the mirrored-and-hash-checked block. The stale WS5-era "cleanroom ships no MCP" claims in `ci/env.sh`,
`ci/mcp/*.sh` and `ci/mcp/README.md` were all swept and corrected in the same range. (3) Evidence
bundle coherence — I re-derived `section12-final.txt`'s summarily-recorded sub-checks against the live
export and all hold: `FENCE-ZONE: A` present in the first ten lines of both Zone A `CLAUDE.md` and
`AGENTS.md`; `run_codex_review.sh` contains all five rubric basenames literally, zero occurrences of
`ci/reviews/*.md`, and `dv/auto_dv/reviews/`; four dated `fence-integrity: PASS` lines present. Item 2
is satisfied — DV_prompt's transcribed text says "names *at least*" the six, so FENCE.md's eight-entry
list is a superset, not a discrepancy. Export SHA `32084c74` and source `ebf47c1a` match the on-disk
export's commit exactly. (4) Export staleness vs the tip — `ebf47c1a..07ed7ded` touches only
`docs/dv/evidence/**`, `docs/dv/process-logs/**` and `docs/superpowers/**`, all of which the export
deletes, so the committed "final export" is byte-equivalent to one rebuilt at `07ed7ded`; the evidence
is not stale w.r.t. the tip. (5) Inventory tripwire vs the range's own additions — the range adds three
top-level namespaces (`ci`, `docs`, `.mex`); the inventory is exactly in sync with HEAD's regenerate
command, `.mex` is correctly excluded as a DENY top-level, and every file the range added under `ci/`
is a `DENY` row, so nothing added in this range ships unnoticed. The tripwire's depth-1 granularity is
the residual gap and is already recorded as deferred item 6. (6) FENCE.md class summary vs `DENY` —
all 28 rows are covered by the prose classes at :34-49 with no orphan on either side.

**Not findings, recorded so they are not re-swept.** `dv/auto_dv/mutations/README.md` predates the
range and is not exempt under `ci/check-landing.sh`'s `gen_*` rule, but it is present at the export
root rather than added in a landing range, so the gate does not see it. The one remaining Section 12
BLOCKED item is the owner's `DV_prompt.txt` signature, which is owner action and outside this review.

VERDICT: APPROVE-WITH-CHANGES
