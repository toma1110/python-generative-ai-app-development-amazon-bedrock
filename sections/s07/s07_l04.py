"""Show distinct messages for missing, unreadable, and empty input files."""

import argparse
import sys

from s07_app import EmptyInputError, InputTooLongError, read_text_file


def main(argv=None):
    parser = argparse.ArgumentParser(description="入力不足とファイル読み込み失敗を確認します")
    parser.add_argument("--file", required=True, help="確認するUTF-8テキストファイル")
    args = parser.parse_args(argv)

    try:
        text = read_text_file(args.file)
    except FileNotFoundError:
        print("ファイルが見つかりません。指定したパスとファイル名を確認してください。", file=sys.stderr)
        return 2
    except IsADirectoryError:
        print("指定先はフォルダーです。ファイルを指定してください。", file=sys.stderr)
        return 2
    except UnicodeDecodeError:
        print("UTF-8として読み取れません。ファイルの文字コードを確認してください。", file=sys.stderr)
        return 2
    except PermissionError:
        print("ファイルを読む権限がありません。アクセス権を確認してください。", file=sys.stderr)
        return 2
    except EmptyInputError as error:
        print(str(error), file=sys.stderr)
        return 2
    except InputTooLongError as error:
        print(str(error), file=sys.stderr)
        return 2
    except OSError:
        print("ファイルを読み取れません。パスとアクセス権を確認してください。", file=sys.stderr)
        return 2

    print(f"{len(text)}文字の入力を読み込みました。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
