# 2つの戻り値を受け取り、テストで確かめる

リポジトリのルートで`cd sections/s13/l06`を実行します。`python -m unittest -v`で2つのテストを実行します。1つ目は戻り値の`checks`が期待するリストと同じで、`error`が`None`であることを`assertEqual`と`assertIsNone`で確認します。2つ目は`checks`が`None`で、`error`にstatusに関する案内が含まれることを`assertIsNone`と`assertRegex`で確認します。このテストコードでは例外を期待していません。

`load_checks`は正常時に`(checks, None)`、不正な値のときに`(None, error)`を返します。括弧内は2つの位置を持つタプルです。テストの`checks, error = load_checks(path)`では、それぞれの位置を2つの名前に受け取っています。

この関数の結果はCLIからではなく、Pythonの対話コマンドで表示します。正常な入力を確認します。

```sh
python -X utf8 -c "from pathlib import Path; from main import load_checks; checks, error = load_checks(Path('cases.json')); print('checks:', checks); print('error:', error)"
```

続けて、不正な入力の案内を確認します。

```sh
python -X utf8 -c "from pathlib import Path; from main import load_checks; checks, error = load_checks(Path('wrong-value.json')); print('checks:', checks); print('error:', error)"
```

それぞれの結果は、正常時にリストと`None`、不正時に`None`と検証メッセージです。`with tempfile.TemporaryDirectory() as directory:`はテスト用の一時フォルダーを作り、ブロックの終了時に片付けます。テスト用ファイルを演習用のサンプルと分けられます。
