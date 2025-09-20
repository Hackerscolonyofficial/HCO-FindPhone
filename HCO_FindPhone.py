# HCO Find Phone by Azhar
# GitHub-ready Termux tool
# -------------------------------------------
# Ethical use only. Only track devices you own or have permission for.

import os
import threading
import time
import json
import subprocess
from flask import Flask, request
import webbrowser

# --------------------------- Terminal Colors ----------------------------
RED = "\033[91m"
GREEN = "\033[92m"
RESET = "\033[0m"
CLEAR = "\033[2J\033[H"

# --------------------------- Flask Server -------------------------------
app = Flask(__name__)
locations = {}

@app.route('/update', methods=['POST'])
def update_location():
    data = request.json
    if data and 'lat' in data and 'lon' in data:
        locations['lat'] = data['lat']
        locations['lon'] = data['lon']
        return "Location Updated"
    return "Invalid Data"

@app.route('/')
def show_location():
    if 'lat' in locations and 'lon' in locations:
        return f"Live Location: Latitude {locations['lat']}, Longitude {locations['lon']}"
    return "Waiting for device location..."

def start_server():
    app.run(host='127.0.0.1', port=5000)

# ------------------------ Cloudflare Tunnel -----------------------------
def start_tunnel():
    # Start cloudflared tunnel automatically
    print(f"{GREEN}Starting Cloudflare Tunnel...{RESET}")
    tunnel_process = subprocess.Popen(
        ["cloudflared", "tunnel", "--url", "http://127.0.0.1:5000"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    # Wait a few seconds for tunnel to generate
    time.sleep(5)
    # Get tunnel URL
    result = subprocess.run(
        ["cloudflared", "tunnel", "list", "--output", "json"],
        stdout=subprocess.PIPE
    )
    try:
        tunnels = json.loads(result.stdout)
        if len(tunnels) > 0:
            url = tunnels[0]['TunnelURL']
            return url
    except Exception:
        pass
    return "CLOUDFLARE_LINK_NOT_FOUND"

# ------------------------ Tool Lock & YouTube Redirect -----------------
def lock_tool():
    print(f"{RED}\n🔒 Tool is locked! To unlock, subscribe and click the bell 🔔{RESET}")
    for i in range(9, 0, -1):
        print(f"{GREEN}{i}{RESET}...", end='', flush=True)
        time.sleep(1)
    print("\nOpening YouTube...")
    webbrowser.open("https://youtube.com/@hackers_colony_tech?si=pvdCWZggTIuGb0ya")
    input("\nPress Enter after returning from YouTube...")

# --------------------------- Display Dashboard --------------------------
def show_dashboard(cloudflare_link):
    os.system(CLEAR)
    print(f"{RED}\n\n\n\n{'HCO Find Phone by Azhar'.center(80)}{RESET}\n")
    print(f"{GREEN}{'Send this link to the phone to track location:'.center(80)}{RESET}\n")
    print(f"{GREEN}{cloudflare_link.center(80)}{RESET}\n")

# --------------------------- Main Execution -----------------------------
if __name__ == "__main__":
    # Start Flask server in background
    threading.Thread(target=start_server, daemon=True).start()

    # Show tool lock & YouTube redirect
    lock_tool()

    # Start Cloudflare tunnel and get live link
    link = start_tunnel()
    if link == "CLOUDFLARE_LINK_NOT_FOUND":
        print(f"{RED}Error: Could not start Cloudflare tunnel. Make sure cloudflared is installed.{RESET}")
        exit()

    # Show dashboard with live link
    show_dashboard(link)

    # Display live location updates
    print(f"{GREEN}Waiting for live location updates...{RESET}")
    while True:
        if 'lat' in locations and 'lon' in locations:
            print(f"{GREEN}Live Location → Lat: {locations['lat']}, Lon: {locations['lon']}{RESET}")
        time.sleep(3)
