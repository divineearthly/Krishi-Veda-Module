from backend.core.crop_manager import crop_manager
"""
Krishi-Veda API — Production Version
Rule-based advice: INSTANT (no model loading)
AI advice: available on /ai-advice endpoint
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from flask import Flask, request, jsonify, send_from_directory
from datetime import datetime

app = Flask(__name__)

@app.after_request
def add_cors(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "*"
    return response

# ── Load Vedic grounding (instant, no model) ─────────────────────────────────
from backend.core.vedic_kernels_bridge import (
    anurupyena_scale, nikhilam_deficit, ahimsa_108_stress_code,
    gunakasamuccaya_wellness, paravartya_ph_inversion,
)

def get_instant_advice(sensor_data, soil_type="alluvial", paksha="waxing", 
                       weather=None, ndvi=None):
    """Pure Python rule engine — instant, no model loading."""
    weather = weather or {}; ndvi = ndvi or {}
    
    if len(sensor_data) < 8:
        sensor_data = (sensor_data + [6.5, 35, 28, 40, 50, 2.0, 0.3, 28])[:8]
    ph, n, p, k, moisture, om, ec, temp = sensor_data
    
    # Vedic calculations
    deficit = nikhilam_deficit(n, p, k)
    liming = paravartya_ph_inversion(ph)
    ph_score = max(0, 100 - abs(ph - 6.5) * 25)
    npk_score = min(100, (n + p + k) / 1.2)
    moist_score = min(100, moisture * 2)
    om_score = min(100, om * 20)
    wellness = gunakasamuccaya_wellness(ph_score, npk_score, moist_score, om_score)
    stress_code = ahimsa_108_stress_code(deficit, liming / 250.0, 0, wellness)
    ahimsa = stress_code >= 75.0
    
    # Soil advice
    if ph < 5.5: soil_advice = "Acidic. Apply lime 2-3 tons/ha."
    elif ph > 8.0: soil_advice = "Alkaline. Add gypsum 1 ton/ha."
    else: soil_advice = "pH good (6.0-7.5). No amendment needed."
    
    # Nutrients
    n_scale = anurupyena_scale(n, 40.0)
    p_scale = anurupyena_scale(p, 30.0)
    k_scale = anurupyena_scale(k, 35.0)
    
    if n < 30:
        nut = f"Low N (scale: {n_scale:.1f}). Apply vermicompost 5t/ha or dhaincha green manure."
    elif p < 20:
        nut = f"Low P (scale: {p_scale:.1f}). Apply rock phosphate 200kg/ha."
    elif k < 25:
        nut = f"Low K (scale: {k_scale:.1f}). Apply wood ash 100kg/ha."
    else:
        nut = f"NPK adequate (N:{n_scale:.1f} P:{p_scale:.1f} K:{k_scale:.1f}). Maintain with vermicompost 2t/ha yearly."
    
    # Crop
    crops = {
        "alluvial": "Sali Rice (transplant Jun-Jul) or Mustard (sow Oct-Nov)",
        "laterite": "Cashew with Black Pepper intercropping",
        "sandy": "Groundnut (sow Feb-Mar) or Sweet Potato (Jun-Jul)",
        "clay": "Boro Rice (transplant Dec-Jan) or Sugarcane (Feb-Mar)",
        "loamy": "Tomato/Brinjal/Cabbage (transplant Oct-Nov)",
    }
    crop = crops.get(soil_type.lower(), "Rice (Sali variety)")
    
    # Water
    temp_val = weather.get("temperature_c", 28)
    rain = weather.get("rainfall_mm_monthly", weather.get("rainfall_mm", 80))
    if rain > 100:
        water = f"Rainfall sufficient ({rain}mm). Ensure drainage. No irrigation needed."
    elif temp_val > 32:
        water = f"Hot ({temp_val}°C). Irrigate every 3-4 days. Mulch to retain moisture."
    else:
        water = f"Moderate climate. Irrigate every 5-7 days. Drip recommended."
    
    # Moon
    moon = "Waxing moon — good for sowing. Sap flows upward." if paksha == "waxing" else "Waning moon — good for harvesting. Sap descends."
    
    # Ahimsa
    ahimsa_text = ""
    if ahimsa:
        ahimsa_text = (
            "\n\n[AHIMSA-108 PROTOCOL ACTIVE] "
            "Stress code: {:.1f}. Use Panchgavya ONLY: mix 5kg cow dung + 5L urine + 2L milk "
            "+ 2L curd + 1kg ghee. Ferment 15 days. Apply 5% solution every 15 days. "
            "NO chemical fertilizers or pesticides."
        ).format(stress_code)
    
    advice = (
        f"🌱 SOIL: {soil_advice}\n"
        f"🧪 FERTILIZER: {nut}\n"
        f"🌾 CROP: {crop}\n"
        f"💧 WATER: {water}\n"
        f"🌙 MOON: {moon}"
        + ahimsa_text
    )
    
    return {
        "advice": advice,
        "vedic": {
            "wellness": round(wellness, 2),
            "stress_code": round(stress_code, 2),
            "deficit_ppm": round(deficit, 2),
            "liming_kg_ha": round(liming, 1),
            "ahimsa_triggered": ahimsa
        },
        "engine": "vedic-rule-instant",
        "inference_ms": 0
    }

# ── Routes ───────────────────────────────────────────────────────────────────
@app.route('/')
def home():
    return jsonify({
        "name": "Krishi-Veda API",
        "version": "2.0.0",
        "status": "active",
        "endpoints": {
            "/": "This info",
            "/health": "Health check",
            "/weather": "Live weather (Open-Meteo, free)",
            "/market-prices": "MSP mandi prices",
            "/ask": "INSTANT farming advice (rule engine)",
            "/ai-advice": "AI-powered advice (slower, uses SLM model)",
            "/realtime-data": "All real-time data"
        },
        "languages": ["en", "as", "hi", "bn"]
    })

@app.route('/health')
def health():
    return jsonify({"status": "healthy", "response_time_ms": 0})

@app.route("/location-vedic")
def location_vedic():
    """Get Vedic analysis based on actual GPS location."""
    from backend.core.live_location_engine import LiveLocationEngine
    engine = LiveLocationEngine()
    loc = engine.get_gps_location()
    geo = engine.reverse_geocode(loc.lat, loc.lon)
    weather = engine.get_hyperlocal_weather(loc.lat, loc.lon)
    soil = engine.get_soil_type(loc.lat, loc.lon)
    vedic = engine.vedic_location_analysis(loc.lat, loc.lon)
    
    return jsonify({
        "location": {"lat": loc.lat, "lon": loc.lon, "source": loc.source},
        "place": geo,
        "weather": weather,
        "soil_type": soil,
        "vedic": vedic,
        "timestamp": datetime.now().isoformat()
    })

@app.route('/weather')
def weather():
    lat = request.args.get('lat', 26.1445, type=float)
    lon = request.args.get('lon', 91.7362, type=float)
    try:
        from backend.services.real_time_data import get_weather_data
        return jsonify(get_weather_data(lat, lon))
    except:
        return jsonify({"temperature_c": 30, "rainfall_mm": 80, "source": "fallback"})

@app.route('/market-prices')
def market_prices():
    try:
        from backend.services.real_time_data import get_market_prices
        return jsonify(get_market_prices(
            request.args.get('state', 'Assam'),
            request.args.get('district', 'Kamrup')
        ))
    except:
        return jsonify({"Rice": "₹2300/quintal", "Mustard": "₹5650/quintal"})

@app.route('/realtime-data')
def realtime_data():
    try:
        from backend.services.real_time_data import get_all_realtime_data
        return jsonify(get_all_realtime_data(
            request.args.get('lat', 26.1445, type=float),
            request.args.get('lon', 91.7362, type=float),
            request.args.get('state', 'Assam'),
            request.args.get('district', 'Kamrup')
        ))
    except:
        return jsonify({"error": "unavailable"})

@app.route('/api/v1/plan', methods=['GET', 'POST'])
@app.route('/ask', methods=['GET', 'POST'])
def ask():
    """INSTANT advice — rule engine, no model loading."""
    soil = request.args.get('soil', 'alluvial')
    paksha = request.args.get('paksha', 'waxing')
    query = request.args.get('q', '').lower()

    # 1. Detect region from user query (Defaults to Assam)
    detected_region = "assam"
    for r in ["punjab", "maharashtra", "assam", "global_temperate"]:
        if r in query:
            detected_region = r
            break
    
    # 2. Query our new lightweight JSON manager
    crop_advice = crop_manager.get_crops_for_region(detected_region)

    # Try to get live weather (Untouched!)
    weather = {"temperature_c": 30, "rainfall_mm": 80}
    ndvi = {"ndvi": 0.5}
    try:
        from backend.services.real_time_data import get_weather_data, get_ndvi_data
        lat = request.args.get('lat', 26.1445, type=float)
        lon = request.args.get('lon', 91.7362, type=float)
        weather = get_weather_data(lat, lon)
        ndvi = get_ndvi_data(lat, lon)
    except:
        pass

    result = get_instant_advice(
        [6.5, 35, 28, 40, 50, 2.0, 0.3, 28],
        soil_type=soil, paksha=paksha, weather=weather, ndvi=ndvi
    )

    # 3. Inject the dynamic global crop database into the final string
    if "advice" in result:
        result["advice"] = f"{result['advice']}\n\n🌱 Global Crop Guide: {crop_advice}"
    else:
        result["crop_advice"] = crop_advice

    return jsonify({
        "question": request.args.get('q', ''),
        **result,
        "weather_used": weather.get("source", "default"),
        "timestamp": datetime.now().isoformat()
    })

@app.route('/ai-advice')
def ai_advice():
    """AI-powered advice using SLM model (5-15 second response time)."""
    soil = request.args.get('soil', 'alluvial')
    
    weather = {"temperature_c": 30, "rainfall_mm_monthly": 80}
    ndvi = {"ndvi": 0.5}
    try:
        from backend.services.real_time_data import get_weather_data, get_ndvi_data
        lat = request.args.get('lat', 26.1445, type=float)
        lon = request.args.get('lon', 91.7362, type=float)
        weather = get_weather_data(lat, lon)
        ndvi = get_ndvi_data(lat, lon)
    except:
        pass
    
    from backend.core.slm_engine import generate_advice
    result = generate_advice(
        [6.5, 35, 28, 40, 50, 2.0, 0.3, 28],
        soil_type=soil, weather=weather, ndvi=ndvi
    )
    
    return jsonify({**result, "timestamp": datetime.now().isoformat()})

@app.route('/app')
def serve_app():
    return send_from_directory("frontend", "offline_app.html")

@app.route("/quantum-ui")
def quantum_ui():
    return send_from_directory("frontend", "quantum_app.html")

@app.route("/quantum")
def vedic_quantum():
    from backend.core.vedic_quantum_engine import VedicQuantumEngine
    engine = VedicQuantumEngine()
    question = request.args.get("q", "What to plant?")
    soil = request.args.get("soil", "alluvial")
    lat = request.args.get("lat", 26.14, type=float)
    lon = request.args.get("lon", 91.74, type=float)
    result = engine.query(question, soil_type=soil, lat=lat, lon=lon)
    return jsonify(result)

if __name__ == '__main__':
    print("=" * 50)
    print("  KRISHI-VEDA API v2 — Instant + AI Advice")
    print("  http://localhost:5000")
    print("  /ask        → INSTANT rule-based advice")
    print("  /ai-advice  → AI model advice (slower)")
    print("=" * 50)
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
