"""Create one empty general purpose S3 bucket and upload the fixed demo note."""

import argparse
import sys
from pathlib import Path

from botocore.exceptions import BotoCoreError, ClientError

from s09_common import configure_console, create_s3_client

SAMPLE_PATH = Path(__file__).parent / "sample" / "incident-note.txt"
OBJECT_KEY = "training/s09/incident-note.txt"


def prepare_bucket(client, bucket, region, note_bytes):
    try:
        client.head_bucket(Bucket=bucket)
    except ClientError as error:
        status = error.response.get("ResponseMetadata", {}).get("HTTPStatusCode")
        code = error.response.get("Error", {}).get("Code")
        if status != 404 and code not in {"404", "NoSuchBucket", "NotFound"}:
            raise ValueError("バケットの存在を確認できません。名前・権限・アカウントを確認し、既存バケットへ上書きしないでください。") from error
    else:
        raise ValueError("指定したバケットは既に存在します。演習専用の新しい名前を指定してください。")

    request = {"Bucket": bucket}
    if region != "us-east-1":
        request["CreateBucketConfiguration"] = {"LocationConstraint": region}
    client.create_bucket(**request)
    client.put_object(Bucket=bucket, Key=OBJECT_KEY, Body=note_bytes, ContentType="text/plain; charset=utf-8")
    return OBJECT_KEY


def main(argv=None):
    parser = argparse.ArgumentParser(description="架空の調査メモを新しいS3バケットへ配置します。")
    parser.add_argument("--bucket", required=True, help="自分で用意した一意な演習用バケット名")
    parser.add_argument("--region", required=True, help="作成するAWS Region")
    args = parser.parse_args(argv)
    configure_console()
    try:
        key = prepare_bucket(create_s3_client(args.region), args.bucket, args.region, SAMPLE_PATH.read_bytes())
    except ValueError as error:
        print(error, file=sys.stderr)
        return 1
    except (BotoCoreError, ClientError, OSError) as error:
        print(f"S3の準備に失敗しました ({type(error).__name__})。認証、Region、権限を確認してください。", file=sys.stderr)
        print("バケット作成後に失敗した場合は、READMEのcleanup手順でオブジェクトと空のバケットを削除してください。", file=sys.stderr)
        return 1
    print(f"作成したバケット: {args.bucket}")
    print(f"配置したオブジェクト: s3://{args.bucket}/{key}")
    print(f"Region: {args.region}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
