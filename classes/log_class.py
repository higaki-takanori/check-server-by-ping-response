from datetime import datetime as dt
from collections import deque
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
IS_VISUABLE_MISS_FORMAT = False

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
      self.network_address = self.get_network_address()

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
    list_network_address = []
    network_address = None
    for i, address in enumerate(ipaddress):
      if i < syo:
        list_network_address.append(address)
      elif i == syo:
        shifted_address = int(address) >> amari
        list_network_address.append(str(int(address) - shifted_address))
      else:
        list_network_address.append("0")
    network_address = ".".join(list_network_address)
    return network_address

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
class LogServer(list):
  def __init__(self, ipaddress=None, network_address=None):
    self.ipaddress = ipaddress
    self.network_address = network_address
    self.period_server_error = []
    self.period_server_overload = []

  def set_ipaddress(self, ipaddress):
    self.ipaddress = ipaddress

  def get_ipaddress(self):
    return self.ipaddress

  def get_period_server_error(self, continue_timeout_error=1):
    self.period_server_error = self.__get_period_server_error(continue_timeout_error)
    return self.period_server_error

  def show_period_server_error(self, continue_timeout_error=1):
    list_period = self.__get_period_server_error(continue_timeout_error)
    for period in list_period:
      if period[1] is None:
        print(f"故障中: {self.ipaddress} は {period[0]} から ping が timeout です。")
      else:
        print(f"復旧済: {self.ipaddress} は {period[0]} から{period[1] - period[0]}の時間、故障していました。")

  def __get_period_server_error(self, continue_timeout_error=1):
    period_server_error = []
    dt_start_error = None
    dt_end_error = None
    count_error = 0
    for log in self:
      if log.restime == '-':
        count_error += 1
        dt_start_error = log.datetime if continue_timeout_error <= count_error and dt_start_error is None else dt_start_error
      else:
        dt_end_error = log.datetime if continue_timeout_error <= count_error else None
        count_error = 0
      if (type(dt_start_error) is dt) and (type(dt_end_error) is dt) and (dt_start_error <= dt_end_error):
        period_server_error.append([dt_start_error, dt_end_error])
        dt_start_error = dt_end_error = None
    if (dt_start_error is not None) and (dt_end_error is None):
      period_server_error.append([dt_start_error, dt_end_error])

    return period_server_error

  def get_period_server_overload(self, last_overload=2, mtime_overload=10):
    self.period_server_overload = self.__get_period_server_overload(last_overload, mtime_overload)
    return self.period_server_overload

  def show_period_server_overload(self, last_overload=2, mtime_overload=10):
    list_period = self.__get_period_server_overload(last_overload, mtime_overload)
    for period in list_period:
      if period[1] is None:
        print(f"未解決: {self.ipaddress} は {period[0]} から過負荷状態です。")
      else:
        print(f"解決済: {self.ipaddress} は {period[0]} から {period[1] - period[0]} の時間、過負荷状態でした。")

  def __get_period_server_overload(self, last_overload=2, mtime_overload=10):
    period_server_overload = []
    queue = deque()
    sum_restime = 0
    ave_restime = 0
    dt_start_overload = None
    dt_end_overload = None
    for log in self:
      if log.restime != '-':
        queue.append(float(log.restime))
        if last_overload <= len(queue): # 直近m回の平均応答回数の算出
          sum_restime = sum(queue)
          ave_restime =  sum_restime / len(queue)
          queue.popleft()
        if mtime_overload < ave_restime:
          dt_start_overload = log.datetime if dt_start_overload is None else dt_start_overload
        else:
          dt_end_overload = log.datetime if dt_start_overload is not None else None
          if (type(dt_start_overload) is dt) and (type(dt_end_overload) is dt) and (dt_start_overload <= dt_end_overload):
            period_server_overload.append([dt_start_overload, dt_end_overload])
            dt_start_overload = dt_end_overload = None
    if (dt_start_overload is not None) and (dt_end_overload is None):
      period_server_overload.append([dt_start_overload, dt_end_overload])

    return period_server_overload

# LogSubnet is log collection per subnet
# ---constract---
# {network_address: [Log, Log, Log, ...],
# network_address: [Log, Log, Log, ...]}
# ex)
# {'192.168.255.1/22': [Log, Log, Log, ...],
# '192.168.255.20/22': [Log, Log, Log, ...]}
class LogSubnet(dict):
  def __init__(self, network_address=None):
    self.network_address = network_address
    self.server_ipaddress = []
    self.period_subnet_error = None
    self.period_subnet_overload = None

  def set_network_address(self, network_address):
    self.network_address = network_address

  def get_network_address(self):
    return self.network_address

  def get_period_subnet_error(self, continue_timeout_error=1):
    self.period_subnet_error = self.__get_period_subnet_error(continue_timeout_error)
    return self.period_subnet_error

  def show_period_subnet_error(self, continue_timeout_error=1):
    list_period = self.__get_period_subnet_error(continue_timeout_error)
    if list_period is not None:
      for period in list_period:
        if period[1] is None:
          print(f"故障中: サブネット({self.network_address}) は {period[0]} から ping が timeout です。")
        else:
          print(f"復旧済: サブネット({self.network_address}) は {period[0]} から{period[1] - period[0]}の時間、故障していました。")

  def get_period_subnet_overload(self, last_overload=2, mtime_overload=10):
    self.period_subnet_overload = self.__get_period_subnet_overload(last_overload, mtime_overload)
    return self.period_subnet_overload

  def show_period_subnet_overload(self, last_overload=2, mtime_overload=10):
    list_period = self.__get_period_subnet_overload(last_overload, mtime_overload)
    if list_period is not None:
      for period in list_period:
        if period[1] is None:
          print(f"未解決: サブネット({self.network_address}) は {period[0]} から過負荷状態です。")
        else:
          print(f"解決済: サブネット({self.network_address}) は {period[0]} から {period[1] - period[0]} の時間、過負荷状態でした。")

  def get_overlap_period(self, period_a, period_b):
    POS_START = 0
    POS_END = 1
    dt_start_a = dt_end_a = None
    dt_start_b = dt_end_b = None
    period_overlap = []
    for dt_a in period_a:
      dt_start_a = dt_a[POS_START]
      dt_end_a = dt_a[POS_END]
      for dt_b in period_b:
        dt_start_b = dt_b[POS_START]
        dt_end_b = dt_b[POS_END]
        if (dt_end_b is not None) and (dt_end_a is not None):
          if dt_end_b < dt_start_a:
            #             <---a--->
            # <--b--->
            continue
          elif dt_end_a < dt_start_b:
            # <---a--->
            #             <---b--->
            continue
          elif dt_start_a < dt_start_b and dt_end_b < dt_end_a:
            # <---a----->
            #   <--b-->
            period_overlap.append([dt_start_b, dt_end_b])
          elif dt_start_a < dt_start_b and dt_end_a < dt_end_b:
            # <---a--->
            #   <---b--->
            period_overlap.append([dt_start_b, dt_end_a])
          elif dt_start_b < dt_start_a and dt_end_b < dt_end_a:
            #   <---a--->
            # <--b--->
            period_overlap.append([dt_start_a, dt_end_b])
        elif (dt_end_a is None) and (dt_end_b is None):
          if dt_start_b < dt_start_a:
            #   <---a---
            # <---b---
            period_overlap.append([dt_start_a, None])
          elif dt_start_a < dt_start_b:
            # <---a---
            #   <---b---
            period_overlap.append([dt_start_b, None])
        elif dt_end_a is None:
          if dt_end_b < dt_start_a:
            #           <---a---
            # <--b-->
            continue
          elif dt_start_a < dt_end_b:
            if dt_start_a < dt_start_b:
              # <---a------
              #   <--b-->
              period_overlap.append([dt_start_b, dt_end_b])
            elif dt_start_b < dt_start_a:
              #   <---a---
              # <--b-->
              period_overlap.append([dt_start_a, dt_end_b])
        elif dt_end_b is None:
          if dt_end_a < dt_start_b:
            # <--a-->
            #           <--b---
            continue
          else:
            if dt_start_a < dt_start_b:
              # <--a-->
              #   <--b-----
              period_overlap.append([dt_start_b, dt_end_a])
            elif dt_start_b < dt_start_a:
              #   <--a-->
              # <----b-----
              period_overlap.append([dt_start_a, dt_end_a])

    return period_overlap

  def __get_period_subnet_error(self, continue_timeout_error=1):
    period_overlap = None
    for network_address, subnet in self.items():
      period_server = subnet.get_period_server_error(continue_timeout_error)
      if period_overlap is None:
        period_overlap = period_server
      else:
        period_overlap = self.get_overlap_period(period_overlap, period_server)

    return period_overlap

  def __get_period_subnet_overload(self, last_overload=2, mtime_overload=10):
    period_overlap = None
    for network_address, subnet in self.items():
      period_server = subnet.get_period_server_overload(last_overload, mtime_overload)
      if period_overlap is None:
        period_overlap = period_server
      else:
        period_overlap = self.get_overlap_period(period_overlap, period_server)

    return period_overlap

class LogCollection(list):
  def __init__(self):
    self.servers = {}
    self.subnets = {}

  def get_servers(self):
    self.servers = self.__update_servers()
    return self.servers

  def get_subnets(self):
    self.subnets = self.__update_subnets()
    return self.subnets

  # private method update servers
  # thid method return servers dict
  # ex) server dict
  # {'10.20.30.1/16': [Log, Log, Log, ...],
  # '192.168.1.1/24': [Log, Log, Log, ...],
  # ...}
  def __update_servers(self):
    servers = {}
    for log in self:
      if log.ipaddress not in servers:
        servers[log.ipaddress] = LogServer(log.ipaddress, log.network_address)
      if type(servers[log.ipaddress]) is LogServer:
        servers[log.ipaddress].append(log)
      else:
        print(f"{servers[log.ipaddress]} can not create LogServer Instance")
        return -1
    return servers

  # private method Update subnets
  # thid method return subnets dict
  # ex) subnets dict
  # {'192.168.252.0':
  #     {'192.168.255.1/22': [Log, Log, Log, ...],
  #     '192.168.255.20/22': [Log, Log, Log, ...]},
  # '10.20.0.0':
  #     {'10.20.30.1/16': [Log, Log, Log, ...],
  #     {'10.20.40.1/16': [Log, Log, Log, ...]}
  # }
  def __update_subnets(self):
    subnets = {}
    servers = self.get_servers()
    for ipaddress, server in servers.items():
      network_address = server.network_address
      if network_address not in subnets:
        subnets[network_address] = LogSubnet(network_address)
      if type(subnets[network_address]) is LogSubnet:
        subnets[network_address][ipaddress] = server
      else:
        print(f"{subnets[network_address]} can not create LogSubnet Instance")
        return -1
    return subnets
