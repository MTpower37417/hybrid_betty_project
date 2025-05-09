import json
import os

LOG_PATH = "trainer/training_data.jsonl"


def log_feedback(user_input, gpt_response, feedback="correct"):
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        entry = {
            "input": user_input,
            "response": gpt_response,
            "feedback": feedback}
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
