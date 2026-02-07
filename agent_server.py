from flask import Flask, request, jsonify
from pathlib import Path
import requests
import json
import textwrap
import subprocess

PROJECT_ROOT = Path(r"C:\Users\prans\Desktop\local-ai-coding-assistant\project")
MODEL_NAME = "qwen2.5-coder:3b"
LLM_URL = "http://localhost:11434/api/generate"

app = Flask(__name__)
def call_llm(prompt: str) -> str:
    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False,
    }
    resp = requests.post(LLM_URL, data=json.dumps(payload))
    resp.raise_for_status()
    data = resp.json()
    return data.get("response", "")

def refactor_file(relative_path: str, instructions: str) -> str:
    file_path = PROJECT_ROOT / relative_path
    code = file_path.read_text(encoding="utf-8")

    prompt = textwrap.dedent(f"""
    You are a coding assistant.
    The user will give you a Python file and instructions.
    Respond ONLY with the new full file content, in a code block.

    File path: {relative_path}

    Original file:
    ```python
    {code}
    ```

    Instructions:
    {instructions}
    """)

    new_code = call_llm(prompt)

    import re
    match = re.search(r"```python(.*?)```", new_code, re.DOTALL)
    if match:
        cleaned = match.group(1).strip()
    else:
        cleaned = new_code.strip()

    file_path.write_text(cleaned, encoding="utf-8")
    return cleaned

def search_in_project(query: str):
    matches = []
    for path in PROJECT_ROOT.rglob("*.py"):
        try:
            text = path.read_text(encoding="utf-8")
        except Exception:
            continue

        if query.lower() in text.lower():
            matches.append(str(path.relative_to(PROJECT_ROOT)))
    return matches

def run_file(relative_path: str):
    file_path = PROJECT_ROOT / relative_path

    result = subprocess.run(
        ["python", str(file_path)],
        capture_output=True,
        text=True
    )
    return {
        "stdout": result.stdout,
        "stderr": result.stderr,
        "returncode": result.returncode,
    }
@app.route("/refactor", methods=["POST"])
def api_refactor():
    data = request.get_json()
    path = data.get("path")
    instructions = data.get("instructions", "")
    if not path:
        return jsonify({"error": "path is required"}), 400
    new_code = refactor_file(path, instructions)
    return jsonify({"ok": True, "path": path, "new_code": new_code})

@app.route("/search", methods=["POST"])
def api_search():
    data = request.get_json()
    query = data.get("query", "")
    matches = search_in_project(query)
    return jsonify({"ok": True, "query": query, "matches": matches})

@app.route("/run", methods=["POST"])
def api_run():
    data = request.get_json()
    path = data.get("path")
    if not path:
        return jsonify({"error": "path is required"}), 400
    result = run_file(path)
    return jsonify({"ok": True, "path": path, **result})

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5002, debug=True)
