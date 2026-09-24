# Section 03: 生成AIアプリで使うPythonの基礎

このSectionでは、架空の障害調査メモを題材に、入力と表示を変数で変え、複数の確認項目を条件に応じて処理し、関数へ分け、最後にJSONファイルから読み込みます。Amazon BedrockやAWSサービスへは接続しません。

## 事前準備

- Python 3.11以降
- リポジトリをダウンロードまたはcloneし、リポジトリ最上位でターミナルを開けること

Pythonのバージョンを確認します。

```text
python --version
```

macOS / Linuxで`python`が見つからない場合は`python3 --version`を使います。以降の例も必要に応じて`python`を`python3`に読み替えてください。

## L02: 変数と文字列で入力・出力を扱う

```text
cd sections/s03/l02
python main.py
```

「SREさん、API応答の確認を始めます。」と表示されます。`main.py`の`audience`または`check_item`の値を変更してもう一度実行し、f-stringで組み立てた表示内容も変わることを確認します。

## L03: list・dict・if・forでデータを処理する

リポジトリ最上位へ戻ってから実行します。

```text
cd ../../..
cd sections/s03/l03
python main.py
```

3件の確認項目が表示されます。`status`が`要確認`の項目では追加確認の案内が出ます。`checks`の値を一つ追加または変更し、listの各dictをforで処理し、ifの結果によって表示が変わることを確かめます。

## L04: 関数とimportで処理を分ける

```text
cd ../../..
cd sections/s03/l04
python main.py
```

`check_data.py`から確認データを読み込み、`main.py`の関数で状態を分類して表示します。`classify_check`の条件を変えると、処理結果が変わります。`get_checks`（入力）、`classify_check`（処理）、`show_check`（表示）がどの役割かを見つけてください。

`ModuleNotFoundError`が出た場合は、`sections/s03/l04`を作業フォルダーにしているか、`main.py`と`check_data.py`が同じフォルダーにあるかを確認します。

## L05: ファイルとJSONを読み、例外を扱う

```text
cd ../../..
cd sections/s03/l05
python main.py
```

`cases.json`の3件を読み込み、確認項目を表示します。JSONは項目の配列で、各項目に空でない文字列の`name`と、`ok`または`needs_review`の`status`が必要です。`main.py`はファイルがない場合、UTF-8で読めない場合、JSONの構文や項目の形が正しくない場合を分けて案内します。失敗時もPythonのtracebackをそのまま出すのではなく、何を確認するかを短く表示します。

存在しないファイルを指定して、ファイル読み込み失敗を確認できます。

```text
python main.py missing.json
```

JSONの構文エラーも確認するには、`cases.json`を別の場所へ一時的に移すのではなく、VS Codeなどで同じフォルダーに`broken.json`を新規作成し、`{`だけを書いて保存します。そのコピーを指定して実行します。

```text
python main.py broken.json
```

確認後、`broken.json`を削除して構いません。`cases.json`は教材の入力なので残してください。

## 想定と異なる場合

- `python` / `python3`が見つからない: Pythonをインストールして新しいターミナルを開き、バージョン確認をやり直します。
- Windowsの古いコンソールで日本語が正しく表示されない: VS Codeの統合ターミナルまたはUTF-8に対応したWindows Terminalを使います。
- `can't open file`またはJSONファイルが見つからない: `pwd`（PowerShellでは`Get-Location`）で現在地を確認し、README記載のLectureフォルダーへ移動します。
- L04でimportに失敗する: `main.py`と`check_data.py`が同じ`l04`フォルダーにあることを確認します。
- L05でJSONの形式エラーが出る: ファイル名、文字列の二重引用符、カンマの位置を確認します。JSONでは末尾の余分なカンマも使えません。

## 料金と後片付け

すべてのプログラムはローカルで動き、AWS resource、AWS認証情報、Bedrock API、外部ライブラリを使いません。AWS利用料金やライブラリ取得費用は発生しません。各コマンドで作るファイルもありません。演習後はプログラムを終了し、L05で作った`broken.json`があれば削除します。

この教材コードはリポジトリのルートにある[MIT License](../../LICENSE)の条件で利用できます。
