#!/bin/bash
echo "📦 Building Krishi-Veda APK..."

cd ~/Krishi-Veda-Module

# Install buildozer if needed
pip install buildozer cython 2>&1 | tail -3

# Clean previous builds
rm -rf .buildozer

# Build APK
buildozer android debug 2>&1 | tail -20

# Check result
if [ -f bin/*.apk ]; then
    echo ""
    echo "✅ APK built successfully!"
    ls -lh bin/*.apk
    echo ""
    echo "📤 Share this APK via Bluetooth, SD card, or direct download."
    cp bin/*.apk /storage/emulated/0/Download/ 2>/dev/null
    echo "📁 Also copied to Downloads folder"
else
    echo "❌ Build failed. Check logs above."
fi
