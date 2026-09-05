# The release was widened, and the requester's account of why this cost a build

Companion to `gen_move_record.md` (committed at 3ff36c4) and to the block's record (85b7bef). Neither is edited;
both are evidence. This file carries two things that were not true or not permitted when they were written.

## The stdout pair is released after all, so one section of the move record is now stale

`gen_move_record.md` has a section headed "What the release did NOT cover, stated rather than inferred", which
records that tb-infra-2's release named two files and two sizes matching the `sim.log` pair exactly, so the
`sim_stdout.log` pair of nearly identical size was left in place and the question put back to its author.

That was true when written. tb-infra-2 then widened the release in writing, in these words: the release covers
the run directories' large output generally, `sim_stdout.log` included, with nothing to be preserved beyond the
excerpt, and any large file appearing there later is to be treated as released too rather than prompting
another question for a name it forgot.

So the stdout pair MOVED at **2026-09-05T14:56:06Z**, by `mv`, to the same trash path, appended as a second line
to `MOVED_UTC.txt` beside the data. Byte counts identical before and after:

| seed | bytes before | bytes after |
|---|---|---|
| `gen_test_irq_basic_165313640` | 1,523,494,036 | 1,523,494,036 |
| `gen_test_irq_basic_1207954461` | 737,993,015 | 737,993,015 |

Both run directories are now 124 KB and hold no file over 50 MB. They keep `result.yaml`, `run_cmd.sh`, the
program directory and the LSF output.

WHAT THE ORIGINAL SECTION GOT RIGHT, and its author said so unprompted: reading the first release narrowly was
the correct reading of what it actually said, and inferring the wider intent would have destroyed 2.2 GB that
had not been released.

## The requester's account of why this cost a build rather than a local run

Quoted verbatim and attributed at its author's request; no gloss of mine is added to it.

tb-infra-2:

> "Six local smokes and an eight-seed comparison both read zero on a driver that writes 4.29 million error lines
> on a real program. That is a measurement about the evidence set, not about the driver: the set could not have
> failed on this defect class, so it never bounded what I claimed it bounded."

The DV Lead has since made the general form a rule, so this block does not carry the point alone: a pre-hand
evidence set for a change to a shared stimulus component or to a checker must include at least one run that
COULD have failed if the change were wrong, and a set that passes on both the committed and the changed
component establishes only that the change is not catastrophic on those shapes.

## What is still held

The re-dump waveforms are covered by no release and remain held for rtl-arch and tb-infra-2.
