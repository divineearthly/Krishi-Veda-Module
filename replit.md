# Krishi-Veda Global Engine v2.0

An offline-first, hybrid intelligence platform for rural farmers in India. Combines 8 Vedic Krishi-Sutras (compiled C++ shared library), external intelligence (OpenWeather, NASA NDVI), the Ahimsa-108 Protocol, a virtual UART N-P-K sensor listener, and a farmer-friendly multi-language dashboard.

## Architecture

- **Backend**: FastAPI (Python) on port 5000
- **Frontend**: Farmer-friendly PWA with big icons, served by FastAPI
- **Database**: SQLite (`krishi_veda_offline.db`) — farmer profiles, regional data
- **Vedic Kernels**: C++ shared library (`vedic_engine/kernels/vedic_kernels.so`)
- **SLM Reasoning**: Rule-based engine (`backend/services/slm_reasoning_engine.py`)
- **External Intel**: OpenWeather + NASA NDVI proxy (`backend/services/external_intel_service.py`)
- **UART Listener**: WebSocket sensor data receiver (`backend/core/uart_listener.py`)

## Project Layout

```
backend/
  main.py                          - FastAPI entry point, all API routes
  core/
    lazy_loader.py                 - Memory-efficient model loader
    vedic_kernels_bridge.py        - ctypes bridge to vedic_kernels.so
    uart_listener.py               - Virtual UART WebSocket listener
  services/
    soil_health.py                 - Legacy TFLite soil prediction
    slm_reasoning_engine.py        - SLM brain + Ahimsa-108 Protocol
    external_intel_service.py      - OpenWeather + NASA NDVI
    vedic_sutra_service.py         - (placeholder)

vedic_engine/kernels/
  vedic_kernels.cpp                - 8 Krishi-Sutras in C++
  vedic_kernels.so                 - Compiled shared library (g++ -O3 -fPIC -shared)

frontend/
  index.html                       - Farmer dashboard (Hindi/Bengali/Assamese/English)
  manifest.json                    - PWA manifest
  sw.js                            - Service worker

localization/dicts/
  hi.json                          - Hindi
  bn.json                          - Bengali
  as.json                          - Assamese (new)
  ta.json                          - Tamil

krishi_veda_offline.db             - SQLite database
```

## The 8 Krishi-Sutras

| # | Sutra | Agricultural Function |
|---|-------|-----------------------|
| 1 | Anurupyena | Proportional NPK scaling |
| 2 | Nikhilam | Complement-based deficit computation |
| 3 | Paravartya | pH inversion → liming recommendation |
| 4 | Ekadhikena | Next growth stage milestone |
| 5 | Urdhva-Tiryak | Cross-multiply yield matrix |
| 6 | Vilokanam | Sensor anomaly detection |
| 7 | Gunakasamuccaya | Geometric wellness index |
| 8 | Shunyam | Residual stress balance |

## Ahimsa-108 Protocol

When `stress_code ≥ 75` (sacred 108 normalized to soil scale):
- Chemical inputs are halted
- Panchgavya (cow-based organic amendment) is prescribed
- Nadep/Vermicomposting recommended for severe cases

## Key API Endpoints

- `POST /api/v1/plan` — Full Vedic agricultural plan from location + sensor data
- `GET /api/v1/weather?lat=&lon=` — Weather intelligence (OpenWeather / heuristic fallback)
- `GET /api/v1/ndvi?lat=&lon=` — NASA NDVI crop health index
- `GET /api/v1/crops/{state_code}` — Regional crop data from SQLite
- `WS /ws/uart` — Real UART N-P-K sensor data (JSON or CSV frames)
- `WS /ws/uart/simulate` — Virtual sensor stream for demos
- `GET /api/v1/uart/latest` — Latest sensor reading

## Environment Variables

- `OPENWEATHER_API_KEY` — OpenWeather API key (optional; heuristic fallback used if missing)
- `NASA_EARTHDATA_TOKEN` — NASA EarthData token (optional; synthetic NDVI if missing)

## Running

```
uvicorn backend.main:app --host 0.0.0.0 --port 5000 --reload
```

## Recompile Vedic Kernels

```
g++ -O3 -fPIC -shared -std=c++14 -o vedic_engine/kernels/vedic_kernels.so vedic_engine/kernels/vedic_kernels.cpp -lm
```

## Deployment

Uses gunicorn: `gunicorn --bind=0.0.0.0:5000 --reuse-port backend.main:app`
