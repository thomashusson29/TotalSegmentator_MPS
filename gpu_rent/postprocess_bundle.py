#!/usr/bin/env python3

from __future__ import annotations

import shutil
from pathlib import Path

from .common import write_bundle_import_helper


def install_portable_bundle_importer(bundle_dir: Path) -> None:
    bundle_dir = bundle_dir.resolve()
    portable_source = Path(__file__).resolve().parent / "portable_import_bundle_into_slicer.py"
    portable_target = bundle_dir / "_portable_import_bundle_into_slicer.py"
    shutil.copy2(portable_source, portable_target)
    write_bundle_import_helper(bundle_dir)

