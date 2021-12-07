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

  conti_timeout_error = 2 # conti_timeout_error 回 timeout が連続すれば、故障とする
  logs.show_errors(conti_timeout_error)

  last_overload = 2 # 直近 last_overload 回の平均応答時間を取得
  mtime_overload = 50 # 平均応答時間が mtime_overload ミリ秒以上となった場合、過負荷状態
  logs.show_overload(last_overload, mtime_overload, DO_LESS_LAST_OVERLOAD)

  logs.show_subnet_error(conti_timeout_error)
```

### main 関数の処理

#### LogCollection インスタンスの作成

list クラスを継承した LogColloction クラスのインスタンスを作成。

ログファイルごとに処理できるように、クラスを作成した。

```python
logs = LogCollection()
```

#### Log インスタンスの作成及び LogCollection への追加

ログファイルからログの情報を入手し、1 つのログに対して、1 つの Log クラスのインスタンスを作成し、LogCollection インスタンスへ追加する。

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

#### 各サーバの故障一覧

logs.show_errors 関数で各サーバの故障一覧を表示する。

その際に引数(conti_timeout_error)に数値を入れることで timeout 連続によるエラーを再現している。

```python
conti_timeout_error = 2 # conti_timeout_error 回 timeout が連続すれば、故障とする
logs.show_errors(conti_timeout_error)
```

出力

```
---故障一覧を表示---
復旧済: 10.20.30.1/16 は 2020-10-19 13:33:25 から0:00:19の時間、故障していました。
復旧済: 10.20.30.1/16 は 2020-10-19 13:33:26 から0:00:18の時間、故障していました。
復旧済: 10.20.30.1/16 は 2020-10-19 13:33:27 から0:00:17の時間、故障していました。
復旧済: 10.20.30.1/16 は 2020-10-19 13:33:28 から0:00:16の時間、故障していました。
復旧済: 10.20.30.1/16 は 2020-10-19 13:33:29 から0:00:15の時間、故障していました。
復旧済: 10.20.30.1/16 は 2020-10-19 13:33:30 から0:00:14の時間、故障していました。
復旧済: 192.168.1.2/24 は 2020-10-19 13:34:45 から10 days, 0:03:00の時間、故障していました。
復旧済: 192.168.1.2/24 は 2020-10-19 13:35:45 から10 days, 0:02:00の時間、故障していました。
復旧済: 192.168.1.2/24 は 2020-10-19 13:36:45 から10 days, 0:01:00の時間、故障していました。
故障中: 192.168.200.1/24 は 2020-10-30 20:59:21 から ping が timeout です。
復旧済: 192.168.255.1/22 は 2020-10-30 21:59:41 から0:00:03の時間、故障していました。
復旧済: 192.168.255.1/22 は 2020-10-30 21:59:42 から0:00:02の時間、故障していました。
復旧済: 192.168.255.1/22 は 2020-10-30 21:59:43 から0:00:01の時間、故障していました。
故障中: 192.168.255.20/22 は 2020-12-01 11:11:13 から ping が timeout です。
故障中: 192.168.255.20/22 は 2020-12-01 11:11:14 から ping が timeout です。
故障中: 192.168.255.20/22 は 2020-12-01 11:11:15 から ping が timeout です。

```

#### 各サーバの過負荷状態一覧

logs.show_overload 関数で各サーバの過負荷状態一覧を表示する。

その際、引数(last_overload)は「直近 last_overload 回の平均応答時間を取得」

引数(mtime_overload)は「平均応答時間が mtime_overload ミリ秒以上となった場合、過負荷状態」

の役割を持つ。

DO_LESS_LAST_OVERLOAD は[参照](#過負荷状態の検出の際に直近の-ping-回数が少ない場合)

```python
last_overload = 2 # 直近 last_overload 回の平均応答時間を取得
mtime_overload = 50 # 平均応答時間が mtime_overload ミリ秒以上となった場合、過負荷状態
logs.show_overload(last_overload, mtime_overload, DO_LESS_LAST_OVERLOAD)
```

出力

```
---過負荷状態一覧を表示---
192.168.1.2/24 は 2020-10-19 13:32:35 から過負荷状態です
192.168.255.1/22 は 2020-10-30 21:59:39 から過負荷状態です
```

#### 各サブネット毎の故障期間一覧

logs.show_subnet_error は、各サブネット毎の故障期間を表示する関数。

**現状、各サブネットの IP アドレスごとの故障開始時間と故障終了時間の一覧表示まで完成**

```python
logs.show_subnet_error(conti_timeout_error)
```

出力

```
---サブネットの故障一覧を表示---
---10.20.0.0---
ipaddress: 10.20.30.1/16
   故障開始時間   ｜   故障終了時間
2020-10-19 13:33:25| 2020-10-19 13:33:44
2020-10-19 13:33:26| 2020-10-19 13:33:44
2020-10-19 13:33:27| 2020-10-19 13:33:44
2020-10-19 13:33:28| 2020-10-19 13:33:44
2020-10-19 13:33:29| 2020-10-19 13:33:44
2020-10-19 13:33:30| 2020-10-19 13:33:44
---192.168.1.0---
ipaddress: 192.168.1.2/24
   故障開始時間   ｜   故障終了時間
2020-10-19 13:34:45| 2020-10-29 13:37:45
2020-10-19 13:35:45| 2020-10-29 13:37:45
2020-10-19 13:36:45| 2020-10-29 13:37:45
---192.168.100.0---
---192.168.200.0---
ipaddress: 192.168.200.1/24
   故障開始時間   ｜   故障終了時間
2020-10-30 20:59:21| None
---192.168.255.0---
---192.168.252.0---
ipaddress: 192.168.255.1/22
   故障開始時間   ｜   故障終了時間
2020-10-30 21:59:41| 2020-10-30 21:59:44
2020-10-30 21:59:42| 2020-10-30 21:59:44
2020-10-30 21:59:43| 2020-10-30 21:59:44
ipaddress: 192.168.255.20/22
   故障開始時間   ｜   故障終了時間
2020-12-01 11:11:13| None
2020-12-01 11:11:14| None
2020-12-01 11:11:15| None
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

#### 過負荷状態の検出の際に直近の ping 回数が少ない場合

直近 m 回の平均応答時間を求める際に、ping が n(< m) 回の場合、以下のオプションを True にすることで直近 n 回の平均応答時間を求める。

例）

直近 5 回の平均応答時間を求めたい。

しかし、A サーバは ping は 3 回しか通っていない。

DO_LESS_LAST_OVERLOAD を True にすると、A サーバは直近 3 回の平均応答時間を求める。

DO_LESS_LAST_OVERLOAD を False にすると、A サーバは直近 3 回しか ping が通っていないため、平均応答時間を求めない。

```python
# DO_LESS_LAST_OVERLOAD
# True: 直近のping回数が少なくても合わせて実行
# False: 直近のping回数が少ない場合、過負荷状態を検出しない
DO_LESS_LAST_OVERLOAD = False
```

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
