import os

import openai

except Exception as e:
    return f"GPT Error: {str(e)}"


class ReflexOSGPTBridge:
    def __init__(self, memory_path=None):
        self.use_gpt = True
        self.memory_path = memory_path

    def process_message(self, user_input, context=None):
        if not self.use_gpt:
            return "Betty without GPT: " + user_input
        return generate_gpt_response(user_input)


def generate_gpt_response(msg, context=None):
    try:
        import os

        import openai

        api_key = ""
        if os.path.exists(".env"):
            with open(".env", "r") as f:
                for line in f:
                    if line.startswith("OPENAI_API_KEY="):
                        api_key = line.split("=")[1].strip()

        if not api_key:
            return "ไม่พบ API Key กรุณาตรวจสอบไฟล์ .env"

        openai.api_key = api_key

        system_content = "คุณคือ Betty AI ผู้ช่วยที่ฉลาด อบอุ่น และจดจำบริบทของผู้ใช้"
        messages = [{"role": "system", "content": system_content}]

        # ฝัง memory context แบบ chat log
        if context:
            for entry in context:
                memory_msg = entry.get("message", "").strip()
                if memory_msg:
                    messages.append({"role": "user", "content": memory_msg})

        # ข้อความล่าสุดจากผู้ใช้
        messages.append({"role": "user", "content": msg})

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=0.7
        )

        return response.choices[0].message["content"]

    except Exception as e:
        return f"GPT Error: {str(e)}"
