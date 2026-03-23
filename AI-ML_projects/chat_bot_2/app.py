from flask import Flask, request, jsonify
import requests
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
API_KEY = os.getenv("GROK_API_KEY")


@app.route("/")
def home():
    return "Chatbot API Running"


@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True)
    user_input = data.get("message") if data else None

    if not user_input:
        return jsonify({"error": "No message provided"}), 400

    response = requests.post(
        "https://api.x.ai/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "model": "llama3-8b-8192",  # ✅ Grok model
            "messages": [
                {
                    "role": "system",
                    "content": "You are a helpful assistant. Answer clearly and simply.",
                },
                {"role": "user", "content": user_input},
            ],
        },
    )

    result = response.json()

    if "choices" not in result:
        return (
            jsonify(
                {"error": result.get("error", {}).get("message", "Grok API error")}
            ),
            500,
        )

    reply = result["choices"][0]["message"]["content"]
    return jsonify({"reply": reply})


if __name__ == "__main__":
    app.run(debug=True)
