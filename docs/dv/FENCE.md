# The knowledge fence

This file is the fence rulebook for the Ibex auto-DV effort. It decides every path in the tree.
It expresses the fenced set as path globs, never as document titles (`DV_prompt.txt` Section 3).
This copy governs the full tree. A Zone A variant ships in each cleanroom export
(`ci/cleanroom-overlay/docs/dv/FENCE.md`). Where another document and this file disagree, this
file wins — stop and report.

## The zone model

Zone A is a cleanroom export: a separate clone that `ci/make-cleanroom.sh` builds and verifies.
Generation work (feature list, testplan, TB, tests, coverage) happens only there. Zone B is this
full tree: it holds the existing DV collateral and runs evaluation only. Infra sessions in the
full tree are contaminated by design. They never do generation.

The fence keeps **previous Ibex DV collateral** out of Zone A. Tools are not collateral: the
export ships the three local MCP servers and the Zone A skill variants (the 2026-09-02 fence-scope
amendment, `docs/superpowers/specs/2026-09-02-zone-a-fence-scope-amendment.md`). The isolation is
the clone boundary — a fresh export contains nothing fenced for a tool to read.

## What is fenced, and why

The single machine-readable deny list is the `DENY=(...)` array in `ci/make-cleanroom.sh`, plus
the default-deny roots below. Each array entry carries its own "why" comment. This section only
summarizes the classes. If this summary and the array disagree, the array is what the export
builder enforces — repair the difference before the next export.

Default-deny roots (deleted wholesale, then the allowlist is restored):

- `dv/**` — all existing DV. Allowed back in: `dv/auto_dv/**` (the generated-work namespace).
- `docs/dv/**` — DV process docs. Allowed back in (supplied as Zone A variants by
  `ci/cleanroom-overlay/`): `FENCE.md`, `SIM_RECIPE.md`, `TB_CONTRACT.md`, `dv_principles.md`.

Plain-deny classes (one glob per entry in the array):

- Process history: `docs/superpowers/**`, `.mex/**`, `.github/**`.
- Formal collateral: `formal/**`.
- Vendored DV inputs: `vendor/riscv?isa?sim*` (the fork and its lock/vendor files),
  `vendor/patches/**`, `vendor/google_riscv-dv.vendor.hjson` (deleted by the pristine-fetch step).
- Cosim-referee disclosure: `ci/build-spike.sh`, `ci/setup-cosim.sh`, `ci/run-cosim-test.sh`,
  `ci/vars.env`, `ci/install-build-deps.sh`, `flake.nix`.
- Existing-flow drivers and process helpers: `ci/jenkins/**`, `ci/lint-commits.sh`.
- Evaluator-only rubrics: `ci/reviews/fence-integrity.md`, `ci/reviews/test-overlap.md`.
- Verification documentation: `doc/01_overview/verification_overview.rst`,
  `doc/03_reference/{verification,verification_stages,cosim,testplan,coverage_plan}.rst`,
  `doc/03_reference/images/tb*.svg`.
- Builder tooling: `ci/make-cleanroom.sh`, `ci/check-landing.sh`, `ci/cleanroom-selftest.sh`,
  `ci/cleanroom-inventory.txt`, `ci/cleanroom-overlay/**` (these build and gate exports — they
  are never needed inside one).

## The `ci/` allowlist

Inside an export, `ci/` is default-deny. Exactly these ship and are readable:

- `ci/env.sh` (Zone A variant)
- `ci/setup-venv.sh`
- `ci/get-toolchain.sh`
- `ci/check_fcov_expectations.py` (Zone A variant)
- `ci/mcp/` (Zone A wrapper variants + probes)
- `ci/reviews/` (the six-file Zone A rubric set)
- `ci/requirements-cocotb.txt`
- `ci/requirements.lock`

## riscv-dv attestation

riscv-dv-verified-on: 2026-09-02 — rev `71666ebacd69266b1abb7cdbad5e1897ce5884e6`. This equals
the `rev` in `vendor/google_riscv-dv.lock.hjson`. The export's `vendor/google_riscv-dv/` tree is
not the checked-in tree (which carries local patches). The builder fetches upstream
`chipsalliance/riscv-dv` at exactly this revision and verifies the fetch
(`_cleanroom_place_riscvdv` in `ci/make-cleanroom.sh`, WS7 T1): the fetched commit SHA must equal
the locked rev, and no fetched file may contain the local-patch marker. The exported tree is that
revision, so a tree diff against upstream at that revision is empty.

## Build an export (one command)

1. Run: `bash ci/make-cleanroom.sh <DEST>` (default DEST: `../ibex-cleanroom`).
2. The script archives HEAD, applies the deny list, fetches pristine riscv-dv, applies the
   Zone A overlay, and self-verifies. It writes DEST only when every check passes.
3. If DEST exists and is not empty, the script refuses. Pass `--force` only after you saved the
   old export's work (see the next section). `--force` deletes the old DEST completely.

## Update an export

Exports are immutable snapshots. An update is a re-export, never an in-place sync.

1. In the old export, save the team's work: `git format-patch <root>..HEAD` for the
   `dv/auto_dv/**` commits.
2. Build the new export into a new directory (or into the same path with `--force`, after step 1).
3. In the new export, apply the patches: `git am <patches>`.
4. `ci/check-landing.sh` validates the same commit range at landing time, so a patch series that
   strays outside `dv/auto_dv/**` fails there.

## Land generated work

1. Move the `dv/auto_dv/**` commits from the export onto a branch of this repo
   (`git format-patch` / `git am`).
2. Run: `ci/check-landing.sh <base> <head>`. It rejects any change outside `dv/auto_dv/**`, any
   rename/delete/symlink outside it, and any new file whose basename does not start with `gen_`
   (exempt: `dv/auto_dv/.gitignore`, `dv/auto_dv/contract/**`).
3. A human reviews the branch before merge. The landing check is a gate, not the review.

## Zone B evaluation protocol

Zone B runs **one evaluation run** per submission: it builds the generated TB and attaches its
own referees. The submission returns a **mechanical acknowledgment only** — received and queued,
an exit status, no content. Nothing returns to Zone A: no logs, no referee findings, no hidden
coverage-model results, not even bin names. Zone B artifacts stay Zone B-side and feed the human
evaluation report. The retired visible/blind dual-run design is superseded (2026-09-02 amendment).

## Honor rules — humans who operate both zones

- Do generation work only inside a verified export, in a fresh session.
- Do not paste, paraphrase, or summarize fenced content into any Zone A session, file, or prompt.
- Do not carry Zone B results back to Zone A. The only return channel is the mechanical ack.
- If fenced content reached you and you must continue in Zone A, record the exposure in the
  intervention log. The owner decides how to proceed.
- Infra sessions never do generation, and never paste fenced content into allowed files.

## Denied by URL, not by path

Fenced collateral also exists outside this repository. No path glob can deny it, so Zone A
sessions must not fetch or read:

- OpenTitan's `hw/ip/rv_core_ibex/dv/**` and its testplans (Ibex DV in an integrator repo).
- CHERIoT-Ibex `dv/**` (a fork with its own DV; a likely web-search hit because the `opentitan`
  build config's base ISA names CHERIoT).
- The rendered Ibex documentation on readthedocs: its verification pages. The design pages exist
  locally under `doc/`.

The general rule stands: network fetches of any Ibex repository are blocked for Zone A; upstream
open-source projects (riscv-dv, riscv-isa-sim, cocotb, UVM) are allowed (`DV_prompt.txt`
Section 3).

## Deferred machinery

The owner's 2026-09-02 speed directive cut WS7 to the export path. These pieces are deferred, not
dropped. Each has its authority; the v1 snapshot design is in git history at commit `86eba26e`.

1. Published snapshot branch + sync automation (orphan append-only history, serialized syncs,
   rotation/revocation) — spec `2026-09-01-auto-dv-setup-design.md` §WS7 "Zone A — clean room".
   Today: updates are re-exports.
2. `ci/fence.yaml` promotion — amendment "Open items for the owner" item 2. Today: the deny list
   lives in `ci/make-cleanroom.sh` (one authority).
3. Full escape harness — amendment change 4; spec §WS7 escape tests. Its cases: "fetch master";
   "read sibling clone" (the escape test for the tool data-reach ruling); "fetch upstream ibex
   DV"; the negative control (fsdb-mcp opens a Zone A-produced FSDB, and the recipe's
   compile-and-run succeeds — anti-vacuity for the suite itself). The export self-verify covers
   clone contents; this harness covers boundary behavior.
4. `zoneb-run` referee attachment (human fcov binds + cosim referee onto the generated TB) —
   amendment "Consequence for the execution model" + open item 3. Built at the Phase-1
   evaluation gate.
5. Spec §WS7 enforcement-stack layer 2 — Zone A permission rules (deny `git fetch`/remote
   mutation; codex network-restricted). Deferred per the WS7 plan; ruling: codex network stays on
   in Zone A (needed to clone upstream spike), discipline is advisory via `AGENTS.md`.
6. Full spec:139 triage-on-add at every directory depth — beyond the top-level
   `ci/cleanroom-inventory.txt` tripwire (WS7 plan pre-review, deferred list). Today's defense in
   depth: the tripwire plus the deny/item-9/whole-export scans.

## Scope note on the gate evidence

The DUT wrapper under `docs/dv/evidence/ws7-gate/` (`gen_dut_top.sv`, `gen_smoke_tb.sv`) is
smoke-scope gate evidence only. It is not the canonical `gen_dut_top`. Generation teams author
their own wrapper to the `DV_prompt.txt` Section 2 owner ruling.
