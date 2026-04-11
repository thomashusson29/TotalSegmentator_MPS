#!/usr/bin/env bash
set -euo pipefail

if [[ -z "${INPUT_DICOM:-}" ]]; then
  echo "INPUT_DICOM is required." >&2
  exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

if [[ -z "${HEIGHT_CM:-}" && -n "${CASE_METADATA_CSV:-}" ]]; then
  HEIGHT_CM="$(
    python3 "${REPO_ROOT}/gpu_rent/lookup_case_height.py" \
      --case-dir "${INPUT_DICOM}" \
      --metadata-csv "${CASE_METADATA_CSV}"
  )"
  export HEIGHT_CM
  echo "Resolved HEIGHT_CM=${HEIGHT_CM} from ${CASE_METADATA_CSV}" >&2
fi

exec bash "${REPO_ROOT}/gpu_rent/run_segment_abdominal_case.sh"
