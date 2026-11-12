"""Display Converse response fields and safe error identifiers."""

import sys

from botocore.exceptions import BotoCoreError, ClientError

from bedrock_call import MAX_OUTPUT_TOKENS, configure_console, create_client, model_id, response_text, user_message

PROMPT = "監視アラームを調査するときの確認項目を一つ、短く答えてください。"


def inspect_response(response):
    usage = response.get("usage", {})
    metrics = response.get("metrics", {})
    return {
        "text": response_text(response),
        "stop_reason": response.get("stopReason", "不明"),
        "input_tokens": usage.get("inputTokens", "不明"),
        "output_tokens": usage.get("outputTokens", "不明"),
        "total_tokens": usage.get("totalTokens", "不明"),
        "latency_ms": metrics.get("latencyMs", "不明"),
    }


def call_once(client):
    return client.converse(
        modelId=model_id(),
        messages=user_message(PROMPT),
        inferenceConfig={"maxTokens": MAX_OUTPUT_TOKENS},
    )


def main():
    configure_console()
    try:
        result = inspect_response(call_once(create_client()))
    except ClientError as error:
        details = error.response.get("Error", {})
        metadata = error.response.get("ResponseMetadata", {})
        print(f"Bedrock APIエラーコード: {details.get('Code', '不明')}", file=sys.stderr)
        if metadata.get("RequestId"):
            print(f"リクエストID: {metadata['RequestId']}", file=sys.stderr)
        print("リージョン、モデル利用可否、IAM権限、クォータを確認してください。", file=sys.stderr)
        return 1
    except BotoCoreError:
        print("AWS接続を確認できませんでした。プロファイル、ログイン状態、リージョン、ネットワークを確認してください。", file=sys.stderr)
        return 1

    print(f"応答: {result['text']}")
    print(f"終了理由: {result['stop_reason']}")
    print(f"入力token数: {result['input_tokens']}")
    print(f"出力token数: {result['output_tokens']}")
    print(f"合計token数: {result['total_tokens']}")
    print(f"応答時間(ms): {result['latency_ms']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
