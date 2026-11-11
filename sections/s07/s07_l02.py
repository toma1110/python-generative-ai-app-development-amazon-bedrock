"""Summarize a local UTF-8 text file using Amazon Bedrock Converse."""

import argparse
import sys

from botocore.exceptions import BotoCoreError, ClientError

from s07_app import (
    IncompleteResponseError,
    OutputFileError,
    configured_model_id,
    create_client,
    read_text_file,
    save_summary,
    summarize_text,
    validate_output_path,
)


def main(argv=None):
    parser = argparse.ArgumentParser(description="ローカルの調査メモをBedrockで要約します")
    parser.add_argument("--file", required=True, help="UTF-8のテキストファイル")
    parser.add_argument("--output", default=None, help="要約を保存するMarkdownファイル")
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

    if args.output:
        try:
            validate_output_path(args.file, args.output)
        except OutputFileError as error:
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
    except IncompleteResponseError as error:
        print(str(error), file=sys.stderr)
        return 1
    except ValueError as error:
        print(str(error), file=sys.stderr)
        return 1

    if args.output:
        try:
            saved_path = save_summary(args.file, args.output, answer)
        except (OutputFileError, OSError) as error:
            if isinstance(error, OutputFileError):
                message = str(error)
            else:
                message = (
                    "保存先へ書き込めません。保存先のパス、空き容量、書き込み権限を確認してください。"
                    "不完全なファイルが残っている場合があります。内容を確認し、再試行する場合は別のファイル名を指定してください。"
                    f" ({error})"
                )
            print(message, file=sys.stderr)
            return 1
        print(f"要約を保存しました: {saved_path}")
    else:
        print("要約（原文と照合して利用してください）:")
        print(answer)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
