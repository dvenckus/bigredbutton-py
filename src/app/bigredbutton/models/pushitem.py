#
# Class PushItem
#

from time import time
from datetime import datetime
import pytz
import json


########################################################################
class PushItem(object):
    """"""
    id = 0
    timestamp = 0
    username = ''
    task = ''
    options = ''
    status = 0

    parsedOptions = {}

    #----------------------------------------------------------------------
    def __init__(self, username, task, options={}, status=0):
        """"""
        # timestamp in unixtime
        self.timestamp = int(time())
        self.username = username
        self.task = task
        self.options = json.dumps(options)
        self.status = status

        self.parsedOptions = options

    def __repr__(self):
        tz = pytz.timezone('America/Chicago')
        ts = datetime.fromtimestamp(self.timestamp, tz).strftime('%Y-%m-%d %H:%M:%S')
        return "<PushItem(id='%d', task='%s', options='%s', username='%s', timestamp='%s', status='%d')>" % (
                     self.id, self.task, self.options, self.username, ts, self.status)


    def toDict(self):
      ''' convert object to dict '''
      dict_ = {}
      for key in self.__mapper__.c.keys():
          dict_[key] = getattr(self, key)
      return dict_


    def parseOptions(self):
      ''' parse options string into json dict '''
      self.parsedOptions = json.loads(self.options)
      return self.parsedOptions

    