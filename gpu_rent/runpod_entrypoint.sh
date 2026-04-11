#!/usr/bin/env bash
set -euo pipefail

INPUT_BASE_DIR="${INPUT_BASE_DIR:-/input}"
OUTPUT_BASE_DIR="${OUTPUT_BASE_DIR:-/output}"
PIPELINE_KIND="${PIPELINE_KIND:-abdominal}"
TOTALSEG_DEVICE="${TOTALSEG_DEVICE:-auto}"
OUTPUT_ROOT="${OUTPUT_ROOT:-$OUTPUT_BASE_DIR}"

if [[ -z "${INPUT_DICOM:-}" ]]; then
  echo "INPUT_DICOM is required. Example: /input/tdm_elena_savier_anonymized/PAT_0001_CASE_01" >&2
  exit 1
fi

echo "Pipeline kind : $PIPELINE_KIND"
echo "Input DICOM   : $INPUT_DICOM"
echo "Output root   : $OUTPUT_ROOT"
echo "Device        : $TOTALSEG_DEVICE"

case "$PIPELINE_KIND" in
  abdominal)
    export OUTPUT_ROOT
    exec bash /workspace/TotalSegmentator_MPS/gpu_rent/run_segment_abdominal_case.sh
    ;;
  *)
    echo "Unsupported PIPELINE_KIND: $PIPELINE_KIND" >&2
    exit 1
    ;;
esac

