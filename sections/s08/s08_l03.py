"""Compare the same sample against an original and a revised prompt."""

import json
import sys
from pathlib import Path

from botocore.exceptions import BotoCoreError, ClientError

from s08_common import (
    MAX_OUTPUT_TOKENS,
    configure_console,
    converse,
    create_client,
    message,
    response_metrics,
    response_text,
)

SAMPLE_PATH = Path(__file__).parent / "sample" / "incident-note.txt"
BASELINE_PROMPT = "この障害調査メモを短く要約してください。"
REVISED_PROMPT = (
    "障害調査メモを読み、確認できる事実と未確認事項を分けてください。"
    "原文にない原因や影響範囲を推測で断定せず、各事実に時刻を添えてください。"
)
SYSTEM = "あなたは運用担当者の調査を補助します。原文にない事実を作りません。"


def build_user_text(case_text, prompt):
    return f"{prompt}\n\n--- 調査メモ ---\n{case_text}"


def compare(client, case_text):
    results = []
    for label, prompt in (("変更前", BASELINE_PROMPT), ("変更後", REVISED_PROMPT)):
        response = converse(client, [message("user", build_user_text(case_text, prompt))], SYSTEM)
        results.append({"label": label, "text": response_text(response), **response_metrics(response)})
    return results


def main():
    configure_console()
    try:
        case_text = SAMPLE_PATH.read_text(encoding="utf-8")
        results = compare(create_client(), case_text)
    except ClientError as error:
        details = error.response.get("Error", {})
        metadata = error.response.get("ResponseMetadata", {})
        print(f"Bedrock APIエラーコード: {details.get('Code', '不明')}", file=sys.stderr)
        if metadata.get("RequestId"):
            print(f"リクエストID: {metadata['RequestId']}", file=sys.stderr)
        print("リージョン、モデル利用可否、IAM権限、クォータを確認してください。", file=sys.stderr)
        return 1
    except (BotoCoreError, OSError) as error:
        print("AWS接続または教材データを確認できません。プロファイル、リージョン、sample fileを確認してください。", file=sys.stderr)
        return 1

    for result in results:
        print(f"\n## {result['label']}のプロンプト")
        print(result["text"])
        print("利用量: 入力 {input_tokens} / 出力 {output_tokens} / 合計 {total_tokens} tokens".format(**result))
        print(f"Bedrock応答時間: {result['latency_ms']} ms")
    print("\n出力を原文と照合し、採用・修正・保留のいずれかと理由を自分で記録してください。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
