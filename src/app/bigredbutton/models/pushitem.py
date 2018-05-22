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
    def __init__(self, username, task, options='', status=0):
        '''
        timestamp in unixtime using unixtimestamp decorator
        options are expected in the form of a json-compatible string
        '''
        self.timestamp = int(time())
        self.username = username
        self.task = task
        self.options = options
        self.status = status

        #self.parsedOptions = {}


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
      ''' 
      parse options string into json dict 
      call json.loads 2x to handle improperly quoted strings; 
      1st call converts to json-compatible string
      2nd call, if necessary, converts to json dict
      '''
      #self.parsedOptions = json.loads(json.loads(self.options))
      json_obj = json.loads(self.options)
      if isinstance(json_obj, str):
        # problem with json, call loads again
        json_obj = json.loads(json_obj)
        
      self.parsedOptions = json_obj
      return self.parsedOptions

    