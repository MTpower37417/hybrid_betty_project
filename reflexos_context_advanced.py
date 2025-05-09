import hashlib
import json
import os
import random
import re
from datetime import datetime


class ContextAdvanced:
    def __init__(self, memory_core=None, context_window=4096):
        self.memory_core = memory_core
        self.context_window = context_window  # จำนวน token สูงสุดที่รองรับ
        self.char_to_token_ratio = 4  # อัตราส่วนโดยประมาณของตัวอักษรต่อ token

        # บัฟเฟอร์บริบท
        self.context_buffer = []
        self.max_buffer_size = 15

        # ประวัติหัวข้อการสนทนา
        self.topic_history = []
        self.max_topics = 10

        # พาธสำหรับจัดเก็บไฟล์
        self.context_path = "./memory/extended"
        self.context_file = f"{self.context_path}/context_history.json"

        # สร้างโฟลเดอร์ถ้ายังไม่มี
        os.makedirs(self.context_path, exist_ok=True)

        # โหลดประวัติบริบท
        self._load_context_history()

        # คำที่ไม่สำคัญ (stop words) สำหรับการวิเคราะห์หัวข้อ
        self.stop_words = {
            # ไทย
            "ฉัน", "คุณ", "เรา", "พวกเขา", "มัน", "นี้", "นั้น", "ที่", "ซึ่ง", "และ", "หรือ", "แต่", "เพราะ",
            "จะ", "ได้", "ให้", "ไป", "มา", "อยู่", "คือ", "ว่า", "เป็น", "มี", "ไม่", "ใน", "กับ", "ของ", "จาก",
            # อังกฤษ
            "i", "you", "he", "she", "we", "they", "it", "this", "that", "the", "a", "an", "and", "or", "but",
            "because", "if", "when", "while", "to", "of", "in", "on", "at", "for", "with", "by", "about", "from"
        }

        # ตัวบ่งชี้การเปลี่ยนหัวข้อ
        self.topic_shift_indicators = [
            # ไทย
            "เปลี่ยนเรื่อง", "พูดถึงเรื่องอื่น", "อีกเรื่องหนึ่ง", "ขอถามอีกเรื่อง", "นอกจากนี้", "อีกอย่าง",
            "ส่วน", "เรื่องใหม่", "ขอเปลี่ยนเรื่อง", "อยากรู้เกี่ยวกับ",
            # อังกฤษ
            "by the way", "on another note", "changing the subject", "speaking of", "that reminds me of",
            "moving on", "let's talk about", "another thing", "regarding", "about", "on the topic of",
            "switch gears", "new topic"
        ]

    def _load_context_history(self):
        """โหลดประวัติบริบทจากไฟล์"""
        if os.path.exists(self.context_file):
            try:
                with open(self.context_file, 'r', encoding='utf-8') as f:
                    loaded_data = json.load(f)
                    self.context_buffer = loaded_data.get('contexts', [])
                    self.topic_history = loaded_data.get('topics', [])

                    # จำกัดขนาดบัฟเฟอร์
                    if len(self.context_buffer) > self.max_buffer_size:
                        self.context_buffer = self.context_buffer[-self.max_buffer_size:]

                    # จำกัดจำนวนหัวข้อ
                    if len(self.topic_history) > self.max_topics:
                        self.topic_history = self.topic_history[-self.max_topics:]
            except BaseException:
                self.context_buffer = []
                self.topic_history = []

    def _save_context_history(self):
        """บันทึกประวัติบริบทลงไฟล์"""
        try:
            data_to_save = {
                'contexts': self.context_buffer[-self.max_buffer_size:],
                'topics': self.topic_history[-self.max_topics:]
            }

            with open(self.context_file, 'w', encoding='utf-8') as f:
                json.dump(data_to_save, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving context history: {e}")

    def extend_context(self, user_input, user_id="user_a"):
        """ขยายบริบทด้วยความจำที่เกี่ยวข้อง"""
        # สร้างบริบทพื้นฐาน
        timestamp = datetime.now().isoformat()
        context = {
            "timestamp": timestamp,
            "user_id": user_id,
            "input": user_input,
            "related_memories": [],
            "emotional_context": {},
            "topics": [],
            "is_topic_shift": self._is_topic_shift(user_input)
        }

        # เพิ่มความจำที่เกี่ยวข้อง
        if self.memory_core:
            related_memories = self.memory_core.get_relevant_memories(
                user_input, limit=5)
            context["related_memories"] = related_memories

        # วิเคราะห์หัวข้อ
        extracted_topics = self._extract_topics(user_input)
        context["topics"] = extracted_topics

        # ตรวจสอบการเปลี่ยนหัวข้อและอัปเดตประวัติหัวข้อ
        if context["is_topic_shift"] and extracted_topics:
            self.topic_history.append({
                "timestamp": timestamp,
                "topics": extracted_topics,
                "input": user_input
            })

        # เพิ่มบริบทในบัฟเฟอร์
        self.context_buffer.append(context)

        # จำกัดขนาดบัฟเฟอร์
        if len(self.context_buffer) > self.max_buffer_size:
            self.context_buffer.pop(0)

        # บันทึกประวัติบริบท
        self._save_context_history()

        # สร้างบริบทที่เหมาะสมสำหรับการใช้งาน
        return self._build_context(context)

    def _is_topic_shift(self, text):
        """ตรวจสอบว่ามีการเปลี่ยนหัวข้อหรือไม่"""
        text_lower = text.lower()

        # ตรวจสอบคำบ่งชี้การเปลี่ยนหัวข้อ
        for indicator in self.topic_shift_indicators:
            if indicator.lower() in text_lower:
                return True

        # ถ้ามีข้อความก่อนหน้า ให้ตรวจสอบความคล้ายคลึงของหัวข้อ
        if self.context_buffer and self.context_buffer[-1].get("topics"):
            previous_topics = set(self.context_buffer[-1]["topics"])
            current_topics = set(self._extract_topics(text))

            # ถ้าไม่มีหัวข้อร่วมกันเลย อาจเป็นการเปลี่ยนหัวข้อ
            if previous_topics and current_topics and not previous_topics.intersection(
                    current_topics):
                return True

        return False

    def _extract_topics(self, text):
        """แยกหัวข้อจากข้อความ"""
        # แยกคำและนับความถี่
        words = re.findall(r'\b\w+\b', text.lower())
        word_counts = {}

        for word in words:
            if word not in self.stop_words and len(
                    word) > 3:  # ข้ามคำสั้นๆ และ stop words
                word_counts[word] = word_counts.get(word, 0) + 1

        # เรียงลำดับตามความถี่
        sorted_topics = sorted(
            word_counts.items(),
            key=lambda x: x[1],
            reverse=True)

        # คืนค่าหัวข้อที่พบบ่อย 5 อันดับแรก
        return [topic for topic, _ in sorted_topics[:5]]

    def _build_context(self, current_context):
        """สร้างบริบทที่เหมาะสมสำหรับการใช้งาน"""
        # เริ่มด้วยข้อความปัจจุบัน
        input_text = current_context.get("input", "")
        context_parts = [f"ข้อความปัจจุบัน: {input_text}"]

        # ประมาณจำนวน token ที่ใช้ไปแล้ว
        approx_tokens_used = len(input_text) / self.char_to_token_ratio

        # เพิ่มความจำที่เกี่ยวข้อง
        if "related_memories" in current_context and current_context["related_memories"]:
            context_parts.append("\nความจำที่เกี่ยวข้อง:")
            for i, memory in enumerate(current_context["related_memories"], 1):
                # ตรวจสอบว่า memory เป็น dict และมี message
                if isinstance(memory, dict) and "message" in memory:
                    memory_text = memory.get("message", "")
                    # ตรวจสอบขนาด token
                    memory_tokens = len(memory_text) / self.char_to_token_ratio

                    if approx_tokens_used + memory_tokens < self.context_window * 0.8:  # เก็บ buffer 20%
                        context_parts.append(f"{i}. {memory_text}")
                        approx_tokens_used += memory_tokens
                    else:
                        break

        # เพิ่มข้อมูลหัวข้อปัจจุบันและประวัติหัวข้อ
        if "topics" in current_context and current_context["topics"]:
            topics = current_context["topics"]
            topics_text = f"\nหัวข้อปัจจุบัน: {', '.join(topics)}"

            # ตรวจสอบขนาด token
            if approx_tokens_used + \
                    len(topics_text) / self.char_to_token_ratio < self.context_window * 0.9:
                context_parts.append(topics_text)
                approx_tokens_used += len(topics_text) / \
                    self.char_to_token_ratio

            # เพิ่มประวัติหัวข้อที่ผ่านมา (3 หัวข้อล่าสุด)
            if self.topic_history and len(self.topic_history) > 1:
                # ไม่รวมหัวข้อปัจจุบัน
                recent_topics = self.topic_history[-4:-1]
                if recent_topics:
                    topics_history_text = "\nหัวข้อที่ผ่านมา:"
                    for i, topic_entry in enumerate(
                            reversed(recent_topics), 1):
                        topic_history_item = f"{i}. {', '.join(topic_entry.get('topics', []))}"

                        # ตรวจสอบขนาด token
                        if approx_tokens_used + \
                                len(topic_history_item) / self.char_to_token_ratio < self.context_window * 0.95:
                            topics_history_text += f"\n{topic_history_item}"
                            approx_tokens_used += len(topic_history_item) / \
                                self.char_to_token_ratio
                        else:
                            break

                    context_parts.append(topics_history_text)

        # เพิ่มข้อมูลการเปลี่ยนหัวข้อ
        if current_context.get("is_topic_shift", False):
            shift_text = "\nหมายเหตุ: มีการเปลี่ยนหัวข้อในการสนทนานี้"

            # ตรวจสอบขนาด token
            if approx_tokens_used + \
                    len(shift_text) / self.char_to_token_ratio < self.context_window * 0.95:
                context_parts.append(shift_text)

        # รวมทุกส่วนเข้าด้วยกัน
        return {
            "text": "\n".join(context_parts),
            "original": current_context
        }

    def generate_response_with_context(self, base_response, context):
        """สร้างการตอบสนองโดยพิจารณาบริบท"""
        # ตรวจสอบว่ามีความจำที่เกี่ยวข้องหรือไม่
        original_context = context.get("original", {})
        related_memories = original_context.get("related_memories", [])

        if related_memories:
            # ตรวจสอบว่ามีความจำที่สำคัญหรือไม่
            important_memory = None
            for memory in related_memories:
                if isinstance(
                        memory,
                        dict) and memory.get(
                        "importance",
                        0) > 0.7:  # ความจำที่มีความสำคัญสูง
                    important_memory = memory
                    break

            if important_memory:
                important_memory.get("message", "")
                # ปรับการตอบสนองโดยอ้างอิงถึงความจำ
                enhanced_response = f"{base_response} (ฉันจำได้ว่าเราเคยคุยเกี่ยวกับเรื่องนี้)"
                return enhanced_response

        # ตรวจสอบการเปลี่ยนหัวข้อ
        if original_context.get("is_topic_shift", False):
            # ปรับการตอบสนองให้เข้ากับการเปลี่ยนหัวข้อ
            topic_shift_responses = [
                f"{base_response} เรื่องนี้น่าสนใจนะคะ",
                f"เปลี่ยนหัวข้อมาคุยเรื่องนี้กันนะคะ {base_response}",
                f"{base_response} เป็นหัวข้อที่น่าสนใจเช่นกันค่ะ",
                f"มาคุยเรื่องนี้กันบ้างนะคะ {base_response}"
            ]
            return random.choice(topic_shift_responses)

        # ถ้าไม่มีการปรับแต่งใดๆ คืนค่าการตอบสนองเดิม
        return base_response

    def save_extended_context(self, user_id="user_a"):
        """บันทึกบริบทขยายลงไฟล์"""
        if not self.context_buffer:
            return None

        # สร้างชื่อไฟล์
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{self.context_path}/extended_context_{user_id}_{timestamp}.json"

        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.context_buffer, f, ensure_ascii=False, indent=2)
            return filename
        except Exception as e:
            print(f"Error saving extended context: {e}")
            return None

    def get_conversation_timeline(self, limit=10):
        """สร้างไทม์ไลน์การสนทนา"""
        # ใช้บริบทในบัฟเฟอร์ (จำกัดตามขนาดที่กำหนด)
        timeline_contexts = self.context_buffer[-limit:] if len(
            self.context_buffer) >= limit else self.context_buffer

        if not timeline_contexts:
            return "ยังไม่มีประวัติการสนทนา"

        # สร้างไทม์ไลน์
        timeline = []
        for ctx in timeline_contexts:
            try:
                timestamp = datetime.fromisoformat(
                    ctx.get("timestamp", "")).strftime('%d/%m/%Y %H:%M')
                input_text = ctx.get("input", "")

                # รวบรวมข้อมูลหัวข้อ
                topics_info = ""
                if "topics" in ctx and ctx["topics"]:
                    topics = ctx["topics"]
                    if topics:
                        topics_info = f" [หัวข้อ: {', '.join(topics[:3])}]"

                # รวบรวมข้อมูลการเปลี่ยนหัวข้อ
                shift_info = ""
                if ctx.get("is_topic_shift", False):
                    shift_info = " [เปลี่ยนหัวข้อ]"

                timeline_entry = f"{timestamp}: {input_text}{topics_info}{shift_info}"
                timeline.append(timeline_entry)
            except BaseException:
                continue

        # รวมไทม์ไลน์เข้าด้วยกัน
        return "\n\n".join(timeline)

    def analyze_conversation_topics(self):
        """วิเคราะห์หัวข้อการสนทนา"""
        if not self.context_buffer:
            return {
                "main_topics": [],
                "topic_frequency": {},
                "topic_shifts": 0,
                "topic_trend": "ไม่มีข้อมูลเพียงพอ"
            }

        # รวบรวมหัวข้อจากทุกบริบท
        all_topics = []
        topic_shifts = 0
        for ctx in self.context_buffer:
            topics = ctx.get("topics", [])
            all_topics.extend(topics)
            if ctx.get("is_topic_shift", False):
                topic_shifts += 1

        # นับความถี่ของหัวข้อ
        topic_counts = {}
        for topic in all_topics:
            topic_counts[topic] = topic_counts.get(topic, 0) + 1

        # เรียงลำดับตามความถี่
        sorted_topics = sorted(
            topic_counts.items(),
            key=lambda x: x[1],
            reverse=True)
        main_topics = [topic for topic, _ in sorted_topics[:5]]

        # วิเคราะห์แนวโน้มหัวข้อ
        topic_trend = "ไม่มีข้อมูลเพียงพอ"
        if len(self.context_buffer) > 1:
            recent_topics = [ctx.get("topics", [])
                             for ctx in self.context_buffer[-3:]]
            flat_recent_topics = [
                topic for sublist in recent_topics for topic in sublist]

            if flat_recent_topics:
                # ตรวจสอบว่าหัวข้อล่าสุดมีความคงที่หรือไม่
                recent_topic_counts = {}
                for topic in flat_recent_topics:
                    recent_topic_counts[topic] = recent_topic_counts.get(
                        topic, 0) + 1

                sorted_recent_topics = sorted(
                    recent_topic_counts.items(), key=lambda x: x[1], reverse=True)

                if len(
                        sorted_recent_topics) > 0 and sorted_recent_topics[0][1] > 1:
                    topic_trend = f"การสนทนากำลังมุ่งเน้นไปที่หัวข้อ '{sorted_recent_topics[0][0]}'"
                elif topic_shifts > 0:
                    topic_trend = "การสนทนามีการเปลี่ยนหัวข้อบ่อย"
                else:
                    topic_trend = "การสนทนามีหัวข้อที่หลากหลาย"

        return {
            "main_topics": main_topics,
            "topic_frequency": topic_counts,
            "topic_shifts": topic_shifts,
            "topic_trend": topic_trend
        }

    def get_context_statistics(self):
        """รับสถิติเกี่ยวกับบริบท"""
        if not self.context_buffer:
            return {
                "context_count": 0,
                "topic_count": 0,
                "topic_shifts": 0,
                "last_updated": None
            }

        # นับจำนวนหัวข้อทั้งหมด
        all_topics = set()
        topic_shifts = 0

        for ctx in self.context_buffer:
            topics = ctx.get("topics", [])
            all_topics.update(topics)
            if ctx.get("is_topic_shift", False):
                topic_shifts += 1

        # รับเวลาอัปเดตล่าสุด
        try:
            last_timestamp = self.context_buffer[-1].get("timestamp", "")
            last_updated = datetime.fromisoformat(
                last_timestamp) if last_timestamp else None
        except BaseException:
            last_updated = None

        return {
            "context_count": len(self.context_buffer),
            "topic_count": len(all_topics),
            "topic_shifts": topic_shifts,
            "last_updated": last_updated.isoformat() if last_updated else None
        }

    def merge_contexts(self, contexts):
        """รวมหลายบริบทเข้าด้วยกัน"""
        if not contexts:
            return {
                "text": "ไม่มีบริบทให้รวม",
                "original": {}
            }

        # เริ่มด้วยบริบทที่สำคัญที่สุด
        merged_text = []

        # รวบรวมความจำที่เกี่ยวข้องจากทุกบริบท
        all_memories = []
        all_topics = []

        for ctx in contexts:
            original = ctx.get("original", {})

            # รวบรวมความจำ
            memories = original.get("related_memories", [])
            all_memories.extend(memories)

            # รวบรวมหัวข้อ
            topics = original.get("topics", [])
            all_topics.extend(topics)

        # ลบความจำที่ซ้ำกัน
        unique_memories = []
        memory_texts = set()

        for memory in all_memories:
            if isinstance(memory, dict) and "message" in memory:
                memory_text = memory.get("message", "")
                if memory_text and memory_text not in memory_texts:
                    memory_texts.add(memory_text)
                    unique_memories.append(memory)

        # สร้างข้อความบริบทรวม
        if unique_memories:
            merged_text.append("ความจำที่เกี่ยวข้อง:")
            for i, memory in enumerate(
                    unique_memories[:5], 1):  # แสดงไม่เกิน 5 รายการ
                memory_text = memory.get("message", "")
                merged_text.append(f"{i}. {memory_text}")

        # ลบหัวข้อที่ซ้ำกัน
        unique_topics = list(set(all_topics))

        if unique_topics:
            # แสดงไม่เกิน 7 หัวข้อ
            merged_text.append(
                f"\nหัวข้อที่เกี่ยวข้อง: {', '.join(unique_topics[:7])}")

        # สร้างบริบทรวม
        merged_context = {
            "text": "\n".join(merged_text),
            "original": {
                "related_memories": unique_memories,
                "topics": unique_topics
            }
        }

        return merged_context

    def detect_topic_from_memory(self, memories, limit=3):
        """ตรวจจับหัวข้อจากความจำที่เกี่ยวข้อง"""
        if not memories:
            return []

        # รวบรวมข้อความจากความจำ
        memory_texts = []
        for memory in memories:
            if isinstance(memory, dict) and "message" in memory:
                memory_texts.append(memory.get("message", ""))

        # รวมข้อความทั้งหมด
        combined_text = " ".join(memory_texts)

        # สกัดหัวข้อจากข้อความรวม
        return self._extract_topics(combined_text)[
            :limit]  # จำกัดไม่เกิน 3 หัวข้อ

    def cache_context(self, user_input, context):
        """แคชบริบทสำหรับการใช้งานในอนาคต"""
        if not user_input or not context:
            return False

        # สร้างคีย์แคช
        cache_key = hashlib.md5(user_input.encode()).hexdigest()

        # สร้างโฟลเดอร์แคช
        cache_dir = f"{self.context_path}/cache"
        os.makedirs(cache_dir, exist_ok=True)

        # บันทึกบริบทลงในแคช
        cache_file = f"{cache_dir}/{cache_key}.json"

        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "input": user_input,
                    "context": context,
                    "timestamp": datetime.now().isoformat()
                }, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"Error caching context: {e}")
            return False

    def get_cached_context(self, user_input):
        """ดึงบริบทจากแคช"""
        if not user_input:
            return None

        # สร้างคีย์แคช
        cache_key = hashlib.md5(user_input.encode()).hexdigest()

        # ตรวจสอบว่ามีแคชหรือไม่
        cache_file = f"{self.context_path}/cache/{cache_key}.json"

        if os.path.exists(cache_file):
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    cached_data = json.load(f)

                # ตรวจสอบอายุของแคช (ไม่เกิน 1 วัน)
                cached_time = datetime.fromisoformat(
                    cached_data.get("timestamp", ""))
                now = datetime.now()

                if (now - cached_time).days < 1:
                    return cached_data.get("context")
            except BaseException:
                pass

        return None
