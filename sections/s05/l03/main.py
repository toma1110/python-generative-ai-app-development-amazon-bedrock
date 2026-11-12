"""教材用JSONを読み、形を確かめてから内容を表示する。"""

import json
import sys
from pathlib import Path
from typing import Any

STATUS_LABELS = {"ok": "確認済み", "needs_review": "要確認"}


def validate_checks(value: Any) -> list[dict[str, str]]:
    """JSON由来の値を検査し、不正な場合はValueErrorを発生させる。"""
    if not isinstance(value, list):
        raise ValueError("最上位は配列にしてください。")

    for index, check in enumerate(value, start=1):
        if not isinstance(check, dict):
            raise ValueError(f"{index}番目の項目はオブジェクトにしてください。")

        name = check.get("name")
        if not isinstance(name, str) or not name.strip():
            raise ValueError(f"{index}番目のnameを空でない文字列にしてください。")

        status = check.get("status")
        if not isinstance(status, str) or status not in STATUS_LABELS:
            raise ValueError(
                f"{index}番目のstatusをokまたはneeds_reviewにしてください。"
            )

    return value


def load_checks(path: Path) -> tuple[list[dict[str, str]] | None, str | None]:
    """失敗を捕捉して案内文字列を返し、正常時は検証済みlistを返す。"""
    # Pathはファイルの場所を表す値。read_textでUTF-8の文字列を読み取ります。
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return None, f"ファイルが見つかりません: {path.name}。名前と場所を確認してください。"
    except UnicodeDecodeError:
        return None, f"UTF-8形式で読み取れません: {path.name}。文字コードを確認してください。"
    except OSError:
        return None, f"ファイルを読み取れません: {path.name}。アクセス権と場所を確認してください。"

    # JSONの文字列を、Pythonで使えるlist/dict/strへ変換します。
    try:
        value = json.loads(text)
    except json.JSONDecodeError as error:
        return None, f"JSONの形式を確認してください: {path.name} {error.lineno}行目。"

    # JSONとして読めても、必要な型や値とは限りません。
    try:
        checks = validate_checks(value)
    except ValueError as error:
        # validate_checksが発生させた例外をここで捕捉し、画面用の文にします。
        return None, f"{path.name}: {error}"

    return checks, None


def main(arguments: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    # 引数がなければ、このmain.pyと同じ場所のcases.jsonを使います。
    if arguments is None:
        arguments = sys.argv[1:]
    path = Path(arguments[0]) if arguments else Path(__file__).with_name("cases.json")

    checks, error = load_checks(path)
    if error is not None:
        # load_checksの戻り値は、ここでprintして初めて画面に出ます。
        print(error)
        return 1

    # 検査が済んだlistからdictを1件ずつ取り出し、値を画面で使います。
    for check in checks or []:
        status = check["status"]
        print(f"{check['name']}: {STATUS_LABELS[status]}")
        if status == "needs_review":
            print("  原文ログで発生時刻とエラー内容を確認します。")

    return 0


if __name__ == "__main__":
    # return した終了コードをOSへ渡します。0は成功、1は入力確認が必要です。
    raise SystemExit(main())
