# Section 03: 生成AIアプリで使うPythonの基礎

このSectionでは、架空の障害調査メモを使い、入力した値がPythonの中をどう進み、画面の結果になるかを確かめます。L02からL05へ進むと、値・複数データ・関数・ファイル入力を順に扱います。AWSやAmazon Bedrockには接続しません。

## 準備

- Python 3.11以降
- [公開hands-on repository](https://github.com/toma1110/python-generative-ai-app-development-amazon-bedrock)をcloneします。

```text
git clone https://github.com/toma1110/python-generative-ai-app-development-amazon-bedrock.git
cd python-generative-ai-app-development-amazon-bedrock
```

ダウンロードする場合は、リンク先の「Code」からZIPを取得して展開し、そのフォルダーをターミナルで開きます。以降のコマンドはrepository最上位で実行します。

```text
python --version
```

macOS / Linuxで`python`が見つからない場合は`python3 --version`を使います。以降も必要に応じて`python`を`python3`に読み替えてください。

コマンド例はすべてrepository最上位で実行します。`cd`は作業場所を移すコマンドです。移動後の場所が分からなくなったら`pwd`（PowerShellでは`Get-Location`）で確認してください。

## L02: 変数と文字列で入力・出力を扱う

```text
python sections/s03/l02/main.py
```

結果:

```text
SREさん、API応答の確認を始めます。
```

`main.py`は上から読むと、値が次の順に移動します。

```text
"SRE" ──代入──> audience ─┐
                          ├─ f-string ─> message ─> print ─> 画面
"API応答" ─代入─> check_item ┘
```

`=`の右側を左側の変数名へ代入します。`audience`や`check_item`は値に付けた名前です。`f"...{変数名}..."`は、波括弧の場所へその時点の値を埋め込んだ文字列を作ります。`print(message)`はその文字列を画面へ表示します。

### 1箇所だけ変える

`main.py`の`check_item = "API応答"`を`check_item = "エラーログ"`に変えて、同じコマンドをもう一度実行します。出力は`SREさん、エラーログの確認を始めます。`となります。担当者名はそのままで、変更した値がf-stringの対応する場所へ入ることを確認できます。確認後は`"API応答"`へ戻します。

### よくある失敗

- `NameError`は、変数名の打ち間違いや、代入より前に使ったときに起きます。代入行と波括弧内の名前が同じか確認します。
- `SyntaxError`は、引用符や`{}`を消したときに起きます。f-stringの先頭に`f`があるか、文字列の引用符が対になっているか確認します。
- 文字を画面に出したいだけなら`print`を使います。関数から別の処理へ値を渡す`return`とは役割が異なり、L04で扱います。

## L03: list・dict・for・ifでデータを処理する

```text
python sections/s03/l03/main.py
```

結果:

```text
API応答: 確認済み
エラーログ: 要確認
  原文ログで発生時刻とエラー内容を確認します。
再試行回数: 確認済み
```

`checks`は角括弧`[]`で囲まれたlistで、複数の確認項目を順番に持ちます。各項目は波括弧`{}`で囲まれたdictです。dictでは`"name"`や`"status"`がkey（値を探す名前）、`"API応答"`や`"確認済み"`がvalue（その中身）です。

実際のコードは`main()`の中にあり、`for`の内側に`if`があります。1周ごとに「今の1件を表示 → 同じ1件のstatusをifで比較 → 条件が真なら追加案内を表示 → 次の1件へ進む」の順です。三件を先に全部表示してからifを実行するのではありません。

| 周回 | `check`の値 | まず表示する行 | ifの判定 | 続けて表示する行 |
| --- | --- | --- | --- | --- |
| 1回目 | API応答 / 確認済み | `API応答: 確認済み` | 偽 | なし |
| 2回目 | エラーログ / 要確認 | `エラーログ: 要確認` | 真 | `原文ログで発生時刻とエラー内容を確認します。` |
| 3回目 | 再試行回数 / 確認済み | `再試行回数: 確認済み` | 偽 | なし |

つまり`for check in checks:`の各周回で、インデントされた表示行とifの両方が実行されます。`check["name"]`のようにkeyを指定すると、その1件のdictからvalueを取り出せます。

### 1箇所だけ変える

`main.py`の3件目を`{"name": "再試行回数", "status": "要確認"}`に変えて実行します。出力は三件の順序を保ち、エラーログと再試行回数の各行の直後に追加案内が表示されます。変更後は`"確認済み"`へ戻します。

### よくある失敗

- `KeyError`は、dictに存在しないkeyを書いたときに起きます。データの`"name"` / `"status"`と、`check[...]`の綴りをそろえます。
- `IndentationError`は、forやifの下の行の字下げがそろわないときに起きます。コロンの次の行を同じ幅だけ字下げします。
- Pythonでは`=`は代入、`==`は値の比較です。ifの条件を`=`にすると構文エラーになります。

## L04: 関数とimportで処理を分ける

```text
python sections/s03/l04/main.py
```

結果:

```text
API応答: 確認済み
エラーログ: 追加確認が必要
再試行回数: 確認済み
```

`classify_check`は「確認項目を分類する関数」です。定義は処理に名前を付けるだけで、その行に来ても中身は実行されません。`main.py`の`main()`内で別ファイル`check_data.py`の`get_checks()`を呼び出すと、データのlistが返ります。次の抜粋では、`for`の中で`show_check`を呼び、その中から分類関数を呼んでいます。

1件ずつの流れは次のとおりです。

```text
main()内: checks = get_checks()
main()内: for check in checks:
             show_check(check)
                 └─ result = classify_check(check)
                       └─ returnで分類文字列を返す
                 └─ print(nameとresult) ─> 画面
```

`return "追加確認が必要"`は呼び出し元へ分類文字列を返すので、`result`へ代入して後で使えます。`print(...)`は画面へ出すだけで、表示した文字列を返しません。`show_check`は表示、`classify_check`は分類を担当します。最後の`if __name__ == "__main__":`が`main()`を呼び、実行を開始します。抜粋の`for`と関数呼び出しはこの`main()`の中で動きます。

### 1箇所だけ変える

編集するファイルは`sections/s03/l04/main.py`です。`classify_check`内の`if check["status"] == "needs_review":`を`if check["status"] == "ok":`へ変え、`python sections/s03/l04/main.py`を実行します。出力は`API応答: 追加確認が必要`、`エラーログ: 確認済み`、`再試行回数: 追加確認が必要`となります。分類対象の比較値だけを変えた結果を確認したら、`"needs_review"`へ戻します。

### よくある失敗

- 実行しても何も表示されないときは、関数を定義しただけで呼び出していない可能性があります。`main()`とその呼び出し条件を確認します。
- `ModuleNotFoundError`は`check_data.py`を見つけられない状態です。2ファイルが同じ`l04`フォルダーにあるか、READMEのコマンドをrepository最上位から実行したか確認します。
- `return "追加確認が必要"`を`print("追加確認が必要")`へ置き換えると、画面にはその文字が出ても関数の戻り値は`None`です。`result`に期待する分類文字列が入らず、後続の`show_check`も`None`を表示します。分類結果を呼び出し元で使うため、この関数は`return`のままにします。

## L05: ファイルとJSONを読み、例外を扱う

このLectureでは、次の段階を順にたどります。

まず完成版を実行する前に、Pythonの対話画面（REPL）でファイルの内容がデータへ変わる様子を追います。repository最上位で`python -X utf8`（macOS / Linuxでは必要に応じて`python3 -X utf8`）を実行すると、`>>>`が表示されます。`-X utf8`はPythonの入出力をUTF-8にする指定です。以下の行を順に入力し、`>>>`は入力しません。

### 1. 固定ファイルを文字列として読む

```pycon
>>> from pathlib import Path
>>> path = Path("sections/s03/l05/cases.json")
>>> text = path.read_text(encoding="utf-8")
>>> print(text)
[
  {"name": "API応答", "status": "ok"},
  {"name": "エラーログ", "status": "needs_review"},
  {"name": "再試行回数", "status": "ok"}
]
```

ここではファイル内容はまだPythonのlistではなく、`text`という文字列です。`Path`はファイルの場所を表し、`read_text`がその内容を読みます。

### 2. JSON文字列をPythonのlist/dictへ変換する

```pycon
>>> import json
>>> checks = json.loads(text)
>>> type(checks).__name__
'list'
>>> type(checks[0]).__name__
'dict'
```

JSONの配列がPythonのlistに、その中のオブジェクトがdictに変わりました。ファイルを読む段階と、JSONとして解釈する段階は別です。

### 3. dictの値を取り出して使う

```pycon
>>> first = checks[0]
>>> first["name"]
'API応答'
>>> first["status"]
'ok'
>>> for check in checks:
...     print(f"{check['name']}: {check['status']}")
...
API応答: ok
エラーログ: needs_review
再試行回数: ok
```

listから`checks[0]`で最初のdictを取り出し、dictのkeyで値を選びます。forはlist内のdictを1件ずつ`check`へ渡します。対話画面を終えるときは`exit()`を入力します。

### 4. 完成版で表示と失敗対応を確認する

ここまでの処理に、値の検査、利用者向け表示、例外対応を加えた完成版を実行します。

1. `Path(__file__).with_name("cases.json")`は、実行中の`main.py`と同じフォルダーにある固定ファイルを指します。
2. `json.loads(text)`でJSON文字列をPythonの値に変換します。
3. 最上位がlistか、項目がdictか、`name`と`status`が使える型・値か確かめてから、表示に使います。
4. `try` / `except`でファイルやJSONの失敗を受け取り、原因と確認方法を表示します。`sys.argv`はコマンドに続けて渡したファイル名を受け取ります。

通常の入力を実行します。

```text
python sections/s03/l05/main.py
```

出力:

```text
API応答: 確認済み
エラーログ: 要確認
  原文ログで発生時刻とエラー内容を確認します。
再試行回数: 確認済み
```

編集するファイルは`sections/s03/l05/cases.json`です。3件目のオブジェクトの後ろにカンマを付け、4件目として`{"name": "デプロイ結果", "status": "needs_review"}`を追加します。`python sections/s03/l05/main.py`を実行すると、4件目の`デプロイ結果: 要確認`とその直下の追加案内が表示されます。listの要素を一つ増やすと、forの周回も一回増えることを確かめたら、追加した4件目を削除して元に戻します。

### 失敗を順に確認する

ファイルがない場合:

```text
python sections/s03/l05/main.py missing.json
```

`missing.json`が見つからない旨が表示され、終了コード1で終わります。コマンドにファイル名を渡した場合、相対pathはターミナルの現在地から探します。確認方法は`Get-Location`（macOS/Linuxは`pwd`）です。引数を省略した通常実行では、`main.py`と同じ場所の`cases.json`を使います。

JSONの書き方が誤っている場合は、同じフォルダーに`broken.json`を作り、`{`だけを書いて保存します。

```text
python sections/s03/l05/main.py sections/s03/l05/broken.json
```

上のコマンドはrepository最上位から実行します。JSONの行番号を含む案内が表示されます。確認後、作成した`broken.json`を削除します。`cases.json`は演習用入力なので残してください。

JSONとしては正しくても、必要な値の型や選択値が違う場合があります。たとえば`cases.json`の`status`を`"unknown"`にすると、`validate_checks`が`ValueError`を発生させます。`load_checks`がその例外を`except ValueError`で捕捉し、`(None, 利用者向けメッセージ)`を返します。`main`は受け取ったメッセージを`print`し、終了コード1を`return`します。実行入口の`SystemExit`がその終了コードをOSへ渡します。`validate_checks`の`return value`は検証済みlistを呼び出し元へ返す命令で、画面には表示しません。`print`は画面表示、`raise`は例外の発生、`except`は例外を捕捉する命令です。修正後は最初の正常実行と同じ出力に戻ることを確認します。

### よくある失敗

- `FileNotFoundError`相当の案内: ファイル名と現在地を確認します。コマンドに渡した相対pathは現在地基準です。
- JSON形式の案内: 二重引用符、カンマ、波括弧、配列の角括弧を確認します。JSONでは末尾の余分なカンマを使えません。
- name/statusの案内: 最上位が配列、その中がオブジェクトか、`name`が空でない文字列か、`status`が許可された文字列かを確認します。
- `python`が見つからない: Pythonをインストールし、新しいターミナルで`python --version`を確認します。

`try`は失敗する可能性のある処理を囲みます。読み込みやJSON変換の`except`は利用者向け案内を作り、値の検査では`validate_checks`の`raise ValueError`を`load_checks`の`except ValueError`が捕捉します。`load_checks`は案内を戻り値として返し、`main`がそれを`print`します。`return 1`は`main`の呼び出し元へ失敗を知らせ、最後の`SystemExit`が終了コードとしてOSへ渡します。正常時は0です。

## 自分で変更した箇所を説明する

- L02: どの代入値を変えると、画面のどの部分が変わるか
- L03: listの何件をforが処理し、どのstatusで追加行が表示されるか
- L04: 引数・return・printがそれぞれどの値や画面を受け持つか
- L05: ファイル文字列がどの段階でlist/dictになり、どの検査が失敗を案内するか

## 自動テスト

L05フォルダーへ移動して実行します。

```text
cd sections/s03/l05
python -m unittest -v
```

7件のテストでJSON値の受け入れ、型・値の誤り、ファイル読み込み、ファイル不在、JSON構文エラーを確認します。テスト後は`cd ../../..`でrepository最上位へ戻れます。

## 料金と後片付け

すべてローカルで実行し、AWS resource、AWS認証情報、Bedrock API、外部ライブラリを使いません。AWS料金やライブラリ取得費用は発生せず、演習コードも追加ファイルを作りません。L05で作った`broken.json`があれば削除します。

この教材コードはrepositoryのルートにある[MIT License](../../LICENSE)の条件で利用できます。
