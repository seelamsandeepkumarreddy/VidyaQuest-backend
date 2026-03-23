import requests
import json
import os

BASE_URL = "http://127.0.0.1:5001/api/courses"

def test_upload_lesson():
    print("Testing /upload-lesson...")
    with open("test.pdf", "w") as f:
        f.write("dummy pdf content")
    
    with open("test.pdf", "rb") as f:
        files = {'file': ('test.pdf', f, 'application/pdf')}
        data = {
            'subject_id': '1',
            'grade': '8',
            'chapter_number': '10',
            'title': 'Test Chapter',
            'lessons_count': '5'
        }
        response = requests.post(f"{BASE_URL}/upload-lesson", files=files, data=data)
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    
    try:
        os.remove("test.pdf")
    except:
        pass

def test_upload_quiz():
    print("\nTesting /upload-quiz...")
    data = {
        "subjectId": 1,
        "grade": "8",
        "chapterNumber": "10",
        "title": "Test Quiz",
        "questions": [
            {
                "text": "What is 2+2?",
                "options": ["3", "4", "5", "6"],
                "correct_option_index": 1,
                "review_text": "2+2 is 4"
            }
        ]
    }
    response = requests.post(f"{BASE_URL}/upload-quiz", json=data)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")

if __name__ == "__main__":
    try:
        test_upload_lesson()
        test_upload_quiz()
    except Exception as e:
        print(f"Error: {e}")
