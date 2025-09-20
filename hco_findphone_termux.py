#!/usr/bin/env python3
"""
HCO-FindPhone — Simple Termux server + auto-tunnel
Single-file. Run in Termux. Shows live phone location and prints lat/lon in Termux console.

Usage (Termux):
  pkg install python openssh termux-api jq curl -y
  pip install flask
  python3 hco_findphone_simple_tunnel.py

What it does:
 - Uses `termux-location -j` to read GPS periodically (requires you to grant location permission).
 - Runs a Flask server on 0.0.0.0:5000 with:
     /device       -> map page showing latest location
     /last.json    -> latest location JSON {found,lat,lon,ts}
 - Attempts to create a public URL using ssh.localhost.run (reverse SSH).
   If successful it will print the public URL. Otherwise it'll print the LAN URL.
 - Prints updates (lat/lon/timestamp) to Termux console so you can monitor live.
 - Legal: Only track devices you own/are authorized to track.

Author: Hackers Colony (Azhar) — prototype. For ethical use only.
"""

import os, subprocess, threading, time, json, sqlite3, secrets, signal
from datetime import datetime
from flask import Flask, jsonify, render_template_string, request

# Config
DB = "hco_findphone_simple.db"
POLL_INTERVAL = 10      # seconds between GPS reads
FLASK_HOST = "0.0.0.0"
FLASK_PORT = 5000
USE_TUNNEL = True       # attempt ssh.localhost.run tunnel by default
DEVICE_ID = "termux-phone-1"

app = Flask(__name__)
_latest = {"found": False}   # in-memory latest location (also stored in sqlite)
ssh_proc = None

# --- DB (simple) ---
def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS beacons (
                 id INTEGER PRIMARY KEY AUTOINCREMENT,
                 lat REAL, lon REAL, ts TEXT)""")
    conn.commit()
    conn.close()

def save_beacon(lat, lon, ts):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("INSERT INTO beacons (lat,lon,ts) VALUES (?,?,?)",(lat,lon,ts))
    conn.commit()
    conn.close()

# --- Termux location reader ---
def read_termux_location():
    """
    Calls `termux-location -j` and parses the JSON output.
    Returns (lat, lon) or None on failure.
    """
    try:
        # termux-location -j returns JSON with "latitude" and "longitude"
        p = subprocess.run(["termux-location","-j"], capture_output=True, text=True, timeout=15)
        out = p.stdout.strip()
        if not out:
            return None
        j = json.loads(out)
        lat = j.get("latitude")
        lon = j.get("longitude")
        if lat is None or lon is None:
            return None
        return float(lat), float(lon)
    except Exception as e:
        return None

def poll_location_loop():
    global _latest
    print("[*] Starting location poll loop (interval {}s). Make sure Termux location permission is granted.".format(POLL_INTERVAL))
    while True:
        loc = read_termux_location()
        ts = datetime.utcnow().isoformat()
        if loc:
            lat, lon = loc
            _latest = {"found": True, "lat": lat, "lon": lon, "ts": ts}
            save_beacon(lat, lon, ts)
            print(f"[{ts}] LOCATION -> lat: {lat} lon: {lon}")
        else:
            # keep _latest as-is but print a warning
            print(f"[{ts}] WARNING -> termux-location failed or returned no GPS. Make sure permissions are granted.")
        time.sleep(POLL_INTERVAL)

# --- Try to start reverse SSH tunnel via ssh.localhost.run ---
def start_ssh_tunnel():
    """
    Uses ssh to create a reverse tunnel via ssh.localhost.run:
    ssh -o StrictHostKeyChecking=no -R 80:localhost:5000 ssh.localhost.run
    This service prints a line containing the public URL; we attempt to parse it.
    """
    global ssh_proc
    try:
        # check if ssh exists
        if not shutil_which("ssh"):
            print("[!] ssh not found. Install openssh: pkg install openssh")
            return None
        cmd = ["ssh","-o","StrictHostKeyChecking=no","-o","ExitOnForwardFailure=yes","-R","80:localhost:5000","ssh.localhost.run"]
        print("[*] Attempting to create public tunnel via ssh.localhost.run ...")
        # start process and capture output lines
        ssh_proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
        url = None
        start = time.time()
        # read lines until we find a forwarding URL or timeout
        while True:
            if ssh_proc.stdout is None:
                break
            line = ssh_proc.stdout.readline()
            if not line:
                # check if process ended
                if ssh_proc.poll() is not None:
                    break
                # else continue waiting
                time.sleep(0.1)
                if time.time() - start > 15:
                    break
                continue
            line = line.strip()
            # example output (may vary): "Forwarding HTTP traffic from https://abc123ssh.localhost.run"
            if "Forwarding HTTP traffic from" in line or "https://" in line:
                # attempt to extract https://... substring
                import re
                m = re.search(r"https?://[^\s]+", line)
                if m:
                    url = m.group(0)
                    break
            # some versions print: "serving on https://..."
            if "serving on" in line:
                import re
                m = re.search(r"https?://[^\s]+", line)
                if m:
                    url = m.group(0); break
            # safety timeout
            if time.time() - start > 20:
                break
        if url:
            print(f"[*] Public URL: {url}")
            return url
        else:
            print("[!] Could not detect public URL from ssh output. Tunnel may have failed or service changed.")
            return None
    except Exception as e:
        print("[!] SSH tunnel failed:", e)
        return None

# helper: shutil.which replacement (avoid extra import issues)
def shutil_which(name):
    for p in os.environ.get("PATH","").split(":"):
        f = os.path.join(p, name)
        if os.path.isfile(f) and os.access(f, os.X_OK):
            return f
    return None

# --- Flask endpoints ---
MAP_HTML = """
<!doctype html>
<html>
<head>
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>HCO-FindPhone Live</title>
  <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
  <style> html,body,#map{height:100%;margin:0;padding:0} body{font-family:Arial;background:#111;color:#eee} .info{position:absolute;z-index:600;left:8px;top:8px;background:#0008;padding:8px;border-radius:6px} a{color:#7fd1ff}</style>
</head>
<body>
  <div class="info"><strong>HCO-FindPhone</strong><br><span id="ts">—</span></div>
  <div id="map"></div>
  <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
  <script>
    const map = L.map('map').setView([20,0],2);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',{maxZoom:19}).addTo(map);
    let marker = null;
    async function refresh(){
      try{
        let r = await fetch('/last.json');
        let j = await r.json();
        if(!j.found){ document.getElementById('ts').innerText='No location yet'; return;}
        document.getElementById('ts').innerText = 'Last: '+j.ts+' • lat:'+j.lat+' lon:'+j.lon;
        const lat = parseFloat(j.lat), lon = parseFloat(j.lon);
        if(!isNaN(lat) && !isNaN(lon)){
          if(marker) marker.setLatLng([lat,lon]);
          else marker = L.marker([lat,lon]).addTo(map);
          map.setView([lat,lon],15);
        }
      }catch(e){ console.error(e); }
    }
    refresh();
    setInterval(refresh, 8000);
  </script>
</body>
</html>
"""

@app.route("/")
def index():
    # log the visit in Termux console
    print(f"[{datetime.utcnow().isoformat()}] WEB: / visited from {request.remote_addr}")
    return render_template_string(MAP_HTML)

@app.route("/last.json")
def last_json():
    return jsonify(_latest)

@app.route("/health")
def health():
    return jsonify(status="ok", device=DEVICE_ID)

# --- signal handling and cleanup ---
def cleanup_and_exit(signum, frame):
    print("[*] Exiting, cleaning up...")
    try:
        if ssh_proc and ssh_proc.poll() is None:
            ssh_proc.terminate()
    except:
        pass
    os._exit(0)

signal.signal(signal.SIGINT, cleanup_and_exit)
signal.signal(signal.SIGTERM, cleanup_and_exit)

# --- Main runner ---
def main():
    import threading
    init_db()

    # start background thread to poll location
    t = threading.Thread(target=poll_location_loop, daemon=True)
    t.start()

    public_url = None
    if USE_TUNNEL:
        # attempt to start ssh tunnel in a thread to avoid blocking
        def start_tunnel_thread():
            nonlocal public_url
            url = start_ssh_tunnel()
            if url:
                public_url = url
        th = threading.Thread(target=start_tunnel_thread, daemon=True)
        th.start()
        # give it a few seconds to come up
        time.sleep(3)

    # compute LAN URL
    lan_ip = get_local_ip() or "localhost"
    lan_url = f"http://{lan_ip}:{FLASK_PORT}"

    # print startup info
    print("="*60)
    print("HCO-FindPhone (simple) — running")
    print(f"Device ID: {DEVICE_ID}")
    if public_url:
        print(f"Public URL: {public_url}")
    else:
        print("Public URL: (not available)")
    print(f"LAN URL: {lan_url}")
    print("Open the public URL (or LAN URL if same WiFi) on another device to view live location.")
    print("Termux console will print lat/lon updates.")
    print("="*60)

    # run Flask (blocking)
    app.run(host=FLASK_HOST, port=FLASK_PORT, debug=False)

# --- helper to get local IP ---
def get_local_ip():
    # tries common interfaces
    import socket
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # doesn't have to connect; just used to get the OS-chosen source IP
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return None

if __name__ == "__main__":
    main()
