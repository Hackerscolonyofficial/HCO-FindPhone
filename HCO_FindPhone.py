# HCO Find Phone by Azhar
# Termux-ready, clean, professional
# -------------------------------------------
# Ethical use only. Track only devices you own or have permission for.

import os
import threading
import time
from flask import Flask, request

# --------------------------- Terminal Colors ----------------------------
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
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
    # Start Flask server silently (suppress debug/log messages)
    import logging
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)
    app.run(host='0.0.0.0', port=5000)

# --------------------------- Tool Lock & Countdown ----------------------
def tool_lock():
    os.system(CLEAR)
    print(f"{RED}{'='*80}")
    print(f"{RED}{'🔒 TOOL LOCKED 🔒'.center(80)}")
    print(f"{RED}{'Subscribe & click the BELL icon on YouTube 🔔'.center(80)}")
    print(f"{RED}{'='*80}{RESET}\n")
    print(f"{YELLOW}{'Redirecting in:'.center(80)}{RESET}\n")
    
    for i in range(9, 0, -1):
        print(f"{CYAN}{str(i).center(80)}{RESET}")
        time.sleep(1)
    
    print(f"\n{GREEN}{'OPEN THIS LINK IN YOUTUBE APP ON YOUR PHONE:'.center(80)}{RESET}")
    print(f"{GREEN}{'https://youtube.com/@hackers_colony_tech?si=pvdCWZggTIuGb0ya'.center(80)}{RESET}\n")
    input(f"{YELLOW}{'Press ENTER after returning from YouTube...'.center(80)}{RESET}")

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
    # First: show lock screen + countdown + YouTube instruction
    tool_lock()
    
    # Ask user for Cloudflare URL
    print(f"{YELLOW}{'NOTE: Start your Cloudflare tunnel manually in another Termux session:'.center(80)}{RESET}")
    print(f"{CYAN}{'cloudflared tunnel --url http://127.0.0.1:5000'.center(80)}{RESET}\n")
    cloudflare_link = input(f"{GREEN}{'Enter your Cloudflare public URL here: '.center(80)}{RESET}")

    # Show dashboard
    show_dashboard(cloudflare_link)

    # Start Flask server in background
    threading.Thread(target=start_server, daemon=True).start()

    # Live location updates
    while True:
        if 'lat' in locations and 'lon' in locations:
            print(f"{GREEN}{'LIVE LOCATION → Lat: ' + str(locations['lat']) + ', Lon: ' + str(locations['lon'])}{RESET}")
        time.sleep(3)
