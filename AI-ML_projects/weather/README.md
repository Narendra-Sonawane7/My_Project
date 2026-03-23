# 🌦️ Weather API — Powered by OpenWeatherMap

![Python](https://img.shields.io/badge/Python-3.8+-blue?style=for-the-badge&logo=python)
![Flask](https://img.shields.io/badge/Flask-2.x-black?style=for-the-badge&logo=flask)
![OpenWeatherMap](https://img.shields.io/badge/OpenWeatherMap-API-orange?style=for-the-badge&logo=cloudflare)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

> A simple and clean **Weather REST API** built with **Flask** and **OpenWeatherMap API**. Get real-time weather data — temperature, humidity, and description — for any city in the world!

---

## 📌 Features

- ✅ Real-time weather data for any city
- ✅ Returns **temperature**, **humidity**, and **weather description**
- ✅ Built with Flask REST API
- ✅ Uses **OpenWeatherMap** free API
- ✅ Secure API key management via `.env`
- ✅ Simple GET request — easy to integrate

---

## 🗂️ Project Structure

```
weather-api/
│
├── app.py               # Main Flask application
├── requirements.txt     # Python dependencies
├── .env                 # API Key (NOT uploaded to GitHub)
└── README.md            # Project documentation
```

---

## ⚙️ Setup & Installation

### 1. Clone the Repository
```bash
git clone https://github.com/Narendra-Sonawane/My_Projects.git
cd My_Projects/weather-api
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

### 4. Get Free API Key
1. Go to → [openweathermap.org](https://openweathermap.org/api)
2. Sign up for a free account
3. Go to **API Keys** section → Copy your key

### 5. Create `.env` file
```bash
OPENWEATHER_API_KEY=your_api_key_here
```
> ⚠️ Never hardcode API keys in your code or push them to GitHub!

### 6. Run the App
```bash
python app.py
```
Server starts at → `http://127.0.0.1:5000`

---

## 🚀 API Usage

### Endpoint
```
GET /weather?city={city_name}
```

### Example Request
```
http://127.0.0.1:5000/weather?city=Pune
```

### Example Response
```json
{
  "city": "Pune",
  "temperature": 28.5,
  "humidity": 65,
  "description": "scattered clouds"
}
```

### Error Response (City not found)
```json
{
  "error": "city not found",
  "cod": "404"
}
```

---

## 🧪 Testing

You can test directly in your browser:
```
http://127.0.0.1:5000/weather?city=Mumbai
http://127.0.0.1:5000/weather?city=London
http://127.0.0.1:5000/weather?city=New York
```

Or using curl:
```bash
curl "http://127.0.0.1:5000/weather?city=Pune"
```

Or using Python:
```python
import requests
response = requests.get("http://127.0.0.1:5000/weather?city=Pune")
print(response.json())
```

---

## 🛠️ Tech Stack

| Technology | Purpose |
|---|---|
| Python | Core language |
| Flask | Web framework / REST API |
| OpenWeatherMap API | Real-time weather data |
| python-dotenv | Secure API key management |
| Requests | HTTP calls to weather API |

---

## 🔐 Security — Fix Hardcoded API Key

Install dotenv:
```bash
pip install python-dotenv
```

Update `app.py`:
```python
from dotenv import load_dotenv
import os

load_dotenv()
API_KEY = os.getenv("OPENWEATHER_API_KEY")
```

Add `.env` to `.gitignore`:
```bash
echo ".env" >> .gitignore
```

> ✅ This keeps your API key safe and off GitHub!

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
