import json
import sys
from pathlib import Path


def load_checks(path):
    value = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(value, list):
        raise ValueError("最上位は配列にしてください。")
    for i, item in enumerate(value, 1):
        if not isinstance(item, dict) or item.get("status") not in {"ok", "needs_review"}:
            raise ValueError(f"{i}番目のデータを確認してください。")
    return value


def main(arguments=None):
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    args = sys.argv[1:] if arguments is None else arguments
    path = Path(args[0]) if args else Path(__file__).with_name("cases.json")
    try:
        checks = load_checks(path)
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as error:
        print(f"入力を確認してください: {error}")
        return 1
    for item in checks:
        print(f"{item.get('name', '項目')}: {item['status']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
