#
# Class PushItem
#

from time import time
from datetime import datetime
import pytz


########################################################################
class PushItem(object):
    """"""
    id = 0
    timestamp = 0
    username = ''
    subdomain = ''
    site = ''
    task = ''
    dbbackup = 0
    status = 0

    #----------------------------------------------------------------------
    def __init__(self, username, subdomain, site, task, dbbackup, status=0):
        """"""
        # timestamp in unixtime
        self.timestamp = int(time())
        self.username = username
        self.subdomain = subdomain
        self.site = site
        self.task = task
        self.dbbackup = dbbackup
        self.status = status

    def __repr__(self):
        tz = pytz.timezone('America/Chicago')
        ts = datetime.fromtimestamp(self.timestamp, tz).strftime('%Y-%m-%d %H:%M:%S')
        return "<PushItem(id='%d', subdomain='%s', site='%s', task='%s', backup='%r', username='%s', timestamp='%s', status='%d')>" % (
                     self.id, self.subdomain, self.site, self.task, self.dbbackup, self.username, ts, self.status)

    def toDict(self):
      dict_ = {}
      for key in self.__mapper__.c.keys():
          dict_[key] = getattr(self, key)
      return dict_
