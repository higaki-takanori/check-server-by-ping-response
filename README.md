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

## main 関数

```python
if __name__ == '__main__':
  logs = LogCollection()
  for line in open(LOGFILENAME, "r"):
    datetime, ipaddress, restime = line.split("\n")[0].split(",")
    is_correct_format = check_format(datetime, ipaddress, restime, IS_VISUABLE_MISS_FORMAT)
    if is_correct_format:
      log = Log(datetime, ipaddress, restime)
      if (log.datetime is not None) and (log.ipaddress is not None) and (log.restime is not None):
        logs.append(log)
      else:
        del log

  servers = logs.get_servers()
  subnets = logs.get_subnets()

  print("---サーバの故障一覧を表示---")
  continue_timeout_error = 2  # continue_timeout_error 回 timeout が連続すれば、故障とする
  for ipaddress, server in servers.items():
    server.show_period_server_error(continue_timeout_error)

  print("---サーバの過負荷状態を表示---")
  last_overload = 2 # 直近 last_overload 回の平均応答時間を取得
  mtime_overload = 50 # 平均応答時間が mtime_overload ミリ秒以上となった場合、過負荷状態
  for ipaddress, server in servers.items():
    server.show_period_server_overload(last_overload, mtime_overload)

  print("---サブネットの故障期間を表示---")
  continue_timeout_error = 1  # continue_timeout_error 回 timeout が連続すれば、故障とする
  for network_address, subnet in subnets.items():
    subnet.show_period_subnet_error(continue_timeout_error)


  print("---サブネットの過負荷状態を表示---")
  last_overload = 2 # 直近 last_overload 回の平均応答時間を取得
  mtime_overload = 50 # 平均応答時間が mtime_overload ミリ秒以上となった場合、過負荷状態
  for network_address, subnet in subnets.items():
    subnet.show_period_subnet_overload(last_overload, mtime_overload)
```

### main 関数の処理

#### LogCollection インスタンスの作成

list クラスを継承した [LogColloction クラス](#LogCollection-クラス)のインスタンスを作成。

ログファイルごとに処理できるように、クラスを作成した。

```python
logs = LogCollection()
```

#### Log インスタンスの作成及び LogCollection への追加

ログファイルからログの情報を入手し、1 つのログに対して、1 つの [Log クラス](#Log-クラス)のインスタンスを作成し、LogCollection インスタンスへ追加する。

追加する前に、形式チェックを行い誤ったものは追加しない。

```python
for line in open(LOGFILENAME, "r"):
    datetime, ipaddress, restime = line.split("\n")[0].split(",")
    is_correct_format = check_format(datetime, ipaddress, restime, IS_VISUABLE_MISS_FORMAT)
    if is_correct_format:
      log = Log(datetime, ipaddress, restime)
      if (log.datetime is not None) and (log.ipaddress is not None) and (log.restime is not None):
        logs.append(log)
      else:
        del log
```

#### LogServer インスタンスの作成

ログをサーバ毎に処理するための[LogServer クラス](#LogServer-クラス)のインスタンスを作成する。

LogCollection クラス内のメソッドからインスタンスを作成することができる。

```python
servers = logs.get_servers()
```

#### LogSubnet インスタンスの作成

ログをサブネット（スイッチ）毎に処理するための[LogSubnet クラス](#LogSubnet-クラス)のインスタンスを作成する。

LogCollection クラス内のメソッドからインスタンスを作成することができる。

```python
subnets = logs.get_subnets()
```

#### 各サーバの故障一覧

各サーバの故障一覧を表示する。

その際に引数(continue_timeout_error)に数値を入れることで timeout 連続によるエラーを再現している。

故障が復旧しているかを判断することができる表示となっている。

```python
  print("---サーバの故障一覧を表示---")
  continue_timeout_error = 2  # continue_timeout_error 回 timeout が連続すれば、故障とする
  for ipaddress, server in servers.items():
    server.show_period_server_error(continue_timeout_error)
```

出力

```
---サーバの故障一覧を表示---
復旧済: 10.20.30.1/16 は 2020-10-19 13:33:25 から0:00:02の時間、故障していました。
復旧済: 10.20.30.1/16 は 2020-10-19 13:33:29 から0:00:15の時間、故障していました。
復旧済: 10.20.30.1/16 は 2021-10-19 13:33:51 から0:00:06の時間、故障していました。
復旧済: 10.20.30.1/16 は 2021-10-19 13:37:20 から0:00:01の時間、故障していました。
復旧済: 10.20.30.2/16 は 2020-10-19 13:33:35 から0:00:08の時間、故障していました。
復旧済: 10.20.30.2/16 は 2021-10-19 13:33:54 から0:00:04の時間、故障していました。
復旧済: 10.20.30.2/16 は 2021-10-19 13:37:12 から0:00:20の時間、故障していました。
復旧済: 192.168.1.2/24 は 2020-10-19 13:34:45 から10 days, 0:03:00の時間、故障していました。
故障中: 192.168.200.1/24 は 2020-10-30 20:59:21 から ping が timeout です。
復旧済: 192.168.255.1/22 は 2020-10-30 21:59:41 から0:00:03の時間、故障していました。
故障中: 192.168.255.20/22 は 2020-12-01 11:11:13 から ping が timeout です。
```

#### 各サーバの過負荷状態一覧

各サーバの過負荷状態一覧を表示する。

その際、引数(last_overload)は「直近 last_overload 回の平均応答時間を取得」

引数(mtime_overload)は「平均応答時間が mtime_overload ミリ秒以上となった場合、過負荷状態」

の役割を持つ。

```python
  print("---サーバの過負荷状態を表示---")
  last_overload = 2 # 直近 last_overload 回の平均応答時間を取得
  mtime_overload = 50 # 平均応答時間が mtime_overload ミリ秒以上となった場合、過負荷状態
  for ipaddress, server in servers.items():
    server.show_period_server_overload(last_overload, mtime_overload)
```

出力

```
---サーバの過負荷状態を表示---
解決済: 10.20.30.1/16 は 2020-10-19 13:32:24 から 0:01:20 の時間、過負荷状態でした。
解決済: 10.20.30.1/16 は 2021-10-19 13:33:45 から 0:00:02 の時間、過負荷状態でした。
未解決: 10.20.30.1/16 は 2021-10-19 13:33:48 から過負荷状態です。
解決済: 10.20.30.2/16 は 2021-10-19 13:33:58 から 0:03:47 の時間、過負荷状態でした。
未解決: 10.20.30.2/16 は 2021-10-19 13:38:57 から過負荷状態です。
未解決: 192.168.1.2/24 は 2020-10-29 13:37:45 から過負荷状態です。
未解決: 192.168.255.1/22 は 2020-10-30 21:59:44 から過負荷状態です。
```

#### 各サブネット毎の故障期間一覧

各サブネット毎の故障期間を表示する。

```python
  print("---サブネットの故障期間を表示---")
  continue_timeout_error = 1  # continue_timeout_error 回 timeout が連続すれば、故障とする
  for network_address, subnet in subnets.items():
    subnet.show_period_subnet_error(continue_timeout_error)
```

出力

```
---サブネットの故障期間を表示---
復旧済: サブネット(10.20.0.0) は 2020-10-19 13:33:30 から0:00:13の時間、故障していました。
復旧済: サブネット(10.20.0.0) は 2021-10-19 13:33:50 から0:00:07の時間、故障していました。
故障中: サブネット(192.168.100.0) は 2020-10-30 09:45:21 から ping が timeout です。
復旧済: サブネット(192.168.200.0) は 2020-10-30 20:45:21 から0:07:10の時間、故障していました。
故障中: サブネット(192.168.200.0) は 2020-10-30 20:55:21 から ping が timeout です。
復旧済: サブネット(192.168.255.0) は 2020-10-30 21:59:21 から0:00:11の時間、故障していました。
```

#### 各サブネット毎の過負荷状態一覧

各サブネット毎の過負荷状態を表示する。

```python
  print("---サブネットの過負荷状態を表示---")
  last_overload = 2 # 直近 last_overload 回の平均応答時間を取得
  mtime_overload = 50 # 平均応答時間が mtime_overload ミリ秒以上となった場合、過負荷状態
  for network_address, subnet in subnets.items():
    subnet.show_period_subnet_overload(last_overload, mtime_overload)
```

出力

```
---サブネットの過負荷状態を表示---
解決済: サブネット(10.20.0.0) は 2021-10-19 13:33:58 から 0:03:47 の時間、過負荷状態でした。
未解決: サブネット(10.20.0.0) は 2021-10-19 13:38:57 から過負荷状態です。
```

### 実行時のオプション

#### ログエラーの出力

ログファイルに想定したエラーが含まれていた場合、以下のオプションを True にすることで標準出力される。

```python
# IS_VISUABLE_MISS_FORMAT
# True: LOGFILENAMEにあるログの形式ミスを表示する
# False:LOGFILENAMEにあるログの形式ミスを表示しない
IS_VISUABLE_MISS_FORMAT = True
```

出力

```
00200119133124 は適切な形式ではありません。
20200019133124 は適切な形式ではありません。
20201250133124 は適切な形式ではありません。
20201219463124 は適切な形式ではありません。
20200119139924 は適切な形式ではありません。
20200119133199 は適切な形式ではありません。
99999999999999 は適切な形式ではありません。
256.a.30.1/16 は適切な形式ではありません。
10.20.30.1/0 は適切な形式ではありません。
10.20.30.1/31 は適切な形式ではありません。
-99 は適切な形式ではありません。
20200231133124 は存在しません
9999999999a999 は適切な形式ではありません。
310.20.30.1/-99 は適切な形式ではありません。
-9999 は適切な形式ではありません。
```

## Log クラス

### インスタンス変数

- datetime : ping の送信日時
- ipaddress : IP アドレス
- restime : 応答時間

### is_timeout 関数

自身がタイムアウトかどうかを返す関数

返り値）

True : タイムアウトしている

False : タイムアウトしていない

### get_network_address 関数

自身のネットワークアドレスを返す関数

例）

192.168.255.20/22 : 自身のアドレス

返り値 : 192.168.252.0

## LogCollection クラス

Log クラスをまとめたクラス

## LogServer クラス

Log をサーバ毎にまとめるクラス

```python
# LogServer is log collection per ipaddress
# ---constract---
# [Log, Log, Log, ...]
# ---instance variables---
# self.ipaddress
# is recognized where server's Log.
#
# self.period_server_error
# is list of datetime of start_error and end_error
# [[dt_start_error, dt_end_error], [dt_start_error, dt_end_error], ... ]
# [[1回目の故障期間], [2回目の故障期間], ...]
```

## LogSubnet クラス

Log をサブネット毎にまとめるクラス

```python
# ---constract---
# {network_address: [Log, Log, Log, ...],
# network_address: [Log, Log, Log, ...]}
# ex)
# {'192.168.255.1/22': [Log, Log, Log, ...],
# '192.168.255.20/22': [Log, Log, Log, ...]}
```

## テストデータ

[テストデータ](/ping.log)

## 想定したログエラー

### 送信日時

ping の送信日時は以下のもの以外受け付けない。

- 年:1900~2999
- 月:01~12
- 日:01~31 # 存在しない日にちは受け付けない 例）2 月 31 日は存在しないため、受け付けない
- 時:00~23
- 分:00~59
- 秒:00~59

例）

2020 年 01 月 02 日 03 時 45 分 59 秒 # OK

**0200** 年 01 月 02 日 03 時 45 分 59 秒 # NG

2020 年 **13** 月 02 日 03 時 45 分 59 秒 # NG

2020 年 01 月 **59** 日 03 時 45 分 59 秒 # NG

2020 年 01 月 02 日 03 時 **60** 分 59 秒 # NG

2020 年 **02 月 31 日** 03 時 45 分 59 秒 # NG

2020 年 01 月 02 日 03 時 **-45** 分 **5a** 秒 # NG

### IP アドレス

IP アドレスは以下が対象範囲

- 0.0.0.0 ~ 255.255.255.255

サブネットマスクは 1-30 以外は受け付けません。

例）

192.168.10.1/24 # OK

192.168.10.1/**0** # NG

**256**.168.10.1/24 # NG

192.168.10.1/**31** # NG

### 応答時間

応答時間は 0 及び正の整数以外受け付けません

例）

20 # OK

0 # OK

**-9** # NG

**a** # NG
