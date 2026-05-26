import subprocess
import json
import sqlite3
import time
import requests

DB_PATH = "krishi_veda.db"

def init_macro_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS macro_telemetry (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            latitude REAL,
            longitude REAL,
            api_source TEXT,
            air_temp REAL,
            precipitation REAL,
            satellite_soil_temp REAL,
            satellite_soil_moisture REAL
        )
    """)
    conn.commit()
    conn.close()

def get_hardware_gps():
    print("[🛰️] Pinging Android Hardware Layer for Spatial Coordinates...")
    
    try:
        print(" ├── Attempting fast Network lock...")
        result = subprocess.run(['termux-location', '-p', 'network', '-r', 'last'], capture_output=True, text=True, timeout=8)
        if result.stdout.strip():
            location_data = json.loads(result.stdout)
            print(" ├── [OK] Hardware Lock Established.")
            return location_data.get('latitude'), location_data.get('longitude')
    except Exception:
        print(" ├── [!] Hardware timeout detected.")
        
    print(" ├── [⚙️] OVERRIDE: Hardware bypassed. Engaging Sovereign Anchor (Silchar, Assam).")
    # Exact coordinates for the Barak Valley / Silchar region
    return 24.8333, 92.7789

def fetch_open_meteo_api(lat, lon):
    print(f"☁️ Engaging Keyless Open-Meteo Agricultural API for Coordinates: [{lat}, {lon}]")
    
    # Fully open, keyless endpoint requesting atmospheric and soil-level data
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,precipitation,soil_temperature_0cm,soil_moisture_0_to_7cm"
    
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            current = data.get('current', {})
            return {
                "air_temp": current.get('temperature_2m', 0.0),
                "precipitation": current.get('precipitation', 0.0),
                "soil_temp": current.get('soil_temperature_0cm', 0.0),
                "soil_moisture": current.get('soil_moisture_0_to_7cm', 0.0)
            }
        else:
            print(f"[!] API Rejection: {response.status_code}")
            return None
    except Exception as e:
        print(f"[!] Network sync failed (Offline Mode Active). Error: {e}")
        return None

def log_macro_telemetry(lat, lon, api_data):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO macro_telemetry (latitude, longitude, api_source, air_temp, precipitation, satellite_soil_temp, satellite_soil_moisture)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (lat, lon, "Open-Meteo Open Data", api_data['air_temp'], api_data['precipitation'], api_data['soil_temp'], api_data['soil_moisture']))
    conn.commit()
    conn.close()
    
    print("\n✅ Macro-Environment Vector Successfully Cached to Local SQLite Vault:")
    print(f"   Air Temp: {api_data['air_temp']}°C | Soil Temp: {api_data['soil_temp']}°C | Sat. Moisture: {api_data['soil_moisture']}m³/m³")

if __name__ == "__main__":
    init_macro_db()
    
    # 1. Acquire Coordinates (Hardware or Fallback)
    lat, lon = get_hardware_gps()
    
    # 2. Fetch Open Agricultural Data
    if lat and lon:
        api_data = fetch_open_meteo_api(lat, lon)
        
        # 3. Log to Sovereign SQLite Database
        if api_data:
            log_macro_telemetry(lat, lon, api_data)
