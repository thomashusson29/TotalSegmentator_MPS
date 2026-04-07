#!/usr/bin/env python3

from __future__ import annotations

from pathlib import Path
import json
import sys

import slicer


PROJECT_DIR = Path("/Users/thomashusson/Documents/Projets/TotalSegmentator_MPS")
OUTPUT_ROOT = PROJECT_DIR / "output"
LATEST_SYMLINK = OUTPUT_ROOT / "latest_abdominal_muscles"
LATEST_TEXT = OUTPUT_ROOT / "latest_abdominal_muscles.txt"


def pretty_name(name: str) -> str:
    return name.replace("_", " ")


def segment_id_for_label(segmentation, label_name: str):
    candidates = [label_name, pretty_name(label_name)]
    for candidate in candidates:
        segment_id = segmentation.GetSegmentIdBySegmentName(candidate)
        if segment_id:
            return segment_id
    return None


def choose_bundle_dir() -> Path | None:
    try:
        import qt
    except Exception:
        return None

    selected = qt.QFileDialog.getExistingDirectory(
        None,
        "Choose TotalSegmentator bundle directory",
        str(OUTPUT_ROOT),
    )
    return Path(selected) if selected else None


def bundle_dir_from_sources() -> Path:
    bundle_dir = globals().get("BUNDLE_DIR")
    if bundle_dir:
        return Path(bundle_dir).expanduser().resolve()

    argv = list(getattr(sys, "argv", []))
    if "--bundle-dir" in argv:
        idx = argv.index("--bundle-dir")
        if idx + 1 >= len(argv):
            raise RuntimeError("Missing value after --bundle-dir")
        return Path(argv[idx + 1]).expanduser().resolve()

    if LATEST_SYMLINK.exists():
        return LATEST_SYMLINK.resolve()

    if LATEST_TEXT.exists():
        return Path(LATEST_TEXT.read_text(encoding="utf-8").strip()).expanduser().resolve()

    selected = choose_bundle_dir()
    if selected:
        return selected.resolve()

    raise RuntimeError(
        "No bundle directory provided and no latest bundle pointer found. "
        "Run segment_abdominal_muscles.py first or pass --bundle-dir."
    )


def load_bundle(bundle_dir: Path) -> tuple[dict, Path, Path]:
    labels_path = bundle_dir / "labels.json"
    if not labels_path.exists():
        raise RuntimeError(f"Missing labels.json in bundle: {bundle_dir}")

    payload = json.loads(labels_path.read_text(encoding="utf-8"))
    nifti_path = bundle_dir / payload["multilabel_nifti"]
    color_table_path = bundle_dir / payload["color_table"]

    if not nifti_path.exists():
        raise RuntimeError(f"Missing multilabel NIfTI: {nifti_path}")
    if not color_table_path.exists():
        raise RuntimeError(f"Missing color table: {color_table_path}")

    return payload, nifti_path, color_table_path


def import_bundle(bundle_dir: Path):
    payload, nifti_path, color_table_path = load_bundle(bundle_dir)
    task = payload["task"]
    label_map = {int(label_id): name for label_id, name in payload["labels"].items()}

    segmentation_name = slicer.mrmlScene.GenerateUniqueName(pretty_name(task))
    color_node = slicer.util.loadColorTable(str(color_table_path))

    segmentation_node = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLSegmentationNode", segmentation_name)
    segmentation_node.CreateDefaultDisplayNodes()
    segmentation_node.SetLabelmapConversionColorTableNodeID(color_node.GetID())
    segmentation_node.AddDefaultStorageNode()

    storage_node = segmentation_node.GetStorageNode()
    storage_node.SetFileName(str(nifti_path))

    loaded_directly = False
    try:
        loaded_directly = bool(storage_node.ReadData(segmentation_node))
    except Exception:
        loaded_directly = False

    if not loaded_directly or segmentation_node.GetSegmentation().GetNumberOfSegments() == 0:
        slicer.mrmlScene.RemoveNode(segmentation_node)
        segmentation_node = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLSegmentationNode", segmentation_name)
        segmentation_node.CreateDefaultDisplayNodes()
        segmentation_node.SetLabelmapConversionColorTableNodeID(color_node.GetID())

        labelmap_node = slicer.util.loadLabelVolume(str(nifti_path), {"name": f"{segmentation_name}-labelmap"})
        labelmap_node.GetDisplayNode().SetAndObserveColorNodeID(color_node.GetID())
        segmentation_node.SetReferenceImageGeometryParameterFromVolumeNode(labelmap_node)
        slicer.modules.segmentations.logic().ImportLabelmapToSegmentationNode(labelmap_node, segmentation_node)
        slicer.mrmlScene.RemoveNode(labelmap_node)

    segmentation = segmentation_node.GetSegmentation()
    for label_id, label_name in sorted(label_map.items()):
        segment_id = segment_id_for_label(segmentation, label_name)
        if not segment_id:
            continue
        segment = segmentation.GetSegment(segment_id)
        rgba = [0.0, 0.0, 0.0, 0.0]
        color_node.GetColor(label_id, rgba)
        segment.SetName(pretty_name(label_name))
        segment.SetColor(rgba[0], rgba[1], rgba[2])

    segmentation_node.CreateClosedSurfaceRepresentation()
    segmentation_node.GetDisplayNode().SetVisibility2D(True)
    segmentation_node.GetDisplayNode().SetVisibility3D(True)
    return segmentation_node


def main() -> None:
    bundle_dir = bundle_dir_from_sources()
    segmentation_node = import_bundle(bundle_dir)
    segmentation = segmentation_node.GetSegmentation()
    print(
        f"Imported segmentation '{segmentation_node.GetName()}' with "
        f"{segmentation.GetNumberOfSegments()} segments from bundle {bundle_dir}"
    )


main()
