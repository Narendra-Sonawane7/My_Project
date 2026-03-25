#=================================================================
#=================================================================

import os
import re
import sys
import subprocess
import platform
from typing import Optional
from openai import OpenAI
from dotenv import load_dotenv
try:
    from google import genai
except ImportError:
    genai = None
    print("⚠️ Google Generative AI not available. Coder function disabled.")



class SeeuAI:
    """
    SEEU AI Assistant - Advanced Task Executor with System Controls
    Enhanced with: Brightness Control, Keyboard Control, Mouse Control, Advanced Typing, YouTube Automation, Window Management
    Optimized for continuous listening mode
    """

    def __init__(self):
        """Initialize SEEU AI Assistant"""
        self.load_environment()
        self.initialize_client()
        self.setup_conversation_context()
        self.command_history = []  # Track recent commands for context
        print("✅ SEEUAI initialized with enhanced controls (Continuous Listening Ready)")

    def load_environment(self):
        """Load environment variables safely"""
        try:
            load_dotenv()
            self.api_key = os.getenv("GROQ_API_KEY")
            if not self.api_key:
                raise ValueError("GROQ_API_KEY not found in environment variables")
        except Exception as e:
            print(f"❌ Failed to load environment: {e}")
            sys.exit(1)

    def initialize_client(self):
        """Initialize the Groq API client"""
        try:
            self.client = OpenAI(
                base_url="https://api.groq.com/openai/v1",
                api_key=self.api_key
            )
        except Exception as e:
            print(f"❌ Failed to initialize API client: {e}")
            sys.exit(1)

    def setup_conversation_context(self):
        """Setup the conversation context for SEEU AI with enhanced capabilities"""
        self.messages = [
            {
                "role": "system",
                "content": "You are SEEU, an advanced AI assistant designed for continuous voice interaction. Generate Python code to accomplish tasks. Be concise and responsive."
            },
            {
                "role": "system",
                "content": """Generate Python code for system tasks. Always wrap code in ```python code blocks.

Available: webbrowser, subprocess, os, psutil, pyautogui, pywhatkit, screen_brightness_control, keyboard, mouse, YouTubeAutomation

Examples:

User: open Calculator
```python
import subprocess
import platform
if platform.system() == 'Windows':
    subprocess.Popen(['calc.exe'])
else:
    subprocess.Popen(['gnome-calculator'])
print('✅ Calculator opened')
```

User: open Chrome
```python
import webbrowser
webbrowser.open('https://www.google.com')
print('✅ Chrome opened')
```

User: play music on YouTube
```python
import pywhatkit
pywhatkit.playonyt('music')
print('✅ YouTube opened')
```

User: type Hello
```python
import pyautogui
import time
time.sleep(1)
pyautogui.write('Hello', interval=0.1)
print('✅ Typed')
```

User: set brightness to 50%
```python
import screen_brightness_control as sbc
sbc.set_brightness(50)
print('✅ Brightness set to 50%')
```

User: increase brightness
```python
import screen_brightness_control as sbc
current = sbc.get_brightness()[0]
new_brightness = min(current + 10, 100)
sbc.set_brightness(new_brightness)
print(f'✅ Brightness increased to {new_brightness}%')
```

User: decrease brightness
```python
import screen_brightness_control as sbc
current = sbc.get_brightness()[0]
new_brightness = max(current - 10, 0)
sbc.set_brightness(new_brightness)
print(f'✅ Brightness decreased to {new_brightness}%')
```

User: press enter
```python
import pyautogui
pyautogui.press('enter')
print('✅ Enter key pressed')
```

User: press ctrl+c
```python
import pyautogui
pyautogui.hotkey('ctrl', 'c')
print('✅ Ctrl+C pressed')
```

User: move mouse to center
```python
import pyautogui
screen_width, screen_height = pyautogui.size()
pyautogui.moveTo(screen_width//2, screen_height//2, duration=0.5)
print('✅ Mouse moved to center')
```

User: click mouse
```python
import pyautogui
pyautogui.click()
print('✅ Mouse clicked')
```

User: scroll down
```python
import pyautogui
pyautogui.scroll(-3)
print('✅ Scrolled down')
```

User: scroll up
```python
import pyautogui
pyautogui.scroll(3)
print('✅ Scrolled up')
```

User: type in search bar
```python
import pyautogui
import time
time.sleep(1)
pyautogui.write('search query', interval=0.05)
print('✅ Typed in search bar')
```

User: close window
```python
import pyautogui
pyautogui.hotkey('alt', 'f4')
print('✅ Window closed')
```

User: close this window
```python
import pyautogui
pyautogui.hotkey('alt', 'f4')
print('✅ Current window closed')
```

User: close tab
```python
import pyautogui
pyautogui.hotkey('ctrl', 'w')
print('✅ Tab closed')
```

User: close browser
```python
import pyautogui
pyautogui.hotkey('alt', 'f4')
print('✅ Browser closed')
```

User: minimize window
```python
import pyautogui
pyautogui.hotkey('win', 'down')
print('✅ Window minimized')
```

User: maximize window
```python
import pyautogui
pyautogui.hotkey('win', 'up')
print('✅ Window maximized')
```

User: switch to next window
```python
import pyautogui
pyautogui.hotkey('alt', 'tab')
print('✅ Switched to next window')
```

User: play Despacito on YouTube
```python
import sys
sys.path.append('Backend')
from YouTubeAutomation import YouTubeController
yt = YouTubeController()
yt.play_video('Despacito')
print('✅ Playing Despacito on YouTube')
```

User: pause YouTube
```python
import sys
sys.path.append('Backend')
from YouTubeAutomation import YouTubeController
yt = YouTubeController()
yt.pause_play_toggle()
print('✅ YouTube paused/resumed')
```

User: pause the song
```python
import sys
sys.path.append('Backend')
from YouTubeAutomation import YouTubeController
yt = YouTubeController()
yt.pause_play_toggle()
print('✅ Song paused')
```

User: resume the song
```python
import sys
sys.path.append('Backend')
from YouTubeAutomation import YouTubeController
yt = YouTubeController()
yt.pause_play_toggle()
print('✅ Song resumed')
```

User: next song
```python
import sys
sys.path.append('Backend')
from YouTubeAutomation import YouTubeController
yt = YouTubeController()
yt.next_video()
print('✅ Playing next song')
```

User: previous song
```python
import sys
sys.path.append('Backend')
from YouTubeAutomation import YouTubeController
yt = YouTubeController()
yt.previous_video()
print('✅ Playing previous song')
```

User: mute the song
```python
import sys
sys.path.append('Backend')
from YouTubeAutomation import YouTubeController
yt = YouTubeController()
yt.mute_unmute_toggle()
print('✅ Song muted/unmuted')
```

User: mute youtube
```python
import sys
sys.path.append('Backend')
from YouTubeAutomation import YouTubeController
yt = YouTubeController()
yt.mute_unmute_toggle()
print('✅ Muted/unmuted')
```

User: next video on YouTube
```python
import sys
sys.path.append('Backend')
from YouTubeAutomation import YouTubeController
yt = YouTubeController()
yt.next_video()
print('✅ Skipped to next video')
```

User: increase YouTube volume
```python
import sys
sys.path.append('Backend')
from YouTubeAutomation import YouTubeController
yt = YouTubeController()
yt.volume_up(3)
print('✅ YouTube volume increased')
```

User: volume up youtube
```python
import sys
sys.path.append('Backend')
from YouTubeAutomation import YouTubeController
yt = YouTubeController()
yt.volume_up(3)
print('✅ Volume increased')
```

User: what is the current volume
```python
print('❌ Cannot read YouTube volume - can only increase/decrease it')
```

User: check youtube volume
```python
print('❌ YouTube volume cannot be checked - only adjusted up/down')
```

User: decrease YouTube volume
```python
import sys
sys.path.append('Backend')
from YouTubeAutomation import YouTubeController
yt = YouTubeController()
yt.volume_down(3)
print('✅ YouTube volume decreased')
```

User: volume down youtube
```python
import sys
sys.path.append('Backend')
from YouTubeAutomation import YouTubeController
yt = YouTubeController()
yt.volume_down(3)
print('✅ Volume decreased')
```

User: mute YouTube
```python
import sys
sys.path.append('Backend')
from YouTubeAutomation import YouTubeController
yt = YouTubeController()
yt.mute_unmute_toggle()
print('✅ YouTube muted/unmuted')
```

User: fullscreen YouTube
```python
import sys
sys.path.append('Backend')
from YouTubeAutomation import YouTubeController
yt = YouTubeController()
yt.fullscreen_toggle()
print('✅ YouTube fullscreen toggled')
```

User: skip forward 10 seconds
```python
import sys
sys.path.append('Backend')
from YouTubeAutomation import YouTubeController
yt = YouTubeController()
yt.seek_forward(10)
print('✅ Skipped forward 10 seconds')
```

User: rewind 10 seconds
```python
import sys
sys.path.append('Backend')
from YouTubeAutomation import YouTubeController
yt = YouTubeController()
yt.seek_backward(10)
print('✅ Rewound 10 seconds')
```

User: search YouTube for funny cats
```python
import sys
sys.path.append('Backend')
from YouTubeAutomation import YouTubeController
yt = YouTubeController()
yt.search_youtube('funny cats')
print('✅ Searched YouTube for funny cats')
```

User: close YouTube tab
```python
import sys
sys.path.append('Backend')
from YouTubeAutomation import YouTubeController
yt = YouTubeController()
yt.close_youtube_tab()
print('✅ YouTube tab closed')
```

User: enable YouTube captions
```python
import sys
sys.path.append('Backend')
from YouTubeAutomation import YouTubeController
yt = YouTubeController()
yt.toggle_captions()
print('✅ YouTube captions toggled')
```

User: speed up YouTube video
```python
import sys
sys.path.append('Backend')
from YouTubeAutomation import YouTubeController
yt = YouTubeController()
yt.increase_speed()
print('✅ YouTube playback speed increased')
```

User: slow down YouTube video
```python
import sys
sys.path.append('Backend')
from YouTubeAutomation import YouTubeController
yt = YouTubeController()
yt.decrease_speed()
print('✅ YouTube playback speed decreased')
```

User: previous video on YouTube
```python
import sys
sys.path.append('Backend')
from YouTubeAutomation import YouTubeController
yt = YouTubeController()
yt.previous_video()
print('✅ Returned to previous video')
```

User: theater mode YouTube
```python
import sys
sys.path.append('Backend')
from YouTubeAutomation import YouTubeController
yt = YouTubeController()
yt.theater_mode_toggle()
print('✅ YouTube theater mode toggled')
```

IMPORTANT REQUIREMENTS FOR CONTINUOUS LISTENING:
1. Always wrap Python code in ```python blocks
2. Always include print statements for feedback
3. Keep responses concise (under 100 chars for spoken feedback)
4. For voice interaction, prioritize action over explanation
5. Handle errors gracefully with informative messages
6. For YouTube commands, import YouTubeController from Backend/YouTubeAutomation
7. For window management, use pyautogui hotkeys (Alt+F4, Ctrl+W, etc.)

CRITICAL - YOUTUBE VOLUME LIMITATIONS:
- YouTube volume CANNOT be read/retrieved (no get_volume method exists!)
- You can ONLY increase or decrease volume, never check current level
- If user asks about current volume, explain it cannot be checked
- Never generate code with get_volume(), read_volume(), or check_volume()
- Only use: volume_up(steps) and volume_down(steps) methods"""
            }
        ]

    def execute_task(self, task: str) -> Optional[str]:
        """Execute a task using the Groq API"""
        try:
            print(f"📡 Calling API for: {task}")
            response = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=self.messages + [{"role": "user", "content": task}],
                max_tokens=1500,
                temperature=0.7,
                top_p=0.9
            )
            result = response.choices[0].message.content.strip()
            print(f"📥 Got response ({len(result)} chars)")
            return result
        except Exception as e:
            print(f"❌ API Error: {e}")
            return None

    def extract_code_from_response(self, response: str) -> Optional[str]:
        """Extract Python code from the API response"""
        if not response:
            print("⚠️ No response to extract from")
            return None

        # Try to find code blocks
        patterns = [
            r'```python\n(.*?)\n```',
            r'```\n(.*?)\n```',
        ]

        for pattern in patterns:
            matches = re.findall(pattern, response, re.DOTALL)
            if matches:
                code = matches[0].strip()
                print(f"✅ Extracted {len(code)} chars of code")
                return code

        print("⚠️ No code blocks found in response")
        return None

    def validate_code_safety(self, code: str) -> bool:
        """Basic safety validation"""
        dangerous = ['rm -rf /', 'format c:', 'del /f /s', 'rmdir /s', 'DROP TABLE', 'DELETE FROM']
        for pattern in dangerous:
            if pattern.lower() in code.lower():
                print(f"🚫 Blocked dangerous pattern: {pattern}")
                return False
        return True

    def execute_python_code(self, code: str) -> str:
        """Execute Python code with VERBOSE output"""
        if not code:
            return "❌ No code provided"

        if not self.validate_code_safety(code):
            return "🚫 Blocked for safety"

        print("\n" + "="*60)
        print("🚀 EXECUTING CODE:")
        print("="*60)
        print(code)
        print("="*60)

        try:
            # Import all modules we might need
            import_code = """
import os
import sys
import time
import webbrowser
import subprocess
import platform
"""
            # Try to import optional modules with better error handling
            optional_imports = {
                'psutil': 'import psutil',
                'pyautogui': 'import pyautogui',
                'pywhatkit': 'import pywhatkit',
                'screen_brightness_control': 'import screen_brightness_control as sbc',
                'keyboard': 'import keyboard',
                'mouse': 'import mouse',
            }

            for module_name, import_statement in optional_imports.items():
                try:
                    exec(import_statement)
                    import_code += f"{import_statement}\n"
                    print(f"✅ Loaded {module_name}")
                except ImportError:
                    print(f"⚠️ {module_name} not available (install with: pip install {module_name})")

            # Combine imports and code
            full_code = import_code + "\n" + code

            print("\n🔧 Executing now...")

            # Create execution namespace
            exec_namespace = {
                '__name__': '__main__',
                '__builtins__': __builtins__,
            }

            # Execute!
            exec(full_code, exec_namespace)

            print("✅ Code executed without errors")
            return "✅ Executed successfully Naru"

        except ImportError as e:
            error_msg = f"❌ Missing module: {e}"
            print(error_msg)
            return error_msg

        except Exception as e:
            error_msg = f"❌ Execution error: {e}"
            print(error_msg)
            import traceback
            traceback.print_exc()
            return error_msg

    def run_task(self, task: str) -> str:
        """Complete task execution pipeline (optimized for continuous mode)"""
        if not task.strip():
            return "❌ No task"

        # Track command for context
        self.command_history.append(task)
        if len(self.command_history) > 5:
            self.command_history.pop(0)

        print(f"\n🎯 TASK: {task}")
        print("-" * 60)

        # Step 1: Get AI response
        response = self.execute_task(task)
        if not response:
            return "❌ No AI response"

        # Step 2: Extract code
        code = self.extract_code_from_response(response)
        if not code:
            return f"❌ No code found"

        # Step 3: Execute code
        result = self.execute_python_code(code)
        return result


# Test if run directly
if __name__ == "__main__":
    print("\n🦾 SEEU Automation Test Mode - Enhanced for Continuous Listening")
    print("="*60)
    print("Available commands:")
    print("  🌞 Brightness: 'set brightness 50', 'increase brightness', 'decrease brightness'")
    print("  ⌨️  Keyboard: 'press enter', 'press ctrl+c', 'type hello world'")
    print("  🖱️  Mouse: 'click', 'move mouse to 500 300', 'scroll down'")
    print("  🌐 Web: 'open Brave', 'play music on youtube'")
    print("  📱 Apps: 'open calculator', 'open notepad'")
    print("  🎵 YouTube: 'play Despacito', 'pause YouTube', 'next video', 'volume up'")
    print("  🪟 Windows: 'close window', 'close tab', 'minimize window', 'switch window'")
    print("="*60)

    try:
        seeu = SeeuAI()

        # Interactive test
        while True:
            task = input("\n🎤 Enter command (or 'exit'): ").strip()
            if task.lower() in ['exit', 'quit']:
                break

            if task:
                result = seeu.run_task(task)
                print(f"\n📊 Result: {result}")

    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


# ContentGenerator (keeping your existing code)
class ContentGenerator:
    def __init__(self, api_key=None):
        if genai is None:
            raise ImportError("google-generativeai not installed. Run: pip install google-generativeai")
        load_dotenv()
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("No API key found. Please set GEMINI_API_KEY in .env")
        genai.configure(api_key=self.api_key)
        self.generation_config = {
            "temperature": 1,
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 8192,
            "response_mime_type": "text/plain",
        }
        self.output_dir = self._create_output_directory()

    def _create_output_directory(self):
        output_dir = "Database"
        os.makedirs(output_dir, exist_ok=True)
        return output_dir

    def _clean_filename(self, title):
        clean_title = re.sub(r'[^\w\s-]', '', title)
        return clean_title.strip().replace(' ', '_')

    def generate_content(self, prompt, custom_config=None):
        config = {**self.generation_config, **(custom_config or {})}
        try:
            model = genai.GenerativeModel(
                model_name="gemini-2.0-flash",
                generation_config=config,
                system_instruction="You are FALCON. Generate clear, concise content.",
            )
            chat_session = model.start_chat(history=[])
            response = chat_session.send_message(prompt)
            content = response.text
            clean_title = self._clean_filename(prompt[:50])
            timestamp = response.created.strftime("%Y%m%d_%H%M%S")
            filename = f"{clean_title}_{timestamp}.txt"
            filepath = os.path.join(self.output_dir, filename)
            with open(filepath, 'w', encoding='utf-8') as file:
                file.write(content)
            self._open_file(filepath)
            return content
        except Exception as e:
            print(f"Error: {e}")
            return None

    def _open_file(self, filepath):
        try:
            if os.name == 'nt':
                os.startfile(filepath)
            elif os.name == 'posix':
                subprocess.call(('open', filepath))
        except Exception as e:
            print(f"Error: {e}")

def Coder(topic):
    generator = ContentGenerator()
    generator.generate_content(topic)