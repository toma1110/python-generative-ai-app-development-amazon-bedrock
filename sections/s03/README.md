# Section 03: 生成AIアプリで使うPythonの基本構文

このSectionでは、架空の障害調査メモを使い、入力した値がPythonの中をどう進み、画面の結果になるかを確かめます。値と複数データの次に、[関数・モジュール](../s04/README.md)と[ファイル・JSON](../s05/README.md)の演習へ進みます。AWSやAmazon Bedrockには接続しません。

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

コードを読む前に、記号と字下げを確認します。`=`は右側の値を左側の名前へ代入し、`==`は左右の値が等しいかを比べます。`for`や`if`の次の行は字下げされ、その処理の内側になります。字下げが戻ると、その`for`や`if`の外側です。

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
- Pythonでは`=`と`==`は役割が異なります。ifの条件には比較の`==`を書きます。

## S03の演習を振り返る

- L02: どの代入値を変えると、画面のどの部分が変わるか
- L03: listの何件をforが処理し、どのstatusで追加行が表示されるか

---

## 次のSection

関数・import・classの演習は[Section 04](../s04/README.md)、ファイル・JSON・失敗の演習は[Section 05](../s05/README.md)へ進みます。各SectionのREADMEに、現在の配布番号と実行コマンドがあります。
