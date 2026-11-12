"""自作モジュールから関数とlistを受け取る例。"""

from check_data import get_checks


def main() -> None:
    import sys

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    checks = get_checks()
    print(f"受け取った確認項目: {len(checks)}件")
    for check in checks:
        print(f"{check['name']}: {check['status']}")


if __name__ == "__main__":
    main()
