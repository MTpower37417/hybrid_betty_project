import hashlib
import json
import os
from datetime import datetime


class BettyMemory:
    def __init__(self, user_id="user_a"):
        """
        เริ่มต้นระบบความจำของ Betty

        Parameters:
            user_id (str): ID ของผู้ใช้
        """
        self.user_id = user_id
        self.memory_path = "./memory"

        # กำหนดพาธสำหรับไฟล์ความจำแต่ละประเภท
        self.shortterm_path = f"{self.memory_path}/stack"
        self.longterm_path = f"{self.memory_path}/longterm"
        self.emotion_path = f"{self.memory_path}/emotion"
        self.capsule_path = f"{self.memory_path}/capsule"
        self.extended_path = f"{self.memory_path}/extended"

        # สร้างโฟลเดอร์ถ้ายังไม่มี
        self._ensure_directories()

        # โหลดความจำที่มีอยู่
        self.shortterm_memory = self._load_shortterm_memory()
        self.emotion_memory = self._load_emotion_memory()

        # แคชสำหรับการค้นหาความจำ
        self.memory_cache = {}
        self.last_cache_refresh = datetime.now()

    def _ensure_directories(self):
        """สร้างโฟลเดอร์ทั้งหมดที่จำเป็น"""
        for path in [
                self.shortterm_path,
                self.longterm_path,
                self.emotion_path,
                self.extended_path,
                self.capsule_path]:
            os.makedirs(path, exist_ok=True)

    def _load_shortterm_memory(self):
        """โหลดความจำระยะสั้นจากไฟล์"""
        filepath = f"{self.shortterm_path}/{self.user_id}_stack.json"
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except BaseException:
                return []
        return []

    def _load_emotion_memory(self):
        """โหลดความจำอารมณ์จากไฟล์"""
        filepath = f"{self.emotion_path}/{self.user_id}_emotion.json"
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except BaseException:
                return []
        return []

    def store_interaction(
            self,
            message,
            response,
            emotion="neutral",
            importance=0.5):
        """
        บันทึกการสนทนาลงในระบบความจำ

        Parameters:
            message (str): ข้อความจากผู้ใช้
            response (str): การตอบกลับของ Betty
            emotion (str): อารมณ์ในขณะสนทนา
            importance (float): ความสำคัญของความจำ (0.0-1.0)
        """
        timestamp = datetime.now().isoformat()

        # บันทึกลงในความจำระยะสั้น
        shortterm_entry = {
            "timestamp": timestamp,
            "user": self.user_id,
            "message": message,
            "response": response,
            "emotion": emotion
        }

        self.shortterm_memory.append(shortterm_entry)

        # บันทึกลงไฟล์ (เก็บแค่ 20 รายการล่าสุด)
        self._save_shortterm_memory()

        # บันทึกอารมณ์
        self._store_emotion(message, response, emotion)

        # ถ้าสำคัญมาก ให้บันทึกเป็น capsule
        if importance >= 0.8:
            self._store_capsule(message, response, emotion, importance)

        # ล้างแคช
        self.memory_cache = {}

    def _save_shortterm_memory(self):
        """บันทึกความจำระยะสั้นลงไฟล์"""
        filepath = f"{self.shortterm_path}/{self.user_id}_stack.json"
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.shortterm_memory[-20:],
                      f, indent=2, ensure_ascii=False)

    def _store_emotion(self, message, response, emotion):
        """บันทึกอารมณ์ลงในความจำอารมณ์"""
        timestamp = datetime.now().isoformat()

        emotion_entry = {
            "timestamp": timestamp,
            "message": message,
            "response": response,
            "emotion": emotion
        }

        self.emotion_memory.append(emotion_entry)

        # บันทึกลงไฟล์ (เก็บแค่ 50 รายการล่าสุด)
        filepath = f"{self.emotion_path}/{self.user_id}_emotion.json"
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.emotion_memory[-50:],
                      f, indent=2, ensure_ascii=False)

    def _store_capsule(self, message, response, emotion, importance):
        """บันทึกความจำสำคัญเป็น capsule"""
        timestamp = datetime.now().isoformat()
        formatted_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

        # สร้าง tags อัตโนมัติ
        tags = [emotion]
        if "ชอบ" in message or "รัก" in message:
            tags.append("ความชอบ")
        if "เงิน" in message or "ธนาคาร" in message:
            tags.append("การเงิน")

        # สร้าง capsule
        capsule_data = {
            "timestamp": timestamp,
            "user": self.user_id,
            "message": message,
            "response": response,
            "emotion": emotion,
            "importance": importance,
            "tags": tags
        }

        # บันทึกเป็นไฟล์ JSON
        json_filepath = f"{self.capsule_path}/capsule_{formatted_time}.json"
        with open(json_filepath, 'w', encoding='utf-8') as f:
            json.dump(capsule_data, f, indent=2, ensure_ascii=False)

    def get_recent_memories(self, limit=5):
        """
        ดึงความจำล่าสุด

        Parameters:
            limit (int): จำนวนความจำที่ต้องการ

        Returns:
            list: รายการความจำล่าสุด
        """
        return self.shortterm_memory[-limit:] if len(
            self.shortterm_memory) >= limit else self.shortterm_memory

    def get_relevant_memories(self, query, limit=3):
        """
        ค้นหาความจำที่เกี่ยวข้องกับคำถาม

        Parameters:
            query (str): คำถามที่ต้องการค้นหาความจำที่เกี่ยวข้อง
            limit (int): จำนวนความจำที่ต้องการ

        Returns:
            list: รายการความจำที่เกี่ยวข้อง
        """
        # สร้าง key สำหรับแคช
        cache_key = hashlib.md5(query.encode()).hexdigest()

        # ถ้ามีในแคชแล้ว ให้ใช้จากแคช
        if cache_key in self.memory_cache:
            return self.memory_cache[cache_key]

        # แยกคำสำคัญจากคำถาม
        query_words = set(query.lower().split())

        # คำนวณความเกี่ยวข้องของแต่ละความจำ
        scored_memories = []

        for memory in self.shortterm_memory:
            if not isinstance(memory, dict) or "message" not in memory:
                continue

            memory_text = memory["message"].lower()
            memory_words = set(memory_text.split())

            # คำนวณความซ้อนทับของคำ
            common_words = query_words.intersection(memory_words)
            relevance = len(common_words) / max(len(query_words), 1)

            # ถ้ามีความเกี่ยวข้อง ให้เพิ่มเข้าไปในรายการ
            if relevance > 0:
                scored_memories.append((relevance, memory))

        # เรียงลำดับตามความเกี่ยวข้อง
        scored_memories.sort(reverse=True, key=lambda x: x[0])

        # เลือกเฉพาะความจำที่เกี่ยวข้องมากที่สุด
        relevant_memories = [memory for score,
                             memory in scored_memories[:limit]]

        # บันทึกลงแคช
        self.memory_cache[cache_key] = relevant_memories

        return relevant_memories

    def get_emotion_trend(self, limit=5):
        """
        วิเคราะห์แนวโน้มอารมณ์ล่าสุด

        Parameters:
            limit (int): จำนวนรายการอารมณ์ที่ต้องการวิเคราะห์

        Returns:
            dict: ข้อมูลแนวโน้มอารมณ์
        """
        recent_emotions = self.emotion_memory[-limit:] if len(
            self.emotion_memory) >= limit else self.emotion_memory

        # นับความถี่ของแต่ละอารมณ์
        emotion_counts = {}
        for entry in recent_emotions:
            emotion = entry.get("emotion", "neutral")
            emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1

        # หาอารมณ์หลัก
        dominant_emotion = "neutral"
        if emotion_counts:
            dominant_emotion = max(
                emotion_counts.items(),
                key=lambda x: x[1])[0]

        return {
            "dominant_emotion": dominant_emotion,
            "emotion_counts": emotion_counts,
            "recent_emotions": [
                entry.get("emotion") for entry in recent_emotions]}
