<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&color=gradient&customColorList=6,11,20&height=200&section=header&text=SEEU%20AI%20Assistant&fontSize=50&fontColor=fff&animation=twinkling&fontAlignY=35&desc=Your%20Intelligent%20Desktop%20Voice%20Assistant&descAlignY=58&descSize=18"/>

![Python](https://img.shields.io/badge/Python-3.8+-blue?style=for-the-badge&logo=python)
![Eel](https://img.shields.io/badge/Eel-Desktop%20GUI-green?style=for-the-badge&logo=google-chrome)
![OpenAI](https://img.shields.io/badge/OpenAI-GPT-412991?style=for-the-badge&logo=openai)
![Groq](https://img.shields.io/badge/Groq-LLaMA-orange?style=for-the-badge)
![Gemini](https://img.shields.io/badge/Google-Gemini-4285F4?style=for-the-badge&logo=google)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

> **SEEU** is a fully-featured AI-powered Desktop Voice Assistant built with Python. It supports multi-LLM intelligence, real-time voice recognition, text-to-speech, system automation, battery monitoring, notification alerts, and image generation — all wrapped in a beautiful web-based GUI.

</div>

---

## ✨ Features

| Feature | Description |
|---|---|
| 🤖 **Multi-LLM Brain** | Supports OpenAI GPT, Groq (LLaMA), and Google Gemini |
| 🎤 **Voice Recognition (STT)** | Push-to-Talk and Continuous Listening modes |
| 🔊 **Text-to-Speech (TTS)** | Microsoft Edge TTS — natural, high-quality voice |
| 🖥️ **Desktop GUI** | Beautiful web-based interface powered by Eel |
| 🌐 **WiFi Control** | Turn WiFi ON/OFF via voice command |
| 📶 **Bluetooth Control** | Toggle Bluetooth with voice |
| 🔋 **Battery Monitoring** | Real-time battery alerts — low, critical, full, charging |
| 🔔 **Notification Monitor** | WhatsApp, Gmail & system notification alerts |
| 🖼️ **Image Generation** | Generate images via Pollinations AI |
| 🧠 **Memory Persistence** | Remembers conversations across sessions |
| ⌨️ **Keyboard & Mouse** | Full system automation support |
| 🔍 **Web & YouTube Search** | Search the web by voice |
| 📸 **Screen Brightness** | Control screen brightness via voice |
| 🚀 **Task Automation** | Automate repetitive system tasks |

---

## 🗂️ Project Structure

```
SEEU/
│
├── SEEU.py                        # 🚀 Main entry point — starts the app
│
├── Backend/
│   ├── Brain.py                   # 🧠 AI engine — multi-LLM processor
│   ├── TTS.py                     # 🔊 Text-to-Speech (Microsoft Edge TTS)
│   ├── STT.py                     # 🎤 Speech-to-Text (Speech Recognition)
│   ├── SystemControl.py           # 🌐 WiFi & Bluetooth control
│   ├── BatteryAutomation.py       # 🔋 Battery monitoring & alerts
│   ├── TaskAutomation.py          # ⚙️ Task & system automation
│   ├── NotificationMonitor.py     # 🔔 WhatsApp, Gmail & system alerts
│   ├── diagnose_microphone.py     # 🎙️ Microphone diagnostic tool
│   ├── migrate_seeu_db.py         # 💾 Database migration utility
│   ├── Database/                  # 🗄️ Persistent memory storage
│   └── Logs/                      # 📋 Application logs
│
├── Web/
│   ├── index.html                 # 🌐 Main GUI interface
│   ├── css/                       # 🎨 Stylesheets
│   └── js/                        # ⚡ Frontend scripts
│
├── requirements.txt               # 📦 Python dependencies
├── .env                           # 🔐 API keys (NOT on GitHub)
├── test.py                        # 🧪 Testing script
└── README.md                      # 📖 Documentation
```

---

## ⚙️ Setup & Installation

### 1. Clone the Repository
```bash
git clone https://github.com/Narendra-Sonawane7/My_Project.git
cd My_Project/AI-ML_projects/SEEU
```

### 2. Create a Virtual Environment
```bash
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac/Linux
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

> ⚠️ **PyAudio** may require extra steps on Windows:
```bash
pip install pipwin
pipwin install pyaudio
```

### 4. Install Tesseract OCR (for screen reading)
- Download from → [tesseract-ocr](https://github.com/UB-Mannheim/tesseract/wiki)
- Add to system PATH

### 5. Create `.env` File
```env
OPENAI_API_KEY=your_openai_key_here
GROQ_API_KEY=your_groq_key_here
GEMINI_API_KEY=your_gemini_key_here
```
> ⚠️ Never upload your `.env` file to GitHub!

### 6. Run SEEU
```bash
python SEEU.py
```

> SEEU will open at → `http://localhost:8000` in Chrome automatically.

---

## 🚀 Voice Commands

### 🤖 AI Chat
```
"Hey SEEU, what is machine learning?"
"Explain quantum computing"
"Write a Python function for sorting"
```

### 🌐 WiFi & Bluetooth
```
"Turn on WiFi"           "Turn off WiFi"
"Enable Bluetooth"       "Disable Bluetooth"
"WiFi status"            "System status"
"Turn off all connections"
```

### 🔋 Battery
```
"Battery percentage"     "Check battery"
"Is it charging?"        "Battery status"
```

### 🔍 Web & Search
```
"Search for AI news"
"Play lo-fi music on YouTube"
"Open Google"
```

### 🖥️ System Control
```
"Increase brightness"    "Decrease brightness"
"Take a screenshot"
"Close Chrome"
```

### 🖼️ Image Generation
```
"Generate an image of a sunset over mountains"
"Create an image of a futuristic city"
```

---

## 🧠 AI Models Supported

| Provider | Model | Use Case |
|---|---|---|
| **Groq** | LLaMA 3 | Fast responses |
| **OpenAI** | GPT-4 / GPT-3.5 | Advanced reasoning |
| **Google** | Gemini | Multimodal AI |

---

## 🛠️ Tech Stack

| Category | Technology |
|---|---|
| **Language** | Python 3.8+ |
| **Desktop GUI** | Eel (HTML/CSS/JS) |
| **AI / LLM** | OpenAI, Groq, Google Gemini |
| **TTS** | Microsoft Edge TTS + Pygame |
| **STT** | SpeechRecognition + PyAudio |
| **System** | psutil, pyautogui, pynput |
| **Connectivity** | subprocess (WiFi/Bluetooth) |
| **Image Gen** | Pollinations AI + Pillow |
| **Notifications** | Custom NotificationMonitor |
| **Web** | pywhatkit, Flask, Requests |
| **Data** | Pandas, SQLite |
| **Screen** | screen-brightness-control, pytesseract |

---

## 🔐 Security

- All API keys stored in `.env` — never hardcoded
- `.env` added to `.gitignore`
- System commands run with minimal privilege
- WiFi/Bluetooth control requires Windows admin rights

---

## 🖥️ System Requirements

| Requirement | Details |
|---|---|
| **OS** | Windows 10 / 11 |
| **Python** | 3.8 or higher |
| **Browser** | Google Chrome |
| **Microphone** | Required for voice features |
| **Internet** | Required for AI API calls |
| **RAM** | 4GB+ recommended |

---

## 📄 License

This project is licensed under the **MIT License**.

---

## 👨‍💻 Author

**Narendra Sonawane**

[![GitHub](https://img.shields.io/badge/GitHub-Narendra--Sonawane7-black?style=for-the-badge&logo=github)](https://github.com/Narendra-Sonawane7)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-blue?style=for-the-badge&logo=linkedin)](https://linkedin.com/in/narendrasonawane77)

---

<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&color=gradient&customColorList=6,11,20&height=120&section=footer&text=Powered%20by%20AI%20%F0%9F%A4%96&fontSize=24&fontColor=fff&animation=twinkling"/>

</div>
