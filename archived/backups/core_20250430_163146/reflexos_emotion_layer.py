
import json
import os
from datetime import datetime

# Path base สำหรับบันทึกอารมณ์
EMOTION_PATH = os.path.join(os.path.dirname(__file__), "memory", "emotion")
os.makedirs(EMOTION_PATH, exist_ok=True)


def save_emotion(user: str, message: str, response: str):
    # วิเคราะห์ emotion เบื้องต้น (rule-based ง่ายๆ)
    sentiment = "neutral"
    if any(word in message.lower()
           for word in ["รัก", "คิดถึง", "ขอบคุณ", "ดีใจ"]):
        sentiment = "positive"
    elif any(word in message.lower() for word in ["โกรธ", "เกลียด", "เบื่อ", "เสียใจ"]):
        sentiment = "negative"

    timestamp = datetime.now().isoformat()
    entry = {
        "time": timestamp,
        "message": message,
        "response": response,
        "emotion": sentiment
    }

    filepath = os.path.join(EMOTION_PATH, f"{user}_emotion.json")
    history = []
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            history = json.load(f)

    history.append(entry)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(history[-100:], f, ensure_ascii=False, indent=2)


def get_emotion_log(user: str):
    filepath = os.path.join(EMOTION_PATH, f"{user}_emotion.json")
    if not os.path.exists(filepath):
        return []
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)
