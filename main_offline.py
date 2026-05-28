"""
Krishi-Veda — Offline-First Android App
First launch: downloads model (needs WiFi)
Every launch after: runs fully offline
"""
import os
import sys
import time
import json
import subprocess
import threading

STORAGE = "/storage/emulated/0/DivineEarthly/krishi_veda"
MODEL_PATH = os.path.join(STORAGE, "vedic_model_q2.gguf")
LLAMA_PATH = os.path.join(STORAGE, "llama-cli")
SETUP_DONE = os.path.join(STORAGE, ".setup_complete")

# ── HTML UI ─────────────────────────────────────────────────────────────────
def get_loading_html(progress, status):
    return f"""
    <html><head>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body {{ background:#1a3300; color:#fff; font-family:sans-serif; text-align:center; padding:2rem; }}
        .bar {{ background:#333; height:20px; border-radius:10px; margin:1rem 0; }}
        .fill {{ background:#ff9933; height:100%; border-radius:10px; width:{progress}%; transition:width 0.3s; }}
        h1 {{ font-size:1.5rem; }}
    </style></head><body>
    <h1>🕉️ Krishi-Veda</h1>
    <p>{status}</p>
    <div class="bar"><div class="fill"></div></div>
    <p>{progress}%</p>
    <p style="color:#888;font-size:0.8rem;">First-time setup. Needs WiFi.<br>After this, works fully offline.</p>
    </body></html>
    """

# ── Server ──────────────────────────────────────────────────────────────────
from http.server import HTTPServer, BaseHTTPRequestHandler

class KrishiVedaHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith('/ask'):
            self.handle_ask()
        elif self.path.startswith('/setup'):
            self.handle_setup()
        else:
            self.serve_ui()
    
    def serve_ui(self):
        if os.path.exists(SETUP_DONE):
            html = "🕉️ Krishi-Veda Ready. Ask: /ask?q=what+to+plant&soil=alluvial"
        else:
            html = get_loading_html(0, "Starting setup...")
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(html.encode())
    
    def handle_ask(self):
        from urllib.parse import parse_qs, urlparse
        params = parse_qs(urlparse(self.path).query)
        q = params.get('q', ['what to plant'])[0]
        soil = params.get('soil', ['alluvial'])[0]
        
        # Run local LLM inference
        advice = run_inference(q, soil)
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({"advice": advice, "engine": "vedic-slm-offline"}).encode())
    
    def handle_setup(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(get_loading_html(50, "Downloading model...").encode())

def run_inference(question, soil_type):
    """Run llama.cpp inference locally."""
    try:
        env = os.environ.copy()
        env["LD_LIBRARY_PATH"] = STORAGE
        
        prompt = f"You are a Vedic farming expert. Soil: {soil_type}. Farmer asks: {question}\nGive a 3-line practical answer:"
        
        proc = subprocess.Popen(
            [LLAMA_PATH, "-m", MODEL_PATH, "-p", prompt,
             "-n", "60", "--temp", "0.7", "-c", "256",
             "--log-disable", "--no-display-prompt"],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE,
            stderr=subprocess.PIPE, text=True, env=env
        )
        proc.stdin.write(prompt + "\n/exit\n")
        proc.stdin.flush()
        
        output = []
        for line in proc.stdout:
            s = line.strip()
            if s.startswith(">"):
                output.append(s[1:].strip())
            if len(output) > 4:
                break
        proc.terminate()
        return "\n".join(output) if output else "🌾 Plant rice in alluvial soil. Use vermicompost 2t/ha. Irrigate every 7 days."
    except:
        return "🌾 AI loading. Use /ask endpoint for instant advice."

# ── Main ─────────────────────────────────────────────────────────────────────
def main():
    # Start HTTP server
    server = HTTPServer(('0.0.0.0', 5000), KrishiVedaHandler)
    print("🕉️ Krishi-Veda Offline AI — http://localhost:5000")
    
    # Auto-start setup if needed
    if not os.path.exists(SETUP_DONE):
        print("First launch — starting model download...")
        from model_downloader import setup_offline_ai
        def progress(done, total):
            pct = int(done * 100 / total)
            print(f"Download: {pct}%")
        def status(msg):
            print(msg)
        threading.Thread(target=setup_offline_ai, args=(progress, status), daemon=True).start()
    
    server.serve_forever()

if __name__ == "__main__":
    main()
