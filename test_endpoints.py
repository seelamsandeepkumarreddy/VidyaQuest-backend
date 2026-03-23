import requests
import json

BASE_URL = 'http://127.0.0.1:5001/api'

def test_endpoints():
    print("Testing Backend Endpoints...")
    
    # 1. Test Attendance
    print("\n--- Testing Attendance ---")
    data = {"student_id": 3, "grade": "8", "date": "2026-03-07", "status": "PRESENT"}
    try:
        r = requests.post(f"{BASE_URL}/attendance", json=data)
        print("POST /attendance:", r.status_code, r.json())
    except Exception as e: print("Fail:", e)

    try:
        r = requests.get(f"{BASE_URL}/attendance/8/2026-03-07")
        print("GET /attendance:", r.status_code, r.json())
    except Exception as e: print("Fail:", e)

    # 2. Test Announcements
    print("\n--- Testing Announcements ---")
    data = {"author_id": 14, "target_grade": "8", "content": "Test Announcement for Grade 8"}
    try:
        r = requests.post(f"{BASE_URL}/announcements", json=data)
        print("POST /announcements:", r.status_code, r.json())
    except Exception as e: print("Fail:", e)

    try:
        r = requests.get(f"{BASE_URL}/announcements/8")
        print("GET /announcements:", r.status_code, r.json())
    except Exception as e: print("Fail:", e)

    # 3. Test Progress
    print("\n--- Testing Progress ---")
    data = {"student_id": 3, "xp": 150, "lessons_completed": 2, "quiz_accuracy": 85, "study_time_minutes": 45}
    try:
        r = requests.post(f"{BASE_URL}/progress/save", json=data)
        print("POST /progress/save:", r.status_code, r.json())
    except Exception as e: print("Fail:", e)

    try:
        r = requests.get(f"{BASE_URL}/progress/3")
        print("GET /progress/3:", r.status_code, r.json())
    except Exception as e: print("Fail:", e)

if __name__ == '__main__':
    test_endpoints()
