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

`uv sync`でboto3とその依存関係をこの演習の仮想環境に準備します。各Python sampleでは`boto3.Session().client("bedrock-runtime")`を呼び、Bedrock Runtimeを呼び出すためのclient objectを作ります。boto3は現在のAWS設定から認証情報を解決し、環境変数または選択したAWSプロファイルの設定からリージョンを使います。ここで設定した`AWS_PROFILE`と`AWS_DEFAULT_REGION`がその選択を助けます。プログラムは認証情報を表示しません。

## L02: userメッセージを1回送る

```text
uv run python s05_l02.py
```

固定のuserメッセージをConverse APIへ1回送り、モデルのテキスト応答を表示します。表示はたとえば、監視アラームの調査時に確認する項目の短い説明です。文章や言い回しは実行ごとに異なる場合があります。

`s05_l02.py`では、`user_message(PROMPT)`が次の形のPythonのlistとdictionaryを作ります。外側のlistには会話の一通を入れ、そのdictionaryで`role`は送信者、`content`は本文のlist、`text`は質問文を表します。

```python
[{"role": "user", "content": [{"text": PROMPT}]}]
```

この`messages`とmodel IDを`client.converse()`へ渡すと、boto3がPythonの値をConverse APIのJSONリクエストにして送信し、JSONレスポンスをPythonのdictionaryやlistにして返します。つまり、ここではJSON文字列を自分で組み立てず、Pythonのlist/dictionaryを使います。応答の形は次のようになります（構造を示す例で、`text`の内容は実行ごとに変わります）。

```json
{"output": {"message": {"content": [{"text": "（モデルが生成した応答文）"}]}}}
```

`call_once`は`client.converse()`の戻り値を返し、`main`はそれを`response`として受け取ります。`response_text(response)`は`output`→`message`→`content`の順にたどって`content` list内の最初のtext blockを取り出し、その文字列が`text`に代入されます。最後に`print(text)`がその内容を画面に表示します。メッセージを自分の質問に変えて再実行し、入力から応答表示までの値の流れを確かめます。

## L03: systemメッセージと推論パラメータを比べる

```text
uv run python s05_l03.py
```

同じ質問・model IDで次の3条件を送り、応答を並べて表示します。

1. 基準: systemメッセージなし、temperature `0.0`、topP `1.0`
2. system変更: systemメッセージだけを追加し、推論パラメータは基準と同じ
3. temperature変更: systemメッセージを使わず、temperatureだけを`0.8`へ変更し、topPは`1.0`のまま

1と2ではsystemメッセージだけが異なり、1と3ではtemperatureだけが異なります。`s05_l03.py`では各`client.converse()`の引数を名前付きで並べているので、固定するmodel IDとmessages、変更する`system`または`inferenceConfig`を見比べられます。temperatureは応答の生成方法に影響しますが、値を変えても特定の文章が必ず出るわけではありません。system文やtemperatureを一つずつ変更して再実行し、実際の応答を比べます。このLectureは比較のため3回呼び出します。

## L04: 応答、利用量、エラーを読む

```text
uv run python s05_l04.py
```

成功時の`response`は、本文を`output`→`message`→`content`→`text`から、`stopReason`は終了理由から読みます。`usage` dictionaryの`inputTokens`、`outputTokens`、`totalTokens`が入出力のtoken数、`metrics` dictionaryの`latencyMs`が応答時間の指標です。コードではそれぞれを`result`という別のdictionaryへ取り出してから表示します。利用量と応答時間は実際の応答に含まれる値で、固定値ではありません。

AWSがAPIエラーを返した場合はboto3の`ClientError`となり、コードはエラーコードと、あればRequest IDを表示します。呼び出しや通信などSDK側で失敗した場合は`BotoCoreError`として接続先などを確認する案内を表示します。どちらの失敗も終了コード`1`で終わり、成功は`0`です。IAM権限、モデル利用可否、クォータ、プロファイル、リージョン、ネットワークを確認してください。エラー本文には環境固有情報が含まれる可能性があるため、コードは全文を画面へ出しません。調査時にも認証情報や個人情報が含まれないことを確認してから共有します。

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
