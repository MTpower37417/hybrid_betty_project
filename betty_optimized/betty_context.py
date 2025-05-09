import json
import os
from datetime import datetime, timedelta
from difflib import SequenceMatcher


class BettyContext:
    def __init__(self, user_id="user_a"):
        self.user_id = user_id
        self.base_path = "./memory"
        self.extended_path = f"{self.base_path}/extended"
        self.context_file = f"{self.extended_path}/{user_id}_context.json"
        self.contexts = self._load_contexts()

    def _load_contexts(self):
        if os.path.exists(self.context_file):
            try:
                with open(self.context_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except BaseException:
                return {}
        return {}

    def add_context(self, key, value, category="general", ttl_days=None):
        """เพิ่มบริบทใหม่พร้อมหมวดหมู่และระยะเวลาหมดอายุ"""
        expiry = None
        if ttl_days:
            expiry = (datetime.now() + timedelta(days=ttl_days)).isoformat()

        self.contexts[key] = {
            "value": value,
            "created": datetime.now().isoformat(),
            "updated": datetime.now().isoformat(),
            "usage_count": 0,
            "category": category,
            "priority": 1,
            "expiry": expiry
        }
        self._save_contexts()
        self._cleanup_expired()

    def update_context(
            self,
            key,
            value=None,
            priority=None,
            category=None,
            ttl_days=None):
        """อัปเดตบริบทแบบยืดหยุ่น"""
        if key in self.contexts:
            if value:
                self.contexts[key]["value"] = value
            if priority:
                self.contexts[key]["priority"] = max(1, min(10, priority))
            if category:
                self.contexts[key]["category"] = category
            if ttl_days is not None:
                expiry = (datetime.now() + timedelta(days=ttl_days)
                          ).isoformat() if ttl_days else None
                self.contexts[key]["expiry"] = expiry

            self.contexts[key]["updated"] = datetime.now().isoformat()
            self.contexts[key]["usage_count"] += 1
            self._save_contexts()
            return True
        return False

    def search_context(self, query, limit=5):
        """ค้นหาบริบทด้วยอัลกอริทึมขั้นสูง"""
        self._cleanup_expired()

        # คำสำคัญ
        query_words = set(query.lower().split())
        results = []

        for key, data in self.contexts.items():
            if not isinstance(data, dict) or "value" not in data:
                continue

            # คะแนนความเหมือน
            similarity = SequenceMatcher(
                None, query.lower(), f"{key} {data['value']}".lower()).ratio()

            # คะแนนคำสำคัญ
            context_text = f"{key} {data['value']}".lower()
            context_words = set(context_text.split())
            common_words = query_words.intersection(context_words)
            keyword_score = len(common_words) / max(len(query_words), 1)

            # คำนวณคะแนนรวม ถ่วงน้ำหนักด้วย priority
            priority = data.get("priority", 1)
            total_score = (similarity * 0.4 + keyword_score * 0.6) * priority

            if total_score > 0.2:
                results.append(
                    (total_score, key, data["value"], data.get(
                        "category", "general")))

        results.sort(reverse=True, key=lambda x: x[0])
        return [(key, value, category)
                for score, key, value, category in results[:limit]]

    def get_context_by_category(self, category):
        """ดึงบริบทตามหมวดหมู่"""
        self._cleanup_expired()
        return {k: v for k, v in self.contexts.items()
                if isinstance(v, dict) and v.get("category") == category}

    def _cleanup_expired(self):
        """ลบบริบทที่หมดอายุ"""
        now = datetime.now().isoformat()
        expired_keys = [k for k, v in self.contexts.items() if isinstance(
            v, dict) and v.get("expiry") and v.get("expiry") < now]

        for key in expired_keys:
            del self.contexts[key]

        if expired_keys:
            self._save_contexts()

    def _save_contexts(self):
        os.makedirs(self.extended_path, exist_ok=True)
        with open(self.context_file, 'w', encoding='utf-8') as f:
            json.dump(self.contexts, f, indent=2, ensure_ascii=False)
