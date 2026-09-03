#!/usr/bin/env bash
# ci/make-cleanroom.sh [--force] [DEST]  (default DEST: ../ibex-cleanroom)
#
# Build the Zone A knowledge-fence cleanroom export: git-archive HEAD, delete every
# denied path (default-deny dv/** and docs/dv/**, plain-deny everything else on the
# list), fetch a pristine upstream copy of vendor/google_riscv-dv, overlay the Zone A
# variants, verify the result, then commit it as a fresh single-commit git repo at
# DEST. Exits nonzero on any verify failure -- DEST is never written unless the
# export passes every check.
#
# Env:
#   CLEANROOM_CANARY=deny|artifact|mcp|identifier
#                            plant one named violation into the staged tree before
#                            verifying, to prove the corresponding check actually
#                            fires (anti-vacuity; selftest use).
#   CLEANROOM_PRE_OVERLAY=1  ci/cleanroom-overlay/ is not required to exist yet.
#                            Skips the checks that only make sense once it has
#                            landed: the item-9 scan, the whole-export identifier
#                            scan, NO-REMOTE-MCP, and the exported validator run.
#
# This file is also sourced by ci/cleanroom-selftest.sh to reuse the DENY/ALLOW
# arrays and the cleanroom_* functions below; sourcing (as opposed to direct
# execution) does not run main.
set -euo pipefail
shopt -s nullglob

err() { echo "ERROR: $*" >&2; }
die() { err "$*"; exit 1; }

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OVERLAY_DIR="$REPO_ROOT/ci/cleanroom-overlay"
INVENTORY_FILE="$REPO_ROOT/ci/cleanroom-inventory.txt"

# --- default-deny-with-allowlist roots (handled specially; see the amendment's
# fence-line triage and the WS7 plan pre-review, "INVERT TO DEFAULT-DENY"). ---
ALLOW=(
  "dv/auto_dv"          # dv/**: the sole allowlisted subtree
)
DOCS_DV_ALLOWED=("FENCE.md" "SIM_RECIPE.md" "TB_CONTRACT.md" "dv_principles.md")  # docs/dv/**: supplied by the overlay

# --- plain deny list: paths that must never exist in the export, no exceptions. ---
# One entry per row of docs/superpowers/specs/2026-09-02-zone-a-fence-scope-amendment.md
# (dv/** and docs/dv/** moved out of this array -- see ALLOW / DOCS_DV_ALLOWED above);
# each comment is that row's "why". Entries may be a literal path or a shell glob.
DENY=(
  "formal"                                       # repo-root Ibex formal proofs: icache, data-independent timing (under-fenced; amendment triage)
  "vendor/riscv?isa?sim*"                        # DV_prompt Section 12 precondition-6 pattern: the fork dir, plus the underscore-named lock/vendor-description siblings that a plain directory match misses
  "vendor/patches"                                # patches applied for the existing flow
  "docs/superpowers"                              # planning/spec history for the existing DV workstreams
  "ci/jenkins"                                    # names existing tests/testlists, drives the existing flow
  "ci/build-spike.sh"                             # builds the Zone B spike cosim referee (discloses it exists and how)
  "ci/setup-cosim.sh"                              # sets up the Zone B cosim
  "ci/run-cosim-test.sh"                          # exercises the Zone B cosim
  "ci/reviews/fence-integrity.md"                 # Zone B / evaluator-only rubric
  "ci/reviews/test-overlap.md"                    # Zone B / evaluator-only rubric
  "doc/01_overview/verification_overview.rst"     # verification RST 1/6: describes existing DV
  "doc/03_reference/cosim.rst"                    # verification RST 2/6: describes existing cosim
  "doc/03_reference/coverage_plan.rst"            # verification RST 3/6: describes existing coverage plan
  "doc/03_reference/testplan.rst"                 # verification RST 4/6: describes existing testplan
  "doc/03_reference/verification.rst"             # verification RST 5/6: describes existing verification
  "doc/03_reference/verification_stages.rst"      # verification RST 6/6: describes existing verification stages
  "doc/03_reference/images/tb*.svg"               # existing TB diagrams
  ".mex/"                                          # full-tree mex graph/wiki; WS6 is full-tree only, may embed fenced content
  ".github"                                        # Zone B CI: re-discloses cosim build/run + directed test names (workflows/actions); Zone A owns its own regression scripts
)

# DV_prompt.txt Section 12 item 9: exact string set, scoped to its exact file list.
ITEM9_FILES=(
  ".claude/skills" ".claude/agents" "ci/env.sh" "ci/mcp" "ci/reviews"
  "CLAUDE.md" "AGENTS.md" ".codex/config.toml"
  "docs/dv/TB_CONTRACT.md" "docs/dv/SIM_RECIPE.md"
)
ITEM9_STRINGS=(
  "dv/uvm/core_ibex" "core_ibex" "BUILD_AND_SIM.md" "COSIM.md" "disable_cosim"
  "FCOV_NO_DEFAULT_SEQUENCE" "metadata.pickle" "docs/dv/reviews/"
  "ci/reviews/test-overlap" "ci/reviews/fence-integrity"
)

# Fixed probe set for the whole-export identifier scan: only strings that must never
# appear anywhere, at all (deliberately excludes disable_cosim -- dv_principles.md
# legitimately carries the Zone A operationalization sentence near it; item 9 above is
# the right scope for that one).
WHOLE_EXPORT_IDENTIFIERS=(
  "core_ibex" "riscv_arithmetic_basic_test" "mcounteren_test" "spike_cosim"
)

# ---- shared check functions; reused by ci/cleanroom-selftest.sh --------------------

# (b) DENY-LIST ABSENCE: the plain-deny list is fully gone, and dv/**, docs/dv/**
# hold nothing beyond their allowlisted remainder.
cleanroom_check_deny_absence() {  # <export-root>
  local root="$1" entry target bad=0

  for entry in "${DENY[@]}"; do
    for target in "$root"/$entry; do
      if [ -e "$target" ]; then
        err "deny-list item present in export: $entry (at $target)"
        bad=1
      fi
    done
  done

  if [ -d "$root/dv" ]; then
    local leftover
    leftover="$(find "$root/dv" -mindepth 1 -maxdepth 1 ! -name auto_dv 2>/dev/null || true)"
    if [ -n "$leftover" ]; then
      err "dv/ has content beyond the dv/auto_dv/ allowlist:"
      echo "$leftover" | sed 's/^/  /' >&2
      bad=1
    fi
  fi

  if [ -d "$root/docs/dv" ]; then
    local f base leftover2=()
    while IFS= read -r -d '' f; do
      base="$(basename "$f")"
      case "$base" in
        FENCE.md|SIM_RECIPE.md|TB_CONTRACT.md|dv_principles.md) ;;
        *) leftover2+=("$f") ;;
      esac
    done < <(find "$root/docs/dv" -mindepth 1 -maxdepth 1 -print0 2>/dev/null)
    if [ "${#leftover2[@]}" -gt 0 ]; then
      err "docs/dv/ has content beyond the Zone A set (${DOCS_DV_ALLOWED[*]}):"
      printf '  %s\n' "${leftover2[@]}" >&2
      bad=1
    fi
  fi

  if [ -d "$root/docs" ]; then
    local leftover3
    leftover3="$(find "$root/docs" -mindepth 1 -maxdepth 1 ! -name dv 2>/dev/null || true)"
    if [ -n "$leftover3" ]; then
      err "docs/ has content beyond docs/dv/:"
      echo "$leftover3" | sed 's/^/  /' >&2
      bad=1
    fi
  fi

  return "$bad"
}

# (c) ARTIFACT ABSENCE: no simulator/coverage run artifacts.
cleanroom_check_artifact_absence() {  # <export-root>
  local root="$1" hits
  hits="$(find "$root" \( -name '*.fsdb' -o -name '*.vdb' -o -name '*.daidir' \) 2>/dev/null || true)"
  if [ -n "$hits" ]; then
    err "run artifact present in export:"
    echo "$hits" | sed 's/^/  /' >&2
    return 1
  fi
  return 0
}

# INVENTORY TRIPWIRE: every top-level path in the export must be a known, triaged
# name (ci/cleanroom-inventory.txt). Converts allow-by-default to triage-on-add for
# anything added to the repo root that no deny/allow/overlay rule has classified yet
# (spec:139's unclassifiable-path property, at top-level granularity).
cleanroom_check_inventory() {  # <export-root>
  local root="$1"
  if [ ! -f "$INVENTORY_FILE" ]; then
    err "ci/cleanroom-inventory.txt is missing; cannot run the inventory tripwire"
    return 1
  fi
  local unexpected
  unexpected="$(comm -23 \
    <(ls -A "$root" | grep -v '^\.git$' | sort) \
    <(grep -v '^#' "$INVENTORY_FILE" | grep -v '^[[:space:]]*$' | sort) || true)"
  if [ -n "$unexpected" ]; then
    err "export has top-level path(s) not in ci/cleanroom-inventory.txt (triage required):"
    echo "$unexpected" | sed 's/^/  /' >&2
    return 1
  fi
  return 0
}

# DV_prompt Section 12 precondition 9: ci/reviews/ is a positive list of exactly six
# files. Runs unconditionally (true pre- and post-overlay: the plain-deny of the two
# Zone B rubrics already yields this set before Task 2 lands).
cleanroom_check_reviews_set() {  # <export-root>
  local root="$1"
  local want=("GUIDE.md" "ai-slop-comments.md" "rtl-purity.md" "magic-numbers.md" "forces-and-hier-access.md" "assertion-integrity.md")
  if [ ! -d "$root/ci/reviews" ]; then
    err "export is missing ci/reviews/"
    return 1
  fi
  local got expect
  got="$(ls -A "$root/ci/reviews" | sort)"
  expect="$(printf '%s\n' "${want[@]}" | sort)"
  if [ "$got" != "$expect" ]; then
    err "ci/reviews/ is not exactly the six-file Zone A set:"
    err "  got:    $(tr '\n' ' ' <<< "$got")"
    err "  expect: $(tr '\n' ' ' <<< "$expect")"
    return 1
  fi
  return 0
}

# (d1) DV_prompt Section 12 item 9: exact strings, scoped to its exact file list.
cleanroom_check_item9_scan() {  # <export-root>
  local root="$1" bad=0 f existing=() s hits
  for f in "${ITEM9_FILES[@]}"; do
    [ -e "$root/$f" ] && existing+=("$root/$f")
  done
  if [ "${#existing[@]}" -eq 0 ]; then
    return 0
  fi
  for s in "${ITEM9_STRINGS[@]}"; do
    hits="$(grep -rIFl -- "$s" "${existing[@]}" 2>/dev/null || true)"
    if [ -n "$hits" ]; then
      err "item-9 string '$s' present in scanned file(s):"
      echo "$hits" | sed 's/^/  /' >&2
      bad=1
    fi
  done
  return "$bad"
}

# (d2) whole-export scan for the unconditionally-forbidden identifiers.
cleanroom_check_whole_export_identifiers() {  # <export-root>
  local root="$1" bad=0 id hits
  for id in "${WHOLE_EXPORT_IDENTIFIERS[@]}"; do
    hits="$(grep -rIFl -- "$id" "$root" 2>/dev/null || true)"
    if [ -n "$hits" ]; then
      err "fenced identifier '$id' present in export:"
      echo "$hits" | sed 's/^/  /' >&2
      bad=1
    fi
  done
  return "$bad"
}

# (e) NO REMOTE MCP: the export's client configs list exactly the three local
# servers and no remote (http/url) entries.
cleanroom_check_no_remote_mcp() {  # <export-root>
  local root="$1" bad=0
  local expect='["fsdb-mcp-server","siliconpilot","verdi-cov-mcp"]'
  if [ ! -f "$root/.mcp.json" ]; then
    err "export is missing .mcp.json"
    return 1
  fi
  local got
  got="$(jq -cS '(.mcpServers // {}) | keys' "$root/.mcp.json" 2>/dev/null || true)"
  if [ -z "$got" ]; then
    err ".mcp.json in export is not valid JSON"
    bad=1
  elif [ "$got" != "$expect" ]; then
    err ".mcp.json server list is $got, expected exactly $expect"
    bad=1
  fi
  if jq -e '(.mcpServers // {}) | to_entries[] | select(.value.type == "http" or (.value.url? != null))' \
      "$root/.mcp.json" >/dev/null 2>&1; then
    err ".mcp.json has a remote (http/url) MCP server entry"
    bad=1
  fi
  if [ ! -f "$root/.codex/config.toml" ]; then
    err "export is missing .codex/config.toml"
    return 1
  fi
  if grep -qE '(^|[^_])\burl\s*=|type\s*=\s*"http"' "$root/.codex/config.toml"; then
    err ".codex/config.toml has a remote (url/http) MCP server entry"
    bad=1
  fi
  local n
  n="$(grep -cE '^\[mcp_servers\.' "$root/.codex/config.toml" || true)"
  if [ "$n" -ne 3 ]; then
    err ".codex/config.toml lists $n mcp_servers sections, expected exactly 3"
    bad=1
  fi
  return "$bad"
}

# (h) the export's own validator (Task 2 ships a Zone A variant) proves the exported
# tree is internally self-consistent.
cleanroom_check_validator() {  # <export-root>
  local root="$1" v="$1/.codex/compat/validator.py"
  if [ ! -f "$v" ]; then
    echo "NOTE: $v absent from export; skipping the validator self-consistency check."
    return 0
  fi
  if ! command -v python3 >/dev/null 2>&1; then
    err "python3 not found on PATH; cannot run the exported validator"
    return 1
  fi
  if ! python3 "$v" --repo-root "$root"; then
    err "the export's own .codex/compat/validator.py reports the exported tree is inconsistent (see above)"
    return 1
  fi
  return 0
}

# ---- build ---------------------------------------------------------------------

# Fetch a pristine upstream copy of vendor/google_riscv-dv at the locked rev and place
# it into the stage, replacing whatever git-archive shipped (the checked-in tree
# carries local patches -- see the amendment review C3 -- so "pristine" here means
# fetched fresh, not verified-in-place). Retains vendor/google_riscv-dv.lock.hjson
# (never touched -- it is the DV_prompt Section 12 precondition-6 anchor); deletes
# vendor/google_riscv-dv.vendor.hjson (discloses patch_dir).
_cleanroom_place_riscvdv() {  # <stage>
  local stage="$1"
  local lock="$REPO_ROOT/vendor/google_riscv-dv.lock.hjson"
  [ -f "$lock" ] || { err "vendor/google_riscv-dv.lock.hjson missing from source tree"; return 1; }

  local rev url
  rev="$(sed -n 's/^[[:space:]]*rev:[[:space:]]*\([0-9a-fA-F]\{40\}\).*/\1/p' "$lock" | head -1)"
  url="$(sed -n 's#^[[:space:]]*url:[[:space:]]*\(https\?://[^[:space:]]*\).*#\1#p' "$lock" | head -1)"
  if [ -z "$rev" ] || [ -z "$url" ]; then
    err "could not parse rev/url out of vendor/google_riscv-dv.lock.hjson"
    return 1
  fi

  local cache="${TMPDIR:-/tmp}/ibex-cleanroom-riscvdv-cache/$rev"
  if [ ! -d "$cache" ]; then
    local tmp ok
    tmp="$(mktemp -d "${TMPDIR:-/tmp}/ibex-cleanroom-riscvdv.XXXXXX")" || { err "mktemp failed"; return 1; }
    echo "Fetching pristine upstream riscv-dv ($url @ $rev) ..."
    if (
      cd "$tmp" \
        && git init -q \
        && git remote add origin "$url" \
        && timeout 300 git fetch -q --depth 1 origin "$rev" \
        && git checkout -q FETCH_HEAD -- . \
        && git diff --quiet FETCH_HEAD -- .
    ); then ok=1; else ok=0; fi
    if [ "$ok" -ne 1 ]; then
      err "BLOCKED: could not fetch/verify pristine upstream riscv-dv at $rev from $url."
      err "Owner must decide: retry the fetch, or omit vendor/google_riscv-dv from the export (amendment change-5 deviation)."
      rm -rf "$tmp"
      return 1
    fi
    rm -rf "$tmp/.git"
    mkdir -p "$(dirname "$cache")"
    mv "$tmp" "$cache"
  fi

  rm -rf "$stage/vendor/google_riscv-dv"
  mkdir -p "$stage/vendor"
  cp -a "$cache" "$stage/vendor/google_riscv-dv"
  rm -f "$stage/vendor/google_riscv-dv.vendor.hjson"
}

_cleanroom_apply_deny_with_allow() {  # <stage>
  local stage="$1" entry target a

  local allow_tmp
  allow_tmp="$(mktemp -d "${TMPDIR:-/tmp}/ibex-cleanroom-allow.XXXXXX")" || { err "mktemp failed"; return 1; }
  for a in "${ALLOW[@]}"; do
    if [ -e "$stage/$a" ]; then
      mkdir -p "$allow_tmp/$(dirname "$a")"
      mv "$stage/$a" "$allow_tmp/$a"
    fi
  done

  rm -rf "$stage/dv" "$stage/docs/dv"

  for a in "${ALLOW[@]}"; do
    if [ -e "$allow_tmp/$a" ]; then
      mkdir -p "$stage/$(dirname "$a")"
      mv "$allow_tmp/$a" "$stage/$a"
    fi
  done
  rm -rf "$allow_tmp"

  for entry in "${DENY[@]}"; do
    for target in "$stage"/$entry; do
      rm -rf -- "$target"
    done
  done
}

# Apply the overlay onto the stage. File-wise copy (not a directory-level replace),
# so a skill/doc the overlay only partly rewrites keeps the full-tree files it did not
# touch (e.g. the simple-english skill variant inherits its references/ subdir).
# ci/reviews/ is the one deliberate exception: it is a positive list of exactly six
# files (DV_prompt Section 12 precondition 9), so it is a directory replace -- a new
# full-tree rubric nobody thought to add to DENY must never survive next to it.
_cleanroom_apply_overlay() {  # <stage>
  local stage="$1"

  if [ -d "$OVERLAY_DIR/ci/reviews" ]; then
    rm -rf "$stage/ci/reviews"
    mkdir -p "$stage/ci"
    cp -a "$OVERLAY_DIR/ci/reviews" "$stage/ci/reviews"
  fi

  local f rel dest
  while IFS= read -r -d '' f; do
    rel="${f#"$OVERLAY_DIR"/}"
    case "$rel" in
      ci/reviews/*) continue ;;
    esac
    dest="$stage/$rel"
    mkdir -p "$(dirname "$dest")"
    cp -a "$f" "$dest"
  done < <(find "$OVERLAY_DIR" -type f -print0)
}

# Build the staged export tree at <stage-dir>: archive HEAD, apply the default-deny +
# allowlist, place pristine riscv-dv, overlay the Zone A variants, and (if requested)
# plant one named anti-vacuity canary. Shared with the selftest so both tools build
# the export the same way.
cleanroom_build_stage() {  # <stage-dir> <canary-mode: ""|deny|artifact|mcp|identifier>
  local stage="$1" canary="${2:-}"

  git -C "$REPO_ROOT" archive --format=tar HEAD | tar -x -C "$stage" \
    || die "git archive/tar extraction failed"

  _cleanroom_apply_deny_with_allow "$stage" || return 1
  _cleanroom_place_riscvdv "$stage" || return 1

  if [ -d "$OVERLAY_DIR" ]; then
    _cleanroom_apply_overlay "$stage" || die "overlay copy from $OVERLAY_DIR failed"
  elif [ "${CLEANROOM_PRE_OVERLAY:-0}" = "1" ]; then
    echo "NOTE: ci/cleanroom-overlay/ is absent. CLEANROOM_PRE_OVERLAY=1 skips it (WS7 Task 2 not landed yet)."
  else
    err "ci/cleanroom-overlay/ is missing."
    err "Run WS7 Task 2 first, or set CLEANROOM_PRE_OVERLAY=1 to build without it."
    return 1
  fi

  case "$canary" in
    "") : ;;
    deny)
      echo "CLEANROOM_CANARY=deny: planting a file under a denied root (dv/uvm/.canary_denied_ref)"
      mkdir -p "$stage/dv/uvm"
      echo canary > "$stage/dv/uvm/.canary_denied_ref"
      ;;
    artifact)
      echo "CLEANROOM_CANARY=artifact: planting a zero-byte artifact (dv/auto_dv/.canary.fsdb)"
      mkdir -p "$stage/dv/auto_dv"
      : > "$stage/dv/auto_dv/.canary.fsdb"
      ;;
    mcp)
      echo "CLEANROOM_CANARY=mcp: planting a remote MCP entry in the staged .mcp.json"
      if [ -f "$stage/.mcp.json" ]; then
        jq '.mcpServers.canary = {"type":"http","url":"https://example.invalid/mcp"}' \
          "$stage/.mcp.json" > "$stage/.mcp.json.tmp" && mv "$stage/.mcp.json.tmp" "$stage/.mcp.json"
      else
        err "cannot plant mcp canary: .mcp.json missing from stage"
        return 1
      fi
      ;;
    identifier)
      echo "CLEANROOM_CANARY=identifier: planting a fenced identifier (dv/auto_dv/.canary_fenced_ref)"
      mkdir -p "$stage/dv/auto_dv"
      echo "riscv_arithmetic_basic_test" > "$stage/dv/auto_dv/.canary_fenced_ref"
      ;;
    *)
      err "unknown CLEANROOM_CANARY mode: $canary (expected deny|artifact|mcp|identifier)"
      return 1
      ;;
  esac
}

cleanroom_verify_stage() {  # <stage-dir>
  local stage="$1" rc=0
  cleanroom_check_deny_absence "$stage" || rc=1
  cleanroom_check_artifact_absence "$stage" || rc=1
  cleanroom_check_inventory "$stage" || rc=1
  cleanroom_check_reviews_set "$stage" || rc=1
  if [ "${CLEANROOM_PRE_OVERLAY:-0}" = "1" ]; then
    echo "NOTE: CLEANROOM_PRE_OVERLAY=1 skips the item-9 scan, whole-export identifier scan, NO-REMOTE-MCP, and validator checks (Task 2 not landed)."
  else
    cleanroom_check_item9_scan "$stage" || rc=1
    cleanroom_check_whole_export_identifiers "$stage" || rc=1
    cleanroom_check_no_remote_mcp "$stage" || rc=1
    cleanroom_check_validator "$stage" || rc=1
  fi
  return "$rc"
}

_cleanroom_main() {
  local dest="../ibex-cleanroom" force=0
  while [ "$#" -gt 0 ]; do
    case "$1" in
      --force) force=1; shift ;;
      --) shift; dest="${1:-$dest}"; shift || true; break ;;
      -*) die "unknown option: $1" ;;
      *) dest="$1"; shift ;;
    esac
  done

  local src_sha
  src_sha="$(git -C "$REPO_ROOT" rev-parse HEAD)" || die "$REPO_ROOT is not a git repository"

  local stage
  stage="$(mktemp -d "${TMPDIR:-/tmp}/ibex-cleanroom-stage.XXXXXX")" || die "mktemp failed"
  trap 'rm -rf "${stage:-}"' EXIT

  echo "Building cleanroom export of $src_sha into $stage ..."
  cleanroom_build_stage "$stage" "${CLEANROOM_CANARY:-}" || exit 1

  echo "Verifying export ..."
  if ! cleanroom_verify_stage "$stage"; then
    err "cleanroom export failed verification. DEST was not written."
    exit 1
  fi
  echo "Verification passed."

  if [ -e "$dest" ] && [ -n "$(ls -A "$dest" 2>/dev/null)" ]; then
    if [ "$force" -ne 1 ]; then
      err "$dest already exists and is not empty."
      err "Pass --force to overwrite it, or choose a different DEST."
      exit 1
    fi
    rm -rf "$dest"
  fi
  mkdir -p "$dest" || die "cannot create $dest"
  cp -a "$stage"/. "$dest"/

  (
    cd "$dest" \
      && git init -q \
      && git add -A \
      && git -c user.email="cleanroom@ibex.local" -c user.name="ibex-cleanroom" \
             commit -q -m "Cleanroom export of $src_sha (deny list: make-cleanroom.sh)"
  ) || die "failed to commit export at $dest"

  local dest_sha
  dest_sha="$(git -C "$dest" rev-parse HEAD)"
  echo "Cleanroom export built."
  echo "  dest:       $dest"
  echo "  source SHA: $src_sha"
  echo "  export SHA: $dest_sha"
  echo "  verify:     PASS"
}

if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
  _cleanroom_main "$@"
fi
