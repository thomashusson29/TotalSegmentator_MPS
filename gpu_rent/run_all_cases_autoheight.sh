#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="${REPO_ROOT:-/workspace/TotalSegmentator_MPS}"
INPUT_ROOT="${INPUT_ROOT:-/input/tdm_elena_savier_anonymized_cohort26_keep_patientid}"
CASE_METADATA_CSV="${CASE_METADATA_CSV:-${INPUT_ROOT}/case_metadata.csv}"
OUTPUT_ROOT="${OUTPUT_ROOT:-/output}"
TOTALSEG_DEVICE="${TOTALSEG_DEVICE:-gpu}"
PYTHON_BIN="${PYTHON_BIN:-python}"

WITH_MUSCLES="${WITH_MUSCLES:-1}"
WITH_ODIASP="${WITH_ODIASP:-1}"
WITH_TISSUE="${WITH_TISSUE:-1}"
WITH_TOTAL="${WITH_TOTAL:-1}"
WITH_TOCSV="${WITH_TOCSV:-1}"

SKIP_EXISTING="${SKIP_EXISTING:-1}"
STOP_ON_ERROR="${STOP_ON_ERROR:-0}"

if [[ ! -d "${INPUT_ROOT}" ]]; then
  echo "INPUT_ROOT not found: ${INPUT_ROOT}" >&2
  exit 1
fi

if [[ ! -f "${CASE_METADATA_CSV}" ]]; then
  echo "CASE_METADATA_CSV not found: ${CASE_METADATA_CSV}" >&2
  exit 1
fi

if [[ -z "${TOTALSEG_LICENSE_NUMBER:-}" ]]; then
  echo "TOTALSEG_LICENSE_NUMBER is required." >&2
  exit 1
fi

mkdir -p "${OUTPUT_ROOT}"
cd "${REPO_ROOT}"

batch_log="${OUTPUT_ROOT}/batch_run.log"
batch_csv="${OUTPUT_ROOT}/batch_run_summary.csv"

echo "case_code;status;height_cm;elapsed_seconds;bundle_dir;message" > "${batch_csv}"

mapfile -t case_dirs < <(find "${INPUT_ROOT}" -mindepth 1 -maxdepth 1 -type d -name 'PAT_*' | sort)

if [[ "${#case_dirs[@]}" -eq 0 ]]; then
  echo "No PAT_* case directories found under ${INPUT_ROOT}" >&2
  exit 1
fi

echo "Batch start: $(date -Iseconds)" | tee -a "${batch_log}"
echo "Input root : ${INPUT_ROOT}" | tee -a "${batch_log}"
echo "Cases      : ${#case_dirs[@]}" | tee -a "${batch_log}"
echo "Output root: ${OUTPUT_ROOT}" | tee -a "${batch_log}"

for case_dir in "${case_dirs[@]}"; do
  case_code="$(basename "${case_dir}")"
  bundle_dir="${OUTPUT_ROOT}/${case_code}"

  if [[ "${SKIP_EXISTING}" == "1" && -d "${bundle_dir}" ]]; then
    echo "[SKIP] ${case_code}: bundle already exists at ${bundle_dir}" | tee -a "${batch_log}"
    echo "${case_code};skipped_existing;;;${bundle_dir};bundle already exists" >> "${batch_csv}"
    continue
  fi

  if ! height_cm="$("${PYTHON_BIN}" "${REPO_ROOT}/gpu_rent/lookup_case_height.py" --case-dir "${case_dir}" --metadata-csv "${CASE_METADATA_CSV}" 2>/tmp/${case_code}.height.err)"; then
    message="$(tr '\n' ' ' < /tmp/${case_code}.height.err | sed 's/;/,/g')"
    echo "[SKIP] ${case_code}: ${message}" | tee -a "${batch_log}"
    echo "${case_code};missing_height;;;${bundle_dir};${message}" >> "${batch_csv}"
    continue
  fi

  start_epoch="$(date +%s)"
  echo "[START] ${case_code} height=${height_cm} $(date -Iseconds)" | tee -a "${batch_log}"

  cmd=(
    "${PYTHON_BIN}"
    -m gpu_rent.segment_abdominal_muscles_gpu
    --input-dicom "${case_dir}"
    --output-root "${OUTPUT_ROOT}"
    --bundle-name "${case_code}"
    --device "${TOTALSEG_DEVICE}"
    --height-cm "${height_cm}"
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

  case_log="${OUTPUT_ROOT}/${case_code}.console.log"
  if "${cmd[@]}" >"${case_log}" 2>&1; then
    end_epoch="$(date +%s)"
    elapsed="$((end_epoch - start_epoch))"
    echo "${elapsed}" > "${OUTPUT_ROOT}/${case_code}.elapsed_seconds.txt"
    echo "[OK] ${case_code}: ${elapsed}s" | tee -a "${batch_log}"
    echo "${case_code};ok;${height_cm};${elapsed};${bundle_dir};" >> "${batch_csv}"
  else
    end_epoch="$(date +%s)"
    elapsed="$((end_epoch - start_epoch))"
    echo "${elapsed}" > "${OUTPUT_ROOT}/${case_code}.elapsed_seconds.txt"
    echo "[ERROR] ${case_code}: ${elapsed}s see ${case_log}" | tee -a "${batch_log}"
    echo "${case_code};error;${height_cm};${elapsed};${bundle_dir};see ${case_log}" >> "${batch_csv}"
    if [[ "${STOP_ON_ERROR}" == "1" ]]; then
      exit 1
    fi
  fi
done

echo "Batch end: $(date -Iseconds)" | tee -a "${batch_log}"
echo "Summary : ${batch_csv}" | tee -a "${batch_log}"
