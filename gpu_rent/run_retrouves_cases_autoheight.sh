#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="${REPO_ROOT:-/workspace/TotalSegmentator_MPS}"
INPUT_ROOT="${INPUT_ROOT:-/workspace/DICOM_RETROUVES_A_TRAITER_7}"
CASE_METADATA_CSV="${CASE_METADATA_CSV:-${INPUT_ROOT}/case_metadata.csv}"
RUN_NAME="${RUN_NAME:-retrouves_7_$(date +%Y%m%d_%H%M%S)}"
CASE_NAME_GLOB="${CASE_NAME_GLOB:-*}"

export REPO_ROOT
export INPUT_ROOT
export CASE_METADATA_CSV
export RUN_NAME
export CASE_NAME_GLOB

exec bash "${REPO_ROOT}/gpu_rent/run_all_cases_autoheight.sh"
