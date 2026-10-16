# PythonからAmazon Bedrockを使うハンズオン

このリポジトリでは、PythonからAmazon Bedrockを使う演習教材をSectionごとに公開しています。Section 02「Pythonの実行環境」からSection 10「おわりに」まで、各SectionのREADMEで実行手順、前提条件、結果の確認、料金の注意、後片付けを確認できます。

## 教材の取得

GitHubページの「Code」から「Download ZIP」を選び、ダウンロードしたZIPを展開してください。展開したフォルダーをターミナルで開き、[Section 02](sections/s02/README.md)の手順から始めます。Gitを使う場合は、このリポジトリをcloneして、ターミナルで展開またはcloneしたフォルダーへ移動してください。

## 演習の一覧

Sectionごとの演習は次のとおりです。

| 学習内容 | 演習 |
| --- | --- |
| Python環境と基本構文 | [Section 02](sections/s02/README.md)、[Section 03](sections/s03/README.md) |
| AWS接続とBedrockの呼び出し | [Section 04](sections/s04/README.md)、[Section 05](sections/s05/README.md) |
| CLI会話とファイル要約 | [Section 06](sections/s06/README.md)、[Section 07](sections/s07/README.md) |
| 出力の比較と改善 | [Section 08](sections/s08/README.md) |
| S3入力を含む完成アプリ | [Section 09](sections/s09/README.md) |
| 演習用AWSリソースの削除 | [Section 10](sections/s10/README.md) |

各SectionのREADMEから準備、実行、結果確認、料金の確認、後片付けへ進めます。

## 実行環境と費用

Courseの演習は受講者自身のPCで、CLIまたはVS Codeを使って進めます。Pythonとuvを使用します。AWSへ接続する演習では、利用するアカウント、リージョン、モデルの利用可否と権限を実行前に確認してください。Amazon Bedrockのモデル利用とAmazon S3の利用には料金が発生する場合があります。実行前に各SectionのREADMEで料金に関する注意と後片付けの手順を確認してください。

AWSの認証情報やアプリ固有の秘密情報をコード、設定ファイル、コマンド履歴へ書き込まない手順を案内しています。教材用データを使い、生成AIの出力を原文と照合して判断する方法も扱います。

## ライセンス

このリポジトリの教材と資料はMIT Licenseで公開しています。利用条件は[LICENSE](LICENSE)を確認してください。
