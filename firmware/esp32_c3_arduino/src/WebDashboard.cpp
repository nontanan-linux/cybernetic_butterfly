#include "WebDashboard.h"

WebDashboard::WebDashboard(WingKinematics& kinematics, LEDEffects& ledEffects)
    : _server(HTTP_PORT),
      _kinematics(kinematics),
      _ledEffects(ledEffects) {}

void WebDashboard::begin() {
    WiFi.mode(WIFI_AP);
    WiFi.softAP(AP_SSID, AP_PASS);

    Serial.print("Access Point started: ");
    Serial.println(AP_SSID);
    Serial.print("Dashboard IP URL: http://");
    Serial.println(WiFi.softAPIP());

    _server.on("/", HTTP_GET, [this]() { handleRoot(); });
    _server.on("/set_state", HTTP_GET, [this]() { handleSetState(); });
    _server.on("/set_pattern", HTTP_GET, [this]() { handleSetPattern(); });
    _server.on("/set_speed", HTTP_GET, [this]() { handleSetSpeed(); });
    _server.on("/status", HTTP_GET, [this]() { handleStatus(); });

    _server.begin();
}

void WebDashboard::handleClient() {
    _server.handleClient();
}

void WebDashboard::handleRoot() {
    const char html[] PROGMEM = R"rawliteral(
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Cybernetic Butterfly Controller</title>
  <style>
    body { font-family: -apple-system, system-ui, sans-serif; background: #0b0f19; color: #f1f5f9; text-align: center; margin: 0; padding: 20px; }
    h1 { color: #64ffda; font-size: 22px; margin-bottom: 4px; }
    p.sub { color: #94a3b8; font-size: 13px; margin-top: 0; }
    .card { background: #151d30; border: 1px solid #1e293b; border-radius: 12px; padding: 16px; margin: 15px auto; max-width: 420px; }
    .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-top: 10px; }
    button { background: #1e293b; border: 1px solid #334155; color: #e2e8f0; padding: 12px; border-radius: 8px; font-weight: bold; cursor: pointer; transition: 0.2s; font-size: 14px; }
    button:hover, button.active { background: #2563eb; border-color: #38bdf8; color: #fff; }
    button.special { background: #059669; border-color: #10b981; }
    .slider-box { margin-top: 12px; text-align: left; }
    label { font-size: 13px; color: #cbd5e1; }
    input[type=range] { width: 100%; accent-color: #64ffda; margin-top: 6px; }
    .badge { display: inline-block; padding: 4px 10px; border-radius: 20px; background: #334155; font-size: 12px; color: #38bdf8; }
  </style>
</head>
<body>
  <h1>🦋 CYBER-BUTTERFLY</h1>
  <p class="sub">ESP32-C3 Kinematics & LED Control</p>
  
  <div class="card">
    <div style="font-size: 14px; font-weight: bold; margin-bottom: 8px;">Wing Kinematics Mode</div>
    <div class="grid">
      <button onclick="sendState(0)">🌙 Sleep (Rest)</button>
      <button onclick="sendState(1)">🫁 Breathe</button>
      <button onclick="sendState(2)">🦋 Flutter</button>
      <button onclick="sendState(3)">⚡ Dynamic Flight</button>
      <button onclick="sendState(4)" class="special">💥 Startled Burst</button>
      <button onclick="sendState(5)">🍃 Glide</button>
    </div>
  </div>

  <div class="card">
    <div style="font-size: 14px; font-weight: bold; margin-bottom: 8px;">PCB Wing LED Patterns</div>
    <div class="grid">
      <button onclick="sendPattern(0)">🌊 Bioluminescence</button>
      <button onclick="sendPattern(1)">💎 Morpho Blue</button>
      <button onclick="sendPattern(2)">🔥 Monarch Ember</button>
      <button onclick="sendPattern(3)">🌌 Cyber Aurora</button>
    </div>
  </div>

  <div class="card">
    <div class="slider-box">
      <label>Flapping Speed: <span id="speedVal" class="badge">1.5 Hz</span></label>
      <input type="range" min="0.2" max="3.5" step="0.1" value="1.5" onchange="sendSpeed(this.value)" oninput="document.getElementById('speedVal').innerText=this.value+' Hz'">
    </div>
  </div>

  <script>
    function sendState(s) { fetch('/set_state?mode=' + s); }
    function sendPattern(p) { fetch('/set_pattern?mode=' + p); }
    function sendSpeed(sp) { fetch('/set_speed?hz=' + sp); }
  </script>
</body>
</html>
)rawliteral";
    _server.send(200, "text/html", html);
}

void WebDashboard::handleSetState() {
    if (_server.hasArg("mode")) {
        int m = _server.arg("mode").toInt();
        _kinematics.setState((KinematicState)m);
    }
    _server.send(200, "text/plain", "OK");
}

void WebDashboard::handleSetPattern() {
    if (_server.hasArg("mode")) {
        int p = _server.arg("mode").toInt();
        _ledEffects.setPattern((LEDPattern)p);
    }
    _server.send(200, "text/plain", "OK");
}

void WebDashboard::handleSetSpeed() {
    if (_server.hasArg("hz")) {
        float hz = _server.arg("hz").toFloat();
        _kinematics.setParameters(hz, 25.0f, 45.0f);
    }
    _server.send(200, "text/plain", "OK");
}

void WebDashboard::handleStatus() {
    String json = "{";
    json += "\"state\":" + String(_kinematics.getState()) + ",";
    json += "\"left_angle\":" + String(_kinematics.getLeftAngle()) + ",";
    json += "\"right_angle\":" + String(_kinematics.getRightAngle());
    json += "}";
    _server.send(200, "application/json", json);
}
