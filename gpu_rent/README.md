# GPU Rent Wrapper

Ce dossier ajoute une couche GPU/Linux/CUDA au pipeline existant sans modifier les fichiers du repo principal.

## Objectif

- garder les scripts actuels inchangés
- permettre un lancement sur machine louée type RunPod, Vast.ai, Lambda, etc.
- choisir automatiquement le backend TotalSegmentator :
  - `gpu` si CUDA est disponible
  - `mps` si CUDA est absent mais MPS est disponible
  - `cpu` sinon
- produire un bundle plus portable pour Slicer, avec un `import_into_slicer.py` autonome dans le bundle final

## Fichiers

- `device_override.py`
  - injecte un backend configurable dans le runtime existant
  - ne touche pas aux fichiers du repo principal
- `segment_abdominal_muscles_gpu.py`
  - wrapper GPU/cloud pour `segment_abdominal_muscles.py`
- `segment_liver_bundle_gpu.py`
  - wrapper GPU/cloud pour `segment_liver_bundle.py`
- `portable_import_bundle_into_slicer.py`
  - importeur Slicer autonome copié dans le bundle final
- `postprocess_bundle.py`
  - remplace le helper d’import du bundle par une version portable
- `run_segment_abdominal_case.sh`
  - point d’entrée shell pratique pour RunPod/Linux
- `run_segment_liver_case.sh`
  - variante foie
- `runpod_entrypoint.sh`
  - point d’entrée unique pour RunPod avec conventions `/input` et `/output`
- `runpod_env.example`
  - exemple minimal des variables d’environnement
- `Dockerfile`
  - image CUDA de base pour une location GPU

## Utilisation directe

Depuis le repo :

```bash
cd /workspace/TotalSegmentator_MPS
python gpu_rent/segment_abdominal_muscles_gpu.py \
  --device auto \
  --input-dicom /data/AAW_avantTH \
  --with-muscles \
  --with-odiasp \
  --with-tissue \
  --with-total \
  --height-cm 162
```

Forcer explicitement un GPU CUDA :

```bash
python gpu_rent/segment_abdominal_muscles_gpu.py \
  --device gpu \
  --input-dicom /data/AAW_avantTH \
  --with-muscles \
  --with-odiasp \
  --with-tissue \
  --with-total \
  --height-cm 162
```

Sélectionner un GPU précis :

```bash
python gpu_rent/segment_abdominal_muscles_gpu.py \
  --device gpu:0 \
  --input-dicom /data/AAW_avantTH \
  --with-muscles \
  --with-odiasp \
  --with-tissue \
  --with-total \
  --height-cm 162
```

## Utilisation shell orientée RunPod

Le plus simple sur RunPod est de monter :
- tes scanners dans `/input`
- un volume persistant dans `/output`

Puis de lancer uniquement :

```bash
bash /workspace/TotalSegmentator_MPS/gpu_rent/runpod_entrypoint.sh
```

avec ces variables d’environnement :

```bash
export INPUT_DICOM=/input/AAW_avantTH
export PIPELINE_KIND=abdominal
export TOTALSEG_DEVICE=gpu
export HEIGHT_CM=162
export WITH_MUSCLES=1
export WITH_ODIASP=1
export WITH_TISSUE=1
export WITH_TOTAL=1
export WITH_TOCSV=1
export TOTALSEG_LICENSE_NUMBER=XXXX-XXXX-XXXX
```

Le fichier [runpod_env.example](/Users/thomashusson/Documents/Projets/TotalSegmentator_MPS/gpu_rent/runpod_env.example) contient ce modèle prêt à recopier.

## Utilisation shell détaillée

```bash
cd /workspace/TotalSegmentator_MPS
export INPUT_DICOM=/data/AAW_avantTH
export TOTALSEG_DEVICE=gpu
export HEIGHT_CM=162
export WITH_MUSCLES=1
export WITH_ODIASP=1
export WITH_TISSUE=1
export WITH_TOTAL=1
export WITH_TOCSV=1
export TOTALSEG_LICENSE_NUMBER=XXXX-XXXX-XXXX
bash gpu_rent/run_segment_abdominal_case.sh
```

Avec `runpod_entrypoint.sh`, les conventions par défaut sont :
- entrée attendue dans `/input`
- sorties écrites dans `/output`
- pipeline abdominal si `PIPELINE_KIND` n’est pas défini

## Licence commerciale tissue_4_types

Deux options :

- passer `--totalseg-license-number` explicitement
- ou définir `TOTALSEG_LICENSE_NUMBER` dans l’environnement

Le wrapper ajoute automatiquement `--totalseg-license-number` si la variable d’environnement est définie et si le flag n’a pas déjà été passé.

## Bundle portable pour Slicer

Après un run réussi, le wrapper recopie un importeur autonome dans le bundle :

- `import_into_slicer.py`
- `_portable_import_bundle_into_slicer.py`
- `SLICER_IMPORT_COMMAND.txt`

Sur ta machine locale, après téléchargement du bundle, tu peux importer directement avec :

```python
exec(open("/chemin/vers/le_bundle/import_into_slicer.py").read())
```

Ce helper ne dépend pas du chemin absolu du serveur GPU.

## Docker

Exemple de build local ou distant :

```bash
cd /workspace/TotalSegmentator_MPS
docker build -f gpu_rent/Dockerfile -t totalseg-gpu-rent .
```

Puis lancement :

```bash
docker run --gpus all --rm -it \
  -v /chemin/local/data:/input \
  -v /chemin/local/output:/output \
  -e INPUT_DICOM=/input/AAW_avantTH \
  -e TOTALSEG_DEVICE=gpu \
  -e HEIGHT_CM=162 \
  -e WITH_MUSCLES=1 \
  -e WITH_ODIASP=1 \
  -e WITH_TISSUE=1 \
  -e WITH_TOTAL=1 \
  -e TOTALSEG_LICENSE_NUMBER=XXXX-XXXX-XXXX \
  totalseg-gpu-rent
```

Le conteneur lance automatiquement `gpu_rent/runpod_entrypoint.sh`.

## Limites

- Les scripts originaux du repo restent orientés `mps` quand ils sont exécutés directement.
- Pour un contexte GPU/Linux, il faut lancer les wrappers de `gpu_rent/`.
- Le Dockerfile est volontairement minimal. Si tu veux figer totalement l’environnement, il faudra aussi pinner précisément les versions Python, Torch et TotalSegmentator.

## Anonymisation DICOM avant upload

Si tu veux envoyer les scanners sur RunPod sans exposer les noms/prénoms dans les dossiers ni dans les tags DICOM, utilise :

```bash
cd /Users/thomashusson/Documents/Projets/TotalSegmentator_MPS
source .venv/bin/activate
python gpu_rent/anonymize_dicom_tree.py \
  --input-root /Users/thomashusson/Documents/Projets/TotalSegmentator_MPS/tdm_elena_savier \
  --output-root /Users/thomashusson/Documents/Projets/TotalSegmentator_MPS/gpu_rent/anonymized_exports/tdm_elena_savier_anonymized \
  --mapping-csv /Users/thomashusson/Documents/Projets/TotalSegmentator_MPS/gpu_rent/local_only/tdm_elena_savier_mapping.csv
```

Le script :
- ne modifie jamais les DICOM originaux
- crée une copie anonymisée avec des dossiers du type `PAT_0001_CASE_01`
- remplace dans les DICOM les identifiants patients et noms
- vide les dates, numéros d’accession et plusieurs champs institutionnels
- supprime les tags privés
- régénère les UIDs DICOM

Le fichier `mapping.csv` contient la correspondance avec les noms originaux. Il est prévu pour rester en local et ne doit pas être uploadé avec les données anonymisées.
