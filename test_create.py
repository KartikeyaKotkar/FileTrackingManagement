import urllib.request
import json
req = urllib.request.Request('http://localhost:8000/auth/users')
req.add_header('X-User-Role', 'admin')
req.add_header('Content-Type', 'application/json')
data = json.dumps({"username": "testuser1", "password": "password", "fullname": "Test User", "role": "user"}).encode('utf-8')
try:
    res = urllib.request.urlopen(req, data=data)
    print(res.read().decode('utf-8'))
except Exception as e:
    print(e.read().decode())
