# HTTPの要求と応答を確かめる

この小さなAPIを動かし、`GET /notes/123`のJSON応答と、`POST /notes`で送るJSONを確認します。`GET /notes/999`も試し、入力したIDに対応するメモがないときのHTTP `404`とエラー本文を読みます。

この教材用APIはPython標準ライブラリだけで動きます。データはプロセス内のメモリに置き、サーバーを止めると初期状態に戻ります。AWS接続、Webフレームワーク、外部サービスは使いません。

## 起動

Python 3.11以降と`curl`を使います。AWS CLI、AWSアカウント、uvの準備は不要です。以下のコマンドはWindows PowerShellの`curl.exe`表記です。macOS/Linuxでは`curl.exe`を`curl`に置き換えてください。

ターミナルを2つ用意します。1つ目はリポジトリ最上位から`sections/s04/l02`へ移動してサーバーを起動し、そのまま待ち受けに使います。2つ目は**リポジトリ最上位**で開き、後述のcurlコマンドを実行します。POSTの入力ファイルもリポジトリ最上位からの相対pathです。

```text
cd sections/s04/l02
python main.py
```

`API ready: http://127.0.0.1:8000`と表示されたら、サーバーは自分のPC内だけで待ち受けています。このターミナルは起動したままにします。

## GETでメモを取得する

2つ目のターミナルから次を実行します。

```text
curl.exe -sS -i -X GET http://127.0.0.1:8000/notes/123
```

応答の先頭に`HTTP/1.0 200 OK`、headerに`Content-Type: application/json; charset=utf-8`、bodyに次のJSONが表示されます。

```json
{"id": "123", "title": "調査メモ", "body": "API応答を確認する"}
```

コマンドの`-X GET`はmethod、`127.0.0.1:8000`は接続先、`/notes/123`はpathです。APIはクライアントが使う操作の約束、HTTPはその要求と応答を運ぶ通信の決まり、JSONはこの例のデータ形式です。RESTはリソースをURIで識別し、表現をやり取りする設計上のスタイルです。JSONのbodyはリソースそのものではなく、メモというリソースの情報を表現します。HTTP要求はmethod、path、headers、（必要なら）bodyからなり、応答ではstatusとheaders、bodyを確認できます。

HTTP要求はそれぞれ直前の要求内容を知らなくても解釈でき、RESTでも要求間のやり取りを独立させることが制約の一つです。これはサーバーがデータを保存できないという意味ではありません。このAPIは作成したメモをメモリに保存します。RESTにはほかにも制約がありますが、この演習では入口だけを扱います。

`Content-Type` headerはbodyの形式を伝えます。認証が必要なAPIでは`Authorization` headerなどで認証情報を送ることがありますが、このローカルAPIには認証機能がなく、認証headerも不要です。HTTPSはHTTP通信をTLSで保護します。この教材は自分のPC内の`127.0.0.1`だけで動かすためHTTPを使い、機密情報を送信しません。

同じメモを短い表示で取得するため、URLへquery parameterを一つ加えます。

```text
curl.exe -sS -i -X GET "http://127.0.0.1:8000/notes/123?view=compact"
```

応答bodyは`{"id": "123", "title": "調査メモ"}`です。接続先は`127.0.0.1:8000`、pathは`/notes/123`、queryは`view=compact`です。queryは今回のAPIが決めた形式で、同じメモの短いJSON表現を選びます。

## 一つの入力を変えてエラーを読む

URL末尾のIDを`123`から`999`へ変えて実行します。

```text
curl.exe -sS -i -X GET http://127.0.0.1:8000/notes/999
```

応答は`HTTP/1.0 404 Not Found`で、bodyは`{"error": "note_not_found", "id": "999"}`です。statusだけでなくbodyも見れば、指定したIDのメモが見つからなかったことが分かります。

## POSTでメモを作る

JSON bodyを付けて`POST /notes`を送ります。`Content-Type`はbodyの形式をサーバーへ伝えます。

```text
curl.exe -sS -i -X POST http://127.0.0.1:8000/notes -H "Content-Type: application/json" --data-binary "@sections/s04/l02/request.json"
```

2つ目のターミナルはリポジトリの最上位で実行します。`Content-Type: application/json`は続けて送るbodyがJSONであることを伝え、`--data-binary`が`request.json`のUTF-8 bytesをそのままbodyとして送ります。期待する応答は次のとおりです。

送るbodyは、`sections/s04/l02/request.json`に保存した次のJSONです。

```json
{"title":"追加メモ","body":"POSTで作成"}
```

```text
HTTP/1.0 201 Created
Content-Type: application/json; charset=utf-8

{"id": "124", "title": "追加メモ", "body": "POSTで作成"}
```

headerのContent-TypeはJSON応答の形式を示し、bodyには作成したメモの表現が返ります。`-i`はstatus lineとresponse headersをbodyと一緒に表示します。

`HTTP/1.0 201 Created`と、`id`が`124`のJSONが返ります。続けてそのIDをGETすると、同じプロセスのメモリに保存された表現を確認できます。

```text
curl.exe -sS -i -X GET http://127.0.0.1:8000/notes/124
```

POSTで作ったメモはサーバーのメモリに残るため、各要求は前の会話手順を覚えていなくても処理できます。statelessは要求間で直前のやり取りの文脈に依存しないという意味で、サーバーがデータを保存できないという意味ではありません。この教材のメモはサーバー内に保存されますが、保存は一時的です。

## AWS Converse APIとの対応

Amazon Bedrock RuntimeのConverse APIも、HTTPの`POST /model/{modelId}/converse`へJSON形式で要求を送ります。boto3はAWS SDK for Python、つまりPythonからAWS APIを呼びやすくするライブラリです。`bedrock-runtime` clientの`converse(modelId=..., messages=...)`を呼ぶと、SDKがHTTP POST要求を組み立ててAWS署名を付けます。`modelId`引数はURL pathの`{modelId}`に、`messages`引数はJSON request bodyの`messages` fieldに対応します。成功時はHTTP response bodyのJSONを読み取ったPython辞書が返り、`output`や`usage`などのfieldを含みます。AWSサービスがHTTPエラー応答を返すと`ClientError`が送出され、HTTP status codeは例外の`error.response['ResponseMetadata']['HTTPStatusCode']`で確認できます。通信障害などでHTTP応答自体を受け取れない場合はstatus codeもありません。エラーの扱いは[Section 05 README](../../s05/README.md)のL04と[Boto3のエラー処理ガイド](https://docs.aws.amazon.com/boto3/latest/guide/error-handling.html)で扱うため、ここではこの対応だけを押さえます。AWS署名の自作やBedrockへの実呼び出しは行いません。

このローカルAPIのPOSTは教材例で、Converse APIと同じURLやデータ形式ではありません。HTTPのmethod・path・header・JSON body・statusという見方を練習し、次のBedrock hands-onではboto3の引数と戻り値へ結び付けます。

## 終了と後片付け

起動したサーバーのターミナルで`Ctrl+C`を押します。ターミナルにプロンプトが戻れば、サーバープロセスは終了しています。2つ目のターミナルから接続も確かめます。

```text
curl.exe -sS --noproxy "*" --connect-timeout 2 -i http://127.0.0.1:8000/notes/123
```

接続拒否のcurl終了コード`7`なら、port 8000で応答するサーバーはありません。終了コード`28`は時間内に接続できなかったことだけを示し、サーバー終了の証明にはなりません。プロンプトが戻らず応答もしない場合は別のプロセスを終了させず、起動したターミナルの状態を確認してください。この演習はローカルプロセスとメモリだけを使うため、AWS resource、従量課金、生成ファイルはありません。別ターミナルは閉じて構いません。

## 実装テスト（任意）

教材コードの正常系とエラー応答をPython標準の`unittest`で確認できます。リポジトリ最上位で実行してください。

```text
python -B -m unittest discover -s sections/s04/l02 -p test_main.py -v
```

5件のテストが成功すれば、GET・query・POST後の取得、存在しないresource、入力不備、route不明、未対応methodを確認できています。

## 参考資料

- [MDN: HTTP messages](https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Messages)
- [RFC 9110: HTTP Semantics](https://www.rfc-editor.org/rfc/rfc9110.html)
- [Fielding: REST architectural style, Chapter 5](https://ics.uci.edu/~fielding/pubs/dissertation/rest_arch_style.htm)
- [Amazon Bedrock Runtime: Converse API](https://docs.aws.amazon.com/bedrock/latest/APIReference/API_runtime_Converse.html)
- [Boto3: Bedrock Runtime `converse`](https://docs.aws.amazon.com/boto3/latest/reference/services/bedrock-runtime/client/converse.html)
