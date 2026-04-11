#!/usr/bin/env python3

from __future__ import annotations

import colorsys
import json
import os
import shlex
import shutil
import subprocess
import sys
import threading
from pathlib import Path
from typing import Any

import nibabel as nib
import numpy as np
import SimpleITK as sitk
from nibabel.nifti1 import Nifti1Extension

try:
    from scipy import ndimage
except Exception:  # pragma: no cover
    ndimage = None

try:
    from totalsegmentator.map_to_binary import class_map as TOTALSEG_CLASS_MAP
except Exception:  # pragma: no cover
    TOTALSEG_CLASS_MAP = {}


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_ROOT = REPO_ROOT / "output"
TOTALSEG_HOME_DIR = REPO_ROOT / ".totalsegmentator"
LATEST_SYMLINK = DEFAULT_OUTPUT_ROOT / "latest_abdominal_muscles"
LATEST_TEXT = DEFAULT_OUTPUT_ROOT / "latest_abdominal_muscles.txt"
LATEST_IMPORTER = DEFAULT_OUTPUT_ROOT / "import_latest_abdominal_muscles_into_slicer.py"

ABDOMINAL_TASK = "abdominal_muscles"
TISSUE_TASK = "tissue_4_types"
TOTAL_TASK = "total"
ODIASP_TASK = "ODIASP"

TISSUE_LABELS = {
    1: "subcutaneous_fat",
    2: "torso_fat",
    3: "skeletal_muscle",
    4: "intermuscular_fat",
}

ODIASP_LABELS_BASE = {
    1: "ODIASP_skeletal_muscle_L3",
    2: "ODIASP_vertebrae_L3",
}

ODIASP_LABELS_WITH_TISSUE = {
    1: "ODIASP_skeletal_muscle_L3",
    2: "ODIASP_vertebrae_L3",
    3: "ODIASP_subcutaneous_fat_L3",
    4: "ODIASP_torso_fat_L3",
    5: "ODIASP_intermuscular_fat_L3",
}

DEFAULT_ABDOMINAL_LABELS = {
    1: "pectoralis_major_right",
    2: "pectoralis_major_left",
    3: "rectus_abdominis_right",
    4: "rectus_abdominis_left",
    5: "serratus_anterior_right",
    6: "serratus_anterior_left",
    7: "latissimus_dorsi_right",
    8: "latissimus_dorsi_left",
    9: "trapezius_right",
    10: "trapezius_left",
    11: "external_oblique_right",
    12: "external_oblique_left",
    13: "internal_oblique_right",
    14: "internal_oblique_left",
    15: "erector_spinae_right",
    16: "erector_spinae_left",
    17: "transversospinalis_right",
    18: "transversospinalis_left",
    19: "psoas_major_right",
    20: "psoas_major_left",
    21: "quadratus_lumborum_right",
    22: "quadratus_lumborum_left",
}


def resolve_device_request(device: str) -> str:
    if device != "auto":
        return device

    try:
        import torch
    except Exception:
        return "cpu"

    if bool(getattr(torch.cuda, "is_available", lambda: False)()):
        return "gpu"

    mps_backend = getattr(torch.backends, "mps", None)
    if mps_backend is not None:
        mps_built = bool(getattr(mps_backend, "is_built", lambda: False)())
        mps_available = bool(getattr(mps_backend, "is_available", lambda: False)())
        if mps_built and mps_available:
            return "mps"

    return "cpu"


def ensure_totalseg_home(license_number: str | None = None) -> Path:
    TOTALSEG_HOME_DIR.mkdir(parents=True, exist_ok=True)
    os.environ["TOTALSEG_HOME_DIR"] = str(TOTALSEG_HOME_DIR)

    config_path = TOTALSEG_HOME_DIR / "config.json"
    payload: dict[str, Any] = {}
    if config_path.exists():
        try:
            payload = json.loads(config_path.read_text(encoding="utf-8"))
        except Exception:
            payload = {}

    changed = False
    if license_number and payload.get("license_number") != license_number:
        payload["license_number"] = license_number
        changed = True

    if changed:
        config_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    return TOTALSEG_HOME_DIR


def ensure_totalsegmentator_available() -> None:
    if shutil.which("TotalSegmentator") is None:
        raise RuntimeError("TotalSegmentator executable not found in PATH.")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def write_json(path: Path, payload: Any) -> None:
    write_text(path, json.dumps(payload, indent=2) + "\n")


def round_or_none(value: float | None, digits: int = 3) -> float | None:
    if value is None:
        return None
    return round(float(value), digits)


def normalize_area_cm2_per_m2(area_cm2: float | None, height_m: float | None) -> float | None:
    if area_cm2 is None or not height_m:
        return None
    return round_or_none(area_cm2 / (height_m * height_m))


def normalize_volume_cm3_per_m3(volume_cm3: float | None, height_m: float | None) -> float | None:
    if volume_cm3 is None or not height_m:
        return None
    return round_or_none(volume_cm3 / (height_m ** 3))


def reverse_label_map(label_map: dict[int, str]) -> dict[str, int]:
    return {name: label_id for label_id, name in label_map.items()}


def total_label_map(task: str) -> dict[int, str]:
    label_map = TOTALSEG_CLASS_MAP.get(task)
    if label_map:
        return {int(key): value for key, value in label_map.items()}

    if task == ABDOMINAL_TASK:
        return DEFAULT_ABDOMINAL_LABELS.copy()
    if task == TISSUE_TASK:
        return TISSUE_LABELS.copy()
    raise RuntimeError(f"No label map available for task '{task}'.")


def pretty_name(name: str) -> str:
    return name.replace("_", " ")


def make_rgba(label_id: int) -> tuple[int, int, int, int]:
    if label_id == 0:
        return (0, 0, 0, 0)
    hue = (label_id * 0.618033988749895) % 1.0
    red, green, blue = colorsys.hsv_to_rgb(hue, 0.65, 0.95)
    return (int(red * 255), int(green * 255), int(blue * 255), 255)


def create_color_table(path: Path, label_map: dict[int, str]) -> None:
    lines = [
        f"# Color table file {path.name}",
        f"# {max(label_map.keys()) + 1} values",
        "0 Background 0 0 0 0",
    ]
    for label_id, label_name in sorted(label_map.items()):
        red, green, blue, alpha = make_rgba(label_id)
        lines.append(f"{label_id} {label_name} {red} {green} {blue} {alpha}")
    write_text(path, "\n".join(lines) + "\n")


def build_label_xml(label_map: dict[int, str]) -> str:
    prefix = (
        '<?xml version="1.0" encoding="UTF-8"?> '
        "<CaretExtension><Date><![CDATA[2026-04-11T00:00:00]]></Date>"
        '<VolumeInformation Index="0"><LabelTable>'
    )
    body = []
    for label_id, label_name in sorted(label_map.items()):
        red, green, blue, _ = make_rgba(label_id)
        body.append(
            f'<Label Key="{label_id}" Red="{red / 255.0}" Green="{green / 255.0}" '
            f'Blue="{blue / 255.0}" Alpha="1"><![CDATA[{label_name}]]></Label>'
        )
    suffix = (
        "</LabelTable><StudyMetaDataLinkSet></StudyMetaDataLinkSet>"
        "<VolumeType><![CDATA[Label]]></VolumeType></VolumeInformation></CaretExtension>"
    )
    return prefix + "".join(body) + suffix


def attach_label_extension(nifti_path: Path, label_map: dict[int, str]) -> None:
    image = nib.load(str(nifti_path))
    image.header.extensions.clear()
    image.header.extensions.append(Nifti1Extension(0, build_label_xml(label_map).encode("utf-8")))
    nib.save(image, str(nifti_path))


def write_labels_json(
    path: Path,
    *,
    task: str,
    source_task: str,
    segmentation_name: str,
    nifti_name: str,
    color_table_name: str,
    label_map: dict[int, str],
) -> None:
    payload = {
        "task": task,
        "source_task": source_task,
        "segmentation_name": segmentation_name,
        "multilabel_nifti": nifti_name,
        "color_table": color_table_name,
        "labels": {str(label_id): label_name for label_id, label_name in sorted(label_map.items())},
    }
    write_json(path, payload)


def write_bundle_import_helper(bundle_dir: Path) -> None:
    portable_importer = bundle_dir / "_portable_import_bundle_into_slicer.py"
    helper = bundle_dir / "import_into_slicer.py"
    command_file = bundle_dir / "SLICER_IMPORT_COMMAND.txt"
    write_text(
        helper,
        "#!/usr/bin/env python3\n"
        "import runpy\n"
        "from pathlib import Path\n\n"
        "BUNDLE_DIR = Path(__file__).resolve().parent\n"
        "runpy.run_path(str(BUNDLE_DIR / '_portable_import_bundle_into_slicer.py'), init_globals={'BUNDLE_DIR': str(BUNDLE_DIR)})\n",
    )
    write_text(
        command_file,
        "# Replace <ABSOLUTE_PATH_TO_DOWNLOADED_BUNDLE> with the local path of this bundle.\n"
        'exec(open(r"<ABSOLUTE_PATH_TO_DOWNLOADED_BUNDLE>/import_into_slicer.py").read())\n',
    )
    helper.chmod(0o755)
    portable_importer.chmod(0o755)


def stream_pipe(stream, log_file, target_stream) -> None:
    try:
        for line in iter(stream.readline, ""):
            if not line:
                break
            log_file.write(line)
            log_file.flush()
            target_stream.write(line)
            target_stream.flush()
    finally:
        stream.close()


def run_command(cmd: list[str], stdout_path: Path, stderr_path: Path, env: dict[str, str]) -> int:
    stdout_path.parent.mkdir(parents=True, exist_ok=True)
    stderr_path.parent.mkdir(parents=True, exist_ok=True)
    with stdout_path.open("w", encoding="utf-8") as stdout_file, stderr_path.open(
        "w", encoding="utf-8"
    ) as stderr_file:
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            env=env,
        )
        stdout_thread = threading.Thread(
            target=stream_pipe,
            args=(process.stdout, stdout_file, sys.stdout),
            daemon=True,
        )
        stderr_thread = threading.Thread(
            target=stream_pipe,
            args=(process.stderr, stderr_file, sys.stderr),
            daemon=True,
        )
        stdout_thread.start()
        stderr_thread.start()
        return_code = process.wait()
        stdout_thread.join()
        stderr_thread.join()
        return return_code


def build_totalseg_command(
    *,
    input_path: Path,
    output_path: Path,
    task: str,
    device: str,
    roi_subset: list[str] | None = None,
    statistics_path: Path | None = None,
    stats_include_incomplete: bool = False,
    license_number: str | None = None,
) -> list[str]:
    cmd = [
        "TotalSegmentator",
        "-i",
        str(input_path),
        "-o",
        str(output_path),
        "--task",
        task,
        "--ml",
        "--device",
        device,
    ]
    if roi_subset:
        cmd.extend(["--roi_subset", *roi_subset])
    if statistics_path is not None:
        cmd.extend(["--statistics", str(statistics_path)])
    if stats_include_incomplete:
        cmd.append("--stats_include_incomplete")
    if license_number:
        cmd.extend(["--license_number", license_number])
    return cmd


def run_totalseg_inference(
    *,
    input_path: Path,
    output_path: Path,
    task: str,
    device: str,
    command_path: Path,
    stdout_path: Path,
    stderr_path: Path,
    roi_subset: list[str] | None = None,
    statistics_path: Path | None = None,
    stats_include_incomplete: bool = False,
    license_number: str | None = None,
) -> Path:
    ensure_totalsegmentator_available()
    ensure_totalseg_home(license_number=license_number)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    cmd = build_totalseg_command(
        input_path=input_path,
        output_path=output_path,
        task=task,
        device=device,
        roi_subset=roi_subset,
        statistics_path=statistics_path,
        stats_include_incomplete=stats_include_incomplete,
        license_number=license_number,
    )
    command_txt = " ".join(shlex.quote(part) for part in cmd)
    print(command_txt)
    write_text(command_path, command_txt + "\n")

    env = os.environ.copy()
    env["TOTALSEG_HOME_DIR"] = str(TOTALSEG_HOME_DIR)

    return_code = run_command(cmd, stdout_path, stderr_path, env)
    if return_code != 0:
        raise RuntimeError(f"TotalSegmentator returned exit code {return_code} for task '{task}'.")
    if not output_path.exists():
        raise RuntimeError(f"Expected output file was not created: {output_path}")
    return output_path


def write_segmentation_bundle_artifacts(
    *,
    bundle_dir: Path,
    task: str,
    source_task: str,
    segmentation_name: str,
    nifti_path: Path,
    color_table_name: str,
    labels_json_name: str,
    label_map: dict[int, str],
) -> None:
    color_table_path = bundle_dir / color_table_name
    labels_json_path = bundle_dir / labels_json_name
    create_color_table(color_table_path, label_map)
    write_labels_json(
        labels_json_path,
        task=task,
        source_task=source_task,
        segmentation_name=segmentation_name,
        nifti_name=nifti_path.name,
        color_table_name=color_table_name,
        label_map=label_map,
    )
    attach_label_extension(nifti_path, label_map)


def load_nifti(path: Path) -> nib.Nifti1Image:
    return nib.load(str(path))


def nifti_data_xyz(path: Path) -> tuple[nib.Nifti1Image, np.ndarray]:
    image = load_nifti(path)
    return image, np.asarray(image.dataobj)


def nifti_spacing_xyz(image: nib.Nifti1Image) -> tuple[float, float, float]:
    zooms = image.header.get_zooms()[:3]
    return (float(zooms[0]), float(zooms[1]), float(zooms[2]))


def voxel_volume_mm3(image: nib.Nifti1Image) -> float:
    spacing = nifti_spacing_xyz(image)
    return float(spacing[0] * spacing[1] * spacing[2])


def axis_lengths_xyz(data_xyz: np.ndarray) -> list[int]:
    return [int(data_xyz.shape[0]), int(data_xyz.shape[1]), int(data_xyz.shape[2])]


def pixel_count_to_area_cm2(pixel_count: int, pixel_spacing_mm: tuple[float, float]) -> float:
    return round_or_none(pixel_count * pixel_spacing_mm[0] * pixel_spacing_mm[1] / 100.0) or 0.0


def mean_hu_or_none(ct_values: np.ndarray, mask: np.ndarray) -> float | None:
    if not np.any(mask):
        return None
    values = ct_values[mask.astype(bool)]
    if values.size == 0:
        return None
    return round_or_none(float(values.mean()))


def dicom_series_files(input_dicom: Path) -> list[str]:
    if not input_dicom.exists():
        raise FileNotFoundError(f"Input DICOM path not found: {input_dicom}")

    reader = sitk.ImageSeriesReader()
    sitk.ProcessObject.SetGlobalWarningDisplay(False)
    try:
        best_files: list[str] = []
        for dirpath, _, _ in os.walk(input_dicom):
            series_ids = reader.GetGDCMSeriesIDs(dirpath) or []
            for series_id in series_ids:
                files = list(reader.GetGDCMSeriesFileNames(dirpath, series_id))
                if len(files) > len(best_files):
                    best_files = files
        if not best_files:
            raise RuntimeError(f"No DICOM series found under {input_dicom}")
        return best_files
    finally:
        sitk.ProcessObject.SetGlobalWarningDisplay(True)


def read_dicom_image(input_dicom: Path) -> sitk.Image:
    reader = sitk.ImageSeriesReader()
    reader.SetFileNames(dicom_series_files(input_dicom))
    return reader.Execute()


def resample_ct_to_reference_xyz(input_source: Path, reference_nifti: Path) -> np.ndarray:
    if input_source.is_dir():
        ct_image = read_dicom_image(input_source)
    else:
        ct_image = sitk.ReadImage(str(input_source))
    reference_image = sitk.ReadImage(str(reference_nifti))
    resampled = sitk.Resample(
        ct_image,
        reference_image,
        sitk.Transform(),
        sitk.sitkLinear,
        0.0,
        ct_image.GetPixelIDValue(),
    )
    ct_zyx = sitk.GetArrayFromImage(resampled)
    return np.transpose(ct_zyx, (2, 1, 0))


def save_nifti_like(path: Path, data_xyz: np.ndarray, reference_image: nib.Nifti1Image) -> None:
    image = nib.Nifti1Image(data_xyz.astype(np.float32 if np.issubdtype(data_xyz.dtype, np.floating) else np.int16), reference_image.affine, reference_image.header.copy())
    nib.save(image, str(path))


def load_json_if_exists(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def read_log_tail(path: Path, max_lines: int = 60) -> list[str]:
    if not path.exists():
        return []
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    return lines[-max_lines:]


def write_failure_status(
    *,
    path: Path,
    reason: str,
    trace: str | None = None,
    stdout_log: Path | None = None,
    stderr_log: Path | None = None,
) -> None:
    payload = {
        "status": "failed",
        "reason": reason,
        "trace": trace,
        "stdout_log": stdout_log.name if stdout_log else None,
        "stderr_log": stderr_log.name if stderr_log else None,
        "stderr_tail": read_log_tail(stderr_log) if stderr_log else [],
    }
    write_json(path, payload)


def largest_connected_component(mask: np.ndarray) -> np.ndarray:
    if ndimage is None or not np.any(mask):
        return mask.astype(bool)
    labeled, count = ndimage.label(mask.astype(bool))
    if count == 0:
        return mask.astype(bool)
    sizes = ndimage.sum(mask, labeled, range(1, count + 1))
    largest = int(np.argmax(sizes)) + 1
    return labeled == largest


def filled_mask(mask: np.ndarray) -> np.ndarray:
    if ndimage is None:
        return mask.astype(bool)
    return ndimage.binary_fill_holes(mask.astype(bool))


def choose_mid_slice_index(mask_xyz: np.ndarray) -> int:
    slice_indices = np.where(mask_xyz.any(axis=(0, 1)))[0]
    if slice_indices.size == 0:
        raise RuntimeError("Mask is empty; cannot determine midpoint slice.")
    return int(slice_indices[len(slice_indices) // 2])


def write_latest_pointers(output_root: Path, bundle_dir: Path) -> None:
    output_root.mkdir(parents=True, exist_ok=True)
    latest_symlink = output_root / "latest_abdominal_muscles"
    latest_text = output_root / "latest_abdominal_muscles.txt"
    latest_importer = output_root / "import_latest_abdominal_muscles_into_slicer.py"

    if latest_symlink.exists() or latest_symlink.is_symlink():
        latest_symlink.unlink()
    latest_symlink.symlink_to(bundle_dir.resolve(), target_is_directory=True)
    write_text(latest_text, str(bundle_dir.resolve()) + "\n")
    write_text(
        latest_importer,
        "#!/usr/bin/env python3\n"
        "import runpy\n"
        f"BUNDLE_DIR = {str(bundle_dir.resolve())!r}\n"
        "runpy.run_path(BUNDLE_DIR + '/import_into_slicer.py', init_globals={'BUNDLE_DIR': BUNDLE_DIR})\n",
    )
    latest_importer.chmod(0o755)

