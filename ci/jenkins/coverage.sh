#!/usr/bin/env bash
# Coverage regression: nightly + COV=1. Archives the urg report and merged vdb.
# Run by hand or from Jenkins; see ci/jenkins/README.md. Options: --help.
set -uo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/common.sh"
CI_JOB_NAME=coverage
CI_TEST=all
CI_SEED="$(date -u +%y%m%d)"
CI_COV=1
ci_main "$@"
