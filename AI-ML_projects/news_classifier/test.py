import requests

response = requests.post(
    "http://127.0.0.1:5000/predict",
    json={"text": "NASA launches a new rocket to explore Mars"}
)

print(response.json())