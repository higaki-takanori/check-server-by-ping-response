from datetime import datetime as dt

TIMESTR = "%Y%m%d%H%M%S"
# INDEX_TIMEOUT = 0  # エラー辞書の配列のインデックス：故障時の日時
# INDEX_RESTIME = 1  # エラー辞書の配列のインデックス：復旧時の日時

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
    self.times_timeout = {}
    self.times_response = {}
    self.count_timeout = {}

  def get_times_timeout(self):
    return self.times_timeout

  def get_times_response(self):
    return self.times_response

  def append_times(self, log, dict):
    l = []
    if log.ipaddress not in dict:
      dict[log.ipaddress] = [log.datetime]
    else:
      l = dict[log.ipaddress]
      l.append(log.datetime)
      dict[log.ipaddress] = l
    return dict

  def update_times(self, num_continue=1):
    self.times_timeout = {}
    self.times_response = {}
    for log in self:
      if log.is_timeout():
        self.times_timeout = self.append_times(log, self.times_timeout)
      else:
        self.times_response = self.append_times(log, self.times_response)

  def show_errors(self):
    self.update_times()

    period_timeout = None
    for ipaddress, times_timeout in self.times_timeout.items(): # タイムアウトの時間
      for time_timeout in times_timeout:
        if ipaddress in self.times_response:
          for time_response in self.times_response[ipaddress]:
            period_timeout = time_response - time_timeout
            if period_timeout.days >= 0:  # タイムアウト後に ping が通った場合
              print(f"復旧済: {ipaddress} は {time_timeout} から{period_timeout}の間、故障していました。")
              break
          if period_timeout.days < 0:     # タイムアウト後に ping が通っていない場合
            print(f"故障中: {ipaddress} は {time_timeout} から ping が timeout です。")
        else:   #　全ての ping がタイムアウトの場合
          print(f"故障中: {ipaddress} は {time_timeout} から ping が timeout です。")
