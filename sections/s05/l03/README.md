# ファイルを読み、JSONを検証して表示する

リポジトリ最上位で次を実行します。

```text
python sections/s05/l03/main.py
```

正常時は確認項目と状態が表示されます。`main.py`は`Path(__file__)`で同じフォルダーの`cases.json`を選び、UTF-8で文字列として読み取ります。`json.loads`でPythonの値に変換した後、最上位がlistであること、各項目がdictで必須の`name`と`status`を持つことを検査してから表示します。

`cases.json`の一つの`status`を`ok`から`needs_review`へ変え、再実行して表示が変わることを確認したら、値を元に戻します。

JSON構文の失敗は、リポジトリ最上位で次を実行して確かめられます。

```text
python sections/s05/l03/main.py sections/s05/l04/malformed.json
```

ファイルがない場合は`missing.json`を指定します。いずれも原因を示す案内が表示され、終了コード1になります。正常な入力、入力形状、ファイル読み込み、JSON構文の動作は次のunit testで確認できます。

```text
python -m unittest discover -s sections/s05/l03 -p "test_*.py" -v
```

この演習はPython標準ライブラリだけでローカル実行し、AWS resourceや料金は発生しません。
