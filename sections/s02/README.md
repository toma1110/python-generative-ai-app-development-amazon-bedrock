# Section 02: Pythonの実行環境

この演習では、同じPythonファイルをCLIとVS Codeから実行し、仮想環境ごとにライブラリを分け、最後に`uv`で小さなCLIアプリを準備します。ここではAWSへ接続せず、Amazon Bedrockの呼び出しもしません。

## 事前準備

- Python 3.11以降
- Visual Studio CodeとMicrosoftのPython拡張機能（L02）
- `uv`（L05）
- インターネット接続（L03のパッケージ導入とL05の初回依存関係取得）

Pythonが利用できることを確認します。すでにPython 3.11以降が使える場合は、そのまま演習へ進めます。WindowsでPythonが見つからない場合は、Python本体を別途インストールしてください。VS CodeのPython拡張機能だけではPython本体はインストールされません。

```powershell
python --version
```

macOS / Linuxでは`python3 --version`を使います。Windowsで`python`が見つからない場合は、Pythonインストール時にPATHへ追加し、新しいターミナルを開いてください。

## L02: CLIとVS Codeから同じファイルを実行する

リポジトリの最上位フォルダーを開いたターミナルで、演習用フォルダーへ移動します。

```powershell
cd sections/s02/l02
```

CLIから実行します。

```powershell
python hello.py
```

macOS / Linuxでは`python3 hello.py`を使います。`Hello, Python!`と、この実行に使われたPythonの場所が表示されます。

次にVS Codeで`l02`フォルダーを開き、`hello.py`を表示します。コマンドパレットから`Python: Select Interpreter`を選び、CLIの実行で表示されたPythonを選択してください。ファイル右上の実行ボタンから実行すると、同じ挨拶と同じPythonの場所が表示されます。Python拡張機能が実行ボタンを提供し、選択したインタープリターがファイルを実行します。

場所が異なる場合は、VS Codeで選択中のインタープリターをもう一度確認します。CLIとVS Codeで別のPythonを使うと、後で導入したライブラリが見つからないことがあります。

## L03: 仮想環境（venv）とpipでライブラリを分ける

L02で使ったターミナルを続けて使います。現在の場所は`l02`なので、リポジトリの最上位フォルダーへ戻ってから`l03`へ移動し、仮想環境を作ります。

```powershell
cd ../../..
cd sections/s02/l03
python -m venv .venv
```

macOS / Linuxでは`python3 -m venv .venv`を使います。次に仮想環境を有効化します。

```powershell
.\.venv\Scripts\Activate.ps1
```

PowerShellの代わりにコマンドプロンプトを使う場合は`.venv\Scripts\activate.bat`、macOS / Linuxでは`source .venv/bin/activate`を実行します。PowerShellの実行ポリシーで有効化できない場合、ポリシーは変更せず、以下の「有効化ができない場合」のコマンドを使えます。

有効化したターミナルで`requests`をインストールし、確認プログラムを実行します。

```text
python -m pip install requests
python inspect_package.py
```

仮想環境のPython、ベースPython、`requests`のバージョンとファイルの場所が表示されます。`requests`の場所が`.venv`の下にあることを確認します。表示されるパスの区切りやユーザー名部分は環境によって異なります。

有効化ができない場合は、仮想環境のPythonを直接指定します。

```powershell
.\.venv\Scripts\python -m pip install requests
.\.venv\Scripts\python inspect_package.py
```

macOS / Linuxでは`./.venv/bin/python -m pip install requests`と`./.venv/bin/python inspect_package.py`を使います。

仮想環境を有効化して使った場合は、終わったら環境を終了します。仮想環境のPythonを直接指定した場合は、この操作は不要です。

```text
deactivate
```

L03では仮想環境を作り、その中でpipを使ってライブラリを追加しました。次のL05では`pyproject.toml`へ依存関係を記録し、`uv sync`で環境を準備します。どちらもライブラリをプロジェクトごとに分けますが、L05では依存関係とlockfileから環境を再現します。

## L05: uvで演習用アプリを準備して実行する

L03と同じターミナルを使います。仮想環境を有効化していた場合は`deactivate`を実行します。現在の場所は`l03`なので、リポジトリの最上位フォルダーへ戻ってから`l05`へ移動します。依存関係を同期してアプリを実行します。

```powershell
cd ../../..
cd sections/s02/l05
uv sync
uv run python section02_demo.py "DB接続数を確認する"
```

出力には入力した確認事項が表示されます。文字を変えて再実行し、表示内容が変わることを確かめます。この小さなプログラムは環境準備用のCLI例です。Bedrockを呼び出すアプリではありません。

アプリはUTF-8で文字を出力します。Windowsの古いコンソールで日本語が正しく表示されない場合は、VS Codeの統合ターミナルまたはUTF-8に対応したWindows Terminalで実行してください。

`pyproject.toml`にはプロジェクトの依存関係、`uv.lock`（ロックファイル）には解決したバージョンが記録されます。`uv run`はプロジェクト環境を同期してからコマンドを実行します。別のPCで同じ演習をするときも、`pyproject.toml`と`uv.lock`から環境を準備できます。

## 想定と異なる場合

- `python` / `python3`や`uv`が見つからない: インストール後に新しいターミナルを開き、バージョン確認をやり直します。
- `requests`をimportできない: venvが有効か、または`.venv`内のPythonでpipとスクリプトの両方を実行したか確認します。
- `python -m venv .venv`で`ensurepip`のエラーが出る: `python -c "import sys; print(sys.executable)"`で実行に使われているPythonを確認し、そのインストールにpipが含まれているか調べます。pipが含まれない場合は、[python.orgのWindows向け案内](https://www.python.org/downloads/windows/)を確認して必要な場合だけPythonを追加し、新しいターミナルからやり直します。venvを作成できた場合、Pythonを追加し直す必要はありません。
- `uv sync`が失敗する: ネットワーク接続と`uv --version`を確認し、表示されたエラーのパッケージ名とPythonバージョンを確認します。
- VS Codeで出力するPythonの場所がCLIと異なる: `Python: Select Interpreter`でCLIに表示されたPythonを選択します。

## 料金と後片付け

このSectionはローカルPCだけで実行し、AWSリソース、AWS認証情報、Bedrock APIを使いません。AWS利用料金は発生しません。L03の`requests`とL05の`rich`はPythonライブラリで、初回取得にインターネット接続が必要です。

演習を終えたら、仮想環境を有効化しているターミナルでは`deactivate`を実行し、実行中のアプリを終了します。リポジトリの最上位フォルダーから、L03とL05の仮想環境だけを削除します。以下のコマンドは対象パスがある場合だけ削除し、続けて存在しないことを確認します。

Windows PowerShell:

```powershell
if (Test-Path -LiteralPath .\sections\s02\l03\.venv) { Remove-Item -LiteralPath .\sections\s02\l03\.venv -Recurse }
if (Test-Path -LiteralPath .\sections\s02\l05\.venv) { Remove-Item -LiteralPath .\sections\s02\l05\.venv -Recurse }
Test-Path -LiteralPath .\sections\s02\l03\.venv
Test-Path -LiteralPath .\sections\s02\l05\.venv
```

最後の2行がどちらも`False`なら、両方の仮想環境を削除できています。

macOS / Linux:

```sh
if [ -d sections/s02/l03/.venv ]; then rm -r -- sections/s02/l03/.venv; fi
if [ -d sections/s02/l05/.venv ]; then rm -r -- sections/s02/l05/.venv; fi
test ! -e sections/s02/l03/.venv && echo "L03の仮想環境を削除しました"
test ! -e sections/s02/l05/.venv && echo "L05の仮想環境を削除しました"
```

各確認行で「仮想環境を削除しました」と表示されれば、そのパスは残っていません。`pyproject.toml`と`uv.lock`は環境の再現に使うため削除せず残します。仮想環境はREADMEの手順で再作成できます。

## 参考資料

- [Python: venv — Creation of virtual environments](https://docs.python.org/3/library/venv.html)
- [Python Packaging User Guide: Installing Packages](https://packaging.python.org/en/latest/tutorials/installing-packages/)
- [VS Code: Getting Started with Python](https://code.visualstudio.com/docs/python/python-tutorial)
- [uv: Working on projects](https://docs.astral.sh/uv/guides/projects/)
- [uv: Managing dependencies](https://docs.astral.sh/uv/concepts/projects/dependencies/)
