"""
SEEU Microphone Diagnostic Tool
Run this to find out why continuous mode crashes
"""

import sys

print("="*60)
print("🔍 SEEU MICROPHONE DIAGNOSTIC")
print("="*60)

# Check 1: Python version
print("\n1️⃣ Checking Python version...")
print(f"   Python {sys.version}")
if sys.version_info < (3, 7):
    print("   ❌ Python 3.7+ required!")
else:
    print("   ✅ Python version OK")

# Check 2: SpeechRecognition
print("\n2️⃣ Checking SpeechRecognition...")
try:
    import speech_recognition as sr
    print(f"   ✅ SpeechRecognition {sr.__version__} installed")
except ImportError:
    print("   ❌ SpeechRecognition NOT installed!")
    print("   Fix: pip install SpeechRecognition --break-system-packages")
    sys.exit(1)

# Check 3: PyAudio
print("\n3️⃣ Checking PyAudio...")
try:
    import pyaudio
    print(f"   ✅ PyAudio installed")
except ImportError:
    print("   ❌ PyAudio NOT installed!")
    print("   This is likely the problem!")
    print("\n   FIX:")
    print("   Windows: pip install pyaudio --break-system-packages")
    print("   Linux:   sudo apt-get install python3-pyaudio")
    print("   Mac:     brew install portaudio && pip install pyaudio")
    sys.exit(1)

# Check 4: Microphone list
print("\n4️⃣ Checking available microphones...")
try:
    mic_list = sr.Microphone.list_microphone_names()
    if not mic_list:
        print("   ❌ No microphones found!")
        print("   Make sure a microphone is connected")
    else:
        print(f"   ✅ Found {len(mic_list)} microphone(s):")
        for i, name in enumerate(mic_list):
            print(f"      {i}: {name}")
except Exception as e:
    print(f"   ⚠️  Error listing microphones: {e}")

# Check 5: Microphone test
print("\n5️⃣ Testing microphone access...")
try:
    recognizer = sr.Recognizer()
    mic = sr.Microphone()
    print("   ✅ Microphone object created")

    with mic as source:
        print("   ✅ Microphone opened successfully")
        print("   🔧 Calibrating (this takes 2 seconds)...")
        recognizer.adjust_for_ambient_noise(source, duration=2)
        print("   ✅ Calibration complete")

    print("\n   ✅✅✅ MICROPHONE IS WORKING! ✅✅✅")

except OSError as os_error:
    print(f"   ❌ OS Error: {os_error}")
    print("\n   POSSIBLE CAUSES:")
    print("   1. Another app is using the microphone (Zoom, Discord, etc.)")
    print("   2. Microphone is not properly connected")
    print("   3. Microphone permissions not granted")
    print("\n   FIX:")
    print("   - Close all other apps")
    print("   - Unplug and replug microphone")
    print("   - Check Windows/Mac/Linux mic permissions")
    sys.exit(1)

except Exception as e:
    print(f"   ❌ Error: {e}")
    print(f"   Type: {type(e).__name__}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Check 6: Quick listen test
print("\n6️⃣ Testing speech recognition...")
print("   Say something in the next 3 seconds...")
try:
    recognizer = sr.Recognizer()
    mic = sr.Microphone()

    with mic as source:
        recognizer.adjust_for_ambient_noise(source, duration=0.5)
        print("   👂 Listening...")
        audio = recognizer.listen(source, timeout=3, phrase_time_limit=3)

    print("   🔄 Recognizing...")
    text = recognizer.recognize_google(audio)
    print(f"   ✅ You said: '{text}'")

except sr.WaitTimeoutError:
    print("   ⏰ No speech detected (this is OK for a test)")
except sr.UnknownValueError:
    print("   ⚠️  Couldn't understand (but mic is working!)")
except sr.RequestError as e:
    print(f"   ❌ Google API error: {e}")
    print("   Check your internet connection")
except Exception as e:
    print(f"   ❌ Error: {e}")
    import traceback
    traceback.print_exc()

# Final summary
print("\n" + "="*60)
print("📊 DIAGNOSTIC SUMMARY")
print("="*60)

print("\n✅ If you see 'MICROPHONE IS WORKING' above:")
print("   Your hardware is fine!")
print("   The crash might be:")
print("   - Missing TTS_Fixed.py in Backend folder")
print("   - Old SEEU.py (not the crash-resistant version)")
print("   - Another app using microphone")

print("\n❌ If you see errors above:")
print("   Fix those errors first before running SEEU")

print("\n💡 NEXT STEPS:")
print("   1. Fix any errors shown above")
print("   2. Make sure you replaced BOTH files:")
print("      - SEEU.py (main file)")
print("      - Backend/TTS.py (with TTS_Fixed.py)")
print("   3. Close all other apps using microphone")
print("   4. Run: python SEEU.py")

print("\n" + "="*60)
print("✅ Diagnostic complete!")
print("="*60)