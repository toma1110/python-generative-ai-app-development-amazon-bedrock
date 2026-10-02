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

`sample/incident-note.txt`は教材用の架空データです。比較する前に、`s08_l03.py`の`BASELINE_PROMPT`と`REVISED_PROMPT`を見比べてください。コードはどちらにも同じメモを付けてuserメッセージを作り、順にBedrockへ1回ずつ送ります。

この比較で変えるのはuserメッセージ内の依頼文だけです。架空メモ、systemメッセージ、モデルID、リージョン、出力上限（160 tokens）は固定します。モデルIDとリージョンは準備時に選んだ値を両方の呼び出しで使います。モデルやリージョンまで同時に変えると、出力差がどの変更によるものか判断しにくくなります。

コードの流れは、`build_user_text`で依頼文とメモをつなぐ → `message`でBedrock用のuserメッセージにする → `compare`から`converse`を2回呼ぶ → 応答本文と応答の`usage` / `metrics.latencyMs`を取り出して表示する、です。利用量はBedrock応答の値で、各呼び出しの入力・出力・合計tokensを表します。`latencyMs`もBedrock応答に含まれるサービス側の時間です。ここではクライアント全体の経過時間は測っていません。

二つの出力を実際に読み、原文で裏付けられる事実・時刻、欠けた情報、原文にない原因や影響範囲の断定を比べます。指示どおりの文面になったかだけでは決めず、根拠が保たれ、必要な情報を落とさず、確認できないことを断定しないかを見て採用・修正・保留を選びます。usageと応答時間は出力の品質点ではなく、同じ設定でのコスト・速度の参考値として一緒に記録します。

次に、自分で`REVISED_PROMPT`の依頼文を一か所だけ変えて保存し、同じコマンドをもう一度実行してください。例えば「時刻を添えてください」を「時刻を添えて箇条書きで示してください」に変えます。架空メモ、`BASELINE_PROMPT`、systemメッセージ、モデル、リージョン、出力上限は変えず、編集前後の出力とusage・応答時間を記録して比べます。出力は実行ごとにも変わるため、一度の結果だけでプロンプト変更が品質を改善したと断定せず、どの差が原文で確かめられたかを説明してください。

出力をメモと照合し、少なくとも次を記録してください。

- 原文で裏付けられる記述と、その時刻
- 原文にない原因や影響範囲の断定がないか
- 変更を採用・修正・保留する判断と、その根拠

表現や事実の正しさはモデル、実行ごとに変わります。期待文面との一致を合格条件にせず、原文と実際の出力から判断します。

## L04: 応答時間・利用量・会話履歴を見る

まず`--history-turns 2`を指定して実行します。ここで変える条件は次の呼び出しへ渡す会話履歴の上限です。`s08_l04.py`では架空メモ、2つの質問、systemメッセージ、モデルID、リージョン、出力上限を同じにして、別々の実行で`--history-turns 0`と`--history-turns 2`を比べます。二つのコマンドの間でモデルIDやリージョンを変えないでください。

```text
uv run python s08_l04.py --history-turns 2
```

このプログラムはsampleの架空メモと2つの固定質問だけを使い、各実行でちょうど2回呼び出します。1つ目は「障害メモでは何が分かっていますか」、2つ目は「原因は特定できていますか」です。質問を入力する必要はありません。各質問のuserメッセージにはメモも含まれます。質問1の応答後、コードは質問1のuserメッセージとassistant応答を`history`へ追加し、質問2の直前に`keep_recent_turns`で指定上限の履歴を取り出します。このため固定2問の実行で質問2へ実際に渡る過去の会話は最大1往復です。`2`は将来の質問にも適用する上限であり、今回2往復分の過去履歴があるという意味ではありません。

この2問目はメモをもう一度含み、「原因は特定できていますか」と単独で尋ねます。履歴なしでも同じメモから答えられるため、この演習は履歴が回答内容を改善するかを検証しません。履歴あり・なしの実行では、質問2へ送られるメッセージと入力token数などがどう変わるかを観察してください。回答が同じでも異なっても、履歴の有効性や回答品質の差だとは結論づけず、答えの正しさはメモと照合します。

`run_turn`は送信するメッセージを組み立てた後、`time.perf_counter()`で`converse`の前後を計り、クライアント側経過時間を出します。応答から本文・token利用量・Bedrock側`metrics.latencyMs`を取り出します。Bedrock側時間とクライアント側時間は計測範囲が違うため、同じ値として扱わないでください。

今度は履歴を送らずに実行します。

```text
uv run python s08_l04.py --history-turns 0
```

同じ2つの質問で実行されます。履歴なしでは2回目のリクエストに直前の質問と応答が入らないことを確認します。`--history-turns 1`なら直近の1往復だけを含めます。履歴を送るほど、同じ質問でも入力token数や料金が増える場合があります。

各応答で、`usage.inputTokens` / `outputTokens` / `totalTokens`、Bedrockの`metrics.latencyMs`、クライアント側の経過時間を表示します。`usage`とBedrock側時間はAPI応答の項目、クライアント側時間はPythonがAPI呼び出しの前後で測った値です。クライアント側には通信等も含まれるため、Bedrock側の時間と同じ指標ではありません。二つの設定で結果を記録し、主に質問2の入力token数と計測時間を比較します。出力の正しさは架空メモと照合しますが、この固定例だけで履歴が回答を改善した、または速度・利用量の差に見合うと判定することはできません。記録にはリージョン、モデル、質問番号、履歴上限を併記します。

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
- 応答にtoken数や時間が`不明`と表示された: 実行自体は続けられますが、その応答の利用量・時間は比較できません。記録では不明とし、AWSへの接続・応答内容を確認してから必要な場合だけ再実行します。
- `Bedrock APIエラーコード`が表示された: コードとRequest IDだけを記録し、表示された案内に沿ってリージョン、モデル利用可否、IAM権限、クォータを確認します。スクリプトは応答本文や認証情報をエラー表示しません。

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
