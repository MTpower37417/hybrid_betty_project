import json
import os


def search_memory_by_keyword(
        keyword,
        date_range=None,
        base_path="memory/capsule"):
    results = []
    for filename in os.listdir(base_path):
        if not filename.endswith(".json"):
            continue
        if date_range and not any(date in filename for date in date_range):
            continue
        with open(os.path.join(base_path, filename), "r", encoding="utf-8") as f:
            data = json.load(f)
            if keyword.lower() in json.dumps(data).lower():
                results.append((filename, data))
    return results


def get_capsule_summary(capsule_data):
    return capsule_data.get("summary", "ไม่พบสรุปในแคปซูลนี้")


def get_capsule_by_emotion(emotion_tag, base_path="memory/capsule"):
    results = []
    for filename in os.listdir(base_path):
        if not filename.endswith(".json"):
            continue
        with open(os.path.join(base_path, filename), "r", encoding="utf-8") as f:
            data = json.load(f)
            if data.get("emotion") == emotion_tag:
                results.append((filename, data))
    return results


def fetch_capsule_for_prompt(user_query, emotion=None):
    keyword = user_query
    matches = search_memory_by_keyword(keyword)
    if emotion:
        matches = [m for m in matches if m[1].get("emotion") == emotion]
    return [get_capsule_summary(m[1]) for m in matches[:3]]
