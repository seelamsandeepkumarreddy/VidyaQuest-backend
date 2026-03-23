import requests
import json
import random
import string

BASE_URL = "http://localhost:5001/api"

def random_string(length=8):
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

def test_registration_and_login():
    email = f"test_{random_string()}@example.com"
    password = "password123"
    full_name = "Test User"
    phone = "1234567890"
    grade = "9"
    school_name = "Test Rural School"
    subject_expertise = "Science"
    experience = "5 years"

    # 1. Register
    register_data = {
        "full_name": full_name,
        "email": email,
        "phone": phone,
        "password": password,
        "role": "student",
        "grade": grade,
        "school_name": school_name,
        "subject_expertise": subject_expertise,
        "experience": experience
    }
    
    print(f"Registering user: {email}")
    register_response = requests.post(f"{BASE_URL}/register", json=register_data)
    print(f"Register Response: {register_response.status_code} - {register_response.text}")
    
    if register_response.status_code != 201:
        print("Registration failed")
        return

    # 2. Login
    login_data = {
        "email": email,
        "password": password
    }
    
    print(f"Logging in user: {email}")
    login_response = requests.post(f"{BASE_URL}/login", json=login_data)
    print(f"Login Response: {login_response.status_code}")
    
    if login_response.status_code != 200:
        print("Login failed")
        return

    res_json = login_response.json()
    user = res_json.get("user", {})
    
    print("\nVerifying fields in login response:")
    fields_to_check = {
        "full_name": full_name,
        "email": email,
        "grade": grade,
        "school_name": school_name,
        "subject_expertise": subject_expertise,
        "experience": experience
    }
    
    success = True
    for field, expected_value in fields_to_check.items():
        actual_value = user.get(field)
        if actual_value == expected_value:
            print(f"[OK] {field}: {actual_value}")
        else:
            print(f"[FAIL] {field}: Expected '{expected_value}', got '{actual_value}'")
            success = False
            
    if success:
        print("\nSUCCESS: All fields correctly stored and retrieved!")
    else:
        print("\nFAILURE: Some fields missing or incorrect.")

if __name__ == "__main__":
    test_registration_and_login()
