FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for llama.cpp
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    cmake \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY . .

# Build llama.cpp (lightweight, CPU-only build)
RUN git clone --depth 1 https://github.com/ggerganov/llama.cpp.git /tmp/llama.cpp && \
    cd /tmp/llama.cpp && \
    cmake -B build -DLLAMA_CURL=OFF -DLLAMA_CUDA=OFF -DLLAMA_METAL=OFF && \
    cmake --build build --config Release -j2 && \
    cp build/bin/llama-completion /app/llama-completion && \
    rm -rf /tmp/llama.cpp

# Download small GGUF model (135M Q4 — ~105MB)
RUN curl -L -o /app/vedic-krishi-135m-q4.gguf \
    https://huggingface.co/divinesouljoy/VedaRta-0.5B-GGUF/resolve/main/vedic-krishi-135m-q4.gguf \
    || echo "Model download will be attempted at runtime"

# Create expected paths
RUN mkdir -p /root/llama.cpp/build/bin && \
    ln -sf /app/llama-completion /root/llama.cpp/build/bin/llama-completion && \
    ln -sf /app/vedic-krishi-135m-q4.gguf /root/vedic-krishi-135m-q4.gguf

# Expose FastAPI port
EXPOSE 8000

# Run FastAPI via uvicorn
CMD ["python3", "-m", "uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
