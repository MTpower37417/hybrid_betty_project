import json
import os
import re
from datetime import datetime


class EmotionAnalyzer:
    def __init__(self):
        self.emotion_path = "./memory/emotion"
        self.emotion_log = f"{self.emotion_path}/emotion_log.json"
        self.emotion_keywords = self._load_emotion_keywords()
        self.emotion_history = self._load_emotion_history()

    def _load_emotion_keywords(self):
        return {
            "happy": [
                "ดีใจ",
                "สุข",
                "สนุก",
                "ยินดี",
                "ขอบคุณ",
                "เยี่ยม",
                "วิเศษ",
                "ยอดเยี่ยม",
                "😊",
                "😄",
                "❤️"],
            "sad": [
                "เศร้า",
                "เสียใจ",
                "ผิดหวัง",
                "ท้อแท้",
                "ร้องไห้",
                "น่าสงสาร",
                "น้ำตา",
                "😢",
                "😭",
                "💔"],
            "angry": [
                "โกรธ",
                "โมโห",
                "ไม่พอใจ",
                "หงุดหงิด",
                "รำคาญ",
                "เกลียด",
                "น่ารำคาญ",
                "😠",
                "😡",
                "💢"],
            "afraid": [
                "กลัว",
                "วิตก",
                "กังวล",
                "ตกใจ",
                "กระวนกระวาย",
                "ระแวง",
                "หวาดกลัว",
                "😨",
                "😱",
                "😰"],
            "surprised": [
                "ตกใจ",
                "ประหลาดใจ",
                "อึ้ง",
                "ไม่เชื่อ",
                "ทึ่ง",
                "อัศจรรย์",
                "ไม่คาดคิด",
                "😲",
                "😮",
                "😯"]}

    def _load_emotion_history(self):
        if os.path.exists(self.emotion_log):
            try:
                with open(self.emotion_log, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except BaseException:
                return []
        return []

    def analyze_emotion(self, text):
        text = text.lower()
        emotion_scores = {}

        for emotion, keywords in self.emotion_keywords.items():
            score = 0
            for keyword in keywords:
                matches = re.findall(
                    r'\b' +
                    re.escape(
                        keyword.lower()) +
                    r'\b',
                    text)
                score += len(matches)
            emotion_scores[emotion] = score

        max_emotion = max(emotion_scores.items(), key=lambda x: x[1])

        if max_emotion[1] == 0:
            return "neutral"
        return max_emotion[0]

    def log_emotion(self, text, detected_emotion):
        entry = {
            "timestamp": datetime.now().isoformat(),
            "text": text,
            "emotion": detected_emotion
        }

        self.emotion_history.append(entry)

        os.makedirs(self.emotion_path, exist_ok=True)
        with open(self.emotion_log, 'w', encoding='utf-8') as f:
            json.dump(self.emotion_history[-100:],
                      f, indent=2, ensure_ascii=False)

        return detected_emotion
