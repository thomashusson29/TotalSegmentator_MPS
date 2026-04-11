#!/usr/bin/env python3

from __future__ import annotations

import traceback
from pathlib import Path

import numpy as np

from .common import (
    TOTAL_TASK,
    nifti_data_xyz,
    nifti_spacing_xyz,
    normalize_volume_cm3_per_m3,
    reverse_label_map,
    round_or_none,
    run_totalseg_inference,
    total_label_map,
    voxel_volume_mm3,
    write_failure_status,
    write_json,
    write_segmentation_bundle_artifacts,
)


def run_total_postprocess(
    *,
    input_dicom: Path,
    bundle_dir: Path,
    device: str,
    height_cm: float | None,
) -> None:
    total_dir = bundle_dir / "total"
    total_dir.mkdir(parents=True, exist_ok=True)
    stdout_path = total_dir / "stdout.log"
    stderr_path = total_dir / "stderr.log"

    try:
        total_nifti = total_dir / "total_multilabel.nii.gz"
        statistics_path = total_dir / "statistics.json"
        label_map = total_label_map(TOTAL_TASK)
        reverse_map = reverse_label_map(label_map)

        run_totalseg_inference(
            input_path=input_dicom,
            output_path=total_nifti,
            task=TOTAL_TASK,
            device=device,
            command_path=total_dir / "command.txt",
            stdout_path=stdout_path,
            stderr_path=stderr_path,
            statistics_path=statistics_path,
            stats_include_incomplete=True,
        )

        write_segmentation_bundle_artifacts(
            bundle_dir=total_dir,
            task=TOTAL_TASK,
            source_task=TOTAL_TASK,
            segmentation_name="Total",
            nifti_path=total_nifti,
            color_table_name="total.ctbl",
            labels_json_name="labels.json",
            label_map=label_map,
        )

        image, data_xyz = nifti_data_xyz(total_nifti)
        spacing_xyz = nifti_spacing_xyz(image)
        voxel_mm3 = voxel_volume_mm3(image)
        height_m = round_or_none(height_cm / 100.0) if height_cm else None

        left_id = reverse_map["iliopsoas_left"]
        right_id = reverse_map["iliopsoas_right"]
        left_voxels = int(np.count_nonzero(data_xyz == left_id))
        right_voxels = int(np.count_nonzero(data_xyz == right_id))
        total_voxels = left_voxels + right_voxels

        left_mm3 = round_or_none(left_voxels * voxel_mm3)
        right_mm3 = round_or_none(right_voxels * voxel_mm3)
        total_mm3 = round_or_none(total_voxels * voxel_mm3)
        left_cm3 = round_or_none(left_mm3 / 1000.0 if left_mm3 is not None else None)
        right_cm3 = round_or_none(right_mm3 / 1000.0 if right_mm3 is not None else None)
        total_cm3 = round_or_none(total_mm3 / 1000.0 if total_mm3 is not None else None)

        warnings: list[str] = []
        if not height_m:
            warnings.append("Height was not provided; height-normalized iliopsoas volumes are left empty.")

        metrics = {
            "method": "Full-scan TotalSegmentator total task with iliopsoas volume summary.",
            "task": TOTAL_TASK,
            "source_task": TOTAL_TASK,
            "segmentation_name": "Total",
            "input_scope": "full_scan",
            "height_cm": round_or_none(height_cm) if height_cm else None,
            "height_m": height_m,
            "voxel_spacing_mm": [round_or_none(v) for v in spacing_xyz],
            "labels_used_for_psoas_volume": ["iliopsoas_left", "iliopsoas_right"],
            "iliopsoas_left": {
                "label_id": left_id,
                "voxel_count": left_voxels,
                "volume_mm3": left_mm3,
                "volume_cm3": left_cm3,
                "volume_cm3_per_m3": normalize_volume_cm3_per_m3(left_cm3, height_m),
            },
            "iliopsoas_right": {
                "label_id": right_id,
                "voxel_count": right_voxels,
                "volume_mm3": right_mm3,
                "volume_cm3": right_cm3,
                "volume_cm3_per_m3": normalize_volume_cm3_per_m3(right_cm3, height_m),
            },
            "iliopsoas_total": {
                "voxel_count": total_voxels,
                "volume_mm3": total_mm3,
                "volume_cm3": total_cm3,
                "volume_cm3_per_m3": normalize_volume_cm3_per_m3(total_cm3, height_m),
            },
            "warnings": warnings,
        }
        write_json(total_dir / "metrics.json", metrics)
        print(f"Total artifacts written under: {total_dir}")
    except Exception as exc:
        write_failure_status(
            path=total_dir / "status.json",
            reason=str(exc),
            trace=traceback.format_exc(),
            stdout_log=stdout_path if stdout_path.exists() else None,
            stderr_log=stderr_path if stderr_path.exists() else None,
        )
        print(f"Total post-processing failed. Details written to: {total_dir / 'status.json'}")

