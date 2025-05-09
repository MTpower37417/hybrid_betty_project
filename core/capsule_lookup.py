import os
import re

CAPSULE_DIR = "./bedroom/capsule/"


def load_capsule_files():
    capsule_texts = []
    for file in os.listdir(CAPSULE_DIR):
        if file.endswith(".txt"):
            path = os.path.join(CAPSULE_DIR, file)
            try:
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()
                    capsule_texts.append({
                        "filename": file,
                        "content": content
                    })
            except Exception as e:
                print(f"Error reading {file}: {e}")
    return capsule_texts


def search_capsules(query: str, capsules: list, max_results: int = 3):
    results = []
    for c in capsules:
        if re.search(query, c["content"], re.IGNORECASE):
            results.append(c)
        if len(results) >= max_results:
            break
    return results


def get_related_memories(query: str):
    all_capsules = load_capsule_files()
    matches = search_capsules(query, all_capsules)
    return [{
        "source": m["filename"],
        "snippet": m["content"][:300]
    } for m in matches]
