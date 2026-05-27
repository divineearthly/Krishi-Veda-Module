# Krishi-Veda APK Build Guide

## Option 1: PWA → Trusted Web Activity (Recommended)
1. Your PWA is ready at index.html
2. Use Bubblewrap to create TWA: `npm i -g @bubblewrap/cli`
3. Upload to Google Play as native app
4. Works offline, installs like regular app

## Option 2: AppsGeyser (Free, No Code)
1. Go to appsgeyser.com
2. Choose "Website" template
3. Enter URL of your Krishi-Veda server
4. Generate APK in 5 minutes
5. Share APK with farmers

## Option 3: GitHub Actions CI/CD
1. Push code to GitHub
2. Use build-apk.yml workflow
3. APK built automatically on every release

## Current Status
- ✅ PWA works on any phone browser
- ✅ Add to Home Screen = app-like experience
- ⏳ Native Kivy APK needs desktop build machine
