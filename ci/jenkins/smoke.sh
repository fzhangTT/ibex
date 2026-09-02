#!/usr/bin/env bash
# Smoke regression: two fast tests, one from each testlist. Budget: ~15 minutes.
# Smoke selection is CI policy; it is defined only here (see README §Smoke policy).
# Run by hand or from Jenkins; see ci/jenkins/README.md. Options: --help.
set -uo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/common.sh"
CI_JOB_NAME=smoke
CI_TEST=riscv_arithmetic_basic_test,mcounteren_test
CI_ITERATIONS=1
CI_SEED=1
ci_main "$@"
