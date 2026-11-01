"""Read UTF-8 JSON text and display the checks."""

import json
import sys
from pathlib import Path


def load_checks(path: Path):
    text = path.read_text(encoding="utf-8")
    return json.loads(text)


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    path = Path(__file__).with_name("cases.json")
    try:
        checks = load_checks(path)
    except FileNotFoundError:
        print(f"ファイルが見つかりません: {path.name}。名前と場所を確認してください。")
        return
    for check in checks:
        print(f"{check['name']}: {check['status']}")


if __name__ == "__main__":
    main()
