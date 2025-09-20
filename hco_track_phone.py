# HCO Track Phone by Azhar - Fixed Version
# Simple and Working!

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
    print(f"\n{CYAN}Opening YouTube in 3 seconds...{RESET}")
    time.sleep(3)
    
    try:
        subprocess.run(["am", "start", "-a", "android.intent.action.VIEW", 
                       "-d", "https://youtube.com/@hackers_colony_tech"],
                      stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except:
        pass
    
    input(f"\n{YELLOW}Press ENTER to continue...{RESET}")

# Get correct local IP
def get_local_ip():
    try:
        # Connect to Google DNS to find our actual IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        try:
            # Alternative method
            hostname = socket.gethostname()
            return socket.gethostbyname(hostname)
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

# Flask routes - FIXED VERSION
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
                color: lime; 
                text-align: center; 
                font-family: Arial; 
                padding: 20px;
                margin: 0;
            }
            .container { 
                max-width: 100%%; 
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
            button { 
                background: lime; 
                color: black; 
                border: none; 
                padding: 20px 40px; 
                border-radius: 10px; 
                font-size: 20px; 
                font-weight: bold; 
                margin: 20px 0; 
                cursor: pointer;
            }
            #status {
                padding: 15px;
                margin: 15px 0;
                border-radius: 5px;
                background: #222;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="logo">HCO TRACK PHONE BY AZHAR</div>
            <p>Click the button below to share your location</p>
            <button onclick="shareLocation()">📡 SHARE LOCATION</button>
            <div id="status">Click the button above to share your location</div>
            <p><small>Make sure to allow location permissions when prompted</small></p>
        </div>
        
        <script>
        function shareLocation() {
            var status = document.getElementById('status');
            status.innerHTML = 'Requesting location access...';
            status.style.color = 'yellow';
            
            if (!navigator.geolocation) {
                status.innerHTML = 'Geolocation is not supported by your browser';
                status.style.color = 'red';
                return;
            }
            
            function success(position) {
                var lat = position.coords.latitude;
                var lon = position.coords.longitude;
                var acc = position.coords.accuracy;
                
                // Send to server
                fetch('/update', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        lat: lat,
                        lon: lon,
                        accuracy: acc
                    })
                })
                .then(response => response.text())
                .then(data => {
                    status.innerHTML = '✅ Location sent successfully!';
                    status.style.color = 'lime';
                })
                .catch(error => {
                    status.innerHTML = '❌ Error sending location';
                    status.style.color = 'red';
                });
            }
            
            function error(err) {
                status.innerHTML = '❌ Please allow location access to continue';
                status.style.color = 'red';
                console.error('Geolocation error:', err);
            }
            
            var options = {
                enableHighAccuracy: true,
                timeout: 10000,
                maximumAge: 0
            };
            
            navigator.geolocation.getCurrentPosition(success, error, options);
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
        return "ERROR: Invalid data"
    except Exception as e:
        print(f"{RED}Error processing location: {e}{RESET}")
        return "ERROR"

def start_server(port):
    from werkzeug.serving import make_server
    server = make_server('0.0.0.0', port, app, threaded=True)
    server.serve_forever()

# Generate QR code
def make_qr(url):
    try:
        import qrcode
        qr = qrcode.QRCode(
            version=4,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=6,
            border=4,
        )
        qr.add_data(url)
        qr.make(fit=True)
        img = qr.make_image(fill_color="red", back_color="white")
        qr_path = "/data/data/com.termux/files/home/track_qr.png"
        img.save(qr_path)
        
        # Try to open the QR code
        try:
            subprocess.run(["termux-open", qr_path],
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except:
            pass
            
        return True
    except Exception as e:
        print(f"{YELLOW}⚠️  QR code generation failed: {e}{RESET}")
        return False

# Install requirements
def install_requirements():
    try:
        import flask
        import qrcode
        import requests
        return True
    except ImportError:
        print(f"{YELLOW}Installing required packages...{RESET}")
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "flask", "qrcode[pil]", "requests"],
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=120)
            return True
        except:
            print(f"{RED}Failed to install packages automatically{RESET}")
            print(f"{YELLOW}Please run: pip install flask qrcode[pil] requests{RESET}")
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
        return
    
    # Get correct IP and port
    local_ip = get_local_ip()
    port = find_port()
    TRACKING_URL = f"http://{local_ip}:{port}"
    
    print(f"{GREEN}✅ Server starting on: {local_ip}:{port}{RESET}")
    
    # Start server in thread
    server_thread = threading.Thread(target=start_server, args=(port,), daemon=True)
    server_thread.start()
    
    time.sleep(2)  # Wait for server to start
    
    # Generate QR code
    print(f"{YELLOW}📱 Generating QR code...{RESET}")
    make_qr(TRACKING_URL)
    
    # Show banner
    print(f"\n{RED}{'═'*60}{RESET}")
    print(f"{RED}{'HCO TRACK PHONE BY AZHAR'.center(60)}{RESET}")
    print(f"{RED}{'═'*60}{RESET}")
    print(f"\n{GREEN}📱 Send this link to target phone:{RESET}")
    print(f"{CYAN}{TRACKING_URL}{RESET}")
    print(f"\n{YELLOW}📍 OR scan the QR code that opened{RESET}")
    print(f"\n{BLUE}💡 Make sure both phones are on same WiFi network{RESET}")
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
        print(f"{YELLOW}Try installing requirements manually:{RESET}")
        print(f"{CYAN}pkg install python{RESET}")
        print(f"{CYAN}pip install flask qrcode[pil] requests{RESET}")
