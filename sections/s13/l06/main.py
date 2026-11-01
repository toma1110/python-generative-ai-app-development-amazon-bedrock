import json
from pathlib import Path
import sys


def validate_checks(value):
    if not isinstance(value, list):
        raise ValueError("最上位は配列にしてください。")
    for i, item in enumerate(value, 1):
        if not isinstance(item, dict):
            raise ValueError(f"{i}番目はオブジェクトにしてください。")
        if item.get("status") not in {"ok", "needs_review"}:
            raise ValueError(f"{i}番目のstatusを確認してください。")
    return value


def load_checks(path: Path):
    value = json.loads(path.read_text(encoding="utf-8"))
    try:
        return validate_checks(value), None
    except ValueError as error:
        return None, str(error)
