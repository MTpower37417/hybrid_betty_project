# betty_auto_feedback_hook.py

from trainer_bridge import learn_from_feedback


def auto_feedback_hook(user_input, gpt_output, rating="perfect"):
    try:
        learn_from_feedback(user_input, gpt_output, rating)
        return True
    except Exception as e:
        print(f"[AutoTrainer] Logging failed: {e}")
        return False
