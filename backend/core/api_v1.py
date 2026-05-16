# Krishi-Veda API v1 Routes
from fastapi import APIRouter, Query
from backend.core.slm_engine import generate_advice, get_slm_status
from backend.services.soil_health_service import analyze_soil
from backend.services.regional_analysis_service import get_crop_recommendation, get_panchgavya_recipe
from vedic_engine.astrological_calendars import get_paksha, get_farming_muhurta

router = APIRouter(prefix='/api/v1')

@router.get('/advice')
def farm_advice(ph: float = 6.5, n: float = 35, p: float = 28, k: float = 40,
                moisture: float = 50, om: float = 2.0, ec: float = 0.3, temp: float = 28,
                soil_type: str = 'loamy'):
    sensor = [ph, n, p, k, moisture, om, ec, temp]
    paksha, _ = get_paksha()
    return generate_advice(sensor, soil_type, paksha)

@router.get('/soil')
def soil_health(ph: float = 6.5, n: float = 35, p: float = 28, k: float = 40,
                moisture: float = 50, om: float = 2.0):
    return analyze_soil([ph, n, p, k, moisture, om, 0.3, 28])

@router.get('/crop')
def crop_recommendation(ph: float = 6.5, season: str = 'kharif'):
    return get_crop_recommendation(ph, season)

@router.get('/panchgavya')
def panchgavya():
    return get_panchgavya_recipe()

@router.get('/muhurta')
def farming_muhurta():
    return get_farming_muhurta()

@router.get('/status')
def slm_status():
    return get_slm_status()
