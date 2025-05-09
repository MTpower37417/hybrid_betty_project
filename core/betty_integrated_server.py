from Betty_Ai_GPT_Trainer_Module.betty_server_integration import \
    BettyGPTTrainer as BettyServerIntegration
import hashlib
import json
import os
import random
import re
from datetime import datetime, timedelta

import gpt_trainer
import reflexos_gpt_bridge
from flask import Flask, jsonify, render_template, request

print(f"Loading module from: {gpt_trainer.__file__}")
print(f"Loading bridge from: {reflexos_gpt_bridge.__file__}")

# --- Configuration ---
CONFIG = {
    'user_id': 'user_a',
    'memory_base_path': './memory',
    'memory_threshold': 0.65,
    'context_window': 4096,
    'char_to_token_ratio': 4,
    'cache_duration': 300,  # 5 minutes
    'log_interactions': True
}

# --- Memory Core System ---


class MemoryCore:
    def __init__(
            self,
            user_id=CONFIG['user_id'],
            memory_base_path=CONFIG['memory_base_path']):
        self.user_id = user_id
        self.memory_base_path = memory_base_path
        self.memory_threshold = CONFIG['memory_threshold']

        # Memory paths
        self.longterm_path = f"{memory_base_path}/longterm"
        self.shortterm_path = f"{memory_base_path}/stack"
        self.emotion_path = f"{memory_base_path}/emotion"
        self.extended_path = f"{memory_base_path}/extended"
        self.capsule_path = f"{memory_base_path}/capsule"
        self.timeline_path = f"{memory_base_path}/timeline"
        self.journal_path = f"{memory_base_path}/journal"

        # Ensure directories exist
        self._ensure_directories()

        # Load existing memories
        self.longterm_memory = self._load_longterm_memory()
        self.shortterm_memory = self._load_shortterm_memory()
        self.emotion_memory = self._load_emotion_memory()
        self.capsule_memory = self._load_capsule_memory()

        # Cache for optimized memory retrieval
        self.memory_cache = {}
        self.last_cache_refresh = datetime.now()

    def _ensure_directories(self):
        """Ensure all memory directories exist"""
        for path in [
                self.longterm_path,
                self.shortterm_path,
                self.emotion_path,
                self.extended_path,
                self.capsule_path,
                self.timeline_path,
                self.journal_path]:
            os.makedirs(path, exist_ok=True)

    def _load_longterm_memory(self):
        """Load longterm memory from file"""
        filepath = f"{self.longterm_path}/{self.user_id}_2025.json"
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except BaseException:
                return []
        return []

    def _load_shortterm_memory(self):
        """Load shortterm memory from file"""
        filepath = f"{self.shortterm_path}/{self.user_id}_stack.json"
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except BaseException:
                return []
        return []

    def _load_emotion_memory(self):
        """Load emotion memory from file"""
        filepath = f"{self.emotion_path}/{self.user_id}_emotion.json"
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except BaseException:
                return []
        return []

    def _load_capsule_memory(self):
        """Load capsule memory from file"""
        filepath = f"{self.capsule_path}/{self.user_id}_capsule.json"
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except BaseException:
                return []
        return []

    def store_user_interaction(
            self,
            message,
            response,
            emotion="neutral",
            memory_type="general"):
        """Store a user interaction in memory"""
        # Store in emotion memory
        self._store_emotion_memory(message, response, emotion)

        # Store in shortterm memory
        self._store_shortterm_memory(message, memory_type)

        # Analyze importance and store in longterm if important
        importance = self.calculate_memory_importance(
            message, memory_type, emotion)
        if importance > self.memory_threshold:
            self._store_longterm_memory(message, memory_type, importance)

        # If very important, store as capsule
        if importance > 0.8:
            self._store_capsule_memory(
                message, response, emotion, memory_type, importance)

        # Update extended context
        self._update_extended_context(message, response)

        # Clear cache to refresh on next retrieval
        self.memory_cache = {}

        return importance

    def _store_emotion_memory(self, message, response, emotion):
        """Store interaction with emotion data"""
        timestamp = datetime.now().isoformat()
        memory_entry = {
            "time": timestamp,
            "message": message,
            "response": response,
            "emotion": emotion
        }

        self.emotion_memory.append(memory_entry)

        # Save to file (keeping last 50 interactions)
        filepath = f"{self.emotion_path}/{self.user_id}_emotion.json"
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.emotion_memory[-50:],
                      f, indent=2, ensure_ascii=False)

    def _store_shortterm_memory(self, message, memory_type="general"):
        """Store message in shortterm memory"""
        timestamp = datetime.now().isoformat()
        memory_entry = {
            "timestamp": timestamp,
            "user": self.user_id,
            "message": message,
            "type": memory_type
        }

        self.shortterm_memory.append(memory_entry)

        # Save to file (keeping last 20 messages)
        filepath = f"{self.shortterm_path}/{self.user_id}_stack.json"
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.shortterm_memory[-20:],
                      f, indent=2, ensure_ascii=False)

    def _store_longterm_memory(
            self,
            message,
            memory_type="general",
            importance=0.5):
        """Store message in longterm memory"""
        timestamp = datetime.now().isoformat()
        memory_entry = {
            "timestamp": timestamp,
            "user": self.user_id,
            "message": message,
            "type": memory_type,
            "importance": importance
        }

        self.longterm_memory.append(memory_entry)

        # Save to file
        filepath = f"{self.longterm_path}/{self.user_id}_2025.json"
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.longterm_memory, f, indent=2, ensure_ascii=False)

    def _store_capsule_memory(
            self,
            message,
            response,
            emotion,
            memory_type,
            importance):
        """Store very important memory as capsule"""
        timestamp = datetime.now().isoformat()
        # Generate tags automatically
        tags = self._auto_generate_tags(message, emotion, memory_type)

        capsule_entry = {
            "timestamp": timestamp,
            "user": self.user_id,
            "message": message,
            "response": response,
            "emotion": emotion,
            "type": memory_type,
            "importance": importance,
            "tags": tags
        }

        self.capsule_memory.append(capsule_entry)

        # Save to JSON file
        filepath = f"{self.capsule_path}/{self.user_id}_capsule.json"
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.capsule_memory, f, indent=2, ensure_ascii=False)

        # Also create a text file for easy reading
        self._create_text_capsule(capsule_entry)

    def _create_text_capsule(self, capsule_entry):
        """Create a text file version of a memory capsule"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        emotion = capsule_entry.get("emotion", "neutral")
        filename = f"{self.capsule_path}/capsule_emotion_{emotion}_{timestamp}.txt"

        content = f"MEMORY CAPSULE - {timestamp}\n"
        content += f"Emotion: {emotion}\n"
        content += f"Type: {capsule_entry.get('type', 'general')}\n"
        content += f"Importance: {capsule_entry.get('importance', 0.5)}\n"
        content += f"Tags: {', '.join(capsule_entry.get('tags', []))}\n\n"
        content += f"User: {capsule_entry.get('message', '')}\n\n"
        content += f"Response: {capsule_entry.get('response', '')}\n"

        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)

    def _auto_generate_tags(self, message, emotion, memory_type):
        """Automatically generate tags for memory capsules"""
        tags = [memory_type, emotion]  # Basic tags from type and emotion

        # Content-based tags
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

        message_lower = message.lower()
        for tag, keywords in content_tags.items():
            for keyword in keywords:
                if keyword in message_lower:
                    tags.append(tag)
                    break

        # Remove duplicates
        return list(set(tags))

    def _update_extended_context(self, message, response):
        """Update extended context memory"""
        timestamp = datetime.now().isoformat()

        # Load existing context
        filepath = f"{self.extended_path}/{self.user_id}_context.json"
        context_data = []
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    context_data = json.load(f)
            except BaseException:
                context_data = []

        # Add new entry
        context_entry = {
            "timestamp": timestamp,
            "message": message,
            "response": response
        }
        context_data.append(context_entry)

        # Save to file (keeping last 15 interactions)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(context_data[-15:], f, indent=2, ensure_ascii=False)

    def calculate_memory_importance(
            self,
            message,
            memory_type="general",
            emotion="neutral"):
        """Calculate importance score of a memory (0-1)"""
        importance = 0.5  # Default importance

        # Type-based adjustment
        type_boost = {
            'emotion': 0.2,
            'identity': 0.3,
            'preference': 0.2,
            'factual': 0.1,
            'general': 0.0
        }

        importance += type_boost.get(memory_type, 0.0)

        # Emotion-based adjustment
        emotion_boost = {
            'joy': 0.1,
            'sadness': 0.15,
            'anger': 0.2,
            'fear': 0.2,
            'surprise': 0.1,
            'love': 0.25,
            'neutral': 0.0
        }

        # จัดการกับ emotion ที่อาจเป็น dict หรือ string
        emotion_key = emotion
        if isinstance(emotion, dict):
            emotion_key = emotion.get('emotion', 'neutral')

        importance += emotion_boost.get(emotion_key, 0.0)

        # Check for important keywords
        important_keywords = [
            # Thai
            "จำ", "จดจำ", "อย่าลืม", "สำคัญ", "ชื่อ", "วันเกิด", "เบอร์", "ชอบ", "รัก", "ไม่ชอบ",
            "ต้องการ", "อยาก", "ฉัน", "คุณ", "เรา", "หวัง", "ความฝัน", "ปัญหา", "แก้ไข",
            # English
            "remember", "important", "birthday", "name", "contact", "like", "love", "hate",
            "need", "want", "I", "you", "we", "hope", "dream", "problem", "fix"
        ]

        message_lower = message.lower()
        for keyword in important_keywords:
            if keyword in message_lower:
                importance += 0.05  # Increase importance for each keyword found

        # Check message length - longer messages often more important
        if len(message) > 100:
            importance += 0.1

        # Normalize to 0-1 range
        return min(1.0, importance)

    def get_relevant_memories(self, query, limit=5):
        """Get memories relevant to a query"""
        # Check if we have cached results
        cache_key = hashlib.md5(query.encode()).hexdigest()
        cache_age = (datetime.now() - self.last_cache_refresh).total_seconds()

        if cache_key in self.memory_cache and cache_age < CONFIG['cache_duration']:
            return self.memory_cache[cache_key]

        # Search in all memory types
        all_memories = []
        all_memories.extend(self.shortterm_memory)
        all_memories.extend(self.longterm_memory)
        all_memories.extend(self.capsule_memory)

        # Simple relevance scoring using word overlap
        scored_memories = []
        query_words = set(query.lower().split())

        for memory in all_memories:
            if not isinstance(memory, dict) or "message" not in memory:
                continue

            memory_text = memory["message"].lower()
            memory_words = set(memory_text.split())

            # Calculate word overlap
            common_words = query_words.intersection(memory_words)
            relevance = len(common_words) / max(len(query_words), 1)

            # Boost based on importance if available
            if 'importance' in memory:
                relevance *= (1 + memory['importance'])

            # Boost recent memories
            if memory in self.shortterm_memory:
                relevance *= 1.5

            # Only consider if there's some relevance
            if relevance > 0:
                scored_memories.append((relevance, memory))

        # Sort by relevance and take top results
        scored_memories.sort(reverse=True, key=lambda x: x[0])
        relevant_memories = [memory for score,
                             memory in scored_memories[:limit]]

        # Update cache
        self.memory_cache[cache_key] = relevant_memories
        self.last_cache_refresh = datetime.now()

        return relevant_memories

    def adjust_memory_weight(self, message, emotion_multiplier=1.0):
        """Adjust memory weight based on emotional intensity"""
        # Find the memory in shortterm
        for memory in self.shortterm_memory:
            if memory.get("message") == message:
                # If emotion is strong, move to longterm immediately
                if emotion_multiplier > 1.2:
                    memory_type = memory.get("type", "general")
                    self._store_longterm_memory(
                        message, memory_type, importance=0.7)
                break

    def get_memory_summary(self):
        """Get summary statistics about memory"""
        return {
            "shortterm_count": len(self.shortterm_memory),
            "longterm_count": len(self.longterm_memory),
            "emotion_records": len(self.emotion_memory),
            "capsule_count": len(self.capsule_memory),
            "memory_threshold": self.memory_threshold
        }

    def create_memory_journal(self, period="day"):
        """Create journal from memories for given time period"""
        now = datetime.now()

        # Define cutoff time based on period
        if period == "day":
            cutoff = now - timedelta(days=1)
            title = f"บันทึกประจำวันที่ {now.strftime('%d/%m/%Y')}"
            filename = f"journal_{now.strftime('%Y%m%d')}.txt"
        elif period == "week":
            cutoff = now - timedelta(days=7)
            title = f"บันทึกประจำสัปดาห์ สิ้นสุดวันที่ {now.strftime('%d/%m/%Y')}"
            filename = f"weekly_journal_{now.strftime('%Y%m%d')}.txt"
        else:  # month
            cutoff = now.replace(day=1)  # First day of current month
            title = f"บันทึกประจำเดือน {now.strftime('%m/%Y')}"
            filename = f"monthly_journal_{now.strftime('%Y%m')}.txt"

        # Collect relevant memories
        relevant_memories = []
        for memory in self.longterm_memory + self.capsule_memory:
            try:
                memory_time = datetime.fromisoformat(
                    memory.get('timestamp', ''))
                if memory_time >= cutoff:
                    relevant_memories.append(memory)
            except BaseException:
                continue

        # Sort by timestamp
        relevant_memories.sort(key=lambda x: x.get('timestamp', ''))

        # Create journal content
        content = f"{title}\n{'=' * len(title)}\n\n"

        # Add emotion summary
        emotions = [m.get('emotion', 'neutral') for m in relevant_memories]
        emotion_counts = {}
        for emotion in emotions:
            emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1

        if emotion_counts:
            dominant_emotion = max(
                emotion_counts.items(),
                key=lambda x: x[1])[0]
            content += f"อารมณ์โดยรวม: {dominant_emotion}\n\n"

        # Add memory entries
        if relevant_memories:
            content += "ความทรงจำที่สำคัญ:\n"
            for i, memory in enumerate(relevant_memories, 1):
                try:
                    memory_time = datetime.fromisoformat(memory.get(
                        'timestamp', '')).strftime('%d/%m/%Y %H:%M')
                    content += f"\n{i}. {memory_time} - อารมณ์: {memory.get('emotion', 'neutral')}\n"
                    content += f"คุณ: {memory.get('message', '')}\n"
                    if 'response' in memory:
                        content += f"Betty: {memory.get('response', '')}\n"

                    if 'tags' in memory:
                        content += f"แท็ก: {', '.join(memory.get('tags', []))}\n"

                    content += "-" * 40 + "\n"
                except BaseException:
                    continue
        else:
            content += "ไม่มีความทรงจำที่สำคัญในช่วงเวลานี้\n"

        # Save journal file
        filepath = f"{self.journal_path}/{filename}"
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

        return {
            "filename": filename,
            "path": filepath,
            "memory_count": len(relevant_memories),
            "dominant_emotion": dominant_emotion if emotion_counts else "neutral"}


# --- Emotion System ---
class EmotionSystem:
    def __init__(self, memory_core=None):
        self.memory_core = memory_core

        # Emotion intensity mapping
        self.emotion_intensity = {
            "joy": 1.3,      # ความสุข
            "sadness": 1.4,  # ความเศร้า
            "anger": 1.5,    # ความโกรธ
            "fear": 1.4,     # ความกลัว
            "surprise": 1.2,  # ความประหลาดใจ
            "love": 1.6,     # ความรัก
            "disgust": 1.3,  # ความรังเกียจ
            "neutral": 1.0,  # เป็นกลาง
            "curious": 1.1,  # ความอยากรู้
            "disappointed": 1.4,  # ผิดหวัง
            "hopeful": 1.2,  # ความหวัง
            "frustrated": 1.4,  # หงุดหงิด
            "relaxed": 1.1   # ผ่อนคลาย
        }

        # Emotion keywords (Thai and English)
        self.emotion_keywords = {
            "joy": [
                # Thai
                "สนุก", "ดีใจ", "มีความสุข", "สุข", "ยินดี", "ยิ้ม", "หัวเราะ", "สุขใจ", "ปลื้ม", "ตื่นเต้น",
                # English
                "happy", "joy", "pleased", "glad", "delighted", "excited", "thrilled", "wonderful", "fun", "enjoy"
            ],
            "sadness": [
                # Thai
                "เศร้า", "เสียใจ", "ผิดหวัง", "สิ้นหวัง", "หดหู่", "ร้องไห้", "น้ำตา", "ทุกข์", "เจ็บใจ",
                # English
                "sad", "upset", "disappointed", "unhappy", "depressed", "blue", "down", "hurt", "pain", "crying"
            ],
            "anger": [
                # Thai
                "โกรธ", "หงุดหงิด", "ฉุนเฉียว", "โมโห", "เดือด", "แค้น", "เคือง", "ไม่พอใจ", "รำคาญ",
                # English
                "angry", "mad", "furious", "annoyed", "irritated", "frustrated", "rage", "hate", "resent"
            ],
            "fear": [
                # Thai
                "กลัว", "หวาดกลัว", "วิตก", "กังวล", "ตื่นกลัว", "ตกใจ", "หวาดระแวง", "ตื่นตระหนก",
                # English
                "scared", "afraid", "worried", "anxious", "terrified", "frightened", "panic", "terror"
            ],
            "surprise": [
                # Thai
                "ประหลาดใจ", "ตกใจ", "อึ้ง", "ทึ่ง", "อัศจรรย์", "ไม่เชื่อ", "ตะลึง",
                # English
                "surprised", "shocked", "amazed", "astonished", "wow", "unexpected", "startled"
            ],
            "love": [
                # Thai
                "รัก", "ชอบ", "หลงรัก", "รักใคร่", "เสน่หา", "ปรารถนา", "อบอุ่น", "ทะนุถนอม", "ผูกพัน", "คิดถึง",
                # English
                "love", "adore", "fond", "affection", "caring", "cherish", "devoted", "miss", "desire"
            ],
            "disgust": [
                # Thai
                "รังเกียจ", "ขยะแขยง", "สะอิดสะเอียน", "เกลียด", "คลื่นไส้",
                # English
                "disgusted", "revolted", "gross", "yuck", "nasty", "repulsed"
            ],
            "neutral": [
                # Thai
                "ปกติ", "เฉยๆ", "ธรรมดา", "ไม่เป็นไร", "พอใช้", "ก็ได้",
                # English
                "neutral", "fine", "okay", "alright", "so-so", "normal"
            ],
            "curious": [
                # Thai
                "สงสัย", "อยากรู้", "สนใจ", "ทำไม", "ยังไง", "อย่างไร", "อะไร", "เหตุใด",
                # English
                "curious", "wonder", "interested", "why", "how", "what", "question"
            ],
            "disappointed": [
                # Thai
                "ผิดหวัง", "ไม่เป็นไปตามที่คิด", "ไม่สมหวัง", "พลาด", "ละทิ้ง",
                # English
                "disappointed", "letdown", "failed", "unfulfilled", "dismayed"
            ],
            "hopeful": [
                # Thai
                "หวัง", "มีความหวัง", "คาดหวัง", "ฝัน", "ดีขึ้น", "โอกาส", "อนาคต",
                # English
                "hope", "hopeful", "optimistic", "looking forward", "positive", "expecting"
            ],
            "frustrated": [
                # Thai
                "หงุดหงิด", "อึดอัด", "ไม่พอใจ", "ติดขัด", "สับสน", "วุ่นวาย", "ยุ่งยาก",
                # English
                "frustrated", "stuck", "blocked", "annoyed", "bothered", "difficulty"
            ],
            "relaxed": [
                # Thai
                "ผ่อนคลาย", "สบาย", "สงบ", "เย็น", "พักผ่อน", "สบายใจ", "ไม่เครียด",
                # English
                "relaxed", "calm", "peaceful", "chill", "easy", "comfortable", "serene"
            ]
        }

        # Emoji for emotions
        self.emotion_emoji = {
            "joy": ["😊", "😄", "🥰", "😁", "😀"],
            "sadness": ["😔", "😢", "💔", "😞", "😥"],
            "anger": ["😠", "😤", "😡", "🤬", "👿"],
            "fear": ["😨", "😰", "😱", "🥺", "😳"],
            "surprise": ["😮", "😲", "😯", "😦", "🤯"],
            "love": ["❤️", "💕", "💖", "💗", "💓"],
            "disgust": ["🤢", "😖", "😬", "👎", "🙄"],
            "neutral": ["😌", "🙂", "👋", "🤔", "😐"],
            "curious": ["🧐", "🤨", "❓", "🔍", "💭"],
            "disappointed": ["😕", "😒", "😟", "🥺", "😣"],
            "hopeful": ["✨", "🙏", "🌟", "🌈", "💫"],
            "frustrated": ["😤", "😣", "😫", "😩", "🤦"],
            "relaxed": ["😌", "😎", "🧘", "☺️", "🛌"]
        }

        # Response templates based on emotions
        self.response_templates = {
            "joy": [
                "ดีใจด้วยนะ! {emoji}",
                "นั่นฟังดูดีมากเลย",
                "ฉันรู้สึกตื่นเต้นแทนคุณ"
            ],
            "sadness": [
                "ฉันอยู่ตรงนี้นะ",
                "ไม่เป็นไรเลย",
                "คุณสามารถเล่าให้ฉันฟังได้เสมอ"
            ],
            "anger": [
                "ฟังแล้วรู้สึกได้เลยว่ามันไม่ง่าย",
                "ถ้าอยากระบายก็ได้นะ",
                "ฉันฟังคุณอยู่"
            ],
            "neutral": [
                "โอเค ได้รับแล้ว",
                "อืม... เข้าใจนะ",
                "เล่าเพิ่มเติมได้เลยนะ"
            ]
        }

        # Emotion history
        self.emotion_history = []

        # Emotion log file
        self.emotion_log_file = "./memory/emotion/emotion_log.json"
        os.makedirs("./memory/emotion", exist_ok=True)

        # Load emotion history if exists
        self._load_emotion_history()

    def _load_emotion_history(self):
        """Load emotion history from file"""
        if os.path.exists(self.emotion_log_file):
            try:
                with open(self.emotion_log_file, 'r', encoding='utf-8') as f:
                    self.emotion_history = json.load(f)
            except BaseException:
                self.emotion_history = []

    def _save_emotion_history(self):
        """Save emotion history to file"""
        try:
            with open(self.emotion_log_file, 'w', encoding='utf-8') as f:
                # Keep only last 100 entries to prevent file growth
                json.dump(self.emotion_history[-100:],
                          f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving emotion history: {e}")

    def detect_emotion(self, text):
        """Detect emotion from text"""
        text_lower = text.lower()
        emotion_scores = {}

        # Calculate scores for each emotion based on keywords
        for emotion, keywords in self.emotion_keywords.items():
            score = 0
            for keyword in keywords:
                if keyword.lower() in text_lower:
                    score += 1

            if score > 0:
                emotion_scores[emotion] = score

        # If no emotion detected, return neutral
        if not emotion_scores:
            return "neutral"

        # Return emotion with highest score
        return max(emotion_scores.items(), key=lambda x: x[1])[0]

    def analyze_emotion_with_context(self, text, context=None):
        """Analyze emotion considering conversation context"""
        # Base emotion from text
        base_emotion = self.detect_emotion(text)

        # If we have context with emotion history, consider it
        if context and isinstance(context,
                                  dict) and "emotion_history" in context:
            recent_emotions = context["emotion_history"][-3:] if len(
                context["emotion_history"]) > 0 else []

            # Process each emotion in history to ensure they're strings
            processed_recent_emotions = []
            for emotion_item in recent_emotions:
                if isinstance(emotion_item, dict):
                    emotion_str = emotion_item.get('emotion', 'neutral')
                    processed_recent_emotions.append(emotion_str)
                else:
                    processed_recent_emotions.append(emotion_item)

            # If consistently same emotion in history, strengthen it
            if processed_recent_emotions and all(
                    e == processed_recent_emotions[0] for e in processed_recent_emotions):
                # Return consistent emotion
                return processed_recent_emotions[0]

            # If neutral but recent emotions are strong, carry over some
            # emotional context
            if base_emotion == "neutral" and processed_recent_emotions:
                # Get most frequent recent emotion
                emotion_counts = {}
                for emotion_str in processed_recent_emotions:
                    emotion_counts[emotion_str] = emotion_counts.get(
                        emotion_str, 0) + 1
                most_frequent = max(
                    emotion_counts.items(),
                    key=lambda x: x[1])[0]
                strong_emotions = ["love", "anger", "fear", "sadness"]
                if most_frequent in strong_emotions:
                    if most_frequent == "anger":
                        return "frustrated"
                    elif most_frequent == "sadness":
                        return "disappointed"
                    elif most_frequent == "fear":
                        return "anxious"
                    elif most_frequent == "love":
                        return "hopeful"

        return base_emotion
        # If we have context with emotion history, consider it
        if context and isinstance(context,
                                  dict) and "emotion_history" in context:
            recent_emotions = context["emotion_history"][-3:] if len(
                context["emotion_history"]) > 0 else []

            # If consistently same emotion in history, strengthen it
            if recent_emotions and all(
                    e == recent_emotions[0] for e in recent_emotions):
                return recent_emotions[0]  # Return consistent emotion

            # If neutral but recent emotions are strong, carry over some
            # emotional context
            if base_emotion == "neutral" and recent_emotions:
                # Get most frequent recent emotion
                emotion_counts = {}
                for emotion in recent_emotions:
                    emotion_counts[emotion] = emotion_counts.get(
                        emotion, 0) + 1

                most_frequent = max(
                    emotion_counts.items(),
                    key=lambda x: x[1])[0]

                # Only carry over if it's a strong emotion
                strong_emotions = ["love", "anger", "fear", "sadness"]
                if most_frequent in strong_emotions:
                    # Create a more nuanced emotion - for example, after anger
                    # might be frustrated
                    if most_frequent == "anger":
                        return "frustrated"
                    elif most_frequent == "sadness":
                        return "disappointed"
                    elif most_frequent == "fear":
                        return "anxious"
                    elif most_frequent == "love":
                        return "hopeful"

        return base_emotion

    def get_emotion_emoji(self, emotion):
        """Get random emoji for the given emotion"""
        if emotion in self.emotion_emoji:
            return random.choice(self.emotion_emoji[emotion])
        return "😊"  # Default emoji

    def format_emotional_response(self, base_response, emotion):
        """Format response based on emotion and conversation intent"""
        if isinstance(emotion, dict):
            emotion_key = emotion.get('emotion', 'neutral')
        else:
            emotion_key = emotion

        # Soft override if emotion stuck in 'neutral'
        if emotion_key == 'neutral' and random.random() < 0.5:
            emotion_key = random.choice(['joy', 'sadness', 'anger'])

        # If user asked a question, change response type
        if isinstance(
                base_response,
                str) and base_response.strip().endswith("?"):
            return random.choice([
                "คำถามดีจัง... ฉันคิดว่ามันซับซ้อนนะ",
                "อืม ฉันว่าคุณน่าจะรู้อยู่แล้วล่ะ 😉",
                "แล้วคุณล่ะ คิดว่ายังไง?",
                "ฉันว่ามันขึ้นอยู่กับสถานการณ์นะ"
            ])

        choice = random.choices(
            ['template', 'freestyle', 'raw'], weights=[0.3, 0.5, 0.2])[0]
        if choice == 'template' and emotion_key in self.response_templates:
            template = random.choice(self.response_templates[emotion_key])
            if base_response.lower().strip() in template.lower():
                return random.choice([
                    "เข้าใจเลย",
                    "อืม... ได้ยินแล้ว",
                    "เล่าอีกได้นะ ฉันฟังอยู่"
                ])
            emoji = self.get_emotion_emoji(emotion_key)
            return template.format(response=base_response, emoji=emoji)
        elif choice == 'freestyle':
            return random.choice([
                "เล่าต่อได้เลย ฉันอยากฟังนะ",
                "แล้วจากนั้นล่ะ?",
                "คุณคิดว่ายังไงต่อเหรอ?",
                "ขอบคุณที่บอกฉันนะ",
                "ฉันชอบเวลาคุณเล่าเรื่องแบบนี้จัง"
            ])
        else:
            return base_response
        # Override if always neutral (simulate emotion diversity)
        if emotion_key == 'neutral' and random.random() < 0.3:
            emotion_key = random.choice(['joy', 'sadness', 'anger'])

        choice = random.choices(
            ['template', 'freestyle', 'raw'], weights=[0.3, 0.4, 0.3])[0]
        if choice == 'template' and emotion_key in self.response_templates:
            template = random.choice(self.response_templates[emotion_key])
            if base_response.lower().strip() in template.lower():
                return random.choice([
                    "เข้าใจเลย",
                    "อืม... ได้ยินแล้ว",
                    "เล่าอีกได้นะ ฉันฟังอยู่"
                ])
            emoji = self.get_emotion_emoji(emotion_key)
            return template.format(response=base_response, emoji=emoji)
        elif choice == 'freestyle':
            return random.choice([
                "เล่าต่อเลย ฉันสนใจอยู่",
                "อยากฟังเพิ่มเติมอีกนะ",
                "แล้วคุณรู้สึกยังไงกับเรื่องนี้เหรอ?",
                "ขอบคุณที่บอกฉันนะ"
            ])
        else:
            return base_response
        choice = random.choices(
            ['template', 'raw', 'freestyle'], weights=[0.4, 0.3, 0.3])[0]
        if choice == 'template' and emotion_key in self.response_templates:
            template = random.choice(self.response_templates[emotion_key])
            emoji = self.get_emotion_emoji(emotion_key)
            return template.format(response=base_response, emoji=emoji)
        elif choice == 'freestyle':
            return random.choice([
                "เข้าใจลึกซึ้งเลยนะ",
                "อืม... ฟังดูน่าสนใจดี",
                "ขอบคุณที่แบ่งปันเรื่องนี้",
                "มันสำคัญมากเลย ฉันรับฟังอยู่เสมอ"
            ])
        else:
            return base_response
        if emotion_key in self.response_templates:
            template = random.choice(self.response_templates[emotion_key])
            emoji = self.get_emotion_emoji(emotion_key)
            return template.format(response=base_response, emoji=emoji)

    def process_user_input(self, user_input, base_response, context=None):
        """Process user input, detect emotion, and format response"""
        # Detect emotion with context
        detected_emotion = self.analyze_emotion_with_context(
            user_input, context)

        # Get emotion intensity
        emotion_intensity = self.emotion_intensity.get(
            detected_emotion if isinstance(
                detected_emotion, str) else "neutral", 1.0)

        # Format response with emotion
        emotional_response = self.format_emotional_response(
            base_response, detected_emotion)

        # Record emotion in history
        self._record_emotion(user_input, base_response, detected_emotion)

        # Link to memory if available
        if self.memory_core:
            self.memory_core.adjust_memory_weight(
                user_input, emotion_intensity)

        return {
            "response": emotional_response,
            "emotion": detected_emotion,
            "intensity": emotion_intensity
        }

    def _record_emotion(self, user_input, response, emotion):
        """บันทึกอารมณ์ในประวัติ"""
        timestamp = datetime.now().isoformat()

        # จัดการกับ emotion ทั้งที่เป็น dict หรือ string
        emotion_key = emotion
        if isinstance(emotion, dict):
            emotion_key = emotion.get('emotion', 'neutral')

        # สร้าง entry บันทึกอารมณ์
        entry = {
            "timestamp": timestamp,
            "input": user_input,
            "response": response,
            "emotion": emotion_key,
            "intensity": self.emotion_intensity.get(emotion_key, 1.0)
        }

        # เพิ่มลงในประวัติ
        self.emotion_history.append(entry)

        # บันทึกลงไฟล์
        self._save_emotion_history()

    def get_emotion_trend(self, limit=10):
        """Get emotion trends from recent history"""
        recent_emotions = self.emotion_history[-limit:] if len(
            self.emotion_history) >= limit else self.emotion_history

        # Count frequency of each emotion
        emotion_counts = {}
        for entry in recent_emotions:
            emotion = entry.get("emotion", "neutral")
            emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1

        # Calculate dominant emotion
        dominant_emotion = "neutral"
        if emotion_counts:
            dominant_emotion = max(
                emotion_counts.items(),
                key=lambda x: x[1])[0]

        # Calculate average intensity
        avg_intensity = 1.0
        if recent_emotions:
            total_intensity = sum(entry.get("intensity", 1.0)
                                  for entry in recent_emotions)
            avg_intensity = total_intensity / len(recent_emotions)

        return {
            "dominant_emotion": dominant_emotion,
            "emotion_counts": emotion_counts,
            "avg_intensity": avg_intensity,
            "recent_emotions": [
                entry.get("emotion") for entry in recent_emotions]}

    def generate_emotion_report(self, period="day"):
        """Generate emotion report for given time period"""
        now = datetime.now()

        # Define period
        if period == "day":
            # Today
            start_time = now.replace(hour=0, minute=0, second=0, microsecond=0)
            title = f"รายงานอารมณ์ประจำวันที่ {now.strftime('%d/%m/%Y')}"
        elif period == "week":
            # Last 7 days
            start_time = now.replace(hour=0, minute=0, second=0, microsecond=0)
            start_time = start_time - timedelta(days=start_time.weekday())
            title = f"รายงานอารมณ์ประจำสัปดาห์ {start_time.strftime('%d/%m/%Y')} - {now.strftime('%d/%m/%Y')}"
        else:  # month
            # This month
            start_time = now.replace(
                day=1, hour=0, minute=0, second=0, microsecond=0)
            title = f"รายงานอารมณ์ประจำเดือน {now.strftime('%m/%Y')}"

        # Filter emotions in time period
        filtered_emotions = []
        for entry in self.emotion_history:
            try:
                entry_time = datetime.fromisoformat(entry.get("timestamp", ""))
                if entry_time >= start_time:
                    filtered_emotions.append(entry)
            except BaseException:
                continue

        # Count emotions
        emotion_counts = {}
        for entry in filtered_emotions:
            emotion = entry.get("emotion", "neutral")
            emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1

        # Create report content
        report = f"{title}\n{'=' * len(title)}\n\n"

        if not filtered_emotions:
            report += "ไม่มีข้อมูลอารมณ์ในช่วงเวลานี้\n"
            return report

        # Summary of main emotion
        dominant_emotion = max(emotion_counts.items(), key=lambda x: x[1])[
            0] if emotion_counts else "neutral"
        report += f"อารมณ์หลัก: {dominant_emotion}\n\n"

        # Show frequency of each emotion
        report += "ความถี่ของอารมณ์:\n"
        for emotion, count in sorted(
                emotion_counts.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / len(filtered_emotions)) * 100
            report += f"- {emotion}: {count} ครั้ง ({percentage:.1f}%)\n"

        # Average intensity
        total_intensity = sum(entry.get("intensity", 1.0)
                              for entry in filtered_emotions)
        avg_intensity = total_intensity / len(filtered_emotions)
        report += f"\nความเข้มของอารมณ์เฉลี่ย: {avg_intensity:.2f}\n"

        # Example conversations with strong emotions
        report += "\nตัวอย่างการสนทนาที่มีอารมณ์ชัดเจน:\n"

        # Sort by intensity
        filtered_emotions.sort(
            key=lambda x: x.get(
                "intensity", 1.0), reverse=True)

        # Show top 3 examples
        for i, entry in enumerate(filtered_emotions[:3], 1):
            try:
                entry_time = datetime.fromisoformat(
                    entry.get("timestamp", "")).strftime('%d/%m/%Y %H:%M')
                report += f"\n{i}. {entry_time} - อารมณ์: {entry.get('emotion', 'neutral')} (ความเข้ม: {entry.get('intensity', 1.0):.2f})\n"
                report += f"   คุณ: {entry.get('input', '')}\n"
                report += f"   Betty: {entry.get('response', '')}\n"
            except BaseException:
                continue

        return report


# --- Context System ---
class ContextSystem:
    def __init__(
            self,
            memory_core=None,
            context_window=CONFIG['context_window']):
        self.memory_core = memory_core
        self.context_window = context_window
        self.char_to_token_ratio = CONFIG['char_to_token_ratio']
        self.context_buffer = []
        self.max_buffer_size = 10

        # Context file path
        self.context_path = "./memory/extended"
        os.makedirs(self.context_path, exist_ok=True)

    def extend_context(self, current_input, user_id=CONFIG['user_id']):
        """Extend context with relevant memories and information"""
        if not self.memory_core:
            return current_input

        # Get relevant memories
        relevant_memories = self.memory_core.get_relevant_memories(
            current_input, limit=5)

        # Extract topics from current input
        topics = self._extract_topics(current_input)

        # Create context object
        timestamp = datetime.now().isoformat()
        context = {
            "timestamp": timestamp,
            "user_id": user_id,
            "input": current_input,
            "topics": topics,
            "relevant_memories": relevant_memories
        }

        # Add to buffer
        self.context_buffer.append(context)
        if len(self.context_buffer) > self.max_buffer_size:
            self.context_buffer.pop(0)

        # Save to file
        self._save_context(context, user_id)

        # Build optimized context
        return self._build_optimized_context(context)

    def _extract_topics(self, text):
        """Extract main topics from text"""
        # Words to ignore
        stop_words = {
            # Thai
            "ฉัน", "คุณ", "เรา", "เขา", "มัน", "นี้", "นั้น", "ที่", "ซึ่ง", "อัน",
            "และ", "หรือ", "แต่", "ถ้า", "จะ", "ได้", "มี", "เป็น", "คือ", "ว่า",
            # English
            "i", "you", "he", "she", "it", "this", "that", "what", "which", "who",
            "and", "or", "but", "if", "then", "will", "have", "has", "had", "is",
            "are", "was", "were", "be", "been", "being", "do", "does", "did"
        }

        # Extract words and count frequency
        words = re.findall(r'\b\w+\b', text.lower())
        word_counts = {}

        for word in words:
            if word not in stop_words and len(word) > 2:
                word_counts[word] = word_counts.get(word, 0) + 1

        # Sort by frequency
        sorted_topics = sorted(
            word_counts.items(),
            key=lambda x: x[1],
            reverse=True)

        # Return top 5 topics
        return [topic for topic, _ in sorted_topics[:5]]

    def _build_optimized_context(self, context):
        """Build optimized context string based on token limits"""
        # Start with current input
        context_parts = [f"ข้อความปัจจุบัน: {context['input']}"]

        # Approximate tokens used
        approx_tokens_used = len(context['input']) / self.char_to_token_ratio

        # Add relevant memories
        if "relevant_memories" in context and context["relevant_memories"]:
            context_parts.append("\nความจำที่เกี่ยวข้อง:")

            for i, memory in enumerate(context["relevant_memories"], 1):
                memory_text = memory.get("message", "")
                memory_tokens = len(memory_text) / self.char_to_token_ratio

                # Add memory if within token limit (keeping 20% buffer)
                if approx_tokens_used + memory_tokens < self.context_window * 0.8:
                    context_parts.append(f"{i}. {memory_text}")
                    approx_tokens_used += memory_tokens
                else:
                    break

        # Add topics if space available
        if "topics" in context and context["topics"]:
            topics_text = f"\nหัวข้อที่เกี่ยวข้อง: {', '.join(context['topics'])}"
            topics_tokens = len(topics_text) / self.char_to_token_ratio

            if approx_tokens_used + topics_tokens < self.context_window * 0.95:
                context_parts.append(topics_text)

        # Combine parts
        extended_context = "\n".join(context_parts)

        return {
            "text": extended_context,
            "original": context
        }

    def _save_context(self, context, user_id):
        """Save context to file"""
        filepath = f"{self.context_path}/{user_id}_context.json"

        # Load existing contexts
        contexts = []
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    contexts = json.load(f)
            except BaseException:
                contexts = []

        # Add new context
        contexts.append(context)

        # Save to file (keeping last 15 contexts)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(contexts[-15:], f, indent=2, ensure_ascii=False)

    def generate_response_with_context(self, base_response, context):
        """Generate response considering the context"""
        # Check if we have context
        if not context or "original" not in context:
            return base_response

        # Get original context
        original = context["original"]

        # If we have relevant memories
        if "relevant_memories" in original and original["relevant_memories"]:
            # Find first important memory
            important_memory = None
            for memory in original["relevant_memories"]:
                if memory.get("importance", 0) > 0.7:
                    important_memory = memory
                    break

            if important_memory:
                # Reference the memory
                return f"{base_response} (ฉันจำได้ว่าเราเคยคุยเกี่ยวกับเรื่องนี้)"

        return base_response

    def get_conversation_timeline(self, limit=10, user_id=CONFIG['user_id']):
        """Generate timeline of conversations"""
        filepath = f"{self.context_path}/{user_id}_context.json"

        if not os.path.exists(filepath):
            return "ยังไม่มีประวัติการสนทนา"

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                contexts = json.load(f)
        except BaseException:
            return "ไม่สามารถโหลดประวัติการสนทนาได้"

        # Get recent contexts
        recent_contexts = contexts[-limit:] if len(
            contexts) > limit else contexts

        # Build timeline
        timeline = []
        for ctx in recent_contexts:
            try:
                timestamp = datetime.fromisoformat(
                    ctx.get("timestamp", "")).strftime('%d/%m/%Y %H:%M')
                input_text = ctx.get("input", "")

                # Add topics if available
                topics_info = ""
                if "topics" in ctx and ctx["topics"]:
                    topics_info = f" [หัวข้อ: {', '.join(ctx['topics'][:3])}]"

                timeline_entry = f"{timestamp}: {input_text}{topics_info}"
                timeline.append(timeline_entry)
            except BaseException:
                continue

        return "\n\n".join(timeline)


# --- Integrated Server ---
class IntegratedServer:
    def __init__(self):
        # Initialize components
        self.memory_core = MemoryCore(user_id=CONFIG['user_id'])
        self.emotion_system = EmotionSystem(self.memory_core)
        self.context_system = ContextSystem(self.memory_core)
        self.gpt_trainer = BettyServerIntegration(mode="train")
        self.betty_integration = self.gpt_trainer  # ใช้ instance เดียวกัน

        # เพิ่ม GPT Bridge
        from reflexos_gpt_bridge import ReflexOSGPTBridge
        self.gpt_bridge = ReflexOSGPTBridge(
            memory_path=CONFIG['memory_base_path'])

        # Create Flask app
        self.app = Flask(__name__, template_folder='../templates')

        # Setup routes
        self.setup_routes()

    def setup_routes(self):
        @self.app.route('/')
        def index():
            return render_template('index.html')

        @self.app.route('/api/chat', methods=['POST'])
        def chat():
            data = request.json
            user_input = data.get('message', '')
            user_id = data.get('user_id', CONFIG['user_id'])

            # ใช้ GPT Bridge แทนการประมวลผลแบบเดิม
            result = self.gpt_bridge.process_message(user_input, user_id)

            # ดึงข้อมูลจากผลลัพธ์
            final_response = result["response"]
            detected_emotion = result["emotion"]

            # ยังคงใช้ระบบ Memory Core ด้วย เพื่อรักษาความเข้ากันได้กับระบบเดิม
            self.memory_core.store_user_interaction(
                user_input, final_response, detected_emotion)

            # Return response
            return jsonify({
                "response": final_response,
                "emotion": detected_emotion,
                "memory_stats": self.memory_core.get_memory_summary()
            })

        @self.app.route('/api/memory_stats', methods=['GET'])
        def get_memory_stats():
            memory_stats = self.memory_core.get_memory_summary()
            emotion_trends = self.emotion_system.get_emotion_trend()

            return jsonify({
                "memory": memory_stats,
                "emotion": emotion_trends
            })

        @self.app.route('/api/timeline', methods=['GET'])
        def get_timeline():
            limit = request.args.get('limit', 10, type=int)
            timeline = self.context_system.get_conversation_timeline(limit)

            return jsonify({
                "timeline": timeline
            })

        @self.app.route('/api/journal', methods=['POST'])
        def create_journal():
            data = request.json
            period = data.get('period', 'day')  # day, week, month

            journal_result = self.memory_core.create_memory_journal(period)

            return jsonify(journal_result)

        @self.app.route('/api/emotion/report', methods=['POST'])
        def create_emotion_report():
            data = request.json
            period = data.get('period', 'day')  # day, week, month

            report = self.emotion_system.generate_emotion_report(period)

            return jsonify({
                "report": report
            })

    def run(self, host='0.0.0.0', port=5000, debug=True):
        if CONFIG['log_interactions']:
            print(
                f"Starting Betty AI with Memory Core, Emotion System and Context Awareness")
            print(f"Server running on http://{host}:{port}")

        # Run Flask app
        self.app.run(host=host, port=port, debug=debug)


# --- Main Entry Point ---
if __name__ == "__main__":
    import argparse

    # Parse arguments
    parser = argparse.ArgumentParser(
        description='Betty AI with Memory and Emotions')
    parser.add_argument(
        '--port',
        type=int,
        default=5000,
        help='Port to run server on')
    parser.add_argument(
        '--host',
        type=str,
        default='0.0.0.0',
        help='Host to run server on')
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Run in debug mode')
    parser.add_argument('--user', type=str, default='user_a', help='User ID')

    args = parser.parse_args()

    # Update config with args
    CONFIG['user_id'] = args.user

    # Create and run server
    server = IntegratedServer()
    server.run(host=args.host, port=args.port, debug=args.debug)
