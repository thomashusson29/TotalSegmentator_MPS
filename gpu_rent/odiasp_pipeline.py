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
    ABDOMINAL_TASK,
    ODIASP_LABELS_BASE,
    ODIASP_LABELS_WITH_TISSUE,
    TOTAL_TASK,
    choose_mid_slice_index,
    filled_mask,
    largest_connected_component,
    mean_hu_or_none,
    nifti_data_xyz,
    nifti_spacing_xyz,
    normalize_area_cm2_per_m2,
    pixel_count_to_area_cm2,
    read_log_tail,
    resample_ct_to_reference_xyz,
    reverse_label_map,
    round_or_none,
    run_totalseg_inference,
    save_nifti_like,
    total_label_map,
    write_failure_status,
    write_json,
    write_segmentation_bundle_artifacts,
)


ODIASP_INCLUDED_LABELS = [
    "rectus_abdominis_right",
    "rectus_abdominis_left",
    "external_oblique_right",
    "external_oblique_left",
    "internal_oblique_right",
    "internal_oblique_left",
    "erector_spinae_right",
    "erector_spinae_left",
    "psoas_major_right",
    "psoas_major_left",
    "quadratus_lumborum_right",
    "quadratus_lumborum_left",
]


def _vertebral_body_mask(vertebra_slice: np.ndarray) -> np.ndarray:
    mask = largest_connected_component(vertebra_slice > 0)
    mask = filled_mask(mask)
    if not np.any(mask):
        return mask
    ys, xs = np.where(mask)
    y_min, y_max = int(ys.min()), int(ys.max())
    x_min, x_max = int(xs.min()), int(xs.max())
    y_center = int(round(float(ys.mean())))
    x_center = int(round(float(xs.mean())))
    half_height = max(1, int(round((y_max - y_min + 1) * 0.25)))
    half_width = max(1, int(round((x_max - x_min + 1) * 0.25)))
    y0 = max(y_min, y_center - half_height)
    y1 = min(y_max + 1, y_center + half_height)
    x0 = max(x_min, x_center - half_width)
    x1 = min(x_max + 1, x_center + half_width)
    roi = np.zeros_like(mask, dtype=bool)
    roi[y0:y1, x0:x1] = True
    candidate = roi & mask
    return candidate if np.any(candidate) else mask


def _measure_tissue_slice_label(
    tissue_slice: np.ndarray,
    label_id: int,
    pixel_spacing_mm: tuple[float, float],
    ct_slice: np.ndarray,
    height_m: float | None,
) -> dict:
    mask = tissue_slice == label_id
    pixel_count = int(np.count_nonzero(mask))
    area_cm2 = pixel_count_to_area_cm2(pixel_count, pixel_spacing_mm)
    return {
        "label_id": label_id,
        "pixel_count": pixel_count,
        "area_cm2": area_cm2,
        "area_cm2_per_m2": normalize_area_cm2_per_m2(area_cm2, height_m),
        "mean_hu": mean_hu_or_none(ct_slice, mask),
    }


def _build_tissue_l3_composition(
    *,
    bundle_dir: Path,
    l3_slice_index: int,
    pixel_spacing_mm: tuple[float, float],
    ct_slice: np.ndarray,
    expected_shape: tuple[int, int],
    height_m: float | None,
) -> tuple[dict | None, list[str]]:
    warnings: list[str] = []
    tissue_dir = bundle_dir / "tissue"
    tissue_status = tissue_dir / "status.json"
    if tissue_status.exists():
        payload = json.loads(tissue_status.read_text(encoding="utf-8"))
        warnings.append(f"Tissue enrichment unavailable: {payload.get('reason', 'unknown tissue failure')}")
        return None, warnings

    tissue_nifti = tissue_dir / "tissue_4_types_original_multilabel.nii.gz"
    if not tissue_nifti.exists():
        warnings.append("Tissue enrichment unavailable: tissue_4_types_original_multilabel.nii.gz is missing.")
        return None, warnings

    _, tissue_xyz = nifti_data_xyz(tissue_nifti)
    if tissue_xyz.shape[:2] != expected_shape or l3_slice_index >= tissue_xyz.shape[2]:
        warnings.append("Tissue enrichment unavailable: tissue geometry is incompatible with the ODIASP reference slice.")
        return None, warnings

    tissue_slice = tissue_xyz[:, :, l3_slice_index]
    payload = {
        "source_task": "tissue_4_types",
        "uses_same_l3_slice_as_odiasp": True,
        "slice_index": int(l3_slice_index),
        "subcutaneous_fat": _measure_tissue_slice_label(tissue_slice, 1, pixel_spacing_mm, ct_slice, height_m),
        "torso_fat": _measure_tissue_slice_label(tissue_slice, 2, pixel_spacing_mm, ct_slice, height_m),
        "intermuscular_fat": _measure_tissue_slice_label(tissue_slice, 4, pixel_spacing_mm, ct_slice, height_m),
        "skeletal_muscle_tissue_4_types": _measure_tissue_slice_label(tissue_slice, 3, pixel_spacing_mm, ct_slice, height_m),
    }
    payload["vat_approx"] = {
        "derived_from": "torso_fat",
        "area_cm2": payload["torso_fat"]["area_cm2"],
        "area_cm2_per_m2": payload["torso_fat"]["area_cm2_per_m2"],
        "mean_hu": payload["torso_fat"]["mean_hu"],
    }
    sat_area = payload["subcutaneous_fat"]["area_cm2"]
    torso_area = payload["torso_fat"]["area_cm2"]
    payload["torso_to_subcutaneous_area_ratio"] = round(float(torso_area / sat_area), 5) if sat_area else None
    warnings.append(
        "VAT approximation: TotalSegmentator tissue_4_types exposes torso_fat rather than an official visceral_adipose_tissue label, so vat_approx is derived directly from torso_fat."
    )
    return payload, warnings


def _save_axial_preview(
    path: Path,
    ct_slice: np.ndarray,
    muscle_mask: np.ndarray,
    vertebra_mask: np.ndarray,
    tissue_masks: dict[str, np.ndarray],
    l3_slice_index: int,
) -> None:
    figure, axis = plt.subplots(figsize=(8, 8))
    axis.imshow(ct_slice.T, cmap="gray", origin="lower")
    axis.imshow(np.ma.masked_where(~muscle_mask.T, muscle_mask.T), cmap="Reds", origin="lower", alpha=0.35)
    axis.imshow(np.ma.masked_where(~vertebra_mask.T, vertebra_mask.T), cmap="Blues", origin="lower", alpha=0.30)
    for name, mask in tissue_masks.items():
        if not np.any(mask):
            continue
        cmap = {
            "subcutaneous": "Greens",
            "torso": "Purples",
            "intermuscular": "Oranges",
        }.get(name, "viridis")
        axis.imshow(np.ma.masked_where(~mask.T, mask.T), cmap=cmap, origin="lower", alpha=0.25)
    axis.set_title(f"ODIASP axial L3 slice z={l3_slice_index}")
    axis.axis("off")
    figure.tight_layout()
    figure.savefig(path, dpi=160)
    plt.close(figure)


def _save_sagittal_preview(path: Path, ct_sagittal: np.ndarray, vertebra_mask_sagittal: np.ndarray, l3_slice_index: int, sagittal_x_index: int) -> None:
    figure, axis = plt.subplots(figsize=(8, 6))
    axis.imshow(ct_sagittal.T, cmap="gray", origin="lower")
    axis.imshow(np.ma.masked_where(~vertebra_mask_sagittal.T, vertebra_mask_sagittal.T), cmap="Blues", origin="lower", alpha=0.35)
    axis.axhline(l3_slice_index, color="yellow", linewidth=1.5)
    axis.set_title(f"ODIASP sagittal x={sagittal_x_index}")
    axis.axis("off")
    figure.tight_layout()
    figure.savefig(path, dpi=160)
    plt.close(figure)


def run_odiasp_postprocess(
    *,
    input_dicom: Path,
    bundle_dir: Path,
    abdominal_nifti: Path,
    device: str,
    height_cm: float | None,
    use_tissue_metrics: bool,
) -> None:
    odiasp_dir = bundle_dir / "odiasp"
    odiasp_dir.mkdir(parents=True, exist_ok=True)
    stdout_log = odiasp_dir / "source_vertebrae_L3_stdout.log"
    stderr_log = odiasp_dir / "source_vertebrae_L3_stderr.log"

    try:
        abdominal_image, abdominal_xyz = nifti_data_xyz(abdominal_nifti)
        abdominal_labels = total_label_map(ABDOMINAL_TASK)
        abdominal_reverse = reverse_label_map(abdominal_labels)
        pixel_spacing = nifti_spacing_xyz(abdominal_image)[:2]
        height_m = round_or_none(height_cm / 100.0) if height_cm else None

        vertebra_source_nifti = odiasp_dir / "source_vertebrae_L3_multilabel.nii.gz"
        run_totalseg_inference(
            input_path=input_dicom,
            output_path=vertebra_source_nifti,
            task=TOTAL_TASK,
            device=device,
            command_path=odiasp_dir / "source_vertebrae_L3_command.txt",
            stdout_path=stdout_log,
            stderr_path=stderr_log,
            roi_subset=["vertebrae_L3"],
        )

        _, vertebra_xyz = nifti_data_xyz(vertebra_source_nifti)
        vertebra_mask_xyz = vertebra_xyz > 0
        l3_slice_index = choose_mid_slice_index(vertebra_mask_xyz)

        included_label_ids = [abdominal_reverse[name] for name in ODIASP_INCLUDED_LABELS if name in abdominal_reverse]
        muscle_mask_xyz = np.isin(abdominal_xyz, included_label_ids)
        muscle_slice = muscle_mask_xyz[:, :, l3_slice_index]
        vertebra_slice = vertebra_mask_xyz[:, :, l3_slice_index]
        if not np.any(vertebra_slice):
            raise RuntimeError("vertebrae_L3 mask is empty on the computed midpoint slice.")

        native_ct_xyz = resample_ct_to_reference_xyz(input_dicom, abdominal_nifti)
        ct_slice = native_ct_xyz[:, :, l3_slice_index]

        muscle_pixel_count = int(np.count_nonzero(muscle_slice))
        vertebra_pixel_count = int(np.count_nonzero(vertebra_slice))
        sma_cm2 = pixel_count_to_area_cm2(muscle_pixel_count, pixel_spacing)
        smi = normalize_area_cm2_per_m2(sma_cm2, height_m)
        smd_hu = mean_hu_or_none(ct_slice, muscle_slice)
        vertebra_mean_hu = mean_hu_or_none(ct_slice, vertebra_slice)
        vertebral_body_mask = _vertebral_body_mask(vertebra_slice)
        vertebral_body_mean_hu = mean_hu_or_none(ct_slice, vertebral_body_mask) or vertebra_mean_hu

        l3_tissue_composition = None
        warnings = [
            "ODIASP-compatible approximation: TotalSegmentator abdominal_muscles does not expose transversus_abdominis, so v1 excludes it instead of substituting another muscle."
        ]
        tissue_overlay_masks: dict[str, np.ndarray] = {}
        odiasp_labels = ODIASP_LABELS_BASE.copy()
        if use_tissue_metrics:
            l3_tissue_composition, tissue_warnings = _build_tissue_l3_composition(
                bundle_dir=bundle_dir,
                l3_slice_index=l3_slice_index,
                pixel_spacing_mm=(pixel_spacing[0], pixel_spacing[1]),
                ct_slice=ct_slice,
                expected_shape=(abdominal_xyz.shape[0], abdominal_xyz.shape[1]),
                height_m=height_m,
            )
            warnings.extend(tissue_warnings)
            if l3_tissue_composition is not None:
                odiasp_labels = ODIASP_LABELS_WITH_TISSUE.copy()
                tissue_dir = bundle_dir / "tissue"
                _, tissue_xyz = nifti_data_xyz(tissue_dir / "tissue_4_types_original_multilabel.nii.gz")
                tissue_slice = tissue_xyz[:, :, l3_slice_index]
                tissue_overlay_masks = {
                    "subcutaneous": tissue_slice == 1,
                    "torso": tissue_slice == 2,
                    "intermuscular": tissue_slice == 4,
                }

        odiasp_xyz = np.zeros(abdominal_xyz.shape, dtype=np.int16)
        odiasp_xyz[:, :, l3_slice_index][muscle_slice] = 1
        odiasp_xyz[:, :, l3_slice_index][vertebra_slice] = 2
        if l3_tissue_composition is not None:
            odiasp_xyz[:, :, l3_slice_index][tissue_overlay_masks["subcutaneous"]] = 3
            odiasp_xyz[:, :, l3_slice_index][tissue_overlay_masks["torso"]] = 4
            odiasp_xyz[:, :, l3_slice_index][tissue_overlay_masks["intermuscular"]] = 5

        odiasp_nifti = odiasp_dir / "ODIASP_multilabel.nii.gz"
        nib.save(nib.Nifti1Image(odiasp_xyz.astype(np.int16), abdominal_image.affine, abdominal_image.header.copy()), str(odiasp_nifti))
        write_segmentation_bundle_artifacts(
            bundle_dir=odiasp_dir,
            task="ODIASP",
            source_task="odiasp_compatible",
            segmentation_name="ODIASP",
            nifti_path=odiasp_nifti,
            color_table_name="ODIASP.ctbl",
            labels_json_name="labels.json",
            label_map=odiasp_labels,
        )

        x_indices = np.where(vertebra_mask_xyz.any(axis=(1, 2)))[0]
        sagittal_x_index = int(x_indices[len(x_indices) // 2]) if x_indices.size else int(abdominal_xyz.shape[0] // 2)
        _save_axial_preview(
            odiasp_dir / "preview_axial.png",
            ct_slice,
            muscle_slice,
            vertebra_slice,
            tissue_overlay_masks,
            l3_slice_index,
        )
        _save_sagittal_preview(
            odiasp_dir / "preview_sagittal.png",
            native_ct_xyz[sagittal_x_index, :, :],
            vertebra_mask_xyz[sagittal_x_index, :, :],
            l3_slice_index,
            sagittal_x_index,
        )

        metrics = {
            "method": "ODIASP-compatible pipeline using TotalSegmentator vertebrae_L3 midpoint selection and a L3 single-slice muscle union derived from abdominal_muscles.",
            "odiasp_compatible": True,
            "task": "ODIASP",
            "l3_slice_index": int(l3_slice_index),
            "slice_axis": "z",
            "voxel_spacing_mm": [round_or_none(v) for v in nifti_spacing_xyz(abdominal_image)],
            "pixel_spacing_mm": [round_or_none(pixel_spacing[0]), round_or_none(pixel_spacing[1])],
            "sma_cm2": sma_cm2,
            "csma_cm2": sma_cm2,
            "height_cm": round_or_none(height_cm) if height_cm else None,
            "height_m": height_m,
            "smi_cm2_per_m2": smi,
            "smd_hu": smd_hu,
            "l3_bone_density_vertebra_mean_hu": vertebra_mean_hu,
            "l3_bone_density_vertebral_body_mean_hu": vertebral_body_mean_hu,
            "muscle_pixel_count": muscle_pixel_count,
            "vertebra_pixel_count": vertebra_pixel_count,
            "included_labels": included_label_ids,
            "l3_tissue_composition": l3_tissue_composition,
            "warnings": warnings,
            "preview_axial": "preview_axial.png",
            "preview_sagittal": "preview_sagittal.png",
            "preview_l3_slice_index_ras": int(l3_slice_index),
            "preview_sagittal_x_index_ras": int(sagittal_x_index),
        }
        write_json(odiasp_dir / "metrics.json", metrics)
        print(f"ODIASP artifacts written under: {odiasp_dir}")
    except Exception as exc:
        write_failure_status(
            path=odiasp_dir / "status.json",
            reason=str(exc),
            trace=traceback.format_exc(),
            stdout_log=stdout_log if stdout_log.exists() else None,
            stderr_log=stderr_log if stderr_log.exists() else None,
        )
        print(f"ODIASP post-processing failed. Details written to: {odiasp_dir / 'status.json'}")

