
import difflib
import json
import os

QA_DIR = "core/memory/imported_logs"
QA_LOG_PATH = "core/memory/qa_hits_log.json"


def load_qa_dict():
    qa_pairs = []
    for file in sorted(os.listdir(QA_DIR)):
        if file.endswith(".txt"):
            with open(os.path.join(QA_DIR, file), encoding="utf-8") as f:
                content = f.read()
                entries = content.split("\nQ: ")
                for entry in entries:
                    if entry.strip():
                        lines = entry.strip().split("\nA: ")
                        if len(lines) == 2:
                            question = lines[0].replace("Q: ", "").strip()
                            answer = lines[1].strip()
                            qa_pairs.append((question, answer))
    return qa_pairs


QA_MEMORY = load_qa_dict()


def search_qa_memory(user_input, threshold=0.6):
    questions = [q for q, a in QA_MEMORY]
    closest = difflib.get_close_matches(
        user_input, questions, n=1, cutoff=threshold)
    if closest:
        for q, a in QA_MEMORY:
            if q == closest[0]:
                return a
    return None


def log_qa_hit(question, answer):
    try:
        if os.path.exists(QA_LOG_PATH):
            with open(QA_LOG_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
        else:
            data = {}

        key = question.strip()
        if key in data:
            data[key]["hits"] += 1
        else:
            data[key] = {"answer": answer, "hits": 1}

        with open(QA_LOG_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print("Error logging QA hit:", e)
