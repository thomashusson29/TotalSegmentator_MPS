#!/usr/bin/env python3

from __future__ import annotations

import json
import sys
from pathlib import Path

import slicer


def pretty_name(name: str) -> str:
    return name.replace("_", " ")


def bundle_root_from_context() -> Path:
    bundle_dir = globals().get("BUNDLE_DIR")
    if bundle_dir:
        return Path(bundle_dir).expanduser().resolve()
    return Path(__file__).resolve().parent


def segment_id_for_label(segmentation, label_name: str):
    for candidate in (label_name, pretty_name(label_name)):
        segment_id = segmentation.GetSegmentIdBySegmentName(candidate)
        if segment_id:
            return segment_id
    return None


def load_labels_bundle(bundle_dir: Path) -> list[dict]:
    labels_path = bundle_dir / "labels.json"
    payload = json.loads(labels_path.read_text(encoding="utf-8"))
    return [
        {
            "bundle_dir": bundle_dir,
            "task": payload["task"],
            "segmentation_name": payload.get("segmentation_name", pretty_name(payload["task"])),
            "multilabel_nifti": bundle_dir / payload["multilabel_nifti"],
            "color_table": bundle_dir / payload["color_table"],
            "labels": {int(k): v for k, v in payload["labels"].items()},
        }
    ]


def load_manifest_bundle(bundle_dir: Path) -> list[dict]:
    manifest_path = bundle_dir / "manifest.json"
    payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    outputs: list[dict] = []
    for entry in payload.get("outputs", []):
        outputs.append(
            {
                "bundle_dir": bundle_dir,
                "task": entry["task"],
                "segmentation_name": entry.get("segmentation_name", pretty_name(entry["task"])),
                "multilabel_nifti": bundle_dir / entry["multilabel_nifti"],
                "color_table": bundle_dir / entry["color_table"],
                "labels": {int(k): v for k, v in entry["labels"].items()},
            }
        )
    return outputs


def discover_imports(bundle_root: Path) -> list[dict]:
    imports: list[dict] = []
    if (bundle_root / "labels.json").exists():
        imports.extend(load_labels_bundle(bundle_root))

    for child in sorted(bundle_root.iterdir()):
        if not child.is_dir():
            continue
        if (child / "labels.json").exists():
            imports.extend(load_labels_bundle(child))
        elif (child / "manifest.json").exists():
            imports.extend(load_manifest_bundle(child))

    if not imports:
        raise RuntimeError(f"No importable segmentation bundle found under {bundle_root}")
    return imports


def import_single_bundle(entry: dict):
    segmentation_name = slicer.mrmlScene.GenerateUniqueName(entry["segmentation_name"])
    color_node = slicer.util.loadColorTable(str(entry["color_table"]))
    segmentation_node = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLSegmentationNode", segmentation_name)
    segmentation_node.CreateDefaultDisplayNodes()
    segmentation_node.SetLabelmapConversionColorTableNodeID(color_node.GetID())
    segmentation_node.AddDefaultStorageNode()

    storage_node = segmentation_node.GetStorageNode()
    storage_node.SetFileName(str(entry["multilabel_nifti"]))

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
        labelmap_node = slicer.util.loadLabelVolume(str(entry["multilabel_nifti"]), {"name": f"{segmentation_name}-labelmap"})
        labelmap_node.GetDisplayNode().SetAndObserveColorNodeID(color_node.GetID())
        segmentation_node.SetReferenceImageGeometryParameterFromVolumeNode(labelmap_node)
        slicer.modules.segmentations.logic().ImportLabelmapToSegmentationNode(labelmap_node, segmentation_node)
        slicer.mrmlScene.RemoveNode(labelmap_node)

    segmentation = segmentation_node.GetSegmentation()
    for label_id, label_name in sorted(entry["labels"].items()):
        segment_id = segment_id_for_label(segmentation, label_name)
        if not segment_id:
            continue
        rgba = [0.0, 0.0, 0.0, 0.0]
        color_node.GetColor(label_id, rgba)
        segment = segmentation.GetSegment(segment_id)
        segment.SetName(pretty_name(label_name))
        segment.SetColor(rgba[0], rgba[1], rgba[2])

    segmentation_node.CreateClosedSurfaceRepresentation()
    segmentation_node.GetDisplayNode().SetVisibility2D(True)
    segmentation_node.GetDisplayNode().SetVisibility3D(True)
    return segmentation_node


def main() -> None:
    bundle_root = bundle_root_from_context()
    entries = discover_imports(bundle_root)
    imported = [import_single_bundle(entry) for entry in entries]
    print(
        f"Imported {len(imported)} segmentation node(s) from bundle {bundle_root}: "
        + ", ".join(node.GetName() for node in imported)
    )


main()

