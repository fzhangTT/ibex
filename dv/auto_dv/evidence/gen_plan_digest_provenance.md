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

Both commands below are one line each and run as written from the repository root. The function they
reproduce is `_inputs_digest()` in dv/auto_dv/work/dv-lead/gen_build_docs.py, which hashes each input's NAME
before its BYTES, in sorted order, `parts/` before `parts6/`, and then the generator's own file last.

    $ sha256sum dv/auto_dv/work/dv-lead/gen_build_docs.py | cut -c1-16
    48e6d3aa9a1590c5

    $ python3 -c "import hashlib,pathlib; W=pathlib.Path('dv/auto_dv/work/dv-lead'); h=hashlib.sha256(); [(h.update(f.name.encode()), h.update(f.read_bytes())) for f in sorted((W/'parts').glob('*'))+sorted((W/'parts6').glob('*')) if f.is_file()]; print(h.hexdigest()[:12])"
    916cc594a845                                  # the parts alone

    $ python3 -c "import hashlib,pathlib; W=pathlib.Path('dv/auto_dv/work/dv-lead'); h=hashlib.sha256(); [(h.update(f.name.encode()), h.update(f.read_bytes())) for f in sorted((W/'parts').glob('*'))+sorted((W/'parts6').glob('*')) if f.is_file()]; me=(W/'gen_build_docs.py').resolve(); h.update(me.name.encode()); h.update(me.read_bytes()); print(h.hexdigest()[:12])"
    f9a685486369                                  # the parts and then the generator, which is what the
                                                  # header carries today

## What it settles

| commit | inputs digest in the documents | reading |
|---|---|---|
| 4f2b578^ | 916cc594a845 | the last documents committed BEFORE the provenance touch, so a parts-only digest |
| 4f2b578 | 86c54a6a6319 | the provenance touch itself: the generator became an input |
| 66a4f48 | 266624bb25d4 | the rule (b) clarification, a generator edit |
| ef2385a | f9a685486369 | v3.4 and the recording sentence, a generator edit |

The parts-only digest of the tree TODAY is 916cc594a845, which is exactly the digest the documents carried
before the provenance touch. So no part file has changed across any of these touches, and every digest
movement since is the generator's own source, which is what those commit messages said. The parts+generator
digest of the tree today, f9a685486369, is what ef2385a's documents carry, so the tree reproduces the
committed header.

## Why this file exists rather than a sentence in a commit message

The parts, the generator and the digest function are all gitignored, so a reader cannot recompute any of this
from the repository alone; the commands above and the generator's sha are what make the numbers checkable.
A reviewer raised the commit-message version as failing the standard of my own recording rule, and was right.
