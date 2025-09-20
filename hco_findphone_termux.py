#!/usr/bin/env python3
"""
HCO-FindPhone (Single-file Termux-ready Lost-Phone Helper server)
File: hco_findphone_termux.py
Usage (Termux):
  pkg install python
  pip install flask
  python3 hco_findphone_termux.py

What it provides:
 - /register  (POST JSON: {"device_id":"<id>","name":"My Phone"}) -> returns token
 - /beacon    (POST JSON: {"lat":..,"lon":..}) with header Authorization: Bearer <token>
 - /dashboard (GET) simple web UI showing devices + last known location (links to Google Maps)
 - /beacons/<device_id> (GET) returns JSON history for a device (for debugging)
 - Database: lostphone.db (SQLite)

Security notes:
 - This is a starter prototype. For production use add HTTPS, stronger auth, rate-limiting,
   input validation, token rotation, and other hardening.
 - Use only on devices you own and with explicit consent. Do NOT use to track others.

Author: Hackers Colony — prototype by Azhar (for legitimate, ethical use only)
Tool name: HCO-FindPhone
"""

from flask import Flask, request, jsonify, g, render_template_string, redirect, url_for
import sqlite3, os, secrets, time
from datetime import datetime

# Config
DB_PATH = "hco_findphone.db"
APP_HOST = "0.0.0.0"
APP_PORT = 5000
BEACON_RETENTION = 10000  # keep recent rows cap (not enforced strictly here)

app = Flask(__name__)

# ---------- Database helpers ----------
def get_db():
    db = getattr(g, "_db", None)
    if db is None:
        db = sqlite3.connect(DB_PATH, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
        db.row_factory = sqlite3.Row
        g._db = db
    return db

def init_db():
    if not os.path.exists(DB_PATH):
        db = sqlite3.connect(DB_PATH)
        c = db.cursor()
        c.execute("""
            CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT
            );
        """)
        c.execute("""
            CREATE TABLE devices (
                id TEXT PRIMARY KEY,
                name TEXT,
                token TEXT,
                registered_at TEXT
            );
        """)
        c.execute("""
            CREATE TABLE beacons (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                device_id TEXT,
                lat REAL,
                lon REAL,
                ts TEXT,
                ip TEXT,
                wifi TEXT
            );
        """)
        db.commit()
        db.close()

@app.teardown_appcontext
def close_db(exc):
    db = getattr(g, "_db", None)
    if db is not None:
        db.close()

# ---------- Utility ----------
def generate_token():
    return secrets.token_hex(24)

def now_iso():
    return datetime.utcnow().isoformat()

def device_by_token(token):
    db = get_db()
    cur = db.execute("SELECT id, name FROM devices WHERE token = ?", (token,))
    row = cur.fetchone()
    return row

# ---------- Endpoints ----------
@app.route("/")
def index():
    return redirect(url_for("dashboard"))

@app.route("/register", methods=["POST"])
def register():
    """
    Register a device.
    JSON input: {"device_id":"<some-unique-id>","name":"My Phone"}
    Response: {"success":true,"token":"<token>"}
    """
    data = request.get_json(force=True, silent=True) or {}
    device_id = (data.get("device_id") or "").strip()
    name = (data.get("name") or "").strip() or "Unnamed"
    if not device_id:
        return jsonify(error="device_id required"), 400

    token = generate_token()
    db = get_db()
    db.execute("INSERT OR REPLACE INTO devices (id,name,token,registered_at) VALUES (?,?,?,?)",
               (device_id, name, token, now_iso()))
    db.commit()
    return jsonify(success=True, token=token, device_id=device_id)

@app.route("/beacon", methods=["POST"])
def beacon():
    """
    Send a beacon from the device.
    Header: Authorization: Bearer <token>
    JSON body: {"lat": xx.xxxx, "lon": yy.yyyy, "wifi": "SSID (optional)"}
    """
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        return jsonify(error="missing bearer token"), 401
    token = auth.split(" ",1)[1].strip()
    dev = device_by_token(token)
    if not dev:
        return jsonify(error="invalid token"), 403
    data = request.get_json(force=True, silent=True) or {}
    try:
        lat = float(data.get("lat"))
        lon = float(data.get("lon"))
    except Exception:
        return jsonify(error="lat and lon numeric required"), 400
    wifi = data.get("wifi")
    ip = request.remote_addr
    ts = now_iso()
    db = get_db()
    db.execute("INSERT INTO beacons (device_id,lat,lon,ts,ip,wifi) VALUES (?,?,?,?,?,?)",
               (dev["id"], lat, lon, ts, ip, wifi))
    db.commit()
    return jsonify(success=True, ts=ts)

@app.route("/beacons/<device_id>", methods=["GET"])
def beacons(device_id):
    # Return list of beacons (JSON) - for debugging
    db = get_db()
    cur = db.execute("SELECT id,lat,lon,ts,ip,wifi FROM beacons WHERE device_id=? ORDER BY id DESC LIMIT 200", (device_id,))
    rows = [dict(r) for r in cur.fetchall()]
    return jsonify(device_id=device_id, beacons=rows)

# ---------- Dashboard ----------
DASH_TEMPLATE = """
<!doctype html>
<title>HCO-FindPhone Dashboard</title>
<style>
body{font-family:Inter,Helvetica,Arial;margin:18px;background:#0b0b0c;color:#e9eef6}
.card{background:#0f1720;padding:12px;border-radius:8px;margin-bottom:12px;box-shadow:0 6px 18px rgba(0,0,0,0.6)}
h1{font-size:20px}
table{width:100%;border-collapse:collapse}
th,td{padding:8px;text-align:left;border-bottom:1px solid rgba(255,255,255,0.04)}
.small{font-size:12px;color:#9aa6b2}
a{color:#76c7ff;text-decoration:none}
.badge{display:inline-block;padding:4px 8px;border-radius:6px;background:#1f2937;color:#dbeafe;font-weight:600;font-size:12px}
</style>
<h1>HCO-FindPhone — Dashboard</h1>
<p class="small">Prototype server running at <strong>{{host}}:{{port}}</strong>. Use on your own devices only.</p>
<div class="card">
  <h3>Registered devices</h3>
  {% if devices %}
  <table>
    <tr><th>Device ID</th><th>Name</th><th>Registered</th><th>Last Beacon</th><th>Action</th></tr>
    {% for d in devices %}
      <tr>
        <td><code>{{d.id}}</code></td>
        <td>{{d.name}}</td>
        <td class="small">{{d.registered_at}}</td>
        <td>
          {% if d.last %}
            <div><span class="small">{{d.last.ts}}</span></div>
            <div>Lat: {{d.last.lat}} Lon: {{d.last.lon}}</div>
            <div class="small">IP: {{d.last.ip}} {% if d.last.wifi %} • WiFi: {{d.last.wifi}}{% endif %}</div>
            <div><a href="https://www.google.com/maps/search/?api=1&query={{d.last.lat}},{{d.last.lon}}" target="_blank">Open in Google Maps</a></div>
          {% else %}
            <span class="small">No beacons yet</span>
          {% endif %}
        </td>
        <td>
          <div class="small">Token: <code style="word-break:break-all">{{d.token[:12]}}…</code></div>
          <div style="margin-top:6px"><a href="/beacons/{{d.id}}">View history (JSON)</a></div>
        </td>
      </tr>
    {% endfor %}
  </table>
  {% else %}
    <div class="small">No devices registered yet. Use POST /register to add one.</div>
  {% endif %}
</div>

<div class="card small">
  <strong>Quick register example (use on device):</strong>
  <pre style="background:#071024;padding:10px;border-radius:6px;color:#bfeeff">
curl -X POST -H "Content-Type: application/json" -d '{"device_id":"myphone-01","name":"Azhar Phone"}' http://{{host}}:{{port}}/register
  </pre>
  <strong>Quick beacon example (use on device after you get token):</strong>
  <pre style="background:#071024;padding:10px;border-radius:6px;color:#bfeeff">
curl -X POST -H "Authorization: Bearer <TOKEN>" -H "Content-Type: application/json" \
  -d '{"lat":12.9716,"lon":77.5946,"wifi":"HomeWiFi"}' \
  http://{{host}}:{{port}}/beacon
  </pre>
</div>
"""

@app.route("/dashboard")
def dashboard():
    db = get_db()
    cur = db.execute("SELECT id,name,token,registered_at FROM devices ORDER BY registered_at DESC")
    devices = []
    for r in cur.fetchall():
        last = db.execute("SELECT lat,lon,ts,ip,wifi FROM beacons WHERE device_id=? ORDER BY id DESC LIMIT 1", (r["id"],)).fetchone()
        lastd = dict(last) if last else None
        devices.append({"id": r["id"], "name": r["name"], "token": r["token"], "registered_at": r["registered_at"], "last": lastd})
    return render_template_string(DASH_TEMPLATE, devices=devices, host=APP_HOST, port=APP_PORT)

# ---------- CLI / Run ----------
def print_banner():
    print("="*60)
    print("HCO-FindPhone (Termux-ready single-file server)")
    print(f"DB: {DB_PATH}")
    print("Endpoints:")
    print("  POST /register  -> register device (returns token)")
    print("  POST /beacon    -> send location (Authorization: Bearer <token>)")
    print("  GET  /dashboard -> web UI")
    print("  GET  /beacons/<device_id> -> JSON history")
    print("="*60)
    print("Legal: Use only on devices you own. Do NOT track others without consent.\n")

if __name__ == "__main__":
    init_db()
    print_banner()
    # Simple dev server. For Termux you can run: python3 hco_findphone_termux.py
    # To run detached in background in Termux:
    #   nohup python3 hco_findphone_termux.py &> hco.log &
    app.run(host=APP_HOST, port=APP_PORT, debug=False)
