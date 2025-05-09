def build_betty_prompt_v4(message, memory_context, persona_config, emotion):
    prompt_parts = []

    if memory_context:
        prompt_parts.append("[Memory Context]\n" + memory_context.strip())

    if persona_config:
        persona_section = "[Betty Persona Style: {}]\n{}".format(
            persona_config.get("style", "default"),
            persona_config.get("text", "")
        )
        prompt_parts.append(persona_section)

    if emotion:
        prompt_parts.append("[Detected Emotion]\n" + emotion.strip())

    prompt_parts.append("[User Message]\n" + message.strip())

    return "\n\n".join(prompt_parts)
