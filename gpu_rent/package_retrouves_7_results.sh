#!/usr/bin/env bash
set -euo pipefail

RUN_NAME="${RUN_NAME:-retrouves_7}"
RUN_ROOT="${RUN_ROOT:-/workspace/run_outputs/${RUN_NAME}}"
REPO_ROOT="${REPO_ROOT:-/workspace/TotalSegmentator_MPS}"

exec bash "${REPO_ROOT}/gpu_rent/package_batch_results.sh" "${RUN_ROOT}"
