#!/usr/bin/env python3

from __future__ import annotations

import argparse
import colorsys
import json
import os
import shlex
import shutil
import subprocess
import sys
import threading
from pathlib import Path

import nibabel as nib
from nibabel.nifti1 import Nifti1Extension

from totalsegmentator.map_to_binary import class_map


PROJECT_DIR = Path(__file__).resolve().parent
OUTPUT_ROOT = PROJECT_DIR / "output"
DEFAULT_TASK = "abdominal_muscles"
DEFAULT_OUTPUT_SUFFIX = "_multilabel.nii.gz"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run TotalSegmentator on a DICOM series using Apple Silicon MPS and generate a 3D Slicer-friendly bundle."
    )
    parser.add_argument(
        "--input-dicom",
        required=True,
        type=Path,
        help="Path to the input DICOM series directory.",
    )
    parser.add_argument(
        "--output-dir",
        required=True,
        type=Path,
        help="Path to the output directory.",
    )
    parser.add_argument(
        "--task",
        default=DEFAULT_TASK,
        help=f"TotalSegmentator task to run. Default: {DEFAULT_TASK}",
    )
    return parser.parse_args()


def ensure_exists(path: Path, label: str) -> None:
    if not path.exists():
        raise SystemExit(f"{label} not found: {path}")


def validate_task(task: str) -> dict[int, str]:
    label_map = class_map.get(task)
    if not label_map:
        supported_tasks = ", ".join(sorted(class_map.keys()))
        raise SystemExit(f"Unsupported task '{task}'. Supported tasks include: {supported_tasks}")
    return label_map


def check_mps() -> None:
    try:
        import torch
    except Exception as exc:
        raise SystemExit(
            "PyTorch is not importable in this environment. Activate the dedicated venv first."
        ) from exc

    mps_built = bool(getattr(torch.backends.mps, "is_built", lambda: False)())
    mps_available = bool(getattr(torch.backends.mps, "is_available", lambda: False)())

    if not mps_built:
        raise SystemExit("This PyTorch build was not compiled with MPS support.")
    if not mps_available:
        raise SystemExit("MPS is not available at runtime on this machine/environment.")


def build_command(args: argparse.Namespace, output_nifti: Path) -> list[str]:
    return [
        "TotalSegmentator",
        "-i",
        str(args.input_dicom),
        "-o",
        str(output_nifti),
        "--task",
        args.task,
        "--ml",
        "--device",
        "mps",
    ]


def write_text(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")


def make_rgba(label_id: int) -> tuple[int, int, int, int]:
    if label_id == 0:
        return (0, 0, 0, 0)
    hue = ((label_id * 0.618033988749895) % 1.0)
    saturation = 0.65
    value = 0.95
    red, green, blue = colorsys.hsv_to_rgb(hue, saturation, value)
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


def write_labels_json(path: Path, task: str, nifti_name: str, color_table_name: str, label_map: dict[int, str]) -> None:
    payload = {
        "task": task,
        "multilabel_nifti": nifti_name,
        "color_table": color_table_name,
        "labels": {str(label_id): label_name for label_id, label_name in sorted(label_map.items())},
    }
    write_text(path, json.dumps(payload, indent=2) + "\n")


def write_slicer_import_helper(path: Path, task: str, nifti_name: str, color_table_name: str, labels_name: str) -> None:
    bundle_dir = str(path.parent.resolve())
    importer_path = str((PROJECT_DIR / "import_bundle_into_slicer.py").resolve())
    helper = f"""#!/usr/bin/env python3
import runpy

BUNDLE_DIR = {bundle_dir!r}
runpy.run_path({importer_path!r}, init_globals={{"BUNDLE_DIR": BUNDLE_DIR}})
"""
    write_text(path, helper)


def build_label_xml(label_map: dict[int, str]) -> str:
    xml_prefix = (
        '<?xml version="1.0" encoding="UTF-8"?> '
        "<CaretExtension><Date><![CDATA[2026-04-07T00:00:00]]></Date>"
        '<VolumeInformation Index="0"><LabelTable>'
    )
    xml_body = []
    for label_id, label_name in sorted(label_map.items()):
        red, green, blue, _ = make_rgba(label_id)
        xml_body.append(
            f'<Label Key="{label_id}" Red="{red / 255.0}" Green="{green / 255.0}" '
            f'Blue="{blue / 255.0}" Alpha="1"><![CDATA[{label_name}]]></Label>'
        )
    xml_suffix = (
        "</LabelTable><StudyMetaDataLinkSet></StudyMetaDataLinkSet>"
        "<VolumeType><![CDATA[Label]]></VolumeType></VolumeInformation></CaretExtension>"
    )
    return xml_prefix + "".join(xml_body) + xml_suffix


def attach_label_extension(nifti_path: Path, label_map: dict[int, str]) -> None:
    image = nib.load(str(nifti_path))
    image.header.extensions.clear()
    image.header.extensions.append(Nifti1Extension(0, build_label_xml(label_map).encode("utf-8")))
    nib.save(image, str(nifti_path))


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


def create_bundle(output_dir: Path, task: str, output_nifti: Path, label_map: dict[int, str]) -> None:
    labels_path = output_dir / "labels.json"
    color_table_path = output_dir / f"{task}.ctbl"
    helper_path = output_dir / "import_into_slicer.py"

    write_labels_json(labels_path, task, output_nifti.name, color_table_path.name, label_map)
    create_color_table(color_table_path, label_map)
    attach_label_extension(output_nifti, label_map)
    write_slicer_import_helper(helper_path, task, output_nifti.name, color_table_path.name, labels_path.name)


def run_pipeline(input_dicom: Path, output_dir: Path, task: str) -> Path:
    label_map = validate_task(task)

    ensure_exists(input_dicom, "Input DICOM directory")
    if not input_dicom.is_dir():
        raise SystemExit(f"Input DICOM path is not a directory: {input_dicom}")

    if shutil.which("TotalSegmentator") is None:
        raise SystemExit("TotalSegmentator executable not found in PATH. Activate the dedicated venv first.")

    output_dir.mkdir(parents=True, exist_ok=True)
    output_nifti = output_dir / f"{task}{DEFAULT_OUTPUT_SUFFIX}"

    check_mps()

    cli_args = argparse.Namespace(input_dicom=input_dicom, output_dir=output_dir, task=task)
    cmd = build_command(cli_args, output_nifti)

    env = os.environ.copy()
    command_txt = " ".join(shlex.quote(part) for part in cmd)
    print(command_txt)
    write_text(output_dir / "command.txt", command_txt + "\n")

    stdout_path = output_dir / "stdout.log"
    stderr_path = output_dir / "stderr.log"
    return_code = run_command(cmd, stdout_path, stderr_path, env)
    if return_code != 0:
        raise SystemExit(return_code)

    if not output_nifti.exists():
        raise SystemExit(f"TotalSegmentator finished without producing the expected multilabel file: {output_nifti}")

    create_bundle(output_dir, task, output_nifti, label_map)
    print(f"Finished successfully. Outputs are under: {output_dir}")
    return output_dir


def main() -> int:
    args = parse_args()
    run_pipeline(args.input_dicom, args.output_dir, args.task)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
