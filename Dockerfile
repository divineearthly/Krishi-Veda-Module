FROM python:3.10-slim

# ── System deps: C++ compiler + build tools ──────────────────────────────────
RUN apt-get update && apt-get install -y --no-install-recommends \
        g++ \
        build-essential \
    && rm -rf /var/lib/apt/lists/*

# ── Working directory ─────────────────────────────────────────────────────────
WORKDIR /app

# ── Copy only what we need first (for better layer caching) ──────────────────
COPY requirements.txt .

# ── Install Python deps ───────────────────────────────────────────────────────
# Install torch CPU-only first (smaller wheel); then the rest.
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu && \
    pip install --no-cache-dir -r requirements.txt

# ── Copy source code ──────────────────────────────────────────────────────────
COPY . .

# ── Compile the 8 Krishi-Sutras into a shared library ────────────────────────
# -Os  : optimise for binary size (runs well on old/low-RAM processors)
# -fPIC: position-independent code required for .so
# -lm  : link math library
RUN g++ -Os -fPIC -shared -std=c++14 \
        -o vedic_engine/kernels/vedic_kernels.so \
        vedic_engine/kernels/vedic_kernels.cpp \
        -lm

# ── Port ──────────────────────────────────────────────────────────────────────
# HuggingFace Spaces expects 7860.
# Railway / generic cloud defaults to 8080.
# Override at runtime: docker run -e PORT=8080 ...
ENV PORT=7860
EXPOSE 7860
EXPOSE 8080

# ── Start FastAPI ─────────────────────────────────────────────────────────────
CMD uvicorn backend.main:app --host 0.0.0.0 --port ${PORT}
