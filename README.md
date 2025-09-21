HCO Find Phone 🔍📱

https://img.shields.io/badge/Python-3.x-blue?style=flat&logo=python
https://img.shields.io/badge/License-MIT-green?style=flat
https://img.shields.io/badge/Platform-Termux-orange?style=flat&logo=android

A powerful Termux-based phone tracking tool that creates a Cloudflare tunnel to receive live location data from target devices.

⚠️ IMPORTANT DISCLAIMER

HCO Find Phone is for educational purposes only. Use this tool ONLY on devices YOU OWN or have EXPLICIT PERMISSION to track. Unauthorized tracking is illegal and unethical. The developers are not responsible for any misuse of this tool.

📋 Features

· 🔒 Tool Lock System - Requires YouTube subscription to unlock
· ⏳ Countdown Timer - Before redirecting to YouTube channel
· 🌐 Cloudflare Tunnel - Automatic public URL generation
· 📍 Live Location Tracking - Real-time GPS coordinates in Termux
· 📱 QR Code Generator - Easy sharing with target device
· 🎯 Auto Permission Request - Automatically requests location access
· ✅ Single File Solution - No complex setup required

📥 Installation

1. Update Termux:
   ```bash
   pkg update && pkg upgrade -y
   ```
2. Install Python and dependencies:
   ```bash
   pkg install python wget -y
   ```
3. Install Python packages:
   ```bash
   pip install flask requests qrcode[pil]
   ```
4. Download the script:
   ```bash
   wget https://raw.githubusercontent.com/azhar/hco-find-phone/main/HCO_FindPhone.py
   ```
5. Make it executable:
   ```bash
   chmod +x HCO_FindPhone.py
   ```

🚀 Usage

1. Run the script:
   ```bash
   python HCO_FindPhone.py
   ```
2. Follow the unlock process:
   · Watch the countdown
   · Subscribe to the YouTube channel when redirected
   · Return to Termux and press ENTER
3. Share the generated link:
   · Send the Cloudflare URL to your target device
   · Or scan the QR code with the target device
4. Receive location data:
   · When target allows location access, coordinates will appear in Termux
   · Google Maps link will be generated automatically

🎯 How It Works

1. Tool Initialization: Script starts with a locked screen requiring YouTube subscription
2. Cloudflare Tunnel: Creates a secure public URL using cloudflared
3. Web Server: Flask server hosts the location request page
4. Location Access: Target device gets prompted for location permission
5. Data Transmission: Coordinates are sent to your Termux session
6. Live Updates: Continuous location updates displayed in real-time

📝 Code Overview

The script consists of several key components:

· Tool Lock System - Ensures users subscribe before using
· Dependency Installer - Automatically installs required packages
· Cloudflare Tunnel - Creates public accessible URL
· Flask Web Server - Hosts the location request page
· QR Code Generator - Creates scannable QR codes for easy sharing
· Location Handler - Processes and displays received coordinates

🔧 Technical Requirements

· Android device with Termux
· Python 3.x
· Internet connection
· Cloudflared (automatically installed)
· Flask, Requests, QRCode libraries

📊 Sample Output

When successfully running, you'll see:

```
╔══════════════════════════════════════════════════════╗
║                   🔒 TOOL LOCKED 🔒                  ║
║               HCO FIND PHONE BY AZHAR                ║
║         Subscribe @hackers_colony_tech 🔔            ║
╚══════════════════════════════════════════════════════╝

✅ Cloudflare tunnel established: https://xyz.trycloudflare.com
✅ LIVE LOCATION RECEIVED
Latitude: 22.533400
Longitude: 88.378963
Accuracy: 13.663 m
Maps: https://maps.google.com/?q=22.533400,88.378963
```

🛡️ Privacy & Security

· All location data is transmitted directly to your Termux session
· No data is stored on external servers
· Cloudflare tunnel provides HTTPS encryption
· Source code is transparent and auditable

⚠️ Troubleshooting

Common issues and solutions:

1. "Command not found" errors:
   ```bash
   pkg update && pkg upgrade
   ```
2. Python package installation fails:
   ```bash
   pip install --upgrade pip
   ```
3. Cloudflared not working:
   ```bash
   pkg install cloudflared -y
   ```
4. Location permission denied:
   · Ensure target device has location services enabled
   · Use HTTPS URL (Cloudflare provides this automatically)

📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

🙏 Credits

Developed by: Azhar
YouTube Channel: Hackers Colony Tech
Special Thanks: Cloudflare for tunneling service

💡 Quote

"With great power comes great responsibility. Use knowledge ethically."

---

🔔 Remember: Always get proper authorization before tracking any device. Respect privacy laws and individual rights.

📞 Support: For issues and questions, please open a GitHub issue or comment on the YouTube channel.

---

⭐ If you find this tool useful, please give it a star on GitHub!
