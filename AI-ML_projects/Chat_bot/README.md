# ⚡ Groq Chatbot

A fast, terminal-based conversational AI chatbot powered by [Groq's LPU Inference API](https://console.groq.com). Supports multiple LLMs, persistent conversation memory, and slash commands — all from the command line.

---

## Features

- 🚀 **Blazing fast responses** — Groq's LPU chips run LLMs ~10x faster than GPUs
- 🧠 **Conversation memory** — full history sent with every API call so the bot remembers context
- 🤖 **Multiple models** — switch between Llama, Gemma, and Mixtral mid-conversation
- 💬 **Slash commands** — `/clear`, `/stats`, `/model`, `/system`, `/help`, `/exit`
- 🎨 **Colour-coded terminal UI** — clean, readable output with ANSI colours
- 🔑 **Secure API key handling** — loaded from `.env`, never hardcoded

---

## Project Structure

```
groq-chatbot/
├── main.py          # Entry point — input loop and command handling
├── chatbot.py       # Core ChatBot class — orchestrates API + memory
├── groq_client.py   # Groq API HTTP client — all network logic lives here
├── memory.py        # Conversation history management
├── config.py        # All settings and constants
├── utils.py         # Terminal UI helpers and formatting
├── requirements.txt # Python dependencies
└── .env             # Your API key (create this yourself — see setup below)
```

### Architecture Overview

```
main.py  (Controller)
   └── ChatBot  (chatbot.py)
         ├── GroqClient      (groq_client.py)  → HTTP calls to Groq API
         └── ConversationMemory (memory.py)    → Stores message history
```

`utils.py` handles all display/formatting. `config.py` holds all settings. Nothing is mixed together — each file has a single job.

---

## Quickstart

### 1. Clone the repository

```bash
git clone https://github.com/your-username/groq-chatbot.git
cd groq-chatbot
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Get a free Groq API key

Go to [console.groq.com](https://console.groq.com), sign up, and generate an API key.

### 4. Create a `.env` file

```bash
# .env
GROQ_API_KEY=gsk_your_key_here
```

> ⚠️ Never commit your `.env` file. Add it to `.gitignore`.

### 5. Run the chatbot

```bash
python main.py
```

---

## Available Models

| # | Model | Notes |
|---|-------|-------|
| 1 | `llama-3.3-70b-versatile` | Best quality (default) |
| 2 | `llama-3.1-8b-instant` | Fastest, great for testing |
| 3 | `gemma2-9b-it` | Google's model, balanced |
| 4 | `mixtral-8x7b-32768` | Largest context window (32k tokens) |

You can switch models at any time during a conversation using `/model`.

---

## Slash Commands

| Command | Description |
|---------|-------------|
| `/help` | Show all available commands |
| `/clear` | Clear conversation history, start fresh |
| `/stats` | Show model, turn count, and token estimate |
| `/model` | Switch to a different LLM model |
| `/system` | Change the bot's persona/system prompt |
| `/exit` | Exit the program |

---

## How Memory Works

LLMs are stateless — they remember nothing between API calls. This chatbot simulates memory by sending the **full conversation history** with every request:

```
API Call 1:  [system_prompt, user_1]
API Call 2:  [system_prompt, user_1, assistant_1, user_2]
API Call 3:  [system_prompt, user_1, assistant_1, user_2, assistant_2, user_3]
```

To prevent the context window from overflowing, the oldest messages are dropped once history exceeds `MAX_HISTORY` (default: 20 messages / 10 turns), configured in `config.py`.

---

## Configuration

All settings are in `config.py`:

| Setting | Default | Description |
|---------|---------|-------------|
| `DEFAULT_MODEL` | `llama-3.3-70b-versatile` | Model used on startup |
| `MAX_TOKENS` | `1024` | Max tokens per response |
| `TEMPERATURE` | `0.7` | Creativity (0 = focused, 1 = creative) |
| `MAX_HISTORY` | `20` | Max messages kept in memory |
| `DEFAULT_SYSTEM_PROMPT` | See config.py | Bot persona/instructions |

---

## Requirements

- Python 3.10+
- `requests` 2.31.0
- `python-dotenv` 1.0.0

---

## License

MIT License — free to use, modify, and distribute.
