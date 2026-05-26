import os
import subprocess
import re
import sqlite3
import time
import threading
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import List, Dict

app = FastAPI(
    title="Divine Earthly - Krishi Veda Core Matrix",
    description="Sovereign Edge Node: Bound Shabda Pramana & Unified Daemon Guardrails",
    version="2.3.1"
)

DB_PATH = "krishi_veda.db"
UI_PATH = "dashboard.html"

class QueryRequest(BaseModel):
    prompt: str
    max_tokens: int = 64

class SensorTelemetry(BaseModel):
    temperature: float
    moisture: float
    humidity: float
    ph: float

# --- DATABASE ENGINE & SCHEMAS ---
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS advisories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            prompt TEXT NOT NULL,
            advice TEXT NOT NULL,
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
        CREATE TABLE IF NOT EXISTS vilokanam_cache (
            keyword TEXT PRIMARY KEY, cached_response TEXT NOT NULL
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS shabda_pramana (
            keyword TEXT PRIMARY KEY, factual_context TEXT NOT NULL
        )
    """)
    
    # Ingest baseline structural truths
    cursor.executemany("""
        INSERT OR IGNORE INTO vilokanam_cache (keyword, cached_response) VALUES (?, ?)
    """, [
        ("pest", "Ahimsa-108 Alert: Deploy localized neem kernel aqueous extract (5% concentration) combined with traditional light traps during twilight hours to preserve ecosystem balance naturally."),
        ("ph", "Soil Management Directive: For abnormal pH fluctuations outside the 6.0-7.0 optimum baseline window, introduce local organic compost or green manure to stabilize soil buffer capacity safely.")
    ])
    
    cursor.executemany("""
        INSERT OR IGNORE INTO shabda_pramana (keyword, factual_context) VALUES (?, ?)
    """, [
        ("silchar", "Context Verification: Silchar is the headquarters of Cachar district in Assam, India, situated in the high-humidity, flood-prone alluvial basin of the Barak River Valley. Major regional crops include winter rice (Sali), autumn rice (Ahu), and extensive tea cultivation inside undulating hillocks."),
        ("assam", "Context Verification: Assam is located in Northeast India, dominated by the Brahmaputra and Barak river networks, characterized by subtropical rain forests, highly acidic to alluvial soil compositions, and heavy monsoon distribution arrays."),
        ("barak", "Context Verification: The Barak Valley is located in the southern region of Assam, India. It is named after the Barak River and primarily consists of three administrative districts: Cachar, Karimganj, and Hailakandi.")
    ])
    
    conn.commit()
    conn.close()

# --- COGNITIVE KERNELS & FILTERS ---
def check_vilokanam_cache(prompt: str) -> str:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT keyword, cached_response FROM vilokanam_cache")
    rows = cursor.fetchall()
    conn.close()
    normalized = prompt.lower()
    for row in rows:
        if row[0] in normalized:
            return row[1]
    return ""

def inject_shabda_pramana(prompt: str) -> str:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT keyword, factual_context FROM shabda_pramana")
    rows = cursor.fetchall()
    conn.close()
    
    normalized = prompt.lower()
    injected_context = ""
    for row in rows:
        if row[0] in normalized:
            injected_context += row[1] + " "
            
    if injected_context:
        return f"[Truth Vectors: {injected_context.strip()}] User Query: {prompt} Instructions: Analyze matching agricultural frameworks using the provided verified vectors only."
    return prompt

def verify_nyaya_pramana(raw_advice: str, telemetry: dict) -> str:
    if "moisture" in raw_advice.lower() and telemetry:
        if telemetry.get('moisture', 100) < 40 and "irrigate" not in raw_advice.lower():
            return raw_advice + " [Nyaya Note // Pratyaksha Correction: Low soil moisture threshold crossed. Immediate localized irrigation loop highly recommended.]"
    if "hyper-chemical" in raw_advice.lower() or "pesticide" in raw_advice.lower():
        return "Ahimsa-108 Protocol Active Rule Override: Non-destructive soil governance models require organic, regenerative botanical interventions over chemical alternatives."
    return raw_advice

# --- OPTIMIZED SLM EXECUTOR CORE ---
def run_local_slm_inference(prompt_text: str, max_tokens: int):
    is_termux = os.path.exists('/data/data/com.termux')
    if is_termux:
        binary_path = os.path.expanduser("~/llama-b9297/llama-cli")
        lib_dir = os.path.expanduser("~/llama-b9297")
        paths_to_check = [
            os.path.expanduser("~/vedic_model_q2.gguf"),
            os.path.expanduser("~/llama-b9297/vedic_model_q2.gguf"),
            "vedic_model_q2.gguf"
        ]
        model_path = None
        for path in paths_to_check:
            if os.path.exists(path): model_path = os.path.abspath(path); break
        if not model_path: raise FileNotFoundError("Inference weight model array missing.")
        formatted_prompt = prompt_text
    else:
        binary_path = "/home/codespace/llama_source/build/bin/llama-cli"
        lib_dir = "/home/codespace/llama_source/build/bin"
        model_path = "test_model.gguf"
        formatted_prompt = f"<|im_start|>user\n{prompt_text}<|im_end|>\n<|im_start|>assistant\n"

    if not os.path.exists(binary_path): raise FileNotFoundError(f"Binary missing at {binary_path}")

    env = os.environ.copy()
    env['LD_LIBRARY_PATH'] = f"{lib_dir}:{env.get('LD_LIBRARY_PATH', '')}"
    cmd = [binary_path, "-m", model_path, "-p", formatted_prompt, "-n", str(max_tokens), "-st", "-t", "2", "-c", "128", "--mmap"]
    
    try:
        res = subprocess.run(cmd, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=env, preexec_fn=os.setsid, timeout=120)
        raw_data = res.stdout
        if not raw_data: return "[!] Error: Null token matrix stream."
        if not is_termux and "<|im_start|>assistant" in raw_data:
            raw_data = raw_data.split("<|im_start|>assistant")[-1]
        elif prompt_text in raw_data:
            raw_data = raw_data.split(prompt_text)[-1]
        if "[ Prompt:" in raw_data: raw_data = raw_data.split("[ Prompt:")[0]
        clean_text = re.sub(r'[\x08\s|\\/-]+', ' ', raw_data).strip()
        return re.sub(r'^>\s*', '', clean_text).strip()
    except Exception as e:
        return f"[!] Engine Execution Error: {e}"

# --- RTA-DHARMA AUTOMATION DAEMON (UNIFIED GUARDRAILS) ---
def rta_dharma_observer_loop():
    print("[⚡] Rta-Dharma Entanglement Engine Online // Monitoring Physical Thresholds Safely...")
    alert_cooldown = 0
    
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
            conn.close()
            
            if last_record:
                temp, moisture, humidity, ph = last_record
                if moisture < 40.0:
                    print("[🚨] Rta Boundary Breach: Soil Moisture Critical Low Detected. Processing Enriched Background Loop...")
                    t_bg_start = time.time()
                    
                    automated_prompt = f"System alert active. Soil liquid matrix is low at {moisture}% inside the Barak Valley array. Formulate localized irrigation strategy:"
                    
                    # ENFORCE COGNITIVE PIPELINE SYMMETRY NATIVELY FOR DAEMON EXECUTION
                    enriched_bg_prompt = inject_shabda_pramana(automated_prompt)
                    raw_advice = run_local_slm_inference(enriched_bg_prompt, max_tokens=64)
                    
                    if not raw_advice.startswith("[!]"):
                        validated_advice = verify_nyaya_pramana(raw_advice, {'moisture': moisture})
                        bg_latency = time.time() - t_bg_start
                        
                        conn = sqlite3.connect(DB_PATH)
                        conn.cursor().execute(
                            "INSERT INTO advisories (prompt, advice, p_dharma, p_artha, p_kama) VALUES (?, ?, ?, ?, ?)",
                            ("🚨 AUTOMATED THRESHOLD ALERT: Soil Moisture < 40%", validated_advice + " (Autonomous Rta-Dharma Execution)", 1, bg_latency, 1)
                        )
                        conn.commit(); conn.close()
                        alert_cooldown = 180 
        except Exception as e:
            print(f"Rta-Dharma Loop Intercept Exception: {e}")

# --- WEB NODE CONTROL PORT STRUCTURES ---
@app.on_event("startup")
def startup_event():
    init_db()
    t = threading.Thread(target=rta_dharma_observer_loop, daemon=True)
    t.start()

@app.get("/ui", response_class=HTMLResponse)
def serve_dashboard():
    with open(UI_PATH, "r", encoding="utf-8") as f:
        return f.read()

@app.post("/api/v1/advisory")
def generate_agricultural_advisory(request: QueryRequest):
    t_start = time.time()
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT temperature, moisture, humidity, ph FROM sensors ORDER BY id DESC LIMIT 1")
    last_sensor = cursor.fetchone()
    conn.close()
    
    telemetry_dict = {}
    if last_sensor:
        telemetry_dict = {'temp': last_sensor[0], 'moisture': last_sensor[1], 'humidity': last_sensor[2], 'ph': last_sensor[3]}

    cached_hit = check_vilokanam_cache(request.prompt)
    if cached_hit:
        execution_time = time.time() - t_start
        conn = sqlite3.connect(DB_PATH)
        conn.cursor().execute("INSERT INTO advisories (prompt, advice, p_dharma, p_artha, p_kama) VALUES (?, ?, ?, ?, ?)",
            (request.prompt, cached_hit + " (Intercepted via Vilokanam Heuristics)", 1, execution_time, 1))
        conn.commit(); conn.close()
        return {"success": True, "source": "Vilokanam Heuristic Core", "advice": cached_hit}

    enriched_prompt = inject_shabda_pramana(request.prompt)
    raw_advice = run_local_slm_inference(enriched_prompt, request.max_tokens)
    if raw_advice.startswith("[!]"): raise HTTPException(status_code=500, detail=raw_advice)
    
    validated_advice = verify_nyaya_pramana(raw_advice, telemetry_dict)
    execution_time = time.time() - t_start
    
    conn = sqlite3.connect(DB_PATH)
    conn.cursor().execute("INSERT INTO advisories (prompt, advice, p_dharma, p_artha, p_kama) VALUES (?, ?, ?, ?, ?)",
        (request.prompt, validated_advice, 1, execution_time, 1))
    conn.commit(); conn.close()
    
    return {"success": True, "source": "Vedic Tensor Inference Core", "advice": validated_advice}

@app.get("/api/v1/history")
def get_advisory_history():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, timestamp, prompt, advice, p_artha FROM advisories ORDER BY id DESC LIMIT 5")
    rows = cursor.fetchall()
    conn.close()
    return {"history": [{"id": r[0], "time": r[1], "prompt": r[2], "advice": r[3], "latency": f"{r[4]:.4f}s"} for r in rows]}

@app.post("/api/v1/sensors")
def ingest_sensor_metrics(data: SensorTelemetry):
    conn = sqlite3.connect(DB_PATH)
    conn.cursor().execute("INSERT INTO sensors (temperature, moisture, humidity, ph) VALUES (?, ?, ?, ?)",
        (data.temperature, data.moisture, data.humidity, data.ph))
    conn.commit(); conn.close()
    return {"success": True, "message": "Telemetry matrix logged to SQLite data vault."}

@app.get("/api/v1/sensors")
def get_sensor_history():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, timestamp, temperature, moisture, humidity, ph FROM sensors ORDER BY id DESC LIMIT 5")
    rows = cursor.fetchall()
    conn.close()
    return {"telemetry": [{"id": r[0], "time": r[1], "temp": r[2], "moist": r[3], "humid": r[4], "ph": r[5]} for r in rows]}
