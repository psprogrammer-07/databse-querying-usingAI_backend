import requests
import json

url = "http://127.0.0.1:5000/api/generate_kpi"
payload = {"query": "Key metrics for sales and users"}

try:
    print(f"Sending request to {url} with payload: {payload}")
    response = requests.post(url, json=payload)
    
    print(f"Status Code: {response.status_code}")
    print("Response JSON:")
    print(json.dumps(response.json(), indent=2))
except Exception as e:
    print(f"Request failed: {e}")
