# The knowledge fence (Zone A clone)

This file is the fence authority for this clone. It decides every path in the tree. It expresses
the fenced set as path globs, never as document titles. Where another document and this file
disagree, this file wins — stop and report (`DV_prompt.txt` Section 3).

## What this clone is

This clone is a verified cleanroom export. A builder script in the full tree (not shipped here)
deleted all previous Ibex DV collateral before the export was committed, and a launch check
(`DV_prompt.txt` Section 12) verified the result. Everything present in a clone that passed
Section 12 and that this file does not deny is allowed, with one exception: `ci/` is default-deny,
and only the allowlist below may be read.

The fence covers data, not tools. This clone ships the three local MCP servers, the skills, and
the agents. Point them at this clone's own files and out-tree. Any new MCP server addition
requires a fence review in the full tree.

## Denied path globs

These globs are fenced everywhere: in this clone (they must not exist or reappear), in patches,
and in anything you fetch.

- `dv/**` except `dv/auto_dv/**`. All generated work lands under `dv/auto_dv/**` with the `gen_`
  prefix (`dv/auto_dv/contract/README.md`).
- `docs/**` except `docs/dv/FENCE.md`, `docs/dv/SIM_RECIPE.md`, `docs/dv/TB_CONTRACT.md`, and
  `docs/dv/dv_principles.md`.
- `formal/**`
- `vendor/patches/**`
- `vendor/riscv?isa?sim*` — no Spike is vendored here. Clone upstream `riscv/riscv-isa-sim` over
  the network and build it yourself (`DV_prompt.txt` Section 7).
- `doc/01_overview/verification_overview.rst`, `doc/03_reference/verification.rst`,
  `doc/03_reference/verification_stages.rst`, `doc/03_reference/cosim.rst`,
  `doc/03_reference/testplan.rst`, `doc/03_reference/coverage_plan.rst`,
  `doc/03_reference/images/tb*.svg`
- `.mex/**` from the full tree (this clone builds its own mex instance from visible files)

## The `ci/` allowlist

`ci/` is default-deny. Exactly these ship and are readable:

- `ci/env.sh` (Zone A variant)
- `ci/setup-venv.sh`
- `ci/get-toolchain.sh`
- `ci/check_fcov_expectations.py` (Zone A variant)
- `ci/mcp/` (server launch wrappers + probes)
- `ci/reviews/` (exactly six files: `GUIDE.md` plus five rubrics)
- `ci/requirements-cocotb.txt`
- `ci/requirements.lock`

## Denied by URL, not by path

Fenced collateral also exists outside this clone. No path glob can deny it, so do not fetch or
read:

- Any Ibex repository over the network: lowRISC upstream, forks, and integrators. `git fetch` of
  other branches or remotes is blocked. Reading sibling clones on this filesystem is blocked.
- OpenTitan's Ibex-block DV and its testplans (Ibex DV inside an integrator repo).
- CHERIoT-Ibex `dv/**` (a fork with its own DV; a likely web-search hit because this clone's
  `opentitan` build config names CHERIoT in its base ISA).
- The rendered Ibex documentation on readthedocs: its verification pages. The design pages exist
  locally under `doc/`.

Upstream open-source projects that are not Ibex DV collateral are allowed: riscv-dv,
riscv-isa-sim (Spike), cocotb, UVM, and similar (`DV_prompt.txt` Section 3).

## riscv-dv attestation

riscv-dv-verified-on: 2026-09-02 — rev `71666ebacd69266b1abb7cdbad5e1897ce5884e6`. This equals
the `rev` in `vendor/google_riscv-dv.lock.hjson`. The export builder fetched upstream
`chipsalliance/riscv-dv` at exactly this revision and verified the fetch: the fetched commit SHA
equals the locked rev, and no fetched file carries a local-patch marker. The shipped tree is that
revision, so a tree diff against upstream at that revision is empty.

## Zone B evaluation protocol

Zone B (the full tree) evaluates submitted work. It runs **one evaluation run** per submission
with its own referees attached. The submission command is in `docs/dv/SIM_RECIPE.md`. The
submission returns a **mechanical acknowledgment only** — received and queued, an exit status, no
content. Nothing returns to this clone: no logs, no findings, no coverage results, no bin names.
Never read anything produced in Zone B.

## Updates and landing

Exports are immutable snapshots. An updated export arrives as a new clone. To carry work across:
save the `dv/auto_dv/**` commits with `git format-patch`, then apply them in the new clone with
`git am`. Landing on the full tree goes through a landing check plus human review: only
`dv/auto_dv/**` paths, no symlinks, new files use the `gen_` prefix (exempt:
`dv/auto_dv/.gitignore`, `dv/auto_dv/contract/**`).

## Honor rules — humans who operate both zones

- Do generation work only inside this clone, in a fresh session.
- Do not paste, paraphrase, or summarize fenced content into any session, file, or prompt here.
- Do not carry Zone B results back. The only return channel is the mechanical ack.
- If fenced content reached you and you must continue here, record the exposure in the
  intervention log. The owner decides how to proceed.
