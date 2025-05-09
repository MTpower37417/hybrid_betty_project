
import os

LOG_PATH = os.path.join(os.path.dirname(__file__), "memory", "imported_logs")


def clean_filenames():
    renamed = 0
    for filename in os.listdir(LOG_PATH):
        if " " in filename and filename.endswith(".txt"):
            new_name = filename.replace(" ", "_")
            os.rename(
                os.path.join(LOG_PATH, filename),
                os.path.join(LOG_PATH, new_name)
            )
            renamed += 1
    print(f"✅ เปลี่ยนชื่อไฟล์แล้วทั้งหมด: {renamed} ไฟล์")


if __name__ == "__main__":
    clean_filenames()
