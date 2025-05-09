import json
import os
from datetime import datetime


class ReflexIntegration:
    def __init__(self):
        self.reflex_path = "./core/ReflexOS"
        self.capsule_path = f"{self.reflex_path}/memory_capsule"
        self.sync_path = f"{self.reflex_path}/ReflexSystem_Sync"

    def save_to_capsule(self, message, response, emotion):
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        capsule_data = {
            "timestamp": timestamp,
            "message": message,
            "response": response,
            "emotion": emotion,
            "type": "conversation"
        }

        # สร้างไฟล์ capsule
        filename = f"capsule_{timestamp}.json"
        path = f"./memory/capsule/{filename}"
        os.makedirs(os.path.dirname(path), exist_ok=True)

        with open(path, 'w', encoding='utf-8') as f:
            json.dump(capsule_data, f, ensure_ascii=False, indent=2)

        # ส่งไปยัง ReflexOS
        if os.path.exists(f"{self.capsule_path}"):
            reflex_path = f"{self.capsule_path}/{filename}"
            with open(reflex_path, 'w', encoding='utf-8') as f:
                json.dump(capsule_data, f, ensure_ascii=False, indent=2)

        return filename

    def sync_emotions(self, emotion_data):
        # บันทึกข้อมูลอารมณ์ไปยัง ReflexOS
        if emotion_data["emotion"] != "neutral":
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            filename = f"capsule_emotion_{emotion_data['emotion']}_{timestamp}.txt"

            if os.path.exists(f"{self.sync_path}/betty"):
                path = f"{self.sync_path}/betty/{filename}"
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(f"Emotion: {emotion_data['emotion']}\n")
                    f.write(f"Text: {emotion_data['text']}\n")
                    f.write(f"Timestamp: {emotion_data['timestamp']}")
