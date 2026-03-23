# =============================================================================
# config.py — All configuration and settings in one place
# =============================================================================
# Why a separate config file?
#   → Easy to change settings without touching core logic
#   → Clean separation: settings vs behaviour
#   → Interviewers love this — shows you think about maintainability
# =============================================================================

import os
from dotenv import load_dotenv

# Load variables from .env file into the environment
load_dotenv()


# ── API SETTINGS ──────────────────────────────────────────────────────────────

GROQ_API_KEY = os.getenv("GROQ_API_KEY")          # Read from .env (never hardcode!)
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

# Available Groq models (all free-tier)
AVAILABLE_MODELS = {
    "1": ("llama-3.3-70b-versatile",  "Llama 3.3 70B  — best quality, slightly slower"),
    "2": ("llama-3.1-8b-instant",     "Llama 3.1 8B   — fastest, good for testing"),
    "3": ("gemma2-9b-it",             "Gemma 2 9B     — Google's model, balanced"),
    "4": ("mixtral-8x7b-32768",       "Mixtral 8x7B   — large context window (32k)"),
}

DEFAULT_MODEL = "llama-3.3-70b-versatile"


# ── MODEL PARAMETERS ──────────────────────────────────────────────────────────

MAX_TOKENS     = 1024   # Max tokens in the response
TEMPERATURE    = 0.7    # 0.0 = deterministic, 1.0 = very creative
                        # 0.7 is a good balance for a chatbot

# ── SYSTEM PROMPT ─────────────────────────────────────────────────────────────
# The system prompt defines the bot's PERSONA and behaviour.
# It is always sent as the FIRST message in every API call.

DEFAULT_SYSTEM_PROMPT = """You are a helpful, concise, and friendly AI assistant.
Answer clearly and directly. If you don't know something, say so honestly."""


# ── UI SETTINGS ───────────────────────────────────────────────────────────────

APP_NAME      = "Groq Chatbot"
APP_VERSION   = "1.0.0"
MAX_HISTORY   = 20      # Keep last 20 messages in memory (10 turns)
                        # Prevents the context window from getting too large