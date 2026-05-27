#!/bin/bash
# ═══════════════════════════════════════════════════════
# CREATE SHAREABLE OFFLINE PACKAGE
# Share via SD card, Bluetooth, or WiFi Direct
# ═══════════════════════════════════════════════════════

PACKAGE_DIR=~/krishi_veda_offline_package
rm -rf $PACKAGE_DIR
mkdir -p $PACKAGE_DIR

echo "📦 Creating offline package..."

# 1. Copy all essential files
cp -r ~/Krishi-Veda-Module/*.py $PACKAGE_DIR/
cp -r ~/Krishi-Veda-Module/*.html $PACKAGE_DIR/
cp -r ~/Krishi-Veda-Module/*.sh $PACKAGE_DIR/
cp -r ~/Krishi-Veda-Module/*.md $PACKAGE_DIR/
cp -r ~/Krishi-Veda-Module/*.json $PACKAGE_DIR/
cp -r ~/Krishi-Veda-Module/backend $PACKAGE_DIR/
cp -r ~/Krishi-Veda-Module/vedic_core $PACKAGE_DIR/
cp -r ~/Krishi-Veda-Module/vedic_engine $PACKAGE_DIR/
cp ~/Krishi-Veda-Module/veda_accelerator $PACKAGE_DIR/ 2>/dev/null
cp ~/Krishi-Veda-Module/krishi_veda.db $PACKAGE_DIR/ 2>/dev/null

# 2. Copy best model (small, fast)
if [ -f ~/krishi-veda-135m-f16.gguf ]; then
    cp ~/krishi-veda-135m-f16.gguf $PACKAGE_DIR/
fi

# 3. Create README
cat > $PACKAGE_DIR/README.md << 'README'
# 🌾 Krishi-Veda Offline Package

## What is this?
Sovereign agricultural AI that runs entirely offline on Android phones.

## How to Install
1. Install Termux from F-Droid
2. Copy this folder to ~/Krishi-Veda-Module
3. Run: bash install.sh
4. Open: http://localhost:5000/ask?query=your+question

## No Internet? No Problem!
Everything works offline - AI models, weather cache, market prices cache.

## Languages
English | Assamese | Hindi | Bengali

## Free & Open Source
github.com/divineearthly/Krishi-Veda-Module
README

# 4. Create quick install script inside package
cat > $PACKAGE_DIR/install.sh << 'INSTALL'
#!/bin/bash
echo "🌾 Installing Krishi-Veda..."
pkg install python sqlite curl -y
pip install fastapi uvicorn flask requests pydantic httpx
cd ~/Krishi-Veda-Module
python3 app.py &
echo "✅ Done! Open: http://localhost:5000/ask?query=hello"
INSTALL
chmod +x $PACKAGE_DIR/install.sh

# 5. Create archive
cd ~
tar -czf krishi_veda_offline.tar.gz krishi_veda_offline_package/

SIZE=$(ls -lh krishi_veda_offline.tar.gz | awk '{print $5}')
echo ""
echo "╔══════════════════════════════════════════════════╗"
echo "║   ✅ OFFLINE PACKAGE CREATED!                    ║"
echo "║   📦 ~/krishi_veda_offline.tar.gz               ║"
echo "║   📏 Size: $SIZE                                ║"
echo "║                                                  ║"
echo "║   📤 Share via:                                  ║"
echo "║   • Bluetooth: termux-share -a send             ║"
echo "║   • WiFi Direct: FTP server                     ║"
echo "║   • SD Card: cp to /storage/emulated/0/         ║"
echo "║   • USB: Connect to PC and transfer             ║"
echo "╚══════════════════════════════════════════════════╝"
