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
from backend.core.sync_manager import sync_location, get_cached
from backend.core import slm_engine
from backend.services.slm_reasoning_engine import reason, FarmContext

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


class PlanRequest(BaseModel):
    lat: float
    lon: float
    sensor_data: Optional[List[float]] = None
    soil_type: Optional[str] = "General"
    growth_stage: Optional[int] = 0
    paksha: Optional[str] = None
    use_slm: Optional[bool] = False   # set True to request SLM advice


class SyncRequest(BaseModel):
    lat: float
    lon: float
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
    result = await sync_location(req.lat, req.lon, force=req.force)
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
