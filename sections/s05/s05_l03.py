"""Compare system-message and inference-parameter changes separately."""

from bedrock_call import MAX_OUTPUT_TOKENS, configure_console, create_client, model_id, response_text, user_message

PROMPT = "監視アラームのしきい値を決めるとき、最初に確認することを一つ説明してください。"
SYSTEM = [{"text": "日本語で、短い一文だけで回答してください。"}]


def compare(client):
    common = {
        "modelId": model_id(),
        "messages": user_message(PROMPT),
        "inferenceConfig": {"temperature": 0.0, "topP": 1.0, "maxTokens": MAX_OUTPUT_TOKENS},
    }
    baseline = client.converse(**common)

    system_changed = client.converse(**common, system=SYSTEM)

    parameter_changed = client.converse(
        modelId=model_id(),
        messages=user_message(PROMPT),
        inferenceConfig={"temperature": 0.8, "topP": 0.9, "maxTokens": MAX_OUTPUT_TOKENS},
    )
    return baseline, system_changed, parameter_changed


def main():
    configure_console()
    results = compare(create_client())
    labels = ("基準", "system変更", "推論パラメータ変更")
    for label, response in zip(labels, results):
        print(f"【{label}】")
        print(response_text(response))
        print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
