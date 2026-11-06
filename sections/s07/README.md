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

空のファイルでは内容が空という案内になります。文字コードがUTF-8でない場合、フォルダーを指定した場合、読み取り権限がない場合も、それぞれ利用者が次に確認する内容を表示します。ファイルを読めた後、本文が空白だけなら内容が空という案内になります。これはファイルの読み込みエラーではなく、読み込み後に本文を確かめる処理の結果です。例外tracebackやファイル内容は表示しません。引数`--file`を付け忘れたときは、argparseが使い方を案内します。

## L05: 入力条件を変更し、テストで確かめる

この演習では、利用者に必要な本文まで短さだけで拒否しないよう、任意の最小文字数条件を取り除きます。空白を除いて1文字以上なら入力として受け付け、空または空白だけは `EmptyInputError`、12,000文字を超える本文は `InputTooLongError` にします。12,000文字はこのアプリが長大な入力を避けるために設けた上限です。AWSやモデルの上限を示す値ではなく、利用料金の上限を保証するものでもありません。

アプリ全体では、`s07_l02.py` がファイルを読み、`s07_app.py` の `validate_input` が前後の空白を除いて入力を確かめ、`summarize_text` がBedrockへ渡します。`validate_input` が数えるのは前後の空白を除いた後のPython文字列の文字数です。たとえば `"  x  "` は1文字として扱い、返り値も `"x"` です。空白だけなら空入力として扱います。

### 演習の開始用コード

開始用コードは、同じGit commit `a98160ae1889986893cf3da1a22d4019f50b0ff7` にある次の3ファイルです。既に用意している作業用リポジトリへ、この3ファイルだけを同じpathに保存し、ほかのSectionや設定fileは置き換えずに演習します。開始用コードでは最小20文字の条件があり、1文字の本文を渡すと `InputTooShortError` で拒否されます。

- [開始用 s07_app.py（commit a98160a）](https://raw.githubusercontent.com/toma1110/python-generative-ai-app-development-amazon-bedrock/a98160ae1889986893cf3da1a22d4019f50b0ff7/sections/s07/s07_app.py)
- [開始用 tests/test_s07.py（commit a98160a）](https://raw.githubusercontent.com/toma1110/python-generative-ai-app-development-amazon-bedrock/a98160ae1889986893cf3da1a22d4019f50b0ff7/sections/s07/tests/test_s07.py)
- [開始用 s07_l04.py（commit a98160a）](https://raw.githubusercontent.com/toma1110/python-generative-ai-app-development-amazon-bedrock/a98160ae1889986893cf3da1a22d4019f50b0ff7/sections/s07/s07_l04.py)

完成例は、このREADMEと同じ現在のSection 07にある3ファイルです。演習では別の解答用ファイルを作らず、固定した開始用コードからアプリ、テスト、CLIの入力案内を一緒に更新します。テストコマンドは `sections/s07` ディレクトリーを現在の場所として実行します。

`FileInputTests` は `unittest.TestCase` を継承して作ったテスト用のクラスです。`TestCase` が `assertEqual` や `assertRaises` などの確認用メソッドを用意するため、各テストの期待値と実際の結果を比べられます。各 `test_` メソッドの `self` は、そのテストを実行している `FileInputTests` のオブジェクトを指します。

固定した開始用3ファイルを次のように更新します。`s07_app.py` では `MIN_INPUT_CHARACTERS`、`InputTooShortError` class、短い入力を拒否する分岐を削除します。`tests/test_s07.py` では `InputTooShortError` のimport、最小文字数の期待値、短い入力の拒否テストを削除し、前後の空白を除いた1文字を受け付けるテストを追加します。さらに上限の直前・上限ちょうど・上限超過の期待値を置きます。テスト側は実装定数を読み取らず、仕様上の境界を独立して持ちます。`s07_l04.py` では同じclassのimportと `except InputTooShortError` 節を削除し、argparseの説明を「入力条件とファイル読み込み失敗」に更新します。これら3ファイルを同時に変更することで、CLIのimportを壊さず、最小文字数がなくなった後の受け入れ結果を確認できます。

`sections/s07` から個別に次を実行し、短い入力と上限境界を確かめます。

```text
uv run python -m unittest tests.test_s07.FileInputTests.test_accepts_one_character_after_trimming -v
uv run python -m unittest tests.test_s07.FileInputTests.test_accepts_input_below_the_maximum_length -v
uv run python -m unittest tests.test_s07.FileInputTests.test_accepts_input_at_the_maximum_length -v
uv run python -m unittest tests.test_s07.FileInputTests.test_rejects_input_above_the_exercise_limit -v
uv run python -m unittest discover -s tests -v
```

期待する結果は、前後の空白を除いた1文字、11,999文字、12,000文字が受理され、12,001文字が拒否されることです。空白だけの入力は別の `EmptyInputError` となります。変更した条件と、正常・異常の境界テストがそれぞれ何を確かめるか対応づけてください。テストが失敗した場合は、表示された期待値と実際の値を比べ、実装または期待値のどちらに変更漏れがあるか調べます。

このユニットテストで確認するのは、ローカルのファイル読み込み、入力検査、アプリがモデルclientへ渡すリクエストと応答の受け渡しです。通常のプログラムテストは関数の戻り値、例外、CLIの終了結果など、コードに書かれた動作を確かめます。要約内容が原文に忠実か、変更で品質が改善したかは確かめません。品質は原文と出力を照合して人が評価します。指示や出力形式などを変更した効果を評価する場合は、同じ評価用入力で変更前後を比べ、問題が減ったか、別の問題が生じなかったかを見て、採用・追加修正・保留を判断します。一度よい出力が出ても品質が保証されたとは扱いません。たとえば「DB接続待ちが発生した」という原文を、要約が「障害の原因はDBだった」と断定するケースは説明用の例です。実際に観測したモデル出力ではありません。S08では出力の問題を見つけ、変更し、同じ事例で比べて判断する流れを扱います。

ファイル読み込みテストは一時ファイルを作ってパスを `read_text_file` へ渡し、戻り値や例外を確認します。ファイルがない、空白だけ、UTF-8で読めない場合は、ファイル読み込みと入力確認の結果を区別します。`read_text_file` はローカルファイルだけを扱い、Bedrock clientを受け取りません。

スタブとは、テスト時に外部サービスの代わりとなり、決められた応答を返すものです。このSectionの `FakeClient` は、その役割を持つ具体的な実装名です。本物のBedrockへ毎回接続せず、アプリのリクエストと応答処理を同じ条件で繰り返し確かめられます。FakeClientは受け取った引数を記録し、テストは入力本文、モデルID、system/userメッセージ、`maxTokens`、応答からのテキスト取り出しを確認します。指定した固定応答に応じた処理も確認します。現行テストはAWS接続・認証・サービスの実挙動やモデルの要約品質を確かめていません。未実装の異常応答ケースをテスト済みとは扱いません。本物のAWS接続はL02の実行で確かめ、要約の各文は原文と照合します。

テストを実行します。

```text
uv run python -m unittest discover -s tests -v
```

テストではUTF-8ファイル、空入力、存在しないファイル、文字コードの誤り、上限の境界、Converseへ渡す入力と出力上限、応答からテキストを取り出す処理、終了理由を確認します。ファイル処理だけのテストはAWSクライアントを作りません。Converseの形を確かめるテストはFakeClientを使うためAWSへ接続しません。

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
