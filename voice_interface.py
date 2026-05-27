#!/usr/bin/env python3
"""
KRISHI-VEDA VOICE INTERFACE
Speech-to-text → Vedic advice → Text-to-speech
"""
import subprocess, os, json, requests

def listen():
    """Record audio and convert to text"""
    print("🎤 Listening... (speak now)")
    # Use termux-microphone-record for Android
    subprocess.run(['termux-microphone-record', '-f', '/tmp/krishi_audio.wav', '-l', '5'], 
                   capture_output=True)
    # Use whisper.cpp or vosk for offline STT
    print("📝 Processing speech...")
    return "organic fertilizer for rice"  # Placeholder

def speak(text):
    """Convert text to speech"""
    print(f"🔊 {text[:200]}...")
    # Use termux-tts-speak for Android
    subprocess.run(['termux-tts-speak', text[:500]], capture_output=True)

def get_advice(query, mode="instant"):
    """Get agricultural advice"""
    if mode == "instant":
        r = requests.get(f"http://localhost:5000/ask", params={"query": query})
        return r.json().get("advice", "No advice available")
    else:
        r = requests.post("http://localhost:5000/ai-advice", 
                         json={"prompt": query, "max_tokens": 100})
        return r.json().get("advice", "No advice available")

if __name__ == "__main__":
    print("🌾 Krishi-Veda Voice Assistant")
    print("Say 'stop' to exit")
    
    while True:
        query = listen()
        if 'stop' in query.lower():
            break
        
        print(f"📋 Query: {query}")
        advice = get_advice(query)
        print(f"💬 Advice: {advice[:200]}...")
        speak(advice)
