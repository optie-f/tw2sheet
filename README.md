# tw2sheet

## 概要

Twitterにログインしたのち、[Twitterアナリティクス](https://analytics.twitter.com/)(ツイートアクティビティ)の直近1週間分のcsvを自動でダウンロードし、指定のSpreadsheet上のSheetに書き込むスクリプト。

**本スクリプトの利用に起因していかなるトラブルや損害が発生した場合も、当方は一切の責任を負担できかねますので、自己責任でのご利用をお願いします。**


## Requirements

```
google-api-python-client==1.6.4
pandas==0.20.3
selenium==3.8.1
```

## 使い方

1. 以下ページから、Google Chromeのweb driverを`tw2sheet`ディレクトリにダウンロードする。

https://sites.google.com/a/chromium.org/chromedriver/downloads

2. 以下ドキュメントを参考にGoogle APIを有効化し、`client_secret.json`を`tw2sheet`ディレクトリにダウンロードする。

https://developers.google.com/sheets/api/quickstart/python

3. `para.ini` の `XXXX` となっている箇所を埋める。

```para.ini
APPLICATION_NAME   = XXXX  # API有効化時に設定した名前
 
...
 
SPREADSHEET_ID = XXXX  # データをインポートしたいスプレッドシートID
SHEET_NAME     = XXXX  # その中の、書き込みに使用したいシート名(半角英数で)
 
...
 
[TWITTER]  # ログインに使用
USER_ID  = XXXX
PASSWORD = XXXX
```

4. `tw2sheet` をカレントディレクトリとし、以下のコマンドを実行。

```
$ python ScrapeTwitter.py
$ python InsertToSheet.py
```
