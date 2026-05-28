"""
Krishi-Veda Android App — Starts server + opens browser
"""
import os
import sys
import time
import threading
import webbrowser

# Add backend path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("🕉️ Krishi-Veda starting...")
print("Starting API server on port 5000...")

def start_server():
    from app import app
    app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False)

# Start server in background
server_thread = threading.Thread(target=start_server, daemon=True)
server_thread.start()
time.sleep(3)

# Auto-open the dashboard in browser
print("Opening farmer dashboard...")
webbrowser.open("http://localhost:5000")

print("=" * 50)
print("🌾 Krishi-Veda Ready")
print("http://localhost:5000")
print("=" * 50)

# Keep alive
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("Server stopped.")
