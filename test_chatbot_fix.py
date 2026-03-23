import requests
import time

BASE_URL = 'http://127.0.0.1:5001/api'

def test_chatbot():
    print("Testing Chatbot with Retry Logic...")
    
    # Send multiple requests in parallel or rapid succession to trigger 429 if possible
    # or just send one and check output
    data = {"question": "What is photosynthesis?"}
    
    try:
        print(f"Sending request to {BASE_URL}/chatbot/ask...")
        start_time = time.time()
        r = requests.post(f"{BASE_URL}/chatbot/ask", json=data)
        end_time = time.time()
        
        print(f"Status: {r.status_code}")
        print(f"Response: {r.json()}")
        print(f"Time taken: {end_time - start_time:.2f} seconds")
        
    except Exception as e:
        print(f"Test failed: {e}")

if __name__ == '__main__':
    # Make sure server is running
    test_chatbot()
