import os
import subprocess
import re
import sqlite3
import time
import threading
import hashlib
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import List, Dict
import requests

app = FastAPI(
    title="Divine Earthly - Krishi Veda Core v3.0",
    description="Unified AGI Node: RAG Memory, Ayurvedic C++, P2P Mesh, & Voice",
    version="3.0.0"
)

DB_PATH = "krishi_veda.db"
UI_PATH = "dashboard.html"

# --- PYDANTIC CONTRACTS ---
class QueryRequest(BaseModel):
    prompt: str
    max_tokens: int = 64

class SensorTelemetry(BaseModel):
    temperature: float
    moisture: float
    humidity: float
    ph: float

class IdentityRequest(BaseModel):
    name: str
    pin: str

class MeshSyncPayload(BaseModel):
    advisories: List[Dict]
    sensors: List[Dict]

# --- CORE DATABASE INIT (WITH RAG & IDENTITY) ---
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS advisories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            prompt TEXT NOT NULL,
            advice TEXT NOT NULL,
            dosha_context TEXT,
            p_dharma INTEGER, p_artha REAL, p_kama INTEGER
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sensors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            temperature REAL NOT NULL, moisture REAL NOT NULL, humidity REAL NOT NULL, ph REAL NOT NULL
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS shabda_pramana (
            keyword TEXT PRIMARY KEY, factual_context TEXT NOT NULL
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sovereign_identities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            pin_hash TEXT NOT NULL,
            mesh_clearance_level INTEGER DEFAULT 1
        )
    """)
    # NEW: The RAG Structural Memory Vault
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS rag_memory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            dosha_trigger TEXT NOT NULL,
            successful_strategy TEXT NOT NULL,
            success_score INTEGER DEFAULT 1
        )
    """)
    
    cursor.executemany("""
        INSERT OR IGNORE INTO shabda_pramana (keyword, factual_context) VALUES (?, ?)
    """, [
        ("silchar", "Context: Silchar lies in the high-humidity alluvial basin of the Barak River Valley. Crops require monsoonal flood-resilient protocols."),
        ("barak", "Context: The Barak Valley consists of Cachar, Karimganj, and Hailakandi. Characterized by clay-loam plains and acidic undulating hillocks (tillash).")
    ])
    conn.commit(); conn.close()

# --- SOVEREIGN SECURITY & HARDWARE INTERFACES ---
def hash_pin(pin: str) -> str:
    return hashlib.sha256(pin.encode()).hexdigest()

def trigger_voice_alert(message: str, lang="en-IN"):
    """Fires native Termux TTS using regional Indian linguistics."""
    print(f"[🗣️] Voice Core Routing: {message}")
    try:
        # Defaults to Indian English accent, switchable to 'bn-IN' or 'hi-IN'
        subprocess.run(['termux-tts-speak', '-l', lang, message], check=False)
    except Exception as e:
        print(f"[!] Voice Engine Intercept: {e}")

def run_ayurvedic_cpp_kernel(temp: float, moisture: float, ph: float) -> str:
    """Invokes the optimized C++ Urdhva Tiryakbhyam logic."""
    if not os.path.exists('./veda_accelerator'): return "TRIDOSHIC BALANCE"
    try:
        result = subprocess.run(
            ['./veda_accelerator', str(temp), str(moisture), str(ph)],
            capture_output=True, text=True, timeout=2
        )
        return result.stdout.strip()
    except Exception:
        return "TRIDOSHIC BALANCE"

# --- AUTONOMOUS LEARNING (RAG MEMORY) ---
def get_rag_context(dosha: str) -> str:
    """Retrieves the highest-scoring successful strategy for a specific Dosha imbalance."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT successful_strategy FROM rag_memory WHERE dosha_trigger = ? ORDER BY success_score DESC LIMIT 1", (dosha,))
    row = cursor.fetchone()
    conn.close()
    if row: return f"[RAG Memory Protocol: Previously successful local strategy -> {row[0]}]"
    return ""

def inject_shabda_pramana(prompt: str) -> str:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT keyword, factual_context FROM shabda_pramana")
    rows = cursor.fetchall()
    conn.close()
    
    injected_context = ""
    for row in rows:
        if row[0] in prompt.lower(): injected_context += row[1] + " "
    if injected_context: return f"[Truth Vectors: {injected_context.strip()}] {prompt}"
    return prompt

# --- 2-BIT VEDIC INFERENCE ENGINE ---
def run_local_slm_inference(prompt_text: str, max_tokens: int):
    is_termux = os.path.exists('/data/data/com.termux')
    binary_path = os.path.expanduser("~/llama-b9297/llama-cli") if is_termux else "/home/codespace/llama_source/build/bin/llama-cli"
    model_path = os.path.expanduser("~/vedic_model_q2.gguf") if is_termux else "test_model.gguf"
    lib_dir = os.path.expanduser("~/llama-b9297") if is_termux else "/home/codespace/llama_source/build/bin"

    MARKER = "__SOLM_RESPONSE__"
    execution_prompt = f"{prompt_text}\n{MARKER}\n"

    env = os.environ.copy()
    env['LD_LIBRARY_PATH'] = f"{lib_dir}:{env.get('LD_LIBRARY_PATH', '')}"
    cmd = [binary_path, "-m", model_path, "-p", execution_prompt, "-n", str(max_tokens), "-st", "-t", "2", "-c", "128", "--mmap"]
    
    try:
        res = subprocess.run(cmd, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=env, preexec_fn=os.setsid, timeout=120)
        raw_data = res.stdout if res.stdout else ""
        
        if MARKER in raw_data: clean_text = raw_data.split(MARKER)[-1]
        else: clean_text = raw_data.split(prompt_text)[-1] if prompt_text in raw_data else raw_data

        noise_patterns = [
            r"build\s*:\s*\S+\s+\S+", r"model\s*:\s*\S+", r"modalities\s*:\s*\S+",
            r"available\s+commands:.*?(?=To\s+implement|Active|System|$)", r"read\s+<file>",
            r"add\s+a\s+text\s+file", r"glob\s+<pattern>", r"text\s+files\s+using\s+globbing\s+pattern",
            r"ctrl\+c\s+stop\s+or\s+exit\s+regen", r"regenerate\s+the\s+last\s+response\s+clear", r"loading\s+model.*?(?=\n|$)"
        ]
        for pattern in noise_patterns: clean_text = re.sub(pattern, "", clean_text, flags=re.IGNORECASE | re.DOTALL)
        clean_text = re.sub(r'[\u2580-\u259F]+', '', clean_text)
        clean_text = re.sub(r'[\x08\s|\\/-]+', ' ', clean_text).strip()
        clean_text = re.sub(r'^>\s*', '', clean_text).strip()
        
        return clean_text if clean_text and len(clean_text) > 5 else "Active Matrix Sequence Engaged: Maintaining local protective frameworks."
    except Exception as e: return f"[!] Engine Error: {e}"

# --- RTA-DHARMA BACKGROUND LEARNING DAEMON ---
def rta_dharma_observer_loop():
    print("[⚡] Autonomous RAG Learning Daemon Online...")
    alert_cooldown = 0
    last_action_dosha = None
    last_action_advice = None
    
    while True:
        time.sleep(10)
        if alert_cooldown > 0:
            alert_cooldown -= 10
            continue
            
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("SELECT temperature, moisture, humidity, ph FROM sensors ORDER BY id DESC LIMIT 1")
            last_record = cursor.fetchone()
            
            if last_record:
                temp, moisture, humidity, ph = last_record
                dosha = run_ayurvedic_cpp_kernel(temp, moisture, ph)
                
                # Structural Learning: Did the previous strategy fix the moisture issue?
                if moisture > 40.0 and last_action_dosha:
                    print(f"🧠 [LEARNING EVENT] Moisture recovered. Logging strategy for {last_action_dosha} as successful.")
                    cursor.execute("INSERT OR IGNORE INTO rag_memory (dosha_trigger, successful_strategy) VALUES (?, ?)", (last_action_dosha, last_action_advice))
                    cursor.execute("UPDATE rag_memory SET success_score = success_score + 1 WHERE dosha_trigger = ? AND successful_strategy = ?", (last_action_dosha, last_action_advice))
                    conn.commit()
                    last_action_dosha = None
                
                # Threshold Breach Trigger
                elif moisture < 40.0 and ("IMBALANCE" in dosha or "TOXICITY" in dosha):
                    print(f"[🚨] Boundary Breach: {dosha}. Processing RAG Matrix...")
                    trigger_voice_alert(f"Warning. {dosha.split('.')[0]}", lang="en-IN")
                    
                    t_bg_start = time.time()
                    rag_context = get_rag_context(dosha)
                    automated_prompt = f"System alert. Moisture is {moisture}%. {rag_context} Formulate recovery strategy:"
                    
                    enriched_prompt = inject_shabda_pramana(automated_prompt)
                    raw_advice = run_local_slm_inference(enriched_prompt, max_tokens=64)
                    
                    if not raw_advice.startswith("[!]"):
                        bg_latency = time.time() - t_bg_start
                        cursor.execute(
                            "INSERT INTO advisories (prompt, advice, dosha_context, p_dharma, p_artha, p_kama) VALUES (?, ?, ?, ?, ?, ?)",
                            ("🚨 AUTOMATED THRESHOLD ALERT", raw_advice + " (Autonomous Execution)", dosha, 1, bg_latency, 1)
                        )
                        conn.commit()
                        
                        # Store context to verify success later
                        last_action_dosha = dosha
                        last_action_advice = raw_advice
                        alert_cooldown = 180 
            conn.close()
        except Exception as e: print(f"Observer Intercept: {e}")

@app.on_event("startup")
def startup_event():
    init_db()
    t = threading.Thread(target=rta_dharma_observer_loop, daemon=True)
    t.start()

# --- FASTAPI ENDPOINTS ---
@app.post("/api/v1/auth/register")
def register_sovereign_identity(auth: IdentityRequest):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO sovereign_identities (name, pin_hash) VALUES (?, ?)", (auth.name.lower(), hash_pin(auth.pin)))
        conn.commit()
        return {"success": True, "message": f"Cryptographic identity secured for {auth.name}."}
    except sqlite3.IntegrityError:
        return {"success": False, "message": "Identity already exists."}
    finally: conn.close()

@app.post("/api/v1/sensors")
def ingest_sensor_metrics(data: SensorTelemetry):
    conn = sqlite3.connect(DB_PATH)
    conn.cursor().execute("INSERT INTO sensors (temperature, moisture, humidity, ph) VALUES (?, ?, ?, ?)",
        (data.temperature, data.moisture, data.humidity, data.ph))
    conn.commit(); conn.close()
    return {"success": True, "message": "Telemetry logged."}

@app.post("/api/v1/advisory")
def generate_agricultural_advisory(request: QueryRequest):
    t_start = time.time()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT temperature, moisture, humidity, ph FROM sensors ORDER BY id DESC LIMIT 1")
    last_sensor = cursor.fetchone()
    
    dosha = "TRIDOSHIC BALANCE"
    if last_sensor:
        dosha = run_ayurvedic_cpp_kernel(last_sensor[0], last_sensor[1], last_sensor[2])
    
    rag_context = get_rag_context(dosha)
    combined_prompt = f"[{dosha}] {rag_context} {request.prompt}"
    enriched_prompt = inject_shabda_pramana(combined_prompt)
    
    raw_advice = run_local_slm_inference(enriched_prompt, request.max_tokens)
    execution_time = time.time() - t_start
    
    cursor.execute("INSERT INTO advisories (prompt, advice, dosha_context, p_dharma, p_artha, p_kama) VALUES (?, ?, ?, ?, ?, ?)",
        (request.prompt, raw_advice, dosha, 1, execution_time, 1))
    conn.commit(); conn.close()
    
    return {"success": True, "ayurvedic_state": dosha, "advice": raw_advice}

@app.get("/api/v1/history")
def get_advisory_history():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, timestamp, prompt, advice, p_artha FROM advisories ORDER BY id DESC LIMIT 5")
    rows = cursor.fetchall()
    conn.close()
    return {"history": [{"id": r[0], "time": r[1], "prompt": r[2], "advice": r[3], "latency": f"{r[4]:.4f}s"} for r in rows]}

@app.get("/api/v1/sensors")
def get_sensor_history():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, timestamp, temperature, moisture, humidity, ph FROM sensors ORDER BY id DESC LIMIT 5")
    rows = cursor.fetchall()
    conn.close()
    return {"telemetry": [{"id": r[0], "time": r[1], "temp": r[2], "moist": r[3], "humid": r[4], "ph": r[5]} for r in rows]}

# --- 🌐 P2P MESH INTERNET-FREE EXCHANGE LAYERS ---
@app.get("/api/v1/mesh/export")
def export_mesh_data_packets():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT timestamp, prompt, advice FROM advisories ORDER BY id DESC LIMIT 50")
    adv_rows = cursor.fetchall()
    cursor.execute("SELECT timestamp, temperature, moisture, humidity, ph FROM sensors ORDER BY id DESC LIMIT 50")
    sens_rows = cursor.fetchall()
    conn.close()
    return {
        "advisories": [{"time": r[0], "prompt": r[1], "advice": r[2]} for r in adv_rows],
        "sensors": [{"time": r[0], "temp": r[1], "moist": r[2], "humid": r[3], "ph": r[4]} for r in sens_rows]
    }

@app.post("/api/v1/mesh/sync")
def integrate_peer_mesh_packet(payload: MeshSyncPayload):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    for s in payload.sensors:
        cursor.execute("INSERT OR IGNORE INTO sensors (timestamp, temperature, moisture, humidity, ph) SELECT ?, ?, ?, ?, ? WHERE NOT EXISTS (SELECT 1 FROM sensors WHERE timestamp = ? AND moisture = ?)", (s['time'], s['temp'], s['moist'], s['humid'], s['ph'], s['time'], s['moist']))
    for a in payload.advisories:
        cursor.execute("INSERT OR IGNORE INTO advisories (timestamp, prompt, advice, p_dharma, p_artha, p_kama) SELECT ?, ?, ?, 1, 0.0, 1 WHERE NOT EXISTS (SELECT 1 FROM advisories WHERE timestamp = ? AND prompt = ?)", (a['time'], a['prompt'], a['advice'], a['time'], a['prompt']))
    conn.commit(); conn.close()
    return {"success": True, "status": "Mesh convergence aligned."}
