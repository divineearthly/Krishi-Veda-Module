"""
Krishi-Veda SLM Engine — Vedic Inference Integrated
Qwen2.5-0.5B + vedic-inference-engine (Nyaya + Rta-Dharma)
Final working: Popen with process group kill via os.killpg.
"""

import subprocess, os, sys, time, re, signal

VIE_PATH = os.path.expanduser("~/vedic-inference-engine")
if VIE_PATH not in sys.path:
    sys.path.insert(0, VIE_PATH)

from vedic_inference_engine import NyayaScaffold, PramanaSource, RtaDharmaRouter

LLAMA_DIR = os.path.expanduser("~/llama-b9297")
MODEL = os.path.expanduser("~/qwen2.5-0.5b-instruct-q4.gguf")
MODEL_BACKUP = os.path.expanduser("~/vedic_model_q2.gguf")
AHIMSA_THRESHOLD = 75.0
LLAMA_TIMEOUT = 20


def nikhilam_deficit(n, p, k): return 100 - (n + p + k) / 3
def paravartya_ph_inversion(ph): return abs(ph - 6.5) * 250
def ahimsa_108_stress_code(a, b, c, d): return (a + b + c + d) / 4
def gunakasamuccaya_wellness(a, b, c, d): return (a + b + c + d) / 4


def _get_model():
    if os.path.isfile(MODEL): return MODEL
    if os.path.isfile(MODEL_BACKUP): return MODEL_BACKUP
    return MODEL


def _vedic_grounding(sensor_data):
    if len(sensor_data) < 8:
        sensor_data = (sensor_data + [6.5, 35, 28, 40, 50, 2.0, 0.3, 28])[:8]
    ph, n, p, k, moisture, om, ec, temp = sensor_data
    deficit = nikhilam_deficit(n, p, k)
    liming = paravartya_ph_inversion(ph)
    ph_score = max(0, 100 - abs(ph - 6.5) * 25)
    npk_score = min(100, (n + p + k) / 1.2)
    moist_score = min(100, moisture * 2)
    om_score = min(100, om * 20)
    wellness = gunakasamuccaya_wellness(ph_score, npk_score, moist_score, om_score)
    stress_code = ahimsa_108_stress_code(deficit, liming / 250.0, 0, wellness)
    return {
        "ahimsa_triggered": stress_code >= AHIMSA_THRESHOLD,
        "stress_code": round(stress_code, 2),
        "wellness": round(wellness, 2),
        "deficit_ppm": round(deficit, 2),
        "liming_kg_ha": round(liming, 1),
    }


def _fallback(sensor_data, soil_type, paksha, vedic):
    ph, n, p, k = (sensor_data + [6.5, 35, 28, 40])[:4]
    if ph < 5.5: s = "Acidic. Apply lime 2-3 tons/ha."
    elif ph > 8.0: s = "Alkaline. Add gypsum."
    else: s = "pH good (6.0-7.5)."
    if n < 30: nut = "Low N. Vermicompost 5t/ha."
    elif p < 20: nut = "Low P. Rock phosphate 200kg/ha."
    elif k < 25: nut = "Low K. Wood ash 100kg/ha."
    else: nut = "NPK adequate. Annual vermicompost 2t/ha."
    crops = {"alluvial":"Sali Rice or Mustard","laterite":"Cashew/Coconut",
             "sandy":"Groundnut","clay":"Boro Rice","loamy":"Tomato/Brinjal"}
    c = crops.get(soil_type.lower(), "Rice")
    m = "Good for sowing." if paksha == "waxing" else "Good for harvesting."
    a = "\n[AHIMSA-108] Panchgavya ONLY. No chemicals." if vedic.get("ahimsa_triggered") else ""
    return f"SOIL: {s}\nFERTILIZER: {nut}\nCROP: {c}\nMOON: {m}{a}"


def _parse_response(raw_text):
    if not raw_text: return ""
    cleaned = re.sub(r'\x1b\[[0-9;]*[a-zA-Z]', '', raw_text)
    lines = cleaned.split('\n')
    response_lines = []
    past_prompt = False
    
    for line in lines:
        s = line.strip()
        if not s: continue
        if any(h in s for h in [
            'build ', 'model:', 'modalities:', 'available commands:',
            '/exit', '/regen', '/clear', '/read', '/glob',
            'loading model', '▄', '█', 'llama_', 'ggml_',
        ]): continue
        if re.match(r'^\[\s*(Prompt|Generation):.*t/s.*\]$', s):
            break
        if s.startswith('> '):
            past_prompt = True
            continue
        if s == '>' and past_prompt:
            break
        if past_prompt and s:
            response_lines.append(s)
    
    result = ' '.join(response_lines).strip()
    
    if len(result) < 15:
        for i, line in enumerate(lines):
            if line.strip().startswith('> ') and i + 1 < len(lines):
                after = []
                for l in lines[i+1:]:
                    s = l.strip()
                    if not s: continue
                    if any(h in s for h in ['build ', 'model:', '[ Prompt:', '[ Generation:']):
                        continue
                    if s.startswith('>'):
                        continue
                    after.append(s)
                if after:
                    result = ' '.join(after).strip()
                    break
    
    for marker in ['</s>', '<|im_end|>', '<|endoftext|>', '<|assistant|>']:
        result = result.replace(marker, '').strip()
    return result[:500] if len(result) > 10 else ""


def _infer(prompt, timeout_sec=LLAMA_TIMEOUT):
    """Run llama-cli via Popen with stdin pipe, kill process group on timeout."""
    model = _get_model()
    if not os.path.isfile(model): return ""

    env = os.environ.copy()
    env["LD_LIBRARY_PATH"] = LLAMA_DIR

    try:
        proc = subprocess.Popen(
            ["./llama-cli", "-m", model,
             "-n", "80", "-c", "1024",
             "--temp", "0.7",
             "--log-disable", "--no-display-prompt"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            cwd=LLAMA_DIR,
            env=env,
            text=True,
            start_new_session=True  # Create new process group
        )

        # Write prompt and close stdin
        proc.stdin.write(prompt)
        proc.stdin.close()

        # Read output with timeout
        output_lines = []
        t0 = time.time()
        
        while time.time() - t0 < timeout_sec:
            # Check if process has terminated
            if proc.poll() is not None:
                break
            
            try:
                line = proc.stdout.readline()
                if not line:
                    time.sleep(0.1)
                    continue
                output_lines.append(line)
            except:
                break

        # Kill the process group if still running
        if proc.poll() is None:
            try:
                os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
            except:
                proc.kill()
        
        proc.wait(timeout=2)

        raw = ''.join(output_lines)
        return _parse_response(raw)

    except Exception:
        return ""


def generate_advice(sensor_data, soil_type="General", paksha="waxing",
                    weather=None, ndvi=None):
    weather = weather or {}
    ndvi = ndvi or {}
    vedic = _vedic_grounding(sensor_data)

    nyaya = NyayaScaffold()
    router = RtaDharmaRouter()

    ph, n, p, k = (sensor_data + [6.5, 35, 28, 40])[:4]
    nyaya.tag(f"Soil pH={ph}, N={n}ppm, P={p}ppm, K={k}ppm, type={soil_type}",
              PramanaSource.PRATYAKSHA, 0.95)
    nyaya.tag(f"Soil wellness: {vedic['wellness']:.0f}/100",
              PramanaSource.PRATYAKSHA, 0.90)

    temp = weather.get("temperature_c", 28)
    rain = weather.get("rainfall_mm_monthly", 80)
    if weather:
        nyaya.tag(f"Weather: {temp}C, {rain}mm rain",
                  PramanaSource.PRATYAKSHA, 0.85)

    nyaya.tag(f"Ahimsa stress: {vedic['stress_code']}",
              PramanaSource.ANUMANA, 0.75,
              hetu="Vedic kernel: NPK deficit + pH inversion")

    if vedic["ahimsa_triggered"]:
        nyaya.tag("Ahimsa-108: organic only",
                  PramanaSource.SHABDA, 0.90)

    severity = max(0.0, min(1.0, vedic["deficit_ppm"] / 200.0))
    router.add("SLM advice",
               crop_importance=0.85,
               season_urgency=0.7 if paksha == "waxing" else 0.4,
               severity_weight=severity,
               farmers_affected=100,
               ahimsa_score=0.3 if vedic["ahimsa_triggered"] else 1.0)

    if os.path.isfile(os.path.join(LLAMA_DIR, "llama-cli")) and os.path.isfile(_get_model()):
        ahimsa = vedic["ahimsa_triggered"]
        ahimsa_line = "ONLY organic Panchgavya. NO chemicals." if ahimsa else "Prefer organic methods."

        prompt_raw = (
            f"Assam farmer: Soil {soil_type}, health {vedic['wellness']:.0f}/100, "
            f"NPK deficit {vedic['deficit_ppm']:.0f}ppm, temp {temp}C, rain {rain}mm.\n"
            f"{ahimsa_line}\n"
            f"Give 3 short lines: best crop, fertilizer amount per bigha, when to plant."
        )

        t0 = time.time()
        raw = _infer(prompt_raw)
        elapsed = round(time.time() - t0, 2)

        if raw and len(raw) > 10:
            nyaya.tag(f"SLM: {raw[:120]}",
                      PramanaSource.ANUMANA, 0.70,
                      hetu="Qwen2.5-0.5B ARM64 inference")
            hallucinations = nyaya.detect_hallucinations()
            return {
                "advice": raw,
                "vedic": vedic,
                "model": os.path.basename(_get_model()),
                "time_s": elapsed,
                "ahimsa": ahimsa,
                "engine": "slm",
                "nyaya_confidence": round(nyaya.overall_confidence(), 3),
                "hallucination_risk": len(hallucinations) > 0,
                "dharma_priority": round(router.top_priority().compute_score(), 3) if router.top_priority() else 0.0,
            }

    nyaya.tag("SLM unavailable — rule fallback",
              PramanaSource.SHABDA, 0.85)
    fallback_advice = _fallback(sensor_data, soil_type, paksha, vedic)
    return {
        "advice": fallback_advice,
        "vedic": vedic,
        "model": "fallback",
        "ahimsa": vedic["ahimsa_triggered"],
        "engine": "rule",
        "nyaya_confidence": round(nyaya.overall_confidence(), 3),
        "hallucination_risk": False,
        "dharma_priority": round(router.top_priority().compute_score(), 3) if router.top_priority() else 0.0,
    }
