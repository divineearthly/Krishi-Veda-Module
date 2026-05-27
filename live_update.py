"""
Krishi-Veda Live Update System
Checks GitHub for new kernels, models, and data — syncs to device.
Works with or without internet. Dharma-compliant (no tracking, no auth).
"""
import os
import json
import hashlib
import requests
from datetime import datetime

HOME = os.path.expanduser("~")
KV_DIR = os.path.join(HOME, "Krishi-Veda-Module")
CACHE_DIR = os.path.join(HOME, ".krishi_veda")
UPDATE_URL = "https://raw.githubusercontent.com/divineearthly/Krishi-Veda-Module/main/updates.json"

os.makedirs(CACHE_DIR, exist_ok=True)


def check_internet():
    """Check if internet is available — silently fail if offline."""
    try:
        requests.get("https://github.com", timeout=3)
        return True
    except:
        return False


def get_local_version():
    """Read current version from local cache."""
    version_file = os.path.join(CACHE_DIR, "version.json")
    if os.path.exists(version_file):
        with open(version_file) as f:
            return json.load(f)
    return {"kernel_version": "0.0.0", "model_version": "0.0.0", 
            "data_version": "0.0.0", "last_check": None}


def check_updates():
    """Check GitHub for updates. Returns list of available updates."""
    if not check_internet():
        return {"status": "offline", "updates": []}
    
    local = get_local_version()
    
    try:
        remote = requests.get(UPDATE_URL, timeout=5).json()
    except:
        return {"status": "error", "updates": []}
    
    updates = []
    
    # Check kernel updates
    if remote.get("kernel_version", "0.0.0") > local["kernel_version"]:
        updates.append({
            "type": "kernel",
            "name": "Vedic Kernels",
            "current": local["kernel_version"],
            "latest": remote["kernel_version"],
            "size_mb": remote.get("kernel_size_mb", 5),
            "description": remote.get("kernel_changes", "Improved Vedic algorithms")
        })
    
    # Check model updates
    if remote.get("model_version", "0.0.0") > local["model_version"]:
        updates.append({
            "type": "model",
            "name": "AI Model",
            "current": local["model_version"],
            "latest": remote["model_version"],
            "size_mb": remote.get("model_size_mb", 144),
            "description": remote.get("model_changes", "Better agricultural knowledge")
        })
    
    # Check data updates (market prices, crop data)
    if remote.get("data_version", "0.0.0") > local["data_version"]:
        updates.append({
            "type": "data",
            "name": "Market & Crop Data",
            "current": local["data_version"],
            "latest": remote["data_version"],
            "size_mb": remote.get("data_size_mb", 2),
            "description": "Updated MSP prices and crop calendar"
        })
    
    return {"status": "online", "updates": updates, "last_check": datetime.now().isoformat()}


def apply_update(update_type):
    """Download and apply a specific update."""
    if not check_internet():
        return {"status": "offline", "message": "No internet. Try when connected."}
    
    update_map = {
        "kernel": {
            "url": f"{UPDATE_URL.replace('updates.json', '')}kernels/vedic_kernels.so",
            "path": os.path.join(KV_DIR, "vedic_engine/kernels/vedic_kernels.so")
        },
        "data": {
            "url": f"{UPDATE_URL.replace('updates.json', '')}data/market_prices.json",
            "path": os.path.join(CACHE_DIR, "market_prices.json")
        }
    }
    
    if update_type not in update_map:
        return {"status": "error", "message": f"Unknown update type: {update_type}"}
    
    info = update_map[update_type]
    
    try:
        response = requests.get(info["url"], timeout=30)
        os.makedirs(os.path.dirname(info["path"]), exist_ok=True)
        with open(info["path"], "wb") as f:
            f.write(response.content)
        
        # Update version tracking
        local = get_local_version()
        remote = requests.get(UPDATE_URL, timeout=5).json()
        local[f"{update_type}_version"] = remote.get(f"{update_type}_version", "0.0.0")
        local["last_check"] = datetime.now().isoformat()
        
        with open(os.path.join(CACHE_DIR, "version.json"), "w") as f:
            json.dump(local, f)
        
        return {"status": "success", "message": f"{update_type} updated successfully"}
    
    except Exception as e:
        return {"status": "error", "message": str(e)}


def get_system_info():
    """Get current system status for display."""
    local = get_local_version()
    
    return {
        "app_version": "2.0.0",
        "kernel_version": local["kernel_version"],
        "model_version": local["model_version"],
        "data_version": local["data_version"],
        "last_update_check": local.get("last_check", "Never"),
        "internet_available": check_internet(),
        "offline_mode": not check_internet(),
        "models_available": [
            f for f in os.listdir(HOME) if f.endswith(".gguf")
        ]
    }


# ── Auto-update on startup ───────────────────────────────────────────────
def startup_check():
    """Run on app launch. Checks for critical updates silently."""
    status = check_updates()
    if status["status"] == "online":
        for update in status.get("updates", []):
            if update["type"] in ["kernel", "data"]:  # Auto-apply small updates
                result = apply_update(update["type"])
                print(f"Auto-update {update['type']}: {result['status']}")
    return status


if __name__ == "__main__":
    # Test the update system
    print("System Info:", json.dumps(get_system_info(), indent=2))
    print("\nChecking updates...")
    print(json.dumps(check_updates(), indent=2))
