
import json
import os
from datetime import datetime

# Path base
STACK_PATH = os.path.join(os.path.dirname(__file__), "memory", "stack")
EXTENDED_PATH = os.path.join(os.path.dirname(__file__), "memory", "extended")
os.makedirs(EXTENDED_PATH, exist_ok=True)


def append_context_segment(user: str, message: str, response: str):
    file_path = os.path.join(EXTENDED_PATH, f"{user}_context.json")
    entry = {
        "timestamp": datetime.now().isoformat(),
        "message": message,
        "response": response
    }

    context = []
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            context = json.load(f)

    context.append(entry)

    # Keep latest ~300 entries (approx ~25,000 tokens depending on length)
    context = context[-300:]
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(context, f, ensure_ascii=False, indent=2)


def get_extended_context(user: str):
    file_path = os.path.join(EXTENDED_PATH, f"{user}_context.json")
    if not os.path.exists(file_path):
        return []

    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)
