"""確認項目のlistを作るモジュール。"""


def get_checks() -> list[dict[str, str]]:
    """呼び出し元で表示できる確認項目を返す。"""
    return [
        {"name": "API応答", "status": "ok"},
        {"name": "エラーログ", "status": "needs_review"},
        {"name": "再試行回数", "status": "ok"},
    ]
