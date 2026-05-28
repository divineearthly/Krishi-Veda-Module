"""
Krishi-Veda Android App
Opens the live Hugging Face API in the phone browser.
No local server needed — works instantly.
"""
import android
from android.permissions import request_permissions, Permission
import webbrowser
import time

print("🕉️ Krishi-Veda starting...")

# Request network permission
try:
    request_permissions([Permission.INTERNET])
except:
    pass

# Wait briefly then open the live API
time.sleep(2)
webbrowser.open("https://divinesouljoy-krishi-veda-api.hf.space")

print("Dashboard opened in browser.")
print("If nothing appears, go to: krishi-veda-api.hf.space")

# Keep the app alive
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("Closed.")
