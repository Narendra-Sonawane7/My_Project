# =============================================================================
# groq_client.py — Handles all communication with the Groq API
# =============================================================================
# Why a separate API client file?
#   → If Groq changes their API, you only update THIS file
#   → Easy to swap Groq for OpenAI or any other LLM — just swap this file
#   → Keeps HTTP/API logic OUT of your business logic (chatbot.py)
#   → This pattern is called "Separation of Concerns"
# =============================================================================

import requests
import json
from config import GROQ_API_KEY, GROQ_API_URL, MAX_TOKENS, TEMPERATURE


class GroqAPIError(Exception):
    """Custom exception for Groq API errors.

    Why a custom exception?
    → You can catch GroqAPIError specifically in your code
    → Gives users clear, helpful error messages
    → Much better than a generic requests.HTTPError
    """

    pass


class GroqClient:
    """
    A wrapper around the Groq REST API.

    Groq's API is OpenAI-compatible — it uses the exact same
    request/response format as OpenAI's chat completions endpoint.
    This means switching from OpenAI to Groq (or back) is trivial.

    Example usage:
        client = GroqClient(api_key="gsk_xxx", model="llama-3.3-70b-versatile")
        reply = client.chat(messages=[{"role": "user", "content": "Hello!"}])
    """

    def __init__(self, api_key: str = None, model: str = None):
        """
        Initialise the Groq client.

        Args:
            api_key: Your Groq API key (starts with 'gsk_').
                     Falls back to config.py / .env if not provided.
            model:   The model to use. Falls back to DEFAULT_MODEL in config.py.
        """
        from config import DEFAULT_MODEL

        self.api_key = api_key or GROQ_API_KEY
        self.model = model or DEFAULT_MODEL

        if not self.api_key:
            raise GroqAPIError(
                "No API key found!\n"
                "  Option 1: Set GROQ_API_KEY in your .env file\n"
                "  Option 2: Pass it as GroqClient(api_key='gsk_...')\n"
                "  Get your free key at: https://console.groq.com"
            )

        # Build HTTP headers — sent with every request
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",  # Standard Bearer token auth
        }

    def chat(self, messages: list[dict]) -> str:
        """
        Send a conversation to Groq and get the assistant's reply.

        This is the CORE method. It:
          1. Builds the request payload
          2. POSTs to the Groq API
          3. Handles errors clearly
          4. Returns just the text reply

        Args:
            messages: List of message dicts in OpenAI format:
                      [{"role": "system",    "content": "You are ..."},
                       {"role": "user",      "content": "Hello"},
                       {"role": "assistant", "content": "Hi there!"},
                       {"role": "user",      "content": "How are you?"}]

                      The FULL history is passed here — this is what gives
                      the chatbot its "memory".

        Returns:
            The assistant's reply as a plain string.

        Raises:
            GroqAPIError: If the API call fails for any reason.
        """

        # ── Build request body ──
        payload = {
            "model": self.model,
            "messages": messages,
            "max_tokens": MAX_TOKENS,
            "temperature": TEMPERATURE,
        }

        # ── Make the HTTP POST request ──
        try:
            response = requests.post(
                GROQ_API_URL,
                headers=self.headers,
                json=payload,  # Automatically serialises dict to JSON
                timeout=30,  # Don't wait more than 30 seconds
            )
        except requests.exceptions.ConnectionError:
            raise GroqAPIError("No internet connection. Please check your network.")
        except requests.exceptions.Timeout:
            raise GroqAPIError("Request timed out after 30 seconds. Try again.")

        # ── Handle HTTP errors ──
        if response.status_code == 401:
            raise GroqAPIError("Invalid API key. Check your key at console.groq.com")
        elif response.status_code == 429:
            raise GroqAPIError("Rate limit hit. Wait a moment and try again.")
        elif response.status_code == 400:
            error_detail = (
                response.json().get("error", {}).get("message", "Bad request")
            )
            raise GroqAPIError(f"Bad request: {error_detail}")
        elif not response.ok:
            raise GroqAPIError(f"API error {response.status_code}: {response.text}")

        # ── Parse the response ──
        # Groq returns JSON in OpenAI format:
        # { "choices": [{ "message": { "role": "assistant", "content": "..." } }] }
        data = response.json()
        return data["choices"][0]["message"]["content"]

    def get_model_info(self) -> str:
        """Return a short string describing the current model."""
        return f"Model: {self.model}"
