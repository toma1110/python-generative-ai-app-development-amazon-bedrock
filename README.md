# PythonからAmazon Bedrockを使うハンズオン

このリポジトリは、PythonからAmazon Bedrockを使う演習教材をSectionごとに掲載します。Section 02「Pythonの実行環境」、Section 03「生成AIアプリで使うPythonの基礎」、Section 04「APIとAWS接続」、Section 05「Bedrockを1回呼ぶ」の演習を公開しています。各READMEで実行手順、前提条件、結果の確認、後片付けを確認してください。

## 演習の一覧

公開済みのSectionと今後追加する演習は次のとおりです。

| 学習内容 | 演習 |
| --- | --- |
| Python環境と基本構文 | [Section 02](sections/s02/README.md)、[Section 03](sections/s03/README.md) |
| AWS接続とBedrockの呼び出し | [Section 04](sections/s04/README.md)、[Section 05](sections/s05/README.md) |
| CLI会話とファイル要約 | Section 06、07（公開予定） |
| 出力の比較と改善 | Section 08（公開予定） |
| S3入力を含む完成アプリ | Section 09（公開予定） |
| 演習用AWSリソースの削除 | Section 10（公開予定） |

各SectionのREADMEから準備、実行、結果確認、料金の確認、後片付けへ進めます。

## 実行環境と費用

Courseの演習は受講者自身のPCで、CLIまたはVS Codeを使って進める予定です。Pythonとuvを使用します。AWSへ接続する演習では、利用するアカウント、リージョン、モデルの利用可否と権限を実行前に確認する内容を教材に含めます。Amazon Bedrockのモデル利用とAmazon S3の利用には料金が発生する場合があります。各演習の公開時に、料金と後片付けの手順を案内します。

AWSの認証情報やアプリ固有の秘密情報をコード、設定ファイル、コマンド履歴へ書き込まない手順を教材に含める予定です。教材用データを使い、生成AIの出力を原文と照合して判断する方法も扱います。

## ライセンス

このリポジトリの教材と資料はMIT Licenseで公開しています。利用条件は[LICENSE](LICENSE)を確認してください。
