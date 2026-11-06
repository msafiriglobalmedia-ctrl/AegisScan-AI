import base64
import io
from PIL import Image
from app import app


def _make_b64(color):
    img = Image.new("RGB", (64, 64), color)
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()


def test_health():
    c = app.test_client()
    r = c.get("/api/health")
    assert r.status_code == 200
    assert r.get_json()["status"] == "ok"


def test_scan_fire():
    c = app.test_client()
    r = c.post("/api/scan", json={"image": _make_b64((255, 60, 20))})
    assert r.status_code == 200
    assert r.get_json()["analysis"]["risk_level"] in ("high", "critical")


def test_scan_clear():
    c = app.test_client()
    r = c.post("/api/scan", json={"image": _make_b64((100, 150, 200))})
    assert r.status_code == 200
    assert "hazards" in r.get_json()["analysis"]
