# Carry-over of this block to the current generator: the comparison the rule asks for (Test Writer, 2026-09-05)

WHAT THIS IS. gen_fcov_plan.md Section 0 (DV Lead): a generator change carries a block over only when the emitted programs
are byte-identical at the block's seeds AND at its red forms, with the comparison recorded beside the block. Block 2 of this
directory (gen_index.md) measured gen_bit_ratified_prog.py at blob sha256
70f318080711d7845c88341a012461bd21d57695536daf2db33189a675a3b8d0, committed at ba4860b. The generator changed once since,
at 0679715 (the rev58 follow-up: the spelling of one emitted comment's source and the bookkeeping of the no-report op), to
blob b8a99dc827c382587112226e20c62372bd8f85fff8f1ec793e93bade2b686dc4. This file records the comparison between those two
blobs so a reader who follows the carry-over finds it here; the run itself is the retained log
dv/auto_dv/evidence/gen_tdd_logs/test_writer/gen_fu_bit_ratified_carryover.log (md5 f2cd7f15e0ca039a8b1055061bc439e8, 8919 bytes), which folds in its
script (sha256 911851126a771d5ae6330798f602ee7d4ae83c53bc03ea017a958b6561d55ec0). An earlier, smaller comparison (80 green seeds; the red forms at seeds 1, 2, 3 only) is
gen_fu_bit_ratified_rev58.log with its sidecar gen_fu_bit_ratified_rev58_script.md; this one supersedes it in scope.

THE SEEDS COMPARED: the block's forty (gen_pairfix_seeds.txt, listed below) and 1..40.

THE RED FORMS COMPARED: the red fixture of every built item, `plan(seed, red=True, red_item=<item>)`, for TP-BIT-002, 003,
004, 005, 006, 007, 008, 009, 010, 014, 015, 017, 018, 019, 020, 021, 038 and 040 (the generator's BUILT_ITEMS), plus the
green program: 19 forms per seed, 1520 pairs over the 80 seeds.

WHAT IS COMPARED PER PAIR: the full emitted program text (comment lines included), the report word list, k and
min_retired, between the two generators loaded side by side from their own trees.

THE PER-SEED RESULT at the block's forty seeds (pairs identical of 19):
    140681439  19/19  identical
    275115791  19/19  identical
    322097203  19/19  identical
    447188228  19/19  identical
    451705593  19/19  identical
    517903650  19/19  identical
    590501458  19/19  identical
    598009562  19/19  identical
    639215811  19/19  identical
    658118464  19/19  identical
    795121614  19/19  identical
    795121748  19/19  identical
    856721794  19/19  identical
    859927737  19/19  identical
    974310432  19/19  identical
   1013974387  19/19  identical
   1087572542  19/19  identical
   1327152986  19/19  identical
   1349621060  19/19  identical
   1364802963  19/19  identical
   1399741704  19/19  identical
   1470859231  19/19  identical
   1539148183  19/19  identical
   1588369926  19/19  identical
   1620257934  19/19  identical
   1630460430  19/19  identical
   1641265529  19/19  identical
   1650469786  19/19  identical
   1676380956  19/19  identical
   1749035339  19/19  identical
   1777794037  19/19  identical
   1782140117  19/19  identical
   1785273978  19/19  identical
   1793868022  19/19  identical
   1945941221  19/19  identical
   1982825852  19/19  identical
   1986775234  19/19  identical
   2102236322  19/19  identical
   2102415926  19/19  identical
   2107093390  19/19  identical

THE PER-FORM RESULT over the 80 seeds: every form 80 of 80 (green, TP-BIT-002, TP-BIT-003, TP-BIT-004, TP-BIT-005, TP-BIT-006, TP-BIT-007, TP-BIT-008, TP-BIT-009, TP-BIT-010, TP-BIT-014, TP-BIT-015, TP-BIT-017, TP-BIT-018, TP-BIT-019, TP-BIT-020, TP-BIT-021, TP-BIT-038, TP-BIT-040).
WHICH CHANGE COULD HAVE MOVED A DRAW, so a reader knows where to look and need not re-derive it. Of the two changes at
0679715, the comment's source spelling (chr() arithmetic replaced by a plain local spelling the same word, in the emitter
_body) cannot move a draw: it runs after the plan is built and consumes no random value. The bookkeeping of the no-report
op (the plan's _items placing it in an "unreported" list instead of "ops" and "floor", and the test's match rule) is the
half worth naming as checked: it runs inside plan() and could in principle have changed what a later draw saw had it
touched the op stream or the report indices; it touches neither, and the identity at all 1520 pairs is the check of that
claim, not the claim itself. The argument is the reason to expect identity; the log is the evidence.

TOTAL: 1520 of 1520 pairs identical; 0 differ. The block therefore carries over to the current generator at every one of
its seeds and every red form, as the rule requires, and the identity is shown rather than argued: the two changes at
0679715 consume no random draw and reorder none, which is why identity holds at every seed, and the log is the proof of
that expectation at all eighty.
