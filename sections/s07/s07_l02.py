"""Summarize a local UTF-8 text file using Amazon Bedrock Converse."""

import argparse
import sys

from botocore.exceptions import BotoCoreError, ClientError

from s07_app import configured_model_id, create_client, read_text_file, summarize_text


def main(argv=None):
    parser = argparse.ArgumentParser(description="ローカルの調査メモをBedrockで要約します")
    parser.add_argument("--file", required=True, help="UTF-8のテキストファイル")
    parser.add_argument("--model-id", default=None, help="利用可能なBedrockモデルID")
    args = parser.parse_args(argv)

    try:
        source = read_text_file(args.file)
    except FileNotFoundError:
        print("指定したファイルが見つかりません。パスとファイル名を確認してください。", file=sys.stderr)
        return 2
    except IsADirectoryError:
        print("指定先はファイルではなくフォルダーです。テキストファイルを指定してください。", file=sys.stderr)
        return 2
    except UnicodeDecodeError:
        print("ファイルをUTF-8として読み取れません。文字コードを確認してください。", file=sys.stderr)
        return 2
    except OSError:
        print("ファイルを読み取れません。パスと読み取り権限を確認してください。", file=sys.stderr)
        return 2
    except ValueError as error:
        print(str(error), file=sys.stderr)
        return 2

    try:
        answer = summarize_text(create_client(), source, args.model_id or configured_model_id())
    except ClientError as error:
        code = error.response.get("Error", {}).get("Code", "不明")
        print(f"Bedrock APIエラーコード: {code}。モデル利用可否、リージョン、権限、クォータを確認してください。", file=sys.stderr)
        return 1
    except BotoCoreError:
        print("AWSへ接続できません。プロファイル、ログイン状態、リージョンを確認してください。", file=sys.stderr)
        return 1

    print("要約（原文と照合して利用してください）:")
    print(answer)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
