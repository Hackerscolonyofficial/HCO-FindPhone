# HCO Find Phone 🔍📱

[![YouTube](https://img.shields.io/badge/YouTube-Hackers_Colony_red)](https://youtube.com/@hackers_colony_tech?si=pvdCWZggTIuGb0ya)
[![Python](https://img.shields.io/badge/Python-3.x-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

---

## Description

**HCO Find Phone** by Azhar is a Termux-based educational tool for **tracking the location of your own devices**.  
It generates a **Cloudflare tunnel link** that you can open on your phone. When the phone allows location access, your **live GPS coordinates** are displayed in Termux.  

> ⚠️ **Disclaimer:** Only use on devices you own or have permission to track. Unauthorized tracking is illegal.

---

## Features

- 🔒 **Tool Lock & YouTube Redirect:** The tool is locked. Unlock by subscribing and clicking the bell icon on YouTube.  
- ⏳ **Countdown Timer:** Countdown before redirecting to YouTube.  
- 🖥️ **Dashboard:** Displays **HCO Find Phone by Azhar** in large red letters.  
- 🌐 **Cloudflare Tunnel:** Generates a public link to receive location data.  
- 📍 **Live Location:** Displays target phone location live in Termux.  
- ✅ **Single Python File:** No messy setup; all code in one file.  

---

## Requirements

- **Termux** on Android  
- **Python 3.x**  
- **Flask** Python package  
- **Cloudflared** for public URL tunneling  

---

## Installation

Open Termux and run the following commands:

```bash
pkg update && pkg upgrade
pkg install python -y
pip install flask
pkg install cloudflared -y


---

Usage

1. Save the script as HCO_FindPhone.py.


2. Run in Termux:



python HCO_FindPhone.py

3. Tool behavior:


```
🔒 Shows tool lock message and countdown.

Opens YouTube app for unlock.

After returning, displays HCO Find Phone by Azhar in big red letters.

Shows a Cloudflare link to send to your target phone.

Target opens link → browser asks permission → location sent to Termux dashboard.

Live location updates appear automatically in Termux.



---

Notes

Make sure your cloudflared tunnel is running properly.

Replace YOUR_CLOUDFLARE_LINK in the script if you use manual tunnels.

Ethical use only. Do not attempt to track someone without consent.



---

Screenshots

[Optional: Add screenshots of Termux running HCO Find Phone]


---

License

This project is licensed under the MIT License.
You can view the license file here.


---

Credits

Code by: Azhar

Hackers Colony Official



---

Quote

> "Knowledge is power, hacking is skill."
