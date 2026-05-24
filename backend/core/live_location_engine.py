"""
Live Location + Real-Time Vedic Analysis Engine
===============================================
Gets actual GPS location → Fetches hyperlocal weather → Analyzes with Vedic algorithms
→ Predicts based on Kala-Chakra + actual soil + real climate patterns
"""

import json, time, os, math
from typing import Dict, Optional, Tuple
from dataclasses import dataclass

# Try to get Android GPS via Termux
try:
    import androidhelper
    droid = androidhelper.Android()
    HAS_ANDROID = True
except:
    HAS_ANDROID = False

@dataclass
class GeoLocation:
    lat: float
    lon: float
    accuracy: float = 0.0
    source: str = "unknown"
    village: str = ""
    district: str = ""
    state: str = "Assam"

class LiveLocationEngine:
    """
    Gets real GPS location and hyperlocal data for Vedic analysis.
    
    Layers:
    1. GPS → lat/lon
    2. Reverse geocode → village/district  
    3. Hyperlocal weather → actual temp/rain/humidity
    4. Soil type → from ISRO Bhuvan/regional maps
    5. Vedic analysis → Kala-Chakra + Ritu + Nakshatra
    """
    
    def __init__(self):
        self.last_location: Optional[GeoLocation] = None
        self.last_weather: Dict = {}
        self.location_history = []
    
    def get_gps_location(self) -> GeoLocation:
        """Get real GPS coordinates from Android."""
        if HAS_ANDROID:
            try:
                droid.startLocating()
                time.sleep(3)
                loc = droid.readLocation()
                droid.stopLocating()
                
                if loc and loc.result:
                    data = loc.result
                    gps = data.get('gps', {}) or data.get('network', {}) or data
                    
                    lat = gps.get('latitude', 0)
                    lon = gps.get('longitude', 0)
                    acc = gps.get('accuracy', 0)
                    
                    if lat != 0 and lon != 0:
                        gl = GeoLocation(
                            lat=round(lat, 4),
                            lon=round(lon, 4),
                            accuracy=acc,
                            source="gps",
                        )
                        self.last_location = gl
                        self.location_history.append(gl)
                        return gl
            except Exception as e:
                print(f"GPS error: {e}")
        
        # Fallback: IP-based coarse location
        try:
            import urllib.request
            resp = urllib.request.urlopen('http://ip-api.com/json/', timeout=5)
            data = json.loads(resp.read())
            if data.get('lat'):
                gl = GeoLocation(
                    lat=data['lat'],
                    lon=data['lon'],
                    source="ip",
                    village=data.get('city', ''),
                    district=data.get('regionName', ''),
                    state=data.get('country', 'Assam'),
                )
                self.last_location = gl
                return gl
        except:
            pass
        
        # Ultimate fallback: Silchar
        return GeoLocation(lat=24.81, lon=92.80, source="default", 
                          village="Silchar", district="Cachar", state="Assam")
    
    def reverse_geocode(self, lat: float, lon: float) -> Dict:
        """Get village/district from coordinates."""
        try:
            import urllib.request
            url = f'https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lon}&format=json'
            req = urllib.request.Request(url, headers={'User-Agent': 'KrishiVeda/1.0'})
            resp = urllib.request.urlopen(req, timeout=5)
            data = json.loads(resp.read())
            
            address = data.get('address', {})
            return {
                'village': address.get('village', address.get('town', address.get('city', ''))),
                'district': address.get('state_district', address.get('county', '')),
                'state': address.get('state', 'Assam'),
                'country': address.get('country', 'India'),
                'display_name': data.get('display_name', ''),
            }
        except:
            return {'village': '', 'district': 'Cachar', 'state': 'Assam'}
    
    def get_hyperlocal_weather(self, lat: float, lon: float) -> Dict:
        """Get actual weather at exact GPS coordinates."""
        try:
            import urllib.request
            url = (f'https://api.open-meteo.com/v1/forecast?'
                   f'latitude={lat}&longitude={lon}'
                   f'&current=temperature_2m,relative_humidity_2m,rain,wind_speed_10m,soil_moisture_0_to_7cm,soil_temperature_0_to_7cm'
                   f'&daily=precipitation_sum,temperature_2m_max,temperature_2m_min'
                   f'&timezone=Asia/Kolkata&forecast_days=3')
            
            resp = urllib.request.urlopen(url, timeout=10)
            data = json.loads(resp.read())
            
            current = data.get('current', {})
            daily = data.get('daily', {})
            
            weather = {
                'temperature_c': current.get('temperature_2m', 28),
                'humidity_pct': current.get('relative_humidity_2m', 70),
                'rainfall_mm': current.get('rain', 0),
                'wind_speed_kmh': current.get('wind_speed_10m', 5),
                'soil_moisture': current.get('soil_moisture_0_to_7cm', 0.3),
                'soil_temp_c': current.get('soil_temperature_0_to_7cm', 26),
                'source': f'Open-Meteo ({lat:.2f},{lon:.2f})',
                'forecast': {
                    'today_max': daily.get('temperature_2m_max', [30])[0] if daily.get('temperature_2m_max') else 30,
                    'today_min': daily.get('temperature_2m_min', [22])[0] if daily.get('temperature_2m_min') else 22,
                    'rain_next_3days': sum(daily.get('precipitation_sum', [0])[:3]),
                }
            }
            
            self.last_weather = weather
            return weather
        except:
            return {
                'temperature_c': 28, 'humidity_pct': 70,
                'rainfall_mm': 0, 'source': 'default',
            }
    
    def get_soil_type(self, lat: float, lon: float) -> str:
        """Estimate soil type from location + ISRO soil map data."""
        # Barak Valley region mapping (approximate)
        if 24.6 <= lat <= 25.0 and 92.5 <= lon <= 93.0:
            # Silchar region
            if lon > 92.75:
                return "alluvial"  # Barak river plains
            else:
                return "laterite"  # Foothills
        
        # Brahmaputra valley
        if 26.0 <= lat <= 27.5 and 90.0 <= lon <= 95.0:
            return "alluvial"
        
        # General: return alluvial as most common in Assam
        return "alluvial"
    
    def vedic_location_analysis(self, lat: float, lon: float) -> Dict:
        """
        Complete Vedic analysis based on actual location.
        Uses Kala-Chakra, Jyotisha principles.
        """
        import sys
        sys.path.insert(0, os.path.expanduser("~/vedic-inference-engine"))
        from vedic_inference_engine import KalaChakra, Ritu, VedicDate
        
        kala = KalaChakra()
        
        # Current Vedic time
        doy = time.localtime().tm_yday
        ritu = kala.ritu_for_day(doy)
        today = VedicDate(ritu=ritu, day_of_year=doy)
        encoding = kala.encode(today)
        
        # Determine if sowing/harvesting is favorable
        ritu_names = {
            Ritu.VASANTA: "Vasanta (Spring) — Good for nursery, vegetables",
            Ritu.GRISHMA: "Grishma (Summer) — Sali rice nursery, irrigation needed",
            Ritu.VARSHA: "Varsha (Monsoon) — BEST for paddy transplanting",
            Ritu.SHARAD: "Sharad (Autumn) — Harvest, Rabi preparation",
            Ritu.HEMANTA: "Hemanta (Pre-winter) — Rabi sowing, mustard",
            Ritu.SHISHIRA: "Shishira (Winter) — Boro rice, protect from cold",
        }
        
        # Moon phase (simplified — actual calculation needs panchanga)
        moon_day = doy % 30
        if moon_day <= 15:
            paksha = "Shukla (Waxing) — Favorable for sowing"
        else:
            paksha = "Krishna (Waning) — Favorable for harvesting"
        
        return {
            'ritu': ritu.name,
            'ritu_meaning': ritu_names.get(ritu, ''),
            'paksha': paksha,
            'day_of_year': doy,
            'kala_chakra_encoding': [round(v, 3) for v in encoding[:4]],
            'sowable_crops': self._sowable_crops(ritu),
            'prediction': self._vedic_prediction(ritu, lat, lon),
        }
    
    def _sowable_crops(self, ritu) -> list:
        """Crops suitable for current Ritu in Assam."""
        from vedic_inference_engine.kala_chakra import Ritu as R
        crop_map = {
            R.VASANTA: ["Summer vegetables", "Maize", "Jute", "Cucumber"],
            R.GRISHMA: ["Sali Rice (nursery)", "Okra", "Brinjal", "Green gram"],
            R.VARSHA: ["Sali Rice (transplant)", "Black gram", "Finger millet", "Colocasia"],
            R.SHARAD: ["Mustard", "Potato", "Tomato", "Cabbage"],
            R.HEMANTA: ["Wheat", "Mustard", "Winter vegetables", "Pea"],
            R.SHISHIRA: ["Boro Rice (nursery)", "Lentil", "Chickpea", "Sunflower"],
        }
        return crop_map.get(ritu, ["Consult local KVK"])
    
    def _vedic_prediction(self, ritu, lat: float, lon: float) -> str:
        """Vedic prediction based on location + season + soil."""
        predictions = {
            'VASANTA': "Spring brings new growth. Soil warming up. Good for land preparation. Apply Panchgavya to activate soil microbes.",
            'GRISHMA': f"Summer heat at {lat:.1f}°N. Irrigation critical. Mulch heavily. Monitor for pests — they multiply in heat. Neem-Astra recommended.",
            'VARSHA': "Monsoon energy peaks. Maximum growth phase. Ensure drainage. Paddy transplanting ideal. Watch for fungal diseases — apply buttermilk spray.",
            'SHARAD': "Post-monsoon clarity. Harvest window. Grains must be dried properly. Prepare fields for Rabi. Soil testing recommended now.",
            'HEMANTA': f"Cooling trend. Dew formation helps crops. Rabi sowing window open. Soil moisture retained from monsoon. Minimal irrigation needed.",
            'SHISHIRA': "Winter dormancy phase. Protect sensitive crops from cold. Boro rice nursery preparation. Light irrigation only — avoid waterlogging.",
        }
        return predictions.get(ritu.name if hasattr(ritu, 'name') else str(ritu), "Follow natural rhythms.")


if __name__ == "__main__":
    engine = LiveLocationEngine()
    
    print("॥ Live Location + Vedic Analysis Engine ॥\n")
    
    # Get GPS
    loc = engine.get_gps_location()
    print(f"📍 Location: {loc.lat}, {loc.lon}")
    print(f"   Source: {loc.source}, Accuracy: {loc.accuracy}m\n")
    
    # Reverse geocode
    geo = engine.reverse_geocode(loc.lat, loc.lon)
    print(f"🏘 Village: {geo.get('village', 'Unknown')}")
    print(f"   District: {geo.get('district', 'Unknown')}")
    print(f"   State: {geo.get('state', 'Assam')}\n")
    
    # Weather
    weather = engine.get_hyperlocal_weather(loc.lat, loc.lon)
    print(f"🌤 Weather: {weather['temperature_c']}°C, {weather['humidity_pct']}% humidity")
    print(f"   Rain: {weather['rainfall_mm']}mm, Soil moisture: {weather['soil_moisture']}")
    
    # Soil
    soil = engine.get_soil_type(loc.lat, loc.lon)
    print(f"\n🌱 Estimated Soil: {soil}")
    
    # Vedic analysis
    vedic = engine.vedic_location_analysis(loc.lat, loc.lon)
    print(f"\n🕉 Vedic Analysis:")
    print(f"   Ritu: {vedic['ritu_meaning']}")
    print(f"   Paksha: {vedic['paksha']}")
    print(f"   Sowable: {', '.join(vedic['sowable_crops'])}")
    print(f"\n   Prediction: {vedic['prediction']}")
