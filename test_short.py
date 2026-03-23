import requests
import json

base_url = "http://127.0.0.1:5001/api/admin"
endpoints = ["stats", "users", "content/recent", "analytics/detailed", "attendance/summary", "notifications"]

for ep in endpoints:
    url = f"{base_url}/{ep}"
    try:
        r = requests.get(url)
        print(f"{ep}: {r.status_code}")
        if r.status_code != 200:
            print(f"  ERR: {r.text[:100]}")
    except Exception as e:
        print(f"{ep}: FAIL {str(e)[:50]}")
