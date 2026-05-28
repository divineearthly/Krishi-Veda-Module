"""
Krishi-Veda Model Downloader
Downloads LLM model + inference engine on first launch.
After download, works fully offline forever.
"""
import os
import requests
import json

# Storage paths
STORAGE = "/storage/emulated/0/DivineEarthly/krishi_veda"
MODEL_PATH = os.path.join(STORAGE, "vedic_model_q2.gguf")
LLAMA_PATH = os.path.join(STORAGE, "llama-cli")
SETUP_DONE = os.path.join(STORAGE, ".setup_complete")

# Download URLs (GitHub Releases — free, no auth needed)
MODEL_URL = "https://github.com/divineearthly/Krishi-Veda-Module/releases/download/v2.0.0/vedic_model_q2.gguf"
LLAMA_URL = "https://github.com/divineearthly/Krishi-Veda-Module/releases/download/v2.0.0/llama-cli-arm64"
FALLBACK_MODEL = "https://huggingface.co/divinesouljoy/Vedic-Transformer-Core/resolve/main/vedic_model_q2.gguf"

def is_setup_complete():
    return os.path.exists(SETUP_DONE)

def get_download_size(url):
    try:
        r = requests.head(url, timeout=5)
        return int(r.headers.get('content-length', 0))
    except:
        return 0

def download_file(url, path, progress_callback=None):
    """Download with progress. Returns True on success."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    
    try:
        r = requests.get(url, stream=True, timeout=300)
        total = int(r.headers.get('content-length', 0))
        downloaded = 0
        
        with open(path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
                downloaded += len(chunk)
                if progress_callback and total > 0:
                    progress_callback(downloaded, total)
        
        return True
    except Exception as e:
        print(f"Download failed: {e}")
        return False

def setup_offline_ai(progress_callback=None, status_callback=None):
    """
    First-time setup. Downloads everything needed for offline AI.
    Call this when app launches for the first time with WiFi.
    """
    os.makedirs(STORAGE, exist_ok=True)
    
    # Step 1: Download LLM model (144MB)
    if status_callback:
        status_callback("Downloading Vedic AI model (144MB)...")
    
    model_ok = os.path.exists(MODEL_PATH)
    if not model_ok:
        model_ok = download_file(MODEL_URL, MODEL_PATH, progress_callback)
    if not model_ok:
        if status_callback:
            status_callback("Trying backup server...")
        model_ok = download_file(FALLBACK_MODEL, MODEL_PATH, progress_callback)
    
    if not model_ok:
        return False, "Model download failed. Connect to WiFi and try again."
    
    # Step 2: Download llama.cpp binary (5MB)
    if status_callback:
        status_callback("Installing inference engine...")
    
    if not os.path.exists(LLAMA_PATH):
        download_file(LLAMA_URL, LLAMA_PATH)
        os.chmod(LLAMA_PATH, 0o755)
    
    # Step 3: Mark setup complete
    with open(SETUP_DONE, 'w') as f:
        f.write('1')
    
    return True, "Ready! AI is now offline."

def get_model_path():
    """Get path to downloaded model."""
    if os.path.exists(MODEL_PATH):
        return MODEL_PATH
    return None

def get_llama_path():
    """Get path to llama binary."""
    if os.path.exists(LLAMA_PATH):
        return LLAMA_PATH
    return None
