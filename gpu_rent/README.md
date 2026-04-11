# GPU Rent

Ce dossier contient la version autonome du pipeline abdominal pour RunPod / machine GPU Linux, sans dépendre des anciens scripts racine orientés MPS.

## Fichiers utiles

- `segment_abdominal_muscles_gpu.py`
  - pipeline principal autonome
  - gère `--with-muscles`, `--with-odiasp`, `--with-tissue`, `--with-total`, `--with-tocsv`, `--height-cm`
- `common.py`
  - helpers TotalSegmentator, DICOM, bundles, import Slicer
- `abdominal_muscles_metrics.py`
  - métriques 3D musculaires T4-L4-like
- `odiasp_pipeline.py`
  - sortie ODIASP compatible L3
- `tissue_pipeline.py`
  - sorties `tissue_4_types_original` et `tissue_4_types_T4_L4`
- `total_pipeline.py`
  - sortie `total` complète et résumé `iliopsoas`
- `metrics_csv.py`
  - export CSV par cas
- `portable_import_bundle_into_slicer.py`
  - importeur Slicer autonome copié dans chaque bundle
- `postprocess_bundle.py`
  - installe l’importeur Slicer portable dans le bundle
- `run_segment_abdominal_case.sh`
  - wrapper shell pratique
- `runpod_entrypoint.sh`
  - entrypoint RunPod `/input` -> `/output`
- `runpod_env.example`
  - exemple minimal d’environnement
- `requirements.txt`
  - dépendances Python de base

## Utilisation directe

Depuis le repo :

```bash
cd /workspace/TotalSegmentator_MPS
python -m gpu_rent.segment_abdominal_muscles_gpu \
  --input-dicom /input/tdm_elena_savier_anonymized/PAT_0001_CASE_01 \
  --output-root /output \
  --device gpu \
  --with-muscles \
  --with-odiasp \
  --with-tissue \
  --with-total \
  --with-tocsv \
  --height-cm 162 \
  --totalseg-license-number XXXX-XXXX-XXXX
```

Si aucun `--with-*` n’est fourni, le pipeline sort seulement `abdominal_muscles`.

## Utilisation RunPod

Le plus simple sur RunPod est :

```bash
export INPUT_DICOM=/input/tdm_elena_savier_anonymized/PAT_0001_CASE_01
export PIPELINE_KIND=abdominal
export TOTALSEG_DEVICE=gpu
export OUTPUT_ROOT=/output
export HEIGHT_CM=162
export WITH_MUSCLES=1
export WITH_ODIASP=1
export WITH_TISSUE=1
export WITH_TOTAL=1
export WITH_TOCSV=1
export TOTALSEG_LICENSE_NUMBER=XXXX-XXXX-XXXX

bash /workspace/TotalSegmentator_MPS/gpu_rent/runpod_entrypoint.sh
```

## Sorties

Le bundle final contient :

- racine :
  - `abdominal_muscles_multilabel.nii.gz` si `with-muscles`
  - `abdominal_muscles_metrics.json`
  - `labels.json` / `abdominal_muscles.ctbl` si `with-muscles`
  - `import_into_slicer.py`
  - `_portable_import_bundle_into_slicer.py`
  - `SLICER_IMPORT_COMMAND.txt`
- `odiasp/`
- `tissue/`
- `total/`

## Import dans Slicer

Après téléchargement du bundle sur ta machine locale :

```python
exec(open("/chemin/vers/le_bundle/import_into_slicer.py").read())
```

Le helper importe automatiquement la racine du bundle et les sous-bundles immédiats (`odiasp`, `tissue`, `total`) quand ils existent.

## DICOM anonymisés

Le dossier déjà préparé pour RunPod est :

`gpu_rent/anonymized_exports/tdm_elena_savier_anonymized`

Le mapping patient réel ↔ identifiant anonymisé doit rester local et ne pas être uploadé.

