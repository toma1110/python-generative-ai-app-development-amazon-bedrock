"""Summarize, inspect, or ask about the same note from a local file or S3."""

import argparse
import sys
from pathlib import Path

from botocore.exceptions import BotoCoreError, ClientError

from s09_common import ask_model, configure_console, create_bedrock_client, create_s3_client, read_local_text
from s09_l03 import read_s3_text

SAMPLE_PATH = Path(__file__).parent / "sample" / "incident-note.txt"


def load_note(source, path, bucket, key):
    if source == "local":
        return read_local_text(path)
    if not bucket:
        raise ValueError("S3入力には--bucketまたはS09_BUCKETが必要です。")
    return read_s3_text(create_s3_client(), bucket, key)


def main(argv=None):
    parser = argparse.ArgumentParser(description="架空の調査メモを読み、要約・確認項目・追加質問を実行します。")
    parser.add_argument("--source", choices=("local", "s3"), default="local")
    parser.add_argument("--path", type=Path, default=SAMPLE_PATH)
    parser.add_argument("--bucket", default=None)
    parser.add_argument("--key", default="training/s09/incident-note.txt")
    parser.add_argument("--task", choices=("summary", "checks", "ask"), default="summary")
    parser.add_argument("--question", help="--task askで使う追加質問")
    args = parser.parse_args(argv)
    configure_console()
    try:
        note = load_note(args.source, args.path, args.bucket, args.key)
        result = ask_model(create_bedrock_client(), note, args.task, args.question)
    except ValueError as error:
        print(error, file=sys.stderr)
        return 1
    except (BotoCoreError, ClientError, OSError, UnicodeDecodeError) as error:
        print(f"AWS接続または入力の読み込みに失敗しました ({type(error).__name__})。認証、Region、対象オブジェクト、権限を確認してください。", file=sys.stderr)
        return 1

    print("## モデルの応答（原文と照合してください）")
    print(result["text"])
    print(f"利用量: 入力 {result['input_tokens']} / 出力 {result['output_tokens']} tokens")
    print(f"Bedrock応答時間: {result['latency_ms']} ms")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
