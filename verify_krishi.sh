#!/bin/bash
echo "🔱 KRISHI-VEDA VERIFICATION"
passed=0
for f in backend/main.py vedic_engine/kernels/vedic_kernels.cpp slm_engine.py frontend/index.html localization/dicts/hi.json .gitignore; do
    if [ -f "$f" ]; then
        echo "✅ $f"
        passed=$((passed+1))
    else
        echo "❌ $f MISSING"
    fi
done
echo "Passed: $passed/6"
