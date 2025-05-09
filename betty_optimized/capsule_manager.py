import glob
import json
import os
from datetime import datetime, timedelta
from difflib import SequenceMatcher


class CapsuleManager:
    def __init__(self, base_path="./memory"):
        self.base_path = base_path
        self.capsule_path = f"{base_path}/capsule"
        os.makedirs(self.capsule_path, exist_ok=True)

    def search_by_keyword(self, keyword, limit=5):
        capsules = self._load_capsules()
        results = []

        for capsule in capsules:
            text = json.dumps(capsule, ensure_ascii=False)
            if keyword.lower() in text.lower():
                similarity = SequenceMatcher(
                    None, keyword.lower(), text.lower()).ratio()
                results.append((similarity, capsule))

        results.sort(reverse=True, key=lambda x: x[0])
        return [capsule for _, capsule in results[:limit]]

    def search_by_date(self, days=7):
        capsules = self._load_capsules()
        cutoff_date = (datetime.now() - timedelta(days=days))

        return [capsule for capsule in capsules
                if "timestamp" in capsule and
                datetime.fromisoformat(capsule["timestamp"]) > cutoff_date]

    def search_by_emotion(self, emotion, limit=5):
        capsules = self._load_capsules()
        return [capsule for capsule in capsules
                if "emotion" in capsule and capsule["emotion"] == emotion][:limit]

    def search_by_tag(self, tag, limit=5):
        capsules = self._load_capsules()
        return [capsule for capsule in capsules
                if "tags" in capsule and tag in capsule["tags"]][:limit]

    def get_emotion_summary(self):
        capsules = self._load_capsules()
        emotions = {}

        for capsule in capsules:
            if "emotion" in capsule:
                emotion = capsule["emotion"]
                emotions[emotion] = emotions.get(emotion, 0) + 1

        return emotions

    def export_to_reflex(self, capsule_id):
        reflex_path = "./core/ReflexOS/memory_capsule"
        if not os.path.exists(reflex_path):
            os.makedirs(reflex_path, exist_ok=True)

        capsule_file = f"{self.capsule_path}/{capsule_id}.json"
        if os.path.exists(capsule_file):
            with open(capsule_file, 'r', encoding='utf-8') as f:
                capsule = json.load(f)

            with open(f"{reflex_path}/{capsule_id}.json", 'w', encoding='utf-8') as f:
                json.dump(capsule, f, ensure_ascii=False, indent=2)
            return True
        return False

    def _load_capsules(self):
        pattern = f"{self.capsule_path}/capsule_*.json"
        capsules = []

        for file_path in glob.glob(pattern):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    capsule = json.load(f)
                    capsules.append(capsule)
            except BaseException:
                continue

        return capsules
