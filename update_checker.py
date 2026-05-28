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
