
# ── Stage 1: Emscripten WASM build ──────────────────────────────────────────
# Install emsdk to compile vedic_kernels_wasm.cpp → vedic_kernels.js + .wasm
FROM python:3.10-slim AS wasm-builder

RUN apt-get update && apt-get install -y --no-install-recommends \
        git cmake python3 nodejs npm xz-utils \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /emsdk
RUN git clone --depth 1 https://github.com/emscripten-core/emsdk.git . && \
    ./emsdk install latest && \
    ./emsdk activate latest

RUN mkdir -p /wasm_out
WORKDIR /app
COPY vedic_core/vedic_kernels_wasm.cpp vedic_core/

RUN /bin/bash -c "source /emsdk/emsdk_env.sh && \
    emcc -Os -s WASM=1 \
         -s EXPORTED_RUNTIME_METHODS='[\"cwrap\",\"ccall\",\"FS\"]' \
         -s EXPORTED_FUNCTIONS='[\"_anurupyena_scale\",\"_nikhilam_deficit\",\
\"_paravartya_ph_inversion\",\"_ekadhikena_next_stage\",\
\"_urdhva_yield_score\",\"_vilokanam_anomaly\",\
\"_gunakasamuccaya_wellness\",\"_shunyam_stress_balance\",\
\"_ahimsa_108_stress_code\",\"_malloc\",\"_free\"]' \
         -s MODULARIZE=0 \
         -s ENVIRONMENT='web,worker' \
         vedic_core/vedic_kernels_wasm.cpp \
         -o /wasm_out/vedic_kernels.js" && \
    echo 'WASM build complete'

# ── Stage 2: Runtime ─────────────────────────────────────────────────────────
FROM python:3.10-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
        g++ \
        build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Python deps (cached layer)
COPY requirements.txt .
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu && \
    pip install --no-cache-dir -r requirements.txt

# Copy full source
COPY . .

# Copy compiled WASM artefacts into the frontend/ directory (served as /static/)
COPY --from=wasm-builder /wasm_out/vedic_kernels.js  frontend/vedic_kernels.js
COPY --from=wasm-builder /wasm_out/vedic_kernels.wasm frontend/vedic_kernels.wasm

# Compile native .so for the Python backend (separate from WASM)
RUN g++ -Os -fPIC -shared -std=c++14 \
        -o vedic_core/vedic_kernels.so \
        vedic_core/vedic_kernels.cpp \
        -lm && \
    cp vedic_core/vedic_kernels.so vedic_engine/kernels/vedic_kernels.so

# ── Environment variables ─────────────────────────────────────────────────────
ENV OPENWEATHER_API_KEY=""
ENV NASA_EARTHDATA_TOKEN=""
ENV SLM_CACHE_DIR="/tmp/slm_cache"

# ── Port ──────────────────────────────────────────────────────────────────────
# HuggingFace Spaces → 7860 (default)
# Railway / Render   → 8080  (set PORT=8080)
ENV PORT=7860
EXPOSE 7860
EXPOSE 8080

CMD uvicorn backend.main:app --host 0.0.0.0 --port ${PORT}
