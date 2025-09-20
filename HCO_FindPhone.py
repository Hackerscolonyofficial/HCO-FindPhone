# HCO Find Phone Server by Azhar
# Fully automatic live GPS tracking
import os
import threading
import time
from flask import Flask, request, render_template_string

RED = "\033[91m"
GREEN = "\033[92m"
CYAN = "\033[96m"
CLEAR = "\033[2J\033[H"

app = Flask(__name__)
locations = {}

# -------------------- Web dashboard --------------------
dashboard_template = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>HCO Find Phone by Azhar</title>
<style>
body { background: black; color: red; text-align: center; font-family: Arial; }
h1 { font-size: 50px; margin-top: 50px; }
p { font-size: 25px; }
</style>
</head>
<body>
<h1>HCO FIND PHONE BY AZHAR</h1>
<p>Send this link to the device to track location:</p>
<p style="color:green;">{{ link }}</p>
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
setInterval(updateLocation, 3000);
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

# -------------------- Start Flask server --------------------
def start_server():
    import logging
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)
    app.run(host='0.0.0.0', port=5000)

# -------------------- Tool Lock + Countdown + YouTube --------------------
def tool_lock_and_youtube():
    os.system(CLEAR)
    print(f"{RED}{'='*80}")
    print(f"{RED}{'🔒 TOOL LOCKED 🔒'.center(80)}")
    print(f"{RED}{'Subscribe & click the BELL icon on YouTube 🔔'.center(80)}")
    print(f"{RED}{'='*80}")
    print("\n")
    for i in range(9,0,-1):
        print(f"{CYAN}{str(i).center(80)}")
        time.sleep(1)
    youtube_url = "https://youtube.com/@hackers_colony_tech?si=pvdCWZggTIuGb0ya"
    try:
        import subprocess
        subprocess.run(["am","start","-a","android.intent.action.VIEW","-d",youtube_url])
    except:
        print(f"Open YouTube manually: {youtube_url}")
    input("\nPress ENTER after returning from YouTube...")

# -------------------- Main --------------------
if __name__ == "__main__":
    cloudflare_link = input("Paste your Cloudflare public URL here: ")
    tool_lock_and_youtube()
    threading.Thread(target=start_server, daemon=True).start()
    print(f"\n{GREEN}Dashboard running! Open this in browser to view live updates:{cloudflare_link}{GREEN}")
    while True:
        if locations:
            print(f"{GREEN}LIVE LOCATION → Lat: {locations.get('lat')} , Lon: {locations.get('lon')}{GREEN}")
        time.sleep(3)
