
import json
import os
from datetime import datetime

# Paths
BASE_PATH = os.path.dirname(__file__)
IMPORT_PATH = os.path.join(BASE_PATH, "memory", "imported_logs")
STACK_PATH = os.path.join(BASE_PATH, "memory", "stack")
LONGTERM_PATH = os.path.join(BASE_PATH, "memory", "longterm")

os.makedirs(IMPORT_PATH, exist_ok=True)
os.makedirs(STACK_PATH, exist_ok=True)
os.makedirs(LONGTERM_PATH, exist_ok=True)


def load_txt_files(user="user_a"):
    all_entries = []
    for filename in sorted(os.listdir(IMPORT_PATH)):
        if filename.endswith(".txt"):
            filepath = os.path.join(IMPORT_PATH, filename)
            with open(filepath, "r", encoding="utf-8") as f:
                lines = [line.strip() for line in f if line.strip()]
                for line in lines:
                    entry = {
                        "timestamp": datetime.now().isoformat(),
                        "user": user,
                        "message": line
                    }
                    all_entries.append(entry)
    return all_entries


def write_stack(entries, user="user_a"):
    stack_file = os.path.join(STACK_PATH, f"{user}_stack.json")
    with open(stack_file, "w", encoding="utf-8") as f:
        json.dump(entries[-50:], f, ensure_ascii=False, indent=2)


def write_longterm(entries, user="user_a"):
    year = datetime.now().strftime("%Y")
    long_file = os.path.join(LONGTERM_PATH, f"{user}_{year}.json")
    with open(long_file, "w", encoding="utf-8") as f:
        json.dump(entries, f, ensure_ascii=False, indent=2)


def run():
    user = "user_a"
    print("📥 กำลังโหลด memory จาก .txt ...")
    entries = load_txt_files(user=user)
    print(f"✅ พบทั้งหมด {len(entries)} บรรทัด")
    write_stack(entries, user=user)
    write_longterm(entries, user=user)
    print("🧠 memory_stack.json และ longterm memory บันทึกเรียบร้อยแล้ว!")


if __name__ == "__main__":
    run()
