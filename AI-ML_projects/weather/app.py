from flask import Flask, request, jsonify
import requests

app = Flask(__name__)
API_KEY = "your api key"

@app.route("/")
def home():
    return "Weather API is running!"

@app.route("/weather", methods=["GET"])
def get_weather():
    city = request.args.get("city")
    if not city:
        return jsonify({"error": "Please provide city name"}), 400

    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
    response = requests.get(url)
    data = response.json()

    print("API Response:", data)

    cod = data.get("cod")
    if cod != 200:
        # Return the actual API error message for easier debugging
        return jsonify({
            "error": data.get("message", "Unknown error"),
            "cod": cod
        }), 404

    result = {
        "city": city,
        "temperature": data["main"]["temp"],
        "humidity": data["main"]["humidity"],
        "description": data["weather"][0]["description"]
    }
    return jsonify(result)

if __name__ == "__main__":
    app.run(debug=True)

# http://127.0.0.1:5000/weather?city=Pune
