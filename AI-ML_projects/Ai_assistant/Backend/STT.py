
#====================================================================



import speech_recognition as sr
import time
import threading

def recognize_speech(callback=None, timeout=10, phrase_time_limit=5):
    """
    Enhanced speech recognition with better error handling and configuration.
    """
    recognizer = sr.Recognizer()

    recognizer.energy_threshold = 300
    recognizer.dynamic_energy_threshold = True
    recognizer.dynamic_energy_adjustment_damping = 0.15
    recognizer.dynamic_energy_ratio = 1.5
    recognizer.pause_threshold = 0.8
    recognizer.operation_timeout = None
    recognizer.phrase_threshold = 0.3
    recognizer.non_speaking_duration = 0.5

    mic = sr.Microphone()

    with mic as source:
        print("🎤 SEEU is listening...")
        recognizer.adjust_for_ambient_noise(source, duration=1)
        print("🔧 Audio calibrated. Speak now...")

        try:
            audio = recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
        except sr.WaitTimeoutError:
            print("⏰ Listening timeout - no speech detected")
            return None

    try:
        text = recognizer.recognize_google(
            audio,
            language='en-US',
            show_all=False
        )

        print(f"🗣️  User: {text}")
        if callback:
            callback(text)
        return text

    except sr.UnknownValueError:
        print("🤖 Could not understand audio - please speak clearly")
        return None
    except sr.RequestError as e:
        print(f"📡 Could not request results from Google Speech Recognition service; {e}")
        return None
    except Exception as e:
        print(f"❌ Unexpected error in speech recognition: {e}")
        return None


class ContinuousListeningManager:
    """
    Continuous listening mode - NO WAKE WORD, just listens and processes commands immediately.
    """
    def __init__(self):
        self.is_listening = False
        self.should_stop = False
        self.stop_event = threading.Event()
        self.recognizer = sr.Recognizer()
        self.setup_recognizer()

    def setup_recognizer(self):
        """Configure recognizer for optimal continuous listening"""
        self.recognizer.energy_threshold = 400
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.dynamic_energy_adjustment_damping = 0.15
        self.recognizer.dynamic_energy_ratio = 1.5
        self.recognizer.pause_threshold = 0.6
        self.recognizer.phrase_threshold = 0.3
        self.recognizer.non_speaking_duration = 0.5


def continuous_listen(callback=None, stop_flag=None):
    """
    Continuous listening mode - NO WAKE WORD.
    Listens continuously and calls callback with any recognized speech.

    Args:
        callback: Function to call with recognized commands
        stop_flag: threading.Event to signal when to stop
    """
    manager = ContinuousListeningManager()

    if stop_flag is None:
        stop_flag = threading.Event()

    print(f"\n{'='*60}")
    print(f"🎯 CONTINUOUS LISTENING MODE ACTIVATED")
    print(f"{'='*60}")
    print(f"Listening continuously - just speak your commands!")
    print(f"Press Ctrl+C to stop\n")
    print(f"{'='*60}\n")

    manager.is_listening = True
    mic = sr.Microphone()

    try:
        with mic as source:
            manager.recognizer.adjust_for_ambient_noise(source, duration=2)
            print("✅ Background noise calibrated\n")

        while manager.is_listening and not stop_flag.is_set():
            try:
                with mic as source:
                    print("👂 Listening for command...", end='\r')

                    audio = manager.recognizer.listen(
                        source,
                        timeout=1,
                        phrase_time_limit=10
                    )

                try:
                    text = manager.recognizer.recognize_google(
                        audio,
                        language='en-US',
                        show_all=False
                    )

                    if text and text.strip():
                        print(f"\n🗣️  Command: '{text}'")
                        if callback:
                            callback(text)

                except sr.UnknownValueError:
                    # Could not understand audio - continue listening
                    pass
                except sr.RequestError as e:
                    print(f"\n📡 Recognition service error: {e}")
                    time.sleep(2)

            except sr.WaitTimeoutError:
                # No speech detected - continue listening
                continue
            except Exception as e:
                if not stop_flag.is_set():
                    print(f"\n❌ Error: {e}")
                time.sleep(0.5)

    except Exception as e:
        print(f"\n❌ Fatal error in continuous listening: {e}")
    finally:
        manager.is_listening = False
        print("\n✅ Continuous listening mode exited")


def start_continuous_listening(callback=None, stop_flag=None):
    """
    Start continuous listening in a background thread.

    Args:
        callback: Function to call with recognized commands
        stop_flag: threading.Event to signal when to stop

    Returns:
        tuple: (listening_thread, stop_flag)
    """
    if stop_flag is None:
        stop_flag = threading.Event()

    listen_thread = threading.Thread(
        target=continuous_listen,
        args=(callback, stop_flag),
        daemon=True
    )
    listen_thread.start()
    return listen_thread, stop_flag


if __name__ == "__main__":
    print("\n🧪 TEST: Continuous Listening Mode (No Wake Word)")
    print("="*60)

    def test_callback(command):
        print(f"\n✨ COMMAND RECEIVED: {command}")

    stop_flag = threading.Event()

    try:
        thread, flag = start_continuous_listening(test_callback, stop_flag)
        thread.join()
    except KeyboardInterrupt:
        print("\n\n🛑 Test stopped by user")
        stop_flag.set()