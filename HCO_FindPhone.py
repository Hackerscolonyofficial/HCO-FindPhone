# HCO Find Phone by Azhar
# Fully automatic Termux version
# -------------------------------------------
# Requirements:
# - Termux
# - Python 3
# - Flask (pip install flask)
# - Cloudflared (pkg install cloudflared)
# - Termux:API (pkg install termux-api)

import os
import threading
import time
import subprocess
from flask import Flask, request

# --------------------------- Colors ----------------------------
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
RESET = "\033[0m"
CLEAR = "\033[2J\033[H"

# --------------------------- Flask ----------------------------
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
    import logging
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)
    app.run(host='0.0.0.0', port=5000)

# --------------------------- Lock & YouTube ---------------------
def tool_lock_and_youtube():
    os.system(CLEAR)
    print(f"{RED}{'='*80}")
    print(f"{RED}{'🔒 TOOL LOCKED 🔒'.center(80)}")
    print(f"{RED}{'Subscribe & click the BELL icon on YouTube 🔔'.center(80)}")
    print(f"{RED}{'='*80}{RESET}\n")
    print(f"{YELLOW}{'Redirecting in:'.center(80)}{RESET}\n")
    
    for i in range(9,0,-1):
        print(f"{CYAN}{str(i).center(80)}{RESET}")
        time.sleep(1)
    
    # Open YouTube app automatically using Termux intent
    youtube_url = "https://youtube.com/@hackers_colony_tech?si=pvdCWZggTIuGb0ya"
    subprocess.run(["am", "start", "-a", "android.intent.action.VIEW", "-d", youtube_url])
    
    input(f"\n{YELLOW}{'Press ENTER after returning from YouTube...'.center(80)}{RESET}")

# --------------------------- Cloudflare Tunnel -------------------
def start_cloudflare():
    # Run cloudflared in background
    process = subprocess.Popen(
        ["cloudflared", "tunnel", "--url", "http://127.0.0.1:5000"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )
    url = ""
    # Wait for the public URL in stdout
    while True:
        line = process.stdout.readline()
        if "trycloudflare.com" in line or "trycloudflare.com" in line.lower():
            url = line.strip().split()[-1]
            break
    return url

# --------------------------- Dashboard --------------------------
def show_dashboard(cloudflare_link):
    os.system(CLEAR)
    print(f"{RED}{'='*80}")
    print(f"{RED}{'HCO FIND PHONE BY AZHAR'.center(80)}")
    print(f"{RED}{'='*80}{RESET}\n")
    print(f"{GREEN}{'Send this link to the phone to track location:'.center(80)}{RESET}\n")
    print(f"{GREEN}{cloudflare_link.center(80)}{RESET}\n")
    print(f"{CYAN}{'Waiting for live location updates...'.center(80)}{RESET}\n")

# --------------------------- Main --------------------------
if __name__ == "__main__":
    # Lock message + YouTube redirect
    tool_lock_and_youtube()
    
    # Start Flask server in background
    threading.Thread(target=start_server, daemon=True).start()
    
    # Start Cloudflare tunnel automatically
    print(f"{YELLOW}{'Starting Cloudflare tunnel...'.center(80)}{RESET}")
    cloudflare_link = start_cloudflare()
    
    # Show dashboard with big red title + link
    show_dashboard(cloudflare_link)
    
    # Live location updates
    while True:
        if 'lat' in locations and 'lon' in locations:
            print(f"{GREEN}{'LIVE LOCATION → Lat: ' + str(locations['lat']) + ', Lon: ' + str(locations['lon'])}{RESET}")
        time.sleep(3)
