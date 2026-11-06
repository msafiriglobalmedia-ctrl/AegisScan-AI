# aegisscan/hazard-vision-v0.1

## Description
Demo heuristic hazard detector for the AegisScan AI platform.
Detects possible fire, overexposure/smoke, and low-visibility environments
from a single RGB image.

## Intended use
- Demo / prototype on Render free tier.
- Teaching and pitching the SafeScan concept.

## NOT intended for
- Life-safety decisions.
- Replacing trained inspectors or emergency services.
- Real-time mission-critical deployment.

## Limitations
- Heuristic, not a trained neural network in this version.
- Ignores motion, sound, thermal signals.
- Sensitive to lighting.

## Production roadmap
- v0.2 — TFLite MobileNetV3 fine-tuned on fire/smoke dataset
- v0.3 — ONNX pipeline with audio hazard classifier
- v1.0 — Multimodal: vision + audio + sensor fusion
