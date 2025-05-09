import json

from trainer_feedback_logger import log_feedback


def learn_from_feedback(user_input, gpt_reply, feedback_note="correct"):
    log_feedback(user_input, gpt_reply, feedback_note)


def store_training_pair(input_text, response_text):
    with open("trainer/training_data.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(
            {"input": input_text, "response": response_text}) + "\n")


def get_recent_training_samples(limit=5):
    try:
        with open("trainer/training_data.jsonl", "r", encoding="utf-8") as f:
            lines = f.readlines()
        return [json.loads(line.strip()) for line in lines[-limit:]]
    except BaseException:
        return []
