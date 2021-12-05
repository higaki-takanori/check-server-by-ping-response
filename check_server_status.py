from classes.log_class import Log, LogCollection

LOGFILENAME = "ping.log"
INDEX_TIMEOUT = 0
INDEX_RESTIME = 1

if __name__ == '__main__':
  logs = LogCollection()
  for line in open(LOGFILENAME, "r"):
    datetime, ipaddress, restime = line.split("\n")[0].split(",")
    logs.append(Log(datetime, ipaddress, restime))

  logs.update_times()
  logs.show_errors()
