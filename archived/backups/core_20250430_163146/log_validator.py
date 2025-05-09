
import os

LOG_PATH = os.path.join(os.path.dirname(__file__), "memory", "imported_logs")


def is_valid_line(line):
    ignore_tokens = ["ChatGPT", "Title:", "Skip to",
                     "icon", "[", "]", "Transcript", ":", "::"]
    return line.strip() and not any(tok in line for tok in ignore_tokens)


def validate_logs():
    valid = []
    skipped = []
    for filename in os.listdir(LOG_PATH):
        if filename.endswith(".txt"):
            path = os.path.join(LOG_PATH, filename)
            with open(path, "r", encoding="utf-8") as f:
                lines = [line.strip() for line in f.readlines()]
                good_lines = [l for l in lines if is_valid_line(l)]
                if len(good_lines) >= 5:
                    valid.append((filename, len(good_lines)))
                else:
                    skipped.append((filename, len(good_lines)))
    print(f"✅ ใช้ได้ทั้งหมด: {len(valid)} ไฟล์")
    for name, count in valid:
        print(f" - {name} ({count} บรรทัด)")
    print(f"⚠️ ถูกข้าม: {len(skipped)} ไฟล์")
    for name, count in skipped:
        print(f" - {name} ({count} บรรทัด)")


if __name__ == "__main__":
    validate_logs()
