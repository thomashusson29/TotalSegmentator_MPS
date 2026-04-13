#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "Usage: bash gpu_rent/package_batch_results.sh /workspace/run_outputs/<run_name>" >&2
  exit 1
fi

RUN_ROOT="$1"
if [[ ! -d "${RUN_ROOT}" ]]; then
  echo "RUN_ROOT not found: ${RUN_ROOT}" >&2
  exit 1
fi

RUN_ROOT="$(cd "${RUN_ROOT}" && pwd)"
RUN_PARENT="$(dirname "${RUN_ROOT}")"
RUN_NAME="$(basename "${RUN_ROOT}")"

LIGHT_ARCHIVE="${RUN_PARENT}/${RUN_NAME}_light.tar.gz"
FULL_ARCHIVE="${RUN_PARENT}/${RUN_NAME}_full.tar.gz"

tar -C "${RUN_PARENT}" -czf "${LIGHT_ARCHIVE}" \
  "${RUN_NAME}/tables" \
  "${RUN_NAME}/logs" \
  "${RUN_NAME}/3d_exports"

tar -C "${RUN_PARENT}" -czf "${FULL_ARCHIVE}" \
  "${RUN_NAME}"

echo "Light archive: ${LIGHT_ARCHIVE}"
echo "Full archive : ${FULL_ARCHIVE}"
