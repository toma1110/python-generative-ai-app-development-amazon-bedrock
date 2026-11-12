# JSON文法とアプリのデータ検証を分ける

リポジトリのルートで`cd sections/s05/l04`を実行します。

`python main.py malformed.json`ではJSONの文法が不正なため、解析時の`JSONDecodeError`に対応する案内が表示されます。この入力からPythonの値ができたわけではありません。

`python main.py wrong-shape.json`ではJSONの解析は成功しますが、最上位が必要な配列ではなく辞書なので、アプリの検証で`ValueError`になります。`python main.py wrong-item.json`では配列内の要素が辞書ではなく、`python main.py wrong-value.json`では`status`が許可された値ではありません。どの入力が文法で止まり、どれがアプリの条件で止まるかを比べてください。`python main.py cases.json`では正しいデータが表示されます。

一つの不正な入力を修正して確認する場合は、`wrong-shape.json`を`[{"name":"API応答","status":"ok"}]`に置き換えて`python main.py wrong-shape.json`を実行します。名前と状態が表示されたら、続きの演習のために元の内容`{"name":"API応答","status":"ok"}`へ戻してください。他の入力ファイルも変更した場合は、次の内容へ戻します。

- `malformed.json`: `[{"name":"API応答",]`
- `wrong-item.json`: `["API応答"]`
- `wrong-value.json`: `[{"name":"API応答","status":"unknown"}]`

不正なJSONの解析と、解析後の値に対するアプリの検証は別の段階です。
