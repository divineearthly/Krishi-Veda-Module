from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import json
import sys
import os

# Add the path to our Krishi-Veda-Module/vedic_engine directory to sys.path
# This allows us to import krishi_veda_logic
sys.path.insert(0, './Krishi-Veda-Module/vedic_engine/')

# Import our main logic function
from krishi_veda_logic import generate_farmer_advice

app = FastAPI(
    title="Krishi-Veda FastAPI Server",
    description="AI-powered farmer advice system with Vedic override and multilingual support.",
    version="1.0.0"
)

# Pydantic models for request body validation
class SoilData(BaseModel):
    pH: float
    nitrogen: str
    phosphorus: str
    potassium: str

class WeatherData(BaseModel):
    temperature: float
    humidity: float
    precipitation: str

class AdviceRequest(BaseModel):
    soil_data: SoilData
    weather_data: WeatherData
    language_code: str = "en"

@app.get("/", summary="Root endpoint", description="Check if the server is running.")
async def root():
    return {"message": "Krishi-Veda FastAPI Server is running! Visit /docs for API documentation."}

@app.post("/soil-analysis", summary="Soil Analysis Advice", description="Provides farming advice based on soil data, including Vedic override and multilingual translation.")
async def soil_analysis(request: AdviceRequest):
    try:
        advice = generate_farmer_advice(request.soil_data.dict(), request.weather_data.dict(), request.language_code)
        return json.loads(advice)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {e}")

@app.post("/weather-risk", summary="Weather Risk Assessment", description="Assesses weather risks and provides advice, including Vedic override and multilingual translation.")
async def weather_risk(request: AdviceRequest):
    try:
        advice = generate_farmer_advice(request.soil_data.dict(), request.weather_data.dict(), request.language_code)
        return json.loads(advice)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {e}")

@app.post("/crop-recommendation", summary="Crop Recommendation", description="Recommends crops based on soil and weather data, including Vedic override and multilingual translation.")
async def crop_recommendation(request: AdviceRequest):
    try:
        advice = generate_farmer_advice(request.soil_data.dict(), request.weather_data.dict(), request.language_code)
        return json.loads(advice)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {e}")
