#!/usr/bin/env bash
set -euo pipefail

# Edit only this block on the RunPod machine.
REPO_ROOT="/workspace/TotalSegmentator_MPS"
INPUT_DICOM="/input/PAT_0001_CASE_01"
HEIGHT_CM="156"
TOTALSEG_LICENSE_NUMBER="CHANGE_ME"

OUTPUT_ROOT="/output"
BUNDLE_NAME=""
TOTALSEG_DEVICE="gpu"

WITH_MUSCLES="1"
WITH_ODIASP="1"
WITH_TISSUE="1"
WITH_TOTAL="1"
WITH_TOCSV="1"

PYTHON_BIN="python"

if [[ "${INPUT_DICOM}" == "/input/PAT_0001_CASE_01" ]]; then
  echo "Edit INPUT_DICOM at the top of gpu_rent/run_one_case_manual.sh before running it." >&2
  exit 1
fi

if [[ -z "${HEIGHT_CM}" ]]; then
  echo "HEIGHT_CM is required in gpu_rent/run_one_case_manual.sh." >&2
  exit 1
fi

if [[ -z "${TOTALSEG_LICENSE_NUMBER}" || "${TOTALSEG_LICENSE_NUMBER}" == "CHANGE_ME" ]]; then
  echo "Set TOTALSEG_LICENSE_NUMBER at the top of gpu_rent/run_one_case_manual.sh." >&2
  exit 1
fi

if [[ -z "${BUNDLE_NAME}" ]]; then
  BUNDLE_NAME="$(basename "${INPUT_DICOM}")"
fi

mkdir -p "${OUTPUT_ROOT}"
cd "${REPO_ROOT}"

cmd=(
  "${PYTHON_BIN}"
  -m gpu_rent.segment_abdominal_muscles_gpu
  --input-dicom "${INPUT_DICOM}"
  --output-root "${OUTPUT_ROOT}"
  --bundle-name "${BUNDLE_NAME}"
  --device "${TOTALSEG_DEVICE}"
  --height-cm "${HEIGHT_CM}"
  --totalseg-license-number "${TOTALSEG_LICENSE_NUMBER}"
)

if [[ "${WITH_MUSCLES}" == "1" ]]; then
  cmd+=(--with-muscles)
fi
if [[ "${WITH_ODIASP}" == "1" ]]; then
  cmd+=(--with-odiasp)
fi
if [[ "${WITH_TISSUE}" == "1" ]]; then
  cmd+=(--with-tissue)
fi
if [[ "${WITH_TOTAL}" == "1" ]]; then
  cmd+=(--with-total)
fi
if [[ "${WITH_TOCSV}" == "1" ]]; then
  cmd+=(--with-tocsv)
fi

time_log="${OUTPUT_ROOT}/${BUNDLE_NAME}.time.txt"

echo "Running bundle     : ${BUNDLE_NAME}"
echo "Input DICOM        : ${INPUT_DICOM}"
echo "Height (cm)        : ${HEIGHT_CM}"
echo "Device             : ${TOTALSEG_DEVICE}"
echo "Output root        : ${OUTPUT_ROOT}"
echo "Timing log         : ${time_log}"
echo "Command:"
printf '  %q' "${cmd[@]}"
printf '\n'

/usr/bin/time -v -o "${time_log}" "${cmd[@]}"

echo
echo "Done."
echo "Bundle directory   : ${OUTPUT_ROOT}/${BUNDLE_NAME}"
echo "Timing log         : ${time_log}"
