# The binv-pair fix: the failing block and the passing block, retained

Written 2026-09-05T10:15Z by the Runtime Manager. Two blocks on ONE entry, gen_test_bit_ratified, measuring two
successive versions of the Test Writer's binv-pair fix. Both measure UNCOMMITTED SOURCES and neither is a property
of any commit; each is pinned to the generator's bytes instead.

Both blocks share a root shape, and the sharing is the point: each root is an archive of commit
40175738c709d1151a7d6a448ac46034767b7a09, the WAVE's own pin, with the bit_ratified generator as the ONLY changed
file. That commit was chosen over HEAD deliberately, because HEAD changes `gen_fcov_pkg.sv` and
`gen_fcov_groups.svh`, the sampler package and the covergroup definitions the bins are measured by, which would
have made the comparison against the wave's block two-variable. `env/` is byte-identical to the wave root in both.

Both blocks ran THE WAVE'S OWN FORTY bit_ratified SEEDS, listed in `gen_pairfix_seeds.txt`. The disagreement rule
is a paired comparison and attributes a difference to the generator delta, which only holds on identical seeds.

| file | bytes | sha256 |
|---|---|---|
| `gen_pairfix_red_lines.txt` | 7392 | `1569e57d54b860ed878b9d3a2d7b6944f2543f8d8377c48a280e606afc74e377` |
| `gen_pairfix_census.txt` | 217 | `cfe0f38dfa257d97e834b0cbf588ed7658cd12357afeb06712eff9301d72f657` |
| `gen_pairfix_shapes.txt` | 2407 | `51b0321e4fd2de6c699a41084b39105d3102c505e305abce303d0600738ba624` |
| `gen_pairfix_seeds.txt` | 430 | `a7e1c4b4838d92cf7446aea10c4bc17bc974fb2912c1d14ece1b054b7fc65992` |

## Block 1, pin 557a4812: RED EVIDENCE against the first fix

  generator pin  sha256 557a4812175aa171d16eaf52dc6f5a27ef99ac500da6a56e2427f5e0e7066bd0, recomputed INSIDE the
                 built root after building rather than in the clone
  root           /proj_soc/user_dev/fzhang/ibex_dv_probe/binvfix, tree_sha256 1e88c1a8dc9c
  out            /proj_soc/user_dev/fzhang/ibex_dv_out/regress_binv2

40 runs, 40 FAIL. NOT on coverage: all 617 declared bins were hit in every run with zero unmet. The refusal is the
entry's own fire check, and the per-run line is retained in full in `gen_pairfix_red_lines.txt`, one row per seed.

The signature is identical across all forty: exactly ONE mismatch per run, the mnemonic `binvi` in every run, and
in all forty the value the DUT produced equals the `rs1` the model recorded.

THE FIX DID HIT ITS BIN EVEN SO. In a run's own report `gen_bit_sbit_cg.cp_binv_twice` reads its single bin `yes`
COVERED with count 1, where it reads 0 in every run of the earlier sweep and 0 of 40 in the wave.

THE CAUSE, established by the Test Writer from these numbers and recorded here because a reader of the red rows
will otherwise re-derive it. The model chains correctly. What broke is the REPORT INDEX: the no-report op still
declared an expected value, so every consumer slicing `reports[rep : rep+len(expects)]` read the NEXT op's word,
and the checker compared the first op's expectation against the second op's reported value. Both operands in every
retained line are exactly that. The Runtime Manager's first reading, that the model predicted the pair's second op
from the pre-pair register value, was one level too low and is corrected here.

## Block 2, pin 70f31808: the entry's AUTHORITY

  generator pin  sha256 70f318080711d7845c88341a012461bd21d57695536daf2db33189a675a3b8d0, recomputed INSIDE the
                 built root; supersedes 557a4812
  root           /proj_soc/user_dev/fzhang/ibex_dv_probe/binvfix2, tree_sha256 22593bd323d3
  out            /proj_soc/user_dev/fzhang/ibex_dv_out/regress_binv3

40 runs, 40 PASS. Declared 617, EVERY 617, none under the every-seed bar, and all 494 declared cross legs at every
seed. Per-bin detail in `gen_pairfix_census.txt`.

All 24 stimulus-class shapes at 40 of 40, including `gen_bit_sbit_cg.cp_binv_twice.yes`, which is 0 of 40 in the
wave's block. Full table in `gen_pairfix_shapes.txt`.

## The disagreement rule fires on exactly one shape, and it is the target bin

The rule asks whether any of the 23 carry-over shapes differs between this block and the wave's bit_ratified
block, and attributes a difference to the one-to-three instruction delta the fix introduces.

Twenty-three of the 24 shapes are IDENTICAL between the two blocks, seed count for seed count. The only shape that
differs is `cp_binv_twice.yes` itself, 40 of 40 here against 0 of 40 in the wave, which is the intended change.

So the delta does NOT move bins, and the decision not to re-pin the wave for this fix is now supported by
measurement rather than by argument. Nothing is written up as a finding, because nothing differs except the change
the fix was for.

## The comparison this block's carry-over rests on

Added 2026-09-05T14:14Z on the DV Lead's ruling that the comparison a carry-over rests on lives beside the block.

| file | bytes | sha256 first-12 |
|---|---|---|
| `gen_carryover_comparison.md` | 4778 | `9fad5d2dbde1` |

Written by the Test Writer: the byte comparison of this block's generator (70f31808) against HEAD's
(b8a99dc827c3) over the block's forty seeds and every red form, 1520 of 1520 pairs identical, with the retained
log `gen_tdd_logs/test_writer/gen_fu_bit_ratified_carryover.log` and its script. It is the evidence that this
block's measurements still describe the generator in the tree.
