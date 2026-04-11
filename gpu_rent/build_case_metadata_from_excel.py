#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
from pathlib import Path
from typing import Dict, Iterator, List, Optional
from xml.etree import ElementTree as ET
from zipfile import ZipFile

import pydicom


NS = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"


def parse_args() -> argparse.Namespace:
    repo_root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(
        description=(
            "Build a non-identifying metadata CSV for anonymized cases by joining "
            "their preserved DICOM PatientID to the source Excel workbook."
        )
    )
    parser.add_argument(
        "--xlsx",
        type=Path,
        default=repo_root / "tdm_elena_savier" / "BDD_memoire_ER_versionThomas.xlsx",
        help="Source workbook containing IPP and height.",
    )
    parser.add_argument(
        "--anonymized-root",
        type=Path,
        default=repo_root / "anonymized_exports" / "tdm_elena_savier_anonymized",
        help="Root directory containing PAT_xxxx_CASE_xx anonymized folders.",
    )
    parser.add_argument(
        "--output-csv",
        type=Path,
        default=repo_root / "anonymized_exports" / "tdm_elena_savier_anonymized" / "case_metadata.csv",
        help="Output CSV containing case_code -> patient_id -> height mapping.",
    )
    return parser.parse_args()


def _load_shared_strings(zf: ZipFile) -> List[str]:
    if "xl/sharedStrings.xml" not in zf.namelist():
        return []
    root = ET.fromstring(zf.read("xl/sharedStrings.xml"))
    strings: List[str] = []
    for si in root.findall(f"{NS}si"):
        strings.append("".join(node.text or "" for node in si.iter(f"{NS}t")))
    return strings


def _iter_sheet_rows(xlsx_path: Path, sheet_name: str = "xl/worksheets/sheet1.xml") -> Iterator[Dict[str, str]]:
    with ZipFile(xlsx_path) as zf:
        shared_strings = _load_shared_strings(zf)
        sheet_root = ET.fromstring(zf.read(sheet_name))
        sheet_data = sheet_root.find(f"{NS}sheetData")
        if sheet_data is None:
            return
        for row in sheet_data.findall(f"{NS}row"):
            values: Dict[str, str] = {}
            for cell in row.findall(f"{NS}c"):
                ref = cell.attrib.get("r", "")
                column = "".join(ch for ch in ref if ch.isalpha())
                value_node = cell.find(f"{NS}v")
                if value_node is None:
                    values[column] = ""
                    continue
                raw_value = value_node.text or ""
                if cell.attrib.get("t") == "s":
                    values[column] = shared_strings[int(raw_value)]
                else:
                    values[column] = raw_value
            yield values


def _parse_height_cm(raw_value: str) -> Optional[float]:
    value = (raw_value or "").strip().replace(",", ".")
    if not value or value.upper() in {"NA", "NF"}:
        return None
    try:
        numeric = float(value)
    except ValueError:
        return None
    if numeric <= 0:
        return None
    if numeric < 3.0:
        return round(numeric * 100.0, 1)
    return round(numeric, 1)


def load_workbook_patient_metadata(xlsx_path: Path) -> Dict[str, Dict[str, str | float | None]]:
    rows = list(_iter_sheet_rows(xlsx_path))
    if not rows:
        raise SystemExit(f"No rows found in workbook: {xlsx_path}")
    metadata: Dict[str, Dict[str, str | float | None]] = {}
    for row in rows[1:]:
        ipp = (row.get("B") or "").strip()
        if not ipp:
            continue
        initiale = (row.get("C") or "").strip()
        height_cm = _parse_height_cm((row.get("J") or row.get("BX") or "").strip())
        metadata[ipp] = {
            "ipp": ipp,
            "initiale": initiale,
            "height_cm": height_cm,
        }
    return metadata


def find_first_dicom(case_dir: Path) -> Path:
    for path in sorted(case_dir.rglob("*.dcm")):
        if path.is_file():
            return path
    raise FileNotFoundError(f"No DICOM found under {case_dir}")


def read_case_identity(case_dir: Path) -> Dict[str, str]:
    sample = find_first_dicom(case_dir)
    ds = pydicom.dcmread(str(sample), stop_before_pixels=True, force=True)
    patient_id = str(ds.get("PatientID") or "").strip()
    patient_name = str(ds.get("PatientName") or "").strip()
    return {
        "sample_dicom": str(sample),
        "patient_id": patient_id,
        "patient_name": patient_name,
    }


def build_case_rows(
    anonymized_root: Path,
    workbook_metadata: Dict[str, Dict[str, str | float | None]],
) -> List[Dict[str, str | float | None]]:
    rows: List[Dict[str, str | float | None]] = []
    for case_dir in sorted(path for path in anonymized_root.iterdir() if path.is_dir()):
        case_identity = read_case_identity(case_dir)
        patient_id = case_identity["patient_id"]
        workbook_row = workbook_metadata.get(patient_id, {})
        rows.append(
            {
                "case_code": case_dir.name,
                "patient_code": case_dir.name.rsplit("_CASE_", 1)[0] if "_CASE_" in case_dir.name else "",
                "patient_name_pseudonym": case_identity["patient_name"],
                "patient_id": patient_id,
                "initiale_source": workbook_row.get("initiale", ""),
                "height_cm": workbook_row.get("height_cm", ""),
                "sample_dicom": case_identity["sample_dicom"],
                "case_dir": str(case_dir),
                "height_found": "1" if workbook_row.get("height_cm") is not None else "0",
            }
        )
    return rows


def write_csv(output_csv: Path, rows: List[Dict[str, str | float | None]]) -> None:
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    with output_csv.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "case_code",
                "patient_code",
                "patient_name_pseudonym",
                "patient_id",
                "initiale_source",
                "height_cm",
                "height_found",
                "sample_dicom",
                "case_dir",
            ],
            delimiter=";",
        )
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def main() -> int:
    args = parse_args()
    workbook_metadata = load_workbook_patient_metadata(args.xlsx)
    case_rows = build_case_rows(args.anonymized_root, workbook_metadata)
    write_csv(args.output_csv, case_rows)
    found_count = sum(1 for row in case_rows if row["height_found"] == "1")
    print(f"Wrote {len(case_rows)} case rows to {args.output_csv}")
    print(f"Heights found: {found_count}/{len(case_rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
