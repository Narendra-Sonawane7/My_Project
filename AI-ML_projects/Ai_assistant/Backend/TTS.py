
# # ====================================================================



import pygame
import random
import asyncio
import edge_tts
import os
import re
import unicodedata
import tempfile
import time
import threading
from dotenv import load_dotenv

load_dotenv()

class TTSEngine:
    """Enhanced TTS Engine with better interrupt handling"""

    def __init__(self):
        self.is_playing = False
        self.should_stop = False
        self.current_audio_file = None
        self.playback_thread = None
        self.lock = threading.Lock()

        # Initialize pygame mixer
        if not pygame.mixer.get_init():
            try:
                pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
            except pygame.error as e:
                print(f"Failed to initialize pygame mixer: {e}")
                raise

    def stop_playback(self):
        """Stop current playback immediately"""
        with self.lock:
            self.should_stop = True
            if pygame.mixer.get_init() and pygame.mixer.music.get_busy():
                pygame.mixer.music.stop()

    def is_currently_playing(self):
        """Check if TTS is currently playing"""
        with self.lock:
            return self.is_playing

def clean_text(text):
    """
    Thoroughly cleans text for speech synthesis by removing emojis and
    normalizing special characters while preserving speech-relevant punctuation.
    """
    if not text or not isinstance(text, str):
        return ""

    # First normalize unicode characters
    normalized_text = unicodedata.normalize('NFKD', text)

    # Remove emojis and other symbol characters
    cleaned_text = ''.join(
        char for char in normalized_text
        if not unicodedata.category(char).startswith('So') and
           not unicodedata.category(char).startswith('Cs') and
           not unicodedata.category(char).startswith('Co')
    )

    # Keep only alphanumeric, spaces, and punctuation important for speech
    cleaned_text = re.sub(r'[^\w\s.,!?:;\'"-()]', '', cleaned_text)

    # Fix common speech issues
    cleaned_text = re.sub(r'\s+', ' ', cleaned_text)
    cleaned_text = re.sub(r'\.{2,}', '.', cleaned_text)
    cleaned_text = re.sub(r'\?{2,}', '?', cleaned_text)
    cleaned_text = re.sub(r'!{2,}', '!', cleaned_text)

    return cleaned_text.strip()

async def text_to_audio_file(text, voice="en-US-AriaNeural"):
    """Converts text to speech audio file using edge-tts."""
    # Use timestamp and random number to create unique filename
    timestamp = int(time.time() * 1000)
    random_num = random.randint(1000, 9999)
    file_path = f"Database/TTS_{timestamp}_{random_num}.mp3"

    # Ensure the directory exists
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    try:
        communicate = edge_tts.Communicate(
            text,
            voice,
            pitch='+0Hz',
            rate='+13%',
            volume='+0%'
        )
        await communicate.save(file_path)
        return file_path
    except Exception as e:
        print(f"Error generating TTS audio: {e}")
        raise

def cleanup_old_tts_files():
    """Clean up old TTS files to prevent disk space issues."""
    try:
        database_dir = "Database"
        if not os.path.exists(database_dir):
            return

        current_time = time.time()
        for filename in os.listdir(database_dir):
            if filename.startswith("TTS_") and filename.endswith(".mp3"):
                file_path = os.path.join(database_dir, filename)
                try:
                    # Delete files older than 2 minutes
                    if current_time - os.path.getctime(file_path) > 120:
                        os.remove(file_path)
                        print(f"Cleaned up old TTS file: {filename}")
                except (OSError, FileNotFoundError):
                    continue
    except Exception as e:
        print(f"Error during TTS cleanup: {e}")

def text_to_speech(text, callback_func=None, voice="en-US-AriaNeural"):
    """
    Plays text as speech using pygame with improved interrupt handling.

    Returns:
        bool: True if playback completed, False if interrupted or error
    """
    if callback_func is None:
        callback_func = lambda: True

    audio_file = None
    completed = False

    try:
        # Initialize pygame mixer if not already initialized
        if not pygame.mixer.get_init():
            pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)

        # Clean up old files first
        cleanup_old_tts_files()

        # Generate the audio file
        print(f"Generating TTS for: {text[:50]}...")
        audio_file = asyncio.run(text_to_audio_file(text, voice))

        if not os.path.exists(audio_file):
            print("Error: TTS audio file was not created")
            return False

        # Load and play the audio
        pygame.mixer.music.load(audio_file)
        pygame.mixer.music.play()

        print("TTS playback started")

        # Wait while audio is playing with better interrupt checking
        clock = pygame.time.Clock()
        while pygame.mixer.music.get_busy():
            # Check callback more frequently for better responsiveness
            if not callback_func():
                print("TTS playback interrupted by callback")
                pygame.mixer.music.stop()
                break

            clock.tick(50)

        else:
            completed = True
            print("TTS playback completed")

    except Exception as e:
        print(f"Text-to-speech error: {e}")
        completed = False

    finally:
        # Clean up
        try:
            if pygame.mixer.get_init():
                pygame.mixer.music.stop()
                try:
                    pygame.mixer.music.unload()
                except:
                    pass
        except Exception as e:
            print(f"Error stopping TTS: {e}")

        # Clean up the audio file after a short delay
        if audio_file and os.path.exists(audio_file):
            def delayed_cleanup():
                time.sleep(0.5)
                try:
                    if os.path.exists(audio_file):
                        os.remove(audio_file)
                        print(f"Cleaned up TTS file: {os.path.basename(audio_file)}")
                except (OSError, FileNotFoundError):
                    pass

            cleanup_thread = threading.Thread(target=delayed_cleanup, daemon=True)
            cleanup_thread.start()

    return completed

def SpeakSeeu(text, callback_func=None, voice="en-US-AriaNeural"):
    """
    Enhanced text-to-speech function with better interrupt handling and smart text processing.

    Returns:
        bool: True if speech completed, False if interrupted or error
    """
    if not text or not isinstance(text, str):
        print("SpeakSeeu: No valid text provided")
        return False

    if callback_func is None:
        callback_func = lambda: True

    print(f"SpeakSeeu called with text length: {len(text)}")

    # Clean the input text
    cleaned_text = clean_text(text)

    if not cleaned_text:
        print("SpeakSeeu: No valid text after cleaning")
        return False

    try:
        # For very long text, speak only the beginning and add a note
        if len(cleaned_text) > 800:
            print("Long text detected, speaking summary...")
            sentences = re.split(r'(?<=[.!?])\s+', cleaned_text)

            if len(sentences) > 2:
                shortened_text = ' '.join(sentences[:2])
                shortened_text += " ... The complete response is displayed on screen."
                return text_to_speech(shortened_text, callback_func, voice)
            else:
                shortened_text = cleaned_text[:400] + "... The complete response is displayed on screen."
                return text_to_speech(shortened_text, callback_func, voice)
        else:
            return text_to_speech(cleaned_text, callback_func, voice)

    except Exception as e:
        print(f"Error in SpeakSeeu: {e}")
        return False

AVAILABLE_VOICES = {
    'aria': 'en-US-AriaNeural',
    'jenny': 'en-US-JennyNeural',
    'guy': 'en-US-GuyNeural',
    'jason': 'en-US-JasonNeural',
    'liam': 'en-CA-LiamNeural',
    'clara': 'en-CA-ClaraNeural'
}

def set_voice(voice_name):
    """Set the default voice for TTS"""
    return AVAILABLE_VOICES.get(voice_name.lower(), 'en-US-AriaNeural')

def pre_initialize():
    """Pre-initialize TTS system for faster first response."""
    print("⚡ Pre-initializing TTS system...")

    if not pygame.mixer.get_init():
        try:
            pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
            print("✅ Pygame mixer initialized")
            return True
        except Exception as e:
            print(f"❌ Failed to initialize pygame mixer: {e}")
            return False
    return True

if __name__ == "__main__":
    def test_callback():
        import time
        start_time = time.time()
        def callback():
            return time.time() - start_time < 3.0
        return callback

    pre_initialize()

    test_text = "This is a test of the improved text to speech system. It should respond much faster now."
    print("🧪 Testing optimized TTS...")

    start_time = time.time()
    result = SpeakSeeu(test_text)
    elapsed = time.time() - start_time
    print(f"✅ Normal TTS result: {result} (took {elapsed:.2f} seconds)")

    start_time = time.time()
    result = SpeakSeeu(test_text)
    elapsed = time.time() - start_time
    print(f"✅ Cached TTS result: {result} (took {elapsed:.2f} seconds)")

    print("⏱️ Testing interruptible TTS (will stop after 3 seconds)...")
    callback = test_callback()
    result = SpeakSeeu("This is a longer text that should be interrupted after three seconds.", callback)
    print(f"⏱️ Interruptible TTS result: {result}")