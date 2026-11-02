# クラス・インスタンス・メソッドのミニ演習

この例は、関数版とクラス版で同じ表示を作ります。関数版では`name`と`status`を呼び出し時に渡します。クラス版では値をインスタンスに保存し、そのインスタンスのメソッドを呼びます。

## 実行

Python 3が使える環境で、このフォルダーを開き、次を実行します。

```text
python class_check_item.py
```

出力:

```text
API応答: ok
API応答: ok
```

1行目は関数、2行目はクラスの例です。`return`は文字列を呼び出し元へ返し、`print`が画面へ表示します。

## 1つだけ変更して予測する

`class_check_item.py`の`CheckItem("API応答", "ok")`にある`"ok"`だけを`"needs_review"`へ変更します。実行前に、2行目がどう変わるか予測してください。

```text
API応答: ok
API応答: needs_review
```

関数版、`format`メソッド、`print`は変更しません。`status`は初期値としてインスタンスに保存され、`format`の戻り値にそのまま使われます。

