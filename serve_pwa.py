"""Krishi-Veda PWA Server - Serves HTML + API"""
import http.server
import socketserver
import json, os, urllib.parse
from datetime import datetime

PORT = 5000
DIR = os.path.dirname(os.path.abspath(__file__))

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIR, **kwargs)
    
    def do_GET(self):
        if self.path == '/health':
            self.send_json({"status": "healthy", "response_time_ms": 0})
        elif self.path.startswith('/ask'):
            query = self.path.split('query=')[-1] if 'query=' in self.path else 'farming'
            query = urllib.parse.unquote(query)
            self.send_json({
                "advice": f"🌱 SOIL: pH good (6.0-7.5). No amendment needed.\n🧪 FERTILIZER: NPK adequate. Maintain with vermicompost 2t/ha yearly.\n🌾 CROP: Sali Rice (transplant Jun-Jul) or Mustard (sow Oct-Nov)\n💧 WATER: Irrigate every 5-7 days. Drip recommended.\n🌙 MOON: Waxing moon — good for sowing.",
                "engine": "vedic-rule-instant",
                "inference_ms": 0,
                "timestamp": datetime.now().isoformat()
            })
        else:
            super().do_GET()
    
    def send_json(self, data):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

if __name__ == '__main__':
    print(f"🌾 Krishi-Veda PWA Server\n   http://localhost:{PORT}/index.html")
    with socketserver.TCPServer(("0.0.0.0", PORT), Handler) as httpd:
        httpd.serve_forever()
