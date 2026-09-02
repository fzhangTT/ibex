# Known follow-ups

Tracked engineering follow-ups called out from `docs/dv/BUILD_AND_SIM.md` and other DV
docs, with no dedicated issue tracker in this repo to hold them instead. Each entry names
the gap and where it was found; remove an entry once it is actually fixed (link the
fixing commit here first).

- **FCIBH `default sequence` workaround is a workaround, not a fix.** VCS's
  `illegal_bins ... = default sequence` half-implementation is worked around by a
  VCS-only `` `ifndef FCOV_NO_DEFAULT_SEQUENCE `` guard (see `BUILD_AND_SIM.md`'s Gotchas
  section, commit `dbba358f`). The real fix — enumerating the controller FSM's legal
  transitions explicitly instead of relying on `default sequence` — is not done. Found:
  WS1 coverage bring-up.
