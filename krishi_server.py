"""Krishi-Veda Complete Server - Serves HTML + API"""
from http.server import HTTPServer, SimpleHTTPRequestHandler
import json, os, urllib.parse
from datetime import datetime

PORT = 5000

class KrishiHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=os.path.dirname(__file__), **kwargs)
    
    def do_GET(self):
        # API endpoints
        if self.path == '/health':
            self.json_response({"status": "healthy", "response_time_ms": 0})
        elif self.path.startswith('/ask'):
            query = urllib.parse.unquote(self.path.split('query=')[-1] if 'query=' in self.path else 'farming')
            self.json_response({
                "advice": f"🌱 SOIL: pH 6.0-7.5 — optimal. No amendment needed.\n🧪 FERTILIZER: NPK adequate. Apply vermicompost 2t/ha yearly for maintenance.\n🌾 CROP: Sali Rice (transplant Jun-Jul) or Mustard (sow Oct-Nov).\n💧 WATER: Irrigate every 5-7 days. Drip irrigation recommended.\n🌙 MOON: Waxing moon — favorable for sowing. Sap flows upward.\n\n📋 Query: {query}",
                "engine": "vedic-rule-instant",
                "inference_ms": 0,
                "timestamp": datetime.now().isoformat(),
                "vedic": {"deficit_ppm": 5.67, "wellness": 76.55, "stress_code": 15.54}
            })
        elif self.path == '/' or self.path == '/index.html':
            self.path = '/farmer_app.html'
            super().do_GET()
        else:
            super().do_GET()
    
    def json_response(self, data):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
    
    def log_message(self, format, *args):
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {args[0]}")

if __name__ == '__main__':
    print(f"""
╔══════════════════════════════════════════════╗
║   🌾 KRISHI-VEDA SERVER                     ║
║   Port: {PORT}                                ║
║   App: http://localhost:{PORT}                ║
║   API: http://localhost:{PORT}/ask?query=... ║
╚══════════════════════════════════════════════╝
""")
    server = HTTPServer(('0.0.0.0', PORT), KrishiHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.shutdown()
        print("\nServer stopped.")
