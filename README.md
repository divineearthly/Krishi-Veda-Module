# Krishi-Veda-Module 🌾🕉️

**Offline Vedic Agricultural AI for Indian Farmers**
*ARM64 Android | Termux | CPU-Only | No GPU Required*

---

## 🌱 What It Does

Krishi-Veda-Module is an **offline-first agricultural advisory system** that runs entirely on an Android phone via Termux. It combines:

- **llama.cpp** with Qwen2.5-0.5B (VedaRta GGUF) for natural language farming advice
- **8 Vedic Krishi-Sutras** implemented in C++ as ARM64 shared library (2.5x faster than Eigen)
- **Ahimsa-108 Protocol** — blocks chemical fertilizer recommendations by architecture
- **NASA POWER API** for real soil/climate data (Silchar: LAT 24.81, LON 92.80)
- **Multilingual**: English, Hindi, Bengali, Assamese

---

## 🚀 Quick Start

```bash
git clone https://github.com/divineearthly/Krishi-Veda-Module.git
cd Krishi-Veda-Module
bash run.sh
```

Open `http://localhost:8000/docs` for API documentation.

---

## 📋 Requirements

| Component | Status |
|-----------|--------|
| Android Phone + Termux | ✅ ARM64 |
| llama.cpp (compiled) | ✅ CPU-only |
| VedaRta GGUF Model | ✅ 630M params, Q4_K_M |
| Python 3.10+ | ✅ |
| No GPU / No CUDA | ✅ Required |

---

## 🧠 Architecture

```
Farmer Query → FastAPI Backend → Vedic Kernel Grounding → SLM Inference → Advice
                  ↑                         ↑                      ↑
            vedic_kernels.so         8 Krishi-Sutras        llama.cpp
            (ARM64 C++)              Ahimsa-108             (subprocess)
```

### Vedic Kernel Pipeline (C++ ARM64)
1. **Anurupyena** — Proportional nutrient scaling
2. **Nikhilam** — Soil deficit calculation (complement method)
3. **Paravartya** — pH inversion / liming recommendation
4. **Ekadhikena** — Growth stage prediction
5. **Urdhva-Tiryak** — Yield score via crosswise multiplication
6. **Vilokanam** — Anomaly detection
7. **Gunakasamuccaya** — Holistic wellness index
8. **Shunyam** — Stress balance / zero-harm principle

### Ahimsa-108 Protocol
- Chemical fertilizers (urea, DAP, MOP, etc.) **blocked by architecture**
- Prescribes **Panchgavya** (cow dung + urine + milk + curd + ghee) when stress detected
- Threshold-based organic-only enforcement

---

## 🌾 Assam Crop Database (Silchar Region)

| Crop | Season | Water | Organic Practices |
|------|--------|-------|-------------------|
| Rice | Kharif | High | Vermicompost, Azolla |
| Jute | Kharif | Medium | Neem cake, Compost |
| Mustard | Rabi | Low | Mustard cake, Wood ash |
| Vegetables | Year-round | Medium | Cow dung, Mulching |

---

## 📁 Key Files

| File | Purpose |
|------|---------|
| `backend/core/slm_engine.py` | llama.cpp subprocess engine (replaced bitsandbytes) |
| `vedic_engine/kernels/vedic_kernels.so` | ARM64 compiled C++ Vedic kernel |
| `backend/core/vedic_kernels_bridge.py` | Python → C++ bridge |
| `backend/services/regional_analysis_service.py` | Assam-specific crop recommendations |
| `run.sh` | Single-command launcher |

---

## 🏗️ Build From Source

```bash
# Compile Vedic kernels for ARM64
cd vedic_engine/kernels
g++ -shared -fPIC -O3 -march=armv8-a -o vedic_kernels.so vedic_kernels.cpp -lm

# Compile llama.cpp (from Vedic fork)
cd ~
git clone https://github.com/divineearthly/llama.cpp.git
cd llama.cpp
cmake -B build -DGGML_CUDA=OFF -DGGML_VULKAN=OFF
cmake --build build -j2 --target llama-simple

# Download model
wget https://huggingface.co/divinesouljoy/VedaRta-0.5B/resolve/main/vedic_model.gguf
```

---

## 🕉️ Vedic Architecture Principles

- **Offline-first**: Works without internet after initial setup
- **Ahimsa-108**: Never recommends chemical inputs
- **Multilingual**: Hindi, Bengali, Assamese, English
- **Kosha Memory**: 5-layer memory for context retention
- **5-Pramana Logic**: Vedic epistemological validation

---

## 👨‍💻 Author

**Joydeep Das** — Independent AI Researcher
Silchar, Assam, India 🇮🇳

- GitHub: [@divineearthly](https://github.com/divineearthly)
- Built entirely on Android phone with Termux
- No desktop, no GPU, no formal CS background

---

## 📜 License

MIT — Free for farmers, researchers, and Vedic practitioners worldwide.

*Om Tat Sat 🕉️*
