import sys

import requests


def main() -> None:
    print(f"Virtual environment: {sys.prefix}")
    print(f"Base Python: {sys.base_prefix}")
    print(f"requests version: {requests.__version__}")
    print(f"requests location: {requests.__file__}")


if __name__ == "__main__":
    main()
