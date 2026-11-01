"""printは表示するが、呼び出し元へ分類結果を返さない例。"""


def classify_with_print(status: str) -> str | None:
    if status == "needs_review":
        return "追加確認が必要"
    print("確認済み")  # returnではないため、この関数の結果はNoneになる。
    # returnを省略した関数はNoneを返す。


def main() -> None:
    import sys

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    result = classify_with_print("ok")
    print(f"受け取った値: {result}")


if __name__ == "__main__":
    main()
