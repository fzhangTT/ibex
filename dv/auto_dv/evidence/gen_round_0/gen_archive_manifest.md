# Round 0 archive manifest: how to re-open the first measured coverage run

Written 2026-09-05T01:47:21Z by the Runtime Manager under owner directive LOG-097. No collected file of the
record was changed; this manifest and the archives it lists are additions.

The team calls this measurement **round 1**; the flow indexes it as **measured round 0**, regression
tag `round_1`. Pinned commit `4a0070285557a2a7dfb50cea9390597143b984b0`. The record is commit
`d29d5db` (23 files under `dv/auto_dv/evidence/gen_round_0`) and its supplement is `a6f811a`
(`gen_modlist.txt.gz`, `gen_modinfo.txt.gz`).

## What is archived, and where

Archive root: `/proj_soc/user_dev/fzhang/ibex_dv_out/regress_round_1/archive`

| file | bytes | sha256 |
|---|---|---|
| `gen_round_0_merged_vdb.tar.gz` | 487548 | `ad51a837b7ea809be81d9a8fee1291d5c0fa3209ee79cb2130bbdc75e2956e1f` |
| `gen_round_0_urg_report.tar.gz` | 1106782 | `e2bc3f51231a41d43288766aaf577a8dfec711e2bee05228343c4688a77756be` |
| `KEEP_ROUND_0_ARCHIVE.txt` | 1438 | `725b6d3d4fcf3880f0a66337506d350e844e7b428b77556bda644de61bd0f869` |

The coverage-database archive's sha256, called out separately because it is the artefact a later
round will want to merge against, is:

    ad51a837b7ea809be81d9a8fee1291d5c0fa3209ee79cb2130bbdc75e2956e1f

Sources, both under `/proj_soc/user_dev/fzhang/ibex_dv_out/regress_round_1/cov`:

| archive | source directory | files |
|---|---|---|
| `gen_round_0_merged_vdb.tar.gz` | `cov/merged.vdb` | 51 |
| `gen_round_0_urg_report.tar.gz` | `cov/report` | 92 |

## Reproducibility

Both archives were built with a fixed member order and fixed metadata, then compressed without a
stored filename or timestamp:

    tar --sort=name --mtime='UTC 1970-01-01' --owner=0 --group=0 --numeric-owner -cf - <dir> | gzip -n > <archive>

Rebuilding either from the same source reproduces its sha256 exactly; I verified both. This is what
lets a reader tell a re-compression from a changed input, which plain `tar czf` would not, because
it stores mtimes and the gzip header stores the source name and time.

Extraction was also checked: `diff -r` between each extracted tree and its source reports no
difference, for all 51 and all 92 files.

## How to re-open the coverage database

    tar xzf gen_round_0_merged_vdb.tar.gz -C <somewhere>
    urg -full64 -format both -dir <somewhere>/merged.vdb -report <somewhere>/report -show ratios

Two things that will otherwise waste a reader's time, both found by running the commands rather
than transcribing them:

- The input flag is `-dir`. `-dbname` names urg's OUTPUT database, and pointing it at the
  archived database fails with `Error-[URG-ND] No source data`.
- Without `-format both` urg writes only HTML, so there is no `dashboard.txt` to read.

Verified 2026-09-05T01:47:21Z: that command exits 0 and its Total Coverage Summary line is character-identical to
the committed `gen_round_0/gen_dashboard.txt`:

     72.64   83.91 3688/4395   67.18 6471/9633   67.15 19231/28640   44.19 38/86   75.49 1848/2448   89.11 229/257   81.47 3477/4268

Those are the report-wide (ungated) figures. The round's gated numbers are the two DUT subtrees
combined and are in the record's `gen_round_summary.md`; the group column has three definitions and
none of them should be quoted without its scope.

## How to re-open the report without urg

    tar xzf gen_round_0_urg_report.tar.gz -C <somewhere>

The text reports are then readable directly: `report/dashboard.txt`, `hierarchy.txt`,
`modinfo.txt`, `modlist.txt`, `groups.txt`, `grpinfo.txt`, `asserts.txt`, `tests.txt`.
The record already carries copies of six of these plus gzipped `modlist`/`modinfo`; this archive
is the complete directory including the HTML.

## Per-run logs

Not archived (208 MB across 53 run directories) and still in place at:

    /proj_soc/user_dev/fzhang/ibex_dv_out/regress_round_1/runs/<test>_<seed>/

Each run directory holds `result.yaml` (the verdict and, for a checked entry, its `fcov_check`
block with declared/hit/unmet bins), `sim.log`, `sim_stdout.log`, `run.log`, `driver.log`,
`run_cmd.sh`, `bsub_cmd.txt`, `lsf.out`, `lsf.err`, `results.xml`, `exit_code`,
`gen_program_driver.log`, `ucli.key`, and the generated `program/`. Nothing was pruned: the
regression manifest's retention block records `files_pruned: 0` over `runs_planned: 0`, because
no run of this round named an export file.

The regression manifest itself is archived twice over: in place at `/proj_soc/user_dev/fzhang/ibex_dv_out/regress_round_1/manifest.yaml` and in the
record as `gen_round_0/gen_regress_manifest.yaml`.

## Sizes in the out-tree, for a later prune decision

| path | size |
|---|---|
| `runs/` | 208M |
| `build/` | 74M |
| `cov/` | 19M |
| `cov_unmeasured/` | 15M |
| `archive/` | 1.6M |
| whole outdir | 319M |

The two archives are 1.6 MB together, so the coverage evidence survives a prune of the 319 MB
out-tree if one is ever needed. The per-run logs would not; a prune should keep `archive/` and
`manifest.yaml` at minimum.
