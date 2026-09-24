"""入力・処理・表示を関数に分ける例。"""

from check_data import get_checks


def classify_check(check: dict[str, str]) -> str:
    if check["status"] == "needs_review":
        return "追加確認が必要"
    return "確認済み"


def show_check(check: dict[str, str]) -> None:
    result = classify_check(check)
    print(f"{check['name']}: {result}")


def main() -> None:
    import sys

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    checks = get_checks()
    for check in checks:
        show_check(check)


if __name__ == "__main__":
    main()
