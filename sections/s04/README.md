# Section 04: APIとAWS接続

このSectionでは、PythonアプリからAPIへ送る入力と応答を確認し、AWS認証情報とアプリ固有の秘密情報の違いを学びます。L04では、認証情報をコードへ書かずにAWSへ接続し、実行先のアカウントとリージョンを確かめます。

## 事前準備

- Python 3.11以降
- `uv`
- AWS CLI v2
- AWS IAM Identity Centerなどを使って設定済みのAWS CLIプロファイル
- 選んだAWSアカウントで利用できる有効なログインセッション

AWS CLIでまだプロファイルを設定していない場合は、組織のAWS管理者が案内する方法を使ってください。新しいアクセスキーを発行したり、ソースコードや`.env`ファイルに認証情報を保存したりしません。IAM Identity Centerのプロファイルを使う場合は、先にログインします。

```text
aws sso login --profile <profile-name>
```

`<profile-name>`は実際のプロファイル名に置き換えます。

## L04: 認証情報をコードへ書かずに接続先を確認する

リポジトリ最上位で、演習の依存関係を準備します。`uv sync`はこの演習の仮想環境へboto3をインストールします。

```text
cd sections/s04/l04
uv sync
```

実行するシェルでプロファイルとリージョンを選びます。これらの環境変数は、コードを変えずに使うAWS設定を選ぶためのものです。認証情報そのものを環境変数へコピーする必要はありません。

Windows PowerShell:

```powershell
$env:AWS_PROFILE = "<profile-name>"
$env:AWS_DEFAULT_REGION = "ap-northeast-1"
uv run python main.py
```

macOS / Linux:

```sh
export AWS_PROFILE="<profile-name>"
export AWS_DEFAULT_REGION="ap-northeast-1"
uv run python main.py
```

プロファイル名とリージョンは、自分が使うものに置き換えてください。`AWS_PROFILE`はAWS CLIとboto3が参照する名前付きプロファイルを選びます。`AWS_DEFAULT_REGION`はこのシェルで使うリージョンを指定します。リージョンを環境変数で指定しない場合、boto3は選択したプロファイルの共有AWS設定からリージョンを読み取ります。

プログラムはSTSの`GetCallerIdentity`を呼び、応答に含まれるAWS Account IDと、boto3セッションが選んだリージョンを表示します。Account IDが自分の想定したAWSアカウントと一致すること、リージョンが演習で使う予定のものと一致することを確認してください。ARNや認証情報は表示しません。違うアカウントが表示された場合は、そのまま次の演習へ進まず、プロファイルやシェルの設定を確認します。

このコードはboto3の認証情報プロバイダーを使います。認証情報は、IAM Identity Centerのログインセッション、共有AWS設定、実行環境に割り当てられたIAMロールなど、AWSがサポートする設定元から解決されます。AWS認証情報は「誰としてAWSへ接続するか」を示し、IAM権限は「そのIDで何を実行できるか」を制御します。アプリ固有の外部サービス用パスワードやAPIトークンは別の秘密情報です。必要なアプリではSecrets Managerなどへ保存し、AWSの認証情報でその値を取得する権限を管理します。この演習では秘密情報を作成・取得しません。

## 期待する結果

成功すると、次のような2行が表示されます。Account IDは実行したAWSアカウントごとに異なります。

```text
接続先アカウント: <12桁のAWS Account ID>
接続先リージョン: ap-northeast-1
```

この確認はAWSの読み取り専用APIを1回呼び出します。`GetCallerIdentity`にはIAM権限の追加が不要です。AWS resourceを作成・変更せず、Bedrockのモデルも呼び出しません。

## 想定と異なる場合

- 認証情報が見つからない、またはSSOセッションの期限切れ: 正しいプロファイルを指定し、必要なら`aws sso login --profile <profile-name>`を実行してから再実行します。
- 想定と違うアカウントが表示される: `AWS_PROFILE`が選んだプロファイル名と、プロファイルを設定したAWSアカウントを確認します。表示された値を確認するまで次へ進みません。
- プロファイルを指定したのに別の認証情報が使われる: `AWS_ACCESS_KEY_ID`、`AWS_SECRET_ACCESS_KEY`、`AWS_SESSION_TOKEN`の環境変数が設定されていると、プロファイルより優先される場合があります。値を表示せず、設定されている変数名だけを確認します。

  Windows PowerShell:

  ```powershell
  Get-ChildItem Env: | Where-Object Name -In @("AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY", "AWS_SESSION_TOKEN") | Select-Object -ExpandProperty Name
  ```

  macOS / Linux:

  ```sh
  for name in AWS_ACCESS_KEY_ID AWS_SECRET_ACCESS_KEY AWS_SESSION_TOKEN; do
    if printenv "$name" > /dev/null; then printf '%s is set\n' "$name"; fi
  done
  ```

  指定プロファイルを使う場合は、このターミナル内だけで意図しない環境変数を解除してから再実行します。値を表示したり、共有したりしないでください。

  ```powershell
  Remove-Item Env:AWS_ACCESS_KEY_ID, Env:AWS_SECRET_ACCESS_KEY, Env:AWS_SESSION_TOKEN -ErrorAction SilentlyContinue
  ```

  ```sh
  unset AWS_ACCESS_KEY_ID AWS_SECRET_ACCESS_KEY AWS_SESSION_TOKEN
  ```
- リージョンが空、または想定と違う: シェルの`AWS_DEFAULT_REGION`と、プロファイルのリージョン設定を確認します。環境変数に設定がある場合はそちらを直します。
- 接続エラー: ネットワークとAWS CLIのログイン状態を確認して再実行します。エラー詳細に個人のプロファイル名などが含まれる場合があるため、公開場所へそのまま貼り付けないでください。
- `uv`が見つからない、または依存関係の取得に失敗する: `uv --version`とインターネット接続を確認します。AWS接続に進む前に`uv sync`を完了してください。

## 料金と後片付け

この演習はSTSの`GetCallerIdentity`だけを実行し、AWS resourceやSecrets Managerのsecretを作りません。Bedrockやその他の従量課金APIも呼ばないため、この演習によるAWSサービス利用料金は発生しません。`uv sync`はboto3などのPythonパッケージをダウンロードします。

演習後は、実行中のプログラムを終了します。PowerShellでは次のコマンドで、このターミナルに設定したプロファイルとリージョンを解除できます。

```powershell
Remove-Item Env:AWS_PROFILE -ErrorAction SilentlyContinue
Remove-Item Env:AWS_DEFAULT_REGION -ErrorAction SilentlyContinue
```

macOS / Linux:

```sh
unset AWS_PROFILE AWS_DEFAULT_REGION
```

仮想環境は次の演習でも使えるよう残して構いません。不要になった場合は、リポジトリ最上位からこの演習の`.venv`だけを削除します。

Windows PowerShell:

```powershell
if (Test-Path -LiteralPath .\sections\s04\l04\.venv) { Remove-Item -LiteralPath .\sections\s04\l04\.venv -Recurse }
Test-Path -LiteralPath .\sections\s04\l04\.venv
```

macOS / Linux:

```sh
if [ -d sections/s04/l04/.venv ]; then rm -r -- sections/s04/l04/.venv; fi
test ! -e sections/s04/l04/.venv && echo "演習用仮想環境を削除しました"
```

削除確認が`False`（Windows）または「演習用仮想環境を削除しました」（macOS / Linux）なら、仮想環境は残っていません。`pyproject.toml`と`uv.lock`は依存関係の再現に使うため残します。

## 参考資料

- [Boto3 credentials](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/credentials.html)
- [AWS SDKs and tools shared config and credentials files](https://docs.aws.amazon.com/sdkref/latest/guide/file-location.html)
- [AWS CLI: get-caller-identity](https://docs.aws.amazon.com/cli/latest/reference/sts/get-caller-identity.html)
- [AWS STS API: GetCallerIdentity](https://docs.aws.amazon.com/STS/latest/APIReference/API_GetCallerIdentity.html)
- [AWS IAM: Service cost information (IAM, IAM Identity Center, and STS)](https://docs.aws.amazon.com/IAM/latest/UserGuide/introduction.html)
- [AWS Secrets Manager: Retrieve secrets](https://docs.aws.amazon.com/secretsmanager/latest/userguide/retrieving-secrets.html)

この教材コードはリポジトリのルートにある[MIT License](../../LICENSE)の条件で利用できます。
