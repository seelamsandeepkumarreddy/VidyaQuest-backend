import requests
import json

base_url = "http://127.0.0.1:5001/api/admin"
endpoints = [
    "stats",
    "users",
    "content/recent",
    "analytics/detailed",
    "attendance/summary",
    "notifications"
]

for ep in endpoints:
    url = f"{base_url}/{ep}"
    print(f"Testing {url}...")
    try:
        response = requests.get(url)
        print(f"  Status: {response.status_code}")
        if response.status_code != 200:
            print(f"  Error Response: {response.text}")
    except Exception as e:
        print(f"  Request failed: {e}")
    print("-" * 20)
