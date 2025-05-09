# betty_emotion_temperature_mapper.py

def map_emotion_to_temperature(emotion):
    mapping = {
        "sad": 0.5,
        "happy": 0.9,
        "angry": 0.3,
        "insecure": 0.6,
        "neutral": 0.7
    }
    return mapping.get(emotion.lower(), 0.7)
