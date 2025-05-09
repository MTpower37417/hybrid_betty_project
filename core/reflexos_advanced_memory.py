# reflexos_advanced_memory.py
import hashlib
import json
import os
from datetime import datetime


class AdvancedMemorySystem:
    def __init__(self, user_id='user_a', base_path='./memory'):
        self.user_id = user_id
        self.base_path = base_path
        self.memory_paths = {
            'shortterm': f"{base_path}/stack",
            'longterm': f"{base_path}/longterm",
            'emotion': f"{base_path}/emotion",
            'extended': f"{base_path}/extended",
            'capsule': f"{base_path}/capsule",
            'timeline': f"{base_path}/timeline",
            'journal': f"{base_path}/journal"
        }

        # สร้างโฟลเดอร์ที่จำเป็น
        self._create_directories()

        # โหลดข้อมูลความจำ
        self.memories = self._load_memories()

        # ตั้งค่าค่าความสำคัญเริ่มต้น
        self.memory_thresholds = {
            'emotion': 0.7,   # อารมณ์มีความสำคัญสูง
            'identity': 0.9,  # ข้อมูลเกี่ยวกับตัวตนมีความสำคัญสูงสุด
            'preference': 0.8,  # ความชอบมีความสำคัญสูง
            'factual': 0.6,     # ข้อมูลทั่วไปมีความสำคัญปานกลาง
            'general': 0.5      # ข้อความทั่วไปมีความสำคัญต่ำ
        }

        # เก็บแคช
        self.memory_cache = {}
        self.last_cache_refresh = datetime.now()

    def _create_directories(self):
        """สร้างโฟลเดอร์ที่จำเป็นทั้งหมด"""
        for path in self.memory_paths.values():
            os.makedirs(path, exist_ok=True)

    def _load_memories(self):
        """โหลดข้อมูลความจำทั้งหมด"""
        memories = {}

        # โหลดความจำระยะสั้น
        shortterm_path = f"{self.memory_paths['shortterm']}/{self.user_id}_stack.json"
        if os.path.exists(shortterm_path):
            try:
                with open(shortterm_path, 'r', encoding='utf-8') as f:
                    memories['shortterm'] = json.load(f)
            except BaseException:
                memories['shortterm'] = []
        else:
            memories['shortterm'] = []

        # โหลดความจำระยะยาว
        longterm_path = f"{self.memory_paths['longterm']}/{self.user_id}_2025.json"
        if os.path.exists(longterm_path):
            try:
                with open(longterm_path, 'r', encoding='utf-8') as f:
                    memories['longterm'] = json.load(f)
            except BaseException:
                memories['longterm'] = []
        else:
            memories['longterm'] = []

        # โหลดความจำอารมณ์
        emotion_path = f"{self.memory_paths['emotion']}/{self.user_id}_emotion.json"
        if os.path.exists(emotion_path):
            try:
                with open(emotion_path, 'r', encoding='utf-8') as f:
                    memories['emotion'] = json.load(f)
            except BaseException:
                memories['emotion'] = []
        else:
            memories['emotion'] = []

        # โหลดข้อมูล capsule (ถ้ามี)
        capsule_path = f"{self.memory_paths['capsule']}/{self.user_id}_capsule.json"
        if os.path.exists(capsule_path):
            try:
                with open(capsule_path, 'r', encoding='utf-8') as f:
                    memories['capsule'] = json.load(f)
            except BaseException:
                memories['capsule'] = []
        else:
            memories['capsule'] = []

        return memories

    def store_memory(
            self,
            message,
            response,
            emotion="neutral",
            memory_type="general",
            context=None):
        """เก็บความจำใหม่ในระบบ"""
        timestamp = datetime.now().isoformat()

        # สร้างรายการความจำพื้นฐาน
        memory_entry = {
            "timestamp": timestamp,
            "user": self.user_id,
            "message": message,
            "response": response,
            "emotion": emotion,
            "type": memory_type
        }

        # เพิ่มบริบทถ้ามี
        if context:
            memory_entry["context"] = context

        # เก็บในความจำระยะสั้นเสมอ
        self.memories['shortterm'].append(memory_entry)

        # บันทึกไฟล์ความจำระยะสั้น (เก็บแค่ 30 รายการล่าสุด)
        with open(f"{self.memory_paths['shortterm']}/{self.user_id}_stack.json", 'w', encoding='utf-8') as f:
            json.dump(self.memories['shortterm'][-30:],
                      f, indent=2, ensure_ascii=False)

        # เก็บข้อมูลอารมณ์
        emotion_entry = {
            "time": timestamp,
            "message": message,
            "response": response,
            "emotion": emotion
        }
        self.memories['emotion'].append(emotion_entry)

        # บันทึกไฟล์อารมณ์ (เก็บแค่ 50 รายการล่าสุด)
        with open(f"{self.memory_paths['emotion']}/{self.user_id}_emotion.json", 'w', encoding='utf-8') as f:
            json.dump(self.memories['emotion'][-50:],
                      f, indent=2, ensure_ascii=False)

        # ตรวจสอบความสำคัญของความจำ
        importance = self._calculate_memory_importance(
            message, memory_type, emotion)

        # ถ้าความจำสำคัญพอ เก็บในความจำระยะยาว
        if importance >= self.memory_thresholds[memory_type]:
            self.memories['longterm'].append(memory_entry)

            # บันทึกไฟล์ความจำระยะยาว
            with open(f"{self.memory_paths['longterm']}/{self.user_id}_2025.json", 'w', encoding='utf-8') as f:
                json.dump(self.memories['longterm'], f,
                          indent=2, ensure_ascii=False)

        # ถ้าความจำสำคัญมาก เก็บใน capsule
        if importance > 0.8:
            # เพิ่มความสำคัญลงในรายการ
            memory_entry["importance"] = importance

            # เพิ่มแท็กโดยอัตโนมัติ
            memory_entry["tags"] = self._auto_tag(
                message, emotion, memory_type)

            # เก็บใน capsule
            if 'capsule' not in self.memories:
                self.memories['capsule'] = []

            self.memories['capsule'].append(memory_entry)

            # บันทึกไฟล์ capsule
            with open(f"{self.memory_paths['capsule']}/{self.user_id}_capsule.json", 'w', encoding='utf-8') as f:
                json.dump(
                    self.memories['capsule'],
                    f,
                    indent=2,
                    ensure_ascii=False)

            # สร้าง capsule file แบบ text สำหรับการเรียกใช้ง่าย
            self._create_capsule_file(memory_entry)

        # ล้างแคช
        self.memory_cache = {}

        return {
            "stored": True,
            "importance": importance,
            "long_term": importance >= self.memory_thresholds[memory_type],
            "capsule": importance > 0.8
        }

    def _calculate_memory_importance(self, message, memory_type, emotion):
        """คำนวณความสำคัญของความจำ"""
        base_importance = 0.5  # ความสำคัญพื้นฐาน

        # ปรับตามประเภทของความจำ
        type_boost = {
            'emotion': 0.2,
            'identity': 0.3,
            'preference': 0.2,
            'factual': 0.1,
            'general': 0.0
        }

        base_importance += type_boost.get(memory_type, 0.0)

        # ปรับตามอารมณ์
        emotion_boost = {
            'joy': 0.1,
            'sadness': 0.15,
            'anger': 0.2,
            'fear': 0.2,
            'surprise': 0.1,
            'love': 0.25,
            'neutral': 0.0
        }

        base_importance += emotion_boost.get(emotion, 0.0)

        # ตรวจสอบคำสำคัญในข้อความ
        important_keywords = [
            # ไทย
            "จำ", "จดจำ", "อย่าลืม", "สำคัญ", "ชื่อ", "วันเกิด", "เบอร์", "ชอบ", "รัก", "ไม่ชอบ",
            "ต้องการ", "อยาก", "ฉัน", "คุณ", "เรา", "หวัง", "ความฝัน", "ปัญหา", "แก้ไข",
            # อังกฤษ
            "remember", "important", "birthday", "name", "contact", "like", "love", "hate",
            "need", "want", "I", "you", "we", "hope", "dream", "problem", "fix"
        ]

        for keyword in important_keywords:
            if keyword in message.lower():
                base_importance += 0.05  # เพิ่มความสำคัญสำหรับแต่ละคำสำคัญที่พบ

        # ปรับตามความยาวของข้อความ
        if len(message) > 100:
            base_importance += 0.1  # ข้อความยาวอาจมีความสำคัญมากขึ้น

        # ตัดให้อยู่ในช่วง 0-1
        return min(1.0, base_importance)

    def _auto_tag(self, message, emotion, memory_type):
        """สร้างแท็กอัตโนมัติสำหรับความจำ"""
        tags = [memory_type, emotion]  # เพิ่มประเภทและอารมณ์เป็นแท็กพื้นฐาน

        # แท็กตามเนื้อหา
        content_tags = {
            "ความชอบ": [
                "ชอบ",
                "รัก",
                "ชื่นชอบ",
                "โปรด",
                "like",
                "love",
                "favorite"],
            "การเงิน": [
                "เงิน",
                "บาท",
                "ธนาคาร",
                "เดบิต",
                "เครดิต",
                "ค่าใช้จ่าย",
                "money",
                "bank",
                "cost"],
            "การทำงาน": [
                "งาน",
                "ออฟฟิศ",
                "บริษัท",
                "โปรเจค",
                "work",
                "office",
                "project"],
            "ความสัมพันธ์": [
                "แฟน",
                "เพื่อน",
                "ครอบครัว",
                "พ่อ",
                "แม่",
                "พี่",
                "น้อง",
                "relationship",
                "friend",
                "family"],
            "การศึกษา": [
                "เรียน",
                "มหาวิทยาลัย",
                "โรงเรียน",
                "คอร์ส",
                "วิชา",
                "study",
                "university",
                "school",
                "course"],
            "สุขภาพ": [
                "ป่วย",
                "หมอ",
                "ยา",
                "โรงพยาบาล",
                "เจ็บ",
                "sick",
                "doctor",
                "medicine",
                "hospital",
                "pain"]}

        for tag, keywords in content_tags.items():
            for keyword in keywords:
                if keyword in message.lower():
                    tags.append(tag)
                    break

        # ลบแท็กซ้ำ
        return list(set(tags))

    def _create_capsule_file(self, memory_entry):
        """สร้างไฟล์ capsule แบบ text"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        emotion = memory_entry.get("emotion", "neutral")
        capsule_dir = self.memory_paths['capsule']

        # สร้างชื่อไฟล์
        filename = f"{capsule_dir}/capsule_emotion_{emotion}_{timestamp}.txt"

        # สร้างเนื้อหา
        content = f"MEMORY CAPSULE - {timestamp}\n"
        content += f"Emotion: {emotion}\n"
        content += f"Type: {memory_entry.get('type', 'general')}\n"
        content += f"Importance: {memory_entry.get('importance', 0.5)}\n"
        content += f"Tags: {', '.join(memory_entry.get('tags', []))}\n"
        content += f"\nUser: {memory_entry.get('message', '')}\n"
        content += f"\nResponse: {memory_entry.get('response', '')}\n"

        if 'context' in memory_entry:
            content += f"\nContext:\n{memory_entry['context']}\n"

        # บันทึกไฟล์
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)

    def search_memories(
            self,
            query,
            limit=5,
            memory_types=None,
            emotions=None):
        """ค้นหาความจำที่เกี่ยวข้อง"""
        if not memory_types:
            memory_types = ['shortterm', 'longterm', 'capsule']

        # สร้าง key สำหรับแคช
        cache_key = f"{query}_{'-'.join(memory_types)}_{'-'.join(emotions) if emotions else 'all'}"
        cache_key = hashlib.md5(cache_key.encode()).hexdigest()

        # ตรวจสอบแคช
        if cache_key in self.memory_cache:
            return self.memory_cache[cache_key]

        # รวมความจำจากทุกแหล่ง
        all_memories = []
        for memory_type in memory_types:
            if memory_type in self.memories:
                for memory in self.memories[memory_type]:
                    # กรองตามอารมณ์ (ถ้ามีการระบุ)
                    if emotions and memory.get('emotion') not in emotions:
                        continue
                    all_memories.append(memory)

        # คำนวณความเกี่ยวข้อง
        relevant_memories = []
        query_terms = set(query.lower().split())

        for memory in all_memories:
            if 'message' not in memory:
                continue

            message = memory['message'].lower()
            message_terms = set(message.split())

            # ความเกี่ยวข้องตามคำที่ตรงกัน
            common_terms = query_terms.intersection(message_terms)
            relevance = len(common_terms) / max(len(query_terms), 1)

            # ปรับความเกี่ยวข้องตามความสำคัญ
            if 'importance' in memory:
                relevance *= (1 + memory['importance'])

            # ปรับความเกี่ยวข้องตามความใหม่
            if memory in self.memories.get('shortterm', []):
                relevance *= 1.3  # ข้อความใหม่มีความสำคัญมากกว่า

            relevant_memories.append((relevance, memory))

        # เรียงลำดับตามความเกี่ยวข้อง
        relevant_memories.sort(reverse=True, key=lambda x: x[0])

        # เก็บในแคช
        result = [memory for _, memory in relevant_memories[:limit]]
        self.memory_cache[cache_key] = result

        return result

    def create_memory_journal(self, time_period="day"):
        """สร้างบันทึกความจำประจำวัน/สัปดาห์/เดือน"""
        now = datetime.now()

        # กำหนดชื่อไฟล์
        if time_period == "day":
            filename = f"journal_{now.strftime('%Y%m%d')}.txt"
            title = f"บันทึกประจำวันที่ {now.strftime('%d/%m/%Y')}"
            # กรองความจำ 24 ชั่วโมงล่าสุด
            cutoff = now.replace(hour=0, minute=0, second=0, microsecond=0)
        elif time_period == "week":
            filename = f"weekly_journal_{now.strftime('%Y%m%d')}.txt"
            title = f"บันทึกประจำสัปดาห์ สิ้นสุดวันที่ {now.strftime('%d/%m/%Y')}"
            # กรองความจำสัปดาห์ล่าสุด
            cutoff = now.replace(hour=0, minute=0, second=0, microsecond=0)
            cutoff = cutoff.replace(day=cutoff.day - cutoff.weekday())
        else:  # month
            filename = f"monthly_journal_{now.strftime('%Y%m')}.txt"
            title = f"บันทึกประจำเดือน {now.strftime('%m/%Y')}"
            # กรองความจำเดือนล่าสุด
            cutoff = now.replace(
                day=1,
                hour=0,
                minute=0,
                second=0,
                microsecond=0)

        # รวมความจำที่สำคัญในช่วงเวลา
        important_memories = []
        for memory in self.memories.get('longterm', []):
            try:
                memory_time = datetime.fromisoformat(
                    memory.get('timestamp', ''))
                if memory_time >= cutoff:
                    important_memories.append(memory)
            except BaseException:
                continue

        # เพิ่มข้อมูล capsule
        for memory in self.memories.get('capsule', []):
            try:
                memory_time = datetime.fromisoformat(
                    memory.get('timestamp', ''))
                if memory_time >= cutoff and memory not in important_memories:
                    important_memories.append(memory)
            except BaseException:
                continue

        # เรียงลำดับตามเวลา
        important_memories.sort(key=lambda x: x.get('timestamp', ''))

        # สร้างเนื้อหาบันทึก
        content = f"{title}\n{'=' * len(title)}\n\n"

        # วิเคราะห์อารมณ์โดยรวม
        emotions = [m.get('emotion', 'neutral') for m in important_memories]
        emotion_counts = {}
        for emotion in emotions:
            emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1

        if emotion_counts:
            dominant_emotion = max(
                emotion_counts.items(),
                key=lambda x: x[1])[0]
            content += f"อารมณ์โดยรวม: {dominant_emotion}\n\n"

        # เขียนความจำที่สำคัญ
        if important_memories:
            content += "ความจำที่สำคัญ:\n"
            for i, memory in enumerate(important_memories, 1):
                memory_time = datetime.fromisoformat(memory.get(
                    'timestamp', '')).strftime('%d/%m/%Y %H:%M')
                content += f"\n{i}. {memory_time} - อารมณ์: {memory.get('emotion', 'neutral')}\n"
                content += f"คุณ: {memory.get('message', '')}\n"
                content += f"Betty: {memory.get('response', '')}\n"

                if 'tags' in memory:
                    content += f"แท็ก: {', '.join(memory.get('tags', []))}\n"

                content += "-" * 40 + "\n"
        else:
            content += "ไม่มีความจำที่สำคัญในช่วงเวลานี้\n"

        # บันทึกไฟล์
        journal_path = os.path.join(self.memory_paths['journal'], filename)
        os.makedirs(os.path.dirname(journal_path), exist_ok=True)

        with open(journal_path, 'w', encoding='utf-8') as f:
            f.write(content)

        return {
            "filename": filename,
            "path": journal_path,
            "memory_count": len(important_memories),
            "dominant_emotion": dominant_emotion if emotion_counts else "neutral"}
