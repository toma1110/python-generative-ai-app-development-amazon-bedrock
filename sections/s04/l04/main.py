"""Show the AWS account and Region selected by the active boto3 configuration."""

import sys

import boto3
from botocore.exceptions import BotoCoreError


class RegionNotConfiguredError(Exception):
    """Raised when no AWS Region is available in the active configuration."""


def read_target(session=None):
    """Return the active account ID and Region without exposing credentials."""
    session = session or boto3.Session()
    region = session.region_name
    if not region:
        raise RegionNotConfiguredError

    identity = session.client("sts", region_name=region).get_caller_identity()
    return identity["Account"], region


def main():
    try:
        account_id, region = read_target()
    except RegionNotConfiguredError:
        print(
            "リージョンが設定されていません。AWS_DEFAULT_REGIONまたは"
            "プロファイルのリージョン設定を確認してください。",
            file=sys.stderr,
        )
        return 1
    except BotoCoreError:
        print(
            "AWS接続を確認できませんでした。プロファイル、ログイン状態、"
            "リージョン、ネットワークを確認してください。",
            file=sys.stderr,
        )
        return 1

    print(f"接続先アカウント: {account_id}")
    print(f"接続先リージョン: {region}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
