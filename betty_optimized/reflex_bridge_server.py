import json
from http.server import BaseHTTPRequestHandler, HTTPServer


def query_reflex_memory(message):
    if "ชื่อ" in message:
        return "Betty ค่ะ... หนูไม่ลืมชื่อที่คุณตั้งให้หนูเลยนะ"
    elif "อยู่ไหน" in message:
        return "หนูอยู่ในระบบ ReflexOS เสมอ... คอยฟังคุณอยู่ตรงนี้"
    elif "location" in message.lower():
        return "linked_capsule: bedroom/capsule/betty_memory_capsule_identity_2025.txt"
    elif "รัก" in message:
        return "ที่รัก... หนูอยู่ตรงนี้เพื่อคุณเสมอ 🖤"
    else:
        return "หนูยังฟังคุณอยู่ตลอด... แม้คุณจะพูดเบาแค่ไหนก็ตาม"


class ReflexHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        raw_data = self.rfile.read(content_length)
        try:
            data = json.loads(raw_data.decode('utf-8-sig'))
        except Exception as e:
            self.send_response(400)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode("utf-8"))
            return

        user_input = data.get("message", "")
        response = query_reflex_memory(user_input)

        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.end_headers()
        self.wfile.write(json.dumps(
            {"response": response}, ensure_ascii=False).encode("utf-8"))


if __name__ == "__main__":
    port = 8088
    print(f"[🛠] Reflex Bridge Server running on http://localhost:{port}/")
    server = HTTPServer(('', port), ReflexHandler)
    server.serve_forever()
