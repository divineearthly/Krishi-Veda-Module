# Simple file-based cache for offline use
import json, os, time

CACHE_DIR = os.path.expanduser("~/.cache/krishi_veda")
os.makedirs(CACHE_DIR, exist_ok=True)

def get_cache(key):
    fpath = os.path.join(CACHE_DIR, key + ".json")
    if os.path.exists(fpath):
        with open(fpath) as f:
            data = json.load(f)
        if time.time() - data.get("ts", 0) < 86400:
            return data.get("val")
    return None

def set_cache(key, value):
    fpath = os.path.join(CACHE_DIR, key + ".json")
    with open(fpath, "w") as f:
        json.dump({"ts": time.time(), "val": value}, f)
