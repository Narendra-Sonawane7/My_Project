# 🤖 AI Chatbot — Powered by Grok API

![Python](https://img.shields.io/badge/Python-3.8+-blue?style=for-the-badge&logo=python)
![Flask](https://img.shields.io/badge/Flask-2.x-black?style=for-the-badge&logo=flask)
![Grok API](https://img.shields.io/badge/Grok-xAI-white?style=for-the-badge&logo=x)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

> A lightweight AI Chatbot REST API built with **Flask** and powered by **xAI's Grok API**. Send a message, get an intelligent reply instantly.

---

## 📌 Features

- ✅ REST API built with Flask
- ✅ Integrated with **Grok (xAI)** language model
- ✅ Secure API key management using `.env`
- ✅ Simple POST endpoint for chat
- ✅ Easy to test and extend

---

## 🗂️ Project Structure

```
chatbot/
│
├── app.py               # Main Flask application
├── test.py              # API testing script
├── requirements.txt     # Python dependencies
├── .env                 # API keys (NOT uploaded to GitHub)
└── README.md            # Project documentation
```

---

## ⚙️ Setup & Installation

### 1. Clone the Repository
```bash
git clone https://github.com/Narendra-Sonawane/My_Projects.git
cd My_Projects/chatbot
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

### 4. Create `.env` file
```bash
GROK_API_KEY=your_grok_api_key_here
```
> ⚠️ Never share or upload your `.env` file to GitHub!

### 5. Run the App
```bash
python app.py
```
Server will start at → `http://127.0.0.1:5000`

---

## 🚀 API Usage

### Endpoint
```
POST /chat
```

### Request Body
```json
{
  "message": "What is artificial intelligence?"
}
```

### Response
```json
{
  "reply": "Artificial intelligence (AI) is the simulation of human intelligence..."
}
```

---

## 🧪 Testing

Run the test script to verify the API is working:
```bash
python test.py
```

Expected output:
```
Status Code: 200
Raw Response: {"reply": "Artificial intelligence is..."}
```

---

## 🛠️ Tech Stack

| Technology | Purpose |
|---|---|
| Python | Core language |
| Flask | Web framework |
| Grok API (xAI) | AI language model |
| python-dotenv | Secure env management |
| Requests | HTTP calls |

---

## 🔐 Security

- API keys are stored in `.env` file
- `.env` is added to `.gitignore` — never pushed to GitHub
- Always regenerate API keys if accidentally exposed

---

## 📄 License

This project is licensed under the **MIT License** — feel free to use and modify.

---

## 👨‍💻 Author

**Narendra Sonawane**  
[![GitHub](https://img.shields.io/badge/GitHub-Narendra--Sonawane-black?style=flat&logo=github)](https://github.com/Narendra-Sonawane)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-blue?style=flat&logo=linkedin)](https://linkedin.com/in/your-profile)

---

⭐ **If you found this helpful, give it a star!**
