# 🌾 Krishi-Veda Module
### Sovereign Offline Agricultural AI — Powered by Vedic Intelligence

<p align="center">
  <img src="https://img.shields.io/badge/Status-Prototype%20%2F%20TRL%204-green?style=for-the-badge"/>
  <img src="https://img.shields.io/badge/Python-FastAPI-blue?style=for-the-badge&logo=python"/>
  <img src="https://img.shields.io/badge/AI-Qwen2--0.5B%20SLM-orange?style=for-the-badge"/>
  <img src="https://img.shields.io/badge/Deploy-HuggingFace%20Spaces-yellow?style=for-the-badge"/>
  <img src="https://img.shields.io/badge/License-MIT-lightgrey?style=for-the-badge"/>
</p>

<p align="center">
  <b>Divine Earthly</b> · Built by <a href="https://github.com/divineearthly">Joydeep Das</a> · Silchar, Assam, India
</p>

---

## 🧭 What Is This?

**Krishi-Veda Module** is a sovereign, offline-capable agricultural AI assistant designed for Indian farmers — especially those in low-connectivity, rural regions like Northeast India.

It combines:
- A **quantised Small Language Model (SLM)** running entirely on CPU
- **Vedic Mathematical kernels** replacing standard LLM matrix operations
- A **multilingual voice UI** (Bengali, Assamese, Hindi)
- A **Pramana epistemological layer** — making AI advice explainable and culturally grounded

> **No cloud. No subscription. No literacy barrier. Just intelligent farming advice — in your language, on your phone.**

---

## 🚜 The Problem We Solve

| Problem | Scale |
|--------|-------|
| Farmers without reliable internet | 65% of India |
| Smartphones farmers own (RAM) | 2–4 GB only |
| AgriTech AI solutions working fully offline | **0** |
| Languages spoken across India | 22+ official |

Modern AgriTech is almost entirely cloud-dependent. Krishi-Veda runs **locally on Android via Termux** or as a **HuggingFace Space** — no internet required for core advisory functions.

---

## ✨ Key Features

### 🔌 1. Sovereign Offline AI
- FastAPI backend + Docker container
- Runs Qwen2-0.5B (quantised) on CPU-only hardware
- Compatible with Android (Termux), Raspberry Pi, basic laptops

### 🧮 2. Vedic Mathematical Kernels
- Core LLM matrix operations replaced by **Urdhva-Tiryagbhyam** sutra
- Based on the **64-Sutra AI Framework** (Divine Earthly research)
- Dramatically reduced compute footprint vs standard transformer math

### 🗣️ 3. Multilingual Voice UI
- WASM-based lightweight frontend
- Supports Bengali, Assamese, Hindi
- Designed for farmers with low literacy — voice-first interaction

### 🧠 4. Pramana Epistemological Layer
Advice is structured across 5 Vedic knowledge categories:

| Pramana | Meaning | Application |
|---------|---------|-------------|
| Pratyaksha | Direct perception | Crop visual diagnosis |
| Anumana | Inference | Yield prediction |
| Upamana | Comparison | Crop variety recommendation |
| Shabda | Expert testimony | Government scheme advisory |
| Anupalabdhi | Absence/negation | Pest/disease ruling out |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────┐
│           KRISHI-VEDA MODULE            │
│                                         │
│  ┌──────────┐    ┌────────────────────┐ │
│  │  WASM    │    │   FastAPI Backend  │ │
│  │  Voice   │───▶│   + Pramana Layer  │ │
│  │  UI      │    └────────┬───────────┘ │
│  └──────────┘             │             │
│                           ▼             │
│              ┌────────────────────────┐ │
│              │  Qwen2-0.5B (CPU SLM) │ │
│              │  + Vedic Math Kernels  │ │
│              │  Urdhva-Tiryagbhyam   │ │
│              └────────────────────────┘ │
│                                         │
│  📦 Docker  |  🐍 Python  |  ⚡ C++    │
└─────────────────────────────────────────┘
```

**Stack:** FastAPI · Docker · Qwen2-0.5B · WASM · C++ NEON Kernels · HuggingFace Spaces

---

## 🚀 Quick Start

### Option 1 — Docker (Recommended)
```bash
git clone https://github.com/divineearthly/krishi-veda-module
cd krishi-veda-module
docker build -t krishi-veda .
docker run -p 8000:8000 krishi-veda
```
Then open: `http://localhost:8000`

### Option 2 — Local Python
```bash
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000
```

### Option 3 — Android (Termux)
```bash
pkg install python git
git clone https://github.com/divineearthly/krishi-veda-module
cd krishi-veda-module
pip install -r requirements-termux.txt
python main.py
```

### Option 4 — HuggingFace Spaces
> 🔗 Deployed `https://huggingface.co/spaces/divinesouljoy/Krishi-Veda`

---

## 📁 Repository Structure

```
krishi-veda-module/
├── main.py                  # FastAPI entry point
├── Dockerfile               # Container definition
├── requirements.txt         # Python dependencies
├── requirements-termux.txt  # Lightweight mobile deps
│
├── vedic_kernels/           # Vedic Math computation layer
│   ├── urdhva_tiryagbhyam.cpp   # Matrix multiply sutra
│   ├── sulba_geometry.cpp       # Geometric reasoning
│   └── __init__.py
│
├── pramana_layer/           # Epistemological advisory engine
│   ├── pratyaksha.py        # Direct diagnosis
│   ├── anumana.py           # Inference engine
│   ├── upamana.py           # Comparison/recommendation
│   ├── shabda.py            # Scheme/knowledge lookup
│   └── anupalabdhi.py       # Negation/ruling out
│
├── api/                     # FastAPI route handlers
│   ├── advisory.py
│   ├── diagnosis.py
│   └── schemes.py
│
├── frontend/                # WASM voice UI
│   ├── index.html
│   └── voice_interface.js
│
└── models/                  # SLM model configs
    └── qwen2_config.json
```

---

## 🌱 Roadmap

| Phase | Timeline | Milestone |
|-------|----------|-----------|
| ✅ Phase 1 | Mar–Apr 2026 | Core FastAPI + Vedic kernel functional |
| 🔄 Phase 2 | May 2026 | HuggingFace Spaces deployment |
| 📍 Phase 3 | Jun–Jul 2026 | Cachar district pilot — 50 farmers |
| 🔜 Phase 4 | Q3 2026 | IP filing · ICAR grant · NE India expansion |
| 🔜 Phase 5 | Q4 2026 | 5-language voice UI · 500-farmer network |
| 🔜 Phase 6 | 2027 | National scale · DST SERB partnership |

---

## 🏆 Competition & Recognition

- 🥇 **ARC-AGI-2** — Kaggle Competition (C++ Vedic Sutras geometric solver submitted)
- 🎯 **AGI Hackathon** — Google DeepMind × Kaggle — Pramana Metacognition Benchmark submitted (Apr 2026)
- 🌿 **ACIC-KIF SISFS** — Startup India Seed Fund Scheme application (Under Review, Apr 2026)

---

## 🔬 Related Projects (Divine Earthly Ecosystem)

| Project | Description |
|---------|-------------|
| [KAVACH](https://github.com/divineearthly) | Sovereign cybercrime defense — 6 Vedic-named modules |
| [SASI](https://github.com/divineearthly) | Sovereign Artificial Supreme Intelligence — mobile LLM |
| [Pramana Benchmark](https://github.com/divineearthly) | AGI metacognition evaluation framework |
| [64-Sutra Framework](https://github.com/divineearthly) | Vedic AI architecture — all Divine Earthly projects |

---

## 👤 About the Founder

**Joydeep Das** — Independent AI Researcher & Developer  
Divine Earthly · Silchar, Assam, India · PIN 788005

- 📧 jdas794@gmail.com
- 📱 +91 90857 51162
- 🐙 [github.com/divineearthly](https://github.com/divineearthly)
- 📊 [kaggle.com/divinesouljoy](https://kaggle.com/divinesouljoy)

> *"Vasudhaiva Kutumbakam — The Earth is One Family.  
> Sovereign AI rooted in Vedic wisdom. Built for Bharat's farmers."*

---

## 📜 License

MIT License · © 2026 Divine Earthly / Joydeep Das

---

<p align="center">
  <b>🌾 Krishi-Veda Module · Divine Earthly · Built in Assam, for India</b>
</p>
