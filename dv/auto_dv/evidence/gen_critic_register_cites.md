# Critic verdict: the TB defect register touch and its citation check, 6982953..398727a (DV Lead)

Artifacts at 398727a: dv/auto_dv/evidence/gen_tb_defects.md (T9 closed at ac2d306, T10 new, every citation pinned to the commit it was
read at) and dv/auto_dv/tools/gen_register_cites.py (the check, both ways). Date 2026-09-05. Role: Critic. Method: the tool run in a
detached worktree of 398727a (it resolves commits, so a plain archive is refused), from the clone root, at the register's pin and at
older pins, against the pre-touch register as committed at 3990916, against copies with a fabricated stale citation and with an
appended prose citation, and in an archive with an empty git init; the register's rows read against the records they cite; findings
fixed before rev86 (dv/auto_dv/work/critic/register/draft_prerev86.txt), rev86 then read and its rows checked on the tree.
Exposure: the Orchestrator's messages summarised the touch and rev86's shape before the reconciliation. Logs:
dv/auto_dv/work/critic/register/preread_398727a.txt.

CRITIC VERDICT: REQUEST-CHANGES, confined to M-1 (T8's Fixed cell contradicts T9's account of where the fix landed).

## 1. The tool, exercised

58 citations checked at the pin 398727a, PASS, from the clone root; the message's reds reproduce from committed blobs: the register as
committed one commit earlier (3990916) checked at the same pin fails with 7 UNCHECKED citations (T4's gen_fcov_pkg.sv:2108, :2110,
:2112, T5's gen_checkers_pkg.sv:399, T6's ibex_cs_registers.sv:512, :452, :2912), the "seven"; the new register pinned at c1239af or
ac2d306 fails with 9 unresolved, the "nine"; pinned at 9a8d852 it passes, no cited file having moved since. A fabricated stale citation
inside a row (gen_checkers_pkg.sv:9999) fails as UNCHECKED. A plain archive without .git is refused with exit 2 and the message the
docstring promises.

## 2. The register's rows against the records

T9 closes at ac2d306 with the sum-form arithmetic my counters Sections 8 and 9 read, and its row says my Section 8 REQUEST-CHANGES was a
build-identity row lifted by Section 9, which is accurate. T10, the driver's phantom grant, cites the committed pair record and the gated
shape as the repair, consistent with rtl-arch's Section 12, which I read and whose RTL and doc cites hold. The pinned-citation
convention is right and the tool is its enforcement.

- M-1 (Medium, records; DV Lead): T8's Fixed cell reads "FIXED at c045115 (landing 53)" while T9's row says the c045115 form saturated
  the SUM and kept the one-low offset that landing 58 removed, and names ac2d306 as the fix with the decrement form at gen_bus_if.sv:42.
  The two rows of one record disagree on where T8's counters were fixed, and the register's own arithmetic says c045115 was not it.
  rev86 found this; I verified it on both cells and had not read T8 myself.

## 3. The tool's own evidence

- L-1 (Low, tool; DV Lead): the reverse direction reads only the table rows (lines starting "| T"); a file:line citation in the record's
  prose outside the rows is not scanned, and a well-formed backticked dv/auto_dv/tb/gen_dut_top.sv:51 appended to a copy passed
  unexamined, against the docstring's "every file:line the register cites must appear in the table". Every citation lives in a row
  today, so the hole is latent; the docstring should state the row scope or the scan cover the whole record.
- L-2 (Low, evidence; DV Lead): the tool has no self-test, nothing in the tree invokes it, and its red (the seven and the nine) is stated
  in the commit message without a retained transcript; both reproduce from committed blobs as Section 1 shows, so the basis exists in
  git, and a self-test case that perturbs a citation, or a retained run, is what the trust triad asks of a new checker. rev86's Low on
  the absent invocation is this row.
- L-3 (Low, records; DV Lead), rev86's, VERIFIED: the commit message says the tool "refuses with exit 2 where it cannot resolve
  commits"; an archive with an empty git init exits 1 with "58 unresolved" and "matches 0 tracked files", so exit 2 is the no-checkout
  case only, as the docstring correctly says.
- L-4 (Low, tool; DV Lead), rev86's, agreed: on a pass the tool prints one summary line and no per-citation result, so a green run cannot
  be audited without the table.
- L-5 (Low, records; DV Lead), rev86's, VERIFIED on my own run: the commit message says the failing run "prints what three of those
  lines read now"; the committed tool prints seven UNCHECKED lines and no line contents, so that transcript is not the committed tool's
  output and is not retained.
- rev86's Infos (the token regex binds a bare :NNN to the last .sv or .py path across an intervening other-type mention; basename
  resolution uses the checkout's git ls-files rather than the citing commit's tree) are fair design notes, not rows.

## 4. Conformance

DV modifies no RTL. The register's rows are records; the tool is a checker of records and carries no measurement claim of its own
beyond the resolution of citations, which I reproduced. ASCII in both files.

## 5. Reconciliation with rev86

rev86 (dv/auto_dv/reviews/2026-09-05-claude-diff-69829539-398727ab.md at 7cdad7c, fdf5cf820b13ee73) on 6982953..398727a, read after
Sections 1 to 3's findings were fixed. Its verification matches mine (58 at the pin, the seven and the nine, the exit-2 refusal, the
parser's 58 tokens, T9's arithmetic, T10 against the pair record). Its Medium is M-1, found by it, verified by me and adopted; its Lows
are L-2 to L-5 above; L-1 is mine and not in its list. Verdict as stated: REQUEST-CHANGES confined to M-1; the tool itself and the
citation convention are approved as they stand, and the lift is the DV Lead's touch correcting T8's cell.

## 6. The T8 touch at b5f499e, 398727a..b5f499e: M-1 closed, the tool gains its self-test; REQUEST-CHANGES lifted (2026-09-05T18:48:42Z; Sections 1-5 unchanged)

Artifacts at b5f499e: gen_tb_defects.md (the T8 cell), gen_register_cites.py (150 lines changed); no review of b5f499e exists at HEAD, so none is read here. Method: a detached worktree of
b5f499e: the tool with no argument (the pin read from the record's header), --verbose, --self-test, the prose-citation probe of Section 3
repeated, and an archive with an empty git init for the refusal; the T8 cell read against the blobs Sections 8 and 9 of the counters
record already read; findings fixed before any review of b5f499e (register/preread_b5f499e.txt).

- M-1 CLOSED: T8's cell now reads "FIXED IN TWO STEPS" and names both commits with their arithmetic, c045115's sum-qualified form at
  gen_protocol_props.sv:133 and :135 (the form T9 calls defective, the one-low offset kept) and ac2d306's decrement gated on a positive
  count at :135-138, and says why both are named; that is what the blobs say and what the counters record's Sections 8 and 9 read. The
  four new table entries pin those lines at their commits and the tool resolves them (62 citations checked at the pin, PASS).
- L-2 CLOSED for the self-test: --self-test passes four cases (the table resolves at the pin; a moved line fails through the resolution
  half; a citation the table does not carry fails through the coverage half; an absent pin is refused and reported as the pin, not as bad
  citations). Nothing in the tree invokes the tool as a gate yet; the tool now takes no argument so a gate can, and the invocation is the
  DV Lead's next step, not a row here.
- L-3 CLOSED: an archive with an empty git init refuses with exit 2 and names the commits it cannot carry, "unchecked rather than wrong".
  L-4 CLOSED: --verbose prints one line per citation, 62 of them. L-5 answered: the commit message states that the three "reads now"
  lines came from the verify script's own git show, not from the tool, which is what my run of the shipped tool showed.
- L-1 OPEN: the reverse scan still reads the table rows; the same well-formed prose citation appended to a copy passes unexamined
  (62 checked, PASS). Owed as before.
- L-6 (Low, records; DV Lead): the header (:21) reads "every other citation was read at 398727a, the record's own last commit"; after
  this touch the record's last commit is b5f499e, so the clause is false by one commit while the pin itself stays right (no cited file
  moved). Say "read at 398727a" and drop the clause, or let the tool's self-test pin the header's commit against git log.
- The T8 entries pin per commit in-row, so the header pin is untouched, as the convention intends.

A reconciliation follows as a further line if a review of b5f499e lands and the Orchestrator asks for one.

CRITIC VERDICT: APPROVE on 398727a..b5f499e. The REQUEST-CHANGES of this file's opening verdict, confined to M-1, is LIFTED; L-1 and L-6 are owed
to the DV Lead's next touch of the register or the tool.
