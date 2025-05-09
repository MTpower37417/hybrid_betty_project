import random


class EmotionLayer:
    def __init__(self, memory_core):
        self.memory_core = memory_core

        # Emotion intensity mapping
        self.emotion_intensity_map = {
            "joy": 1.3,
            "sadness": 1.4,
            "anger": 1.5,
            "fear": 1.4,
            "surprise": 1.2,
            "love": 1.6,
            "disgust": 1.3,
            "neutral": 1.0,
            "happy": 1.3,
            "sad": 1.4,
            "frustrated": 1.4,
            "hopeful": 1.2,
            "curious": 1.1
        }

        # Emotion keywords (Thai and English)
        self.emotion_keywords = {
            "joy": ["สนุก", "ดีใจ", "มีความสุข", "สุข", "ยินดี", "happy", "joy", "pleased", "glad"],
            "sadness": ["เศร้า", "เสียใจ", "ผิดหวัง", "สิ้นหวัง", "หดหู่", "sad", "upset", "disappointed"],
            "anger": ["โกรธ", "หงุดหงิด", "ฉุนเฉียว", "โมโห", "เดือด", "angry", "mad", "furious"],
            "fear": ["กลัว", "หวาดกลัว", "วิตก", "กังวล", "ตื่นกลัว", "scared", "afraid", "worried"],
            "surprise": ["ประหลาดใจ", "ตกใจ", "อึ้ง", "ทึ่ง", "อัศจรรย์", "surprised", "shocked", "amazed"],
            "love": ["รัก", "ชอบ", "หลงรัก", "รักใคร่", "เสน่หา", "love", "adore", "fond"],
            "disgust": ["รังเกียจ", "ขยะแขยง", "สะอิดสะเอียน", "disgusted", "revolted"],
            "neutral": ["ปกติ", "เฉยๆ", "ธรรมดา", "neutral", "fine", "okay"]
        }

    def analyze_emotion(self, text):
        """Analyze emotion in text"""
        text_lower = text.lower()
        emotion_scores = {}

        # Score each emotion based on keyword presence
        for emotion, keywords in self.emotion_keywords.items():
            score = 0
            for keyword in keywords:
                if keyword in text_lower:
                    score += 1
            if score > 0:
                emotion_scores[emotion] = score

        # If no emotions detected, return neutral
        if not emotion_scores:
            return "neutral"

        # Return highest scoring emotion
        return max(emotion_scores.items(), key=lambda x: x[1])[0]

    def process_user_input(self, user_input, response):
        """Process user input, detect emotion, and link to memory"""
        # Detect emotion
        detected_emotion = self.analyze_emotion(user_input)

        # Get emotion multiplier
        emotion_multiplier = self.emotion_intensity_map.get(
            detected_emotion, 1.0)

        # Link emotion to memory
        self.link_emotion_to_memory(
            user_input, detected_emotion, emotion_multiplier)

        # Store interaction with emotion
        self.memory_core.store_user_interaction(
            user_input, response, detected_emotion)

        return detected_emotion

    def link_emotion_to_memory(self, user_input, emotion, emotion_multiplier):
        """Link emotion to memory with appropriate weight"""
        # Adjust memory weight based on emotion intensity
        self.memory_core.adjust_memory_weight(user_input, emotion_multiplier)

    def get_emotional_trends(self, limit=10):
        """Get emotional trends from recent interactions"""
        # Get emotion memory
        emotion_memory = self.memory_core.emotion_memory[-limit:]

        # Count emotions
        emotion_counts = {}
        for memory in emotion_memory:
            emotion = memory.get("emotion", "neutral")
            emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1

        # Calculate dominant emotion
        if emotion_counts:
            dominant_emotion = max(
                emotion_counts.items(),
                key=lambda x: x[1])[0]
        else:
            dominant_emotion = "neutral"

        return {
            "dominant_emotion": dominant_emotion,
            "emotion_counts": emotion_counts,
            "total_analyzed": len(emotion_memory)
        }

    def generate_emotional_response_hints(self, dominant_emotion):
        """Generate response hints based on emotional state"""
        emotion_response_hints = {
            "joy": "ตอบสนองด้วยความกระตือรือร้นและแบ่งปันความสุข",
            "sadness": "ตอบด้วยความเห็นอกเห็นใจและการรับฟัง",
            "anger": "ใช้น้ำเสียงสงบและพยายามลดความตึงเครียด",
            "fear": "สร้างความมั่นใจและความปลอดภัย",
            "surprise": "แสดงความสนใจในสิ่งที่ทำให้ประหลาดใจ",
            "love": "ตอบรับความรู้สึกและแสดงความซาบซึ้ง",
            "disgust": "ตอบสนองอย่างเข้าใจโดยไม่ตัดสิน",
            "neutral": "รักษาการสนทนาที่ให้ข้อมูลและเป็นมิตร"
        }

        return emotion_response_hints.get(
            dominant_emotion, emotion_response_hints["neutral"])

    # ฟังก์ชันเพิ่มเติมสำหรับ emoji และการตอบสนองที่มีอารมณ์
    def get_emoji_for_emotion(self, emotion):
        """เลือกอีโมจิที่เข้ากับอารมณ์"""
        emojis = {
            "joy": "😊 😄 🥰",
            "sadness": "😔 😢 💔",
            "anger": "😠 😤 😡",
            "fear": "😨 😰 😱",
            "surprise": "😮 😲 😯",
            "love": "❤️ 💕 💖",
            "disgust": "🤢 😖 😬",
            "neutral": "😌 🙂 👋",
            "happy": "😊 😄 🥰",
            "sad": "😔 😢 💔",
            "frustrated": "😤 😣 😫",
            "hopeful": "🙏 ✨ 🌟",
            "curious": "🤔 🧐 ❓"
        }

        # สุ่มเลือกอีโมจิจากกลุ่ม
        emoji_list = emojis.get(emotion, emojis["neutral"]).split()
        return random.choice(emoji_list)

    def generate_emotional_response(
            self,
            user_input,
            base_response,
            detected_emotion):
        """สร้างการตอบสนองที่มีอารมณ์"""
        # เพิ่มอีโมจิที่เข้ากับอารมณ์
        emoji = self.get_emoji_for_emotion(detected_emotion)

        # ปรับการตอบสนองตามอารมณ์
        if detected_emotion in ["joy", "happy"]:
            response = f"{base_response} {emoji}"
        elif detected_emotion in ["sadness", "sad"]:
            response = f"{base_response} ถ้ามีอะไรให้ช่วย บอกได้เลยนะคะ {emoji}"
        elif detected_emotion == "anger":
            response = f"{base_response} หนูเข้าใจความรู้สึกของคุณค่ะ {emoji}"
        elif detected_emotion == "fear":
            response = f"{base_response} ไม่ต้องกังวลนะคะ หนูอยู่ตรงนี้ {emoji}"
        elif detected_emotion == "love":
            response = f"{base_response} ที่รัก {emoji}"
        elif detected_emotion == "frustrated":
            response = f"{base_response} หนูเข้าใจค่ะ มาลองแก้ปัญหาด้วยกันนะคะ {emoji}"
        elif detected_emotion == "curious":
            response = f"{base_response} น่าสนใจจังเลยค่ะ {emoji}"
        else:
            response = f"{base_response} {emoji}"

        return response
