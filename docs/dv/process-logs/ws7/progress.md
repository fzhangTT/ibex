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
      **Post-review fix round 1 (see below): full mode (no `--pre-overlay`) is now green
      end-to-end** — all of a–h and all four named canaries pass against T2's landed overlay.
- [x] **T2** — Zone A overlay (`ci/cleanroom-overlay/`) — landed (commit `583b4be9`, 36 files),
      concurrent with T1/T3.
- [x] **T3** — mex (WS6), full tree — landed (commit `b23f4725`), concurrent with T1/T2.
- [x] **T4** — GATE: export, verify, compile+run, cleanroom mex (serial, after 1–3). Results
      in the "T4 gate results" section below; evidence: `docs/dv/evidence/ws7-gate/`.
- [ ] **T5** — `docs/dv/FENCE.md` + supersessions + close-out docs.

## T4 gate results (2026-09-02)

- **Step 1 (export + verify):** fresh export of `f9ac6933` to `/localdev/fzhang/ws/ibex-cleanroom`
  (no stale dir existed — verified absent before the run), export SHA `cc114e05`, verify PASS
  (all checks; raw output `ws7-gate/export-verify-raw.txt`). Canary/selftest separately re-proven:
  full-mode `ci/cleanroom-selftest.sh` rerun green — a–h, all four canaries each caught by its own
  named check, all landing-check sub-cases (`ws7-gate/selftest-fullmode-rerun.txt`).
- **Step 2 (the irreducible gate): PASS on compile invocation 1.** Following only the export's
  `docs/dv/SIM_RECIPE.md` + `TB_CONTRACT.md` + RTL/.core files, wrote `dv/auto_dv/gen_dut_top.sv`
  (ibex_core + ibex_register_file_ff mirroring ibex_top wiring; ICache RAM stub + scramble-key
  answer + MemECC encoders as bench equipment; `cheriot_enable_i = IbexMuBiOff`) and
  `gen_smoke_tb.sv` (3-instruction ROM, magic-store SVA check) + two hand-derived filelists,
  opentitan config via `util/ibex_config.py opentitan vcs_opts`. Clean elaboration and
  TEST PASSED sim (exit 0, seed 1) on the FIRST VCS invocation — zero recipe insufficiencies hit;
  no fence files consulted. Red→green: stimulus immediate toggled 0x5A5→0x2A5, assertion
  `a_gen_magic_store_value` fired (captured), restored, green re-proven
  (`ws7-gate/redgreen-transcript.txt`). One TB defect found and fixed during the red run: the SVA
  action block printed post-edge values instead of `$sampled()` — check itself was always correct.
  5 VCS compiles total (green, red, debug probe, red re-capture, final green), 13–16s each.
  `executed-on: 2026-09-02` stamped in `ci/cleanroom-overlay/docs/dv/SIM_RECIPE.md` (+ the
  export's copy, kept in sync).
- **Step 2b (upstream spike): PASS.** `riscv/riscv-isa-sim` cloned from github at
  `4ffd6ba860f4190ceac2716fa3c2cf139e85538f`, built + installed under the export's `tools/spike`
  (wall 125s). One site gotcha: default configure picks up system boost 1.66, which does not
  compile under gcc-11 C++17 — rebuilt `--with-boost=no --with-boost-asio=no --with-boost-regex=no`;
  recorded as new SIM_RECIPE §11 (recipe improvement, not a gate failure).
  `spike-built-on: 2026-09-02` stamped next to `executed-on:`.
- **Step 2c (Section-12 items 2–9):** transcribed + run (`ws7-gate/section12-checklist.txt`).
  Items 3, 4, 5, 7, 9 PASS. Item 6 PASS except its lock-rev-attestation sub-check (BLOCKED on
  `docs/dv/FENCE.md` — T5's deliverable). Item 2 BLOCKED (same named blocker: FENCE.md is T5).
  Item 8 BLOCKED (DV_prompt.txt owner sign-off line is still the unsigned template — owner
  action). No unnamed blockers.
- **Step 3 (cleanroom mex): PASS.** `mex setup` ran inside the export (its own instance, Node-24
  fts5 workaround as on the full tree); graph + wiki built from visible files only, population
  agent in the export root, ~19 min. `mex check`: **100/100 — 0 errors, 0 warnings, 0 info**
  (19 files). No fence config exists or was needed — verified structurally
  (`ws7-gate/cleanroom-mex-check.txt`); the export CLAUDE.md's Zone A marker and item-9 scan
  re-verified clean after mex's anchor append.
- **Step 4 (WS5 closure):** gate item 3 closed against the amendment's replacement criterion,
  citing check (e) + `ws7-gate/check-e-no-remote-mcp.txt`; WS5 ledger flipped PARTIAL → DONE.

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
   **Superseded by fix round 1 (see below):** the original finding here (pristine riscv-dv's own
   docs disclosing existing-TB filenames, breaking the whole-export identifier scan permanently)
   is resolved by carving `vendor/google_riscv-dv/**` out of that one scan — see fix round 1 item 1.
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

## Fix round 1 (post-commit review: 2 Critical, 2 Important, 2 Minor)

1. **[Critical] (d2) whole-export identifier scan now excludes `vendor/google_riscv-dv/**`**
   (`grep --exclude-dir=google_riscv-dv`). Rationale comment in the code: upstream, fair-game
   content, gated by its own precondition-6 checks in `_cleanroom_place_riscvdv` (item 4 below),
   not by this scan. This is what makes full mode pass end-to-end for the first time — the scan
   was previously detecting riscv-dv's own docs/tests linking `core_ibex`/naming
   `riscv_arithmetic_basic_test` as worked examples, permanently.
2. **[Critical] `ci/make-cleanroom.sh`, `ci/check-landing.sh`, `ci/cleanroom-selftest.sh`, and
   `ci/cleanroom-inventory.txt` were shipping into every export** (no `DENY` entry covered them;
   `ci/` is not wholesale-denied). None are needed *inside* a Zone A clone — they build/verify
   *other* clones (this repo's own tree, or a landing branch on the full-tree receiving repo).
   Added as a labeled class in `DENY` with a class-level comment. (This also means the reviewer's
   live reproduction — the scan detecting its own literal string arrays — is fixed as a side
   effect: the scanner script itself no longer ships.)
3. **[Important]** The canary selftest now asserts each mode's own named check-error substring
   appears in the log (not just "exit nonzero") — `canary_expect()` in
   `ci/cleanroom-selftest.sh` maps `deny|artifact|mcp|identifier` to the exact string its intended
   check emits. A canary caught by the wrong check, or failing for an unrelated reason (e.g. a
   riscv-dv fetch network hiccup), now fails the selftest instead of passing vacuously.
4. **[Important]** The pristine-fetch verify was tautological (checkout `FETCH_HEAD`, diff against
   `FETCH_HEAD` — always empty). Replaced with two independent, meaningful checks: (a) `git
   rev-parse FETCH_HEAD` equals the locked rev in `vendor/google_riscv-dv.lock.hjson` exactly,
   logged; (b) no file in the fetched tree contains `Ibex Specific` — DV_prompt §12
   precondition 6's own pristine test, and the actual evidence of pristine-ness. Item 3's ledger
   text above and the function's header comment were rewritten to describe what is actually
   verified.
5. **[Minor]** `cleanroom_check_deny_absence`'s `docs/dv` membership test now iterates
   `DOCS_DV_ALLOWED` instead of a hardcoded `case` with the same four names duplicated — single
   authority.
6. **[Minor]** `ci/cleanroom-inventory.txt`'s regenerate command now excludes `.mex` (was missing)
   and its header note says explicitly to keep the exclusion set in sync with `DENY`'s top-level
   entries in `ci/make-cleanroom.sh`, rather than silently drifting.

**Full-mode selftest is now green end-to-end** (all of a–h, all four canaries, all four
landing-check sub-cases) — captured at `docs/dv/evidence/ws7-selftest-tdd/t1-fullmode-green.txt`.
`--pre-overlay` green re-captured at `t1-green.txt` (canary assertions now check the named error
string too, not just nonzero exit).

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
  directory", exit 127) and `t1-green.txt` (`ci/cleanroom-selftest.sh --pre-overlay`, 0 failures,
  re-captured post-fix-round-1 with the named canary-string assertions).
- `t1-fullmode-green.txt` (`ci/cleanroom-selftest.sh`, no flag): full mode, 0 failures, all of
  a–h, all four canaries (each caught by its own named check), all four landing-check sub-cases.
  Captured post-fix-round-1 against T2's landed overlay (commits `583b4be9` + `d3b70285`).
