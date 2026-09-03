# WS7 knowledge-fence ledger

Plan: `docs/superpowers/plans/2026-09-02-ws7-knowledge-fence.md`. Authorities: spec
`2026-09-01-auto-dv-setup-design.md` §WS5/§WS6/§WS7 as amended by
`docs/superpowers/specs/2026-09-02-zone-a-fence-scope-amendment.md` (v2.1, BINDING), further
folded per the plan pre-review `docs/dv/reviews/2026-09-02-claude-plan-ws7-export-path.md`
(APPROVE-WITH-CHANGES).

## Task checkboxes

- [x] **T1** — `ci/make-cleanroom.sh` + `ci/check-landing.sh` + `ci/cleanroom-selftest.sh` +
      `ci/cleanroom-inventory.txt` + this ledger. Selftest green in `--pre-overlay` mode
      (proves a, b, c, f-partial (deny/artifact canaries; mcp/identifier canaries SKIP — their
      checks are themselves skipped pre-overlay), g; d1/d2/e/h SKIP by design until Task 2/4).
- [x] **T2** — Zone A overlay (`ci/cleanroom-overlay/`) — landed (commit `583b4be9`, 36 files),
      concurrent with T1/T3.
- [x] **T3** — mex (WS6), full tree — landed (commit `b23f4725`), concurrent with T1/T2.
- [ ] **T4** — GATE: export, verify, compile+run, cleanroom mex (serial, after 1–3).
- [ ] **T5** — `docs/dv/FENCE.md` + supersessions + close-out docs.

## Carried rulings (from the plan / pre-flight conflict scan)

- Owner directive: re-cut to export path and start; Wave-1 execution concurrent with the plan
  pre-review, findings fold as fix rounds.
- Pre-review is single-round targeted; APPROVE-WITH-CHANGES folds and goes (this ledger records
  the T1-relevant folds below).
- Rulings carried from the v1 draft: precondition-6 verify-not-edit; identifier scans outside the
  export; codex network on; ChipSmart-import variants; `DV_prompt.txt` owner-delivered/untracked;
  `gen_` prefix only.
- T1↔T2: `make-cleanroom.sh` requires `ci/cleanroom-overlay/` to exist; T1's selftest
  `--pre-overlay` mode covers the window before it lands. T3 mirrors T1's deny globs into mex's
  ignore config (documented single-authority risk: two copies, accepted).

## T1-specific folds from the pre-review (`2026-09-02-claude-plan-ws7-export-path.md`)

The pre-review found the original enumerated `DENY` array was allow-by-default and measurably
incomplete against the tree as it stood. T1's implementation changed shape (not just entries) to
fold these in:

1. **Default-deny inversion (Critical).** `dv` and `docs/dv` are now wholesale-deleted from the
   stage, with an `ALLOW=("dv/auto_dv")` stage-aside/delete/restore for `dv`, and `docs/dv`'s four
   Zone A files (`FENCE.md`, `SIM_RECIPE.md`, `TB_CONTRACT.md`, `dv_principles.md`) supplied purely
   by the Task 2 overlay (no restore needed — full replacement is the correct behavior for these).
   This closes the 37-file gap the review found (`dv/cocotb/**` WS2 cocotb TB,
   `dv/cs_registers/**` CSR testbench + C++ reference model) without denying `dv/**` mechanics
   that were never meant to leave (moot now — everything under `dv/` except `dv/auto_dv/` is gone
   regardless of directory name).
2. **Vendor globs (Critical).** `vendor/riscv?isa?sim*` (DV_prompt §12 precondition 6's own
   pattern) replaces a plain directory-name deny, so the underscore-named
   `vendor/riscv_isa_sim.{lock,vendor}.hjson` siblings (which disclose the fork's URL/branch/patch
   mapping) are caught too.
3. **riscv-dv pristine-fetch ruling (Critical, owner ruling: option (a)).** The checked-in
   `vendor/google_riscv-dv/` is *not* pristine (`Ibex Specific` patches in 2 files per the
   review), so `make-cleanroom.sh` does not ship it as-is or merely delete it. It fetches
   upstream `chipsalliance/riscv-dv` at the rev pinned in `vendor/google_riscv-dv.lock.hjson`
   (shallow `git fetch --depth 1` + checkout, cached by rev under
   `${TMPDIR}/ibex-cleanroom-riscvdv-cache/<rev>` to avoid re-fetching on every selftest build),
   verifies the checkout's working tree has an empty `git diff` against its own recorded commit
   (an integrity check on the fetch/checkout itself, not a diff against the patched checked-in
   tree — replacement, not reconciliation, is the strategy), places that tree at
   `vendor/google_riscv-dv/` in the stage, retains `vendor/google_riscv-dv.lock.hjson` untouched
   (never denied — it is the precondition-6 anchor), and deletes
   `vendor/google_riscv-dv.vendor.hjson` (discloses `patch_dir`). **Open item for T5/FENCE.md:**
   the `riscv-dv-verified-on:` dated attestation line that precondition 6 wants in `FENCE.md` is
   not written by this script (FENCE.md is Task 5's file) — the ruling and mechanism are recorded
   here for T5 to close against.
   **Residual finding for the owner (not fixed by T1, found via a full-mode selftest run after
   Task 2 landed, not part of T1's required pre-overlay proof):** pristine upstream riscv-dv's own
   docs (`docs/source/handshake.rst`, `end_to_end_simulation.rst`) hyperlink directly to
   `github.com/lowRISC/ibex/blob/master/dv/uvm/core_ibex/tests/core_ibex_{base_test,test_lib}.sv`
   as a worked example — a real disclosure of the existing TB's test filenames, inherent to
   shipping riscv-dv pristine (patching it would break the verified-empty-diff property). Separately,
   `riscv_arithmetic_basic_test` also appears in riscv-dv's own stock `yaml/base_testlist.yaml` —
   this one is benign (the amendment's own "adopted, reference-only" testlist ruling covers a
   generic upstream example name coinciding with Ibex's adopted test of the same name). The first
   is a structural tension between "ship riscv-dv pristine" and "no fenced identifiers in the
   export" with no clean fix inside `make-cleanroom.sh`; it needs an owner ruling (accept as a
   documented residual risk in FENCE.md, or a targeted, diff-recorded doc redaction that
   consciously breaks strict pristine-ness).
4. **`.github` deny (Major).** Workflows/actions re-disclosed the cosim build+run and directed
   test names after the three `ci/*cosim*.sh` scripts were denied; added to `DENY` wholesale.
5. **Identifier check realignment (Major).** Split into `cleanroom_check_item9_scan` (DV_prompt
   §12 item 9's exact 10-string set, scoped to item 9's exact file list) and
   `cleanroom_check_whole_export_identifiers` (4 unconditionally-forbidden strings: `core_ibex`,
   `riscv_arithmetic_basic_test`, `mcounteren_test`, `spike_cosim` — deliberately excludes
   `disable_cosim`, which `docs/dv/dv_principles.md` legitimately carries near its Zone A
   scoping sentence). Both are skipped in `--pre-overlay` mode; the brief's original claim that
   `--pre-overlay` "still proves a–d" was corrected to a–c, f, g per the review.
6. **Canary enum (Major, anti-vacuity).** `CLEANROOM_CANARY=deny|artifact|mcp|identifier` plants
   one named violation each; the selftest asserts a named failure for each meaningful in the
   current mode (mcp/identifier canaries are pre-overlay SKIPs, symmetric with their checks being
   skipped).
7. **Inventory tripwire (Major).** `ci/cleanroom-inventory.txt` (committed) lists every top-level
   path expected in the export (46 entries: the repo's current top-level tree minus the two
   wholesale-denied roots, `formal` and `.github`; regenerate with the command in the file's own
   header comment). `cleanroom_check_inventory` fails loud on any
   top-level export path absent from that file — converts allow-by-default to triage-on-add for
   new top-level additions (spec:139's unclassifiable-path property, at top-level granularity
   only: a new *file* added inside an already-allowed top-level directory is not caught by this
   check alone — defense in depth comes from the deny/item9/whole-export scans layered on top).
   `.git` (present only once DEST is git-init'd, not part of the archived content) is explicitly
   excluded from the comparison.
8. **DEST guard (Major).** Refuses a non-empty DEST unless `--force`.
9. **`set -euo pipefail` (Minor).** Was `-uo pipefail`; the archive/tar and overlay-copy stages
   now use explicit `|| die`. (Required auditing every check function for the `set -e` +
   command-substitution gotcha — `x="$(cmd)"` aborts the script if `cmd` exits nonzero on the
   *expected* "nothing found" case; every such assignment in the check functions now ends
   `2>/dev/null || true`.)
10. **Check (h): exported validator (Major/New).** Runs the export's own
    `.codex/compat/validator.py --repo-root <export>` (Task 2 ships a Zone A variant); skipped
    pre-overlay via `[ -f ... ]` (absent) — also always skipped by the `CLEANROOM_PRE_OVERLAY=1`
    gate alongside d1/d2/e.

**Late interface fix (post-T2-landing, folded before commit):** `ci/cleanroom-overlay/` is
applied **file-wise** (`cp -a` per file, preserving un-overlaid siblings — e.g. the
`simple-english` skill variant inherits its `references/` subdir from the full tree), **except**
`ci/reviews/`, which is a **directory replace** (delete staged `ci/reviews/` entirely, then copy
the overlay's) so the six-file Zone A rubric set can never gain a stray full-tree rubric nobody
thought to add to `DENY`. Added `cleanroom_check_reviews_set` (positive list: `GUIDE.md` + the
five rubrics) to the selftest, unconditional (true pre- and post-overlay, since plain-denying the
two Zone B rubrics already yields exactly six). Confirmed `ci/check_fcov_expectations.py` is not
and must not be denied (it is on FENCE.md's `ci/` allowlist, precondition 2); its Zone A variant
arrives via the file-wise overlay copy once Task 2 supplies it.

## Deferred (named per the pre-review, not fixed in T1)

- **spec:139's unclassifiable-path rejection**, beyond the top-level inventory tripwire (item 7
  above) — a full positive-list check at every directory depth is out of T1's scope; the
  tripwire plus the layered deny/item9/whole-export scans are the current defense-in-depth.
- **spec §WS7 enforcement-stack layer 2** — Zone A agent runtime profile (permission rules
  denying `git fetch`/remote mutation, codex network-restricted). `.claude/settings.json` ships
  unmodified; not a T1 file.
- **Escape-test harness beyond the script's self-verify** — "fetch master" (unrepresentable by
  construction per the pre-review's mechanism assessment), "read sibling clone" (retained escape
  test for the tool data-reach ruling), "fetch upstream ibex DV", and the negative control
  (fsdb-mcp opens a Zone A-produced FSDB) are not implemented here; they are a later, T4/T5-scoped
  harness, not `cleanroom-selftest.sh`'s job (which verifies clone *contents*, not clone *boundary
  behavior*).
- **DV_prompt §12 precondition 11's full positive-list checks** (`dv/` contains only
  `dv/auto_dv/`, `docs/` contains only `docs/dv/` etc.) are covered *incidentally* by
  `cleanroom_check_deny_absence`'s dv/docs-dv leftover checks, but the full item-11 checklist
  (ci/, vendor/, formal/, the six RSTs) is the Orchestrator's mechanical launch check per the
  amendment, not re-implemented as its own selftest layer here.

## Evidence

- Red→green TDD transcripts: `docs/dv/evidence/ws7-selftest-tdd/t1-red.txt` (real capture: the
  three scripts moved aside, `ci/cleanroom-selftest.sh` invocation fails with "No such file or
  directory", exit 127) and `t1-green.txt` (`ci/cleanroom-selftest.sh --pre-overlay`, 0 failures).
- A full (non-`--pre-overlay`) run was also exercised as due diligence once Task 2's overlay
  landed mid-session (not required for T1's pre-overlay contract): it correctly fails on the
  riscv-dv pristine-doc disclosure noted above, and all four canary modes plus the landing-check
  sub-cases behave as designed. Not saved as a t1-*.txt pair (it is not the required pre-overlay
  proof and the overlay is still moving), but reproducible with
  `ci/cleanroom-selftest.sh` (no flag).
