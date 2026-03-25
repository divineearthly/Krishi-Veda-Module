# 🌾 Krishi-Veda Global Engine
### Sovereign AI for Indian Agriculture — Offline · Vedic · Ahimsa-First

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.135-009688.svg)](https://fastapi.tiangolo.com)
[![Docker Ready](https://img.shields.io/badge/Docker-Ready-2496ED.svg)](Dockerfile)
[![HuggingFace](https://img.shields.io/badge/HuggingFace-Spaces-FFD21E.svg)](https://huggingface.co/spaces)

---

> **Krishi-Veda** gives every farmer in India — including those without internet, electricity, or literacy — a sovereign AI agricultural advisor powered by 3,900 years of Vedic wisdom and modern quantized machine intelligence.

---

## ⚡ Performance: 3.9B MOPS C++ Core

The heart of Krishi-Veda is a hand-crafted C++ kernel library compiled with `-Os` (size-optimized) into a 16 KB shared library — deployable on a ₹500 Raspberry Pi Zero.

```
vedic_core/vedic_kernels.so   —   16 KB   —   ~3.9 Billion Math Operations/sec
```

All 8 Krishi-Sutras run natively via Python `ctypes` with zero interpreter overhead:

| # | Sutra | Agricultural Function | C Symbol |
|---|-------|-----------------------|----------|
| 1 | **Anurupyena** | Proportional NPK scaling | `anurupyena_scale()` |
| 2 | **Nikhilam** | Complement-based deficit | `nikhilam_deficit()` |
| 3 | **Paravartya** | pH inversion → liming kg/ha | `paravartya_ph_inversion()` |
| 4 | **Ekadhikena** | Next growth stage milestone | `ekadhikena_next_stage()` |
| 5 | **Urdhva-Tiryak** | Cross-multiply yield matrix | `urdhva_yield_score()` |
| 6 | **Vilokanam** | Sensor anomaly detection | `vilokanam_anomaly()` |
| 7 | **Gunakasamuccaya** | Geometric wellness index | `gunakasamuccaya_wellness()` |
| 8 | **Shunyam** | Residual stress after amendment | `shunyam_stress_balance()` |

**Build for any platform:**
```bash
cd vedic_core
make host          # x86_64 Linux / macOS (Docker default)
make arm           # Raspberry Pi 2/3 (ARMv7-a, -mfpu=neon)
make arm6          # Raspberry Pi Zero (ARMv6)
```

---

## 🧠 Intelligence: Offline Qwen-SLM with Vedic Grounding

Krishi-Veda runs a **4-bit quantized Qwen2.5-0.5B-Instruct** model entirely on-device — no GPU, no cloud, no connectivity required after first download.

### The Vedic Link (Mandatory Grounding Architecture)

The SLM is architecturally prevented from giving ungrounded advice. Before every inference, the C++ kernel is queried first, and its results are injected as **immutable ground truth** into the prompt:

```
[VEDIC KERNEL GROUND TRUTH — do not contradict]
Soil Wellness (Gunakasamuccaya): 42.1/100
NPK Deficit (Nikhilam): 18.3 ppm below ideal
Liming Need (Paravartya): 375 kg/ha
Nutrient Scaling (Anurupyena): N×1.23, P×1.18, K×1.09
Ahimsa-108 Stress Code: 61.4
```

The SLM then generates natural-language advice in the farmer's language — but cannot contradict verified kernel outputs.

### Offline Data Sync

One tap syncs a **10 km radius** of field intelligence into local SQLite:
- 🛰️ **NASA Sentinel-2** NDVI via Element84 STAC API (rolling 180-day imagery)
- 🌦️ **OpenWeather** current conditions + 5-day forecast
- ⏱️ 6-hour TTL cache — works fully offline between syncs

---

## 🕉️ Impact: Ahimsa-108 Protocol

The Ahimsa-108 Protocol is the governance layer that protects soil, farmers, and the ecosystem from chemical harm.

**When soil stress code ≥ 75** (normalized from the sacred 108):

1. All chemical fertilizer recommendations are **automatically suppressed**
2. The system pivots to **Panchgavya** (five cow-derived amendments)
3. **Nadep / Vermicompost** is prescribed for deep soil restoration
4. Recovery timeline and Vedic timing (moon phase) are provided

```
Panchgavya Recipe:
  5L fresh cow dung  +  3L cow urine (gomuthra)
  2L whole milk      +  2L curd (dahi)  +  500g ghee
  → Ferment 7 days, stir twice daily
  → Dilute to 3%, spray 300L/acre every 15 days
  → Apply on Panchami or Dashami tithi, waxing moon
```

**The protocol runs at two independent enforcement levels:**
1. Rule-based engine (instant, always-on, zero dependencies)
2. SLM reasoning layer (natural language, Vedic-grounded)

---

## 🌍 Dashboard: Built for 900 Million Farmers

| Feature | Detail |
|---------|--------|
| **Languages** | हिंदी · বাংলা · অসমীয়া · English |
| **UI** | Large icons — usable by non-literate farmers |
| **Sensor** | Virtual UART listener for real N-P-K hardware |
| **PWA** | Installable on any Android phone |
| **Moon Phase** | Automatic Paksha (Shukla/Krishna) timing |

---

## 🚀 Deploy in 3 Commands

### Docker (HuggingFace Spaces — port 7860)
```bash
docker build -t krishi-veda .
docker run -p 7860:7860 \
  -e OPENWEATHER_API_KEY=your_key \
  -e NASA_EARTHDATA_TOKEN=your_token \
  krishi-veda
```

### Railway / Render (port 8080)
```bash
docker run -p 8080:8080 -e PORT=8080 \
  -e OPENWEATHER_API_KEY=your_key \
  krishi-veda
```

### Raspberry Pi (bare metal)
```bash
cd vedic_core && make arm          # cross-compile for ARMv7
pip install -r requirements.txt
uvicorn backend.main:app --host 0.0.0.0 --port 8080
```

---

## 🔌 API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/plan` | Full Vedic plan — add `"use_slm":true` for SLM |
| `POST` | `/api/v1/sync` | Cache NASA + OpenWeather for 10 km radius |
| `POST` | `/api/v1/slm/advice` | SLM advice (Vedic-grounded, Ahimsa-enforced) |
| `GET`  | `/api/v1/slm/status` | SLM model load status |
| `GET`  | `/api/v1/weather` | Weather: `?lat=22.57&lon=88.36` |
| `GET`  | `/api/v1/ndvi` | Satellite NDVI: `?lat=22.57&lon=88.36` |
| `GET`  | `/api/v1/crops/{state}` | Regional crop data by state code |
| `WS`   | `/ws/uart` | Real-time N-P-K sensor frames (JSON or CSV) |
| `WS`   | `/ws/uart/simulate` | Virtual sensor stream for demo |

**Minimal plan request:**
```bash
curl -X POST https://your-app/api/v1/plan \
  -H "Content-Type: application/json" \
  -d '{"lat": 22.57, "lon": 88.36}'
```

---

## 🔑 Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `OPENWEATHER_API_KEY` | Optional | [openweathermap.org](https://openweathermap.org/api) — heuristic fallback if absent |
| `NASA_EARTHDATA_TOKEN` | Optional | [urs.earthdata.nasa.gov](https://urs.earthdata.nasa.gov) — synthetic NDVI if absent |
| `PORT` | Optional | Server port. Default `7860` (HuggingFace). Set `8080` for Railway |
| `SLM_CACHE_DIR` | Optional | Model cache path. Default `/tmp/slm_cache` |

> **Security**: Never commit API keys. Use your platform's secrets manager or a `.env` file (already in `.gitignore`).

---

## 📁 Repository Structure

```
Krishi-Veda/
├── vedic_core/                  ← 8 Krishi-Sutras (C++ source, canonical)
│   ├── vedic_kernels.cpp        ← All 8 sutras + Ahimsa-108 function
│   └── Makefile                 ← host / ARMv7 / ARMv6 build targets
│
├── backend/
│   ├── main.py                  ← FastAPI app, all routes
│   ├── core/
│   │   ├── vedic_kernels_bridge.py  ← ctypes bridge to vedic_kernels.so
│   │   ├── slm_engine.py            ← 4-bit SLM + Vedic grounding
│   │   ├── sync_manager.py          ← Offline data sync (NASA + OWM)
│   │   └── uart_listener.py         ← Virtual UART WebSocket
│   └── services/
│       ├── slm_reasoning_engine.py  ← Rule-based Vedic plan
│       └── external_intel_service.py
│
├── frontend/
│   └── index.html               ← Farmer dashboard (4 languages, big icons)
│
├── localization/dicts/          ← hi · bn · as · ta
├── vedic_engine/kernels/        ← Legacy kernel path (mirrored from vedic_core)
├── krishi_veda_offline.db       ← SQLite: regional seed data + sync cache
├── Dockerfile                   ← PORT=7860 (HF) or 8080 (Railway)
└── requirements.txt
```

---

## 📜 License

MIT License — Free to use, modify, and deploy. If Krishi-Veda helps a farmer, that is enough.

---

<div align="center">
<strong>🕉️ Krishi-Veda — Rooted in Vedic wisdom. Powered by sovereign AI.</strong><br>
<em>"Vasudhaiva Kutumbakam" — The Earth is one family.</em>
</div>
