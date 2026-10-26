# Section 02 環境準備用アプリ

この小さなCLIアプリで、uvを使ったPythonプロジェクトの準備と実行を練習します。Amazon BedrockやAWSサービスへは接続しません。

このフォルダーで次のコマンドを実行します。

```text
uv sync --locked
uv run --locked python section02_demo.py "DB接続数を確認する"
```

L03では仮想環境内でpipを実行してライブラリを追加しました。ここでは`pyproject.toml`に依存関係を記録し、`uv.lock`に解決済みのバージョンを保存します。`uv sync --locked`は`pyproject.toml`の依存関係指定と`uv.lock`の記録が整合しているか確認してから環境を同期します。整合しない場合は`uv.lock`を書き換えずにエラーで停止します。実行時の`uv run --locked`も、両者の整合を確認してからアプリを実行します。
