# Section 13：ファイルとJSONを読み、失敗の原因を確かめる

このSectionでは、ファイルの場所を指定して内容を読み、JSONからPythonの値を取り出し、入力の誤りに応じた結果を確認します。演習はPython標準ライブラリだけで実行できます。AWSへの接続や認証情報は必要ありません。

## 演習を始める

[演習リポジトリ](https://github.com/toma1110/python-generative-ai-app-development-amazon-bedrock)を開き、どちらかの方法で手元に用意します。

- Gitを使う場合は、`git clone https://github.com/toma1110/python-generative-ai-app-development-amazon-bedrock.git`を実行します。
- ZIPを使う場合は、リポジトリ画面の「Code」から「Download ZIP」を選び、展開します。

展開またはcloneしたフォルダーをターミナルで開きます。PathとJSONの演習は既存の[sections/s03/l05のコード](../s03/l05/)を使い、その他の演習は`sections/s13/`内のフォルダーを使います。Pythonのバージョンは3.10以降です。以下の例は`python`コマンドを使います。Windowsで認識されない場合は`py`、macOS/Linuxで認識されない場合は`python3`に読み替えてください。

## 演習の順序

| 順番 | フォルダー | 学ぶこと |
|---|---|---|
| 1 | このREADME | ファイルからCLIの結果まで、値が進む段階をつかむ |
| 2 | [l02](l02/) | 実行前の`SyntaxError`と、実行中の例外を読み分ける |
| 3 | [sections/s03/l05](../s03/l05/) | `Path`でファイルを読み、JSON文字列をPythonの値にする |
| 4 | [l04](l04/) | JSON文法の誤りと、アプリが必要とするデータ形状の違いを確かめる |
| 5 | [l05](l05/) | `raise ValueError`で失敗を知らせ、`try/except`で案内を返す |
| 6 | [l06](l06/) | 2つの戻り値を受け取り、テストで結果を比べる |
| 7 | [l07](l07/) | CLIの入力先、表示、プロセスの終了コードを確認する |
| 8 | このREADME | 失敗した段階と、修正後に確かめる結果を振り返る |

### PathとJSONを読む演習

[sections/s03/l05](../s03/l05/)のプログラムをrepository最上位から実行します。

```text
python sections/s03/l05/main.py
```

正常時は、API応答・エラーログ・再試行回数の状態が表示されます。ファイルを指定して案内を確認するときは、次のように実行します。

```text
python sections/s03/l05/main.py missing.json
```

`missing.json`が見つからない案内が表示され、終了コードは1になります。コードの置き場所は移動していないため、REPLの例でも`sections/s03/l05/cases.json`を指定します。

ファイル内容が文字列になり、その後JSONからlistへ変わることをREPLで確かめる場合は、repository最上位で`python -X utf8`を実行し、次の行を順に入力します。

```pycon
>>> from pathlib import Path
>>> path = Path("sections/s03/l05/cases.json")
>>> text = path.read_text(encoding="utf-8")
>>> import json
>>> checks = json.loads(text)
>>> type(checks).__name__
'list'
>>> exit()
```

## 振り返り

入力を調べるときは、ファイルを読めたか、JSON文法を解析できたか、データがアプリの条件を満たすか、CLIがどの結果を表示したかを順に確認します。原因を直した後は、同じ入力とコマンドをもう一度使い、値または案内が期待どおりになったことを確かめます。画面に出るメッセージと、プロセスの終了コードは別々に確認します。
