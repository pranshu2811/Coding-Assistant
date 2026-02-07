import requests
import json
import re

url = "http://localhost:11434/api/generate"

prompt = "Refactor this Python function to use type hints:\n\ndef square_of_number(number):\n    return number * number\n"

payload = {
    "model": "qwen2.5-coder:3b",
    "prompt": prompt,
    "stream": False
}

response = requests.post(url, data=json.dumps(payload))
data = response.json()

full_response = data.get("response", "")
# Try to pull out only the code block between ```python ... ```
match = re.search(r"```python(.*?)```", full_response, re.DOTALL)
if match:
    code_only = match.group(1).strip()
else:
    code_only = full_response.strip()

print("=== MODEL CODE OUTPUT ===")
print(code_only)
