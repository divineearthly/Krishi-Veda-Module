[app]
title = Divine Earthly
package.name = divineearthly
package.domain = org.divineearthly
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json,js,css,html,db,so,bin,gguf
version = 1.0.0

# Core requirements
requirements = python3,kivy==2.2.1,fastapi,uvicorn,pydantic,aiofiles,psutil,httpx,requests,fpdf2,joblib,scikit-learn,pandas,numpy

# Android settings
orientation = portrait
fullscreen = 0
android.api = 30
android.minapi = 24
android.ndk = 25b
android.arch = arm64-v8a

# Permissions for full functionality
android.permissions = INTERNET,ACCESS_NETWORK_STATE,ACCESS_WIFI_STATE,ACCESS_FINE_LOCATION,ACCESS_COARSE_LOCATION,CAMERA,RECORD_AUDIO,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE

# App metadata
android.manifest.launch_mode = singleTop
android.allow_backup = True
android.presplash_color = #1b4332
android.splash_color = #1b4332

# Features
android.gradle_dependencies = androidx.core:core:1.9.0,androidx.webkit:webkit:1.7.0

# Auto-update via GitHub Releases
# App checks https://github.com/divineearthly/Krishi-Veda-Module/releases/latest
# Downloads and applies update.zip if newer version available

[buildozer]
log_level = 2
warn_on_root = 1
p4a.branch = develop
