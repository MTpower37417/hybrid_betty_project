import os
import shutil
import time


def schedule_capsule_sync(interval_min=30):
    while True:
        backup_recent_memory()
        log_sync_activity()
        time.sleep(interval_min * 60)


def backup_recent_memory(
        source_dir="memory/capsule",
        backup_dir="memory/backup"):
    os.makedirs(backup_dir, exist_ok=True)
    for file in os.listdir(source_dir):
        full_path = os.path.join(source_dir, file)
        if os.path.isfile(full_path):
            shutil.copy(full_path, os.path.join(backup_dir, file))


def log_sync_activity(log_file="memory/backup/sync_log.txt"):
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(f"Sync complete: {time.ctime()}\n")
