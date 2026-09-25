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

プログラムはファイルをUTF-8で読み、空白だけの入力を拒否してからConverse APIを1回呼びます。応答の最大長は256 tokens、入力ファイルは12,000文字までです。別のファイルを使う場合も、Bedrockにはファイルの内容全体が送信されます。**この演習では公開済みの架空サンプルだけを使ってください。実データ、個人情報、認証情報、機密情報や業務データを含むファイルは指定しないでください。**

出力が表示されたら、`data/investigation-notes.txt`を開き、要約の各文が原文のどこにあるか確認します。とくに、原因、影響範囲、復旧状況を原文以上に断定していないかを確認してください。モデルの文章は実行ごとに異なります。原文にない内容があれば、そのまま結論として使わず、原文を根拠に判断します。

## L04: 入力不足とファイルエラーを区別する

一意な一時ディレクトリの中に、まだ存在しないファイル名を作って指定します。これにより、同名の既存ファイルを誤って使いません。

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

空のファイルでは内容が空という案内になります。文字コードがUTF-8でない場合、フォルダーを指定した場合、読み取り権限がない場合も、それぞれ利用者が次に確認する内容を表示します。例外tracebackやファイル内容は表示しません。引数`--file`を付け忘れたときは、argparseが使い方を案内します。

## L05: APIを呼ばずにファイル処理をテストする

Section 07のテストは一時ファイルとモック応答を使うため、AWS認証情報なしで実行できます。

```text
uv run python -m unittest discover -s tests -v
```

テストではUTF-8ファイルの読み込み、空入力、存在しないファイル、文字コードの誤り、Converseへ渡す入力と出力上限を確認します。ファイル処理だけのテストはAWSクライアントを作りません。Converseの形を確認するテストも、応答を返すモックを使いAWSへ接続しません。

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
