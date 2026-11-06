import io
import base64
import uuid
from datetime import datetime, timezone

from flask import Flask, request, jsonify, render_template
from PIL import Image

from config import MODEL_ID, APP_VERSION, MAX_INCIDENTS
from models import analyze_image

app = Flask(__name__)

# Demo-only stores. Production: use Supabase / MongoDB.
INCIDENTS: list = []
ALERTS: list = []


@app.get("/")
def index():
    return render_template("index.html", model_id=MODEL_ID, version=APP_VERSION)


@app.get("/api/health")
def health():
    return jsonify({
        "status": "ok",
        "model_id": MODEL_ID,
        "version": APP_VERSION,
        "time": datetime.now(timezone.utc).isoformat(),
    })


@app.post("/api/scan")
def scan():
    data = request.get_json(silent=True) or {}
    image_b64 = data.get("image")
    if not image_b64:
        return jsonify({"error": "missing 'image' (base64)"}), 400

    try:
        if "," in image_b64:
            image_b64 = image_b64.split(",", 1)[1]
        raw = base64.b64decode(image_b64)
        img = Image.open(io.BytesIO(raw))
    except Exception as e:
        return jsonify({"error": f"invalid image: {e}"}), 400

    analysis = analyze_image(img)
    incident = {
        "id": str(uuid.uuid4()),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "risk_level": analysis["risk_level"],
        "risk_score": analysis["risk_score"],
        "hazards": analysis["hazards"],
        "location": data.get("location"),
    }
    INCIDENTS.append(incident)
    del INCIDENTS[:-MAX_INCIDENTS]
    return jsonify({"incident": incident, "analysis": analysis})


@app.get("/api/incidents")
def get_incidents():
    return jsonify({"incidents": list(reversed(INCIDENTS))})


@app.post("/api/alert")
def send_alert():
    data = request.get_json(silent=True) or {}
    alert = {
        "id": str(uuid.uuid4()),
        "incident_id": data.get("incident_id"),
        "channels": data.get("channels", ["sms", "push"]),
        "recipients": data.get("recipients", []),
        "status": "queued",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "note": "Demo: no real messages sent. Wire Twilio / Africa's Talking / FCM here.",
    }
    ALERTS.append(alert)
    return jsonify({"alert": alert})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
