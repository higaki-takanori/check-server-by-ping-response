import re
from datetime import datetime as dt
from classes.log_class import Log, LogCollection, check_format, TIMESTR

LOGFILENAME = "ping.log"

# IS_VISUABLE_MISS_FORMAT
# True: LOGFILENAMEにあるログの形式ミスを表示する
# False:LOGFILENAMEにあるログの形式ミスを表示しない
IS_VISUABLE_MISS_FORMAT = True

if __name__ == '__main__':
  logs = LogCollection()
  for line in open(LOGFILENAME, "r"):
    datetime, ipaddress, restime = line.split("\n")[0].split(",")
    is_correct_format = check_format(datetime, ipaddress, restime, IS_VISUABLE_MISS_FORMAT)
    if is_correct_format:
      try:
        logs.append(Log(datetime, ipaddress, restime))
      except:
        print(f"{datetime} は存在しません") if IS_VISUABLE_MISS_FORMAT else None # 存在しない日にちは受け付けない 例）2 月 31 日は存在ため、受け付けない

  conti_timeout_error = 2
  logs.show_errors(conti_timeout_error)
