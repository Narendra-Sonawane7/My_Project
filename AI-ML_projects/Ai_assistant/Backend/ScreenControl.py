"""
ScreenControl.py - Screen Vision & Control Module for SEEU AI
=============================================================
Gives SEEU the ability to:
  • See & describe what's on the screen
  • Read text / error messages from the screen
  • Detect and suggest fixes for on-screen problems
  • Type text on command
  • Click, scroll and perform mouse actions by voice
  • Solve on-screen problems automatically

Uses:
  - pyautogui  → screenshot + mouse/keyboard control
  - Pillow     → image processing
  - Groq API   → vision model (llama-3.2-11b-vision-preview) for screen understanding
  - pytesseract (optional) → OCR fallback
"""

import os
import sys
import base64
import time
import threading
import re
from io import BytesIO
from datetime import datetime
from typing import Optional

# ── Third-party ──────────────────────────────────────────────────────────────
try:
    import pyautogui
    pyautogui.FAILSAFE = True          # move mouse to top-left corner to abort
    PYAUTOGUI_AVAILABLE = True
except ImportError:
    PYAUTOGUI_AVAILABLE = False
    print("⚠️ pyautogui not installed: pip install pyautogui")

try:
    from PIL import Image, ImageEnhance, ImageFilter
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    print("⚠️ Pillow not installed: pip install Pillow")

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("⚠️ openai not installed: pip install openai")

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Optional OCR fallback
try:
    import pytesseract
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False

# ─────────────────────────────────────────────────────────────────────────────
#  SCREEN KEYWORDS – used by Brain.py to detect screen commands
# ─────────────────────────────────────────────────────────────────────────────
SCREEN_KEYWORDS = [
    # What's on screen
    'what is on the screen', 'what\'s on the screen', 'whats on screen',
    'what do you see', 'look at the screen', 'see the screen',
    'describe the screen', 'describe what you see', 'show me what',
    # Error / problem detection
    'what does the error say', 'read the error', 'what error',
    'what is the error', 'error on screen', 'solve the problem',
    'fix the problem', 'fix the error', 'help me with the error',
    'what is wrong', 'whats wrong on screen',
    # Read screen text
    'read the screen', 'read what is written', 'what does it say',
    'what is written', 'read this', 'what text',
    # Take screenshot
    'take a screenshot', 'capture the screen', 'screenshot',
    # Typing commands
    'type ', 'write ', 'enter text',
    # Screen analysis
    'analyze the screen', 'analyse the screen', 'check the screen',
    'look at this', 'tell me about the screen',
]

# ─────────────────────────────────────────────────────────────────────────────
#  SCREEN CONTROLLER CLASS
# ─────────────────────────────────────────────────────────────────────────────
class ScreenController:
    """
    Main class that gives SEEU eyes on the screen and fine-grained control.
    """

    # Vision model via Groq (supports images)
    VISION_MODEL = "meta-llama/llama-4-scout-17b-16e-instruct"
    FALLBACK_MODEL = "llama-3.2-11b-vision-preview"

    def __init__(self):
        self.screenshot_dir = "Database/Screenshots"
        os.makedirs(self.screenshot_dir, exist_ok=True)

        # Groq client for vision
        self.client = None
        self._init_groq_client()

        print("✅ ScreenController initialized")

    # ── Initialisation ────────────────────────────────────────────────────────
    def _init_groq_client(self):
        """Initialize Groq API client for vision model."""
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            print("⚠️ GROQ_API_KEY not found – vision features disabled")
            return
        if not OPENAI_AVAILABLE:
            print("⚠️ openai library missing – vision features disabled")
            return
        try:
            self.client = OpenAI(
                base_url="https://api.groq.com/openai/v1",
                api_key=api_key
            )
            print("✅ Groq vision client ready")
        except Exception as e:
            print(f"❌ Groq client init failed: {e}")

    def is_available(self) -> bool:
        return PYAUTOGUI_AVAILABLE and PIL_AVAILABLE

    def is_vision_available(self) -> bool:
        return self.client is not None

    # ── Screenshot ───────────────────────────────────────────────────────────
    def capture_screenshot(self, region=None) -> Optional[str]:
        """
        Take a screenshot and save it.

        Args:
            region: (left, top, width, height) or None for full screen

        Returns:
            Path to saved screenshot or None on failure
        """
        if not PYAUTOGUI_AVAILABLE or not PIL_AVAILABLE:
            return None
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath = os.path.join(self.screenshot_dir, f"screen_{timestamp}.png")

            screenshot = pyautogui.screenshot(region=region)
            screenshot.save(filepath, "PNG")
            print(f"📸 Screenshot saved: {filepath}")
            return filepath
        except Exception as e:
            print(f"❌ Screenshot failed: {e}")
            return None

    def _image_to_base64(self, image_path: str) -> Optional[str]:
        """Convert image file to base64 string for API."""
        try:
            with open(image_path, "rb") as f:
                return base64.b64encode(f.read()).decode("utf-8")
        except Exception as e:
            print(f"❌ Image to base64 failed: {e}")
            return None

    def _enhance_image_for_ocr(self, image_path: str) -> Optional[str]:
        """Enhance screenshot for better text readability by the AI."""
        try:
            img = Image.open(image_path)
            # Increase contrast slightly for better text visibility
            enhancer = ImageEnhance.Contrast(img)
            img = enhancer.enhance(1.3)
            enhanced_path = image_path.replace(".png", "_enhanced.png")
            img.save(enhanced_path, "PNG")
            return enhanced_path
        except Exception as e:
            print(f"⚠️ Image enhancement failed (using original): {e}")
            return image_path

    # ── Vision Analysis ───────────────────────────────────────────────────────
    def _analyze_image_with_ai(self, image_path: str, prompt: str) -> Optional[str]:
        """
        Send screenshot to Groq vision model for analysis.

        Args:
            image_path: Path to screenshot
            prompt: Question/instruction for the AI

        Returns:
            AI response text or None
        """
        if not self.is_vision_available():
            return self._ocr_fallback(image_path)

        # Enhance for better results
        enhanced_path = self._enhance_image_for_ocr(image_path)
        b64_image = self._image_to_base64(enhanced_path or image_path)
        if not b64_image:
            return None

        try:
            print(f"🔍 Sending screenshot to vision AI...")
            response = self.client.chat.completions.create(
                model=self.VISION_MODEL,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{b64_image}"
                                }
                            },
                            {
                                "type": "text",
                                "text": prompt
                            }
                        ]
                    }
                ],
                max_tokens=1024,
                temperature=0.3
            )
            result = response.choices[0].message.content.strip()
            print(f"✅ Vision AI response received ({len(result)} chars)")
            return result

        except Exception as e:
            print(f"❌ Vision model error: {e}")
            # Try fallback model
            try:
                print(f"🔄 Trying fallback model: {self.FALLBACK_MODEL}")
                response = self.client.chat.completions.create(
                    model=self.FALLBACK_MODEL,
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:image/png;base64,{b64_image}"
                                    }
                                },
                                {
                                    "type": "text",
                                    "text": prompt
                                }
                            ]
                        }
                    ],
                    max_tokens=1024,
                    temperature=0.3
                )
                return response.choices[0].message.content.strip()
            except Exception as e2:
                print(f"❌ Fallback model also failed: {e2}")
                return self._ocr_fallback(image_path)

    def _ocr_fallback(self, image_path: str) -> Optional[str]:
        """Use pytesseract OCR if vision AI is unavailable."""
        if not TESSERACT_AVAILABLE:
            return "Vision AI and OCR are both unavailable. Please check your API key and install pytesseract."
        try:
            img = Image.open(image_path)
            text = pytesseract.image_to_string(img)
            return f"Screen text (OCR): {text.strip()}" if text.strip() else "No readable text found on screen."
        except Exception as e:
            return f"Could not read screen: {e}"

    # ── Public Screen Commands ────────────────────────────────────────────────
    def describe_screen(self) -> str:
        """
        Describe everything visible on the current screen.

        Returns:
            Natural language description of the screen
        """
        if not self.is_available():
            return "Screen capture is not available. Please install pyautogui and Pillow."

        print("👁️ Capturing screen for description...")
        screenshot_path = self.capture_screenshot()
        if not screenshot_path:
            return "I couldn't capture the screen. Please try again."

        prompt = (
            "You are SEEU, an AI assistant looking at a computer screen. "
            "Describe clearly and concisely what you see on this screen. "
            "Include: what application is open, what content is visible, "
            "any text, buttons, or important UI elements. "
            "Speak directly to the user as if describing it to them verbally. "
            "Keep it natural and conversational, under 150 words."
        )

        result = self._analyze_image_with_ai(screenshot_path, prompt)
        return result or "I could see the screen but couldn't process the image. Please try again."

    def read_screen_text(self) -> str:
        """
        Read and return all visible text from the screen.

        Returns:
            Text visible on screen
        """
        if not self.is_available():
            return "Screen capture is not available."

        print("📖 Reading text from screen...")
        screenshot_path = self.capture_screenshot()
        if not screenshot_path:
            return "I couldn't capture the screen."

        prompt = (
            "Read and transcribe ALL visible text from this screen exactly as written. "
            "Include: window titles, menu items, body text, error messages, labels, buttons. "
            "Format it clearly. If there are error messages, highlight them."
        )

        result = self._analyze_image_with_ai(screenshot_path, prompt)
        return result or "I couldn't read the text from the screen."

    def detect_and_explain_error(self) -> str:
        """
        Detect any error messages or problems on screen and explain them.

        Returns:
            Explanation of the error and suggested fix
        """
        if not self.is_available():
            return "Screen capture is not available."

        print("🔍 Analyzing screen for errors...")
        screenshot_path = self.capture_screenshot()
        if not screenshot_path:
            return "I couldn't capture the screen."

        prompt = (
            "Look at this screen carefully and identify any errors, warnings, or problems. "
            "If you find an error or warning: "
            "1. Describe what the error is in simple language "
            "2. Explain what caused it "
            "3. Suggest 2-3 specific steps to fix it "
            "If there is no error, simply say the screen looks normal and describe what you see. "
            "Be concise and speak directly to the user."
        )

        result = self._analyze_image_with_ai(screenshot_path, prompt)
        return result or "I analyzed the screen but couldn't get a clear response."

    def solve_screen_problem(self) -> str:
        """
        Detect the problem on screen and automatically attempt to solve it.

        Returns:
            Description of what was found and what action was taken
        """
        if not self.is_available():
            return "Screen capture is not available."

        print("🛠️ Analyzing screen problem to solve...")
        screenshot_path = self.capture_screenshot()
        if not screenshot_path:
            return "I couldn't capture the screen."

        prompt = (
            "Analyze this screen for any error, dialog, or problem that needs attention. "
            "Respond in this EXACT format:\n"
            "PROBLEM: [describe the problem in one sentence]\n"
            "ACTION: [one of: CLOSE_DIALOG, PRESS_OK, PRESS_CANCEL, PRESS_ENTER, "
            "PRESS_ESCAPE, CLOSE_TAB, NONE]\n"
            "EXPLANATION: [brief explanation for the user]\n"
            "If no problem exists, use ACTION: NONE"
        )

        result = self._analyze_image_with_ai(screenshot_path, prompt)
        if not result:
            return "I couldn't analyze the screen problem."

        # Parse and act on the result
        return self._execute_problem_solution(result)

    def _execute_problem_solution(self, ai_response: str) -> str:
        """Parse AI response and execute appropriate action."""
        action_match = re.search(r'ACTION:\s*(\w+)', ai_response, re.IGNORECASE)
        explanation_match = re.search(r'EXPLANATION:\s*(.+)', ai_response, re.IGNORECASE | re.DOTALL)
        problem_match = re.search(r'PROBLEM:\s*(.+?)(?:\n|ACTION:)', ai_response, re.IGNORECASE | re.DOTALL)

        action = action_match.group(1).upper() if action_match else "NONE"
        explanation = explanation_match.group(1).strip() if explanation_match else ai_response
        problem = problem_match.group(1).strip() if problem_match else "Unknown issue"

        if not PYAUTOGUI_AVAILABLE:
            return f"Found: {problem}. Suggested fix: {explanation} (keyboard control unavailable)."

        time.sleep(0.5)  # Small delay before acting

        action_map = {
            "CLOSE_DIALOG": lambda: pyautogui.press('escape'),
            "PRESS_OK":      lambda: pyautogui.press('enter'),
            "PRESS_CANCEL":  lambda: pyautogui.press('escape'),
            "PRESS_ENTER":   lambda: pyautogui.press('enter'),
            "PRESS_ESCAPE":  lambda: pyautogui.press('escape'),
            "CLOSE_TAB":     lambda: pyautogui.hotkey('ctrl', 'w'),
            "NONE":          lambda: None,
        }

        if action in action_map and action != "NONE":
            try:
                action_map[action]()
                print(f"✅ Executed action: {action}")
                return f"I found: {problem}. I pressed the appropriate key to resolve it. {explanation}"
            except Exception as e:
                return f"I found: {problem}, but couldn't execute the fix: {e}. {explanation}"
        else:
            return f"{explanation}"

    def answer_screen_question(self, question: str) -> str:
        """
        Answer a specific question about what's on the screen.

        Args:
            question: The user's question about the screen

        Returns:
            Answer based on screen content
        """
        if not self.is_available():
            return "Screen capture is not available."

        print(f"❓ Answering screen question: {question}")
        screenshot_path = self.capture_screenshot()
        if not screenshot_path:
            return "I couldn't capture the screen."

        prompt = (
            f"Look at this screenshot and answer this question: '{question}'\n"
            "Give a clear, direct, concise answer based only on what you can see on the screen. "
            "If the answer isn't visible on screen, say so clearly."
        )

        result = self._analyze_image_with_ai(screenshot_path, prompt)
        return result or "I couldn't find the answer on the screen."

    def take_and_save_screenshot(self) -> str:
        """
        Take a screenshot and tell the user where it was saved.

        Returns:
            Confirmation message with file path
        """
        screenshot_path = self.capture_screenshot()
        if screenshot_path:
            filename = os.path.basename(screenshot_path)
            return f"Screenshot saved as {filename} in the Screenshots folder."
        return "Failed to take screenshot."

    # ── Typing Control ────────────────────────────────────────────────────────
    def type_text(self, text: str, delay: float = 0.05) -> str:
        """
        Type the given text using keyboard simulation.

        Args:
            text: Text to type
            delay: Delay between keystrokes in seconds

        Returns:
            Confirmation message
        """
        if not PYAUTOGUI_AVAILABLE:
            return "Keyboard control is not available. Please install pyautogui."

        try:
            print(f"⌨️ Typing: {text[:50]}...")
            time.sleep(0.5)  # Give user time to focus the target window
            pyautogui.write(text, interval=delay)
            print(f"✅ Typed: {text[:50]}")
            return f"Done, I typed: {text}"
        except Exception as e:
            print(f"❌ Typing failed: {e}")
            return f"I couldn't type the text: {e}"

    def type_and_enter(self, text: str) -> str:
        """Type text and then press Enter."""
        result = self.type_text(text)
        if "Done" in result:
            time.sleep(0.2)
            pyautogui.press('enter')
            return f"Typed and submitted: {text}"
        return result

    # ── Mouse Control ────────────────────────────────────────────────────────
    def click_at(self, x: int, y: int, button: str = 'left') -> str:
        """Click at specific coordinates."""
        if not PYAUTOGUI_AVAILABLE:
            return "Mouse control unavailable."
        try:
            pyautogui.click(x, y, button=button)
            return f"Clicked at position ({x}, {y})."
        except Exception as e:
            return f"Click failed: {e}"

    def scroll(self, direction: str = 'down', amount: int = 3) -> str:
        """Scroll the screen up or down."""
        if not PYAUTOGUI_AVAILABLE:
            return "Mouse control unavailable."
        try:
            clicks = amount if direction == 'up' else -amount
            pyautogui.scroll(clicks)
            return f"Scrolled {direction}."
        except Exception as e:
            return f"Scroll failed: {e}"

    def press_key(self, key: str) -> str:
        """Press a specific key."""
        if not PYAUTOGUI_AVAILABLE:
            return "Keyboard control unavailable."
        try:
            pyautogui.press(key)
            return f"Pressed {key} key."
        except Exception as e:
            return f"Key press failed: {e}"

    def hotkey(self, *keys) -> str:
        """Press a key combination (e.g. ctrl+c)."""
        if not PYAUTOGUI_AVAILABLE:
            return "Keyboard control unavailable."
        try:
            pyautogui.hotkey(*keys)
            return f"Pressed {'+'.join(keys)}."
        except Exception as e:
            return f"Hotkey failed: {e}"


# ─────────────────────────────────────────────────────────────────────────────
#  COMMAND PROCESSOR – used by Brain.py
# ─────────────────────────────────────────────────────────────────────────────
class ScreenCommandProcessor:
    """
    Detects and handles screen-related voice commands.
    Integrates with Brain.py's process_message flow.
    """

    def __init__(self):
        self.controller = ScreenController()
        print("✅ ScreenCommandProcessor ready")

    def is_screen_command(self, user_input: str) -> bool:
        """
        Check if user input is a screen-related command.

        Args:
            user_input: Raw voice/text input from user

        Returns:
            True if this is a screen command
        """
        input_lower = user_input.lower().strip()
        return any(keyword in input_lower for keyword in SCREEN_KEYWORDS)

    def process_command(self, user_input: str) -> Optional[str]:
        """
        Process a screen command and return the response.

        Args:
            user_input: User's voice command

        Returns:
            Response string, or None if not a screen command
        """
        if not self.is_screen_command(user_input):
            return None

        input_lower = user_input.lower().strip()
        print(f"🖥️ Screen command detected: {user_input}")

        # ── Typing commands ──────────────────────────────────────────────────
        # "type Hello World" / "write Hello World" / "type and enter ..."
        type_match = re.search(
            r'(?:type|write|enter text)[:\s]+["\']?(.+?)["\']?\s*$',
            user_input, re.IGNORECASE
        )
        if type_match:
            text_to_type = type_match.group(1).strip()
            if 'enter' in input_lower and 'type' in input_lower:
                return self.controller.type_and_enter(text_to_type)
            return self.controller.type_text(text_to_type)

        # ── Screenshot ───────────────────────────────────────────────────────
        if any(k in input_lower for k in ['take a screenshot', 'capture the screen', 'screenshot']):
            return self.controller.take_and_save_screenshot()

        # ── Error detection & fixing ─────────────────────────────────────────
        if any(k in input_lower for k in [
            'solve the problem', 'fix the problem', 'fix the error',
            'fix it', 'solve it', 'help me with the error'
        ]):
            return self.controller.solve_screen_problem()

        if any(k in input_lower for k in [
            'what does the error say', 'read the error', 'what error',
            'what is the error', 'error on screen', 'what is wrong', 'whats wrong'
        ]):
            return self.controller.detect_and_explain_error()

        # ── Read text ────────────────────────────────────────────────────────
        if any(k in input_lower for k in [
            'read the screen', 'read what is written', 'what does it say',
            'what is written', 'what text', 'read this'
        ]):
            return self.controller.read_screen_text()

        # ── General screen description ───────────────────────────────────────
        if any(k in input_lower for k in [
            'what is on the screen', "what's on the screen", 'whats on screen',
            'what do you see', 'look at the screen', 'see the screen',
            'describe the screen', 'describe what you see',
            'analyze the screen', 'analyse the screen',
            'check the screen', 'tell me about the screen'
        ]):
            return self.controller.describe_screen()

        # ── Specific question about screen ───────────────────────────────────
        # Catch-all: user is asking something about the screen
        question_indicators = [
            'what is', "what's", 'where is', 'how many', 'can you see',
            'is there', 'do you see', 'show me', 'look at this'
        ]
        if any(k in input_lower for k in question_indicators):
            return self.controller.answer_screen_question(user_input)

        # Default: describe the screen
        return self.controller.describe_screen()


# ─────────────────────────────────────────────────────────────────────────────
#  GLOBAL INSTANCE (singleton pattern, like other modules)
# ─────────────────────────────────────────────────────────────────────────────
_screen_processor = None

def get_screen_processor() -> ScreenCommandProcessor:
    """Get or create the global ScreenCommandProcessor instance."""
    global _screen_processor
    if _screen_processor is None:
        _screen_processor = ScreenCommandProcessor()
    return _screen_processor


def process_screen_command(user_input: str) -> Optional[str]:
    """
    Quick function: process a screen command.
    Returns response string, or None if not a screen command.
    """
    processor = get_screen_processor()
    return processor.process_command(user_input)


def is_screen_command(user_input: str) -> bool:
    """Quick function: check if input is a screen command."""
    processor = get_screen_processor()
    return processor.is_screen_command(user_input)


# ─────────────────────────────────────────────────────────────────────────────
#  STANDALONE TEST
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("\n🖥️  SEEU ScreenControl Module – Test Mode")
    print("=" * 60)
    print("Commands you can test:")
    print("  describe the screen")
    print("  what's on the screen")
    print("  what does the error say")
    print("  solve the problem")
    print("  read the screen")
    print("  take a screenshot")
    print("  type Hello World")
    print("  exit")
    print("=" * 60)

    processor = ScreenCommandProcessor()

    while True:
        user_cmd = input("\n🎤 Enter command: ").strip()
        if user_cmd.lower() in ['exit', 'quit']:
            break

        if not user_cmd:
            continue

        response = processor.process_command(user_cmd)
        if response:
            print(f"\n🤖 SEEU: {response}")
        else:
            print("⚠️ Not recognised as a screen command.")

    print("\n👋 ScreenControl test complete.")