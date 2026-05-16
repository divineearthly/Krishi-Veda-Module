#!/usr/bin/env bash
# Krishi-Veda-Module Offline Launcher
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"
echo "Krishi-Veda-Module — Vedic Farming AI"
echo "Ahimsa-108 Protocol ACTIVE"

if [ ! -f "/root/llama.cpp/build/bin/llama-simple" ]; then
    echo "ERROR: llama-simple not found"
    exit 1
fi

if [ ! -f "/data/data/com.termux/files/home/vedic_model.gguf" ]; then
    echo "ERROR: vedic_model.gguf not found"
    exit 1
fi

echo "Starting server on port 8000..."
python3 -m uvicorn backend.main:app --host 0.0.0.0 --port 8000
