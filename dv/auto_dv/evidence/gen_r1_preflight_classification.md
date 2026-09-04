# Round-1 fcov pre-flight: the 24 checked runs classified (Test Writer)

Round-1 evidence. Derived analysis, not a copied run artifact: every figure below is computed
from runtime-2's round-1 fcov pre-flight, whose regression manifest is
/proj_soc/user_dev/fzhang/ibex_dv_out/regress_r1_fcov_preflight/manifest.yaml and whose per-run
sources are the 24 result.yaml and fcov_check.log files under its runs/ directory. The
pre-flight ran the eight tier-full manifest-naming entries at base seed 20260904, coverage on,
head mode pinned to 726682a, no purpose 4, so nothing was indexed.
Classified with scratchpad test_writer_r3/read_unmet.py, which reads the checker's own
per-bin state from each run's fcov_check.log rather than inferring from the unmet count.

## The state is UNHIT, so this is the declaration question and it is mine

Across all 18 failing runs the per-bin state is UNHIT with the keys present: 0
MISSING-FROM-REPORT anywhere. That is the opposite of the earlier isa_alu probe, whose 602
bins were all MISSING-FROM-REPORT and which therefore said nothing about declarations. The
hit counts are high, so these are near-misses and not wholesale failures.

| test | declared | seeds | stable unmet | seed-dependent | union |
| --- | --- | --- | --- | --- | --- |
| gen_test_cmp_zcb | 110 | 3 | 6 | 8 | 14 |
| gen_test_cmp_zcmp_basic | 472 | 3 | 74 | 73 | 147 |
| gen_test_isa_alu | 602 | 3 | 6 | 33 | 39 |
| gen_test_isa_cti | 200 | 3 | 16 | 0 | 16 |
| gen_test_isa_shift | 120 | 3 | 0 | 0 | 0 |
| gen_test_mul_div | 224 | 3 | 19 | 9 | 28 |
| gen_test_mul_mul | 338 | 3 | 0 | 0 | 0 |
| gen_test_rst_boot | 8 | 3 | 2 | 0 | 2 |

Stable means unhit in every seed; seed-dependent means unhit in some seed and hit in another.
Only the stable set can be a declaration or stimulus defect. The seed-dependent set is by
construction an over-declaration: the manifest asserts per run what only the seed decides.

## The systematic cause of the seed-dependent set: auto crosses

The plan declares 110 crosses as `bins auto{all combinations}`, and those account for most
declarations in the affected manifests:

| manifest | declarations on an auto cross | of total |
| --- | --- | --- |
| gen_test_cmp_zcb | 70 | 110 |
| gen_test_cmp_zcmp_basic | 382 | 472 |
| gen_test_isa_alu | 455 | 602 |
| gen_test_isa_cti | 140 | 200 |
| gen_test_isa_shift | 81 | 120 |
| gen_test_mul_div | 160 | 224 |
| gen_test_mul_mul | 287 | 338 |
| gen_test_rst_boot | 0 | 8 |

An auto cross enumerates a full product (cp_insn x cp_rlist x cp_spimm, for one). Declaring
every combination as a per-run expectation asserts that one run drives the whole product,
which no single run guarantees. That is a real defect in the per-run semantics and it is mine
to fix.

CORRECTION, from runtime-2 and then measured: this mechanism explains the SEED-DEPENDENT set
only. It does NOT explain why these six fail, and I had extended it to the stable core, which
was wrong. Two counterexamples settle it. gen_test_mul_mul is the most auto-cross-heavy
manifest of the eight, 287 of 338 declarations and a single 245-bin auto cross, the largest
product in the set, and it PASSES at all three seeds. gen_test_rst_boot has ZERO auto-cross
declarations and FAILS, on two plain coverpoint boundary values. I tested both formulations:
neither the share of declarations on auto crosses nor the size of the largest single auto cross
separates pass from fail (passing sizes 36 and 245 against failing sizes 0, 30, 40, 66, 98 and
192). So auto crosses are what make a manifest fragile to the seed, not what makes these six
fail. The stable core is stimulus reach, test by test, which is what the per-test causes below
actually record.

## The stable unmet sets, by root cause

123 stable bins across six tests reduce to a small number of causes.

### gen_test_cmp_zcb, 6 stable

ONE cause, and it confirms the component rule. `cp_alu_operand.rand` is itself stable-unhit, and all five stable cross bins are its `_rand` combinations. `rand{default}` is a catch-all that fires only when the operand matches no named class, and the program always uses named values, so the default never fires and the crosses above it drop. Declaring a `default` bin as a per-run expectation is a declaration defect, not a stimulus gap.

### gen_test_isa_cti, 16 stable

TWO causes. Twelve bins are compressed branches never emitted (cp_op.c_beqz/c_bnez plus their cr_op_align and cr_op_taken_cmp combinations); four are `jalr` with rs1 = x0 never emitted (cp_jalr_rs1.x0 plus three cr_jalr_rs1_imm crosses). Both are stimulus gaps in the program generator, each one root cause rather than many bins.

### gen_test_mul_div, 19 stable

THREE causes. Nine are data-independent timing never enabled (cp_dit.on plus the eight cr_op_div0 `*_on` crosses that depend on it); eight are divide-by-zero with dividend classes the program never produces; two are `c.mul` never emitted. Again the crosses fail because a component does.

### gen_test_isa_alu, 6 stable

Ordering gaps, not unreachable bins. All six are cr_writer_read combinations. I checked the plan rather than assuming: cp_x0_read samples the NEXT retirement, so `jal_rs1_zero` means a jal wrote rd and the following instruction read x0 through rs1. That is reachable, so my first reading that jal has no rs1 and the bin is impossible was wrong. The program simply never places those writer classes immediately before an x0 read.

### gen_test_rst_boot, 2 stable

Two boundary values never driven: cp_boot_addr.zero and cp_bit8_readback.zero. Needs an owner decision on whether a zero boot address is drivable at all in this TB; if it is not, these are unreachable declarations to prune rather than stimulus to add.

### gen_test_cmp_zcmp_basic, 74 stable

Dominated by one auto cross: 57 of the 74 are cr_insn_rlist_spimm combinations, the full insn x rlist x spimm product. The rest are hazard-window and alignment combinations. The 57 are the clearest case of the auto-cross over-declaration above.

## What I propose, for the post-round re-scope

1. Auto crosses come out of the per-run declared set and are asserted at the merged level
   instead, where the product can actually be covered. That addresses the seed-dependent set.
   It does NOT close the stable core, including cmp_zcmp_basic's 57: those bins are stable
   because the stimulus never reaches those rlist and spimm combinations, not because the
   product is large. Moving them to the merged level stops them failing a run; it does not
   make them covered, and the round record should say so rather than counting them closed.
2. `default` bins (the `rand` catch-all) are never declared per run. A default that the
   stimulus deliberately avoids cannot be an expectation.
3. A cross bin is never declared when its component bin is not: the component decides, per
   the renderer's one-sample-per-coverpoint rule.
4. The remaining stable bins are genuine stimulus asks, and they are few: compressed
   branches and c.mul, jalr with rs1 = x0, data-independent timing on, divide-by-zero
   dividend classes, and the writer-then-x0-read orderings.
5. rst_boot's two boundary values need an owner ruling on drivability before I either add
   stimulus or prune the declaration.

Nothing here is a tree edit. The re-scope itself waits for the round record and the round HEAD.
