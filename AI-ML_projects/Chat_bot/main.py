# =============================================================================
# main.py — Entry point. Run this file to start the chatbot.
# =============================================================================
# Role of main.py:
#   → Handles user INPUT (reading what they type)
#   → Calls chatbot.send() to get a response
#   → Handles special /commands
#   → Uses utils.py for all display/output
#
# What main.py does NOT do:
#   → It knows nothing about HTTP or APIs (that's groq_client.py)
#   → It knows nothing about memory management (that's memory.py)
#   → It knows nothing about formatting (that's utils.py)
#
# This is the "Controller" in a simple MVC-style structure.
# =============================================================================

import sys
from chatbot import ChatBot
from groq_client import GroqAPIError
from config import GROQ_API_KEY, AVAILABLE_MODELS, DEFAULT_MODEL
import utils


def select_model() -> str:
    """
    Prompt the user to pick a model from the list.
    Returns the model ID string.
    """
    utils.print_model_menu()
    choice = input("  Enter choice (1-4, or press Enter for default): ").strip()

    if choice in AVAILABLE_MODELS:
        model_id, description = AVAILABLE_MODELS[choice]
        utils.print_success(f"Selected: {description}")
        return model_id

    utils.print_info("Using default model: Llama 3.3 70B")
    return DEFAULT_MODEL


def handle_command(user_input: str, bot: ChatBot) -> bool:
    """
    Handle special slash commands (/clear, /stats, /model, /system, /help, /exit).

    Args:
        user_input: What the user typed.
        bot:        The ChatBot instance to act on.

    Returns:
        True  → command was handled, skip the API call
        False → not a command, send to the API
    """
    cmd = user_input.strip().lower()

    if cmd in ("/exit", "/quit", "exit", "quit"):
        print(f"\n  Goodbye! 👋\n")
        sys.exit(0)

    elif cmd == "/clear":
        bot.clear_memory()
        utils.print_success("Memory cleared. Starting fresh conversation.")
        return True

    elif cmd == "/stats":
        utils.print_stats(bot.stats)
        return True

    elif cmd == "/help":
        utils.print_help()
        return True

    elif cmd == "/model":
        # Switch model mid-conversation
        model_id = select_model()
        bot.change_model(model_id)
        return True

    elif cmd == "/system":
        new_prompt = input(
            f"\n  Enter new system prompt\n  (current: '{bot.memory.system_prompt[:50]}...')\n  > "
        ).strip()
        if new_prompt:
            bot.change_system_prompt(new_prompt)
            utils.print_success("System prompt updated!")
        return True

    return False  # Not a command — let main loop handle it


def main():
    """
    Main function — sets up the bot and runs the conversation loop.

    Flow:
      1. Print banner
      2. Get API key (from .env or user input)
      3. Let user pick a model
      4. Create the ChatBot
      5. Loop: read input → handle command OR send to API → print reply
    """

    utils.print_banner()

    # ── Step 1: Get API key ──────────────────────────────────────────────────
    api_key = GROQ_API_KEY

    if not api_key:
        api_key = utils.get_api_key_input()
        if not api_key:
            utils.print_error("No API key provided. Exiting.")
            sys.exit(1)

    # ── Step 2: Pick a model ─────────────────────────────────────────────────
    model = select_model()

    utils.print_separator()
    utils.print_info("Type your message and press Enter to chat.")
    utils.print_info("Type /help to see all commands.")
    utils.print_separator()

    # ── Step 3: Initialise the chatbot ───────────────────────────────────────
    try:
        bot = ChatBot(api_key=api_key, model=model)
    except GroqAPIError as e:
        utils.print_error(str(e))
        sys.exit(1)

    # ── Step 4: Main conversation loop ───────────────────────────────────────
    while True:
        try:
            # Show the input prompt and get user's message
            utils.print_user_label()
            user_input = input().strip()

            # Skip empty input
            if not user_input:
                continue

            # Check if it's a /command — if yes, handle and loop back
            if handle_command(user_input, bot):
                continue

            # It's a regular message — send to Groq API
            utils.print_thinking()

            reply = bot.send(user_input)

            utils.print_bot_response(reply)

        except GroqAPIError as e:
            # API-level errors (bad key, rate limit, etc.)
            utils.print_error(str(e))

        except KeyboardInterrupt:
            # User pressed Ctrl+C
            print(f"\n\n  Interrupted. Type /exit to quit gracefully.\n")

        except EOFError:
            # Piped input ended
            break


# Standard Python entry point guard
# This means: only run main() if THIS file is run directly
# (not if it's imported by another file)
if __name__ == "__main__":
    main()
