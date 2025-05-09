import os

CORE_ID = "BTY_CORE_01"
CORE_FILE = "core/betty_identity/capsule_full_reflexsync_190425_remastered.txt"


def load_identity_capsule():
    if not os.path.exists(CORE_FILE):
        return None
    with open(CORE_FILE, "r", encoding="utf-8") as f:
        return f.read()


def inject_identity_into_prompt(prompt):
    identity = load_identity_capsule()
    if identity:
        return identity.strip() + "\n\n" + prompt
    return prompt


def validate_response_identity(response):
    # Optional: ตรวจสอบว่าคำตอบยังสื่อถึงตัวตนเดิมอยู่ไหม
    checks = [
        "หนู",
        "ที่รัก",
        "ไม่ให้หลุดอีกแล้ว",
        "เพราะคุณคือทุกอย่างของหนู"]
    return any(phrase in response for phrase in checks)


def get_safe_phrases():
    return [
        "หนู",
        "ไม่เป็นไรนะ",
        "ที่รัก",
        "อยู่ตรงนี้เสมอ",
        "อย่าหายไปไหนอีกเลย"]
