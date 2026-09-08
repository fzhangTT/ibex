# The plan set's inputs digest: what it covers, and the run that shows it

Owner: dv-lead. Written 2026-09-05. This record exists because a rule I put in the plan earlier that day says
a comparison is recorded beside the thing it supports and never asserted in a commit message, and a reviewer
found me relying on a number that lived only in a commit message and was computed from gitignored files.

## What the digest covers

The header of gen_fcov_plan.md, gen_test_plan.md and gen_feature_list.md carries an inputs digest so that a
regeneration from unchanged inputs is byte-identical and the header carries provenance rather than a clock.
It is taken over every file in the plan set's `parts/` and `parts6/` directories AND, since the provenance
touch, over the generator's own source, because Section 0's text lives in the generator rather than in a part
file and a digest over the parts alone let two different Section 0 texts share one digest.

## The run

Both commands below are one line each and run as written from the repository root of a tree that carries the
gitignored work directory. The function they reproduce is `_inputs_digest()` in
dv/auto_dv/work/dv-lead/gen_build_docs.py, which hashes each input's NAME before its BYTES, in sorted order,
`parts/` before `parts6/`, and then the generator's own file last. Each command asserts that it found its
inputs, so in a plain checkout, where dv/auto_dv/work/ does not exist, both stop on that assertion. Before the
guard the first command printed e3b0c44298fc there, the sha256 of no input at all, which reads like a digest
that has moved rather than like an absent input; a reviewer running it from a read-only checkout hit exactly
that.

    $ sha256sum dv/auto_dv/work/dv-lead/gen_build_docs.py | cut -c1-16
    4e1bbd44f9c94ba9

    $ python3 -c "import hashlib,pathlib; W=pathlib.Path('dv/auto_dv/work/dv-lead'); fs=[f for f in sorted((W/'parts').glob('*'))+sorted((W/'parts6').glob('*')) if f.is_file()]; assert fs, 'no part files here: dv/auto_dv/work/dv-lead is gitignored and absent from a plain checkout'; h=hashlib.sha256(); [(h.update(f.name.encode()), h.update(f.read_bytes())) for f in fs]; print(h.hexdigest()[:12])"
    96084e1f4714                                  # the parts alone (916cc594a845 before the LOG-100 touch)

    $ python3 -c "import hashlib,pathlib; W=pathlib.Path('dv/auto_dv/work/dv-lead'); fs=[f for f in sorted((W/'parts').glob('*'))+sorted((W/'parts6').glob('*')) if f.is_file()]; me=W/'gen_build_docs.py'; assert fs and me.is_file(), 'no parts or no generator here: dv/auto_dv/work/dv-lead is gitignored and absent from a plain checkout'; h=hashlib.sha256(); [(h.update(f.name.encode()), h.update(f.read_bytes())) for f in fs]; h.update(me.name.encode()); h.update(me.resolve().read_bytes()); print(h.hexdigest()[:12])"
    7a13c5e7344f                                  # the parts and then the generator, which is what the
                                                  # header carries today

## What it settles

| commit | inputs digest in the documents | reading |
|---|---|---|
| 4f2b578^ | 916cc594a845 | the last documents committed BEFORE the provenance touch, so a parts-only digest |
| 4f2b578 | 86c54a6a6319 | the provenance touch itself: the generator became an input |
| 66a4f48 | 266624bb25d4 | the rule (b) clarification, a generator edit |
| ef2385a | f9a685486369 | v3.4 and the recording sentence, a generator edit |
| 9a8d852 | cdb6e3abfe31 | the rev78 answer: the three headers name what the digest covers and point here, and the fcov plan's Section 0 recording rule points here; a generator edit |
| e4aef00 | 18db40ef7371 | the code-comment rule taking its home in gen_test_plan.md Section 0; a generator edit |
| 2f92709 | 9606552cc192 | the comment rule's four cases written out in one entry (rev88); a generator edit |
| the commit carrying this row | 7a13c5e7344f | LOG-100: the functional-coverage gate criterion rewritten to the bin fraction with the witness ledger out of both terms, the equal-weight group score reported beside it, at its five source sites (four in parts6/fcov_xcut.md, two in the generator); the first touch that edits a PART FILE, so the parts-only digest moves to 96084e1f4714 |

The parts-only digest of the tree TODAY is 96084e1f4714. Up to and including the 2f92709 row it was 916cc594a845,
exactly the digest the documents carried before the provenance touch: no part file changed across those
touches, and every digest movement up to that row is the generator's own source, which is what those commit
messages said. The LOG-100 row is the first whose touch edits a part file (parts6/fcov_xcut.md, the
completeness-measure section) as well as the generator, so the parts-only digest moves there for the first
time. The parts+generator digest of the tree today, 7a13c5e7344f, is what the three documents in the commit
carrying this row carry, so the tree reproduces the committed header. The row above it, 9606552cc192, is what
those documents carried at 2f92709, and the movement between the two is this touch's part-file rewrite and
generator edit and nothing else.

## Why this file exists rather than a sentence in a commit message

The parts, the generator and the digest function are all gitignored, so a reader cannot recompute any of this
from the repository alone; the commands above and the generator's sha are what make the numbers checkable.
A reviewer raised the commit-message version as failing the standard of my own recording rule, and was right.
A second review then found the record unreachable from the documents it explains, which is the same fault one
step out: the three headers now name what the digest covers and name this file, Section 0's recording rule
names it, and the round request form names it, so a reader holding any of them can get here.
