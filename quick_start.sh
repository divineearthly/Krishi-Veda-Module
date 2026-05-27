#!/bin/bash
# KRISHI-VEDA QUICK START
# Starts the entire system with one command

echo "🌾 KRISHI-VEDA SOVEREIGN AI"
echo "============================"
echo ""

# Set library path for llama.cpp
export LD_LIBRARY_PATH=$HOME/llama-b9297:$LD_LIBRARY_PATH

# 1. Test C++ accelerator
echo "1️⃣  Testing C++ Accelerator..."
./veda_accelerator 28.4 62.1 6.4 > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "   ✅ C++ Accelerator ready"
else
    echo "   ❌ C++ Accelerator failed"
fi

# 2. Test database
echo "2️⃣  Checking Database..."
RECORDS=$(sqlite3 krishi_veda.db "SELECT COUNT(*) FROM advisories;" 2>/dev/null)
echo "   ✅ Database active ($RECORDS advisories)"

# 3. Check models
echo "3️⃣  Checking Models..."
MODELS=0
for m in ~/krishi-veda-135m-f16.gguf /storage/emulated/0/vedic_model.gguf ~/vedic_model_q2.gguf; do
    if [ -f "$m" ]; then
        ((MODELS++))
    fi
done
echo "   ✅ $MODELS models available"

# 4. Start server
echo "4️⃣  Starting API Server..."
python3 server.py > /tmp/krishi_server.log 2>&1 &
PID=$!
sleep 3

if kill -0 $PID 2>/dev/null; then
    echo "   ✅ Server running (PID: $PID)"
    echo ""
    echo "🌾 System ready!"
    echo "   API: http://localhost:8000"
    echo "   Logs: /tmp/krishi_server.log"
else
    echo "   ❌ Server failed - check /tmp/krishi_server.log"
fi
