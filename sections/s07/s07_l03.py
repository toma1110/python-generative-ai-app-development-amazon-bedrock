"""Compare system-message and inference-parameter changes separately."""

from bedrock_call import MAX_OUTPUT_TOKENS, configure_console, create_client, model_id, response_text, user_message

PROMPT = "監視アラームのしきい値を決めるとき、最初に確認することを一つ説明してください。"
SYSTEM = [{"text": "日本語で、短い一文だけで回答してください。"}]


def compare(client):
    model = model_id()
    messages = user_message(PROMPT)
    baseline = client.converse(
        modelId=model,
        messages=messages,
        inferenceConfig={"temperature": 0.0, "topP": 1.0, "maxTokens": MAX_OUTPUT_TOKENS},
    )

    system_changed = client.converse(
        modelId=model,
        messages=messages,
        system=SYSTEM,
        inferenceConfig={"temperature": 0.0, "topP": 1.0, "maxTokens": MAX_OUTPUT_TOKENS},
    )

    temperature_changed = client.converse(
        modelId=model,
        messages=messages,
        inferenceConfig={"temperature": 0.8, "topP": 1.0, "maxTokens": MAX_OUTPUT_TOKENS},
    )
    return baseline, system_changed, temperature_changed


def main():
    configure_console()
    results = compare(create_client())
    labels = ("基準", "system変更", "temperature変更")
    for label, response in zip(labels, results):
        print(f"【{label}】")
        print(response_text(response))
        print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
