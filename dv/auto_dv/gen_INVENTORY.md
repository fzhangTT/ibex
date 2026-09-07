# Ibex auto-DV cleanroom: inventory for human review

Branch `cleanroom/run-a` of the Zone A cleanroom export (export commit 1908ddd). Written 2026-09-07T18:17Z by the
Orchestrator at HEAD 041e2b3 (1141 commits above the export), after the owner stopped the agent team on 2026-09-05
19:05Z (owner ruling LOG-100 in `dv/auto_dv/docs/gen_intervention_log.md`). Every count below was taken from
`git ls-files` at that HEAD; the two commits that add this file and the handoff copies come after it.

Everything the team produced is under `dv/auto_dv/**` with the `gen_` prefix (the contract in
`dv/auto_dv/contract/README.md`; two exceptions are listed in Section 9). The RTL under `rtl/` was never modified.

## 1. Reading order

1. This file.
2. `dv/auto_dv/handoff/gen_orchestrator_handoff_2026-09-05.md`: where work stopped, the first resume items, the rows
   each role still owes, held artefacts, open owner items. The six role handovers are beside it
   (`gen_status_<role>_2026-09-05.md`; the HANDOVER block is at the top of each, the rest is that role's running log).
3. `dv/auto_dv/docs/gen_intervention_log.md`: every owner question, ruling and directive, LOG-001 through LOG-100 with
   corrigenda. This is the authority for anything the plan documents cite by LOG id.
4. `dv/auto_dv/docs/gen_dashboard.md`: the regression dashboard regenerated after the measured round (coverage table,
   closure-round index, every purpose-4 regression seen in the out root).
5. `dv/auto_dv/evidence/gen_round_0/gen_round_summary.md`: the measured coverage record (Section 6 below).

## 2. Deliverables (DV_prompt.txt Section 11)

| Deliverable | File | Owner role | Notes |
|---|---|---|---|
| 1 Feature list | `dv/auto_dv/docs/gen_feature_list.md` | dv-lead | Version 2, promoted after the Critic's review |
| 2 Test plan | `dv/auto_dv/docs/gen_test_plan.md` | dv-lead | feature -> test-plan items -> tests -> bins; Section 0 carries the code-comment rule |
| 3 Functional-coverage plan | `dv/auto_dv/docs/gen_fcov_plan.md` | dv-lead | bin definitions; the gate criterion text is owed a LOG-100 rewrite (handoff Section 2 item 1) |
| Traceability | `dv/auto_dv/docs/gen_trace_feature_tp.csv`, `gen_trace_tp_bin.csv`, `gen_trace_witness_ids.csv` | dv-lead | checked by `dv/auto_dv/tools/gen_trace_check.py` |
| TB architecture | `dv/auto_dv/docs/gen_tb_architecture.md` | tb-infra | Section 5 defines the gated coverage scopes |
| Component APIs | `dv/auto_dv/docs/gen_component_api_*.md` (24 files) | tb-infra | one per TB component |
| Runtime flow API | `dv/auto_dv/docs/gen_runtime_api.md` | runtime | the testlist schema and every flow script's contract |
| 5 Probe register | `dv/auto_dv/docs/gen_probe_register.md` | tb-infra / Critic | every TB probe into the DUT, with the Critic's approval status |
| 7 Bug log | `dv/auto_dv/docs/gen_bug_log.md` | dv-lead | B1..B20 RTL bug candidates (every one "candidate" until a committed reproducer log exists); Section 2 security-relevant behaviours for owner decision; Section 3 doc defects |
| TB defect register | `dv/auto_dv/evidence/gen_tb_defects.md` | dv-lead | defects of the team's own TB, tests and harness (kept out of the bug log) |
| Coverage exclusions | `dv/auto_dv/excl/gen_exclusions.el`, `gen_exclusions_README.md`, `gen_excl_f1_pass.py`, `gen_excl_select.py`, `gen_precheck/` | rtl-arch | pass 14, generated from the measured round; the README carries the authority chain |
| Unreachability evidence | `dv/auto_dv/evidence/gen_unreachability_evidence.md`, `dv/auto_dv/evidence/gen_t022_formal/` (113 files) | rtl-arch | machine evidence (formal jobs, logs, model) behind the exclusion candidates |
| RTL facts records | `dv/auto_dv/evidence/gen_b8_rtl_facts.md`, `gen_b4_rtl_facts.md`, `gen_t090_rtl_facts.md`, `gen_t102_rtl_facts.md`, `gen_nmi_nested_mret_rtl_facts.md` | rtl-arch | behaviour statements with every gating term line-cited |
| Test Writer plan | `dv/auto_dv/docs/gen_test_writer_plan.md` | test-writer | |
| Round requests | `dv/auto_dv/evidence/gen_round1_request.md`, `gen_round2_request.md` | dv-lead | the request form of record for each measured round |

## 3. Tree map (tracked files under `dv/auto_dv/`, 5499 in total)

| Directory | Files | What it holds |
|---|---|---|
| `contract/` | 1 | the landing contract (README) |
| `docs/` | 125 | the deliverables above, 81 Critic verdicts (`gen_critic_*.md`), the intervention log, the dashboard, the plan sets |
| `env/` | 12 | SystemVerilog packages: agents, checkers, config, export (RVFI record lines), fcov covergroups, memory model, RVFI |
| `tb/` | 37 | `gen_tb_top.sv`, `gen_dut_top.sv` (wraps `ibex_core`), interfaces, binds, protocol properties, probes, file lists (`gen_tb.f`, `gen_rtl.f`, `gen_smoke_tb.f`), the knobs and fcov code generators, `gen_tb_local.sh` (local compile/run), `unit/` (SV unit-test tops) |
| `gen_tb/` | 25 | the cocotb side: bridge, export, handles, image, knobs, and `gen_tests/` (the `gen_ut_*` unit and lockstep tests) |
| `tests/` | 69 | `gen_test_*.py` cocotb tests on `gen_test_lib.py`, `gen_programs/` (per-test program generators), `gen_fixtures/` (harness unit tests and the local run fixture), `gen_fcov_manifest.py` (renders the fcov manifests) |
| `stim/` | 53 | `gen_program.py` (assemble and link a program image), `gen_directed/` (39 directed `.S` programs), the riscv-dv target, ELF to memory tools |
| `isa/` | 8 | the Spike ISA shim (DPI): `gen_isa_shim.cc`, counters, `gen_isa_shim_build.sh` |
| `flow/` | 21 | `gen_build.py`, `gen_run.py`, `gen_regress.py`, `gen_round.py`, `gen_cov_report.py`, `gen_verdict.py`, `gen_dashboard.py`, `gen_mirror.py`, `gen_testlist.yaml`, coverage config (`gen_cm_hier.cfg`), `gen_site.yaml.example` |
| `fcov_expectations/` | 27 | one `<test>.fcov.yaml` manifest per cocotb test that declares bins (17: the 15 measured tests plus `gen_test_irq_basic` and `gen_test_pmc_ctrl`, unmeasured at HEAD) and per icache-ECC unit test (10) |
| `excl/` | 20 | the exclusion file and its generators, `gen_precheck/` (URG pre-check logs of every pass) |
| `mutations/` | 7 | mutation records (`gen_mut_*.md`), one block per mutation next to the checker it proves |
| `evidence/` | 4738 | see Section 8: `gen_tdd_logs/` (4294 retained run logs with a manifest), the round records, formal evidence, fixtures, verdict excerpts, 84 Critic verdicts and response records |
| `reviews/` | 332 | cross-model review artifacts (Section 7) |
| `tools/` | 23 | record and plan checkers (`gen_record_check.py`, `gen_section_check.py`, `gen_register_cites.py`, `gen_trace_check.py`, `gen_comment_census.py`, `gen_round_form_check.py`, ...), `gen_cross_review.sh` (the review wrapper), `gen_launch_check.sh` (DV_prompt Section 12 launch preconditions) |
| `handoff/` | 7 | committed copies of the Orchestrator handoff and the six role STATUS files (added with this inventory) |

Not tracked (gitignored by `dv/auto_dv/.gitignore`): `dv/auto_dv/work/` (each role's working directory, the
Orchestrator's `TASKS.md` event log of 2565 lines, the commit-chain scripts under `work/orchestrator/chains/`) and
`dv/auto_dv/out_*` (1.8 GB of local smoke and mutation runs, each with its own `vcs_simv.vdb`). Both exist only in the
originating clone `/localdev/fzhang/ws/ibex-challenge`. The out-of-tree regression root is in Section 6.

## 4. Tests

`dv/auto_dv/flow/gen_testlist.yaml` is the single testlist (schema: `gen_runtime_api.md`). At HEAD it carries 3 builds
(`gen_smoke`, `gen_smoke_cocotb`, `gen_tb`) and 105 test entries:

| Tier | Entries | Meaning |
|---|---|---|
| smoke | 17 | the measured cocotb tests plus two TB boot/lockstep smokes; run by `--tier smoke` and every higher tier |
| targeted | 3 | `gen_test_bit_draft`, `gen_test_pmp_mseccfg`, `gen_test_pmp_lock` |
| check | 85 | build/elaboration checks, `gen_ut_*` unit and lockstep tests, every `*_red` forced-failure companion; `measured: false`, never in a coverage merge |

15 entries are `measured: true` (they alone feed the coverage gate); 63 entries belong to tb-infra, 41 to
test-writer, 1 to runtime. Every measured test has an fcov-expectation manifest in `dv/auto_dv/fcov_expectations/`,
checked after each run by the flow (`gen_run.py --fcov-check`, `ci/check_fcov_expectations.py`).

Each test's evidence (its red run, green run, mutation proof and forty-seed sweep where required) is a record under
`dv/auto_dv/evidence/gen_tdd_*.md` with the retained logs under `dv/auto_dv/evidence/gen_tdd_logs/<area>/` and the
log manifest `dv/auto_dv/evidence/gen_tdd_logs/gen_manifest.md` (path, source, bytes, md5 per retained file).

## 5. How to run

The commands are quoted from `docs/dv/SIM_RECIPE.md` and the flow scripts' own usage text (`python3 <script> --help`
prints the full option list). The measured round of Section 6 was produced by exactly this flow (`gen_round.py`); the
Orchestrator did not re-run them while writing this file.

Environment, once per shell (a login shell on a site host; source from the clone root):

```bash
cd /path/to/clone
bash -lc 'source ci/env.sh'      # or, interactively: source ci/env.sh
```

One-time per checkout: `bash ci/setup-venv.sh` (Python venv from `ci/requirements.lock`, cocotb included), then
`bash ci/get-toolchain.sh` (the lowRISC rv32imcb GCC into `$IBEX_TOOLS_DIR`). Spike (the reference model) is built per
`docs/dv/SIM_RECIPE.md` Section 11. `ci/env.sh` fails loud when a tool is missing (LOG-100 decision 2).

Out-tree root: LSF compute hosts must see it, so it lives on shared storage. Copy
`dv/auto_dv/flow/gen_site.yaml.example` to `dv/auto_dv/work/runtime/gen_site.yaml` and set `out_root` and
`mirror_root`, or export `GEN_DV_OUT_ROOT`. The team's root was `/proj_soc/user_dev/fzhang/ibex_dv_out`.

Regressions (`dv/auto_dv/flow/gen_regress.py`; builds are compiled on demand, runs fan out on LSF with `bsub -K`,
coverage is merged with URG at the end, `<outdir>/manifest.yaml` and a one-screen summary are written):

```bash
python3 dv/auto_dv/flow/gen_regress.py --tier smoke --tag smoke_$(date -u +%m%d)          # the smoke tier
python3 dv/auto_dv/flow/gen_regress.py --tier check --tag check_$(date -u +%m%d)          # unit and forced-red checks, unmeasured
python3 dv/auto_dv/flow/gen_regress.py --tests gen_test_isa_alu,gen_test_mul_div --seeds 3
python3 dv/auto_dv/flow/gen_regress.py --repro gen_test_isa_alu 12345 --waves            # one test, one seed, FSDB
python3 dv/auto_dv/flow/gen_regress.py --tier full --purpose 4 --tag <tag>               # a measured full regression
```

Common knobs: `--outdir DIR | --tag T`, `--local` (run on this host), `--max-parallel N`, `--no-coverage`,
`--no-cond`, `--elfile F` (an exclusion file, loaded strict), `--dump-exclusions`, `--base-seed S`. Pass/fail is
decided by `gen_verdict.py` from collected failure mechanisms in the logs, never from the simulator exit code; read
`<outdir>/manifest.yaml` (or the per-run `verdict.txt`) for verdicts, not the driver log.

One run by hand (`dv/auto_dv/flow/gen_run.py`; one seed drives `+ntb_random_seed` and `RANDOM_SEED`):

```bash
python3 dv/auto_dv/flow/gen_build.py --build gen_tb --outdir <out>/build/gen_tb --coverage --cond
python3 dv/auto_dv/flow/gen_run.py --build-dir <out>/build/gen_tb --test gen_test_isa_alu --seed 12345 \
    --run-dir <out>/runs/gen_test_isa_alu_12345 --cov-dir <out>/cov/merged.vdb [--fcov-check] [--waves] [--lsf]
```

A measured closure round (`dv/auto_dv/flow/gen_round.py`; DV_prompt Sections 4 and 5): a full-tier purpose-4
regression with the exclusion files, its URG report copied into `dv/auto_dv/evidence/gen_round_<n>/`, and the index
`dv/auto_dv/evidence/gen_rounds.yaml` updated with the gate row, the gain against the previous round (G = 0.5 points)
and the no-gain streak (N = 5):

```bash
python3 dv/auto_dv/flow/gen_round.py --round <n> [--elfile dv/auto_dv/excl/gen_exclusions.el] [--seeds N] [--base-seed S] [--tag T]
python3 dv/auto_dv/flow/gen_round.py --dry-run --tag <tag>                 # check tier, unmeasured; not a round
python3 dv/auto_dv/flow/gen_round.py --collect <regress outdir> --round <n> # evidence and index from an existing regression
python3 dv/auto_dv/flow/gen_dashboard.py                                    # regenerates dv/auto_dv/docs/gen_dashboard.md
```

Fast local loop without LSF (what the roles used between landings; the exact quirks are in the Test Writer handover):
`FORCE=1 bash dv/auto_dv/tb/gen_tb_local.sh compile <out>` compiles the TB in about a minute; a program image comes
from `python3 dv/auto_dv/stim/gen_program.py --seed S --out <dir> --directed <file.S> --gcc-opts=-Idv/auto_dv/tests/gen_programs`;
`SEED=S bash dv/auto_dv/tests/gen_fixtures/gen_run_fixture.sh <out> <name> <module> <vmem>` runs one cocotb test in a
few seconds. Read `<out>/<name>/verdict.txt` for the result.

Self-tests of the flow and tools (each exits non-zero on failure): `python3 dv/auto_dv/flow/gen_build.py --self-test`,
`python3 dv/auto_dv/flow/gen_cov_report.py self-test`, `python3 dv/auto_dv/tests/gen_fcov_manifest.py --self-test`,
`python3 dv/auto_dv/tb/gen_fcov_codegen.py --check`, `python3 dv/auto_dv/tb/gen_knobs_codegen.py --check`, and
`--self-test` on `dv/auto_dv/tools/gen_section_check.py`, `gen_register_cites.py`, `gen_comment_census.py`,
`gen_norm_probe.py`, `gen_unbuilt_mark_check.py`. Launch preconditions: `bash dv/auto_dv/tools/gen_launch_check.sh`
(prints `ITEM <n> PASS|FAIL`). Cross-model review of a range: `dv/auto_dv/tools/gen_cross_review.sh diff <BASE> <HEAD>`
(the `cross-review` skill wraps it; the artifact lands in `dv/auto_dv/reviews/`).

## 6. Coverage: where the numbers, the VDB and the reports are

One measured coverage run exists. The team called it round 1; the flow's index records it as measured round 0 with
regression tag `round_1` (the naming note is in `dv/auto_dv/evidence/gen_round_0/gen_archive_manifest.md`). Pinned
commit 4a0070285557, 2026-09-04T22:06Z, build configuration `opentitan`, 53 of 53 runs passed, 36 tests in the report.

Gate row (scopes `gen_tb_top.u_dut.u_ibex_core` + `gen_tb_top.u_dut.u_register_file`, gate 80 percent per metric):

| Metric | Percent | covered/total | Gate |
|---|---|---|---|
| line | 83.83 | 3654/4359 | PASS |
| cond | 67.17 | 6464/9624 | below gate |
| toggle | 67.39 | 16877/25044 | below gate |
| fsm | 44.19 | 38/86 | below gate |
| branch | 75.41 | 1831/2428 | below gate |
| assert | 92.74 | 166/179 | PASS |
| group (functional) | 81.47 stored | 3477/4268 | bins >= 80; traceability confirmation NOT claimed |

Owner ruling LOG-100 redefined the functional gate as the bin fraction with the witness ledger out of both terms:
3477/4048 = 85.89 for this run. The stored 81.47 is to be restated beside it in the index by the next team (handoff
Section 2 item 1); the collected record files are never edited (LOG-092). The gate's second condition, a non-author
reviewer confirming the bin-to-plan mapping, has never been claimed, so the functional gate is not called PASSED.

Where the artefacts are:

| Artefact | Location |
|---|---|
| Round index (every measured round and dry run, gate and gain rows) | `dv/auto_dv/evidence/gen_rounds.yaml` |
| Round record (metrics, rulings, regression facts) | `dv/auto_dv/evidence/gen_round_0/gen_round_summary.md` |
| URG text reports copied into the tree | `dv/auto_dv/evidence/gen_round_0/gen_dashboard.txt`, `gen_groups.txt`, `gen_grpinfo.txt`, `gen_asserts.txt`, `gen_hierarchy.txt`, `gen_modinfo.txt.gz`, `gen_modlist.txt.gz`, `gen_merge.log`, `full_exclusions/` |
| Regression manifest, testlist snapshot, build manifest of the run | `dv/auto_dv/evidence/gen_round_0/gen_regress_manifest.yaml`, `gen_testlist_snapshot.yaml`, `gen_build_manifest_gen_tb.yaml` |
| Merged VDB (out of tree, 319 MB with the run tree) | `/proj_soc/user_dev/fzhang/ibex_dv_out/regress_round_1/cov/merged.vdb` |
| Full URG report, HTML and text | `/proj_soc/user_dev/fzhang/ibex_dv_out/regress_round_1/cov/report/` (`dashboard.html`, `dashboard.txt`, `groups.html`, `asserts.html`, ...) |
| The URG command that produced it, its log | `/proj_soc/user_dev/fzhang/ibex_dv_out/regress_round_1/cov/urg_cmd.sh`, `cov/merge.log` |
| Per-run logs and verdicts | `/proj_soc/user_dev/fzhang/ibex_dv_out/regress_round_1/runs/`, `manifest.yaml`, `regress.log` |
| Unmeasured merge of the same regression (check-tier and red runs) | `/proj_soc/user_dev/fzhang/ibex_dv_out/regress_round_1/cov_unmeasured/` |
| Retention manifest (paths, sizes, sha256, how to re-open the VDB) | `dv/auto_dv/evidence/gen_round_0/gen_archive_manifest.md` (LOG-097) |
| Coverage analysis of the run and the bins not hit | `dv/auto_dv/evidence/gen_round_0_coverage_analysis.md`, `gen_round_0_coverage_tables.md`, `gen_bins_not_hit_worklist.md`, `gen_round1_credit/`, `gen_round1_promotion_table.md`, `gen_round1_covergroup_set.md` |
| Critic's verdicts on the round | `dv/auto_dv/evidence/gen_critic_round1_record.md`, `gen_critic_round1_coverage_analysis.md` |

The out-tree root `/proj_soc/user_dev/fzhang/ibex_dv_out` holds 187 entries (about 20 GB): every regression, probe and
canary build of the project, named by tag. `gen_dashboard.md` Section 1a lists the purpose-4 regressions found there.
To re-read the merged VDB open it with Verdi or URG as the retention manifest describes; the two dry runs of the
procedure (`gen_round_0_dryrun`, `gen_round_0_rebaseline`, unmeasured) are in the same index and must not be read as
rounds. Round 2 has not run; its request form is `dv/auto_dv/evidence/gen_round2_request.md` and the dispatch
mechanics are in the handoff, Section 2 item 3.

## 7. Reviews and verdicts

Every feature group was reviewed by a model other than the executing one and, for plan and code changes, judged by the
Critic role (owner directive LOG-095: one cross-model review per feature group, Critic only on plan and code).

- `dv/auto_dv/reviews/`: 332 artifacts, 308 diff reviews (`<date>-claude-diff-<base8>-<head8>.md`) and 24 plan or
  re-plan reviews. The identity header of each names the reviewer CLI, model and effort; from the point Codex hit its
  spend cap the fallback Claude reviewer from a fresh session was used (owner ruling A-001), and each artifact says so.
  Every verdict is `APPROVE`, `APPROVE-WITH-CHANGES` or `REQUEST-CHANGES`; a `REQUEST-CHANGES` blocked the group until a
  recorded re-review (the artifacts of 2026-09-05, rev75 to rev95, are all APPROVE or APPROVE-WITH-CHANGES; their open
  rows are listed per role in the handoff, Section 3).
- Critic verdicts: 81 under `dv/auto_dv/docs/gen_critic_*.md` (plans, TB landings, exclusions, probe register, test
  template) and 84 under `dv/auto_dv/evidence/gen_critic_*.md` (rounds, records, responses).
- Review rubrics the wrapper asserts: `ci/reviews/GUIDE.md` and its five rubric files.

## 8. Evidence tree (`dv/auto_dv/evidence/`, 4738 files)

- `gen_tdd_logs/<area>/` (4294 files): ASCII-normalised copies of run logs (red, green, mutation, sweep) for every
  component and test, indexed by `gen_tdd_logs/gen_manifest.md`. Retained logs are never edited; corrections are
  companion files.
- `gen_tdd_*.md`: the TDD records per component and per test batch (`gen_tdd_batch1..3.md`, `gen_tdd_fcov.md`,
  `gen_tdd_lockstep.md`, ...) and the templates `gen_tdd_test_template.md`, `gen_critic_response_test_template.md`.
- `gen_round_0*`, `gen_round0_*`, `gen_round1_*`, `gen_rounds.yaml`: the measured round and its analyses (Section 6).
- `gen_t022_formal/` (113 files): formal jobs, logs and model behind the unreachability arguments.
- `gen_irq_fixtures/`, `gen_irq_triage/`, `gen_agentfix_pair/`, `gen_wave_4017573/`, `gen_generator_sweep/`,
  `gen_bit_ratified_pairfix/`, `gen_pmp_measurement/`, `gen_sunset_pass1/2/`: the fixture, triage and measurement
  records of the individual landings, each with its logs.
- `gen_fcov_proof_slice*.fcov.yaml`: the fcov-expectation proof slices and their ablations (a manifest that must fail
  when a bin is removed).
- `gen_acceptance_*_verdict_excerpt.log`: acceptance-run verdict excerpts.
- `gen_launch_check_2026-09-03.log`: the launch-precondition record.

## 9. Files outside the landing scope (owner decision needed)

The landing check on the receiving branch accepts only `dv/auto_dv/**` paths (FENCE.md, "Updates and landing"). Two
paths outside it were changed on this branch:

| Path | Commits | Why |
|---|---|---|
| `ci/env.sh` | fca6942 | owner decision LOG-100 (2): `LIBPYTHON_LOC` derived from the clone venv, fail loud when `cocotb-config --libpython` cannot answer; tested three ways (venv present, absent, failing tool) |
| `.claude/skills/cross-review/SKILL.md` | 8f8ab1a, c32d8f3, f127f03 | text kept in step with `dv/auto_dv/tools/gen_cross_review.sh` (the fallback wrapper's detached-checkout rule, the committed-at-HEAD rule, the A-001 pointer) |

Both need to be carried by hand or dropped at landing. Two untracked files at the clone root, `DV_prompt.txt` and
`agent_team_prompt.txt`, are the seed prompt and the team prompt; they were never committed.

## 10. State at the stop, in one screen

- Round 1 (index round 0) measured and recorded; its record accepted (LOG-098); the functional gate's first condition
  passes under LOG-100 (85.89), the traceability condition is unclaimed.
- Round 2 is prepared (request form, selector, canary and dispatch mechanics in the handoff) but not run.
- Open engineering items, in the order the handoff gives them: apply LOG-100 to the plan text and the report tool as
  one joint group; the bus-agent repair on the gated grant shape with its per-seed acceptance; then the round-2
  dispatch. The irq-entry promotion conditions (d), (e), (f) stay open.
- Every role owes review rows (handoff Section 3); nothing is blocked on the owner after LOG-100 except the
  traceability finding.
- Held artefact: the re-dump waveforms of seeds 165313640 and 1207954461, held by tb-infra for the export-cycle-18333
  window; the agent-fix pair's 4.3 GB of regression logs moved to the site trash path recorded in
  `dv/auto_dv/evidence/gen_agentfix_pair/gen_move_record.md` (reversible).

## 11. Caveats for a reviewer

- Dates in records are UTC (`date -u`); the intervention log is the authority when a record and a message disagree.
- A record may cite a `dv/auto_dv/work/...` or an out-tree path only as provenance, never as evidence; evidence is the
  committed excerpt. Where this inventory names an out-tree path (Section 6) it is a location, not evidence.
- The word "round" is overloaded (Section 6); `gen_rounds.yaml` is the count that matters.
- The Orchestrator's own errors of 2026-09-05 (wrong causes repeated in two commit messages, a conditional relayed as a
  fact) are recorded in the handoff and owed corrigenda; the review rows that found them are rev89 and rev94.
