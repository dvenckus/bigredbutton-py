#
# Class PushItem
#

import calendar
import time


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
        self.timestamp = calendar.timegm(time.gmtime())
        self.username = username
        self.subdomain = subdomain
        self.site = site
        self.task = task
        self.dbbackup = dbbackup
        self.status = status

    def __repr__(self):
        return "<PushItem(id='%d', subdomain='%s', site='%s', task='%s', backup='%r', username='%s', timestamp='%d', status='%d')>" % (
                     self.id, self.subdomain, self.site, self.task, self.dbbackup, self.username, self.timestamp, self.status)

    def toDict(self):
      dict_ = {}
      for key in self.__mapper__.c.keys():
          dict_[key] = getattr(self, key)
      return dict_
