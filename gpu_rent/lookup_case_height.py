#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
from pathlib import Path


def parse_args() -> argparse.Namespace:
    repo_root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(
        description="Lookup height_cm for a PAT_xxxx_CASE_xx anonymized case from a metadata CSV."
    )
    parser.add_argument("--case-code", help="PAT_xxxx_CASE_xx code. Optional if --case-dir is provided.")
    parser.add_argument("--case-dir", type=Path, help="Path to the anonymized case directory.")
    parser.add_argument(
        "--metadata-csv",
        type=Path,
        default=repo_root / "anonymized_exports" / "tdm_elena_savier_anonymized" / "case_metadata.csv",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    case_code = args.case_code or (args.case_dir.name if args.case_dir else "")
    if not case_code:
        raise SystemExit("Provide --case-code or --case-dir.")
    with args.metadata_csv.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter=";")
        for row in reader:
            if row.get("case_code") == case_code:
                height_cm = (row.get("height_cm") or "").strip()
                if not height_cm:
                    raise SystemExit(f"No height found for {case_code} in {args.metadata_csv}")
                print(height_cm)
                return 0
    raise SystemExit(f"Case {case_code} not found in {args.metadata_csv}")


if __name__ == "__main__":
    raise SystemExit(main())
