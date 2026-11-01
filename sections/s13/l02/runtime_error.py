import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Exercise: this file is intentionally absent at first.
text = Path("missing.txt").read_text(encoding="utf-8")
print(text)
