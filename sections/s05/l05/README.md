# 例外を捕まえて利用者向けの案内にする

リポジトリのルートで`cd sections/s05/l05`を実行します。`python main.py wrong-value.json`を実行し、statusの入力を確認する案内が表示されることを確かめます。

`validate_checks`の`raise ValueError(...)`は、読み取った値をアプリで使えないと知らせます。呼び出し元の`load_checks`はその関数を`try`の中で呼び、想定した`ValueError`を`except`で捕まえて案内文を返します。`main`はその文を表示します。例外を発生させる箇所と捕まえる箇所をコードで追ってください。

`python main.py cases.json`では正常な結果が表示されます。`return checks`は通常の値を呼び出し元へ返し、失敗を知らせる`raise`とは役割が異なります。`cases.json`のstatusを一時的に`unknown`へ変えて実行し、案内を確認したら`ok`へ戻して再実行します。

この例が捕まえるのはデータ検証で予想される`ValueError`です。ほかの例外までまとめて隠さず、調査できるようにしています。
