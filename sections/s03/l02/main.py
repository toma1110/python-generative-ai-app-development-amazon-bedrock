"""変数に値を入れ、その値から表示文を作る例。"""


def main() -> None:
    import sys

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    # 右側の文字列を、左側の名前へ代入します。
    audience = "SRE"
    check_item = "API応答"

    # f-stringの{}に変数の現在値を埋め込み、新しい文字列を作ります。
    message = f"{audience}さん、{check_item}の確認を始めます。"

    # printは値を画面へ表示します。後続の変数へ値を返す命令ではありません。
    print(message)


if __name__ == "__main__":
    main()
