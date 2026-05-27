# 🌍 How to Share Krishi-Veda Offline

## Method 1: Bluetooth (Phone-to-Phone)
1. Open Termux on both phones
2. Sender: `termux-share -a send krishi_veda_offline.tar.gz`
3. Receiver: Accept and extract: `tar -xzf krishi_veda_offline.tar.gz`
4. Run: `cd krishi_veda_offline_package && bash install.sh`

## Method 2: SD Card (Best for Villages)
1. Copy package to SD card
2. Share SD card among farmers
3. Each farmer: Insert SD, copy folder, run install.sh
4. One download serves entire village!

## Method 3: WiFi Direct / Hotspot
1. Start hotspot on one phone
2. Others connect to hotspot
3. Download from: http://192.168.43.1:8000/krishi_veda_offline.tar.gz
4. Install and use offline thereafter

## Method 4: WhatsApp / ShareIt
1. Send krishi_veda_offline.tar.gz via WhatsApp
2. Or use ShareIt/Xender for faster transfer
3. Extract and install

## Method 5: Pre-loaded Phones
1. Install on one phone fully
2. Use "Clone Phone" or "Smart Switch"
3. Transfer everything to new phone
4. Ready to use immediately

## After Install - No Internet Needed!
- ✅ AI advice works offline
- ✅ Weather uses cached data
- ✅ Market prices from stored database
- ✅ All 4 languages available
- ✅ Updates via Bluetooth/WiFi Direct when nearby

## Update via Sneakernet
When one phone gets internet:
1. Run: `cd ~/Krishi-Veda-Module && git pull`
2. Share updated package with others via Bluetooth
