#!/usr/bin/env python3
"""KRISHI-VEDA LIVE SYSTEM DASHBOARD"""
import sqlite3, time, os, requests

db = sqlite3.connect('krishi_veda.db')

advisories = db.execute("SELECT COUNT(*) FROM advisories").fetchone()[0]
sensors = db.execute("SELECT COUNT(*) FROM sensors").fetchone()[0]
knowledge = db.execute("SELECT COUNT(*) FROM shabda_pramana").fetchone()[0]

last = db.execute("SELECT datetime(timestamp,'localtime'), substr(advice,1,60) FROM advisories ORDER BY id DESC LIMIT 1").fetchone()
last_s = db.execute("SELECT datetime(timestamp,'localtime'), temperature, moisture, ph FROM sensors ORDER BY id DESC LIMIT 1").fetchone()

try:
    health = requests.get("http://localhost:5000/health", timeout=2).json()
    api = health.get('status', '?')
except:
    api = 'down'

# Count models
import glob
models = len(glob.glob(os.path.expanduser('~/*.gguf'))) + len(glob.glob('/storage/emulated/0/*.gguf')) + len(glob.glob('/storage/emulated/0/Download/*.gguf'))

db.close()

print("""
╔══════════════════════════════════════════════════╗
║     🌾 KRISHI-VEDA LIVE SYSTEM DASHBOARD         ║
╠══════════════════════════════════════════════════╣
║  🟢 API: {:8}   📅 {}          ║
║  🤖 Models: {:3}   💾 Advisories: {:3}            ║
║  📡 Sensors: {:3}   📚 Knowledge: {:3}             ║
╠══════════════════════════════════════════════════╣""".format(api, time.strftime('%Y-%m-%d %H:%M'), models, advisories, sensors, knowledge))

if last:
    print("║  📋 Last: {}                  ║".format(last[0]))
    print("║  {}... ║".format(last[1][:55]))

if last_s:
    print("╠══════════════════════════════════════════════════╣")
    print("║  🌡️  Sensor: {}          ║".format(last_s[0]))
    print("║  Temp: {}°C | Moist: {}% | pH: {}                  ║".format(last_s[1], last_s[2], last_s[3]))

print("""╠══════════════════════════════════════════════════╣
║  📡 /health | /ask | /weather | /market-prices    ║
╚══════════════════════════════════════════════════╝""")
