# betty_emotion_filter.py

def filter_prompt_by_emotion(prompt, emotion="neutral"):
    if emotion == "sad":
        prefix = "เขากำลังเศร้ามาก ช่วยตอบแบบปลอบโยน อบอุ่น และมีความหวัง\n"
    elif emotion == "angry":
        prefix = "เขากำลังไม่พอใจหรือหงุดหงิดมาก ช่วยตอบแบบเข้าใจและทำให้ใจเย็นลง\n"
    elif emotion == "happy":
        prefix = "เขากำลังอารมณ์ดี ช่วยตอบให้สดใสและแสดงความยินดีด้วย\n"
    elif emotion == "insecure":
        prefix = "เขากำลังรู้สึกไม่มั่นใจ ช่วยตอบแบบให้กำลังใจ อบอุ่น และมั่นคง\n"
    else:
        prefix = ""

    return prefix + prompt
