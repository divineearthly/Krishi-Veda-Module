#!/bin/bash
# ═══════════════════════════════════════════════════════
# KRISHI-VEDA GLOBAL OFFLINE INSTALLER
# Works on any Android phone via Termux
# No internet required after initial install
# ═══════════════════════════════════════════════════════

echo "🌾 Krishi-Veda Global Offline Installer"
echo "========================================"
echo ""

# Detect device
ARCH=$(uname -m)
RAM=$(free -h | grep Mem | awk '{print $2}')
echo "📱 Device: $ARCH | RAM: $RAM"

# Install dependencies (offline-capable)
echo "📦 Installing dependencies..."
pkg update -y && pkg upgrade -y
pkg install python git cmake binutils clang sqlite curl termux-api -y
pip install fastapi uvicorn flask requests pydantic httpx

# Clone Krishi-Veda
echo "📥 Installing Krishi-Veda..."
cd ~
if [ -d "Krishi-Veda-Module" ]; then
    cd Krishi-Veda-Module && git pull
else
    git clone https://github.com/divineearthly/Krishi-Veda-Module.git
    cd Krishi-Veda-Module
fi

# Install llama.cpp (lightweight)
echo "🦙 Setting up AI engine..."
if [ ! -d "llama.cpp" ]; then
    git clone --depth 1 https://github.com/ggerganov/llama.cpp.git
    cd llama.cpp
    cmake -B build
    cmake --build build --config Release
    cd ..
fi

# Download best model for the device
echo "🤖 Installing AI model..."
MODEL_DIR=~/Krishi-Veda-Module/models
mkdir -p $MODEL_DIR

# Choose model based on RAM
RAM_MB=$(free -m | grep Mem | awk '{print $2}')
if [ $RAM_MB -gt 4000 ]; then
    MODEL="krishi-veda-360m-q4.gguf"
elif [ $RAM_MB -gt 2000 ]; then
    MODEL="krishi-veda-135m-f16.gguf"
else
    MODEL="krishi-veda-135m-q4.gguf"
fi

echo "   Selected: $MODEL for $RAM_MB MB RAM"

# Download from HuggingFace (or use local copy)
if [ ! -f "$MODEL_DIR/$MODEL" ]; then
    python3 -c "
from huggingface_hub import hf_hub_download
try:
    hf_hub_download('divinesouljoy/Vedic-Transformer-Core', '$MODEL', local_dir='$MODEL_DIR')
    print('✅ Model downloaded')
except:
    print('⚠️  Could not download model - copy manually to $MODEL_DIR/')
"
fi

# Create start script
cat > ~/start_krishi.sh << 'STARTEOF'
#!/bin/bash
cd ~/Krishi-Veda-Module
echo "🌾 Starting Krishi-Veda..."
python3 app.py &
sleep 2
echo "✅ Server running on http://localhost:5000"
echo "📱 Open: http://localhost:5000/ask?query=your+question"
STARTEOF
chmod +x ~/start_krishi.sh

# Create desktop shortcut
cat > ~/.termux/termux.url 2>/dev/null << 'SHORTCUT'
[Krishi-Veda]
URL = http://localhost:5000/ask?query=
SHORTCUT

echo ""
echo "╔══════════════════════════════════════════════════╗"
echo "║   ✅ INSTALLATION COMPLETE!                      ║"
echo "║                                                  ║"
echo "║   🚀 Start: ~/start_krishi.sh                    ║"
echo "║   📱 Open: http://localhost:5000/ask?query=...   ║"
echo "║   📦 Offline: Works without internet             ║"
echo "║   🌍 Languages: en, as, hi, bn                   ║"
echo "║                                                  ║"
echo "╚══════════════════════════════════════════════════╝"
