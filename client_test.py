import requests

BASE = "http://127.0.0.1:5002"

# Test search
resp = requests.post(BASE + "/search", json={"query": "square_of_number"})
print("SEARCH RESULT:", resp.json())

# Test run
resp = requests.post(BASE + "/run", json={"path": "main.py"})
print("RUN RESULT:", resp.json())
