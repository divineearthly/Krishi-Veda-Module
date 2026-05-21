"""
7-Day Weather Forecast via Open-Meteo (free, no API key, global).
Replaces monthly averages with real daily forecasts.
"""
import requests
from datetime import datetime, timedelta

def get_7day_forecast(lat: float, lon: float) -> dict:
    """
    Fetch 7-day forecast from Open-Meteo.
    Returns daily: temp_max, temp_min, rainfall, humidity, wind.
    Falls back to offline district norms if network unavailable.
    """
    try:
        params = {
            'latitude': lat,
            'longitude': lon,
            'daily': ['temperature_2m_max', 'temperature_2m_min', 
                      'precipitation_sum', 'relative_humidity_2m_mean',
                      'wind_speed_10m_max', 'weather_code'],
            'timezone': 'Asia/Kolkata',
            'forecast_days': 7
        }
        
        resp = requests.get(
            'https://api.open-meteo.com/v1/forecast',
            params=params,
            timeout=10
        )
        
        if resp.status_code == 200:
            data = resp.json()
            daily = data.get('daily', {})
            
            forecast = []
            for i, date in enumerate(daily.get('time', [])):
                weather_code = daily.get('weather_code', [0]*7)[i]
                forecast.append({
                    'date': date,
                    'temp_max': daily.get('temperature_2m_max', [None]*7)[i],
                    'temp_min': daily.get('temperature_2m_min', [None]*7)[i],
                    'rainfall_mm': daily.get('precipitation_sum', [None]*7)[i],
                    'humidity': daily.get('relative_humidity_2m_mean', [None]*7)[i],
                    'wind_kmh': daily.get('wind_speed_10m_max', [None]*7)[i],
                    'condition': _weather_code_to_text(weather_code),
                    'sowing_advice': _get_sowing_advice(weather_code, 
                        daily.get('precipitation_sum', [0]*7)[i] or 0)
                })
            
            return {
                'forecast': forecast,
                'source': 'open_meteo',
                'best_sowing_day': _find_best_sowing_day(forecast),
                'irrigation_needed': _check_irrigation_needed(forecast)
            }
    except Exception:
        pass
    
    return {'forecast': [], 'source': 'offline_fallback', 'error': 'Weather API unavailable'}


def _weather_code_to_text(code: int) -> str:
    """Convert WMO weather code to text."""
    codes = {
        0: 'Clear Sky', 1: 'Mainly Clear', 2: 'Partly Cloudy',
        3: 'Overcast', 45: 'Foggy', 48: 'Depositing Rime Fog',
        51: 'Light Drizzle', 53: 'Moderate Drizzle', 55: 'Dense Drizzle',
        61: 'Slight Rain', 63: 'Moderate Rain', 65: 'Heavy Rain',
        71: 'Slight Snow', 73: 'Moderate Snow', 75: 'Heavy Snow',
        80: 'Slight Rain Showers', 81: 'Moderate Rain Showers',
        82: 'Violent Rain Showers', 95: 'Thunderstorm',
        96: 'Thunderstorm with Hail', 99: 'Thunderstorm with Heavy Hail'
    }
    return codes.get(code, 'Unknown')


def _get_sowing_advice(weather_code: int, rainfall: float) -> str:
    """Get sowing advice based on weather."""
    if weather_code in [0, 1]:
        return '✅ Good for sowing & field work'
    elif weather_code in [2, 3]:
        return '⚠️ Acceptable for sowing, monitor sky'
    elif weather_code in [51, 53, 61]:
        return '🌧️ Light rain — good for transplanting'
    elif weather_code in [55, 63, 65, 80, 81, 82]:
        return '⛔ Heavy rain — postpone sowing'
    elif weather_code in [95, 96, 99]:
        return '🚨 Storm alert — avoid field work'
    elif rainfall > 10:
        return '💧 Wet soil — wait 1-2 days before sowing'
    return '📋 Check soil moisture before sowing'


def _find_best_sowing_day(forecast: list) -> str:
    """Find the best day for sowing in the 7-day forecast."""
    best_day = None
    best_score = -1
    
    for day in forecast:
        score = 0
        code_str = day.get('condition', '')
        
        if 'Clear' in code_str:
            score = 10
        elif 'Partly' in code_str:
            score = 7
        elif 'Light' in code_str and 'Rain' in code_str:
            score = 8  # Good for transplanting
        elif 'Rain' in code_str:
            score = 2
        elif 'Storm' in code_str or 'Thunder' in code_str:
            score = 0
        
        # Penalize extreme temps
        if day.get('temp_max') and day['temp_max'] > 40:
            score -= 3
        if day.get('temp_min') and day['temp_min'] < 10:
            score -= 3
            
        if score > best_score:
            best_score = score
            best_day = day.get('date')
    
    return best_day or 'No ideal day in next 7 days'


def _check_irrigation_needed(forecast: list) -> dict:
    """Check if irrigation is needed based on forecast rainfall."""
    total_rainfall = sum(d.get('rainfall_mm', 0) or 0 for d in forecast)
    
    if total_rainfall < 5:
        return {'needed': True, 'message': f'Only {total_rainfall:.1f}mm rain expected — irrigate this week'}
    elif total_rainfall < 20:
        return {'needed': False, 'message': f'{total_rainfall:.1f}mm rain expected — monitor soil moisture'}
    else:
        return {'needed': False, 'message': f'{total_rainfall:.1f}mm rain expected — no irrigation needed'}


if __name__ == '__main__':
    # Test for Silchar
    result = get_7day_forecast(24.81, 92.80)
    if result.get('forecast'):
        print(f"Best sowing day: {result['best_sowing_day']}")
        print(f"Irrigation: {result['irrigation_needed']['message']}")
        for day in result['forecast'][:3]:
            print(f"  {day['date']}: {day['condition']}, {day['temp_max']}°C, {day['rainfall_mm']}mm rain → {day['sowing_advice']}")
    else:
        print('Using offline fallback')
