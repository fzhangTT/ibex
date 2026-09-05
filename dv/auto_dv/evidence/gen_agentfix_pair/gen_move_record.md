# The released logs: where they went and when

Companion to `gen_index.md`, whose retention paragraph says the two run logs move only after that record is
committed and names the path they move to. This file carries the part that could not be written before the
move: the time it happened and the proof it was a move rather than a loss.

The committed record is 85b7bef. tb-infra-2 released the two logs in writing; its release names ONLY these two
files.

## The move

At **2026-09-05T14:39:50Z**, by `mv` and never by `rm` on a variable path, to
`/proj_soc/user_dev/fzhang/ibex_dv_out/trash/agentfixF_runs_released/`, one directory per seed, with the same
timestamp written beside them in `MOVED_UTC.txt`.

| seed | bytes before | bytes after |
|---|---|---|
| `gen_test_irq_basic_165313640` | 1,523,479,976 | 1,523,479,976 |
| `gen_test_irq_basic_1207954461` | 737,967,946 | 737,967,946 |

The run directories keep their `result.yaml`, `run_cmd.sh`, `program`, LSF output and the rest, and no longer
hold a `sim.log`.

## What the release did NOT cover, stated rather than inferred

Each run also holds a `sim_stdout.log` of essentially the same size, 1,523,494,036 and 737,993,015 bytes. The
release named "both logs, 1.5 GB and 738 MB", figures that match the `sim.log` pair exactly, so it was read as
covering those two files only. The stdout pair is UNTOUCHED and the question is back with its requester. The two
run directories are therefore still 1.5 GB and 704 MB.

## Why the excerpt survives the move intact

`gen_agentfix_early_cycles.txt`, committed with the record, was verified line for line against the `sim.log`
pair BEFORE the move: every one of its 25 cited line numbers resolved in the file it names and matched the
quoted text, zero mismatched and zero unresolved. That check was possible only while those files sat at the
paths the excerpt cites, which is why it was done then and recorded there rather than owed now.

The re-dump waveforms are not covered by any release and remain held for rtl-arch and tb-infra-2.
