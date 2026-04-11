# CSV Variable Dictionary

Generated on `2026-04-10T17:26:10` from `/Users/thomashusson/Documents/Projets/TotalSegmentator_MPS/tdm_elena_savier/segmentation_metrics.csv`.

## Scope

- Source table: the semicolon-separated file produced by `segment_abdominal_muscles.py --with-tocsv`.
- Row definition: one row per input DICOM folder, keyed by `case_id`.
- Missing values: empty cells mean that the metric was not requested, the branch failed, or `--height-cm` was not provided for height-normalized variables.
- Height normalization convention:
  - areas are exported in `cm²/m²`
  - volumes are exported in `cm³/m³`
  - Hounsfield units and ratios are not height-normalized

## Model Overview

- `abdominal_muscles`: TotalSegmentator `abdominal_muscles`, used for 3D T4-L4-like muscle metrics over the native extent returned by that task.
- `odiasp`: ODIASP-compatible L3 single-slice pipeline using TotalSegmentator `abdominal_muscles` plus `vertebrae_L3` from the `total` task.
- `tissue_original`: TotalSegmentator `tissue_4_types` on the full native CT volume.
- `tissue_T4_L4`: TotalSegmentator `tissue_4_types` on the reproducible z-slab defined by the superior and inferior extent of `abdominal_muscles`.
- `total`: TotalSegmentator `total` on the full CT volume, with iliopsoas summary metrics.

## Column Dictionary

### Case metadata

#### `case_id`

- Clinical label: Case identifier
- Unit: text
- Family: Case metadata
- Source metrics file: CSV row metadata
- Model / task: Not applicable
- Detection / computation method: Set to the name of the input DICOM directory.
- Appears when: Always present.
- Interpretation / notes: Example: `AAW_avantTH`.

#### `input_dicom_dir`

- Clinical label: Absolute input DICOM directory
- Unit: filesystem path
- Family: Case metadata
- Source metrics file: CSV row metadata
- Model / task: Not applicable
- Detection / computation method: Resolved from `--input-dicom`.
- Appears when: Always present.
- Interpretation / notes: Allows traceability back to the source scanner folder.

#### `input_parent_dir`

- Clinical label: Parent directory of the input DICOM folder
- Unit: filesystem path
- Family: Case metadata
- Source metrics file: CSV row metadata
- Model / task: Not applicable
- Detection / computation method: Computed as the parent of `input_dicom_dir`.
- Appears when: Always present.
- Interpretation / notes: This is also the default location of `segmentation_metrics.csv`.

#### `bundle_dir`

- Clinical label: Output bundle directory
- Unit: filesystem path
- Family: Case metadata
- Source metrics file: CSV row metadata
- Model / task: Not applicable
- Detection / computation method: Resolved output directory of the current segmentation bundle.
- Appears when: Always present.
- Interpretation / notes: Contains the multilabel NIfTI files, logs, metrics JSON files, previews and Slicer importer.

#### `bundle_name`

- Clinical label: Bundle name
- Unit: text
- Family: Case metadata
- Source metrics file: CSV row metadata
- Model / task: Not applicable
- Detection / computation method: Set to the final directory name of `bundle_dir`.
- Appears when: Always present.
- Interpretation / notes: Useful to map CSV rows back to a specific segmentation run.

#### `csv_exported_at`

- Clinical label: CSV export timestamp
- Unit: ISO-8601 datetime
- Family: Case metadata
- Source metrics file: CSV row metadata
- Model / task: Not applicable
- Detection / computation method: Generated at CSV write time.
- Appears when: Always present.
- Interpretation / notes: Indicates when the row was last written or replaced.

#### `requested_with_muscles`

- Clinical label: Request flag `--with-muscles`
- Unit: boolean
- Family: Case metadata
- Source metrics file: CLI invocation of `segment_abdominal_muscles.py`
- Model / task: Not applicable
- Detection / computation method: Boolean copy of whether `--with-muscles` was enabled when the row was written.
- Appears when: Always present.
- Interpretation / notes: Useful to distinguish a genuinely missing branch from one that was simply not requested.

#### `requested_with_odiasp`

- Clinical label: Request flag `--with-odiasp`
- Unit: boolean
- Family: Case metadata
- Source metrics file: CLI invocation of `segment_abdominal_muscles.py`
- Model / task: Not applicable
- Detection / computation method: Boolean copy of whether `--with-odiasp` was enabled when the row was written.
- Appears when: Always present.
- Interpretation / notes: Useful to distinguish a genuinely missing branch from one that was simply not requested.

#### `requested_with_tissue`

- Clinical label: Request flag `--with-tissue`
- Unit: boolean
- Family: Case metadata
- Source metrics file: CLI invocation of `segment_abdominal_muscles.py`
- Model / task: Not applicable
- Detection / computation method: Boolean copy of whether `--with-tissue` was enabled when the row was written.
- Appears when: Always present.
- Interpretation / notes: Useful to distinguish a genuinely missing branch from one that was simply not requested.

#### `requested_with_total`

- Clinical label: Request flag `--with-total`
- Unit: boolean
- Family: Case metadata
- Source metrics file: CLI invocation of `segment_abdominal_muscles.py`
- Model / task: Not applicable
- Detection / computation method: Boolean copy of whether `--with-total` was enabled when the row was written.
- Appears when: Always present.
- Interpretation / notes: Useful to distinguish a genuinely missing branch from one that was simply not requested.

#### `requested_with_tocsv`

- Clinical label: Request flag `--with-tocsv`
- Unit: boolean
- Family: Case metadata
- Source metrics file: CLI invocation of `segment_abdominal_muscles.py`
- Model / task: Not applicable
- Detection / computation method: Boolean copy of whether `--with-tocsv` was enabled when the row was written.
- Appears when: Always present.
- Interpretation / notes: Useful to distinguish a genuinely missing branch from one that was simply not requested.

#### `muscles_status`

- Clinical label: Abdominal muscles root segmentation status
- Unit: categorical status
- Family: Pipeline diagnostics
- Source metrics file: CSV row metadata or branch status/metrics files
- Model / task: Not applicable
- Detection / computation method: Status exported by the CSV writer for `muscles_status`. Values are typically `success`, `failed`, or `not_requested`.
- Appears when: Always present for the corresponding branch status field.
- Interpretation / notes: Reflects whether the root `abdominal_muscles_multilabel.nii.gz` exists in the bundle.

### Abdominal Muscles

#### `abdominal_muscles_status`

- Clinical label: Abdominal muscles 3D metrics status
- Unit: categorical status
- Family: Pipeline diagnostics
- Source metrics file: CSV row metadata or branch status/metrics files
- Model / task: Not applicable
- Detection / computation method: Status exported by the CSV writer for `abdominal_muscles_status`. Values are typically `success`, `failed`, or `not_requested`.
- Appears when: Always present for the corresponding branch status field.
- Interpretation / notes: Reflects whether `abdominal_muscles_metrics.json` exists and could be flattened into the CSV.

#### `abdominal_muscles_height_cm`

- Clinical label: Patient height
- Unit: cm
- Family: Abdominal Muscles
- Source metrics file: abdominal_muscles_metrics.json
- Model / task: TotalSegmentator `abdominal_muscles`
- Detection / computation method: Height provided on the CLI with `--height-cm`.
- Appears when: When `abdominal_muscles` was run as a public output or as a dependency of `--with-odiasp` or `--with-tissue`.
- Interpretation / notes: Derived from the native `abdominal_muscles` output.

#### `abdominal_muscles_height_m`

- Clinical label: Patient height in metres
- Unit: m
- Family: Abdominal Muscles
- Source metrics file: abdominal_muscles_metrics.json
- Model / task: TotalSegmentator `abdominal_muscles`
- Detection / computation method: Height converted from centimetres to metres from `--height-cm`.
- Appears when: When `abdominal_muscles` was run as a public output or as a dependency of `--with-odiasp` or `--with-tissue`.
- Interpretation / notes: Derived from the native `abdominal_muscles` output.

#### `abdominal_muscles_input_scope`

- Clinical label: input scope
- Unit: text
- Family: Abdominal Muscles
- Source metrics file: abdominal_muscles_metrics.json
- Model / task: TotalSegmentator `abdominal_muscles`
- Detection / computation method: Metadata copied from `abdominal_muscles_metrics.json`.
- Appears when: When `abdominal_muscles` was run as a public output or as a dependency of `--with-odiasp` or `--with-tissue`.
- Interpretation / notes: Technical provenance field.

#### `abdominal_muscles_method`

- Clinical label: Abdominal muscles 3D metrics method
- Unit: text
- Family: Abdominal Muscles
- Source metrics file: abdominal_muscles_metrics.json
- Model / task: TotalSegmentator `abdominal_muscles`
- Detection / computation method: Literal method string written into `abdominal_muscles_metrics.json`.
- Appears when: When `abdominal_muscles` was run as a public output or as a dependency of `--with-odiasp` or `--with-tissue`.
- Interpretation / notes: Describes that these metrics are derived from the native `abdominal_muscles` extent.

#### `abdominal_muscles_regional_muscles_erector_spinae_left_label_id`

- Clinical label: Regional T4-L4 muscle metric for erector spinae left (label id)
- Unit: value
- Family: T4-L4 regional muscle volumes
- Source metrics file: abdominal_muscles_metrics.json
- Model / task: TotalSegmentator `abdominal_muscles`
- Detection / computation method: Numeric label identifier from the `abdominal_muscles` label map.
- Appears when: When `abdominal_muscles` was run as a public output or as a dependency of `--with-odiasp` or `--with-tissue`.
- Interpretation / notes: Derived from the native TotalSegmentator `abdominal_muscles` label without regrouping. The region is measured over the full 3D extent returned by the `abdominal_muscles` task.

#### `abdominal_muscles_regional_muscles_erector_spinae_left_volume_cm3`

- Clinical label: Regional T4-L4 muscle metric for erector spinae left (volume)
- Unit: cm³
- Family: T4-L4 regional muscle volumes
- Source metrics file: abdominal_muscles_metrics.json
- Model / task: TotalSegmentator `abdominal_muscles`
- Detection / computation method: Regional volume converted from mm³ to cm³.
- Appears when: When `abdominal_muscles` was run as a public output or as a dependency of `--with-odiasp` or `--with-tissue`.
- Interpretation / notes: Derived from the native TotalSegmentator `abdominal_muscles` label without regrouping. The region is measured over the full 3D extent returned by the `abdominal_muscles` task.

#### `abdominal_muscles_regional_muscles_erector_spinae_left_volume_cm3_per_m3`

- Clinical label: Regional T4-L4 muscle metric for erector spinae left (height-normalized volume)
- Unit: cm³/m³
- Family: T4-L4 regional muscle volumes
- Source metrics file: abdominal_muscles_metrics.json
- Model / task: TotalSegmentator `abdominal_muscles`
- Detection / computation method: Regional volume in cm³ divided by patient height cubed in m³.
- Appears when: When `abdominal_muscles` was run as a public output or as a dependency of `--with-odiasp` or `--with-tissue`. In addition, `--height-cm` must be provided to populate the height-normalized value.
- Interpretation / notes: Derived from the native TotalSegmentator `abdominal_muscles` label without regrouping. The region is measured over the full 3D extent returned by the `abdominal_muscles` task.

#### `abdominal_muscles_regional_muscles_erector_spinae_left_volume_mm3`

- Clinical label: Regional T4-L4 muscle metric for erector spinae left (volume)
- Unit: mm³
- Family: T4-L4 regional muscle volumes
- Source metrics file: abdominal_muscles_metrics.json
- Model / task: TotalSegmentator `abdominal_muscles`
- Detection / computation method: Voxel count multiplied by the native voxel volume.
- Appears when: When `abdominal_muscles` was run as a public output or as a dependency of `--with-odiasp` or `--with-tissue`.
- Interpretation / notes: Derived from the native TotalSegmentator `abdominal_muscles` label without regrouping. The region is measured over the full 3D extent returned by the `abdominal_muscles` task.

#### `abdominal_muscles_regional_muscles_erector_spinae_left_voxel_count`

- Clinical label: Regional T4-L4 muscle metric for erector spinae left (voxel count)
- Unit: value
- Family: T4-L4 regional muscle volumes
- Source metrics file: abdominal_muscles_metrics.json
- Model / task: TotalSegmentator `abdominal_muscles`
- Detection / computation method: Number of voxels equal to this native muscle label in `abdominal_muscles_multilabel.nii.gz`.
- Appears when: When `abdominal_muscles` was run as a public output or as a dependency of `--with-odiasp` or `--with-tissue`.
- Interpretation / notes: Derived from the native TotalSegmentator `abdominal_muscles` label without regrouping. The region is measured over the full 3D extent returned by the `abdominal_muscles` task.

#### `abdominal_muscles_regional_muscles_erector_spinae_right_label_id`

- Clinical label: Regional T4-L4 muscle metric for erector spinae right (label id)
- Unit: value
- Family: T4-L4 regional muscle volumes
- Source metrics file: abdominal_muscles_metrics.json
- Model / task: TotalSegmentator `abdominal_muscles`
- Detection / computation method: Numeric label identifier from the `abdominal_muscles` label map.
- Appears when: When `abdominal_muscles` was run as a public output or as a dependency of `--with-odiasp` or `--with-tissue`.
- Interpretation / notes: Derived from the native TotalSegmentator `abdominal_muscles` label without regrouping. The region is measured over the full 3D extent returned by the `abdominal_muscles` task.

#### `abdominal_muscles_regional_muscles_erector_spinae_right_volume_cm3`

- Clinical label: Regional T4-L4 muscle metric for erector spinae right (volume)
- Unit: cm³
- Family: T4-L4 regional muscle volumes
- Source metrics file: abdominal_muscles_metrics.json
- Model / task: TotalSegmentator `abdominal_muscles`
- Detection / computation method: Regional volume converted from mm³ to cm³.
- Appears when: When `abdominal_muscles` was run as a public output or as a dependency of `--with-odiasp` or `--with-tissue`.
- Interpretation / notes: Derived from the native TotalSegmentator `abdominal_muscles` label without regrouping. The region is measured over the full 3D extent returned by the `abdominal_muscles` task.

#### `abdominal_muscles_regional_muscles_erector_spinae_right_volume_cm3_per_m3`

- Clinical label: Regional T4-L4 muscle metric for erector spinae right (height-normalized volume)
- Unit: cm³/m³
- Family: T4-L4 regional muscle volumes
- Source metrics file: abdominal_muscles_metrics.json
- Model / task: TotalSegmentator `abdominal_muscles`
- Detection / computation method: Regional volume in cm³ divided by patient height cubed in m³.
- Appears when: When `abdominal_muscles` was run as a public output or as a dependency of `--with-odiasp` or `--with-tissue`. In addition, `--height-cm` must be provided to populate the height-normalized value.
- Interpretation / notes: Derived from the native TotalSegmentator `abdominal_muscles` label without regrouping. The region is measured over the full 3D extent returned by the `abdominal_muscles` task.

#### `abdominal_muscles_regional_muscles_erector_spinae_right_volume_mm3`

- Clinical label: Regional T4-L4 muscle metric for erector spinae right (volume)
- Unit: mm³
- Family: T4-L4 regional muscle volumes
- Source metrics file: abdominal_muscles_metrics.json
- Model / task: TotalSegmentator `abdominal_muscles`
- Detection / computation method: Voxel count multiplied by the native voxel volume.
- Appears when: When `abdominal_muscles` was run as a public output or as a dependency of `--with-odiasp` or `--with-tissue`.
- Interpretation / notes: Derived from the native TotalSegmentator `abdominal_muscles` label without regrouping. The region is measured over the full 3D extent returned by the `abdominal_muscles` task.

#### `abdominal_muscles_regional_muscles_erector_spinae_right_voxel_count`

- Clinical label: Regional T4-L4 muscle metric for erector spinae right (voxel count)
- Unit: value
- Family: T4-L4 regional muscle volumes
- Source metrics file: abdominal_muscles_metrics.json
- Model / task: TotalSegmentator `abdominal_muscles`
- Detection / computation method: Number of voxels equal to this native muscle label in `abdominal_muscles_multilabel.nii.gz`.
- Appears when: When `abdominal_muscles` was run as a public output or as a dependency of `--with-odiasp` or `--with-tissue`.
- Interpretation / notes: Derived from the native TotalSegmentator `abdominal_muscles` label without regrouping. The region is measured over the full 3D extent returned by the `abdominal_muscles` task.

#### `abdominal_muscles_regional_muscles_external_oblique_left_label_id`

- Clinical label: Regional T4-L4 muscle metric for external oblique left (label id)
- Unit: value
- Family: T4-L4 regional muscle volumes
- Source metrics file: abdominal_muscles_metrics.json
- Model / task: TotalSegmentator `abdominal_muscles`
- Detection / computation method: Numeric label identifier from the `abdominal_muscles` label map.
- Appears when: When `abdominal_muscles` was run as a public output or as a dependency of `--with-odiasp` or `--with-tissue`.
- Interpretation / notes: Derived from the native TotalSegmentator `abdominal_muscles` label without regrouping. The region is measured over the full 3D extent returned by the `abdominal_muscles` task.

#### `abdominal_muscles_regional_muscles_external_oblique_left_volume_cm3`

- Clinical label: Regional T4-L4 muscle metric for external oblique left (volume)
- Unit: cm³
- Family: T4-L4 regional muscle volumes
- Source metrics file: abdominal_muscles_metrics.json
- Model / task: TotalSegmentator `abdominal_muscles`
- Detection / computation method: Regional volume converted from mm³ to cm³.
- Appears when: When `abdominal_muscles` was run as a public output or as a dependency of `--with-odiasp` or `--with-tissue`.
- Interpretation / notes: Derived from the native TotalSegmentator `abdominal_muscles` label without regrouping. The region is measured over the full 3D extent returned by the `abdominal_muscles` task.

#### `abdominal_muscles_regional_muscles_external_oblique_left_volume_cm3_per_m3`

- Clinical label: Regional T4-L4 muscle metric for external oblique left (height-normalized volume)
- Unit: cm³/m³
- Family: T4-L4 regional muscle volumes
- Source metrics file: abdominal_muscles_metrics.json
- Model / task: TotalSegmentator `abdominal_muscles`
- Detection / computation method: Regional volume in cm³ divided by patient height cubed in m³.
- Appears when: When `abdominal_muscles` was run as a public output or as a dependency of `--with-odiasp` or `--with-tissue`. In addition, `--height-cm` must be provided to populate the height-normalized value.
- Interpretation / notes: Derived from the native TotalSegmentator `abdominal_muscles` label without regrouping. The region is measured over the full 3D extent returned by the `abdominal_muscles` task.

#### `abdominal_muscles_regional_muscles_external_oblique_left_volume_mm3`

- Clinical label: Regional T4-L4 muscle metric for external oblique left (volume)
- Unit: mm³
- Family: T4-L4 regional muscle volumes
- Source metrics file: abdominal_muscles_metrics.json
- Model / task: TotalSegmentator `abdominal_muscles`
- Detection / computation method: Voxel count multiplied by the native voxel volume.
- Appears when: When `abdominal_muscles` was run as a public output or as a dependency of `--with-odiasp` or `--with-tissue`.
- Interpretation / notes: Derived from the native TotalSegmentator `abdominal_muscles` label without regrouping. The region is measured over the full 3D extent returned by the `abdominal_muscles` task.

#### `abdominal_muscles_regional_muscles_external_oblique_left_voxel_count`

- Clinical label: Regional T4-L4 muscle metric for external oblique left (voxel count)
- Unit: value
- Family: T4-L4 regional muscle volumes
- Source metrics file: abdominal_muscles_metrics.json
- Model / task: TotalSegmentator `abdominal_muscles`
- Detection / computation method: Number of voxels equal to this native muscle label in `abdominal_muscles_multilabel.nii.gz`.
- Appears when: When `abdominal_muscles` was run as a public output or as a dependency of `--with-odiasp` or `--with-tissue`.
- Interpretation / notes: Derived from the native TotalSegmentator `abdominal_muscles` label without regrouping. The region is measured over the full 3D extent returned by the `abdominal_muscles` task.

#### `abdominal_muscles_regional_muscles_external_oblique_right_label_id`

- Clinical label: Regional T4-L4 muscle metric for external oblique right (label id)
- Unit: value
- Family: T4-L4 regional muscle volumes
- Source metrics file: abdominal_muscles_metrics.json
- Model / task: TotalSegmentator `abdominal_muscles`
- Detection / computation method: Numeric label identifier from the `abdominal_muscles` label map.
- Appears when: When `abdominal_muscles` was run as a public output or as a dependency of `--with-odiasp` or `--with-tissue`.
- Interpretation / notes: Derived from the native TotalSegmentator `abdominal_muscles` label without regrouping. The region is measured over the full 3D extent returned by the `abdominal_muscles` task.

#### `abdominal_muscles_regional_muscles_external_oblique_right_volume_cm3`

- Clinical label: Regional T4-L4 muscle metric for external oblique right (volume)
- Unit: cm³
- Family: T4-L4 regional muscle volumes
- Source metrics file: abdominal_muscles_metrics.json
- Model / task: TotalSegmentator `abdominal_muscles`
- Detection / computation method: Regional volume converted from mm³ to cm³.
- Appears when: When `abdominal_muscles` was run as a public output or as a dependency of `--with-odiasp` or `--with-tissue`.
- Interpretation / notes: Derived from the native TotalSegmentator `abdominal_muscles` label without regrouping. The region is measured over the full 3D extent returned by the `abdominal_muscles` task.

#### `abdominal_muscles_regional_muscles_external_oblique_right_volume_cm3_per_m3`

- Clinical label: Regional T4-L4 muscle metric for external oblique right (height-normalized volume)
- Unit: cm³/m³
- Family: T4-L4 regional muscle volumes
- Source metrics file: abdominal_muscles_metrics.json
- Model / task: TotalSegmentator `abdominal_muscles`
- Detection / computation method: Regional volume in cm³ divided by patient height cubed in m³.
- Appears when: When `abdominal_muscles` was run as a public output or as a dependency of `--with-odiasp` or `--with-tissue`. In addition, `--height-cm` must be provided to populate the height-normalized value.
- Interpretation / notes: Derived from the native TotalSegmentator `abdominal_muscles` label without regrouping. The region is measured over the full 3D extent returned by the `abdominal_muscles` task.

#### `abdominal_muscles_regional_muscles_external_oblique_right_volume_mm3`

- Clinical label: Regional T4-L4 muscle metric for external oblique right (volume)
- Unit: mm³
- Family: T4-L4 regional muscle volumes
- Source metrics file: abdominal_muscles_metrics.json
- Model / task: TotalSegmentator `abdominal_muscles`
- Detection / computation method: Voxel count multiplied by the native voxel volume.
- Appears when: When `abdominal_muscles` was run as a public output or as a dependency of `--with-odiasp` or `--with-tissue`.
- Interpretation / notes: Derived from the native TotalSegmentator `abdominal_muscles` label without regrouping. The region is measured over the full 3D extent returned by the `abdominal_muscles` task.

#### `abdominal_muscles_regional_muscles_external_oblique_right_voxel_count`

- Clinical label: Regional T4-L4 muscle metric for external oblique right (voxel count)
- Unit: value
- Family: T4-L4 regional muscle volumes
- Source metrics file: abdominal_muscles_metrics.json
- Model / task: TotalSegmentator `abdominal_muscles`
- Detection / computation method: Number of voxels equal to this native muscle label in `abdominal_muscles_multilabel.nii.gz`.
- Appears when: When `abdominal_muscles` was run as a public output or as a dependency of `--with-odiasp` or `--with-tissue`.
- Interpretation / notes: Derived from the native TotalSegmentator `abdominal_muscles` label without regrouping. The region is measured over the full 3D extent returned by the `abdominal_muscles` task.

#### `abdominal_muscles_regional_muscles_internal_oblique_left_label_id`

- Clinical label: Regional T4-L4 muscle metric for internal oblique left (label id)
- Unit: value
- Family: T4-L4 regional muscle volumes
- Source metrics file: abdominal_muscles_metrics.json
- Model / task: TotalSegmentator `abdominal_muscles`
- Detection / computation method: Numeric label identifier from the `abdominal_muscles` label map.
- Appears when: When `abdominal_muscles` was run as a public output or as a dependency of `--with-odiasp` or `--with-tissue`.
- Interpretation / notes: Derived from the native TotalSegmentator `abdominal_muscles` label without regrouping. The region is measured over the full 3D extent returned by the `abdominal_muscles` task.

#### `abdominal_muscles_regional_muscles_internal_oblique_left_volume_cm3`

- Clinical label: Regional T4-L4 muscle metric for internal oblique left (volume)
- Unit: cm³
- Family: T4-L4 regional muscle volumes
- Source metrics file: abdominal_muscles_metrics.json
- Model / task: TotalSegmentator `abdominal_muscles`
- Detection / computation method: Regional volume converted from mm³ to cm³.
- Appears when: When `abdominal_muscles` was run as a public output or as a dependency of `--with-odiasp` or `--with-tissue`.
- Interpretation / notes: Derived from the native TotalSegmentator `abdominal_muscles` label without regrouping. The region is measured over the full 3D extent returned by the `abdominal_muscles` task.

#### `abdominal_muscles_regional_muscles_internal_oblique_left_volume_cm3_per_m3`

- Clinical label: Regional T4-L4 muscle metric for internal oblique left (height-normalized volume)
- Unit: cm³/m³
- Family: T4-L4 regional muscle volumes
- Source metrics file: abdominal_muscles_metrics.json
- Model / task: TotalSegmentator `abdominal_muscles`
- Detection / computation method: Regional volume in cm³ divided by patient height cubed in m³.
- Appears when: When `abdominal_muscles` was run as a public output or as a dependency of `--with-odiasp` or `--with-tissue`. In addition, `--height-cm` must be provided to populate the height-normalized value.
- Interpretation / notes: Derived from the native TotalSegmentator `abdominal_muscles` label without regrouping. The region is measured over the full 3D extent returned by the `abdominal_muscles` task.

#### `abdominal_muscles_regional_muscles_internal_oblique_left_volume_mm3`

- Clinical label: Regional T4-L4 muscle metric for internal oblique left (volume)
- Unit: mm³
- Family: T4-L4 regional muscle volumes
- Source metrics file: abdominal_muscles_metrics.json
- Model / task: TotalSegmentator `abdominal_muscles`
- Detection / computation method: Voxel count multiplied by the native voxel volume.
- Appears when: When `abdominal_muscles` was run as a public output or as a dependency of `--with-odiasp` or `--with-tissue`.
- Interpretation / notes: Derived from the native TotalSegmentator `abdominal_muscles` label without regrouping. The region is measured over the full 3D extent returned by the `abdominal_muscles` task.

#### `abdominal_muscles_regional_muscles_internal_oblique_left_voxel_count`

- Clinical label: Regional T4-L4 muscle metric for internal oblique left (voxel count)
- Unit: value
- Family: T4-L4 regional muscle volumes
- Source metrics file: abdominal_muscles_metrics.json
- Model / task: TotalSegmentator `abdominal_muscles`
- Detection / computation method: Number of voxels equal to this native muscle label in `abdominal_muscles_multilabel.nii.gz`.
- Appears when: When `abdominal_muscles` was run as a public output or as a dependency of `--with-odiasp` or `--with-tissue`.
- Interpretation / notes: Derived from the native TotalSegmentator `abdominal_muscles` label without regrouping. The region is measured over the full 3D extent returned by the `abdominal_muscles` task.

#### `abdominal_muscles_regional_muscles_internal_oblique_right_label_id`

- Clinical label: Regional T4-L4 muscle metric for internal oblique right (label id)
- Unit: value
- Family: T4-L4 regional muscle volumes
- Source metrics file: abdominal_muscles_metrics.json
- Model / task: TotalSegmentator `abdominal_muscles`
- Detection / computation method: Numeric label identifier from the `abdominal_muscles` label map.
- Appears when: When `abdominal_muscles` was run as a public output or as a dependency of `--with-odiasp` or `--with-tissue`.
- Interpretation / notes: Derived from the native TotalSegmentator `abdominal_muscles` label without regrouping. The region is measured over the full 3D extent returned by the `abdominal_muscles` task.

#### `abdominal_muscles_regional_muscles_internal_oblique_right_volume_cm3`

- Clinical label: Regional T4-L4 muscle metric for internal oblique right (volume)
- Unit: cm³
- Family: T4-L4 regional muscle volumes
- Source metrics file: abdominal_muscles_metrics.json
- Model / task: TotalSegmentator `abdominal_muscles`
- Detection / computation method: Regional volume converted from mm³ to cm³.
- Appears when: When `abdominal_muscles` was run as a public output or as a dependency of `--with-odiasp` or `--with-tissue`.
- Interpretation / notes: Derived from the native TotalSegmentator `abdominal_muscles` label without regrouping. The region is measured over the full 3D extent returned by the `abdominal_muscles` task.

#### `abdominal_muscles_regional_muscles_internal_oblique_right_volume_cm3_per_m3`

- Clinical label: Regional T4-L4 muscle metric for internal oblique right (height-normalized volume)
- Unit: cm³/m³
- Family: T4-L4 regional muscle volumes
- Source metrics file: abdominal_muscles_metrics.json
- Model / task: TotalSegmentator `abdominal_muscles`
- Detection / computation method: Regional volume in cm³ divided by patient height cubed in m³.
- Appears when: When `abdominal_muscles` was run as a public output or as a dependency of `--with-odiasp` or `--with-tissue`. In addition, `--height-cm` must be provided to populate the height-normalized value.
- Interpretation / notes: Derived from the native TotalSegmentator `abdominal_muscles` label without regrouping. The region is measured over the full 3D extent returned by the `abdominal_muscles` task.

#### `abdominal_muscles_regional_muscles_internal_oblique_right_volume_mm3`

- Clinical label: Regional T4-L4 muscle metric for internal oblique right (volume)
- Unit: mm³
- Family: T4-L4 regional muscle volumes
- Source metrics file: abdominal_muscles_metrics.json
- Model / task: TotalSegmentator `abdominal_muscles`
- Detection / computation method: Voxel count multiplied by the native voxel volume.
- Appears when: When `abdominal_muscles` was run as a public output or as a dependency of `--with-odiasp` or `--with-tissue`.
- Interpretation / notes: Derived from the native TotalSegmentator `abdominal_muscles` label without regrouping. The region is measured over the full 3D extent returned by the `abdominal_muscles` task.

#### `abdominal_muscles_regional_muscles_internal_oblique_right_voxel_count`

- Clinical label: Regional T4-L4 muscle metric for internal oblique right (voxel count)
- Unit: value
- Family: T4-L4 regional muscle volumes
- Source metrics file: abdominal_muscles_metrics.json
- Model / task: TotalSegmentator `abdominal_muscles`
- Detection / computation method: Number of voxels equal to this native muscle label in `abdominal_muscles_multilabel.nii.gz`.
- Appears when: When `abdominal_muscles` was run as a public output or as a dependency of `--with-odiasp` or `--with-tissue`.
- Interpretation / notes: Derived from the native TotalSegmentator `abdominal_muscles` label without regrouping. The region is measured over the full 3D extent returned by the `abdominal_muscles` task.

#### `abdominal_muscles_regional_muscles_latissimus_dorsi_left_label_id`

- Clinical label: Regional T4-L4 muscle metric for latissimus dorsi left (label id)
- Unit: value
- Family: T4-L4 regional muscle volumes
- Source metrics file: abdominal_muscles_metrics.json
- Model / task: TotalSegmentator `abdominal_muscles`
- Detection / computation method: Numeric label identifier from the `abdominal_muscles` label map.
- Appears when: When `abdominal_muscles` was run as a public output or as a dependency of `--with-odiasp` or `--with-tissue`.
- Interpretation / notes: Derived from the native TotalSegmentator `abdominal_muscles` label without regrouping. The region is measured over the full 3D extent returned by the `abdominal_muscles` task.

#### `abdominal_muscles_regional_muscles_latissimus_dorsi_left_volume_cm3`

- Clinical label: Regional T4-L4 muscle metric for latissimus dorsi left (volume)
- Unit: cm³
- Family: T4-L4 regional muscle volumes
- Source metrics file: abdominal_muscles_metrics.json
- Model / task: TotalSegmentator `abdominal_muscles`
- Detection / computation method: Regional volume converted from mm³ to cm³.
- Appears when: When `abdominal_muscles` was run as a public output or as a dependency of `--with-odiasp` or `--with-tissue`.
- Interpretation / notes: Derived from the native TotalSegmentator `abdominal_muscles` label without regrouping. The region is measured over the full 3D extent returned by the `abdominal_muscles` task.

#### `abdominal_muscles_regional_muscles_latissimus_dorsi_left_volume_cm3_per_m3`

- Clinical label: Regional T4-L4 muscle metric for latissimus dorsi left (height-normalized volume)
- Unit: cm³/m³
- Family: T4-L4 regional muscle volumes
- Source metrics file: abdominal_muscles_metrics.json
- Model / task: TotalSegmentator `abdominal_muscles`
- Detection / computation method: Regional volume in cm³ divided by patient height cubed in m³.
- Appears when: When `abdominal_muscles` was run as a public output or as a dependency of `--with-odiasp` or `--with-tissue`. In addition, `--height-cm` must be provided to populate the height-normalized value.
- Interpretation / notes: Derived from the native TotalSegmentator `abdominal_muscles` label without regrouping. The region is measured over the full 3D extent returned by the `abdominal_muscles` task.

#### `abdominal_muscles_regional_muscles_latissimus_dorsi_left_volume_mm3`

- Clinical label: Regional T4-L4 muscle metric for latissimus dorsi left (volume)
- Unit: mm³
- Family: T4-L4 regional muscle volumes
- Source metrics file: abdominal_muscles_metrics.json
- Model / task: TotalSegmentator `abdominal_muscles`
- Detection / computation method: Voxel count multiplied by the native voxel volume.
- Appears when: When `abdominal_muscles` was run as a public output or as a dependency of `--with-odiasp` or `--with-tissue`.
- Interpretation / notes: Derived from the native TotalSegmentator `abdominal_muscles` label without regrouping. The region is measured over the full 3D extent returned by the `abdominal_muscles` task.

#### `abdominal_muscles_regional_muscles_latissimus_dorsi_left_voxel_count`

- Clinical label: Regional T4-L4 muscle metric for latissimus dorsi left (voxel count)
- Unit: value
- Family: T4-L4 regional muscle volumes
- Source metrics file: abdominal_muscles_metrics.json
- Model / task: TotalSegmentator `abdominal_muscles`
- Detection / computation method: Number of voxels equal to this native muscle label in `abdominal_muscles_multilabel.nii.gz`.
- Appears when: When `abdominal_muscles` was run as a public output or as a dependency of `--with-odiasp` or `--with-tissue`.
- Interpretation / notes: Derived from the native TotalSegmentator `abdominal_muscles` label without regrouping. The region is measured over the full 3D extent returned by the `abdominal_muscles` task.

#### `abdominal_muscles_regional_muscles_latissimus_dorsi_right_label_id`

- Clinical label: Regional T4-L4 muscle metric for latissimus dorsi right (label id)
- Unit: value
- Family: T4-L4 regional muscle volumes
- Source metrics file: abdominal_muscles_metrics.json
- Model / task: TotalSegmentator `abdominal_muscles`
- Detection / computation method: Numeric label identifier from the `abdominal_muscles` label map.
- Appears when: When `abdominal_muscles` was run as a public output or as a dependency of `--with-odiasp` or `--with-tissue`.
- Interpretation / notes: Derived from the native TotalSegmentator `abdominal_muscles` label without regrouping. The region is measured over the full 3D extent returned by the `abdominal_muscles` task.

#### `abdominal_muscles_regional_muscles_latissimus_dorsi_right_volume_cm3`

- Clinical label: Regional T4-L4 muscle metric for latissimus dorsi right (volume)
- Unit: cm³
- Family: T4-L4 regional muscle volumes
- Source metrics file: abdominal_muscles_metrics.json
- Model / task: TotalSegmentator `abdominal_muscles`
- Detection / computation method: Regional volume converted from mm³ to cm³.
- Appears when: When `abdominal_muscles` was run as a public output or as a dependency of `--with-odiasp` or `--with-tissue`.
- Interpretation / notes: Derived from the native TotalSegmentator `abdominal_muscles` label without regrouping. The region is measured over the full 3D extent returned by the `abdominal_muscles` task.

#### `abdominal_muscles_regional_muscles_latissimus_dorsi_right_volume_cm3_per_m3`

- Clinical label: Regional T4-L4 muscle metric for latissimus dorsi right (height-normalized volume)
- Unit: cm³/m³
- Family: T4-L4 regional muscle volumes
- Source metrics file: abdominal_muscles_metrics.json
- Model / task: TotalSegmentator `abdominal_muscles`
- Detection / computation method: Regional volume in cm³ divided by patient height cubed in m³.
- Appears when: When `abdominal_muscles` was run as a public output or as a dependency of `--with-odiasp` or `--with-tissue`. In addition, `--height-cm` must be provided to populate the height-normalized value.
- Interpretation / notes: Derived from the native TotalSegmentator `abdominal_muscles` label without regrouping. The region is measured over the full 3D extent returned by the `abdominal_muscles` task.

#### `abdominal_muscles_regional_muscles_latissimus_dorsi_right_volume_mm3`

- Clinical label: Regional T4-L4 muscle metric for latissimus dorsi right (volume)
- Unit: mm³
- Family: T4-L4 regional muscle volumes
- Source metrics file: abdominal_muscles_metrics.json
- Model / task: TotalSegmentator `abdominal_muscles`
- Detection / computation method: Voxel count multiplied by the native voxel volume.
- Appears when: When `abdominal_muscles` was run as a public output or as a dependency of `--with-odiasp` or `--with-tissue`.
- Interpretation / notes: Derived from the native TotalSegmentator `abdominal_muscles` label without regrouping. The region is measured over the full 3D extent returned by the `abdominal_muscles` task.

#### `abdominal_muscles_regional_muscles_latissimus_dorsi_right_voxel_count`

- Clinical label: Regional T4-L4 muscle metric for latissimus dorsi right (voxel count)
- Unit: value
- Family: T4-L4 regional muscle volumes
- Source metrics file: abdominal_muscles_metrics.json
- Model / task: TotalSegmentator `abdominal_muscles`
- Detection / computation method: Number of voxels equal to this native muscle label in `abdominal_muscles_multilabel.nii.gz`.
- Appears when: When `abdominal_muscles` was run as a public output or as a dependency of `--with-odiasp` or `--with-tissue`.
- Interpretation / notes: Derived from the native TotalSegmentator `abdominal_muscles` label without regrouping. The region is measured over the full 3D extent returned by the `abdominal_muscles` task.

#### `abdominal_muscles_regional_muscles_pectoralis_major_left_label_id`

- Clinical label: Regional T4-L4 muscle metric for pectoralis major left (label id)
- Unit: value
- Family: T4-L4 regional muscle volumes
- Source metrics file: abdominal_muscles_metrics.json
- Model / task: TotalSegmentator `abdominal_muscles`
- Detection / computation method: Numeric label identifier from the `abdominal_muscles` label map.
- Appears when: When `abdominal_muscles` was run as a public output or as a dependency of `--with-odiasp` or `--with-tissue`.
- Interpretation / notes: Derived from the native TotalSegmentator `abdominal_muscles` label without regrouping. The region is measured over the full 3D extent returned by the `abdominal_muscles` task.

#### `abdominal_muscles_regional_muscles_pectoralis_major_left_volume_cm3`

- Clinical label: Regional T4-L4 muscle metric for pectoralis major left (volume)
- Unit: cm³
- Family: T4-L4 regional muscle volumes
- Source metrics file: abdominal_muscles_metrics.json
- Model / task: TotalSegmentator `abdominal_muscles`
- Detection / computation method: Regional volume converted from mm³ to cm³.
- Appears when: When `abdominal_muscles` was run as a public output or as a dependency of `--with-odiasp` or `--with-tissue`.
- Interpretation / notes: Derived from the native TotalSegmentator `abdominal_muscles` label without regrouping. The region is measured over the full 3D extent returned by the `abdominal_muscles` task.

#### `abdominal_muscles_regional_muscles_pectoralis_major_left_volume_cm3_per_m3`

- Clinical label: Regional T4-L4 muscle metric for pectoralis major left (height-normalized volume)
- Unit: cm³/m³
- Family: T4-L4 regional muscle volumes
- Source metrics file: abdominal_muscles_metrics.json
- Model / task: TotalSegmentator `abdominal_muscles`
- Detection / computation method: Regional volume in cm³ divided by patient height cubed in m³.
- Appears when: When `abdominal_muscles` was run as a public output or as a dependency of `--with-odiasp` or `--with-tissue`. In addition, `--height-cm` must be provided to populate the height-normalized value.
- Interpretation / notes: Derived from the native TotalSegmentator `abdominal_muscles` label without regrouping. The region is measured over the full 3D extent returned by the `abdominal_muscles` task.

#### `abdominal_muscles_regional_muscles_pectoralis_major_left_volume_mm3`

- Clinical label: Regional T4-L4 muscle metric for pectoralis major left (volume)
- Unit: mm³
- Family: T4-L4 regional muscle volumes
- Source metrics file: abdominal_muscles_metrics.json
- Model / task: TotalSegmentator `abdominal_muscles`
- Detection / computation method: Voxel count multiplied by the native voxel volume.
- Appears when: When `abdominal_muscles` was run as a public output or as a dependency of `--with-odiasp` or `--with-tissue`.
- Interpretation / notes: Derived from the native TotalSegmentator `abdominal_muscles` label without regrouping. The region is measured over the full 3D extent returned by the `abdominal_muscles` task.

#### `abdominal_muscles_regional_muscles_pectoralis_major_left_voxel_count`

- Clinical label: Regional T4-L4 muscle metric for pectoralis major left (voxel count)
- Unit: value
- Family: T4-L4 regional muscle volumes
- Source metrics file: abdominal_muscles_metrics.json
- Model / task: TotalSegmentator `abdominal_muscles`
- Detection / computation method: Number of voxels equal to this native muscle label in `abdominal_muscles_multilabel.nii.gz`.
- Appears when: When `abdominal_muscles` was run as a public output or as a dependency of `--with-odiasp` or `--with-tissue`.
- Interpretation / notes: Derived from the native TotalSegmentator `abdominal_muscles` label without regrouping. The region is measured over the full 3D extent returned by the `abdominal_muscles` task.

#### `abdominal_muscles_regional_muscles_pectoralis_major_right_label_id`

- Clinical label: Regional T4-L4 muscle metric for pectoralis major right (label id)
- Unit: value
- Family: T4-L4 regional muscle volumes
- Source metrics file: abdominal_muscles_metrics.json
- Model / task: TotalSegmentator `abdominal_muscles`
- Detection / computation method: Numeric label identifier from the `abdominal_muscles` label map.
- Appears when: When `abdominal_muscles` was run as a public output or as a dependency of `--with-odiasp` or `--with-tissue`.
- Interpretation / notes: Derived from the native TotalSegmentator `abdominal_muscles` label without regrouping. The region is measured over the full 3D extent returned by the `abdominal_muscles` task.

#### `abdominal_muscles_regional_muscles_pectoralis_major_right_volume_cm3`

- Clinical label: Regional T4-L4 muscle metric for pectoralis major right (volume)
- Unit: cm³
- Family: T4-L4 regional muscle volumes
- Source metrics file: abdominal_muscles_metrics.json
- Model / task: TotalSegmentator `abdominal_muscles`
- Detection / computation method: Regional volume converted from mm³ to cm³.
- Appears when: When `abdominal_muscles` was run as a public output or as a dependency of `--with-odiasp` or `--with-tissue`.
- Interpretation / notes: Derived from the native TotalSegmentator `abdominal_muscles` label without regrouping. The region is measured over the full 3D extent returned by the `abdominal_muscles` task.

#### `abdominal_muscles_regional_muscles_pectoralis_major_right_volume_cm3_per_m3`

- Clinical label: Regional T4-L4 muscle metric for pectoralis major right (height-normalized volume)
- Unit: cm³/m³
- Family: T4-L4 regional muscle volumes
- Source metrics file: abdominal_muscles_metrics.json
- Model / task: TotalSegmentator `abdominal_muscles`
- Detection / computation method: Regional volume in cm³ divided by patient height cubed in m³.
- Appears when: When `abdominal_muscles` was run as a public output or as a dependency of `--with-odiasp` or `--with-tissue`. In addition, `--height-cm` must be provided to populate the height-normalized value.
- Interpretation / notes: Derived from the native TotalSegmentator `abdominal_muscles` label without regrouping. The region is measured over the full 3D extent returned by the `abdominal_muscles` task.

#### `abdominal_muscles_regional_muscles_pectoralis_major_right_volume_mm3`

- Clinical label: Regional T4-L4 muscle metric for pectoralis major right (volume)
- Unit: mm³
- Family: T4-L4 regional muscle volumes
- Source metrics file: abdominal_muscles_metrics.json
- Model / task: TotalSegmentator `abdominal_muscles`
- Detection / computation method: Voxel count multiplied by the native voxel volume.
- Appears when: When `abdominal_muscles` was run as a public output or as a dependency of `--with-odiasp` or `--with-tissue`.
- Interpretation / notes: Derived from the native TotalSegmentator `abdominal_muscles` label without regrouping. The region is measured over the full 3D extent returned by the `abdominal_muscles` task.

#### `abdominal_muscles_regional_muscles_pectoralis_major_right_voxel_count`

- Clinical label: Regional T4-L4 muscle metric for pectoralis major right (voxel count)
- Unit: value
- Family: T4-L4 regional muscle volumes
- Source metrics file: abdominal_muscles_metrics.json
- Model / task: TotalSegmentator `abdominal_muscles`
- Detection / computation method: Number of voxels equal to this native muscle label in `abdominal_muscles_multilabel.nii.gz`.
- Appears when: When `abdominal_muscles` was run as a public output or as a dependency of `--with-odiasp` or `--with-tissue`.
- Interpretation / notes: Derived from the native TotalSegmentator `abdominal_muscles` label without regrouping. The region is measured over the full 3D extent returned by the `abdominal_muscles` task.

#### `abdominal_muscles_regional_muscles_psoas_major_left_label_id`

- Clinical label: Regional T4-L4 muscle metric for psoas major left (label id)
- Unit: value
- Family: T4-L4 regional muscle volumes
- Source metrics file: abdominal_muscles_metrics.json
- Model / task: TotalSegmentator `abdominal_muscles`
- Detection / computation method: Numeric label identifier from the `abdominal_muscles` label map.
- Appears when: When `abdominal_muscles` was run as a public output or as a dependency of `--with-odiasp` or `--with-tissue`.
- Interpretation / notes: Derived from the native TotalSegmentator `abdominal_muscles` label without regrouping. The region is measured over the full 3D extent returned by the `abdominal_muscles` task.

#### `abdominal_muscles_regional_muscles_psoas_major_left_volume_cm3`

- Clinical label: Regional T4-L4 muscle metric for psoas major left (volume)
- Unit: cm³
- Family: T4-L4 regional muscle volumes
- Source metrics file: abdominal_muscles_metrics.json
- Model / task: TotalSegmentator `abdominal_muscles`
- Detection / computation method: Regional volume converted from mm³ to cm³.
- Appears when: When `abdominal_muscles` was run as a public output or as a dependency of `--with-odiasp` or `--with-tissue`.
- Interpretation / notes: Derived from the native TotalSegmentator `abdominal_muscles` label without regrouping. The region is measured over the full 3D extent returned by the `abdominal_muscles` task.

#### `abdominal_muscles_regional_muscles_psoas_major_left_volume_cm3_per_m3`

- Clinical label: Regional T4-L4 muscle metric for psoas major left (height-normalized volume)
- Unit: cm³/m³
- Family: T4-L4 regional muscle volumes
- Source metrics file: abdominal_muscles_metrics.json
- Model / task: TotalSegmentator `abdominal_muscles`
- Detection / computation method: Regional volume in cm³ divided by patient height cubed in m³.
- Appears when: When `abdominal_muscles` was run as a public output or as a dependency of `--with-odiasp` or `--with-tissue`. In addition, `--height-cm` must be provided to populate the height-normalized value.
- Interpretation / notes: Derived from the native TotalSegmentator `abdominal_muscles` label without regrouping. The region is measured over the full 3D extent returned by the `abdominal_muscles` task.

#### `abdominal_muscles_regional_muscles_psoas_major_left_volume_mm3`

- Clinical label: Regional T4-L4 muscle metric for psoas major left (volume)
- Unit: mm³
- Family: T4-L4 regional muscle volumes
- Source metrics file: abdominal_muscles_metrics.json
- Model / task: TotalSegmentator `abdominal_muscles`
- Detection / computation method: Voxel count multiplied by the native voxel volume.
- Appears when: When `abdominal_muscles` was run as a public output or as a dependency of `--with-odiasp` or `--with-tissue`.
- Interpretation / notes: Derived from the native TotalSegmentator `abdominal_muscles` label without regrouping. The region is measured over the full 3D extent returned by the `abdominal_muscles` task.

#### `abdominal_muscles_regional_muscles_psoas_major_left_voxel_count`

- Clinical label: Regional T4-L4 muscle metric for psoas major left (voxel count)
- Unit: value
- Family: T4-L4 regional muscle volumes
- Source metrics file: abdominal_muscles_metrics.json
- Model / task: TotalSegmentator `abdominal_muscles`
- Detection / computation method: Number of voxels equal to this native muscle label in `abdominal_muscles_multilabel.nii.gz`.
- Appears when: When `abdominal_muscles` was run as a public output or as a dependency of `--with-odiasp` or `--with-tissue`.
- Interpretation / notes: Derived from the native TotalSegmentator `abdominal_muscles` label without regrouping. The region is measured over the full 3D extent returned by the `abdominal_muscles` task.

#### `abdominal_muscles_regional_muscles_psoas_major_right_label_id`

- Clinical label: Regional T4-L4 muscle metric for psoas major right (label id)
- Unit: value
- Family: T4-L4 regional muscle volumes
- Source metrics file: abdominal_muscles_metrics.json
- Model / task: TotalSegmentator `abdominal_muscles`
- Detection / computation method: Numeric label identifier from the `abdominal_muscles` label map.
- Appears when: When `abdominal_muscles` was run as a public output or as a dependency of `--with-odiasp` or `--with-tissue`.
- Interpretation / notes: Derived from the native TotalSegmentator `abdominal_muscles` label without regrouping. The region is measured over the full 3D extent returned by the `abdominal_muscles` task.

#### `abdominal_muscles_regional_muscles_psoas_major_right_volume_cm3`

- Clinical label: Regional T4-L4 muscle metric for psoas major right (volume)
- Unit: cm³
- Family: T4-L4 regional muscle volumes
- Source metrics file: abdominal_muscles_metrics.json
- Model / task: TotalSegmentator `abdominal_muscles`
- Detection / computation method: Regional volume converted from mm³ to cm³.
- Appears when: When `abdominal_muscles` was run as a public output or as a dependency of `--with-odiasp` or `--with-tissue`.
- Interpretation / notes: Derived from the native TotalSegmentator `abdominal_muscles` label without regrouping. The region is measured over the full 3D extent returned by the `abdominal_muscles` task.

#### `abdominal_muscles_regional_muscles_psoas_major_right_volume_cm3_per_m3`

- Clinical label: Regional T4-L4 muscle metric for psoas major right (height-normalized volume)
- Unit: cm³/m³
- Family: T4-L4 regional muscle volumes
- Source metrics file: abdominal_muscles_metrics.json
- Model / task: TotalSegmentator `abdominal_muscles`
- Detection / computation method: Regional volume in cm³ divided by patient height cubed in m³.
- Appears when: When `abdominal_muscles` was run as a public output or as a dependency of `--with-odiasp` or `--with-tissue`. In addition, `--height-cm` must be provided to populate the height-normalized value.
- Interpretation / notes: Derived from the native TotalSegmentator `abdominal_muscles` label without regrouping. The region is measured over the full 3D extent returned by the `abdominal_muscles` task.

#### `abdominal_muscles_regional_muscles_psoas_major_right_volume_mm3`

- Clinical label: Regional T4-L4 muscle metric for psoas major right (volume)
- Unit: mm³
- Family: T4-L4 regional muscle volumes
- Source metrics file: abdominal_muscles_metrics.json
- Model / task: TotalSegmentator `abdominal_muscles`
- Detection / computation method: Voxel count multiplied by the native voxel volume.
- Appears when: When `abdominal_muscles` was run as a public output or as a dependency of `--with-odiasp` or `--with-tissue`.
- Interpretation / notes: Derived from the native TotalSegmentator `abdominal_muscles` label without regrouping. The region is measured over the full 3D extent returned by the `abdominal_muscles` task.

#### `abdominal_muscles_regional_muscles_psoas_major_right_voxel_count`

- Clinical label: Regional T4-L4 muscle metric for psoas major right (voxel count)
- Unit: value
- Family: T4-L4 regional muscle volumes
- Source metrics file: abdominal_muscles_metrics.json
- Model / task: TotalSegmentator `abdominal_muscles`
- Detection / computation method: Number of voxels equal to this native muscle label in `abdominal_muscles_multilabel.nii.gz`.
- Appears when: When `abdominal_muscles` was run as a public output or as a dependency of `--with-odiasp` or `--with-tissue`.
- Interpretation / notes: Derived from the native TotalSegmentator `abdominal_muscles` label without regrouping. The region is measured over the full 3D extent returned by the `abdominal_muscles` task.

#### `abdominal_muscles_regional_muscles_quadratus_lumborum_left_label_id`

- Clinical label: Regional T4-L4 muscle metric for quadratus lumborum left (label id)
- Unit: value
- Family: T4-L4 regional muscle volumes
- Source metrics file: abdominal_muscles_metrics.json
- Model / task: TotalSegmentator `abdominal_muscles`
- Detection / computation method: Numeric label identifier from the `abdominal_muscles` label map.
- Appears when: When `abdominal_muscles` was run as a public output or as a dependency of `--with-odiasp` or `--with-tissue`.
- Interpretation / notes: Derived from the native TotalSegmentator `abdominal_muscles` label without regrouping. The region is measured over the full 3D extent returned by the `abdominal_muscles` task.

#### `abdominal_muscles_regional_muscles_quadratus_lumborum_left_volume_cm3`

- Clinical label: Regional T4-L4 muscle metric for quadratus lumborum left (volume)
- Unit: cm³
- Family: T4-L4 regional muscle volumes
- Source metrics file: abdominal_muscles_metrics.json
- Model / task: TotalSegmentator `abdominal_muscles`
- Detection / computation method: Regional volume converted from mm³ to cm³.
- Appears when: When `abdominal_muscles` was run as a public output or as a dependency of `--with-odiasp` or `--with-tissue`.
- Interpretation / notes: Derived from the native TotalSegmentator `abdominal_muscles` label without regrouping. The region is measured over the full 3D extent returned by the `abdominal_muscles` task.

#### `abdominal_muscles_regional_muscles_quadratus_lumborum_left_volume_cm3_per_m3`

- Clinical label: Regional T4-L4 muscle metric for quadratus lumborum left (height-normalized volume)
- Unit: cm³/m³
- Family: T4-L4 regional muscle volumes
- Source metrics file: abdominal_muscles_metrics.json
- Model / task: TotalSegmentator `abdominal_muscles`
- Detection / computation method: Regional volume in cm³ divided by patient height cubed in m³.
- Appears when: When `abdominal_muscles` was run as a public output or as a dependency of `--with-odiasp` or `--with-tissue`. In addition, `--height-cm` must be provided to populate the height-normalized value.
- Interpretation / notes: Derived from the native TotalSegmentator `abdominal_muscles` label without regrouping. The region is measured over the full 3D extent returned by the `abdominal_muscles` task.

#### `abdominal_muscles_regional_muscles_quadratus_lumborum_left_volume_mm3`

- Clinical label: Regional T4-L4 muscle metric for quadratus lumborum left (volume)
- Unit: mm³
- Family: T4-L4 regional muscle volumes
- Source metrics file: abdominal_muscles_metrics.json
- Model / task: TotalSegmentator `abdominal_muscles`
- Detection / computation method: Voxel count multiplied by the native voxel volume.
- Appears when: When `abdominal_muscles` was run as a public output or as a dependency of `--with-odiasp` or `--with-tissue`.
- Interpretation / notes: Derived from the native TotalSegmentator `abdominal_muscles` label without regrouping. The region is measured over the full 3D extent returned by the `abdominal_muscles` task.

#### `abdominal_muscles_regional_muscles_quadratus_lumborum_left_voxel_count`

- Clinical label: Regional T4-L4 muscle metric for quadratus lumborum left (voxel count)
- Unit: value
- Family: T4-L4 regional muscle volumes
- Source metrics file: abdominal_muscles_metrics.json
- Model / task: TotalSegmentator `abdominal_muscles`
- Detection / computation method: Number of voxels equal to this native muscle label in `abdominal_muscles_multilabel.nii.gz`.
- Appears when: When `abdominal_muscles` was run as a public output or as a dependency of `--with-odiasp` or `--with-tissue`.
- Interpretation / notes: Derived from the native TotalSegmentator `abdominal_muscles` label without regrouping. The region is measured over the full 3D extent returned by the `abdominal_muscles` task.

#### `abdominal_muscles_regional_muscles_quadratus_lumborum_right_label_id`

- Clinical label: Regional T4-L4 muscle metric for quadratus lumborum right (label id)
- Unit: value
- Family: T4-L4 regional muscle volumes
- Source metrics file: abdominal_muscles_metrics.json
- Model / task: TotalSegmentator `abdominal_muscles`
- Detection / computation method: Numeric label identifier from the `abdominal_muscles` label map.
- Appears when: When `abdominal_muscles` was run as a public output or as a dependency of `--with-odiasp` or `--with-tissue`.
- Interpretation / notes: Derived from the native TotalSegmentator `abdominal_muscles` label without regrouping. The region is measured over the full 3D extent returned by the `abdominal_muscles` task.

#### `abdominal_muscles_regional_muscles_quadratus_lumborum_right_volume_cm3`

- Clinical label: Regional T4-L4 muscle metric for quadratus lumborum right (volume)
- Unit: cm³
- Family: T4-L4 regional muscle volumes
- Source metrics file: abdominal_muscles_metrics.json
- Model / task: TotalSegmentator `abdominal_muscles`
- Detection / computation method: Regional volume converted from mm³ to cm³.
- Appears when: When `abdominal_muscles` was run as a public output or as a dependency of `--with-odiasp` or `--with-tissue`.
- Interpretation / notes: Derived from the native TotalSegmentator `abdominal_muscles` label without regrouping. The region is measured over the full 3D extent returned by the `abdominal_muscles` task.

#### `abdominal_muscles_regional_muscles_quadratus_lumborum_right_volume_cm3_per_m3`

- Clinical label: Regional T4-L4 muscle metric for quadratus lumborum right (height-normalized volume)
- Unit: cm³/m³
- Family: T4-L4 regional muscle volumes
- Source metrics file: abdominal_muscles_metrics.json
- Model / task: TotalSegmentator `abdominal_muscles`
- Detection / computation method: Regional volume in cm³ divided by patient height cubed in m³.
- Appears when: When `abdominal_muscles` was run as a public output or as a dependency of `--with-odiasp` or `--with-tissue`. In addition, `--height-cm` must be provided to populate the height-normalized value.
- Interpretation / notes: Derived from the native TotalSegmentator `abdominal_muscles` label without regrouping. The region is measured over the full 3D extent returned by the `abdominal_muscles` task.

#### `abdominal_muscles_regional_muscles_quadratus_lumborum_right_volume_mm3`

- Clinical label: Regional T4-L4 muscle metric for quadratus lumborum right (volume)
- Unit: mm³
- Family: T4-L4 regional muscle volumes
- Source metrics file: abdominal_muscles_metrics.json
- Model / task: TotalSegmentator `abdominal_muscles`
- Detection / computation method: Voxel count multiplied by the native voxel volume.
- Appears when: When `abdominal_muscles` was run as a public output or as a dependency of `--with-odiasp` or `--with-tissue`.
- Interpretation / notes: Derived from the native TotalSegmentator `abdominal_muscles` label without regrouping. The region is measured over the full 3D extent returned by the `abdominal_muscles` task.

#### `abdominal_muscles_regional_muscles_quadratus_lumborum_right_voxel_count`

- Clinical label: Regional T4-L4 muscle metric for quadratus lumborum right (voxel count)
- Unit: value
- Family: T4-L4 regional muscle volumes
- Source metrics file: abdominal_muscles_metrics.json
- Model / task: TotalSegmentator `abdominal_muscles`
- Detection / computation method: Number of voxels equal to this native muscle label in `abdominal_muscles_multilabel.nii.gz`.
- Appears when: When `abdominal_muscles` was run as a public output or as a dependency of `--with-odiasp` or `--with-tissue`.
- Interpretation / notes: Derived from the native TotalSegmentator `abdominal_muscles` label without regrouping. The region is measured over the full 3D extent returned by the `abdominal_muscles` task.

#### `abdominal_muscles_regional_muscles_rectus_abdominis_left_label_id`

- Clinical label: Regional T4-L4 muscle metric for rectus abdominis left (label id)
- Unit: value
- Family: T4-L4 regional muscle volumes
- Source metrics file: abdominal_muscles_metrics.json
- Model / task: TotalSegmentator `abdominal_muscles`
- Detection / computation method: Numeric label identifier from the `abdominal_muscles` label map.
- Appears when: When `abdominal_muscles` was run as a public output or as a dependency of `--with-odiasp` or `--with-tissue`.
- Interpretation / notes: Derived from the native TotalSegmentator `abdominal_muscles` label without regrouping. The region is measured over the full 3D extent returned by the `abdominal_muscles` task.

#### `abdominal_muscles_regional_muscles_rectus_abdominis_left_volume_cm3`

- Clinical label: Regional T4-L4 muscle metric for rectus abdominis left (volume)
- Unit: cm³
- Family: T4-L4 regional muscle volumes
- Source metrics file: abdominal_muscles_metrics.json
- Model / task: TotalSegmentator `abdominal_muscles`
- Detection / computation method: Regional volume converted from mm³ to cm³.
- Appears when: When `abdominal_muscles` was run as a public output or as a dependency of `--with-odiasp` or `--with-tissue`.
- Interpretation / notes: Derived from the native TotalSegmentator `abdominal_muscles` label without regrouping. The region is measured over the full 3D extent returned by the `abdominal_muscles` task.

#### `abdominal_muscles_regional_muscles_rectus_abdominis_left_volume_cm3_per_m3`

- Clinical label: Regional T4-L4 muscle metric for rectus abdominis left (height-normalized volume)
- Unit: cm³/m³
- Family: T4-L4 regional muscle volumes
- Source metrics file: abdominal_muscles_metrics.json
- Model / task: TotalSegmentator `abdominal_muscles`
- Detection / computation method: Regional volume in cm³ divided by patient height cubed in m³.
- Appears when: When `abdominal_muscles` was run as a public output or as a dependency of `--with-odiasp` or `--with-tissue`. In addition, `--height-cm` must be provided to populate the height-normalized value.
- Interpretation / notes: Derived from the native TotalSegmentator `abdominal_muscles` label without regrouping. The region is measured over the full 3D extent returned by the `abdominal_muscles` task.

#### `abdominal_muscles_regional_muscles_rectus_abdominis_left_volume_mm3`

- Clinical label: Regional T4-L4 muscle metric for rectus abdominis left (volume)
- Unit: mm³
- Family: T4-L4 regional muscle volumes
- Source metrics file: abdominal_muscles_metrics.json
- Model / task: TotalSegmentator `abdominal_muscles`
- Detection / computation method: Voxel count multiplied by the native voxel volume.
- Appears when: When `abdominal_muscles` was run as a public output or as a dependency of `--with-odiasp` or `--with-tissue`.
- Interpretation / notes: Derived from the native TotalSegmentator `abdominal_muscles` label without regrouping. The region is measured over the full 3D extent returned by the `abdominal_muscles` task.

#### `abdominal_muscles_regional_muscles_rectus_abdominis_left_voxel_count`

- Clinical label: Regional T4-L4 muscle metric for rectus abdominis left (voxel count)
- Unit: value
- Family: T4-L4 regional muscle volumes
- Source metrics file: abdominal_muscles_metrics.json
- Model / task: TotalSegmentator `abdominal_muscles`
- Detection / computation method: Number of voxels equal to this native muscle label in `abdominal_muscles_multilabel.nii.gz`.
- Appears when: When `abdominal_muscles` was run as a public output or as a dependency of `--with-odiasp` or `--with-tissue`.
- Interpretation / notes: Derived from the native TotalSegmentator `abdominal_muscles` label without regrouping. The region is measured over the full 3D extent returned by the `abdominal_muscles` task.

#### `abdominal_muscles_regional_muscles_rectus_abdominis_right_label_id`

- Clinical label: Regional T4-L4 muscle metric for rectus abdominis right (label id)
- Unit: value
- Family: T4-L4 regional muscle volumes
- Source metrics file: abdominal_muscles_metrics.json
- Model / task: TotalSegmentator `abdominal_muscles`
- Detection / computation method: Numeric label identifier from the `abdominal_muscles` label map.
- Appears when: When `abdominal_muscles` was run as a public output or as a dependency of `--with-odiasp` or `--with-tissue`.
- Interpretation / notes: Derived from the native TotalSegmentator `abdominal_muscles` label without regrouping. The region is measured over the full 3D extent returned by the `abdominal_muscles` task.

#### `abdominal_muscles_regional_muscles_rectus_abdominis_right_volume_cm3`

- Clinical label: Regional T4-L4 muscle metric for rectus abdominis right (volume)
- Unit: cm³
- Family: T4-L4 regional muscle volumes
- Source metrics file: abdominal_muscles_metrics.json
- Model / task: TotalSegmentator `abdominal_muscles`
- Detection / computation method: Regional volume converted from mm³ to cm³.
- Appears when: When `abdominal_muscles` was run as a public output or as a dependency of `--with-odiasp` or `--with-tissue`.
- Interpretation / notes: Derived from the native TotalSegmentator `abdominal_muscles` label without regrouping. The region is measured over the full 3D extent returned by the `abdominal_muscles` task.

#### `abdominal_muscles_regional_muscles_rectus_abdominis_right_volume_cm3_per_m3`

- Clinical label: Regional T4-L4 muscle metric for rectus abdominis right (height-normalized volume)
- Unit: cm³/m³
- Family: T4-L4 regional muscle volumes
- Source metrics file: abdominal_muscles_metrics.json
- Model / task: TotalSegmentator `abdominal_muscles`
- Detection / computation method: Regional volume in cm³ divided by patient height cubed in m³.
- Appears when: When `abdominal_muscles` was run as a public output or as a dependency of `--with-odiasp` or `--with-tissue`. In addition, `--height-cm` must be provided to populate the height-normalized value.
- Interpretation / notes: Derived from the native TotalSegmentator `abdominal_muscles` label without regrouping. The region is measured over the full 3D extent returned by the `abdominal_muscles` task.

#### `abdominal_muscles_regional_muscles_rectus_abdominis_right_volume_mm3`

- Clinical label: Regional T4-L4 muscle metric for rectus abdominis right (volume)
- Unit: mm³
- Family: T4-L4 regional muscle volumes
- Source metrics file: abdominal_muscles_metrics.json
- Model / task: TotalSegmentator `abdominal_muscles`
- Detection / computation method: Voxel count multiplied by the native voxel volume.
- Appears when: When `abdominal_muscles` was run as a public output or as a dependency of `--with-odiasp` or `--with-tissue`.
- Interpretation / notes: Derived from the native TotalSegmentator `abdominal_muscles` label without regrouping. The region is measured over the full 3D extent returned by the `abdominal_muscles` task.

#### `abdominal_muscles_regional_muscles_rectus_abdominis_right_voxel_count`

- Clinical label: Regional T4-L4 muscle metric for rectus abdominis right (voxel count)
- Unit: value
- Family: T4-L4 regional muscle volumes
- Source metrics file: abdominal_muscles_metrics.json
- Model / task: TotalSegmentator `abdominal_muscles`
- Detection / computation method: Number of voxels equal to this native muscle label in `abdominal_muscles_multilabel.nii.gz`.
- Appears when: When `abdominal_muscles` was run as a public output or as a dependency of `--with-odiasp` or `--with-tissue`.
- Interpretation / notes: Derived from the native TotalSegmentator `abdominal_muscles` label without regrouping. The region is measured over the full 3D extent returned by the `abdominal_muscles` task.

#### `abdominal_muscles_regional_muscles_serratus_anterior_left_label_id`

- Clinical label: Regional T4-L4 muscle metric for serratus anterior left (label id)
- Unit: value
- Family: T4-L4 regional muscle volumes
- Source metrics file: abdominal_muscles_metrics.json
- Model / task: TotalSegmentator `abdominal_muscles`
- Detection / computation method: Numeric label identifier from the `abdominal_muscles` label map.
- Appears when: When `abdominal_muscles` was run as a public output or as a dependency of `--with-odiasp` or `--with-tissue`.
- Interpretation / notes: Derived from the native TotalSegmentator `abdominal_muscles` label without regrouping. The region is measured over the full 3D extent returned by the `abdominal_muscles` task.

#### `abdominal_muscles_regional_muscles_serratus_anterior_left_volume_cm3`

- Clinical label: Regional T4-L4 muscle metric for serratus anterior left (volume)
- Unit: cm³
- Family: T4-L4 regional muscle volumes
- Source metrics file: abdominal_muscles_metrics.json
- Model / task: TotalSegmentator `abdominal_muscles`
- Detection / computation method: Regional volume converted from mm³ to cm³.
- Appears when: When `abdominal_muscles` was run as a public output or as a dependency of `--with-odiasp` or `--with-tissue`.
- Interpretation / notes: Derived from the native TotalSegmentator `abdominal_muscles` label without regrouping. The region is measured over the full 3D extent returned by the `abdominal_muscles` task.

#### `abdominal_muscles_regional_muscles_serratus_anterior_left_volume_cm3_per_m3`

- Clinical label: Regional T4-L4 muscle metric for serratus anterior left (height-normalized volume)
- Unit: cm³/m³
- Family: T4-L4 regional muscle volumes
- Source metrics file: abdominal_muscles_metrics.json
- Model / task: TotalSegmentator `abdominal_muscles`
- Detection / computation method: Regional volume in cm³ divided by patient height cubed in m³.
- Appears when: When `abdominal_muscles` was run as a public output or as a dependency of `--with-odiasp` or `--with-tissue`. In addition, `--height-cm` must be provided to populate the height-normalized value.
- Interpretation / notes: Derived from the native TotalSegmentator `abdominal_muscles` label without regrouping. The region is measured over the full 3D extent returned by the `abdominal_muscles` task.

#### `abdominal_muscles_regional_muscles_serratus_anterior_left_volume_mm3`

- Clinical label: Regional T4-L4 muscle metric for serratus anterior left (volume)
- Unit: mm³
- Family: T4-L4 regional muscle volumes
- Source metrics file: abdominal_muscles_metrics.json
- Model / task: TotalSegmentator `abdominal_muscles`
- Detection / computation method: Voxel count multiplied by the native voxel volume.
- Appears when: When `abdominal_muscles` was run as a public output or as a dependency of `--with-odiasp` or `--with-tissue`.
- Interpretation / notes: Derived from the native TotalSegmentator `abdominal_muscles` label without regrouping. The region is measured over the full 3D extent returned by the `abdominal_muscles` task.

#### `abdominal_muscles_regional_muscles_serratus_anterior_left_voxel_count`

- Clinical label: Regional T4-L4 muscle metric for serratus anterior left (voxel count)
- Unit: value
- Family: T4-L4 regional muscle volumes
- Source metrics file: abdominal_muscles_metrics.json
- Model / task: TotalSegmentator `abdominal_muscles`
- Detection / computation method: Number of voxels equal to this native muscle label in `abdominal_muscles_multilabel.nii.gz`.
- Appears when: When `abdominal_muscles` was run as a public output or as a dependency of `--with-odiasp` or `--with-tissue`.
- Interpretation / notes: Derived from the native TotalSegmentator `abdominal_muscles` label without regrouping. The region is measured over the full 3D extent returned by the `abdominal_muscles` task.

#### `abdominal_muscles_regional_muscles_serratus_anterior_right_label_id`

- Clinical label: Regional T4-L4 muscle metric for serratus anterior right (label id)
- Unit: value
- Family: T4-L4 regional muscle volumes
- Source metrics file: abdominal_muscles_metrics.json
- Model / task: TotalSegmentator `abdominal_muscles`
- Detection / computation method: Numeric label identifier from the `abdominal_muscles` label map.
- Appears when: When `abdominal_muscles` was run as a public output or as a dependency of `--with-odiasp` or `--with-tissue`.
- Interpretation / notes: Derived from the native TotalSegmentator `abdominal_muscles` label without regrouping. The region is measured over the full 3D extent returned by the `abdominal_muscles` task.

#### `abdominal_muscles_regional_muscles_serratus_anterior_right_volume_cm3`

- Clinical label: Regional T4-L4 muscle metric for serratus anterior right (volume)
- Unit: cm³
- Family: T4-L4 regional muscle volumes
- Source metrics file: abdominal_muscles_metrics.json
- Model / task: TotalSegmentator `abdominal_muscles`
- Detection / computation method: Regional volume converted from mm³ to cm³.
- Appears when: When `abdominal_muscles` was run as a public output or as a dependency of `--with-odiasp` or `--with-tissue`.
- Interpretation / notes: Derived from the native TotalSegmentator `abdominal_muscles` label without regrouping. The region is measured over the full 3D extent returned by the `abdominal_muscles` task.

#### `abdominal_muscles_regional_muscles_serratus_anterior_right_volume_cm3_per_m3`

- Clinical label: Regional T4-L4 muscle metric for serratus anterior right (height-normalized volume)
- Unit: cm³/m³
- Family: T4-L4 regional muscle volumes
- Source metrics file: abdominal_muscles_metrics.json
- Model / task: TotalSegmentator `abdominal_muscles`
- Detection / computation method: Regional volume in cm³ divided by patient height cubed in m³.
- Appears when: When `abdominal_muscles` was run as a public output or as a dependency of `--with-odiasp` or `--with-tissue`. In addition, `--height-cm` must be provided to populate the height-normalized value.
- Interpretation / notes: Derived from the native TotalSegmentator `abdominal_muscles` label without regrouping. The region is measured over the full 3D extent returned by the `abdominal_muscles` task.

#### `abdominal_muscles_regional_muscles_serratus_anterior_right_volume_mm3`

- Clinical label: Regional T4-L4 muscle metric for serratus anterior right (volume)
- Unit: mm³
- Family: T4-L4 regional muscle volumes
- Source metrics file: abdominal_muscles_metrics.json
- Model / task: TotalSegmentator `abdominal_muscles`
- Detection / computation method: Voxel count multiplied by the native voxel volume.
- Appears when: When `abdominal_muscles` was run as a public output or as a dependency of `--with-odiasp` or `--with-tissue`.
- Interpretation / notes: Derived from the native TotalSegmentator `abdominal_muscles` label without regrouping. The region is measured over the full 3D extent returned by the `abdominal_muscles` task.

#### `abdominal_muscles_regional_muscles_serratus_anterior_right_voxel_count`

- Clinical label: Regional T4-L4 muscle metric for serratus anterior right (voxel count)
- Unit: value
- Family: T4-L4 regional muscle volumes
- Source metrics file: abdominal_muscles_metrics.json
- Model / task: TotalSegmentator `abdominal_muscles`
- Detection / computation method: Number of voxels equal to this native muscle label in `abdominal_muscles_multilabel.nii.gz`.
- Appears when: When `abdominal_muscles` was run as a public output or as a dependency of `--with-odiasp` or `--with-tissue`.
- Interpretation / notes: Derived from the native TotalSegmentator `abdominal_muscles` label without regrouping. The region is measured over the full 3D extent returned by the `abdominal_muscles` task.

#### `abdominal_muscles_regional_muscles_transversospinalis_left_label_id`

- Clinical label: Regional T4-L4 muscle metric for transversospinalis left (label id)
- Unit: value
- Family: T4-L4 regional muscle volumes
- Source metrics file: abdominal_muscles_metrics.json
- Model / task: TotalSegmentator `abdominal_muscles`
- Detection / computation method: Numeric label identifier from the `abdominal_muscles` label map.
- Appears when: When `abdominal_muscles` was run as a public output or as a dependency of `--with-odiasp` or `--with-tissue`.
- Interpretation / notes: Derived from the native TotalSegmentator `abdominal_muscles` label without regrouping. The region is measured over the full 3D extent returned by the `abdominal_muscles` task.

#### `abdominal_muscles_regional_muscles_transversospinalis_left_volume_cm3`

- Clinical label: Regional T4-L4 muscle metric for transversospinalis left (volume)
- Unit: cm³
- Family: T4-L4 regional muscle volumes
- Source metrics file: abdominal_muscles_metrics.json
- Model / task: TotalSegmentator `abdominal_muscles`
- Detection / computation method: Regional volume converted from mm³ to cm³.
- Appears when: When `abdominal_muscles` was run as a public output or as a dependency of `--with-odiasp` or `--with-tissue`.
- Interpretation / notes: Derived from the native TotalSegmentator `abdominal_muscles` label without regrouping. The region is measured over the full 3D extent returned by the `abdominal_muscles` task.

#### `abdominal_muscles_regional_muscles_transversospinalis_left_volume_cm3_per_m3`

- Clinical label: Regional T4-L4 muscle metric for transversospinalis left (height-normalized volume)
- Unit: cm³/m³
- Family: T4-L4 regional muscle volumes
- Source metrics file: abdominal_muscles_metrics.json
- Model / task: TotalSegmentator `abdominal_muscles`
- Detection / computation method: Regional volume in cm³ divided by patient height cubed in m³.
- Appears when: When `abdominal_muscles` was run as a public output or as a dependency of `--with-odiasp` or `--with-tissue`. In addition, `--height-cm` must be provided to populate the height-normalized value.
- Interpretation / notes: Derived from the native TotalSegmentator `abdominal_muscles` label without regrouping. The region is measured over the full 3D extent returned by the `abdominal_muscles` task.

#### `abdominal_muscles_regional_muscles_transversospinalis_left_volume_mm3`

- Clinical label: Regional T4-L4 muscle metric for transversospinalis left (volume)
- Unit: mm³
- Family: T4-L4 regional muscle volumes
- Source metrics file: abdominal_muscles_metrics.json
- Model / task: TotalSegmentator `abdominal_muscles`
- Detection / computation method: Voxel count multiplied by the native voxel volume.
- Appears when: When `abdominal_muscles` was run as a public output or as a dependency of `--with-odiasp` or `--with-tissue`.
- Interpretation / notes: Derived from the native TotalSegmentator `abdominal_muscles` label without regrouping. The region is measured over the full 3D extent returned by the `abdominal_muscles` task.

#### `abdominal_muscles_regional_muscles_transversospinalis_left_voxel_count`

- Clinical label: Regional T4-L4 muscle metric for transversospinalis left (voxel count)
- Unit: value
- Family: T4-L4 regional muscle volumes
- Source metrics file: abdominal_muscles_metrics.json
- Model / task: TotalSegmentator `abdominal_muscles`
- Detection / computation method: Number of voxels equal to this native muscle label in `abdominal_muscles_multilabel.nii.gz`.
- Appears when: When `abdominal_muscles` was run as a public output or as a dependency of `--with-odiasp` or `--with-tissue`.
- Interpretation / notes: Derived from the native TotalSegmentator `abdominal_muscles` label without regrouping. The region is measured over the full 3D extent returned by the `abdominal_muscles` task.

#### `abdominal_muscles_regional_muscles_transversospinalis_right_label_id`

- Clinical label: Regional T4-L4 muscle metric for transversospinalis right (label id)
- Unit: value
- Family: T4-L4 regional muscle volumes
- Source metrics file: abdominal_muscles_metrics.json
- Model / task: TotalSegmentator `abdominal_muscles`
- Detection / computation method: Numeric label identifier from the `abdominal_muscles` label map.
- Appears when: When `abdominal_muscles` was run as a public output or as a dependency of `--with-odiasp` or `--with-tissue`.
- Interpretation / notes: Derived from the native TotalSegmentator `abdominal_muscles` label without regrouping. The region is measured over the full 3D extent returned by the `abdominal_muscles` task.

#### `abdominal_muscles_regional_muscles_transversospinalis_right_volume_cm3`

- Clinical label: Regional T4-L4 muscle metric for transversospinalis right (volume)
- Unit: cm³
- Family: T4-L4 regional muscle volumes
- Source metrics file: abdominal_muscles_metrics.json
- Model / task: TotalSegmentator `abdominal_muscles`
- Detection / computation method: Regional volume converted from mm³ to cm³.
- Appears when: When `abdominal_muscles` was run as a public output or as a dependency of `--with-odiasp` or `--with-tissue`.
- Interpretation / notes: Derived from the native TotalSegmentator `abdominal_muscles` label without regrouping. The region is measured over the full 3D extent returned by the `abdominal_muscles` task.

#### `abdominal_muscles_regional_muscles_transversospinalis_right_volume_cm3_per_m3`

- Clinical label: Regional T4-L4 muscle metric for transversospinalis right (height-normalized volume)
- Unit: cm³/m³
- Family: T4-L4 regional muscle volumes
- Source metrics file: abdominal_muscles_metrics.json
- Model / task: TotalSegmentator `abdominal_muscles`
- Detection / computation method: Regional volume in cm³ divided by patient height cubed in m³.
- Appears when: When `abdominal_muscles` was run as a public output or as a dependency of `--with-odiasp` or `--with-tissue`. In addition, `--height-cm` must be provided to populate the height-normalized value.
- Interpretation / notes: Derived from the native TotalSegmentator `abdominal_muscles` label without regrouping. The region is measured over the full 3D extent returned by the `abdominal_muscles` task.

#### `abdominal_muscles_regional_muscles_transversospinalis_right_volume_mm3`

- Clinical label: Regional T4-L4 muscle metric for transversospinalis right (volume)
- Unit: mm³
- Family: T4-L4 regional muscle volumes
- Source metrics file: abdominal_muscles_metrics.json
- Model / task: TotalSegmentator `abdominal_muscles`
- Detection / computation method: Voxel count multiplied by the native voxel volume.
- Appears when: When `abdominal_muscles` was run as a public output or as a dependency of `--with-odiasp` or `--with-tissue`.
- Interpretation / notes: Derived from the native TotalSegmentator `abdominal_muscles` label without regrouping. The region is measured over the full 3D extent returned by the `abdominal_muscles` task.

#### `abdominal_muscles_regional_muscles_transversospinalis_right_voxel_count`

- Clinical label: Regional T4-L4 muscle metric for transversospinalis right (voxel count)
- Unit: value
- Family: T4-L4 regional muscle volumes
- Source metrics file: abdominal_muscles_metrics.json
- Model / task: TotalSegmentator `abdominal_muscles`
- Detection / computation method: Number of voxels equal to this native muscle label in `abdominal_muscles_multilabel.nii.gz`.
- Appears when: When `abdominal_muscles` was run as a public output or as a dependency of `--with-odiasp` or `--with-tissue`.
- Interpretation / notes: Derived from the native TotalSegmentator `abdominal_muscles` label without regrouping. The region is measured over the full 3D extent returned by the `abdominal_muscles` task.

#### `abdominal_muscles_regional_muscles_trapezius_left_label_id`

- Clinical label: Regional T4-L4 muscle metric for trapezius left (label id)
- Unit: value
- Family: T4-L4 regional muscle volumes
- Source metrics file: abdominal_muscles_metrics.json
- Model / task: TotalSegmentator `abdominal_muscles`
- Detection / computation method: Numeric label identifier from the `abdominal_muscles` label map.
- Appears when: When `abdominal_muscles` was run as a public output or as a dependency of `--with-odiasp` or `--with-tissue`.
- Interpretation / notes: Derived from the native TotalSegmentator `abdominal_muscles` label without regrouping. The region is measured over the full 3D extent returned by the `abdominal_muscles` task.

#### `abdominal_muscles_regional_muscles_trapezius_left_volume_cm3`

- Clinical label: Regional T4-L4 muscle metric for trapezius left (volume)
- Unit: cm³
- Family: T4-L4 regional muscle volumes
- Source metrics file: abdominal_muscles_metrics.json
- Model / task: TotalSegmentator `abdominal_muscles`
- Detection / computation method: Regional volume converted from mm³ to cm³.
- Appears when: When `abdominal_muscles` was run as a public output or as a dependency of `--with-odiasp` or `--with-tissue`.
- Interpretation / notes: Derived from the native TotalSegmentator `abdominal_muscles` label without regrouping. The region is measured over the full 3D extent returned by the `abdominal_muscles` task.

#### `abdominal_muscles_regional_muscles_trapezius_left_volume_cm3_per_m3`

- Clinical label: Regional T4-L4 muscle metric for trapezius left (height-normalized volume)
- Unit: cm³/m³
- Family: T4-L4 regional muscle volumes
- Source metrics file: abdominal_muscles_metrics.json
- Model / task: TotalSegmentator `abdominal_muscles`
- Detection / computation method: Regional volume in cm³ divided by patient height cubed in m³.
- Appears when: When `abdominal_muscles` was run as a public output or as a dependency of `--with-odiasp` or `--with-tissue`. In addition, `--height-cm` must be provided to populate the height-normalized value.
- Interpretation / notes: Derived from the native TotalSegmentator `abdominal_muscles` label without regrouping. The region is measured over the full 3D extent returned by the `abdominal_muscles` task.

#### `abdominal_muscles_regional_muscles_trapezius_left_volume_mm3`

- Clinical label: Regional T4-L4 muscle metric for trapezius left (volume)
- Unit: mm³
- Family: T4-L4 regional muscle volumes
- Source metrics file: abdominal_muscles_metrics.json
- Model / task: TotalSegmentator `abdominal_muscles`
- Detection / computation method: Voxel count multiplied by the native voxel volume.
- Appears when: When `abdominal_muscles` was run as a public output or as a dependency of `--with-odiasp` or `--with-tissue`.
- Interpretation / notes: Derived from the native TotalSegmentator `abdominal_muscles` label without regrouping. The region is measured over the full 3D extent returned by the `abdominal_muscles` task.

#### `abdominal_muscles_regional_muscles_trapezius_left_voxel_count`

- Clinical label: Regional T4-L4 muscle metric for trapezius left (voxel count)
- Unit: value
- Family: T4-L4 regional muscle volumes
- Source metrics file: abdominal_muscles_metrics.json
- Model / task: TotalSegmentator `abdominal_muscles`
- Detection / computation method: Number of voxels equal to this native muscle label in `abdominal_muscles_multilabel.nii.gz`.
- Appears when: When `abdominal_muscles` was run as a public output or as a dependency of `--with-odiasp` or `--with-tissue`.
- Interpretation / notes: Derived from the native TotalSegmentator `abdominal_muscles` label without regrouping. The region is measured over the full 3D extent returned by the `abdominal_muscles` task.

#### `abdominal_muscles_regional_muscles_trapezius_right_label_id`

- Clinical label: Regional T4-L4 muscle metric for trapezius right (label id)
- Unit: value
- Family: T4-L4 regional muscle volumes
- Source metrics file: abdominal_muscles_metrics.json
- Model / task: TotalSegmentator `abdominal_muscles`
- Detection / computation method: Numeric label identifier from the `abdominal_muscles` label map.
- Appears when: When `abdominal_muscles` was run as a public output or as a dependency of `--with-odiasp` or `--with-tissue`.
- Interpretation / notes: Derived from the native TotalSegmentator `abdominal_muscles` label without regrouping. The region is measured over the full 3D extent returned by the `abdominal_muscles` task.

#### `abdominal_muscles_regional_muscles_trapezius_right_volume_cm3`

- Clinical label: Regional T4-L4 muscle metric for trapezius right (volume)
- Unit: cm³
- Family: T4-L4 regional muscle volumes
- Source metrics file: abdominal_muscles_metrics.json
- Model / task: TotalSegmentator `abdominal_muscles`
- Detection / computation method: Regional volume converted from mm³ to cm³.
- Appears when: When `abdominal_muscles` was run as a public output or as a dependency of `--with-odiasp` or `--with-tissue`.
- Interpretation / notes: Derived from the native TotalSegmentator `abdominal_muscles` label without regrouping. The region is measured over the full 3D extent returned by the `abdominal_muscles` task.

#### `abdominal_muscles_regional_muscles_trapezius_right_volume_cm3_per_m3`

- Clinical label: Regional T4-L4 muscle metric for trapezius right (height-normalized volume)
- Unit: cm³/m³
- Family: T4-L4 regional muscle volumes
- Source metrics file: abdominal_muscles_metrics.json
- Model / task: TotalSegmentator `abdominal_muscles`
- Detection / computation method: Regional volume in cm³ divided by patient height cubed in m³.
- Appears when: When `abdominal_muscles` was run as a public output or as a dependency of `--with-odiasp` or `--with-tissue`. In addition, `--height-cm` must be provided to populate the height-normalized value.
- Interpretation / notes: Derived from the native TotalSegmentator `abdominal_muscles` label without regrouping. The region is measured over the full 3D extent returned by the `abdominal_muscles` task.

#### `abdominal_muscles_regional_muscles_trapezius_right_volume_mm3`

- Clinical label: Regional T4-L4 muscle metric for trapezius right (volume)
- Unit: mm³
- Family: T4-L4 regional muscle volumes
- Source metrics file: abdominal_muscles_metrics.json
- Model / task: TotalSegmentator `abdominal_muscles`
- Detection / computation method: Voxel count multiplied by the native voxel volume.
- Appears when: When `abdominal_muscles` was run as a public output or as a dependency of `--with-odiasp` or `--with-tissue`.
- Interpretation / notes: Derived from the native TotalSegmentator `abdominal_muscles` label without regrouping. The region is measured over the full 3D extent returned by the `abdominal_muscles` task.

#### `abdominal_muscles_regional_muscles_trapezius_right_voxel_count`

- Clinical label: Regional T4-L4 muscle metric for trapezius right (voxel count)
- Unit: value
- Family: T4-L4 regional muscle volumes
- Source metrics file: abdominal_muscles_metrics.json
- Model / task: TotalSegmentator `abdominal_muscles`
- Detection / computation method: Number of voxels equal to this native muscle label in `abdominal_muscles_multilabel.nii.gz`.
- Appears when: When `abdominal_muscles` was run as a public output or as a dependency of `--with-odiasp` or `--with-tissue`.
- Interpretation / notes: Derived from the native TotalSegmentator `abdominal_muscles` label without regrouping. The region is measured over the full 3D extent returned by the `abdominal_muscles` task.

#### `abdominal_muscles_segmentation_name`

- Clinical label: segmentation name
- Unit: text
- Family: Abdominal Muscles
- Source metrics file: abdominal_muscles_metrics.json
- Model / task: TotalSegmentator `abdominal_muscles`
- Detection / computation method: Metadata copied from `abdominal_muscles_metrics.json`.
- Appears when: When `abdominal_muscles` was run as a public output or as a dependency of `--with-odiasp` or `--with-tissue`.
- Interpretation / notes: Technical provenance field.

#### `abdominal_muscles_slice_count`

- Clinical label: Number of occupied muscle z slices
- Unit: voxels
- Family: Abdominal Muscles
- Source metrics file: abdominal_muscles_metrics.json
- Model / task: TotalSegmentator `abdominal_muscles`
- Detection / computation method: Number of z slices between `z_min` and `z_max`, inclusive.
- Appears when: When `abdominal_muscles` was run as a public output or as a dependency of `--with-odiasp` or `--with-tissue`.
- Interpretation / notes: Derived from the native `abdominal_muscles` output.

#### `abdominal_muscles_source_task`

- Clinical label: source task
- Unit: text
- Family: Abdominal Muscles
- Source metrics file: abdominal_muscles_metrics.json
- Model / task: TotalSegmentator `abdominal_muscles`
- Detection / computation method: Metadata copied from `abdominal_muscles_metrics.json`.
- Appears when: When `abdominal_muscles` was run as a public output or as a dependency of `--with-odiasp` or `--with-tissue`.
- Interpretation / notes: Technical provenance field.

#### `abdominal_muscles_task`

- Clinical label: task
- Unit: text
- Family: Abdominal Muscles
- Source metrics file: abdominal_muscles_metrics.json
- Model / task: TotalSegmentator `abdominal_muscles`
- Detection / computation method: Metadata copied from `abdominal_muscles_metrics.json`.
- Appears when: When `abdominal_muscles` was run as a public output or as a dependency of `--with-odiasp` or `--with-tissue`.
- Interpretation / notes: Technical provenance field.

#### `abdominal_muscles_total_muscle_mean_hu`

- Clinical label: Mean 3D muscle density over T4-L4
- Unit: HU
- Family: Abdominal Muscles
- Source metrics file: abdominal_muscles_metrics.json
- Model / task: TotalSegmentator `abdominal_muscles`
- Detection / computation method: Mean CT attenuation over the 3D union of all native `abdominal_muscles` voxels after resampling the CT onto the NIfTI grid.
- Appears when: When `abdominal_muscles` was run as a public output or as a dependency of `--with-odiasp` or `--with-tissue`.
- Interpretation / notes: Exploratory tridimensional muscle density derived from the union of all native `abdominal_muscles` labels.

#### `abdominal_muscles_total_muscle_volume_cm3`

- Clinical label: Total T4-L4 muscle volume
- Unit: cm³
- Family: Abdominal Muscles
- Source metrics file: abdominal_muscles_metrics.json
- Model / task: TotalSegmentator `abdominal_muscles`
- Detection / computation method: Total T4-L4 muscle volume converted from mm³ to cm³.
- Appears when: When `abdominal_muscles` was run as a public output or as a dependency of `--with-odiasp` or `--with-tissue`.
- Interpretation / notes: Exploratory 3D T4-L4 muscle volume derived from the dedicated `abdominal_muscles` task.

#### `abdominal_muscles_total_muscle_volume_cm3_per_m3`

- Clinical label: Height-normalized total T4-L4 muscle volume
- Unit: cm³/m³
- Family: Abdominal Muscles
- Source metrics file: abdominal_muscles_metrics.json
- Model / task: TotalSegmentator `abdominal_muscles`
- Detection / computation method: Total T4-L4 muscle volume in cm³ divided by patient height cubed in m³.
- Appears when: When `abdominal_muscles` was run as a public output or as a dependency of `--with-odiasp` or `--with-tissue`. In addition, `--height-cm` must be provided to populate the height-normalized value.
- Interpretation / notes: Exploratory 3D T4-L4 muscle volume derived from the dedicated `abdominal_muscles` task.

#### `abdominal_muscles_total_muscle_volume_mm3`

- Clinical label: Total T4-L4 muscle volume
- Unit: mm³
- Family: Abdominal Muscles
- Source metrics file: abdominal_muscles_metrics.json
- Model / task: TotalSegmentator `abdominal_muscles`
- Detection / computation method: Union voxel count multiplied by voxel volume.
- Appears when: When `abdominal_muscles` was run as a public output or as a dependency of `--with-odiasp` or `--with-tissue`.
- Interpretation / notes: Derived from the native `abdominal_muscles` output.

#### `abdominal_muscles_total_muscle_voxel_count`

- Clinical label: Total T4-L4 muscle voxel count
- Unit: voxels
- Family: Abdominal Muscles
- Source metrics file: abdominal_muscles_metrics.json
- Model / task: TotalSegmentator `abdominal_muscles`
- Detection / computation method: Number of voxels in the union of all native `abdominal_muscles` labels.
- Appears when: When `abdominal_muscles` was run as a public output or as a dependency of `--with-odiasp` or `--with-tissue`.
- Interpretation / notes: Derived from the native `abdominal_muscles` output.

#### `abdominal_muscles_voxel_spacing_mm_x`

- Clinical label: Voxel spacing x
- Unit: mm
- Family: Abdominal Muscles
- Source metrics file: abdominal_muscles_metrics.json
- Model / task: TotalSegmentator `abdominal_muscles`
- Detection / computation method: Native voxel spacing along x, taken from the NIfTI header.
- Appears when: When `abdominal_muscles` was run as a public output or as a dependency of `--with-odiasp` or `--with-tissue`.
- Interpretation / notes: Derived from the native `abdominal_muscles` output.

#### `abdominal_muscles_voxel_spacing_mm_y`

- Clinical label: Voxel spacing y
- Unit: mm
- Family: Abdominal Muscles
- Source metrics file: abdominal_muscles_metrics.json
- Model / task: TotalSegmentator `abdominal_muscles`
- Detection / computation method: Native voxel spacing along y, taken from the NIfTI header.
- Appears when: When `abdominal_muscles` was run as a public output or as a dependency of `--with-odiasp` or `--with-tissue`.
- Interpretation / notes: Derived from the native `abdominal_muscles` output.

#### `abdominal_muscles_voxel_spacing_mm_z`

- Clinical label: Voxel spacing z
- Unit: mm
- Family: Abdominal Muscles
- Source metrics file: abdominal_muscles_metrics.json
- Model / task: TotalSegmentator `abdominal_muscles`
- Detection / computation method: Native voxel spacing along z, taken from the NIfTI header.
- Appears when: When `abdominal_muscles` was run as a public output or as a dependency of `--with-odiasp` or `--with-tissue`.
- Interpretation / notes: Derived from the native `abdominal_muscles` output.

#### `abdominal_muscles_voxel_volume_mm3`

- Clinical label: Voxel volume
- Unit: mm³
- Family: Abdominal Muscles
- Source metrics file: abdominal_muscles_metrics.json
- Model / task: TotalSegmentator `abdominal_muscles`
- Detection / computation method: Product of x, y and z voxel spacing.
- Appears when: When `abdominal_muscles` was run as a public output or as a dependency of `--with-odiasp` or `--with-tissue`.
- Interpretation / notes: Used to convert voxel counts into physical volumes.

#### `abdominal_muscles_warnings`

- Clinical label: Abdominal muscle warnings
- Unit: value
- Family: Abdominal Muscles
- Source metrics file: abdominal_muscles_metrics.json
- Model / task: TotalSegmentator `abdominal_muscles`
- Detection / computation method: Warnings emitted during abdominal muscle metric extraction.
- Appears when: When `abdominal_muscles` was run as a public output or as a dependency of `--with-odiasp` or `--with-tissue`.
- Interpretation / notes: Derived from the native `abdominal_muscles` output.

#### `abdominal_muscles_z_max`

- Clinical label: Superior muscle z boundary
- Unit: index
- Family: Abdominal Muscles
- Source metrics file: abdominal_muscles_metrics.json
- Model / task: TotalSegmentator `abdominal_muscles`
- Detection / computation method: Last occupied z slice of the `abdominal_muscles` segmentation.
- Appears when: When `abdominal_muscles` was run as a public output or as a dependency of `--with-odiasp` or `--with-tissue`.
- Interpretation / notes: Derived from the native `abdominal_muscles` output.

#### `abdominal_muscles_z_min`

- Clinical label: Inferior muscle z boundary
- Unit: index
- Family: Abdominal Muscles
- Source metrics file: abdominal_muscles_metrics.json
- Model / task: TotalSegmentator `abdominal_muscles`
- Detection / computation method: First occupied z slice of the `abdominal_muscles` segmentation.
- Appears when: When `abdominal_muscles` was run as a public output or as a dependency of `--with-odiasp` or `--with-tissue`.
- Interpretation / notes: Derived from the native `abdominal_muscles` output.

### ODIASP

#### `odiasp_status`

- Clinical label: ODIASP status
- Unit: categorical status
- Family: Pipeline diagnostics
- Source metrics file: CSV row metadata or branch status/metrics files
- Model / task: Not applicable
- Detection / computation method: Status exported by the CSV writer for `status`. Values are typically `success`, `failed`, or `not_requested`.
- Appears when: Always present for the corresponding branch status field.
- Interpretation / notes: Status of the `ODIASP` metrics branch.

#### `odiasp_csma_cm2`

- Clinical label: L3 cross-sectional muscle area
- Unit: cm²
- Family: ODIASP
- Source metrics file: odiasp/metrics.json
- Model / task: ODIASP-compatible L3 pipeline using TotalSegmentator `abdominal_muscles` + `vertebrae_L3` from `total`
- Detection / computation method: Compatibility alias of `sma_cm2`.
- Appears when: When `--with-odiasp` succeeded.
- Interpretation / notes: Equivalent to the ODIASP-style cross-sectional muscle area at L3.

#### `odiasp_height_cm`

- Clinical label: Patient height
- Unit: cm
- Family: ODIASP
- Source metrics file: odiasp/metrics.json
- Model / task: ODIASP-compatible L3 pipeline using TotalSegmentator `abdominal_muscles` + `vertebrae_L3` from `total`
- Detection / computation method: Height passed with `--height-cm`.
- Appears when: When `--with-odiasp` succeeded.
- Interpretation / notes: Needed to compute height-normalized ODIASP area metrics.

#### `odiasp_height_m`

- Clinical label: Patient height in metres
- Unit: m
- Family: ODIASP
- Source metrics file: odiasp/metrics.json
- Model / task: ODIASP-compatible L3 pipeline using TotalSegmentator `abdominal_muscles` + `vertebrae_L3` from `total`
- Detection / computation method: Height converted from centimetres to metres.
- Appears when: When `--with-odiasp` succeeded.
- Interpretation / notes: Intermediate normalization value.

#### `odiasp_included_label_ids`

- Clinical label: Included abdominal muscle label ids
- Unit: text
- Family: ODIASP
- Source metrics file: odiasp/metrics.json
- Model / task: ODIASP-compatible L3 pipeline using TotalSegmentator `abdominal_muscles` + `vertebrae_L3` from `total`
- Detection / computation method: List of native `abdominal_muscles` label ids merged into the ODIASP muscle mask.
- Appears when: When `--with-odiasp` succeeded.
- Interpretation / notes: Pipe-separated CSV field describing the labels included in the ODIASP muscle union.

#### `odiasp_included_label_names`

- Clinical label: Included abdominal muscle label names
- Unit: text
- Family: ODIASP
- Source metrics file: odiasp/metrics.json
- Model / task: ODIASP-compatible L3 pipeline using TotalSegmentator `abdominal_muscles` + `vertebrae_L3` from `total`
- Detection / computation method: List of native `abdominal_muscles` label names merged into the ODIASP muscle mask.
- Appears when: When `--with-odiasp` succeeded.
- Interpretation / notes: Pipe-separated CSV field describing the labels included in the ODIASP muscle union.

#### `odiasp_l3_bone_density_vertebra_mean_hu`

- Clinical label: L3 opportunistic bone density, whole vertebra
- Unit: HU
- Family: ODIASP
- Source metrics file: odiasp/metrics.json
- Model / task: ODIASP-compatible L3 pipeline using TotalSegmentator `abdominal_muscles` + `vertebrae_L3` from `total`
- Detection / computation method: Mean Hounsfield units of the whole `vertebrae_L3` mask on the same ODIASP L3 slice.
- Appears when: When `--with-odiasp` succeeded.
- Interpretation / notes: Opportunistic bone density proxy measured on the exact ODIASP slice.

#### `odiasp_l3_bone_density_vertebral_body_mean_hu`

- Clinical label: L3 opportunistic bone density, vertebral body heuristic
- Unit: HU
- Family: ODIASP
- Source metrics file: odiasp/metrics.json
- Model / task: ODIASP-compatible L3 pipeline using TotalSegmentator `abdominal_muscles` + `vertebrae_L3` from `total`
- Detection / computation method: Mean Hounsfield units inside an automatic central ROI extracted from the L3 vertebral mask on the same ODIASP slice.
- Appears when: When `--with-odiasp` succeeded.
- Interpretation / notes: Automatic approximation of the vertebral body only, with fallback to whole-vertebra density when the ROI is empty.

#### `odiasp_l3_slice_index`

- Clinical label: ODIASP L3 slice index
- Unit: index
- Family: ODIASP
- Source metrics file: odiasp/metrics.json
- Model / task: ODIASP-compatible L3 pipeline using TotalSegmentator `abdominal_muscles` + `vertebrae_L3` from `total`
- Detection / computation method: Median occupied z slice of the `vertebrae_L3` mask.
- Appears when: When `--with-odiasp` succeeded.
- Interpretation / notes: This is the single reference slice used for all ODIASP L3 metrics.

#### `odiasp_l3_tissue_composition_intermuscular_fat_area_cm2`

- Clinical label: L3 intermuscular fat (area)
- Unit: cm²
- Family: ODIASP L3 tissue composition
- Source metrics file: odiasp/metrics.json
- Model / task: ODIASP-compatible L3 pipeline using TotalSegmentator `abdominal_muscles` + `vertebrae_L3` from `total`
- Detection / computation method: Pixel count multiplied by the in-plane pixel area on the ODIASP L3 slice.
- Appears when: Only when `--with-odiasp --with-tissue` both succeed.
- Interpretation / notes: Exploratory muscle quality-related fat compartment, often referred to as IMAT at L3.

#### `odiasp_l3_tissue_composition_intermuscular_fat_area_cm2_per_m2`

- Clinical label: L3 intermuscular fat (height-normalized area)
- Unit: cm²/m²
- Family: ODIASP L3 tissue composition
- Source metrics file: odiasp/metrics.json
- Model / task: ODIASP-compatible L3 pipeline using TotalSegmentator `abdominal_muscles` + `vertebrae_L3` from `total`
- Detection / computation method: L3 area in cm² divided by patient height squared in m².
- Appears when: Only when `--with-odiasp --with-tissue` both succeed. In addition, `--height-cm` must be provided to populate the height-normalized value.
- Interpretation / notes: Exploratory muscle quality-related fat compartment, often referred to as IMAT at L3.

#### `odiasp_l3_tissue_composition_intermuscular_fat_label_id`

- Clinical label: L3 intermuscular fat (label id)
- Unit: value
- Family: ODIASP L3 tissue composition
- Source metrics file: odiasp/metrics.json
- Model / task: ODIASP-compatible L3 pipeline using TotalSegmentator `abdominal_muscles` + `vertebrae_L3` from `total`
- Detection / computation method: Numeric label identifier from the `tissue_4_types` label map.
- Appears when: Only when `--with-odiasp --with-tissue` both succeed.
- Interpretation / notes: Exploratory muscle quality-related fat compartment, often referred to as IMAT at L3.

#### `odiasp_l3_tissue_composition_intermuscular_fat_mean_hu`

- Clinical label: L3 intermuscular fat (mean density)
- Unit: value
- Family: ODIASP L3 tissue composition
- Source metrics file: odiasp/metrics.json
- Model / task: ODIASP-compatible L3 pipeline using TotalSegmentator `abdominal_muscles` + `vertebrae_L3` from `total`
- Detection / computation method: Mean Hounsfield units inside this tissue class on the ODIASP L3 slice.
- Appears when: Only when `--with-odiasp --with-tissue` both succeed.
- Interpretation / notes: Exploratory muscle quality-related fat compartment, often referred to as IMAT at L3.

#### `odiasp_l3_tissue_composition_intermuscular_fat_pixel_count`

- Clinical label: L3 intermuscular fat (pixel count)
- Unit: value
- Family: ODIASP L3 tissue composition
- Source metrics file: odiasp/metrics.json
- Model / task: ODIASP-compatible L3 pipeline using TotalSegmentator `abdominal_muscles` + `vertebrae_L3` from `total`
- Detection / computation method: Number of pixels of this tissue class on the exact ODIASP L3 slice.
- Appears when: Only when `--with-odiasp --with-tissue` both succeed.
- Interpretation / notes: Exploratory muscle quality-related fat compartment, often referred to as IMAT at L3.

#### `odiasp_l3_tissue_composition_skeletal_muscle_tissue_4_types_area_cm2`

- Clinical label: L3 skeletal muscle from tissue_4_types (area)
- Unit: cm²
- Family: ODIASP L3 tissue composition
- Source metrics file: odiasp/metrics.json
- Model / task: ODIASP-compatible L3 pipeline using TotalSegmentator `abdominal_muscles` + `vertebrae_L3` from `total`
- Detection / computation method: Pixel count multiplied by the in-plane pixel area on the ODIASP L3 slice.
- Appears when: Only when `--with-odiasp --with-tissue` both succeed.
- Interpretation / notes: Complementary tissue-derived muscle measurement on the same L3 slice. ODIASP canonical muscle metrics still come from `abdominal_muscles`.

#### `odiasp_l3_tissue_composition_skeletal_muscle_tissue_4_types_area_cm2_per_m2`

- Clinical label: L3 skeletal muscle from tissue_4_types (height-normalized area)
- Unit: cm²/m²
- Family: ODIASP L3 tissue composition
- Source metrics file: odiasp/metrics.json
- Model / task: ODIASP-compatible L3 pipeline using TotalSegmentator `abdominal_muscles` + `vertebrae_L3` from `total`
- Detection / computation method: L3 area in cm² divided by patient height squared in m².
- Appears when: Only when `--with-odiasp --with-tissue` both succeed. In addition, `--height-cm` must be provided to populate the height-normalized value.
- Interpretation / notes: Complementary tissue-derived muscle measurement on the same L3 slice. ODIASP canonical muscle metrics still come from `abdominal_muscles`.

#### `odiasp_l3_tissue_composition_skeletal_muscle_tissue_4_types_label_id`

- Clinical label: L3 skeletal muscle from tissue_4_types (label id)
- Unit: value
- Family: ODIASP L3 tissue composition
- Source metrics file: odiasp/metrics.json
- Model / task: ODIASP-compatible L3 pipeline using TotalSegmentator `abdominal_muscles` + `vertebrae_L3` from `total`
- Detection / computation method: Numeric label identifier from the `tissue_4_types` label map.
- Appears when: Only when `--with-odiasp --with-tissue` both succeed.
- Interpretation / notes: Complementary tissue-derived muscle measurement on the same L3 slice. ODIASP canonical muscle metrics still come from `abdominal_muscles`.

#### `odiasp_l3_tissue_composition_skeletal_muscle_tissue_4_types_mean_hu`

- Clinical label: L3 skeletal muscle from tissue_4_types (mean density)
- Unit: value
- Family: ODIASP L3 tissue composition
- Source metrics file: odiasp/metrics.json
- Model / task: ODIASP-compatible L3 pipeline using TotalSegmentator `abdominal_muscles` + `vertebrae_L3` from `total`
- Detection / computation method: Mean Hounsfield units inside this tissue class on the ODIASP L3 slice.
- Appears when: Only when `--with-odiasp --with-tissue` both succeed.
- Interpretation / notes: Complementary tissue-derived muscle measurement on the same L3 slice. ODIASP canonical muscle metrics still come from `abdominal_muscles`.

#### `odiasp_l3_tissue_composition_skeletal_muscle_tissue_4_types_pixel_count`

- Clinical label: L3 skeletal muscle from tissue_4_types (pixel count)
- Unit: value
- Family: ODIASP L3 tissue composition
- Source metrics file: odiasp/metrics.json
- Model / task: ODIASP-compatible L3 pipeline using TotalSegmentator `abdominal_muscles` + `vertebrae_L3` from `total`
- Detection / computation method: Number of pixels of this tissue class on the exact ODIASP L3 slice.
- Appears when: Only when `--with-odiasp --with-tissue` both succeed.
- Interpretation / notes: Complementary tissue-derived muscle measurement on the same L3 slice. ODIASP canonical muscle metrics still come from `abdominal_muscles`.

#### `odiasp_l3_tissue_composition_slice_index`

- Clinical label: L3 tissue composition slice index
- Unit: index
- Family: ODIASP L3 tissue composition
- Source metrics file: odiasp/metrics.json
- Model / task: ODIASP-compatible L3 pipeline using TotalSegmentator `abdominal_muscles` + `vertebrae_L3` from `total`
- Detection / computation method: ODIASP L3 slice index reused for the tissue enrichment metrics.
- Appears when: Only when `--with-odiasp --with-tissue` both succeed.
- Interpretation / notes: Should match `odiasp_l3_slice_index`.

#### `odiasp_l3_tissue_composition_source_task`

- Clinical label: L3 tissue composition source task
- Unit: text
- Family: ODIASP L3 tissue composition
- Source metrics file: odiasp/metrics.json
- Model / task: ODIASP-compatible L3 pipeline using TotalSegmentator `abdominal_muscles` + `vertebrae_L3` from `total`
- Detection / computation method: Metadata copied from ODIASP L3 tissue composition.
- Appears when: Only when `--with-odiasp --with-tissue` both succeed.
- Interpretation / notes: Technical provenance field.

#### `odiasp_l3_tissue_composition_subcutaneous_fat_area_cm2`

- Clinical label: L3 subcutaneous fat (area)
- Unit: cm²
- Family: ODIASP L3 tissue composition
- Source metrics file: odiasp/metrics.json
- Model / task: ODIASP-compatible L3 pipeline using TotalSegmentator `abdominal_muscles` + `vertebrae_L3` from `total`
- Detection / computation method: Pixel count multiplied by the in-plane pixel area on the ODIASP L3 slice.
- Appears when: Only when `--with-odiasp --with-tissue` both succeed.
- Interpretation / notes: Secondary adiposity measure, often referred to clinically as SAT area at L3.

#### `odiasp_l3_tissue_composition_subcutaneous_fat_area_cm2_per_m2`

- Clinical label: L3 subcutaneous fat (height-normalized area)
- Unit: cm²/m²
- Family: ODIASP L3 tissue composition
- Source metrics file: odiasp/metrics.json
- Model / task: ODIASP-compatible L3 pipeline using TotalSegmentator `abdominal_muscles` + `vertebrae_L3` from `total`
- Detection / computation method: L3 area in cm² divided by patient height squared in m².
- Appears when: Only when `--with-odiasp --with-tissue` both succeed. In addition, `--height-cm` must be provided to populate the height-normalized value.
- Interpretation / notes: Secondary adiposity measure, often referred to clinically as SAT area at L3.

#### `odiasp_l3_tissue_composition_subcutaneous_fat_label_id`

- Clinical label: L3 subcutaneous fat (label id)
- Unit: value
- Family: ODIASP L3 tissue composition
- Source metrics file: odiasp/metrics.json
- Model / task: ODIASP-compatible L3 pipeline using TotalSegmentator `abdominal_muscles` + `vertebrae_L3` from `total`
- Detection / computation method: Numeric label identifier from the `tissue_4_types` label map.
- Appears when: Only when `--with-odiasp --with-tissue` both succeed.
- Interpretation / notes: Secondary adiposity measure, often referred to clinically as SAT area at L3.

#### `odiasp_l3_tissue_composition_subcutaneous_fat_mean_hu`

- Clinical label: L3 subcutaneous fat (mean density)
- Unit: value
- Family: ODIASP L3 tissue composition
- Source metrics file: odiasp/metrics.json
- Model / task: ODIASP-compatible L3 pipeline using TotalSegmentator `abdominal_muscles` + `vertebrae_L3` from `total`
- Detection / computation method: Mean Hounsfield units inside this tissue class on the ODIASP L3 slice.
- Appears when: Only when `--with-odiasp --with-tissue` both succeed.
- Interpretation / notes: Secondary adiposity measure, often referred to clinically as SAT area at L3.

#### `odiasp_l3_tissue_composition_subcutaneous_fat_pixel_count`

- Clinical label: L3 subcutaneous fat (pixel count)
- Unit: value
- Family: ODIASP L3 tissue composition
- Source metrics file: odiasp/metrics.json
- Model / task: ODIASP-compatible L3 pipeline using TotalSegmentator `abdominal_muscles` + `vertebrae_L3` from `total`
- Detection / computation method: Number of pixels of this tissue class on the exact ODIASP L3 slice.
- Appears when: Only when `--with-odiasp --with-tissue` both succeed.
- Interpretation / notes: Secondary adiposity measure, often referred to clinically as SAT area at L3.

#### `odiasp_l3_tissue_composition_torso_fat_area_cm2`

- Clinical label: L3 torso fat (area)
- Unit: cm²
- Family: ODIASP L3 tissue composition
- Source metrics file: odiasp/metrics.json
- Model / task: ODIASP-compatible L3 pipeline using TotalSegmentator `abdominal_muscles` + `vertebrae_L3` from `total`
- Detection / computation method: Pixel count multiplied by the in-plane pixel area on the ODIASP L3 slice.
- Appears when: Only when `--with-odiasp --with-tissue` both succeed.
- Interpretation / notes: Internal trunk fat measure exported directly from TotalSegmentator `torso_fat`.

#### `odiasp_l3_tissue_composition_torso_fat_area_cm2_per_m2`

- Clinical label: L3 torso fat (height-normalized area)
- Unit: cm²/m²
- Family: ODIASP L3 tissue composition
- Source metrics file: odiasp/metrics.json
- Model / task: ODIASP-compatible L3 pipeline using TotalSegmentator `abdominal_muscles` + `vertebrae_L3` from `total`
- Detection / computation method: L3 area in cm² divided by patient height squared in m².
- Appears when: Only when `--with-odiasp --with-tissue` both succeed. In addition, `--height-cm` must be provided to populate the height-normalized value.
- Interpretation / notes: Internal trunk fat measure exported directly from TotalSegmentator `torso_fat`.

#### `odiasp_l3_tissue_composition_torso_fat_label_id`

- Clinical label: L3 torso fat (label id)
- Unit: value
- Family: ODIASP L3 tissue composition
- Source metrics file: odiasp/metrics.json
- Model / task: ODIASP-compatible L3 pipeline using TotalSegmentator `abdominal_muscles` + `vertebrae_L3` from `total`
- Detection / computation method: Numeric label identifier from the `tissue_4_types` label map.
- Appears when: Only when `--with-odiasp --with-tissue` both succeed.
- Interpretation / notes: Internal trunk fat measure exported directly from TotalSegmentator `torso_fat`.

#### `odiasp_l3_tissue_composition_torso_fat_mean_hu`

- Clinical label: L3 torso fat (mean density)
- Unit: value
- Family: ODIASP L3 tissue composition
- Source metrics file: odiasp/metrics.json
- Model / task: ODIASP-compatible L3 pipeline using TotalSegmentator `abdominal_muscles` + `vertebrae_L3` from `total`
- Detection / computation method: Mean Hounsfield units inside this tissue class on the ODIASP L3 slice.
- Appears when: Only when `--with-odiasp --with-tissue` both succeed.
- Interpretation / notes: Internal trunk fat measure exported directly from TotalSegmentator `torso_fat`.

#### `odiasp_l3_tissue_composition_torso_fat_pixel_count`

- Clinical label: L3 torso fat (pixel count)
- Unit: value
- Family: ODIASP L3 tissue composition
- Source metrics file: odiasp/metrics.json
- Model / task: ODIASP-compatible L3 pipeline using TotalSegmentator `abdominal_muscles` + `vertebrae_L3` from `total`
- Detection / computation method: Number of pixels of this tissue class on the exact ODIASP L3 slice.
- Appears when: Only when `--with-odiasp --with-tissue` both succeed.
- Interpretation / notes: Internal trunk fat measure exported directly from TotalSegmentator `torso_fat`.

#### `odiasp_l3_tissue_composition_torso_to_subcutaneous_area_ratio`

- Clinical label: L3 torso fat to subcutaneous fat area ratio
- Unit: ratio (unitless)
- Family: ODIASP L3 tissue composition
- Source metrics file: odiasp/metrics.json
- Model / task: ODIASP-compatible L3 pipeline using TotalSegmentator `abdominal_muscles` + `vertebrae_L3` from `total`
- Detection / computation method: L3 torso fat area divided by L3 subcutaneous fat area on the same ODIASP slice.
- Appears when: Only when `--with-odiasp --with-tissue` both succeed.
- Interpretation / notes: Exploratory adiposity balance indicator. Not height-normalized.

#### `odiasp_l3_tissue_composition_uses_same_l3_slice_as_odiasp`

- Clinical label: Shared L3 slice flag
- Unit: boolean
- Family: ODIASP L3 tissue composition
- Source metrics file: odiasp/metrics.json
- Model / task: ODIASP-compatible L3 pipeline using TotalSegmentator `abdominal_muscles` + `vertebrae_L3` from `total`
- Detection / computation method: Boolean flag indicating that tissue metrics use exactly the same ODIASP L3 slice.
- Appears when: Only when `--with-odiasp --with-tissue` both succeed.
- Interpretation / notes: Should be `True` when tissue enrichment succeeded.

#### `odiasp_l3_tissue_composition_vat_approx_area_cm2`

- Clinical label: L3 visceral adipose tissue approximation (area)
- Unit: cm²
- Family: ODIASP L3 tissue composition
- Source metrics file: odiasp/metrics.json
- Model / task: ODIASP-compatible L3 pipeline using TotalSegmentator `abdominal_muscles` + `vertebrae_L3` from `total`
- Detection / computation method: Pixel count multiplied by the in-plane pixel area on the ODIASP L3 slice.
- Appears when: Only when `--with-odiasp --with-tissue` both succeed.
- Interpretation / notes: Explicit approximation of VAT derived from `torso_fat`, because `tissue_4_types` does not expose a separate visceral adipose label.

#### `odiasp_l3_tissue_composition_vat_approx_area_cm2_per_m2`

- Clinical label: L3 visceral adipose tissue approximation (height-normalized area)
- Unit: cm²/m²
- Family: ODIASP L3 tissue composition
- Source metrics file: odiasp/metrics.json
- Model / task: ODIASP-compatible L3 pipeline using TotalSegmentator `abdominal_muscles` + `vertebrae_L3` from `total`
- Detection / computation method: L3 area in cm² divided by patient height squared in m².
- Appears when: Only when `--with-odiasp --with-tissue` both succeed. In addition, `--height-cm` must be provided to populate the height-normalized value.
- Interpretation / notes: Explicit approximation of VAT derived from `torso_fat`, because `tissue_4_types` does not expose a separate visceral adipose label.

#### `odiasp_l3_tissue_composition_vat_approx_derived_from`

- Clinical label: L3 visceral adipose tissue approximation (source)
- Unit: value
- Family: ODIASP L3 tissue composition
- Source metrics file: odiasp/metrics.json
- Model / task: ODIASP-compatible L3 pipeline using TotalSegmentator `abdominal_muscles` + `vertebrae_L3` from `total`
- Detection / computation method: Literal metadata field indicating the source structure used to define the approximation.
- Appears when: Only when `--with-odiasp --with-tissue` both succeed.
- Interpretation / notes: Explicit approximation of VAT derived from `torso_fat`, because `tissue_4_types` does not expose a separate visceral adipose label.

#### `odiasp_l3_tissue_composition_vat_approx_mean_hu`

- Clinical label: L3 visceral adipose tissue approximation (mean density)
- Unit: value
- Family: ODIASP L3 tissue composition
- Source metrics file: odiasp/metrics.json
- Model / task: ODIASP-compatible L3 pipeline using TotalSegmentator `abdominal_muscles` + `vertebrae_L3` from `total`
- Detection / computation method: Mean Hounsfield units inside this tissue class on the ODIASP L3 slice.
- Appears when: Only when `--with-odiasp --with-tissue` both succeed.
- Interpretation / notes: Explicit approximation of VAT derived from `torso_fat`, because `tissue_4_types` does not expose a separate visceral adipose label.

#### `odiasp_method`

- Clinical label: ODIASP-compatible method description
- Unit: text
- Family: ODIASP
- Source metrics file: odiasp/metrics.json
- Model / task: ODIASP-compatible L3 pipeline using TotalSegmentator `abdominal_muscles` + `vertebrae_L3` from `total`
- Detection / computation method: Literal method string written in `odiasp/metrics.json`.
- Appears when: When `--with-odiasp` succeeded.
- Interpretation / notes: Documents that ODIASP is approximated with TotalSegmentator `abdominal_muscles` and `vertebrae_L3`.

#### `odiasp_muscle_pixel_count`

- Clinical label: ODIASP muscle pixel count
- Unit: pixels
- Family: ODIASP
- Source metrics file: odiasp/metrics.json
- Model / task: ODIASP-compatible L3 pipeline using TotalSegmentator `abdominal_muscles` + `vertebrae_L3` from `total`
- Detection / computation method: Number of ODIASP muscle pixels on the L3 slice.
- Appears when: When `--with-odiasp` succeeded.
- Interpretation / notes: Intermediate area computation variable.

#### `odiasp_odiasp_compatible`

- Clinical label: ODIASP compatibility flag
- Unit: boolean
- Family: ODIASP
- Source metrics file: odiasp/metrics.json
- Model / task: ODIASP-compatible L3 pipeline using TotalSegmentator `abdominal_muscles` + `vertebrae_L3` from `total`
- Detection / computation method: Boolean marker indicating that the output follows the ODIASP-compatible branch.
- Appears when: When `--with-odiasp` succeeded.
- Interpretation / notes: Indicates this is an ODIASP-style approximation, not the exact historical ODIASP implementation.

#### `odiasp_pixel_spacing_mm_x`

- Clinical label: L3 in-plane pixel spacing x
- Unit: mm
- Family: ODIASP
- Source metrics file: odiasp/metrics.json
- Model / task: ODIASP-compatible L3 pipeline using TotalSegmentator `abdominal_muscles` + `vertebrae_L3` from `total`
- Detection / computation method: First in-plane spacing used to convert pixels to area.
- Appears when: When `--with-odiasp` succeeded.
- Interpretation / notes: Used for L3 area computation.

#### `odiasp_pixel_spacing_mm_y`

- Clinical label: L3 in-plane pixel spacing y
- Unit: mm
- Family: ODIASP
- Source metrics file: odiasp/metrics.json
- Model / task: ODIASP-compatible L3 pipeline using TotalSegmentator `abdominal_muscles` + `vertebrae_L3` from `total`
- Detection / computation method: Second in-plane spacing used to convert pixels to area.
- Appears when: When `--with-odiasp` succeeded.
- Interpretation / notes: Used for L3 area computation.

#### `odiasp_preview_axial`

- Clinical label: preview axial
- Unit: value
- Family: ODIASP preview metadata
- Source metrics file: odiasp/metrics.json
- Model / task: ODIASP-compatible L3 pipeline using TotalSegmentator `abdominal_muscles` + `vertebrae_L3` from `total`
- Detection / computation method: Preview metadata exported alongside the ODIASP axial and sagittal QC images.
- Appears when: When `--with-odiasp` succeeded.
- Interpretation / notes: Technical QA/QC field used to interpret the preview PNGs rather than a clinical endpoint.

#### `odiasp_preview_l3_slice_index_ras`

- Clinical label: preview l3 slice index ras
- Unit: value
- Family: ODIASP preview metadata
- Source metrics file: odiasp/metrics.json
- Model / task: ODIASP-compatible L3 pipeline using TotalSegmentator `abdominal_muscles` + `vertebrae_L3` from `total`
- Detection / computation method: Preview metadata exported alongside the ODIASP axial and sagittal QC images.
- Appears when: When `--with-odiasp` succeeded.
- Interpretation / notes: Technical QA/QC field used to interpret the preview PNGs rather than a clinical endpoint.

#### `odiasp_preview_sagittal`

- Clinical label: preview sagittal
- Unit: value
- Family: ODIASP preview metadata
- Source metrics file: odiasp/metrics.json
- Model / task: ODIASP-compatible L3 pipeline using TotalSegmentator `abdominal_muscles` + `vertebrae_L3` from `total`
- Detection / computation method: Preview metadata exported alongside the ODIASP axial and sagittal QC images.
- Appears when: When `--with-odiasp` succeeded.
- Interpretation / notes: Technical QA/QC field used to interpret the preview PNGs rather than a clinical endpoint.

#### `odiasp_preview_sagittal_x_index_ras`

- Clinical label: preview sagittal x index ras
- Unit: value
- Family: ODIASP preview metadata
- Source metrics file: odiasp/metrics.json
- Model / task: ODIASP-compatible L3 pipeline using TotalSegmentator `abdominal_muscles` + `vertebrae_L3` from `total`
- Detection / computation method: Preview metadata exported alongside the ODIASP axial and sagittal QC images.
- Appears when: When `--with-odiasp` succeeded.
- Interpretation / notes: Technical QA/QC field used to interpret the preview PNGs rather than a clinical endpoint.

#### `odiasp_slice_axis`

- Clinical label: ODIASP slice axis
- Unit: text
- Family: ODIASP
- Source metrics file: odiasp/metrics.json
- Model / task: ODIASP-compatible L3 pipeline using TotalSegmentator `abdominal_muscles` + `vertebrae_L3` from `total`
- Detection / computation method: Axis metadata for the chosen L3 slice.
- Appears when: When `--with-odiasp` succeeded.
- Interpretation / notes: Technical provenance field.

#### `odiasp_sma_cm2`

- Clinical label: L3 skeletal muscle area
- Unit: cm²
- Family: ODIASP
- Source metrics file: odiasp/metrics.json
- Model / task: ODIASP-compatible L3 pipeline using TotalSegmentator `abdominal_muscles` + `vertebrae_L3` from `total`
- Detection / computation method: Number of ODIASP muscle pixels on the selected L3 slice multiplied by the in-plane pixel area.
- Appears when: When `--with-odiasp` succeeded.
- Interpretation / notes: Primary L3 muscle quantity. `csma_cm2` is kept as an equivalent compatibility alias.

#### `odiasp_smd_hu`

- Clinical label: L3 skeletal muscle density
- Unit: HU
- Family: ODIASP
- Source metrics file: odiasp/metrics.json
- Model / task: ODIASP-compatible L3 pipeline using TotalSegmentator `abdominal_muscles` + `vertebrae_L3` from `total`
- Detection / computation method: Mean Hounsfield units inside the ODIASP muscle mask on the selected L3 slice.
- Appears when: When `--with-odiasp` succeeded.
- Interpretation / notes: Primary L3 muscle quality variable. Higher values generally indicate less fatty infiltration.

#### `odiasp_smi_cm2_per_m2`

- Clinical label: L3 skeletal muscle index
- Unit: cm²/m²
- Family: ODIASP
- Source metrics file: odiasp/metrics.json
- Model / task: ODIASP-compatible L3 pipeline using TotalSegmentator `abdominal_muscles` + `vertebrae_L3` from `total`
- Detection / computation method: L3 skeletal muscle area divided by patient height squared.
- Appears when: When `--with-odiasp` succeeded. In addition, `--height-cm` must be provided to populate the height-normalized value.
- Interpretation / notes: This is the canonical height-normalized form of the L3 skeletal muscle area.

#### `odiasp_task`

- Clinical label: ODIASP task name
- Unit: text
- Family: ODIASP
- Source metrics file: odiasp/metrics.json
- Model / task: ODIASP-compatible L3 pipeline using TotalSegmentator `abdominal_muscles` + `vertebrae_L3` from `total`
- Detection / computation method: Task metadata field.
- Appears when: When `--with-odiasp` succeeded.
- Interpretation / notes: Technical provenance field.

#### `odiasp_vertebra_pixel_count`

- Clinical label: ODIASP vertebra pixel count
- Unit: pixels
- Family: ODIASP
- Source metrics file: odiasp/metrics.json
- Model / task: ODIASP-compatible L3 pipeline using TotalSegmentator `abdominal_muscles` + `vertebrae_L3` from `total`
- Detection / computation method: Number of vertebral pixels on the ODIASP L3 slice.
- Appears when: When `--with-odiasp` succeeded.
- Interpretation / notes: Quality-control quantity for the L3 vertebral reference slice.

#### `odiasp_voxel_spacing_mm_x`

- Clinical label: Voxel spacing x for ODIASP volume
- Unit: mm
- Family: ODIASP
- Source metrics file: odiasp/metrics.json
- Model / task: ODIASP-compatible L3 pipeline using TotalSegmentator `abdominal_muscles` + `vertebrae_L3` from `total`
- Detection / computation method: Native voxel spacing x from the NIfTI header.
- Appears when: When `--with-odiasp` succeeded.
- Interpretation / notes: Technical provenance field.

#### `odiasp_voxel_spacing_mm_y`

- Clinical label: Voxel spacing y for ODIASP volume
- Unit: mm
- Family: ODIASP
- Source metrics file: odiasp/metrics.json
- Model / task: ODIASP-compatible L3 pipeline using TotalSegmentator `abdominal_muscles` + `vertebrae_L3` from `total`
- Detection / computation method: Native voxel spacing y from the NIfTI header.
- Appears when: When `--with-odiasp` succeeded.
- Interpretation / notes: Technical provenance field.

#### `odiasp_voxel_spacing_mm_z`

- Clinical label: Voxel spacing z for ODIASP volume
- Unit: mm
- Family: ODIASP
- Source metrics file: odiasp/metrics.json
- Model / task: ODIASP-compatible L3 pipeline using TotalSegmentator `abdominal_muscles` + `vertebrae_L3` from `total`
- Detection / computation method: Native voxel spacing z from the NIfTI header.
- Appears when: When `--with-odiasp` succeeded.
- Interpretation / notes: Technical provenance field.

#### `odiasp_warnings`

- Clinical label: ODIASP warnings
- Unit: text
- Family: ODIASP
- Source metrics file: odiasp/metrics.json
- Model / task: ODIASP-compatible L3 pipeline using TotalSegmentator `abdominal_muscles` + `vertebrae_L3` from `total`
- Detection / computation method: Warnings emitted during ODIASP metric extraction.
- Appears when: When `--with-odiasp` succeeded.
- Interpretation / notes: Includes approximation caveats and missing auxiliary data.

### Tissue Original

#### `tissue_status`

- Clinical label: Overall tissue bundle status
- Unit: categorical status
- Family: Pipeline diagnostics
- Source metrics file: CSV row metadata or branch status/metrics files
- Model / task: Not applicable
- Detection / computation method: Status exported by the CSV writer for `tissue_status`. Values are typically `success`, `failed`, or `not_requested`.
- Appears when: Always present for the corresponding branch status field.
- Interpretation / notes: Reflects whether the `tissue/manifest.json` exists for the branch as a whole.

#### `tissue_original_status`

- Clinical label: Tissue Original status
- Unit: categorical status
- Family: Pipeline diagnostics
- Source metrics file: CSV row metadata or branch status/metrics files
- Model / task: Not applicable
- Detection / computation method: Status exported by the CSV writer for `status`. Values are typically `success`, `failed`, or `not_requested`.
- Appears when: Always present for the corresponding branch status field.
- Interpretation / notes: Status of the `Tissue Original` metrics branch.

#### `tissue_original_crop_strategy`

- Clinical label: Tissue crop strategy
- Unit: text
- Family: Tissue Original
- Source metrics file: tissue/metrics_original.json
- Model / task: TotalSegmentator `tissue_4_types` on the full native CT
- Detection / computation method: Literal crop strategy field from the tissue metrics JSON.
- Appears when: When `--with-tissue` succeeded.
- Interpretation / notes: Documents whether no z-crop was used or whether the abdominal_muscles-derived z-slab was applied.

#### `tissue_original_cropped_shape_x`

- Clinical label: Cropped shape x
- Unit: voxels
- Family: Tissue Original
- Source metrics file: tissue/metrics_original.json
- Model / task: TotalSegmentator `tissue_4_types` on the full native CT
- Detection / computation method: Width of the effective processing volume in voxels.
- Appears when: When `--with-tissue` succeeded.
- Interpretation / notes: Technical geometry field.

#### `tissue_original_cropped_shape_y`

- Clinical label: Cropped shape y
- Unit: voxels
- Family: Tissue Original
- Source metrics file: tissue/metrics_original.json
- Model / task: TotalSegmentator `tissue_4_types` on the full native CT
- Detection / computation method: Height of the effective processing volume in voxels.
- Appears when: When `--with-tissue` succeeded.
- Interpretation / notes: Technical geometry field.

#### `tissue_original_cropped_shape_z`

- Clinical label: Cropped shape z
- Unit: voxels
- Family: Tissue Original
- Source metrics file: tissue/metrics_original.json
- Model / task: TotalSegmentator `tissue_4_types` on the full native CT
- Detection / computation method: Depth of the effective processing volume in voxels.
- Appears when: When `--with-tissue` succeeded.
- Interpretation / notes: Technical geometry field.

#### `tissue_original_height_cm`

- Clinical label: Patient height
- Unit: cm
- Family: Tissue Original
- Source metrics file: tissue/metrics_original.json
- Model / task: TotalSegmentator `tissue_4_types` on the full native CT
- Detection / computation method: Height passed with `--height-cm`.
- Appears when: When `--with-tissue` succeeded.
- Interpretation / notes: Required for height-normalized tissue volumes.

#### `tissue_original_height_m`

- Clinical label: Patient height in metres
- Unit: m
- Family: Tissue Original
- Source metrics file: tissue/metrics_original.json
- Model / task: TotalSegmentator `tissue_4_types` on the full native CT
- Detection / computation method: Height converted from centimetres to metres.
- Appears when: When `--with-tissue` succeeded.
- Interpretation / notes: Intermediate normalization value.

#### `tissue_original_input_shape_x`

- Clinical label: Input shape x
- Unit: voxels
- Family: Tissue Original
- Source metrics file: tissue/metrics_original.json
- Model / task: TotalSegmentator `tissue_4_types` on the full native CT
- Detection / computation method: Native image width in voxels.
- Appears when: When `--with-tissue` succeeded.
- Interpretation / notes: Technical geometry field.

#### `tissue_original_input_shape_y`

- Clinical label: Input shape y
- Unit: voxels
- Family: Tissue Original
- Source metrics file: tissue/metrics_original.json
- Model / task: TotalSegmentator `tissue_4_types` on the full native CT
- Detection / computation method: Native image height in voxels.
- Appears when: When `--with-tissue` succeeded.
- Interpretation / notes: Technical geometry field.

#### `tissue_original_input_shape_z`

- Clinical label: Input shape z
- Unit: voxels
- Family: Tissue Original
- Source metrics file: tissue/metrics_original.json
- Model / task: TotalSegmentator `tissue_4_types` on the full native CT
- Detection / computation method: Native image depth in voxels.
- Appears when: When `--with-tissue` succeeded.
- Interpretation / notes: Technical geometry field.

#### `tissue_original_method`

- Clinical label: Tissue branch method
- Unit: text
- Family: Tissue Original
- Source metrics file: tissue/metrics_original.json
- Model / task: TotalSegmentator `tissue_4_types` on the full native CT
- Detection / computation method: Method string stored in the tissue metrics JSON.
- Appears when: When `--with-tissue` succeeded.
- Interpretation / notes: Describes whether the run used the full scan or the abdominal_muscles z-slab.

#### `tissue_original_preview_axial`

- Clinical label: Axial preview filename
- Unit: text
- Family: Tissue Original
- Source metrics file: tissue/metrics_original.json
- Model / task: TotalSegmentator `tissue_4_types` on the full native CT
- Detection / computation method: QC preview PNG filename.
- Appears when: When `--with-tissue` succeeded.
- Interpretation / notes: Technical QA field.

#### `tissue_original_preview_axial_z_index_ras`

- Clinical label: Axial preview z index
- Unit: index
- Family: Tissue Original
- Source metrics file: tissue/metrics_original.json
- Model / task: TotalSegmentator `tissue_4_types` on the full native CT
- Detection / computation method: RAS z index used for the axial preview.
- Appears when: When `--with-tissue` succeeded.
- Interpretation / notes: Technical QA field.

#### `tissue_original_preview_sagittal`

- Clinical label: Sagittal preview filename
- Unit: text
- Family: Tissue Original
- Source metrics file: tissue/metrics_original.json
- Model / task: TotalSegmentator `tissue_4_types` on the full native CT
- Detection / computation method: QC preview PNG filename.
- Appears when: When `--with-tissue` succeeded.
- Interpretation / notes: Technical QA field.

#### `tissue_original_preview_sagittal_x_index_ras`

- Clinical label: Sagittal preview x index
- Unit: index
- Family: Tissue Original
- Source metrics file: tissue/metrics_original.json
- Model / task: TotalSegmentator `tissue_4_types` on the full native CT
- Detection / computation method: RAS x index used for the sagittal preview.
- Appears when: When `--with-tissue` succeeded.
- Interpretation / notes: Technical QA field.

#### `tissue_original_segmentation_name`

- Clinical label: Tissue segmentation name
- Unit: text
- Family: Tissue Original
- Source metrics file: tissue/metrics_original.json
- Model / task: TotalSegmentator `tissue_4_types` on the full native CT
- Detection / computation method: Segmentation metadata field.
- Appears when: When `--with-tissue` succeeded.
- Interpretation / notes: Human-readable name used for Slicer import.

#### `tissue_original_slice_count`

- Clinical label: Number of z slices in the tissue volume
- Unit: count
- Family: Tissue Original
- Source metrics file: tissue/metrics_original.json
- Model / task: TotalSegmentator `tissue_4_types` on the full native CT
- Detection / computation method: Number of z slices between `z_min` and `z_max`, inclusive.
- Appears when: When `--with-tissue` succeeded.
- Interpretation / notes: Volume extent metadata.

#### `tissue_original_source_task`

- Clinical label: Tissue source task
- Unit: text
- Family: Tissue Original
- Source metrics file: tissue/metrics_original.json
- Model / task: TotalSegmentator `tissue_4_types` on the full native CT
- Detection / computation method: Source task metadata field.
- Appears when: When `--with-tissue` succeeded.
- Interpretation / notes: Technical provenance field.

#### `tissue_original_task`

- Clinical label: Tissue task name
- Unit: text
- Family: Tissue Original
- Source metrics file: tissue/metrics_original.json
- Model / task: TotalSegmentator `tissue_4_types` on the full native CT
- Detection / computation method: Task metadata field.
- Appears when: When `--with-tissue` succeeded.
- Interpretation / notes: Technical provenance field.

#### `tissue_original_tissues_intermuscular_fat_label_id`

- Clinical label: intermuscular fat (label id)
- Unit: value
- Family: 3D tissue composition
- Source metrics file: tissue/metrics_original.json
- Model / task: TotalSegmentator `tissue_4_types` on the full native CT
- Detection / computation method: Numeric label identifier from the `tissue_4_types` label map.
- Appears when: When `--with-tissue` succeeded.
- Interpretation / notes: Fat compartment around and between muscle groups. Measured on the full non-cropped scan.

#### `tissue_original_tissues_intermuscular_fat_mean_hu`

- Clinical label: intermuscular fat (mean density)
- Unit: value
- Family: 3D tissue composition
- Source metrics file: tissue/metrics_original.json
- Model / task: TotalSegmentator `tissue_4_types` on the full native CT
- Detection / computation method: Mean Hounsfield units copied from the TotalSegmentator tissue statistics payload.
- Appears when: When `--with-tissue` succeeded.
- Interpretation / notes: Fat compartment around and between muscle groups. Measured on the full non-cropped scan.

#### `tissue_original_tissues_intermuscular_fat_volume_cm3`

- Clinical label: intermuscular fat (volume)
- Unit: cm³
- Family: 3D tissue composition
- Source metrics file: tissue/metrics_original.json
- Model / task: TotalSegmentator `tissue_4_types` on the full native CT
- Detection / computation method: Volume converted from mm³ to cm³.
- Appears when: When `--with-tissue` succeeded.
- Interpretation / notes: Fat compartment around and between muscle groups. Measured on the full non-cropped scan.

#### `tissue_original_tissues_intermuscular_fat_volume_cm3_per_m3`

- Clinical label: intermuscular fat (height-normalized volume)
- Unit: cm³/m³
- Family: 3D tissue composition
- Source metrics file: tissue/metrics_original.json
- Model / task: TotalSegmentator `tissue_4_types` on the full native CT
- Detection / computation method: Volume in cm³ divided by patient height cubed in m³.
- Appears when: When `--with-tissue` succeeded. In addition, `--height-cm` must be provided to populate the height-normalized value.
- Interpretation / notes: Fat compartment around and between muscle groups. Measured on the full non-cropped scan.

#### `tissue_original_tissues_intermuscular_fat_volume_mm3`

- Clinical label: intermuscular fat (volume)
- Unit: mm³
- Family: 3D tissue composition
- Source metrics file: tissue/metrics_original.json
- Model / task: TotalSegmentator `tissue_4_types` on the full native CT
- Detection / computation method: Volume read from the corresponding `statistics.json` file emitted by TotalSegmentator.
- Appears when: When `--with-tissue` succeeded.
- Interpretation / notes: Fat compartment around and between muscle groups. Measured on the full non-cropped scan.

#### `tissue_original_tissues_intermuscular_fat_voxel_count`

- Clinical label: intermuscular fat (voxel count)
- Unit: value
- Family: 3D tissue composition
- Source metrics file: tissue/metrics_original.json
- Model / task: TotalSegmentator `tissue_4_types` on the full native CT
- Detection / computation method: Number of voxels of this tissue class in the full native CT volume.
- Appears when: When `--with-tissue` succeeded.
- Interpretation / notes: Fat compartment around and between muscle groups. Measured on the full non-cropped scan.

#### `tissue_original_tissues_skeletal_muscle_label_id`

- Clinical label: skeletal muscle (label id)
- Unit: value
- Family: 3D tissue composition
- Source metrics file: tissue/metrics_original.json
- Model / task: TotalSegmentator `tissue_4_types` on the full native CT
- Detection / computation method: Numeric label identifier from the `tissue_4_types` label map.
- Appears when: When `--with-tissue` succeeded.
- Interpretation / notes: 3D tissue-model muscle compartment, distinct from the dedicated `abdominal_muscles` task. Measured on the full non-cropped scan.

#### `tissue_original_tissues_skeletal_muscle_mean_hu`

- Clinical label: skeletal muscle (mean density)
- Unit: value
- Family: 3D tissue composition
- Source metrics file: tissue/metrics_original.json
- Model / task: TotalSegmentator `tissue_4_types` on the full native CT
- Detection / computation method: Mean Hounsfield units copied from the TotalSegmentator tissue statistics payload.
- Appears when: When `--with-tissue` succeeded.
- Interpretation / notes: 3D tissue-model muscle compartment, distinct from the dedicated `abdominal_muscles` task. Measured on the full non-cropped scan.

#### `tissue_original_tissues_skeletal_muscle_volume_cm3`

- Clinical label: skeletal muscle (volume)
- Unit: cm³
- Family: 3D tissue composition
- Source metrics file: tissue/metrics_original.json
- Model / task: TotalSegmentator `tissue_4_types` on the full native CT
- Detection / computation method: Volume converted from mm³ to cm³.
- Appears when: When `--with-tissue` succeeded.
- Interpretation / notes: 3D tissue-model muscle compartment, distinct from the dedicated `abdominal_muscles` task. Measured on the full non-cropped scan.

#### `tissue_original_tissues_skeletal_muscle_volume_cm3_per_m3`

- Clinical label: skeletal muscle (height-normalized volume)
- Unit: cm³/m³
- Family: 3D tissue composition
- Source metrics file: tissue/metrics_original.json
- Model / task: TotalSegmentator `tissue_4_types` on the full native CT
- Detection / computation method: Volume in cm³ divided by patient height cubed in m³.
- Appears when: When `--with-tissue` succeeded. In addition, `--height-cm` must be provided to populate the height-normalized value.
- Interpretation / notes: 3D tissue-model muscle compartment, distinct from the dedicated `abdominal_muscles` task. Measured on the full non-cropped scan.

#### `tissue_original_tissues_skeletal_muscle_volume_mm3`

- Clinical label: skeletal muscle (volume)
- Unit: mm³
- Family: 3D tissue composition
- Source metrics file: tissue/metrics_original.json
- Model / task: TotalSegmentator `tissue_4_types` on the full native CT
- Detection / computation method: Volume read from the corresponding `statistics.json` file emitted by TotalSegmentator.
- Appears when: When `--with-tissue` succeeded.
- Interpretation / notes: 3D tissue-model muscle compartment, distinct from the dedicated `abdominal_muscles` task. Measured on the full non-cropped scan.

#### `tissue_original_tissues_skeletal_muscle_voxel_count`

- Clinical label: skeletal muscle (voxel count)
- Unit: value
- Family: 3D tissue composition
- Source metrics file: tissue/metrics_original.json
- Model / task: TotalSegmentator `tissue_4_types` on the full native CT
- Detection / computation method: Number of voxels of this tissue class in the full native CT volume.
- Appears when: When `--with-tissue` succeeded.
- Interpretation / notes: 3D tissue-model muscle compartment, distinct from the dedicated `abdominal_muscles` task. Measured on the full non-cropped scan.

#### `tissue_original_tissues_subcutaneous_fat_label_id`

- Clinical label: subcutaneous fat (label id)
- Unit: value
- Family: 3D tissue composition
- Source metrics file: tissue/metrics_original.json
- Model / task: TotalSegmentator `tissue_4_types` on the full native CT
- Detection / computation method: Numeric label identifier from the `tissue_4_types` label map.
- Appears when: When `--with-tissue` succeeded.
- Interpretation / notes: Represents peripheral adiposity. Measured on the full non-cropped scan.

#### `tissue_original_tissues_subcutaneous_fat_mean_hu`

- Clinical label: subcutaneous fat (mean density)
- Unit: value
- Family: 3D tissue composition
- Source metrics file: tissue/metrics_original.json
- Model / task: TotalSegmentator `tissue_4_types` on the full native CT
- Detection / computation method: Mean Hounsfield units copied from the TotalSegmentator tissue statistics payload.
- Appears when: When `--with-tissue` succeeded.
- Interpretation / notes: Represents peripheral adiposity. Measured on the full non-cropped scan.

#### `tissue_original_tissues_subcutaneous_fat_volume_cm3`

- Clinical label: subcutaneous fat (volume)
- Unit: cm³
- Family: 3D tissue composition
- Source metrics file: tissue/metrics_original.json
- Model / task: TotalSegmentator `tissue_4_types` on the full native CT
- Detection / computation method: Volume converted from mm³ to cm³.
- Appears when: When `--with-tissue` succeeded.
- Interpretation / notes: Represents peripheral adiposity. Measured on the full non-cropped scan.

#### `tissue_original_tissues_subcutaneous_fat_volume_cm3_per_m3`

- Clinical label: subcutaneous fat (height-normalized volume)
- Unit: cm³/m³
- Family: 3D tissue composition
- Source metrics file: tissue/metrics_original.json
- Model / task: TotalSegmentator `tissue_4_types` on the full native CT
- Detection / computation method: Volume in cm³ divided by patient height cubed in m³.
- Appears when: When `--with-tissue` succeeded. In addition, `--height-cm` must be provided to populate the height-normalized value.
- Interpretation / notes: Represents peripheral adiposity. Measured on the full non-cropped scan.

#### `tissue_original_tissues_subcutaneous_fat_volume_mm3`

- Clinical label: subcutaneous fat (volume)
- Unit: mm³
- Family: 3D tissue composition
- Source metrics file: tissue/metrics_original.json
- Model / task: TotalSegmentator `tissue_4_types` on the full native CT
- Detection / computation method: Volume read from the corresponding `statistics.json` file emitted by TotalSegmentator.
- Appears when: When `--with-tissue` succeeded.
- Interpretation / notes: Represents peripheral adiposity. Measured on the full non-cropped scan.

#### `tissue_original_tissues_subcutaneous_fat_voxel_count`

- Clinical label: subcutaneous fat (voxel count)
- Unit: value
- Family: 3D tissue composition
- Source metrics file: tissue/metrics_original.json
- Model / task: TotalSegmentator `tissue_4_types` on the full native CT
- Detection / computation method: Number of voxels of this tissue class in the full native CT volume.
- Appears when: When `--with-tissue` succeeded.
- Interpretation / notes: Represents peripheral adiposity. Measured on the full non-cropped scan.

#### `tissue_original_tissues_torso_fat_label_id`

- Clinical label: torso fat (label id)
- Unit: value
- Family: 3D tissue composition
- Source metrics file: tissue/metrics_original.json
- Model / task: TotalSegmentator `tissue_4_types` on the full native CT
- Detection / computation method: Numeric label identifier from the `tissue_4_types` label map.
- Appears when: When `--with-tissue` succeeded.
- Interpretation / notes: Internal trunk adipose compartment; also used as the VAT approximation at L3 in ODIASP enrichment. Measured on the full non-cropped scan.

#### `tissue_original_tissues_torso_fat_mean_hu`

- Clinical label: torso fat (mean density)
- Unit: value
- Family: 3D tissue composition
- Source metrics file: tissue/metrics_original.json
- Model / task: TotalSegmentator `tissue_4_types` on the full native CT
- Detection / computation method: Mean Hounsfield units copied from the TotalSegmentator tissue statistics payload.
- Appears when: When `--with-tissue` succeeded.
- Interpretation / notes: Internal trunk adipose compartment; also used as the VAT approximation at L3 in ODIASP enrichment. Measured on the full non-cropped scan.

#### `tissue_original_tissues_torso_fat_volume_cm3`

- Clinical label: torso fat (volume)
- Unit: cm³
- Family: 3D tissue composition
- Source metrics file: tissue/metrics_original.json
- Model / task: TotalSegmentator `tissue_4_types` on the full native CT
- Detection / computation method: Volume converted from mm³ to cm³.
- Appears when: When `--with-tissue` succeeded.
- Interpretation / notes: Internal trunk adipose compartment; also used as the VAT approximation at L3 in ODIASP enrichment. Measured on the full non-cropped scan.

#### `tissue_original_tissues_torso_fat_volume_cm3_per_m3`

- Clinical label: torso fat (height-normalized volume)
- Unit: cm³/m³
- Family: 3D tissue composition
- Source metrics file: tissue/metrics_original.json
- Model / task: TotalSegmentator `tissue_4_types` on the full native CT
- Detection / computation method: Volume in cm³ divided by patient height cubed in m³.
- Appears when: When `--with-tissue` succeeded. In addition, `--height-cm` must be provided to populate the height-normalized value.
- Interpretation / notes: Internal trunk adipose compartment; also used as the VAT approximation at L3 in ODIASP enrichment. Measured on the full non-cropped scan.

#### `tissue_original_tissues_torso_fat_volume_mm3`

- Clinical label: torso fat (volume)
- Unit: mm³
- Family: 3D tissue composition
- Source metrics file: tissue/metrics_original.json
- Model / task: TotalSegmentator `tissue_4_types` on the full native CT
- Detection / computation method: Volume read from the corresponding `statistics.json` file emitted by TotalSegmentator.
- Appears when: When `--with-tissue` succeeded.
- Interpretation / notes: Internal trunk adipose compartment; also used as the VAT approximation at L3 in ODIASP enrichment. Measured on the full non-cropped scan.

#### `tissue_original_tissues_torso_fat_voxel_count`

- Clinical label: torso fat (voxel count)
- Unit: value
- Family: 3D tissue composition
- Source metrics file: tissue/metrics_original.json
- Model / task: TotalSegmentator `tissue_4_types` on the full native CT
- Detection / computation method: Number of voxels of this tissue class in the full native CT volume.
- Appears when: When `--with-tissue` succeeded.
- Interpretation / notes: Internal trunk adipose compartment; also used as the VAT approximation at L3 in ODIASP enrichment. Measured on the full non-cropped scan.

#### `tissue_original_variant`

- Clinical label: Tissue variant
- Unit: text
- Family: Tissue Original
- Source metrics file: tissue/metrics_original.json
- Model / task: TotalSegmentator `tissue_4_types` on the full native CT
- Detection / computation method: Variant metadata field.
- Appears when: When `--with-tissue` succeeded.
- Interpretation / notes: Distinguishes `original` from `T4_L4`.

#### `tissue_original_voxel_spacing_mm_x`

- Clinical label: Voxel spacing x
- Unit: mm
- Family: Tissue Original
- Source metrics file: tissue/metrics_original.json
- Model / task: TotalSegmentator `tissue_4_types` on the full native CT
- Detection / computation method: Native voxel spacing x from the NIfTI header.
- Appears when: When `--with-tissue` succeeded.
- Interpretation / notes: Technical geometry field.

#### `tissue_original_voxel_spacing_mm_y`

- Clinical label: Voxel spacing y
- Unit: mm
- Family: Tissue Original
- Source metrics file: tissue/metrics_original.json
- Model / task: TotalSegmentator `tissue_4_types` on the full native CT
- Detection / computation method: Native voxel spacing y from the NIfTI header.
- Appears when: When `--with-tissue` succeeded.
- Interpretation / notes: Technical geometry field.

#### `tissue_original_voxel_spacing_mm_z`

- Clinical label: Voxel spacing z
- Unit: mm
- Family: Tissue Original
- Source metrics file: tissue/metrics_original.json
- Model / task: TotalSegmentator `tissue_4_types` on the full native CT
- Detection / computation method: Native voxel spacing z from the NIfTI header.
- Appears when: When `--with-tissue` succeeded.
- Interpretation / notes: Technical geometry field.

#### `tissue_original_warnings`

- Clinical label: Tissue warnings
- Unit: text
- Family: Tissue Original
- Source metrics file: tissue/metrics_original.json
- Model / task: TotalSegmentator `tissue_4_types` on the full native CT
- Detection / computation method: Warnings emitted during tissue metric extraction.
- Appears when: When `--with-tissue` succeeded.
- Interpretation / notes: Includes boundary-touch and missing-height warnings.

#### `tissue_original_z_max`

- Clinical label: Superior tissue z boundary
- Unit: index
- Family: Tissue Original
- Source metrics file: tissue/metrics_original.json
- Model / task: TotalSegmentator `tissue_4_types` on the full native CT
- Detection / computation method: Last z slice included in the tissue volume.
- Appears when: When `--with-tissue` succeeded.
- Interpretation / notes: For `T4_L4`, this comes from the last occupied `abdominal_muscles` slice.

#### `tissue_original_z_min`

- Clinical label: Inferior tissue z boundary
- Unit: index
- Family: Tissue Original
- Source metrics file: tissue/metrics_original.json
- Model / task: TotalSegmentator `tissue_4_types` on the full native CT
- Detection / computation method: First z slice included in the tissue volume.
- Appears when: When `--with-tissue` succeeded.
- Interpretation / notes: For `T4_L4`, this comes from the first occupied `abdominal_muscles` slice.

### Tissue T4 L4

#### `tissue_T4_L4_status`

- Clinical label: Tissue T4 L4 status
- Unit: categorical status
- Family: Pipeline diagnostics
- Source metrics file: CSV row metadata or branch status/metrics files
- Model / task: Not applicable
- Detection / computation method: Status exported by the CSV writer for `status`. Values are typically `success`, `failed`, or `not_requested`.
- Appears when: Always present for the corresponding branch status field.
- Interpretation / notes: Status of the `Tissue T4 L4` metrics branch.

#### `tissue_T4_L4_crop_strategy`

- Clinical label: Tissue crop strategy
- Unit: text
- Family: Tissue T4 L4
- Source metrics file: tissue/metrics_T4_L4.json
- Model / task: TotalSegmentator `tissue_4_types` on the abdominal_muscles-derived T4-L4 z-slab
- Detection / computation method: Literal crop strategy field from the tissue metrics JSON.
- Appears when: When `--with-tissue` succeeded.
- Interpretation / notes: Documents whether no z-crop was used or whether the abdominal_muscles-derived z-slab was applied.

#### `tissue_T4_L4_cropped_shape_x`

- Clinical label: Cropped shape x
- Unit: voxels
- Family: Tissue T4 L4
- Source metrics file: tissue/metrics_T4_L4.json
- Model / task: TotalSegmentator `tissue_4_types` on the abdominal_muscles-derived T4-L4 z-slab
- Detection / computation method: Width of the effective processing volume in voxels.
- Appears when: When `--with-tissue` succeeded.
- Interpretation / notes: Technical geometry field.

#### `tissue_T4_L4_cropped_shape_y`

- Clinical label: Cropped shape y
- Unit: voxels
- Family: Tissue T4 L4
- Source metrics file: tissue/metrics_T4_L4.json
- Model / task: TotalSegmentator `tissue_4_types` on the abdominal_muscles-derived T4-L4 z-slab
- Detection / computation method: Height of the effective processing volume in voxels.
- Appears when: When `--with-tissue` succeeded.
- Interpretation / notes: Technical geometry field.

#### `tissue_T4_L4_cropped_shape_z`

- Clinical label: Cropped shape z
- Unit: voxels
- Family: Tissue T4 L4
- Source metrics file: tissue/metrics_T4_L4.json
- Model / task: TotalSegmentator `tissue_4_types` on the abdominal_muscles-derived T4-L4 z-slab
- Detection / computation method: Depth of the effective processing volume in voxels.
- Appears when: When `--with-tissue` succeeded.
- Interpretation / notes: Technical geometry field.

#### `tissue_T4_L4_height_cm`

- Clinical label: Patient height
- Unit: cm
- Family: Tissue T4 L4
- Source metrics file: tissue/metrics_T4_L4.json
- Model / task: TotalSegmentator `tissue_4_types` on the abdominal_muscles-derived T4-L4 z-slab
- Detection / computation method: Height passed with `--height-cm`.
- Appears when: When `--with-tissue` succeeded.
- Interpretation / notes: Required for height-normalized tissue volumes.

#### `tissue_T4_L4_height_m`

- Clinical label: Patient height in metres
- Unit: m
- Family: Tissue T4 L4
- Source metrics file: tissue/metrics_T4_L4.json
- Model / task: TotalSegmentator `tissue_4_types` on the abdominal_muscles-derived T4-L4 z-slab
- Detection / computation method: Height converted from centimetres to metres.
- Appears when: When `--with-tissue` succeeded.
- Interpretation / notes: Intermediate normalization value.

#### `tissue_T4_L4_input_shape_x`

- Clinical label: Input shape x
- Unit: voxels
- Family: Tissue T4 L4
- Source metrics file: tissue/metrics_T4_L4.json
- Model / task: TotalSegmentator `tissue_4_types` on the abdominal_muscles-derived T4-L4 z-slab
- Detection / computation method: Native image width in voxels.
- Appears when: When `--with-tissue` succeeded.
- Interpretation / notes: Technical geometry field.

#### `tissue_T4_L4_input_shape_y`

- Clinical label: Input shape y
- Unit: voxels
- Family: Tissue T4 L4
- Source metrics file: tissue/metrics_T4_L4.json
- Model / task: TotalSegmentator `tissue_4_types` on the abdominal_muscles-derived T4-L4 z-slab
- Detection / computation method: Native image height in voxels.
- Appears when: When `--with-tissue` succeeded.
- Interpretation / notes: Technical geometry field.

#### `tissue_T4_L4_input_shape_z`

- Clinical label: Input shape z
- Unit: voxels
- Family: Tissue T4 L4
- Source metrics file: tissue/metrics_T4_L4.json
- Model / task: TotalSegmentator `tissue_4_types` on the abdominal_muscles-derived T4-L4 z-slab
- Detection / computation method: Native image depth in voxels.
- Appears when: When `--with-tissue` succeeded.
- Interpretation / notes: Technical geometry field.

#### `tissue_T4_L4_method`

- Clinical label: Tissue branch method
- Unit: text
- Family: Tissue T4 L4
- Source metrics file: tissue/metrics_T4_L4.json
- Model / task: TotalSegmentator `tissue_4_types` on the abdominal_muscles-derived T4-L4 z-slab
- Detection / computation method: Method string stored in the tissue metrics JSON.
- Appears when: When `--with-tissue` succeeded.
- Interpretation / notes: Describes whether the run used the full scan or the abdominal_muscles z-slab.

#### `tissue_T4_L4_preview_axial`

- Clinical label: Axial preview filename
- Unit: text
- Family: Tissue T4 L4
- Source metrics file: tissue/metrics_T4_L4.json
- Model / task: TotalSegmentator `tissue_4_types` on the abdominal_muscles-derived T4-L4 z-slab
- Detection / computation method: QC preview PNG filename.
- Appears when: When `--with-tissue` succeeded.
- Interpretation / notes: Technical QA field.

#### `tissue_T4_L4_preview_axial_z_index_ras`

- Clinical label: Axial preview z index
- Unit: index
- Family: Tissue T4 L4
- Source metrics file: tissue/metrics_T4_L4.json
- Model / task: TotalSegmentator `tissue_4_types` on the abdominal_muscles-derived T4-L4 z-slab
- Detection / computation method: RAS z index used for the axial preview.
- Appears when: When `--with-tissue` succeeded.
- Interpretation / notes: Technical QA field.

#### `tissue_T4_L4_preview_sagittal`

- Clinical label: Sagittal preview filename
- Unit: text
- Family: Tissue T4 L4
- Source metrics file: tissue/metrics_T4_L4.json
- Model / task: TotalSegmentator `tissue_4_types` on the abdominal_muscles-derived T4-L4 z-slab
- Detection / computation method: QC preview PNG filename.
- Appears when: When `--with-tissue` succeeded.
- Interpretation / notes: Technical QA field.

#### `tissue_T4_L4_preview_sagittal_x_index_ras`

- Clinical label: Sagittal preview x index
- Unit: index
- Family: Tissue T4 L4
- Source metrics file: tissue/metrics_T4_L4.json
- Model / task: TotalSegmentator `tissue_4_types` on the abdominal_muscles-derived T4-L4 z-slab
- Detection / computation method: RAS x index used for the sagittal preview.
- Appears when: When `--with-tissue` succeeded.
- Interpretation / notes: Technical QA field.

#### `tissue_T4_L4_segmentation_name`

- Clinical label: Tissue segmentation name
- Unit: text
- Family: Tissue T4 L4
- Source metrics file: tissue/metrics_T4_L4.json
- Model / task: TotalSegmentator `tissue_4_types` on the abdominal_muscles-derived T4-L4 z-slab
- Detection / computation method: Segmentation metadata field.
- Appears when: When `--with-tissue` succeeded.
- Interpretation / notes: Human-readable name used for Slicer import.

#### `tissue_T4_L4_slice_count`

- Clinical label: Number of z slices in the tissue volume
- Unit: count
- Family: Tissue T4 L4
- Source metrics file: tissue/metrics_T4_L4.json
- Model / task: TotalSegmentator `tissue_4_types` on the abdominal_muscles-derived T4-L4 z-slab
- Detection / computation method: Number of z slices between `z_min` and `z_max`, inclusive.
- Appears when: When `--with-tissue` succeeded.
- Interpretation / notes: Volume extent metadata.

#### `tissue_T4_L4_source_task`

- Clinical label: Tissue source task
- Unit: text
- Family: Tissue T4 L4
- Source metrics file: tissue/metrics_T4_L4.json
- Model / task: TotalSegmentator `tissue_4_types` on the abdominal_muscles-derived T4-L4 z-slab
- Detection / computation method: Source task metadata field.
- Appears when: When `--with-tissue` succeeded.
- Interpretation / notes: Technical provenance field.

#### `tissue_T4_L4_task`

- Clinical label: Tissue task name
- Unit: text
- Family: Tissue T4 L4
- Source metrics file: tissue/metrics_T4_L4.json
- Model / task: TotalSegmentator `tissue_4_types` on the abdominal_muscles-derived T4-L4 z-slab
- Detection / computation method: Task metadata field.
- Appears when: When `--with-tissue` succeeded.
- Interpretation / notes: Technical provenance field.

#### `tissue_T4_L4_tissues_intermuscular_fat_label_id`

- Clinical label: intermuscular fat (label id)
- Unit: value
- Family: 3D tissue composition
- Source metrics file: tissue/metrics_T4_L4.json
- Model / task: TotalSegmentator `tissue_4_types` on the abdominal_muscles-derived T4-L4 z-slab
- Detection / computation method: Numeric label identifier from the `tissue_4_types` label map.
- Appears when: When `--with-tissue` succeeded.
- Interpretation / notes: Fat compartment around and between muscle groups. Measured on the reproducible z-slab defined by the abdominal_muscles superior and inferior limits.

#### `tissue_T4_L4_tissues_intermuscular_fat_mean_hu`

- Clinical label: intermuscular fat (mean density)
- Unit: value
- Family: 3D tissue composition
- Source metrics file: tissue/metrics_T4_L4.json
- Model / task: TotalSegmentator `tissue_4_types` on the abdominal_muscles-derived T4-L4 z-slab
- Detection / computation method: Mean Hounsfield units copied from the TotalSegmentator tissue statistics payload.
- Appears when: When `--with-tissue` succeeded.
- Interpretation / notes: Fat compartment around and between muscle groups. Measured on the reproducible z-slab defined by the abdominal_muscles superior and inferior limits.

#### `tissue_T4_L4_tissues_intermuscular_fat_volume_cm3`

- Clinical label: intermuscular fat (volume)
- Unit: cm³
- Family: 3D tissue composition
- Source metrics file: tissue/metrics_T4_L4.json
- Model / task: TotalSegmentator `tissue_4_types` on the abdominal_muscles-derived T4-L4 z-slab
- Detection / computation method: Volume converted from mm³ to cm³.
- Appears when: When `--with-tissue` succeeded.
- Interpretation / notes: Fat compartment around and between muscle groups. Measured on the reproducible z-slab defined by the abdominal_muscles superior and inferior limits.

#### `tissue_T4_L4_tissues_intermuscular_fat_volume_cm3_per_m3`

- Clinical label: intermuscular fat (height-normalized volume)
- Unit: cm³/m³
- Family: 3D tissue composition
- Source metrics file: tissue/metrics_T4_L4.json
- Model / task: TotalSegmentator `tissue_4_types` on the abdominal_muscles-derived T4-L4 z-slab
- Detection / computation method: Volume in cm³ divided by patient height cubed in m³.
- Appears when: When `--with-tissue` succeeded. In addition, `--height-cm` must be provided to populate the height-normalized value.
- Interpretation / notes: Fat compartment around and between muscle groups. Measured on the reproducible z-slab defined by the abdominal_muscles superior and inferior limits.

#### `tissue_T4_L4_tissues_intermuscular_fat_volume_mm3`

- Clinical label: intermuscular fat (volume)
- Unit: mm³
- Family: 3D tissue composition
- Source metrics file: tissue/metrics_T4_L4.json
- Model / task: TotalSegmentator `tissue_4_types` on the abdominal_muscles-derived T4-L4 z-slab
- Detection / computation method: Volume read from the corresponding `statistics.json` file emitted by TotalSegmentator.
- Appears when: When `--with-tissue` succeeded.
- Interpretation / notes: Fat compartment around and between muscle groups. Measured on the reproducible z-slab defined by the abdominal_muscles superior and inferior limits.

#### `tissue_T4_L4_tissues_intermuscular_fat_voxel_count`

- Clinical label: intermuscular fat (voxel count)
- Unit: value
- Family: 3D tissue composition
- Source metrics file: tissue/metrics_T4_L4.json
- Model / task: TotalSegmentator `tissue_4_types` on the abdominal_muscles-derived T4-L4 z-slab
- Detection / computation method: Number of voxels of this tissue class in the abdominal_muscles-derived T4-L4 z-slab.
- Appears when: When `--with-tissue` succeeded.
- Interpretation / notes: Fat compartment around and between muscle groups. Measured on the reproducible z-slab defined by the abdominal_muscles superior and inferior limits.

#### `tissue_T4_L4_tissues_skeletal_muscle_label_id`

- Clinical label: skeletal muscle (label id)
- Unit: value
- Family: 3D tissue composition
- Source metrics file: tissue/metrics_T4_L4.json
- Model / task: TotalSegmentator `tissue_4_types` on the abdominal_muscles-derived T4-L4 z-slab
- Detection / computation method: Numeric label identifier from the `tissue_4_types` label map.
- Appears when: When `--with-tissue` succeeded.
- Interpretation / notes: 3D tissue-model muscle compartment, distinct from the dedicated `abdominal_muscles` task. Measured on the reproducible z-slab defined by the abdominal_muscles superior and inferior limits.

#### `tissue_T4_L4_tissues_skeletal_muscle_mean_hu`

- Clinical label: skeletal muscle (mean density)
- Unit: value
- Family: 3D tissue composition
- Source metrics file: tissue/metrics_T4_L4.json
- Model / task: TotalSegmentator `tissue_4_types` on the abdominal_muscles-derived T4-L4 z-slab
- Detection / computation method: Mean Hounsfield units copied from the TotalSegmentator tissue statistics payload.
- Appears when: When `--with-tissue` succeeded.
- Interpretation / notes: 3D tissue-model muscle compartment, distinct from the dedicated `abdominal_muscles` task. Measured on the reproducible z-slab defined by the abdominal_muscles superior and inferior limits.

#### `tissue_T4_L4_tissues_skeletal_muscle_volume_cm3`

- Clinical label: skeletal muscle (volume)
- Unit: cm³
- Family: 3D tissue composition
- Source metrics file: tissue/metrics_T4_L4.json
- Model / task: TotalSegmentator `tissue_4_types` on the abdominal_muscles-derived T4-L4 z-slab
- Detection / computation method: Volume converted from mm³ to cm³.
- Appears when: When `--with-tissue` succeeded.
- Interpretation / notes: 3D tissue-model muscle compartment, distinct from the dedicated `abdominal_muscles` task. Measured on the reproducible z-slab defined by the abdominal_muscles superior and inferior limits.

#### `tissue_T4_L4_tissues_skeletal_muscle_volume_cm3_per_m3`

- Clinical label: skeletal muscle (height-normalized volume)
- Unit: cm³/m³
- Family: 3D tissue composition
- Source metrics file: tissue/metrics_T4_L4.json
- Model / task: TotalSegmentator `tissue_4_types` on the abdominal_muscles-derived T4-L4 z-slab
- Detection / computation method: Volume in cm³ divided by patient height cubed in m³.
- Appears when: When `--with-tissue` succeeded. In addition, `--height-cm` must be provided to populate the height-normalized value.
- Interpretation / notes: 3D tissue-model muscle compartment, distinct from the dedicated `abdominal_muscles` task. Measured on the reproducible z-slab defined by the abdominal_muscles superior and inferior limits.

#### `tissue_T4_L4_tissues_skeletal_muscle_volume_mm3`

- Clinical label: skeletal muscle (volume)
- Unit: mm³
- Family: 3D tissue composition
- Source metrics file: tissue/metrics_T4_L4.json
- Model / task: TotalSegmentator `tissue_4_types` on the abdominal_muscles-derived T4-L4 z-slab
- Detection / computation method: Volume read from the corresponding `statistics.json` file emitted by TotalSegmentator.
- Appears when: When `--with-tissue` succeeded.
- Interpretation / notes: 3D tissue-model muscle compartment, distinct from the dedicated `abdominal_muscles` task. Measured on the reproducible z-slab defined by the abdominal_muscles superior and inferior limits.

#### `tissue_T4_L4_tissues_skeletal_muscle_voxel_count`

- Clinical label: skeletal muscle (voxel count)
- Unit: value
- Family: 3D tissue composition
- Source metrics file: tissue/metrics_T4_L4.json
- Model / task: TotalSegmentator `tissue_4_types` on the abdominal_muscles-derived T4-L4 z-slab
- Detection / computation method: Number of voxels of this tissue class in the abdominal_muscles-derived T4-L4 z-slab.
- Appears when: When `--with-tissue` succeeded.
- Interpretation / notes: 3D tissue-model muscle compartment, distinct from the dedicated `abdominal_muscles` task. Measured on the reproducible z-slab defined by the abdominal_muscles superior and inferior limits.

#### `tissue_T4_L4_tissues_subcutaneous_fat_label_id`

- Clinical label: subcutaneous fat (label id)
- Unit: value
- Family: 3D tissue composition
- Source metrics file: tissue/metrics_T4_L4.json
- Model / task: TotalSegmentator `tissue_4_types` on the abdominal_muscles-derived T4-L4 z-slab
- Detection / computation method: Numeric label identifier from the `tissue_4_types` label map.
- Appears when: When `--with-tissue` succeeded.
- Interpretation / notes: Represents peripheral adiposity. Measured on the reproducible z-slab defined by the abdominal_muscles superior and inferior limits.

#### `tissue_T4_L4_tissues_subcutaneous_fat_mean_hu`

- Clinical label: subcutaneous fat (mean density)
- Unit: value
- Family: 3D tissue composition
- Source metrics file: tissue/metrics_T4_L4.json
- Model / task: TotalSegmentator `tissue_4_types` on the abdominal_muscles-derived T4-L4 z-slab
- Detection / computation method: Mean Hounsfield units copied from the TotalSegmentator tissue statistics payload.
- Appears when: When `--with-tissue` succeeded.
- Interpretation / notes: Represents peripheral adiposity. Measured on the reproducible z-slab defined by the abdominal_muscles superior and inferior limits.

#### `tissue_T4_L4_tissues_subcutaneous_fat_volume_cm3`

- Clinical label: subcutaneous fat (volume)
- Unit: cm³
- Family: 3D tissue composition
- Source metrics file: tissue/metrics_T4_L4.json
- Model / task: TotalSegmentator `tissue_4_types` on the abdominal_muscles-derived T4-L4 z-slab
- Detection / computation method: Volume converted from mm³ to cm³.
- Appears when: When `--with-tissue` succeeded.
- Interpretation / notes: Represents peripheral adiposity. Measured on the reproducible z-slab defined by the abdominal_muscles superior and inferior limits.

#### `tissue_T4_L4_tissues_subcutaneous_fat_volume_cm3_per_m3`

- Clinical label: subcutaneous fat (height-normalized volume)
- Unit: cm³/m³
- Family: 3D tissue composition
- Source metrics file: tissue/metrics_T4_L4.json
- Model / task: TotalSegmentator `tissue_4_types` on the abdominal_muscles-derived T4-L4 z-slab
- Detection / computation method: Volume in cm³ divided by patient height cubed in m³.
- Appears when: When `--with-tissue` succeeded. In addition, `--height-cm` must be provided to populate the height-normalized value.
- Interpretation / notes: Represents peripheral adiposity. Measured on the reproducible z-slab defined by the abdominal_muscles superior and inferior limits.

#### `tissue_T4_L4_tissues_subcutaneous_fat_volume_mm3`

- Clinical label: subcutaneous fat (volume)
- Unit: mm³
- Family: 3D tissue composition
- Source metrics file: tissue/metrics_T4_L4.json
- Model / task: TotalSegmentator `tissue_4_types` on the abdominal_muscles-derived T4-L4 z-slab
- Detection / computation method: Volume read from the corresponding `statistics.json` file emitted by TotalSegmentator.
- Appears when: When `--with-tissue` succeeded.
- Interpretation / notes: Represents peripheral adiposity. Measured on the reproducible z-slab defined by the abdominal_muscles superior and inferior limits.

#### `tissue_T4_L4_tissues_subcutaneous_fat_voxel_count`

- Clinical label: subcutaneous fat (voxel count)
- Unit: value
- Family: 3D tissue composition
- Source metrics file: tissue/metrics_T4_L4.json
- Model / task: TotalSegmentator `tissue_4_types` on the abdominal_muscles-derived T4-L4 z-slab
- Detection / computation method: Number of voxels of this tissue class in the abdominal_muscles-derived T4-L4 z-slab.
- Appears when: When `--with-tissue` succeeded.
- Interpretation / notes: Represents peripheral adiposity. Measured on the reproducible z-slab defined by the abdominal_muscles superior and inferior limits.

#### `tissue_T4_L4_tissues_torso_fat_label_id`

- Clinical label: torso fat (label id)
- Unit: value
- Family: 3D tissue composition
- Source metrics file: tissue/metrics_T4_L4.json
- Model / task: TotalSegmentator `tissue_4_types` on the abdominal_muscles-derived T4-L4 z-slab
- Detection / computation method: Numeric label identifier from the `tissue_4_types` label map.
- Appears when: When `--with-tissue` succeeded.
- Interpretation / notes: Internal trunk adipose compartment; also used as the VAT approximation at L3 in ODIASP enrichment. Measured on the reproducible z-slab defined by the abdominal_muscles superior and inferior limits.

#### `tissue_T4_L4_tissues_torso_fat_mean_hu`

- Clinical label: torso fat (mean density)
- Unit: value
- Family: 3D tissue composition
- Source metrics file: tissue/metrics_T4_L4.json
- Model / task: TotalSegmentator `tissue_4_types` on the abdominal_muscles-derived T4-L4 z-slab
- Detection / computation method: Mean Hounsfield units copied from the TotalSegmentator tissue statistics payload.
- Appears when: When `--with-tissue` succeeded.
- Interpretation / notes: Internal trunk adipose compartment; also used as the VAT approximation at L3 in ODIASP enrichment. Measured on the reproducible z-slab defined by the abdominal_muscles superior and inferior limits.

#### `tissue_T4_L4_tissues_torso_fat_volume_cm3`

- Clinical label: torso fat (volume)
- Unit: cm³
- Family: 3D tissue composition
- Source metrics file: tissue/metrics_T4_L4.json
- Model / task: TotalSegmentator `tissue_4_types` on the abdominal_muscles-derived T4-L4 z-slab
- Detection / computation method: Volume converted from mm³ to cm³.
- Appears when: When `--with-tissue` succeeded.
- Interpretation / notes: Internal trunk adipose compartment; also used as the VAT approximation at L3 in ODIASP enrichment. Measured on the reproducible z-slab defined by the abdominal_muscles superior and inferior limits.

#### `tissue_T4_L4_tissues_torso_fat_volume_cm3_per_m3`

- Clinical label: torso fat (height-normalized volume)
- Unit: cm³/m³
- Family: 3D tissue composition
- Source metrics file: tissue/metrics_T4_L4.json
- Model / task: TotalSegmentator `tissue_4_types` on the abdominal_muscles-derived T4-L4 z-slab
- Detection / computation method: Volume in cm³ divided by patient height cubed in m³.
- Appears when: When `--with-tissue` succeeded. In addition, `--height-cm` must be provided to populate the height-normalized value.
- Interpretation / notes: Internal trunk adipose compartment; also used as the VAT approximation at L3 in ODIASP enrichment. Measured on the reproducible z-slab defined by the abdominal_muscles superior and inferior limits.

#### `tissue_T4_L4_tissues_torso_fat_volume_mm3`

- Clinical label: torso fat (volume)
- Unit: mm³
- Family: 3D tissue composition
- Source metrics file: tissue/metrics_T4_L4.json
- Model / task: TotalSegmentator `tissue_4_types` on the abdominal_muscles-derived T4-L4 z-slab
- Detection / computation method: Volume read from the corresponding `statistics.json` file emitted by TotalSegmentator.
- Appears when: When `--with-tissue` succeeded.
- Interpretation / notes: Internal trunk adipose compartment; also used as the VAT approximation at L3 in ODIASP enrichment. Measured on the reproducible z-slab defined by the abdominal_muscles superior and inferior limits.

#### `tissue_T4_L4_tissues_torso_fat_voxel_count`

- Clinical label: torso fat (voxel count)
- Unit: value
- Family: 3D tissue composition
- Source metrics file: tissue/metrics_T4_L4.json
- Model / task: TotalSegmentator `tissue_4_types` on the abdominal_muscles-derived T4-L4 z-slab
- Detection / computation method: Number of voxels of this tissue class in the abdominal_muscles-derived T4-L4 z-slab.
- Appears when: When `--with-tissue` succeeded.
- Interpretation / notes: Internal trunk adipose compartment; also used as the VAT approximation at L3 in ODIASP enrichment. Measured on the reproducible z-slab defined by the abdominal_muscles superior and inferior limits.

#### `tissue_T4_L4_variant`

- Clinical label: Tissue variant
- Unit: text
- Family: Tissue T4 L4
- Source metrics file: tissue/metrics_T4_L4.json
- Model / task: TotalSegmentator `tissue_4_types` on the abdominal_muscles-derived T4-L4 z-slab
- Detection / computation method: Variant metadata field.
- Appears when: When `--with-tissue` succeeded.
- Interpretation / notes: Distinguishes `original` from `T4_L4`.

#### `tissue_T4_L4_voxel_spacing_mm_x`

- Clinical label: Voxel spacing x
- Unit: mm
- Family: Tissue T4 L4
- Source metrics file: tissue/metrics_T4_L4.json
- Model / task: TotalSegmentator `tissue_4_types` on the abdominal_muscles-derived T4-L4 z-slab
- Detection / computation method: Native voxel spacing x from the NIfTI header.
- Appears when: When `--with-tissue` succeeded.
- Interpretation / notes: Technical geometry field.

#### `tissue_T4_L4_voxel_spacing_mm_y`

- Clinical label: Voxel spacing y
- Unit: mm
- Family: Tissue T4 L4
- Source metrics file: tissue/metrics_T4_L4.json
- Model / task: TotalSegmentator `tissue_4_types` on the abdominal_muscles-derived T4-L4 z-slab
- Detection / computation method: Native voxel spacing y from the NIfTI header.
- Appears when: When `--with-tissue` succeeded.
- Interpretation / notes: Technical geometry field.

#### `tissue_T4_L4_voxel_spacing_mm_z`

- Clinical label: Voxel spacing z
- Unit: mm
- Family: Tissue T4 L4
- Source metrics file: tissue/metrics_T4_L4.json
- Model / task: TotalSegmentator `tissue_4_types` on the abdominal_muscles-derived T4-L4 z-slab
- Detection / computation method: Native voxel spacing z from the NIfTI header.
- Appears when: When `--with-tissue` succeeded.
- Interpretation / notes: Technical geometry field.

#### `tissue_T4_L4_warnings`

- Clinical label: Tissue warnings
- Unit: text
- Family: Tissue T4 L4
- Source metrics file: tissue/metrics_T4_L4.json
- Model / task: TotalSegmentator `tissue_4_types` on the abdominal_muscles-derived T4-L4 z-slab
- Detection / computation method: Warnings emitted during tissue metric extraction.
- Appears when: When `--with-tissue` succeeded.
- Interpretation / notes: Includes boundary-touch and missing-height warnings.

#### `tissue_T4_L4_z_max`

- Clinical label: Superior tissue z boundary
- Unit: index
- Family: Tissue T4 L4
- Source metrics file: tissue/metrics_T4_L4.json
- Model / task: TotalSegmentator `tissue_4_types` on the abdominal_muscles-derived T4-L4 z-slab
- Detection / computation method: Last z slice included in the tissue volume.
- Appears when: When `--with-tissue` succeeded.
- Interpretation / notes: For `T4_L4`, this comes from the last occupied `abdominal_muscles` slice.

#### `tissue_T4_L4_z_min`

- Clinical label: Inferior tissue z boundary
- Unit: index
- Family: Tissue T4 L4
- Source metrics file: tissue/metrics_T4_L4.json
- Model / task: TotalSegmentator `tissue_4_types` on the abdominal_muscles-derived T4-L4 z-slab
- Detection / computation method: First z slice included in the tissue volume.
- Appears when: When `--with-tissue` succeeded.
- Interpretation / notes: For `T4_L4`, this comes from the first occupied `abdominal_muscles` slice.

### Total

#### `total_status`

- Clinical label: Total status
- Unit: categorical status
- Family: Pipeline diagnostics
- Source metrics file: CSV row metadata or branch status/metrics files
- Model / task: Not applicable
- Detection / computation method: Status exported by the CSV writer for `status`. Values are typically `success`, `failed`, or `not_requested`.
- Appears when: Always present for the corresponding branch status field.
- Interpretation / notes: Status of the `Total` metrics branch.

#### `total_height_cm`

- Clinical label: Patient height
- Unit: cm
- Family: Total
- Source metrics file: total/metrics.json
- Model / task: TotalSegmentator `total` on the full native CT
- Detection / computation method: Height passed with `--height-cm`.
- Appears when: When `--with-total` succeeded.
- Interpretation / notes: Required for height-normalized iliopsoas volumes.

#### `total_height_m`

- Clinical label: Patient height in metres
- Unit: m
- Family: Total
- Source metrics file: total/metrics.json
- Model / task: TotalSegmentator `total` on the full native CT
- Detection / computation method: Height converted from centimetres to metres.
- Appears when: When `--with-total` succeeded.
- Interpretation / notes: Intermediate normalization value.

#### `total_iliopsoas_left_label_id`

- Clinical label: Left iliopsoas volume (label id)
- Unit: value
- Family: Full-scan iliopsoas volumes
- Source metrics file: total/metrics.json
- Model / task: TotalSegmentator `total` on the full native CT
- Detection / computation method: Numeric label identifier from the `total` label map.
- Appears when: When `--with-total` succeeded.
- Interpretation / notes: This branch addresses the full visible iliopsoas volume on the entire scan, not only at L3.

#### `total_iliopsoas_left_volume_cm3`

- Clinical label: Left iliopsoas volume (volume)
- Unit: cm³
- Family: Full-scan iliopsoas volumes
- Source metrics file: total/metrics.json
- Model / task: TotalSegmentator `total` on the full native CT
- Detection / computation method: Volume converted from mm³ to cm³.
- Appears when: When `--with-total` succeeded.
- Interpretation / notes: This branch addresses the full visible iliopsoas volume on the entire scan, not only at L3.

#### `total_iliopsoas_left_volume_cm3_per_m3`

- Clinical label: Left iliopsoas volume (height-normalized volume)
- Unit: cm³/m³
- Family: Full-scan iliopsoas volumes
- Source metrics file: total/metrics.json
- Model / task: TotalSegmentator `total` on the full native CT
- Detection / computation method: Volume in cm³ divided by patient height cubed in m³.
- Appears when: When `--with-total` succeeded. In addition, `--height-cm` must be provided to populate the height-normalized value.
- Interpretation / notes: This branch addresses the full visible iliopsoas volume on the entire scan, not only at L3.

#### `total_iliopsoas_left_volume_mm3`

- Clinical label: Left iliopsoas volume (volume)
- Unit: mm³
- Family: Full-scan iliopsoas volumes
- Source metrics file: total/metrics.json
- Model / task: TotalSegmentator `total` on the full native CT
- Detection / computation method: Volume read from `total/statistics.json` for this iliopsoas label.
- Appears when: When `--with-total` succeeded.
- Interpretation / notes: This branch addresses the full visible iliopsoas volume on the entire scan, not only at L3.

#### `total_iliopsoas_left_voxel_count`

- Clinical label: Left iliopsoas volume (voxel count)
- Unit: value
- Family: Full-scan iliopsoas volumes
- Source metrics file: total/metrics.json
- Model / task: TotalSegmentator `total` on the full native CT
- Detection / computation method: Number of voxels equal to the iliopsoas label in `total_multilabel.nii.gz`.
- Appears when: When `--with-total` succeeded.
- Interpretation / notes: This branch addresses the full visible iliopsoas volume on the entire scan, not only at L3.

#### `total_iliopsoas_right_label_id`

- Clinical label: Right iliopsoas volume (label id)
- Unit: value
- Family: Full-scan iliopsoas volumes
- Source metrics file: total/metrics.json
- Model / task: TotalSegmentator `total` on the full native CT
- Detection / computation method: Numeric label identifier from the `total` label map.
- Appears when: When `--with-total` succeeded.
- Interpretation / notes: This branch addresses the full visible iliopsoas volume on the entire scan, not only at L3.

#### `total_iliopsoas_right_volume_cm3`

- Clinical label: Right iliopsoas volume (volume)
- Unit: cm³
- Family: Full-scan iliopsoas volumes
- Source metrics file: total/metrics.json
- Model / task: TotalSegmentator `total` on the full native CT
- Detection / computation method: Volume converted from mm³ to cm³.
- Appears when: When `--with-total` succeeded.
- Interpretation / notes: This branch addresses the full visible iliopsoas volume on the entire scan, not only at L3.

#### `total_iliopsoas_right_volume_cm3_per_m3`

- Clinical label: Right iliopsoas volume (height-normalized volume)
- Unit: cm³/m³
- Family: Full-scan iliopsoas volumes
- Source metrics file: total/metrics.json
- Model / task: TotalSegmentator `total` on the full native CT
- Detection / computation method: Volume in cm³ divided by patient height cubed in m³.
- Appears when: When `--with-total` succeeded. In addition, `--height-cm` must be provided to populate the height-normalized value.
- Interpretation / notes: This branch addresses the full visible iliopsoas volume on the entire scan, not only at L3.

#### `total_iliopsoas_right_volume_mm3`

- Clinical label: Right iliopsoas volume (volume)
- Unit: mm³
- Family: Full-scan iliopsoas volumes
- Source metrics file: total/metrics.json
- Model / task: TotalSegmentator `total` on the full native CT
- Detection / computation method: Volume read from `total/statistics.json` for this iliopsoas label.
- Appears when: When `--with-total` succeeded.
- Interpretation / notes: This branch addresses the full visible iliopsoas volume on the entire scan, not only at L3.

#### `total_iliopsoas_right_voxel_count`

- Clinical label: Right iliopsoas volume (voxel count)
- Unit: value
- Family: Full-scan iliopsoas volumes
- Source metrics file: total/metrics.json
- Model / task: TotalSegmentator `total` on the full native CT
- Detection / computation method: Number of voxels equal to the iliopsoas label in `total_multilabel.nii.gz`.
- Appears when: When `--with-total` succeeded.
- Interpretation / notes: This branch addresses the full visible iliopsoas volume on the entire scan, not only at L3.

#### `total_iliopsoas_total_volume_cm3`

- Clinical label: Total iliopsoas volume (volume)
- Unit: cm³
- Family: Full-scan iliopsoas volumes
- Source metrics file: total/metrics.json
- Model / task: TotalSegmentator `total` on the full native CT
- Detection / computation method: Volume converted from mm³ to cm³.
- Appears when: When `--with-total` succeeded.
- Interpretation / notes: This branch addresses the full visible iliopsoas volume on the entire scan, not only at L3.

#### `total_iliopsoas_total_volume_cm3_per_m3`

- Clinical label: Total iliopsoas volume (height-normalized volume)
- Unit: cm³/m³
- Family: Full-scan iliopsoas volumes
- Source metrics file: total/metrics.json
- Model / task: TotalSegmentator `total` on the full native CT
- Detection / computation method: Volume in cm³ divided by patient height cubed in m³.
- Appears when: When `--with-total` succeeded. In addition, `--height-cm` must be provided to populate the height-normalized value.
- Interpretation / notes: This branch addresses the full visible iliopsoas volume on the entire scan, not only at L3.

#### `total_iliopsoas_total_volume_mm3`

- Clinical label: Total iliopsoas volume (volume)
- Unit: mm³
- Family: Full-scan iliopsoas volumes
- Source metrics file: total/metrics.json
- Model / task: TotalSegmentator `total` on the full native CT
- Detection / computation method: Volume read from `total/statistics.json` for this iliopsoas label.
- Appears when: When `--with-total` succeeded.
- Interpretation / notes: This branch addresses the full visible iliopsoas volume on the entire scan, not only at L3.

#### `total_iliopsoas_total_voxel_count`

- Clinical label: Total iliopsoas volume (voxel count)
- Unit: value
- Family: Full-scan iliopsoas volumes
- Source metrics file: total/metrics.json
- Model / task: TotalSegmentator `total` on the full native CT
- Detection / computation method: Number of voxels equal to the iliopsoas label in `total_multilabel.nii.gz`.
- Appears when: When `--with-total` succeeded.
- Interpretation / notes: This branch addresses the full visible iliopsoas volume on the entire scan, not only at L3.

#### `total_input_scope`

- Clinical label: Total input scope
- Unit: text
- Family: Total
- Source metrics file: total/metrics.json
- Model / task: TotalSegmentator `total` on the full native CT
- Detection / computation method: Input scope metadata field.
- Appears when: When `--with-total` succeeded.
- Interpretation / notes: Should indicate that the full scan was used.

#### `total_labels_used_for_psoas_volume`

- Clinical label: Labels used for the iliopsoas summary
- Unit: text
- Family: Total
- Source metrics file: total/metrics.json
- Model / task: TotalSegmentator `total` on the full native CT
- Detection / computation method: Pipe-separated list of native `total` labels merged in the iliopsoas summary.
- Appears when: When `--with-total` succeeded.
- Interpretation / notes: Should list `iliopsoas_left|iliopsoas_right`.

#### `total_method`

- Clinical label: Total branch method
- Unit: text
- Family: Total
- Source metrics file: total/metrics.json
- Model / task: TotalSegmentator `total` on the full native CT
- Detection / computation method: Literal method string from the total metrics JSON.
- Appears when: When `--with-total` succeeded.
- Interpretation / notes: Documents that the full-scan `total` task is used.

#### `total_segmentation_name`

- Clinical label: Total segmentation name
- Unit: text
- Family: Total
- Source metrics file: total/metrics.json
- Model / task: TotalSegmentator `total` on the full native CT
- Detection / computation method: Segmentation metadata field.
- Appears when: When `--with-total` succeeded.
- Interpretation / notes: Human-readable name used for Slicer import.

#### `total_source_task`

- Clinical label: Total source task
- Unit: text
- Family: Total
- Source metrics file: total/metrics.json
- Model / task: TotalSegmentator `total` on the full native CT
- Detection / computation method: Source task metadata field.
- Appears when: When `--with-total` succeeded.
- Interpretation / notes: Technical provenance field.

#### `total_task`

- Clinical label: Total task name
- Unit: text
- Family: Total
- Source metrics file: total/metrics.json
- Model / task: TotalSegmentator `total` on the full native CT
- Detection / computation method: Task metadata field.
- Appears when: When `--with-total` succeeded.
- Interpretation / notes: Technical provenance field.

#### `total_voxel_spacing_mm_x`

- Clinical label: Voxel spacing x
- Unit: mm
- Family: Total
- Source metrics file: total/metrics.json
- Model / task: TotalSegmentator `total` on the full native CT
- Detection / computation method: Native voxel spacing x from the NIfTI header.
- Appears when: When `--with-total` succeeded.
- Interpretation / notes: Technical geometry field.

#### `total_voxel_spacing_mm_y`

- Clinical label: Voxel spacing y
- Unit: mm
- Family: Total
- Source metrics file: total/metrics.json
- Model / task: TotalSegmentator `total` on the full native CT
- Detection / computation method: Native voxel spacing y from the NIfTI header.
- Appears when: When `--with-total` succeeded.
- Interpretation / notes: Technical geometry field.

#### `total_voxel_spacing_mm_z`

- Clinical label: Voxel spacing z
- Unit: mm
- Family: Total
- Source metrics file: total/metrics.json
- Model / task: TotalSegmentator `total` on the full native CT
- Detection / computation method: Native voxel spacing z from the NIfTI header.
- Appears when: When `--with-total` succeeded.
- Interpretation / notes: Technical geometry field.

#### `total_warnings`

- Clinical label: Total warnings
- Unit: text
- Family: Total
- Source metrics file: total/metrics.json
- Model / task: TotalSegmentator `total` on the full native CT
- Detection / computation method: Warnings emitted during total metric extraction.
- Appears when: When `--with-total` succeeded.
- Interpretation / notes: Includes missing-height warnings and missing stats entries.
