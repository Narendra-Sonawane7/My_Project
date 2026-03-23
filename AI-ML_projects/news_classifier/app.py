from flask import Flask, request, jsonify
from model import predict_news

app = Flask(__name__)

@app.route("/")
def home():
    return "News Classifier API Running"

# ✅ After — accepts both GET and POST
@app.route("/predict", methods=["GET", "POST"])
def predict():
    if request.method == "GET":
        return '''
            <form method="POST">
                <input name="text" placeholder="Enter news text" style="width:400px; padding:8px">
                <button type="submit">Classify</button>
            </form>
        '''

    if request.is_json:
        data = request.get_json(silent=True)
        text = data.get("text") if data else None
    else:
        text = request.form.get("text")

    if not text:
        return jsonify({"error": "No text provided"}), 400

    category = predict_news(text)
    return jsonify({"input": text, "category": category})

if __name__ == "__main__":
    app.run(debug=True)