from datetime import datetime as dt
import re

PATTERN_DATETIME = "[12]\d{3}" + "(0[1-9]|1[0-2])" + "(0[1-9]|[1-2]\d|3[0-1])" + "([0-1]\d|2[0-3])" + "[0-5]\d" + "[0-5]\d" # YYYYMMDDHHhhmmss
PATTERN_IPADDRESS = "((\d{1,2}|1\d{0,2}|2[0-4]\d|25[0-5])\.){3}(\d{1,2}|1\d{0,2}|2[0-4]\d|25[0-5])" + "\/([1-9]|[1-2]\d|30)" # 0.0.0.0/1 ~ 255.255.255.255/30
PATTERN_RESTIME = "(\d+)|-" # timeout は "-", 応答時間は 0 ~
INDEX_DATETIME = 0
INDEX_RESTIME = 1

TIMESTR = "%Y%m%d%H%M%S"

# IS_VISUABLE_MISS_FORMAT
# True: LOGFILENAMEにあるログの形式ミスを表示する
# False:LOGFILENAMEにあるログの形式ミスを表示しない
IS_VISUABLE_MISS_FORMAT = True

def check_format(datetime, ipaddress, restime, visuable=True):
  check_datetime = re.fullmatch(PATTERN_DATETIME, datetime)
  check_ipaddress = re.fullmatch(PATTERN_IPADDRESS, ipaddress)
  check_restime = re.fullmatch(PATTERN_RESTIME, restime)
  is_correct_format = True
  if check_datetime is None:
    print(f"{datetime} は適切な形式ではありません。") if visuable else None
    is_correct_format = False
  if check_ipaddress is None:
    print(f"{ipaddress} は適切な形式ではありません。") if visuable else None
    is_correct_format = False
  if check_restime is None:
    print(f"{restime} は適切な形式ではありません。") if visuable else None
    is_correct_format = False
  return is_correct_format

class Log:
  def __init__(self, datetime, ipaddress, restime):
    self.datetime = None
    self.ipaddress = None
    self.restime = None
    is_correct_format = check_format(datetime, ipaddress, restime, IS_VISUABLE_MISS_FORMAT)
    if is_correct_format:
      try:
        self.datetime = dt.strptime(datetime, TIMESTR)
      except:
        print(f"{datetime} は存在しません") if IS_VISUABLE_MISS_FORMAT else None # 存在しない日にちは受け付けない 例）2 月 31 日は存在ため、受け付けない
        return
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

  def append_datetimes(self, log, dict):
    l = [[] for i in range(2)]
    if log.ipaddress not in dict:
      dict[log.ipaddress] = [[log.datetime], [log.restime]]
    else:
      l = dict[log.ipaddress]
      l[INDEX_DATETIME].append(log.datetime)
      l[INDEX_RESTIME].append(log.restime)
      dict[log.ipaddress] = l
    return dict

  def update_datetimes(self):
    self.times_timeout = {}
    self.times_response = {}
    for log in self:
      if log.is_timeout():
        self.times_timeout = self.append_datetimes(log, self.times_timeout)
      else:
        self.times_response = self.append_datetimes(log, self.times_response)

  def get_response_and_period(self, ipaddress, datetime_timeout):
    if ipaddress in self.times_response:
      for datetime_response in self.times_response[ipaddress][INDEX_DATETIME]:
        period_timeout = datetime_response - datetime_timeout
        if period_timeout.days >= 0:  # タイムアウト後に復旧した場合
          return datetime_response, period_timeout
    return None, None

  def is_recovered(self, ipaddress):
    if ipaddress not in self.times_response:
      return False
    elif self.times_timeout[ipaddress][-1] > self.times_response[ipaddress][-1]: # 最終的に復旧していない
      return False
    else:
      return True

  def show_errors(self, conti_timeout_error=1):
    print("---故障一覧を表示---")
    self.update_datetimes()
    for ipaddress, times_timeout in self.times_timeout.items():
      before_response = None
      for datetime_timeout in times_timeout[INDEX_DATETIME]:
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
            print(f"復旧済: {ipaddress} は {datetime_timeout} から{period_timeout}の時間、故障していました。")
      if self.is_recovered(ipaddress):
        self.count_timeout[ipaddress] = 0

  def show_overload(self, last_overload=1, mtime_overload=10, do_less_last_overload=True):
    print("---過負荷状態一覧を表示---")
    self.update_datetimes()
    for ipaddress, times_response in self.times_response.items():
      sum_restime_overload = 0
      ave_restime_overload = 0
      if do_less_last_overload:
        last_overload = len(times_response[INDEX_RESTIME]) if last_overload > len(times_response[INDEX_RESTIME]) else last_overload
      else:
        if last_overload > len(times_response[INDEX_RESTIME]):
          continue
      for i, (restime, datetime_response) in enumerate(zip(reversed(times_response[INDEX_RESTIME]), reversed(times_response[INDEX_DATETIME]))):
        sum_restime_overload += int(restime)
        if last_overload <= i + 1:
          break
      ave_restime_overload = sum_restime_overload / last_overload
      if mtime_overload < ave_restime_overload:
        print(f"{ipaddress} は {datetime_response} から過負荷状態です")