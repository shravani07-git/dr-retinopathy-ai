# ML training starter

This folder contains an EfficientNet-B0 training script for a 5-class diabetic retinopathy dataset such as APTOS/EyePACS-style data.

## Expected labels
- 0 = No DR
- 1 = Mild
- 2 = Moderate
- 3 = Severe
- 4 = Proliferative DR

## Example
```bash
pip install -r ../backend/requirements-ml.txt
python train_model.py --csv ./train.csv --images ./train_images --epochs 8
```

The best weights are written to `backend/model/dr_efficientnet_b0.pt`, where the API automatically detects them.

For a serious research project, add patient-level splitting, quadratic weighted kappa, sensitivity/specificity, calibration, external validation, bias analysis, and clinician review.
