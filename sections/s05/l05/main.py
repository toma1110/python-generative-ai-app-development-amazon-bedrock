import json
import sys
from pathlib import Path


def validate_checks(value):
    if not isinstance(value, list):
        raise ValueError("最上位は配列にしてください。")
    for index, item in enumerate(value, 1):
        if not isinstance(item, dict):
            raise ValueError(f"{index}番目はオブジェクトにしてください。")
        if item.get("status") not in {"ok", "needs_review"}:
            raise ValueError(f"{index}番目のstatusを確認してください。")
    return value


def load_checks(path):
    value = json.loads(Path(path).read_text(encoding="utf-8"))
    try:
        checks = validate_checks(value)
    except ValueError as error:
        return None, f"入力データを確認してください: {error}"
    return checks, None


def main(path):
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    checks, error = load_checks(path)
    if error is not None:
        print(error)
        return
    for item in checks:
        print(f"{item['name']}: {item['status']}")


if __name__ == "__main__":
    main(sys.argv[1])
