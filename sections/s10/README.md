# Section 10: 演習用AWSリソースを片付ける

Section 9で作成したS3演習用バケットと調査メモを、対象を確かめながら削除します。Courseの演習では新しいバケット1個と、その中の`training/s09/incident-note.txt`だけを作成します。Bedrockの推論は永続resourceを作らないため、ここで削除するBedrock resourceはありません。

## 削除前の確認

AWS CLIを使える環境で、Section 9の演習時に記録したprofile、Region、バケット名を用意します。別のターミナルやAWS profileへ切り替えた場合も、同じ値を指定してください。まずアカウントとRegionを確認します。

```sh
aws sts get-caller-identity --profile <profile>
aws configure get region --profile <profile>
aws s3api get-bucket-location --bucket <bucket> --profile <profile>
```

表示されたアカウントが演習に使ったアカウントであること、バケット名がSection 9で自分が新しく作成したものと完全に一致することを確認します。Regionも作成時のRegionと一致させてください。`get-bucket-location`の結果が`null`なら`us-east-1`、`EU`なら`eu-west-1`です。どれか一つでも確認できない場合は、削除せずに停止します。

この演習で作ったバケットに限り、オブジェクト一覧が次の固定keyだけであることを確認します。

```sh
aws s3api list-objects-v2 --bucket <bucket> --profile <profile> --region <region> --query 'Contents[].Key' --output json
aws s3api get-bucket-versioning --bucket <bucket> --profile <profile> --region <region> --query Status --output text
```

オブジェクト一覧が`["training/s09/incident-note.txt"]`で、versioningの状態が設定なし（CLI出力の`None`）なら次へ進めます。別のkeyが一つでもある、一覧が空、versioningが有効または停止状態になっている場合は、この手順で一括削除しません。別のデータや過去versionが含まれる可能性があるため、内容と所有者を確認してください。

## オブジェクトを削除して確認する

対象keyだけを削除します。

```sh
aws s3api delete-object --bucket <bucket> --key training/s09/incident-note.txt --profile <profile> --region <region>
```

削除後、オブジェクト一覧が空であることを確認します。

```sh
aws s3api list-objects-v2 --bucket <bucket> --profile <profile> --region <region> --query 'Contents[].Key' --output json
```

空の場合は`[]`または`null`が表示されます。keyが残っている、または一覧を確認できない場合はバケットを削除しません。`delete-object`を実行しても、versioningが有効なバケットではdelete markerが作成されるだけの場合があります。versioningが有効または停止状態なら、version IDを確認せずに削除を続けないでください。

## 空のバケットを削除して確認する

バケット削除は復元できず、削除した名前を別のAWS利用者が取得できるようになる可能性があります。アカウント、Region、バケット名をもう一度照合し、この演習のために自分で作ったバケットで、オブジェクト一覧が空であることを確認してから実行します。

```sh
aws s3api delete-bucket --bucket <bucket> --profile <profile> --region <region>
```

削除後に存在確認を行います。

```sh
aws s3api head-bucket --bucket <bucket> --profile <profile> --region <region>
```

バケットが存在しないことを示す応答（通常は`404`）なら削除を確認できます。別のエラーは削除確認として扱わず、アカウント、Region、権限を調べます。削除の伝播に時間がかかる場合があります。再実行で解決しようとせず、状態を確認してください。

## 必要な権限と料金

この手順では対象バケットの`s3:GetBucketLocation`、`s3:GetBucketVersioning`、`s3:ListBucket`、`s3:DeleteObject`、空になったバケットの`s3:DeleteBucket`が必要です。必要権限がない場合は、バケット名・Region・必要なactionを管理者へ伝えて相談してください。権限を自分で追加しないでください。

S3の保管、リクエスト、転送には料金が発生する場合があります。演習後に残ったresourceがないか、AWSコンソールでも対象アカウントとRegionを選んで確認してください。Bedrockの推論料金は呼び出しごとに発生し得ますが、削除するresourceはありません。

## ローカル環境

Section 9の実行で作成した`sections/s09/.venv`が不要なら、演習repositoryの最上位でそのdirectoryだけを削除できます。AWS CLI profileや認証情報は削除しません。

PowerShell:

```powershell
if (Test-Path -LiteralPath .\sections\s09\.venv) { Remove-Item -LiteralPath .\sections\s09\.venv -Recurse }
Test-Path -LiteralPath .\sections\s09\.venv
```

macOS / Linux:

```sh
if [ -d sections/s09/.venv ]; then rm -r -- sections/s09/.venv; fi
test ! -e sections/s09/.venv && echo "s09の仮想環境を削除しました"
```

## 参考資料

- [Amazon S3バケットの削除](https://docs.aws.amazon.com/AmazonS3/latest/userguide/delete-bucket.html)
- [Amazon S3オブジェクトversionの削除](https://docs.aws.amazon.com/AmazonS3/latest/userguide/DeletingObjectVersions.html)
- [Amazon S3料金表](https://aws.amazon.com/s3/pricing/)
