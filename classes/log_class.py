class Log:
  def __init__(self, datetime, ipaddress, restime):
    self.datetime = datetime
    self.ipaddress = ipaddress
    self.restime = restime

  def is_arrive(self):
    if self.restime == '-':
      return -1
    else:
      return 0

  def subnet(self):
    subnet = self.ipaddress.split('/')[1]
    return subnet

  def address(self):
    address = self.ipaddress.split('/')[0]
    return address

class LogCollection(list):
  def __init__(self, logs=[]):
    self.logs = logs
