
from flask import Flask, jsonify, render_template, request
from gpt_trainer_gpt_enabled import BettyGPTTrainer

app = Flask(__name__)
trainer = BettyGPTTrainer(mode="train")


@app.route("/")
def index():
    return render_template("index.html", title="Betty GPT Web UI")


@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_input = data.get("message", "")
    print("[API] Message received:", user_input)

    try:
        result = trainer.process_interaction(user_input)
        print("[API] GPT Response:", result["response"])
        return jsonify({
            "response": result["response"],
            "emotion": result["emotion"],
            "pattern": result["pattern"],
            "capsule": result.get("memory_capsule", {})
        })
    except Exception as e:
        import traceback
        print("[API ERROR]", str(e))
        traceback.print_exc()
        return jsonify({
            "response": "เกิดข้อผิดพลาดขณะประมวลผล",
            "emotion": "error",
            "pattern": "error"
        }), 500


@app.route("/api/set_mode", methods=["POST"])
def set_mode():
    data = request.get_json()
    mode = data.get("mode", "train")
    trainer.set_mode(mode)
    return jsonify({"status": "success", "mode": mode})


if __name__ == "__main__":
    app.run(debug=True)
