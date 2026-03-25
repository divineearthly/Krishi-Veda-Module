# Krishi-Veda Global Engine v2.1 — Offline Sovereign Architecture

An offline-first, hybrid intelligence platform for rural farmers in India.
Combines 8 Vedic Krishi-Sutras (compiled C++ .so), 4-bit quantized SLM (Qwen2.5-0.5B),
NASA Sentinel-2 NDVI, OpenWeather, Ahimsa-108 Protocol, and a virtual UART sensor listener.

## Architecture

- **Backend**: FastAPI (Python) on port 5000
- **Frontend**: Farmer-friendly PWA — Hindi, Bengali, Assamese, English — big icon UI
- **Database**: SQLite (`krishi_veda_offline.db`) — farmer profiles, regional data, weather/NDVI cache
- **Vedic Kernels**: C++ `.so` compiled with `-Os` for size (`vedic_engine/kernels/vedic_kernels.so`)
- **SLM**: Qwen2.5-0.5B-Instruct loaded 4-bit quantized via bitsandbytes (background lazy load)
- **Sync Manager**: 10km-radius data fetch + SQLite cache (`backend/core/sync_manager.py`)
- **UART Listener**: WebSocket real-time N-P-K sensor receiver

## Project Layout

```
backend/
  main.py                          - All API routes + startup
  core/
    vedic_kernels_bridge.py        - ctypes → vedic_kernels.so (8 sutras)
    slm_engine.py                  - 4-bit SLM, Vedic-grounded, Ahimsa-108 enforced
    sync_manager.py                - NASA Sentinel-2 + OpenWeather offline cache
    uart_listener.py               - Virtual UART WebSocket listener
    lazy_loader.py                 - TFLite model lazy loader
  services/
    slm_reasoning_engine.py        - Rule-based Vedic plan (fast, always-on)
    external_intel_service.py      - Live weather + NDVI (used when cache is cold)

vedic_engine/kernels/
  vedic_kernels.cpp                - 8 Krishi-Sutras in C++ (-Os optimized)
  vedic_kernels.so                 - Compiled host binary
  vedic_kernels_armv7.so           - Cross-compiled for Raspberry Pi (via Makefile)
  Makefile                         - Build rules: host (-Os), arm (-Os -march=armv7-a), arm6

frontend/
  index.html                       - Farmer dashboard (4 languages, big icons)

localization/dicts/
  hi.json  bn.json  as.json  ta.json   - Hindi, Bengali, Assamese, Tamil

krishi_veda_offline.db             - SQLite: farmers, regional_data, weather_cache, ndvi_cache, sync_log
```

## The 8 Krishi-Sutras (C++ → Python bridge)

| Sutra | C Function | Agricultural Role |
|-------|-----------|-------------------|
| Anurupyena | `anurupyena_scale()` | Proportional NPK scaling |
| Nikhilam | `nikhilam_deficit()` | Complement-based NPK deficit |
| Paravartya | `paravartya_ph_inversion()` | pH→liming recommendation |
| Ekadhikena | `ekadhikena_next_stage()` | Growth milestone projection |
| Urdhva-Tiryak | `urdhva_yield_score()` | Cross-multiply yield matrix |
| Vilokanam | `vilokanam_anomaly()` | Sensor anomaly detection |
| Gunakasamuccaya | `gunakasamuccaya_wellness()` | Geometric wellness index |
| Shunyam | `shunyam_stress_balance()` | Residual stress after amendment |

## Ahimsa-108 Protocol

Enforced at TWO levels:
1. **Rule-based engine** (`slm_reasoning_engine.py`): instant fallback
2. **SLM engine** (`slm_engine.py`): Vedic kernels queried FIRST, result injected as ground truth into the SLM prompt

When `stress_code ≥ 75` → Panchgavya + Nadep composting prescribed.

## Compiler Notes

Host build: `g++ -Os -fPIC -shared -std=c++14 -lm`
ARM build:   `arm-linux-gnueabihf-g++ -Os -march=armv7-a -mfpu=neon -mfloat-abi=hard -fPIC -shared`
(ARM cross-compilation requires `apt install gcc-arm-linux-gnueabihf`)

## Key API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/v1/plan` | Full Vedic plan (add `"use_slm":true` for SLM advice) |
| POST | `/api/v1/sync` | Cache NASA + OpenWeather for 10km radius |
| POST | `/api/v1/slm/advice` | SLM-only advice (Vedic-grounded) |
| GET | `/api/v1/slm/status` | SLM load status |
| GET | `/api/v1/weather?lat=&lon=` | Weather (cache → live → heuristic) |
| GET | `/api/v1/ndvi?lat=&lon=` | NDVI crop health |
| WS | `/ws/uart` | Real N-P-K UART frames (JSON or CSV) |
| WS | `/ws/uart/simulate` | Virtual sensor stream |
| GET | `/api/v1/uart/latest` | Latest sensor reading |

## Environment Variables

| Variable | Description |
|----------|-------------|
| `OPENWEATHER_API_KEY` | OpenWeather API (heuristic fallback if missing) |
| `NASA_EARTHDATA_TOKEN` | NASA EarthData token (synthetic NDVI if missing) |
| `SLM_CACHE_DIR` | Override model cache dir (default: `~/.cache/krishi_veda_slm`) |

## Run

```bash
uvicorn backend.main:app --host 0.0.0.0 --port 5000 --reload \
  --reload-dir backend --reload-dir frontend
```

## Recompile Kernels

```bash
cd vedic_engine/kernels
make host          # x86_64 with -Os
make arm           # ARMv7-a (Raspberry Pi 2/3) — needs cross-compiler
make arm6          # ARMv6 (Raspberry Pi Zero)
```
