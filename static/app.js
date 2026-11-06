const video = document.getElementById("cam");
const canvas = document.getElementById("canvas");
const preview = document.getElementById("preview");
const resultEl = document.getElementById("result");
const alertBtn = document.getElementById("alert");
const incidentsEl = document.getElementById("incidents");

let lastIncidentId = null;

document.getElementById("start").onclick = async () => {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({
      video: { facingMode: "environment" },
    });
    video.srcObject = stream;
  } catch (e) {
    alert("Camera error: " + e.message);
  }
};

document.getElementById("capture").onclick = () => {
  if (!video.videoWidth) return alert("Start camera first");
  canvas.width = video.videoWidth;
  canvas.height = video.videoHeight;
  canvas.getContext("2d").drawImage(video, 0, 0);
  const dataUrl = canvas.toDataURL("image/jpeg", 0.8);
  preview.innerHTML = `<img src="${dataUrl}" alt="capture" />`;
  scan(dataUrl);
};

document.getElementById("file").onchange = (e) => {
  const f = e.target.files[0];
  if (!f) return;
  const reader = new FileReader();
  reader.onload = () => {
    preview.innerHTML = `<img src="${reader.result}" alt="upload" />`;
    scan(reader.result);
  };
  reader.readAsDataURL(f);
};

async function scan(imageDataUrl) {
  resultEl.textContent = "Scanning…";
  const res = await fetch("/api/scan", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ image: imageDataUrl }),
  });
  const data = await res.json();
  if (!res.ok) {
    resultEl.textContent = "Error: " + (data.error || "unknown");
    return;
  }
  lastIncidentId = data.incident.id;
  alertBtn.disabled = false;
  const a = data.analysis;
  resultEl.innerHTML = `
    <p><strong>Risk:</strong>
      <span class="lvl ${a.risk_level}">${a.risk_level.toUpperCase()}</span>
      (${a.risk_score}/100)</p>
    <p><strong>Model:</strong> <code>${a.model_id}</code></p>
    <ul>${a.hazards.map(h =>
      `<li>${h.type} — ${Math.round(h.confidence * 100)}% (${h.severity})</li>`
    ).join("")}</ul>
    <p class="note">${a.demo_note}</p>
  `;
  loadIncidents();
}

alertBtn.onclick = async () => {
  if (!lastIncidentId) return;
  const res = await fetch("/api/alert", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      incident_id: lastIncidentId,
      channels: ["sms", "push"],
      recipients: ["+255000000000"],
    }),
  });
  const data = await res.json();
  alert("Alert queued ✅\nID: " + data.alert.id);
};

async function loadIncidents() {
  const res = await fetch("/api/incidents");
  const data = await res.json();
  incidentsEl.innerHTML =
    data.incidents.slice(0, 10).map(i =>
      `<li><span class="lvl ${i.risk_level}">${i.risk_level}</span>
       ${i.risk_score}/100 — ${i.hazards[0]?.type || ""}
       <small>${i.timestamp}</small></li>`
    ).join("") || "<li>No incidents yet.</li>";
}

loadIncidents();
