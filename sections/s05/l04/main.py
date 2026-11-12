import json
import sys
from pathlib import Path


def validate(value):
    if not isinstance(value, list):
        raise ValueError("validation: 最上位は配列にしてください。")
    for i, item in enumerate(value, 1):
        if not isinstance(item, dict):
            raise ValueError(f"validation: {i}番目はオブジェクトにしてください。")
        if not isinstance(item.get("name"), str) or not item["name"].strip():
            raise ValueError(f"validation: {i}番目のnameは空でない文字列にしてください。")
        if item.get("status") not in {"ok", "needs_review"}:
            raise ValueError(f"validation: {i}番目のstatusを確認してください。")
    return value


def main(path):
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    text = Path(path).read_text(encoding="utf-8")
    try:
        value = json.loads(text)
    except json.JSONDecodeError as error:
        print(f"parse: JSON文法を確認してください ({error.lineno}行目)")
        return
    try:
        checks = validate(value)
    except ValueError as error:
        print(error)
        return
    for check in checks:
        print(f"{check['name']}: {check['status']}")


if __name__ == "__main__":
    main(sys.argv[1])
