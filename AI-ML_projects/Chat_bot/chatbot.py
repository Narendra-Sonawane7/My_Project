# =============================================================================
# chatbot.py — The core ChatBot class (orchestrates everything)
# =============================================================================
# Why a ChatBot class?
#   → Combines GroqClient (API) + ConversationMemory (history) in one place
#   → The main.py only needs to call chatbot.send("hello") — simple interface
#   → "Single Responsibility" concept: this class knows HOW to chat.
#     It doesn't know about API HTTP details (groq_client.py handles that)
#     or how to display output (utils.py handles that)
# =============================================================================

from groq_client import GroqClient, GroqAPIError
from memory import ConversationMemory
from config import DEFAULT_SYSTEM_PROMPT


class ChatBot:
    """
    The main chatbot class.

    Combines the Groq API client with conversation memory to create
    a stateful chatbot that remembers the full conversation.

    Architecture:
        ChatBot
          ├── GroqClient   → handles HTTP calls to Groq API
          └── ConversationMemory → stores and manages message history

    Usage:
        bot = ChatBot(api_key="gsk_...", model="llama-3.3-70b-versatile")
        reply = bot.send("Hello, who are you?")
        reply = bot.send("What did I just ask you?")  # Bot remembers!
    """

    def __init__(
        self, api_key: str = None, model: str = None, system_prompt: str = None
    ):
        """
        Set up the chatbot with an API client and memory.

        Args:
            api_key:       Groq API key. Falls back to .env file.
            model:         Model name. Falls back to DEFAULT_MODEL in config.
            system_prompt: Persona/instructions for the bot.
        """
        # Create the API client (handles all HTTP/network logic)
        self.client = GroqClient(api_key=api_key, model=model)

        # Create the memory (handles all conversation history logic)
        self.memory = ConversationMemory(
            system_prompt=system_prompt or DEFAULT_SYSTEM_PROMPT
        )

        print(f"  Bot ready | {self.client.get_model_info()}")

    def send(self, user_message: str) -> str:
        """
        Send a message and get a reply.

        This is the MAIN method. Here's exactly what happens:

          Step 1: Add the user's message to memory
          Step 2: Build the full messages list (system + history)
          Step 3: Send it to Groq API
          Step 4: Add the reply to memory
          Step 5: Return the reply

        Because we send the FULL history every time (step 2),
        the bot can refer to anything said earlier — that's the "memory".

        Args:
            user_message: What the user typed.

        Returns:
            The assistant's reply as a string.

        Raises:
            GroqAPIError: If the API call fails.
        """

        # Step 1: Store what the user said
        self.memory.add_user_message(user_message)

        # Step 2: Build complete message list for the API
        # This includes: [system_prompt, msg1, reply1, msg2, reply2, ..., user_message]
        messages = self.memory.get_messages_for_api()

        # Step 3: Call the Groq API
        # This can raise GroqAPIError — we let it bubble up to main.py
        assistant_reply = self.client.chat(messages)

        # Step 4: Store the assistant's reply so future calls remember it
        self.memory.add_assistant_message(assistant_reply)

        # Step 5: Return the reply to be displayed
        return assistant_reply

    def clear_memory(self) -> None:
        """
        Clear the conversation history.
        The bot will forget everything but keep its system prompt/persona.
        """
        self.memory.clear()

    def change_model(self, model: str) -> None:
        """
        Switch to a different Groq model mid-conversation.
        Memory is preserved — only the model changes.
        """
        self.client.model = model
        print(f"  Switched to: {model}")

    def change_system_prompt(self, new_prompt: str) -> None:
        """
        Change the bot's persona/system prompt.
        Takes effect from the next message onwards.
        """
        self.memory.system_prompt = new_prompt

    # ── Read-only stats ───────────────────────────────────────────────────────

    @property
    def stats(self) -> dict:
        """Return current stats about the conversation."""
        return {
            "model": self.client.model,
            "turns": self.memory.turn_count,
            "messages_in_memory": self.memory.message_count,
            "approx_tokens": self.memory.approximate_tokens,
        }
