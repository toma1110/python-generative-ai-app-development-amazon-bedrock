# 要約を引き継ぎ用ファイルへ保存する

この演習では、架空の障害調査メモをUTF-8のテキストファイルから読み、Amazon Bedrock Converse APIで短く要約します。要約は調査結果の代わりにはなりません。実行後に必ず原文と照合し、記載された事実と不明な項目を確認します。

## 準備

- Python 3.11以降
- `uv`
- AWS CLI v2で設定したAWSプロファイルと有効なログインセッション
- Amazon Bedrockで利用できるモデル（初期値: `amazon.nova-lite-v1:0`）
- 対象モデルへの`bedrock:InvokeModel`権限

AWS認証情報をコードや`.env`ファイルへコピーしません。IAM Identity Centerを利用する場合、先にAWS CLIでログインします。

```text
aws sso login --profile <profile-name>
```

リポジトリの最上位フォルダーからSection 07へ移動し、プロファイルとリージョンを設定します。モデルが対象リージョンで利用できることも確認してください。

Windows PowerShell:

```powershell
$env:AWS_PROFILE = "<profile-name>"
$env:AWS_DEFAULT_REGION = "ap-northeast-1"
cd sections/s07
uv sync
```

macOS / Linux:

```sh
export AWS_PROFILE="<profile-name>"
export AWS_DEFAULT_REGION="ap-northeast-1"
cd sections/s07
uv sync
```

`uv sync`はこのSection専用の仮想環境へboto3を準備します。boto3は標準のAWS認証情報プロバイダーを使います。必要なら`BEDROCK_MODEL_ID`環境変数または`--model-id`で、利用可能な別モデルIDを指定できます。

## L02: ファイルを読み、要約を画面へ表示する流れを追う

まず、サンプルの調査メモを要約して画面に表示します。

```text
uv run python s07_l02.py --file data/investigation-notes.txt
```

このコマンドは `sections/s07` を現在のフォルダーとして実行します。そのため `data/investigation-notes.txt` は、今いる場所を基準にした相対パスです。`--file`で別の相対パスを指定するときも、Section 07のフォルダーからたどれる場所を書きます。

コードでは、値が次の順に流れます。

1. `s07_l02.py` の `main` が `args.file` を `read_text_file` に渡します。
2. `s07_app.py` の `read_text_file` がそのパスをUTF-8で読み、`validate_input` が前後の空白を除きます。空の文字列や12,000文字を超える入力は例外になり、ここで処理が止まります。
3. 読み込み関数が返した文字列を、`main` が `summarize_text` の `text` 引数へ渡します。
4. `summarize_text` は入力をもう一度確認し、system指示と文字列を含むuserメッセージを作って `client.converse` を呼びます。
5. `summarize_text` は応答dictの `stopReason` も確認します。`end_turn` なら最初の `text` blockを返し、`main` が画面へ表示します。`max_tokens` なら途中までの文を完成した要約として返さず、上限で終了した案内を表示します。通常完了でもtext blockがなければ、要約テキストがないことを表示します。

### 要約を引き継ぎ用Markdownへ保存する

画面の要約を別の担当者へ渡すときは、コピーして文書へ貼り直す代わりに `--output` を指定します。次の例は `sections/s07` から実行し、`report.md` を同じフォルダーへ作成します。

```text
uv run python s07_l02.py --file data/investigation-notes.txt --output report.md
```

保存先は現在の作業フォルダーを基準にします。保存先の親フォルダーは事前に作成してください。成功すると入力ファイル名と要約を含むUTF-8 Markdownが作られ、保存場所が表示されます。`report.md`を開き、ファイル名と要約があることを確認してください。要約は原文と照合して利用します。

`--output`を省いた実行は、従来どおり要約を画面へ表示し、レポートファイルを作りません。指定した保存先が既にある場合は別の名前を選び、親フォルダーがない場合はそのフォルダーを作成するか保存先を変更してください。どちらもBedrockを呼び出す前に案内して終了します。既存ファイルを上書きしたり、フォルダーを自動作成したりしません。書き込みエラーが起きた場合は保存先のパス、空き容量、書き込み権限を確認してください。書き込み途中で失敗すると不完全なfileが残る場合があります。内容を確認し、この実行で作られたものと確認できた場合に限って個別に削除してください。再試行には別の未使用file名を指定します。どの失敗も成功とは表示せず、終了コードは0以外です。Bedrockの処理が失敗した場合、レポートは作成されません。

同じ入力ファイルを保存先にも指定しないでください。入力を読み込んだ後、内容を壊さないよう保存先の検査と排他的な新規作成を行います。

API呼び出しが成功して応答が返ったことと、回答が通常完了したことは別です。`stopReason`を確認するのは、途中までの文章を完成した要約として使わないためです。この演習では自動再試行や出力上限の自動変更はしません。

system指示は日本語で100字程度の要約を求め、応答の最大長は512 tokensです。入力ファイルは12,000文字までです。別のファイルを使う場合も、Bedrockにはファイルの内容全体が送信されます。**この演習では公開済みの架空サンプルだけを使ってください。実データ、個人情報、認証情報、機密情報や業務データを含むファイルは指定しないでください。**

出力が表示された場合もファイルへ保存した場合も、`data/investigation-notes.txt`を開き、要約の各文が原文のどこにあるか確認します。とくに、原因、影響範囲、復旧状況を原文以上に断定していないかを確認してください。モデルの文章は実行ごとに異なります。原文にない内容があれば、そのまま結論として使わず、原文を根拠に判断します。

## L04: 保存の仕様と編集するコードを決める

画面に表示された要約を引き継ぐには、ファイルへ保存できる必要があります。実装前に、保存先・保存内容・保存を指定しない場合・失敗時の扱いを決めます。

このSectionの受入条件は次のとおりです。

- `--output report.md` を指定すると、入力ファイル名と要約をUTF-8 Markdownへ保存する
- `--output`を省くと、今までどおり画面へ表示し、ファイルを作らない
- 既にある保存先、ない親フォルダー、入力ファイルと同じ保存先、書き込み失敗では非0で終了し、成功したと案内しない
- 既存ファイルを上書きせず、親フォルダーを自動作成しない

実装箇所は `s07_l02.py` の `--output` 引数と処理分岐、`s07_app.py` の保存先確認とMarkdown保存関数、`tests/test_s07.py` の正常系・失敗系テストです。ここでは受入条件と編集箇所を決め、実際の変更とテストはL05で行います。

## L05: 保存機能を実装し、テストで確かめる

この演習では、画面に表示していた要約を引き継ぎ用Markdownへ保存できるようにします。開始用コードは外部repositoryのbaseline commit `3fdba894161c95f90ee85d3ec0efd816cdc73594` にある次の3ファイルです。既に用意している作業用リポジトリへ同じpathで保存し、ほかのSectionや設定fileを置き換えないでください。

- [開始用 s07_l02.py（baseline 3fdba89）](https://raw.githubusercontent.com/toma1110/python-generative-ai-app-development-amazon-bedrock/3fdba894161c95f90ee85d3ec0efd816cdc73594/sections/s07/s07_l02.py)
- [開始用 s07_app.py（baseline 3fdba89）](https://raw.githubusercontent.com/toma1110/python-generative-ai-app-development-amazon-bedrock/3fdba894161c95f90ee85d3ec0efd816cdc73594/sections/s07/s07_app.py)
- [開始用 tests/test_s07.py（baseline 3fdba89）](https://raw.githubusercontent.com/toma1110/python-generative-ai-app-development-amazon-bedrock/3fdba894161c95f90ee85d3ec0efd816cdc73594/sections/s07/tests/test_s07.py)

まず `s07_l02.py` に任意の `--output` を追加します。保存先が既にある、親フォルダーがない、入力ファイルと同じ場所を指定した場合はBedrockを呼び出す前に終了します。`s07_app.py` には保存先確認と、入力ファイルのbasename・要約・原文との照合案内をUTF-8 Markdownへ書く `save_summary` を用意します。排他的な新規作成で既存fileを上書きしません。要約の取得に成功した後で保存し、`--output`を省いたときは従来どおり画面へ表示します。APIや書き込みが失敗した場合は非0で終了し、保存成功を案内しません。

テストは `FakeClient` を使い、Bedrockへ接続しません。保存した本文の文字コードと構成、画面表示の従来動作、既存保存先・入力との衝突・親フォルダーなしではclientを作らないこと、API失敗時にfileを作らないこと、書き込み失敗を成功扱いしないことを確かめます。書き込み途中の失敗で部分fileが残るケースも確認します。追加した9テストと、既存18テストを実行します。

`sections/s07` から次を実行してください。

```text
uv run python -m unittest discover -s tests -v
```

27件すべてが成功したら、L02の保存コマンドを実行して `report.md` を開き、入力ファイル名と今回の要約があることを確認します。FakeClientやunit testが確かめるのは保存処理やコードの動作です。固定応答を保存できても、要約が原文に忠実だとは分かりません。実際の要約を利用する場合は、原文と照合して事実と不明な項目を確認します。出力の内容評価と改善はS08で扱います。

### FakeClientとテストで確かめる範囲

スタブはテスト時に外部サービスの代わりとなり、決められた応答を返します。このSectionの `FakeClient` はその実装名です。新しい9テストは、UTF-8 Markdownへの保存、既定の画面表示、既存保存先・入力との衝突・親フォルダーなしでの事前終了、API失敗時に保存しないこと、書き込み失敗時の非0終了と成功案内の抑止、部分fileが残ることを確認します。既存の18テストはファイル読み込み・入力条件、Converseへ渡す内容、応答テキストと終了理由を確認します。

通常のunit testが確かめるのは戻り値、例外、CLIの終了結果など、コードに書かれた動作です。FakeClientの固定応答を保存できても、その文章が原文に忠実だとは分かりません。要約の各文を原文と照合し、事実と不明な項目を見分ける内容評価はS08で扱います。参考例として「DB接続待ちが発生した」という原文を要約が「原因はDBだった」と断定するケースを考えられますが、これは説明用であり、実行で観測した出力ではありません。
## 料金と権限

L02の有効な実行では、Bedrock Runtimeへ1回リクエストします。課金はモデル、リージョン、入力・出力tokensなどで変わります。短い教材用ファイルを使い、実行前に[Amazon Bedrock料金表](https://aws.amazon.com/bedrock/pricing/)で対象モデルとリージョンの料金を確認してください。出力tokensには上限を設定していますが、実際の料金は利用状況によって異なります。

L04の仕様確認と、L05のunit testはローカルで動き、AWSへ接続しません。L02で実際に要約する場合はBedrock Runtimeへ接続しますが、`--output`は同じ要約結果を保存するだけで追加のAPI呼び出しをしません。このSectionはAWS resourceを作りません。権限は対象モデルへの`bedrock:InvokeModel`に限定し、利用モデルとリージョンは自分のAWS環境で利用可能なものを選びます。

## 後片付け

このSectionはAWS resourceやクラウド上のファイルを作成しません。L02で自分が作成した `sections/s07/report.md` を削除する場合は、そのfileが今回の演習で作ったものだと確認してから、Section 07のディレクトリーで次を実行します。指定したfileだけを削除します。保存先に別の名前を使った場合は、その自分が作成したfileを確認して個別に削除してください。

Windows PowerShell:

```powershell
if (Test-Path -LiteralPath .\report.md) { Remove-Item -LiteralPath .\report.md }
Test-Path -LiteralPath .\report.md
```

`False`なら `report.md` はありません。続けて仮想環境を削除する場合は、Section 07のディレクトリーからリポジトリ最上位へ戻り、`.venv`だけを削除します。

Windows PowerShell:

```powershell
cd ../..
if (Test-Path -LiteralPath .\sections\s07\.venv) { Remove-Item -LiteralPath .\sections\s07\.venv -Recurse }
Test-Path -LiteralPath .\sections\s07\.venv
```

結果が`False`なら削除できています。

macOS / Linux:

```sh
if [ -f report.md ]; then rm -- report.md; fi
test ! -e report.md && echo "report.mdはありません"
```

続けて仮想環境を削除する場合は、Section 07のディレクトリーからリポジトリ最上位へ戻ります。

```sh
cd ../..
if [ -d sections/s07/.venv ]; then rm -r -- sections/s07/.venv; fi
test ! -e sections/s07/.venv && echo "s07の仮想環境を削除しました"
```

必要なら`AWS_PROFILE`、`AWS_DEFAULT_REGION`、`BEDROCK_MODEL_ID`を現在のターミナルから解除します。AWS CLIのプロファイルや認証情報は削除しません。

## 参考資料

- [Amazon Bedrock Converse APIのPython演習](https://docs.aws.amazon.com/bedrock/latest/userguide/getting-started-api-ex-python.html)
- [Converse APIのリクエストとinferenceConfig](https://docs.aws.amazon.com/bedrock/latest/userguide/conversation-inference.html)
- [Amazon Bedrock料金表](https://aws.amazon.com/bedrock/pricing/)
