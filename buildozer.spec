[app]
title = Krishi Veda
package.name = krishiveda
package.domain = org.earthly
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json,db,html,gguf,so,tflite
version = 2.0.0
requirements = python3,kivy==2.1.0,fastapi,uvicorn,flask,requests,pydantic,httpx,aiofiles
orientation = portrait
fullscreen = 0
android.permissions = INTERNET,ACCESS_NETWORK_STATE,ACCESS_FINE_LOCATION,ACCESS_COARSE_LOCATION,RECORD_AUDIO
android.api = 33
android.minapi = 24
android.ndk = 25b
android.sdk = 33
android.arch = arm64-v8a
android.allow_backup = True
android.presplash_color = #2D5016

[buildozer]
log_level = 2
warn_on_root = 1
