# =============================================================================
# memory.py — Manages the conversation history (the "memory")
# =============================================================================
# Why a separate memory file?
#   → Memory management is its own concern — how many messages to keep,
#     how to add/clear/summarise history. Don't mix this with API logic.
#   → In real products, memory can be extended to save to a database,
#     Redis, or a vector store. Having it isolated makes that easy.
#   → Great talking point in interviews: "I designed the memory module
#     to be swappable — I could replace the in-memory list with Redis
#     without touching anything else."
# =============================================================================

from config import DEFAULT_SYSTEM_PROMPT, MAX_HISTORY


class ConversationMemory:
    """
    Stores and manages the full conversation history.

    How LLM memory works:
    ┌─────────────────────────────────────────────────────────────┐
    │  LLMs are STATELESS — they remember nothing between calls.  │
    │  "Memory" = we send the full history with every API call.   │
    │                                                             │
    │  API Call 1:  [system, user_1]                              │
    │  API Call 2:  [system, user_1, assistant_1, user_2]         │
    │  API Call 3:  [system, user_1, assistant_1, user_2, ...]    │
    └─────────────────────────────────────────────────────────────┘

    This class manages that growing list of messages.
    """

    def __init__(self, system_prompt: str = None):
        """
        Initialise memory with a system prompt.

        Args:
            system_prompt: Defines the bot's persona/behaviour.
                           Sent as the first message in every API call.
        """
        self.system_prompt = system_prompt or DEFAULT_SYSTEM_PROMPT
        self._history: list[dict] = []  # Stores user + assistant messages
        # (NOT the system prompt — that's separate)

    def add_user_message(self, content: str) -> None:
        """Add a user message to the history."""
        self._history.append({"role": "user", "content": content})
        self._trim_if_needed()

    def add_assistant_message(self, content: str) -> None:
        """Add the assistant's reply to the history."""
        self._history.append({"role": "assistant", "content": content})

    def get_messages_for_api(self) -> list[dict]:
        """
        Build the complete messages list to send to the Groq API.

        Returns:
            List starting with the system prompt, followed by all
            conversation turns in order. This is the full "memory"
            passed to the API.

        Example output:
            [
                {"role": "system",    "content": "You are a helpful assistant..."},
                {"role": "user",      "content": "What is Python?"},
                {"role": "assistant", "content": "Python is a programming language..."},
                {"role": "user",      "content": "What is it used for?"},
            ]
        """
        return [{"role": "system", "content": self.system_prompt}] + self._history

    def clear(self) -> None:
        """Clear all conversation history (but keep the system prompt)."""
        self._history = []

    def _trim_if_needed(self) -> None:
        """
        Keep memory within MAX_HISTORY limit.

        Why? Each message uses tokens. If history grows too large:
          → API calls become slow and expensive
          → You can exceed the model's context window limit

        Strategy: Drop the OLDEST messages first (sliding window).
        Always keep pairs (user + assistant) together.
        """
        if len(self._history) > MAX_HISTORY:
            # Remove the 2 oldest messages (1 user + 1 assistant turn)
            self._history = self._history[2:]

    # ── Properties for displaying stats ──────────────────────────────────────

    @property
    def message_count(self) -> int:
        """Total number of messages in history (both user and assistant)."""
        return len(self._history)

    @property
    def turn_count(self) -> int:
        """Number of complete conversation turns (user + assistant pairs)."""
        return len(self._history) // 2

    @property
    def approximate_tokens(self) -> int:
        """
        Rough token estimate for all messages.
        Rule of thumb: 1 token ≈ 4 characters in English.
        """
        total_chars = sum(len(m["content"]) for m in self._history)
        total_chars += len(self.system_prompt)
        return total_chars // 4

    def is_empty(self) -> bool:
        """Return True if no messages have been added yet."""
        return len(self._history) == 0
