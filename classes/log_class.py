from datetime import datetime as dt

TIMESTR = "%Y%m%d%H%M%S"

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
    self.errors = {}

  def get_errors(self):
    for log in self:
      if log.is_timeout():
        self.errors[log.ipaddress] = log.datetime
    return self.errors
