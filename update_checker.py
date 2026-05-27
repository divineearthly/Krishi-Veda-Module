"""
Krishi-Veda Auto-Update Module
Checks GitHub Releases for new versions. Downloads and installs APK.
Dharma-compliant: no tracking, no telemetry, no forced updates.
"""
import requests
import json
import os

GITHUB_API = "https://api.github.com/repos/divineearthly/Krishi-Veda-Module/releases"
CURRENT_VERSION = "2.0.0"

def check_for_update():
    """Check if a newer version exists on GitHub Releases."""
    try:
        response = requests.get(GITHUB_API, timeout=10)
        releases = response.json()
        
        if not releases:
            return None
        
        latest = releases[0]
        latest_version = latest.get("tag_name", "").replace("nightly-", "")
        
        # Find APK asset
        apk_url = None
        apk_size = 0
        for asset in latest.get("assets", []):
            if asset["name"].endswith(".apk"):
                apk_url = asset["browser_download_url"]
                apk_size = asset["size"]
                break
        
        if apk_url and latest_version > CURRENT_VERSION:
            return {
                "version": latest_version,
                "url": apk_url,
                "size_mb": round(apk_size / 1024 / 1024, 1),
                "name": latest.get("name", "Krishi-Veda Update"),
                "body": latest.get("body", "")[:200]
            }
        
        return None
    except Exception:
        return None

def download_update(url, progress_callback=None):
    """Download the APK update. Returns local path."""
    import tempfile
    local_path = os.path.join(tempfile.gettempdir(), "krishi_veda_update.apk")
    
    response = requests.get(url, stream=True)
    total = int(response.headers.get('content-length', 0))
    downloaded = 0
    
    with open(local_path, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
            downloaded += len(chunk)
            if progress_callback and total:
                progress_callback(downloaded, total)
    
    return local_path
