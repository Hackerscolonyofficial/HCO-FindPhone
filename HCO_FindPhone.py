# HCO Find Phone by Azhar - Fully Automatic Termux Version
# Requirements: Termux, Python3, Flask, cloudflared, Termux:API

import os, subprocess, threading, time, re
from flask import Flask, request, render_template_string

RED = "\033[91m"
GREEN = "\033[92m"
CYAN = "\033[96m"
CLEAR = "\033[2J\033[H"

locations = {}
app = Flask(__name__)

# ---------------- Flask routes -----------------
dashboard_template = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>HCO Find Phone by Azhar</title>
<style>
body { background:black; color:red; text-align:center; font-family:Arial; }
h1 { font-size:50px; margin-top:50px; }
p { font-size:25px; color:green; }
</style>
</head>
<body>
<h1>HCO FIND PHONE BY AZHAR</h1>
<p>Send this link to the device to track location:</p>
<p>{{ link }}</p>
<p id="location">Waiting for live location updates...</p>

<script>
function updateLocation() {
    fetch('/location')
    .then(response => response.json())
    .then(data => {
        if(data.lat && data.lon){
            document.getElementById('location').innerHTML = 'LIVE LOCATION → Lat: ' + data.lat + ', Lon: ' + data.lon;
        }
    });
}
setInterval(updateLocation,3000);
</script>
</body>
</html>
"""

@app.route('/')
def dashboard():
    return render_template_string(dashboard_template, link=cloudflare_link)

@app.route('/location')
def get_location():
    return locations if locations else {}

@app.route('/update', methods=['POST'])
def update_location():
    data = request.json
    if data and 'lat' in data and 'lon' in data:
        locations['lat'] = data['lat']
        locations['lon'] = data['lon']
        return "OK"
    return "Invalid Data"

def start_server():
    import logging
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)
    app.run(host='0.0.0.0', port=5000)

# ---------------- Tool lock + countdown + YouTube -----------------
def tool_lock_youtube():
    os.system(CLEAR)
    print(f"{RED}{'='*80}")
    print(f"{RED}{'🔒 TOOL LOCKED 🔒'.center(80)}")
    print(f"{RED}{'Subscribe & click the BELL icon on YouTube 🔔'.center(80)}")
    print(f"{RED}{'='*80}{RED}\n")
    print(f"{CYAN}{'Redirecting in:'.center(80)}{CYAN}\n")
    for i in range(9,0,-1):
        print(f"{CYAN}{str(i).center(80)}")
        time.sleep(1)
    youtube_url="https://youtube.com/@hackers_colony_tech?si=pvdCWZggTIuGb0ya"
    try:
        subprocess.run(["am","start","-a","android.intent.action.VIEW","-d",youtube_url])
    except:
        print(f"Open YouTube manually: {youtube_url}")
    input("\nPress ENTER after returning from YouTube...")

# ---------------- Start cloudflared tunnel and capture URL -----------------
def start_cloudflared():
    global cloudflare_link
    # Start cloudflared process
    process = subprocess.Popen(["cloudflared","tunnel","--url","http://127.0.0.1:5000"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    cloudflare_link = None
    # Parse output for public URL
    for line in process.stdout:
        if "https://" in line:
            match = re.search(r"(https://[^\s]+)", line)
            if match:
                cloudflare_link = match.group(1)
                break
    if not cloudflare_link:
        cloudflare_link = input("Enter Cloudflare URL manually: ")

# ---------------- Main -----------------
if __name__=="__main__":
    # Start Flask server
    threading.Thread(target=start_server, daemon=True).start()
    # Start Cloudflare tunnel and capture public URL
    threading.Thread(target=start_cloudflared, daemon=True).start()
    time.sleep(5)  # Wait for Cloudflare to initialize
    # Tool lock + countdown + YouTube
    tool_lock_youtube()
    # Dashboard display
    if cloudflare_link:
        os.system(CLEAR)
        print(f"{RED}{'='*80}")
        print(f"{RED}{'HCO FIND PHONE BY AZHAR'.center(80)}")
        print(f"{RED}{'='*80}{RED}\n")
        print(f"{GREEN}{'Send this link to the phone to track location:'.center(80)}{GREEN}\n")
        print(f"{GREEN}{cloudflare_link.center(80)}{GREEN}\n")
        print(f"{CYAN}{'Waiting for live location updates...'.center(80)}{CYAN}\n")
    # Live location printing in Termux
    while True:
        if locations:
            print(f"{GREEN}LIVE LOCATION → Lat: {locations.get('lat')} , Lon: {locations.get('lon')}{GREEN}")
        time.sleep(3)
