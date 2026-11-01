# 関数とモジュールで処理を再利用する

このSectionでは、入力した値を関数へ渡し、処理結果を呼び出し元で受け取り、表示する流れを練習します。続けて、別のPythonファイルをモジュールとして読み込みます。実行にはPython 3.11以降を使います。外部ライブラリ、AWSアカウント、Bedrock接続は不要です。

コマンドは公開repositoryの最上位フォルダーで実行します。Section 2で作った仮想環境を有効にしている場合も、追加パッケージのインストールは必要ありません。Section 2の`requests`は、インストールして使う配布物の例でした。ここではPython標準の仕組みで、同じrepository内の`.py`ファイルをimportします。

## L02: 引数と戻り値で関数の処理を分ける

```text
python sections/s12/l02/main.py
```

```text
API応答: 確認済み
エラーログ: 追加確認が必要
再試行回数: 確認済み
```

`def classify_check(check)`の`check`は関数内で使う仮引数名です。呼び出し時の`classify_check(check)`では、呼び出し元の`check`の値が渡されます。関数内で`return`した文字列は`show_check`の`result`に入り、その後`print`が画面へ表示します。`return`は値を呼び出し元へ返し、`print`は画面へ出す役割です。

### 値を一つ変えて予想する

`sections/s12/l02/main.py`の`if check["status"] == "needs_review":`を、比較する値だけ`"ok"`へ変えます。実行前に3件の表示を予想してから、同じコマンドを実行します。結果は次のとおりです。

```text
API応答: 追加確認が必要
エラーログ: 確認済み
再試行回数: 追加確認が必要
```

比較値の変更で3件すべての分類が変わることを確認したら、比較を`"needs_review"`へ戻します。通常の確認に戻した後、必要なら下のテストを実行します。

関数の戻り値だけを確認するテストも実行できます。

```text
python -m unittest discover -s sections/s12/l02 -p "test_*.py" -v
```

### 独立した失敗例: returnの代わりにprintする

通常コードを変更せず、別ファイルの例を実行します。

```text
python sections/s12/l02/return_vs_print_demo.py
```

```text
確認済み
受け取った値: None
```

`print("確認済み")`は文字を表示しますが、関数からその文字列を返しません。呼び出し元が受け取る値は`None`です。失敗例は通常の`main.py`とは独立しているため、比較を終えたらコードを戻す必要はありません。

## L03: importで自作モジュールの関数を呼び出す

`sections/s12/l03/`には`main.py`と`check_data.py`があります。両方を同じフォルダーに置いた状態で、repository最上位から実行します。

```text
python sections/s12/l03/main.py
```

```text
受け取った確認項目: 3件
API応答: ok
エラーログ: needs_review
再試行回数: ok
```

`from check_data import get_checks`は、同じフォルダーの`check_data.py`から`get_checks`という関数を読み込みます。`checks = get_checks()`で関数を呼ぶと、関数が返したlistを`checks`が受け取ります。forはlistの各dictを一件ずつ読み、呼び出し側で表示します。listの一つの表示値を変えるには`check_data.py`の該当する`status`を変更し、再実行して同じ項目の行を確認します。終了後は変更を元に戻します。

確認項目のlistが期待どおり返ることは、次のテストで確かめられます。

```text
python -m unittest discover -s sections/s12/l03 -p "test_*.py" -v
```

`ModuleNotFoundError`が出た場合は、`main.py`と`check_data.py`が両方`sections/s12/l03/`にあり、コマンドをrepository最上位で実行したかを確認します。このSectionはローカルファイルだけを扱い、AWSリソースや料金は発生しません。
