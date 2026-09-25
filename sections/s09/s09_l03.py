"""Read a specific S3 object and print its UTF-8 text."""

from botocore.exceptions import BotoCoreError, ClientError


def read_s3_text(client, bucket, key):
    response = client.get_object(Bucket=bucket, Key=key)
    with response["Body"] as body:
        text = body.read().decode("utf-8")
    if not text.strip():
        raise ValueError("S3オブジェクトが空です。")
    return text


def main(argv=None):
    import argparse
    import sys

    from s09_common import configure_console, create_s3_client

    parser = argparse.ArgumentParser(description="指定したS3オブジェクトをUTF-8で読み取ります。")
    parser.add_argument("--bucket", required=True)
    parser.add_argument("--key", default="training/s09/incident-note.txt")
    args = parser.parse_args(argv)
    configure_console()
    try:
        print(read_s3_text(create_s3_client(), args.bucket, args.key))
    except (BotoCoreError, ClientError, UnicodeDecodeError, ValueError) as error:
        print(f"読み取りに失敗しました ({type(error).__name__})。バケット・key・Regionとs3:GetObject権限を確認してください。", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
