def generate_gpt_response(msg):
    import json

    import openai

    try:
        with open("Betty_Ai_GPT_Trainer_Module/gpt_config.json", "r") as f:
            config = json.load(f)

        openai.api_key = config["api_key"]
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "system", "content": "ฉันคือ Betty AI"},
                      {"role": "user", "content": msg}]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"GPT Error: {str(e)}"
