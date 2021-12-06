# check-server-by-ping-response

ping の応答によりサーバの状態を確認するプログラム

## 実行コマンド

### pipenv の環境構築

```
% pipenv install
% pipenv shell
```

### サーバの状態を確認

```
% python check_server_status.py
```

## 想定したログエラー

### 形式ミス

ping の送信日時は

- 年:1900~2000
- 月:01~12
- 日:01~31 # どの月の 31 日でも弾きません 例）2 月 31 日は存在しないが、今回は弾かない設定

サブネットマスクは 1-30 以外は弾きます。

### 保存順番ミス

### 不正な値
