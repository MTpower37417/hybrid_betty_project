
import os

IMPORT_PATH = os.path.join(
    os.path.dirname(__file__),
    "memory",
    "imported_logs")
KEYWORDS_IGNORE = [
    "ChatGPT",
    "Sora icon",
    "Skip to content",
    "[CAPSULE]",
    "Title:",
    "Date:",
    "Source:",
    "Transcript:",
    "Chat history"]


def is_valid_line(line):
    return line and not any(k in line for k in KEYWORDS_IGNORE)


def clean_file(input_path, output_path):
    with open(input_path, "r", encoding="utf-8") as infile:
        lines = [line.strip()
                 for line in infile if is_valid_line(line.strip())]
    with open(output_path, "w", encoding="utf-8") as outfile:
        outfile.write("\n".join(lines))


def run_cleaning():
    if not os.path.exists(IMPORT_PATH):
        print("❌ ไม่พบโฟลเดอร์ imported_logs")
        return

    cleaned = 0
    for filename in os.listdir(IMPORT_PATH):
        if filename.endswith(".txt") and not filename.endswith(".clean.txt"):
            input_path = os.path.join(IMPORT_PATH, filename)
            output_path = os.path.join(
                IMPORT_PATH, filename.replace(
                    ".txt", ".clean.txt"))
            clean_file(input_path, output_path)
            cleaned += 1
    print(f"✅ เคลียร์ไฟล์แล้วทั้งหมด: {cleaned} ไฟล์")


if __name__ == "__main__":
    run_cleaning()
