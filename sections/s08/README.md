# Section 08: 生成AIの出力を評価・改善する

この演習では、同じ架空の障害調査メモで変更前後のプロンプトを比べ、出力を原文と照合します。続いて会話履歴の長さを変え、Bedrockが返すtoken利用量と応答時間を観察します。出力の正しさを自動採点せず、事実と未確認事項を自分で見分けて、採用・修正・保留を判断します。

## 準備

- Python 3.11以降と`uv`
- AWS CLI v2で設定したプロファイルと有効なログインセッション
- 使用するリージョンでAmazon Bedrockの推論が利用できること
- 対象モデルへの`bedrock:InvokeModel`権限

この教材をまだ取得していない場合は、作業用フォルダーで公開リポジトリをcloneします。

```text
git clone https://github.com/toma1110/python-generative-ai-app-development-amazon-bedrock.git
cd python-generative-ai-app-development-amazon-bedrock
```

ZIPで取得する場合は、GitHubのCodeメニューから「Download ZIP」を選び、展開したフォルダーを開きます。すでにclone済みの場合は、リポジトリ最上位へ移動してください。

認証情報をコードや`.env`へコピーしません。IAM Identity Centerプロファイルを使う場合は先にログインします。

```text
aws sso login --profile <profile-name>
```

リポジトリ最上位から、使用するAWSプロファイルとリージョンを設定してください。モデルIDは既定で`amazon.nova-lite-v1:0`ですが、対象リージョンとアカウントで使えるモデルを確認し、必要なら`BEDROCK_MODEL_ID`で変更します。モデルIDを固定条件として扱わないでください。

Windows PowerShell:

```powershell
$env:AWS_PROFILE = "<profile-name>"
$env:AWS_DEFAULT_REGION = "ap-northeast-1"
$env:BEDROCK_MODEL_ID = "<available-model-id>" # 任意。省略するとコードの既定値を使います
cd sections/s08
uv sync
```

macOS / Linux:

```sh
export AWS_PROFILE="<profile-name>"
export AWS_DEFAULT_REGION="ap-northeast-1"
export BEDROCK_MODEL_ID="<available-model-id>" # 任意。省略するとコードの既定値を使います
cd sections/s08
uv sync
```

## L03: 同じ事例でプロンプト変更前後を比べる

```text
uv run python s08_l03.py
```

`sample/incident-note.txt`は教材用の架空データです。スクリプトは同じ本文を2回送り、プロンプトだけを変えます。変更前は短い要約を依頼し、変更後は確認できる事実と未確認事項の区別、時刻の提示、原文にない断定を避けるよう依頼します。各呼び出しは最大160 output tokensです。

出力をメモと照合し、少なくとも次を記録してください。

- 原文で裏付けられる記述と、その時刻
- 原文にない原因や影響範囲の断定がないか
- 変更を採用・修正・保留する判断と、その根拠

表現や事実の正しさはモデル、実行ごとに変わります。期待文面との一致を合格条件にせず、原文と実際の出力から判断します。

## L04: 応答時間・利用量・会話履歴を見る

履歴を直近2往復まで含めて起動します。

```text
uv run python s08_l04.py --history-turns 2
```

このプログラムはsampleの架空メモと2つの固定質問だけを使い、各実行でちょうど2回呼び出します。1つ目は「障害メモでは何が分かっていますか」、2つ目は「原因は特定できていますか」です。質問を入力する必要はありません。2回目の送信メッセージに先の質問と応答が含まれ、文脈を参照できることを確認します。

今度は履歴を送らずに実行します。

```text
uv run python s08_l04.py --history-turns 0
```

同じ2つの質問で実行されます。履歴なしでは2回目のメッセージに直前のやり取りが入らないことを確認します。`--history-turns 1`なら直近の1往復だけを含めます。履歴を送るほど、同じ質問でも入力token数や料金が増える場合があります。

各応答で、`usage.inputTokens` / `outputTokens` / `totalTokens`、Bedrockの`metrics.latencyMs`、クライアント側の経過時間を表示します。クライアント側の値は通信等を含む全体の計測値で、Bedrock側の応答時間と同じ指標ではありません。記録を比較するときはリージョン、モデル、入力と履歴範囲も併記してください。

## 自動テスト

テストはモック応答を使い、AWSへ接続しません。

```text
uv run python -m unittest discover -s tests -v
```

## 料金と権限

この演習はBedrock Runtimeへの推論のみを行い、AWS resourceを作成しません。L03は1回の実行につき2回、L04も1回の実行につき2回呼び出します。L04で履歴あり・なしを比べる場合は2回実行するため、計4回です。各出力の上限は160 tokensです。料金はモデル、リージョン、各リクエストの入力token数と出力token数に応じて変わります。実行前に[Amazon Bedrock料金表](https://aws.amazon.com/bedrock/pricing/)で選択したモデルとリージョンの単価を確認し、表示された`input_tokens`と`output_tokens`を記録します。単価が1,000 tokensあたりの場合は、各実行の入力token数と出力token数をそれぞれ1,000で割って単価を掛け、種類ごとの金額を合計して概算します。料金表の課金単位が異なる場合はそちらに合わせます。実行を繰り返す分も課金対象になり得ます。

L04は固定の架空データと質問だけを送ります。コードを変更して任意入力を扱う場合でも、実データ、本番情報、機密情報、個人情報、credentialを入力しないでください。

権限は対象モデルの`bedrock:InvokeModel`に限定します。Converse APIが要求する権限とrequest/response項目は[AWS Converse APIリファレンス](https://docs.aws.amazon.com/bedrock/latest/APIReference/API_runtime_Converse.html)を確認してください。モデルの利用条件やリージョン対応はアカウントごとに確認します。

## 想定と異なる場合

- 認証エラー: 使用する`AWS_PROFILE`を確かめ、必要なら`aws sso login --profile <profile-name>`を実行します。
- リージョンまたはモデルエラー: `AWS_DEFAULT_REGION`、モデルのリージョン対応、アカウント内の利用条件を確認します。
- `AccessDeniedException`: 対象モデルに対する`bedrock:InvokeModel`を管理者に確認します。
- `ThrottlingException`: 連続再試行せず、クォータと利用状況を確認してから必要な場合だけ再実行します。
- sampleが見つからない: リポジトリ最上位から`sections/s08`で実行していることを確認します。

エラー画面へ質問や応答、認証情報を出さない設計です。共有するログも秘密情報や個人情報を含まないことを確認してください。

## 後片付け

この演習はAWS resourceを作成しません。2つの質問への応答後、プログラムは終了します。仮想環境が不要になったらリポジトリ最上位へ戻り、`sections/s08/.venv`だけを削除します。

Windows PowerShell:

```powershell
cd ../..
if (Test-Path -LiteralPath .\sections\s08\.venv) { Remove-Item -LiteralPath .\sections\s08\.venv -Recurse }
Test-Path -LiteralPath .\sections\s08\.venv
```

最後に`False`と表示されれば削除済みです。

macOS / Linux:

```sh
cd ../..
if [ -d sections/s08/.venv ]; then rm -r -- sections/s08/.venv; fi
test ! -e sections/s08/.venv && echo "s08の仮想環境を削除しました"
```

必要なら現在のターミナルから`AWS_PROFILE`、`AWS_DEFAULT_REGION`、`BEDROCK_MODEL_ID`だけを解除します。AWS CLIプロファイルや認証情報は削除しません。

## 参考資料

- [Amazon Bedrock Converse API](https://docs.aws.amazon.com/bedrock/latest/userguide/conversation-inference.html)
- [Converse API response structure](https://docs.aws.amazon.com/bedrock/latest/APIReference/API_runtime_Converse.html)
- [Amazon Bedrock料金表](https://aws.amazon.com/bedrock/pricing/)
- [Boto3 Bedrock Runtime client](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/bedrock-runtime.html)
