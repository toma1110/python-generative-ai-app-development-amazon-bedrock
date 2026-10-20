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

次のコマンドで空のバケットを削除します。成功した場合、AWSが削除を受け付けたことを確認できます。失敗した場合は削除完了とせず、アカウント、Region、バケット名、権限を調べて停止してください。再実行で解決しようとしないでください。

PowerShell:

```powershell
aws s3api delete-bucket --bucket <bucket> --profile <profile> --region <region>
if ($LASTEXITCODE -ne 0) { throw "バケット削除を確認できません。終了コード: $LASTEXITCODE" }
```

macOS / Linux:

```sh
if aws s3api delete-bucket --bucket <bucket> --profile <profile> --region <region>; then
  echo "AWSがバケット削除を受け付けました"
else
  echo "バケット削除を確認できません。アカウント、Region、バケット名、権限を調べて停止してください" >&2
  exit 1
fi
```

削除成功後、同じprofileのアカウントが作成時と一致していることを再確認し、アカウント全体のバケット一覧を更新して対象名がないことを確認します。

```sh
aws sts get-caller-identity --profile <profile>
aws s3api list-buckets --profile <profile> --query "Buckets[?Name=='<bucket>'].Name" --output json
```

アカウントIDが一致し、一覧結果が`[]`なら、このアカウントの一覧に対象名がないことを確認できます。対象名が表示される、一覧を取得できない、またはアカウントIDを照合できない場合は削除完了と扱わず、`DeleteBucket`を繰り返さずに管理者へ相談してください。`ListBuckets`はアカウント全体を返すため、Regionで絞り込む操作ではありません。

`HeadBucket`は状況を調べるために実行できますが、削除完了の判定には使いません。

```sh
aws s3api head-bucket --bucket <bucket> --profile <profile> --region <region>
```

`HeadBucket`の`400`、`403`、`404`はいずれも、バケットが存在しないこととアクセス上の問題を区別できない場合があります。どの応答も削除の成否を単独では証明しません。`DeleteBucket`が成功していない場合は削除完了とせず、アカウント、Region、バケット名、権限を調べてください。結果が食い違う場合も削除を繰り返さず、状態を確認してください。

## 必要な権限と料金

この手順では対象バケットの`s3:GetBucketLocation`、`s3:GetBucketVersioning`、`s3:ListBucket`、`s3:DeleteObject`、空になったバケットの`s3:DeleteBucket`、削除後の一覧確認に`s3:ListAllMyBuckets`が必要です。必要権限がない場合は、バケット名・Region・必要なactionを管理者へ伝えて相談してください。権限を自分で追加しないでください。

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
