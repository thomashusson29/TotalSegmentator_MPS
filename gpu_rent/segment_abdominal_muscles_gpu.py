#!/usr/bin/env python3

from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path

from .abdominal_muscles_metrics import build_abdominal_muscles_metrics
from .common import (
    ABDOMINAL_TASK,
    DEFAULT_OUTPUT_ROOT,
    read_dicom_image,
    resample_ct_to_reference_xyz,
    resolve_device_request,
    round_or_none,
    run_totalseg_inference,
    total_label_map,
    write_json,
    write_latest_pointers,
    write_segmentation_bundle_artifacts,
)
from .metrics_csv import export_case_metrics_csv
from .odiasp_pipeline import run_odiasp_postprocess
from .postprocess_bundle import install_portable_bundle_importer
from .tissue_pipeline import run_tissue_postprocess
from .total_pipeline import run_total_postprocess


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the complete abdominal TotalSegmentator pipeline on Linux/CUDA/RunPod without relying on the legacy MPS-only wrappers."
    )
    parser.add_argument("--input-dicom", required=True, type=Path, help="Path to the input DICOM directory.")
    parser.add_argument("--output-root", default=DEFAULT_OUTPUT_ROOT, type=Path, help="Directory where bundles are created.")
    parser.add_argument("--bundle-name", default=None, help="Optional bundle directory name.")
    parser.add_argument("--device", default="auto", help="TotalSegmentator device: auto, gpu, gpu:0, mps, cpu.")
    parser.add_argument("--with-muscles", action="store_true", help="Expose abdominal_muscles as a public output.")
    parser.add_argument("--with-odiasp", action="store_true", help="Generate the ODIASP-compatible sub-bundle.")
    parser.add_argument("--with-tissue", action="store_true", help="Generate the tissue_4_types sub-bundle.")
    parser.add_argument("--with-total", action="store_true", help="Generate the full total sub-bundle.")
    parser.add_argument("--with-tocsv", action="store_true", help="Export all available metrics into a CSV row.")
    parser.add_argument("--height-cm", type=float, default=None, help="Optional patient height in centimetres.")
    parser.add_argument("--totalseg-license-number", default=None, help="Optional TotalSegmentator commercial license number.")
    return parser.parse_args()


def build_bundle_name(input_dicom: Path) -> str:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{ABDOMINAL_TASK}_{input_dicom.name}_{timestamp}"


def resolve_requested_outputs(args: argparse.Namespace) -> tuple[bool, bool, bool, bool]:
    requested_any = args.with_muscles or args.with_odiasp or args.with_tissue or args.with_total
    if not requested_any:
        return True, False, False, False
    return args.with_muscles, args.with_odiasp, args.with_tissue, args.with_total


def run_abdominal_muscles_pipeline(
    *,
    input_dicom: Path,
    bundle_dir: Path,
    device: str,
    public_output: bool,
    height_cm: float | None,
) -> Path:
    bundle_dir.mkdir(parents=True, exist_ok=True)
    abdominal_nifti = bundle_dir / "abdominal_muscles_multilabel.nii.gz"

    run_totalseg_inference(
        input_path=input_dicom,
        output_path=abdominal_nifti,
        task=ABDOMINAL_TASK,
        device=device,
        command_path=bundle_dir / "command.txt",
        stdout_path=bundle_dir / "stdout.log",
        stderr_path=bundle_dir / "stderr.log",
    )

    if public_output:
        write_segmentation_bundle_artifacts(
            bundle_dir=bundle_dir,
            task=ABDOMINAL_TASK,
            source_task=ABDOMINAL_TASK,
            segmentation_name="abdominal muscles",
            nifti_path=abdominal_nifti,
            color_table_name="abdominal_muscles.ctbl",
            labels_json_name="labels.json",
            label_map=total_label_map(ABDOMINAL_TASK),
        )

    native_ct_xyz = resample_ct_to_reference_xyz(input_dicom, abdominal_nifti)
    metrics = build_abdominal_muscles_metrics(
        input_dicom=input_dicom,
        abdominal_nifti=abdominal_nifti,
        height_cm=height_cm,
        native_ct_xyz=native_ct_xyz,
    )
    write_json(bundle_dir / "abdominal_muscles_metrics.json", metrics)

    if public_output:
        print(f"Finished successfully. Outputs are under: {bundle_dir}")
    else:
        print(f"Finished successfully. Dependency outputs are under: {bundle_dir}")
    return abdominal_nifti


def main() -> int:
    args = parse_args()
    if args.height_cm is not None and args.height_cm <= 0:
        raise SystemExit("--height-cm must be strictly positive.")

    with_muscles, with_odiasp, with_tissue, with_total = resolve_requested_outputs(args)
    bundle_name = args.bundle_name or build_bundle_name(args.input_dicom)
    bundle_dir = args.output_root / bundle_name
    bundle_dir.mkdir(parents=True, exist_ok=True)

    resolved_device = resolve_device_request(args.device)
    print(f"Resolved TotalSegmentator device: {resolved_device}")

    needs_abdominal = with_muscles or with_odiasp or with_tissue
    abdominal_nifti: Path | None = None
    if needs_abdominal:
        abdominal_nifti = run_abdominal_muscles_pipeline(
            input_dicom=args.input_dicom,
            bundle_dir=bundle_dir,
            device=resolved_device,
            public_output=with_muscles,
            height_cm=args.height_cm,
        )

    if with_tissue:
        if abdominal_nifti is None:
            raise RuntimeError("Internal error: tissue pipeline requested without abdominal_muscles dependency.")
        run_tissue_postprocess(
            input_dicom=args.input_dicom,
            bundle_dir=bundle_dir,
            abdominal_nifti=abdominal_nifti,
            device=resolved_device,
            height_cm=args.height_cm,
            license_number=args.totalseg_license_number,
        )

    if with_odiasp:
        if abdominal_nifti is None:
            raise RuntimeError("Internal error: ODIASP pipeline requested without abdominal_muscles dependency.")
        run_odiasp_postprocess(
            input_dicom=args.input_dicom,
            bundle_dir=bundle_dir,
            abdominal_nifti=abdominal_nifti,
            device=resolved_device,
            height_cm=args.height_cm,
            use_tissue_metrics=with_tissue,
        )

    if with_total:
        run_total_postprocess(
            input_dicom=args.input_dicom,
            bundle_dir=bundle_dir,
            device=resolved_device,
            height_cm=args.height_cm,
        )

    install_portable_bundle_importer(bundle_dir)
    write_latest_pointers(args.output_root, bundle_dir)
    print(f"Latest bundle pointer updated: {args.output_root / 'latest_abdominal_muscles'} -> {bundle_dir}")
    print("Slicer import command:")
    print(f'exec(open("{(bundle_dir / "import_into_slicer.py").resolve()}").read())')

    if args.with_tocsv:
        csv_path = export_case_metrics_csv(
            bundle_dir=bundle_dir,
            input_dicom_dir=args.input_dicom,
            with_muscles=with_muscles,
            with_odiasp=with_odiasp,
            with_tissue=with_tissue,
            with_total=with_total,
            with_tocsv=True,
        )
        print(f"CSV metrics updated: {csv_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

