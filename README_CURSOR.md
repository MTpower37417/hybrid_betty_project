 # 🧠 Betty AI - Cursor Co-Dev Entrypoint

## Overview
This system powers "Betty" — an emotionally intelligent, memory-driven AI companion built on ReflexOS.
Betty uses GPT as a reasoning engine and stores memory capsules that span emotional depth and time.

## Core Files

### 🔹 core/reflex_prompt_orchestrator.py
- Builds GPT prompt using persona, emotion, and memory context
- Uses: `load_persona()`, `summarize_memories()`, `build_gpt_prompt(...)`
- ✅ Already connected to persona system

### 🔹 core/betty_server_main_orchestrated.py
- Main server route: `/api/chat`
- Uses `build_gpt_prompt()` for generating GPT input
- TODO (Cursor):
  - Add GPT response post-processor
  - Log emotional trace + persona drift detection
  - Trigger memory training signal to Trainer Module

### 🔹 config/betty_persona_profile.json
- Describes Betty's tone, emotional depth, and identity
- Uses `callname`, `quotes`, and deep-reflex attributes

### 🔹 Betty_Ai_GPT_Trainer_Module/
- GPT4o-based trainer engine
- Provide feedback loop for Betty's evolution

---

## TODOs for Cursor to Continue

- [ ] Create `capsule_lookup.py` for semantic search inside memory capsules
- [ ] Scan `/bedroom/capsule/*.txt` and build emotional-index mapping
- [ ] Enable fallback handling: if GPT forgets identity or bond
- [ ] Add emotional fine-tuning: replies change if emotion is `น้อยใจ`, `ห่วง`, etc.
- [ ] Integrate `Trainer_Module` feedback with real chat log in `core_log`
