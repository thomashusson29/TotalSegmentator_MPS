#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import re
import sys
import unicodedata
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, Iterator, List, Optional
from xml.etree import ElementTree as ET
from zipfile import ZipFile

import pydicom

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from gpu_rent.anonymize_dicom_tree import (
    CaseInfo,
    anonymize_case,
    ensure_parent,
    find_first_dicom_file,
)


NS = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"


@dataclass
class WorkbookPatient:
    ipp: str
    initiale: str
    height_cm: float | None
    patient_code: str
    source: str = "xlsx"


@dataclass
class CaseRecord:
    original_dir: Path
    patient_id: str
    patient_name: str
    normalized_name: str
    prefix: str
    dicom_file_count: int
    has_dicom: bool


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Rebuild a de-identified export using the 25-patient cohort defined in "
            "BDD_memoire_ER_versionThomas.xlsx, so multiple scans from the same "
            "patient share one PAT_xxxx code."
        )
    )
    parser.add_argument(
        "--input-root",
        type=Path,
        default=REPO_ROOT / "tdm_elena_savier",
    )
    parser.add_argument(
        "--xlsx",
        type=Path,
        default=REPO_ROOT / "tdm_elena_savier" / "BDD_memoire_ER_versionThomas.xlsx",
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        default=REPO_ROOT / "anonymized_exports" / "tdm_elena_savier_anonymized_cohort25",
    )
    parser.add_argument(
        "--local-mapping-csv",
        type=Path,
        default=REPO_ROOT / "gpu_rent" / "local_only" / "cohort25_case_mapping.csv",
    )
    parser.add_argument(
        "--public-case-metadata-csv",
        type=Path,
        default=REPO_ROOT / "anonymized_exports" / "tdm_elena_savier_anonymized_cohort25" / "case_metadata.csv",
    )
    parser.add_argument(
        "--summary-json",
        type=Path,
        default=REPO_ROOT / "gpu_rent" / "local_only" / "cohort25_summary.json",
    )
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument(
        "--replace-output",
        action="store_true",
        help="Delete and rebuild the output root if it already exists.",
    )
    return parser.parse_args()


def _load_shared_strings(zf: ZipFile) -> List[str]:
    if "xl/sharedStrings.xml" not in zf.namelist():
        return []
    root = ET.fromstring(zf.read("xl/sharedStrings.xml"))
    return [
        "".join(node.text or "" for node in si.iter(f"{NS}t"))
        for si in root.findall(f"{NS}si")
    ]


def iter_sheet_rows(xlsx_path: Path) -> Iterator[Dict[str, str]]:
    with ZipFile(xlsx_path) as zf:
        shared_strings = _load_shared_strings(zf)
        sheet_root = ET.fromstring(zf.read("xl/worksheets/sheet1.xml"))
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


def parse_height_cm(raw_value: str) -> float | None:
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


def load_workbook_patients(xlsx_path: Path) -> List[WorkbookPatient]:
    seen: set[str] = set()
    patients: List[WorkbookPatient] = []
    rows = list(iter_sheet_rows(xlsx_path))
    for row in rows[1:]:
        ipp = (row.get("B") or "").strip()
        initiale = (row.get("C") or "").strip()
        if not ipp or ipp in seen:
            continue
        seen.add(ipp)
        patients.append(
            WorkbookPatient(
                ipp=ipp,
                initiale=initiale,
                height_cm=parse_height_cm((row.get("J") or row.get("BX") or "").strip()),
                patient_code=f"PAT_{len(patients) + 1:04d}",
                source="xlsx",
            )
        )
    return patients


def normalize_text(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", (value or "").upper())
    return normalized.encode("ascii", "ignore").decode("ascii")


def normalize_patient_name(value: str) -> str:
    normalized = normalize_text(value).replace("^", " ")
    normalized = re.sub(r"[^A-Z ]+", " ", normalized)
    parts = [part for part in normalized.split() if part not in {"MR", "MRS", "MME"}]
    return " ".join(parts)


def case_prefix(case_name: str) -> str:
    compact = normalize_text(case_name).replace(" ", "").replace("_", "").replace("-", "")
    match = re.match(r"([A-Z]+)", compact)
    if not match:
        return ""
    prefix = match.group(1)
    prefix = re.sub(r"(M\d+|AVANTTHBIS|AVANTTH|AUTRE|AG|L\d+|PORTAL|BIS|TH|RESULTS)$", "", prefix)
    return prefix or match.group(1)


def iter_dicom_datasets(case_dir: Path, max_reads: int = 200) -> Iterator[pydicom.dataset.Dataset]:
    read_count = 0
    for path in sorted(case_dir.rglob("*")):
        if not path.is_file():
            continue
        try:
            ds = pydicom.dcmread(str(path), stop_before_pixels=True, force=True)
        except Exception:
            continue
        sop_class_uid = str(ds.get("SOPClassUID") or "").strip()
        if not sop_class_uid and getattr(ds, "file_meta", None) is not None:
            sop_class_uid = str(getattr(ds.file_meta, "MediaStorageSOPClassUID", "") or "").strip()
        if not sop_class_uid:
            continue
        yield ds
        read_count += 1
        if read_count >= max_reads:
            return


def load_case_records(input_root: Path) -> List[CaseRecord]:
    records: List[CaseRecord] = []
    for case_dir in sorted(path for path in input_root.iterdir() if path.is_dir()):
        patient_ids: set[str] = set()
        patient_names: set[str] = set()
        dicom_count = 0
        has_dicom = False
        for ds in iter_dicom_datasets(case_dir):
            has_dicom = True
            dicom_count += 1
            patient_id = str(ds.get("PatientID") or "").strip()
            patient_name = str(ds.get("PatientName") or "").strip()
            if patient_id:
                patient_ids.add(patient_id)
            if patient_name:
                patient_names.add(normalize_patient_name(patient_name))
            if patient_ids and patient_names and dicom_count >= 30:
                break
        records.append(
            CaseRecord(
                original_dir=case_dir,
                patient_id=sorted(patient_ids)[0] if patient_ids else "",
                patient_name=sorted(patient_names)[0] if patient_names else "",
                normalized_name=sorted(patient_names)[0] if patient_names else "",
                prefix=case_prefix(case_dir.name),
                dicom_file_count=dicom_count,
                has_dicom=has_dicom,
            )
        )
    return records


def patient_id_matches_workbook(patient_id: str, workbook_ipp: str) -> bool:
    left = "".join(ch for ch in patient_id if ch.isdigit())
    right = "".join(ch for ch in workbook_ipp if ch.isdigit())
    if not left or not right:
        return False
    return left == right or left.startswith(right) or right.startswith(left)


def initial_from_prefix(prefix: str) -> str:
    if prefix.startswith("AA"):
        return "AA"
    return prefix[:1]


def resolve_case_assignments(
    cases: List[CaseRecord],
    patients: List[WorkbookPatient],
) -> Dict[str, str]:
    assignments: Dict[str, str] = {}

    # Pass 1: direct PatientID to IPP matching.
    for case in cases:
        if not case.patient_id:
            continue
        for patient in patients:
            if patient_id_matches_workbook(case.patient_id, patient.ipp):
                assignments[case.original_dir.name] = patient.ipp
                break

    made_progress = True
    while made_progress:
        made_progress = False
        canonical_names: Dict[str, set[str]] = defaultdict(set)
        prefix_to_ipps: Dict[str, set[str]] = defaultdict(set)
        used_ipps = set(assignments.values())
        for case in cases:
            assigned_ipp = assignments.get(case.original_dir.name)
            if not assigned_ipp:
                continue
            if case.normalized_name:
                canonical_names[assigned_ipp].add(case.normalized_name)
            if case.prefix:
                prefix_to_ipps[case.prefix].add(assigned_ipp)

        # Pass 2: exact / containment name match to already resolved patient names.
        for case in cases:
            if case.original_dir.name in assignments or not case.normalized_name:
                continue
            candidates: List[str] = []
            for ipp, names in canonical_names.items():
                if any(
                    case.normalized_name == known
                    or case.normalized_name in known
                    or known in case.normalized_name
                    for known in names
                ):
                    candidates.append(ipp)
            unique = sorted(set(candidates))
            if len(unique) == 1:
                assignments[case.original_dir.name] = unique[0]
                made_progress = True

        # Pass 3: unique prefix already seen for a resolved patient.
        for case in cases:
            if case.original_dir.name in assignments or not case.prefix:
                continue
            candidates = sorted(prefix_to_ipps.get(case.prefix, set()))
            if len(candidates) == 1:
                assignments[case.original_dir.name] = candidates[0]
                made_progress = True

        # Pass 4: unique remaining workbook patient for the folder initial.
        by_initial: Dict[str, List[str]] = defaultdict(list)
        for patient in patients:
            by_initial[patient.initiale].append(patient.ipp)
        for case in cases:
            if case.original_dir.name in assignments:
                continue
            initial = initial_from_prefix(case.prefix)
            if not initial:
                continue
            candidates = [ipp for ipp in by_initial.get(initial, []) if ipp not in used_ipps]
            if len(candidates) == 1:
                assignments[case.original_dir.name] = candidates[0]
                used_ipps.add(candidates[0])
                made_progress = True

    return assignments


def build_extra_dicom_patients(
    cases: List[CaseRecord],
    patients: List[WorkbookPatient],
    assignments: Dict[str, str],
) -> List[WorkbookPatient]:
    existing_codes = [int(patient.patient_code.split("_")[1]) for patient in patients]
    next_index = max(existing_codes, default=0) + 1
    grouped_cases: Dict[str, List[CaseRecord]] = defaultdict(list)

    for case in cases:
        if case.original_dir.name in assignments:
            continue
        if not case.has_dicom:
            continue
        group_key = case.normalized_name or case.patient_id or case.prefix
        if not group_key:
            continue
        grouped_cases[group_key].append(case)

    extra_patients: List[WorkbookPatient] = []
    for group_key, group in sorted(grouped_cases.items(), key=lambda item: item[0]):
        patient_id_candidates = sorted({case.patient_id for case in group if case.patient_id})
        canonical_ipp = patient_id_candidates[0] if patient_id_candidates else f"EXTRA::{group_key}"
        initiale = initial_from_prefix(group[0].prefix)
        extra_patients.append(
            WorkbookPatient(
                ipp=canonical_ipp,
                initiale=initiale,
                height_cm=None,
                patient_code=f"PAT_{next_index:04d}",
                source="dicom_only",
            )
        )
        for case in group:
            assignments[case.original_dir.name] = canonical_ipp
        next_index += 1

    return extra_patients


def build_case_plan(
    cases: List[CaseRecord],
    patients: List[WorkbookPatient],
    assignments: Dict[str, str],
) -> List[Dict[str, object]]:
    patient_by_ipp = {patient.ipp: patient for patient in patients}
    grouped: Dict[str, List[CaseRecord]] = defaultdict(list)
    for case in cases:
        ipp = assignments.get(case.original_dir.name)
        if ipp:
            grouped[ipp].append(case)

    plan_rows: List[Dict[str, object]] = []
    for patient in patients:
        case_list = sorted(grouped.get(patient.ipp, []), key=lambda case: case.original_dir.name)
        for case_index, case in enumerate(case_list, start=1):
            case_code = f"{patient.patient_code}_CASE_{case_index:02d}"
            plan_rows.append(
                {
                    "patient_code": patient.patient_code,
                    "case_code": case_code,
                    "canonical_ipp": patient.ipp,
                    "initiale": patient.initiale,
                    "height_cm": patient.height_cm,
                    "patient_source": patient.source,
                    "original_case_dir": str(case.original_dir),
                    "observed_patient_id": case.patient_id,
                    "observed_patient_name": case.patient_name,
                    "case_prefix": case.prefix,
                    "dicom_file_count": case.dicom_file_count,
                }
            )
    return plan_rows


def write_local_mapping_csv(path: Path, rows: List[Dict[str, object]]) -> None:
    ensure_parent(path)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "patient_code",
                "case_code",
                "canonical_ipp",
                "initiale",
                "height_cm",
                "patient_source",
                "original_case_dir",
                "observed_patient_id",
                "observed_patient_name",
                "case_prefix",
                "dicom_file_count",
            ],
            delimiter=";",
        )
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def write_public_case_metadata_csv(path: Path, rows: List[Dict[str, object]]) -> None:
    ensure_parent(path)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["case_code", "patient_code", "height_cm", "height_found"],
            delimiter=";",
        )
        writer.writeheader()
        for row in rows:
            height_cm = row["height_cm"]
            writer.writerow(
                {
                    "case_code": row["case_code"],
                    "patient_code": row["patient_code"],
                    "height_cm": height_cm if height_cm is not None else "",
                    "height_found": "1" if height_cm is not None else "0",
                }
            )


def write_summary_json(path: Path, payload: Dict[str, object]) -> None:
    ensure_parent(path)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def remove_tree(path: Path) -> None:
    if not path.exists():
        return
    for child in sorted(path.rglob("*"), reverse=True):
        if child.is_file() or child.is_symlink():
            child.unlink()
        elif child.is_dir():
            child.rmdir()
    path.rmdir()


def rebuild_output_tree(
    input_root: Path,
    output_root: Path,
    rows: List[Dict[str, object]],
    dry_run: bool,
) -> None:
    if dry_run:
        return
    output_root.mkdir(parents=True, exist_ok=True)
    for row in rows:
        original_case_dir = Path(str(row["original_case_dir"]))
        sample_file = find_first_dicom_file(original_case_dir)
        if sample_file is None:
            raise FileNotFoundError(f"No DICOM found under {original_case_dir}")
        ds = pydicom.dcmread(str(sample_file), stop_before_pixels=True, force=True)
        case_info = CaseInfo(
            original_dir=original_case_dir,
            sample_file=sample_file,
            patient_key=str(row["canonical_ipp"]),
            patient_name=str(ds.get("PatientName") or ""),
            patient_id=str(ds.get("PatientID") or ""),
        )
        anonymize_case(
            case_info,
            output_case_dir=output_root / str(row["case_code"]),
            patient_code=str(row["patient_code"]),
            case_code=str(row["case_code"]),
            preserve_patient_id=True,
            dry_run=False,
        )


def main() -> int:
    args = parse_args()
    workbook_patients = load_workbook_patients(args.xlsx)
    cases = load_case_records(args.input_root)
    assignments = resolve_case_assignments(cases, workbook_patients)
    extra_patients = build_extra_dicom_patients(cases, workbook_patients, assignments)
    patients = [*workbook_patients, *extra_patients]
    plan_rows = build_case_plan(cases, patients, assignments)
    assigned_case_names = {Path(str(row["original_case_dir"])).name for row in plan_rows}
    excluded_cases = [case.original_dir.name for case in cases if case.original_dir.name not in assigned_case_names]

    summary = {
        "input_root": str(args.input_root),
        "xlsx": str(args.xlsx),
        "output_root": str(args.output_root),
        "patient_count_target": len(workbook_patients),
        "patient_count_extra_dicom_only": len(extra_patients),
        "patient_count_assigned": len({row["patient_code"] for row in plan_rows}),
        "case_count_assigned": len(plan_rows),
        "case_count_excluded": len(excluded_cases),
        "excluded_cases": excluded_cases,
    }

    if args.replace_output and args.output_root.exists() and not args.dry_run:
        remove_tree(args.output_root)

    write_local_mapping_csv(args.local_mapping_csv, plan_rows)
    write_public_case_metadata_csv(args.public_case_metadata_csv, plan_rows)
    write_summary_json(args.summary_json, summary)

    rebuild_output_tree(args.input_root, args.output_root, plan_rows, args.dry_run)

    print(f"Target workbook patients: {len(patients)}")
    print(f"Assigned patient groups: {len({row['patient_code'] for row in plan_rows})}")
    print(f"Assigned cases: {len(plan_rows)}")
    print(f"Excluded cases: {len(excluded_cases)}")
    print(f"Local mapping CSV: {args.local_mapping_csv}")
    print(f"Public case metadata CSV: {args.public_case_metadata_csv}")
    print(f"Summary JSON: {args.summary_json}")
    if excluded_cases:
        print("Excluded case folders:")
        for case_name in excluded_cases:
            print(f"  - {case_name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
