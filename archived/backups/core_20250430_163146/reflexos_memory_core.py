
import json
import os
from datetime import datetime

# Paths
BASE_PATH = os.path.dirname(__file__)
MEMORY_PATH = os.path.join(BASE_PATH, "memory")
STACK_PATH = os.path.join(MEMORY_PATH, "stack")
LONGTERM_PATH = os.path.join(MEMORY_PATH, "longterm")

os.makedirs(STACK_PATH, exist_ok=True)
os.makedirs(LONGTERM_PATH, exist_ok=True)


def save_memory(message: str, user: str = "default"):
    timestamp = datetime.now().isoformat()
    entry = {"timestamp": timestamp, "user": user, "message": message}

    # Save to short-term memory stack
    short_file = os.path.join(STACK_PATH, f"{user}_stack.json")
    stack = []
    if os.path.exists(short_file):
        with open(short_file, "r", encoding="utf-8") as f:
            stack = json.load(f)
    stack.append(entry)
    with open(short_file, "w", encoding="utf-8") as f:
        json.dump(stack[-50:], f, ensure_ascii=False, indent=2)

    # Save to long-term memory by year
    year = datetime.now().strftime("%Y")
    long_file = os.path.join(LONGTERM_PATH, f"{user}_{year}.json")
    long_stack = []
    if os.path.exists(long_file):
        with open(long_file, "r", encoding="utf-8") as f:
            long_stack = json.load(f)
    long_stack.append(entry)
    with open(long_file, "w", encoding="utf-8") as f:
        json.dump(long_stack, f, ensure_ascii=False, indent=2)


def recall_memory(keyword: str, user: str = "default", year: str = None):
    results = []
    if not year:
        years = [f.split("_")[-1].split(".")[0]
                 for f in os.listdir(LONGTERM_PATH) if f.startswith(user)]
    else:
        years = [year]

    for y in years:
        file_path = os.path.join(LONGTERM_PATH, f"{user}_{y}.json")
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                matched = [
                    entry for entry in data if keyword in entry["message"]]
                results.extend(matched)
    return results


def load_memory_context(user: str = "default"):
    stack_file = os.path.join(STACK_PATH, f"{user}_stack.json")
    if not os.path.exists(stack_file):
        return []
    with open(stack_file, "r", encoding="utf-8") as f:
        entries = json.load(f)
    return [{"role": "user", "content": e["message"]} for e in entries[-10:]]
