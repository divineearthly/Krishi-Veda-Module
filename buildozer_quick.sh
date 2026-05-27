#!/bin/bash
echo "📱 Building Krishi-Veda Android APK..."
echo "This takes 10-20 minutes on first build"

# Install buildozer dependencies
pkg install openjdk-17 python buildozer -y

# Clean previous builds
rm -rf .buildozer

# Build APK
buildozer android debug

if [ -f bin/*.apk ]; then
    APK=$(ls bin/*.apk | head -1)
    echo "✅ APK built: $APK"
    echo "   Size: $(ls -lh $APK | awk '{print $5}')"
    echo "   Install: termux-open $APK"
else
    echo "❌ Build failed. Check .buildozer/logs/"
fi
