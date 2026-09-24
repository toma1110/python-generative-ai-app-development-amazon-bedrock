"""JSONファイルを読み、読み込み失敗を利用者へ案内する例。"""

import json
import sys
from pathlib import Path


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).with_name("cases.json")

    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        print(f"ファイルが見つかりません: {path.name}")
        print("ファイル名と実行しているフォルダーを確認してください。")
        return 1
    except UnicodeDecodeError:
        print(f"UTF-8形式で読み取れません: {path.name}")
        print("ファイルの文字コードを確認してください。")
        return 1
    except OSError as error:
        print(f"ファイルを読み取れません: {path.name} ({error.strerror})")
        return 1

    try:
        checks = json.loads(text)
    except json.JSONDecodeError as error:
        print(f"JSONの形式を確認してください: {path.name} {error.lineno}行目")
        return 1

    if not isinstance(checks, list):
        print(f"JSONの最上位は配列にしてください: {path.name}")
        return 1

    status_labels = {"ok": "確認済み", "needs_review": "要確認"}
    for index, check in enumerate(checks, start=1):
        if not isinstance(check, dict):
            print(f"JSONの{index}番目の項目はオブジェクトにしてください。")
            return 1

        name = check.get("name")
        if not isinstance(name, str) or not name.strip():
            print(f"JSONの{index}番目の項目でnameを空でない文字列にしてください。")
            return 1

        status = check.get("status")
        if not isinstance(status, str) or status not in status_labels:
            print(
                f"JSONの{index}番目の項目でstatusを"
                "okまたはneeds_reviewにしてください。"
            )
            return 1

        print(f"{name}: {status_labels[status]}")
        if status == "needs_review":
            print("  原文ログで発生時刻とエラー内容を確認します。")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
