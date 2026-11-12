# 関数とモジュールで処理を再利用する

このSectionでは、入力した値を関数へ渡し、処理結果を呼び出し元で受け取り、表示する流れを練習します。続けて、別のPythonファイルをモジュールとして読み込みます。実行にはPython 3.11以降を使います。外部ライブラリ、AWSアカウント、Bedrock接続は不要です。

コマンドは公開repositoryの最上位フォルダーで実行します。Section 2で作った仮想環境を有効にしている場合も、追加パッケージのインストールは必要ありません。Section 2の`requests`は、インストールして使う配布物の例でした。ここではPython標準の仕組みで、同じrepository内の`.py`ファイルをimportします。

## 関数の引数と戻り値を試す

この演習では、関数の引数と戻り値を扱う[演習コード](l02/)を使います。コマンドはrepository最上位から実行します。

```text
python sections/s04/l02/main.py
```

```text
API応答: 確認済み
エラーログ: 追加確認が必要
再試行回数: 確認済み
```

`sections/s04/l02/main.py`の`if check["status"] == "needs_review":`を、比較する値だけ`"ok"`へ変えて同じコマンドを実行すると、API応答と再試行回数が「追加確認が必要」、エラーログが「確認済み」と表示されます。変更後は`"needs_review"`へ戻してください。

## L03: importで自作モジュールの関数を呼び出す

`sections/s04/l03/`には`main.py`と`check_data.py`があります。両方を同じフォルダーに置いた状態で、repository最上位から実行します。

```text
python sections/s04/l03/main.py
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
python -m unittest discover -s sections/s04/l03 -p "test_*.py" -v
```

`ModuleNotFoundError`が出た場合は、`main.py`と`check_data.py`が両方`sections/s04/l03/`にあり、コマンドをrepository最上位で実行したかを確認します。このSectionはローカルファイルだけを扱い、AWSリソースや料金は発生しません。

## クラス・インスタンス・メソッドの演習

この演習では、関数版とクラス版で同じ表示を作ります。実行します。

```text
python -X utf8 sections/s04/l04/class_check_item.py
```

```text
API応答: ok
API応答: ok
```

1行目は関数、2行目は`CheckItem`クラスのインスタンスが`format`メソッドで作った結果です。どちらも`status`だけを受け取り、`API応答`は固定の表示名です。`return`は文字列を呼び出し元へ返し、`print`が画面へ表示します。

`sections/s04/l04/class_check_item.py`の`CheckItem("ok")`にある`"ok"`だけを`"needs_review"`に変え、実行前に2行目を予想してください。実行すると次のようになります。

```text
API応答: ok
API応答: needs_review
```

確認後は値を`"ok"`へ戻します。この演習はローカルで動作し、AWSへの接続は不要です。
