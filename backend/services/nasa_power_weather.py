"""
NASA POWER API integration for real weather data.
Free, no API key required. Returns temperature, rainfall, humidity.
Works offline with fallback values for common Indian regions.
"""
import requests
from datetime import datetime, timedelta

# Offline fallback: monthly averages for Indian agricultural regions
REGIONAL_FALLBACK = {
    'Assam': {'temperature_c': 26, 'rainfall_mm': 250, 'humidity': 80},
    'Bihar': {'temperature_c': 28, 'rainfall_mm': 100, 'humidity': 65},
    'Punjab': {'temperature_c': 30, 'rainfall_mm': 40, 'humidity': 50},
    'Tamil Nadu': {'temperature_c': 32, 'rainfall_mm': 80, 'humidity': 70},
    'Uttar Pradesh': {'temperature_c': 30, 'rainfall_mm': 60, 'humidity': 55},
    'West Bengal': {'temperature_c': 28, 'rainfall_mm': 180, 'humidity': 75},
    'Maharashtra': {'temperature_c': 30, 'rainfall_mm': 70, 'humidity': 60},
    'Karnataka': {'temperature_c': 28, 'rainfall_mm': 90, 'humidity': 65},
    'Gujarat': {'temperature_c': 32, 'rainfall_mm': 30, 'humidity': 45},
    'Rajasthan': {'temperature_c': 34, 'rainfall_mm': 20, 'humidity': 35},
    'Kerala': {'temperature_c': 28, 'rainfall_mm': 300, 'humidity': 85},
    'Odisha': {'temperature_c': 30, 'rainfall_mm': 150, 'humidity': 70},
}

# Moon phase (paksha) approximation
def get_paksha():
    """Approximate paksha based on lunar day."""
    today = datetime.now()
    # Simple approximation: new moon to full moon = waxing (Shukla)
    # Full moon to new moon = waning (Krishna)
    new_moon = datetime(2026, 5, 17)  # Approximate new moon
    days_since_new = (today - new_moon).days % 30
    return "waxing" if days_since_new < 15 else "waning"


def get_weather(lat: float, lon: float) -> dict:
    """
    Fetch weather data from NASA POWER API.
    Falls back to regional averages if offline.
    
    Returns:
        {
            'temperature_c': float,
            'rainfall_mm': float,
            'humidity': float,
            'paksha': str,
            'source': 'nasa_power' or 'regional_fallback'
        }
    """
    try:
        today = datetime.now()
        start = (today - timedelta(days=30)).strftime('%Y%m%d')
        end = today.strftime('%Y%m%d')
        
        params = {
            'parameters': 'T2M,PRECTOTCORR,RH2M',
            'community': 'AG',
            'longitude': lon,
            'latitude': lat,
            'start': start,
            'end': end,
            'format': 'JSON'
        }
        
        resp = requests.get(
            'https://power.larc.nasa.gov/api/temporal/daily/point',
            params=params,
            timeout=15
        )
        
        if resp.status_code == 200:
            data = resp.json()
            props = data.get('properties', {}).get('parameter', {})
            
            temps = [v for v in props.get('T2M', {}).values() if v > -900]
            rains = [v for v in props.get('PRECTOTCORR', {}).values() if v > -900]
            humids = [v for v in props.get('RH2M', {}).values() if v > -900]
            
            avg_temp = sum(temps) / len(temps) if temps else 28
            total_rain = sum(rains) if rains else 80
            avg_humid = sum(humids) / len(humids) if humids else 65
            
            return {
                'temperature_c': round(avg_temp, 1),
                'rainfall_mm': round(total_rain, 1),
                'humidity': round(avg_humid, 1),
                'paksha': get_paksha(),
                'source': 'nasa_power'
            }
    except Exception:
        pass
    
    # Fallback: try to guess region from coordinates
    region = 'Assam'  # Default for Northeast India
    if 20 <= lat <= 28 and 68 <= lon <= 76:
        region = 'Gujarat'
    elif 25 <= lat <= 32 and 74 <= lon <= 82:
        region = 'Uttar Pradesh'
    elif 10 <= lat <= 20 and 74 <= lon <= 80:
        region = 'Karnataka'
    elif 8 <= lat <= 13 and 74 <= lon <= 78:
        region = 'Kerala'
    
    fallback = REGIONAL_FALLBACK.get(region, REGIONAL_FALLBACK['Assam'])
    fallback['paksha'] = get_paksha()
    fallback['source'] = 'regional_fallback'
    return fallback


if __name__ == '__main__':
    # Test for Silchar (24.81, 92.80)
    result = get_weather(24.81, 92.80)
    print('Silchar weather:', result)
    
    # Test for Delhi
    result2 = get_weather(28.61, 77.23)
    print('Delhi weather:', result2)
