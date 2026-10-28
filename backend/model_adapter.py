"""Model adapter for RetinaGuard AI.

If backend/model/dr_efficientnet_b0.pt exists and PyTorch/torchvision are installed,
the API will use it. The expected weights are for torchvision EfficientNet-B0 with
classifier output size 5 in the order:
0 No DR, 1 Mild DR, 2 Moderate DR, 3 Severe DR, 4 Proliferative DR.
"""
from pathlib import Path

MODEL_PATH = Path(__file__).parent / "model" / "dr_efficientnet_b0.pt"
LABELS = ["No DR", "Mild DR", "Moderate DR", "Severe DR", "Proliferative DR"]
_MODEL = None
_TRANSFORM = None


def model_available() -> bool:
    if not MODEL_PATH.exists():
        return False
    try:
        import torch  # noqa
        import torchvision  # noqa
        return True
    except Exception:
        return False


def _load():
    global _MODEL, _TRANSFORM
    if _MODEL is not None:
        return
    import torch
    from torchvision import models, transforms

    model = models.efficientnet_b0(weights=None)
    model.classifier[1] = torch.nn.Linear(model.classifier[1].in_features, 5)
    state = torch.load(MODEL_PATH, map_location="cpu")
    model.load_state_dict(state)
    model.eval()

    _MODEL = model
    _TRANSFORM = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
    ])


def predict_with_model(image):
    import torch
    _load()
    x = _TRANSFORM(image).unsqueeze(0)
    with torch.no_grad():
        logits = _MODEL(x)
        probs = torch.softmax(logits, dim=1)[0]
    idx = int(torch.argmax(probs).item())
    return LABELS[idx], float(probs[idx].item()), [round(float(x), 5) for x in probs.tolist()]
