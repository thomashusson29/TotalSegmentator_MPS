#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="${REPO_ROOT:-/workspace/TotalSegmentator_MPS}"
INPUT_ROOT="${INPUT_ROOT:-/workspace/tdm_elena_savier_anonymized_cohort26_keep_patientid}"
CASE_METADATA_CSV="${CASE_METADATA_CSV:-${INPUT_ROOT}/case_metadata.csv}"
TOTALSEG_DEVICE="${TOTALSEG_DEVICE:-gpu}"
PYTHON_BIN="${PYTHON_BIN:-python}"

WITH_MUSCLES="${WITH_MUSCLES:-1}"
WITH_ODIASP="${WITH_ODIASP:-1}"
WITH_TISSUE="${WITH_TISSUE:-1}"
WITH_TOTAL="${WITH_TOTAL:-1}"
WITH_TOCSV="${WITH_TOCSV:-1}"

SKIP_EXISTING="${SKIP_EXISTING:-1}"
STOP_ON_ERROR="${STOP_ON_ERROR:-0}"

PATIENT_SELECTION="${PATIENT_SELECTION:-}"
CASE_SELECTION="${CASE_SELECTION:-}"

RUN_NAME="${RUN_NAME:-batch_$(date +%Y%m%d_%H%M%S)}"
RUN_ROOT="${RUN_ROOT:-/workspace/run_outputs/${RUN_NAME}}"
BUNDLES_DIR="${BUNDLES_DIR:-${RUN_ROOT}/bundles}"
LOGS_DIR="${LOGS_DIR:-${RUN_ROOT}/logs}"
TABLES_DIR="${TABLES_DIR:-${RUN_ROOT}/tables}"
EXPORTS_3D_DIR="${EXPORTS_3D_DIR:-${RUN_ROOT}/3d_exports}"

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

mkdir -p "${RUN_ROOT}" "${BUNDLES_DIR}" "${LOGS_DIR}" "${TABLES_DIR}" "${EXPORTS_3D_DIR}"
mkdir -p \
  "${EXPORTS_3D_DIR}/abdominal_muscles" \
  "${EXPORTS_3D_DIR}/odiasp" \
  "${EXPORTS_3D_DIR}/tissue_original" \
  "${EXPORTS_3D_DIR}/tissue_T4_L4" \
  "${EXPORTS_3D_DIR}/total"

cd "${REPO_ROOT}"

batch_log="${LOGS_DIR}/batch_run.log"
batch_csv="${TABLES_DIR}/batch_run_summary.csv"
global_csv_source="${BUNDLES_DIR}/segmentation_metrics.csv"
global_csv_target="${TABLES_DIR}/segmentation_metrics.csv"

echo "case_code;status;height_cm;elapsed_seconds;bundle_dir;console_log;message" > "${batch_csv}"

copy_if_exists() {
  local source_path="$1"
  local target_path="$2"
  if [[ -f "${source_path}" ]]; then
    cp -f "${source_path}" "${target_path}"
  fi
}

sync_case_exports() {
  local case_code="$1"
  local bundle_dir="$2"

  copy_if_exists \
    "${bundle_dir}/abdominal_muscles_multilabel.nii.gz" \
    "${EXPORTS_3D_DIR}/abdominal_muscles/${case_code}__abdominal_muscles_multilabel.nii.gz"

  copy_if_exists \
    "${bundle_dir}/odiasp/ODIASP_multilabel.nii.gz" \
    "${EXPORTS_3D_DIR}/odiasp/${case_code}__ODIASP_multilabel.nii.gz"

  copy_if_exists \
    "${bundle_dir}/tissue/tissue_4_types_original_multilabel.nii.gz" \
    "${EXPORTS_3D_DIR}/tissue_original/${case_code}__tissue_4_types_original_multilabel.nii.gz"

  copy_if_exists \
    "${bundle_dir}/tissue/tissue_4_types_T4_L4_multilabel.nii.gz" \
    "${EXPORTS_3D_DIR}/tissue_T4_L4/${case_code}__tissue_4_types_T4_L4_multilabel.nii.gz"

  copy_if_exists \
    "${bundle_dir}/total/total_multilabel.nii.gz" \
    "${EXPORTS_3D_DIR}/total/${case_code}__total_multilabel.nii.gz"
}

sync_global_csv() {
  if [[ -f "${global_csv_source}" ]]; then
    cp -f "${global_csv_source}" "${global_csv_target}"
  fi
}

normalize_patient_code() {
  local token="$1"
  token="${token//,/}"
  if [[ "${token}" =~ ^PAT_([0-9]{4})$ ]]; then
    printf 'PAT_%04d\n' "${BASH_REMATCH[1]#0}"
    return 0
  fi
  if [[ "${token}" =~ ^[0-9]+$ ]]; then
    printf 'PAT_%04d\n' "${token#0}"
    return 0
  fi
  return 1
}

declare -A selected_patients=()
declare -A selected_cases=()

if [[ -n "${PATIENT_SELECTION}" ]]; then
  while read -r token; do
    [[ -z "${token}" ]] && continue
    if [[ "${token}" =~ ^([0-9]+)-([0-9]+)$ ]]; then
      start="${BASH_REMATCH[1]}"
      end="${BASH_REMATCH[2]}"
      if (( start <= end )); then
        for ((i=start; i<=end; i++)); do
          selected_patients["$(printf 'PAT_%04d' "${i}")"]=1
        done
      else
        for ((i=start; i>=end; i--)); do
          selected_patients["$(printf 'PAT_%04d' "${i}")"]=1
        done
      fi
      continue
    fi

    if [[ "${token}" =~ ^PAT_([0-9]{4})-PAT_([0-9]{4})$ ]]; then
      start=$((10#${BASH_REMATCH[1]}))
      end=$((10#${BASH_REMATCH[2]}))
      if (( start <= end )); then
        for ((i=start; i<=end; i++)); do
          selected_patients["$(printf 'PAT_%04d' "${i}")"]=1
        done
      else
        for ((i=start; i>=end; i--)); do
          selected_patients["$(printf 'PAT_%04d' "${i}")"]=1
        done
      fi
      continue
    fi

    if patient_code="$(normalize_patient_code "${token}")"; then
      selected_patients["${patient_code}"]=1
    else
      echo "Invalid PATIENT_SELECTION token: ${token}" >&2
      exit 1
    fi
  done < <(printf '%s\n' "${PATIENT_SELECTION}" | tr ', ' '\n\n')
fi

if [[ -n "${CASE_SELECTION}" ]]; then
  while read -r token; do
    [[ -z "${token}" ]] && continue
    selected_cases["$(basename "${token}")"]=1
  done < <(printf '%s\n' "${CASE_SELECTION}" | tr ', ' '\n\n')
fi

all_case_dirs=()
mapfile -t all_case_dirs < <(find "${INPUT_ROOT}" -mindepth 1 -maxdepth 1 -type d -name 'PAT_*' | sort)

case_dirs=()
for case_dir in "${all_case_dirs[@]}"; do
  case_code="$(basename "${case_dir}")"
  patient_code="${case_code%%_CASE_*}"

  include_case=1
  if [[ "${#selected_patients[@]}" -gt 0 || "${#selected_cases[@]}" -gt 0 ]]; then
    include_case=0
    if [[ "${#selected_patients[@]}" -gt 0 && -n "${selected_patients[${patient_code}]:-}" ]]; then
      include_case=1
    fi
    if [[ "${#selected_cases[@]}" -gt 0 && -n "${selected_cases[${case_code}]:-}" ]]; then
      include_case=1
    fi
  fi

  if [[ "${include_case}" == "1" ]]; then
    case_dirs+=("${case_dir}")
  fi
done

if [[ "${#case_dirs[@]}" -eq 0 ]]; then
  echo "No matching case directories found under ${INPUT_ROOT}" >&2
  exit 1
fi

{
  echo "Batch start : $(date -Iseconds)"
  echo "Repo root   : ${REPO_ROOT}"
  echo "Input root  : ${INPUT_ROOT}"
  echo "Cases       : ${#case_dirs[@]}"
  echo "Patient sel : ${PATIENT_SELECTION:-<all>}"
  echo "Case sel    : ${CASE_SELECTION:-<all>}"
  echo "Run root    : ${RUN_ROOT}"
  echo "Bundles dir : ${BUNDLES_DIR}"
  echo "Logs dir    : ${LOGS_DIR}"
  echo "Tables dir  : ${TABLES_DIR}"
  echo "3D dir      : ${EXPORTS_3D_DIR}"
} | tee -a "${batch_log}"

for case_dir in "${case_dirs[@]}"; do
  case_code="$(basename "${case_dir}")"
  bundle_dir="${BUNDLES_DIR}/${case_code}"
  case_log="${LOGS_DIR}/${case_code}.console.log"
  case_time="${LOGS_DIR}/${case_code}.elapsed_seconds.txt"
  height_err="${LOGS_DIR}/${case_code}.height.err"

  if [[ "${SKIP_EXISTING}" == "1" && -d "${bundle_dir}" ]]; then
    echo "[SKIP] ${case_code}: bundle already exists at ${bundle_dir}" | tee -a "${batch_log}"
    sync_case_exports "${case_code}" "${bundle_dir}"
    sync_global_csv
    echo "${case_code};skipped_existing;;;${bundle_dir};${case_log};bundle already exists" >> "${batch_csv}"
    continue
  fi

  height_cm=""
  height_status="found"
  height_message=""
  if ! height_cm="$("${PYTHON_BIN}" "${REPO_ROOT}/gpu_rent/lookup_case_height.py" --case-dir "${case_dir}" --metadata-csv "${CASE_METADATA_CSV}" 2>"${height_err}")"; then
    height_cm=""
    height_status="missing"
    height_message="$(tr '\n' ' ' < "${height_err}" | sed 's/;/,/g')"
    echo "[WARN] ${case_code}: running without height (${height_message})" | tee -a "${batch_log}"
  fi

  start_epoch="$(date +%s)"
  echo "[START] ${case_code}: height=${height_cm:-NA} $(date -Iseconds)" | tee -a "${batch_log}"

  cmd=(
    "${PYTHON_BIN}"
    -m gpu_rent.segment_abdominal_muscles_gpu
    --input-dicom "${case_dir}"
    --output-root "${BUNDLES_DIR}"
    --bundle-name "${case_code}"
    --device "${TOTALSEG_DEVICE}"
    --totalseg-license-number "${TOTALSEG_LICENSE_NUMBER}"
  )

  if [[ -n "${height_cm}" ]]; then
    cmd+=(--height-cm "${height_cm}")
  fi

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

  if "${cmd[@]}" >"${case_log}" 2>&1; then
    end_epoch="$(date +%s)"
    elapsed="$((end_epoch - start_epoch))"
    printf '%s\n' "${elapsed}" > "${case_time}"
    sync_case_exports "${case_code}" "${bundle_dir}"
    sync_global_csv
    if [[ "${height_status}" == "missing" ]]; then
      echo "[OK] ${case_code}: ${elapsed}s (without height)" | tee -a "${batch_log}"
      echo "${case_code};ok_missing_height;;${elapsed};${bundle_dir};${case_log};${height_message}" >> "${batch_csv}"
    else
      echo "[OK] ${case_code}: ${elapsed}s" | tee -a "${batch_log}"
      echo "${case_code};ok;${height_cm};${elapsed};${bundle_dir};${case_log};" >> "${batch_csv}"
    fi
  else
    end_epoch="$(date +%s)"
    elapsed="$((end_epoch - start_epoch))"
    printf '%s\n' "${elapsed}" > "${case_time}"
    sync_case_exports "${case_code}" "${bundle_dir}"
    sync_global_csv
    if [[ "${height_status}" == "missing" ]]; then
      echo "[ERROR] ${case_code}: ${elapsed}s without height see ${case_log}" | tee -a "${batch_log}"
      echo "${case_code};error_missing_height;;${elapsed};${bundle_dir};${case_log};${height_message} | see ${case_log}" >> "${batch_csv}"
    else
      echo "[ERROR] ${case_code}: ${elapsed}s see ${case_log}" | tee -a "${batch_log}"
      echo "${case_code};error;${height_cm};${elapsed};${bundle_dir};${case_log};see ${case_log}" >> "${batch_csv}"
    fi
    if [[ "${STOP_ON_ERROR}" == "1" ]]; then
      exit 1
    fi
  fi
done

sync_global_csv

{
  echo "Batch end   : $(date -Iseconds)"
  echo "Summary CSV : ${batch_csv}"
  echo "Metrics CSV : ${global_csv_target}"
  echo "3D exports  : ${EXPORTS_3D_DIR}"
} | tee -a "${batch_log}"
