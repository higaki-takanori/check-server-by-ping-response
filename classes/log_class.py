from datetime import datetime as dt

TIMESTR = "%Y%m%d%H%M%S"
INDEX_TIMEOUT = 0  # エラー辞書の配列のインデックス：故障時の日時
INDEX_RESTIME = 1  # エラー辞書の配列のインデックス：復旧時の日時

class Log:
  def __init__(self, datetime, ipaddress, restime):
    self.datetime = dt.strptime(datetime, TIMESTR)
    self.ipaddress = ipaddress
    self.restime = restime

  def is_timeout(self):
    if self.restime == '-':
      return True
    else:
      return False

  def get_subnet(self):
    subnet = self.ipaddress.split('/')[1]
    return subnet

  def get_address(self):
    address = self.ipaddress.split('/')[0]
    return address

class LogCollection(list):
  def __init__(self):
    self.errors = {}

  def get_errors(self):
    return self.errors

  def update_errors(self):
  # 関数：self.errorsの更新
  # errorsの構造
  # errors = {IPアドレス: [故障時の日時][復旧時の日時]}
  # 配列のインデックスは以下の通り
  # 故障時の日時：INDEX_TIMEOUT = 0
  # 復旧時の日時：INDEX_RESTIME = 1
  # 例）
  # errors = {'10.20.30.1/16': [datetime.datetime(2020, 10, 19, 13, 33, 24), datetime.datetime(2020, 10, 19, 13, 33, 36)],
  #           '192.168.100.1/24': [datetime.datetime(2020, 10, 20, 9, 45, 21), None]}
    for log in self:
      if log.is_timeout():
        self.errors[log.ipaddress] = [log.datetime, None]
      # 同一サーバにて、前回のpingがtimeoutの場合
      elif (log.ipaddress in self.errors) and (self.errors[log.ipaddress][INDEX_RESTIME] == None):
        self.errors[log.ipaddress][INDEX_RESTIME] = log.datetime

  def show_errors(self):
    # self.errorsを更新するために実行
    self.update_errors()
    for ipaddress, times in self.errors.items():
      if times[INDEX_RESTIME] is None:
        print(f"故障中(ping is timeout)： {ipaddress}")
      else:
        print(f"復旧済：{ipaddress} は {times[INDEX_TIMEOUT]} から {times[INDEX_RESTIME] - times[INDEX_TIMEOUT]} の間、故障でした")