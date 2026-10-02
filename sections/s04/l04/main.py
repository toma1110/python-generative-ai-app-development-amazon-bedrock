"""Show the AWS account and Region selected by the active boto3 configuration."""

import sys

import boto3
from botocore.exceptions import BotoCoreError, ClientError


def read_target(session, region):
    """Return the account ID selected by this session and Region."""
    sts_client = session.client("sts", region_name=region)
    response = sts_client.get_caller_identity()
    account_id = response["Account"]
    return account_id


def main():
    try:
        session = boto3.Session()
        region = session.region_name
        if not region:
            print(
                "リージョンが設定されていません。AWS_DEFAULT_REGIONまたは"
                "プロファイルのリージョン設定を確認してください。",
                file=sys.stderr,
            )
            return 1
        account_id = read_target(session, region)
    except (BotoCoreError, ClientError):
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
