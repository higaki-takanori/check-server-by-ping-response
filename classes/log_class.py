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
    self.datetimes_timeout = {}
    self.datetimes_response = {}
    self.count_timeout = {}

  def get_datetimes_timeout(self):
    return self.datetimes_timeout

  def get_datetimes_response(self):
    return self.datetimes_response

  def append_times(self, log, dict):
    l = []
    if log.ipaddress not in dict:
      dict[log.ipaddress] = [log.datetime]
    else:
      l = dict[log.ipaddress]
      l.append(log.datetime)
      dict[log.ipaddress] = l
    return dict

  def update_times(self):
    self.datetimes_timeout = {}
    self.datetimes_response = {}
    for log in self:
      if log.is_timeout():
        self.datetimes_timeout = self.append_times(log, self.datetimes_timeout)
      else:
        self.datetimes_response = self.append_times(log, self.datetimes_response)

  def get_response_and_period(self, ipaddress, datetime_timeout):
    if ipaddress in self.datetimes_response:
      for datetime_response in self.datetimes_response[ipaddress]:
        period_timeout = datetime_response - datetime_timeout
        if period_timeout.days >= 0:  # タイムアウト後に復旧した場合
          return datetime_response, period_timeout
    return None, None

  def show_errors(self):
    self.update_times()

    period_timeout = None
    for ipaddress, datetimes_timeout in self.datetimes_timeout.items(): # タイムアウトの時間
      for datetime_timeout in datetimes_timeout:
        datetime_response, period_timeout = self.get_response_and_period(ipaddress, datetime_timeout)
        if datetime_response is None:
          print(f"故障中: {ipaddress} は {datetime_timeout} から ping が timeout です。")
        else:
          print(f"復旧済: {ipaddress} は {datetime_timeout} から{period_timeout}の間、故障していました。")