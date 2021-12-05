from classes.log_class import Log, LogCollection

LOGFILENAME = "ping.log"

if __name__ == '__main__':
  logs = LogCollection()
  for line in open(LOGFILENAME, "r"):
    datetime, ipaddress, restime = line.split("\n")[0].split(",")
    logs.append(Log(datetime, ipaddress, restime))

  errors = logs.get_errors()
  print(errors)
  for error, value in errors.items():
    print(error, value)

  print(logs.get_errors())

  # for log in logs:
  #   print(log.datetime - time)
  #   print(time)
  #   time = log.datetime
  #   print(log.datetime, log.ipaddress, log.restime)
