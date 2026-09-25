"""Send one user message to the Amazon Bedrock Converse API."""

from bedrock_call import MAX_OUTPUT_TOKENS, configure_console, create_client, model_id, response_text, user_message

PROMPT = "監視アラームのしきい値を決めるとき、最初に確認することを一つ説明してください。"


def call_once(client):
    return client.converse(
        modelId=model_id(),
        messages=user_message(PROMPT),
        inferenceConfig={"maxTokens": MAX_OUTPUT_TOKENS},
    )


def main():
    configure_console()
    response = call_once(create_client())
    print(response_text(response))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
