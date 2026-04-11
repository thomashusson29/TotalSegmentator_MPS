#!/usr/bin/env python3

from __future__ import annotations

import csv
from datetime import datetime
from pathlib import Path
from typing import Any


def _join_list(values: list[Any]) -> str:
    return "|".join("" if value is None else str(value) for value in values)


def _flatten(prefix: str, value: Any, out: dict[str, Any]) -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            _flatten(f"{prefix}_{key}" if prefix else key, child, out)
        return

    if isinstance(value, list):
        if prefix.endswith("voxel_spacing_mm") or prefix.endswith("pixel_spacing_mm") or prefix.endswith("input_shape") or prefix.endswith("cropped_shape"):
            axes = ("x", "y", "z")
            for index, item in enumerate(value):
                suffix = axes[index] if index < len(axes) else str(index)
                out[f"{prefix}_{suffix}"] = item
        elif prefix.endswith("included_labels"):
            out[f"{prefix}_ids"] = _join_list(value)
        elif prefix.endswith("included_label_names"):
            out[prefix] = _join_list(value)
        elif prefix.endswith("warnings"):
            out[prefix] = " | ".join(str(item) for item in value if item)
        else:
            out[prefix] = _join_list(value)
        return

    out[prefix] = value


def _status_for(bundle_subdir: Path) -> str:
    if bundle_subdir.exists() and (bundle_subdir / "status.json").exists():
        return "failed"
    if bundle_subdir.exists():
        return "success"
    return "not_requested"


def _load_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    import json

    return json.loads(path.read_text(encoding="utf-8"))


def export_case_metrics_csv(
    *,
    bundle_dir: Path,
    input_dicom_dir: Path,
    with_muscles: bool,
    with_odiasp: bool,
    with_tissue: bool,
    with_total: bool,
    with_tocsv: bool,
) -> Path:
    csv_paths: list[Path] = []
    try:
        csv_paths.append(input_dicom_dir.parent / "segmentation_metrics.csv")
    except Exception:
        pass
    csv_paths.append(bundle_dir.parent / "segmentation_metrics.csv")

    abdominal_metrics = _load_json(bundle_dir / "abdominal_muscles_metrics.json")
    odiasp_metrics = _load_json(bundle_dir / "odiasp" / "metrics.json")
    tissue_original = _load_json(bundle_dir / "tissue" / "metrics_original.json")
    tissue_t4_l4 = _load_json(bundle_dir / "tissue" / "metrics_T4_L4.json")
    total_metrics = _load_json(bundle_dir / "total" / "metrics.json")

    row: dict[str, Any] = {
        "case_id": input_dicom_dir.name,
        "input_dicom_dir": str(input_dicom_dir.resolve()),
        "input_parent_dir": str(input_dicom_dir.parent.resolve()),
        "bundle_dir": str(bundle_dir.resolve()),
        "bundle_name": bundle_dir.name,
        "csv_exported_at": datetime.now().isoformat(timespec="seconds"),
        "requested_with_muscles": with_muscles,
        "requested_with_odiasp": with_odiasp,
        "requested_with_tissue": with_tissue,
        "requested_with_total": with_total,
        "requested_with_tocsv": with_tocsv,
        "muscles_status": "success" if abdominal_metrics else "not_requested",
        "abdominal_muscles_status": "success" if abdominal_metrics else "not_requested",
        "odiasp_status": _status_for(bundle_dir / "odiasp") if with_odiasp else "not_requested",
        "tissue_status": _status_for(bundle_dir / "tissue") if with_tissue else "not_requested",
        "tissue_original_status": "success" if tissue_original else (_status_for(bundle_dir / "tissue") if with_tissue else "not_requested"),
        "tissue_T4_L4_status": "success" if tissue_t4_l4 else (_status_for(bundle_dir / "tissue") if with_tissue else "not_requested"),
        "total_status": _status_for(bundle_dir / "total") if with_total else "not_requested",
    }

    if abdominal_metrics:
        _flatten("abdominal_muscles", abdominal_metrics, row)
    if odiasp_metrics:
        _flatten("odiasp", odiasp_metrics, row)
        if "odiasp_included_labels_ids" in row:
            ids = row.pop("odiasp_included_labels_ids")
            row["odiasp_included_label_ids"] = ids
    if tissue_original:
        _flatten("tissue_original", tissue_original, row)
    if tissue_t4_l4:
        _flatten("tissue_T4_L4", tissue_t4_l4, row)
    if total_metrics:
        _flatten("total", total_metrics, row)
        if "total_labels_used_for_psoas_volume" in row and isinstance(row["total_labels_used_for_psoas_volume"], str):
            pass

    headers = list(row.keys())
    for csv_path in csv_paths:
        csv_path.parent.mkdir(parents=True, exist_ok=True)
        rows: list[dict[str, Any]] = []
        if csv_path.exists():
            with csv_path.open("r", encoding="utf-8", newline="") as handle:
                reader = csv.DictReader(handle, delimiter=";")
                for existing in reader:
                    rows.append(existing)
                existing_headers = reader.fieldnames or []
                for header in existing_headers:
                    if header not in headers:
                        headers.append(header)
        rows = [existing for existing in rows if existing.get("case_id") != row["case_id"]]
        rows.append(row)
        with csv_path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=headers, delimiter=";", extrasaction="ignore")
            writer.writeheader()
            for item in rows:
                normalized = {key: item.get(key, "") for key in headers}
                writer.writerow(normalized)

    return csv_paths[-1]

