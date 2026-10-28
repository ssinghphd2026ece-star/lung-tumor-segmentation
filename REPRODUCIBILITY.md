# Fidelity and missing information

The manuscript specifies: 33 eligible reference–target pairs from 20 TCIA subjects (20 phase + 13 longitudinal), an 11-pair patient-separated development subset, 1.5 mm isotropic CT resampling, HU clipping [-1000,1000], rigid → affine → B-spline stages, Mattes MI, three resolution levels (4/2/1; smoothing 2/1/0), one-voxel dilated three-plane mask prompts (P5), nnInteractive and MedSAM2, DSC/HD50/HD95/ASSD/2mm Surface Dice/precision/recall, DIR-Lab TRE, Jacobian folding QA and patient-level significance tests.

**Not supplied in the manuscript:** original 33 pair IDs, full target GTV RTSTRUCT mapping, 11-pair development assignment, exact B-spline mesh/grid/control-point spacing, optimizer settings/iterations/sampling, precise model checkpoint and code revision, nnInteractive/MedSAM2 prompt API, complete raw per-pair predictions, preprocessing crop specifics, individual measured timing environment, original inference stochasticity. The default 45-mm B-spline mesh and optimization settings are explicit reconstruction assumptions, not paper-verified settings.

**Reported results conflict:** Table 4 lists DIR+nnInteractive mean DSC 0.850±0.030; Table 5 and Discussion give 0.840±0.060. This repository NEVER hardcodes either result. It produces actual output data for comparison. Also Table 1 includes an unexplained external registration-validation count of 11 versus DIR-Lab n=10. Resolve before exact reproducibility claims.

**Validation caution:** The paper says 11 development pairs selected P5 and later reports 33-pair full-cohort performance. Because the 11 development pairs are included in 33, the primary full-cohort descriptive estimate is not an untouched test-set estimate. The implementation outputs development/evaluation splits separately and requires subject-level independence. For unbiased inference report the held-out evaluation partition separately.

**Masks and geometry:** DICOM/RTSTRUCT conversion needs linkage and contour geometry verification by a qualified reviewer. CT inputs must have correct HU values. `score_predictions.py` computes physical-space distances in original target geometry. Failed/empty-segmentation HD95 is NaN, never silently set to 0. Jacobian folding is diagnostic rather than a clinical safety guarantee.

**Timing:** reported 84s/pair is an article claim; actual measured timings vary with CPU/GPU/hardware, and this reconstruction will not fabricate timings.

This toolkit is for research and methodology evaluation, **not** clinically approved contour generation.

**Verification in the authoring environment:** Six dependency-light core tests passed and Python source compilation completed. A real SimpleITK registration smoke test could not run because SimpleITK was not installed in this environment. Installation, registration convergence, physical orientation, DICOM metadata and external model adapters require validation in the researcher's environment before use.
