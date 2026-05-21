from fastapi import FastAPI, HTTPException, WebSocket, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, Response
from pydantic import BaseModel
from typing import List, Optional
import sqlite3
import os
import asyncio

from backend.core.lazy_loader import loader
from backend.core.uart_listener import uart_websocket_handler, simulate_sensor_stream, get_latest_reading
from backend.core.sync_manager import sync_data_for_location, get_cached
from backend.core import slm_engine
from backend.services.slm_reasoning_engine import reason, FarmContext
from backend.services.nasa_power_weather import get_weather as fetch_nasa_weather
from backend.services.weather_forecast import get_7day_forecast
from backend.services.crop_disease import identify_disease, get_all_diseases_for_crop
from backend.services.mandi_prices import get_crop_prices, get_best_selling_crop
from backend.services.voice_interface import parse_voice_command
from backend.services.validation_engine import validate_plan, get_sau_guidelines, record_farmer_feedback, get_validation_stats

app = FastAPI(title="Krishi-Veda Global Engine", version="2.1")

FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "../frontend")
LOCALIZATION_DIR = os.path.join(os.path.dirname(__file__), "../localization/dicts")

app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")
app.mount("/localization/dicts", StaticFiles(directory=LOCALIZATION_DIR), name="localization")

DB_PATH = os.path.join(os.path.dirname(__file__), "../krishi_veda_offline.db")


# ── Startup: kick off SLM background load ───────────────────────────────────

@app.on_event("startup")
async def startup_event():
    slm_engine.trigger_background_load()


# ── Models ───────────────────────────────────────────────────────────────────

class SoilRequest(BaseModel):
    farmer_id: int
    sensor_data: List[float]
    paksha: Optional[str] = "waxing"


class SyncRequest(BaseModel):
    lat: float
    lon: float
    force: Optional[bool] = False

class PlanRequest(BaseModel):
    lat: Optional[float] = None
    lon: Optional[float] = None
    sensor_data: Optional[List[float]] = None
    soil_type: Optional[str] = "General"
    growth_stage: Optional[int] = 0
    paksha: Optional[str] = None
    use_slm: Optional[bool] = False   # set True to request SLM advice
    weather: Optional[dict] = None      # optional pre-fetched weather
    ndvi: Optional[dict] = None         # optional pre-fetched NDVI
    target_language: Optional[str] = None  # language code for localization

class SyncRequest(BaseModel):
    lat: float
    lon: float
    force: Optional[bool] = False
    force: Optional[bool] = False


# ── Frontend ─────────────────────────────────────────────────────────────────

@app.get("/")
async def root():
    return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))


@app.get("/sw.js")
async def service_worker():
    """
    Serve the Service Worker from the root path so it controls the entire
    origin (not just /static/). The Service-Worker-Allowed header explicitly
    grants root scope to a file served from /sw.js.
    """
    sw_path = os.path.join(FRONTEND_DIR, "sw.js")
    with open(sw_path, "r") as f:
        content = f.read()
    return Response(
        content=content,
        media_type="application/javascript",
        headers={"Service-Worker-Allowed": "/"},
    )


# ── Health + SLM Status ──────────────────────────────────────────────────────

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "engine": "Krishi-Veda Global Engine v2.1",
        "slm": slm_engine.get_slm_status(),
    }


# ── Sync: prime offline cache for 10km radius ────────────────────────────────

@app.post("/api/v1/sync")
async def trigger_sync(req: SyncRequest, background_tasks: BackgroundTasks):
    """
    Fetches NASA Sentinel-2 NDVI + OpenWeather data for a 10km radius
    and caches it in the local SQLite DB.
    Can also be triggered from the browser before going offline.
    """
    result = await sync_data_for_location(req.lat, req.lon, force=req.force)
    return {
        "message": "Sync complete. Data cached for offline use.",
        "result": result,
    }


# ── Core: Full Vedic Agricultural Plan ───────────────────────────────────────

@app.post("/api/v1/plan")
async def get_vedic_plan(req: PlanRequest):
    """
    Returns a full Vedic agricultural plan in < 2 seconds.
    Uses cached data when available; falls back to heuristics offline.
    When use_slm=True, the SLM (Vedic-grounded) generates natural language advice.
    """
    sensor_data = req.sensor_data or [6.5, 35.0, 28.0, 40.0, 50.0, 2.0, 0.3, 28.0]

    # 1. Try to get data from local cache first (instant, offline-safe)
    cached = get_cached(req.lat, req.lon)
    weather = cached["weather"] if cached["weather"].get("temperature_c") else None
    ndvi_data = cached["ndvi"] if cached["ndvi"].get("ndvi") else None

    # 2. If cache miss, fetch live (or use heuristics) in parallel
    if not weather or not ndvi_data:
        from backend.services.external_intel_service import get_weather, get_ndvi
        tasks = []
        if not weather:
            tasks.append(asyncio.create_task(get_weather(req.lat, req.lon)))
        if not ndvi_data:
            tasks.append(asyncio.create_task(get_ndvi(req.lat, req.lon)))

        results = await asyncio.gather(*tasks)
        idx = 0
        if not weather:
            weather = results[idx]; idx += 1
        if not ndvi_data:
            ndvi_data = results[idx]

    # 3. Determine paksha
    paksha = req.paksha or weather.get("paksha", "waxing")

    # 4. Check for live UART reading
    uart = get_latest_reading()
    if uart and req.sensor_data is None:
        sensor_data = [
            uart.get("pH", 6.5), uart.get("N", 35.0), uart.get("P", 28.0),
            uart.get("K", 40.0), uart.get("moisture", 50.0),
            2.0, 0.3, weather.get("temperature_c", 28.0)
        ]

    # 5. Rule-based Vedic reasoning (always fast)
    ctx = FarmContext(
        lat=req.lat, lon=req.lon,
        sensor_data=sensor_data,
        paksha=paksha,
        soil_type=req.soil_type or "General",
        growth_stage=req.growth_stage or 0,
        ndvi=ndvi_data.get("ndvi", 0.5),
        rainfall_mm=weather.get("rainfall_mm_monthly", 80.0),
        temperature_c=weather.get("temperature_c", 28.0),
    )
    plan = reason(ctx)

    response = {
        "vedic_plan": {
            "summary": plan.summary,
            "stress_code": plan.stress_code,
            "ahimsa_108_triggered": plan.ahimsa_triggered,
            "wellness_score": plan.wellness_score,
            "yield_index": plan.yield_index,
            "paksha": paksha,
            "paksha_advice": plan.paksha_advice,
            "primary_crops": plan.primary_crops,
            "recommendations": plan.recommendations,
            "liming_kg_per_ha": plan.liming_recommendation_kg_ha,
            "intervention": plan.intervention,
            "next_growth_milestone": plan.next_stage_index,
        },
        "sutra_computations": plan.sutra_computations,
        "external_data": {
            "weather": weather,
            "crop_health_ndvi": ndvi_data,
        },
        "sensor_used": sensor_data,
        "uart_live": bool(uart),
        "slm_advice": None,
    }

    # 6. Optional: SLM-generated natural language advice (Vedic-grounded)
    if req.use_slm:
        slm_result = slm_engine.generate_advice(
            sensor_data=sensor_data,
            soil_type=req.soil_type or "General",
            paksha=paksha,
            weather=weather,
            ndvi=ndvi_data,
        )
        response["slm_advice"] = slm_result

    return response


# ── Weather + NDVI ───────────────────────────────────────────────────────────

# ── Languages ─────────────────────────────────────────────────────────────────

@app.get("/api/v1/languages")
async def get_languages():
    """Return list of supported languages and their full dictionaries."""
    import json
    languages = []
    if os.path.isdir(LOCALIZATION_DIR):
        for fname in sorted(os.listdir(LOCALIZATION_DIR)):
            if fname.endswith(".json"):
                code = fname.replace(".json", "")
                try:
                    with open(os.path.join(LOCALIZATION_DIR, fname), "r") as f:
                        data = json.load(f)
                    languages.append({
                        "code": code,
                        "name": data.get("_language_name", code),
                        "dict": data
                    })
                except Exception:
                    pass
    return {"languages": languages}


@app.get("/api/v1/languages/{lang_code}")
async def get_language_dict(lang_code: str):
    """Return a single language dictionary JSON."""
    import json
    path = os.path.join(LOCALIZATION_DIR, f"{lang_code}.json")
    if not os.path.isfile(path):
        raise HTTPException(status_code=404, detail=f"Language {lang_code} not found")
    with open(path, "r") as f:
        return json.load(f)


# ── Offline cached plan retrieval (used by service worker) ───────────────────

@app.get("/api/v1/plan/cached/{body_hash}")
async def get_cached_plan(body_hash: str):
    """
    Returns a previously cached /api/v1/plan response. Used by the service
    worker when offline. The service worker intercepts this and returns
    from its cache. If reached directly, returns a hint.
    """
    return Response(
        content='{"message": "This endpoint is used by the service worker for offline caching. Use POST /api/v1/plan instead."}',
        media_type="application/json",
        headers={"X-Krishi-Veda-Offline": "false"},
    )

@app.get("/api/v1/weather")
async def weather_endpoint(lat: float, lon: float):
    from backend.services.external_intel_service import get_weather
    return await get_weather(lat, lon)


@app.get("/api/v1/ndvi")
async def ndvi_endpoint(lat: float, lon: float):
    from backend.services.external_intel_service import get_ndvi
    return await get_ndvi(lat, lon)


# ── Regional crops ───────────────────────────────────────────────────────────

@app.get("/api/v1/crops/{state_code}")
async def get_regional_crops(state_code: str):
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(
            "SELECT soil_type, primary_crops FROM regional_data WHERE state_code = ?",
            (state_code.upper(),)
        )
        row = cursor.fetchone()
        conn.close()
        if not row:
            raise HTTPException(status_code=404, detail=f"No data found for state: {state_code}")
        return {
            "state": state_code.upper(),
            "soil_type": row["soil_type"],
            "primary_crops": row["primary_crops"]
        }
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


# ── SLM standalone endpoint ───────────────────────────────────────────────────

@app.post("/api/v1/slm/advice")
async def slm_advice(req: PlanRequest):
    """
    Dedicated endpoint for SLM natural-language advice.
    Vedic kernels are ALWAYS queried first (grounding), then SLM or fallback.
    """
    sensor_data = req.sensor_data or [6.5, 35.0, 28.0, 40.0, 50.0, 2.0, 0.3, 28.0]
    cached = get_cached(req.lat, req.lon)
    weather = cached["weather"] if cached["weather"].get("temperature_c") else {"temperature_c": 28}
    ndvi = cached["ndvi"] if cached["ndvi"].get("ndvi") else {"ndvi": 0.5}
    return slm_engine.generate_advice(
        sensor_data=sensor_data,
        soil_type=req.soil_type or "General",
        paksha=req.paksha or "waxing",
        weather=weather,
        ndvi=ndvi,
    )


@app.get("/api/v1/slm/status")
async def slm_status():
    return slm_engine.get_slm_status()



# ── 7-Day Weather Forecast ─────────────────────────────────────────────────

@app.get("/api/v1/weather/forecast")
async def weather_forecast(lat: float, lon: float):
    """7-day weather forecast with sowing advice."""
    return get_7day_forecast(lat, lon)


# ── Crop Disease Identification ─────────────────────────────────────────────

@app.post("/api/v1/disease/identify")
async def disease_identify(crop: str, symptoms: str):
    """Identify crop disease from symptoms. Symptoms as comma-separated string."""
    symptom_list = [s.strip() for s in symptoms.split(",")]
    return identify_disease(crop, symptom_list)


@app.get("/api/v1/disease/list/{crop}")
async def disease_list(crop: str):
    """List all known diseases for a crop."""
    return get_all_diseases_for_crop(crop)


# ── Mandi Prices ─────────────────────────────────────────────────────────────

@app.get("/api/v1/mandi/prices")
async def mandi_prices(crop: str, state: str = "Assam"):
    """Get current mandi prices for a crop."""
    return get_crop_prices(crop, state)


@app.get("/api/v1/mandi/best-crop")
async def best_crop(state: str = "Assam", season: str = "kharif"):
    """Get most profitable crop recommendation based on mandi prices."""
    return get_best_selling_crop(state, season)



# ── Validation & Ground Truth ───────────────────────────────────────────────

@app.post("/api/v1/validate/plan")
async def validate_vedic_plan(plan_data: dict):
    """Validate AI plan against SAU guidelines. Returns confidence score."""
    district = plan_data.get('district', 'Unknown')
    state = plan_data.get('state', 'Assam')
    season = plan_data.get('season', 'kharif')
    vedic_plan = plan_data.get('vedic_plan', {})
    return validate_plan(vedic_plan, district, state, season)


@app.get("/api/v1/validate/guidelines")
async def sau_guidelines(state: str = "Assam", soil: str = "Alluvial", season: str = "kharif"):
    """Get SAU agricultural university guidelines for validation."""
    return get_sau_guidelines(state, soil, season)


@app.post("/api/v1/validate/feedback")
async def farmer_feedback(plan_id: str, actual_yield: float, satisfaction: int, notes: str = ""):
    """Record farmer feedback on AI advice for continuous improvement."""
    return record_farmer_feedback(plan_id, actual_yield, satisfaction, notes)


@app.get("/api/v1/validate/stats")
async def validation_statistics():
    """Get aggregate validation statistics from farmer feedback."""
    return get_validation_stats()


# ── Voice Command ────────────────────────────────────────────────────────────

@app.post("/api/v1/voice/command")
async def voice_command(text: str, language: str = "hi"):
    """Parse spoken voice command into Krishi-Veda action."""
    return parse_voice_command(text, language)


# ── UART WebSocket ───────────────────────────────────────────────────────────

@app.websocket("/ws/uart")
async def uart_ws(websocket: WebSocket):
    await uart_websocket_handler(websocket)


@app.websocket("/ws/uart/simulate")
async def uart_sim_ws(websocket: WebSocket):
    await simulate_sensor_stream(websocket)


@app.get("/api/v1/uart/latest")
async def get_latest_uart():
    reading = get_latest_reading()
    if not reading:
        return {"status": "no_data", "message": "No UART readings received yet."}
    return {"status": "ok", "reading": reading}
