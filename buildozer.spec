[app]
title = Krishi-Veda
package.name = krishiveda
package.domain = org.earthly.divine
source.dir = .
source.include_exts = py,png,jpg,html,css,js,json,md,gguf,so
version = 2.0.0
requirements = python3,flask,requests,httpx
orientation = portrait
android.permissions = INTERNET,ACCESS_NETWORK_STATE,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE,BLUETOOTH,BLUETOOTH_ADMIN,ACCESS_FINE_LOCATION
android.api = 26
android.minapi = 21
android.ndk = 25b
android.sdk = 34
android.gradle_dependencies = androidx.core:core:1.12.0
android.archs = arm64-v8a
android.allow_backup = True
fullscreen = 0
presplash.color = #1a3300
android.presplash_color = #1a3300

[buildozer]
log_level = 2
warn_on_root = 1
