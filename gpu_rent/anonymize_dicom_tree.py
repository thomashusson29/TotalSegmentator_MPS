#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, Iterator, List, Optional, Tuple

import pydicom
from pydicom.dataset import Dataset
from pydicom.dataset import FileMetaDataset
from pydicom.uid import generate_uid


SKIP_FILENAMES = {"DICOMDIR", "LOCKFILE"}
DATE_KEYWORDS = ("Date", "Time")
PERSON_NAME_FIELDS = {
    "PatientName",
    "OtherPatientNames",
    "ReferringPhysicianName",
    "RequestingPhysician",
    "PerformingPhysicianName",
    "NameOfPhysiciansReadingStudy",
    "OperatorsName",
    "AdmittingDiagnosesDescription",
    "PhysiciansOfRecord",
    "PhysiciansOfRecordIdentificationSequence",
}
TEXT_FIELDS_TO_CLEAR = {
    "PatientAddress",
    "PatientTelephoneNumbers",
    "PatientBirthName",
    "PatientMotherBirthName",
    "OtherPatientIDs",
    "OtherPatientIDsSequence",
    "EthnicGroup",
    "Occupation",
    "InstitutionName",
    "InstitutionAddress",
    "InstitutionalDepartmentName",
    "ReferringPhysicianAddress",
    "ReferringPhysicianTelephoneNumbers",
    "AccessionNumber",
    "StudyID",
    "MedicalRecordLocator",
    "IssuerOfPatientID",
    "CountryOfResidence",
    "RegionOfResidence",
    "CurrentPatientLocation",
    "StationName",
    "PerformedLocation",
    "ProtocolName",
}
DATE_FIELDS_TO_CLEAR = {
    "PatientBirthDate",
    "StudyDate",
    "SeriesDate",
    "AcquisitionDate",
    "ContentDate",
    "PerformedProcedureStepStartDate",
    "PerformedProcedureStepEndDate",
    "InstanceCreationDate",
    "StudyTime",
    "SeriesTime",
    "AcquisitionTime",
    "ContentTime",
    "PerformedProcedureStepStartTime",
    "PerformedProcedureStepEndTime",
    "InstanceCreationTime",
}


@dataclass
class CaseInfo:
    original_dir: Path
    sample_file: Path
    patient_key: str
    patient_name: str
    patient_id: str


def parse_args() -> argparse.Namespace:
    repo_root = Path(__file__).resolve().parents[1]
    default_input = repo_root / "tdm_elena_savier"
    default_output = repo_root / "gpu_rent" / "anonymized_exports" / "tdm_elena_savier_anonymized"
    default_mapping = repo_root / "gpu_rent" / "local_only" / "tdm_elena_savier_mapping.csv"
    default_summary = repo_root / "gpu_rent" / "local_only" / "tdm_elena_savier_anonymization_summary.json"

    parser = argparse.ArgumentParser(
        description=(
            "Create a de-identified copy of a DICOM case tree. "
            "Original files are never modified."
        )
    )
    parser.add_argument("--input-root", type=Path, default=default_input)
    parser.add_argument("--output-root", type=Path, default=default_output)
    parser.add_argument("--mapping-csv", type=Path, default=default_mapping)
    parser.add_argument("--summary-json", type=Path, default=default_summary)
    parser.add_argument(
        "--case-prefix",
        default="PAT",
        help="Public pseudonym prefix written into folders and DICOM PatientName/PatientID.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Inspect and plan anonymization without writing the anonymized copy.",
    )
    parser.add_argument(
        "--limit-cases",
        type=int,
        default=None,
        help="Optional limit for a smoke test on the first N cases.",
    )
    parser.add_argument(
        "--preserve-patient-id",
        action="store_true",
        default=True,
        help="Keep the original DICOM PatientID in anonymized copies.",
    )
    parser.add_argument(
        "--replace-patient-id",
        dest="preserve_patient_id",
        action="store_false",
        help="Replace DICOM PatientID with the pseudonym instead of preserving it.",
    )
    return parser.parse_args()


def iter_candidate_case_dirs(root: Path) -> Iterator[Path]:
    for child in sorted(root.iterdir()):
        if not child.is_dir():
            continue
        if child.name.startswith("."):
            continue
        yield child


def find_first_dicom_file(case_dir: Path) -> Optional[Path]:
    for path in sorted(case_dir.rglob("*")):
        if not path.is_file():
            continue
        if path.name in SKIP_FILENAMES:
            continue
        try:
            pydicom.dcmread(str(path), stop_before_pixels=True, force=True)
            return path
        except Exception:
            continue
    return None


def clean_string(value: object) -> str:
    if value is None:
        return ""
    return str(value).strip()


def load_case_infos(root: Path, limit_cases: Optional[int]) -> List[CaseInfo]:
    cases: List[CaseInfo] = []
    for case_dir in iter_candidate_case_dirs(root):
        sample_file = find_first_dicom_file(case_dir)
        if sample_file is None:
            continue
        ds = pydicom.dcmread(str(sample_file), stop_before_pixels=True, force=True)
        patient_name = clean_string(ds.get("PatientName"))
        patient_id = clean_string(ds.get("PatientID"))
        patient_key = patient_id or patient_name or case_dir.name
        cases.append(
            CaseInfo(
                original_dir=case_dir,
                sample_file=sample_file,
                patient_key=patient_key,
                patient_name=patient_name,
                patient_id=patient_id,
            )
        )
        if limit_cases is not None and len(cases) >= limit_cases:
            break
    return cases


def assign_case_codes(cases: Iterable[CaseInfo], case_prefix: str) -> List[Tuple[CaseInfo, str, str]]:
    patient_codes: Dict[str, str] = {}
    patient_case_counts: Dict[str, int] = defaultdict(int)
    indexed_cases: List[Tuple[CaseInfo, str, str]] = []

    for patient_index, patient_key in enumerate(sorted({case.patient_key for case in cases}), start=1):
        patient_codes[patient_key] = f"{case_prefix}_{patient_index:04d}"

    for case in sorted(cases, key=lambda item: (patient_codes[item.patient_key], item.original_dir.name)):
        patient_code = patient_codes[case.patient_key]
        patient_case_counts[patient_code] += 1
        case_code = f"{patient_code}_CASE_{patient_case_counts[patient_code]:02d}"
        indexed_cases.append((case, patient_code, case_code))
    return indexed_cases


def ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def clear_if_present(ds: Dataset, field_name: str) -> None:
    if field_name in ds:
        ds.data_element(field_name).value = ""


def deidentify_dataset(
    ds: Dataset,
    *,
    patient_code: str,
    original_patient_id: str,
    preserve_patient_id: bool,
    uid_maps: Dict[str, Dict[str, str]],
) -> Dataset:
    original_file_meta = getattr(ds, "file_meta", None)
    original_sop_class_uid = clean_string(ds.get("SOPClassUID"))
    if not original_sop_class_uid and original_file_meta is not None:
        original_sop_class_uid = clean_string(getattr(original_file_meta, "MediaStorageSOPClassUID", ""))
    original_sop_instance_uid = clean_string(ds.get("SOPInstanceUID"))
    if not original_sop_instance_uid and original_file_meta is not None:
        original_sop_instance_uid = clean_string(getattr(original_file_meta, "MediaStorageSOPInstanceUID", ""))
    original_transfer_syntax_uid = ""
    if original_file_meta is not None:
        original_transfer_syntax_uid = clean_string(getattr(original_file_meta, "TransferSyntaxUID", ""))

    ds = ds.copy()
    ds.remove_private_tags()

    for field_name in PERSON_NAME_FIELDS | TEXT_FIELDS_TO_CLEAR | DATE_FIELDS_TO_CLEAR:
        clear_if_present(ds, field_name)

    ds.PatientName = patient_code
    ds.PatientID = original_patient_id if preserve_patient_id and original_patient_id else patient_code
    ds.PatientIdentityRemoved = "YES"
    ds.DeidentificationMethod = "Custom gpu_rent anonymizer"

    for field_name in list(ds.dir()):
        if field_name.endswith("Date") or field_name.endswith("Time"):
            if field_name in DATE_FIELDS_TO_CLEAR:
                clear_if_present(ds, field_name)

    for uid_field in ("StudyInstanceUID", "SeriesInstanceUID", "SOPInstanceUID"):
        if uid_field in ds and clean_string(ds.get(uid_field)):
            original_uid = str(ds.get(uid_field))
            replacement = uid_maps.setdefault(uid_field, {}).setdefault(original_uid, generate_uid())
            ds.data_element(uid_field).value = replacement

    if "SOPClassUID" not in ds and original_sop_class_uid:
        ds.SOPClassUID = original_sop_class_uid
    if "SOPInstanceUID" not in ds:
        if original_sop_instance_uid:
            ds.SOPInstanceUID = uid_maps.setdefault("SOPInstanceUID", {}).setdefault(
                original_sop_instance_uid,
                generate_uid(),
            )
        else:
            ds.SOPInstanceUID = generate_uid()

    if not hasattr(ds, "file_meta") or ds.file_meta is None:
        ds.file_meta = FileMetaDataset()

    if "SOPClassUID" in ds and clean_string(ds.get("SOPClassUID")):
        ds.file_meta.MediaStorageSOPClassUID = ds.SOPClassUID
    if "SOPInstanceUID" in ds and clean_string(ds.get("SOPInstanceUID")):
        ds.file_meta.MediaStorageSOPInstanceUID = ds.SOPInstanceUID
    if not getattr(ds.file_meta, "TransferSyntaxUID", None) and original_transfer_syntax_uid:
        ds.file_meta.TransferSyntaxUID = original_transfer_syntax_uid
    if not getattr(ds.file_meta, "ImplementationClassUID", None):
        ds.file_meta.ImplementationClassUID = generate_uid()

    return ds


def anonymize_case(
    case: CaseInfo,
    *,
    output_case_dir: Path,
    patient_code: str,
    case_code: str,
    preserve_patient_id: bool,
    dry_run: bool,
) -> Dict[str, object]:
    study_codes: Dict[str, str] = {}
    series_codes: Dict[str, str] = {}
    uid_maps: Dict[str, Dict[str, str]] = {}
    file_counters: Dict[Tuple[str, str], int] = defaultdict(int)
    dicom_files_written = 0
    skipped_non_image_files = 0

    for path in sorted(case.original_dir.rglob("*")):
        if not path.is_file():
            continue
        if path.name in SKIP_FILENAMES:
            continue
        try:
            ds = pydicom.dcmread(str(path), force=True)
        except Exception:
            continue

        sop_class_uid = clean_string(ds.get("SOPClassUID"))
        if not sop_class_uid and getattr(ds, "file_meta", None) is not None:
            sop_class_uid = clean_string(getattr(ds.file_meta, "MediaStorageSOPClassUID", ""))
        if not sop_class_uid:
            skipped_non_image_files += 1
            continue

        study_uid = clean_string(ds.get("StudyInstanceUID")) or "STUDY_DEFAULT"
        series_uid = clean_string(ds.get("SeriesInstanceUID")) or f"SERIES_DEFAULT_{study_uid}"

        study_code = study_codes.setdefault(study_uid, f"STUDY_{len(study_codes) + 1:03d}")
        series_key = f"{study_uid}::{series_uid}"
        series_code = series_codes.setdefault(series_key, f"SERIES_{len(series_codes) + 1:03d}")

        file_counters[(study_code, series_code)] += 1
        image_index = file_counters[(study_code, series_code)]
        relative_path = Path(study_code) / series_code / f"IMG_{image_index:06d}.dcm"
        output_path = output_case_dir / relative_path

        if not dry_run:
            ensure_parent(output_path)
            sanitized = deidentify_dataset(
                ds,
                patient_code=patient_code,
                original_patient_id=case.patient_id,
                preserve_patient_id=preserve_patient_id,
                uid_maps=uid_maps,
            )
            sanitized.save_as(str(output_path), write_like_original=False)
        dicom_files_written += 1

    return {
        "case_code": case_code,
        "patient_code": patient_code,
        "original_case_dir": str(case.original_dir),
        "output_case_dir": str(output_case_dir),
        "dicom_file_count": dicom_files_written,
        "skipped_non_image_files": skipped_non_image_files,
        "study_count": len(study_codes),
        "series_count": len(series_codes),
    }


def write_mapping_csv(mapping_csv: Path, rows: List[Dict[str, object]], dry_run: bool) -> None:
    if dry_run:
        return
    ensure_parent(mapping_csv)
    with mapping_csv.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "patient_code",
                "case_code",
                "original_case_dir",
                "output_case_dir",
                "original_patient_name",
                "original_patient_id",
                "original_patient_key_sha256",
                "dicom_file_count",
                "skipped_non_image_files",
                "study_count",
                "series_count",
            ],
            delimiter=";",
        )
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def write_summary_json(summary_json: Path, payload: Dict[str, object], dry_run: bool) -> None:
    if dry_run:
        return
    ensure_parent(summary_json)
    summary_json.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def main() -> int:
    args = parse_args()
    cases = load_case_infos(args.input_root, args.limit_cases)
    if not cases:
        raise SystemExit(f"No DICOM case found under {args.input_root}")

    indexed_cases = assign_case_codes(cases, args.case_prefix)

    if not args.dry_run:
        args.output_root.mkdir(parents=True, exist_ok=True)

    mapping_rows: List[Dict[str, object]] = []
    summary_cases: List[Dict[str, object]] = []

    for case, patient_code, case_code in indexed_cases:
        output_case_dir = args.output_root / case_code
        result = anonymize_case(
            case,
            output_case_dir=output_case_dir,
            patient_code=patient_code,
            case_code=case_code,
            preserve_patient_id=args.preserve_patient_id,
            dry_run=args.dry_run,
        )
        if result["dicom_file_count"] == 0:
            continue
        mapping_rows.append(
            {
                **result,
                "original_patient_name": case.patient_name,
                "original_patient_id": case.patient_id,
                "original_patient_key_sha256": sha256_text(case.patient_key),
            }
        )
        summary_cases.append(
            {
                "patient_code": patient_code,
                "case_code": case_code,
                "dicom_file_count": result["dicom_file_count"],
                "skipped_non_image_files": result["skipped_non_image_files"],
                "study_count": result["study_count"],
                "series_count": result["series_count"],
            }
        )

    summary_payload = {
        "input_root": str(args.input_root),
        "output_root": str(args.output_root),
        "case_count": len(summary_cases),
        "patient_count": len({row["patient_code"] for row in summary_cases}),
        "dry_run": args.dry_run,
        "cases": summary_cases,
    }

    write_mapping_csv(args.mapping_csv, mapping_rows, args.dry_run)
    write_summary_json(args.summary_json, summary_payload, args.dry_run)

    print(f"Anonymization planned for {len(summary_cases)} cases." if args.dry_run else f"Anonymized {len(summary_cases)} cases.")
    print(f"Input root: {args.input_root}")
    print(f"Output root: {args.output_root}")
    if not args.dry_run:
        print(f"Local-only mapping CSV: {args.mapping_csv}")
        print(f"Summary JSON: {args.summary_json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
