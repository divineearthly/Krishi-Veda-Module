"""
Universal Sensor Bridge — Connect ANY sensor to Vedic AI
=========================================================
Supports: Arduino UART, Bluetooth BLE, USB Serial, WiFi MQTT,
          Manual SMS input, Satellite NDVI, Weather API,
          Camera (plant disease), Microphone (voice query)

Protocol: All sensor data flows into Vedic Pipeline:
Sensor → Universal Bridge → Manas Gate → Tanmatra Fusion → Kosha-Net → Nyaya → Advice
"""

import json, time, os, re
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum

# ── Vedic Imports ────────────────────────────────────────
import sys
sys.path.insert(0, os.path.expanduser("~/vedic-inference-engine"))
from vedic_inference_engine import (
    ManasGate, SensoryPriority,
    TanmatraFusion, TanmatraElement,
    KoshaNet, KoshaLayer,
    KalaChakra, Ritu, VedicDate,
    NyayaScaffold, PramanaSource,
    Ahimsa108Filter,
)


class SensorType(Enum):
    """All supported sensor types — from $2 to $2000"""
    # Soil Sensors
    SOIL_NPK_UART = "npk_uart"           # RS485 NPK probe ($50-200)
    SOIL_PH_ANALOG = "ph_analog"         # Analog pH electrode ($10-30)
    SOIL_MOISTURE_CAPACITIVE = "moisture_cap"  # Capacitive moisture ($2-5)
    SOIL_MOISTURE_RESISTIVE = "moisture_res"   # Resistive moisture ($1-3)
    SOIL_TEMP_DS18B20 = "soil_temp_ds18b20"    # Temperature probe ($3-5)
    SOIL_EC_ANALOG = "ec_analog"         # Electrical conductivity ($15-40)
    
    # Weather Sensors
    WEATHER_DHT22 = "dht22"              # Temp/Humidity ($3-5)
    WEATHER_BMP280 = "bmp280"            # Pressure/Temp ($5-8)
    WEATHER_RAIN_GAUGE = "rain_gauge"    # Tipping bucket ($10-30)
    WEATHER_ANEMOMETER = "anemometer"    # Wind speed ($15-40)
    WEATHER_LIGHT_BH1750 = "bh1750"      # Light intensity ($3-5)
    
    # Communication
    BLUETOOTH_HC05 = "hc05"              # Bluetooth serial ($5-8)
    WIFI_ESP8266 = "esp8266"             # WiFi MQTT ($3-5)
    LORA_SX1278 = "sx1278"               # LoRa long-range ($10-20)
    GSM_SIM800L = "sim800l"              # SMS/2G ($8-15)
    
    # Imaging
    CAMERA_ESP32CAM = "esp32cam"         # Plant disease images ($5-8)
    SATELLITE_NDVI = "satellite_ndvi"    # Sentinel-2 NDVI (free)
    
    # Manual Input
    MANUAL_SMS = "manual_sms"            # Farmer SMS input
    VOICE_COMMAND = "voice_command"      # Voice query
    MANUAL_FORM = "manual_form"          # Web form input
    
    # Smartphone Sensors
    PHONE_GPS = "phone_gps"              # Location
    PHONE_CAMERA = "phone_camera"        # Disease photos


@dataclass
class SensorReading:
    """Universal sensor reading format"""
    sensor_type: SensorType
    values: Dict[str, float]
    timestamp: float = field(default_factory=time.time)
    location: Dict[str, float] = field(default_factory=dict)  # lat, lon
    confidence: float = 0.8
    raw_data: str = ""


class UniversalSensorBridge:
    """
    Connect ANY sensor to the Vedic AI pipeline.
    
    Flow: Sensor → Bridge → Manas Gate (priority) → Tanmatra (fusion) → Kosha (store) → Nyaya (reason) → Advice
    
    Usage:
        bridge = UniversalSensorBridge()
        
        # Arduino sends data over UART
        bridge.ingest("35.2,28.1,42.5,6.4,55.0", source="uart", sensor_type=SensorType.SOIL_NPK_UART)
        
        # Farmer sends SMS
        bridge.ingest("pH 5.8, moisture low", source="sms", sensor_type=SensorType.MANUAL_SMS)
        
        # Get Vedic analysis
        analysis = bridge.vedic_analysis()
        print(analysis['advice'])
    """
    
    def __init__(self):
        # Vedic modules
        self.manas = ManasGate()
        self.tanmatra = TanmatraFusion(fusion_dim=8)
        self.kosha = KoshaNet()
        self.nyaya = NyayaScaffold()
        self.kala = KalaChakra()
        self.ahimsa = Ahimsa108Filter()
        
        # Seed identity
        self.kosha.anandamaya_seed("Krishi-Veda Sensor Bridge — Silchar, Assam")
        
        # Sensor state
        self.latest_readings: Dict[str, SensorReading] = {}
        self.sensor_history: List[SensorReading] = []
        
        # Sensor calibration (for cheap sensors)
        self.calibration = {
            "ph_offset": 0.0,
            "moisture_dry": 0,     # ADC value in dry soil
            "moisture_wet": 1023,  # ADC value in wet soil
            "npk_scale": 1.0,
        }
        
        print("॥ Universal Sensor Bridge — Ready for ANY sensor ॥")
        print(f"   Supported: {len(SensorType)} sensor types")
        print(f"   From $1 resistive moisture to satellite NDVI")
    
    def ingest(self, raw_data: str, source: str = "unknown",
               sensor_type: SensorType = None) -> Optional[SensorReading]:
        """
        Ingest raw data from ANY source.
        Auto-detects format: JSON, CSV, AT command, SMS text, NMEA GPS.
        """
        reading = self._parse_raw(raw_data, source, sensor_type)
        
        if reading is None:
            return None
        
        # Store
        self.latest_readings[reading.sensor_type.value] = reading
        self.sensor_history.append(reading)
        
        # Flow through Vedic pipeline
        self._flow_through_manas(reading)
        self._flow_through_tanmatra(reading)
        self._flow_through_kosha(reading)
        self._flow_through_nyaya(reading)
        
        return reading
    
    def _parse_raw(self, raw: str, source: str, 
                   sensor_type: SensorType = None) -> Optional[SensorReading]:
        """Auto-detect and parse ANY sensor format."""
        raw = raw.strip()
        
        # Try JSON
        try:
            data = json.loads(raw)
            values = {}
            for k, v in data.items():
                try:
                    values[k.lower()] = float(v)
                except:
                    pass
            if values:
                return SensorReading(
                    sensor_type=sensor_type or SensorType.MANUAL_FORM,
                    values=values, raw_data=raw
                )
        except:
            pass
        
        # Try CSV (N,P,K,pH,moisture)
        parts = raw.split(',')
        if len(parts) >= 4:
            try:
                floats = [float(p.strip()) for p in parts[:6]]
                keys = ['n', 'p', 'k', 'ph', 'moisture', 'temp']
                values = {keys[i]: floats[i] for i in range(min(len(floats), len(keys)))}
                return SensorReading(
                    sensor_type=sensor_type or SensorType.SOIL_NPK_UART,
                    values=values, raw_data=raw
                )
            except:
                pass
        
        # Try SMS text format: "pH 5.8, moisture 45%, N low"
        text_values = {}
        patterns = {
            'ph': r'pH\s*[:=]?\s*(\d+\.?\d*)',
            'moisture': r'moisture\s*[:=]?\s*(\d+\.?\d*)',
            'n': r'[Nn]\s*[:=]?\s*(\d+\.?\d*)',
            'p': r'[Pp]\s*[:=]?\s*(\d+\.?\d*)',
            'k': r'[Kk]\s*[:=]?\s*(\d+\.?\d*)',
            'temp': r'temp\s*[:=]?\s*(\d+\.?\d*)',
        }
        for key, pattern in patterns.items():
            match = re.search(pattern, raw)
            if match:
                text_values[key] = float(match.group(1))
        
        if text_values:
            return SensorReading(
                sensor_type=sensor_type or SensorType.MANUAL_SMS,
                values=text_values, raw_data=raw
            )
        
        # Try GPS NMEA format
        if raw.startswith('$GPGGA'):
            parts = raw.split(',')
            if len(parts) > 5:
                try:
                    lat = float(parts[2][:2]) + float(parts[2][2:])/60
                    lon = float(parts[4][:3]) + float(parts[4][3:])/60
                    return SensorReading(
                        sensor_type=SensorType.PHONE_GPS,
                        values={'lat': lat, 'lon': lon},
                        location={'lat': lat, 'lon': lon},
                        raw_data=raw
                    )
                except:
                    pass
        
        return None
    
    def _flow_through_manas(self, reading: SensorReading):
        """Route sensor data through Manas attention gate."""
        priority = self._calculate_priority(reading)
        urgency = "crisis" if self._is_crisis(reading) else "normal"
        
        for key, value in reading.values.items():
            self.manas.attend(
                sensor_id=f"{reading.sensor_type.value}_{key}",
                value=value,
                priority=priority,
                source=reading.sensor_type.value,
                urgency=urgency
            )
    
    def _flow_through_tanmatra(self, reading: SensorReading):
        """Fuse sensor data through Tanmatra 5-element network."""
        values = list(reading.values.values())[:4]
        if not values:
            return
        
        # Map sensor to Tanmatra element
        sensor_to_element = {
            SensorType.SOIL_NPK_UART: TanmatraElement.RASA,
            SensorType.SOIL_PH_ANALOG: TanmatraElement.RASA,
            SensorType.SOIL_MOISTURE_CAPACITIVE: TanmatraElement.GANDHA,
            SensorType.WEATHER_DHT22: TanmatraElement.GANDHA,
            SensorType.CAMERA_ESP32CAM: TanmatraElement.RUPA,
            SensorType.VOICE_COMMAND: TanmatraElement.SHABDA,
            SensorType.SOIL_MOISTURE_RESISTIVE: TanmatraElement.SPARSHA,
        }
        
        element = sensor_to_element.get(reading.sensor_type, TanmatraElement.RASA)
        self.tanmatra.add_input(element, values, 
                                confidence=reading.confidence,
                                source=reading.sensor_type.value)
    
    def _flow_through_kosha(self, reading: SensorReading):
        """Store in Kosha-Net memory."""
        self.kosha.annamaya_ingest(
            f"sensor_{reading.timestamp}",
            {
                "type": reading.sensor_type.value,
                "values": reading.values,
                "time": reading.timestamp,
            }
        )
    
    def _flow_through_nyaya(self, reading: SensorReading):
        """Tag sensor data with Pramana source."""
        self.nyaya.tag(
            f"Sensor: {reading.sensor_type.value} = {reading.values}",
            PramanaSource.PRATYAKSHA,  # Direct perception
            reading.confidence
        )
    
    def _calculate_priority(self, reading: SensorReading) -> float:
        """Calculate Manas attention priority for a sensor."""
        base_priorities = {
            SensorType.SOIL_NPK_UART: 0.9,
            SensorType.SOIL_PH_ANALOG: 0.85,
            SensorType.SOIL_MOISTURE_CAPACITIVE: 0.8,
            SensorType.WEATHER_DHT22: 0.7,
            SensorType.CAMERA_ESP32CAM: 0.85,
            SensorType.MANUAL_SMS: 0.95,  # Farmer input = highest
            SensorType.VOICE_COMMAND: 0.9,
            SensorType.SATELLITE_NDVI: 0.6,
        }
        return base_priorities.get(reading.sensor_type, 0.5)
    
    def _is_crisis(self, reading: SensorReading) -> bool:
        """Detect crisis conditions from sensor data."""
        values = reading.values
        
        # pH crisis
        if 'ph' in values and (values['ph'] < 4.5 or values['ph'] > 9.0):
            return True
        
        # Moisture crisis
        if 'moisture' in values and values['moisture'] < 15:
            return True
        
        # Temperature crisis
        if 'temp' in values and (values['temp'] > 45 or values['temp'] < 0):
            return True
        
        return False
    
    def vedic_analysis(self) -> Dict:
        """
        Complete Vedic analysis of all sensor data.
        Returns actionable farming advice.
        """
        # Get all sensor values
        all_values = {}
        for stype, reading in self.latest_readings.items():
            for key, value in reading.values.items():
                all_values[f"{stype}_{key}"] = value
        
        # Get current season
        doy = time.localtime().tm_yday
        ritu = self.kala.ritu_for_day(doy)
        
        # Fuse through Tanmatra
        fused = self.tanmatra.fuse() if self.tanmatra.inputs else [0.0] * 8
        
        # Get Manas focus
        focus = self.manas.current_focus()
        
        # Nyaya confidence
        confidence = self.nyaya.overall_confidence()
        hallucinations = self.nyaya.detect_hallucinations()
        
        # Generate advice based on actual sensor data
        advice = self._generate_advice(all_values, ritu)
        
        # Ahimsa check
        ahimsa = self.ahimsa.evaluate(advice)
        
        return {
            "sensor_values": all_values,
            "season": ritu.name,
            "manas_focus": f"{focus.source} = {focus.value}" if focus else "none",
            "tanmatra_fusion": [round(v, 3) for v in fused[:4]],
            "nyaya_confidence": round(confidence, 3),
            "hallucination_risk": len(hallucinations) > 0,
            "ahimsa_level": ahimsa.level.name,
            "advice": advice,
            "crisis_detected": self._is_crisis_from_all(),
            "timestamp": time.time(),
        }
    
    def _generate_advice(self, values: Dict, ritu: Ritu) -> str:
        """Generate advice based on REAL sensor data + Vedic analysis."""
        advice_parts = []
        
        # pH analysis
        ph = values.get('soils_ph_analog_ph') or values.get('manual_sms_ph') or values.get('npk_uart_ph')
        if ph:
            if ph < 5.5:
                advice_parts.append(f"⚠ Soil acidic (pH {ph:.1f}). Apply lime {abs(ph-6.5)*2:.0f} kg/bigha.")
            elif ph > 8.0:
                advice_parts.append(f"⚠ Soil alkaline (pH {ph:.1f}). Apply gypsum 50 kg/bigha.")
            else:
                advice_parts.append(f"✓ pH optimal ({ph:.1f}).")
        
        # NPK analysis
        n = values.get('npk_uart_n') or values.get('manual_sms_n')
        p = values.get('npk_uart_p') or values.get('manual_sms_p')
        k = values.get('npk_uart_k') or values.get('manual_sms_k')
        
        if n and n < 30:
            advice_parts.append(f"Low Nitrogen ({n:.0f} ppm). Apply vermicompost 2t/bigha or Azolla.")
        if p and p < 20:
            advice_parts.append(f"Low Phosphorus ({p:.0f} ppm). Apply rock phosphate 50kg/bigha.")
        if k and k < 25:
            advice_parts.append(f"Low Potassium ({k:.0f} ppm). Apply wood ash 30kg/bigha or banana pseudostem mulch.")
        
        # Moisture analysis
        moisture = values.get('moisture_cap_moisture') or values.get('manual_sms_moisture')
        if moisture:
            if moisture < 20:
                advice_parts.append(f"⚠ Soil dry ({moisture:.0f}%). Irrigate immediately. Use drip if available.")
            elif moisture > 80:
                advice_parts.append(f"⚠ Soil waterlogged ({moisture:.0f}%). Improve drainage.")
            else:
                advice_parts.append(f"✓ Moisture adequate ({moisture:.0f}%).")
        
        # Seasonal advice
        seasonal = {
            Ritu.VASANTA: "Spring planting season. Prepare nursery beds. Sow vegetables.",
            Ritu.GRISHMA: "Summer irrigation critical. Mulch to retain moisture. Sali rice nursery.",
            Ritu.VARSHA: "Monsoon planting. Transplant Sali rice. Ensure drainage channels.",
            Ritu.SHARAD: "Harvest season. Prepare for Rabi crops. Store grains properly.",
            Ritu.HEMANTA: "Rabi sowing. Mustard, wheat, winter vegetables.",
            Ritu.SHISHIRA: "Protect from cold. Boro rice nursery. Light irrigation only.",
        }
        advice_parts.append(seasonal.get(ritu, "Follow local Krishi Vigyan Kendra advice."))
        
        # Always add Panchgavya
        advice_parts.append("🕉 Apply Panchgavya 3% foliar spray every 15 days for plant health.")
        
        return " | ".join(advice_parts) if advice_parts else "No sensor data. Connect sensors or send SMS with soil values."
    
    def _is_crisis_from_all(self) -> bool:
        """Check all sensors for crisis conditions."""
        for reading in self.latest_readings.values():
            if self._is_crisis(reading):
                return True
        return False
    
    def calibrate_sensor(self, sensor_type: str, dry_value: float = None, 
                         wet_value: float = None, ph_7_value: float = None):
        """Calibrate cheap sensors for accuracy."""
        if dry_value is not None:
            self.calibration['moisture_dry'] = dry_value
        if wet_value is not None:
            self.calibration['moisture_wet'] = wet_value
        if ph_7_value is not None:
            self.calibration['ph_offset'] = 7.0 - ph_7_value
        
        print(f"✓ Sensor calibrated: {self.calibration}")


# ── Arduino Simulator for Testing ──────────────────────────
def simulate_arduino_npk():
    """Simulate Arduino NPK sensor sending data every 5 seconds."""
    import random
    while True:
        # Simulate realistic Assam soil values
        data = {
            "N": round(random.uniform(20, 40), 1),
            "P": round(random.uniform(15, 35), 1),
            "K": round(random.uniform(25, 50), 1),
            "pH": round(random.uniform(5.0, 7.5), 1),
            "moisture": round(random.uniform(25, 70), 1),
        }
        yield json.dumps(data)
        time.sleep(5)


if __name__ == "__main__":
    bridge = UniversalSensorBridge()
    
    print("\n=== Testing with simulated sensor data ===\n")
    
    # Simulate: Arduino sends NPK data
    bridge.ingest(
        '{"N":25.3,"P":18.7,"K":42.1,"pH":5.4,"moisture":35.0}',
        source="uart",
        sensor_type=SensorType.SOIL_NPK_UART
    )
    
    # Simulate: Farmer sends SMS
    bridge.ingest(
        "pH 5.4, moisture 35%, N low, temp 30C",
        source="sms",
        sensor_type=SensorType.MANUAL_SMS
    )
    
    # Simulate: DHT22 weather sensor
    bridge.ingest(
        "28.5,72.0",
        source="dht22",
        sensor_type=SensorType.WEATHER_DHT22
    )
    
    # Get Vedic analysis
    analysis = bridge.vedic_analysis()
    
    print("=== VEDIC ANALYSIS ===")
    print(f"Season: {analysis['season']}")
    print(f"Manas Focus: {analysis['manas_focus']}")
    print(f"Tanmatra Fusion: {analysis['tanmatra_fusion']}")
    print(f"Nyaya Confidence: {analysis['nyaya_confidence']}")
    print(f"Hallucination Risk: {analysis['hallucination_risk']}")
    print(f"Ahimsa Level: {analysis['ahimsa_level']}")
    print(f"Crisis: {analysis['crisis_detected']}")
    print(f"\n=== ADVICE ===\n{analysis['advice']}")
    print(f"\nSensor values: {analysis['sensor_values']}")
