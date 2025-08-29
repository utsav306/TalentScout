import json
import os

SAVE_PATH = "candidates.json"

def save_candidate(data):
    existing = []
    if os.path.exists(SAVE_PATH):
        try:
            with open(SAVE_PATH, "r") as f:
                content = f.read().strip()
                if content:
                    existing = json.loads(content)
        except Exception:
            existing = []
    existing.append(data)
    with open(SAVE_PATH, "w") as f:
        json.dump(existing, f, indent=2)
