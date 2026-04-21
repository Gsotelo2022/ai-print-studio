#!/usr/bin/env python3
import urllib.request
import json

payload = {
    "fullname": "Juan Perez",
    "email": "juan@example.com",
    "phone": "+541123456789",
    "password": "Password123"
}

data = json.dumps(payload).encode('utf-8')
req = urllib.request.Request(
    'http://127.0.0.1:8000/api/register',
    data=data,
    headers={'Content-Type': 'application/json'}
)

try:
    with urllib.request.urlopen(req) as response:
        result = json.loads(response.read().decode())
        print(json.dumps(result, indent=2))
except Exception as e:
    print(f"Error: {e}")
