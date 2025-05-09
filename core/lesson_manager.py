
import json
import os


class LessonManager:
    def __init__(self, lesson_folder='./lessons'):
        self.lesson_folder = lesson_folder
        self.loaded_packs = {}
        self.load_all_lessons()

    def load_all_lessons(self):
        if not os.path.exists(self.lesson_folder):
            print(f"Lesson folder not found: {self.lesson_folder}")
            return

        for filename in os.listdir(self.lesson_folder):
            if filename.endswith('.json'):
                path = os.path.join(self.lesson_folder, filename)
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        pack_name = data.get("pack_name", filename)
                        self.loaded_packs[pack_name] = data
                        print(
                            f"[LessonManager] Loaded lesson pack: {pack_name}")
                except Exception as e:
                    print(f"[LessonManager] Failed to load {filename}: {e}")

    def find_matching_lesson(self, user_input):
        for pack in self.loaded_packs.values():
            for lesson in pack.get("lessons", []):
                for keyword in lesson.get("trigger_keywords", []):
                    if keyword in user_input.lower():
                        return lesson
        return None

    def get_response(self, user_input):
        lesson = self.find_matching_lesson(user_input)
        if lesson:
            responses = lesson.get("response_templates", [])
            if responses:
                import random
                return random.choice(responses)
        return None
