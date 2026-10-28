# RetinaGuard AI — Diabetic Retinopathy Screening Project

A polished React + FastAPI project for uploading retinal/fundus images and classifying diabetic retinopathy into five severity levels.

> **Important:** This project is for education/research demonstrations. It is not a medical device and must not be used as a substitute for diagnosis by an ophthalmologist.

## Features

- Modern responsive React UI/UX with dark/light mode
- Drag-and-drop fundus image upload and preview
- Five DR classes: No DR, Mild, Moderate, Severe, Proliferative DR
- Image-quality gate: brightness, contrast, and sharpness checks
- Model confidence and severity visualization
- Lesion/visual-indicator panel ready for real explainability outputs
- Optional risk context: years with diabetes, HbA1c, hypertension, vision changes
- Exportable screening summary
- Privacy-oriented backend: uploads are processed in memory by default
- FastAPI API with validation and CORS
- Automatic **real model / demo model** detection
- EfficientNet-B0 training starter
- Clear adapter for plugging trained weights into production inference

## Project structure

```text
dr_retinopathy_ai/
├── frontend/                 React + Vite UI
│   └── src/
├── backend/
│   ├── main.py              FastAPI server + image quality checks
│   ├── model_adapter.py     real-model loader
│   └── model/               put trained .pt weights here
├── ml/
│   └── train_model.py       EfficientNet-B0 training starter
└── README.md
```

## 1. Run the backend

Open Terminal 1:

```bash
cd backend
python -m venv .venv
```

### Windows PowerShell
```powershell
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

Backend: http://localhost:8000  
Swagger docs: http://localhost:8000/docs

## 2. Run the React frontend

Open Terminal 2:

```bash
cd frontend
npm install
npm run dev
```

Frontend: http://localhost:5173

## Demo mode vs real model mode

The ZIP does **not** include trained medical weights or a medical dataset. Therefore, on first run the backend uses a deterministic **demo simulation** and the UI displays a clear warning.

To enable real ML inference:

1. Install ML dependencies:
   ```bash
   pip install -r requirements-ml.txt
   ```
2. Train a model with `ml/train_model.py` or use compatible weights.
3. Save the weights as:
   ```text
   backend/model/dr_efficientnet_b0.pt
   ```
4. Restart FastAPI.

The API then automatically changes `is_demo` to `false` and uses EfficientNet-B0 inference.

## ML pipeline

```text
User
  ↓
Upload Eye Image
  ↓
Image Validation + Quality Gate
  ↓
Resize / Normalize
  ↓
EfficientNet-B0 CNN
  ↓
5-Class DR Prediction
  ↓
Confidence + Visual Indicator Layer
  ↓
Risk Context (kept separate)
  ↓
Recommendation / Exportable Summary
```

## Unique functionality explained

### 1. Image Quality Gate
Before inference, the backend estimates brightness, contrast, and sharpness. Bad fundus images can cause unreliable AI predictions, so the project warns users when the image should be retaken.

### 2. Separation of Image Diagnosis and Risk Context
Years with diabetes, HbA1c, hypertension, and vision-change inputs are shown as contextual risk factors but are **not silently fused** into the image prediction. This makes the model behavior easier to explain and safer for an academic demonstration.

### 3. Explainability-ready Design
The results panel includes a lesion/indicator area. With a trained CNN, you can add Grad-CAM heatmaps and lesion segmentation without redesigning the UI.

### 4. Privacy-first Processing
The starter API reads the uploaded image into memory and does not save it to disk automatically.

### 5. Exportable Screening Summary
A user can export the result, confidence, image-quality score, and recommendation as a text report.

## Good next upgrades for a final-year project

- Add Grad-CAM heatmap generation
- Add retinal cropping / black-border removal
- Add left-eye vs right-eye comparison
- Add patient history dashboard and progression chart
- Add user authentication and encrypted reports
- Add PostgreSQL/MongoDB for opt-in report history
- Add bilingual accessibility
- Add doctor-review workflow
- Add PDF clinical-style report
- Add model calibration and uncertainty flag
- Add lesion segmentation for microaneurysms/exudates

## Evaluation metrics you should report

For a real dissertation/final project, do not report accuracy alone. Include:

- Confusion matrix
- Class-wise precision, recall, F1-score
- Sensitivity / specificity
- Quadratic Weighted Kappa (QWK)
- ROC-AUC where appropriate
- Calibration / confidence reliability
- External validation on a separate dataset if available

## Medical disclaimer

This software is a research/education prototype. A retinal image classifier can produce false positives and false negatives. Any concerning symptoms or abnormal screening output should be evaluated by a qualified eye-care professional.
