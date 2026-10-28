# Registration-Derived Spatial Prompting for Lung GTV Refinement

Research reproduction toolkit for the manuscript **Registration-Derived Spatial Prompting for Foundation-Model Refinement of Lung Tumor Contours in Adaptive Radiotherapy**.

This project implements the reproducible registration, propagation, prompt construction, quality assurance, original-geometry scoring, patient-level analysis, ablation orchestration and plots. **Actual nnInteractive and MedSAM2 require separately installed authentic models and custom version-pinned wrappers**; their checkpoints and exact API are not present in the paper and are not distributed here. See `adapters/README.md` and `REPRODUCIBILITY.md`.

## Installation

```bash
python -m venv .venv
# activate your environment
pip install -r requirements.txt
pytest -q
```

## Dataset preparation

Obtain TCIA 4D-Lung and DIR-Lab data under their respective terms. Choose CT series and verified physician GTV RTSTRUCT, reconstruct the CT as NIfTI and obtain the corresponding GTV binary NIfTI in the **same physical frame**. `scripts/convert_dicom.py` and `scripts/convert_rtstruct.py` are aids, not an automatic patient/ROI eligibility detector. Run visual checks and verify FrameOfReferenceUID and contour references.

Make a manifest in the format of `examples/pairs.csv` with **absolute** file paths, verified target contours for quantitative work, `development` vs `evaluation` subset, distinct patients across subsets. The paper's exact 33 pairs and 11 development IDs were not supplied and cannot be manufactured from aggregate outcomes.

## Run registration, propagation, QA and metrics

```bash
python -m scripts.run_pipeline --manifest pairs.csv --out outputs/registration
```

To prepare P5 and run the external REAL model, populate `models.nninteractive_command` in `configs/default.yaml` (see `adapters/README.md`), then:

```bash
python -m scripts.run_pipeline --manifest pairs.csv --out outputs/with_nn --models nninteractive
python -m scripts.run_pipeline --manifest pairs.csv --out outputs/all --models nninteractive medsam2 --all-stages
```

**Warning:** the models will fail fast with a descriptive message if wrappers are not configured. No stand-in network can validate the paper's claimed zero-shot foundation-model results.

## Original-geometry score and statistical analysis

```bash
python -m scripts.score_predictions --manifest pairs.csv --pred-dir outputs/with_nn --method bspline+nninteractive --out outputs/nn_metrics.csv
python -m scripts.analyze --metrics outputs/with_nn/pair_metrics.csv --out outputs/analysis
python -m scripts.plot_results --metrics outputs/with_nn/pair_metrics.csv --out outputs/figures
```

## Prompt ablation (development data only)

```bash
python -m scripts.prompt_ablation --manifest pairs.csv --model nninteractive --out outputs/prompt_ablation
```

## DIR-Lab TRE

Landmarks must be verified **physical coordinates in millimetres (x,y,z)**, with correspondence preserved. Registration transforms map target/fixed to reference/moving coordinates.

```bash
python -m scripts.validate_landmarks --target-landmarks target_points.csv --source-landmarks source_points.csv --transform outputs/registration/pair001/bspline.tfm --out outputs/tre.csv
```

## Metrics and limitations

DSC, HD50, HD95, ASSD, 2-mm surface Dice, precision, recall, tumor volume, motion category, Jacobian folding fraction, and paired subject-level Wilcoxon tests with Holm correction are implemented. 4D-Lung 33-pair and 11-pair cohort counts, published DSC, and 84-second runtime **are reported manuscript values, not program outputs**.

The code contains no patient data or pretrained model weights. Requires independent verification before using in a medical research report. Not for clinical use.
