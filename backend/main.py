from fastapi import FastAPI, HTTPException, WebSocket
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Optional
import sqlite3
import os
import asyncio

from backend.core.lazy_loader import loader
from backend.core.uart_listener import uart_websocket_handler, simulate_sensor_stream, get_latest_reading
from backend.services.external_intel_service import get_weather, get_ndvi
from backend.services.slm_reasoning_engine import reason, FarmContext

app = FastAPI(title="Krishi-Veda Global Engine", version="2.0")

FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "../frontend")
LOCALIZATION_DIR = os.path.join(os.path.dirname(__file__), "../localization/dicts")

app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")
app.mount("/localization/dicts", StaticFiles(directory=LOCALIZATION_DIR), name="localization")

DB_PATH = os.path.join(os.path.dirname(__file__), "../krishi_veda_offline.db")


# --- Models ---

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


# --- Frontend ---

@app.get("/")
async def root():
    return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))


# --- Health ---

@app.get("/health")
async def health_check():
    return {"status": "healthy", "engine": "Krishi-Veda Global Engine v2.0"}


# --- Core: Full Vedic Agricultural Plan ---

@app.post("/api/v1/plan")
async def get_vedic_plan(req: PlanRequest):
    """
    Primary endpoint: Given location + optional sensor data,
    returns a full Vedic-optimized agricultural plan in <2 seconds.
    Applies all 8 Krishi-Sutras + Ahimsa-108 Protocol.
    """
    sensor_data = req.sensor_data or [6.5, 35.0, 28.0, 40.0, 50.0, 2.0, 0.3, 28.0]

    # Fetch weather and NDVI in parallel
    weather_task = asyncio.create_task(get_weather(req.lat, req.lon))
    ndvi_task = asyncio.create_task(get_ndvi(req.lat, req.lon))
    weather, ndvi_data = await asyncio.gather(weather_task, ndvi_task)

    # Determine paksha
    paksha = req.paksha or weather.get("paksha", "waxing")

    # Also check if there's a live UART reading
    uart = get_latest_reading()
    if uart and req.sensor_data is None:
        sensor_data = [
            uart.get("pH", 6.5),
            uart.get("N", 35.0),
            uart.get("P", 28.0),
            uart.get("K", 40.0),
            uart.get("moisture", 50.0),
            2.0, 0.3, weather.get("temperature_c", 28.0)
        ]

    ctx = FarmContext(
        lat=req.lat,
        lon=req.lon,
        sensor_data=sensor_data,
        paksha=paksha,
        soil_type=req.soil_type or "General",
        growth_stage=req.growth_stage or 0,
        ndvi=ndvi_data.get("ndvi", 0.5),
        rainfall_mm=weather.get("rainfall_mm_monthly", 80.0),
        temperature_c=weather.get("temperature_c", 28.0),
    )

    plan = reason(ctx)

    return {
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
    }


# --- Legacy: Soil prediction endpoint ---

@app.post("/api/v1/predict/soil")
async def predict_soil(request: SoilRequest):
    if len(request.sensor_data) != 8:
        raise HTTPException(status_code=400, detail="Sensor data must contain exactly 8 features.")
    try:
        result = loader.soil_service.predict(
            farmer_id=request.farmer_id,
            sensor_data=request.sensor_data,
            current_paksha=request.paksha
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# --- Weather + NDVI proxy endpoints ---

@app.get("/api/v1/weather")
async def weather_endpoint(lat: float, lon: float):
    return await get_weather(lat, lon)


@app.get("/api/v1/ndvi")
async def ndvi_endpoint(lat: float, lon: float):
    return await get_ndvi(lat, lon)


# --- Regional crops ---

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


# --- UART WebSocket endpoints ---

@app.websocket("/ws/uart")
async def uart_ws(websocket: WebSocket):
    """Real UART sensor data. Send JSON or CSV frames."""
    await uart_websocket_handler(websocket)


@app.websocket("/ws/uart/simulate")
async def uart_sim_ws(websocket: WebSocket):
    """Simulated N-P-K sensor stream for demos."""
    await simulate_sensor_stream(websocket)


@app.get("/api/v1/uart/latest")
async def get_latest_uart():
    reading = get_latest_reading()
    if not reading:
        return {"status": "no_data", "message": "No UART readings received yet."}
    return {"status": "ok", "reading": reading}
