# Section 09: S3の調査メモを読む

この演習では、架空の障害調査メモをS3に置き、boto3で読み取ってAmazon BedrockのConverse APIへ渡します。最後に、ローカルファイルとS3を同じアプリで切り替え、同じ原文に対するプロンプト変更前後の応答を人が照合します。モデルの応答だけで原因や対応を決めないでください。

## 準備

- Python 3.11以上、[uv](https://docs.astral.sh/uv/)、AWS CLIを使えるローカル環境を用意します。
- AWS認証は既存のAWS CLI profileまたはIAM Identity Center profileを利用します。コードにaccess keyを書きません。
- AWS profileとRegionを設定し、操作対象を確認します。`<profile>`と`<region>`は自分の値に置き換えます。

```sh
aws sts get-caller-identity --profile <profile>
aws configure get region --profile <profile>
```

表示されたアカウントが演習用であることを確認してください。想定外のアカウントならここで止め、正しいprofileを選び直します。以降のPython commandを実行する同じterminalでprofileとRegionを指定します。

```sh
export AWS_PROFILE=<profile>
export AWS_DEFAULT_REGION=<region>
```

PowerShellでは次のように設定します。

```powershell
$env:AWS_PROFILE = "<profile>"
$env:AWS_DEFAULT_REGION = "<region>"
```

作るresourceは、指定したRegionの新しいS3 general purpose bucket 1個と、その中の`training/s09/incident-note.txt`だけです。bucketは世界で一意な名前が必要です。既存bucketは使わず、S3演習専用の新しい名前を決めます。scriptも既存bucketを検出したら書き込みません。

## 準備とS3への配置（s09-l02）

リポジトリの最上位で依存関係を用意します。

```sh
uv sync --project sections/s09
```

アカウントIDとRegionをもう一度確認し、bucket名を一意な値へ置き換えてから実行します。

```sh
uv run --project sections/s09 python sections/s09/s09_l02.py --bucket <unique-bucket-name> --region <region>
```

成功すると作成したbucket、object URI、Regionが表示されます。表示された3項目をcleanupまで控えてください。途中でobject uploadに失敗した場合、bucketだけが残ることがあります。cleanup手順で中身を確認し、空にしてから削除します。

## boto3で指定したS3 objectを読む（s09-l03）

```sh
uv run --project sections/s09 python sections/s09/s09_l03.py --bucket <unique-bucket-name>
```

演習用の架空メモが表示されます。`--key`を省略した場合の既定値は`training/s09/incident-note.txt`です。この演習では別のkeyを指定せず、L02で配置したobjectだけを読みます。

## 要約・確認項目・追加質問（s09-l04 / s09-l05）

まずローカル入力で要約します。

```sh
uv run --project sections/s09 python sections/s09/s09_app.py --source local --task summary
```

同じメモから、次に確認する項目を挙げます。

```sh
uv run --project sections/s09 python sections/s09/s09_app.py --source local --task checks
```

S3入力に切り替えて、担当者からの追加質問を実行します。

```sh
uv run --project sections/s09 python sections/s09/s09_app.py --source s3 --bucket <unique-bucket-name> --task ask --question "影響した注文数は確認できていますか"
```

応答を表示された原文と照合し、各主張の根拠と未確認事項を自分で確かめます。メモにはエラー率低下、timeoutを含むログ3件、デプロイ履歴の調査開始が書かれています。一方、timeoutが原因だったか、影響注文数、デプロイの有無、ロールバック要否は未確認です。モデルがこれらを確定事項のように答えた場合はその箇所を記録し、追加確認が必要と判断してください。

## 同じ原文で変更前後を比べる（s09-l06）

まず変更前の結果を記録します。次のcommandは同じローカルメモに2つの異なるプロンプトを適用します。

```sh
uv run --project sections/s09 python sections/s09/s09_l06.py --source local
```

続いて`sections/s09/s09_l06.py`を開き、`REVISED_PROMPT`の末尾に「影響した注文数は未確認なら未確認と明記してください。」を追加して保存します。`BASELINE_PROMPT`、`sample/incident-note.txt`、入力元、モデル、Regionは変えません。`main`が同じメモを`load_note`で1回読み、`compare`がその文字列を変更前・変更後の2回の`ask_model`へ渡す箇所をコードで確認してください。表示される2組の回答とtoken量・応答時間が出力です。

同じcommandを再実行し、編集前に控えた結果と並べてください。変更前側のpromptは同じでも生成結果は実行ごとに揺れるため、文字列の完全一致を合否基準にしません。次にAWS APIを呼ばないunit testを実行し、同じメモを2回の推論へ渡すテストが成功することを確認します。

```sh
uv run --directory sections/s09 python -m unittest discover -s tests -v
```

`sample/incident-note.txt`の原文と各回答を照合し、影響した注文数を根拠なく断定していないか、確認済みの事実と未確認事項が分かれているかを記録します。コードの編集箇所、入力→処理→出力、テスト結果、原文との一致・不一致を根拠に、その変更を採用・修正・保留のどれにするか決めてください。提案されたコードを確認せず正解として扱わないでください。`--source s3 --bucket <unique-bucket-name>`へ変えれば、S3から読み取った同じメモでも比較できます。S3へ切り替える場合は、比較する間の入力元をそろえます。

各実行で入力token、出力token、Bedrock応答時間を表示します。料金は選択したモデルとRegion、実際のtoken量で変わります。モデルとRegionを決めたら[Amazon Bedrock料金表](https://aws.amazon.com/bedrock/pricing/)で入力・出力単価を確認し、単価の課金単位に合わせて見積もってください。比較commandは推論を2回呼び出すため、再実行ごとに追加料金がかかり得ます。S3のbucket作成自体に料金はありませんが、オブジェクト保管、request、データ転送等が発生し得ます。小さな教材メモ1個に限定し、演習後は削除してください。[Amazon S3料金表](https://aws.amazon.com/s3/pricing/)を参照します。

## 権限

必要な権限は次の操作に限定します。

- 準備: bucket存在確認の`s3:ListBucket`、`s3:CreateBucket`、固定keyへの`s3:PutObject`
- S3入力: 固定keyへの`s3:GetObject`
- Section 10のcleanup: 対象keyへの`s3:DeleteObject`、空になった演習用bucketへの`s3:DeleteBucket`
- Bedrock呼び出し: 利用するモデルに対する`bedrock:InvokeModel`

権限は自分で追加せず、必要なら管理者へ対象bucket、key、actionを示して相談してください。Converse APIは`bedrock:InvokeModel`権限を必要とします。[Amazon Bedrock Converse API](https://docs.aws.amazon.com/bedrock/latest/APIReference/API_runtime_Converse.html)と[S3 IAM action一覧](https://docs.aws.amazon.com/AmazonS3/latest/userguide/access-management.html)を参照してください。

## 自動テスト

テストはAWS APIを呼ばず、S3とBedrockの応答をmockします。

```sh
uv run --directory sections/s09 python -m unittest discover -s tests -v
```

## 想定と異なる場合

- `AccessDenied`や`403`: `AWS_PROFILE`、表示されたアカウント、Region、対象bucket/keyと上記actionを確認します。S3に`ListBucket`権限がない場合、存在しないkeyでも404でなく403になる場合があります。
- bucket作成時の名前エラー: 別の新しい名前を選びます。既存bucketが見つかったときは上書きしません。
- Regionエラー: `AWS_DEFAULT_REGION`とs09-l02の`--region`を同じ値にし、作成後は同じRegionを使います。
- `NoSuchKey`: 表示されたbucketと固定keyを照合します。object名の大文字小文字も一致させます。
- Bedrockのmodel/access/quota error: accountでのモデル利用可否、Region、`BEDROCK_MODEL_ID`、IAM権限とquotaを確認します。既定modelは`amazon.nova-lite-v1:0`で、変更する場合は`BEDROCK_MODEL_ID`へ設定します。
- UTF-8 decode error: 指定objectがこの教材のテキストfileか確認します。

エラー表示には応答本文やAWS credentialを含めません。実データ、個人情報、機密情報、credentialを入力しないでください。

## Cleanup

このSectionでは作成したbucket/objectを残し、Section 10で削除します。削除前に`aws sts get-caller-identity`でaccountを再確認し、手元に控えた完全なbucket名がこの演習で自分が新規作成したものと一致することを確認します。bucket名が違う場合、または他のobjectがある場合は停止し、bucket全体を削除しないでください。

Section 10の手順で、まず演習objectだけを削除します。

```sh
aws s3api delete-object --bucket <unique-bucket-name> --key training/s09/incident-note.txt
aws s3api head-object --bucket <unique-bucket-name> --key training/s09/incident-note.txt
aws s3api list-objects-v2 --bucket <unique-bucket-name>
```

`head-object`が`404 Not Found`となり、list-objects-v2の`KeyCount`が`0`ならobjectがなく、bucketが空であることを確認できます。`404`以外、または`KeyCount`が0でなければ原因を確認し、bucketを削除しません。空の演習bucketだけを削除します。

```sh
aws s3api delete-bucket --bucket <unique-bucket-name> --region <region>
aws s3api head-bucket --bucket <unique-bucket-name>
```

削除成功後、head-bucketがbucket不存在を示す応答になることを確認します。bucket削除は復元できない操作なので、名前・account・Regionを確認できない場合は実行しません。[DeleteBucketの注意](https://docs.aws.amazon.com/AmazonS3/latest/userguide/delete-bucket.html)を参照してください。削除後、必要ならアプリ用の一時環境だけを片付けます。

`uv sync`が作った`sections/s09/.venv`を削除する場合は、演習用repositoryの最上位で次のいずれかを実行し、そのpathだけを削除してください。AWS CLI profileや認証情報は削除しません。

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

- [S3 GetObject API](https://docs.aws.amazon.com/AmazonS3/latest/API/API_GetObject.html)
- [S3 bucket作成](https://docs.aws.amazon.com/AmazonS3/latest/userguide/creating-bucket.html)
- [Amazon Bedrock Converse API](https://docs.aws.amazon.com/bedrock/latest/APIReference/API_runtime_Converse.html)
- [Amazon Bedrock料金表](https://aws.amazon.com/bedrock/pricing/)
- [Amazon S3料金表](https://aws.amazon.com/s3/pricing/)
