from classes.log_class import Log, LogCollection

LOGFILENAME = "ping.log"

if __name__ == '__main__':
  logs = LogCollection()
  for line in open(LOGFILENAME, "r"):
    datetime, ipaddress, restime = line.split("¥n")[0].split(",")
    # print(datetime, ipaddress, restime)
    logs.append(Log(datetime, ipaddress, restime))

  print(logs.__class__)
  print(logs)
  for log in logs:
    print(log.address())
