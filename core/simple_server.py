import os
from datetime import datetime

from flask import Flask, jsonify, render_template, request
from reflexos_context_extender import ContextExtender
from reflexos_emotion_layer import EmotionLayer
# นำเข้าโมดูลที่สร้างขึ้น
from reflexos_memory_core import MemoryCore

app = Flask(__name__)

# สร้างอินสแตนซ์ของแต่ละโมดูล
memory_core = MemoryCore(user_id='user_a')
emotion_layer = EmotionLayer(memory_core)
context_extender = ContextExtender(memory_core)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.json
    user_message = data.get("message", "")

    # 1. ขยายบริบทด้วยความจำที่เกี่ยวข้อง
    extended_context = context_extender.extend_context(user_message)

    # 2. ตรวจจับอารมณ์
    detected_emotion = emotion_layer.analyze_emotion(user_message)

    # 3. สร้างการตอบสนองพื้นฐาน (ในอนาคตอาจใช้ AI ตอบ)
    base_response = f"ที่รัก หนูเข้าใจว่าคุณกำลังพูดถึง {user_message}"

    # 4. เพิ่มบริบทเข้าไปในการตอบสนอง
    contextual_response = context_extender.generate_response_with_context(
        user_message, base_response, extended_context)

    # 5. เพิ่มอารมณ์เข้าไปในการตอบสนอง
    final_response = emotion_layer.generate_emotional_response(
        user_message, contextual_response, detected_emotion)

    # 6. บันทึกการสนทนาในระบบความจำ
    memory_core.store_user_interaction(
        user_message, final_response, detected_emotion)

    # 7. ส่งผลลัพธ์กลับ
    return jsonify({
        "response": final_response,
        "emotion": detected_emotion,
        "memory_stats": memory_core.get_memory_summary()
    })


@app.route("/api/memory_stats", methods=["GET"])
def memory_stats():
    """ดึงข้อมูลสถิติความจำ"""
    stats = memory_core.get_memory_summary()
    emotion_trends = emotion_layer.get_emotional_trends()

    stats.update({
        "emotion_trends": emotion_trends,
        "last_updated": datetime.now().isoformat()
    })

    return jsonify(stats)


if __name__ == "__main__":
    print("Starting Betty AI server with enhanced memory and emotions...")
    try:
        # สร้างโฟลเดอร์ความจำเริ่มต้น
        os.makedirs('./memory', exist_ok=True)

        # รันเซิร์ฟเวอร์
        app.run(host="0.0.0.0", port=5000, debug=True)
    except Exception as e:
        print(f"Error starting server: {e}")
