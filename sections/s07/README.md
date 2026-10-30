# Section 07: ローカルファイルを読む要約アプリ

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

## L02: ファイルを読んで要約する

サンプルの調査メモを要約します。

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

API呼び出しが成功して応答が返ったことと、回答が通常完了したことは別です。`stopReason`を確認するのは、途中までの文章を完成した要約として使わないためです。この演習では自動再試行や出力上限の自動変更はしません。

system指示は日本語で100字程度の要約を求め、応答の最大長は512 tokensです。入力ファイルは12,000文字までです。別のファイルを使う場合も、Bedrockにはファイルの内容全体が送信されます。**この演習では公開済みの架空サンプルだけを使ってください。実データ、個人情報、認証情報、機密情報や業務データを含むファイルは指定しないでください。**

出力が表示されたら、`data/investigation-notes.txt`を開き、要約の各文が原文のどこにあるか確認します。とくに、原因、影響範囲、復旧状況を原文以上に断定していないかを確認してください。モデルの文章は実行ごとに異なります。原文にない内容があれば、そのまま結論として使わず、原文を根拠に判断します。

## L04: 入力不足とファイルエラーを区別する

一意な一時ディレクトリの中に、まだ存在しないファイル名を作って指定します。これにより、同名の既存ファイルを誤って使いません。

Windows PowerShell:

```powershell
$missingDir = Join-Path ([System.IO.Path]::GetTempPath()) ([guid]::NewGuid().ToString())
New-Item -ItemType Directory -Path $missingDir | Out-Null
$missingFile = Join-Path $missingDir "not-found.txt"
try {
    uv run python s07_l04.py --file $missingFile
} finally {
    Remove-Item -LiteralPath $missingDir -Recurse -Force
}
```

この例はファイルを作らず、GUIDで作った専用ディレクトリだけを削除します。

macOS / Linux:

```sh
(
  missing_dir=$(mktemp -d)
  trap 'rmdir -- "$missing_dir"' EXIT
  uv run python s07_l04.py --file "$missing_dir/not-found.txt"
)
```

ファイルがないという案内が表示されます。次に、システムが一意な一時ファイルを作り、そのファイルだけを使って内容不足を確認します。既存ファイルは変更しません。

Windows PowerShell:

```powershell
$emptyFile = New-TemporaryFile
try {
    uv run python s07_l04.py --file $emptyFile.FullName
} finally {
    Remove-Item -LiteralPath $emptyFile.FullName
}
```

macOS / Linux:

```sh
(
  temp_dir=$(mktemp -d)
  trap 'rm -f -- "$temp_dir/empty.txt"; rmdir -- "$temp_dir"' EXIT
  : > "$temp_dir/empty.txt"
  uv run python s07_l04.py --file "$temp_dir/empty.txt"
)
```

空のファイルでは内容が空という案内になります。文字コードがUTF-8でない場合、フォルダーを指定した場合、読み取り権限がない場合も、それぞれ利用者が次に確認する内容を表示します。ファイルを読めても本文が20文字未満なら、入力チェックが短すぎることを案内します。これはファイルの読み込みエラーではなく、読み込み後に本文を確かめる処理の結果です。例外tracebackやファイル内容は表示しません。引数`--file`を付け忘れたときは、argparseが使い方を案内します。

## L05: 入力条件を変更し、テストで確かめる

ここでは、短すぎるメモをBedrockへ送る前に止める動作を確かめます。確認するのは要約の品質ではなく、本文の長さを調べる入力チェックです。アプリ全体では、`s07_l02.py` がファイルを読み、`s07_app.py` の `validate_input` が本文を整え、長さを確認してから `summarize_text` がBedrockへ渡します。今回はそのうち、`validate_input` にある最小文字数の条件を変更します。

最初の配布状態では `MIN_INPUT_CHARACTERS` とテストの期待値が20で、Section 07の17件すべてが通ります。まず `sections/s07` で次のコマンドを実行し、初期状態を確かめてください。これは最初から失敗するテストを配る演習ではありません。境界テストは20文字を受け入れ、21文字も受け入れ、19文字では `InputTooShortError` になることを確認します。

```text
uv run python -m unittest discover -s tests -v
```

この課題では別の解答用ファイルを使わず、実行対象のアプリとテストを編集します。リポジトリ最上位から開くファイルは `sections/s07/s07_app.py` と `sections/s07/tests/test_s07.py` です。テストコマンドは `sections/s07` ディレクトリーを現在の場所として実行します。

短いメモだけでは要約の材料が足りないケースを避けるため、まず `sections/s07/s07_app.py` の `MIN_INPUT_CHARACTERS` を20から40へ変更します。テストの期待値はまだ20のままにして、`sections/s07` から次の2件を実行してください。どちらも20/21文字を受け入れる旧仕様のテストなので、新しい40文字条件を実装した時点では失敗します。この結果を見て、実装とテストが別々の役割を持つことを確認します。

```text
uv run python -m unittest tests.test_s07.FileInputTests.test_accepts_input_at_the_minimum_length -v
uv run python -m unittest tests.test_s07.FileInputTests.test_accepts_input_above_the_minimum_length -v
```

次に `sections/s07/tests/test_s07.py` の `EXPECTED_MINIMUM_LENGTH` を20から40へ変更します。テスト側は実装定数を読み取らず期待条件を独立して持つため、実装だけを変えた場合に旧条件を見逃しません。実装と期待仕様の両方を変更した後、次の3つの境界テストを個別に実行してからSectionの全17件を実行します。

```text
uv run python -m unittest tests.test_s07.FileInputTests.test_accepts_input_at_the_minimum_length -v
uv run python -m unittest tests.test_s07.FileInputTests.test_accepts_input_above_the_minimum_length -v
uv run python -m unittest tests.test_s07.FileInputTests.test_rejects_input_below_the_minimum_length -v
uv run python -m unittest discover -s tests -v
```

変更後は40文字と41文字の本文が受け入れられ、39文字では `InputTooShortError` になることを確認します。`test_too_short_input_does_not_call_the_model` は、短すぎる本文がBedrock呼び出し前に拒否され、clientの呼び出し回数が0回であることも確かめます。L04の `test_l04_reports_short_input_without_traceback` は、39文字のファイルをCLIへ渡したとき利用者向け案内と終了コード2が返ることを確認します。変更した条件と正常・異常のテスト結果を対応づけて説明してください。テストが失敗したら、表示された期待値と実際の値を読み、コードまたはテストのどちらに変更漏れがあるか調べます。期待値をわざと誤らせて失敗を作る作業はしません。

この長さの確認に必要なのはローカルの文字列とPythonだけです。本文をBedrockへ渡す前の条件なので、まずここを手元で繰り返し確認すれば、AWSの認証・通信やモデルの応答に左右されず、入力チェックを変更した効果が分かります。L02の実行は別の確認です。L02では実際にBedrockへ要約を依頼し、原文と応答を見比べます。このユニットテストだけではAWS接続やモデルの要約品質は確認しません。

ファイル読み込みテストは、一時ファイルを作ってパスを `read_text_file` へ渡し、戻り値や例外を確認します。ファイルがない、空白だけ、UTF-8で読めない場合は、ファイル読み込みと入力確認のそれぞれの結果をテストします。`read_text_file` はローカルファイルだけを扱い、Bedrock clientを受け取りません。

`FakeClient` を使うAPI境界のテストは、`summarize_text(client, text)` が本文・モデルID・出力上限を `client.converse` へ渡し、応答からテキストを取り出すことを確認します。FakeClientは渡された引数を記録し、決めておいた応答を返すテスト用の相手です。実際のAWS接続やモデル応答の正しさまでは確認しません。AWSへ接続して要約を得る動作はL02の実行で確かめ、要約の各文は原文と照合します。

テストを実行します。

```text
uv run python -m unittest discover -s tests -v
```

テストではUTF-8ファイルの読み込み、空入力、存在しないファイル、文字コードの誤り、Converseへ渡す入力と出力上限、応答の終了理由を確認します。ファイル処理だけのテストはAWSクライアントを作りません。Converseの形を確認するテストも、応答を返すモックを使いAWSへ接続しません。

## 料金と権限

L02の有効な実行では、Bedrock Runtimeへ1回リクエストします。課金はモデル、リージョン、入力・出力tokensなどで変わります。短い教材用ファイルを使い、実行前に[Amazon Bedrock料金表](https://aws.amazon.com/bedrock/pricing/)で対象モデルとリージョンの料金を確認してください。出力tokensには上限を設定していますが、実際の料金は利用状況によって異なります。

L04とL05はローカル処理だけでAWSへ接続しません。このSectionはAWS resourceを作りません。権限は対象モデルへの`bedrock:InvokeModel`に限定し、利用モデルとリージョンは自分のAWS環境で利用可能なものを選びます。

## 後片付け

このSectionはAWS resourceやクラウド上のファイルを作成しません。演習後に仮想環境を削除する場合は、Section 07のディレクトリーからリポジトリ最上位へ戻り、`.venv`だけを削除します。

Windows PowerShell:

```powershell
cd ../..
if (Test-Path -LiteralPath .\sections\s07\.venv) { Remove-Item -LiteralPath .\sections\s07\.venv -Recurse }
Test-Path -LiteralPath .\sections\s07\.venv
```

結果が`False`なら削除できています。

macOS / Linux:

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
