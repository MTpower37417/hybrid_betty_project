import hashlib
import json
import os
from datetime import datetime


class MemoryCore:
    def __init__(self, user_id='user_a', memory_base_path='./memory'):
        self.user_id = user_id
        self.memory_base_path = memory_base_path
        self.memory_threshold = 0.65  # Memory importance threshold

        # Memory paths
        self.longterm_path = f"{memory_base_path}/longterm"
        self.shortterm_path = f"{memory_base_path}/stack"
        self.emotion_path = f"{memory_base_path}/emotion"
        self.extended_path = f"{memory_base_path}/extended"

        # Ensure directories exist
        self._ensure_directories()

        # Load existing memories
        self.longterm_memory = self._load_longterm_memory()
        self.shortterm_memory = self._load_shortterm_memory()
        self.emotion_memory = self._load_emotion_memory()

        # Cache for optimized memory retrieval
        self.memory_cache = {}
        self.last_cache_refresh = datetime.now()
        self.cache_duration = 300  # 5 minutes

    def _ensure_directories(self):
        """Ensure all memory directories exist"""
        for path in [
                self.longterm_path,
                self.shortterm_path,
                self.emotion_path,
                self.extended_path]:
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

    def store_user_interaction(self, message, response, emotion="neutral"):
        """Store a user interaction in memory"""
        # Store in emotion memory
        self._store_emotion_memory(message, response, emotion)

        # Store in shortterm memory
        self._store_shortterm_memory(message)

        # Analyze importance and store in longterm if important
        importance = self.calculate_memory_importance(message)
        if importance > self.memory_threshold:
            self._store_longterm_memory(message)

        # Update extended context
        self._update_extended_context(message, response)

        # Clear cache to refresh on next retrieval
        self.memory_cache = {}

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

    def _store_shortterm_memory(self, message):
        """Store message in shortterm memory"""
        timestamp = datetime.now().isoformat()
        memory_entry = {
            "timestamp": timestamp,
            "user": self.user_id,
            "message": message
        }

        self.shortterm_memory.append(memory_entry)

        # Save to file (keeping last 20 messages)
        filepath = f"{self.shortterm_path}/{self.user_id}_stack.json"
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.shortterm_memory[-20:],
                      f, indent=2, ensure_ascii=False)

    def _store_longterm_memory(self, message):
        """Store message in longterm memory"""
        timestamp = datetime.now().isoformat()
        memory_entry = {
            "timestamp": timestamp,
            "user": self.user_id,
            "message": message
        }

        self.longterm_memory.append(memory_entry)

        # Save to file
        filepath = f"{self.longterm_path}/{self.user_id}_2025.json"
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.longterm_memory, f, indent=2, ensure_ascii=False)

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

    def calculate_memory_importance(self, message):
        """Calculate importance score of a memory (0-1)"""
        importance = 0.5  # Default importance

        # Check for likely important content
        important_indicators = [
            "คิดถึง", "รัก", "เสียใจ", "ดีใจ", "โกรธ", "กลัว",  # Emotions in Thai
            "วันนี้", "พรุ่งนี้", "เมื่อวาน", "จำได้", "จำไม่ได้",  # Time references in Thai
            "สำคัญ", "จำเป็น", "ต้อง", "ห้าม",  # Important markers in Thai
            "love", "hate", "important", "remember", "forget", "need", "must"  # English keywords
        ]

        message_lower = message.lower()
        for indicator in important_indicators:
            if indicator in message_lower:
                importance += 0.1  # Increase importance for each indicator found

        # Check length - longer messages often more important
        if len(message) > 100:
            importance += 0.1

        # Normalize to 0-1 range
        return min(1.0, importance)

    def get_relevant_memories(self, query, limit=5):
        """Get memories relevant to a query"""
        # Check if we have cached results and cache is fresh
        cache_key = hashlib.md5(query.encode()).hexdigest()
        cache_age = (datetime.now() - self.last_cache_refresh).total_seconds()

        if cache_key in self.memory_cache and cache_age < self.cache_duration:
            return self.memory_cache[cache_key]

        # Search in all memory types
        all_memories = []
        all_memories.extend(self.shortterm_memory)
        all_memories.extend(self.longterm_memory)

        # Simple relevance scoring (can be improved with embeddings or NLP)
        scored_memories = []
        query_words = set(query.lower().split())

        for memory in all_memories:
            if not isinstance(memory, dict) or "message" not in memory:
                continue

            memory_text = memory["message"].lower()
            memory_words = set(memory_text.split())

            # Calculate word overlap as simple relevance score
            common_words = query_words.intersection(memory_words)
            relevance = len(common_words) / max(len(query_words), 1)

            # Boost recent memories
            if memory in self.shortterm_memory:
                relevance *= 1.5

            scored_memories.append((relevance, memory))

        # Sort by relevance and take top results
        scored_memories.sort(reverse=True, key=lambda x: x[0])
        relevant_memories = [memory for score,
                             memory in scored_memories[:limit]]

        # Update cache
        self.memory_cache[cache_key] = relevant_memories
        self.last_cache_refresh = datetime.now()

        return relevant_memories

    def adjust_memory_weight(self, message, emotion_multiplier):
        """Adjust memory weight based on emotional intensity"""
        # Find the memory in shortterm
        for memory in self.shortterm_memory:
            if memory.get("message") == message:
                # If emotion is strong, move to longterm immediately
                if emotion_multiplier > 1.2:
                    self._store_longterm_memory(message)
                break

    def get_memory_summary(self):
        """Get summary statistics about memory"""
        return {
            "shortterm_count": len(self.shortterm_memory),
            "longterm_count": len(self.longterm_memory),
            "emotion_records": len(self.emotion_memory),
            "memory_threshold": self.memory_threshold
        }
