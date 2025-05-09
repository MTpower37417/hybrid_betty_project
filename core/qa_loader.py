
import os

QA_DIR = "core/memory/imported_logs"


def load_qa_memory():
    memory = []
    for file in sorted(os.listdir(QA_DIR)):
        if file.endswith(".txt"):
            with open(os.path.join(QA_DIR, file), encoding="utf-8") as f:
                memory.append(f.read())
    return "\n".join(memory)
