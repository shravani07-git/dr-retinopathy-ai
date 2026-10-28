from __future__ import annotations

import io
import math
import os
from typing import Dict

import numpy as np
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image

from model_adapter import predict_with_model, model_available

app = FastAPI(title="RetinaGuard AI API", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

LABELS = ["No DR", "Mild DR", "Moderate DR", "Severe DR", "Proliferative DR"]


def _quality_metrics(img: Image.Image) -> Dict[str, float | int | str]:
    rgb = np.asarray(img.convert("RGB").resize((512, 512)), dtype=np.float32) / 255.0
    gray = 0.299 * rgb[..., 0] + 0.587 * rgb[..., 1] + 0.114 * rgb[..., 2]
    brightness = float(gray.mean())
    contrast = float(gray.std())

    gx = np.diff(gray, axis=1)
    gy = np.diff(gray, axis=0)
    sharpness = float(np.sqrt((gx[:, :-1] ** 2 + gy[:-1, :] ** 2).mean()))

    brightness_score = max(0.0, 1.0 - abs(brightness - 0.42) / 0.42)
    contrast_score = min(1.0, contrast / 0.18)
    sharpness_score = min(1.0, sharpness / 0.06)
    score = int(round(100 * (0.35 * brightness_score + 0.30 * contrast_score + 0.35 * sharpness_score)))

    if score >= 75:
        label = "Good"
    elif score >= 50:
        label = "Usable"
    else:
        label = "Poor — retake suggested"

    return {
        "score": score,
        "label": label,
        "brightness": round(brightness, 3),
        "contrast": round(contrast, 3),
        "sharpness": round(sharpness, 3),
    }


def _demo_predict(img: Image.Image):
    """Deterministic UI-only simulation. NOT a medical model."""
    arr = np.asarray(img.convert("RGB").resize((256, 256)), dtype=np.float32) / 255.0
    r, g, b = arr[..., 0], arr[..., 1], arr[..., 2]
    red_dominance = float(np.mean(np.clip(r - (g + b) / 2.0, 0, 1)))
    bright_spots = float(np.mean((r > 0.72) & (g > 0.58) & (b < 0.48)))
    dark_spots = float(np.mean((r < 0.28) & (g < 0.20) & (b < 0.20)))
    texture = float(np.std(np.diff((r + g + b) / 3.0, axis=0)))

    raw = 1.2 * red_dominance + 3.0 * bright_spots + 2.3 * dark_spots + 1.2 * texture
    idx = int(np.clip(math.floor(raw * 8), 0, 4))
    confidence = float(np.clip(0.58 + abs(raw - round(raw, 1)) * 0.7, 0.58, 0.88))

    indicators = {
        "microaneurysm_proxy": "low" if dark_spots < 0.08 else "elevated",
        "hemorrhage_proxy": "low" if red_dominance < 0.12 else "elevated",
        "exudate_proxy": "low" if bright_spots < 0.03 else "elevated",
        "texture_irregularity": "low" if texture < 0.09 else "elevated",
    }
    return LABELS[idx], confidence, indicators


def _recommendation(label: str, quality_score: int) -> str:
    if quality_score < 50:
        return "Image quality is poor. Capture a clearer, well-centered fundus image and repeat screening. If symptoms are present, seek professional eye care instead of relying on a repeat image."
    mapping = {
        "No DR": "No DR was predicted by the model. Continue routine diabetic eye screening at intervals recommended by your clinician.",
        "Mild DR": "Mild DR was predicted. Arrange a non-urgent professional retinal review and maintain glucose, blood-pressure, and lipid control with your healthcare team.",
        "Moderate DR": "Moderate DR was predicted. A timely ophthalmology or retinal evaluation is recommended for confirmation and management planning.",
        "Severe DR": "Severe DR was predicted. Prompt specialist retinal evaluation is recommended because vision-threatening disease may be present.",
        "Proliferative DR": "Proliferative DR was predicted. Urgent ophthalmology/retina specialist assessment is recommended, especially if there is new vision loss, floaters, or visual distortion.",
    }
    return mapping[label]


@app.get("/")
def root():
    return {"name": "RetinaGuard AI API", "status": "ok", "model_available": model_available()}


@app.post("/analyze")
async def analyze(
    file: UploadFile = File(...),
    years_with_diabetes: float = Form(0),
    hba1c: float = Form(0),
    hypertension: bool = Form(False),
    vision_change: bool = Form(False),
):
    if file.content_type not in {"image/jpeg", "image/png"}:
        raise HTTPException(status_code=400, detail="Only JPG/JPEG and PNG images are supported.")

    content = await file.read()
    if len(content) > 12 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Image is too large. Maximum size is 12 MB.")

    try:
        image = Image.open(io.BytesIO(content)).convert("RGB")
    except Exception:
        raise HTTPException(status_code=400, detail="The uploaded file is not a readable image.")

    if image.width < 224 or image.height < 224:
        raise HTTPException(status_code=400, detail="Image resolution is too small. Use at least 224×224 pixels.")

    quality = _quality_metrics(image)

    if model_available():
        severity, confidence, probabilities = predict_with_model(image)
        indicators = {
            "microaneurysms": "model-ready",
            "hemorrhages": "model-ready",
            "hard_exudates": "model-ready",
            "cotton_wool_spots": "model-ready",
        }
        is_demo = False
    else:
        severity, confidence, indicators = _demo_predict(image)
        probabilities = None
        is_demo = True

    return {
        "severity": severity,
        "confidence": round(float(confidence), 4),
        "quality": quality,
        "indicators": indicators,
        "recommendation": _recommendation(severity, int(quality["score"])),
        "is_demo": is_demo,
        "probabilities": probabilities,
        "risk_context": {
            "years_with_diabetes": years_with_diabetes,
            "hba1c": hba1c,
            "hypertension": hypertension,
            "vision_change": vision_change,
            "note": "Risk context is returned separately and is not fused into the image-model prediction in this starter project.",
        },
    }
