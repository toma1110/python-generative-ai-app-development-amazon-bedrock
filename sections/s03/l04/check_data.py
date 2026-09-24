"""演習で処理する入力データを用意する。"""


def get_checks() -> list[dict[str, str]]:
    return [
        {"name": "API応答", "status": "ok"},
        {"name": "エラーログ", "status": "needs_review"},
        {"name": "再試行回数", "status": "ok"},
    ]
