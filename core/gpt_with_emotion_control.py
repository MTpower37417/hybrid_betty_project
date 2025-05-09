# gpt_with_emotion_control.py

from betty_emotion_filter import filter_prompt_by_emotion
from betty_emotion_temperature_mapper import map_emotion_to_temperature
from reflexos_gpt_bridge import generate_gpt_response


def gpt_reply_with_emotion(user_input, emotion="neutral"):
    try:
        # Filter emotional tone into prompt
        emotional_prompt = filter_prompt_by_emotion(user_input, emotion)
        # Convert emotion to temperature safely
        temperature = map_emotion_to_temperature(emotion)
        # Send to GPT
        return generate_gpt_response(emotional_prompt, temperature=temperature)
    except Exception as e:
        return f"[Emotion GPT Error] {str(e)}"
