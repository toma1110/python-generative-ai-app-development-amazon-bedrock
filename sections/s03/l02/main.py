"""変数と文字列で表示内容を組み立てる例。"""


def main() -> None:
    import sys

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    audience = "SRE"
    check_item = "API応答"
    message = f"{audience}さん、{check_item}の確認を始めます。"
    print(message)


if __name__ == "__main__":
    main()
