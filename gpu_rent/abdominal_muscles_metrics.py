#!/usr/bin/env python3

from __future__ import annotations

from pathlib import Path

import numpy as np

from .common import (
    ABDOMINAL_TASK,
    nifti_data_xyz,
    nifti_spacing_xyz,
    normalize_volume_cm3_per_m3,
    reverse_label_map,
    round_or_none,
    total_label_map,
    voxel_volume_mm3,
)


def build_abdominal_muscles_metrics(
    *,
    input_dicom: Path,
    abdominal_nifti: Path,
    height_cm: float | None,
    native_ct_xyz: np.ndarray,
) -> dict:
    image, data_xyz = nifti_data_xyz(abdominal_nifti)
    label_map = total_label_map(ABDOMINAL_TASK)
    reverse_map = reverse_label_map(label_map)
    spacing_xyz = nifti_spacing_xyz(image)
    voxel_mm3 = voxel_volume_mm3(image)
    height_m = round_or_none(height_cm / 100.0) if height_cm else None

    union_mask = data_xyz > 0
    z_indices = np.where(union_mask.any(axis=(0, 1)))[0]
    if z_indices.size == 0:
        raise RuntimeError("abdominal_muscles segmentation is empty.")

    total_voxel_count = int(np.count_nonzero(union_mask))
    total_volume_mm3 = round_or_none(total_voxel_count * voxel_mm3)
    total_volume_cm3 = round_or_none(total_volume_mm3 / 1000.0 if total_volume_mm3 is not None else None)
    total_mean_hu = round_or_none(float(native_ct_xyz[union_mask].mean())) if total_voxel_count else None

    regional_muscles: dict[str, dict] = {}
    for label_name, label_id in sorted(reverse_map.items()):
        label_mask = data_xyz == label_id
        voxel_count = int(np.count_nonzero(label_mask))
        volume_mm3 = round_or_none(voxel_count * voxel_mm3)
        volume_cm3 = round_or_none(volume_mm3 / 1000.0 if volume_mm3 is not None else None)
        regional_muscles[label_name] = {
            "label_id": label_id,
            "voxel_count": voxel_count,
            "volume_mm3": volume_mm3,
            "volume_cm3": volume_cm3,
            "volume_cm3_per_m3": normalize_volume_cm3_per_m3(volume_cm3, height_m),
        }

    warnings: list[str] = []
    if not height_m:
        warnings.append("Height was not provided; height-normalized muscle volumes are left empty.")

    return {
        "method": "3D muscle metrics derived from TotalSegmentator abdominal_muscles over the native abdominal_muscles output extent.",
        "task": ABDOMINAL_TASK,
        "source_task": ABDOMINAL_TASK,
        "segmentation_name": ABDOMINAL_TASK,
        "input_scope": "abdominal_muscles_native_extent",
        "height_cm": round_or_none(height_cm) if height_cm else None,
        "height_m": height_m,
        "voxel_spacing_mm": [round_or_none(v) for v in spacing_xyz],
        "voxel_volume_mm3": round_or_none(voxel_mm3),
        "z_min": int(z_indices[0]),
        "z_max": int(z_indices[-1]),
        "slice_count": int(z_indices[-1] - z_indices[0] + 1),
        "total_muscle_voxel_count": total_voxel_count,
        "total_muscle_volume_mm3": total_volume_mm3,
        "total_muscle_volume_cm3": total_volume_cm3,
        "total_muscle_volume_cm3_per_m3": normalize_volume_cm3_per_m3(total_volume_cm3, height_m),
        "total_muscle_mean_hu": total_mean_hu,
        "regional_muscles": regional_muscles,
        "warnings": warnings,
    }

