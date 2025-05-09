# betty_memory_gpt_bridge.py

from betty_core_identity import inject_identity_into_prompt
from capsule_recall_agent import fetch_capsule_for_prompt
from reflexos_gpt_bridge import call_gpt  # <-- ต้องมีโมดูลนี้เชื่อม GPT


def get_gpt_response_with_memory(user_input):
    try:
        memories = fetch_capsule_for_prompt(user_input)
        memory_context = "\n".join(memories)
        full_prompt = inject_identity_into_prompt(
            memory_context + "\n\n" + user_input)
        return call_gpt(full_prompt)
    except Exception as e:
        return f"[ERROR] Memory GPT Response Failed: {str(e)}"
