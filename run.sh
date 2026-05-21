#!/bin/bash
# Krishi-Veda Startup Script
# Works on ARM64 (Android/Termux) and x86_64 (Hugging Face/Docker)

echo "🕉️ Starting Krishi-Veda Global Engine..."

# Locate llama.cpp binary
if [ -f "/root/llama.cpp/build/bin/llama-completion" ]; then
    export LLAMA_BIN="/root/llama.cpp/build/bin/llama-completion"
elif [ -f "/app/llama-completion" ]; then
    export LLAMA_BIN="/app/llama-completion"
else
    echo "⚠️ llama.cpp binary not found — SLM will use fallback"
fi

# Locate GGUF model
if [ -f "/root/vedic-krishi-135m-q4.gguf" ]; then
    export GGUF_MODEL="/root/vedic-krishi-135m-q4.gguf"
elif [ -f "/app/vedic-krishi-135m-q4.gguf" ]; then
    export GGUF_MODEL="/app/vedic-krishi-135m-q4.gguf"
else
    echo "⚠️ GGUF model not found — SLM will use fallback"
fi

echo "✅ LLAMA_BIN: ${LLAMA_BIN:-not found}"
echo "✅ GGUF_MODEL: ${GGUF_MODEL:-not found}"

# Start the server
python3 -m uvicorn backend.main:app --host 0.0.0.0 --port 8000
