# Corrigendum beside gen_fu_shape_check.log: what that log's runs did and did not settle (CM229)

WHY A COMPANION. The log is retained and is never reopened, so this file carries the correction and
the log's bytes stay as they were written. Two sentences in it, and one in Section 16 of
gen_tdd_batch3.md, claim more than the evidence supports. The runs themselves are unaffected: the
red still exits 1 at the commit it names and the green still exits 0 on the handed generators.

## 1. The 56 are not 56 bins, and 45 of them are not declared

The log says "56 bins fail at that commit" and groups them in three classes. Counted against the two
committed manifests rather than against the checker's own labels:

  45 of the 56 are `# not_hit <bin>: stimulus: ...` COMMENT lines, not declared bins. Not one of the
     45 appears in either manifest's `bins:` list. They are shapes the manifests record as absent.
  11 of the 56 are declared bins, all of them produced at some seeds and not at every seed.

So the honest sentence is: 11 declared bins and 45 recorded stimulus gaps fail the every-seed bar at
that commit. The checker was reading the manifests' not_hit lines by design, which is stated in its
own docstring; the log's summary line lost that distinction.

## 2. What the simulated sweep graded, and what it therefore cannot settle

The log says "the bins themselves are settled by simulation in the companion retained log
gen_fu_generator_fix_sweep.log, where both entries hit every declared bin at all forty seeds." The
second clause is true and the first does not follow from it. The coverage check grades DECLARED bins:
617 for gen_test_bit_ratified and 300 for gen_test_cmp_zca. The 45 shapes above are not among them,
so no run in that sweep could pass or fail on their account, and the sweep says nothing about them.

The same limit read from the other direction, which is CM229's low row about the sweep's "before":
the pre-fix root's generators were an INTERMEDIATE pair, sha256 7f3ec33390c2 and aaa8e29f7370,
neither the parent commit's blobs (c1580d22a361, 125ef1a1cf5d) nor the handed ones (14405978b07d,
b31555f595b4). Measured line counts of the two directions:

  parent blob -> pre-fix root      bit_ratified +71 -6 (10 of the added are blank), cmp_zca +121 -1 (7 blank)
  pre-fix root -> handed/committed bit_ratified +26 -2 (4 of the added are blank), cmp_zca +10 -0

Added and removed are counted separately, excluding the diff's own `---` and `+++` header lines, with
the blank-line share stated, because "changed lines" reads two ways: a blank added line is a bare `+`
in a unified diff. Non-blank changed lines are 67 and 115 for the first pair and 24 and 10 for the
second, which is the convention the Runtime Manager's index uses, so the two records agree. The
command, so each figure is checkable rather than quoted:

  diff -u <a> <b> | grep -v '^\(---\|+++\)' | grep -c '^+'      # added, blanks included
  diff -u <a> <b> | grep -v '^\(---\|+++\)' | grep -c '^-'      # removed

THE DELTAS THEMSELVES ARE RETAINED, so no reader has to take a count on trust:
gen_generator_sweep/gen_prefix_delta_bit_ratified.diff and gen_prefix_delta_cmp_zca.diff. I applied
each to its pre-fix file myself and got the committed blob back, 14405978b07d and b31555f595b4, which
is the property that makes them the delta and not a description of one.

A CORRECTION TO THIS FILE'S OWN FIRST VERSION, stated rather than quietly fixed: it published 79,
124, 30 and 12 for these four deltas. Those came from `grep -c '^[+-]'`, which counts the diff's two
header lines as changed lines. The Runtime Manager reported 24 and 10 from the bytes, which is what
sent me back to re-derive mine. The conclusion the numbers support is unchanged.

The second delta is the WHOLE of what the before/after sweep measured, and it is exactly the four
later fixes: the value-classifier draw `_plain_rand` with its two call sites and the directed
five-bit cpop spec in gen_bit_ratified_prog.py, and the directed c.swsp register-range unit in
gen_cmp_zca_prog.py. Everything else in the group -- the pack family with its reference lambdas, the
relationship sweep, the binv-twice pair, the compressed-successor clones, the control-transfer unit
and the alignment block -- was ALREADY PRESENT IN BOTH ARMS of the sweep. Those additions are the
ones that serve the 45 shapes, and they were never a variable in it.

## 3. What is therefore owed, and what nothing yet provides

The 46 stimulus-class not_hit lines (24 in gen_test_bit_ratified.fcov.yaml, 22 in
gen_test_cmp_zca.fcov.yaml; 45 measured here, cp_cj_off.self named unmeasurable) still read
"the program never ..." -- 24 of 24 and 21 of 22 of them use that word -- and those sentences are
false for the committed generators. Meanwhile nothing declares the new shapes, so no per-run
guarantee exists for any of them. Both halves close the same way and neither is closed here: when
the wave's 40-seed blocks of the two entries land, the manifests are re-rendered so that the shapes
produced at EVERY seed become declared bins under the every-seed bar, with the coverpoint and cross
halves reported separately, and none of the 46 is credited before that measurement exists.

## 4. What the log's runs do still establish

The model-level claim, unchanged and not weakened: at the commit named in the log the generators do
not produce these shapes at every seed, and with the handed generators every one of them is produced
at every one of forty seeds with each family's control live. That is a statement about emitted
instruction shapes. It was never a statement about coverage bins, and the log now says so here.
