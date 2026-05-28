"""
Krishi-Veda Auto-Update — Checks GitHub for new APK versions.
Runs silently on app startup. Dharma-compliant: no tracking.
"""
import requests
import json

CURRENT_VERSION = "2.0.0"
CHECK_URL = "https://api.github.com/repos/divineearthly/Krishi-Veda-Module/releases?per_page=1"

def check_for_update():
    """Returns update info dict if newer version exists, else None."""
    try:
        resp = requests.get(CHECK_URL, timeout=10)
        latest = resp.json()[0]
        tag = latest.get("tag_name", "")
        
        # Skip if same version
        if CURRENT_VERSION in tag:
            return None
        
        # Find APK download URL
        for asset in latest.get("assets", []):
            if asset["name"].endswith(".apk"):
                return {
                    "version": tag,
                    "url": asset["browser_download_url"],
                    "size_mb": round(asset["size"] / 1024 / 1024, 1),
                    "name": latest.get("name", "Update")
                }
    except:
        pass
    return None

def apply_update_and_restart(zip_path):
    """Extract update zip and restart the app server."""
    import zipfile
    import os
    
    target_dir = "/sdcard/DivineEarthly/krishi_veda/"
    os.makedirs(target_dir, exist_ok=True)
    
    with zipfile.ZipFile(zip_path, 'r') as zf:
        zf.extractall(target_dir)
    
    # Signal the server to restart with new code
    restart_flag = os.path.join(target_dir, ".restart")
    with open(restart_flag, 'w') as f:
        f.write("1")
    
    return True
