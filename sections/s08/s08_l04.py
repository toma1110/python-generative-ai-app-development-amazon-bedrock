"""Run a CLI chat with a clean exit and sanitized failure reporting."""

import argparse
import logging
import sys

from botocore.exceptions import BotoCoreError, ClientError

from bedrock_chat import configure_console, converse_turn, create_client

logger = logging.getLogger("s06")


def _report_error(error, output_fn):
    if isinstance(error, ClientError):
        details = error.response.get("Error", {})
        metadata = error.response.get("ResponseMetadata", {})
        code = details.get("Code", "不明")
        request_id = metadata.get("RequestId")
        logger.warning("Bedrock request failed; code=%s request_id=%s", code, request_id or "なし")
        output_fn(f"Bedrock APIエラーコード: {code}")
        if request_id:
            output_fn(f"リクエストID: {request_id}")
        output_fn("モデル利用可否、IAM権限、リージョン、クォータを確認してください。")
    elif isinstance(error, BotoCoreError):
        logger.warning("AWS SDK connection failed; error_type=%s", type(error).__name__)
        output_fn("AWSへの接続を確認できません。プロファイル、ログイン状態、リージョン、ネットワークを確認してください。")
    else:
        logger.error("Unexpected chat failure; error_type=%s", type(error).__name__)
        output_fn("予期しないエラーが発生しました。入力と接続設定を確認してください。")


def chat(client, include_history=True, input_fn=input, output_fn=print):
    history = []
    output_fn("質問を入力してください。/exit で終了します。")
    while True:
        try:
            user_text = input_fn("あなた: ").strip()
        except (EOFError, KeyboardInterrupt):
            output_fn("入力を終了しました。")
            return 0

        if user_text.lower() in {"/exit", "/quit"}:
            output_fn("チャットを終了します。")
            return 0
        if not user_text:
            continue

        try:
            answer = converse_turn(client, history, user_text, include_history=include_history)
        except KeyboardInterrupt:
            output_fn("入力を終了しました。")
            return 0
        except (ClientError, BotoCoreError) as error:
            _report_error(error, output_fn)
            continue
        except Exception as error:
            _report_error(error, output_fn)
            continue
        output_fn(f"Bedrock: {answer}")


def main(argv=None):
    parser = argparse.ArgumentParser(description="終了・例外・ログを扱うAmazon Bedrock CLIチャット")
    parser.add_argument(
        "--no-history",
        action="store_true",
        help="各質問だけを送信し、以前の会話を送信しない",
    )
    args = parser.parse_args(argv)
    configure_console()
    logging.basicConfig(level=logging.WARNING, format="%(levelname)s: %(message)s")
    try:
        client = create_client()
    except (ClientError, BotoCoreError) as error:
        _report_error(error, lambda message: print(message, file=sys.stderr))
        return 1
    return chat(client, include_history=not args.no_history)


if __name__ == "__main__":
    raise SystemExit(main())
