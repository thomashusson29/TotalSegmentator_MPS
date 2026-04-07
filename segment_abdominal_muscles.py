#!/usr/bin/env python3

from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path

from run_totalseg_dicom import OUTPUT_ROOT, run_pipeline, write_text


LATEST_SYMLINK = OUTPUT_ROOT / "latest_abdominal_muscles"
LATEST_TEXT = OUTPUT_ROOT / "latest_abdominal_muscles.txt"
TASK = "abdominal_muscles"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run TotalSegmentator on a DICOM series to isolate abdominal muscles with Apple Silicon MPS."
    )
    parser.add_argument(
        "--input-dicom",
        required=True,
        type=Path,
        help="Path to the input DICOM series directory.",
    )
    parser.add_argument(
        "--output-root",
        default=OUTPUT_ROOT,
        type=Path,
        help=f"Directory where result bundles are created. Default: {OUTPUT_ROOT}",
    )
    parser.add_argument(
        "--bundle-name",
        default=None,
        help="Optional bundle directory name. By default a timestamped name is generated automatically.",
    )
    return parser.parse_args()


def build_bundle_name(input_dicom: Path) -> str:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{TASK}_{input_dicom.name}_{timestamp}"


def update_latest_pointers(bundle_dir: Path) -> None:
    bundle_dir = bundle_dir.resolve()
    LATEST_SYMLINK.parent.mkdir(parents=True, exist_ok=True)

    if LATEST_SYMLINK.exists() or LATEST_SYMLINK.is_symlink():
        LATEST_SYMLINK.unlink()
    LATEST_SYMLINK.symlink_to(bundle_dir, target_is_directory=True)
    write_text(LATEST_TEXT, str(bundle_dir) + "\n")


def main() -> int:
    args = parse_args()
    bundle_name = args.bundle_name or build_bundle_name(args.input_dicom)
    bundle_dir = args.output_root / bundle_name
    run_pipeline(args.input_dicom, bundle_dir, TASK)
    update_latest_pointers(bundle_dir)
    print(f"Latest bundle pointer updated: {LATEST_SYMLINK} -> {bundle_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
