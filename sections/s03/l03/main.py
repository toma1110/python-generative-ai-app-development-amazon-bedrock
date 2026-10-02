"""listからdictを1件ずつ取り出し、ifで表示を分ける例。"""


def main() -> None:
    import sys

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    checks = [
        {"name": "API応答", "status": "確認済み"},
        {"name": "エラーログ", "status": "要確認"},
        {"name": "再試行回数", "status": "確認済み"},
    ]

    # listは複数の値を順番に持ちます。forは中身を先頭から1件ずつcheckへ渡します。
    for check in checks:
        # dictはkey（name/status）でvalue（各文字列）を取り出します。
        print(f"{check['name']}: {check['status']}")

        # この条件は、今の1件のstatusが「要確認」かを調べています。
        if check["status"] == "要確認":
            print("  原文ログで発生時刻とエラー内容を確認します。")


if __name__ == "__main__":
    main()
