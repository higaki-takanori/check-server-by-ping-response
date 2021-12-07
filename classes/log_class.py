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

  def get_network_address(self):
    subnet = self.get_subnet()
    ipaddress = self.get_address()
    ipaddress = ipaddress.split(".")
    syo = int(subnet) // 8
    amari = int(subnet) % 8
    network_address = []
    for i, address in enumerate(ipaddress):
      if i < syo:
        network_address.append(address)
      elif i == syo:
        shifted_address = int(address) >> amari
        network_address.append(str(int(address) - shifted_address))
      else:
        network_address.append("0")
    return network_address

class LogCollection(list):
  def __init__(self):
    self.times_timeout = {}
    self.times_response = {}
    self.count_timeout = {}
    self.subnet_timeout = {}
    self.subnet_response = {}
    self.subnet_count_timeout = {}

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
    for ipaddress, times_timeout_list in self.times_timeout.items():
      before_response = None
      for datetime_timeout in times_timeout_list[INDEX_DATETIME]:
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
    for ipaddress, times_response_list in self.times_response.items():
      sum_restime_overload = 0
      ave_restime_overload = 0
      if do_less_last_overload:
        last_overload = len(times_response_list[INDEX_RESTIME]) if last_overload > len(times_response_list[INDEX_RESTIME]) else last_overload
      else:
        if last_overload > len(times_response_list[INDEX_RESTIME]):
          continue
      for i, (restime, datetime_response) in enumerate(zip(reversed(times_response_list[INDEX_RESTIME]), reversed(times_response_list[INDEX_DATETIME]))):
        sum_restime_overload += int(restime)
        if last_overload <= i + 1:
          break
      ave_restime_overload = sum_restime_overload / last_overload
      if mtime_overload < ave_restime_overload:
        print(f"{ipaddress} は {datetime_response} から過負荷状態です")

  def update_subnets(self):
    self.subnet_timeout = {}
    self.subnet_response = {}
    for log in self:
      network_address = ".".join(log.get_network_address())
      if log.is_timeout():
        self.subnet_timeout[network_address] = {} if network_address not in self.subnet_timeout else self.subnet_timeout[network_address]
        self.subnet_timeout[network_address] = self.append_datetimes(log, self.subnet_timeout[network_address])
      else:
        self.subnet_response[network_address] = {} if network_address not in self.subnet_response else self.subnet_response[network_address]
        self.subnet_response[network_address] = self.append_datetimes(log, self.subnet_response[network_address])

  def get_period_subnet_error(self, conti_timeout_error):
    period_subnet_error = {}
    for network_address, times_timeout in self.subnet_timeout.items():
      period_subnet_error[network_address] = {}
      for ipaddress, times_timeout_list in times_timeout.items():
        before_response = None
        for datetime_timeout in times_timeout_list[INDEX_DATETIME]:
          datetime_response, period_timeout = self.get_response_and_period(ipaddress, datetime_timeout) # 復旧日時と故障期間の取得
          if before_response == datetime_response:  # datetime_response が前回と同じ場合、連続したタイムアウトとなる
            self.subnet_count_timeout[ipaddress] = 1 if ipaddress not in self.subnet_count_timeout else self.subnet_count_timeout[ipaddress] + 1
          else:
            before_response = datetime_response
            self.subnet_count_timeout[ipaddress] = 1
          count_now_timeout = 1 if ipaddress not in self.subnet_count_timeout else self.subnet_count_timeout[ipaddress]
          if count_now_timeout >= conti_timeout_error:
            if ipaddress not in period_subnet_error[network_address]:
              period_subnet_error[network_address][ipaddress] = [[datetime_timeout, datetime_response]]
            else:
              period_subnet_error[network_address][ipaddress].append([datetime_timeout, datetime_response])
    return period_subnet_error

  def show_subnet_error(self, conti_timeout_error=1):
    print("---サブネットの故障一覧を表示---")
    self.update_subnets()
    period_subnet_error = {}
    period_subnet_error =  self.get_period_subnet_error(conti_timeout_error)
    for network_address, periods_error in period_subnet_error.items():
      print(f"---{network_address}---")
      for ipaddress, datetimes in periods_error.items():
        print(f"ipaddress: {ipaddress}")
        print("   故障開始時間   ｜   故障終了時間   ")
        for start_time1, end_time1 in datetimes:
          print(f"{start_time1}| {end_time1}")

  def compare_period(self, start_time1, end_time1, start_time2, end_time2):
    start_time = None
    end_time = None
    if end_time1 < start_time2:
      start_time = None
      end_time = None
    elif start_time2 < end_time1:
      start_time = start_time2 if start_time1 < start_time2 else start_time1
      end_time = end_time1 if end_time1 < end_time2 else end_time2
    return start_time, end_time
