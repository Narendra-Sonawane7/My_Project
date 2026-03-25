
# --------------------------------------------------------------------------------------------------------

import eel
import os
import sys
import threading
import time
import json
import atexit
import signal
from datetime import datetime

# ------------------------------------------------------------
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Import backend modules
try:
    from Backend.Brain import SEEUAssistant
    from Backend.TTS import SpeakSeeu
    from Backend.STT import recognize_speech, continuous_listen, ContinuousListeningManager, start_continuous_listening
except ImportError as e:
    print(f"Critical Import Error: {e}. Ensure Backend modules exist.")
    sys.exit(1)
except Exception as ex:
    print(f"An unexpected error occurred during initial imports: {ex}")
    sys.exit(1)

# Import NotificationMonitor (graceful fallback if unavailable)
try:
    from Backend.NotificationMonitor import NotificationMonitor
    NOTIFICATION_MONITOR_AVAILABLE = True
except ImportError:
    NOTIFICATION_MONITOR_AVAILABLE = False
    print("⚠️  NotificationMonitor not found – notification alerts disabled")


# --- MODE CONSTANTS ---
MODE_PUSH_TO_TALK = "push_to_talk"
MODE_CONTINUOUS = "continuous"

# Global shutdown flag and stop event for continuous listening
shutdown_flag = threading.Event()
continuous_stop_flag = None
continuous_thread = None

# --- TTS Manager for Stoppable, Threaded Speech ---
class TTSManager:
    """Manages TTS playback in a non-blocking thread, allowing for interruption."""

    def __init__(self):
        self.tts_thread = None
        self.stop_event = threading.Event()
        self.is_speaking = False
        self.lock = threading.Lock()

    def speak(self, text_to_speak):
        """Speaks the given text in a non-blocking thread."""
        with self.lock:
            if self.tts_thread and self.tts_thread.is_alive():
                self.stop()
                self.tts_thread.join(timeout=2.0)

            self.stop_event.clear()

            self.tts_thread = threading.Thread(
                target=self._run_tts_in_thread,
                args=(text_to_speak,),
                daemon=True
            )
            self.tts_thread.start()

    def _run_tts_in_thread(self, text):
        """Worker function that runs in a separate thread."""
        try:
            with self.lock:
                self.is_speaking = True

            try:
                eel.notify_tts_status('speaking')
            except Exception as e:
                print(f"Could not notify frontend of TTS start: {e}")

            print(f"TTS Playback initiated: {text[:50]}...")

            def stoppable_callback():
                return not self.stop_event.is_set() and not shutdown_flag.is_set()

            try:
                SpeakSeeu(text, callback_func=stoppable_callback)
            except TypeError:
                print("Warning: SpeakSeeu doesn't support callback. TTS won't be interruptible.")
                SpeakSeeu(text)
            except Exception as tts_error:
                print(f"Error in SpeakSeeu: {tts_error}")

        except Exception as e:
            print(f"Error during TTS playback in thread: {e}")
        finally:
            with self.lock:
                self.is_speaking = False

            print("TTS playback finished or was stopped.")
            self.stop_event.clear()

            try:
                eel.notify_tts_status('idle')
            except Exception as e:
                print(f"Could not notify frontend of TTS end: {e}")

    def stop(self):
        """Signals the currently running TTS thread to stop playback."""
        print("TTS stop request received.")
        self.stop_event.set()

    def is_currently_speaking(self):
        """Check if TTS is currently active."""
        with self.lock:
            return self.is_speaking


# --- STT (Speech Recognition) Manager ---
class STTManager:
    """Manages speech-to-text functionality with proper threading and state management."""

    def __init__(self):
        self.is_listening = False
        self.listen_thread = None
        self.continuous_thread = None
        self.continuous_stop_flag = None
        self.stop_listening_flag = threading.Event()
        self.lock = threading.Lock()
        self.mode = MODE_PUSH_TO_TALK

    def set_mode(self, mode):
        """Set the listening mode."""
        if mode not in [MODE_PUSH_TO_TALK, MODE_CONTINUOUS]:
            return False
        self.mode = mode
        return True

    def get_mode(self):
        """Get current listening mode."""
        return self.mode

    def start_listening(self, callback):
        """Start listening for speech input in a separate thread (Push-to-Talk)."""
        with self.lock:
            if self.is_listening:
                print("Already listening...")
                return False

            self.is_listening = True
            self.stop_listening_flag.clear()

        self.listen_thread = threading.Thread(
            target=self._listen_worker,
            args=(callback,),
            daemon=True
        )
        self.listen_thread.start()
        return True

    def _listen_worker(self, callback):
        """Worker thread that handles speech recognition."""
        try:
            print("🎤 Starting speech recognition (Push-to-Talk)...")
            recognized_text = recognize_speech(
                callback=None,
                timeout=10,
                phrase_time_limit=10
            )

            if recognized_text:
                print(f"✅ Recognized: {recognized_text}")
                if callback:
                    callback(recognized_text)
            else:
                print("⚠️ No speech recognized")

        except Exception as e:
            print(f"❌ Error in speech recognition: {e}")
        finally:
            with self.lock:
                self.is_listening = False
            print("🎤 Speech recognition stopped")

    def stop_listening(self):
        """Stop the current listening session."""
        with self.lock:
            if not self.is_listening:
                return
            self.stop_listening_flag.set()
            self.is_listening = False
        print("🛑 Stopping speech recognition...")

    def is_currently_listening(self):
        """Check if currently listening for speech."""
        with self.lock:
            return self.is_listening

    # --- CONTINUOUS LISTENING MODE METHODS (NO WAKE WORD) ---
    def start_continuous_listening(self, callback):
        """Start continuous listening mode - NO WAKE WORD."""
        global continuous_stop_flag, continuous_thread

        with self.lock:
            if self.continuous_thread and self.continuous_thread.is_alive():
                print("Continuous listening already active")
                return False

        print(f"🎯 Starting continuous listening mode (no wake word)...")

        # Create a new stop flag for this session
        self.continuous_stop_flag = threading.Event()
        continuous_stop_flag = self.continuous_stop_flag

        self.continuous_thread = threading.Thread(
            target=self._continuous_listen_worker,
            args=(callback, self.continuous_stop_flag),
            daemon=True
        )
        self.continuous_thread.start()
        continuous_thread = self.continuous_thread
        return True

    def _continuous_listen_worker(self, callback, stop_flag):
        """Worker thread for continuous listening - NO WAKE WORD."""
        try:
            print(f"🎯 Continuous listening started (no wake word required)")
            continuous_listen(
                callback=callback,
                stop_flag=stop_flag
            )
        except Exception as e:
            print(f"❌ Error in continuous listening: {e}")
        finally:
            print("🎯 Continuous listening stopped")

    def stop_continuous_listening(self):
        """Stop continuous listening mode."""
        global continuous_stop_flag, continuous_thread

        with self.lock:
            if self.continuous_stop_flag:
                print("🛑 Stopping continuous listening...")
                self.continuous_stop_flag.set()
                self.continuous_stop_flag = None
            self.continuous_thread = None
            continuous_thread = None
            continuous_stop_flag = None
        return True

    def cleanup(self):
        """Clean up all listening threads."""
        print("🧹 Cleaning up STT manager...")
        self.stop_listening()
        self.stop_continuous_listening()
        time.sleep(0.5)


# Initialize managers and assistant
tts_manager = TTSManager()
stt_manager = STTManager()
assistant = None
assistant_ready = False
web_folder = os.path.join(current_dir, 'web')

# Notification monitor (Windows Action Center)
notification_monitor = None

def initialize_assistant():
    """Initialize assistant with proper error handling."""
    global assistant, assistant_ready
    try:
        print("🧠 Initializing SEEU Assistant with memory...")
        assistant = SEEUAssistant()
        assistant_ready = True
        print("✅ SEEU Assistant initialized successfully with memory persistence")

        if hasattr(assistant, 'get_summary'):
            summary = assistant.get_summary()
            print(f"\n{summary}")

        return True
    except ValueError as ve:
        print(f"Configuration Error: {ve}")
        return False
    except Exception as e:
        print(f"Error initializing SEEUAssistant: {e}")
        return False

def cleanup_assistant():
    """Clean up assistant memory and resources."""
    global assistant
    if assistant:
        try:
            print("💾 Saving SEEU memory before shutdown...")
            if hasattr(assistant, 'cleanup'):
                assistant.cleanup()
            print("✅ Memory saved successfully")
        except Exception as e:
            print(f"Error during cleanup: {e}")

def cleanup_all():
    """Clean up all resources before shutdown."""
    print("\n🛑 Shutting down SEEU...")

    # Set shutdown flag
    shutdown_flag.set()

    # Stop Notification Monitor
    global notification_monitor
    if notification_monitor and notification_monitor.is_running():
        print("🔕 Stopping Notification Monitor...")
        notification_monitor.stop()

    # Stop TTS
    if tts_manager:
        print("🔇 Stopping TTS...")
        tts_manager.stop()
        time.sleep(0.5)

    # Stop STT
    if stt_manager:
        print("🎤 Stopping STT...")
        stt_manager.cleanup()
        time.sleep(0.5)

    # Save assistant memory
    cleanup_assistant()

    # Stop Eel
    try:
        eel._shutdown = True
    except:
        pass

    print("✅ SEEU shutdown complete.")

    # Force exit after cleanup
    os._exit(0)

# Register cleanup functions
atexit.register(cleanup_all)

# Handle signals
def signal_handler(sig, frame):
    print(f"\n⚠️  Received signal {sig}")
    cleanup_all()

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

# Initialize assistant
initialize_assistant()

# Verify web folder exists
if not os.path.exists(web_folder):
    print(f"⚠️  Web folder not found at {web_folder}")
    web_folder = current_dir
    print(f"Using current directory: {web_folder}")

# Initialize Eel with web folder
eel.init(web_folder)


# ====================================================================
# EXPOSED FUNCTIONS FOR FRONTEND
# ====================================================================

@eel.expose
def process_voice_command(user_input):
    """Process voice command and get AI response."""
    if not assistant:
        return {'success': False, 'response': 'Assistant not initialized', 'command': None}

    try:
        print(f"\n{'='*60}")
        print(f"📩 Processing voice command: {user_input}")
        print(f"{'='*60}")

        response = assistant.process_message(user_input)

        # Notify frontend
        try:
            if hasattr(eel, 'command_processed'):
                eel.command_processed(user_input, response)
        except:
            pass

        return {
            'success': True,
            'response': response,
            'command': user_input
        }

    except Exception as e:
        error_msg = f"Error processing command: {str(e)}"
        print(f"❌ {error_msg}")
        return {'success': False, 'response': error_msg, 'command': user_input}


@eel.expose
def start_speech_recognition():
    """Start speech recognition based on current mode."""
    print(f"🎤 Starting speech recognition in {stt_manager.get_mode()} mode...")

    def handle_recognized_text(text):
        """Handle recognized text and send to frontend."""
        if not text:
            return

        try:
            eel.speech_recognized(text)
        except Exception as e:
            print(f"Error handling recognized text: {e}")

    try:
        if stt_manager.get_mode() == MODE_CONTINUOUS:
            success = stt_manager.start_continuous_listening(handle_recognized_text)
            return {'success': success, 'message': 'Continuous listening started' if success else 'Already listening', 'mode': stt_manager.get_mode()}
        else:
            success = stt_manager.start_listening(handle_recognized_text)
            return {'success': success, 'message': 'Listening started' if success else 'Already listening', 'mode': stt_manager.get_mode()}
    except Exception as e:
        print(f"Error starting speech recognition: {e}")
        return {'success': False, 'message': str(e), 'mode': stt_manager.get_mode()}


@eel.expose
def stop_speech_recognition():
    """Stop listening for speech input."""
    print("🛑 Stop speech recognition requested")
    try:
        if stt_manager.get_mode() == MODE_CONTINUOUS:
            stt_manager.stop_continuous_listening()
        else:
            stt_manager.stop_listening()
        return True
    except Exception as e:
        print(f"Error stopping speech recognition: {e}")
        return False


@eel.expose
def set_listening_mode(mode):
    """Switch between push-to-talk and continuous listening modes."""
    print(f"🔄 Switching to {mode} mode...")

    # Stop current listening first
    if stt_manager.get_mode() == MODE_CONTINUOUS:
        stt_manager.stop_continuous_listening()
    else:
        stt_manager.stop_listening()
    time.sleep(0.5)

    success = stt_manager.set_mode(mode)

    if success:
        print(f"✅ Mode switched to: {mode}")
        return {'success': True, 'current_mode': mode, 'message': f'Switched to {mode} mode'}
    else:
        return {'success': False, 'current_mode': stt_manager.get_mode(), 'message': 'Invalid mode'}


@eel.expose
def get_listening_mode():
    """Get current listening mode."""
    return stt_manager.get_mode()


@eel.expose
def is_listening():
    """Check if currently listening for speech."""
    if stt_manager.get_mode() == MODE_CONTINUOUS:
        return stt_manager.continuous_thread is not None and stt_manager.continuous_thread.is_alive()
    else:
        return stt_manager.is_currently_listening()


@eel.expose
def get_system_status():
    """Get current system status."""
    try:
        import speech_recognition as sr
        mic_available = True
        try:
            mic = sr.Microphone()
            with mic as source:
                pass
        except:
            mic_available = False

        status = {
            'assistant_ready': assistant is not None and assistant_ready,
            'tts_speaking': tts_manager.is_currently_speaking(),
            'stt_listening': is_listening(),
            'listening_mode': stt_manager.get_mode(),
            'system_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'microphone_available': mic_available,
            'speech_recognition_available': True,
            'memory_persistence': True if assistant else False
        }
        return status
    except Exception as e:
        print(f"Error getting system status: {e}")
        return {
            'assistant_ready': False,
            'tts_speaking': False,
            'stt_listening': False,
            'listening_mode': MODE_PUSH_TO_TALK,
            'system_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'microphone_available': False,
            'speech_recognition_available': False,
            'memory_persistence': False
        }


@eel.expose
def request_tts(text_to_speak):
    """Handle text-to-speech requests."""
    print(f"TTS Request: '{text_to_speak[:50]}...'")

    if not text_to_speak or not isinstance(text_to_speak, str) or not text_to_speak.strip():
        print("TTS Request Ignored: No valid text provided.")
        return False

    try:
        tts_manager.speak(text_to_speak.strip())
        return True
    except Exception as e:
        print(f"Error initiating TTS: {e}")
        return False


@eel.expose
def stop_tts():
    """Stop TTS from the frontend."""
    print("Stop TTS requested from frontend")
    try:
        tts_manager.stop()
        return True
    except Exception as e:
        print(f"Error stopping TTS: {e}")
        return False


@eel.expose
def notify_tts_status(status):
    """Notify frontend of TTS status."""
    pass


def main():
    """Main function to start the application."""
    host = 'localhost'
    port = 8000

    # Pre-initialize TTS
    print("⚡ Pre-initializing TTS system...")
    try:
        from Backend.TTS import pre_initialize
        pre_initialize()
        print("✅ TTS pre-initialized successfully")
    except:
        pass

    # Start Notification Monitor
    global notification_monitor
    if NOTIFICATION_MONITOR_AVAILABLE:
        try:
            print("🔔 Starting Notification Monitor...")
            notification_monitor = NotificationMonitor(
                speak_callback=tts_manager.speak,
                poll_interval=4.0,
            )
            # Let the monitor know when SEEU is speaking so it can wait
            notification_monitor.set_speaking_check(tts_manager.is_currently_speaking)
            notification_monitor.start()
            print("✅ Notification Monitor started – WhatsApp, Gmail & system alerts active")
        except Exception as e:
            print(f"⚠️  Notification Monitor failed to start: {e}")
    else:
        print("⚠️  Notification Monitor unavailable – skipping")

    print("=" * 60)
    print("🚀 Starting SEEU AI Assistant Interface")
    print("=" * 60)
    print(f"🌐 Web Interface: http://{host}:{port}")
    print(f"📁 Web Folder: {web_folder}")
    print(f"🤖 Assistant Ready: {assistant_ready}")
    print(f"💾 Memory Persistence: ENABLED")
    print(f"🔊 TTS Manager: Ready")
    print(f"🎤 STT Manager: Ready")
    print(f"🎯 Current Mode: {stt_manager.get_mode()}")
    print(f"🔔 Notification Monitor: {'Active' if notification_monitor and notification_monitor.is_running() else 'Inactive'}")
    if stt_manager.get_mode() == MODE_CONTINUOUS:
        print(f"🎯 Listening Mode: Continuous (No wake word required)")
    print("=" * 60)

    try:
        index_path = os.path.join(web_folder, 'index.html')
        if not os.path.exists(index_path):
            print(f"❌ Error: index.html not found at {index_path}")
            return

        print("🎯 Starting web server...")
        eel.start('index.html',
                 size=(1200, 800),
                 block=True,
                 host=host,
                 port=port,
                 mode='chrome',
                 close_callback=lambda page, sockets: cleanup_all(),
                 cmdline_args=['--disable-web-security'])

    except Exception as e:
        print(f"❌ Error: {e}")
        cleanup_all()


if __name__ == '__main__':
    main()