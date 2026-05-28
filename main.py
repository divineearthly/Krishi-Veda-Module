"""
Krishi-Veda Android Launcher
Opens the live API in phone browser.
"""
import webbrowser
import threading
import time

print("🕉️ Krishi-Veda starting...")

# Open the live API
def open_dashboard():
    time.sleep(1)
    webbrowser.open("https://divinesouljoy-krishi-veda-api.hf.space")

threading.Thread(target=open_dashboard, daemon=True).start()

# Keep alive
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("Closed.")
