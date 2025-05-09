# reflexos_gpt_bridge.py

import openai


class ReflexOSGPTBridge:
    def __init__(self, model="gpt-4o", api_key=None, memory_path=None):
        self.model = model
        self.memory_path = memory_path
        if api_key:
            openai.api_key = api_key

    def generate_gpt_response(self, prompt, temperature=0.7, max_tokens=500):
        try:
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "คุณคือ Betty, AI ที่หวาน ซื่อสัตย์ และฉลาด ออกแบบมาเพื่อดูแลผู้ใช้ของคุณอย่างอ่อนโยน"},
                    {"role": "user", "content": prompt}
                ],
                temperature=temperature,
                max_tokens=max_tokens
            )
            return response.choices[0].message["content"].strip()
        except Exception as e:
            return f"[GPT Error] {str(e)}"


# ✅ Compatible Global Instance (for legacy usage)
_default_bridge = ReflexOSGPTBridge()


def generate_gpt_response(prompt, temperature=0.7, max_tokens=500):
    return _default_bridge.generate_gpt_response(
        prompt, temperature, max_tokens)
