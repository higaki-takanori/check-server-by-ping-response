from classes.log_class import Log, LogCollection, check_format, TIMESTR

LOGFILENAME = "ping.log"

# IS_VISUABLE_MISS_FORMAT
# True: LOGFILENAMEにあるログの形式ミスを表示する
# False:LOGFILENAMEにあるログの形式ミスを表示しない
IS_VISUABLE_MISS_FORMAT = False

# DO_LESS_LAST_OVERLOAD
# True: 直近のping回数が少なくても合わせて実行
# False: 直近のping回数が少ない場合、過負荷状態を検出しない
DO_LESS_LAST_OVERLOAD = False

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
  continue_timeout_error = 2
  for ipaddress, server in servers.items():
    server.show_period_server_error(continue_timeout_error)

  print("---サーバの過負荷状態を表示---")
  last_overload = 2
  mtime_overload = 50
  for ipaddress, server in servers.items():
    server.show_period_server_overload(last_overload, mtime_overload)

  # for network_address, subnet in subnets.items():
  #   print(f"--- network_address: {network_address} ---")
  #   for ipaddress, server in subnet.items():
  #     print(ipaddress)
  #     for log in server:
  #       print(log.datetime, log.ipaddress, log.restime)


  # conti_timeout_error = 2 # conti_timeout_error 回 timeout が連続すれば、故障とする
  # logs.show_errors(conti_timeout_error)

  # last_overload = 2 # 直近 last_overload 回の平均応答時間を取得
  # mtime_overload = 50 # 平均応答時間が mtime_overload ミリ秒以上となった場合、過負荷状態
  # logs.show_overload(last_overload, mtime_overload, DO_LESS_LAST_OVERLOAD)

  # logs.show_subnet_error(conti_timeout_error)
