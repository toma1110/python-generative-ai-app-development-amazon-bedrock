"""複数の確認項目をlist・dict・if・forで処理する例。"""


def main() -> None:
    import sys

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    checks = [
        {"name": "API応答", "status": "確認済み"},
        {"name": "エラーログ", "status": "要確認"},
        {"name": "再試行回数", "status": "確認済み"},
    ]

    for check in checks:
        print(f"{check['name']}: {check['status']}")
        if check["status"] == "要確認":
            print("  原文ログで発生時刻とエラー内容を確認します。")


if __name__ == "__main__":
    main()
