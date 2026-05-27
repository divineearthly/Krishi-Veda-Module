#!/bin/bash
# KRISHI-VEDA ONE-CLICK FARMER INSTALLER
# Installs everything needed on a fresh Android phone

echo "🌾 Krishi-Veda Farmer Installer"
echo "================================"

# Install Termux packages
echo "Installing dependencies..."
pkg update -y && pkg upgrade -y
pkg install python git cmake binutils clang sqlite curl -y

# Install Python packages
pip install fastapi uvicorn flask requests pydantic huggingface_hub

# Clone repository
echo "Cloning Krishi-Veda..."
cd ~
git clone https://github.com/divineearthly/Krishi-Veda-Module.git
cd Krishi-Veda-Module

# Download best model
echo "Downloading AI model (258MB)..."
python3 -c "
from huggingface_hub import hf_hub_download
hf_hub_download('divinesouljoy/Vedic-Transformer-Core', 'krishi-veda-135m-f16.gguf', local_dir='.')
" 2>/dev/null || echo "Model download skipped - copy manually"

# Create shortcuts
echo "Creating shortcuts..."
cat > ~/start_krishi.sh << 'SHORTCUT'
#!/bin/bash
cd ~/Krishi-Veda-Module
python3 -m uvicorn server:app --host 0.0.0.0 --port 5000 &
echo "Krishi-Veda started! Open browser: http://localhost:5000"
SHORTCUT
chmod +x ~/start_krishi.sh

cat > ~/ask_krishi.sh << 'SHORTCUT'
#!/bin/bash
curl "http://localhost:5000/ask?query=$*"
SHORTCUT
chmod +x ~/ask_krishi.sh

echo ""
echo "✅ Installation complete!"
echo ""
echo "Usage:"
echo "  ~/start_krishi.sh     - Start the server"
echo "  ~/ask_krishi.sh 'best fertilizer for rice'  - Get advice"
echo ""
echo "Open in browser: http://localhost:5000"
