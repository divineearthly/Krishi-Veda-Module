[app]
title = KrishiVeda
package.name = krishiveda
package.domain = org.divinearthly
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json,js,css,html,db,so,bin
version = 1.0.0
requirements = python3,fastapi,uvicorn,pydantic,aiofiles,psutil,httpx,hostpython3
orientation = portrait
osx.python_version = 3
osx.kivy_version = 2.2.1
fullscreen = 0
android.api = 30
android.minapi = 24
android.ndk = 25b
android.gradle_dependencies = 
android.manifest.launch_mode = singleTop
android.manifest.permissions = INTERNET,ACCESS_NETWORK_STATE,ACCESS_WIFI_STATE,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE
android.allow_backup = True
android.presplash_color = #2d6a4f
android.splash_color = #2d6a4f

# APK downloads VedaRta GGUF from HuggingFace CDN on first launch
# Model cached in app storage for offline use thereafter

[buildozer]
log_level = 2
warn_on_root = 1

# ARM64 optimizations
android.arch = arm64-v8a
android.gradle_dependencies = androidx.core:core:1.9.0
p4a.branch = develop
