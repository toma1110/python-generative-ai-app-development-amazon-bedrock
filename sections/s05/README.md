# Section 05: Bedrockを1回呼ぶ

この演習では、PythonからAmazon Bedrock Converse APIへ1回のuserメッセージを送り、応答を読みます。次にsystemメッセージと推論パラメータを別々に変えて出力を比べ、最後に応答の利用量と失敗情報を確認します。モデルの出力は毎回変わることがあり、表示例との一致を正解条件にはしません。

## 事前準備

- Python 3.11以降
- `uv`
- AWS CLI v2で設定したAWSプロファイルと有効なログインセッション
- `bedrock:InvokeModel`を許可されたAWS identity。Converse APIでは`bedrock:InvokeModel`が必要です。モデルごと・リージョンごとの利用条件も確認してください。
- Amazon Bedrockで利用できるモデル。初期設定では`amazon.nova-lite-v1:0`を使います。

認証情報をコードや`.env`へコピーしません。AWS CLIのIAM Identity Centerプロファイルを使う場合は、先にログインしてください。

```text
aws sso login --profile <profile-name>
```

## 接続先と依存関係

リポジトリの最上位フォルダーで実行します。プロファイル名とリージョンは、自分が使う値に置き換えてください。モデルが指定リージョンで使用可能かも確認します。

Windows PowerShell:

```powershell
$env:AWS_PROFILE = "<profile-name>"
$env:AWS_DEFAULT_REGION = "ap-northeast-1"
cd sections/s05
uv sync
```

macOS / Linux:

```sh
export AWS_PROFILE="<profile-name>"
export AWS_DEFAULT_REGION="ap-northeast-1"
cd sections/s05
uv sync
```

`uv sync`でboto3とその依存関係をこの演習の仮想環境に準備します。コードはboto3の標準認証情報プロバイダーを使い、認証情報を表示しません。リージョンは`AWS_DEFAULT_REGION`またはAWSプロファイルから選ばれます。

## L02: userメッセージを1回送る

```text
uv run python s05_l02.py
```

固定のuserメッセージをConverse APIへ1回送り、モデルのテキスト応答を表示します。表示はたとえば、監視アラームの調査時に確認する項目の短い説明です。文章や言い回しは実行ごとに異なる場合があります。

`s05_l02.py`では`messages`に`role: "user"`と`content`のテキストを設定し、`client.converse()`を1回呼び出しています。メッセージを自分の質問に変えて再実行し、入力と応答の関係を確かめます。

## L03: systemメッセージと推論パラメータを比べる

```text
uv run python s05_l03.py
```

同じ質問を次の3条件で送り、応答を並べて表示します。

1. 基準: systemメッセージなし、temperature `0.0`、topP `1.0`
2. system変更: systemメッセージだけを追加し、推論パラメータは基準と同じ
3. 推論パラメータ変更: systemメッセージを使わず、temperature `0.8`、topP `0.9`へ変更

条件を一つずつ変えて出力を比べます。temperatureやsystemの変更で必ず特定の文面になるわけではありません。`s05_l03.py`の`SYSTEM`と`inferenceConfig`を見つけ、それぞれ一箇所だけ変更して再実行します。このLectureは比較のため3回呼び出します。

## L04: 応答、利用量、エラーを読む

```text
uv run python s05_l04.py
```

成功時は応答本文、`stopReason`、`usage`の入力・出力・合計token数、`metrics.latencyMs`を表示します。利用量と応答時間は実際の応答に含まれる値を表示し、固定値ではありません。

失敗時はAWSエラーコードと、応答に含まれる場合はRequest IDを表示します。IAM権限、モデル利用可否、クォータ、プロファイル、リージョン、ネットワークを確認してください。エラー本文には環境固有情報が含まれる可能性があるため、コードは全文を画面へ出しません。調査時にも認証情報や個人情報が含まれないことを確認してから共有します。

## 自動テスト

テストはAWSへ接続せず、モック応答でメッセージ構造、Converse呼び出し回数、比較時の変更箇所、応答の利用量抽出、エラー表示を確認します。

```text
uv run python -m unittest discover -s tests -v
```

## 料金、権限、安全上の注意

Bedrock Runtimeのモデル利用は入力・出力token数に応じた従量課金です。Sectionを一巡すると、L02で1回、L03で3回、L04で1回、合計5回呼び出します。各呼び出しの出力上限は96 tokensです。したがって一巡の出力上限は480 tokensで、入力はコード内の短い固定文です。実際の料金はモデル、リージョン、利用token数で変わるため、実行前に[Amazon Bedrock料金表](https://aws.amazon.com/bedrock/pricing/)で現在のモデル・リージョンの単価を確認してください。繰り返し実行するとその分の従量料金が増えます。

この演習はBedrock Runtimeへの推論だけを実行し、AWS resourceを作成しません。最小権限のIAM policyを使い、対象モデルへの`bedrock:InvokeModel`に絞ってください。たとえば東京リージョンのNova Lite foundation model ARNは`arn:aws:bedrock:ap-northeast-1::foundation-model/amazon.nova-lite-v1:0`です。必要な利用条件はアカウントとモデルにより異なることがあります。権限を自分で広げず、利用可能なモデルと許可範囲を管理者に確認してください。

## 想定と異なる場合

- 認証情報が見つからない、またはSSO期限切れ: 正しいプロファイルを指定し、`aws sso login --profile <profile-name>`でログインします。
- 違うアカウントを使っていそう: `aws sts get-caller-identity`で接続先を確認し、演習を続ける前に意図したアカウントであることを確かめます。
- リージョンが空・違う、またはモデルが利用できない: `AWS_DEFAULT_REGION`とプロファイル設定を確認し、Bedrockのモデルのリージョン対応とアカウント内の利用条件を確認します。
- `AccessDeniedException`: エラーコードを見て、対象モデルで`bedrock:InvokeModel`が許可されているか管理者に確認します。
- `ThrottlingException`またはクォータ関連エラー: 少し時間を空けて再試行する前に、そのリージョンとモデルのクォータおよびアカウント利用状況を確認します。ループで繰り返し再試行しません。
- `ValidationException`: `inferenceConfig`の値がモデルの範囲に合っているか、model IDとリージョンが正しいかを確認します。
- `uv`や依存関係のエラー: `uv --version`、Pythonバージョン、ネットワーク接続を確認してから`uv sync`をやり直します。

## 後片付け

停止中のプログラムはありません。AWS resourceは作成しないため削除作業は不要です。仮想環境を削除する場合は、リポジトリ最上位フォルダーへ戻り、`sections/s05/.venv`だけを削除して存在しないことを確認します。

Windows PowerShell:

```powershell
cd ../..
if (Test-Path -LiteralPath .\sections\s05\.venv) { Remove-Item -LiteralPath .\sections\s05\.venv -Recurse }
Test-Path -LiteralPath .\sections\s05\.venv
```

最後が`False`なら削除できています。

macOS / Linux:

```sh
cd ../..
if [ -d sections/s05/.venv ]; then rm -r -- sections/s05/.venv; fi
test ! -e sections/s05/.venv && echo "s05の仮想環境を削除しました"
```

確認メッセージが表示されれば削除できています。`pyproject.toml`と`uv.lock`は依存関係の再現に使うので残します。必要ならAWSプロファイルとリージョンの環境変数だけを現在のターミナルから解除します。

## 参考資料

- [Amazon Bedrock Converse API](https://docs.aws.amazon.com/bedrock/latest/userguide/conversation-inference.html)
- [Nova Lite model card](https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-amazon-nova-lite.html)
- [Amazon Bedrock inference prerequisites](https://docs.aws.amazon.com/bedrock/latest/userguide/inference-prereq.html)
- [Amazon Bedrock pricing](https://aws.amazon.com/bedrock/pricing/)
- [Boto3 Bedrock Runtime client](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/bedrock-runtime.html)
