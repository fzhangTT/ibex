#!/usr/bin/env bash
# ci/check-landing.sh <base> <head>
#
# Gate for a Zone A cleanroom submission landing back onto a full-tree branch: every
# changed path in <base>..<head> must be under dv/auto_dv/, with no rename/delete
# touching outside it, no symlink anywhere in the range, and every added dv/auto_dv/
# file named gen_* (exempt: dv/auto_dv/.gitignore, dv/auto_dv/contract/**).
#
# Exit 0 iff the range lands clean; exit 1 with a named reason per violation.
set -uo pipefail

err() { echo "ERROR: $*" >&2; }

if [ "$#" -ne 2 ]; then
  err "usage: ci/check-landing.sh <base> <head>"
  exit 2
fi
BASE="$1"
HEAD="$2"
NS="dv/auto_dv/"

is_under_ns() { case "$1" in "$NS"*) return 0 ;; *) return 1 ;; esac; }
is_exempt() {
  case "$1" in
    "${NS}.gitignore") return 0 ;;
    "${NS}contract/"*) return 0 ;;
    *) return 1 ;;
  esac
}

fail=0
reasons=()
reject() { reasons+=("$1"); fail=1; }

while IFS= read -r -d '' metaline; do
  status_full="${metaline##* }"
  status="${status_full:0:1}"
  oldmode="$(printf '%s' "$metaline" | awk '{print $1}' | tr -d ':')"
  newmode="$(printf '%s' "$metaline" | awk '{print $2}')"

  IFS= read -r -d '' path1
  path2=""
  case "$status" in
    R|C) IFS= read -r -d '' path2 ;;
  esac

  if [ "$oldmode" = "120000" ] || [ "$newmode" = "120000" ]; then
    reject "symlink touched: ${path2:-$path1}"
  fi

  if [ -n "$path2" ]; then
    if ! is_under_ns "$path1" || ! is_under_ns "$path2"; then
      reject "rename touches outside dv/auto_dv/: $path1 -> $path2"
    else
      base="$(basename "$path2")"
      if ! is_exempt "$path2" && [[ "$base" != gen_* ]]; then
        reject "renamed dv/auto_dv/ file '$path2' does not start with gen_"
      fi
    fi
  else
    if ! is_under_ns "$path1"; then
      reject "path outside dv/auto_dv/: $path1 (status $status)"
    elif [ "$status" = "A" ]; then
      base="$(basename "$path1")"
      if ! is_exempt "$path1" && [[ "$base" != gen_* ]]; then
        reject "added dv/auto_dv/ file '$path1' does not start with gen_"
      fi
    fi
  fi
done < <(git diff --raw --find-renames -z "$BASE".."$HEAD")

if [ "$fail" -ne 0 ]; then
  err "landing check FAILED for range $BASE..$HEAD:"
  printf '  %s\n' "${reasons[@]}" >&2
  exit 1
fi
echo "landing check PASSED for range $BASE..$HEAD"
exit 0
