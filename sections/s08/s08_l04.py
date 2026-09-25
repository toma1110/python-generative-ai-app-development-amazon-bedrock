"""Observe latency, token usage, and how much conversation history is sent."""

import argparse
import sys
import time
from pathlib import Path

from botocore.exceptions import BotoCoreError, ClientError

from s08_common import (
    configure_console,
    converse,
    create_client,
    keep_recent_turns,
    message,
    response_metrics,
    response_text,
)

SYSTEM = "運用調査の補助をします。確認できない内容は未確認と伝えてください。"
SAMPLE_PATH = Path(__file__).parent / "sample" / "incident-note.txt"
QUESTIONS = (
    "障害メモでは何が分かっていますか。時刻と一緒に短く答えてください。",
    "原因は特定できていますか。未確認の点を原文に沿って答えてください。",
)


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description="会話履歴の範囲で入力token数と応答時間を観察します。")
    parser.add_argument(
        "--history-turns",
        type=int,
        default=2,
        help="各リクエストに含める直近のuser/assistant往復数。0なら履歴を送りません。",
    )
    args = parser.parse_args(argv)
    if args.history_turns < 0:
        parser.error("--history-turns は0以上を指定してください")
    return args


def request_messages(history, user_text, history_turns):
    return keep_recent_turns(history, history_turns) + [message("user", user_text)]


def run_turn(client, history, user_text, history_turns):
    sent = request_messages(history, user_text, history_turns)
    started = time.perf_counter()
    response = converse(client, sent, SYSTEM)
    client_elapsed_ms = (time.perf_counter() - started) * 1000
    answer = response_text(response)
    result = response_metrics(response)
    result.update({"text": answer, "messages_sent": len(sent), "client_elapsed_ms": round(client_elapsed_ms, 1)})
    return result


def main(argv=None):
    configure_console()
    args = parse_args(argv)
    print(f"直近{args.history_turns}往復の履歴を送り、架空の調査メモについて2問だけ実行します。")
    try:
        sample_text = SAMPLE_PATH.read_text(encoding="utf-8")
    except OSError:
        print("架空の調査メモを読めません。sample/incident-note.txtを確認してください。", file=sys.stderr)
        return 1
    history = []
    client = create_client()
    for turn_number, question in enumerate(QUESTIONS, start=1):
        user_text = f"次の教材用メモだけを根拠にしてください。\n\n{sample_text}\n\n質問: {question}"
        print(f"\n質問{turn_number}: {question}")
        try:
            result = run_turn(client, history, user_text, args.history_turns)
        except ClientError as error:
            details = error.response.get("Error", {})
            metadata = error.response.get("ResponseMetadata", {})
            print(f"Bedrock APIエラーコード: {details.get('Code', '不明')}", file=sys.stderr)
            if metadata.get("RequestId"):
                print(f"リクエストID: {metadata['RequestId']}", file=sys.stderr)
            print("リージョン、モデル利用可否、IAM権限、クォータを確認してください。", file=sys.stderr)
            return 1
        except BotoCoreError:
            print("AWS接続を確認できません。プロファイル、ログイン状態、リージョン、ネットワークを確認してください。", file=sys.stderr)
            return 1
        print(f"応答: {result['text']}")
        print("送信メッセージ数: {messages_sent} / 入力token: {input_tokens} / 出力token: {output_tokens} / 合計token: {total_tokens}".format(**result))
        print(f"Bedrock応答時間: {result['latency_ms']} ms（クライアント計測: {result['client_elapsed_ms']} ms）")
        history.extend([message("user", user_text), message("assistant", result["text"])])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
