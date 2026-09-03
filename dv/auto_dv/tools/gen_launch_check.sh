#!/usr/bin/env bash
# Launch-precondition check: DV_prompt.txt Section 12, items 1-11. Exit 0 only when every item passes.
# Run from the clone root. Output is the evidence record; keep it terse and greppable (`ITEM <n> PASS|FAIL <detail>`).
set -u
export LC_ALL=C  # byte-order sort: set comparisons below must not depend on locale collation
cd "$(git rev-parse --show-toplevel)" || exit 3
fail=0
res() { # res <item> <PASS|FAIL> <detail>
  printf 'ITEM %-3s %s  %s\n' "$1" "$2" "$3"; [ "$2" = PASS ] || fail=1; }
chk() { # chk <item> <detail> <cmd...>  -> PASS if cmd exits 0
  local it=$1 d=$2; shift 2; if "$@" >/dev/null 2>&1; then res "$it" PASS "$d"; else res "$it" FAIL "$d"; fi; }
DATE_RE='[0-9]{4}-[0-9]{2}-[0-9]{2}'
FENCE_STRINGS=(dv/uvm/core_ibex core_ibex BUILD_AND_SIM.md COSIM.md disable_cosim FCOV_NO_DEFAULT_SEQUENCE
               metadata.pickle docs/dv/reviews/ ci/reviews/test-overlap ci/reviews/fence-integrity)
scan_clean() { # scan_clean <path...> -> 0 if none of FENCE_STRINGS appear in any regular file under the paths
  local p s; for p in "$@"; do [ -e "$p" ] || continue
    for s in "${FENCE_STRINGS[@]}"; do grep -rIFq -- "$s" "$p" && { echo "  hit: '$s' in $p" >&2; return 1; }; done; done; return 0; }

# 1
chk 1 "no '^- PROPOSED RULING' marker in DV_prompt.txt" test "$(grep -c '^- PROPOSED RULING' DV_prompt.txt)" -eq 0
# 2
ok=1; [ -f docs/dv/FENCE.md ] || ok=0
allow=$(awk '/^## The `ci\/` allowlist/{s=1;next} s&&/^## /{exit} s' docs/dv/FENCE.md 2>/dev/null)
for n in ci/env.sh ci/setup-venv.sh ci/get-toolchain.sh ci/check_fcov_expectations.py ci/mcp/ ci/reviews/; do
  printf '%s' "$allow" | grep -Fq -- "$n" || { ok=0; echo "  FENCE.md ci/ allowlist section missing $n" >&2; }; done
chk 2 "FENCE.md exists with ci/ allowlist naming the six required entries" test $ok -eq 1
# 3
ok=1; [ -f docs/dv/SIM_RECIPE.md ] || ok=0
for m in 'executed-on:' 'submission-command:' 'spike-built-on:' 'fence-integrity: PASS'; do
  grep -Eq -- "^${m}.*${DATE_RE}" docs/dv/SIM_RECIPE.md 2>/dev/null || { ok=0; echo "  SIM_RECIPE.md missing dated '$m'" >&2; }; done
chk 3 "SIM_RECIPE.md carries four dated marker lines" test $ok -eq 1
# 4
ok=1; scan_clean docs/dv/TB_CONTRACT.md || ok=0
grep -Eq -- "^fence-integrity: PASS.*${DATE_RE}" docs/dv/TB_CONTRACT.md 2>/dev/null || ok=0
chk 4 "TB_CONTRACT.md is Zone A variant (clean scan, dated fence-integrity PASS)" test $ok -eq 1
# 5
ok=1
for f in CLAUDE.md AGENTS.md; do head -10 "$f" | grep -Fq 'FENCE-ZONE: A' || { ok=0; echo "  $f lacks FENCE-ZONE: A in first ten lines" >&2; }
  scan_clean "$f" || ok=0; done
[ -f docs/dv/dv_principles.md ] || ok=0
awk '/^## 6\. /{s=1} /^## 7\. /{s=0} s' docs/dv/dv_principles.md 2>/dev/null | grep -Fq 'Zone A' || { ok=0; echo "  dv_principles.md Section 6 lacks 'Zone A'" >&2; }
grep -Eq -- "^fence-integrity: PASS.*${DATE_RE}" docs/dv/dv_principles.md 2>/dev/null || ok=0
chk 5 "CLAUDE.md/AGENTS.md Zone A markers + clean scan; dv_principles.md present, S6 'Zone A', dated PASS" test $ok -eq 1
# 6
ok=1
[ -z "$(find vendor -maxdepth 1 -name 'riscv?isa?sim*' 2>/dev/null)" ] || { ok=0; echo "  vendor/riscv?isa?sim* present" >&2; }
[ ! -e vendor/patches ] || { ok=0; echo "  vendor/patches present" >&2; }
lock_rev=$(grep -Eo 'rev:[[:space:]]*"?[0-9a-f]{40}' vendor/google_riscv-dv.lock.hjson 2>/dev/null | grep -Eo '[0-9a-f]{40}' | head -1)
fence_line=$(grep -E "^riscv-dv-verified-on: ${DATE_RE}" docs/dv/FENCE.md 2>/dev/null | head -1)
fence_rev=$(printf '%s' "$fence_line" | grep -Eo '[0-9a-f]{40}' | head -1)
[ -n "$lock_rev" ] && [ "$lock_rev" = "$fence_rev" ] || { ok=0; echo "  lock rev '$lock_rev' != FENCE.md attested rev '$fence_rev'" >&2; }
# the attestation paragraph (from the marker line to the next blank line) must state the tree diff was empty
awk '/^riscv-dv-verified-on:/{s=1} s&&/^$/{exit} s' docs/dv/FENCE.md 2>/dev/null | grep -Eiq 'tree diff .* empty' || { ok=0; echo "  FENCE.md attestation lacks 'tree diff ... empty'" >&2; }
! grep -rIFq -- 'Ibex Specific' vendor/google_riscv-dv/ 2>/dev/null || { ok=0; echo "  'Ibex Specific' found under vendor/google_riscv-dv/" >&2; }
chk 6 "no vendored spike/patches; riscv-dv lock rev == FENCE.md attested rev (empty diff); no 'Ibex Specific'" test $ok -eq 1
# 7
chk 7 "dv/auto_dv/.gitignore exists and ignores work/" bash -c '[ -f dv/auto_dv/.gitignore ] && git check-ignore -q dv/auto_dv/work/probe_file'
# 8
ok=1
s4=$(awk '/^4\. Goal and how it is measured/{s=1} /^5\. Method/{s=0} s' DV_prompt.txt)
printf '%s' "$s4" | grep -Eq 'G = [0-9]+(\.[0-9]+)?' && printf '%s' "$s4" | grep -Eq 'N = [0-9]+' || { ok=0; echo "  S4 lacks numeric N/G" >&2; }
n_rul=$(awk '/^2\. DUT and build configuration/{s=1} /^3\. What you may read/{s=0} s' DV_prompt.txt | grep -c '^- Owner ruling (')
[ "$n_rul" -eq 2 ] || { ok=0; echo "  S2 has $n_rul 'Owner ruling (' bullets, need 2" >&2; }
awk '/^12\. Launch preconditions/{s=1} s' DV_prompt.txt | grep -Eq -- "^Owner sign-off: [A-Za-z][^,]+, ${DATE_RE}\s*$" || { ok=0; echo "  S12 sign-off line missing name+date" >&2; }
chk 8 "S4 numeric N and G; S2 two 'Owner ruling (' bullets; signed and dated sign-off line" test $ok -eq 1
# 9
ok=1
scan_clean .claude/skills/ .claude/agents/ ci/env.sh ci/mcp/ ci/reviews/ CLAUDE.md AGENTS.md .codex/config.toml docs/dv/TB_CONTRACT.md docs/dv/SIM_RECIPE.md || ok=0
want="GUIDE.md ai-slop-comments.md assertion-integrity.md forces-and-hier-access.md magic-numbers.md rtl-purity.md"
have=$(ls -A ci/reviews/ 2>/dev/null | sort | tr '\n' ' ' | sed 's/ $//')
[ "$have" = "$want" ] || { ok=0; echo "  ci/reviews/ contents: '$have'" >&2; }
grep -Eq -- "^fence-integrity: PASS.*${DATE_RE}" ci/reviews/GUIDE.md 2>/dev/null || { ok=0; echo "  GUIDE.md lacks dated fence-integrity PASS" >&2; }
w=.claude/skills/cross-review/scripts/run_codex_review.sh
for r in ai-slop-comments.md rtl-purity.md magic-numbers.md forces-and-hier-access.md assertion-integrity.md; do
  grep -Fq -- "$r" "$w" 2>/dev/null || { ok=0; echo "  wrapper lacks literal $r" >&2; }; done
! grep -Fq -- 'ci/reviews/*.md' "$w" 2>/dev/null || { ok=0; echo "  wrapper contains ci/reviews/*.md glob" >&2; }
grep -Fq -- 'dv/auto_dv/reviews/' "$w" 2>/dev/null || { ok=0; echo "  wrapper lacks dv/auto_dv/reviews/" >&2; }
chk 9 "fence-string scan clean; ci/reviews/ exactly six files; GUIDE.md dated PASS; review wrapper literals" test $ok -eq 1
# 10
ok=1
mcp_keys=$(python3 -c 'import json,sys; d=json.load(open(".mcp.json"))["mcpServers"]; print(" ".join(sorted(d))); sys.exit(1 if any(("url" in v) or ("type" in v and v["type"]!="stdio") for v in d.values()) else 0)' 2>/dev/null) || ok=0
[ "$mcp_keys" = "fsdb-mcp-server siliconpilot verdi-cov-mcp" ] || { ok=0; echo "  .mcp.json servers: '$mcp_keys'" >&2; }
toml_keys=$(grep -Eo '^\[mcp_servers\.[^]]+\]' .codex/config.toml 2>/dev/null | sed 's/\[mcp_servers\.//; s/\]//' | sort | tr '\n' ' ' | sed 's/ $//')
[ "$toml_keys" = "fsdb-mcp-server siliconpilot verdi-cov-mcp" ] || { ok=0; echo "  config.toml servers: '$toml_keys'" >&2; }
! grep -Eq '^\s*url\s*=' .codex/config.toml 2>/dev/null || { ok=0; echo "  config.toml has a remote url" >&2; }
chk 10 ".mcp.json and .codex/config.toml list exactly the three local MCP servers, no remote" test $ok -eq 1
# 11
ok=1
[ "$(ls -A dv | tr '\n' ' ')" = "auto_dv " ] || { ok=0; echo "  dv/ contents: $(ls -A dv | tr '\n' ' ')" >&2; }
[ "$(ls -A docs | tr '\n' ' ')" = "dv " ] || { ok=0; echo "  docs/ contents: $(ls -A docs | tr '\n' ' ')" >&2; }
[ "$(ls -A docs/dv | sort | tr '\n' ' ')" = "FENCE.md SIM_RECIPE.md TB_CONTRACT.md dv_principles.md " ] || { ok=0; echo "  docs/dv contents: $(ls -A docs/dv | tr '\n' ' ')" >&2; }
for p in ci/jenkins ci/build-spike.sh ci/setup-cosim.sh ci/run-cosim-test.sh vendor/patches formal \
         doc/01_overview/verification_overview.rst doc/03_reference/verification.rst doc/03_reference/verification_stages.rst \
         doc/03_reference/cosim.rst doc/03_reference/testplan.rst doc/03_reference/coverage_plan.rst; do
  [ ! -e "$p" ] || { ok=0; echo "  fenced path present: $p" >&2; }; done
[ -z "$(find vendor -maxdepth 1 -name 'riscv?isa?sim*' 2>/dev/null)" ] || ok=0
chk 11 "positive-list checks (dv/, docs/, ci/, vendor/, formal/, six doc files)" test $ok -eq 1

echo "---"
psha=$(sha256sum DV_prompt.txt | cut -c1-16)
if [ $fail -eq 0 ]; then echo "LAUNCH-CHECK: PASS ($(date +%F) HEAD=$(git rev-parse --short HEAD) DV_prompt.txt sha256=$psha)"; else echo "LAUNCH-CHECK: FAIL ($(date +%F) HEAD=$(git rev-parse --short HEAD) DV_prompt.txt sha256=$psha)"; fi
exit $fail
