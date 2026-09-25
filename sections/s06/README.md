# Section 06: CLIチャットと会話履歴

この演習では、CLIからAmazon Bedrockへ質問し、応答を受け取る小さなチャットを作ります。複数の質問を続けるとき、過去のメッセージを次のリクエストにも含める方法と、含めない方法を比べます。最後に終了操作と、秘密情報を表示しないエラー確認を加えます。

## 準備

- Python 3.11以降
- `uv`
- AWS CLI v2で設定したAWSプロファイルと有効なログインセッション
- Amazon Bedrockで利用できるモデル。初期設定は`amazon.nova-lite-v1:0`
- 対象モデルに対する`bedrock:InvokeModel`権限

認証情報をコードや`.env`へコピーしません。IAM Identity Centerを使う場合は、演習前にログインします。

```text
aws sso login --profile <profile-name>
```

リポジトリの最上位フォルダーで、使うプロファイルとリージョンを設定します。モデルがそのリージョンで利用できることも確認してください。

Windows PowerShell:

```powershell
$env:AWS_PROFILE = "<profile-name>"
$env:AWS_DEFAULT_REGION = "ap-northeast-1"
cd sections/s06
uv sync
```

macOS / Linux:

```sh
export AWS_PROFILE="<profile-name>"
export AWS_DEFAULT_REGION="ap-northeast-1"
cd sections/s06
uv sync
```

`uv sync`で、この演習専用の仮想環境にboto3を準備します。認証にはboto3の標準認証情報プロバイダーを使います。必要なら環境変数`BEDROCK_MODEL_ID`で、利用可能な別モデルIDを指定できます。

## L02: CLIから質問する

```text
uv run python s06_l02.py
```

質問を入力すると、プログラムは`role: "user"`のメッセージを一つ作り、Converse APIを一度呼び出して本文を表示します。表示される文章はモデルが生成するため、実行ごとに変わる場合があります。空の質問を入力するとAPIを呼ばずに終了します。

`converse_turn()`と`s06_l02.py`を見て、CLI入力がメッセージになり、応答本文が表示される流れを追ってください。

## L03: 履歴あり・なしを比べる

履歴ありで起動します。

```text
uv run python s06_l03.py
```

まず「私は東京に住んでいます」と入力し、次に「私はどこに住んでいますか」と聞きます。2回目のリクエストには最初のuserメッセージとassistant応答も含まれます。`/exit`または`/quit`で終了します。

同じ流れを履歴なしでも試します。

```text
uv run python s06_l03.py --no-history
```

2回目の質問にはその質問だけが送られます。応答はモデルや実行ごとに異なりますが、リクエストの`messages`に過去のやり取りがあるかどうかをコードで確認できます。履歴が長くなると、各回で送る入力token数と料金が増えることにも注目してください。

## L04: 終了と失敗時の確認

```text
uv run python s06_l04.py
```

`/exit`または`/quit`で終了します。ターミナルで`Ctrl+C`を押すか入力を終了した場合も、tracebackを表示せずチャットを閉じます。

APIエラー時はエラーコードと、応答に含まれる場合はRequest IDを表示します。AWS接続エラーではプロファイル、ログイン状態、リージョン、ネットワークの確認を案内します。ログと画面には例外本文、質問、応答、認証情報を出しません。失敗後も次の質問を入力できます。

原因を調べるときは、まずAWS CLIのログイン状態とプロファイル、リージョン、モデルの利用可否、IAM権限を確認します。`AccessDeniedException`なら対象モデルに対する`bedrock:InvokeModel`、`ThrottlingException`なら利用状況とクォータを確認し、連続再試行は避けてください。

## 自動テスト

テストはモック応答を使い、AWSへ接続しません。履歴を含むリクエスト、履歴なしのリクエスト、終了操作、エラー表示と会話継続を確認します。

```text
uv run python -m unittest discover -s tests -v
```

## 料金と権限

このSectionはBedrock Runtimeへの推論を行い、AWS resourceを作成しません。各有効な質問でAPIを1回呼び、応答上限は128 tokensです。課金はモデル、リージョン、入力・出力token数で変わります。履歴ありでは過去の会話も各リクエストの入力に含まれるため、長く続けるほど入力量が増えます。実行前に[Amazon Bedrock料金表](https://aws.amazon.com/bedrock/pricing/)で対象モデルとリージョンの料金を確認してください。

権限は対象モデルへの`bedrock:InvokeModel`に限定してください。必要なモデル利用条件を確認し、自分で権限を広げず、利用可能な範囲を管理者に確認します。

## 後片付け

チャットを終了すると実行中の処理はありません。AWS resourceは作らないため、AWS側の削除作業はありません。仮想環境を削除する場合はリポジトリ最上位へ戻り、`sections/s06/.venv`だけを削除します。

Windows PowerShell:

```powershell
cd ../..
if (Test-Path -LiteralPath .\sections\s06\.venv) { Remove-Item -LiteralPath .\sections\s06\.venv -Recurse }
Test-Path -LiteralPath .\sections\s06\.venv
```

最後の結果が`False`なら削除できています。

macOS / Linux:

```sh
cd ../..
if [ -d sections/s06/.venv ]; then rm -r -- sections/s06/.venv; fi
test ! -e sections/s06/.venv && echo "s06の仮想環境を削除しました"
```

必要なら`AWS_PROFILE`、`AWS_DEFAULT_REGION`、`BEDROCK_MODEL_ID`の環境変数を現在のターミナルから解除します。AWS CLIのプロファイルや認証情報は削除しません。

## 参考資料

- [Amazon Bedrock Converse API](https://docs.aws.amazon.com/bedrock/latest/APIReference/API_runtime_Converse.html)
- [Amazon Bedrock Converse APIの概要](https://docs.aws.amazon.com/bedrock/latest/userguide/conversation-inference.html)
- [Amazon Nova Lite model card](https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-amazon-nova-lite.html)
- [Amazon Bedrock料金表](https://aws.amazon.com/bedrock/pricing/)
