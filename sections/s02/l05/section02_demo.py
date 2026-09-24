import argparse
import sys

from rich.console import Console
from rich.panel import Panel


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Display a note using a project dependency managed by uv."
    )
    parser.add_argument("note", help="A short note to display")
    args = parser.parse_args()

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    Console(legacy_windows=False).print(
        Panel(args.note, title="確認事項", border_style="cyan")
    )


if __name__ == "__main__":
    main()
