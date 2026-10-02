"""入力用の確認データを返す。"""


def get_checks() -> list[dict[str, str]]:
    return [
        {"name": "API応答", "status": "ok"},
        {"name": "エラーログ", "status": "needs_review"},
        {"name": "再試行回数", "status": "ok"},
    ]
