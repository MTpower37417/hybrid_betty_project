import openai


class BettyGPTBridge:
    def __init__(self):
        """
        เริ่มต้นการทำงานของ Bridge ที่เชื่อมต่อระหว่าง Betty และ OpenAI API
        """
        self.load_api_key()
        self.load_persona()

    def load_api_key(self):
        """
        โหลด API key จากไฟล์ .env
        """
        try:
            with open(".env", "r") as f:
                for line in f:
                    if line.startswith("OPENAI_API_KEY="):
                        openai.api_key = line.split("=")[1].strip()
                        print("โหลด API key สำเร็จ")
        except Exception as e:
            print(f"เกิดข้อผิดพลาดในการโหลด API key: {e}")

    def load_persona(self):
        """
        โหลดข้อมูลบุคลิก Betty จากไฟล์ BettyPersona.txt
        """
        try:
            with open("BettyPersona.txt", "r", encoding="utf-8") as f:
                self.persona = f.read()
                print("โหลดข้อมูลบุคลิก Betty สำเร็จ")
        except Exception as e:
            print(f"เกิดข้อผิดพลาดในการโหลดบุคลิก Betty: {e}")
            self.persona = "คุณคือ Betty AI ผู้ช่วยส่วนตัวที่ฉลาดและเป็นมิตร ตอบคำถามสุภาพและลงท้ายด้วยคำว่า 'ค่ะ' เสมอ"

    def generate_response(self, message, context=None):
        """
        สร้างการตอบกลับโดยใช้ OpenAI API

        Parameters:
            message (str): ข้อความที่ต้องการตอบกลับ
            context (list): ข้อความบริบทที่เกี่ยวข้อง

        Returns:
            str: ข้อความตอบกลับจาก GPT
        """
        try:
            # สร้าง system prompt ที่มีบุคลิกชัดเจน
            system_content = self.persona

            # สร้าง messages สำหรับส่งไป OpenAI
            messages = [{"role": "system", "content": system_content}]

            # เพิ่ม context ถ้ามี
            if context and len(context) > 0:
                messages.extend(context)

            # เพิ่มข้อความปัจจุบัน
            messages.append({"role": "user", "content": message})

            # เรียกใช้ OpenAI API
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=messages
            )

            return response.choices[0].message["content"]
        except Exception as e:
            return f"ขออภัยค่ะ เกิดข้อผิดพลาดในการเชื่อมต่อ: {str(e)}"

    def generate_emotion_response(self, message, context=None, emotion=None):
        """
        สร้างการตอบกลับที่มีอารมณ์เฉพาะ

        Parameters:
            message (str): ข้อความที่ต้องการตอบกลับ
            context (list): ข้อความบริบทที่เกี่ยวข้อง
            emotion (str): อารมณ์ที่ต้องการให้แสดงออก เช่น "happy", "sad", "surprised"

        Returns:
            str: ข้อความตอบกลับจาก GPT ที่แสดงอารมณ์ตามที่กำหนด
        """
        try:
            # สร้าง system prompt ที่มีบุคลิกและอารมณ์ชัดเจน
            system_content = self.persona

            if emotion:
                system_content += f"\n\nตอนนี้คุณรู้สึก{emotion} ให้ตอบด้วยอารมณ์นี้"

            # สร้าง messages สำหรับส่งไป OpenAI
            messages = [{"role": "system", "content": system_content}]

            # เพิ่ม context ถ้ามี
            if context and len(context) > 0:
                messages.extend(context)

            # เพิ่มข้อความปัจจุบัน
            messages.append({"role": "user", "content": message})

            # เรียกใช้ OpenAI API
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=messages
            )

            return response.choices[0].message["content"]
        except Exception as e:
            return f"ขออภัยค่ะ เกิดข้อผิดพลาดในการเชื่อมต่อ: {str(e)}"
