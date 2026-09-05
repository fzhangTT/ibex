# Agent-fix pair: the restructured bus driver against the committed agent, retained

Written 2026-09-05T14:21Z by the Runtime Manager, on tb-infra-2's request. EVIDENCE ABOUT AN UNCOMMITTED AGENT: no property
of any commit, and no manifest row. The record beside this file is BYTE-IDENTICAL to the served copy under
`dv/auto_dv/work/runtime/done/`, which git does not track.

| file | bytes | sha256 |
|---|---|---|
| `gen_agentfix_early_cycles.txt` | 9240 | `a8a976daff786aeb35779e058d1d4f955e34d4622705bec9f90873c4ecffca12` |
| `gen_agentfix_pair.yaml` | 6373 | `96cb06397c4ea508ddea7379af318127d1c73953926b68790d702593944ae193` |

## The result: FAILS the acceptance on both seeds

The acceptance was ZERO firings of `sva_ibus_gnt_only_with_req` on both seeds.

| seed | verdict | firings, ported | firings, committed | error lines, ported | error lines, committed |
|---|---|---|---|---|---|
| `165313640` | FAIL | 4 | 1 | 4294133 | 627 |
| `1207954461` | FAIL | 108 | 1 | 1825734 | 693238 |

## The secondary fact, reported either way as asked

The divergence does not merely survive; it starts earlier. On 1207954461 the first model-versus-DUT instruction
mismatch moves from cycle 9290.5 to 178.5, about 9100 cycles earlier, and `irq_entry` goes from 258 firings to
5332. Seed 165313640 diverges 101 times on the committed agent and 264,940 times from cycle 111.5 on the ported
one. So the restructured driver is not a candidate for the wedge's cause: it makes the core lose the model almost
immediately.

## What is proved about the build, so a mix-up is ruled out first

The build's filelist names the ported file and that file hashes to `7704b99309910ef5`; the build manifest's
`inputs.sources_sha256` is `a0c0ea3d6714286a` against
`fc6a99f777d55b3d` for BOTH committed-agent builds, with the source count equal at 117 either side. One file's
content differs and it is the ported agent. The overlay went into a private `cp -rL` copy of the mirror behind a
guard refusing any destination under the shared mirror family, and the shared agent still reads
`7f9e7d6cb8b6efa2` after the run.

## Two process facts that bear on reading the numbers

A 20 GB cap was armed on the second run BEFORE it started, because the first had written 1.5 GB and the second
seed is the larger one. It finished at 738 MB, so neither count is taken over a truncated log.

My first reading of seed 165313640 sampled the first 400 KB, saw the grant property in it, and was about to
report that property as firing constantly. It fires four times; the flood is two other counters. Every figure
here is counted over a complete log.

## Retention: the logs are released, and what survives them

tb-infra-2 RELEASED the two run logs in writing at 2026-09-05T14:34Z, after asking for the early-cycle lines it needs to
build a local fixture; its release names ONLY these two logs. rtl-arch separately said it does not need the
divergence window, which is not a release of the re-dump waveforms, and those stay held.

`gen_agentfix_early_cycles.txt` is what survives them: seed 165313640's first 20 real UVM_ERROR lines in file
order, its first 5 grant-property firings with cycles, and seed 1207954461's first 5 `isa_insn` lines, each
carrying its 1-based `sim.log` line number.

IT IS PROVED FAITHFUL, a check possible only while the logs existed: every one of its 25 cited line numbers was
resolved in the file it names and compared against the quoted text, across both sources, ZERO mismatched and
ZERO unresolved. The lines are reproduced in full; an earlier extraction truncated them at 190 characters and
was discarded before it reached this record.

WHAT THE EARLY CYCLES SHOW. On 165313640 the grant property fires at cycles 76 and 101 BEFORE the first
model-versus-DUT mismatch at 111.5, then again at 118 and 132 while the ISA comparison cascades at 138.5 across
four checkers at once. The bus anomaly LEADS the divergence by about 35 cycles, which is consistent with
tb-infra-2's own reading of its source: the driver books and answers a transaction the core was no longer
requesting. On 1207954461 the first five `isa_insn` lines are at cycles 178.5, 179.5, 182.5, 198.5 and 223.5.

THE LOGS ARE STILL IN PLACE AS THIS RECORD LANDS, 1.5 GB and 704 MB, and that is deliberate. They are MOVED,
never removed by an rm on a variable path, to `/proj_soc/user_dev/fzhang/ibex_dv_out/trash/agentfixF_runs_released`, and only AFTER this record is committed: a chain can
refuse, and a record whose logs are already gone cannot be re-verified. So a reader of this page at its commit
can still open either `sim.log` and check every line the excerpt quotes; a reader afterwards has the excerpt and
the trash path.

## Retention

Both run directories are kept untouched at `/proj_soc/user_dev/fzhang/ibex_dv_out/regress_agentfixF/runs/`. tb-infra-2 has not released them.
