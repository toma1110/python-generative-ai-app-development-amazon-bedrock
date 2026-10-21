"""Compare two prompts on exactly the same selected note."""

import argparse
import sys
from pathlib import Path

from botocore.exceptions import BotoCoreError, ClientError

from s09_app import load_note
from s09_common import IncompleteResponseError, ask_model, configure_console, create_bedrock_client

SAMPLE_PATH = Path(__file__).parent / "sample" / "incident-note.txt"
BASELINE_PROMPT = "この障害調査メモを短く要約してください。"
REVISED_PROMPT = "確認できる事実と未確認事項を分け、各事実の時刻を示してください。原文にない原因や影響を断定しないでください。"


def compare(client, note_text):
    for label, prompt in (
        ("BASELINE（既存の短い要約指示）", BASELINE_PROMPT),
        ("REVISED（編集対象の指示）", REVISED_PROMPT),
    ):
        yield label, ask_model(client, note_text, "summary", prompt_override=prompt)


def display_result(label, result):
    print(f"\n## {label}", flush=True)
    print(result["text"], flush=True)
    print(
        f"利用量: 入力 {result['input_tokens']} / 出力 {result['output_tokens']} tokens; "
        f"Bedrock応答時間: {result['latency_ms']} ms; stopReason: {result['stop_reason']}",
        flush=True,
    )


def main(argv=None):
    configure_console()
    parser = argparse.ArgumentParser(description="同じ教材メモを2種類の指示で処理し、結果を比べます。")
    parser.add_argument("--source", choices=("local", "s3"), default="local")
    parser.add_argument("--path", type=Path, default=SAMPLE_PATH)
    parser.add_argument("--bucket")
    parser.add_argument("--key", default="training/s09/incident-note.txt")
    args = parser.parse_args(argv)
    try:
        note = load_note(args.source, args.path, args.bucket, args.key)
        for label, result in compare(create_bedrock_client(), note):
            display_result(label, result)
    except IncompleteResponseError as error:
        print(str(error), file=sys.stderr)
        return 1
    except (BotoCoreError, ClientError, OSError, UnicodeDecodeError, ValueError) as error:
        print(f"比較を実行できませんでした ({type(error).__name__})。入力、AWS認証、Regionと権限を確認してください。", file=sys.stderr)
        return 1
    print("\nこの2つは既存の別々の指示です。演習での変更前後は、編集前に控えたREVISEDの結果と編集後のREVISEDの結果を同じ原文で比べてください。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
