#!/usr/bin/env python3
# HCO-FindPhone by Azhar
# GitHub-ready version

import os, time, json, threading, subprocess
from flask import Flask, jsonify, render_template_string
from datetime import datetime

app = Flask(__name__)

# HTML Dashboard
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
  <title>HCO-FindPhone — by Azhar</title>
  <style>
    body { background:#0d0d0d; color:#00ff99; font-family:monospace; text-align:center; }
    h1 { color:#ff4444; }
    .box { border:2px solid #00ff99; padding:20px; margin:20px; border-radius:15px; }
    iframe { width:100%; height:400px; border:none; border-radius:10px; }
  </style>
</head>
<body>
  <h1>📍 HCO-FindPhone</h1>
  <p>Code by Azhar | Hackers Colony</p>
  <div class="box">
    <h3>Last Known Location</h3>
    {% if lat and lon %}
      <p><b>Lat:</b> {{lat}}, <b>Lon:</b> {{lon}}</p>
      <iframe src="https://maps.google.com/maps?q={{lat}},{{lon}}&z=15&output=embed"></iframe>
    {% else %}
      <p>No location yet...</p>
    {% endif %}
    <p>Last Update: {{ts}}</p>
  </div>
</body>
</html>
"""

last_location = {"lat": None, "lon": None, "ts": None}

@app.route("/")
def dashboard():
    return render_template_string(HTML_TEMPLATE, **last_location)

@app.route("/last.json")
def last_json():
    return jsonify(last_location)

def update_location():
    while True:
        try:
            # Get GPS using termux-location
            result = subprocess.getoutput("termux-location -p gps -r once")
            data = json.loads(result)
            lat, lon = data["latitude"], data["longitude"]
            last_location.update({
                "lat": lat,
                "lon": lon,
                "ts": datetime.utcnow().isoformat()
            })
            print(f"[{last_location['ts']}] Location -> {lat}, {lon}")
        except Exception as e:
            print(f"⚠️ GPS Error: {e}")
        time.sleep(10)

if __name__ == "__main__":
    # Tool lock
    print("🔒 This tool is locked. Redirecting to YouTube in 8 seconds...")
    time.sleep(8)
    os.system("xdg-open https://youtube.com/@hackers_colony_tech")

    # Start GPS updater
    threading.Thread(target=update_location, daemon=True).start()

    # Start Cloudflared tunnel
    print("\n[+] Starting Cloudflare tunnel...")
    subprocess.Popen(["cloudflared", "tunnel", "--url", "http://localhost:5000", "--no-autoupdate"])
    print("[+] Opening server on :5000")

    app.run(host="0.0.0.0", port=5000)
