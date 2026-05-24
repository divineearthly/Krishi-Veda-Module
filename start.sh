#!/bin/bash
echo "=========================================="
echo "  KRISHI-VEDA — Sovereign AI Farm Advisor"
echo "  Running on ARM64 Android (Termux)"
echo "=========================================="
echo ""

# Set library path for llama.cpp
export LD_LIBRARY_PATH=$HOME/llama-b9297:$LD_LIBRARY_PATH

# Start the FastAPI server
cd $HOME/Krishi-Veda-Module

echo "Starting API server..."
echo "Access at: http://localhost:8000"
echo "Docs at:   http://localhost:8000/docs"
echo ""

# Install requirements if needed
pip install fastapi uvicorn requests pydantic 2>/dev/null

# Launch server
uvicorn backend.core.api_v1:app --host 0.0.0.0 --port 8000 --reload
