# CLIの入力先と終了コードを確かめる

リポジトリのルートで`cd sections/s05/l07`を実行します。`python main.py`は既定の`cases.json`を読みます。`python main.py other.json`は指定したファイルを読みます。どちらも名前とstatusが表示され、終了コードは`0`です。

`python main.py wrong-value.json`では入力の案内が表示され、終了コードは`1`です。案内は`print`で画面に表示されます。`main()`が返した整数は、ファイル末尾の`SystemExit(main())`からプロセスの終了コードとして渡されます。

実行直後に終了コードを確認します。PowerShellでは次のように実行します。

```powershell
python main.py wrong-value.json
Write-Output $LASTEXITCODE
```

Command Promptでは実行直後に`echo %ERRORLEVEL%`、macOS/Linuxでは`echo $?`を入力します。成功時の表示と終了コード、失敗時の案内と終了コードは別々に確認してください。

`wrong-value.json`のstatusを一時的に`unknown`から`ok`へ変えて実行すると、通常の結果と終了コード`0`になります。確認後はstatusを`unknown`へ戻してください。
