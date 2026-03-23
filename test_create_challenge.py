import requests
import json

# Try 127.0.0.1 instead of localhost
BASE_URL = "http://127.0.0.1:5001/api/courses/challenges"

def test_create_challenge():
    # Try with a valid teacher ID (ID 10 from our check)
    payload = {
        "author_id": 10,
        "grade": "8",
        "title": "Test Challenge",
        "description": "Test Description",
        "questions": [
            {
                "id": 0,
                "text": "What is 1+1?",
                "options": ["1", "2", "3", "4"],
                "correct_option_index": 1,
                "review_text": "Math"
            }
        ]
    }
    
    print(f"Sending request to {BASE_URL}...")
    try:
        response = requests.post(BASE_URL, json=payload, timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Response Body: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_create_challenge()
