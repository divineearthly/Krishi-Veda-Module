import sys
import os
import time
import json
import requests

# Install pyserial locally if missing: pip install pyserial
try:
    import serial
except ImportError:
    print("[!] Python serial library missing. Running auto-installer...")
    os.system("pip install pyserial")
    import serial

# Termux standard USB-to-UART bridge paths are typically /dev/ttyACM0 or /dev/ttyUSB0
SERIAL_PORT = "/dev/ttyACM0" 
BAUD_RATE = 115200
API_ENDPOINT = "http://127.0.0.1:8080/api/v1/sensors"

print("🔌 INITIALIZING HARDWARE TELEMETRY BRIDGE NODE...")

# Symmetrical fallback simulation if no physical MCU is plugged into the device USB port
try:
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=2)
    print(f"✅ Physical link bound successfully at {SERIAL_PORT}")
except Exception as e:
    print(f"[!] Physical Serial Hardware not detected ({e}). Entering high-fidelity sensor simulation matrix...")
    ser = None

while True:
    time.sleep(4)
    try:
        if ser and ser.in_waiting > 0:
            raw_line = ser.readline().decode('utf-8', errors='ignore').strip()
            # Expecting MCU JSON format: {"temp": 30.2, "moist": 35.4, "humid": 65.0, "ph": 6.4}
            packet = json.loads(raw_line)
        else:
            # High-fidelity field simulation loop for physical layer validation
            import random
            packet = {
                "temp": round(random.uniform(28.0, 34.0), 1),
                "moist": round(random.uniform(22.0, 45.0), 1),
                "humid": round(random.uniform(60.0, 80.0), 1),
                "ph": round(random.uniform(5.8, 6.8), 2)
            }
            print(f"🎲 Simulated Field Packet Generated: {packet}")

        # Map internal JSON coordinates to the FastAPI pydantic contract layout
        payload = {
            "temperature": packet["temp"],
            "moisture": packet["moist"],
            "humidity": packet["humid"],
            "ph": packet["ph"]
        }

        response = requests.post(API_ENDPOINT, json=payload, timeout=2)
        if response.status_code == 200:
            print(f"🛰️ Telemetry successfully routed to core ledger database storage layer.")
        else:
            print(f"[!] Server Pipeline Rejection Token: {response.status_code}")

    except Exception as e:
        print(f"[!] Telemetry Bridging Stream Intercept Exception: {e}")
