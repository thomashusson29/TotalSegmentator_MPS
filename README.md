# TotalSegmentator MPS for 3D Slicer

Pipeline autonome pour lancer `TotalSegmentator` hors 3D Slicer sur macOS Apple Silicon avec `MPS` obligatoire et une sortie pensée pour une importation propre dans `3D Slicer`.

Cas d'usage visé :
- entrée : série DICOM CT
- tâche par défaut : `abdominal_muscles`
- device : `mps` uniquement
- sortie principale : `multilabel NIfTI`
- bundle Slicer généré automatiquement :
  - `labels.json`
  - `<task>.ctbl`
  - `import_into_slicer.py`

## Contexte

Ce projet évite le chemin d'exécution Slicer de `TotalSegmentator` sur macOS et s'appuie sur un environnement Python dédié avec un `PyTorch` nightly récent, conformément à la piste confirmée dans :

- <https://github.com/wasserth/TotalSegmentator/issues/250>

## Environnement validé

Validation locale actuelle :
- macOS Apple Silicon
- Homebrew Python `3.13`
- `torch 2.12.0.dev20260407`
- `torch.backends.mps.is_built() == True`
- `torch.backends.mps.is_available() == True`

## Installation

```bash
cd /Users/thomashusson/Documents/Projets/TotalSegmentator_MPS
/opt/homebrew/bin/python3.13 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
python -m pip install --pre torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/nightly/cpu
python -m pip install TotalSegmentator highdicom
```

## Vérification rapide

```bash
cd /Users/thomashusson/Documents/Projets/TotalSegmentator_MPS
source .venv/bin/activate
python - <<'PY'
import torch
print("torch:", torch.__version__)
print("mps_built:", torch.backends.mps.is_built())
print("mps_available:", torch.backends.mps.is_available())
PY
```

Le script échoue explicitement si `MPS` n'est pas disponible.

## Usage courant

```bash
cd /Users/thomashusson/Documents/Projets/TotalSegmentator_MPS
source .venv/bin/activate
python run_totalseg_dicom.py \
  --input-dicom /chemin/vers/dicom_series \
  --output-dir /chemin/vers/output_bundle
```

Arguments exposés :
- `--input-dicom`
- `--output-dir`
- `--task` avec défaut `abdominal_muscles`

Le wrapper :
- force `--device mps`
- génère une sortie `--ml` au format NIfTI
- stream les logs vers la console et vers `stdout.log` / `stderr.log`
- produit un bundle prêt pour Slicer

## Usage le plus simple

Deux scripts stables sont prévus pour l'usage courant :

### 1. Segmenter les muscles abdominaux

```bash
cd /Users/thomashusson/Documents/Projets/TotalSegmentator_MPS
source .venv/bin/activate
python segment_abdominal_muscles.py \
  --input-dicom /chemin/vers/dicom_series
```

Ce script :
- lance toujours la tâche `abdominal_muscles`
- crée automatiquement un dossier de sortie daté dans `output/`
- met à jour un pointeur stable vers le dernier bundle :
  - `output/latest_abdominal_muscles`
  - `output/latest_abdominal_muscles.txt`

### 2. Importer le dernier bundle dans 3D Slicer

Dans la console Python de Slicer :

```python
exec(open("/Users/thomashusson/Documents/Projets/TotalSegmentator_MPS/import_bundle_into_slicer.py").read())
```

Ce script :
- importe par défaut le dernier bundle pointé par `output/latest_abdominal_muscles`
- n'a pas besoin de connaître le nom du dernier dossier daté
- peut aussi recevoir un bundle précis si besoin

## Bundle généré

Dans `--output-dir`, tu obtiens au minimum :
- `<task>_multilabel.nii.gz`
- `labels.json`
- `<task>.ctbl`
- `import_into_slicer.py`
- `command.txt`
- `stdout.log`
- `stderr.log`

Le NIfTI multilabel reçoit aussi une extension d'en-tête avec la table des labels.

## Import dans 3D Slicer

La voie recommandée est :

1. Charger ton volume CT dans Slicer si tu veux l'utiliser comme image de référence.
2. Ouvrir la console Python de Slicer.
3. Exécuter :

```python
exec(open("/Users/thomashusson/Documents/Projets/TotalSegmentator_MPS/import_bundle_into_slicer.py").read())
```

Le script d'import :
- charge la color table générée
- crée un `vtkMRMLSegmentationNode`
- lit le NIfTI multilabel directement comme segmentation si possible
- sinon bascule sur un import `labelmap -> segmentation`
- applique les noms et couleurs des segments
- crée la représentation fermée 3D

Un helper local `import_into_slicer.py` est aussi généré dans chaque bundle, mais le script stable à la racine du projet est plus pratique au quotidien.

## Exemple validé

Le pipeline a été validé sur :

- entrée :
  `/Users/thomashusson/Documents/Projets/TotalSegmentator_MPS/dicom/samples/ScalarVolume_17`
- sortie :
  `/Users/thomashusson/Documents/Projets/TotalSegmentator_MPS/output/scalarvolume17`

Commande :

```bash
cd /Users/thomashusson/Documents/Projets/TotalSegmentator_MPS
source .venv/bin/activate
python run_totalseg_dicom.py \
  --input-dicom /Users/thomashusson/Documents/Projets/TotalSegmentator_MPS/dicom/samples/ScalarVolume_17 \
  --output-dir /Users/thomashusson/Documents/Projets/TotalSegmentator_MPS/output/scalarvolume17
```

## Notes

- `abdominal_muscles` ne supporte pas `--fast` ni `--fastest`.
- Ce workflow ne fait pas de fallback CPU automatique.
- `DICOM SEG` n'est plus la sortie principale de cet outil ; l'objectif ici est l'import fiable comme segmentation dans `3D Slicer`.
- Le pipeline peut faire un **crop interne temporaire** pour accélérer l'inférence, ce que tu vois dans les logs.
- En revanche, la **sortie finale n'est pas rognée** : elle est rééchantillonnée et sauvegardée dans la géométrie du scanner d'origine. Sur l'exemple validé, l'entrée détectée était `(512, 512, 685)` et le NIfTI final a bien la forme `(512, 512, 685)`.
