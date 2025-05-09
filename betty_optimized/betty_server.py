from reflex_integration import ReflexIntegration
from flask import Flask, jsonify, request, send_file
from emotion_analyzer import EmotionAnalyzer
from capsule_memory import CapsuleMemory
from capsule_manager import CapsuleManager
from betty_memory import BettyMemory
from betty_gpt_bridge import BettyGPTBridge
from betty_context import BettyContext
from datetime import datetime
import os
import sys

sys.path.insert(0, os.getcwd())  # รองรับ Git Bash, CMD, PowerShell


MEMORY_PATH = "./memory"

app = Flask(__name__)
gpt_bridge = BettyGPTBridge()
memory = BettyMemory()
context = BettyContext()
emotion_analyzer = EmotionAnalyzer()
reflex = ReflexIntegration()
capsule_memory = CapsuleMemory()
capsule_manager = CapsuleManager()


@app.route('/')
def index():
    return send_file('index.html')


@app.route('/api/capsules/search', methods=['POST'])
def search_capsules():
    data = request.json
    keyword = data.get('keyword', '')
    results = capsule_manager.search_by_keyword(keyword)
    return jsonify({"capsules": results})


@app.route('/api/capsules/emotions', methods=['GET'])
def get_emotion_summary():
    summary = capsule_manager.get_emotion_summary()
    return jsonify(summary)


@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    message = data.get('message', '')

    relevant_memories = memory.get_relevant_memories(message)
    relevant_contexts = context.search_context(message)

    gpt_context = []
    for key, value in relevant_contexts:
        gpt_context.append({"role": "system",
                            "content": f"บริบทที่เกี่ยวข้อง: {key} - {value}"})

    if relevant_memories:
        for mem in relevant_memories:
            if 'message' in mem and 'response' in mem:
                gpt_context.append({"role": "user", "content": mem["message"]})
                gpt_context.append(
                    {"role": "assistant", "content": mem["response"]})

    if "เก็บบริบท:" in message:
        parts = message.split("เก็บบริบท:", 1)
        if len(parts) > 1 and ":" in parts[1]:
            key_value = parts[1].strip().split(":", 1)
            if len(key_value) == 2:
                context.add_context(key_value[0].strip(), key_value[1].strip())

    detected_emotion = emotion_analyzer.analyze_emotion(message)
    emotion_analyzer.log_emotion(message, detected_emotion)

    gpt_response = gpt_bridge.generate_response(message, gpt_context)

    memory.store_interaction(message, gpt_response, emotion=detected_emotion)

    reflex.save_to_capsule(message, gpt_response, detected_emotion)
    reflex.sync_emotions({
        "emotion": detected_emotion,
        "text": message,
        "timestamp": datetime.now().isoformat()
    })

    capsule_data = {
        "message": message,
        "response": gpt_response,
        "emotion": detected_emotion
    }
    capsule_memory.create_capsule(capsule_data)

    return jsonify({
        "response": gpt_response,
        "emotion": detected_emotion
    })


if __name__ == "__main__":
    print("กำลังเริ่มต้น Betty AI Optimized...")
    app.run(host='0.0.0.0', port=8080, debug=True)
