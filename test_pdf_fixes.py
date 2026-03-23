import urllib.request
import json
import socket

def test_api():
    try:
        url = 'http://127.0.0.1:5001/api/courses/chapters/1'
        print(f"Testing API: {url}")
        with urllib.request.urlopen(url, timeout=10) as resp:
            data = json.loads(resp.read().decode())
            chapters = data.get('data', [])
            if chapters:
                c = chapters[0]
                print(f"SUCCESS: Chapter '{c.get('title')}' has PDF URL: {c.get('pdf_url')}")
            else:
                print("WARNING: No chapters returned for subject 1")
    except Exception as e:
        print(f"FAILED: API Test error: {e}")

def test_pdf_serving():
    try:
        url = 'http://127.0.0.1:5001/api/pdfs/sample.pdf'
        print(f"Testing PDF serving: {url}")
        with urllib.request.urlopen(url, timeout=10) as resp:
            print(f"SUCCESS: PDF Serving Test (sample.pdf) -> Status {resp.getcode()}")
    except Exception as e:
        print(f"FAILED: PDF Serving Test (sample.pdf) -> Error: {e}")

if __name__ == '__main__':
    test_api()
    print("-" * 30)
    test_pdf_serving()
