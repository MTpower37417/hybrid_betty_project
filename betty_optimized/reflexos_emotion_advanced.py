import json
import os
import random
from datetime import datetime


class EmotionAdvanced:
    def __init__(self, memory_core=None):
        self.memory_core = memory_core

        # ระดับความเข้มของอารมณ์
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

        # คำที่บ่งบอกอารมณ์ (ไทย-อังกฤษ)
        self.emotion_keywords = {
            "joy": [
                # ไทย
                "สนุก", "ดีใจ", "มีความสุข", "สุข", "ยินดี", "ยิ้ม", "หัวเราะ", "สุขใจ", "ปลื้ม", "ตื่นเต้น",
                # อังกฤษ
                "happy", "joy", "pleased", "glad", "delighted", "excited", "thrilled", "wonderful", "fun", "enjoy"
            ],
            "sadness": [
                # ไทย
                "เศร้า", "เสียใจ", "ผิดหวัง", "สิ้นหวัง", "หดหู่", "ร้องไห้", "น้ำตา", "ทุกข์", "เจ็บใจ",
                # อังกฤษ
                "sad", "upset", "disappointed", "unhappy", "depressed", "blue", "down", "hurt", "pain", "crying"
            ],
            "anger": [
                # ไทย
                "โกรธ", "หงุดหงิด", "ฉุนเฉียว", "โมโห", "เดือด", "แค้น", "เคือง", "ไม่พอใจ", "รำคาญ",
                # อังกฤษ
                "angry", "mad", "furious", "annoyed", "irritated", "frustrated", "rage", "hate", "resent"
            ],
            "fear": [
                # ไทย
                "กลัว", "หวาดกลัว", "วิตก", "กังวล", "ตื่นกลัว", "ตกใจ", "หวาดระแวง", "ตื่นตระหนก",
                # อังกฤษ
                "scared", "afraid", "worried", "anxious", "terrified", "frightened", "panic", "terror"
            ],
            "surprise": [
                # ไทย
                "ประหลาดใจ", "ตกใจ", "อึ้ง", "ทึ่ง", "อัศจรรย์", "ไม่เชื่อ", "ตะลึง",
                # อังกฤษ
                "surprised", "shocked", "amazed", "astonished", "wow", "unexpected", "startled"
            ],
            "love": [
                # ไทย
                "รัก", "ชอบ", "หลงรัก", "รักใคร่", "เสน่หา", "ปรารถนา", "อบอุ่น", "ทะนุถนอม", "ผูกพัน", "คิดถึง",
                # อังกฤษ
                "love", "adore", "fond", "affection", "caring", "cherish", "devoted", "miss", "desire"
            ],
            "disgust": [
                # ไทย
                "รังเกียจ", "ขยะแขยง", "สะอิดสะเอียน", "เกลียด", "คลื่นไส้",
                # อังกฤษ
                "disgusted", "revolted", "gross", "yuck", "nasty", "repulsed"
            ],
            "neutral": [
                # ไทย
                "ปกติ", "เฉยๆ", "ธรรมดา", "ไม่เป็นไร", "พอใช้", "ก็ได้",
                # อังกฤษ
                "neutral", "fine", "okay", "alright", "so-so", "normal"
            ],
            "curious": [
                # ไทย
                "สงสัย", "อยากรู้", "สนใจ", "ทำไม", "ยังไง", "อย่างไร", "อะไร", "เหตุใด",
                # อังกฤษ
                "curious", "wonder", "interested", "why", "how", "what", "question"
            ],
            "disappointed": [
                # ไทย
                "ผิดหวัง", "ไม่เป็นไปตามที่คิด", "ไม่สมหวัง", "พลาด", "ละทิ้ง",
                # อังกฤษ
                "disappointed", "letdown", "failed", "unfulfilled", "dismayed"
            ],
            "hopeful": [
                # ไทย
                "หวัง", "มีความหวัง", "คาดหวัง", "ฝัน", "ดีขึ้น", "โอกาส", "อนาคต",
                # อังกฤษ
                "hope", "hopeful", "optimistic", "looking forward", "positive", "expecting"
            ],
            "frustrated": [
                # ไทย
                "หงุดหงิด", "อึดอัด", "ไม่พอใจ", "ติดขัด", "สับสน", "วุ่นวาย", "ยุ่งยาก",
                # อังกฤษ
                "frustrated", "stuck", "blocked", "annoyed", "bothered", "difficulty"
            ],
            "relaxed": [
                # ไทย
                "ผ่อนคลาย", "สบาย", "สงบ", "เย็น", "พักผ่อน", "สบายใจ", "ไม่เครียด",
                # อังกฤษ
                "relaxed", "calm", "peaceful", "chill", "easy", "comfortable", "serene"
            ]
        }

        # อีโมจิสำหรับอารมณ์
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

        # รูปแบบการตอบสนองตามอารมณ์
        self.response_templates = {
            "joy": [
                "ดีใจจังเลยที่ {response} {emoji}",
                "สนุกจัง! {response} {emoji}",
                "{response} ฉันรู้สึกมีความสุขมากๆ {emoji}",
                "สุดยอดเลย! {response} {emoji}"
            ],
            "sadness": [
                "{response} ฉันเข้าใจความรู้สึกของคุณนะ {emoji}",
                "ฉันเสียใจด้วย... {response} {emoji}",
                "{response} ถ้ามีอะไรให้ช่วย บอกฉันได้เลยนะ {emoji}",
                "ฉันอยู่ตรงนี้เสมอถ้าคุณต้องการ {response} {emoji}"
            ],
            "anger": [
                "{response} ฉันเข้าใจว่าคุณรู้สึกไม่พอใจ {emoji}",
                "ลองใจเย็นๆ ก่อนนะ {response} {emoji}",
                "{response} เรามาคุยกันดีๆ นะ {emoji}",
                "ฉันเข้าใจความรู้สึกของคุณ {response} {emoji}"
            ],
            "fear": [
                "ไม่ต้องกังวลนะ {response} {emoji}",
                "{response} ฉันอยู่ตรงนี้เสมอ {emoji}",
                "ทุกอย่างจะเรียบร้อย {response} {emoji}",
                "{response} ลองหายใจลึกๆ ดูนะ {emoji}"
            ],
            "surprise": [
                "ว้าว! {response} {emoji}",
                "เยี่ยมไปเลย! {response} {emoji}",
                "{response} น่าทึ่งจริงๆ {emoji}",
                "นั่นสุดยอดมาก! {response} {emoji}"
            ],
            "love": [
                "{response} ฉันรักคุณเช่นกัน {emoji}",
                "ที่รัก {response} {emoji}",
                "{response} ฉันรู้สึกอบอุ่นใจเสมอเวลาอยู่กับคุณ {emoji}",
                "คุณทำให้ฉันมีความสุขมาก {response} {emoji}"
            ],
            "disgust": [
                "{response} ฉันเข้าใจความรู้สึกของคุณ {emoji}",
                "ใช่ มันไม่น่าพิจารณาเลย {response} {emoji}",
                "{response} เราไม่ต้องคุยเรื่องนี้ต่อก็ได้นะ {emoji}",
                "ฉันเข้าใจว่าเรื่องนี้ทำให้คุณรู้สึกไม่ดี {response} {emoji}"
            ],
            "neutral": [
                "{response} {emoji}",
                "เข้าใจแล้ว {response} {emoji}",
                "{response} มีอะไรให้ช่วยอีกไหม {emoji}",
                "โอเค {response} {emoji}"
            ],
            "curious": [
                "น่าสนใจจังเลย! {response} {emoji}",
                "{response} ฉันก็สงสัยเหมือนกัน {emoji}",
                "คำถามที่ดีมาก {response} {emoji}",
                "{response} ลองมาสำรวจเรื่องนี้ด้วยกันดีไหม {emoji}"
            ],
            "disappointed": [
                "{response} ฉันเข้าใจความรู้สึกของคุณ {emoji}",
                "ฉันเสียใจที่ได้ยินแบบนั้น {response} {emoji}",
                "{response} หวังว่าครั้งหน้าจะดีกว่านี้นะ {emoji}",
                "เข้าใจความรู้สึกของคุณ {response} {emoji}"
            ],
            "hopeful": [
                "{response} มองโลกในแง่ดีไว้นะ {emoji}",
                "ฉันเชื่อว่าคุณทำได้! {response} {emoji}",
                "{response} อนาคตสดใสรออยู่ข้างหน้า {emoji}",
                "เราต้องมองไปข้างหน้า {response} {emoji}"
            ],
            "frustrated": [
                "{response} ฉันเข้าใจว่ามันน่าหงุดหงิด {emoji}",
                "ใจเย็นๆ นะ {response} {emoji}",
                "{response} บางครั้งก็เป็นแบบนี้แหละ แต่เราจะผ่านมันไปด้วยกัน {emoji}",
                "ลองหายใจลึกๆ {response} {emoji}"
            ],
            "relaxed": [
                "{response} ดีใจที่คุณรู้สึกผ่อนคลาย {emoji}",
                "สบายใจไว้นะ {response} {emoji}",
                "{response} บรรยากาศสงบดีจริงๆ {emoji}",
                "เยี่ยมมาก {response} {emoji}"
            ]
        }

        # ประวัติอารมณ์
        self.emotion_history = []

        # ไฟล์บันทึกอารมณ์
        self.emotion_log_file = "./memory/emotion/emotion_log.json"
        os.makedirs("./memory/emotion", exist_ok=True)
        self._load_emotion_history()

    def _load_emotion_history(self):
        """โหลดประวัติอารมณ์จากไฟล์"""
        if os.path.exists(self.emotion_log_file):
            try:
                with open(self.emotion_log_file, 'r', encoding='utf-8') as f:
                    self.emotion_history = json.load(f)
            except BaseException:
                self.emotion_history = []

    def _save_emotion_history(self):
        """บันทึกประวัติอารมณ์ลงไฟล์"""
        try:
            with open(self.emotion_log_file, 'w', encoding='utf-8') as f:
                json.dump(self.emotion_history[-100:],
                          f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving emotion history: {e}")

    def detect_emotion(self, text):
        """ตรวจจับอารมณ์จากข้อความ"""
        text_lower = text.lower()
        emotion_scores = {}

        # คำนวณคะแนนสำหรับแต่ละอารมณ์
        for emotion, keywords in self.emotion_keywords.items():
            score = 0
            for keyword in keywords:
                if keyword.lower() in text_lower:
                    score += 1
            if score > 0:
                emotion_scores[emotion] = score

        # ถ้าไม่พบอารมณ์ใด ให้เป็นกลาง
        if not emotion_scores:
            return "neutral"

        # คืนค่าอารมณ์ที่มีคะแนนสูงสุด
        return max(emotion_scores.items(), key=lambda x: x[1])[0]

    def analyze_emotion_with_context(self, text, context=None):
        """วิเคราะห์อารมณ์โดยคำนึงถึงบริบท"""
        # ตรวจจับอารมณ์พื้นฐาน
        base_emotion = self.detect_emotion(text)

        # ถ้ามีบริบท ให้พิจารณาบริบทด้วย
        if context and self.memory_core:
            # ตรวจสอบความเชื่อมโยงกับความจำในบริบท
            if "related_memories" in context:
                # ดึงอารมณ์จากความจำที่เกี่ยวข้องล่าสุด
                recent_emotions = []
                for memory in context.get(
                        "related_memories", [])[:3]:  # พิจารณาแค่ 3 ความจำล่าสุด
                    if isinstance(memory, dict) and "emotion" in memory:
                        recent_emotions.append(memory["emotion"])

                # ถ้ามีอารมณ์จากความจำ
                if recent_emotions:
                    # ตรวจสอบว่าอารมณ์ปัจจุบันขัดแย้งกับอารมณ์ในความจำหรือไม่
                    opposite_emotions = {
                        "joy": ["sadness", "disappointed", "anger", "disgust"],
                        "sadness": ["joy", "hopeful", "relaxed"],
                        "anger": ["joy", "relaxed", "love"],
                        "fear": ["relaxed", "hopeful", "love"],
                        "surprise": [],  # ความประหลาดใจอาจเข้ากันได้กับทุกอารมณ์
                        "love": ["anger", "disgust", "hate"],
                        "disgust": ["joy", "love"],
                        "neutral": [],  # ความเป็นกลางเข้ากันได้กับทุกอารมณ์
                    }

                    # ถ้าอารมณ์ปัจจุบันขัดแย้งกับอารมณ์ในความจำ
                    if base_emotion in opposite_emotions:
                        for recent_emotion in recent_emotions:
                            if recent_emotion in opposite_emotions[base_emotion]:
                                # ปรับให้อารมณ์มีความซับซ้อนมากขึ้น (เช่น
                                # อาจเป็น hopeful แทน neutral)
                                if base_emotion == "neutral" and recent_emotion == "sadness":
                                    return "hopeful"
                                if base_emotion == "neutral" and recent_emotion == "anger":
                                    return "relaxed"

                    # ถ้าอารมณ์เป็นกลาง แต่บริบทมีอารมณ์ชัดเจน ให้คล้อยตามบริบท
                    if base_emotion == "neutral" and recent_emotions[0] != "neutral":
                        return recent_emotions[0]

        return base_emotion

    def get_emotion_emoji(self, emotion):
        """รับอีโมจิสำหรับอารมณ์ที่ระบุ"""
        if emotion in self.emotion_emoji:
            return random.choice(self.emotion_emoji[emotion])
        return "😊"  # อีโมจิเริ่มต้น

    def format_emotional_response(self, base_response, emotion):
        """จัดรูปแบบการตอบสนองตามอารมณ์"""
        # ตรวจสอบว่ามีเทมเพลตสำหรับอารมณ์นี้หรือไม่
        if emotion in self.response_templates:
            template = random.choice(self.response_templates[emotion])
            emoji = self.get_emotion_emoji(emotion)

            # ใส่การตอบสนองพื้นฐานในเทมเพลต
            return template.format(response=base_response, emoji=emoji)

        # ถ้าไม่มีเทมเพลต ใช้การตอบสนองพื้นฐานพร้อมอีโมจิ
        return f"{base_response} {self.get_emotion_emoji(emotion)}"

    def process_emotion(self, user_input, base_response, context=None):
        """ประมวลผลอารมณ์และจัดรูปแบบการตอบสนอง"""
        # วิเคราะห์อารมณ์
        emotion = self.analyze_emotion_with_context(user_input, context)

        # จัดรูปแบบการตอบสนองตามอารมณ์
        emotional_response = self.format_emotional_response(
            base_response, emotion)

        # บันทึกอารมณ์ในประวัติ
        self._record_emotion(user_input, base_response, emotion)

        # ส่งข้อมูลไปยังระบบความจำ (ถ้ามี)
        if self.memory_core:
            importance = self.emotion_intensity.get(emotion, 1.0)
            self.memory_core.adjust_memory_weight(user_input, importance)

        return {
            "response": emotional_response,
            "emotion": emotion,
            "intensity": self.emotion_intensity.get(emotion, 1.0)
        }

    def _record_emotion(self, user_input, response, emotion):
        """บันทึกอารมณ์ในประวัติ"""
        timestamp = datetime.now().isoformat()

        # สร้างรายการบันทึกอารมณ์
        emotion_entry = {
            "timestamp": timestamp,
            "input": user_input,
            "response": response,
            "emotion": emotion,
            "intensity": self.emotion_intensity.get(emotion, 1.0)
        }

        # เพิ่มเข้าในประวัติ
        self.emotion_history.append(emotion_entry)

        # บันทึกลงไฟล์
        self._save_emotion_history()

    def get_emotion_trend(self, limit=10):
        """รับแนวโน้มอารมณ์จากประวัติ"""
        recent_emotions = self.emotion_history[-limit:] if len(
            self.emotion_history) >= limit else self.emotion_history

        # นับความถี่ของแต่ละอารมณ์
        emotion_counts = {}
        for entry in recent_emotions:
            emotion = entry.get("emotion", "neutral")
            emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1

        # หาอารมณ์ที่พบบ่อยที่สุด
        dominant_emotion = "neutral"
        if emotion_counts:
            dominant_emotion = max(
                emotion_counts.items(),
                key=lambda x: x[1])[0]

        # คำนวณค่าเฉลี่ยความเข้มของอารมณ์
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
        """สร้างรายงานอารมณ์ตามช่วงเวลา"""
        now = datetime.now()

        # กำหนดช่วงเวลา
        if period == "day":
            # วันนี้
            start_time = now.replace(hour=0, minute=0, second=0, microsecond=0)
            title = f"รายงานอารมณ์ประจำวันที่ {now.strftime('%d/%m/%Y')}"
        elif period == "week":
            # 7 วันล่าสุด
            start_time = now.replace(hour=0, minute=0, second=0, microsecond=0)
            start_time = start_time.replace(
                day=start_time.day - start_time.weekday())
            title = f"รายงานอารมณ์ประจำสัปดาห์ {start_time.strftime('%d/%m/%Y')} - {now.strftime('%d/%m/%Y')}"
        else:  # month
            # เดือนนี้
            start_time = now.replace(
                day=1, hour=0, minute=0, second=0, microsecond=0)
            title = f"รายงานอารมณ์ประจำเดือน {now.strftime('%m/%Y')}"

        # กรองอารมณ์ในช่วงเวลา
        filtered_emotions = []
        for entry in self.emotion_history:
            try:
                entry_time = datetime.fromisoformat(entry.get("timestamp", ""))
                if entry_time >= start_time:
                    filtered_emotions.append(entry)
            except BaseException:
                continue

        # นับความถี่ของแต่ละอารมณ์
        emotion_counts = {}
        for entry in filtered_emotions:
            emotion = entry.get("emotion", "neutral")
            emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1

        # สร้างเนื้อหารายงาน
        report = f"{title}\n{'=' * len(title)}\n\n"

        if not filtered_emotions:
            report += "ไม่มีข้อมูลอารมณ์ในช่วงเวลานี้\n"
            return report

        # สรุปอารมณ์หลัก
        dominant_emotion = max(emotion_counts.items(), key=lambda x: x[1])[
            0] if emotion_counts else "neutral"
        report += f"อารมณ์หลัก: {dominant_emotion}\n\n"

        # แสดงความถี่ของแต่ละอารมณ์
        report += "ความถี่ของอารมณ์:\n"
        for emotion, count in sorted(
                emotion_counts.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / len(filtered_emotions)) * 100
            report += f"- {emotion}: {count} ครั้ง ({percentage:.1f}%)\n"

        # สรุปความเข้มของอารมณ์
        total_intensity = sum(entry.get("intensity", 1.0)
                              for entry in filtered_emotions)
        avg_intensity = total_intensity / len(filtered_emotions)
        report += f"\nความเข้มของอารมณ์เฉลี่ย: {avg_intensity:.2f}\n"

        # ตัวอย่างการสนทนาที่มีอารมณ์ชัดเจน
        report += "\nตัวอย่างการสนทนาที่มีอารมณ์ชัดเจน:\n"

        # เรียงลำดับตามความเข้มของอารมณ์
        filtered_emotions.sort(
            key=lambda x: x.get(
                "intensity", 1.0), reverse=True)

        # แสดงตัวอย่าง 3 รายการแรก
        for i, entry in enumerate(filtered_emotions[:3], 1):
            entry_time = datetime.fromisoformat(
                entry.get("timestamp", "")).strftime('%d/%m/%Y %H:%M')
            report += f"\n{i}. {entry_time} - อารมณ์: {entry.get('emotion', 'neutral')} (ความเข้ม: {entry.get('intensity', 1.0):.2f})\n"
            report += f"   คุณ: {entry.get('input', '')}\n"
            report += f"   Betty: {entry.get('response', '')}\n"

        return report

    def create_emotion_timeline(self, limit=24):
        """สร้างไทม์ไลน์อารมณ์ในช่วงเวลาที่กำหนด"""
        # ดึงรายการอารมณ์ล่าสุดตามจำนวนที่กำหนด
        recent_emotions = self.emotion_history[-limit:] if len(
            self.emotion_history) >= limit else self.emotion_history

        if not recent_emotions:
            return "ยังไม่มีข้อมูลอารมณ์"

        # จัดกลุ่มตามช่วงเวลา (เช่น ทุกๆ ชั่วโมง)
        emotion_by_hour = {}

        for entry in recent_emotions:
            try:
                entry_time = datetime.fromisoformat(entry.get("timestamp", ""))
                hour_key = entry_time.strftime('%Y-%m-%d %H:00')

                if hour_key not in emotion_by_hour:
                    emotion_by_hour[hour_key] = []

                emotion_by_hour[hour_key].append(
                    entry.get("emotion", "neutral"))
            except BaseException:
                continue

        # สร้างไทม์ไลน์
        timeline = []
        for hour_key, emotions in sorted(emotion_by_hour.items()):
            # หาอารมณ์ที่พบบ่อยที่สุดในแต่ละชั่วโมง
            emotion_counts = {}
            for emotion in emotions:
                emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1

            dominant_emotion = max(emotion_counts.items(), key=lambda x: x[1])[
                0] if emotion_counts else "neutral"

            # เพิ่มข้อมูลในไทม์ไลน์
            timeline.append({
                "time": hour_key,
                "dominant_emotion": dominant_emotion,
                "emotion_counts": emotion_counts,
                "total": len(emotions)
            })

        # แปลงเป็นข้อความ
        timeline_text = "ไทม์ไลน์อารมณ์:\n"
        timeline_text += "==================\n\n"

        for entry in timeline:
            emotion_emoji = self.get_emotion_emoji(entry["dominant_emotion"])
            timeline_text += f"{entry['time']}: {entry['dominant_emotion']} {emotion_emoji} ({entry['total']} รายการ)\n"

        return timeline_text

    def create_emotional_plot_data(self, limit=48):
        """สร้างข้อมูลสำหรับแผนภูมิอารมณ์"""
        recent_emotions = self.emotion_history[-limit:] if len(
            self.emotion_history) >= limit else self.emotion_history

        if not recent_emotions:
            return {"labels": [], "data": {}}

        # จัดกลุ่มตามช่วงเวลา (ทุกๆ ชั่วโมง)
        emotion_data = {}
        time_labels = []

        # กำหนดอารมณ์ที่จะติดตาม
        tracked_emotions = [
            "joy",
            "sadness",
            "anger",
            "fear",
            "love",
            "neutral"]

        # เตรียมโครงสร้างข้อมูล
        for emotion in tracked_emotions:
            emotion_data[emotion] = []

        # จัดกลุ่มตามเวลา
        hour_groups = {}

        for entry in recent_emotions:
            try:
                entry_time = datetime.fromisoformat(entry.get("timestamp", ""))
                hour_key = entry_time.strftime('%Y-%m-%d %H:00')

                if hour_key not in hour_groups:
                    hour_groups[hour_key] = {}
                    for emotion in tracked_emotions:
                        hour_groups[hour_key][emotion] = 0

                # เพิ่มจำนวนอารมณ์ในช่วงเวลา
                emotion = entry.get("emotion", "neutral")
                if emotion in tracked_emotions:
                    hour_groups[hour_key][emotion] += 1
                else:
                    # ถ้าเป็นอารมณ์อื่นๆ ที่ไม่ได้ติดตาม
                    # จัดเป็นประเภทที่ใกล้เคียง
                    if emotion in ["happy", "pleased", "excited"]:
                        hour_groups[hour_key]["joy"] += 1
                    elif emotion in ["disappointed", "upset"]:
                        hour_groups[hour_key]["sadness"] += 1
                    elif emotion in ["curious", "surprised"]:
                        hour_groups[hour_key]["neutral"] += 1
                    elif emotion in ["frustrated", "annoyed"]:
                        hour_groups[hour_key]["anger"] += 1
                    elif emotion in ["hopeful", "relaxed"]:
                        hour_groups[hour_key]["neutral"] += 1
                    else:
                        hour_groups[hour_key]["neutral"] += 1
            except BaseException:
                continue

        # จัดเรียงตามเวลา
        sorted_hours = sorted(hour_groups.keys())

        # เตรียมข้อมูลสำหรับแผนภูมิ
        for hour in sorted_hours:
            time_labels.append(hour)
            for emotion in tracked_emotions:
                emotion_data[emotion].append(hour_groups[hour][emotion])

        return {
            "labels": time_labels,
            "data": emotion_data
        }

    def suggest_emotional_response(self, user_emotion, context=None):
        """แนะนำวิธีการตอบสนองที่เหมาะสมกับอารมณ์ของผู้ใช้"""
        response_suggestions = {
            "joy": [
                "แสดงความยินดีและร่วมสนุกไปกับผู้ใช้",
                "ใช้ภาษาที่กระตือรือร้นและสนุกสนาน",
                "ชื่นชมหรือชมเชยในสิ่งที่ผู้ใช้พูดถึง"
            ],
            "sadness": [
                "แสดงความเห็นอกเห็นใจและเข้าใจความรู้สึก",
                "ให้กำลังใจและรับฟังด้วยความเข้าใจ",
                "เสนอความช่วยเหลือหรือมุมมองที่สร้างกำลังใจ"
            ],
            "anger": [
                "ตอบด้วยความสงบและพยายามลดความตึงเครียด",
                "แสดงความเข้าใจโดยไม่ตัดสินหรือตำหนิ",
                "ใช้ภาษาที่ชัดเจนแต่นุ่มนวล"
            ],
            "fear": [
                "แสดงความเข้าใจและให้ความมั่นใจ",
                "พูดถึงความกังวลด้วยท่าทีสงบและมั่นคง",
                "ให้ข้อมูลที่ช่วยลดความกังวล"
            ],
            "love": [
                "ตอบด้วยความอบอุ่นและใส่ใจ",
                "แสดงความชื่นชมและซาบซึ้ง",
                "ใช้คำพูดที่แสดงถึงความใกล้ชิดและความเข้าใจ"
            ],
            "neutral": [
                "ตอบด้วยข้อมูลที่เป็นประโยชน์และเป็นมิตร",
                "ใช้ภาษาที่เรียบง่ายและเข้าใจง่าย",
                "รักษาการสนทนาที่สมดุลและเป็นธรรมชาติ"
            ],
            "curious": [
                "ให้ข้อมูลที่น่าสนใจและครบถ้วน",
                "กระตุ้นการสนทนาด้วยคำถามที่น่าคิด",
                "แสดงความกระตือรือร้นในการให้ข้อมูล"
            ],
            "frustrated": [
                "แสดงความเข้าใจและความอดทน",
                "เสนอวิธีแก้ปัญหาอย่างเป็นขั้นตอน",
                "ใช้ภาษาที่ชัดเจนและมีโครงสร้าง"
            ]
        }

        # ดึงคำแนะนำที่เกี่ยวข้องกับอารมณ์
        suggestions = response_suggestions.get(
            user_emotion, response_suggestions["neutral"])

        # ปรับคำแนะนำตามบริบท (ถ้ามี)
        if context and "emotion_history" in context:
            # ถ้าผู้ใช้แสดงอารมณ์เดิมซ้ำๆ
            if len(context["emotion_history"]) > 2:
                recent_emotions = [e.get("emotion")
                                   for e in context["emotion_history"][-3:]]
                if all(e == user_emotion for e in recent_emotions) and user_emotion in [
                        "sadness", "anger", "frustrated"]:
                    suggestions.append(
                        "ลองเปลี่ยนทิศทางการสนทนาเพื่อช่วยเปลี่ยนอารมณ์")
                    suggestions.append(
                        "เสนอมุมมองใหม่หรือหัวข้อที่อาจช่วยยกระดับอารมณ์")

        return suggestions
