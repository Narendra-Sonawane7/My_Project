# =============================================================================
# utils.py — Display helpers and UI formatting
# =============================================================================
# Why a separate utils file?
#   → All print/colour/formatting logic in ONE place
#   → If you want to change the UI (e.g. add colour or build a web UI),
#     you only change this file — nothing in chatbot.py or main.py changes
#   → Keeps main.py clean: it calls display functions, not raw print()
# =============================================================================

from config import APP_NAME, APP_VERSION, AVAILABLE_MODELS


# ANSI colour codes for terminal colours
# Why use these? Makes the output easier to read at a glance.
class Colors:
    RESET   = "\033[0m"
    BOLD    = "\033[1m"
    DIM     = "\033[2m"

    CYAN    = "\033[96m"
    GREEN   = "\033[92m"
    YELLOW  = "\033[93m"
    RED     = "\033[91m"
    BLUE    = "\033[94m"
    MAGENTA = "\033[95m"
    WHITE   = "\033[97m"
    GRAY    = "\033[90m"

C = Colors   # Short alias for convenience


def print_banner() -> None:
    """Print the app welcome banner when the program starts."""
    print(f"\n{C.CYAN}{C.BOLD}")
    print("  ╔══════════════════════════════════════════╗")
    print(f"  ║   ⚡  {APP_NAME} v{APP_VERSION}                   ║")
    print("  ║      Powered by Groq's LPU Inference     ║")
    print("  ╚══════════════════════════════════════════╝")
    print(f"{C.RESET}")
    print(f"  {C.GRAY}Groq's LPU chips run LLMs 10x faster than GPU{C.RESET}")
    print(f"  {C.GRAY}Get your free API key: console.groq.com{C.RESET}\n")


def print_model_menu() -> None:
    """Print the model selection menu."""
    print(f"\n{C.BOLD}  Choose a model:{C.RESET}")
    for key, (model_id, description) in AVAILABLE_MODELS.items():
        print(f"  {C.CYAN}{key}{C.RESET}. {description}")
    print()


def print_separator() -> None:
    """Print a visual divider line."""
    print(f"  {C.GRAY}{'─' * 50}{C.RESET}")


def print_help() -> None:
    """Print available commands."""
    print(f"\n  {C.BOLD}Available commands:{C.RESET}")
    cmds = [
        ("clear",       "Forget the conversation, start fresh"),
        ("stats",       "Show memory and token usage"),
        ("model",       "Switch to a different LLM model"),
        ("system",      "Change the bot's persona/system prompt"),
        ("help",        "Show this help message"),
        ("exit / quit", "Exit the program"),
    ]
    for cmd, desc in cmds:
        print(f"  {C.YELLOW}/{cmd:<14}{C.RESET} {C.GRAY}{desc}{C.RESET}")
    print()


def print_user_label() -> None:
    """Print the 'You:' label before user input."""
    print(f"\n  {C.GREEN}{C.BOLD}You{C.RESET}  {C.GRAY}›{C.RESET} ", end="")


def print_bot_response(reply: str) -> None:
    """
    Print the bot's reply with proper formatting.
    Adds line-by-line indentation for readability.
    """
    print(f"\n  {C.CYAN}{C.BOLD}Bot{C.RESET}  {C.GRAY}›{C.RESET}")
    print()
    # Indent every line of the response for visual clarity
    for line in reply.splitlines():
        print(f"    {line}")
    print()


def print_stats(stats: dict) -> None:
    """Print current conversation statistics."""
    print(f"\n  {C.BOLD}Conversation stats:{C.RESET}")
    print(f"  {C.GRAY}Model   :{C.RESET} {C.CYAN}{stats['model']}{C.RESET}")
    print(f"  {C.GRAY}Turns   :{C.RESET} {stats['turns']} (user + assistant pairs)")
    print(f"  {C.GRAY}Messages:{C.RESET} {stats['messages_in_memory']} in memory")
    print(f"  {C.GRAY}Tokens  :{C.RESET} ~{stats['approx_tokens']} estimated\n")


def print_error(message: str) -> None:
    """Print an error message in red."""
    print(f"\n  {C.RED}✗  Error: {message}{C.RESET}\n")


def print_success(message: str) -> None:
    """Print a success message in green."""
    print(f"\n  {C.GREEN}✓  {message}{C.RESET}\n")


def print_info(message: str) -> None:
    """Print an informational message in gray."""
    print(f"  {C.GRAY}ℹ  {message}{C.RESET}")


def print_thinking() -> None:
    """Print a 'thinking...' indicator."""
    print(f"\n  {C.GRAY}  thinking...{C.RESET}", end="\r")


def get_api_key_input() -> str:
    """Prompt the user to enter their Groq API key."""
    print(f"  {C.YELLOW}No API key found in .env file.{C.RESET}")
    print(f"  {C.GRAY}Get your free key at: https://console.groq.com{C.RESET}")
    print(f"  {C.GRAY}Or create a .env file with: GROQ_API_KEY=gsk_...{C.RESET}\n")
    return input(f"  {C.CYAN}Paste your Groq API key:{C.RESET} ").strip()