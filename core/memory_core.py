import hashlib
import json
import os
import re
from datetime import datetime


class MemoryCore:
    def __init__(self, user_id='user_a', memory_base_path='./memory'):
        self.user_id = user_id
        self.memory_base_path = memory_base_path

        # คุณลักษณะความจำแบบมนุษย์
        self.forgetting_curve = True  # ใช้เส้นโค้งการลืมของ Ebbinghaus
        self.emotional_boost = True   # ความจำที่มีอารมณ์จะจำได้ดีกว่า
        self.repetition_boost = True  # จำได้ดีขึ้นเมื่อมีการพูดซ้ำ

        # เส้นทางสำหรับความจำประเภทต่างๆ
        self.shortterm_path = f"{memory_base_path}/stack"
        self.working_path = f"{memory_base_path}/working"  # เพิ่มความจำทำงาน
        self.longterm_path = f"{memory_base_path}/longterm"
        self.emotion_path = f"{memory_base_path}/emotion"
        self.episodic_path = f"{memory_base_path}/episodic"  # ความจำเหตุการณ์

        # สร้างโฟลเดอร์ที่จำเป็น
        self._ensure_directories()

        # โหลดความจำที่มีอยู่แล้ว
        self.shortterm_memory = self._load_memory_file(
            f"{self.shortterm_path}/{self.user_id}_stack.json")
        self.working_memory = self._load_memory_file(
            f"{self.working_path}/{self.user_id}_working.json")
        self.longterm_memory = self._load_memory_file(
            f"{self.longterm_path}/{self.user_id}_2025.json")
        self.emotion_memory = self._load_memory_file(
            f"{self.emotion_path}/{self.user_id}_emotion.json")
        self.episodic_memory = self._load_memory_file(
            f"{self.episodic_path}/{self.user_id}_episodic.json")

        # แคชสำหรับการค้นหาที่รวดเร็ว
        self.memory_cache = {}
        self.last_cache_refresh = datetime.now()

        # เกณฑ์ความสำคัญในการย้ายระหว่างความจำ
        self.thresholds = {
            'short_to_working': 0.4,  # ระยะสั้น -> ระยะทำงาน
            'working_to_long': 0.7,   # ระยะทำงาน -> ระยะยาว
            'emotion_boost': 0.2,     # เพิ่มเมื่อมีอารมณ์
            'repetition_boost': 0.1   # เพิ่มเมื่อมีการพูดซ้ำ
        }

    def _ensure_directories(self):
        """สร้างโฟลเดอร์ทั้งหมดที่จำเป็น"""
        for path in [
                self.shortterm_path,
                self.working_path,
                self.longterm_path,
                self.emotion_path,
                self.episodic_path]:
            os.makedirs(path, exist_ok=True)

    def _load_memory_file(self, filepath):
        """อ่านไฟล์ความจำ"""
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
            context=None):
        """บันทึกการโต้ตอบระหว่างผู้ใช้และ AI"""
        timestamp = datetime.now().isoformat()

        # สร้างรายการความจำพื้นฐาน
        memory_entry = {
            "timestamp": timestamp,
            "user_id": self.user_id,
            "message": message,
            "response": response,
            "emotion": emotion,
            "importance": 0.5,  # ค่าเริ่มต้น
            "recall_count": 0,  # จำนวนครั้งที่ถูกเรียกใช้
            "last_accessed": timestamp
        }

        # เพิ่มบริบทถ้ามี
        if context:
            memory_entry["context"] = context

        # ประเมินความสำคัญ
        importance = self._evaluate_importance(message, emotion)
        memory_entry["importance"] = importance

        # บันทึกลงความจำระยะสั้นเสมอ
        self._store_memory(self.shortterm_memory, memory_entry, 20,
                           f"{self.shortterm_path}/{self.user_id}_stack.json")

        # บันทึกความจำอารมณ์
        self._store_emotion(message, response, emotion, importance)

        # ตรวจสอบการย้ายไปความจำอื่น
        if importance >= self.thresholds['short_to_working']:
            self._store_memory(
                self.working_memory,
                memory_entry,
                50,
                f"{self.working_path}/{self.user_id}_working.json",
                True)

            # ถ้าสำคัญมากพอ บันทึกลงความจำระยะยาว
            if importance >= self.thresholds['working_to_long']:
                self._store_memory(
                    self.longterm_memory,
                    memory_entry,
                    None,
                    f"{self.longterm_path}/{self.user_id}_2025.json",
                    True)

                # ตรวจสอบว่าเป็นความจำเชิงเหตุการณ์หรือไม่
                if self._is_episodic(message):
                    # เพิ่มแท็กเวลา
                    memory_with_time = memory_entry.copy()
                    memory_with_time["time_tags"] = self._extract_time_references(
                        message)
                    self._store_memory(
                        self.episodic_memory,
                        memory_with_time,
                        None,
                        f"{self.episodic_path}/{self.user_id}_episodic.json",
                        True)

        # ล้างแคช
        self.memory_cache = {}

        return importance

    def _store_memory(
            self,
            memory_list,
            memory_entry,
            max_size,
            filepath,
            check_duplicate=False):
        """บันทึกความจำและจัดการเกี่ยวกับขนาด"""
        # ตรวจสอบซ้ำถ้าต้องการ
        if check_duplicate:
            for i, memory in enumerate(memory_list):
                if memory.get("message") == memory_entry.get("message"):
                    # อัปเดตความจำที่มีอยู่แล้ว
                    memory_list[i]["importance"] = max(
                        memory.get(
                            "importance", 0), memory_entry.get(
                            "importance", 0))
                    memory_list[i]["last_accessed"] = memory_entry.get(
                        "timestamp")
                    memory_list[i]["recall_count"] = memory.get(
                        "recall_count", 0) + 1

                    # บันทึกไฟล์
                    with open(filepath, 'w', encoding='utf-8') as f:
                        json.dump(memory_list, f, indent=2, ensure_ascii=False)
                    return

        # เพิ่มความจำใหม่
        memory_list.append(memory_entry)

        # จำกัดขนาดถ้าจำเป็น
        if max_size and len(memory_list) > max_size:
            # จัดลำดับตามความสำคัญก่อนตัด
            memory_list.sort(
                key=lambda x: x.get(
                    "importance", 0), reverse=True)
            memory_list = memory_list[:max_size]

        # บันทึกไฟล์
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(memory_list, f, indent=2, ensure_ascii=False)

    def _store_emotion(self, message, response, emotion, importance):
        """บันทึกความจำอารมณ์"""
        emotion_entry = {
            "timestamp": datetime.now().isoformat(),
            "message": message,
            "response": response,
            "emotion": emotion,
            "importance": importance
        }

        self.emotion_memory.append(emotion_entry)

        # จำกัดขนาดไม่เกิน 100 รายการ
        if len(self.emotion_memory) > 100:
            self.emotion_memory.pop(0)

        # บันทึกไฟล์
        filepath = f"{self.emotion_path}/{self.user_id}_emotion.json"
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.emotion_memory, f, indent=2, ensure_ascii=False)

    def _evaluate_importance(self, message, emotion):
        """ประเมินความสำคัญของความจำ"""
        base_importance = 0.5  # ค่าเริ่มต้น

        # ตรวจสอบคำสำคัญ
        important_keywords = [
            # ไทย
            "จำ", "จดจำ", "อย่าลืม", "สำคัญ", "ชื่อ", "วันเกิด", "เบอร์", "ชอบ", "รัก",
            "ไม่ชอบ", "ต้องการ", "อยาก", "เสมอ", "ประจำ", "พิเศษ", "เท่านั้น",
            # อังกฤษ
            "remember", "important", "birthday", "name", "contact", "like", "love",
            "hate", "need", "want", "always", "special", "only"
        ]

        for keyword in important_keywords:
            if keyword in message.lower():
                base_importance += 0.05  # เพิ่มความสำคัญต่อคำสำคัญ

        # ตรวจสอบความยาวข้อความ
        if len(message) > 100:
            base_importance += 0.1  # ข้อความยาวอาจมีความสำคัญมากขึ้น

        # ตรวจสอบอารมณ์
        if self.emotional_boost:
            emotion_boost = {
                "joy": 1.1, "sadness": 1.2, "anger": 1.3, "fear": 1.2,
                "surprise": 1.1, "love": 1.4, "neutral": 1.0
            }
            base_importance *= emotion_boost.get(emotion, 1.0)

        # ตรวจสอบการซ้ำ
        if self.repetition_boost and self._has_similar_memory(message):
            base_importance += self.thresholds['repetition_boost']

        # จำกัดไม่เกิน 1.0
        return min(1.0, base_importance)

    def _has_similar_memory(self, message):
        """ตรวจสอบว่ามีความจำที่คล้ายกันหรือไม่"""
        message_words = set(message.lower().split())

        # ตรวจสอบในความจำระยะทำงาน
        for memory in self.working_memory:
            if "message" not in memory:
                continue

            memory_words = set(memory["message"].lower().split())
            common_words = message_words.intersection(memory_words)

            # ถ้ามีคำที่เหมือนกันมากกว่า 60% ถือว่าคล้ายกัน
            similarity = len(common_words) / max(len(message_words), 1)
            if similarity > 0.6:
                return True

        return False

    def _is_episodic(self, message):
        """ตรวจสอบว่าเป็นความจำเชิงเหตุการณ์หรือไม่"""
        # คำที่บ่งบอกเหตุการณ์
        event_indicators = [
            # ไทย
            "เมื่อ", "ตอน", "วัน", "สัปดาห์", "เดือน", "ปี", "ครั้ง", "เวลา",
            # อังกฤษ
            "when", "during", "day", "week", "month", "year", "time", "moment"
        ]

        for indicator in event_indicators:
            if indicator in message.lower():
                return True

        return False

    def _extract_time_references(self, text):
        """แยกการอ้างอิงเวลาจากข้อความ"""
        time_patterns = [
            # ไทย
            r'วันนี้', r'พรุ่งนี้', r'เมื่อวาน', r'สัปดาห์ที่แล้ว', r'สัปดาห์หน้า',
            r'เดือนที่แล้ว', r'เดือนหน้า', r'ปีที่แล้ว', r'ปีหน้า',
            r'วัน(จันทร์|อังคาร|พุธ|พฤหัสบดี|ศุกร์|เสาร์|อาทิตย์)',
            # อังกฤษ
            r'today', r'tomorrow', r'yesterday', r'last week', r'next week',
            r'last month', r'next month', r'last year', r'next year',
            r'(monday|tuesday|wednesday|thursday|friday|saturday|sunday)'
        ]

        time_refs = []
        for pattern in time_patterns:
            matches = re.findall(pattern, text.lower())
            if matches:
                if isinstance(matches[0], tuple):  # Handling groups in regex
                    time_refs.extend([''.join(m) for m in matches])
                else:
                    time_refs.extend(matches)

        return time_refs

    def recall_memories(self, query, limit=5, memory_types=None):
        """เรียกคืนความจำที่เกี่ยวข้องกับคำถาม"""
        if memory_types is None:
            memory_types = ["shortterm", "working", "longterm", "episodic"]

        # สร้าง cache key
        cache_key = hashlib.md5(
            f"{query}-{','.join(memory_types)}".encode()).hexdigest()

        # ตรวจสอบแคช
        if cache_key in self.memory_cache:
            return self.memory_cache[cache_key]

        # รวมความจำจากแหล่งต่างๆ
        all_memories = []

        if "shortterm" in memory_types:
            all_memories.extend(self.shortterm_memory)
        if "working" in memory_types:
            all_memories.extend(self.working_memory)
        if "longterm" in memory_types:
            all_memories.extend(self.longterm_memory)
        if "episodic" in memory_types:
            all_memories.extend(self.episodic_memory)

        # คำนวณความเกี่ยวข้อง
        query_words = set(query.lower().split())
        relevant_memories = []

        for memory in all_memories:
            if not isinstance(memory, dict) or "message" not in memory:
                continue

            # คำนวณความคล้ายคลึงพื้นฐาน
            memory_text = memory["message"].lower()
            memory_words = set(memory_text.split())

            # คำนวณคำที่ตรงกัน
            common_words = query_words.intersection(memory_words)
            base_relevance = len(common_words) / max(len(query_words), 1)

            # ไม่สนใจความจำที่ไม่เกี่ยวข้องเลย
            if base_relevance == 0:
                continue

            # คำนวณคะแนนความเกี่ยวข้องสุดท้าย
            final_relevance = base_relevance

            # ปรับตามความสำคัญ
            if "importance" in memory:
                final_relevance *= (1 + memory["importance"])

            # ปรับตามความใหม่
            if "timestamp" in memory:
                try:
                    memory_time = datetime.fromisoformat(memory["timestamp"])
                    time_diff = (datetime.now() - memory_time).days

                    # ความจำใหม่สำคัญกว่า
                    if time_diff < 1:  # ภายใน 1 วัน
                        final_relevance *= 1.5
                    elif time_diff < 7:  # ภายใน 1 สัปดาห์
                        final_relevance *= 1.3
                    elif time_diff < 30:  # ภายใน 1 เดือน
                        final_relevance *= 1.1
                except BaseException:
                    pass

            # เพิ่มจำนวนครั้งที่ถูกเรียกคืน
            if "recall_count" in memory:
                recall_boost = min(
                    memory["recall_count"] * 0.05,
                    0.5)  # สูงสุด +0.5
                final_relevance *= (1 + recall_boost)

            relevant_memories.append((final_relevance, memory))

        # เรียงลำดับตามความเกี่ยวข้อง
        relevant_memories.sort(reverse=True, key=lambda x: x[0])

        # เพิ่มจำนวนครั้งที่ถูกเรียกคืนและอัปเดตเวลาเข้าถึงล่าสุด
        results = []
        for _, memory in relevant_memories[:limit]:
            # เพิ่มจำนวนการเรียกคืน
            memory["recall_count"] = memory.get("recall_count", 0) + 1
            memory["last_accessed"] = datetime.now().isoformat()

            # สำหรับความจำที่อยู่ในระยะทำงาน ต้องอัปเดตไฟล์
            self._update_memory_access(memory)

            results.append(memory)

        # บันทึกในแคช
        self.memory_cache[cache_key] = results
        self.last_cache_refresh = datetime.now()

        return results

    def _update_memory_access(self, memory):
        """อัปเดตข้อมูลการเข้าถึงความจำ"""
        # อัปเดตในความจำระยะทำงาน
        for memory_list, filepath in [
            (self.working_memory, f"{self.working_path}/{self.user_id}_working.json"),
            (self.longterm_memory, f"{self.longterm_path}/{self.user_id}_2025.json"),
            (self.episodic_memory, f"{self.episodic_path}/{self.user_id}_episodic.json")
        ]:
            updated = False
            for i, m in enumerate(memory_list):
                if m.get("message") == memory.get("message"):
                    memory_list[i]["recall_count"] = memory["recall_count"]
                    memory_list[i]["last_accessed"] = memory["last_accessed"]
                    updated = True
                    break

            if updated:
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(memory_list, f, indent=2, ensure_ascii=False)
