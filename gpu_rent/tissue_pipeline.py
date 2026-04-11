#!/usr/bin/env python3

from __future__ import annotations

import json
import traceback
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import nibabel as nib
import numpy as np

from .common import (
    TISSUE_LABELS,
    TISSUE_TASK,
    nifti_data_xyz,
    nifti_spacing_xyz,
    normalize_volume_cm3_per_m3,
    read_log_tail,
    resample_ct_to_reference_xyz,
    round_or_none,
    run_totalseg_inference,
    save_nifti_like,
    total_label_map,
    voxel_volume_mm3,
    write_failure_status,
    write_json,
    write_segmentation_bundle_artifacts,
)


def _measure_tissues(
    *,
    final_nifti: Path,
    native_ct_xyz: np.ndarray,
    height_cm: float | None,
) -> dict:
    image, data_xyz = nifti_data_xyz(final_nifti)
    spacing_xyz = nifti_spacing_xyz(image)
    voxel_mm3 = voxel_volume_mm3(image)
    height_m = round_or_none(height_cm / 100.0) if height_cm else None

    tissues: dict[str, dict] = {}
    for label_id, label_name in sorted(TISSUE_LABELS.items()):
        mask = data_xyz == label_id
        voxel_count = int(np.count_nonzero(mask))
        volume_mm3 = round_or_none(voxel_count * voxel_mm3)
        volume_cm3 = round_or_none(volume_mm3 / 1000.0 if volume_mm3 is not None else None)
        mean_hu = round_or_none(float(native_ct_xyz[mask].mean())) if voxel_count else None
        tissues[label_name] = {
            "label_id": label_id,
            "voxel_count": voxel_count,
            "volume_mm3": volume_mm3,
            "volume_cm3": volume_cm3,
            "volume_cm3_per_m3": normalize_volume_cm3_per_m3(volume_cm3, height_m),
            "mean_hu": mean_hu,
        }

    warnings: list[str] = []
    if not height_m:
        warnings.append("Height was not provided; height-normalized tissue volumes are left empty.")

    return {
        "height_cm": round_or_none(height_cm) if height_cm else None,
        "height_m": height_m,
        "voxel_spacing_mm": [round_or_none(v) for v in spacing_xyz],
        "tissues": tissues,
        "warnings": warnings,
    }


def _save_axial_preview(path: Path, ct_slice: np.ndarray, label_slice: np.ndarray, title: str, z_index: int) -> None:
    figure, axis = plt.subplots(figsize=(8, 8))
    axis.imshow(ct_slice.T, cmap="gray", origin="lower")
    axis.imshow(np.ma.masked_where(label_slice.T == 0, label_slice.T), cmap="tab10", origin="lower", alpha=0.45, interpolation="nearest")
    axis.set_title(f"{title} axial z={z_index}")
    axis.axis("off")
    figure.tight_layout()
    figure.savefig(path, dpi=160)
    plt.close(figure)


def _save_sagittal_preview(path: Path, ct_sagittal: np.ndarray, z_min: int, z_max: int, x_index: int, title: str) -> None:
    figure, axis = plt.subplots(figsize=(8, 6))
    axis.imshow(ct_sagittal.T, cmap="gray", origin="lower")
    axis.axhline(z_min, color="cyan", linewidth=1.5)
    axis.axhline(z_max, color="cyan", linewidth=1.5)
    axis.set_title(f"{title} sagittal x={x_index}")
    axis.axis("off")
    figure.tight_layout()
    figure.savefig(path, dpi=160)
    plt.close(figure)


def _write_variant(
    *,
    tissue_dir: Path,
    variant: str,
    source_task: str,
    segmentation_name: str,
    input_source: Path,
    final_nifti: Path,
    source_nifti: Path | None,
    reference_image: nib.Nifti1Image,
    native_ct_xyz: np.ndarray,
    device: str,
    height_cm: float | None,
    z_min: int,
    z_max: int,
    input_shape: list[int],
    cropped_shape: list[int],
    crop_strategy: str,
    license_number: str | None,
) -> dict:
    suffix = variant
    if variant == "original":
        command_path = tissue_dir / "command_original.txt"
        stdout_path = tissue_dir / "stdout_original.log"
        stderr_path = tissue_dir / "stderr_original.log"
        statistics_path = tissue_dir / "statistics_original.json"
        preview_axial = tissue_dir / "preview_axial_original.png"
        preview_sagittal = tissue_dir / "preview_sagittal_original.png"
        labels_name = "tissue_4_types_original_labels.json"
        color_name = "tissue_4_types_original.ctbl"
    else:
        command_path = tissue_dir / "command_T4_L4.txt"
        stdout_path = tissue_dir / "stdout_T4_L4.log"
        stderr_path = tissue_dir / "stderr_T4_L4.log"
        statistics_path = tissue_dir / "statistics_T4_L4.json"
        preview_axial = tissue_dir / "preview_axial_T4_L4.png"
        preview_sagittal = tissue_dir / "preview_sagittal_T4_L4.png"
        labels_name = "tissue_4_types_T4_L4_labels.json"
        color_name = "tissue_4_types_T4_L4.ctbl"

    run_totalseg_inference(
        input_path=input_source,
        output_path=source_nifti if source_nifti is not None else final_nifti,
        task=TISSUE_TASK,
        device=device,
        command_path=command_path,
        stdout_path=stdout_path,
        stderr_path=stderr_path,
        statistics_path=statistics_path,
        stats_include_incomplete=True,
        license_number=license_number,
    )

    if source_nifti is not None:
        source_image, source_data = nifti_data_xyz(source_nifti)
        full_data = np.zeros(reference_image.shape, dtype=np.int16)
        full_data[:, :, z_min : z_max + 1] = source_data.astype(np.int16)
        nib.save(nib.Nifti1Image(full_data, reference_image.affine, reference_image.header.copy()), str(final_nifti))

    write_segmentation_bundle_artifacts(
        bundle_dir=tissue_dir,
        task=f"tissue_4_types_{variant}",
        source_task=source_task,
        segmentation_name=segmentation_name,
        nifti_path=final_nifti,
        color_table_name=color_name,
        labels_json_name=labels_name,
        label_map=TISSUE_LABELS,
    )

    metrics = _measure_tissues(final_nifti=final_nifti, native_ct_xyz=native_ct_xyz, height_cm=height_cm)
    axial_z_index = (z_min + z_max) // 2
    sagittal_x_index = int(reference_image.shape[0] // 2)
    _save_axial_preview(preview_axial, native_ct_xyz[:, :, axial_z_index], np.asarray(nib.load(str(final_nifti)).dataobj)[:, :, axial_z_index], segmentation_name, axial_z_index)
    _save_sagittal_preview(preview_sagittal, native_ct_xyz[sagittal_x_index, :, :], z_min, z_max, sagittal_x_index, segmentation_name)

    metrics_payload = {
        "method": (
            "tissue_4_types pipeline on the full native scanner volume without z-cropping."
            if variant == "original"
            else "tissue_4_types pipeline using the superior and inferior z-limits defined by the abdominal_muscles segmentation, while preserving the native x/y field of view."
        ),
        "task": TISSUE_TASK,
        "source_task": source_task,
        "segmentation_name": segmentation_name,
        "variant": variant,
        "crop_strategy": crop_strategy,
        "height_cm": metrics["height_cm"],
        "height_m": metrics["height_m"],
        "z_min": int(z_min),
        "z_max": int(z_max),
        "slice_count": int(z_max - z_min + 1),
        "input_shape": input_shape,
        "cropped_shape": cropped_shape,
        "voxel_spacing_mm": metrics["voxel_spacing_mm"],
        "tissues": metrics["tissues"],
        "warnings": metrics["warnings"],
        "preview_axial": preview_axial.name,
        "preview_sagittal": preview_sagittal.name,
        "preview_axial_z_index_ras": int(axial_z_index),
        "preview_sagittal_x_index_ras": int(sagittal_x_index),
    }
    metrics_name = "metrics_original.json" if variant == "original" else "metrics_T4_L4.json"
    write_json(tissue_dir / metrics_name, metrics_payload)

    manifest_entry = {
        "id": f"tissue_4_types_{variant}",
        "task": f"tissue_4_types_{variant}",
        "source_task": source_task,
        "segmentation_name": segmentation_name,
        "multilabel_nifti": final_nifti.name,
        "color_table": color_name,
        "labels_json": labels_name,
        "labels": {str(k): v for k, v in sorted(TISSUE_LABELS.items())},
        "roi_subset": [],
        "variant": variant,
        "statistics": statistics_path.name,
        "metrics": metrics_name,
        "command_file": command_path.name,
        "stdout_log": stdout_path.name,
        "stderr_log": stderr_path.name,
        "preview_axial": preview_axial.name,
        "preview_sagittal": preview_sagittal.name,
    }
    if source_nifti is not None:
        manifest_entry["source_ct"] = "source_T4_L4_ct.nii.gz"
        manifest_entry["source_multilabel_nifti"] = source_nifti.name
    return manifest_entry


def run_tissue_postprocess(
    *,
    input_dicom: Path,
    bundle_dir: Path,
    abdominal_nifti: Path,
    device: str,
    height_cm: float | None,
    license_number: str | None = None,
) -> None:
    tissue_dir = bundle_dir / "tissue"
    tissue_dir.mkdir(parents=True, exist_ok=True)

    stdout_original = tissue_dir / "stdout_original.log"
    stderr_original = tissue_dir / "stderr_original.log"
    stdout_t4 = tissue_dir / "stdout_T4_L4.log"
    stderr_t4 = tissue_dir / "stderr_T4_L4.log"

    try:
        abdominal_image, abdominal_data = nifti_data_xyz(abdominal_nifti)
        nonzero_z = np.where((abdominal_data > 0).any(axis=(0, 1)))[0]
        if nonzero_z.size == 0:
            raise RuntimeError("abdominal_muscles segmentation is empty; cannot define T4_L4 z-slab.")

        z_min = int(nonzero_z[0])
        z_max = int(nonzero_z[-1])
        input_shape = list(abdominal_data.shape)
        cropped_shape = [int(abdominal_data.shape[0]), int(abdominal_data.shape[1]), int(z_max - z_min + 1)]

        original_nifti = tissue_dir / "tissue_4_types_original_multilabel.nii.gz"
        t4_source_ct = tissue_dir / "source_T4_L4_ct.nii.gz"
        t4_source_nifti = tissue_dir / "source_tissue_4_types_T4_L4_multilabel.nii.gz"
        t4_final_nifti = tissue_dir / "tissue_4_types_T4_L4_multilabel.nii.gz"

        native_ct_xyz = resample_ct_to_reference_xyz(input_dicom, abdominal_nifti)
        cropped_ct = native_ct_xyz[:, :, z_min : z_max + 1]
        cropped_affine = abdominal_image.affine.copy()
        cropped_affine[:3, 3] = abdominal_image.affine[:3, 3] + z_min * abdominal_image.affine[:3, 2]
        cropped_reference = nib.Nifti1Image(cropped_ct.astype(np.float32), cropped_affine, abdominal_image.header.copy())
        save_nifti_like(t4_source_ct, cropped_ct, cropped_reference)

        manifest = {"bundle_type": "tissue_bundle", "outputs": []}
        manifest["outputs"].append(
            _write_variant(
                tissue_dir=tissue_dir,
                variant="original",
                source_task=TISSUE_TASK,
                segmentation_name="Tissue 4 Types Original",
                input_source=input_dicom,
                final_nifti=original_nifti,
                source_nifti=None,
                reference_image=abdominal_image,
                native_ct_xyz=native_ct_xyz,
                device=device,
                height_cm=height_cm,
                z_min=0,
                z_max=int(abdominal_data.shape[2] - 1),
                input_shape=input_shape,
                cropped_shape=input_shape,
                crop_strategy="none",
                license_number=license_number,
            )
        )

        manifest["outputs"].append(
            _write_variant(
                tissue_dir=tissue_dir,
                variant="T4_L4",
                source_task=TISSUE_TASK,
                segmentation_name="Tissue 4 Types T4_L4",
                input_source=t4_source_ct,
                final_nifti=t4_final_nifti,
                source_nifti=t4_source_nifti,
                reference_image=abdominal_image,
                native_ct_xyz=native_ct_xyz,
                device=device,
                height_cm=height_cm,
                z_min=z_min,
                z_max=z_max,
                input_shape=input_shape,
                cropped_shape=cropped_shape,
                crop_strategy="abdominal_muscles_z_extent",
                license_number=license_number,
            )
        )

        if z_min == 0 or z_max == abdominal_data.shape[2] - 1:
            metrics_t4_path = tissue_dir / "metrics_T4_L4.json"
            payload = json.loads(metrics_t4_path.read_text(encoding="utf-8"))
            payload.setdefault("warnings", []).append(
                "The abdominal_muscles-derived T4_L4 z-slab touches the superior or inferior scanner boundary."
            )
            write_json(metrics_t4_path, payload)

        write_json(tissue_dir / "manifest.json", manifest)
        print(f"Tissue artifacts written under: {tissue_dir}")
    except Exception as exc:
        write_failure_status(
            path=tissue_dir / "status.json",
            reason=str(exc),
            trace=traceback.format_exc(),
            stdout_log=stdout_original if stdout_original.exists() else (stdout_t4 if stdout_t4.exists() else None),
            stderr_log=stderr_original if stderr_original.exists() else (stderr_t4 if stderr_t4.exists() else None),
        )
        print(f"Tissue post-processing failed. Details written to: {tissue_dir / 'status.json'}")
