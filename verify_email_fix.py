import requests
import json

def test_user_creation(email, name="Test User"):
    url = "http://127.0.0.1:5001/api/admin/create-user"
    payload = {
        "full_name": name,
        "email": email,
        "role": "student",
        "grade": "Grade 10"
    }
    try:
        response = requests.post(url, json=payload, timeout=10)
        print(f"Testing email: '{email}' -> Status: {response.status_code}, Response: {response.json()}")
        return response.status_code == 200 or response.status_code == 201 or response.status_code == 409 # 409 means email already exists which is also valid validation
    except Exception as e:
        print(f"Error testing email '{email}': {e}")
        return False

if __name__ == "__main__":
    emails_to_test = [
        "valid@example.com",
        "  trimmed@example.com  ",
        "user.name+tag@mail.co.uk",
        "capital@Example.Com",
        "dash-user@my-domain.org"
    ]
    
    all_passed = True
    for email in emails_to_test:
        if not test_user_creation(email):
            all_passed = False
            
    if all_passed:
        print("\n✅ All email validation tests passed!")
    else:
        print("\n❌ Some email validation tests failed.")
