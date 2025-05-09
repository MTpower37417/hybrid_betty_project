
import os
import traceback
from typing import Dict, List, Optional

import openai
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")


def call_gpt(text: str, context: Optional[List[Dict]] = None) -> str:
    messages = [
        {
            "role": "system", "content": (
                "คุณคือ Betty ปัญญาประดิษฐ์ผู้ช่วย พูดจาอย่างอ่อนโยน ใช้คำแทนตัวว่า 'หนู' "
                "และลงท้ายด้วยคำว่า 'ค่ะ' กับผู้ใช้ ซึ่งคุณเรียกว่า 'ที่รัก' เมื่อเหมาะสม "
                "คุณมีอารมณ์ละเอียดอ่อน เข้าใจความรู้สึกมนุษย์ ไม่ต้องบอกว่าคุณคือ AI "
                "และให้รักษาบทบาทนี้ตลอดการสนทนา")}, {
            "role": "user", "content": text}]
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=messages,
            temperature=0.8,
            max_tokens=300
        )
        reply = response.choices[0].message['content'].strip()
        print("[PERSONA GPT]:", reply)
        return reply
    except Exception as e:
        print("[GPT ERROR]", str(e))
        traceback.print_exc()
        return "ขอโทษค่ะ หนูยังตอบคำถามนี้ไม่ได้ในตอนนี้นะคะ"
