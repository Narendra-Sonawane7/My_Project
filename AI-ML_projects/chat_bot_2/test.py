import requests

response = requests.post(
    "http://127.0.0.1:5000/chat",
    json={"message": "What is artificial intelligence?"}
)

print("Status Code:", response.status_code)  # ✅ shows HTTP status
print("Raw Response:", response.text)        # ✅ shows actual response text