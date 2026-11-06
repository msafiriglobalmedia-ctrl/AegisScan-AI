"""
AegisScan hazard detector — DEMO heuristic.
Production: replace `analyze_image` with real inference
(TFLite / ONNX / TorchScript / HuggingFace Inference API).
"""
import numpy as np
from PIL import Image
from config import MODEL_ID


def analyze_image(img: Image.Image) -> dict:
    img = img.convert("RGB").resize((128, 128))
    arr = np.asarray(img, dtype=np.float32) / 255.0
    r, g, b = arr[..., 0], arr[..., 1], arr[..., 2]

    brightness = float(arr.mean())
    fire_pixels = (r > 0.7) & (g < 0.5) & (b < 0.3)
    fire_score = float(fire_pixels.mean())
    darkness = float((arr.mean(axis=2) < 0.12).mean())

    hazards = []
    risk = 0.0

    if fire_score > 0.04:
        hazards.append({
            "type": "possible_fire",
            "confidence": round(min(fire_score * 3, 0.95), 2),
            "severity": "high",
        })
        risk += 70 * min(fire_score * 3, 1.0)

    if brightness > 0.92:
        hazards.append({
            "type": "possible_smoke_or_overexposure",
            "confidence": 0.40,
            "severity": "low",
        })
        risk += 10

    if darkness > 0.7:
        hazards.append({
            "type": "low_visibility",
            "confidence": 0.60,
            "severity": "medium",
        })
        risk += 25

    if not hazards:
        hazards.append({
            "type": "clear",
            "confidence": 0.80,
            "severity": "none",
        })

    risk = min(100.0, round(risk, 1))
    if risk >= 70:
        level = "critical"
    elif risk >= 40:
        level = "high"
    elif risk >= 15:
        level = "medium"
    else:
        level = "low"

    return {
        "hazards": hazards,
        "risk_score": risk,
        "risk_level": level,
        "brightness": round(brightness, 3),
        "model_id": MODEL_ID,
        "demo_note": "Heuristic demo analyzer. Swap with real CV model for production.",
    }
