import requests
import json
import subprocess
import textwrap
from pathlib import Path
from typing import List

PROJECT_ROOT = Path(r"C:\Users\prans\Desktop\local-ai-coding-assistant\project")
MODEL_NAME = "qwen2.5-coder:3b"
LLM_URL = "http://localhost:11434/api/generate"

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

def refactor_file(relative_path: str, instructions: str):
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

    # very simple: if there is a ```python``` block, keep its inside
    import re
    match = re.search(r"```python(.*?)```", new_code, re.DOTALL)
    if match:
        cleaned = match.group(1).strip()
    else:
        cleaned = new_code.strip()

    file_path.write_text(cleaned, encoding="utf-8")
    print(f"Updated {relative_path}")

def run_file(relative_path: str) -> None:
    """
    Run a Python file (like main.py) and print its output or errors.
    """
    file_path = PROJECT_ROOT / relative_path

    # Run: python <that file>
    result = subprocess.run(
        ["python", str(file_path)],
        capture_output=True,
        text=True
    )

    print("=== RUN OUTPUT ===")
    print(result.stdout)

    if result.stderr:
        print("=== RUN ERRORS ===")
        print(result.stderr)

    print("Exit code:", result.returncode)

if __name__ == "__main__":
    print("1) Refactor a file")
    print("2) Search in project")
    print("3) Run a Python file")
    choice = input("Choose an option (1, 2, or 3): ").strip()

    if choice == "1":
        rel = input("File (e.g., main.py): ").strip()
        instr = input("What should I do with this file?: ").strip()
        refactor_file(rel, instr)
    elif choice == "2":
        query = input("Search for (text): ").strip()
        results = search_in_project(query)
        print("Matches:")
        for path in results:
            print(" -", path)
    elif choice == "3":
        rel = input("File to run (e.g., main.py): ").strip()
        run_file(rel)
    else:
        print("Invalid choice")


def search_in_project(query: str) -> List[str]:
    """
    Search for a text query in all .py files under PROJECT_ROOT.
    Returns a list of relative file paths that contain the query.
    """
    matches: List[str] = []
    for path in PROJECT_ROOT.rglob("*.py"):
        try:
            text = path.read_text(encoding="utf-8")
        except Exception:
            continue

        if query.lower() in text.lower():
            matches.append(str(path.relative_to(PROJECT_ROOT)))
    return matches
    refactor_file(rel, instr)
