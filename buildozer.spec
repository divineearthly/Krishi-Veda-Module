[app]
title = Krishi-Veda
package.name = krishiveda
package.domain = org.earthly.divine
source.dir = .
source.include_exts = py,png,jpg,html,css,js,json,md
version = 2.0.0
requirements = python3,flask,requests
orientation = portrait
android.permissions = INTERNET,ACCESS_NETWORK_STATE
android.api = 33
android.minapi = 21
android.ndk = 27.3.13750724
android.archs = arm64-v8a
android.allow_backup = True
fullscreen = 0
presplash.color = #1a3300
p4a.branch = develop

[buildozer]
log_level = 2
warn_on_root = 1
