"""
Krishi-Veda Android Main Activity
Launches the API server + opens the farmer interface.
"""
import os
import sys
import time
import threading
from http.server import HTTPServer, SimpleHTTPRequestHandler

# ── Update Check ──────────────────────────────────────────────────────────
print("🕉️ Krishi-Veda starting...")
print("Checking for updates...")
try:
    from live_update import startup_check, get_system_info
    status = startup_check()
    info = get_system_info()
    print(f"Kernels: {info['kernel_version']} | Model: {info['model_version']}")
    print(f"Offline mode: {info['offline_mode']}")
except Exception as e:
    print(f"Update check skipped: {e}")

# ── Start API Server ─────────────────────────────────────────────────────
print("\nStarting API server on port 5000...")

def start_api():
    """Start Flask API in background thread."""
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, ".")
    from app import app
    app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False)

api_thread = threading.Thread(target=start_api, daemon=True)
api_thread.start()
time.sleep(2)

# ── Open Farmer Interface ─────────────────────────────────────────────────
print("\n" + "=" * 50)
print("  🌾 KRISHI-VEDA — Sovereign AI Farm Advisor")
print("  http://localhost:5000")
print("=" * 50)
print("\n📱 Open your browser to: http://localhost:5000")
print("🌾 Or ask: http://localhost:5000/ask?q=what+to+plant")
print("\nPress Ctrl+C to stop.\n")

# Keep the app alive
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("\n🕉️ Om Shanti. Server stopped.")
