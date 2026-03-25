FROM python:3.10-slim

# ── System deps: C++ compiler + build tools ──────────────────────────────────
RUN apt-get update && apt-get install -y --no-install-recommends \
        g++ \
        build-essential \
    && rm -rf /var/lib/apt/lists/*

# ── Working directory ─────────────────────────────────────────────────────────
WORKDIR /app

# ── Python deps (cached layer — only re-runs if requirements.txt changes) ────
COPY requirements.txt .
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu && \
    pip install --no-cache-dir -r requirements.txt

# ── Copy source code ──────────────────────────────────────────────────────────
COPY . .

# ── Compile the 8 Krishi-Sutras into a shared library ────────────────────────
# Primary source lives in vedic_core/ (canonical location).
# -Os  : optimise for binary size — runs on low-RAM / old processors
# -fPIC: required for shared libraries
# -lm  : link math library
RUN g++ -Os -fPIC -shared -std=c++14 \
        -o vedic_core/vedic_kernels.so \
        vedic_core/vedic_kernels.cpp \
        -lm && \
    # Mirror to legacy path so existing Python bridge still resolves
    cp vedic_core/vedic_kernels.so vedic_engine/kernels/vedic_kernels.so

# ── Runtime environment variables ─────────────────────────────────────────────
# API keys: inject at deploy time via --env-file or platform secrets panel.
# Never hardcode values here.
ENV OPENWEATHER_API_KEY=""
ENV NASA_EARTHDATA_TOKEN=""
ENV SLM_CACHE_DIR="/tmp/slm_cache"

# ── Port ──────────────────────────────────────────────────────────────────────
# HuggingFace Spaces → PORT=7860 (default)
# Railway / Render / generic cloud → PORT=8080
# Override: docker run -e PORT=8080 ...
ENV PORT=7860
EXPOSE 7860
EXPOSE 8080

# ── Start FastAPI ─────────────────────────────────────────────────────────────
CMD uvicorn backend.main:app --host 0.0.0.0 --port ${PORT}
