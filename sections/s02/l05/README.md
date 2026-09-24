# Section 02 環境準備用アプリ

この小さなCLIアプリで、uvを使ったPythonプロジェクトの準備と実行を練習します。Amazon BedrockやAWSサービスへは接続しません。

このフォルダーで次のコマンドを実行します。

```text
uv sync
uv run python section02_demo.py "DB接続数を確認する"
```

L03では仮想環境内でpipを実行してライブラリを追加しました。ここでは`pyproject.toml`に依存関係を記録し、`uv sync`でロックファイルに記録されたバージョンを環境へ同期します。実行時は`uv run`を使うと、依存関係が同期された環境でアプリが動きます。
