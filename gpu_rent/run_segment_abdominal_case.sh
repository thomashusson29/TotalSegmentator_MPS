#!/usr/bin/env bash
set -euo pipefail

cd /workspace/TotalSegmentator_MPS

: "${INPUT_DICOM:?INPUT_DICOM is required}"

PYTHON_BIN="${PYTHON_BIN:-python}"
TOTALSEG_DEVICE="${TOTALSEG_DEVICE:-auto}"
OUTPUT_ROOT="${OUTPUT_ROOT:-/output}"

args=(
  -m gpu_rent.segment_abdominal_muscles_gpu
  --input-dicom "$INPUT_DICOM"
  --output-root "$OUTPUT_ROOT"
  --device "$TOTALSEG_DEVICE"
)

if [[ -n "${BUNDLE_NAME:-}" ]]; then
  args+=(--bundle-name "$BUNDLE_NAME")
fi

if [[ "${WITH_MUSCLES:-0}" == "1" ]]; then
  args+=(--with-muscles)
fi
if [[ "${WITH_ODIASP:-0}" == "1" ]]; then
  args+=(--with-odiasp)
fi
if [[ "${WITH_TISSUE:-0}" == "1" ]]; then
  args+=(--with-tissue)
fi
if [[ "${WITH_TOTAL:-0}" == "1" ]]; then
  args+=(--with-total)
fi
if [[ "${WITH_TOCSV:-0}" == "1" ]]; then
  args+=(--with-tocsv)
fi
if [[ -n "${HEIGHT_CM:-}" ]]; then
  args+=(--height-cm "$HEIGHT_CM")
fi
if [[ -n "${TOTALSEG_LICENSE_NUMBER:-}" ]]; then
  args+=(--totalseg-license-number "$TOTALSEG_LICENSE_NUMBER")
fi

exec "$PYTHON_BIN" "${args[@]}"

