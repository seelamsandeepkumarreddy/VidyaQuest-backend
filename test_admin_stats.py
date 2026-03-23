import requests
import json

BASE_URL = "http://172.23.19.214:5001/api"

def test_admin_stats():
    print("Testing Admin Stats Endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/admin/stats")
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print("Response Data:")
            print(json.dumps(data, indent=2))
            if data['status'] == 'success':
                print("SUCCESS: Admin stats retrieved correctly.")
            else:
                print("FAILURE: Status not success.")
        else:
            print(f"FAILURE: {response.text}")
    except Exception as e:
        print(f"ERROR: {str(e)}")

if __name__ == "__main__":
    test_admin_stats()
