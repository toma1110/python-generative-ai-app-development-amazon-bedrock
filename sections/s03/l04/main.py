"""定義した関数を呼び出し、戻り値を表示する例。"""

from check_data import get_checks


def classify_check(check: dict[str, str]) -> str:
    """1件の確認データを受け取り、表示用の分類文字列を返す。"""
    if check["status"] == "needs_review":
        return "追加確認が必要"
    return "確認済み"


def show_check(check: dict[str, str]) -> None:
    """分類結果を表示する。"""
    result = classify_check(check)
    print(f"{check['name']}: {result}")


def main() -> None:
    import sys

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    # get_checksを呼び出すと、別ファイルで作られたlistが返ります。
    checks = get_checks()
    for check in checks:
        show_check(check)


if __name__ == "__main__":
    # 関数はdefだけでは動きません。ここからmainを呼ぶと処理が始まります。
    main()
