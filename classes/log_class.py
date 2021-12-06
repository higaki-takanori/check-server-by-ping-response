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

  def update_datetimes(self):
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

  def is_recovered(self, ipaddress):
    if ipaddress not in self.datetimes_response:
      return False
    elif self.datetimes_timeout[ipaddress][-1] > self.datetimes_response[ipaddress][-1]: # 最終的に復旧していない
      return False
    else:
      return True

  def show_errors(self, conti_timeout_error=1):
    self.update_datetimes()
    for ipaddress, datetimes_timeout in self.datetimes_timeout.items():
      before_response = None
      for datetime_timeout in datetimes_timeout:
        datetime_response, period_timeout = self.get_response_and_period(ipaddress, datetime_timeout) # 復旧日時と故障期間の取得
        if before_response == datetime_response:  # datetime_response が前回と同じ場合、連続したタイムアウトとなる
          self.count_timeout[ipaddress] = 1 if ipaddress not in self.count_timeout else self.count_timeout[ipaddress] + 1
        else:
          before_response = datetime_response
          self.count_timeout[ipaddress] = 1
        count_now_timeout = 1 if ipaddress not in self.count_timeout else self.count_timeout[ipaddress]
        if count_now_timeout >= conti_timeout_error:
          if datetime_response is None:
            print(f"故障中: {ipaddress} は {datetime_timeout} から ping が timeout です。")
          else:
            print(f"復旧済: {ipaddress} は {datetime_timeout} から{period_timeout}の間、故障していました。")
      if self.is_recovered(ipaddress):
        self.count_timeout[ipaddress] = 0