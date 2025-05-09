
import os
import traceback
from typing import Dict, List, Optional

import openai
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")


def call_gpt(text: str, context: Optional[List[Dict]] = None) -> str:
    messages = [
        {"role": "system", "content": "คุณคือ Betty พูดไทย สุภาพ ฉลาด อ่อนโยน"},
        {"role": "user", "content": text}
    ]
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=messages,
            temperature=0.7,
            max_tokens=300
        )
        reply = response.choices[0].message['content'].strip()
        print("[DEBUG GPT content]:", reply)
        return reply
    except Exception as e:
        print("[GPT ERROR]", str(e))
        traceback.print_exc()
        return "ขออภัยค่ะ มีข้อผิดพลาดเกิดขึ้นระหว่างประมวลผล GPT"
