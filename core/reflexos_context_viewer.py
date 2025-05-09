
import json
import os

from fastapi import APIRouter

router = APIRouter()

EXTENDED_PATH = os.path.join(os.path.dirname(__file__), "memory", "extended")


@router.get("/context")
def view_context(user: str = "user_a"):
    file_path = os.path.join(EXTENDED_PATH, f"{user}_context.json")
    if not os.path.exists(file_path):
        return {"context": []}
    with open(file_path, "r", encoding="utf-8") as f:
        context = json.load(f)
    return {"context": context}
