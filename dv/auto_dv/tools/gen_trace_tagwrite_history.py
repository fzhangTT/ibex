"""gen_trace_tagwrite_history.py <landing root> (<scratch root> | --from-artifact): retain the tag-write history at the
indices where a cache line was valid in both ways at once, and reconstruct the coexistence episodes from it.

The indices come from the retained duplicate-copies artifact rather than a literal, so the filter follows the evidence
rather than a remembered number. With --from-artifact the episode block is re-derived from the raw writes inside the
already-retained artifact, so a reader of the tree can reproduce the reconstruction without the scratch trace session.
Appends or replaces one manifest row."""
import hashlib
import pathlib
import re
import sys
USAGE = "usage: gen_trace_tagwrite_history.py <landing root> (<scratch root> | --from-artifact)"


def _usage(msg=None):
    """A wrong call is answered, not crashed: the tools are read by reviewers who have not seen them before."""
    if msg:
        print(msg)
    print(USAGE)
    sys.exit(2)


# Accept exactly the two forms the usage line describes and nothing else: a trailing argument is refused rather than
# ignored, because an ignored scratch root leaves the caller believing it is being read.
if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help"):
    _usage()
if len(sys.argv) != 3:
    _usage("exactly one of a scratch root or --from-artifact follows the landing root")


ROOT = pathlib.Path(sys.argv[1])
FROM_ARTIFACT = sys.argv[2] == "--from-artifact"   # the mode is the second positional, not a flag found anywhere
# the scratch root is only meaningful when reading the trace session; --from-artifact needs none
S = pathlib.Path(".") if FROM_ARTIFACT else pathlib.Path(sys.argv[2])
L = ROOT / "dv/auto_dv/evidence/gen_tdd_logs"
MAN = L / "gen_manifest.md"
MU = L / "mutations"
SRC = S / "mut_root/TRACE17/out/trace_align_dup/stdout.log"
DUP = MU / "gen_fu_l16_trace17_duplicate_copies.log"
DST = MU / "gen_fu_l16_trace17_tagwrite_history.log"


def die(msg):
    print("REFUSED: " + msg)
    sys.exit(1)


if not DUP.exists():
    die("the duplicate-copies artifact is missing, so the indices cannot be derived: %s" % DUP)

idx = sorted({int(m) for m in re.findall(r"index=(\d+)", DUP.read_text(errors="replace"))})
if not idx:
    die("no index= field in the duplicate-copies artifact")

if FROM_ARTIFACT:
    # Reproduce the reconstruction from the tree alone: the retained artifact already carries every raw write the
    # episode block is derived from. The run's own total cannot be recounted from it, so it is carried forward from
    # the recorded header rather than invented.
    if not DST.exists():
        die("--from-artifact needs the retained artifact to read: %s" % DST)
    prev = DST.read_text(errors="replace").splitlines()
    # filter by the indices derived above rather than trusting that the retained lines match the header: the two agreed
    # only because one filter produced both, so re-applying it makes the mode self-checking
    raw = [l for l in prev if "ICTRACE tagwrite" in l and not l.startswith("#")]
    keep = [l for l in raw if any(re.search(r"index=%d " % i, l) for i in idx)]
    if len(keep) != len(raw):
        n = len(raw) - len(keep)
        die("the retained artifact holds %d tag-write line%s outside the indices %s the duplicate-copies artifact names"
            % (n, "" if n == 1 else "s", idx))
    if not keep:
        die("the retained artifact holds no raw tag-write lines to re-derive from: %s" % DST)
    m = re.search(r"total of (\d+) tag-write lines", "\n".join(l for l in prev if l.startswith("#")))
    if not m:
        die("the retained artifact's header does not record the run's tag-write total")
    tw = [None] * int(m.group(1))
else:
    if not SRC.exists():
        die("the trace run's stdout is gone; re-run with --from-artifact to re-derive from the retained artifact: %s" % SRC)
    lines = SRC.read_text(errors="replace").splitlines()
    tw = [l for l in lines if "ICTRACE tagwrite" in l]
    keep = [l for l in tw if any(re.search(r"index=%d " % i, l) for i in idx)]
if not keep:
    die("no tag-write line at the duplicate indices %s" % idx)

head = [
    "# The tag-write history at the indices where a line was valid in both ways at once, from the landing-15 trace",
    "# session (scratch mut_root/TRACE17, the TRACE displays on the landing build, one-region program prog_icache_ecc).",
    "# WHAT THIS FILE EVIDENCES: that a line was valid in both ways at one index at the same time, and which way's copy",
    "# was added second. Nothing more. Read a way's line as valid=1 until a later write at the same index and way sets",
    "# valid=0.",
    "# WHAT IT DOES NOT EVIDENCE: the cause. That the second copy is allocated after an ECC-correction refetch, because",
    "# each fill captures its way in the IC1 cycle of its own lookup while the correction's invalidation write lands",
    "# later and no comparator compares the captured fill addresses, is DERIVED from rtl/ibex_icache.sv:534-535 and",
    "# :590-592, not measured here. The writes below are CONSISTENT with that account (one way valid=0 before each",
    "# episode, a two-way valid=0 ending it), which is consistency and not causation.",
    "# Indices %s, taken from gen_fu_l16_trace17_duplicate_copies.log rather than hard-coded. %d tag-write lines at"
    % (", ".join(str(i) for i in idx), len(keep)),
    "# those indices. The run's total of %d tag-write lines is counted from the trace session's stdout, which is scratch"
    % len(tw),
    "# and NOT retained, so that total is not checkable from the tree; the %d lines below are." % len(keep),
]
# Reconstruct the valid state per way so the file evidences its own claim instead of asking the reader to replay
# 322 writes: list every interval in which both ways held the same tag valid at one index.
TW = re.compile(r"ICTRACE tagwrite cycle=(\d+) way=(\d+) index=(\d+) valid=(\d) tag=([0-9a-fA-F]+)")
episodes = []
for i in idx:
    state = {0: (0, None), 1: (0, None)}
    start = None
    for l in keep:
        m = TW.match(l)
        if not m or int(m.group(3)) != i:
            continue
        cyc, way, valid, tag = int(m.group(1)), int(m.group(2)), int(m.group(4)), m.group(5)
        state[way] = (valid, tag)
        both = state[0][0] == 1 and state[1][0] == 1 and state[0][1] == state[1][1]
        if both and start is None:
            # the write that completes the coexistence names the way whose copy was added second
            start, start_tag, added = cyc, state[0][1], way
            episodes_added = added
        elif not both and start is not None:
            episodes.append((i, start, cyc, start_tag, episodes_added))
            start = None
    if start is not None:
        episodes.append((i, start, None, start_tag, episodes_added))
per = {}
for i, a, b, tag, added in episodes:
    per[i] = per.get(i, 0) + 1
by_way = {}
for i, a, b, tag, added in episodes:
    by_way[added] = by_way.get(added, 0) + 1
summary = ["#",
           "# Reconstructed from the writes below, by carrying each way's valid bit and tag forward: %d episodes in"
           % len(episodes),
           "# which both ways held the SAME tag valid at one index, %s."
           % ", ".join("%d at index %d" % (per[i], i) for i in sorted(per)),
           "# Each row is the interval from the write that made the second copy valid to the write that ended it, and",
           "# added_way is the way that write names: the copy allocated second, which is the direction of the",
           "# allocation. Across the episodes: %s."
           % ", ".join("%d added into way %d" % (by_way[w], w) for w in sorted(by_way)),
           "# READ THAT AGGREGATE NARROWLY: it is one program at one seed, so it evidences the direction of each",
           "# episode it lists and NOT the way-selection policy. A policy claim needs the RTL selection terms or",
           "# several programs and seeds."]
for i, a, b, tag, added in episodes:
    summary.append("episode index=%d tag=%s added_way=%d both_valid_from_cycle=%d until_cycle=%s"
                   % (i, tag, added, a, b if b is not None else "end_of_run"))
summary.append("#")
summary.append("# The tag writes the reconstruction reads:")
DST.write_text("\n".join(head) + "\n" + "\n".join(summary) + "\n" + "\n".join(l.rstrip()[:300] for l in keep) + "\n")

rel = str(DST.relative_to(ROOT))
size = DST.stat().st_size
h = hashlib.md5(DST.read_bytes()).hexdigest()
desc = ("the tag-write history at the duplicate indices of the trace run: the observational evidence for WP12-F2's "
        "allocation claim")
row = "| %s | %s | %d | %s |" % (rel, desc, size, h)
txt = MAN.read_text().splitlines()
out, replaced = [], 0
for l in txt:
    if l.startswith("| dv/") and l.split("|")[1].strip() == rel:
        out.append(row)
        replaced += 1
    else:
        out.append(l)
if not replaced:
    out.append(row)
MAN.write_text("\n".join(out) + "\n")
print("retained %s (%d bytes, md5 %s); manifest row %s" % (rel, size, h, "replaced" if replaced else "added"))
print("indices %s, %d of %d tag-write lines kept" % (idx, len(keep), len(tw)))
