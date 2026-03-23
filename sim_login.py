import requests
import json

url = "http://127.0.0.1:5001/api/login"
payload = {
    "email": "admin@gmail.com",
    "password": "Adm@10"
}
headers = {
    "Content-Type": "application/json"
}

try:
    response = requests.post(url, data=json.dumps(payload), headers=headers)
    print(f"Status Code: {response.status_code}")
    print(f"Response Body: {response.text}")
except Exception as e:
    print(f"Request failed: {e}")
