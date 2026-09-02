#!/usr/bin/env bash
# Nightly regression: TEST=all at testlist iterations. Seed pins to the UTC date.
# Run by hand or from Jenkins; see ci/jenkins/README.md. Options: --help.
set -uo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/common.sh"
CI_JOB_NAME=nightly
CI_TEST=all
CI_SEED="$(date -u +%y%m%d)"
ci_main "$@"
