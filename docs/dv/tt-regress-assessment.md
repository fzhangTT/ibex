# tt-regress (regression-scheduler) — written assessment

Per the spec's Approved-decisions table (`docs/superpowers/specs/2026-09-01-auto-dv-setup-design.md`
line 13): "Regression flow: Jenkins + LSF shell scripts (tt-regress: written assessment only)". This
doc is that assessment: read the install, verify or correct each recon claim against it, and record
why WS4 chose Jenkins+LSF instead. Per `docs/dv/dv_principles.md` §4 ("Evidence over inference"),
every claim below cites a path into the install; anything not confirmed is marked unverified.

Install read: `/tools_risc/tt/regression-scheduler/latest` (symlink to
`/tools_vendor/tt/regression-scheduler/cde3bef8/`), its `README.md`, and
`regression_scheduler.py`, `regression_scheduler_config.py`, `job.py`, `job_run.py`. Sibling entry
points: `regr-info`, `regr-clean`, `regr-kill`, `regr-launch`, `regr-test` (thin bash wrappers under
`scripts/`, each `exec`'ing a `tools/*.py` script against a MySQL job DB).

## What tt-regress is (verified)

- A YAML-driven job scheduler: repos declare jobs/groups/schedules in a `.regression_config.yaml`
  (syntax documented `README.md:15-132`); a cron-driven `regression_scheduler.py` builds a priority
  queue from `frequency`/`cron`/`priority` fields and `bsub`s ready jobs (`README.md:140`,
  `README.md:213-226`).
- A job is a linear list of shell `commands` run in a clone of the owning repo — genuinely
  arbitrary, not restricted to any one tool: `regression_scheduler_config.py` only special-validates
  a command when its first token matches `bzsim` (`regression_scheduler_config.py:127-140`); every
  other command string passes through unchecked. This is the "raw `command:` escape hatch" and it
  is real and already the primitive the config format is built on, not a fallback bolted on the
  side.
- Per-job execution wraps the command list in `commands.sh`/`job.sh`/`job_wrapper.sh` and launches
  it either as a local subprocess (`--no-lsf`) or via `bsub` (`job_run.py:396-452`).
- Job-run bookkeeping (start/finish/kill/clean, directory retention) lives in a MySQL-backed job DB
  queried by `regr-info`/`regr-clean`/`regr-kill` (`README.md:417-546`; schema at
  `README.md:478-545`).

## Why it does not fit ibex today

The spec's recon line (`docs/superpowers/specs/2026-09-01-auto-dv-setup-design.md:102`) asserted
five points. Verifying each against the code:

1. **"reusable YAML/DAG orchestrator skeleton"** — the YAML half is verified (above). The **DAG**
   half is **not verified — corrected by evidence**: no dependency-graph/`depends_on` concept exists
   anywhere in the install. Jobs are independent, flat list entries ordered only by a scalar
   priority × group-priority product (`README.md:140`); there is no code to express "run B after A
   finishes." What's reusable is the YAML *config* shape, not a DAG engine.
2. **"build/run backends are Bazel/bzsim-only"** — **partially verified**. The scheduler's own code
   has no functional Bazel integration — no invocation, import, or command targets Bazel; the one
   hit is an incidental TODO comment about which "Bazel-generated files are useful to keep"
   (`job_run.py:351`) in a downstream job's output directory, not anything the scheduler drives.
   Bazel otherwise appears only in `README.md`'s prose/diagrams describing what `bzsim` itself does
   downstream (`README.md:196-199`). What *is* bzsim-specific in the scheduler's own code: (a) the
   schema validator requires `--name`/`--lsf-opt=-qriscv...` only on
   commands shaped like bzsim invocations (`regression_scheduler_config.py:127-140`), and (b) every
   job run gets `BZSIM_LSF_GROUP_NAME`/`BZSIM_LSF_PROJECT_NAME`/`BZSIM_LSF_QUEUE` env vars
   (`job_run.py:85-87`) that only bzsim knows how to consume to bsub its own build/run sub-jobs. A
   non-bzsim command (e.g. our `ci/jenkins/*.sh`) runs fine as a raw command, but gets none of that
   plumbing — no adapter exists for a Bazel-less/bzsim-less build+run backend.
3. **"scheduling delegated to LSF `bsub -w`"** — **not verified, contradicted by the code**. The
   actual `bsub` invocation is `bsub -J ... -o ... -e ... -P ... -g ... -q<queue> -W20160 -cwd ...`
   (`job_run.py:411-431`); there is no `-w`/`-K` flag anywhere in the install
   (`grep -n "'-w'\|\"-w\"\|-K\b" *.py` — no hits). Since plain `bsub` submits and returns
   immediately, job pendency is instead re-checked by polling `bjobs -p -J <name>`
   (`job_run.py:481-489`), not by a wait-condition on submission.
4. **"results reporting assumes internal Simscope (hard exit on unknown repos)"** — the
   Simscope-assumption half is verified: every job run (unless `--no-lsf`-local and skip-clone)
   posts a `regr-start`/`regr-finish` pair via `/site/simscope/riscv/bin/tunnel-run.sh`
   (`job_run.py:300-330`). The **"hard exit"** half is **not verified — contradicted by the code**:
   an unmapped `gl_project_path` produces a `logger.warning` and falls back to
   `project="unknown", component="unknown"` (`job_run.py:316-324`), not a `sys.exit`/exception —
   the run continues, just with an unlabeled Simscope entry.
   - **New finding, not in the original recon line**: a stronger, unconditional lock-in than
     Simscope is the tool's dependency on the internal GitLab instance itself. Config download and
     repo cloning go through `python-gitlab` against `aus-gitlab.local.tenstorrent.com`
     (`regression_scheduler.py:7` `import gitlab`; `regression_scheduler.py:389-450` parses
     `--repo-link` as an `aus-gitlab...` URL and authenticates an oauth/private token against it).
     ibex's repo of record is `https://github.com/fzhangTT/ibex.git`
     (`docs/superpowers/specs/2026-09-01-auto-dv-setup-design.md:101`) — not on that GitLab — so
     this is a harder blocker than the Simscope-labeling gap: config fetch and repo clone would need
     a GitHub-shaped code path that does not exist in the install.
5. **"raw-`command:` escape hatch exists but not pursued"** — verified (item 2 above); "not
   pursued" is this workstream's decision, recorded below.

## What adopting it would take (sized honestly)

Adopting tt-regress for ibex means going through the raw-`command:` escape hatch end to end, since
ibex has neither a GitLab-hosted repo nor a bzsim/Bazel build:

- A `.regression_config.yaml` with one job whose `commands:` invokes our own
  `ci/jenkins/{smoke,nightly,coverage}.sh` (no schema changes needed — item 2/5 above already
  permit an arbitrary command).
- A GitHub-shaped repo-fetch path: the scheduler's config download and clone are GitLab-API-only
  (`regression_scheduler.py:389-450`); using it against `github.com/fzhangTT/ibex` would need either
  an upstream code change to the vendored tool (out of scope — we don't own it) or standing up a
  GitLab mirror of the repo purely to satisfy this tool.
- A results backend, since ibex has no Simscope presence: either accept the "unknown"/"unknown"
  Simscope fallback (item 4) and lose per-run visibility beyond the job-level page, or write and
  operate a small adapter that posts ibex's own `regr_junit.xml`/coverage artifacts somewhere
  queryable — real, unbuilt work, not a config tweak.
- Standing up (or getting access to) the MySQL job DB the entry scripts assume
  (`README.md:417-449`), plus the maintainer-side setup in `README.md:547-651`
  (`data/.gitlab_key`, `data/.simscope_key`, `data/simscope_component_map.json`, a cron deployment).

None of this is large in absolute terms, but every piece (repo-fetch, results, DB/cron ownership) is
new integration surface for a tool this fork does not maintain, to get back only what WS4's much
smaller `ci/jenkins/*.sh` + Jenkinsfile + LSF `bsub -n N` already provides for one regression's
worth of scheduling.

## Decision

Per the spec's Approved-decisions table
(`docs/superpowers/specs/2026-09-01-auto-dv-setup-design.md:13`): **Jenkins + LSF shell scripts**,
tt-regress not adopted — the GitHub-vs-GitLab mismatch (item 4) and the missing results backend
(item 4/adoption above) are the two blockers with no cheap fix; the DAG/`bsub -w`/hard-exit claims
in the original recon line turned out to be unverified or contradicted, so they were not weighed in
this decision, and are corrected here for the record.

**Revisit trigger:** if per-test LSF fan-out (WS4 phase 2, `docs/superpowers/specs/2026-09-01-auto-dv-setup-design.md:98`)
is ever needed, tt-regress's priority-queue-over-`bsub` machinery is the natural comparison point —
re-check this doc's item 3 (no wait-condition machinery today) before assuming it solves per-test
fan-out for free.
