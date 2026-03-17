from fastapi import FastAPI, HTTPException
from pylantic import BaseModel
from typing import List, Optional
import sqlite3
import os

# Import the lazy loader
from backend.core.lazy_loader import loader

app = FastAPI(title='Krishi-Veda Local-First API')

# Database path configuration
DB_PATH = os.path.join(os.path.dirname(__file__), '../krishi_veda_offline.db')

class SoilRequest(BaseModel):
    farmer_id: int
    sensor_data: List[float]
    paksha: Optional[str] = 'waxing'

@app.get('/')
async def root():
    return {'message': 'Krishi-Veda Backend is Online', 'mode': 'Offline-First'}

@app.get('/health')
async def health_check():
    return {'status': 'healthy'}

@app.post('/api/v1/predict/soil')
async def predict_soil(request: SoilRequest):
    if len(request.sensor_data) != 8:
        raise HTTPException(status_code=400, detail='Sensor data must contain exactly 8 features.')
    
    try:
        # Accessing soil_service via the lazy loader to conserve RAM
        result = loader.soil_service.predict(
            farmer_id=request.farmer_id, 
            sensor_data=request.sensor_data, 
            current_paksha=request.paksha
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get('/api/v1/crops/{state_code}')
async def get_regional_crops(state_code: str):
    """Queries local SQLite for regional crop data using memory-efficient fetching."""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Use explicit column selection to minimize memory overhead
        cursor.execute('SELECT soil_type, primary_crops FROM regional_data WHERE state_code = ?', (state_code.upper(),))
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            raise HTTPException(status_code=404, detail=f'No data found for state: {state_code}')
            
        return {
            'state': state_code.upper(),
            'soil_type': row['soil_type'],
            'primary_crops': row['primary_crops']
        }
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=f'Database error: {str(e)}')